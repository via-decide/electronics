# Debugging Guide

## Purpose

This document standardizes debugging knowledge for firmware, hardware, validation, and production failures. Debug instructions must be reproducible, instrumented, and tied to observable evidence.

## Debug Workflow

```text
Observe symptom
  ↓
Classify domain: timing, power, memory, bus, network, storage, firmware logic
  ↓
Collect evidence: logs, reset reason, traces, scope captures, analyzer captures
  ↓
Reproduce under controlled load
  ↓
Isolate subsystem
  ↓
Inject fault or stress condition
  ↓
Verify fix with regression test and benchmark
```

## Diagnostic Tools

| Tool | Use |
| --- | --- |
| Serial logs / ESP Monitor | Boot logs, reset reason, driver errors, task progress. |
| JTAG | Breakpoints, register inspection, task state, crash diagnosis. |
| Logic analyzer | I2C/SPI/UART timing, stuck bus detection, protocol validation. |
| Oscilloscope | Brownout, ripple, edge quality, ADC input integrity, Wi-Fi current dips. |
| FreeRTOS tracing | Priority inversion, starvation, queue pressure, deadline misses. |
| Heap tracing | Fragmentation, leaks, allocation spikes, PSRAM/internal RAM pressure. |
| Performance counters | CPU load, ISR frequency, latency, throughput. |

## Common Failure Classes

| Failure | Typical evidence | First checks |
| --- | --- | --- |
| Timing drift | Missed periods, jitter, unstable sampling interval | Hardware timer configuration, ISR duration, queue depth. |
| Queue overflow | Drop counters, stale data, backpressure | Producer/consumer rates, task priority, buffer size. |
| Brownout | `ESP_RST_BROWNOUT`, boot loops, Wi-Fi-correlated resets | Regulator capacity, cable resistance, decoupling, current bursts. |
| I2C stuck bus | SDA/SCL held low, repeated timeout | GPIO bus sampling, recovery pulses, sensor power sequencing. |
| Watchdog reset | WDT reset reason, blocked task | Blocking calls, priority inversion, long critical sections. |
| OTA rollback | Pending verify image, rollback counter | Health check, partition table, image validity, boot confirmation. |
| Corrupt calibration | CRC/schema failure | NVS blob size, CRC, schema version, default fallback. |

## Evidence Storage

Debug evidence should be committed or referenced using the supporting asset folders:

- `assets/oscilloscope/` for supply, reset, analog, and timing captures.
- `assets/logic_analyzer/` for protocol traces.
- `assets/captures/` for logs, monitor output, traces, and benchmark raw data.
- `diagrams/timing/` for timing reconstructions.

## Subsystem Debugging Playbooks

### Debugging Playbook: `esp32_core_installation_v1`
- **Validation ID Reference**: `esp32_core_installation_v1`
- **Common Failure Modes**:
  - Watchdog triggers due to long ISR executions.
  - Stack overflows under concurrent RTOS context swaps.
  - Memory leaks in dynamic allocation paths.
- **Diagnostic Playbook**:
  Inspect memory logs using JTAG/OpenOCD registers monitoring or trace outputs via UART serial interfaces.

### Debugging Playbook: `esp32_hall_diagnostic_v1`
- **Validation ID Reference**: `esp32_hall_diagnostic_v1`
- **Common Failure Modes**:
  - Watchdog triggers due to long ISR executions.
  - Stack overflows under concurrent RTOS context swaps.
  - Memory leaks in dynamic allocation paths.
- **Diagnostic Playbook**:
  Inspect memory logs using JTAG/OpenOCD registers monitoring or trace outputs via UART serial interfaces.

### Debugging Playbook: `nltm_sensor_linearization_v1`
- **Validation ID Reference**: `nltm_sensor_linearization_v1`
- **Common Failure Modes**:
  - Watchdog triggers due to long ISR executions.
  - Stack overflows under concurrent RTOS context swaps.
  - Memory leaks in dynamic allocation paths.
- **Diagnostic Playbook**:
  Inspect memory logs using JTAG/OpenOCD registers monitoring or trace outputs via UART serial interfaces.

### Debugging Playbook: `logic_level_shift_v2`
- **Validation ID Reference**: `logic_level_shift_v2`
- **Common Failure Modes**:
  - Watchdog triggers due to long ISR executions.
  - Stack overflows under concurrent RTOS context swaps.
  - Memory leaks in dynamic allocation paths.
- **Diagnostic Playbook**:
  Inspect memory logs using JTAG/OpenOCD registers monitoring or trace outputs via UART serial interfaces.

### Debugging Playbook: `ledc_pwm_matrix_v1`
- **Validation ID Reference**: `ledc_pwm_matrix_v1`
- **Common Failure Modes**:
  - Watchdog triggers due to long ISR executions.
  - Stack overflows under concurrent RTOS context swaps.
  - Memory leaks in dynamic allocation paths.
