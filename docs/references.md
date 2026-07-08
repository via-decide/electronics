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

## Reference Mapping by Validation ID

### Reference Citations: `esp32_core_installation_v1`
- **Validation ID**: `esp32_core_installation_v1`
- Espressif Technical Reference Manual (Chapter: SPI/I2C/ADC/RTOS depending on module).
- NXP I2C Bus Specification v6.0.
- IEEE Standard for Floating-Point Arithmetic (IEEE 754).

### Reference Citations: `esp32_hall_diagnostic_v1`
- **Validation ID**: `esp32_hall_diagnostic_v1`
- Espressif Technical Reference Manual (Chapter: SPI/I2C/ADC/RTOS depending on module).
- NXP I2C Bus Specification v6.0.
- IEEE Standard for Floating-Point Arithmetic (IEEE 754).

### Reference Citations: `nltm_sensor_linearization_v1`
- **Validation ID**: `nltm_sensor_linearization_v1`
- Espressif Technical Reference Manual (Chapter: SPI/I2C/ADC/RTOS depending on module).
- NXP I2C Bus Specification v6.0.
- IEEE Standard for Floating-Point Arithmetic (IEEE 754).

### Reference Citations: `logic_level_shift_v2`
- **Validation ID**: `logic_level_shift_v2`
- Espressif Technical Reference Manual (Chapter: SPI/I2C/ADC/RTOS depending on module).
- NXP I2C Bus Specification v6.0.
- IEEE Standard for Floating-Point Arithmetic (IEEE 754).

### Reference Citations: `ledc_pwm_matrix_v1`
- **Validation ID**: `ledc_pwm_matrix_v1`
- Espressif Technical Reference Manual (Chapter: SPI/I2C/ADC/RTOS depending on module).
- NXP I2C Bus Specification v6.0.
- IEEE Standard for Floating-Point Arithmetic (IEEE 754).

### Reference Citations: `cap_touch_iir_v1`
- **Validation ID**: `cap_touch_iir_v1`
- Espressif Technical Reference Manual (Chapter: SPI/I2C/ADC/RTOS depending on module).
- NXP I2C Bus Specification v6.0.
- IEEE Standard for Floating-Point Arithmetic (IEEE 754).

### Reference Citations: `freertos_dual_core_v1`
- **Validation ID**: `freertos_dual_core_v1`
- Espressif Technical Reference Manual (Chapter: SPI/I2C/ADC/RTOS depending on module).
- NXP I2C Bus Specification v6.0.
- IEEE Standard for Floating-Point Arithmetic (IEEE 754).

### Reference Citations: `deep_sleep_rtc_retention_v2`
- **Validation ID**: `deep_sleep_rtc_retention_v2`
- Espressif Technical Reference Manual (Chapter: SPI/I2C/ADC/RTOS depending on module).
- NXP I2C Bus Specification v6.0.
- IEEE Standard for Floating-Point Arithmetic (IEEE 754).

### Reference Citations: `nvs_wear_leveling_v1`
- **Validation ID**: `nvs_wear_leveling_v1`
- Espressif Technical Reference Manual (Chapter: SPI/I2C/ADC/RTOS depending on module).
- NXP I2C Bus Specification v6.0.
- IEEE Standard for Floating-Point Arithmetic (IEEE 754).

### Reference Citations: `hw_timer_isr_v1`
- **Validation ID**: `hw_timer_isr_v1`
- Espressif Technical Reference Manual (Chapter: SPI/I2C/ADC/RTOS depending on module).
- NXP I2C Bus Specification v6.0.
- IEEE Standard for Floating-Point Arithmetic (IEEE 754).

### Reference Citations: `bod_panic_suppression_v1`
- **Validation ID**: `bod_panic_suppression_v1`
- Espressif Technical Reference Manual (Chapter: SPI/I2C/ADC/RTOS depending on module).
- NXP I2C Bus Specification v6.0.
- IEEE Standard for Floating-Point Arithmetic (IEEE 754).

### Reference Citations: `ulp_fsm_assembly_v1`
- **Validation ID**: `ulp_fsm_assembly_v1`
- Espressif Technical Reference Manual (Chapter: SPI/I2C/ADC/RTOS depending on module).
- NXP I2C Bus Specification v6.0.
- IEEE Standard for Floating-Point Arithmetic (IEEE 754).

