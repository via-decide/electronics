#include "driver/gpio.h"
#include "driver/i2c.h"
#include "esp_err.h"
#include "esp_log.h"

esp_err_t i2c_recovery_init(i2c_port_t port, gpio_num_t sda_gpio, gpio_num_t scl_gpio,
                            uint32_t frequency_hz);

void app_main(void)
{
    ESP_ERROR_CHECK(i2c_recovery_init(I2C_NUM_0, GPIO_NUM_21, GPIO_NUM_22, 100000));
    ESP_LOGI("i2c_example", "I2C recovery example initialized");
}
