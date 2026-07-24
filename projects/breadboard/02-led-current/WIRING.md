# Wiring

Power off before changing a connection. Orient the ESP32 USB connector toward you and confirm board
labels; orient IC pin 1 by its notch/dot and datasheet, never by an online photo.

| Source | Destination | Colour convention | Test point |
| --- | --- | --- | --- |
| ESP32 3V3 | resistor input | red | TP1 |
| resistor output | LED anode | yellow | TP2 |
| LED cathode | GND | black | TP3 |

Power path begins at ESP32 3V3 and returns only through ESP32 GND. Add 100 nF at each external IC.
Expected idle supply is near 3.3 V but must be measured. The mirrored-IC error swaps pin numbers and is
blocking. A missing common ground, a reversed source/destination assumption or a jumper one row away
is also wrong even when its wire colour looks correct.

Assets: [`breadboard.svg`](../../../assets/projects/02-led-current/breadboard.svg) and
[`schematic.svg`](../../../assets/projects/02-led-current/schematic.svg). The SVG is a connection map,
not a photograph.
