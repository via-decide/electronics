/*
 * ESP32 brownout and power-integrity diagnostics.
 *
 * validation_id: esp32_brownout_diagnostics_v1
 * status: POWER_FAULTS_OBSERVABLE
 *
 * Boot flow:
 *   read reset reason -> classify brownout/watchdog/panic/software reset ->
 *   persist boot/fault counters in NVS -> log diagnostics -> optionally publish
 *   power-fault history over MQTT telemetry.
 */

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "esp_err.h"
#include "esp_log.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "nvs.h"
#include "nvs_flash.h"

#define POWER_DIAG_NAMESPACE              "power_diag"
#define POWER_DIAG_KEY_BOOT_COUNT         "boot_count"
#define POWER_DIAG_KEY_BROWNOUT_COUNT     "brownouts"
#define POWER_DIAG_KEY_WDT_COUNT          "wdt_resets"
#define POWER_DIAG_KEY_PANIC_COUNT        "panic_resets"
#define POWER_DIAG_KEY_WIFI_STRESS_COUNT  "wifi_stress"
#define POWER_DIAG_KEY_LAST_RESET         "last_reset"
#define POWER_DIAG_MQTT_TOPIC             "device/power"
#define POWER_DIAG_JSON_BYTES             256U

typedef enum {
    POWER_DIAG_RESET_OTHER = 0,
    POWER_DIAG_RESET_BROWNOUT,
    POWER_DIAG_RESET_WATCHDOG,
    POWER_DIAG_RESET_PANIC,
    POWER_DIAG_RESET_SOFTWARE,
    POWER_DIAG_RESET_POWER_ON,
} power_diag_reset_class_t;

typedef struct {
    uint32_t boot_count;
    uint32_t brownout_count;
    uint32_t watchdog_count;
    uint32_t panic_count;
    uint32_t wifi_stress_count;
    esp_reset_reason_t last_reset_reason;
    power_diag_reset_class_t last_reset_class;
    uint32_t last_wifi_stress_ms;
    bool nvs_loaded;
} power_diag_snapshot_t;

static const char *TAG = "power_diagnostics";
static power_diag_snapshot_t s_power_diag;

/* Optional MQTT telemetry hook from mqtt_telemetry.c; serial logging always remains available. */
esp_err_t mqtt_telemetry_enqueue_json(const char *topic, const char *json_payload,
                                      uint32_t sequence) __attribute__((weak));

static uint32_t power_diag_now_ms(void)
{
    return (uint32_t)(esp_timer_get_time() / 1000ULL);
}

static const char *power_diag_reset_reason_name(esp_reset_reason_t reason)
{
    switch (reason) {
    case ESP_RST_POWERON:
        return "power_on";
    case ESP_RST_EXT:
        return "external";
    case ESP_RST_SW:
        return "software";
    case ESP_RST_PANIC:
        return "panic";
    case ESP_RST_INT_WDT:
        return "interrupt_wdt";
    case ESP_RST_TASK_WDT:
        return "task_wdt";
    case ESP_RST_WDT:
        return "other_wdt";
    case ESP_RST_DEEPSLEEP:
        return "deep_sleep";
    case ESP_RST_BROWNOUT:
        return "brownout";
    case ESP_RST_SDIO:
        return "sdio";
    case ESP_RST_UNKNOWN:
    default:
        return "unknown";
    }
}

static power_diag_reset_class_t power_diag_classify_reset(esp_reset_reason_t reason)
{
    switch (reason) {
    case ESP_RST_BROWNOUT:
        return POWER_DIAG_RESET_BROWNOUT;
    case ESP_RST_INT_WDT:
    case ESP_RST_TASK_WDT:
    case ESP_RST_WDT:
        return POWER_DIAG_RESET_WATCHDOG;
    case ESP_RST_PANIC:
        return POWER_DIAG_RESET_PANIC;
    case ESP_RST_SW:
        return POWER_DIAG_RESET_SOFTWARE;
    case ESP_RST_POWERON:
        return POWER_DIAG_RESET_POWER_ON;
    default:
        return POWER_DIAG_RESET_OTHER;
    }
}

