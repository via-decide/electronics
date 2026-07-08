# Engineering References

## Purpose

References must prioritize primary engineering sources: official vendor documentation, datasheets, standards, application notes, and peer-reviewed material. Links should support design reasoning, not replace repository explanations.

## ESP32 and ESP-IDF Primary References

| Topic | Primary source |
| --- | --- |
| ESP-IDF Programming Guide | https://docs.espressif.com/projects/esp-idf/en/latest/esp32/ |
| ESP32 Technical Reference Manual | https://www.espressif.com/en/support/documents/technical-documents |
| ESP32 Datasheet | https://www.espressif.com/en/support/documents/technical-documents |
| ESP-IDF ADC continuous driver | https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/adc_continuous.html |
| ESP-IDF FreeRTOS integration | https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/system/freertos.html |
| ESP-IDF GPTimer driver | https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/gptimer.html |
| ESP-IDF OTA APIs | https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/system/ota.html |
| ESP-IDF NVS APIs | https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/storage/nvs_flash.html |
| ESP-IDF I2C driver | https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/i2c.html |
| ESP-IDF sleep modes | https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/system/sleep_modes.html |

## Standards and Background

| Topic | Reference category |
| --- | --- |
| Sampling and aliasing | DSP textbooks, IEEE signal processing tutorials, ADC application notes. |
| I2C electrical recovery | NXP I2C-bus specification and user manual, sensor datasheets. |
| MQTT behavior | OASIS MQTT specification and broker documentation. |
| EMC/EMI | IEC/EN emissions and immunity standards applicable to product class. |
| Reliability testing | HALT/HASS guidance, environmental qualification procedures. |

## Reference Policy

- Prefer official documentation over blog posts.
- Use datasheets for electrical limits and timing requirements.
- Use standards for protocol behavior.
- Link benchmark methodology to instrument settings and raw captures when possible.
