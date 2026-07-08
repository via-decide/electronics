#include "esp_err.h"
#include "esp_log.h"

esp_err_t adc_dma_continuous_start(void);

void app_main(void)
{
    ESP_ERROR_CHECK(adc_dma_continuous_start());
    ESP_LOGI("adc_dma_example", "ADC DMA continuous example started");
}
