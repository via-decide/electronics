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

## Subsystem Performance Benchmarks

### Performance Benchmarks: `esp32_core_installation_v1`
- **Validation ID Reference**: `esp32_core_installation_v1`
- **Resource Footprint**:
  - Flash Occupancy: 12KB - 45KB.
  - Heap SRAM Allocation: 4KB - 16KB.
  - CPU Utilization: < 15% on Core 0.
- **Timing Benchmarks**:
  - ISR Latency: < 2.5 microseconds.
  - Wakeup duration: < 100 milliseconds.

### Performance Benchmarks: `esp32_hall_diagnostic_v1`
- **Validation ID Reference**: `esp32_hall_diagnostic_v1`
- **Resource Footprint**:
  - Flash Occupancy: 12KB - 45KB.
  - Heap SRAM Allocation: 4KB - 16KB.
  - CPU Utilization: < 15% on Core 0.
- **Timing Benchmarks**:
  - ISR Latency: < 2.5 microseconds.
  - Wakeup duration: < 100 milliseconds.

### Performance Benchmarks: `nltm_sensor_linearization_v1`
- **Validation ID Reference**: `nltm_sensor_linearization_v1`
- **Resource Footprint**:
  - Flash Occupancy: 12KB - 45KB.
  - Heap SRAM Allocation: 4KB - 16KB.
  - CPU Utilization: < 15% on Core 0.
- **Timing Benchmarks**:
  - ISR Latency: < 2.5 microseconds.
  - Wakeup duration: < 100 milliseconds.

### Performance Benchmarks: `logic_level_shift_v2`
- **Validation ID Reference**: `logic_level_shift_v2`
- **Resource Footprint**:
  - Flash Occupancy: 12KB - 45KB.
  - Heap SRAM Allocation: 4KB - 16KB.
  - CPU Utilization: < 15% on Core 0.
- **Timing Benchmarks**:
  - ISR Latency: < 2.5 microseconds.
  - Wakeup duration: < 100 milliseconds.

### Performance Benchmarks: `ledc_pwm_matrix_v1`
- **Validation ID Reference**: `ledc_pwm_matrix_v1`
- **Resource Footprint**:
  - Flash Occupancy: 12KB - 45KB.
  - Heap SRAM Allocation: 4KB - 16KB.
  - CPU Utilization: < 15% on Core 0.
- **Timing Benchmarks**:
  - ISR Latency: < 2.5 microseconds.
  - Wakeup duration: < 100 milliseconds.

### Performance Benchmarks: `cap_touch_iir_v1`
- **Validation ID Reference**: `cap_touch_iir_v1`
- **Resource Footprint**:
  - Flash Occupancy: 12KB - 45KB.
  - Heap SRAM Allocation: 4KB - 16KB.
  - CPU Utilization: < 15% on Core 0.
- **Timing Benchmarks**:
  - ISR Latency: < 2.5 microseconds.
  - Wakeup duration: < 100 milliseconds.

### Performance Benchmarks: `freertos_dual_core_v1`
- **Validation ID Reference**: `freertos_dual_core_v1`
- **Resource Footprint**:
  - Flash Occupancy: 12KB - 45KB.
  - Heap SRAM Allocation: 4KB - 16KB.
  - CPU Utilization: < 15% on Core 0.
- **Timing Benchmarks**:
  - ISR Latency: < 2.5 microseconds.
  - Wakeup duration: < 100 milliseconds.

### Performance Benchmarks: `deep_sleep_rtc_retention_v2`
- **Validation ID Reference**: `deep_sleep_rtc_retention_v2`
- **Resource Footprint**:
  - Flash Occupancy: 12KB - 45KB.
  - Heap SRAM Allocation: 4KB - 16KB.
  - CPU Utilization: < 15% on Core 0.
- **Timing Benchmarks**:
  - ISR Latency: < 2.5 microseconds.
  - Wakeup duration: < 100 milliseconds.

