#include "esp_err.h"
#include "esp_log.h"

esp_err_t mqtt_telemetry_start(const char *broker_uri);

void app_main(void)
{
    ESP_ERROR_CHECK(mqtt_telemetry_start("mqtt://broker.example.local"));
    ESP_LOGI("mqtt_example", "MQTT telemetry example started; configure broker URI for hardware tests");
}
