# Wiring

Power off before changing a connection. Orient the ESP32 USB connector toward you and confirm board
labels; orient IC pin 1 by its notch/dot and datasheet, never by an online photo.

| Source | Destination | Colour convention | Test point |
| --- | --- | --- | --- |
| ESP32 GPIO23/MOSI | SN74HC595 SER pin 14 | blue | TP1 |
| ESP32 GPIO18/SCLK | SN74HC595 SRCLK pin 11 | yellow | TP2 |
| ESP32 GPIO32 | SN74HC595 RCLK pin 12 | green | TP3 |
| ESP32 3V3 | VCC pin 16 and SRCLR pin 10 | red | TP4 |
| ESP32 GND | GND pin 8 and OE# pin 13 | black | TP5 |
| SN74HC595 Q0 pin 15 | 1 kohm + LED0 anode; cathode to GND | orange | TP6 |
| SN74HC595 Q1 pin 1 | 1 kohm + LED1 anode; cathode to GND | orange | TP7 |
| SN74HC595 Q2 pin 2 | 1 kohm + LED2 anode; cathode to GND | orange | TP8 |
| SN74HC595 Q3 pin 3 | 1 kohm + LED3 anode; cathode to GND | orange | TP9 |
| SN74HC595 Q4 pin 4 | 1 kohm + LED4 anode; cathode to GND | orange | TP10 |
| SN74HC595 Q5 pin 5 | 1 kohm + LED5 anode; cathode to GND | orange | TP11 |
| SN74HC595 Q6 pin 6 | 1 kohm + LED6 anode; cathode to GND | orange | TP12 |
| SN74HC595 Q7 pin 7 | 1 kohm + LED7 anode; cathode to GND | orange | TP13 |

Power path begins at ESP32 3V3 and returns only through ESP32 GND. Add 100 nF at each external IC.
Expected idle supply is near 3.3 V but must be measured. The mirrored-IC error swaps pin numbers and is
blocking. A missing common ground, a reversed source/destination assumption or a jumper one row away
is also wrong even when its wire colour looks correct.

Assets: [`breadboard.svg`](../../../assets/projects/08-spi-shift-register/breadboard.svg) and
[`schematic.svg`](../../../assets/projects/08-spi-shift-register/schematic.svg). The SVG is a connection map,
not a photograph.
