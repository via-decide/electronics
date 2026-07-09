# Engineering References

## Purpose

References must prioritize primary engineering sources: official vendor documentation, datasheets, standards, application notes, peer-reviewed material, and books. Links support design reasoning; they do not replace repository explanations.

## Official ESP-IDF and ESP32 References
References must prioritize primary engineering sources: official vendor documentation, datasheets, standards, application notes, and peer-reviewed material. Links should support design reasoning, not replace repository explanations.

## ESP32 and ESP-IDF Primary References

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
- Use books and peer-reviewed or academic sources for theory.
- Link benchmark methodology to instrument settings and raw captures when possible.


## Validation ID to Reference Mapping

| Validation ID | Primary Reference |
| --- | --- |
| `adc_dma_nyquist_v1` | ESP-IDF ADC continuous driver, DSP sampling theory (Nyquist-Shannon) |
| `freertos_dual_core_v1` | ESP-IDF FreeRTOS SMP docs, task affinity and queue APIs |
| `deep_sleep_rtc_retention_v2` | ESP-IDF sleep modes, RTC memory documentation |
| `nvs_wear_leveling_v1` | ESP-IDF NVS API, flash wear leveling design notes |
| `hw_timer_isr_v1` | ESP-IDF GPTimer driver, ISR context rules |
| `bod_panic_suppression_v1` | ESP32 datasheet brownout detector section, power integrity app notes |
| `esp32_ota_bootstrap_v2` | ESP-IDF OTA API, partition table documentation |
| `mqtt_telemetry` / `mtls_x509_auth_v1` | OASIS MQTT 3.1.1 spec, ESP-IDF MQTT + mbedTLS docs |
| `i2c_recovery` | NXP I2C-bus specification v6.0, stuck bus recovery procedures |
| `mcpwm_bldc_foc_v1` | ESP-IDF MCPWM driver, BLDC motor control application notes |
| `twai_can_differential_v1` | ISO 11898 CAN specification, SN65HVD230 datasheet |
| `tflm_wakeword_v2` | TensorFlow Lite Micro documentation, ESP32 memory map |
| `lvgl_dma_pingpong_v2` | LVGL porting guide, ESP-IDF SPI master DMA docs |
