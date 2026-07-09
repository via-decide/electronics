# Benchmark suite

Benchmarks measure flash, RAM, stack, CPU, ISR latency, DMA throughput, ADC speed, Wi-Fi throughput, BLE latency, ESP-NOW latency, CAN throughput, MQTT latency, OTA duration, boot time, wake-up time, display FPS, and power consumption.

## Required record format

Each benchmark record must include hardware revision, firmware commit, SDK/toolchain versions, instruments, calibration status, environmental conditions, exact command, raw artifacts, statistics, repeatability notes, and limitations. Do not publish a performance claim without a linked raw log or measurement capture.

## Repeatability policy

Run at least one cold boot, one steady-state run, and one stress run where applicable. Report minimum, maximum, mean, sample count, and known sources of uncertainty. If hardware is unavailable, mark the result as a methodology template rather than a measured benchmark.
