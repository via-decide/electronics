# Wiring

Power off before changing a connection. Orient the ESP32 USB connector toward you and confirm board
labels; orient IC pin 1 by its notch/dot and datasheet, never by an online photo.

| Source | Destination | Colour convention | Test point |
| --- | --- | --- | --- |
| ESP32 3V3 | TMP117 VIN | red | TP1 |
| ESP32 GND | TMP117 GND | black | TP2 |
| ESP32 GPIO21/SDA | TMP117 SDA | blue | TP3 |
| ESP32 GPIO22/SCL | TMP117 SCL | yellow | TP4 |

Power path begins at ESP32 3V3 and returns only through ESP32 GND. Add 100 nF at each external IC.
Expected idle supply is near 3.3 V but must be measured. The mirrored-IC error swaps pin numbers and is
blocking. A missing common ground, a reversed source/destination assumption or a jumper one row away
is also wrong even when its wire colour looks correct.

Assets: [`breadboard.svg`](../../../assets/projects/07-i2c-sensor/breadboard.svg) and
[`schematic.svg`](../../../assets/projects/07-i2c-sensor/schematic.svg). The SVG is a connection map,
not a photograph.
