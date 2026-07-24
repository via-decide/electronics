# Build

1. Disconnect USB and all other power.
2. Map breadboard rail continuity and mark any split.
3. Place components; verify package orientation against the exact datasheet.
4. Add GND, then 3.3 V, then signal wires one at a time.
5. Add each required 100 nF decoupling capacitor at external IC supply pins.
6. Check continuity from every source to destination in `pinmap.yaml`.
7. Complete every blocking item in `BEFORE-YOU-POWER.md`.
8. Use resistance mode on the unpowered circuit to verify 220 ohm, 1 kohm and 10 kohm parts.
9. Start with 1 kohm: 3V3 → resistor → LED anode; LED cathode → GND.
10. Measure the actual rail, LED voltage and resistor voltage without changing to current mode.
11. Calculate current from measured resistor voltage divided by measured resistance.
12. Power down, repeat with 220 ohm, then 10 kohm, and compare calculated current with brightness.
13. Record results in `evidence/measurement-template.csv`; expected values never enter measured fields.
