# Build

1. Disconnect USB and all other power.
2. Map breadboard rail continuity and mark any split.
3. Place components; verify package orientation against the exact datasheet.
4. Add GND, then 3.3 V, then signal wires one at a time.
5. Add each required 100 nF decoupling capacitor at external IC supply pins.
6. Check continuity from every source to destination in `pinmap.yaml`.
7. Complete every blocking item in `BEFORE-YOU-POWER.md`.
8. Read the AO3400A pinout and verify the adapter labels with continuity; reject a mirrored or unlabelled adapter.
9. Wire source to GND, gate to GPIO25 through 100 ohm, and gate to GND through 100 kohm.
10. Wire 3V3 → 1 kohm → LED → drain; no motor, relay or external supply is used.
11. Do not add a flyback diode to this resistive LED load. A flyback diode is required only when a later, separately rated inductive load is introduced.
12. Flash the toggle firmware and measure VGS, drain voltage and resistor voltage in both states.
13. Record results in `evidence/measurement-template.csv`; expected values never enter measured fields.
