# Adc Dma Nyquist V1

Validation ID: `adc_dma_nyquist_v1`

## Purpose

This task is part of `esp32_master_architecture_validation_v1`. It defines a production validation slice with deterministic ownership, measurable pass criteria, required hardware, and traceable source files.

## Phase

Phase 4 of the ESP32 master architecture validation stack.

## Engineering Risk

Production ESP32 systems fail when this subsystem is treated as a demonstration feature instead of a measured engineering interface. Validation must prove timing, power, memory, electrical, security, or lifecycle assumptions under realistic load.

## Source Files

`[firmware/esp32/adc_dma_continuous.c, docs/esp32/adc_dma_continuous.md]`

## Required Hardware

Signal generator and ESP32 ADC input fixture.

## Test Method

Sample sine input with ADC DMA and verify Nyquist margin, callback interval, and no loop analogRead path.

## Pass Metric

Fs > 2*Fmax and callback interval remains predictable under Wi-Fi/MQTT load.

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
