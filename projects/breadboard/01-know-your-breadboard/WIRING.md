# Wiring

Power off before changing a connection. Orient the ESP32 USB connector toward you and confirm board
labels; orient IC pin 1 by its notch/dot and datasheet, never by an online photo.

| Source | Destination | Colour convention | Test point |
| --- | --- | --- | --- |
| ESP32 3V3 | red rail | red | TP1 |
| ESP32 GND | blue rail | black | TP2 |
| rail bridge + | upper/lower red segments | red | TP3 |
| rail bridge - | upper/lower blue segments | black | TP4 |

Power path begins at ESP32 3V3 and returns only through ESP32 GND. Add 100 nF at each external IC.
Expected idle supply is near 3.3 V but must be measured. The mirrored-IC error swaps pin numbers and is
blocking. A missing common ground, a reversed source/destination assumption or a jumper one row away
is also wrong even when its wire colour looks correct.

Assets: [`breadboard.svg`](../../../assets/projects/01-know-your-breadboard/breadboard.svg) and
[`schematic.svg`](../../../assets/projects/01-know-your-breadboard/schematic.svg). The SVG is a connection map,
not a photograph.
