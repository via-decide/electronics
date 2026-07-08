/*
 * ESP32 versioned sensor calibration storage in NVS.
 *
 * validation_id: esp32_nvs_calibration_v1
 * status: CALIBRATION_STORE_SAFE
 *
 * Boot flow:
 *   read NVS blob -> verify magic/schema/length/CRC -> load gain/offset
 *   -> otherwise use safe default coefficients.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "esp_err.h"
#include "esp_log.h"
#include "nvs.h"
#include "nvs_flash.h"

#define NVS_CALIBRATION_NAMESPACE       "sensor_cal"
#define NVS_CALIBRATION_BLOB_KEY        "cal_v1"
#define NVS_CALIBRATION_SCHEMA_VERSION  1U
#define NVS_CALIBRATION_MAGIC           0x314C4143U /* "CAL1" little-endian. */
#define NVS_CALIBRATION_DEFAULT_GAIN    1.0f
#define NVS_CALIBRATION_DEFAULT_OFFSET  0.0f
#define NVS_CALIBRATION_CRC_SEED        0xFFFFFFFFU

typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint16_t schema_version;
    uint16_t payload_size;
    float gain;
    float offset;
    uint32_t crc32;
} nvs_calibration_blob_t;

typedef struct {
    float gain;
    float offset;
    uint16_t schema_version;
    bool loaded_from_nvs;
    bool crc_valid;
} nvs_calibration_t;

static const char *TAG = "nvs_calibration";
static nvs_calibration_t s_calibration = {
    .gain = NVS_CALIBRATION_DEFAULT_GAIN,
    .offset = NVS_CALIBRATION_DEFAULT_OFFSET,
    .schema_version = NVS_CALIBRATION_SCHEMA_VERSION,
    .loaded_from_nvs = false,
    .crc_valid = false,
};

static uint32_t nvs_calibration_crc32(const void *data, size_t length)
{
    const uint8_t *bytes = (const uint8_t *)data;
    uint32_t crc = NVS_CALIBRATION_CRC_SEED;

    for (size_t i = 0; i < length; ++i) {
        crc ^= bytes[i];
        for (uint32_t bit = 0; bit < 8U; ++bit) {
            const uint32_t mask = 0U - (crc & 1U);
            crc = (crc >> 1U) ^ (0xEDB88320U & mask);
        }
    }

    return ~crc;
}

static uint32_t nvs_calibration_blob_crc(const nvs_calibration_blob_t *blob)
{
    nvs_calibration_blob_t crc_blob = *blob;
    crc_blob.crc32 = 0U;
    return nvs_calibration_crc32(&crc_blob, sizeof(crc_blob));
}

static nvs_calibration_blob_t nvs_calibration_make_blob(float gain, float offset)
{
    nvs_calibration_blob_t blob = {
        .magic = NVS_CALIBRATION_MAGIC,
        .schema_version = NVS_CALIBRATION_SCHEMA_VERSION,
        .payload_size = sizeof(nvs_calibration_blob_t),
        .gain = gain,
        .offset = offset,
        .crc32 = 0U,
    };
    blob.crc32 = nvs_calibration_blob_crc(&blob);
    return blob;
}

static void nvs_calibration_use_defaults(const char *reason)
{
    s_calibration = (nvs_calibration_t){
        .gain = NVS_CALIBRATION_DEFAULT_GAIN,
        .offset = NVS_CALIBRATION_DEFAULT_OFFSET,
        .schema_version = NVS_CALIBRATION_SCHEMA_VERSION,
        .loaded_from_nvs = false,
        .crc_valid = false,
    };
    ESP_LOGW(TAG,
             "CALIBRATION_STORE_SAFE: using defaults schema=v%u gain=%.6f offset=%.6f reason=%s",
             s_calibration.schema_version, s_calibration.gain, s_calibration.offset,
             reason != NULL ? reason : "unspecified");
}

static bool nvs_calibration_blob_valid(const nvs_calibration_blob_t *blob, const char **reason)
{
    if (blob->magic != NVS_CALIBRATION_MAGIC) {
        *reason = "bad_magic";
        return false;
    }
    if (blob->schema_version != NVS_CALIBRATION_SCHEMA_VERSION) {
        *reason = "schema_mismatch";
        return false;
    }
    if (blob->payload_size != sizeof(nvs_calibration_blob_t)) {
        *reason = "size_mismatch";
        return false;
    }
    if (blob->crc32 != nvs_calibration_blob_crc(blob)) {
        *reason = "crc_mismatch";
        return false;
    }

    *reason = "valid";
    return true;
}

static esp_err_t nvs_calibration_open(nvs_open_mode_t mode, nvs_handle_t *out_handle)
{
    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_LOGW(TAG, "NVS partition requires erase/reinit: %s", esp_err_to_name(err));
        err = nvs_flash_erase();
        if (err == ESP_OK) {
            err = nvs_flash_init();
        }
    }
    if (err != ESP_OK) {
        return err;
    }

    return nvs_open(NVS_CALIBRATION_NAMESPACE, mode, out_handle);
}