- **Diagnostic Playbook**:
  Inspect memory logs using JTAG/OpenOCD registers monitoring or trace outputs via UART serial interfaces.

### Debugging Playbook: `cap_touch_iir_v1`
- **Validation ID Reference**: `cap_touch_iir_v1`
- **Common Failure Modes**:
  - Watchdog triggers due to long ISR executions.
  - Stack overflows under concurrent RTOS context swaps.
  - Memory leaks in dynamic allocation paths.
- **Diagnostic Playbook**:
  Inspect memory logs using JTAG/OpenOCD registers monitoring or trace outputs via UART serial interfaces.

### Debugging Playbook: `freertos_dual_core_v1`
- **Validation ID Reference**: `freertos_dual_core_v1`
- **Common Failure Modes**:
  - Watchdog triggers due to long ISR executions.
  - Stack overflows under concurrent RTOS context swaps.
  - Memory leaks in dynamic allocation paths.
- **Diagnostic Playbook**:
  Inspect memory logs using JTAG/OpenOCD registers monitoring or trace outputs via UART serial interfaces.

### Debugging Playbook: `deep_sleep_rtc_retention_v2`
- **Validation ID Reference**: `deep_sleep_rtc_retention_v2`
- **Common Failure Modes**:
  - Watchdog triggers due to long ISR executions.
  - Stack overflows under concurrent RTOS context swaps.
  - Memory leaks in dynamic allocation paths.
- **Diagnostic Playbook**:
  Inspect memory logs using JTAG/OpenOCD registers monitoring or trace outputs via UART serial interfaces.

### Debugging Playbook: `nvs_wear_leveling_v1`
- **Validation ID Reference**: `nvs_wear_leveling_v1`
- **Common Failure Modes**:
  - Watchdog triggers due to long ISR executions.
  - Stack overflows under concurrent RTOS context swaps.
  - Memory leaks in dynamic allocation paths.
- **Diagnostic Playbook**:
  Inspect memory logs using JTAG/OpenOCD registers monitoring or trace outputs via UART serial interfaces.

### Debugging Playbook: `hw_timer_isr_v1`
- **Validation ID Reference**: `hw_timer_isr_v1`
- **Common Failure Modes**:
  - Watchdog triggers due to long ISR executions.
  - Stack overflows under concurrent RTOS context swaps.
  - Memory leaks in dynamic allocation paths.
- **Diagnostic Playbook**:
  Inspect memory logs using JTAG/OpenOCD registers monitoring or trace outputs via UART serial interfaces.

### Debugging Playbook: `bod_panic_suppression_v1`
- **Validation ID Reference**: `bod_panic_suppression_v1`
- **Common Failure Modes**:
  - Watchdog triggers due to long ISR executions.
  - Stack overflows under concurrent RTOS context swaps.
  - Memory leaks in dynamic allocation paths.
- **Diagnostic Playbook**:
  Inspect memory logs using JTAG/OpenOCD registers monitoring or trace outputs via UART serial interfaces.

### Debugging Playbook: `ulp_fsm_assembly_v1`
- **Validation ID Reference**: `ulp_fsm_assembly_v1`
- **Common Failure Modes**:
  - Watchdog triggers due to long ISR executions.
  - Stack overflows under concurrent RTOS context swaps.
  - Memory leaks in dynamic allocation paths.
- **Diagnostic Playbook**:
  Inspect memory logs using JTAG/OpenOCD registers monitoring or trace outputs via UART serial interfaces.

### Debugging Playbook: `i2s_dma_audio_v1`
- **Validation ID Reference**: `i2s_dma_audio_v1`
- **Common Failure Modes**:
  - Watchdog triggers due to long ISR executions.
  - Stack overflows under concurrent RTOS context swaps.
  - Memory leaks in dynamic allocation paths.
- **Diagnostic Playbook**:
  Inspect memory logs using JTAG/OpenOCD registers monitoring or trace outputs via UART serial interfaces.

### Debugging Playbook: `adc_dma_nyquist_v1`
- **Validation ID Reference**: `adc_dma_nyquist_v1`
- **Common Failure Modes**:
  - Watchdog triggers due to long ISR executions.
  - Stack overflows under concurrent RTOS context swaps.
  - Memory leaks in dynamic allocation paths.
- **Diagnostic Playbook**:
  Inspect memory logs using JTAG/OpenOCD registers monitoring or trace outputs via UART serial interfaces.

### Debugging Playbook: `spi_dma_throughput_v2`
- **Validation ID Reference**: `spi_dma_throughput_v2`
- **Common Failure Modes**:
  - Watchdog triggers due to long ISR executions.
  - Stack overflows under concurrent RTOS context swaps.
  - Memory leaks in dynamic allocation paths.
