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
