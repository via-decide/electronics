/*
 * ESP32 rollback-safe OTA manager.
 *
 * validation_id: esp32_ota_rollback_v1
 * status: OTA_ROLLBACK_SAFE
 *
 * OTA model:
 *   active partition (P_A) remains bootable while an update is downloaded to the
 *   inactive OTA partition (P_B). ESP-IDF image verification runs before the new
 *   image is selected for trial boot. On the next boot, core-service health
 *   checks must pass before the app is confirmed valid; otherwise rollback is
 *   requested and the bootloader returns to the previous valid partition.
 */

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "esp_app_desc.h"
#include "esp_err.h"
#include "esp_https_ota.h"
#include "esp_log.h"
#include "esp_ota_ops.h"
#include "esp_partition.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "esp_http_client.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define OTA_MANAGER_CONFIRM_TIMEOUT_MS      30000U
#define OTA_MANAGER_HEALTH_POLL_MS          500U
#define OTA_MANAGER_DIAG_LABEL_BYTES        17U
#define OTA_MANAGER_DIAG_VERSION_BYTES      33U

_Static_assert(OTA_MANAGER_CONFIRM_TIMEOUT_MS > OTA_MANAGER_HEALTH_POLL_MS,
               "OTA confirmation timeout must allow at least one health poll");

typedef enum {
    OTA_MANAGER_BOOT_NORMAL = 0,
    OTA_MANAGER_BOOT_PENDING_CONFIRMATION,
    OTA_MANAGER_BOOT_CONFIRMED,
    OTA_MANAGER_BOOT_ROLLBACK_REQUESTED,
} ota_manager_boot_status_t;

typedef struct {
    char running_partition[OTA_MANAGER_DIAG_LABEL_BYTES];
    char boot_partition[OTA_MANAGER_DIAG_LABEL_BYTES];
    char firmware_version[OTA_MANAGER_DIAG_VERSION_BYTES];
    esp_ota_img_states_t running_state;
    ota_manager_boot_status_t boot_status;
    uint32_t rollback_count;
    uint32_t successful_update_count;
    bool rollback_supported;
} ota_manager_diagnostics_t;

static const char *TAG = "ota_manager";
static ota_manager_diagnostics_t s_ota_diag = {
    .running_partition = "unknown",
    .boot_partition = "unknown",
    .firmware_version = "unknown",
    .running_state = ESP_OTA_IMG_UNDEFINED,
    .boot_status = OTA_MANAGER_BOOT_NORMAL,
    .rollback_supported = true,
};

/* Application hook: return true only after acquisition, storage, network, and WDT are healthy. */
bool app_ota_healthcheck_passed(void) __attribute__((weak));

static uint32_t ota_manager_now_ms(void)
{
    return (uint32_t)(esp_timer_get_time() / 1000ULL);
}

static void ota_manager_copy_label(char *dst, size_t dst_size, const esp_partition_t *partition)
{
    if (dst == NULL || dst_size == 0U) {
        return;
    }
    if (partition == NULL) {
        (void)snprintf(dst, dst_size, "none");
        return;
    }
    (void)snprintf(dst, dst_size, "%s", partition->label);
}

static const char *ota_manager_state_name(esp_ota_img_states_t state)
{
    switch (state) {
    case ESP_OTA_IMG_NEW:
        return "new";
    case ESP_OTA_IMG_PENDING_VERIFY:
        return "pending_verify";
    case ESP_OTA_IMG_VALID:
        return "valid";
    case ESP_OTA_IMG_INVALID:
        return "invalid";
    case ESP_OTA_IMG_ABORTED:
        return "aborted";
    case ESP_OTA_IMG_UNDEFINED:
    default:
        return "undefined";
    }
}

static bool ota_manager_partitions_ready(void)
{
    const esp_partition_t *next = esp_ota_get_next_update_partition(NULL);
    const esp_partition_t *running = esp_ota_get_running_partition();
    if (running == NULL || next == NULL) {
        ESP_LOGE(TAG, "OTA partitions unavailable: running=%p next=%p", running, next);
        return false;
    }
    if (running == next) {
        ESP_LOGE(TAG, "dual OTA partition layout not active; running partition equals update partition");
        return false;
    }
    return true;
}

