# Build

1. Disconnect USB and all other power.
2. Map breadboard rail continuity and mark any split.
3. Place components; verify package orientation against the exact datasheet.
4. Add GND, then 3.3 V, then signal wires one at a time.
5. Add each required 100 nF decoupling capacitor at external IC supply pins.
6. Check continuity from every source to destination in `pinmap.yaml`.
7. Complete every blocking item in `BEFORE-YOU-POWER.md`.
8. With all power disconnected, set the DMM to continuity and touch the probes together to confirm the beeper.
9. Test two holes in one five-hole terminal strip, then test across the centre channel; record both results.
10. Test each red and blue rail at the top, centre and bottom. Mark every discontinuity on a paper rail map.
11. Leave a discovered split open, confirm it, then bridge only matching rail segments and retest continuity.
12. Connect ESP32 3V3 to the verified positive rail and GND to the verified return rail; connect USB last.
13. Measure rail-to-ground voltage at both sides of the former split and record the breadboard model.
14. Record results in `evidence/measurement-template.csv`; expected values never enter measured fields.
