# Build

1. Disconnect USB and all other power.
2. Map breadboard rail continuity and mark any split.
3. Place components; verify package orientation against the exact datasheet.
4. Add GND, then 3.3 V, then signal wires one at a time.
5. Add each required 100 nF decoupling capacitor at external IC supply pins.
6. Check continuity from every source to destination in `pinmap.yaml`.
7. Complete every blocking item in `BEFORE-YOU-POWER.md`.
8. Map the two internally common button-pin pairs with continuity mode before placing it across the centre channel.
9. Wire one side to GPIO27 and the opposite side to GND; do not add an external voltage source.
10. Build and flash the official ESP-IDF project, then measure GPIO27 idle and pressed voltage.
11. Record raw and debounced transition counts for ten deliberate presses.
12. For the controlled failure, disable the configured pull-up, leave the pin unconnected and record the undefined behaviour before restoring it.
13. Optional pull-down comparison: power off, disable internal pulls, add 10 kohm from GPIO27 to GND and move the button's far side to 3V3; measure low idle/high pressed, then restore the primary active-low circuit.
14. Record results in `evidence/measurement-template.csv`; expected values never enter measured fields.