static void ota_manager_refresh_diagnostics(ota_manager_boot_status_t boot_status)
{
    const esp_partition_t *running = esp_ota_get_running_partition();
    const esp_partition_t *boot = esp_ota_get_boot_partition();
    const esp_app_desc_t *desc = esp_app_get_description();

    ota_manager_copy_label(s_ota_diag.running_partition,
                           sizeof(s_ota_diag.running_partition), running);
    ota_manager_copy_label(s_ota_diag.boot_partition, sizeof(s_ota_diag.boot_partition), boot);
    (void)snprintf(s_ota_diag.firmware_version, sizeof(s_ota_diag.firmware_version),
                   "%s", desc != NULL ? desc->version : "unknown");
    s_ota_diag.boot_status = boot_status;

    if (running != NULL && esp_ota_get_state_partition(running, &s_ota_diag.running_state) != ESP_OK) {
        s_ota_diag.running_state = ESP_OTA_IMG_UNDEFINED;
    }
}

static bool ota_manager_wait_for_healthcheck(uint32_t timeout_ms)
{
    const uint32_t started_ms = ota_manager_now_ms();
    do {
        if (app_ota_healthcheck_passed != NULL && app_ota_healthcheck_passed()) {
            return true;
        }
        vTaskDelay(pdMS_TO_TICKS(OTA_MANAGER_HEALTH_POLL_MS));
    } while ((uint32_t)(ota_manager_now_ms() - started_ms) < timeout_ms);

    return false;
}

esp_err_t ota_manager_confirm_boot_after_healthcheck(void)
{
    const esp_partition_t *running = esp_ota_get_running_partition();
    esp_ota_img_states_t state = ESP_OTA_IMG_UNDEFINED;

    ota_manager_refresh_diagnostics(OTA_MANAGER_BOOT_NORMAL);
    if (running == NULL || esp_ota_get_state_partition(running, &state) != ESP_OK) {
        ESP_LOGI(TAG, "OTA_ROLLBACK_SAFE: running image has no pending rollback state");
        return ESP_OK;
    }

    s_ota_diag.running_state = state;
    if (state != ESP_OTA_IMG_PENDING_VERIFY) {
        ESP_LOGI(TAG, "OTA_ROLLBACK_SAFE: running image state=%s partition=%s version=%s",
                 ota_manager_state_name(state), s_ota_diag.running_partition,
                 s_ota_diag.firmware_version);
        return ESP_OK;
    }

    s_ota_diag.boot_status = OTA_MANAGER_BOOT_PENDING_CONFIRMATION;
    ESP_LOGW(TAG,
             "trial OTA boot pending confirmation: partition=%s version=%s timeout=%u ms",
             s_ota_diag.running_partition, s_ota_diag.firmware_version,
             OTA_MANAGER_CONFIRM_TIMEOUT_MS);

    if (ota_manager_wait_for_healthcheck(OTA_MANAGER_CONFIRM_TIMEOUT_MS)) {
        const esp_err_t err = esp_ota_mark_app_valid_cancel_rollback();
        if (err == ESP_OK) {
            ++s_ota_diag.successful_update_count;
            ota_manager_refresh_diagnostics(OTA_MANAGER_BOOT_CONFIRMED);
            ESP_LOGI(TAG, "OTA_ROLLBACK_SAFE: app confirmed valid partition=%s version=%s",
                     s_ota_diag.running_partition, s_ota_diag.firmware_version);
        }
        return err;
    }

    ++s_ota_diag.rollback_count;
    s_ota_diag.boot_status = OTA_MANAGER_BOOT_ROLLBACK_REQUESTED;
    ESP_LOGE(TAG, "OTA healthcheck failed; marking app invalid and requesting rollback");
    return esp_ota_mark_app_invalid_rollback_and_reboot();
}

