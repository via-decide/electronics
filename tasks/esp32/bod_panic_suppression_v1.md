# Bod Panic Suppression V1

Validation ID: `bod_panic_suppression_v1`

## Purpose

This task is part of `esp32_master_architecture_validation_v1`. It defines a production validation slice with deterministic ownership, measurable pass criteria, required hardware, and traceable source files.

## Phase

Phase 3 of the ESP32 master architecture validation stack.

## Engineering Risk

Production ESP32 systems fail when this subsystem is treated as a demonstration feature instead of a measured engineering interface. Validation must prove timing, power, memory, electrical, security, or lifecycle assumptions under realistic load.

## Source Files

`[firmware/esp32/power_diagnostics.c]`

## Required Hardware

ESP32 board, power supply, oscilloscope.

## Test Method

Record reset reason and correlate Wi-Fi stress with supply droop; do not blindly disable BOD.

## Pass Metric

Brownout, watchdog, panic, and software resets are distinguishable in diagnostics.

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
