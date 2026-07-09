# Implementation Architecture

## Purpose

This document defines how implementation knowledge is organized for the repository. It explains where firmware architecture, driver usage, peripheral interaction, memory model, RTOS behavior, and code organization are documented.

## Standard Repository Layout

```text
docs/
  theory.md
  implementation.md
  debugging.md
  production.md
  benchmarks.md
  references.md
examples/
  README.md
  esp32/
  stm32/
  raspberry-pi/
  linux/
  power-electronics/
  minimal/
  production/
  advanced/
tests/
  unit/
  integration/
  stress/
  hardware/
  hardware-validation/
  performance/
diagrams/
  architecture/
  state-machines/
  signal-flow/
  hardware-validation/
diagrams/
  architecture/
  state-machines/
  data_flow/
  timing/
  pcb/
assets/
  images/
  oscilloscope/
  logic-analyzer/
  thermal/
  pcb/
  photos/
  logic-analyzer/
  datasheets/
  captures/
```

## Implementation Documentation Responsibilities

Implementation documentation must describe:

- ESP-IDF components and driver ownership.
- Peripheral interaction and initialization order.
- Firmware control flow and task topology.
- ISR-to-task boundaries.
- Queue, ring-buffer, and DMA ownership rules.
- Stack, heap, DMA-capable memory, PSRAM, and alignment constraints.
- Error handling, retries, and recovery paths.
- Code organization and integration points.

## ESP32 Architecture Pattern

```text
Application policy
    ↓
Feature service API
    ↓
FreeRTOS tasks / queues / event groups
    ↓
ESP-IDF drivers
    ↓
ESP32 peripherals
    ↓
External sensors, radios, storage, and power system
```

Time-critical work must be owned by peripherals, hardware timers, DMA, or high-priority tasks. Network, storage, logging, and JSON processing must not be part of sampling or control timing loops.

## Feature Registry

| Feature | Implementation file | Learning document |
| --- | --- | --- |
| Continuous ADC DMA sampling | `firmware/esp32/adc_dma_continuous.c` | `docs/esp32/adc_dma_continuous.md` |
| FreeRTOS task isolation | `firmware/esp32/task_topology.c` | Pending feature document |
| Non-blocking MQTT telemetry | `firmware/esp32/mqtt_telemetry.c` | Pending feature document |
| NVS calibration store | `firmware/esp32/nvs_calibration.c` | Pending feature document |
| Rollback-safe OTA | `firmware/esp32/ota_manager.c` | Pending feature document |
| Brownout diagnostics | `firmware/esp32/power_diagnostics.c` | Pending feature document |
| Deep-sleep sensor node | `firmware/esp32/deep_sleep_node.c` | Pending feature document |
| I2C bus recovery | `firmware/esp32/i2c_recovery.c` | Pending feature document |
| Hardware timer scheduler | `firmware/esp32/hardware_timer_scheduler.c` | Pending feature document |

## Synchronization Requirement

When implementation changes, the corresponding documentation must be updated in the same change set. Repository validation should fail when required documentation files or directories are missing.


## Runnable Example Standard

Subsystem examples must be independently buildable when the target SDK is installed. ESP32 examples use normal ESP-IDF project structure with `CMakeLists.txt`, `sdkconfig.defaults`, and a `main/` component that invokes the related repository firmware module.

## Validation Hierarchy Standard

Tests are organized by purpose: unit tests for host-testable logic, integration tests for component interaction, hardware tests for instrumented boards, performance tests for measured resource and timing behavior, and stress tests for long-duration or fault-injection scenarios.


## Subsystem Implementation Details

### `adc_dma_continuous` — DMA Ring Buffer Pipeline
- Uses `adc_continuous_new_handle()` with 1024-byte DMA pool.
- Half/full callbacks deliver 512-byte frames to a FreeRTOS queue (depth 8).
- DSP and MQTT work is deferred to consumer tasks — never in the DMA callback.
- GPIO34 (ADC1_CH6), attenuation 11dB, max bitwidth.

### `task_topology` — FreeRTOS Task Isolation
- Acquisition → raw queue (depth 64) → DSP → telemetry queue → MQTT.
- Each task pinned to specific core: acquisition on Core 0, networking on Core 1.
- Watchdog supervisor runs at 1 Hz, detects stale acquisition within 250 ms.
- `TASK_TOPOLOGY_ACQUIRE_PERIOD_MS = 10` (100 Hz acquisition rate).

### `deep_sleep_node` — Low-Power Sensor Cycle
- Uses `esp_deep_sleep_start()` with timer wake at 300s intervals.
- Wi-Fi connection bounded to 8s timeout with 100 ms poll interval.
- RTC_DATA_ATTR variables retain boot count and measurement state.
- Peripheral power-up warmup: 500 ms before sensor read.

### `nvs_calibration` — Versioned Blob Storage
- Packed struct: magic (4B) + schema_version (1B) + gain (4B) + offset (4B) + CRC32 (4B).
- Namespace: `sensor_cal`, key: `cal_v1`.
- CRC seed: `0xFFFFFFFF`. Verification rejects mismatched magic, schema, or CRC.

### `ota_manager` — Rollback-Safe Update Flow
- Downloads to inactive OTA partition while active partition remains bootable.
- Image verification via `esp_https_ota()` with hash check.
- Trial boot with health check timeout before `esp_ota_mark_app_valid_cancel_rollback()`.
- Failed health check triggers `esp_ota_mark_app_invalid_rollback_and_reboot()`.

### `mqtt_telemetry` — Non-Blocking Publish State Machine
- Queue depth 128, payload 256B, topic 96B per message.
- State machine: disconnected → connecting → connected → publishing.
- Exponential backoff on connection failure. Drop oldest on queue full.
- Task priority: `tskIDLE_PRIORITY + 1` (lowest non-idle).

### `hardware_timer_scheduler` — GPTimer ISR-to-Task Handoff
- Resolution: 1 MHz clock. Alarm period: configurable (default 10 ms).
- ISR is IRAM-safe: timestamps and enqueues only. Queue depth 16.
- Worker task priority: `tskIDLE_PRIORITY + 4` (above MQTT, below acquisition).
- Missed deadline counter: incremented on `xQueueSendFromISR` failure.

### `power_diagnostics` — Boot Fault Classification
- Reads `esp_reset_reason()` on every boot.
- Persists per-type counters in NVS namespace `power_diag`.
- Tracks: boot_count, brownouts, wdt_resets, panic_resets, wifi_stress.
- Optionally publishes fault history over MQTT telemetry.

### `i2c_recovery` — Stuck Bus Self-Healing
- Detects stuck SDA/SCL via GPIO read after I2C timeout.
- Recovery: delete I2C driver → reconfigure as open-drain GPIO → pulse SCL 9 times → generate STOP → reinstall driver.
- Retry budget: 3 attempts before reporting hard sensor fault.
- Default config: I2C_NUM_0, SDA=GPIO21, SCL=GPIO22, 100 kHz.
