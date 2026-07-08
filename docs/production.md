# Production Engineering Guide

## Purpose

This document captures production constraints that must be considered before firmware or hardware features are deployed to field devices.

## Production Responsibility Areas

| Area | Required considerations |
| --- | --- |
| Manufacturing | Programming flow, serial numbers, test fixtures, calibration, traceability. |
| Calibration | Versioned coefficients, CRC validation, default fallback, lot variation. |
| OTA | Dual partitions, image verification, boot confirmation, rollback, version metadata. |
| Security | TLS credentials, key storage, secure boot, flash encryption, credential rotation. |
| Reliability | Watchdog policy, brownout diagnostics, bus recovery, long-duration stress testing. |
| EMC/EMI | Cable routing, filtering, shielding, ground return, radio coexistence. |
| Telemetry | Non-blocking publish, bounded queues, metrics, offline policy. |
| Versioning | Firmware version, schema version, hardware revision, migration plan. |

## Deployment Checklist

- [ ] Feature has theory, implementation, debugging, production, benchmark, and reference documentation.
- [ ] Build and hardware validation results are recorded.
- [ ] Fault injection cases have been executed.
- [ ] Metrics and diagnostics are exposed.
- [ ] Safe defaults exist for missing or corrupt persistent data.
- [ ] OTA rollback path is validated before field release.
- [ ] Power integrity has been measured under radio, sensor, and storage load.
- [ ] Manufacturing programming and calibration procedures are documented.

## Field Observability

Production firmware should expose enough metrics to distinguish firmware bugs from environmental or hardware faults:

```text
reset_reason
boot_count
brownout_count
watchdog_count
queue_overflow_count
mqtt_drop_count
ota_state
calibration_schema
heap_free_minimum
last_error_code
```

## Subsystem Production Guidelines

### Production Guidelines: `esp32_core_installation_v1`
- **Validation ID Reference**: `esp32_core_installation_v1`
- **Manufacturing & Calibration**:
  Specifies NVS wear-leveling limits, factory calibration offset calculations, and firmware OTA update safety partitions.
- **Reliability Criteria**:
  Maintains system integrity under operational stress (e.g. brownout panic suppression levels).

### Production Guidelines: `esp32_hall_diagnostic_v1`
- **Validation ID Reference**: `esp32_hall_diagnostic_v1`
- **Manufacturing & Calibration**:
  Specifies NVS wear-leveling limits, factory calibration offset calculations, and firmware OTA update safety partitions.
- **Reliability Criteria**:
  Maintains system integrity under operational stress (e.g. brownout panic suppression levels).

### Production Guidelines: `nltm_sensor_linearization_v1`
- **Validation ID Reference**: `nltm_sensor_linearization_v1`
- **Manufacturing & Calibration**:
  Specifies NVS wear-leveling limits, factory calibration offset calculations, and firmware OTA update safety partitions.
- **Reliability Criteria**:
  Maintains system integrity under operational stress (e.g. brownout panic suppression levels).

### Production Guidelines: `logic_level_shift_v2`
- **Validation ID Reference**: `logic_level_shift_v2`
- **Manufacturing & Calibration**:
  Specifies NVS wear-leveling limits, factory calibration offset calculations, and firmware OTA update safety partitions.
- **Reliability Criteria**:
  Maintains system integrity under operational stress (e.g. brownout panic suppression levels).

### Production Guidelines: `ledc_pwm_matrix_v1`
- **Validation ID Reference**: `ledc_pwm_matrix_v1`
- **Manufacturing & Calibration**:
  Specifies NVS wear-leveling limits, factory calibration offset calculations, and firmware OTA update safety partitions.
- **Reliability Criteria**:
  Maintains system integrity under operational stress (e.g. brownout panic suppression levels).

### Production Guidelines: `cap_touch_iir_v1`
- **Validation ID Reference**: `cap_touch_iir_v1`
- **Manufacturing & Calibration**:
  Specifies NVS wear-leveling limits, factory calibration offset calculations, and firmware OTA update safety partitions.
- **Reliability Criteria**:
  Maintains system integrity under operational stress (e.g. brownout panic suppression levels).

### Production Guidelines: `freertos_dual_core_v1`
- **Validation ID Reference**: `freertos_dual_core_v1`
- **Manufacturing & Calibration**:
  Specifies NVS wear-leveling limits, factory calibration offset calculations, and firmware OTA update safety partitions.
- **Reliability Criteria**:
  Maintains system integrity under operational stress (e.g. brownout panic suppression levels).

### Production Guidelines: `deep_sleep_rtc_retention_v2`
- **Validation ID Reference**: `deep_sleep_rtc_retention_v2`
- **Manufacturing & Calibration**:
  Specifies NVS wear-leveling limits, factory calibration offset calculations, and firmware OTA update safety partitions.
- **Reliability Criteria**:
  Maintains system integrity under operational stress (e.g. brownout panic suppression levels).

### Production Guidelines: `nvs_wear_leveling_v1`
- **Validation ID Reference**: `nvs_wear_leveling_v1`
- **Manufacturing & Calibration**:
  Specifies NVS wear-leveling limits, factory calibration offset calculations, and firmware OTA update safety partitions.
- **Reliability Criteria**:
  Maintains system integrity under operational stress (e.g. brownout panic suppression levels).

### Production Guidelines: `hw_timer_isr_v1`
- **Validation ID Reference**: `hw_timer_isr_v1`
- **Manufacturing & Calibration**:
  Specifies NVS wear-leveling limits, factory calibration offset calculations, and firmware OTA update safety partitions.
- **Reliability Criteria**:
  Maintains system integrity under operational stress (e.g. brownout panic suppression levels).

