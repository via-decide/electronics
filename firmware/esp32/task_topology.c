/*
 * ESP32 FreeRTOS task-isolation topology.
 *
 * validation_id: esp32_freertos_task_isolation_v1
 * status: FIRMWARE_TASKS_ISOLATED
 *
 * Task model:
 *   ADC/acquisition task -> bounded raw queue -> DSP task -> bounded telemetry queue
 *   -> MQTT task, with storage/logging isolated on their own bounded queues and a
 *   watchdog supervisor that differentiates real task lockup from normal network latency.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "esp_err.h"
#include "esp_log.h"
#include "esp_system.h"
#include "esp_task_wdt.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"

#define TASK_TOPOLOGY_QUEUE_DEPTH          64U
#define TASK_TOPOLOGY_ACQUIRE_PERIOD_MS    10U
#define TASK_TOPOLOGY_WATCHDOG_PERIOD_MS   1000U
#define TASK_TOPOLOGY_ACQUIRE_STALE_MS     250U
#define TASK_TOPOLOGY_DSP_STALE_MS         1000U
#define TASK_TOPOLOGY_STORAGE_STALE_MS     5000U
#define TASK_TOPOLOGY_NETWORK_STALE_MS     30000U
#define TASK_TOPOLOGY_WDT_TIMEOUT_MS       8000U

#define TASK_TOPOLOGY_ACQUIRE_PRIORITY     (tskIDLE_PRIORITY + 5)
#define TASK_TOPOLOGY_DSP_PRIORITY         (tskIDLE_PRIORITY + 4)
#define TASK_TOPOLOGY_STORAGE_PRIORITY     (tskIDLE_PRIORITY + 2)
#define TASK_TOPOLOGY_MQTT_PRIORITY        (tskIDLE_PRIORITY + 1)
#define TASK_TOPOLOGY_LOG_PRIORITY         (tskIDLE_PRIORITY + 1)
#define TASK_TOPOLOGY_WATCHDOG_PRIORITY    (tskIDLE_PRIORITY + 3)

#define TASK_TOPOLOGY_STACK_WORDS          4096U
#define TASK_TOPOLOGY_LOG_TEXT_BYTES       96U

_Static_assert(TASK_TOPOLOGY_ACQUIRE_PRIORITY > TASK_TOPOLOGY_MQTT_PRIORITY,
               "acquisition task must outrank network task");
_Static_assert(TASK_TOPOLOGY_QUEUE_DEPTH == 64U, "task topology queue depth must be 64");

typedef struct {
    uint32_t sequence;
    uint32_t captured_at_ms;
    int32_t value;
} topology_raw_sample_t;

typedef struct {
    uint32_t sequence;
    uint32_t processed_at_ms;
    int32_t filtered_value;
} topology_telemetry_t;

typedef struct {
    uint32_t sequence;
    uint32_t written_at_ms;
    int32_t value;
} topology_storage_record_t;

typedef struct {
    uint32_t at_ms;
    char text[TASK_TOPOLOGY_LOG_TEXT_BYTES];
} topology_log_record_t;

typedef struct {
    const char *name;
    volatile uint32_t heartbeat_ms;
    uint32_t stale_after_ms;
    bool reset_on_stale;
} topology_watch_entry_t;

typedef struct {
    QueueHandle_t raw_queue;
    QueueHandle_t telemetry_queue;
    QueueHandle_t storage_queue;
    QueueHandle_t log_queue;
    TaskHandle_t acquire_task;
    TaskHandle_t dsp_task;
    TaskHandle_t mqtt_task;
    TaskHandle_t storage_task;
    TaskHandle_t log_task;
    TaskHandle_t watchdog_task;
    volatile uint32_t raw_queue_overflows;
    volatile uint32_t telemetry_queue_overflows;
    volatile uint32_t storage_queue_overflows;
    volatile uint32_t log_queue_overflows;
    topology_watch_entry_t acquire_watch;
    topology_watch_entry_t dsp_watch;
    topology_watch_entry_t mqtt_watch;
    topology_watch_entry_t storage_watch;
    topology_watch_entry_t log_watch;
} topology_context_t;

static const char *TAG = "task_topology";
static topology_context_t s_topology;

/* Application-specific hooks may be provided by sensor, DSP, MQTT, or storage modules. */
int32_t app_acquire_sensor_sample(void) __attribute__((weak));
int32_t app_dsp_filter_sample(int32_t raw_value) __attribute__((weak));
esp_err_t app_mqtt_publish_sample(const topology_telemetry_t *telemetry) __attribute__((weak));
esp_err_t app_storage_write_record(const topology_storage_record_t *record) __attribute__((weak));
void app_topology_log_line(const char *line) __attribute__((weak));

