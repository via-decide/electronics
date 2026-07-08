/*
 * ESP32 non-blocking MQTT telemetry output path.
 *
 * validation_id: esp32_mqtt_nonblocking_v1
 * status: MQTT_OUTPUT_NONBLOCKING
 *
 * Telemetry model:
 *   sensor/acquisition code -> bounded queue -> MQTT state machine task
 *   -> publish when connected -> retry with exponential backoff -> drop oldest
 *   when the queue is full or retry budget is exhausted.
 */

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "esp_err.h"
#include "esp_event.h"
#include "esp_log.h"
#include "mqtt_client.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"

#define MQTT_TELEMETRY_QUEUE_DEPTH          128U
#define MQTT_TELEMETRY_TOPIC_BYTES          96U
#define MQTT_TELEMETRY_PAYLOAD_BYTES        256U
#define MQTT_TELEMETRY_TASK_STACK_WORDS     4096U
#define MQTT_TELEMETRY_TASK_PRIORITY        (tskIDLE_PRIORITY + 1)
#define MQTT_TELEMETRY_RETRY_LIMIT          5U
#define MQTT_TELEMETRY_BACKOFF_INITIAL_MS   250U
#define MQTT_TELEMETRY_BACKOFF_MAX_MS       8000U
#define MQTT_TELEMETRY_QUEUE_WAIT_MS        100U

_Static_assert(MQTT_TELEMETRY_QUEUE_DEPTH == 128U,
               "MQTT telemetry queue depth must remain 128");

typedef enum {
    MQTT_TELEMETRY_NET_OFFLINE = 0,
    MQTT_TELEMETRY_NET_RECONNECTING,
    MQTT_TELEMETRY_NET_CONNECTED,
} mqtt_telemetry_network_state_t;

typedef struct {
    uint32_t sequence;
    uint32_t captured_at_ms;
    uint8_t qos;
    bool retain;
    char topic[MQTT_TELEMETRY_TOPIC_BYTES];
    char payload[MQTT_TELEMETRY_PAYLOAD_BYTES];
} mqtt_telemetry_packet_t;

typedef struct {
    uint32_t queue_depth;
    uint32_t dropped_count;
    uint32_t published_count;
    uint32_t publish_fail_count;
    uint32_t reconnect_count;
    uint32_t retry_count;
    mqtt_telemetry_network_state_t network_state;
} mqtt_telemetry_metrics_t;

typedef struct {
    QueueHandle_t queue;
    TaskHandle_t task;
    esp_mqtt_client_handle_t client;
    volatile uint32_t dropped_count;
    volatile uint32_t published_count;
    volatile uint32_t publish_fail_count;
    volatile uint32_t reconnect_count;
    volatile uint32_t retry_count;
    volatile mqtt_telemetry_network_state_t network_state;
} mqtt_telemetry_context_t;

static const char *TAG = "mqtt_telemetry";
static mqtt_telemetry_context_t s_mqtt_telemetry;

static uint32_t mqtt_telemetry_now_ms(void)
{
    return (uint32_t)(xTaskGetTickCount() * portTICK_PERIOD_MS);
}

static uint32_t mqtt_telemetry_next_backoff_ms(uint32_t attempt)
{
    uint32_t delay_ms = MQTT_TELEMETRY_BACKOFF_INITIAL_MS;
    for (uint32_t i = 0; i < attempt; ++i) {
        if (delay_ms >= MQTT_TELEMETRY_BACKOFF_MAX_MS / 2U) {
            return MQTT_TELEMETRY_BACKOFF_MAX_MS;
        }
        delay_ms *= 2U;
    }
    return delay_ms > MQTT_TELEMETRY_BACKOFF_MAX_MS ? MQTT_TELEMETRY_BACKOFF_MAX_MS : delay_ms;
}

static bool mqtt_telemetry_drop_oldest_and_send(QueueHandle_t queue,
                                                const mqtt_telemetry_packet_t *packet)
{
    mqtt_telemetry_packet_t discarded;
    if (xQueueReceive(queue, &discarded, 0) == pdTRUE) {
        ++s_mqtt_telemetry.dropped_count;
    }
    if (xQueueSend(queue, packet, 0) == pdTRUE) {
        return true;
    }
    ++s_mqtt_telemetry.dropped_count;
    return false;
}

