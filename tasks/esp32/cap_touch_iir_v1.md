# Cap Touch Iir V1

Validation ID: `cap_touch_iir_v1`

## Purpose

This task is part of `esp32_master_architecture_validation_v1`. It defines a production validation slice with deterministic ownership, measurable pass criteria, required hardware, and traceable source files.

## Phase

Phase 2 of the ESP32 master architecture validation stack.

## Engineering Risk

Production ESP32 systems fail when this subsystem is treated as a demonstration feature instead of a measured engineering interface. Validation must prove timing, power, memory, electrical, security, or lifecycle assumptions under realistic load.

## Source Files

`[docs/theory.md]`

## Required Hardware

ESP32 touch-capable pad and optional noisy environment source.

## Test Method

Capture touch raw counts and verify dynamic IIR filter rejects noise while preserving touch response.

## Pass Metric

False triggers remain below threshold while valid touches are detected.

## Failure Conditions

- Timing-critical behavior depends on blocking `delay()` or loop polling.
- ISR context performs heap allocation, filesystem access, serial printing, Wi-Fi, MQTT, or non-IRAM-safe work.
- Hardware limits are not measured or documented.
- Validation evidence cannot be reproduced from a clean checkout.

## Evidence Links

- Benchmarks: `docs/benchmarks.md`
- Debugging: `docs/debugging.md`
- Production guidance: `docs/production.md`
- Reports: `reports/esp32_master_validation.md`
