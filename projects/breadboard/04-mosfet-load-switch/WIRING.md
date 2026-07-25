# Wiring

Power off before changing a connection. Orient the ESP32 USB connector toward you and confirm board
labels; orient IC pin 1 by its notch/dot and datasheet, never by an online photo.

| Source | Destination | Colour convention | Test point |
| --- | --- | --- | --- |
| ESP32 GPIO25 | 100 ohm then AO3400A gate | yellow | TP1 |
| AO3400A gate | 100 kohm to GND | blue | TP2 |
| AO3400A source | GND | black | TP3 |
| 3V3 | 1 kohm → LED anode; LED cathode → AO3400A drain | red | TP4 |

Power path begins at ESP32 3V3 and returns only through ESP32 GND. Add 100 nF at each external IC.
Expected idle supply is near 3.3 V but must be measured. The mirrored-IC error swaps pin numbers and is
blocking. A missing common ground, a reversed source/destination assumption or a jumper one row away
is also wrong even when its wire colour looks correct.

Assets: [`breadboard.svg`](../../../assets/projects/04-mosfet-load-switch/breadboard.svg) and
[`schematic.svg`](../../../assets/projects/04-mosfet-load-switch/schematic.svg). The SVG is a connection map,
not a photograph.
