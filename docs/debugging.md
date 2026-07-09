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
- `assets/logic-analyzer/` for protocol traces.
- `assets/captures/` for logs, monitor output, traces, and benchmark raw data.
- `diagrams/timing/` for timing reconstructions.


## Subsystem Debugging Playbooks

### `adc_dma_nyquist_v1`
- **Symptoms**: Missed samples, aliased waveforms, inconsistent callback intervals.
- **First checks**: Verify F_s > 2×F_max. Check DMA buffer alignment. Confirm no `analogRead()` in loop.
- **Tools**: Oscilloscope on ADC input, ESP monitor for callback timestamps.

### `freertos_dual_core_v1`
- **Symptoms**: Queue overflow counters increment, stale data in telemetry, watchdog resets.
- **First checks**: Verify task core affinity (`xTaskCreatePinnedToCore`). Check queue depths and consumer priority.
- **Tools**: FreeRTOS trace facility, `uxTaskGetStackHighWaterMark()`, task runtime stats.

### `deep_sleep_rtc_retention_v2`
- **Symptoms**: Counter resets to zero after wake, device does not re-enter sleep.
- **First checks**: Verify variable is in `RTC_DATA_ATTR` section. Check wake reason with `esp_sleep_get_wakeup_cause()`. Confirm sleep call is unconditional (no early return paths).
- **Tools**: Current probe on supply rail, ESP monitor for boot/wake logs.

### `nvs_wear_leveling_v1`
- **Symptoms**: CRC failure on boot, calibration defaults loaded unexpectedly.
- **First checks**: Verify blob struct packing (`__attribute__((packed))`), magic number, schema version. Check if writes are rate-limited.
- **Tools**: `nvs_get_stats()` for page utilization, NVS partition dump.

### `hw_timer_isr_v1`
- **Symptoms**: Non-zero missed deadline counter, jitter in control output.
- **First checks**: Verify ISR is IRAM-safe (no flash access). Check worker task priority. Ensure ISR does no heap allocation or logging.
- **Tools**: GPIO toggle in ISR + oscilloscope, queue overflow counter.

### `bod_panic_suppression_v1`
- **Symptoms**: Boot loops, ESP_RST_BROWNOUT in reset reason, correlation with Wi-Fi activity.
- **First checks**: Measure supply voltage during Wi-Fi TX bursts (oscilloscope on 3.3V rail). Check cable resistance, bulk/bypass capacitors.
- **Tools**: Oscilloscope on VDD, NVS fault counters, `esp_reset_reason()`.

### `mqtt_telemetry` (used by `mtls_x509_auth_v1`, `esp_now_p2p_v2`)
- **Symptoms**: Connection drops, messages not published, TLS handshake failure.
- **First checks**: Verify certificate paths exist on filesystem. Check broker hostname/port. Confirm private key is not hardcoded (grep source for PEM headers).
- **Tools**: `openssl s_client` from host to verify broker cert chain, MQTT broker logs.

### `i2c_recovery` (used by `cap_touch_iir_v1`)
- **Symptoms**: SDA or SCL held low, repeated I2C timeout errors.
- **First checks**: Measure SDA/SCL with logic analyzer. Check pull-up resistor values. Verify sensor power sequencing.
- **Tools**: Logic analyzer on SDA/SCL, GPIO bit-bang recovery (9 SCL pulses + STOP).

### `ota_manager` (used by `esp32_ota_bootstrap_v2`)
- **Symptoms**: Device stuck on old firmware, rollback counter incrementing, image marked invalid.
- **First checks**: Verify health check passes before `esp_ota_mark_app_valid_cancel_rollback()`. Check partition table for two OTA slots. Inspect image header integrity.
- **Tools**: `esp_ota_get_running_partition()`, bootloader log level, partition table dump.

### `jtag_openocd_v1`
- **Symptoms**: Cannot halt, GDB connection refused, register corruption after resume.
- **First checks**: Verify JTAG pinout matches board. Check OpenOCD config file target. Ensure flash breakpoints don't exceed hardware limit.
- **Tools**: OpenOCD log level, `monitor reset halt`, `info threads`.

