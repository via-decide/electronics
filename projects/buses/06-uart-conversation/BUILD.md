# Build

1. Disconnect USB and all other power.
2. Map breadboard rail continuity and mark any split.
3. Place components; verify package orientation against the exact datasheet.
4. Add GND, then 3.3 V, then signal wires one at a time.
5. Add each required 100 nF decoupling capacitor at external IC supply pins.
6. Check continuity from every source to destination in `pinmap.yaml`.
7. Complete every blocking item in `BEFORE-YOU-POWER.md`.
8. Confirm the selected module is WROOM-32E, not a WROVER/PSRAM variant.
9. With power off, jumper GPIO17 TX to GPIO16 RX and attach analyzer ground only if its input limits are known.
10. Build, flash and monitor the independent UART1-TX/UART2-RX frame accept/reject log at 115200 baud.
11. Change only RX_BAUD to 57600 for the controlled failure; restore 115200 after recording rejection.
12. Record results in `evidence/measurement-template.csv`; expected values never enter measured fields.
