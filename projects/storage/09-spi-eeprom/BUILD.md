# Build

1. Disconnect USB and all other power.
2. Map breadboard rail continuity and mark any split.
3. Place components; verify package orientation against the exact datasheet.
4. Add GND, then 3.3 V, then signal wires one at a time.
5. Add each required 100 nF decoupling capacitor at external IC supply pins.
6. Check continuity from every source to destination in `pinmap.yaml`.
7. Complete every blocking item in `BEFORE-YOU-POWER.md`.
8. Place 25LC256-I/P across the centre channel; verify notch, pin 1 and the Microchip marking.
9. Wire VCC, GND, SI, SO, SCK and CS exactly; tie WP#/HOLD# high and add 100 nF at pins 8/4.
10. Add a 10 kohm CS# pull-up so the EEPROM remains deselected during reset.
11. Keep WP# high for this lesson. The pin protects status-register writes only when WPEN is set; it is not a universal data-write lock.
12. Run the bounded tests at 0x0100-0x0183; record WEL/WIP status, premature-read observation, page-cross rejection and CRC readback.
13. Do not run an endurance loop. Use only the documented test addresses on a dedicated lab part.
14. Record results in `evidence/measurement-template.csv`; expected values never enter measured fields.
