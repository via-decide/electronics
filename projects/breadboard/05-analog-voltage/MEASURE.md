# Measure

Set the DMM to DC voltage above 3.3 V. Connect black to project GND first. Probe only named test points
with the red lead and avoid adjacent pins.

**Quantity:** DMM wiper voltage, raw 12-bit codes, 64-sample mean and calibrated millivolts at several positions.

Record instrument model, range, resolution, uncertainty if known, exact test point, state and timestamp.
Expected values belong in the expected column; actual readings belong only in measured.

Use the same GND reference for the DMM and ADC. Do not infer accuracy from ADC resolution.

Evidence filename: `05-analog-voltage-measurements-YYYYMMDD.csv`.
