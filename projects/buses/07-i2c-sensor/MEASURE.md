# Measure

Set the DMM to DC voltage above 3.3 V. Connect black to project GND first. Probe only named test points
with the red lead and avoid adjacent pins.

**Quantity:** SDA/SCL idle voltage, detected address, device ID, ACK/NACK result and decoded temperature.

Record instrument model, range, resolution, uncertainty if known, exact test point, state and timestamp.
Expected values belong in the expected column; actual readings belong only in measured.

If the breakout already contains pull-ups, record their values before adding any external pair.

Evidence filename: `07-i2c-sensor-measurements-YYYYMMDD.csv`.
