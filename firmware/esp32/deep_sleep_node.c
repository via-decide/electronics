/*
 * ESP32 deep-sleep sensor-node cycle.
 *
 * validation_id: esp32_deep_sleep_sensor_v1
 * status: LOW_POWER_CYCLE_LOCKED
 *
 * Cycle:
 *   wake -> log wake reason -> power sensor -> wait warm-up -> capture sample
 *   -> attempt telemetry within a bounded Wi-Fi/network window -> shut down
 *   peripherals -> arm timer wake -> enter deep sleep unconditionally.
 */

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#include "esp_err.h"
#include "esp_log.h"
#include "esp_sleep.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define DEEP_SLEEP_NODE_SLEEP_INTERVAL_US     (300ULL * 1000000ULL)
#define DEEP_SLEEP_NODE_SENSOR_WARMUP_MS      500U
#define DEEP_SLEEP_NODE_WIFI_TIMEOUT_MS       8000U
#define DEEP_SLEEP_NODE_TELEMETRY_POLL_MS     100U
#define DEEP_SLEEP_NODE_ACTIVE_CURRENT_MA     80.0f
#define DEEP_SLEEP_NODE_SLEEP_CURRENT_MA      0.015f
#define DEEP_SLEEP_NODE_PAYLOAD_BYTES         160U

_Static_assert(DEEP_SLEEP_NODE_WIFI_TIMEOUT_MS > DEEP_SLEEP_NODE_TELEMETRY_POLL_MS,
               "network timeout must allow at least one telemetry poll");

typedef struct {
    esp_sleep_wakeup_cause_t wake_reason;
    uint32_t active_ms;
    uint32_t sensor_warmup_ms;
    uint32_t network_budget_ms;
    uint64_t sleep_interval_us;
    int32_t raw_measurement;
    bool measurement_valid;
    bool telemetry_attempted;
    bool telemetry_sent;
    float average_current_ma;
} deep_sleep_node_diagnostics_t;

static const char *TAG = "deep_sleep_node";
static deep_sleep_node_diagnostics_t s_deep_sleep_diag;

/* Optional board/application hooks. Defaults still guarantee return to deep sleep. */
void app_deep_sleep_sensor_power(bool enabled) __attribute__((weak));
esp_err_t app_deep_sleep_sensor_read(int32_t *out_raw) __attribute__((weak));
esp_err_t app_deep_sleep_network_start(void) __attribute__((weak));
bool app_deep_sleep_network_ready(void) __attribute__((weak));
esp_err_t app_deep_sleep_publish_payload(const char *payload) __attribute__((weak));
void app_deep_sleep_network_stop(void) __attribute__((weak));
void app_deep_sleep_before_sleep(void) __attribute__((weak));

static uint32_t deep_sleep_node_now_ms(void)
{
    return (uint32_t)(esp_timer_get_time() / 1000ULL);
}

static const char *deep_sleep_node_wake_reason_name(esp_sleep_wakeup_cause_t reason)
{
    switch (reason) {
    case ESP_SLEEP_WAKEUP_EXT0:
        return "ext0";
    case ESP_SLEEP_WAKEUP_EXT1:
        return "ext1";
    case ESP_SLEEP_WAKEUP_TIMER:
        return "timer";
    case ESP_SLEEP_WAKEUP_TOUCHPAD:
        return "touchpad";
    case ESP_SLEEP_WAKEUP_ULP:
        return "ulp";
    case ESP_SLEEP_WAKEUP_GPIO:
        return "gpio";
    case ESP_SLEEP_WAKEUP_UART:
        return "uart";
    case ESP_SLEEP_WAKEUP_WIFI:
        return "wifi";
    case ESP_SLEEP_WAKEUP_COCPU:
        return "cocpu";
    case ESP_SLEEP_WAKEUP_UNDEFINED:
    default:
        return "undefined";
    }
}

static float deep_sleep_node_average_current_ma(uint32_t active_ms, uint64_t sleep_us)
{
    const float active_s = (float)active_ms / 1000.0f;
    const float sleep_s = (float)sleep_us / 1000000.0f;
    const float total_s = active_s + sleep_s;
    if (total_s <= 0.0f) {
        return DEEP_SLEEP_NODE_ACTIVE_CURRENT_MA;
    }
    return ((DEEP_SLEEP_NODE_ACTIVE_CURRENT_MA * active_s) +
            (DEEP_SLEEP_NODE_SLEEP_CURRENT_MA * sleep_s)) / total_s;
}