esp_err_t mqtt_telemetry_enqueue(const mqtt_telemetry_packet_t *packet)
{
    if (packet == NULL || s_mqtt_telemetry.queue == NULL) {
        return ESP_ERR_INVALID_STATE;
    }

    if (xQueueSend(s_mqtt_telemetry.queue, packet, 0) == pdTRUE) {
        return ESP_OK;
    }

    return mqtt_telemetry_drop_oldest_and_send(s_mqtt_telemetry.queue, packet)
               ? ESP_OK
               : ESP_FAIL;
}

esp_err_t mqtt_telemetry_enqueue_json(const char *topic, const char *json_payload,
                                      uint32_t sequence)
{
    if (topic == NULL || json_payload == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    mqtt_telemetry_packet_t packet = {
        .sequence = sequence,
        .captured_at_ms = mqtt_telemetry_now_ms(),
        .qos = 1,
        .retain = false,
    };
    (void)snprintf(packet.topic, sizeof(packet.topic), "%s", topic);
    (void)snprintf(packet.payload, sizeof(packet.payload), "%s", json_payload);
    return mqtt_telemetry_enqueue(&packet);
}

/*
 * Compatibility shim for task_topology.c. The topology passes a compact telemetry
 * record with sequence, timestamp, and filtered value; this implementation only
 * enqueues JSON and never performs network I/O in the caller's task.
 */
typedef struct {
    uint32_t sequence;
    uint32_t processed_at_ms;
    int32_t filtered_value;
} mqtt_telemetry_topology_record_t;

esp_err_t app_mqtt_publish_sample(const void *telemetry_record)
{
    if (telemetry_record == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    const mqtt_telemetry_topology_record_t *record =
        (const mqtt_telemetry_topology_record_t *)telemetry_record;
    char payload[MQTT_TELEMETRY_PAYLOAD_BYTES];
    (void)snprintf(payload, sizeof(payload),
                   "{\"sequence\":%lu,\"processed_at_ms\":%lu,\"value\":%ld}",
                   (unsigned long)record->sequence,
                   (unsigned long)record->processed_at_ms,
                   (long)record->filtered_value);
    return mqtt_telemetry_enqueue_json("device/telemetry", payload, record->sequence);
}

static bool mqtt_telemetry_publish_once(const mqtt_telemetry_packet_t *packet)
{
    if (s_mqtt_telemetry.network_state != MQTT_TELEMETRY_NET_CONNECTED ||
        s_mqtt_telemetry.client == NULL) {
        return false;
    }

    const int message_id = esp_mqtt_client_enqueue(s_mqtt_telemetry.client,
                                                   packet->topic,
                                                   packet->payload,
                                                   0,
                                                   packet->qos,
                                                   packet->retain,
                                                   true);
    if (message_id < 0) {
        ++s_mqtt_telemetry.publish_fail_count;
        return false;
    }

    ++s_mqtt_telemetry.published_count;
    return true;
}

static void mqtt_telemetry_task(void *arg)
{
    (void)arg;
    mqtt_telemetry_packet_t packet;

    for (;;) {
        if (xQueueReceive(s_mqtt_telemetry.queue, &packet,
                          pdMS_TO_TICKS(MQTT_TELEMETRY_QUEUE_WAIT_MS)) != pdTRUE) {
            continue;
        }

        bool published = false;
        for (uint32_t attempt = 0; attempt <= MQTT_TELEMETRY_RETRY_LIMIT; ++attempt) {
            if (mqtt_telemetry_publish_once(&packet)) {
                published = true;
                break;
            }

            ++s_mqtt_telemetry.retry_count;
            const uint32_t backoff_ms = mqtt_telemetry_next_backoff_ms(attempt);
            vTaskDelay(pdMS_TO_TICKS(backoff_ms));
        }

        if (!published) {
            ++s_mqtt_telemetry.dropped_count;
            ESP_LOGW(TAG, "dropping telemetry sequence=%lu after retry budget",
                     (unsigned long)packet.sequence);
        }
    }
}

static void mqtt_telemetry_event_handler(void *handler_args, esp_event_base_t base,
                                         int32_t event_id, void *event_data)
{
    (void)handler_args;
    (void)base;
    (void)event_data;

    switch ((esp_mqtt_event_id_t)event_id) {
    case MQTT_EVENT_CONNECTED:
        s_mqtt_telemetry.network_state = MQTT_TELEMETRY_NET_CONNECTED;
        ESP_LOGI(TAG, "MQTT connected");
        break;
    case MQTT_EVENT_DISCONNECTED:
        s_mqtt_telemetry.network_state = MQTT_TELEMETRY_NET_RECONNECTING;
        ++s_mqtt_telemetry.reconnect_count;
        ESP_LOGW(TAG, "MQTT disconnected; telemetry remains queued/drop-oldest");
        break;
    case MQTT_EVENT_ERROR:
        s_mqtt_telemetry.network_state = MQTT_TELEMETRY_NET_RECONNECTING;
        ++s_mqtt_telemetry.publish_fail_count;
        ESP_LOGW(TAG, "MQTT error; retry state machine will back off");
        break;
    default:
        break;
    }
}

esp_err_t mqtt_telemetry_start(const char *broker_uri)
{
    if (broker_uri == NULL) {
        return ESP_ERR_INVALID_ARG;
    }
    if (s_mqtt_telemetry.queue != NULL) {
        return ESP_ERR_INVALID_STATE;
    }

    s_mqtt_telemetry.queue = xQueueCreate(MQTT_TELEMETRY_QUEUE_DEPTH,
                                          sizeof(mqtt_telemetry_packet_t));
    if (s_mqtt_telemetry.queue == NULL) {
        return ESP_ERR_NO_MEM;
    }

    s_mqtt_telemetry.network_state = MQTT_TELEMETRY_NET_OFFLINE;

    const esp_mqtt_client_config_t mqtt_cfg = {
        .broker.address.uri = broker_uri,
    };
    s_mqtt_telemetry.client = esp_mqtt_client_init(&mqtt_cfg);
    if (s_mqtt_telemetry.client == NULL) {
        return ESP_ERR_NO_MEM;
    }

    esp_err_t err = esp_mqtt_client_register_event(s_mqtt_telemetry.client,
                                                   ESP_EVENT_ANY_ID,
                                                   mqtt_telemetry_event_handler,
                                                   NULL);
    if (err != ESP_OK) {
        return err;
    }

    if (xTaskCreatePinnedToCore(mqtt_telemetry_task, "mqtt_telemetry",
                                MQTT_TELEMETRY_TASK_STACK_WORDS, NULL,
                                MQTT_TELEMETRY_TASK_PRIORITY,
                                &s_mqtt_telemetry.task, 0) != pdPASS) {
        return ESP_ERR_NO_MEM;
    }

    err = esp_mqtt_client_start(s_mqtt_telemetry.client);
    if (err != ESP_OK) {
        return err;
    }

    ESP_LOGI(TAG,
             "MQTT_OUTPUT_NONBLOCKING: queue=%u retry_limit=%u backoff=%u..%u ms policy=drop_oldest",
             MQTT_TELEMETRY_QUEUE_DEPTH, MQTT_TELEMETRY_RETRY_LIMIT,
             MQTT_TELEMETRY_BACKOFF_INITIAL_MS, MQTT_TELEMETRY_BACKOFF_MAX_MS);
    return ESP_OK;
}

uint32_t mqtt_telemetry_queue_capacity(void)
{
    return MQTT_TELEMETRY_QUEUE_DEPTH;
}

uint32_t mqtt_telemetry_queue_depth(void)
{
    if (s_mqtt_telemetry.queue == NULL) {
        return 0;
    }
    return (uint32_t)uxQueueMessagesWaiting(s_mqtt_telemetry.queue);
}

void mqtt_telemetry_get_metrics(mqtt_telemetry_metrics_t *out_metrics)
{
    if (out_metrics == NULL) {
        return;
    }

    *out_metrics = (mqtt_telemetry_metrics_t){
        .queue_depth = mqtt_telemetry_queue_depth(),
        .dropped_count = s_mqtt_telemetry.dropped_count,
        .published_count = s_mqtt_telemetry.published_count,
        .publish_fail_count = s_mqtt_telemetry.publish_fail_count,
        .reconnect_count = s_mqtt_telemetry.reconnect_count,
        .retry_count = s_mqtt_telemetry.retry_count,
        .network_state = s_mqtt_telemetry.network_state,
    };
}

uint32_t mqtt_telemetry_drop_count(void)
{
    return s_mqtt_telemetry.dropped_count;
}

uint32_t mqtt_telemetry_reconnect_count(void)
{
    return s_mqtt_telemetry.reconnect_count;
}
