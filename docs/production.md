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
