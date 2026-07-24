# Build

1. Disconnect USB and all other power.
2. Map breadboard rail continuity and mark any split.
3. Place components; verify package orientation against the exact datasheet.
4. Add GND, then 3.3 V, then signal wires one at a time.
5. Add each required 100 nF decoupling capacitor at external IC supply pins.
6. Check continuity from every source to destination in `pinmap.yaml`.
7. Complete every blocking item in `BEFORE-YOU-POWER.md`.
8. Identify potentiometer ends and wiper with resistance mode before connecting power.
9. Wire the ends to 3V3/GND and the wiper to GPIO34/ADC1_CH6; keep Wi-Fi disabled.
10. Set the wiper near 25%, 50% and 75%; at each point record DMM voltage, raw mean and calibrated millivolts.
11. Calculate error as calibrated ADC voltage minus DMM voltage and state DMM resolution.
12. Repeat one point using a single sample and 64-sample mean to expose noise without claiming accuracy.
13. Record results in `evidence/measurement-template.csv`; expected values never enter measured fields.