static uint32_t topology_now_ms(void)
{
    return (uint32_t)(xTaskGetTickCount() * portTICK_PERIOD_MS);
}

static void topology_heartbeat(topology_watch_entry_t *entry)
{
    entry->heartbeat_ms = topology_now_ms();
}

static bool topology_queue_send_counting(QueueHandle_t queue, const void *item,
                                         volatile uint32_t *overflow_counter)
{
    if (xQueueSend(queue, item, 0) == pdTRUE) {
        return true;
    }
    ++(*overflow_counter);
    return false;
}

static void topology_log_async(const char *text)
{
    topology_log_record_t record = {
        .at_ms = topology_now_ms(),
    };
    (void)snprintf(record.text, sizeof(record.text), "%s", text);
    (void)topology_queue_send_counting(s_topology.log_queue, &record,
                                       &s_topology.log_queue_overflows);
}

static void acquire_task(void *arg)
{
    topology_context_t *ctx = (topology_context_t *)arg;
    TickType_t next_wake = xTaskGetTickCount();
    uint32_t sequence = 0;

    for (;;) {
        topology_heartbeat(&ctx->acquire_watch);

        topology_raw_sample_t sample = {
            .sequence = sequence++,
            .captured_at_ms = topology_now_ms(),
            .value = app_acquire_sensor_sample != NULL ? app_acquire_sensor_sample() : 0,
        };

        if (!topology_queue_send_counting(ctx->raw_queue, &sample, &ctx->raw_queue_overflows)) {
            topology_log_async("raw queue overflow");
        }

        vTaskDelayUntil(&next_wake, pdMS_TO_TICKS(TASK_TOPOLOGY_ACQUIRE_PERIOD_MS));
    }
}

static void dsp_task(void *arg)
{
    topology_context_t *ctx = (topology_context_t *)arg;
    topology_raw_sample_t sample;

    for (;;) {
        topology_heartbeat(&ctx->dsp_watch);
        if (xQueueReceive(ctx->raw_queue, &sample, pdMS_TO_TICKS(100)) != pdTRUE) {
            continue;
        }

        const int32_t filtered = app_dsp_filter_sample != NULL
                                     ? app_dsp_filter_sample(sample.value)
                                     : sample.value;
        const topology_telemetry_t telemetry = {
            .sequence = sample.sequence,
            .processed_at_ms = topology_now_ms(),
            .filtered_value = filtered,
        };
        const topology_storage_record_t storage = {
            .sequence = sample.sequence,
            .written_at_ms = telemetry.processed_at_ms,
            .value = filtered,
        };

        if (!topology_queue_send_counting(ctx->telemetry_queue, &telemetry,
                                          &ctx->telemetry_queue_overflows)) {
            topology_log_async("telemetry queue overflow");
        }
        if (!topology_queue_send_counting(ctx->storage_queue, &storage,
                                          &ctx->storage_queue_overflows)) {
            topology_log_async("storage queue overflow");
        }
    }
}

static void mqtt_task(void *arg)
{
    topology_context_t *ctx = (topology_context_t *)arg;
    topology_telemetry_t telemetry;

    for (;;) {
        topology_heartbeat(&ctx->mqtt_watch);
        if (xQueueReceive(ctx->telemetry_queue, &telemetry, pdMS_TO_TICKS(500)) != pdTRUE) {
            continue;
        }

        if (app_mqtt_publish_sample != NULL) {
            const esp_err_t err = app_mqtt_publish_sample(&telemetry);
            if (err != ESP_OK) {
                topology_log_async("mqtt publish failed");
            }
        }
    }
}

