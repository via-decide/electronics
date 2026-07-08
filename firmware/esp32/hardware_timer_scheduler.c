/*
 * ESP32 hardware-timer periodic scheduler.
 *
 * validation_id: esp32_hardware_timer_scheduler_v1
 * status: PERIODIC_TIMING_HARDWARE_OWNED
 *
 * Timing model:
 *   GPTimer alarm owns the period. The ISR only timestamps and queues a small
 *   event. A worker task performs control/sampling/state-update work outside ISR
 *   context and missed deadlines are counted when the event queue overflows.
 */

#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#include "driver/gptimer.h"
#include "esp_attr.h"
#include "esp_err.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"

#define HW_TIMER_SCHED_PERIOD_MS          10U
#define HW_TIMER_SCHED_RESOLUTION_HZ      1000000ULL
#define HW_TIMER_SCHED_ALARM_TICKS        ((HW_TIMER_SCHED_RESOLUTION_HZ / 1000ULL) * HW_TIMER_SCHED_PERIOD_MS)
#define HW_TIMER_SCHED_QUEUE_DEPTH        16U
#define HW_TIMER_SCHED_TASK_STACK_WORDS   4096U
#define HW_TIMER_SCHED_TASK_PRIORITY      (tskIDLE_PRIORITY + 4)

_Static_assert(HW_TIMER_SCHED_PERIOD_MS == 10U, "default hardware timer period must be 10 ms");
_Static_assert(HW_TIMER_SCHED_ALARM_TICKS > 0ULL, "hardware timer alarm period must be nonzero");

typedef struct {
    uint32_t sequence;
    uint64_t alarm_count;
    uint64_t expected_alarm_count;
} hw_timer_sched_event_t;

typedef struct {
    uint32_t period_ms;
    uint32_t dispatched_events;
    uint32_t missed_deadlines;
    uint32_t worker_errors;
    uint32_t last_sequence;
    bool running;
} hw_timer_sched_metrics_t;

typedef struct {
    gptimer_handle_t timer;
    QueueHandle_t event_queue;
    TaskHandle_t worker_task;
    volatile uint32_t isr_sequence;
    volatile uint32_t missed_deadlines;
    volatile bool running;
    hw_timer_sched_metrics_t metrics;
} hw_timer_sched_context_t;

static const char *TAG = "hardware_timer_scheduler";
static hw_timer_sched_context_t s_hw_timer_sched;

/* Optional application hook. Runs in worker task context, never in the timer ISR. */
esp_err_t app_hardware_timer_periodic_event(uint32_t sequence, uint64_t alarm_count) __attribute__((weak));

static bool IRAM_ATTR hw_timer_sched_on_alarm(gptimer_handle_t timer,
                                              const gptimer_alarm_event_data_t *edata,
                                              void *user_ctx)
{
    (void)timer;
    hw_timer_sched_context_t *ctx = (hw_timer_sched_context_t *)user_ctx;
    const uint32_t sequence = ctx->isr_sequence++;
    const hw_timer_sched_event_t event = {
        .sequence = sequence,
        .alarm_count = edata->count_value,
        .expected_alarm_count = edata->alarm_value,
    };

    BaseType_t must_yield = pdFALSE;
    if (xQueueSendFromISR(ctx->event_queue, &event, &must_yield) != pdTRUE) {
        ++ctx->missed_deadlines;
    }
    return must_yield == pdTRUE;
}

static void hw_timer_sched_worker(void *arg)
{
    hw_timer_sched_context_t *ctx = (hw_timer_sched_context_t *)arg;
    hw_timer_sched_event_t event;

    for (;;) {
        if (xQueueReceive(ctx->event_queue, &event, portMAX_DELAY) != pdTRUE) {
            continue;
        }

        if (app_hardware_timer_periodic_event != NULL) {
            const esp_err_t err = app_hardware_timer_periodic_event(event.sequence,
                                                                    event.alarm_count);
            if (err != ESP_OK) {
                ++ctx->metrics.worker_errors;
            }
        }

        ctx->metrics.dispatched_events++;
        ctx->metrics.last_sequence = event.sequence;
        ctx->metrics.missed_deadlines = ctx->missed_deadlines;
    }
}