## Subsystem Debugging Playbooks

### `adc_dma_nyquist_v1`
- **Symptoms**: Missed samples, aliased waveforms, inconsistent callback intervals.
- **First checks**: Verify F_s > 2×F_max. Check DMA buffer alignment. Confirm no `analogRead()` in loop.
- **Tools**: Oscilloscope on ADC input, ESP monitor for callback timestamps.

### `freertos_dual_core_v1`
- **Symptoms**: Queue overflow counters increment, stale data in telemetry, watchdog resets.
- **First checks**: Verify task core affinity (`xTaskCreatePinnedToCore`). Check queue depths and consumer priority.
- **Tools**: FreeRTOS trace facility, `uxTaskGetStackHighWaterMark()`, task runtime stats.

### `deep_sleep_rtc_retention_v2`
- **Symptoms**: Counter resets to zero after wake, device does not re-enter sleep.
- **First checks**: Verify variable is in `RTC_DATA_ATTR` section. Check wake reason with `esp_sleep_get_wakeup_cause()`. Confirm sleep call is unconditional (no early return paths).
- **Tools**: Current probe on supply rail, ESP monitor for boot/wake logs.

### `nvs_wear_leveling_v1`
- **Symptoms**: CRC failure on boot, calibration defaults loaded unexpectedly.
- **First checks**: Verify blob struct packing (`__attribute__((packed))`), magic number, schema version. Check if writes are rate-limited.
- **Tools**: `nvs_get_stats()` for page utilization, NVS partition dump.

### `hw_timer_isr_v1`
- **Symptoms**: Non-zero missed deadline counter, jitter in control output.
- **First checks**: Verify ISR is IRAM-safe (no flash access). Check worker task priority. Ensure ISR does no heap allocation or logging.
- **Tools**: GPIO toggle in ISR + oscilloscope, queue overflow counter.

### `bod_panic_suppression_v1`
- **Symptoms**: Boot loops, ESP_RST_BROWNOUT in reset reason, correlation with Wi-Fi activity.
- **First checks**: Measure supply voltage during Wi-Fi TX bursts (oscilloscope on 3.3V rail). Check cable resistance, bulk/bypass capacitors.
- **Tools**: Oscilloscope on VDD, NVS fault counters, `esp_reset_reason()`.

### `mqtt_telemetry` (used by `mtls_x509_auth_v1`, `esp_now_p2p_v2`)
- **Symptoms**: Connection drops, messages not published, TLS handshake failure.
- **First checks**: Verify certificate paths exist on filesystem. Check broker hostname/port. Confirm private key is not hardcoded (grep source for PEM headers).
- **Tools**: `openssl s_client` from host to verify broker cert chain, MQTT broker logs.

### `i2c_recovery` (used by `cap_touch_iir_v1`)
- **Symptoms**: SDA or SCL held low, repeated I2C timeout errors.
- **First checks**: Measure SDA/SCL with logic analyzer. Check pull-up resistor values. Verify sensor power sequencing.
- **Tools**: Logic analyzer on SDA/SCL, GPIO bit-bang recovery (9 SCL pulses + STOP).

### `ota_manager` (used by `esp32_ota_bootstrap_v2`)
- **Symptoms**: Device stuck on old firmware, rollback counter incrementing, image marked invalid.
- **First checks**: Verify health check passes before `esp_ota_mark_app_valid_cancel_rollback()`. Check partition table for two OTA slots. Inspect image header integrity.
- **Tools**: `esp_ota_get_running_partition()`, bootloader log level, partition table dump.

### `jtag_openocd_v1`
- **Symptoms**: Cannot halt, GDB connection refused, register corruption after resume.
- **First checks**: Verify JTAG pinout matches board. Check OpenOCD config file target. Ensure flash breakpoints don't exceed hardware limit.
- **Tools**: OpenOCD log level, `monitor reset halt`, `info threads`.
