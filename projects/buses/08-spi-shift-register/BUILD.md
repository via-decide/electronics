# Build

1. Disconnect USB and all other power.
2. Map breadboard rail continuity and mark any split.
3. Place components; verify package orientation against the exact datasheet.
4. Add GND, then 3.3 V, then signal wires one at a time.
5. Add each required 100 nF decoupling capacitor at external IC supply pins.
6. Check continuity from every source to destination in `pinmap.yaml`.
7. Complete every blocking item in `BEFORE-YOU-POWER.md`.
8. Place SN74HC595N across the breadboard centre channel with its notch and pin 1 identified.
9. Wire pin 16 VCC and pin 10 SRCLR to 3V3; pin 8 GND and pin 13 OE# to GND; add 100 nF across pins 16/8.
10. Wire SER pin 14 to GPIO23, SRCLK pin 11 to GPIO18 and RCLK pin 12 to GPIO32.
11. Wire each Q output through its own 1 kohm resistor and LED to GND.
12. Run the walking-bit firmware and compare visible order with captured data/clock/latch transitions.
13. Record results in `evidence/measurement-template.csv`; expected values never enter measured fields.