esp_err_t nvs_calibration_load(void)
{
    nvs_handle_t handle;
    esp_err_t err = nvs_calibration_open(NVS_READONLY, &handle);
    if (err == ESP_ERR_NVS_NOT_FOUND) {
        nvs_calibration_use_defaults("missing_namespace");
        return ESP_OK;
    }
    if (err != ESP_OK) {
        nvs_calibration_use_defaults(esp_err_to_name(err));
        return err;
    }

    nvs_calibration_blob_t blob;
    size_t blob_size = sizeof(blob);
    err = nvs_get_blob(handle, NVS_CALIBRATION_BLOB_KEY, &blob, &blob_size);
    nvs_close(handle);

    if (err == ESP_ERR_NVS_NOT_FOUND) {
        nvs_calibration_use_defaults("missing_blob");
        return ESP_OK;
    }
    if (err != ESP_OK) {
        nvs_calibration_use_defaults(esp_err_to_name(err));
        return err;
    }
    if (blob_size != sizeof(blob)) {
        nvs_calibration_use_defaults("stored_size_mismatch");
        return ESP_ERR_INVALID_SIZE;
    }

    const char *reason = NULL;
    if (!nvs_calibration_blob_valid(&blob, &reason)) {
        nvs_calibration_use_defaults(reason);
        return ESP_ERR_INVALID_CRC;
    }

    s_calibration = (nvs_calibration_t){
        .gain = blob.gain,
        .offset = blob.offset,
        .schema_version = blob.schema_version,
        .loaded_from_nvs = true,
        .crc_valid = true,
    };

    ESP_LOGI(TAG,
             "CALIBRATION_STORE_SAFE: loaded schema=v%u gain=%.6f offset=%.6f crc=0x%08lx",
             s_calibration.schema_version, s_calibration.gain, s_calibration.offset,
             (unsigned long)blob.crc32);
    return ESP_OK;
}

esp_err_t nvs_calibration_save(float gain, float offset)
{
    const nvs_calibration_blob_t blob = nvs_calibration_make_blob(gain, offset);
    nvs_handle_t handle;
    esp_err_t err = nvs_calibration_open(NVS_READWRITE, &handle);
    if (err != ESP_OK) {
        return err;
    }

    err = nvs_set_blob(handle, NVS_CALIBRATION_BLOB_KEY, &blob, sizeof(blob));
    if (err == ESP_OK) {
        err = nvs_commit(handle);
    }
    nvs_close(handle);
    if (err != ESP_OK) {
        return err;
    }

    s_calibration = (nvs_calibration_t){
        .gain = gain,
        .offset = offset,
        .schema_version = NVS_CALIBRATION_SCHEMA_VERSION,
        .loaded_from_nvs = true,
        .crc_valid = true,
    };

    ESP_LOGI(TAG,
             "saved calibration schema=v%u gain=%.6f offset=%.6f crc=0x%08lx",
             NVS_CALIBRATION_SCHEMA_VERSION, gain, offset, (unsigned long)blob.crc32);
    return ESP_OK;
}

float nvs_calibration_apply(int32_t raw_value)
{
    return ((float)raw_value * s_calibration.gain) + s_calibration.offset;
}

void nvs_calibration_get(nvs_calibration_t *out_calibration)
{
    if (out_calibration == NULL) {
        return;
    }
    *out_calibration = s_calibration;
}

uint16_t nvs_calibration_schema_version(void)
{
    return s_calibration.schema_version;
}

bool nvs_calibration_loaded_from_nvs(void)
{
    return s_calibration.loaded_from_nvs;
}

bool nvs_calibration_crc_valid(void)
{
    return s_calibration.crc_valid;
}

esp_err_t nvs_calibration_erase(void)
{
    nvs_handle_t handle;
    esp_err_t err = nvs_calibration_open(NVS_READWRITE, &handle);
    if (err != ESP_OK) {
        return err;
    }

    err = nvs_erase_key(handle, NVS_CALIBRATION_BLOB_KEY);
    if (err == ESP_ERR_NVS_NOT_FOUND) {
        err = ESP_OK;
    }
    if (err == ESP_OK) {
        err = nvs_commit(handle);
    }
    nvs_close(handle);

    if (err == ESP_OK) {
        nvs_calibration_use_defaults("erased");
    }
    return err;
}


void nvs_calibration_log_diagnostics(void)
{
    ESP_LOGI(TAG,
             "CALIBRATION_STORE_SAFE: namespace=%s key=%s schema=v%u gain=%.6f offset=%.6f loaded_from_nvs=%s crc_valid=%s",
             NVS_CALIBRATION_NAMESPACE, NVS_CALIBRATION_BLOB_KEY,
             s_calibration.schema_version, s_calibration.gain, s_calibration.offset,
             s_calibration.loaded_from_nvs ? "yes" : "no",
             s_calibration.crc_valid ? "yes" : "no");
}