static const char *power_diag_reset_class_name(power_diag_reset_class_t reset_class)
{
    switch (reset_class) {
    case POWER_DIAG_RESET_BROWNOUT:
        return "brownout";
    case POWER_DIAG_RESET_WATCHDOG:
        return "watchdog";
    case POWER_DIAG_RESET_PANIC:
        return "panic";
    case POWER_DIAG_RESET_SOFTWARE:
        return "software";
    case POWER_DIAG_RESET_POWER_ON:
        return "power_on";
    case POWER_DIAG_RESET_OTHER:
    default:
        return "other";
    }
}

static esp_err_t power_diag_nvs_open(nvs_open_mode_t mode, nvs_handle_t *out_handle)
{
    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_LOGW(TAG, "NVS requires erase/reinit: %s", esp_err_to_name(err));
        err = nvs_flash_erase();
        if (err != ESP_OK) {
            return err;
        }
        err = nvs_flash_init();
    }
    if (err != ESP_OK) {
        return err;
    }

    return nvs_open(POWER_DIAG_NAMESPACE, mode, out_handle);
}

static uint32_t power_diag_get_u32(nvs_handle_t handle, const char *key)
{
    uint32_t value = 0;
    if (nvs_get_u32(handle, key, &value) != ESP_OK) {
        return 0;
    }
    return value;
}

static void power_diag_increment_class_counter(power_diag_reset_class_t reset_class)
{
    switch (reset_class) {
    case POWER_DIAG_RESET_BROWNOUT:
        ++s_power_diag.brownout_count;
        break;
    case POWER_DIAG_RESET_WATCHDOG:
        ++s_power_diag.watchdog_count;
        break;
    case POWER_DIAG_RESET_PANIC:
        ++s_power_diag.panic_count;
        break;
    default:
        break;
    }
}

static esp_err_t power_diag_persist(nvs_handle_t handle)
{
    esp_err_t err = nvs_set_u32(handle, POWER_DIAG_KEY_BOOT_COUNT, s_power_diag.boot_count);
    if (err == ESP_OK) {
        err = nvs_set_u32(handle, POWER_DIAG_KEY_BROWNOUT_COUNT, s_power_diag.brownout_count);
    }
    if (err == ESP_OK) {
        err = nvs_set_u32(handle, POWER_DIAG_KEY_WDT_COUNT, s_power_diag.watchdog_count);
    }
    if (err == ESP_OK) {
        err = nvs_set_u32(handle, POWER_DIAG_KEY_PANIC_COUNT, s_power_diag.panic_count);
    }
    if (err == ESP_OK) {
        err = nvs_set_u32(handle, POWER_DIAG_KEY_WIFI_STRESS_COUNT, s_power_diag.wifi_stress_count);
    }
    if (err == ESP_OK) {
        err = nvs_set_u32(handle, POWER_DIAG_KEY_LAST_RESET,
                          (uint32_t)s_power_diag.last_reset_reason);
    }
    if (err == ESP_OK) {
        err = nvs_commit(handle);
    }
    return err;
}

esp_err_t power_diagnostics_boot_record(void)
{
    const esp_reset_reason_t reset_reason = esp_reset_reason();
    const power_diag_reset_class_t reset_class = power_diag_classify_reset(reset_reason);

    nvs_handle_t handle;
    esp_err_t err = power_diag_nvs_open(NVS_READWRITE, &handle);
    if (err != ESP_OK) {
        s_power_diag = (power_diag_snapshot_t){
            .boot_count = 1,
            .last_reset_reason = reset_reason,
            .last_reset_class = reset_class,
            .nvs_loaded = false,
        };
        power_diag_increment_class_counter(reset_class);
        ESP_LOGW(TAG, "POWER_FAULTS_OBSERVABLE: reset=%s class=%s boot_count=volatile nvs_error=%s",
                 power_diag_reset_reason_name(reset_reason),
                 power_diag_reset_class_name(reset_class), esp_err_to_name(err));
        return err;
    }

    s_power_diag.boot_count = power_diag_get_u32(handle, POWER_DIAG_KEY_BOOT_COUNT) + 1U;
    s_power_diag.brownout_count = power_diag_get_u32(handle, POWER_DIAG_KEY_BROWNOUT_COUNT);
    s_power_diag.watchdog_count = power_diag_get_u32(handle, POWER_DIAG_KEY_WDT_COUNT);
    s_power_diag.panic_count = power_diag_get_u32(handle, POWER_DIAG_KEY_PANIC_COUNT);
    s_power_diag.wifi_stress_count = power_diag_get_u32(handle, POWER_DIAG_KEY_WIFI_STRESS_COUNT);
    s_power_diag.last_reset_reason = reset_reason;
    s_power_diag.last_reset_class = reset_class;
    s_power_diag.nvs_loaded = true;
    power_diag_increment_class_counter(reset_class);

    err = power_diag_persist(handle);
    nvs_close(handle);

    ESP_LOGI(TAG,
             "POWER_FAULTS_OBSERVABLE: reset=%s class=%s boot_count=%lu brownouts=%lu watchdogs=%lu panics=%lu wifi_stress=%lu",
             power_diag_reset_reason_name(reset_reason), power_diag_reset_class_name(reset_class),
             (unsigned long)s_power_diag.boot_count,
             (unsigned long)s_power_diag.brownout_count,
             (unsigned long)s_power_diag.watchdog_count,
             (unsigned long)s_power_diag.panic_count,
             (unsigned long)s_power_diag.wifi_stress_count);
    if (reset_class == POWER_DIAG_RESET_BROWNOUT) {
        ESP_LOGE(TAG, "brownout reset detected; inspect regulator headroom, USB cable resistance, decoupling, and Wi-Fi TX current bursts");
    }
    return err;
}

