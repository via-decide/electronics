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

### `nltm_sensor_linearization_v1` — Factory Calibration
- Store calibration coefficients via NVS with CRC32 and schema versioning.
- Rate-limit calibration writes to prevent flash wear during manufacturing test loops.
- Ship safe defaults (gain=1.0, offset=0.0) for uncalibrated units.

### `esp32_ota_bootstrap_v2` — Field Update Safety
- Never allow a bad image to become permanently active.
- Health check must validate core services (Wi-Fi, MQTT, sensor init) before confirming image.
- OTA download must use HTTPS with server certificate pinning.
- Rollback partition must always contain a known-good image.

### `mtls_x509_auth_v1` — Certificate Provisioning
- Private keys loaded from encrypted filesystem partition, never compiled into firmware.
- Factory provisioning writes unique device cert + key pair during manufacturing.
- Certificate rotation requires OTA firmware update with new cert bundle.

### `mcpwm_bldc_foc_v1` — Motor Drive Safety
- Dead-time must be validated with oscilloscope on all three phase outputs before connecting motor.
- Shoot-through detection via current sense feedback and hardware fault pin.
- Emergency stop: disable all PWM outputs and engage brake resistor.

### `deep_sleep_rtc_retention_v2` — Battery-Powered Deployment
- Design supply for peak Wi-Fi TX current (up to 500 mA burst).
- Add bulk capacitors (100 µF+) near ESP32 VDD to absorb current transients.
- Sleep interval tunable via NVS configuration without firmware update.

### `bod_panic_suppression_v1` — Power Supply Design
- Never disable BOD in production firmware.
- Size cable gauge and trace width for peak current without violating BOD threshold.
- Log brownout events for field diagnosis of inadequate power supplies.

### `twai_can_differential_v1` — CAN Bus Deployment
- Require 120Ω termination resistors at each physical bus end.
- Verify differential voltage levels (CAN_H − CAN_L) with oscilloscope.
- Set CAN bus speed to match all nodes; mismatched baud rates corrupt the bus.

### `hw_crypto_aes_v2` — Security Hardening
- Enable flash encryption and secure boot in production builds.
- Validate AES output against NIST test vectors during manufacturing self-test.
- Disable JTAG in production efuses to prevent debug-port key extraction.