### Production Guidelines: `bod_panic_suppression_v1`
- **Validation ID Reference**: `bod_panic_suppression_v1`
- **Manufacturing & Calibration**:
  Specifies NVS wear-leveling limits, factory calibration offset calculations, and firmware OTA update safety partitions.
- **Reliability Criteria**:
  Maintains system integrity under operational stress (e.g. brownout panic suppression levels).

### Production Guidelines: `ulp_fsm_assembly_v1`
- **Validation ID Reference**: `ulp_fsm_assembly_v1`
- **Manufacturing & Calibration**:
  Specifies NVS wear-leveling limits, factory calibration offset calculations, and firmware OTA update safety partitions.
- **Reliability Criteria**:
  Maintains system integrity under operational stress (e.g. brownout panic suppression levels).

### Production Guidelines: `i2s_dma_audio_v1`
- **Validation ID Reference**: `i2s_dma_audio_v1`
- **Manufacturing & Calibration**:
  Specifies NVS wear-leveling limits, factory calibration offset calculations, and firmware OTA update safety partitions.
- **Reliability Criteria**:
  Maintains system integrity under operational stress (e.g. brownout panic suppression levels).

### Production Guidelines: `adc_dma_nyquist_v1`
- **Validation ID Reference**: `adc_dma_nyquist_v1`
- **Manufacturing & Calibration**:
  Specifies NVS wear-leveling limits, factory calibration offset calculations, and firmware OTA update safety partitions.
- **Reliability Criteria**:
  Maintains system integrity under operational stress (e.g. brownout panic suppression levels).

### Production Guidelines: `spi_dma_throughput_v2`
- **Validation ID Reference**: `spi_dma_throughput_v2`
- **Manufacturing & Calibration**:
  Specifies NVS wear-leveling limits, factory calibration offset calculations, and firmware OTA update safety partitions.
- **Reliability Criteria**:
  Maintains system integrity under operational stress (e.g. brownout panic suppression levels).

### Production Guidelines: `esp32_ota_bootstrap_v2`
- **Validation ID Reference**: `esp32_ota_bootstrap_v2`
- **Manufacturing & Calibration**:
  Specifies NVS wear-leveling limits, factory calibration offset calculations, and firmware OTA update safety partitions.
- **Reliability Criteria**:
  Maintains system integrity under operational stress (e.g. brownout panic suppression levels).

### Production Guidelines: `esp_now_p2p_v2`
- **Validation ID Reference**: `esp_now_p2p_v2`
- **Manufacturing & Calibration**:
  Specifies NVS wear-leveling limits, factory calibration offset calculations, and firmware OTA update safety partitions.
- **Reliability Criteria**:
  Maintains system integrity under operational stress (e.g. brownout panic suppression levels).

### Production Guidelines: `async_web_littlefs_v1`
- **Validation ID Reference**: `async_web_littlefs_v1`
- **Manufacturing & Calibration**:
  Specifies NVS wear-leveling limits, factory calibration offset calculations, and firmware OTA update safety partitions.
- **Reliability Criteria**:
  Maintains system integrity under operational stress (e.g. brownout panic suppression levels).

### Production Guidelines: `hw_crypto_aes_v2`
- **Validation ID Reference**: `hw_crypto_aes_v2`
- **Manufacturing & Calibration**:
  Specifies NVS wear-leveling limits, factory calibration offset calculations, and firmware OTA update safety partitions.
- **Reliability Criteria**:
  Maintains system integrity under operational stress (e.g. brownout panic suppression levels).

### Production Guidelines: `mtls_x509_auth_v1`
- **Validation ID Reference**: `mtls_x509_auth_v1`
- **Manufacturing & Calibration**:
  Specifies NVS wear-leveling limits, factory calibration offset calculations, and firmware OTA update safety partitions.
- **Reliability Criteria**:
  Maintains system integrity under operational stress (e.g. brownout panic suppression levels).

### Production Guidelines: `jtag_openocd_v1`
- **Validation ID Reference**: `jtag_openocd_v1`
- **Manufacturing & Calibration**:
  Specifies NVS wear-leveling limits, factory calibration offset calculations, and firmware OTA update safety partitions.
- **Reliability Criteria**:
  Maintains system integrity under operational stress (e.g. brownout panic suppression levels).

### Production Guidelines: `tflm_wakeword_v2`
- **Validation ID Reference**: `tflm_wakeword_v2`
- **Manufacturing & Calibration**:
  Specifies NVS wear-leveling limits, factory calibration offset calculations, and firmware OTA update safety partitions.
- **Reliability Criteria**:
  Maintains system integrity under operational stress (e.g. brownout panic suppression levels).

### Production Guidelines: `mcpwm_bldc_foc_v1`
- **Validation ID Reference**: `mcpwm_bldc_foc_v1`
- **Manufacturing & Calibration**:
  Specifies NVS wear-leveling limits, factory calibration offset calculations, and firmware OTA update safety partitions.
- **Reliability Criteria**:
  Maintains system integrity under operational stress (e.g. brownout panic suppression levels).

### Production Guidelines: `twai_can_differential_v1`
- **Validation ID Reference**: `twai_can_differential_v1`
- **Manufacturing & Calibration**:
  Specifies NVS wear-leveling limits, factory calibration offset calculations, and firmware OTA update safety partitions.
- **Reliability Criteria**:
  Maintains system integrity under operational stress (e.g. brownout panic suppression levels).

### Production Guidelines: `lvgl_dma_pingpong_v2`
- **Validation ID Reference**: `lvgl_dma_pingpong_v2`
- **Manufacturing & Calibration**:
  Specifies NVS wear-leveling limits, factory calibration offset calculations, and firmware OTA update safety partitions.
- **Reliability Criteria**:
  Maintains system integrity under operational stress (e.g. brownout panic suppression levels).