static void storage_task(void *arg)
{
    topology_context_t *ctx = (topology_context_t *)arg;
    topology_storage_record_t record;

    for (;;) {
        topology_heartbeat(&ctx->storage_watch);
        if (xQueueReceive(ctx->storage_queue, &record, pdMS_TO_TICKS(500)) != pdTRUE) {
            continue;
        }

        if (app_storage_write_record != NULL) {
            const esp_err_t err = app_storage_write_record(&record);
            if (err != ESP_OK) {
                topology_log_async("storage write failed");
            }
        }
    }
}

static void log_task(void *arg)
{
    topology_context_t *ctx = (topology_context_t *)arg;
    topology_log_record_t record;

    for (;;) {
        topology_heartbeat(&ctx->log_watch);
        if (xQueueReceive(ctx->log_queue, &record, pdMS_TO_TICKS(1000)) != pdTRUE) {
            continue;
        }

        if (app_topology_log_line != NULL) {
            app_topology_log_line(record.text);
        } else {
            ESP_LOGW(TAG, "[%lu ms] %s", (unsigned long)record.at_ms, record.text);
        }
    }
}

static bool watch_entry_is_stale(const topology_watch_entry_t *entry, uint32_t now_ms)
{
    return (uint32_t)(now_ms - entry->heartbeat_ms) > entry->stale_after_ms;
}

static void watchdog_task(void *arg)
{
    topology_context_t *ctx = (topology_context_t *)arg;
    topology_watch_entry_t *entries[] = {
        &ctx->acquire_watch,
        &ctx->dsp_watch,
        &ctx->mqtt_watch,
        &ctx->storage_watch,
        &ctx->log_watch,
    };

    (void)esp_task_wdt_add(NULL);

    for (;;) {
        const uint32_t now = topology_now_ms();
        bool fatal_stale_task = false;

        for (size_t i = 0; i < sizeof(entries) / sizeof(entries[0]); ++i) {
            topology_watch_entry_t *entry = entries[i];
            if (!watch_entry_is_stale(entry, now)) {
                continue;
            }

            ESP_LOGW(TAG, "watchdog stale task=%s age=%lu ms limit=%lu ms",
                     entry->name,
                     (unsigned long)(now - entry->heartbeat_ms),
                     (unsigned long)entry->stale_after_ms);
            fatal_stale_task = fatal_stale_task || entry->reset_on_stale;
        }

        ESP_LOGD(TAG,
                 "queue overflow counters raw=%lu telemetry=%lu storage=%lu log=%lu",
                 (unsigned long)ctx->raw_queue_overflows,
                 (unsigned long)ctx->telemetry_queue_overflows,
                 (unsigned long)ctx->storage_queue_overflows,
                 (unsigned long)ctx->log_queue_overflows);

        if (fatal_stale_task) {
            ESP_LOGE(TAG, "real task lockup detected; restarting");
            esp_restart();
        }

        (void)esp_task_wdt_reset();
        vTaskDelay(pdMS_TO_TICKS(TASK_TOPOLOGY_WATCHDOG_PERIOD_MS));
    }
}

static void topology_init_watch_entries(topology_context_t *ctx)
{
    const uint32_t now = topology_now_ms();
    ctx->acquire_watch = (topology_watch_entry_t){
        .name = "acquire",
        .heartbeat_ms = now,
        .stale_after_ms = TASK_TOPOLOGY_ACQUIRE_STALE_MS,
        .reset_on_stale = true,
    };
    ctx->dsp_watch = (topology_watch_entry_t){
        .name = "dsp",
        .heartbeat_ms = now,
        .stale_after_ms = TASK_TOPOLOGY_DSP_STALE_MS,
        .reset_on_stale = true,
    };
    ctx->mqtt_watch = (topology_watch_entry_t){
        .name = "mqtt",
        .heartbeat_ms = now,
        .stale_after_ms = TASK_TOPOLOGY_NETWORK_STALE_MS,
        .reset_on_stale = false,
    };
    ctx->storage_watch = (topology_watch_entry_t){
        .name = "storage",
        .heartbeat_ms = now,
        .stale_after_ms = TASK_TOPOLOGY_STORAGE_STALE_MS,
        .reset_on_stale = true,
    };
    ctx->log_watch = (topology_watch_entry_t){
        .name = "log",
        .heartbeat_ms = now,
        .stale_after_ms = TASK_TOPOLOGY_STORAGE_STALE_MS,
        .reset_on_stale = false,
    };
}