esp_err_t power_diagnostics_note_wifi_stress_event(const char *reason)
{
    ++s_power_diag.wifi_stress_count;
    s_power_diag.last_wifi_stress_ms = power_diag_now_ms();

    nvs_handle_t handle;
    esp_err_t err = power_diag_nvs_open(NVS_READWRITE, &handle);
    if (err == ESP_OK) {
        err = nvs_set_u32(handle, POWER_DIAG_KEY_WIFI_STRESS_COUNT,
                          s_power_diag.wifi_stress_count);
        if (err == ESP_OK) {
            err = nvs_commit(handle);
        }
        nvs_close(handle);
    }

    ESP_LOGW(TAG, "Wi-Fi/radio current stress event count=%lu at=%lu ms reason=%s",
             (unsigned long)s_power_diag.wifi_stress_count,
             (unsigned long)s_power_diag.last_wifi_stress_ms,
             reason != NULL ? reason : "unspecified");
    return err;
}

void power_diagnostics_get_snapshot(power_diag_snapshot_t *out_snapshot)
{
    if (out_snapshot == NULL) {
        return;
    }
    *out_snapshot = s_power_diag;
}

esp_err_t power_diagnostics_report_mqtt(void)
{
    char json[POWER_DIAG_JSON_BYTES];
    (void)snprintf(json, sizeof(json),
                   "{\"boot_count\":%lu,\"reset\":\"%s\",\"class\":\"%s\",\"brownouts\":%lu,\"watchdogs\":%lu,\"panics\":%lu,\"wifi_stress\":%lu}",
                   (unsigned long)s_power_diag.boot_count,
                   power_diag_reset_reason_name(s_power_diag.last_reset_reason),
                   power_diag_reset_class_name(s_power_diag.last_reset_class),
                   (unsigned long)s_power_diag.brownout_count,
                   (unsigned long)s_power_diag.watchdog_count,
                   (unsigned long)s_power_diag.panic_count,
                   (unsigned long)s_power_diag.wifi_stress_count);

    ESP_LOGI(TAG, "power diagnostics report: %s", json);
    if (mqtt_telemetry_enqueue_json == NULL) {
        return ESP_ERR_NOT_SUPPORTED;
    }
    return mqtt_telemetry_enqueue_json(POWER_DIAG_MQTT_TOPIC, json, s_power_diag.boot_count);
}

void power_diagnostics_log(void)
{
    ESP_LOGI(TAG,
             "POWER_FAULTS_OBSERVABLE: boot_count=%lu reset=%s class=%s brownouts=%lu watchdogs=%lu panics=%lu wifi_stress=%lu last_wifi_stress_ms=%lu nvs=%s",
             (unsigned long)s_power_diag.boot_count,
             power_diag_reset_reason_name(s_power_diag.last_reset_reason),
             power_diag_reset_class_name(s_power_diag.last_reset_class),
             (unsigned long)s_power_diag.brownout_count,
             (unsigned long)s_power_diag.watchdog_count,
             (unsigned long)s_power_diag.panic_count,
             (unsigned long)s_power_diag.wifi_stress_count,
             (unsigned long)s_power_diag.last_wifi_stress_ms,
             s_power_diag.nvs_loaded ? "ok" : "unavailable");
}
