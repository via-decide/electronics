#include "esp_err.h"
#include "esp_log.h"

esp_err_t task_topology_start(void);

void app_main(void)
{
    ESP_ERROR_CHECK(task_topology_start());
    ESP_LOGI("freertos_example", "FreeRTOS task topology example started");
}