static esp_err_t deep_sleep_node_capture_measurement(int32_t *out_raw)
{
    if (out_raw == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    if (app_deep_sleep_sensor_power != NULL) {
        app_deep_sleep_sensor_power(true);
    }
    vTaskDelay(pdMS_TO_TICKS(DEEP_SLEEP_NODE_SENSOR_WARMUP_MS));

    esp_err_t err = ESP_ERR_NOT_SUPPORTED;
    if (app_deep_sleep_sensor_read != NULL) {
        err = app_deep_sleep_sensor_read(out_raw);
    } else {
        *out_raw = 0;
        err = ESP_OK;
    }

    if (app_deep_sleep_sensor_power != NULL) {
        app_deep_sleep_sensor_power(false);
    }
    return err;
}

static bool deep_sleep_node_wait_network_ready(uint32_t timeout_ms)
{
    const uint32_t start_ms = deep_sleep_node_now_ms();
    do {
        if (app_deep_sleep_network_ready != NULL && app_deep_sleep_network_ready()) {
            return true;
        }
        vTaskDelay(pdMS_TO_TICKS(DEEP_SLEEP_NODE_TELEMETRY_POLL_MS));
    } while ((uint32_t)(deep_sleep_node_now_ms() - start_ms) < timeout_ms);

    return false;
}

static bool deep_sleep_node_attempt_telemetry(int32_t raw_measurement, uint32_t active_ms)
{
    s_deep_sleep_diag.telemetry_attempted = true;

    if (app_deep_sleep_network_start != NULL) {
        (void)app_deep_sleep_network_start();
    }

    bool sent = false;
    if (deep_sleep_node_wait_network_ready(DEEP_SLEEP_NODE_WIFI_TIMEOUT_MS)) {
        char payload[DEEP_SLEEP_NODE_PAYLOAD_BYTES];
        (void)snprintf(payload, sizeof(payload),
                       "{\"raw\":%ld,\"wake\":\"%s\",\"active_ms\":%lu}",
                       (long)raw_measurement,
                       deep_sleep_node_wake_reason_name(s_deep_sleep_diag.wake_reason),
                       (unsigned long)active_ms);
        if (app_deep_sleep_publish_payload != NULL) {
            sent = app_deep_sleep_publish_payload(payload) == ESP_OK;
        }
    } else {
        ESP_LOGW(TAG, "network not ready within %u ms; skipping telemetry and sleeping",
                 DEEP_SLEEP_NODE_WIFI_TIMEOUT_MS);
    }

    if (app_deep_sleep_network_stop != NULL) {
        app_deep_sleep_network_stop();
    }
    return sent;
}

static void deep_sleep_node_enter_sleep(uint64_t sleep_interval_us)
{
    if (app_deep_sleep_before_sleep != NULL) {
        app_deep_sleep_before_sleep();
    }

    const esp_err_t err = esp_sleep_enable_timer_wakeup(sleep_interval_us);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "timer wake configuration failed: %s; entering deep sleep anyway",
                 esp_err_to_name(err));
    }
    ESP_LOGI(TAG, "entering deep sleep for %llu us", (unsigned long long)sleep_interval_us);
    esp_deep_sleep_start();
}

void deep_sleep_node_get_diagnostics(deep_sleep_node_diagnostics_t *out_diagnostics)
{
    if (out_diagnostics == NULL) {
        return;
    }
    *out_diagnostics = s_deep_sleep_diag;
}

void deep_sleep_node_log_diagnostics(void)
{
    ESP_LOGI(TAG,
             "LOW_POWER_CYCLE_LOCKED: wake=%s active_ms=%lu sleep_s=%llu measurement_valid=%s telemetry_attempted=%s telemetry_sent=%s avg_current=%.3f mA",
             deep_sleep_node_wake_reason_name(s_deep_sleep_diag.wake_reason),
             (unsigned long)s_deep_sleep_diag.active_ms,
             (unsigned long long)(s_deep_sleep_diag.sleep_interval_us / 1000000ULL),
             s_deep_sleep_diag.measurement_valid ? "yes" : "no",
             s_deep_sleep_diag.telemetry_attempted ? "yes" : "no",
             s_deep_sleep_diag.telemetry_sent ? "yes" : "no",
             s_deep_sleep_diag.average_current_ma);
}

void deep_sleep_node_run_cycle(void)
{
    const uint32_t cycle_start_ms = deep_sleep_node_now_ms();
    s_deep_sleep_diag = (deep_sleep_node_diagnostics_t){
        .wake_reason = esp_sleep_get_wakeup_cause(),
        .sensor_warmup_ms = DEEP_SLEEP_NODE_SENSOR_WARMUP_MS,
        .network_budget_ms = DEEP_SLEEP_NODE_WIFI_TIMEOUT_MS,
        .sleep_interval_us = DEEP_SLEEP_NODE_SLEEP_INTERVAL_US,
        .raw_measurement = 0,
    };

    ESP_LOGI(TAG, "LOW_POWER_CYCLE_LOCKED: wake reason=%s sleep_interval=%llu us warmup=%u ms wifi_timeout=%u ms",
             deep_sleep_node_wake_reason_name(s_deep_sleep_diag.wake_reason),
             (unsigned long long)DEEP_SLEEP_NODE_SLEEP_INTERVAL_US,
             DEEP_SLEEP_NODE_SENSOR_WARMUP_MS, DEEP_SLEEP_NODE_WIFI_TIMEOUT_MS);

    esp_err_t err = deep_sleep_node_capture_measurement(&s_deep_sleep_diag.raw_measurement);
    s_deep_sleep_diag.measurement_valid = err == ESP_OK;
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "measurement failed: %s; telemetry will be skipped", esp_err_to_name(err));
    } else {
        const uint32_t before_network_ms = deep_sleep_node_now_ms() - cycle_start_ms;
        s_deep_sleep_diag.telemetry_sent =
            deep_sleep_node_attempt_telemetry(s_deep_sleep_diag.raw_measurement, before_network_ms);
    }

    s_deep_sleep_diag.active_ms = deep_sleep_node_now_ms() - cycle_start_ms;
    s_deep_sleep_diag.average_current_ma =
        deep_sleep_node_average_current_ma(s_deep_sleep_diag.active_ms,
                                           s_deep_sleep_diag.sleep_interval_us);
    deep_sleep_node_log_diagnostics();
    deep_sleep_node_enter_sleep(s_deep_sleep_diag.sleep_interval_us);
}

void __attribute__((weak)) app_main(void)
{
    deep_sleep_node_run_cycle();
}
