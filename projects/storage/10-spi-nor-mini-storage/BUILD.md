# Build

1. Disconnect USB and all other power.
2. Map breadboard rail continuity and mark any split.
3. Place components; verify package orientation against the exact datasheet.
4. Add GND, then 3.3 V, then signal wires one at a time.
5. Add each required 100 nF decoupling capacitor at external IC supply pins.
6. Check continuity from every source to destination in `pinmap.yaml`.
7. Complete every blocking item in `BEFORE-YOU-POWER.md`.
8. Solder or inspect the 200 mil SOP-8 adapter, then continuity-check every adapter pin to the IC lead.
9. Wire VCC/GND, SI/SO/SCLK, GPIO32 CS#, WP#/HOLD# high, 10 kohm CS# pull-up and 100 nF decoupling.
10. Run first with RUN_RESERVED_SECTOR_WRITE_DEMO=0; accept no write until JEDEC ID is exactly C2-20-16.
11. For a dedicated blank lab part, change the gate to 1 and run once to create two committed generations.
12. Confirm the higher prepared-but-uncommitted generation is rejected and recovery returns the prior committed generation.
13. Restore the write gate to zero after the demonstration.
14. Record results in `evidence/measurement-template.csv`; expected values never enter measured fields.