esp_err_t hardware_timer_scheduler_start(void)
{
    hw_timer_sched_context_t *ctx = &s_hw_timer_sched;
    if (ctx->running) {
        return ESP_ERR_INVALID_STATE;
    }

    ctx->event_queue = xQueueCreate(HW_TIMER_SCHED_QUEUE_DEPTH, sizeof(hw_timer_sched_event_t));
    if (ctx->event_queue == NULL) {
        return ESP_ERR_NO_MEM;
    }

    const gptimer_config_t timer_config = {
        .clk_src = GPTIMER_CLK_SRC_DEFAULT,
        .direction = GPTIMER_COUNT_UP,
        .resolution_hz = HW_TIMER_SCHED_RESOLUTION_HZ,
    };
    esp_err_t err = gptimer_new_timer(&timer_config, &ctx->timer);
    if (err != ESP_OK) {
        return err;
    }

    const gptimer_event_callbacks_t callbacks = {
        .on_alarm = hw_timer_sched_on_alarm,
    };
    err = gptimer_register_event_callbacks(ctx->timer, &callbacks, ctx);
    if (err != ESP_OK) {
        return err;
    }

    const gptimer_alarm_config_t alarm_config = {
        .alarm_count = HW_TIMER_SCHED_ALARM_TICKS,
        .reload_count = 0,
        .flags.auto_reload_on_alarm = true,
    };
    err = gptimer_set_alarm_action(ctx->timer, &alarm_config);
    if (err != ESP_OK) {
        return err;
    }

    if (xTaskCreatePinnedToCore(hw_timer_sched_worker, "hw_timer_sched",
                                HW_TIMER_SCHED_TASK_STACK_WORDS, ctx,
                                HW_TIMER_SCHED_TASK_PRIORITY,
                                &ctx->worker_task, 1) != pdPASS) {
        return ESP_ERR_NO_MEM;
    }

    err = gptimer_enable(ctx->timer);
    if (err == ESP_OK) {
        err = gptimer_start(ctx->timer);
    }
    if (err != ESP_OK) {
        return err;
    }

    ctx->running = true;
    ctx->metrics = (hw_timer_sched_metrics_t){
        .period_ms = HW_TIMER_SCHED_PERIOD_MS,
        .running = true,
    };
    ESP_LOGI(TAG,
             "PERIODIC_TIMING_HARDWARE_OWNED: period=%u ms queue=%u isr=minimal worker=decoupled",
             HW_TIMER_SCHED_PERIOD_MS, HW_TIMER_SCHED_QUEUE_DEPTH);
    return ESP_OK;
}

esp_err_t hardware_timer_scheduler_stop(void)
{
    hw_timer_sched_context_t *ctx = &s_hw_timer_sched;
    if (!ctx->running) {
        return ESP_ERR_INVALID_STATE;
    }

    esp_err_t err = gptimer_stop(ctx->timer);
    if (err == ESP_OK) {
        err = gptimer_disable(ctx->timer);
    }
    if (err == ESP_OK) {
        err = gptimer_del_timer(ctx->timer);
    }
    ctx->timer = NULL;
    ctx->running = false;
    ctx->metrics.running = false;

    if (ctx->worker_task != NULL) {
        vTaskDelete(ctx->worker_task);
        ctx->worker_task = NULL;
    }
    if (ctx->event_queue != NULL) {
        vQueueDelete(ctx->event_queue);
        ctx->event_queue = NULL;
    }
    return err;
}

void hardware_timer_scheduler_get_metrics(hw_timer_sched_metrics_t *out_metrics)
{
    if (out_metrics == NULL) {
        return;
    }
    s_hw_timer_sched.metrics.missed_deadlines = s_hw_timer_sched.missed_deadlines;
    s_hw_timer_sched.metrics.running = s_hw_timer_sched.running;
    *out_metrics = s_hw_timer_sched.metrics;
}

void hardware_timer_scheduler_log_metrics(void)
{
    hw_timer_sched_metrics_t metrics;
    hardware_timer_scheduler_get_metrics(&metrics);
    ESP_LOGI(TAG,
             "PERIODIC_TIMING_HARDWARE_OWNED: period_ms=%lu dispatched=%lu missed_deadlines=%lu worker_errors=%lu last_sequence=%lu running=%s",
             (unsigned long)metrics.period_ms,
             (unsigned long)metrics.dispatched_events,
             (unsigned long)metrics.missed_deadlines,
             (unsigned long)metrics.worker_errors,
             (unsigned long)metrics.last_sequence,
             metrics.running ? "yes" : "no");
}
