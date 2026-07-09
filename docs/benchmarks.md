# Benchmarks and Measurement Methodology

## Purpose

Benchmarks document measurable performance and make engineering claims reproducible. Every benchmark must include hardware configuration, firmware version, test conditions, measurement method, result, and pass/fail criteria.
Benchmarks document measurable performance and make claims reproducible. Every benchmark must include hardware configuration, firmware version, test conditions, measurement method, and pass/fail criteria.

## Required Benchmark Fields

| Field | Description |
| --- | --- |
| Feature | Subsystem under test. |
| Firmware revision | Git commit or release tag. |
| Hardware revision | Board, ESP32 variant, sensor, regulator, wiring. |
| Configuration | Sample rate, queue depth, task priorities, radio state, sleep interval. |
| Instrumentation | Logic analyzer, oscilloscope, ESP logs, FreeRTOS trace, power analyzer. |
| Methodology | Steps to reproduce the measurement. |
| Result | Numeric measurement with units. |
| Acceptance criterion | Engineering threshold and rationale. |

## Required Metrics for Every Implementation

| Metric | Required record |
| --- | --- |
| RAM usage | Heap, stack high-water marks, DMA buffers, PSRAM/internal RAM split. |
| Flash usage | Binary size, partition use, OTA slot margin. |
| CPU usage | Task runtime, ISR frequency, idle percentage. |
| Timing | Period accuracy, jitter, missed deadlines, drift. |
| Latency | ISR-to-task latency, queue residence, publish delay, boot service readiness. |
| Throughput | Samples/s, bytes/s, MQTT messages/s, storage writes/s. |
| Power consumption | Active current, sleep current, radio burst dips, average current. |
| Boot time | Reset-to-main, reset-to-network, reset-to-first-sample. |
| Sampling accuracy | ADC timing, quantization assumptions, calibration error, signal distortion. |
| Network performance | Reconnect time, publish latency, drop rate, offline recovery. |
## Benchmark Categories

| Category | Measurements |
| --- | --- |
| CPU usage | Task runtime, ISR frequency, idle percentage. |
| RAM usage | Heap, stack high-water marks, DMA buffers, PSRAM use. |
| Flash usage | Binary size, partition use, OTA slot margin. |
| Throughput | Samples/s, bytes/s, MQTT messages/s, storage writes/s. |
| Latency | ISR-to-task latency, queue residence, publish delay, boot time. |
| Timing | Jitter, drift, missed deadlines, timer period accuracy. |
| Power | Active current, sleep current, radio burst dips, average current. |
| Reliability | Long-duration uptime, fault recovery time, reset count. |

## Initial Benchmark Matrix

| Feature | Benchmark required | Status |
| --- | --- | --- |
| ADC DMA continuous sampling | Sample-period jitter and DMA callback interval under Wi-Fi/MQTT load | Methodology pending hardware capture. |
| Hardware timer scheduler | 10 ms event jitter under logging load | Methodology pending hardware capture. |
| MQTT telemetry | Queue drops and reconnect recovery time during broker outage | Methodology pending network test. |
| I2C recovery | Recovery success after simulated SDA-low fault | Methodology pending hardware fixture. |
| Deep sleep node | Active time, sleep current, average current estimate | Methodology pending power analyzer. |
| OTA manager | Download failure behavior, rollback confirmation, boot timing | Methodology pending OTA test fixture. |
| NVS calibration | Load/save latency, CRC rejection behavior, flash wear policy | Methodology pending NVS test. |


## Subsystem Benchmark Specifications

### `adc_dma_nyquist_v1`
| Metric | Target | Measurement Method |
| --- | --- | --- |
| Sample rate | 2000 Hz ± 1% | Oscilloscope on ADC input + callback timestamp delta |
| Callback jitter | < 50 µs | Standard deviation of callback intervals over 10,000 samples |
| Nyquist margin | F_max ≤ 800 Hz | Signal generator sweep, verify no aliasing |

### `freertos_dual_core_v1`
| Metric | Target | Measurement Method |
| --- | --- | --- |
| Queue overflow count | 0 | Monitor counter during 60s Wi-Fi stress test |
| Acquisition task CPU | < 15% Core 0 | `vTaskGetRunTimeStats()` |
| Watchdog false positives | 0 | Count during network reconnection cycles |

### `deep_sleep_rtc_retention_v2`
| Metric | Target | Measurement Method |
| --- | --- | --- |
| Sleep current | ≤ 20 µA | Current probe on supply during sleep phase |
| Active current | ≤ 100 mA | Current probe during sample + transmit |
| Wake-to-sleep cycle | ≤ 15s | Boot timestamp to sleep entry timestamp |
| RTC counter survival | 100% | Verify counter increments across 100 wake cycles |

### `hw_timer_isr_v1`
| Metric | Target | Measurement Method |
| --- | --- | --- |
| ISR latency | < 2.5 µs | GPIO toggle in ISR, measure with oscilloscope |
| Missed deadlines | 0 | Queue overflow counter over 60s at 100 Hz |
| Period accuracy | 10.000 ms ± 0.1% | Oscilloscope period measurement |

### `spi_dma_throughput_v2`
| Metric | Target | Measurement Method |
| --- | --- | --- |
| DMA throughput | ≥ 4 MB/s at 40 MHz | Transfer known buffer, measure wall-clock time |
| CPU utilization during DMA | < 5% | `vTaskGetRunTimeStats()` during transfer |

### `tflm_wakeword_v2`
| Metric | Target | Measurement Method |
| --- | --- | --- |
| Model arena RAM | < 100 KB | TFLM arena size report |
| Inference latency | < 200 ms | Timer around `interpreter->Invoke()` |
| Flash footprint | < 300 KB | Partition map / `size` output |

### `ota_bootstrap_v2`
| Metric | Target | Measurement Method |
| --- | --- | --- |
| Download + flash time | < 60s on LAN | Timer from OTA start to reboot |
| Rollback trigger time | < 5s | Timer from boot to rollback decision |
| Bad image persistence | 0 (never permanent) | Force health check failure, verify rollback |

### `lvgl_dma_pingpong_v2`
| Metric | Target | Measurement Method |
| --- | --- | --- |
| Frame rate | ≥ 30 FPS | LVGL `lv_tick_get()` delta per frame |
| Tearing | 0 visible | Visual inspection during scroll test |
| DMA CPU overhead | < 10% | `vTaskGetRunTimeStats()` during rendering |
