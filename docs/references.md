# Engineering References

## Purpose

References must prioritize primary engineering sources: official vendor documentation, datasheets, standards, application notes, peer-reviewed material, and books. Links support design reasoning; they do not replace repository explanations.

## Official ESP-IDF and ESP32 References

| Topic | Primary source |
| --- | --- |
| ESP-IDF Programming Guide | https://docs.espressif.com/projects/esp-idf/en/latest/esp32/ |
| ESP32 technical documents and datasheets | https://www.espressif.com/en/support/documents/technical-documents |
| ADC continuous driver | https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/adc_continuous.html |
| FreeRTOS integration | https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/system/freertos.html |
| GPTimer driver | https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/gptimer.html |
| OTA APIs | https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/system/ota.html |
| NVS APIs | https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/storage/nvs_flash.html |
| I2C driver | https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/i2c.html |
| Sleep modes | https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/system/sleep_modes.html |

## Linux and Tooling References

| Topic | Primary source |
| --- | --- |
| Linux kernel documentation | https://docs.kernel.org/ |
| Device tree specification | https://www.devicetree.org/specifications/ |
| OpenOCD documentation | https://openocd.org/doc/html/ |
| GDB documentation | https://sourceware.org/gdb/documentation/ |

## Standards and Protocol References

| Topic | Reference |
| --- | --- |
| MQTT | OASIS MQTT standard documentation. |
| I2C | NXP I2C-bus specification and user manual. |
| USB | USB-IF specifications. |
| EMC/EMI | IEC, CISPR, FCC, and product-class-specific emissions and immunity standards. |
| Safety and reliability | Product-domain safety standards, HALT/HASS procedures, and environmental qualification requirements. |

## Academic Papers and Books

| Topic | Recommended source type |
| --- | --- |
| Sampling and aliasing | Digital signal processing textbooks and IEEE signal-processing tutorials. |
| Real-time systems | RTOS scheduling textbooks and real-time systems literature. |
| Power integrity | Power electronics textbooks, regulator datasheets, and vendor application notes. |
| Signal integrity | High-speed design books, mixed-signal layout references, and ADC application notes. |
| Reliability engineering | Reliability engineering textbooks and environmental test standards. |

## Reference Policy

- Prefer official documentation over blog posts.
- Use datasheets for electrical limits and timing requirements.
- Use standards for protocol behavior.
- Use books and peer-reviewed or academic sources for theory.
- Link benchmark methodology to instrument settings and raw captures when possible.
