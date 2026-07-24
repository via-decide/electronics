# Build

1. Disconnect USB and all other power.
2. Map breadboard rail continuity and mark any split.
3. Place components; verify package orientation against the exact datasheet.
4. Add GND, then 3.3 V, then signal wires one at a time.
5. Add each required 100 nF decoupling capacitor at external IC supply pins.
6. Check continuity from every source to destination in `pinmap.yaml`.
7. Complete every blocking item in `BEFORE-YOU-POWER.md`.
8. Inspect the TMP117 breakout product and open-hardware schematic; identify VIN, GND, SDA and SCL.
9. Wire 3.3 V, GND, GPIO21 SDA and GPIO22 SCL. Do not add parallel pull-ups until the breakout pull-ups are accounted for.
10. Measure both bus lines idle, then run address probe and read device-ID register 0x0F.
11. Read raw temperature register 0x00 and record the decoded value as MEASURED only when real hardware ran.
12. Power off, disconnect SDA, observe NACK after power-up, then power off and restore it before recovery.
13. Record results in `evidence/measurement-template.csv`; expected values never enter measured fields.
