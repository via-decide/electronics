# Analog Voltage Measurement

**Question:** How different is an ADC code from a voltage you can trust?

**Build:** Wire a 10 kohm potentiometer between 3.3 V and GND with its wiper on GPIO34/ADC1_CH6. Read, average and calibrate.

**Visible or measurable result:** DMM wiper voltage, raw 12-bit codes, 64-sample mean and calibrated millivolts at several positions.

**Why useful:** An ADC returns a code. Voltage requires a transfer function, attenuation setting, calibration and evidence.

**Estimated time:** 110 minutes. **Difficulty:** beginner.

**Required knowledge:** 04-mosfet-load-switch. Read `BEFORE-YOU-POWER.md`.

**Success:** A table contains DMM voltage, raw mean, calibrated voltage, error and measurement conditions.

Hardware status: **HARDWARE_VALIDATION_REQUIRED**. Documentation and firmware are not physical proof.