- **Diagnostic Playbook**:
  Inspect memory logs using JTAG/OpenOCD registers monitoring or trace outputs via UART serial interfaces.

### Debugging Playbook: `esp32_ota_bootstrap_v2`
- **Validation ID Reference**: `esp32_ota_bootstrap_v2`
- **Common Failure Modes**:
  - Watchdog triggers due to long ISR executions.
  - Stack overflows under concurrent RTOS context swaps.
  - Memory leaks in dynamic allocation paths.
- **Diagnostic Playbook**:
  Inspect memory logs using JTAG/OpenOCD registers monitoring or trace outputs via UART serial interfaces.

### Debugging Playbook: `esp_now_p2p_v2`
- **Validation ID Reference**: `esp_now_p2p_v2`
- **Common Failure Modes**:
  - Watchdog triggers due to long ISR executions.
  - Stack overflows under concurrent RTOS context swaps.
  - Memory leaks in dynamic allocation paths.
- **Diagnostic Playbook**:
  Inspect memory logs using JTAG/OpenOCD registers monitoring or trace outputs via UART serial interfaces.

### Debugging Playbook: `async_web_littlefs_v1`
- **Validation ID Reference**: `async_web_littlefs_v1`
- **Common Failure Modes**:
  - Watchdog triggers due to long ISR executions.
  - Stack overflows under concurrent RTOS context swaps.
  - Memory leaks in dynamic allocation paths.
- **Diagnostic Playbook**:
  Inspect memory logs using JTAG/OpenOCD registers monitoring or trace outputs via UART serial interfaces.

### Debugging Playbook: `hw_crypto_aes_v2`
- **Validation ID Reference**: `hw_crypto_aes_v2`
- **Common Failure Modes**:
  - Watchdog triggers due to long ISR executions.
  - Stack overflows under concurrent RTOS context swaps.
  - Memory leaks in dynamic allocation paths.
- **Diagnostic Playbook**:
  Inspect memory logs using JTAG/OpenOCD registers monitoring or trace outputs via UART serial interfaces.

### Debugging Playbook: `mtls_x509_auth_v1`
- **Validation ID Reference**: `mtls_x509_auth_v1`
- **Common Failure Modes**:
  - Watchdog triggers due to long ISR executions.
  - Stack overflows under concurrent RTOS context swaps.
  - Memory leaks in dynamic allocation paths.
- **Diagnostic Playbook**:
  Inspect memory logs using JTAG/OpenOCD registers monitoring or trace outputs via UART serial interfaces.

### Debugging Playbook: `jtag_openocd_v1`
- **Validation ID Reference**: `jtag_openocd_v1`
- **Common Failure Modes**:
  - Watchdog triggers due to long ISR executions.
  - Stack overflows under concurrent RTOS context swaps.
  - Memory leaks in dynamic allocation paths.
- **Diagnostic Playbook**:
  Inspect memory logs using JTAG/OpenOCD registers monitoring or trace outputs via UART serial interfaces.

### Debugging Playbook: `tflm_wakeword_v2`
- **Validation ID Reference**: `tflm_wakeword_v2`
- **Common Failure Modes**:
  - Watchdog triggers due to long ISR executions.
  - Stack overflows under concurrent RTOS context swaps.
  - Memory leaks in dynamic allocation paths.
- **Diagnostic Playbook**:
  Inspect memory logs using JTAG/OpenOCD registers monitoring or trace outputs via UART serial interfaces.

### Debugging Playbook: `mcpwm_bldc_foc_v1`
- **Validation ID Reference**: `mcpwm_bldc_foc_v1`
- **Common Failure Modes**:
  - Watchdog triggers due to long ISR executions.
  - Stack overflows under concurrent RTOS context swaps.
  - Memory leaks in dynamic allocation paths.
- **Diagnostic Playbook**:
  Inspect memory logs using JTAG/OpenOCD registers monitoring or trace outputs via UART serial interfaces.

### Debugging Playbook: `twai_can_differential_v1`
- **Validation ID Reference**: `twai_can_differential_v1`
- **Common Failure Modes**:
  - Watchdog triggers due to long ISR executions.
  - Stack overflows under concurrent RTOS context swaps.
  - Memory leaks in dynamic allocation paths.
- **Diagnostic Playbook**:
  Inspect memory logs using JTAG/OpenOCD registers monitoring or trace outputs via UART serial interfaces.

### Debugging Playbook: `lvgl_dma_pingpong_v2`
- **Validation ID Reference**: `lvgl_dma_pingpong_v2`
- **Common Failure Modes**:
  - Watchdog triggers due to long ISR executions.
  - Stack overflows under concurrent RTOS context swaps.
  - Memory leaks in dynamic allocation paths.
- **Diagnostic Playbook**:
  Inspect memory logs using JTAG/OpenOCD registers monitoring or trace outputs via UART serial interfaces.

