# Buy

Use shared kits; do not repurchase common parts. The machine-readable copy is `bom.csv`.

| Need/status | Exact part or reference | Package/form | Voltage boundary | India-friendly search | Substitution/prohibition | Source |
| --- | --- | --- | --- | --- | --- | --- |
| required / verified | Espressif Systems `ESP32-DEVKITC-32E` | development board, male headers | USB input; 3.3 V logic and project rail | Espressif ESP32 DevKitC V4 WROOM-32E original India | A clone is SUGGESTED only after pinout, regulator and module marking are verified. | [source](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html) |
| required / suggested | varies `model must be recorded by learner` | 2.54 mm terminal strips | 3.3 V project use | 830 point solderless breadboard split power rail India | Any board is acceptable only after continuity mapping. | learner must verify |
| required / suggested | varies `n/a` | Dupont-compatible | 3.3 V project use | male male jumper wire 2.54mm India | Verify continuity; do not trust colour. | learner must verify |
| required / verified | Macronix `MX25L3233FM2I-08G` | 200 mil SOP-8 on pin-labelled 2.54 mm adapter | 2.65-3.6 V; use 3.3 V | MX25L3233FM2I-08G genuine India SOP8 adapter | Same-command NOR is SUGGESTED only after JEDEC ID, voltage, page and erase geometry checks. | [source](https://www.macronix.com/Lists/Datasheet/Attachments/8933/MX25L3233F%2C%203V%2C%2032Mb%2C%20v1.7.pdf) |
| required / suggested | documented manufacturer `value-specific 0.25 W metal-film or carbon-film series` | axial through-hole | power checked per circuit | quarter watt through hole resistor assortment India | Measure value before insertion; 0.125 W is allowed only after power calculation. | learner must verify |
| required / suggested | documented manufacturer `record purchased series` | breadboard-compatible leads | 10 V minimum; 25 V preferred for 100 nF ceramic | 100nF X7R 25V and 10uF 16V through hole India | Capacitance may vary; electrolytic polarity must be marked. | learner must verify |
| optional / verified | Saleae reference; alternatives require verification `Logic 8 reference` | USB instrument | select 3.3 V threshold; obey input range | logic analyzer documented 3.3V input India | Generic 24 MHz clones are SUGGESTED only; verify input protection and never attach unknown voltages. | [source](https://www.saleae.com/logic) |

India-friendly search terms are provided without price or stock claims. Prefer authorized distributors.
`verified` means the named part's documented electrical properties fit this circuit; it does not mean
the received item or physical build was tested. Sources were retrieved 2026-07-25.
