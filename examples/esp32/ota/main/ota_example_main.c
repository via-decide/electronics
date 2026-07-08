#include "esp_err.h"
#include "esp_log.h"

esp_err_t ota_manager_confirm_boot_after_healthcheck(void);

void app_main(void)
{
    ESP_ERROR_CHECK(ota_manager_confirm_boot_after_healthcheck());
    ESP_LOGI("ota_example", "OTA rollback-safe boot confirmation example completed");
}