static esp_err_t ota_manager_validate_candidate(esp_https_ota_handle_t ota_handle,
                                                const char *expected_project_name)
{
    esp_app_desc_t candidate_desc;
    esp_err_t err = esp_https_ota_get_img_desc(ota_handle, &candidate_desc);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "candidate image metadata unavailable: %s", esp_err_to_name(err));
        return err;
    }

    const esp_app_desc_t *running_desc = esp_app_get_description();
    if (expected_project_name != NULL && expected_project_name[0] != '\0' &&
        strncmp(candidate_desc.project_name, expected_project_name,
                sizeof(candidate_desc.project_name)) != 0) {
        ESP_LOGE(TAG, "candidate project mismatch: got=%s expected=%s",
                 candidate_desc.project_name, expected_project_name);
        return ESP_ERR_INVALID_RESPONSE;
    }

    ESP_LOGI(TAG, "candidate image verified: project=%s version=%s current_version=%s",
             candidate_desc.project_name, candidate_desc.version,
             running_desc != NULL ? running_desc->version : "unknown");
    return ESP_OK;
}

esp_err_t ota_manager_start_update(const char *url, const char *expected_project_name,
                                   const char *cert_pem)
{
    if (url == NULL || url[0] == '\0') {
        return ESP_ERR_INVALID_ARG;
    }
    if (!ota_manager_partitions_ready()) {
        return ESP_ERR_NOT_SUPPORTED;
    }

    esp_http_client_config_t http_config = {
        .url = url,
        .cert_pem = cert_pem,
        .timeout_ms = 10000,
        .keep_alive_enable = true,
    };
    esp_https_ota_config_t ota_config = {
        .http_config = &http_config,
        .bulk_flash_erase = true,
    };

    esp_https_ota_handle_t ota_handle = NULL;
    esp_err_t err = esp_https_ota_begin(&ota_config, &ota_handle);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "OTA begin failed: %s", esp_err_to_name(err));
        return err;
    }

    bool candidate_checked = false;
    while (true) {
        err = esp_https_ota_perform(ota_handle);
        if (!candidate_checked) {
            const esp_err_t validate_err = ota_manager_validate_candidate(ota_handle,
                                                                         expected_project_name);
            if (validate_err != ESP_OK) {
                (void)esp_https_ota_abort(ota_handle);
                return validate_err;
            }
            candidate_checked = true;
        }

        if (err != ESP_ERR_HTTPS_OTA_IN_PROGRESS) {
            break;
        }
    }

    if (err != ESP_OK) {
        ESP_LOGE(TAG, "OTA download/write failed: %s", esp_err_to_name(err));
        (void)esp_https_ota_abort(ota_handle);
        return err;
    }

    if (!esp_https_ota_is_complete_data_received(ota_handle)) {
        ESP_LOGE(TAG, "OTA image incomplete; keeping current partition active");
        (void)esp_https_ota_abort(ota_handle);
        return ESP_ERR_INVALID_SIZE;
    }

    err = esp_https_ota_finish(ota_handle);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "OTA finish verification failed: %s", esp_err_to_name(err));
        return err;
    }

    ota_manager_refresh_diagnostics(OTA_MANAGER_BOOT_PENDING_CONFIRMATION);
    ESP_LOGI(TAG, "OTA image staged on inactive partition; reboot required for trial boot");
    return ESP_OK;
}

void ota_manager_reboot_to_trial_image(void)
{
    ESP_LOGI(TAG, "rebooting into trial OTA image; boot confirmation required after healthcheck");
    esp_restart();
}

void ota_manager_get_diagnostics(ota_manager_diagnostics_t *out_diagnostics)
{
    if (out_diagnostics == NULL) {
        return;
    }
    ota_manager_refresh_diagnostics(s_ota_diag.boot_status);
    *out_diagnostics = s_ota_diag;
}

void ota_manager_log_diagnostics(void)
{
    ota_manager_refresh_diagnostics(s_ota_diag.boot_status);
    ESP_LOGI(TAG,
             "OTA_ROLLBACK_SAFE: running=%s boot=%s version=%s state=%s status=%d rollbacks=%lu successful_updates=%lu",
             s_ota_diag.running_partition, s_ota_diag.boot_partition,
             s_ota_diag.firmware_version, ota_manager_state_name(s_ota_diag.running_state),
             (int)s_ota_diag.boot_status, (unsigned long)s_ota_diag.rollback_count,
             (unsigned long)s_ota_diag.successful_update_count);
}