### Reference Citations: `i2s_dma_audio_v1`
- **Validation ID**: `i2s_dma_audio_v1`
- Espressif Technical Reference Manual (Chapter: SPI/I2C/ADC/RTOS depending on module).
- NXP I2C Bus Specification v6.0.
- IEEE Standard for Floating-Point Arithmetic (IEEE 754).

### Reference Citations: `adc_dma_nyquist_v1`
- **Validation ID**: `adc_dma_nyquist_v1`
- Espressif Technical Reference Manual (Chapter: SPI/I2C/ADC/RTOS depending on module).
- NXP I2C Bus Specification v6.0.
- IEEE Standard for Floating-Point Arithmetic (IEEE 754).

### Reference Citations: `spi_dma_throughput_v2`
- **Validation ID**: `spi_dma_throughput_v2`
- Espressif Technical Reference Manual (Chapter: SPI/I2C/ADC/RTOS depending on module).
- NXP I2C Bus Specification v6.0.
- IEEE Standard for Floating-Point Arithmetic (IEEE 754).

### Reference Citations: `esp32_ota_bootstrap_v2`
- **Validation ID**: `esp32_ota_bootstrap_v2`
- Espressif Technical Reference Manual (Chapter: SPI/I2C/ADC/RTOS depending on module).
- NXP I2C Bus Specification v6.0.
- IEEE Standard for Floating-Point Arithmetic (IEEE 754).

### Reference Citations: `esp_now_p2p_v2`
- **Validation ID**: `esp_now_p2p_v2`
- Espressif Technical Reference Manual (Chapter: SPI/I2C/ADC/RTOS depending on module).
- NXP I2C Bus Specification v6.0.
- IEEE Standard for Floating-Point Arithmetic (IEEE 754).

### Reference Citations: `async_web_littlefs_v1`
- **Validation ID**: `async_web_littlefs_v1`
- Espressif Technical Reference Manual (Chapter: SPI/I2C/ADC/RTOS depending on module).
- NXP I2C Bus Specification v6.0.
- IEEE Standard for Floating-Point Arithmetic (IEEE 754).

### Reference Citations: `hw_crypto_aes_v2`
- **Validation ID**: `hw_crypto_aes_v2`
- Espressif Technical Reference Manual (Chapter: SPI/I2C/ADC/RTOS depending on module).
- NXP I2C Bus Specification v6.0.
- IEEE Standard for Floating-Point Arithmetic (IEEE 754).

### Reference Citations: `mtls_x509_auth_v1`
- **Validation ID**: `mtls_x509_auth_v1`
- Espressif Technical Reference Manual (Chapter: SPI/I2C/ADC/RTOS depending on module).
- NXP I2C Bus Specification v6.0.
- IEEE Standard for Floating-Point Arithmetic (IEEE 754).

### Reference Citations: `jtag_openocd_v1`
- **Validation ID**: `jtag_openocd_v1`
- Espressif Technical Reference Manual (Chapter: SPI/I2C/ADC/RTOS depending on module).
- NXP I2C Bus Specification v6.0.
- IEEE Standard for Floating-Point Arithmetic (IEEE 754).

### Reference Citations: `tflm_wakeword_v2`
- **Validation ID**: `tflm_wakeword_v2`
- Espressif Technical Reference Manual (Chapter: SPI/I2C/ADC/RTOS depending on module).
- NXP I2C Bus Specification v6.0.
- IEEE Standard for Floating-Point Arithmetic (IEEE 754).

### Reference Citations: `mcpwm_bldc_foc_v1`
- **Validation ID**: `mcpwm_bldc_foc_v1`
- Espressif Technical Reference Manual (Chapter: SPI/I2C/ADC/RTOS depending on module).
- NXP I2C Bus Specification v6.0.
- IEEE Standard for Floating-Point Arithmetic (IEEE 754).

### Reference Citations: `twai_can_differential_v1`
- **Validation ID**: `twai_can_differential_v1`
- Espressif Technical Reference Manual (Chapter: SPI/I2C/ADC/RTOS depending on module).
- NXP I2C Bus Specification v6.0.
- IEEE Standard for Floating-Point Arithmetic (IEEE 754).

### Reference Citations: `lvgl_dma_pingpong_v2`
- **Validation ID**: `lvgl_dma_pingpong_v2`
- Espressif Technical Reference Manual (Chapter: SPI/I2C/ADC/RTOS depending on module).
- NXP I2C Bus Specification v6.0.
- IEEE Standard for Floating-Point Arithmetic (IEEE 754).

