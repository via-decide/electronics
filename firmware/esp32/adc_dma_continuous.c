/*
 * ESP32 continuous ADC acquisition pipeline.
 *
 * validation_id: esp32_adc_dma_continuous_v1
 * status: ADC_SAMPLING_LOCKED
 *
 * Sampling model:
 *   - ADC peripheral owns the conversion cadence.
 *   - ESP-IDF adc_continuous DMA buffers own sample transport.
 *   - No samples are collected from loop() or analogRead().
 *   - DSP/storage/MQTT work is moved out of the ADC callback.
 *
 * Default target: 2 kHz on GPIO34 (ADC1 channel 6) with a 1024-byte DMA pool
 * and half/full-style 512-byte conversion-frame callbacks.
 */

#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#include "esp_adc/adc_continuous.h"
#include "esp_check.h"
#include "esp_err.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"
#include "hal/adc_types.h"
#include "soc/soc_caps.h"

#define ADC_DMA_SAMPLE_RATE_HZ      2000U
#define ADC_DMA_GPIO                34U
#define ADC_DMA_UNIT                ADC_UNIT_1
#define ADC_DMA_CHANNEL             ADC_CHANNEL_6 /* GPIO34 on ESP32 ADC1. */
#define ADC_DMA_ATTEN               ADC_ATTEN_DB_11
#define ADC_DMA_BIT_WIDTH           SOC_ADC_DIGI_MAX_BITWIDTH
#define ADC_DMA_BUFFER_BYTES        1024U
#define ADC_DMA_HALF_BUFFER_BYTES   (ADC_DMA_BUFFER_BYTES / 2U)
#define ADC_DMA_RESULT_BYTES        SOC_ADC_DIGI_RESULT_BYTES
#define ADC_DMA_QUEUE_DEPTH         8U

/*
 * Jitter budget declaration:
 * Fs = 2000 Hz, Ts = 500 us. The ADC digital controller is hardware-timed;
 * remaining conversion-time jitter should be bounded by the APB/digital-controller
 * clock domain and driver/DMA latency affects only delivery time, not sample time.
 * Keep Fmax below 1 kHz by Nyquist; in production choose margin, e.g. Fmax <= 800 Hz.
 */
#define ADC_DMA_NYQUIST_MAX_HZ      (ADC_DMA_SAMPLE_RATE_HZ / 2U)
#define ADC_DMA_RECOMMENDED_FMAX_HZ 800U

_Static_assert((ADC_DMA_BUFFER_BYTES % 2U) == 0U, "DMA buffer must have half/full halves");
_Static_assert((ADC_DMA_HALF_BUFFER_BYTES % ADC_DMA_RESULT_BYTES) == 0U,
               "Conversion frame must hold complete ADC samples");

typedef enum {
    ADC_DMA_EVENT_HALF_BUFFER = 0,
    ADC_DMA_EVENT_FULL_BUFFER = 1,
} adc_dma_event_phase_t;

typedef struct {
    adc_dma_event_phase_t phase;
    uint32_t sample_count;
    uint32_t frame_bytes;
} adc_dma_event_t;

static const char *TAG = "adc_dma_continuous";
static adc_continuous_handle_t s_adc_handle;
static QueueHandle_t s_adc_event_queue;
static TaskHandle_t s_dsp_task_handle;
static volatile uint32_t s_callback_count;

/* Optional application hooks supplied by Wi-Fi/MQTT/storage modules. */
void app_wifi_start(void) __attribute__((weak));
void app_mqtt_start(void) __attribute__((weak));
void app_storage_write_adc_samples(const adc_digi_output_data_t *samples,
                                   uint32_t sample_count) __attribute__((weak));

static bool IRAM_ATTR adc_dma_on_frame_ready(adc_continuous_handle_t handle,
                                             const adc_continuous_evt_data_t *edata,
                                             void *user_data)
{
    (void)handle;
    (void)user_data;

    const uint32_t callback_index = s_callback_count++;
    const adc_dma_event_t event = {
        .phase = (callback_index & 1U) ? ADC_DMA_EVENT_FULL_BUFFER : ADC_DMA_EVENT_HALF_BUFFER,
        .sample_count = edata->size / ADC_DMA_RESULT_BYTES,
        .frame_bytes = edata->size,
    };

    BaseType_t must_yield = pdFALSE;
    if (s_adc_event_queue != NULL) {
        (void)xQueueSendFromISR(s_adc_event_queue, &event, &must_yield);
    }
    return must_yield == pdTRUE;
}

