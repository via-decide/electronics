# Wiring

Power off before changing a connection. Orient the ESP32 USB connector toward you and confirm board
labels; orient IC pin 1 by its notch/dot and datasheet, never by an online photo.

| Source | Destination | Colour convention | Test point |
| --- | --- | --- | --- |
| ESP32 GPIO23/MOSI | 25LC256 SI pin 5 | blue | TP1 |
| ESP32 GPIO19/MISO | 25LC256 SO pin 2 | green | TP2 |
| ESP32 GPIO18/SCLK | 25LC256 SCK pin 6 | yellow | TP3 |
| ESP32 GPIO32/CS | 25LC256 CS# pin 1 and 10 kohm pull-up to 3V3 | white | TP4 |
| ESP32 3V3 | VCC pin 8, WP# pin 3, HOLD# pin 7 | red | TP5 |
| ESP32 GND | VSS pin 4 | black | TP6 |

Power path begins at ESP32 3V3 and returns only through ESP32 GND. Add 100 nF at each external IC.
Expected idle supply is near 3.3 V but must be measured. The mirrored-IC error swaps pin numbers and is
blocking. A missing common ground, a reversed source/destination assumption or a jumper one row away
is also wrong even when its wire colour looks correct.

Assets: [`breadboard.svg`](../../../assets/projects/09-spi-eeprom/breadboard.svg) and
[`schematic.svg`](../../../assets/projects/09-spi-eeprom/schematic.svg). The SVG is a connection map,
not a photograph.