### Performance Benchmarks: `nvs_wear_leveling_v1`
- **Validation ID Reference**: `nvs_wear_leveling_v1`
- **Resource Footprint**:
  - Flash Occupancy: 12KB - 45KB.
  - Heap SRAM Allocation: 4KB - 16KB.
  - CPU Utilization: < 15% on Core 0.
- **Timing Benchmarks**:
  - ISR Latency: < 2.5 microseconds.
  - Wakeup duration: < 100 milliseconds.

### Performance Benchmarks: `hw_timer_isr_v1`
- **Validation ID Reference**: `hw_timer_isr_v1`
- **Resource Footprint**:
  - Flash Occupancy: 12KB - 45KB.
  - Heap SRAM Allocation: 4KB - 16KB.
  - CPU Utilization: < 15% on Core 0.
- **Timing Benchmarks**:
  - ISR Latency: < 2.5 microseconds.
  - Wakeup duration: < 100 milliseconds.

### Performance Benchmarks: `bod_panic_suppression_v1`
- **Validation ID Reference**: `bod_panic_suppression_v1`
- **Resource Footprint**:
  - Flash Occupancy: 12KB - 45KB.
  - Heap SRAM Allocation: 4KB - 16KB.
  - CPU Utilization: < 15% on Core 0.
- **Timing Benchmarks**:
  - ISR Latency: < 2.5 microseconds.
  - Wakeup duration: < 100 milliseconds.

### Performance Benchmarks: `ulp_fsm_assembly_v1`
- **Validation ID Reference**: `ulp_fsm_assembly_v1`
- **Resource Footprint**:
  - Flash Occupancy: 12KB - 45KB.
  - Heap SRAM Allocation: 4KB - 16KB.
  - CPU Utilization: < 15% on Core 0.
- **Timing Benchmarks**:
  - ISR Latency: < 2.5 microseconds.
  - Wakeup duration: < 100 milliseconds.

### Performance Benchmarks: `i2s_dma_audio_v1`
- **Validation ID Reference**: `i2s_dma_audio_v1`
- **Resource Footprint**:
  - Flash Occupancy: 12KB - 45KB.
  - Heap SRAM Allocation: 4KB - 16KB.
  - CPU Utilization: < 15% on Core 0.
- **Timing Benchmarks**:
  - ISR Latency: < 2.5 microseconds.
  - Wakeup duration: < 100 milliseconds.

### Performance Benchmarks: `adc_dma_nyquist_v1`
- **Validation ID Reference**: `adc_dma_nyquist_v1`
- **Resource Footprint**:
  - Flash Occupancy: 12KB - 45KB.
  - Heap SRAM Allocation: 4KB - 16KB.
  - CPU Utilization: < 15% on Core 0.
- **Timing Benchmarks**:
  - ISR Latency: < 2.5 microseconds.
  - Wakeup duration: < 100 milliseconds.

### Performance Benchmarks: `spi_dma_throughput_v2`
- **Validation ID Reference**: `spi_dma_throughput_v2`
- **Resource Footprint**:
  - Flash Occupancy: 12KB - 45KB.
  - Heap SRAM Allocation: 4KB - 16KB.
  - CPU Utilization: < 15% on Core 0.
- **Timing Benchmarks**:
  - ISR Latency: < 2.5 microseconds.
  - Wakeup duration: < 100 milliseconds.

### Performance Benchmarks: `esp32_ota_bootstrap_v2`
- **Validation ID Reference**: `esp32_ota_bootstrap_v2`
- **Resource Footprint**:
  - Flash Occupancy: 12KB - 45KB.
  - Heap SRAM Allocation: 4KB - 16KB.
  - CPU Utilization: < 15% on Core 0.
- **Timing Benchmarks**:
  - ISR Latency: < 2.5 microseconds.
  - Wakeup duration: < 100 milliseconds.

### Performance Benchmarks: `esp_now_p2p_v2`
- **Validation ID Reference**: `esp_now_p2p_v2`
- **Resource Footprint**:
  - Flash Occupancy: 12KB - 45KB.
  - Heap SRAM Allocation: 4KB - 16KB.
  - CPU Utilization: < 15% on Core 0.