esp_err_t task_topology_start(void)
{
    topology_context_t *ctx = &s_topology;
    if (ctx->raw_queue != NULL) {
        return ESP_ERR_INVALID_STATE;
    }

    topology_init_watch_entries(ctx);

    ctx->raw_queue = xQueueCreate(TASK_TOPOLOGY_QUEUE_DEPTH, sizeof(topology_raw_sample_t));
    ctx->telemetry_queue = xQueueCreate(TASK_TOPOLOGY_QUEUE_DEPTH, sizeof(topology_telemetry_t));
    ctx->storage_queue = xQueueCreate(TASK_TOPOLOGY_QUEUE_DEPTH, sizeof(topology_storage_record_t));
    ctx->log_queue = xQueueCreate(TASK_TOPOLOGY_QUEUE_DEPTH, sizeof(topology_log_record_t));
    if (ctx->raw_queue == NULL || ctx->telemetry_queue == NULL ||
        ctx->storage_queue == NULL || ctx->log_queue == NULL) {
        return ESP_ERR_NO_MEM;
    }

    if (xTaskCreatePinnedToCore(acquire_task, "acquire", TASK_TOPOLOGY_STACK_WORDS, ctx,
                                TASK_TOPOLOGY_ACQUIRE_PRIORITY, &ctx->acquire_task, 1) != pdPASS ||
        xTaskCreatePinnedToCore(dsp_task, "dsp", TASK_TOPOLOGY_STACK_WORDS, ctx,
                                TASK_TOPOLOGY_DSP_PRIORITY, &ctx->dsp_task, 1) != pdPASS ||
        xTaskCreatePinnedToCore(mqtt_task, "mqtt", TASK_TOPOLOGY_STACK_WORDS, ctx,
                                TASK_TOPOLOGY_MQTT_PRIORITY, &ctx->mqtt_task, 0) != pdPASS ||
        xTaskCreatePinnedToCore(storage_task, "storage", TASK_TOPOLOGY_STACK_WORDS, ctx,
                                TASK_TOPOLOGY_STORAGE_PRIORITY, &ctx->storage_task, 0) != pdPASS ||
        xTaskCreatePinnedToCore(log_task, "log", TASK_TOPOLOGY_STACK_WORDS, ctx,
                                TASK_TOPOLOGY_LOG_PRIORITY, &ctx->log_task, 0) != pdPASS ||
        xTaskCreatePinnedToCore(watchdog_task, "watchdog", TASK_TOPOLOGY_STACK_WORDS, ctx,
                                TASK_TOPOLOGY_WATCHDOG_PRIORITY, &ctx->watchdog_task, 0) != pdPASS) {
        return ESP_ERR_NO_MEM;
    }

    ESP_LOGI(TAG,
             "FIRMWARE_TASKS_ISOLATED: acquire=%u ms, queues=%u, priorities acquire=%u dsp=%u mqtt=%u storage=%u watchdog=%u",
             TASK_TOPOLOGY_ACQUIRE_PERIOD_MS, TASK_TOPOLOGY_QUEUE_DEPTH,
             TASK_TOPOLOGY_ACQUIRE_PRIORITY, TASK_TOPOLOGY_DSP_PRIORITY,
             TASK_TOPOLOGY_MQTT_PRIORITY, TASK_TOPOLOGY_STORAGE_PRIORITY,
             TASK_TOPOLOGY_WATCHDOG_PRIORITY);
    ESP_LOGI(TAG,
             "watchdog policy: acquire/dsp/storage stale resets; mqtt latency tolerated up to %u ms",
             TASK_TOPOLOGY_NETWORK_STALE_MS);
    return ESP_OK;
}

uint32_t task_topology_raw_overflows(void)
{
    return s_topology.raw_queue_overflows;
}

uint32_t task_topology_telemetry_overflows(void)
{
    return s_topology.telemetry_queue_overflows;
}

uint32_t task_topology_storage_overflows(void)
{
    return s_topology.storage_queue_overflows;
}

void app_main(void)
{
    ESP_ERROR_CHECK(task_topology_start());
}
