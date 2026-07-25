# Component Selection Ledger

Retrieval date: 2026-07-25
Physical test status for all v1 components: **not tested in this repository change**.

| Key | Manufacturer | Exact part/reference | Form | Supply/logic boundary | Primary source | Status | Physically tested |
| --- | --- | --- | --- | --- | --- | --- | --- |
| board | Espressif Systems | ESP32-DEVKITC-32E | development board, male headers | USB input; 3.3 V logic and project rail | https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html | VERIFIED by official board guide; physical execution remains unverified. | no |
| breadboard | varies | model must be recorded by learner | 2.54 mm terminal strips | 3.3 V project use | learner-selected; verify datasheet | SUGGESTED; internal rail topology must be measured, not assumed. | no |
| dmm | varies | record owned meter | handheld | rated probes; used only on SELV circuits here | learner-selected; verify datasheet | SUGGESTED; never use damaged probes. | no |
| jumper | varies | n/a | Dupont-compatible | 3.3 V project use | learner-selected; verify datasheet | SUGGESTED. | no |
| led | Kingbright or documented equivalent | L-7113ID or verified equivalent | 5 mm through-hole | forward voltage must be measured; do not exceed datasheet current | https://www.kingbrightusa.com/images/catalog/SPEC/L-7113ID.pdf | VERIFIED reference part; marketplace loose LEDs are SUGGESTED. | no |
| resistors | documented manufacturer | value-specific 0.25 W metal-film or carbon-film series | axial through-hole | power checked per circuit | learner-selected; verify datasheet | SUGGESTED; project dissipation is far below 0.25 W when wired as specified. | no |
| caps | documented manufacturer | record purchased series | breadboard-compatible leads | 10 V minimum; 25 V preferred for 100 nF ceramic | learner-selected; verify datasheet | SUGGESTED; 100 nF is placed at each IC supply pair. | no |
| button | documented manufacturer | 6x6 mm, four-lead breadboard type | through-hole | 3.3 V logic | learner-selected; verify datasheet | SUGGESTED; pin pairing must be measured. | no |
| pot | documented manufacturer | B10K breadboard module or through-hole | three terminal | 3.3 V divider | learner-selected; verify datasheet | SUGGESTED. | no |
| mosfet | Alpha & Omega Semiconductor | AO3400A | SOT-23 on pin-labelled 2.54 mm adapter | 3.3 V gate drive; project load is <=10 mA | https://www.aosmd.com/res/data_sheets/AO3400A.pdf | VERIFIED silicon; adapter assembly and pin labels require inspection. | no |
| bjt | onsemi | P2N2222AG | TO-92, straight leads | 40 V VCEO absolute maximum; v1 circuits use 3.3 V and <=30 mA | https://www.onsemi.com/download/data-sheet/pdf/p2n2222a-d.pdf | VERIFIED part family; not used as the Project 04 baseline. | no |
| buzzer | Same Sky | CMI-1295IC-0385T | 12 mm through-hole, polarity marked | 2-5 V operating range; 3 V rated; 30 mA rated supply current | https://www.sameskydevices.com/product/resource/cmi-1295ic-0385t.pdf | VERIFIED; optional for later output experiments, not a default Project 04 load. | no |
| usb_cable | documented USB-IF-listed supplier | record the purchased USB-IF certification or exact cable model | USB host plug to Micro-B plug, data capable | 5 V USB bus for the selected development board | https://www.usb.org/document-library/usb-20-specification | SUGGESTED until the purchased cable identity and data operation are verified. | no |
| tmp117 | Texas Instruments / Adafruit | TMP117AIDRVR on Adafruit product 4821 | header-compatible breakout | 1.7-5.5 V device range at stated temperature range; use 3.3 V | https://www.ti.com/lit/gpn/TMP117 | VERIFIED part and open-hardware reference; breakout authenticity must be checked. | no |
| level_shifter | Texas Instruments | PCA9306DCTR | SM8 on a schematic-verified, pin-labelled breakout | VREF1 1.2-3.3 V; VREF2 up to 5.5 V; not required for the 3.3 V-only v1 path | https://www.ti.com/lit/gpn/PCA9306 | VERIFIED silicon; optional breakout implementation is SUGGESTED until its schematic is checked. | no |
| hc595 | Texas Instruments | SN74HC595N | PDIP-16 | 2-6 V; use 3.3 V | https://www.ti.com/lit/ds/symlink/sn74hc595.pdf | VERIFIED. | no |
| eeprom | Microchip | 25LC256-I/P | PDIP-8 | 2.5-5.5 V; use 3.3 V | https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/25AA256-25LC256-256K-SPI-Bus-Serial-EEPROM-20001822J.pdf | VERIFIED; 64-byte pages. | no |
| nor | Macronix | MX25L3233FM2I-08G | 200 mil SOP-8 on pin-labelled 2.54 mm adapter | 2.65-3.6 V; use 3.3 V | https://www.macronix.com/Lists/Datasheet/Attachments/8933/MX25L3233F%2C%203V%2C%2032Mb%2C%20v1.7.pdf | VERIFIED, production/new-design family; adapter soldering requires inspection. | no |
| logic_analyzer | Saleae reference; alternatives require verification | Logic 8 reference | USB instrument | select 3.3 V threshold; obey input range | https://www.saleae.com/logic | VERIFIED reference instrument; no capture is claimed. | no |
| nand_fixture | Winbond / Texas Instruments / repository design | W25N01JWZEIQ + TPS7A20-1V8 | PCB-only WSON-8 fixture with validated bidirectional level shifting | 1.7-1.95 V NAND; 3.3 V host only through validated shifter | https://www.winbond.com/hq/product/code-storage-flash/qspi-nand/w25n-jw/?__locale=en | VERIFIED design reference; hardware remains DESIGN_RULES_PASSED, not bench verified. | no |
| usb_uart | Silicon Labs / Adafruit | CP2102N Friend, Adafruit product 5335 | USB-C breakout | 3.3 V UART logic; USB powers the adapter | https://www.silabs.com/documents/public/data-sheets/cp2102n-datasheet.pdf | VERIFIED reference adapter; selected DevKit already includes USB-UART. | no |
| usb_meter | documented manufacturer | record purchased model | inline USB or bench instrument | 5 V input side only; project rail remains 3.3 V | learner-selected; verify datasheet | SUGGESTED. | no |
| test_clips | documented manufacturer | record purchased model | 2.54 mm compatible hooks | 3.3 V signal use | learner-selected; verify datasheet | SUGGESTED. | no |
| flash_programmer | device support list required | not frozen | USB programmer plus SOP-8 fixture | 3.3 V only for selected NOR | learner-selected; verify datasheet | SUGGESTED optional tool. | no |
| carrier | repository design | TBD after connector contract freeze | custom PCB | 3.3 V host domain; separate 1.8 V NAND domain if used | learner-selected; verify datasheet | SUGGESTED future build; not yet frozen. | no |
| connector | TBD | TBD by cartridge mechanical/eject contract | PCB connector | 3.3 V and GND pin ordering must be frozen | learner-selected; verify datasheet | SUGGESTED placeholder; purchase prohibited until decision record exists. | no |
| protection | Texas Instruments | TPD4E05U06DQAR | USON-10, PCB-only | 5.5 V working-voltage class; validate clamping for final connector | https://www.ti.com/lit/ds/symlink/tpd4e05u06.pdf | SUGGESTED PCB protection candidate; not a breadboard part. | no |
| debug_header | repository design | TBD with carrier | PCB-only | 3.3 V logic | learner-selected; verify datasheet | SUGGESTED until carrier pinout freezes. | no |
| test_fixture | repository design | TBD from carrier test-point map | fixture | independently limited 3.3 V/1.8 V domains | learner-selected; verify datasheet | SUGGESTED future fixture. | no |