- **Timing Benchmarks**:
  - ISR Latency: < 2.5 microseconds.
  - Wakeup duration: < 100 milliseconds.

### Performance Benchmarks: `async_web_littlefs_v1`
- **Validation ID Reference**: `async_web_littlefs_v1`
- **Resource Footprint**:
  - Flash Occupancy: 12KB - 45KB.
  - Heap SRAM Allocation: 4KB - 16KB.
  - CPU Utilization: < 15% on Core 0.
- **Timing Benchmarks**:
  - ISR Latency: < 2.5 microseconds.
  - Wakeup duration: < 100 milliseconds.

### Performance Benchmarks: `hw_crypto_aes_v2`
- **Validation ID Reference**: `hw_crypto_aes_v2`
- **Resource Footprint**:
  - Flash Occupancy: 12KB - 45KB.
  - Heap SRAM Allocation: 4KB - 16KB.
  - CPU Utilization: < 15% on Core 0.
- **Timing Benchmarks**:
  - ISR Latency: < 2.5 microseconds.
  - Wakeup duration: < 100 milliseconds.

### Performance Benchmarks: `mtls_x509_auth_v1`
- **Validation ID Reference**: `mtls_x509_auth_v1`
- **Resource Footprint**:
  - Flash Occupancy: 12KB - 45KB.
  - Heap SRAM Allocation: 4KB - 16KB.
  - CPU Utilization: < 15% on Core 0.
- **Timing Benchmarks**:
  - ISR Latency: < 2.5 microseconds.
  - Wakeup duration: < 100 milliseconds.

### Performance Benchmarks: `jtag_openocd_v1`
- **Validation ID Reference**: `jtag_openocd_v1`
- **Resource Footprint**:
  - Flash Occupancy: 12KB - 45KB.
  - Heap SRAM Allocation: 4KB - 16KB.
  - CPU Utilization: < 15% on Core 0.
- **Timing Benchmarks**:
  - ISR Latency: < 2.5 microseconds.
  - Wakeup duration: < 100 milliseconds.

### Performance Benchmarks: `tflm_wakeword_v2`
- **Validation ID Reference**: `tflm_wakeword_v2`
- **Resource Footprint**:
  - Flash Occupancy: 12KB - 45KB.
  - Heap SRAM Allocation: 4KB - 16KB.
  - CPU Utilization: < 15% on Core 0.
- **Timing Benchmarks**:
  - ISR Latency: < 2.5 microseconds.
  - Wakeup duration: < 100 milliseconds.

### Performance Benchmarks: `mcpwm_bldc_foc_v1`
- **Validation ID Reference**: `mcpwm_bldc_foc_v1`
- **Resource Footprint**:
  - Flash Occupancy: 12KB - 45KB.
  - Heap SRAM Allocation: 4KB - 16KB.
  - CPU Utilization: < 15% on Core 0.
- **Timing Benchmarks**:
  - ISR Latency: < 2.5 microseconds.
  - Wakeup duration: < 100 milliseconds.

### Performance Benchmarks: `twai_can_differential_v1`
- **Validation ID Reference**: `twai_can_differential_v1`
- **Resource Footprint**:
  - Flash Occupancy: 12KB - 45KB.
  - Heap SRAM Allocation: 4KB - 16KB.
  - CPU Utilization: < 15% on Core 0.
- **Timing Benchmarks**:
  - ISR Latency: < 2.5 microseconds.
  - Wakeup duration: < 100 milliseconds.

### Performance Benchmarks: `lvgl_dma_pingpong_v2`
- **Validation ID Reference**: `lvgl_dma_pingpong_v2`
- **Resource Footprint**:
  - Flash Occupancy: 12KB - 45KB.
  - Heap SRAM Allocation: 4KB - 16KB.
  - CPU Utilization: < 15% on Core 0.
- **Timing Benchmarks**:
  - ISR Latency: < 2.5 microseconds.
  - Wakeup duration: < 100 milliseconds.

