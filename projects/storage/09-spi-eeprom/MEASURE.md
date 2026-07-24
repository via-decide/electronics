# Measure

Set the DMM to DC voltage above 3.3 V. Connect black to project GND first. Probe only named test points
with the red lead and avoid adjacent pins.

**Quantity:** Supply, CS# idle, SPI signals, status register transitions and readback CRC.

Record instrument model, range, resolution, uncertainty if known, exact test point, state and timestamp.
Expected values belong in the expected column; actual readings belong only in measured.

Record WIP/WEL status bytes and the exact address range. Do not infer a write from MOSI alone.

Evidence filename: `09-spi-eeprom-measurements-YYYYMMDD.csv`.
