/*
 * ESP32 I2C bus recovery for stuck sensor networks.
 *
 * validation_id: esp32_i2c_recovery_v1
 * status: I2C_BUS_SELF_RECOVERING
 *
 * Recovery flow:
 *   detect timeout or stuck SDA/SCL -> delete I2C driver -> reconfigure lines as
 *   open-drain GPIO -> pulse SCL up to 9 times -> generate STOP -> reinstall
 *   ESP-IDF I2C driver -> retry bounded transaction or report hard sensor fault.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "driver/gpio.h"
#include "driver/i2c.h"
#include "esp_err.h"
#include "esp_log.h"
#include "esp_rom_sys.h"
#include "freertos/FreeRTOS.h"

#define I2C_RECOVERY_DEFAULT_PORT          I2C_NUM_0
#define I2C_RECOVERY_DEFAULT_SDA_GPIO      GPIO_NUM_21
#define I2C_RECOVERY_DEFAULT_SCL_GPIO      GPIO_NUM_22
#define I2C_RECOVERY_DEFAULT_FREQ_HZ       100000U
#define I2C_RECOVERY_PULSES                9U
#define I2C_RECOVERY_RETRY_COUNT           3U
#define I2C_RECOVERY_HALF_PERIOD_US        5U
#define I2C_RECOVERY_LINE_SETTLE_US        10U
#define I2C_RECOVERY_TRANSACTION_TIMEOUT_MS 50U

_Static_assert(I2C_RECOVERY_PULSES <= 9U, "I2C recovery must use no more than 9 SCL pulses");

typedef enum {
    I2C_RECOVERY_BUS_IDLE = 0,
    I2C_RECOVERY_BUS_STUCK_SDA,
    I2C_RECOVERY_BUS_STUCK_SCL,
    I2C_RECOVERY_BUS_STUCK_BOTH,
} i2c_recovery_bus_state_t;

typedef struct {
    i2c_port_t port;
    gpio_num_t sda_gpio;
    gpio_num_t scl_gpio;
    uint32_t frequency_hz;
    uint32_t recovery_count;
    uint32_t hard_fault_count;
    i2c_recovery_bus_state_t last_bus_state;
    bool driver_installed;
} i2c_recovery_context_t;

static const char *TAG = "i2c_recovery";
static i2c_recovery_context_t s_i2c_recovery = {
    .port = I2C_RECOVERY_DEFAULT_PORT,
    .sda_gpio = I2C_RECOVERY_DEFAULT_SDA_GPIO,
    .scl_gpio = I2C_RECOVERY_DEFAULT_SCL_GPIO,
    .frequency_hz = I2C_RECOVERY_DEFAULT_FREQ_HZ,
    .last_bus_state = I2C_RECOVERY_BUS_IDLE,
};

static const char *i2c_recovery_state_name(i2c_recovery_bus_state_t state)
{
    switch (state) {
    case I2C_RECOVERY_BUS_IDLE:
        return "idle";
    case I2C_RECOVERY_BUS_STUCK_SDA:
        return "stuck_sda";
    case I2C_RECOVERY_BUS_STUCK_SCL:
        return "stuck_scl";
    case I2C_RECOVERY_BUS_STUCK_BOTH:
        return "stuck_both";
    default:
        return "unknown";
    }
}

static i2c_recovery_bus_state_t i2c_recovery_read_bus_state(void)
{
    const bool sda_high = gpio_get_level(s_i2c_recovery.sda_gpio) != 0;
    const bool scl_high = gpio_get_level(s_i2c_recovery.scl_gpio) != 0;

    if (sda_high && scl_high) {
        return I2C_RECOVERY_BUS_IDLE;
    }
    if (!sda_high && !scl_high) {
        return I2C_RECOVERY_BUS_STUCK_BOTH;
    }
    if (!sda_high) {
        return I2C_RECOVERY_BUS_STUCK_SDA;
    }
    return I2C_RECOVERY_BUS_STUCK_SCL;
}

static void i2c_recovery_drive_line(gpio_num_t gpio, bool high)
{
    if (high) {
        (void)gpio_set_level(gpio, 1);
        (void)gpio_set_direction(gpio, GPIO_MODE_INPUT_OUTPUT_OD);
    } else {
        (void)gpio_set_direction(gpio, GPIO_MODE_OUTPUT_OD);
        (void)gpio_set_level(gpio, 0);
    }
}

static esp_err_t i2c_recovery_configure_gpio_bus(void)
{
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << s_i2c_recovery.sda_gpio) | (1ULL << s_i2c_recovery.scl_gpio),
        .mode = GPIO_MODE_INPUT_OUTPUT_OD,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    esp_err_t err = gpio_config(&io_conf);
    if (err != ESP_OK) {
        return err;
    }

    i2c_recovery_drive_line(s_i2c_recovery.sda_gpio, true);
    i2c_recovery_drive_line(s_i2c_recovery.scl_gpio, true);
    esp_rom_delay_us(I2C_RECOVERY_LINE_SETTLE_US);
    return ESP_OK;
}

static esp_err_t i2c_recovery_install_driver(void)
{
    const i2c_config_t config = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = s_i2c_recovery.sda_gpio,
        .scl_io_num = s_i2c_recovery.scl_gpio,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = s_i2c_recovery.frequency_hz,
    };

    esp_err_t err = i2c_param_config(s_i2c_recovery.port, &config);
    if (err != ESP_OK) {
        return err;
    }

    err = i2c_driver_install(s_i2c_recovery.port, I2C_MODE_MASTER, 0, 0, 0);
    if (err == ESP_ERR_INVALID_STATE) {
        s_i2c_recovery.driver_installed = true;
        return ESP_OK;
    }
    s_i2c_recovery.driver_installed = err == ESP_OK;
    return err;
}

static void i2c_recovery_delete_driver(void)
{
    const esp_err_t err = i2c_driver_delete(s_i2c_recovery.port);
    if (err == ESP_OK || err == ESP_ERR_INVALID_STATE) {
        s_i2c_recovery.driver_installed = false;
    }
}

static void i2c_recovery_generate_stop(void)
{
    i2c_recovery_drive_line(s_i2c_recovery.sda_gpio, false);
    esp_rom_delay_us(I2C_RECOVERY_HALF_PERIOD_US);
    i2c_recovery_drive_line(s_i2c_recovery.scl_gpio, true);
    esp_rom_delay_us(I2C_RECOVERY_HALF_PERIOD_US);
    i2c_recovery_drive_line(s_i2c_recovery.sda_gpio, true);
    esp_rom_delay_us(I2C_RECOVERY_LINE_SETTLE_US);
}

esp_err_t i2c_recovery_init(i2c_port_t port, gpio_num_t sda_gpio, gpio_num_t scl_gpio,
                            uint32_t frequency_hz)
{
    s_i2c_recovery.port = port;
    s_i2c_recovery.sda_gpio = sda_gpio;
    s_i2c_recovery.scl_gpio = scl_gpio;
    s_i2c_recovery.frequency_hz = frequency_hz == 0U ? I2C_RECOVERY_DEFAULT_FREQ_HZ : frequency_hz;

    esp_err_t err = i2c_recovery_configure_gpio_bus();
    if (err != ESP_OK) {
        return err;
    }
    err = i2c_recovery_install_driver();
    ESP_LOGI(TAG, "I2C_BUS_SELF_RECOVERING: port=%d sda=%d scl=%d freq=%lu init=%s",
             s_i2c_recovery.port, s_i2c_recovery.sda_gpio, s_i2c_recovery.scl_gpio,
             (unsigned long)s_i2c_recovery.frequency_hz, esp_err_to_name(err));
    return err;
}

bool i2c_recovery_bus_idle(void)
{
    s_i2c_recovery.last_bus_state = i2c_recovery_read_bus_state();
    return s_i2c_recovery.last_bus_state == I2C_RECOVERY_BUS_IDLE;
}

esp_err_t i2c_recovery_recover_bus(void)
{
    s_i2c_recovery.last_bus_state = i2c_recovery_read_bus_state();
    if (s_i2c_recovery.last_bus_state == I2C_RECOVERY_BUS_IDLE) {
        return ESP_OK;
    }

    ESP_LOGW(TAG, "I2C timeout/stuck bus detected state=%s; starting GPIO recovery",
             i2c_recovery_state_name(s_i2c_recovery.last_bus_state));

    i2c_recovery_delete_driver();
    esp_err_t err = i2c_recovery_configure_gpio_bus();
    if (err != ESP_OK) {
        ++s_i2c_recovery.hard_fault_count;
        return err;
    }

    for (uint32_t pulse = 0; pulse < I2C_RECOVERY_PULSES; ++pulse) {
        if (gpio_get_level(s_i2c_recovery.sda_gpio) != 0 &&
            gpio_get_level(s_i2c_recovery.scl_gpio) != 0) {
            break;
        }

        i2c_recovery_drive_line(s_i2c_recovery.scl_gpio, false);
        esp_rom_delay_us(I2C_RECOVERY_HALF_PERIOD_US);
        i2c_recovery_drive_line(s_i2c_recovery.scl_gpio, true);
        esp_rom_delay_us(I2C_RECOVERY_HALF_PERIOD_US);
    }

    i2c_recovery_generate_stop();
    s_i2c_recovery.last_bus_state = i2c_recovery_read_bus_state();
    err = i2c_recovery_install_driver();
    if (err != ESP_OK) {
        ++s_i2c_recovery.hard_fault_count;
        return err;
    }

    if (s_i2c_recovery.last_bus_state != I2C_RECOVERY_BUS_IDLE) {
        ++s_i2c_recovery.hard_fault_count;
        ESP_LOGE(TAG, "I2C recovery failed; hard sensor fault state=%s faults=%lu",
                 i2c_recovery_state_name(s_i2c_recovery.last_bus_state),
                 (unsigned long)s_i2c_recovery.hard_fault_count);
        return ESP_ERR_TIMEOUT;
    }

    ++s_i2c_recovery.recovery_count;
    ESP_LOGI(TAG, "I2C bus recovered after GPIO clock pulses recoveries=%lu",
             (unsigned long)s_i2c_recovery.recovery_count);
    return ESP_OK;
}

esp_err_t i2c_recovery_master_write_read_device(uint8_t device_address,
                                                const uint8_t *write_buffer,
                                                size_t write_size,
                                                uint8_t *read_buffer,
                                                size_t read_size,
                                                uint32_t timeout_ms)
{
    const TickType_t timeout_ticks = pdMS_TO_TICKS(timeout_ms == 0U
                                                      ? I2C_RECOVERY_TRANSACTION_TIMEOUT_MS
                                                      : timeout_ms);

    for (uint32_t attempt = 0; attempt < I2C_RECOVERY_RETRY_COUNT; ++attempt) {
        esp_err_t err = i2c_master_write_read_device(s_i2c_recovery.port, device_address,
                                                     write_buffer, write_size,
                                                     read_buffer, read_size,
                                                     timeout_ticks);
        if (err == ESP_OK) {
            return ESP_OK;
        }

        ESP_LOGW(TAG, "I2C transaction failed attempt=%lu err=%s; recovering bus",
                 (unsigned long)(attempt + 1U), esp_err_to_name(err));
        err = i2c_recovery_recover_bus();
        if (err != ESP_OK) {
            return err;
        }
    }

    ++s_i2c_recovery.hard_fault_count;
    ESP_LOGE(TAG, "I2C transaction exhausted retries; hard sensor fault count=%lu",
             (unsigned long)s_i2c_recovery.hard_fault_count);
    return ESP_ERR_TIMEOUT;
}

void i2c_recovery_log_diagnostics(void)
{
    s_i2c_recovery.last_bus_state = i2c_recovery_read_bus_state();
    ESP_LOGI(TAG,
             "I2C_BUS_SELF_RECOVERING: port=%d sda=%d scl=%d state=%s recoveries=%lu hard_faults=%lu driver=%s",
             s_i2c_recovery.port, s_i2c_recovery.sda_gpio, s_i2c_recovery.scl_gpio,
             i2c_recovery_state_name(s_i2c_recovery.last_bus_state),
             (unsigned long)s_i2c_recovery.recovery_count,
             (unsigned long)s_i2c_recovery.hard_fault_count,
             s_i2c_recovery.driver_installed ? "installed" : "stopped");
}
