# Buy

Use shared kits; do not repurchase common parts. The machine-readable copy is `bom.csv`.

| Need/status | Exact part or reference | Package/form | Voltage boundary | India-friendly search | Substitution/prohibition | Source |
| --- | --- | --- | --- | --- | --- | --- |
| required / verified | Espressif Systems `ESP32-DEVKITC-32E` | development board, male headers | USB input; 3.3 V logic and project rail | Espressif ESP32 DevKitC V4 WROOM-32E original India | A clone is SUGGESTED only after pinout, regulator and module marking are verified. | [source](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html) |
| required / suggested | varies `model must be recorded by learner` | 2.54 mm terminal strips | 3.3 V project use | 830 point solderless breadboard split power rail India | Any board is acceptable only after continuity mapping. | learner must verify |
| required / suggested | varies `n/a` | Dupont-compatible | 3.3 V project use | male male jumper wire 2.54mm India | Verify continuity; do not trust colour. | learner must verify |
| required / verified | Texas Instruments `SN74HC595N` | PDIP-16 | 2-6 V; use 3.3 V | SN74HC595N DIP16 TI India | 74HCT595 is prohibited at 3.3 V unless its input thresholds are revalidated. | [source](https://www.ti.com/lit/ds/symlink/sn74hc595.pdf) |
| required / verified | Kingbright or documented equivalent `L-7113ID or verified equivalent` | 5 mm through-hole | forward voltage must be measured; do not exceed datasheet current | L-7113ID red LED 5mm India | Colour and forward voltage may change; recalculate the resistor. | [source](https://www.kingbrightusa.com/images/catalog/SPEC/L-7113ID.pdf) |
| required / suggested | documented manufacturer `value-specific 0.25 W metal-film or carbon-film series` | axial through-hole | power checked per circuit | quarter watt through hole resistor assortment India | Measure value before insertion; 0.125 W is allowed only after power calculation. | learner must verify |
| required / suggested | documented manufacturer `record purchased series` | breadboard-compatible leads | 10 V minimum; 25 V preferred for 100 nF ceramic | 100nF X7R 25V and 10uF 16V through hole India | Capacitance may vary; electrolytic polarity must be marked. | learner must verify |
| optional / verified | Saleae reference; alternatives require verification `Logic 8 reference` | USB instrument | select 3.3 V threshold; obey input range | logic analyzer documented 3.3V input India | Generic 24 MHz clones are SUGGESTED only; verify input protection and never attach unknown voltages. | [source](https://www.saleae.com/logic) |

India-friendly search terms are provided without price or stock claims. Prefer authorized distributors.
`verified` means the named part's documented electrical properties fit this circuit; it does not mean
the received item or physical build was tested. Sources were retrieved 2026-07-25.
