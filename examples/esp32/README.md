# ESP32 Examples

ESP32 examples should be independently buildable ESP-IDF projects or clearly scoped components with build instructions.

| Subdirectory | Subsystem |
| --- | --- |
| `adc_dma/` | Hardware-timed ADC sampling and DMA buffering. |
| `freertos/` | Task isolation, queues, watchdog supervision, and priority design. |
| `mqtt/` | Non-blocking telemetry and network state machines. |
| `ota/` | Rollback-safe OTA lifecycle examples. |
| `deep_sleep/` | Battery sensor-node wake/sample/publish/sleep cycles. |
| `i2c/` | Stuck-bus detection and recovery. |
| `timers/` | Hardware timer scheduling and ISR-to-task handoff. |
