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
  hardware_validation/
diagrams/
  architecture/
  state_machine/
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
  logic_analyzer/
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
