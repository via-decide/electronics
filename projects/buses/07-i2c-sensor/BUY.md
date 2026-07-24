# Buy

Use shared kits; do not repurchase common parts. The machine-readable copy is `bom.csv`.

| Need/status | Exact part or reference | Package/form | Voltage boundary | India-friendly search | Substitution/prohibition | Source |
| --- | --- | --- | --- | --- | --- | --- |
| required / verified | Espressif Systems `ESP32-DEVKITC-32E` | development board, male headers | USB input; 3.3 V logic and project rail | Espressif ESP32 DevKitC V4 WROOM-32E original India | A clone is SUGGESTED only after pinout, regulator and module marking are verified. | [source](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html) |
| required / suggested | varies `model must be recorded by learner` | 2.54 mm terminal strips | 3.3 V project use | 830 point solderless breadboard split power rail India | Any board is acceptable only after continuity mapping. | learner must verify |
| required / suggested | varies `n/a` | Dupont-compatible | 3.3 V project use | male male jumper wire 2.54mm India | Verify continuity; do not trust colour. | learner must verify |
| required / verified | Texas Instruments / Adafruit `TMP117AIDRVR on Adafruit product 4821` | header-compatible breakout | 1.7-5.5 V device range at stated temperature range; use 3.3 V | Adafruit 4821 TMP117 India | Alternative breakout is SUGGESTED only with published schematic and 3.3 V I/O. | [source](https://www.ti.com/lit/gpn/TMP117) |
| optional / verified | Saleae reference; alternatives require verification `Logic 8 reference` | USB instrument | select 3.3 V threshold; obey input range | logic analyzer documented 3.3V input India | Generic 24 MHz clones are SUGGESTED only; verify input protection and never attach unknown voltages. | [source](https://www.saleae.com/logic) |

India-friendly search terms are provided without price or stock claims. Prefer authorized distributors.
`verified` means the named part's documented electrical properties fit this circuit; it does not mean
the received item or physical build was tested. Sources were retrieved 2026-07-25.