## Verified semiconductor operating fields

| Part | Min/max supply | Logic requirement | Relevant rating used by v1 | Decoupling | Interface | Counterfeit/clone risk |
| --- | --- | --- | --- | --- | --- | --- |
| ESP32-WROOM-32E | 3.0-3.6 V module supply; DevKit powered as documented | VIH/VIL and drive limits from ESP32 datasheet; no 5 V GPIO | learner loads are resistor-bounded; board current capability is not treated as GPIO capability | present on official board; external ICs still get local 100 nF | GPIO, ADC, UART, I2C, SPI | module marking, regulator, USB bridge and pin labels vary on clones |
| L-7113ID LED | forward device; no supply range | polarity required | v1 calculates current and stays below the exact LED continuous rating; typical Vf is never assumed measured | none | visual current path | loose LEDs may have unknown colour, polarity marking and rating |
| P2N2222AG | transistor junctions; v1 uses a 3.3 V control domain | base current must be resistor limited; verify the TO-92 E-B-C pinout | 40 V VCEO and 600 mA absolute maximum are not design targets; kit exercises remain <=30 mA | none at the transistor; decouple the switched load where its datasheet requires it | NPN low-side switch | PN2222A, P2N2222A and metal-can 2N2222A can have different pin arrangements |
| AO3400A | VDS absolute max 30 V; v1 uses 3.3 V | RDS(on) is specified at VGS=2.5 V; this is why it is selected | dedicated v1 load is about 10 mA or less; package thermal limits are not used as breadboard load targets | 100 ohm gate series, 100 kohm gate pull-down; no supply capacitor on the MOSFET itself | low-side switch | top markings and generic “AO3400 modules” are frequently untraceable |
| CMI-1295IC-0385T | 2-5 V operating; 3 V rated | internally driven DC input with marked polarity | 30 mA rated current, therefore not a direct GPIO load | local rail decoupling follows the switched-stage design | audible indicator | unmarked active and passive buzzers are not interchangeable |
| TMP117AIDRVR | 1.7-5.5 V over the datasheet's stated range; v1 uses 3.3 V | I2C/SMBus levels; breakout must preserve 3.3 V compatibility | device ID 0x0117; temperature is measured, never fabricated | breakout schematic plus local rail check | I2C register device | breakout may contain a different sensor or undocumented pull-ups |
| PCA9306DCTR | VREF1 1.2-3.3 V and VREF2 up to 5.5 V; unused in the 3.3 V-only v1 path | passive open-drain translation requires correctly biased reference rails and pull-ups | no push-pull drive; it is explicitly prohibited as a generic SPI translator | 100 nF per local reference rail on a verified breakout | optional I2C/SMBus translation | BSS138 modules are not assumed equivalent without a schematic |
| SN74HC595N | 2-6 V; v1 uses 3.3 V | same-rail CMOS logic; HCT substitution is prohibited without threshold analysis | eight LED outputs each use 1 kohm; output-current and package limits remain datasheet gates | 100 nF at pins 16/8 | synchronous serial shift plus separate RCLK latch | HC/HCT suffix and pin-1 orientation are common purchasing errors |
| 25LC256-I/P | 2.5-5.5 V; v1 uses 3.3 V | SPI levels referenced to VCC | maximum write current is documented as 5 mA; page size is 64 bytes | 100 nF at pins 8/4 | SPI EEPROM | 24LC256 is I2C, not a valid title-level substitute |
| MX25L3233FM2I-08G | 2.65-3.6 V; v1 uses 3.3 V | SPI levels referenced to VCC | 256-byte page, 4 KiB sector; writes blocked unless JEDEC ID is C2-20-16 | 100 nF at pins 8/4 and 10 kohm CS# pull-up | JEDEC SPI NOR | recycled or remarked flash and mirrored SOP adapters are blocking risks |
| W25N01JWZEIQ fixture | 1.7-1.95 V NAND rail; never connect the bare device to 3.3 V | host signalling only through the repository's validated bidirectional translation design | 1 Gbit raw NAND geometry and ECC/status behaviour are handled by the existing platform contract | fixture power tree uses local high-frequency and bulk decoupling from the versioned design | QSPI NAND, advanced continuation only | WSON marking, adapter topology and undocumented breakout regulators are blocking risks |
| CP2102N Friend | USB-powered adapter; UART side is selected for 3.3 V logic | TX and RX cross at the endpoint and all devices share ground | adapter is optional because DevKitC already contains a USB-UART bridge | use the published breakout schematic; no learner-added IC bypassing | USB to UART | generic adapters may expose 5 V TX, counterfeit bridges or mislabeled power pins |
| TPD4E05U06DQAR | 5.5 V working-voltage class; final clamping must be validated against the connector | place at the protected connector with a short return path | four low-capacitance channels; PCB-only future carrier component | not applicable | ESD protection | similarly named arrays can have different pinouts, capacitance and clamping behaviour |

Generic breadboards, passives, buttons, potentiometers and instruments remain **SUGGESTED** until
the learner records manufacturer, model, electrical rating and received-item inspection. Their
unknown fields are not silently replaced with typical values.

## Counterfeit and clone controls

Buy semiconductors from an authorized distributor when possible. For Indian purchasing, search
Mouser India, DigiKey India and element14 India by exact MPN before using a marketplace. A clone
board is not automatically unsafe, but its regulator, USB-UART bridge, pin labels, module marking
and power path must be revalidated. AO3400A and serial flash top markings are commonly copied;
record seller, lot marking and received package before assembly.

## Decoupling policy

Each external IC receives 100 nF ceramic directly across its supply pins. A 10 uF bulk capacitor
may be added at the project rail entry. Capacitor dielectric, value, voltage rating and polarity are
recorded in the evidence sheet.