static esp_err_t adc_dma_configure(adc_continuous_handle_t *out_handle)
{
    adc_continuous_handle_cfg_t handle_cfg = {
        .max_store_buf_size = ADC_DMA_BUFFER_BYTES,
        .conv_frame_size = ADC_DMA_HALF_BUFFER_BYTES,
    };
    ESP_RETURN_ON_ERROR(adc_continuous_new_handle(&handle_cfg, out_handle), TAG,
                        "create ADC continuous handle");

    adc_digi_pattern_config_t pattern = {
        .atten = ADC_DMA_ATTEN,
        .channel = ADC_DMA_CHANNEL,
        .unit = ADC_DMA_UNIT,
        .bit_width = ADC_DMA_BIT_WIDTH,
    };

    adc_continuous_config_t config = {
        .sample_freq_hz = ADC_DMA_SAMPLE_RATE_HZ,
        .conv_mode = ADC_CONV_SINGLE_UNIT_1,
        .format = ADC_DIGI_OUTPUT_FORMAT_TYPE1,
        .pattern_num = 1,
        .adc_pattern = &pattern,
    };
    ESP_RETURN_ON_ERROR(adc_continuous_config(*out_handle, &config), TAG,
                        "configure ADC continuous mode");

    adc_continuous_evt_cbs_t callbacks = {
        .on_conv_done = adc_dma_on_frame_ready,
    };
    ESP_RETURN_ON_ERROR(adc_continuous_register_event_callbacks(*out_handle, &callbacks, NULL),
                        TAG, "register ADC DMA callback");

    return ESP_OK;
}

static void adc_dsp_task(void *arg)
{
    (void)arg;

    uint8_t frame[ADC_DMA_HALF_BUFFER_BYTES];
    adc_dma_event_t event;

    for (;;) {
        if (xQueueReceive(s_adc_event_queue, &event, portMAX_DELAY) != pdTRUE) {
            continue;
        }

        uint32_t bytes_read = 0;
        const esp_err_t err = adc_continuous_read(s_adc_handle, frame, sizeof(frame),
                                                  &bytes_read, 0);
        if (err == ESP_ERR_TIMEOUT) {
            continue;
        }
        if (err != ESP_OK) {
            ESP_LOGW(TAG, "adc_continuous_read failed: %s", esp_err_to_name(err));
            continue;
        }

        const uint32_t samples_read = bytes_read / ADC_DMA_RESULT_BYTES;
        const uint32_t expected_ms = (samples_read * 1000U) / ADC_DMA_SAMPLE_RATE_HZ;
        ESP_LOGD(TAG, "%s frame: %lu samples, %lu bytes, interval ~= %lu ms",
                 event.phase == ADC_DMA_EVENT_HALF_BUFFER ? "half" : "full",
                 (unsigned long)samples_read,
                 (unsigned long)bytes_read,
                 (unsigned long)expected_ms);

        if (app_storage_write_adc_samples != NULL) {
            app_storage_write_adc_samples((const adc_digi_output_data_t *)frame, samples_read);
        }
    }
}

esp_err_t adc_dma_continuous_start(void)
{
    if (s_adc_handle != NULL) {
        return ESP_ERR_INVALID_STATE;
    }

    s_adc_event_queue = xQueueCreate(ADC_DMA_QUEUE_DEPTH, sizeof(adc_dma_event_t));
    ESP_RETURN_ON_FALSE(s_adc_event_queue != NULL, ESP_ERR_NO_MEM, TAG,
                        "create ADC event queue");

    ESP_RETURN_ON_ERROR(adc_dma_configure(&s_adc_handle), TAG, "configure ADC DMA");

    const BaseType_t task_ok = xTaskCreatePinnedToCore(adc_dsp_task, "adc_dsp", 4096,
                                                       NULL, tskIDLE_PRIORITY + 3,
                                                       &s_dsp_task_handle, 1);
    ESP_RETURN_ON_FALSE(task_ok == pdPASS, ESP_ERR_NO_MEM, TAG, "create DSP task");

    ESP_RETURN_ON_ERROR(adc_continuous_start(s_adc_handle), TAG, "start ADC continuous mode");

    ESP_LOGI(TAG,
             "ADC_SAMPLING_LOCKED: GPIO%u, Fs=%u Hz, DMA=%u bytes, callback frame=%u bytes, Nyquist=%u Hz, recommended Fmax<=%u Hz",
             ADC_DMA_GPIO, ADC_DMA_SAMPLE_RATE_HZ, ADC_DMA_BUFFER_BYTES,
             ADC_DMA_HALF_BUFFER_BYTES, ADC_DMA_NYQUIST_MAX_HZ,
             ADC_DMA_RECOMMENDED_FMAX_HZ);
    return ESP_OK;
}

esp_err_t adc_dma_continuous_stop(void)
{
    if (s_adc_handle == NULL) {
        return ESP_ERR_INVALID_STATE;
    }

    ESP_RETURN_ON_ERROR(adc_continuous_stop(s_adc_handle), TAG, "stop ADC continuous mode");
    ESP_RETURN_ON_ERROR(adc_continuous_deinit(s_adc_handle), TAG, "deinit ADC continuous mode");
    s_adc_handle = NULL;

    if (s_dsp_task_handle != NULL) {
        vTaskDelete(s_dsp_task_handle);
        s_dsp_task_handle = NULL;
    }
    if (s_adc_event_queue != NULL) {
        vQueueDelete(s_adc_event_queue);
        s_adc_event_queue = NULL;
    }
    return ESP_OK;
}

void __attribute__((weak)) app_main(void)
{
    /* Radio/network work may run concurrently; ADC sample timing remains peripheral-owned. */
    if (app_wifi_start != NULL) {
        app_wifi_start();
    }
    if (app_mqtt_start != NULL) {
        app_mqtt_start();
    }

    ESP_ERROR_CHECK(adc_dma_continuous_start());
}
