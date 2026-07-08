# Benchmarks and Measurement Methodology

## Purpose

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
