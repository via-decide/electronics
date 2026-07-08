# Repository Roadmap

## Objective

Evolve the repository into a reusable engineering platform that supports learning, implementation, validation, and long-term maintenance.

## Documentation Maturity Stages

| Stage | Definition | Current focus |
| --- | --- | --- |
| 1. Structure | Canonical folders and repository-level README exist. | Complete. |
| 2. Coverage | Every implementation has theory, implementation, debugging, production, benchmark, and reference coverage. | In progress. |
| 3. Examples | Each subsystem has runnable minimal and production examples. | In progress. |
| 4. Validation | Hardware, stress, performance, and integration procedures are executable and repeatable. | In progress. |
| 5. Evidence | Measurements, captures, photos, and benchmark records are linked to documentation. | Planned. |
| 6. Production | Deployment, manufacturing, calibration, OTA, security, and certification procedures are complete. | Planned. |

## Priority Backlog

1. Add ESP32 example projects for ADC DMA, FreeRTOS task isolation, MQTT, OTA, deep sleep, I2C recovery, and timers.
2. Add editable diagrams for boot flow, ADC pipeline, task topology, MQTT state machine, OTA lifecycle, memory layout, interrupt flow, DMA pipeline, power architecture, and signal path.
3. Add hardware-validation templates for oscilloscope, logic analyzer, power analysis, and long-duration testing.
4. Add benchmark records for RAM, flash, CPU, timing, latency, throughput, power consumption, boot time, sampling accuracy, and network performance.
5. Expand platform support for STM32, Raspberry Pi, Linux tooling, and power electronics.
