#include "esp_err.h"
#include "esp_log.h"

esp_err_t hardware_timer_scheduler_start(void);

void app_main(void)
{
    ESP_ERROR_CHECK(hardware_timer_scheduler_start());
    ESP_LOGI("timers_example", "Hardware timer scheduler example started");
}
