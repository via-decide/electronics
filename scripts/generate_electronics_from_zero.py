#!/usr/bin/env python3
"""Generate the Electronics From Zero v1 curriculum and physical project set.

The generator makes the repeated project contract reviewable: shared structure is
produced from one implementation while electrical choices, wiring, measurements,
failures, and firmware remain project-specific data.
"""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
RETRIEVED = "2026-07-25"
BOARD = "Espressif ESP32-DevKitC V4 with ESP32-WROOM-32E"
SDK = "ESP-IDF v5.2.3"


SOURCES = {
    "devkit": (
        "Espressif",
        "ESP32-DevKitC V4 User Guide",
        "https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/"
        "esp32-devkitc/user_guide.html",
    ),
    "module": (
        "Espressif",
        "ESP32-WROOM-32E/32UE Datasheet",
        "https://www.espressif.com/sites/default/files/documentation/"
        "esp32-wroom-32e_esp32-wroom-32ue_datasheet_en.pdf",
    ),
    "soc": (
        "Espressif",
        "ESP32 Series Datasheet",
        "https://documentation.espressif.com/esp32_datasheet_en.pdf",
    ),
    "gpio": (
        "Espressif",
        "ESP-IDF GPIO Driver",
        "https://docs.espressif.com/projects/esp-idf/en/stable/esp32/"
        "api-reference/peripherals/gpio.html",
    ),
    "adc": (
        "Espressif",
        "ESP-IDF ADC Oneshot Driver",
        "https://docs.espressif.com/projects/esp-idf/en/stable/esp32/"
        "api-reference/peripherals/adc/adc_oneshot.html",
    ),
    "uart": (
        "Espressif",
        "ESP-IDF UART Driver",
        "https://docs.espressif.com/projects/esp-idf/en/stable/esp32/"
        "api-reference/peripherals/uart.html",
    ),
    "i2c": (
        "Espressif",
        "ESP-IDF I2C Driver",
        "https://docs.espressif.com/projects/esp-idf/en/stable/esp32/"
        "api-reference/peripherals/i2c.html",
    ),
    "spi": (
        "Espressif",
        "ESP-IDF SPI Master Driver",
        "https://docs.espressif.com/projects/esp-idf/en/stable/esp32/"
        "api-reference/peripherals/spi_master.html",
    ),
    "i2c_spec": (
        "NXP",
        "UM10204 I2C-bus Specification and User Manual",
        "https://www.nxp.com/documents/user_manual/UM10204.pdf",
    ),
    "tmp117": (
        "Texas Instruments",
        "TMP117 Datasheet",
        "https://www.ti.com/lit/gpn/TMP117",
    ),
    "tmp117_breakout": (
        "Adafruit",
        "TMP117 Breakout Product 4821 and Open Hardware",
        "https://github.com/adafruit/Adafruit-TMP117-PCB",
    ),
    "level_shifter": (
        "Texas Instruments",
        "PCA9306 Dual Bidirectional I2C/SMBus Voltage-Level Translator Datasheet",
        "https://www.ti.com/lit/gpn/PCA9306",
    ),
    "hc595": (
        "Texas Instruments",
        "SN74HC595 Datasheet",
        "https://www.ti.com/lit/ds/symlink/sn74hc595.pdf",
    ),
    "eeprom": (
        "Microchip",
        "25AA256/25LC256 Datasheet",
        "https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/"
        "ProductDocuments/DataSheets/25AA256-25LC256-256K-SPI-Bus-Serial-"
        "EEPROM-20001822J.pdf",
    ),
    "nor": (
        "Macronix",
        "MX25L3233F Datasheet",
        "https://www.macronix.com/Lists/Datasheet/Attachments/8933/"
        "MX25L3233F%2C%203V%2C%2032Mb%2C%20v1.7.pdf",
    ),
    "nor_status": (
        "Macronix",
        "Serial NOR Product Status",
        "https://www.macronix.com/en-us/products/NOR-Flash/Serial-NOR-Flash/"
        "Pages/default.aspx",
    ),
    "mosfet": (
        "Alpha & Omega Semiconductor",
        "AO3400A Datasheet",
        "https://www.aosmd.com/res/data_sheets/AO3400A.pdf",
    ),
    "bjt": (
        "onsemi",
        "P2N2222A Datasheet",
        "https://www.onsemi.com/download/data-sheet/pdf/p2n2222a-d.pdf",
    ),
    "buzzer": (
        "Same Sky",
        "CMI-1295IC-0385T Magnetic Buzzer Indicator Datasheet",
        "https://www.sameskydevices.com/product/resource/cmi-1295ic-0385t.pdf",
    ),
    "usb_cable": (
        "USB Implementers Forum",
        "USB 2.0 Specification and Micro-USB Documents",
        "https://www.usb.org/document-library/usb-20-specification",
    ),
    "logic": (
        "Saleae",
        "Logic Analyzer Input Specifications",
        "https://www.saleae.com/logic",
    ),
    "nand": (
        "Winbond",
        "W25N-JW QSPI NAND Product Page",
        "https://www.winbond.com/hq/product/code-storage-flash/qspi-nand/w25n-jw/"
        "?__locale=en",
    ),
    "ldo": (
        "Texas Instruments",
        "TPS7A20 Datasheet",
        "https://www.ti.com/lit/ds/symlink/tps7a20.pdf",
    ),
    "esd": (
        "Texas Instruments",
        "TPD4E05U06 Datasheet",
        "https://www.ti.com/lit/ds/symlink/tpd4e05u06.pdf",
    ),
    "usb_uart": (
        "Silicon Labs / Adafruit",
        "CP2102N Datasheet and Friend Open Hardware",
        "https://www.silabs.com/documents/public/data-sheets/cp2102n-datasheet.pdf",
    ),
}


PARTS = {
    "board": {
        "category": "controller",
        "description": BOARD,
        "manufacturer": "Espressif Systems",
        "mpn": "ESP32-DEVKITC-32E",
        "package": "development board, male headers",
        "voltage": "USB input; 3.3 V logic and project rail",
        "search": "Espressif ESP32 DevKitC V4 WROOM-32E original India",
        "sub": "A clone is SUGGESTED only after pinout, regulator and module marking are verified.",
        "url": SOURCES["devkit"][2],
        "notes": "VERIFIED by official board guide; physical execution remains unverified.",
    },
    "breadboard": {
        "category": "interconnect",
        "description": "830-point solderless breadboard with documented split rails",
        "manufacturer": "varies",
        "mpn": "model must be recorded by learner",
        "package": "2.54 mm terminal strips",
        "voltage": "3.3 V project use",
        "search": "830 point solderless breadboard split power rail India",
        "sub": "Any board is acceptable only after continuity mapping.",
        "url": "",
        "notes": "SUGGESTED; internal rail topology must be measured, not assumed.",
    },
    "dmm": {
        "category": "instrument",
        "description": "Digital multimeter with DC voltage, resistance and continuity",
        "manufacturer": "varies",
        "mpn": "record owned meter",
        "package": "handheld",
        "voltage": "rated probes; used only on SELV circuits here",
        "search": "digital multimeter continuity replaceable fuse India",
        "sub": "Must have intact leads and a fused current input if current mode is used.",
        "url": "",
        "notes": "SUGGESTED; never use damaged probes.",
    },
    "jumper": {
        "category": "interconnect",
        "description": "Male-to-male 2.54 mm jumper wires",
        "manufacturer": "varies",
        "mpn": "n/a",
        "package": "Dupont-compatible",
        "voltage": "3.3 V project use",
        "search": "male male jumper wire 2.54mm India",
        "sub": "Verify continuity; do not trust colour.",
        "url": "",
        "notes": "SUGGESTED.",
    },
    "led": {
        "category": "indicator",
        "description": "Diffused red LED",
        "manufacturer": "Kingbright or documented equivalent",
        "mpn": "L-7113ID or verified equivalent",
        "package": "5 mm through-hole",
        "voltage": "forward voltage must be measured; do not exceed datasheet current",
        "search": "L-7113ID red LED 5mm India",
        "sub": "Colour and forward voltage may change; recalculate the resistor.",
        "url": "https://www.kingbrightusa.com/images/catalog/SPEC/L-7113ID.pdf",
        "notes": "VERIFIED reference part; marketplace loose LEDs are SUGGESTED.",
    },
    "resistors": {
        "category": "passive",
        "description": "220 ohm, 1 kohm, 4.7 kohm, 10 kohm, 100 kohm resistors",
        "manufacturer": "documented manufacturer",
        "mpn": "value-specific 0.25 W metal-film or carbon-film series",
        "package": "axial through-hole",
        "voltage": "power checked per circuit",
        "search": "quarter watt through hole resistor assortment India",
        "sub": "Measure value before insertion; 0.125 W is allowed only after power calculation.",
        "url": "",
        "notes": "SUGGESTED; project dissipation is far below 0.25 W when wired as specified.",
    },
    "caps": {
        "category": "passive",
        "description": "100 nF X7R ceramic and 10 uF electrolytic capacitors",
        "manufacturer": "documented manufacturer",
        "mpn": "record purchased series",
        "package": "breadboard-compatible leads",
        "voltage": "10 V minimum; 25 V preferred for 100 nF ceramic",
        "search": "100nF X7R 25V and 10uF 16V through hole India",
        "sub": "Capacitance may vary; electrolytic polarity must be marked.",
        "url": "",
        "notes": "SUGGESTED; 100 nF is placed at each IC supply pair.",
    },
    "button": {
        "category": "switch",
        "description": "Normally-open tactile push button",
        "manufacturer": "documented manufacturer",
        "mpn": "6x6 mm, four-lead breadboard type",
        "package": "through-hole",
        "voltage": "3.3 V logic",
        "search": "6x6 tactile switch breadboard India",
        "sub": "Map internally common pin pairs with continuity mode.",
        "url": "",
        "notes": "SUGGESTED; pin pairing must be measured.",
    },
    "pot": {
        "category": "passive",
        "description": "10 kohm linear potentiometer",
        "manufacturer": "documented manufacturer",
        "mpn": "B10K breadboard module or through-hole",
        "package": "three terminal",
        "voltage": "3.3 V divider",
        "search": "B10K linear potentiometer breadboard India",
        "sub": "Verify end terminals and wiper using resistance mode.",
        "url": "",
        "notes": "SUGGESTED.",
    },
    "mosfet": {
        "category": "semiconductor",
        "description": "30 V N-channel MOSFET, RDS(on) specified at VGS=2.5 V",
        "manufacturer": "Alpha & Omega Semiconductor",
        "mpn": "AO3400A",
        "package": "SOT-23 on pin-labelled 2.54 mm adapter",
        "voltage": "3.3 V gate drive; project load is <=10 mA",
        "search": "AO3400A genuine SOT23 breakout adapter India",
        "sub": "Do not substitute IRF520, IRLZ44N or an untraceable module.",
        "url": SOURCES["mosfet"][2],
        "notes": "VERIFIED silicon; adapter assembly and pin labels require inspection.",
    },
    "bjt": {
        "category": "semiconductor",
        "description": "NPN switching transistor for later bounded low-current experiments",
        "manufacturer": "onsemi",
        "mpn": "P2N2222AG",
        "package": "TO-92, straight leads",
        "voltage": "40 V VCEO absolute maximum; v1 circuits use 3.3 V and <=30 mA",
        "search": "P2N2222AG onsemi TO-92 India authorized distributor",
        "sub": "PN2222A and metal-can 2N2222A pinouts may differ; verify the exact datasheet before insertion.",
        "url": SOURCES["bjt"][2],
        "notes": "VERIFIED part family; not used as the Project 04 baseline.",
    },
    "buzzer": {
        "category": "output",
        "description": "3 V internally driven magnetic indicator buzzer",
        "manufacturer": "Same Sky",
        "mpn": "CMI-1295IC-0385T",
        "package": "12 mm through-hole, polarity marked",
        "voltage": "2-5 V operating range; 3 V rated; 30 mA rated supply current",
        "search": "CMI-1295IC-0385T Same Sky India authorized distributor",
        "sub": "Do not drive this 30 mA load directly from a GPIO; use a verified transistor stage and observe polarity.",
        "url": SOURCES["buzzer"][2],
        "notes": "VERIFIED; optional for later output experiments, not a default Project 04 load.",
    },
    "usb_cable": {
        "category": "power and data",
        "description": "USB data cable matching the DevKitC Micro-B receptacle and host connector",
        "manufacturer": "documented USB-IF-listed supplier",
        "mpn": "record the purchased USB-IF certification or exact cable model",
        "package": "USB host plug to Micro-B plug, data capable",
        "voltage": "5 V USB bus for the selected development board",
        "search": "USB-IF certified USB data cable Micro-B India",
        "sub": "A charge-only cable is unsuitable for firmware upload; reject damaged, unmarked or loose cables.",
        "url": SOURCES["usb_cable"][2],
        "notes": "SUGGESTED until the purchased cable identity and data operation are verified.",
    },
    "tmp117": {
        "category": "sensor",
        "description": "TMP117 I2C temperature sensor breakout",
        "manufacturer": "Texas Instruments / Adafruit",
        "mpn": "TMP117AIDRVR on Adafruit product 4821",
        "package": "header-compatible breakout",
        "voltage": "1.7-5.5 V device range at stated temperature range; use 3.3 V",
        "search": "Adafruit 4821 TMP117 India",
        "sub": "Alternative breakout is SUGGESTED only with published schematic and 3.3 V I/O.",
        "url": SOURCES["tmp117"][2],
        "notes": "VERIFIED part and open-hardware reference; breakout authenticity must be checked.",
    },
    "level_shifter": {
        "category": "interface",
        "description": "Optional dual bidirectional I2C/SMBus voltage-level translator",
        "manufacturer": "Texas Instruments",
        "mpn": "PCA9306DCTR",
        "package": "SM8 on a schematic-verified, pin-labelled breakout",
        "voltage": "VREF1 1.2-3.3 V; VREF2 up to 5.5 V; not required for the 3.3 V-only v1 path",
        "search": "PCA9306DCTR genuine I2C level shifter breakout India",
        "sub": "Use only for justified mixed-voltage open-drain I2C; never treat it as a push-pull SPI translator.",
        "url": SOURCES["level_shifter"][2],
        "notes": "VERIFIED silicon; optional breakout implementation is SUGGESTED until its schematic is checked.",
        "status": "suggested",
    },
    "hc595": {
        "category": "logic",
        "description": "8-bit serial-in parallel-out shift register",
        "manufacturer": "Texas Instruments",
        "mpn": "SN74HC595N",
        "package": "PDIP-16",
        "voltage": "2-6 V; use 3.3 V",
        "search": "SN74HC595N DIP16 TI India",
        "sub": "74HCT595 is prohibited at 3.3 V unless its input thresholds are revalidated.",
        "url": SOURCES["hc595"][2],
        "notes": "VERIFIED.",
    },
    "eeprom": {
        "category": "memory",
        "description": "256 Kbit SPI serial EEPROM",
        "manufacturer": "Microchip",
        "mpn": "25LC256-I/P",
        "package": "PDIP-8",
        "voltage": "2.5-5.5 V; use 3.3 V",
        "search": "25LC256-I/P Microchip DIP8 India",
        "sub": "25AA256 is compatible only after speed/voltage needs are checked; 24LC256 is I2C and prohibited.",
        "url": SOURCES["eeprom"][2],
        "notes": "VERIFIED; 64-byte pages.",
    },
    "nor": {
        "category": "memory",
        "description": "32 Mbit 3 V serial NOR flash",
        "manufacturer": "Macronix",
        "mpn": "MX25L3233FM2I-08G",
        "package": "200 mil SOP-8 on pin-labelled 2.54 mm adapter",
        "voltage": "2.65-3.6 V; use 3.3 V",
        "search": "MX25L3233FM2I-08G genuine India SOP8 adapter",
        "sub": "Same-command NOR is SUGGESTED only after JEDEC ID, voltage, page and erase geometry checks.",
        "url": SOURCES["nor"][2],
        "notes": "VERIFIED, production/new-design family; adapter soldering requires inspection.",
    },
    "logic_analyzer": {
        "category": "instrument",
        "description": "Logic analyzer with documented 3.3 V-compatible inputs",
        "manufacturer": "Saleae reference; alternatives require verification",
        "mpn": "Logic 8 reference",
        "package": "USB instrument",
        "voltage": "select 3.3 V threshold; obey input range",
        "search": "logic analyzer documented 3.3V input India",
        "sub": "Generic 24 MHz clones are SUGGESTED only; verify input protection and never attach unknown voltages.",
        "url": SOURCES["logic"][2],
        "notes": "VERIFIED reference instrument; no capture is claimed.",
    },
    "nand_fixture": {
        "category": "storage fixture",
        "description": "Existing W25N01JW 1.8 V serial NAND lab fixture",
        "manufacturer": "Winbond / Texas Instruments / repository design",
        "mpn": "W25N01JWZEIQ + TPS7A20-1V8",
        "package": "PCB-only WSON-8 fixture with validated bidirectional level shifting",
        "voltage": "1.7-1.95 V NAND; 3.3 V host only through validated shifter",
        "search": "W25N01JWZEIQ TPS7A20 1V8 authorized distributor India",
        "sub": "Never connect the bare NAND to 3.3 V; reuse the versioned fixture constraints.",
        "url": SOURCES["nand"][2],
        "notes": "VERIFIED design reference; hardware remains DESIGN_RULES_PASSED, not bench verified.",
    },
    "usb_uart": {
        "category": "interface",
        "description": "Optional 3.3 V-logic USB-to-UART adapter",
        "manufacturer": "Silicon Labs / Adafruit",
        "mpn": "CP2102N Friend, Adafruit product 5335",
        "package": "USB-C breakout",
        "voltage": "3.3 V UART logic; USB powers the adapter",
        "search": "Adafruit 5335 CP2102N Friend India",
        "sub": "Required only for a second external UART device; verify TX/RX voltage before use.",
        "url": SOURCES["usb_uart"][2],
        "notes": "VERIFIED reference adapter; selected DevKit already includes USB-UART.",
    },
    "usb_meter": {
        "category": "instrument",
        "description": "USB voltage/current meter or current-limited 5 V bench source",
        "manufacturer": "documented manufacturer",
        "mpn": "record purchased model",
        "package": "inline USB or bench instrument",
        "voltage": "5 V input side only; project rail remains 3.3 V",
        "search": "USB power meter current limit data cable India",
        "sub": "Must document voltage/current range and connector wiring.",
        "url": "",
        "notes": "SUGGESTED.",
    },
    "test_clips": {
        "category": "instrument accessory",
        "description": "Insulated micro-hook logic test leads",
        "manufacturer": "documented manufacturer",
        "mpn": "record purchased model",
        "package": "2.54 mm compatible hooks",
        "voltage": "3.3 V signal use",
        "search": "insulated micro hook logic analyzer test clip India",
        "sub": "Reject exposed clips that can bridge adjacent IC pins.",
        "url": "",
        "notes": "SUGGESTED.",
    },
    "flash_programmer": {
        "category": "instrument",
        "description": "Optional programmer supporting the exact NOR MPN and 3.3 V",
        "manufacturer": "device support list required",
        "mpn": "not frozen",
        "package": "USB programmer plus SOP-8 fixture",
        "voltage": "3.3 V only for selected NOR",
        "search": "SPI NOR programmer MX25L3233F supported device list India",
        "sub": "Do not buy until the programmer's current device list names MX25L3233F.",
        "url": "",
        "notes": "SUGGESTED optional tool.",
    },
    "carrier": {
        "category": "development carrier",
        "description": "Versioned cartridge development carrier PCB",
        "manufacturer": "repository design",
        "mpn": "TBD after connector contract freeze",
        "package": "custom PCB",
        "voltage": "3.3 V host domain; separate 1.8 V NAND domain if used",
        "search": "do not purchase before design freeze",
        "sub": "Perfboard may prototype signals but cannot replace the frozen carrier for validation.",
        "url": "",
        "notes": "SUGGESTED future build; not yet frozen.",
    },
    "connector": {
        "category": "connector",
        "description": "Keyed cartridge connector and mating fixture",
        "manufacturer": "TBD",
        "mpn": "TBD by cartridge mechanical/eject contract",
        "package": "PCB connector",
        "voltage": "3.3 V and GND pin ordering must be frozen",
        "search": "do not purchase before pin-order and mating-cycle decision",
        "sub": "No generic edge connector is a safe substitute before power-first/ground-first analysis.",
        "url": "",
        "notes": "SUGGESTED placeholder; purchase prohibited until decision record exists.",
    },
    "protection": {
        "category": "protection",
        "description": "Four-channel low-capacitance ESD protection array",
        "manufacturer": "Texas Instruments",
        "mpn": "TPD4E05U06DQAR",
        "package": "USON-10, PCB-only",
        "voltage": "5.5 V working-voltage class; validate clamping for final connector",
        "search": "TPD4E05U06DQAR authorized distributor India",
        "sub": "Final selection requires connector ESD target, layout and signal-integrity review.",
        "url": SOURCES["esd"][2],
        "notes": "SUGGESTED PCB protection candidate; not a breadboard part.",
    },
    "debug_header": {
        "category": "debug",
        "description": "Ground-adjacent test pads and keyed debug header",
        "manufacturer": "repository design",
        "mpn": "TBD with carrier",
        "package": "PCB-only",
        "voltage": "3.3 V logic",
        "search": "2.54mm keyed debug header test point India",
        "sub": "Every signal probe requires an adjacent ground reference.",
        "url": "",
        "notes": "SUGGESTED until carrier pinout freezes.",
    },
    "test_fixture": {
        "category": "test fixture",
        "description": "Pogo-pin carrier fixture with current limit and emergency disconnect",
        "manufacturer": "repository design",
        "mpn": "TBD from carrier test-point map",
        "package": "fixture",
        "voltage": "independently limited 3.3 V/1.8 V domains",
        "search": "pogo pin test fixture components India",
        "sub": "Fixture cannot be finalized before carrier test points and current limits freeze.",
        "url": "",
        "notes": "SUGGESTED future fixture.",
    },
}


PROJECTS = [
    {
        "id": "01-know-your-breadboard",
        "group": "breadboard",
        "title": "Know Your Breadboard",
        "difficulty": "beginner",
        "minutes": 60,
        "question": "Which holes are electrically connected, and where does the power rail stop?",
        "why": "The breadboard is not a drawing surface. Its hidden metal strips decide which points share a node.",
        "build": "Map terminal strips and split rails with continuity mode, then apply 3.3 V and record the first rail measurement.",
        "measure": "Continuity between selected holes and DC voltage between the labelled 3.3 V rail and GND.",
        "expected": "Connected clips produce continuity; isolated clips do not. Powered rail is expected near the board 3.3 V output, but the measured value must be recorded.",
        "break": "First leave the centre break in a split rail unbridged. Detect the break with continuity mode, power down, add one bridge, then retest.",
        "success": "The learner can identify every connected row, the centre channel, each rail segment, 3.3 V, and GND without using wire colour as evidence.",
        "parts": ["board", "breadboard", "dmm", "jumper"],
        "tools": ["digital multimeter", "USB cable"],
        "interfaces": [],
        "prereqs": ["none"],
        "pins": [
            ("ESP32 3V3", "red rail", "red", "TP1"),
            ("ESP32 GND", "blue rail", "black", "TP2"),
            ("rail bridge +", "upper/lower red segments", "red", "TP3"),
            ("rail bridge -", "upper/lower blue segments", "black", "TP4"),
        ],
        "firmware": None,
    },
    {
        "id": "02-led-current",
        "group": "breadboard",
        "title": "LED Current Experiment",
        "difficulty": "beginner",
        "minutes": 75,
        "question": "Why does an LED need current control, and what changes when resistance changes?",
        "why": "The LED is not the experiment. Current control is the experiment.",
        "build": "Wire 3.3 V, a measured resistor and a red LED in series. Repeat with 220 ohm, 1 kohm and 10 kohm.",
        "measure": "LED voltage, resistor voltage and calculated current I=V_R/R for each resistor.",
        "expected": "For an illustrative 1.8 V LED drop, calculated current is about 6.8 mA, 1.5 mA and 0.15 mA. These are EXPECTED examples, not measured values.",
        "break": "Replace 220 ohm with 10 kohm and diagnose the dim LED as reduced current. Never omit the resistor.",
        "success": "Measured V_LED plus V_R is consistent with the measured rail within instrument and contact uncertainty.",
        "parts": ["board", "breadboard", "dmm", "jumper", "led", "resistors"],
        "tools": ["digital multimeter"],
        "interfaces": ["DC"],
        "prereqs": ["01-know-your-breadboard"],
        "pins": [
            ("ESP32 3V3", "resistor input", "red", "TP1"),
            ("resistor output", "LED anode", "yellow", "TP2"),
            ("LED cathode", "GND", "black", "TP3"),
        ],
        "firmware": None,
    },
    {
        "id": "03-button-input",
        "group": "breadboard",
        "title": "Button Input: Floating, Pulled and Debounced",
        "difficulty": "beginner",
        "minutes": 90,
        "question": "Why does an unconnected digital input change when nobody pressed anything?",
        "why": "The button is not unstable. The unconnected input is electrically undefined; mechanical contacts also bounce.",
        "build": "Wire a normally-open button from GPIO27 to GND, use the internal pull-up, and compare raw state with a 30 ms debounced state.",
        "measure": "Idle and pressed voltage at GPIO27, raw transition count and debounced transition count.",
        "expected": "Idle is logic high near 3.3 V; pressed is logic low near 0 V. Exact values are MEASURED.",
        "break": "Disable the pull-up in firmware and leave the input open. Observe undefined changes, then restore the pull-up.",
        "success": "Serial output distinguishes raw and stable state and one deliberate press produces one stable transition.",
        "parts": ["board", "breadboard", "dmm", "jumper", "button"],
        "tools": ["digital multimeter", "serial terminal"],
        "interfaces": ["GPIO"],
        "prereqs": ["02-led-current"],
        "pins": [
            ("ESP32 GPIO27", "button side A", "yellow", "TP1"),
            ("button side B", "GND", "black", "TP2"),
        ],
        "firmware": "button",
    },
    {
        "id": "04-mosfet-load-switch",
        "group": "breadboard",
        "title": "MOSFET Low-Side Load Switch",
        "difficulty": "beginner",
        "minutes": 100,
        "question": "How can a GPIO control a load without supplying the load current?",
        "why": "A GPIO is a logic source, not a general-purpose power supply. The MOSFET separates control current from load current.",
        "build": "Use AO3400A as a 3.3 V low-side switch for a red LED and 1 kohm series resistor. Add 100 ohm gate series and 100 kohm gate pull-down.",
        "measure": "Gate-to-source voltage, drain voltage and load resistor voltage in ON and OFF states.",
        "expected": "GPIO low keeps the load off; GPIO high drives the gate near 3.3 V and lights the bounded low-current load.",
        "break": "Remove only the 100 kohm gate pull-down while power is off, then explain why the gate can retain charge. Restore it before normal use.",
        "success": "The load follows the logged gate command and the learner identifies gate, drain and source from the datasheet and adapter labels.",
        "parts": ["board", "breadboard", "dmm", "jumper", "led", "resistors", "mosfet"],
        "tools": ["digital multimeter", "serial terminal"],
        "interfaces": ["GPIO"],
        "prereqs": ["03-button-input"],
        "pins": [
            ("ESP32 GPIO25", "100 ohm then AO3400A gate", "yellow", "TP1"),
            ("AO3400A gate", "100 kohm to GND", "blue", "TP2"),
            ("AO3400A source", "GND", "black", "TP3"),
            ("3V3", "1 kohm → LED anode; LED cathode → AO3400A drain", "red", "TP4"),
        ],
        "firmware": "mosfet",
    },
    {
        "id": "05-analog-voltage",
        "group": "breadboard",
        "title": "Analog Voltage Measurement",
        "difficulty": "beginner",
        "minutes": 110,
        "question": "How different is an ADC code from a voltage you can trust?",
        "why": "An ADC returns a code. Voltage requires a transfer function, attenuation setting, calibration and evidence.",
        "build": "Wire a 10 kohm potentiometer between 3.3 V and GND with its wiper on GPIO34/ADC1_CH6. Read, average and calibrate.",
        "measure": "DMM wiper voltage, raw 12-bit codes, 64-sample mean and calibrated millivolts at several positions.",
        "expected": "Raw code should move monotonically with wiper voltage. Agreement with a DMM is UNKNOWN until calibrated and measured.",
        "break": "Compare one raw sample with a 64-sample average; then move the wiper near the rails and record where nonlinearity or clipping appears.",
        "success": "A table contains DMM voltage, raw mean, calibrated voltage, error and measurement conditions.",
        "parts": ["board", "breadboard", "dmm", "jumper", "pot", "caps"],
        "tools": ["digital multimeter", "serial terminal"],
        "interfaces": ["ADC"],
        "prereqs": ["04-mosfet-load-switch"],
        "pins": [
            ("ESP32 3V3", "potentiometer end A", "red", "TP1"),
            ("ESP32 GPIO34/ADC1_CH6", "potentiometer wiper", "yellow", "TP2"),
            ("ESP32 GND", "potentiometer end B", "black", "TP3"),
        ],
        "firmware": "adc",
    },
    {
        "id": "06-uart-conversation",
        "group": "buses",
        "title": "UART Framed Conversation",
        "difficulty": "intermediate",
        "minutes": 120,
        "question": "How do two devices agree where a message begins and whether it arrived intact?",
        "why": "UART moves bits. A frame adds meaning: magic, sequence, length, payload and CRC.",
        "build": "Jumper UART1 TX GPIO17 to UART2 RX GPIO16 on the selected WROOM-32E board and loop back a binary frame between independently configured peripherals.",
        "measure": "TX/RX idle voltage, accepted frame count, CRC rejection count and optional logic timing.",
        "expected": "At 115200 8N1, the looped frame is accepted and sequence increments. GPIO16/17 are not approved for WROVER variants with PSRAM.",
        "break": "Change only RX_BAUD to 57600, observe timeout/framing/CRC rejection, then restore 115200.",
        "success": "The receiver validates magic, length and CRC before printing the payload.",
        "parts": ["board", "breadboard", "jumper", "logic_analyzer"],
        "tools": ["serial terminal", "logic analyzer optional"],
        "interfaces": ["UART"],
        "prereqs": ["05-analog-voltage"],
        "pins": [
            ("ESP32 GPIO17/UART1 TX", "ESP32 GPIO16/UART2 RX", "yellow", "TP1"),
            ("ESP32 GND", "logic analyzer GND", "black", "TP2"),
        ],
        "firmware": "uart",
    },
    {
        "id": "07-i2c-sensor",
        "group": "buses",
        "title": "I2C TMP117 Register Transaction",
        "difficulty": "intermediate",
        "minutes": 130,
        "question": "How can two open-drain wires address a device and read a specific register?",
        "why": "I2C is not a library call. SDA and SCL are shared open-drain lines whose rise time comes from pull-ups and bus capacitance.",
        "build": "Wire Adafruit TMP117 breakout 4821 at 3.3 V, scan addresses, read device-ID register 0x0F, then temperature register 0x00.",
        "measure": "SDA/SCL idle voltage, detected address, device ID, ACK/NACK result and decoded temperature.",
        "expected": "Default 7-bit address is expected at 0x48 and device ID register reset value is 0x0117. Temperature is MEASURED, not predicted.",
        "break": "Disconnect SDA with power off, rerun and observe NACK/missing device. Restore it and run the documented nine-clock recovery.",
        "success": "Firmware shows at least one raw register transaction without a sensor abstraction library.",
        "parts": ["board", "breadboard", "jumper", "tmp117", "logic_analyzer"],
        "tools": ["digital multimeter", "serial terminal", "logic analyzer optional"],
        "interfaces": ["I2C"],
        "prereqs": ["06-uart-conversation"],
        "pins": [
            ("ESP32 3V3", "TMP117 VIN", "red", "TP1"),
            ("ESP32 GND", "TMP117 GND", "black", "TP2"),
            ("ESP32 GPIO21/SDA", "TMP117 SDA", "blue", "TP3"),
            ("ESP32 GPIO22/SCL", "TMP117 SCL", "yellow", "TP4"),
        ],
        "firmware": "i2c",
    },
    {
        "id": "08-spi-shift-register",
        "group": "buses",
        "title": "SPI-Like Shift Register",
        "difficulty": "intermediate",
        "minutes": 140,
        "question": "What do clock, data and latch signals physically do to eight visible outputs?",
        "why": "The shift register comes before flash because its output is visible. RCLK is a storage-register latch, not a generic SPI chip-select.",
        "build": "Wire SN74HC595N at 3.3 V with eight 1 kohm LED paths, shift a walking bit on MOSI/SHCP and latch it with RCLK.",
        "measure": "Clock, serial data and latch timing; Q0-Q7 visible state; 3.3 V supply at the IC.",
        "expected": "One LED moves across the outputs. Reversing bit order mirrors the direction.",
        "break": "Set SHIFT_LSB_FIRST to 1, rebuild and explain why the visible sequence reverses.",
        "success": "Captured or manually traced clock/data/latch transitions agree with the displayed output byte.",
        "parts": ["board", "breadboard", "jumper", "hc595", "led", "resistors", "caps", "logic_analyzer"],
        "tools": ["digital multimeter", "serial terminal", "logic analyzer recommended"],
        "interfaces": ["SPI-like synchronous serial"],
        "prereqs": ["07-i2c-sensor"],
        "pins": [
            ("ESP32 GPIO23/MOSI", "SN74HC595 SER pin 14", "blue", "TP1"),
            ("ESP32 GPIO18/SCLK", "SN74HC595 SRCLK pin 11", "yellow", "TP2"),
            ("ESP32 GPIO32", "SN74HC595 RCLK pin 12", "green", "TP3"),
            ("ESP32 3V3", "VCC pin 16 and SRCLR pin 10", "red", "TP4"),
            ("ESP32 GND", "GND pin 8 and OE# pin 13", "black", "TP5"),
            ("SN74HC595 Q0 pin 15", "1 kohm + LED0 anode; cathode to GND", "orange", "TP6"),
            ("SN74HC595 Q1 pin 1", "1 kohm + LED1 anode; cathode to GND", "orange", "TP7"),
            ("SN74HC595 Q2 pin 2", "1 kohm + LED2 anode; cathode to GND", "orange", "TP8"),
            ("SN74HC595 Q3 pin 3", "1 kohm + LED3 anode; cathode to GND", "orange", "TP9"),
            ("SN74HC595 Q4 pin 4", "1 kohm + LED4 anode; cathode to GND", "orange", "TP10"),
            ("SN74HC595 Q5 pin 5", "1 kohm + LED5 anode; cathode to GND", "orange", "TP11"),
            ("SN74HC595 Q6 pin 6", "1 kohm + LED6 anode; cathode to GND", "orange", "TP12"),
            ("SN74HC595 Q7 pin 7", "1 kohm + LED7 anode; cathode to GND", "orange", "TP13"),
        ],
        "firmware": "shift",
    },
    {
        "id": "09-spi-eeprom",
        "group": "storage",
        "title": "SPI EEPROM: Pages, Busy State and CRC",
        "difficulty": "intermediate",
        "minutes": 180,
        "question": "Why can a memory accept SPI traffic yet refuse or corrupt a write?",
        "why": "A storage write is a protocol: address validation, write-enable, page geometry, busy polling, readback and integrity.",
        "build": "Wire 25LC256-I/P at 3.3 V, write one bounded record within a 64-byte page, poll WIP, read back and verify CRC32.",
        "measure": "Supply, CS# idle, SPI signals, status register transitions and readback CRC.",
        "expected": "WREN sets WEL, WRITE begins a self-timed cycle, WIP eventually clears, and readback matches. Timing is MEASURED if captured.",
        "break": "Attempt a write without WREN; try a page-crossing request that firmware must reject; demonstrate a premature read path.",
        "success": "Every accepted write is bounds-checked, page-contained, busy-polled and verified.",
        "parts": ["board", "breadboard", "jumper", "eeprom", "resistors", "caps", "logic_analyzer"],
        "tools": ["digital multimeter", "serial terminal", "logic analyzer recommended"],
        "interfaces": ["SPI"],
        "prereqs": ["08-spi-shift-register"],
        "pins": [
            ("ESP32 GPIO23/MOSI", "25LC256 SI pin 5", "blue", "TP1"),
            ("ESP32 GPIO19/MISO", "25LC256 SO pin 2", "green", "TP2"),
            ("ESP32 GPIO18/SCLK", "25LC256 SCK pin 6", "yellow", "TP3"),
            ("ESP32 GPIO32/CS", "25LC256 CS# pin 1 and 10 kohm pull-up to 3V3", "white", "TP4"),
            ("ESP32 3V3", "VCC pin 8, WP# pin 3, HOLD# pin 7", "red", "TP5"),
            ("ESP32 GND", "VSS pin 4", "black", "TP6"),
        ],
        "firmware": "eeprom",
    },
    {
        "id": "10-spi-nor-mini-storage",
        "group": "storage",
        "title": "SPI NOR Mini-Storage",
        "difficulty": "advanced-beginner",
        "minutes": 240,
        "question": "How do pages and erase sectors become a recoverable committed record?",
        "why": "Storage is not saving bytes. A usable record needs geometry, integrity, commit ordering, redundant metadata and recovery.",
        "build": "Wire MX25L3233FM2I-08G at 3.3 V, read JEDEC ID, erase only reserved sectors, page-program a CRC-protected record, commit it and select last-known-good metadata.",
        "measure": "Supply, JEDEC ID, status transitions, program/erase busy time, record CRC and selected generation.",
        "expected": "A prepared but uncommitted higher generation is ignored; the newest fully committed CRC-valid copy wins.",
        "break": "Run the staged-record path that intentionally omits the final commit-state program. Recovery must retain the earlier committed copy.",
        "success": "Power-on scan returns a committed record or an explicit empty/corrupt state; it never silently accepts an invalid record.",
        "parts": ["board", "breadboard", "jumper", "nor", "resistors", "caps", "logic_analyzer"],
        "tools": ["digital multimeter", "serial terminal", "logic analyzer recommended"],
        "interfaces": ["SPI", "JEDEC NOR"],
        "prereqs": ["09-spi-eeprom"],
        "pins": [
            ("ESP32 GPIO23/MOSI", "MX25L3233F SI pin 5", "blue", "TP1"),
            ("ESP32 GPIO19/MISO", "MX25L3233F SO pin 2", "green", "TP2"),
            ("ESP32 GPIO18/SCLK", "MX25L3233F SCLK pin 6", "yellow", "TP3"),
            ("ESP32 GPIO32/CS", "MX25L3233F CS# pin 1 and 10 kohm pull-up to 3V3", "white", "TP4"),
            ("ESP32 3V3", "VCC pin 8, WP# pin 3, HOLD# pin 7", "red", "TP5"),
            ("ESP32 GND", "GND pin 4", "black", "TP6"),
        ],
        "firmware": "nor",
    },
]


LESSONS = [
    ("00-how-to-use-this-repository", "How to Use This Repository", "turn a question into a measured physical result", "none", "board, breadboard, DMM and notebook", "Project 01", "record FACT, EXPECTED, MEASURED and UNKNOWN separately"),
    ("01-electricity-you-can-measure", "Electricity You Can Measure", "make voltage, resistance and continuity observable", "lesson 00", "DMM, leads, resistor and unpowered breadboard", "Project 01", "predict the meter mode before touching a node"),
    ("02-breadboard-without-confusion", "Breadboard Without Confusion", "discover hidden connections and split rails", "lessons 00-01", "breadboard, DMM and jumpers", "Project 01", "draw a rail map supported by continuity tests"),
    ("03-led-and-resistor", "LED and Resistor", "bound current through a nonlinear component", "lessons 01-02", "red LED and 220 ohm, 1 kohm, 10 kohm resistors", "Project 02", "calculate current from measured resistor voltage"),
    ("04-button-and-pull-resistor", "Button and Pull Resistor", "give an otherwise floating input a defined state", "lesson 03", "button and GPIO27", "Project 03", "separate electrical definition from mechanical bounce"),
    ("05-transistor-as-a-switch", "Transistor as a Switch", "control load current without sourcing it from a GPIO", "lesson 04", "AO3400A adapter, LED load and gate resistors", "Project 04", "identify gate, drain and source from authoritative pin data"),
    ("06-voltage-divider-and-adc", "Voltage Divider and ADC", "turn a bounded analog voltage into evidence", "lesson 05", "10 kohm potentiometer and ADC1 pin", "Project 05", "compare calibrated ADC voltage with a DMM"),
    ("07-capacitor-and-time", "Capacitor and Time", "observe stored charge and RC settling", "lesson 06", "10 kohm resistor, 10 uF capacitor and DMM", "Project 05 extension", "record charge/discharge time without claiming an oscilloscope trace"),
    ("08-power-supply-and-decoupling", "Power Supply and Decoupling", "keep local IC supply voltage defined during switching", "lesson 07", "100 nF and 10 uF capacitors", "Projects 07-10", "place 100 nF at the device pins and identify the current loop"),
    ("09-uart", "UART", "frame asynchronous bytes into validated messages", "lesson 08", "GPIO17/GPIO16 loopback wire", "Project 06", "reject a bad magic, length or CRC"),
    ("10-i2c", "I2C", "address a register device on open-drain shared lines", "lesson 09", "TMP117 breakout", "Project 07", "show address, ACK/NACK, register pointer and data"),
    ("11-spi", "SPI", "control when synchronous bits move and which device answers", "lesson 10", "SN74HC595N and logic analyzer", "Project 08", "trace clock, data and latch/selection separately"),
    ("12-external-eeprom", "External EEPROM", "respect page and busy-state rules during nonvolatile writes", "lesson 11", "25LC256-I/P", "Project 09", "perform WREN, bounded write, WIP poll and readback"),
    ("13-spi-nor-flash", "SPI NOR Flash", "work with program pages and erase sectors", "lesson 12", "MX25L3233FM2I-08G on adapter", "Project 10", "identify, erase a reserved sector, program and verify"),
    ("14-crc-and-corruption", "CRC and Corruption", "detect changed bytes before accepting an object", "lesson 13", "Project 10 firmware and host test", "Project 10", "cause a controlled bit change in simulation and reject it"),
    ("15-power-loss-safe-write", "Power-Loss-Safe Write", "preserve last-known-good state across interruption", "lesson 14", "dual metadata sectors and commit states", "Project 10", "ignore a valid-CRC but uncommitted higher generation"),
    ("16-logic-analyzer", "Logic Analyzer", "turn protocol timing into reviewable evidence", "lesson 11", "documented 3.3 V logic analyzer", "Projects 06-10", "save real captures only, with probe map and sample settings"),
    ("17-oscilloscope", "Oscilloscope", "observe analog shape instead of inferred digital state", "lesson 16", "bandwidth-limited probe and scope", "future lab extension", "state probe grounding, bandwidth and uncertainty"),
    ("18-custom-pcb", "Custom PCB", "move a proven circuit from jumpers to controlled geometry", "lessons 08 and 16", "schematic, ERC, layout, DRC and test points", "Sovereign Cartridge carrier", "preserve every validated pin and safety constraint"),
    ("19-raw-nand", "Raw NAND", "manage bad blocks, spare area and ECC instead of treating NAND as NOR", "lessons 13-18", "existing W25N01JW lab platform", "projects/ssd_lab", "complete read-only bring-up before destructive authorization"),
    ("20-storage-controller", "Storage Controller", "coordinate mapping, integrity, recovery and media state", "lesson 19", "existing simulator, FTL and future FPGA", "projects/ssd_lab", "explain how evidence closes each controller invariant"),
]


PROJECT_STEPS = {
    "01-know-your-breadboard": [
        "With all power disconnected, set the DMM to continuity and touch the probes together to confirm the beeper.",
        "Test two holes in one five-hole terminal strip, then test across the centre channel; record both results.",
        "Test each red and blue rail at the top, centre and bottom. Mark every discontinuity on a paper rail map.",
        "Leave a discovered split open, confirm it, then bridge only matching rail segments and retest continuity.",
        "Connect ESP32 3V3 to the verified positive rail and GND to the verified return rail; connect USB last.",
        "Measure rail-to-ground voltage at both sides of the former split and record the breadboard model.",
    ],
    "02-led-current": [
        "Use resistance mode on the unpowered circuit to verify 220 ohm, 1 kohm and 10 kohm parts.",
        "Start with 1 kohm: 3V3 → resistor → LED anode; LED cathode → GND.",
        "Measure the actual rail, LED voltage and resistor voltage without changing to current mode.",
        "Calculate current from measured resistor voltage divided by measured resistance.",
        "Power down, repeat with 220 ohm, then 10 kohm, and compare calculated current with brightness.",
    ],
    "03-button-input": [
        "Map the two internally common button-pin pairs with continuity mode before placing it across the centre channel.",
        "Wire one side to GPIO27 and the opposite side to GND; do not add an external voltage source.",
        "Build and flash the official ESP-IDF project, then measure GPIO27 idle and pressed voltage.",
        "Record raw and debounced transition counts for ten deliberate presses.",
        "For the controlled failure, disable the configured pull-up, leave the pin unconnected and record the undefined behaviour before restoring it.",
        "Optional pull-down comparison: power off, disable internal pulls, add 10 kohm from GPIO27 to GND and move the button's far side to 3V3; measure low idle/high pressed, then restore the primary active-low circuit.",
    ],
    "04-mosfet-load-switch": [
        "Read the AO3400A pinout and verify the adapter labels with continuity; reject a mirrored or unlabelled adapter.",
        "Wire source to GND, gate to GPIO25 through 100 ohm, and gate to GND through 100 kohm.",
        "Wire 3V3 → 1 kohm → LED → drain; no motor, relay or external supply is used.",
        "Do not add a flyback diode to this resistive LED load. A flyback diode is required only when a later, separately rated inductive load is introduced.",
        "Flash the toggle firmware and measure VGS, drain voltage and resistor voltage in both states.",
    ],
    "05-analog-voltage": [
        "Identify potentiometer ends and wiper with resistance mode before connecting power.",
        "Wire the ends to 3V3/GND and the wiper to GPIO34/ADC1_CH6; keep Wi-Fi disabled.",
        "Set the wiper near 25%, 50% and 75%; at each point record DMM voltage, raw mean and calibrated millivolts.",
        "Calculate error as calibrated ADC voltage minus DMM voltage and state DMM resolution.",
        "Repeat one point using a single sample and 64-sample mean to expose noise without claiming accuracy.",
    ],
    "06-uart-conversation": [
        "Confirm the selected module is WROOM-32E, not a WROVER/PSRAM variant.",
        "With power off, jumper GPIO17 TX to GPIO16 RX and attach analyzer ground only if its input limits are known.",
        "Build, flash and monitor the independent UART1-TX/UART2-RX frame accept/reject log at 115200 baud.",
        "Change only RX_BAUD to 57600 for the controlled failure; restore 115200 after recording rejection.",
    ],
    "07-i2c-sensor": [
        "Inspect the TMP117 breakout product and open-hardware schematic; identify VIN, GND, SDA and SCL.",
        "Wire 3.3 V, GND, GPIO21 SDA and GPIO22 SCL. Do not add parallel pull-ups until the breakout pull-ups are accounted for.",
        "Measure both bus lines idle, then run address probe and read device-ID register 0x0F.",
        "Read raw temperature register 0x00 and record the decoded value as MEASURED only when real hardware ran.",
        "Power off, disconnect SDA, observe NACK after power-up, then power off and restore it before recovery.",
    ],
    "08-spi-shift-register": [
        "Place SN74HC595N across the breadboard centre channel with its notch and pin 1 identified.",
        "Wire pin 16 VCC and pin 10 SRCLR to 3V3; pin 8 GND and pin 13 OE# to GND; add 100 nF across pins 16/8.",
        "Wire SER pin 14 to GPIO23, SRCLK pin 11 to GPIO18 and RCLK pin 12 to GPIO32.",
        "Wire each Q output through its own 1 kohm resistor and LED to GND.",
        "Run the walking-bit firmware and compare visible order with captured data/clock/latch transitions.",
    ],
    "09-spi-eeprom": [
        "Place 25LC256-I/P across the centre channel; verify notch, pin 1 and the Microchip marking.",
        "Wire VCC, GND, SI, SO, SCK and CS exactly; tie WP#/HOLD# high and add 100 nF at pins 8/4.",
        "Add a 10 kohm CS# pull-up so the EEPROM remains deselected during reset.",
        "Keep WP# high for this lesson. The pin protects status-register writes only when WPEN is set; it is not a universal data-write lock.",
        "Run the bounded tests at 0x0100-0x0183; record WEL/WIP status, premature-read observation, page-cross rejection and CRC readback.",
        "Do not run an endurance loop. Use only the documented test addresses on a dedicated lab part.",
    ],
    "10-spi-nor-mini-storage": [
        "Solder or inspect the 200 mil SOP-8 adapter, then continuity-check every adapter pin to the IC lead.",
        "Wire VCC/GND, SI/SO/SCLK, GPIO32 CS#, WP#/HOLD# high, 10 kohm CS# pull-up and 100 nF decoupling.",
        "Run first with RUN_RESERVED_SECTOR_WRITE_DEMO=0; accept no write until JEDEC ID is exactly C2-20-16.",
        "For a dedicated blank lab part, change the gate to 1 and run once to create two committed generations.",
        "Confirm the higher prepared-but-uncommitted generation is rejected and recovery returns the prior committed generation.",
        "Restore the write gate to zero after the demonstration.",
    ],
}


MEASURE_NOTES = {
    "01-know-your-breadboard": "Continuity mode is used only without power. Record each tested hole pair, not only pass/fail.",
    "02-led-current": "Current mode is optional. Before using it, move the lead to the fused current jack, choose the highest safe range and insert the meter in series. Never place a current-mode meter across 3.3 V and GND.",
    "05-analog-voltage": "Use the same GND reference for the DMM and ADC. Do not infer accuracy from ADC resolution.",
    "06-uart-conversation": "A logic capture is MEASURED evidence only when sample rate, threshold, channels and probe ground are recorded.",
    "07-i2c-sensor": "If the breakout already contains pull-ups, record their values before adding any external pair.",
    "09-spi-eeprom": "Record WIP/WEL status bytes and the exact address range. Do not infer a write from MOSI alone.",
    "10-spi-nor-mini-storage": "Erase and program timing are UNKNOWN until captured. Record the exact JEDEC ID before enabling writes.",
}

PROJECT_SAFETY_CHECKS = {
    "01-know-your-breadboard": [
        "Continuity mode is selected only while every power source is disconnected",
        "Every rail segment and discovered split is marked before 3.3 V is applied",
    ],
    "02-led-current": [
        "LED polarity is identified and a measured resistor is in series",
        "Meter lead remains in the voltage/resistance jack unless a powered-down series-current setup is reviewed",
    ],
    "03-button-input": [
        "The two internally common button-pin pairs were mapped before placement",
        "Only one pull direction is enabled for the currently wired active-high or active-low experiment",
    ],
    "04-mosfet-load-switch": [
        "AO3400A adapter pin labels agree with the datasheet and continuity test",
        "Load is the bounded 3.3 V resistor/LED path; no motor, relay or external supply is connected",
        "100 kohm gate pull-down is present before firmware starts",
    ],
    "05-analog-voltage": [
        "Potentiometer wiper remains between the verified 3.3 V and GND endpoints",
        "GPIO34 is ADC1_CH6 on the selected module and no external voltage source is connected",
    ],
    "06-uart-conversation": [
        "Board module is ESP32-WROOM-32E, so GPIO16/17 are available",
        "Loopback is TX-to-RX with common GND and no external driven output attached",
    ],
    "07-i2c-sensor": [
        "Breakout identity and schematic match TMP117 product 4821",
        "Existing breakout pull-ups are accounted for before adding any external pull-up",
    ],
    "08-spi-shift-register": [
        "SN74HC595N pin 1, OE#, SRCLR, VCC and GND are verified",
        "Every LED output has its own 1 kohm current-limiting resistor",
    ],
    "09-spi-eeprom": [
        "Device marking is 25LC256-I/P, not the I2C 24LC256",
        "CS# has a 10 kohm pull-up; WP# and HOLD# are tied high",
        "Only dedicated test addresses 0x0100 through 0x0183 will be written",
    ],
    "10-spi-nor-mini-storage": [
        "Adapter pin map and exact MX25L3233FM2I-08G marking are inspected",
        "CS# has a 10 kohm pull-up; WP# and HOLD# are tied high",
        "Write gate remains zero until JEDEC ID C2-20-16 and a dedicated blank lab part are confirmed",
    ],
}

EXPECTED_SERIAL = {
    "button": "`raw=<0|1>` and `debounced=<0|1>` transitions; counts and timing are MEASURED.",
    "mosfet": "`gate_command=ON|OFF` with `measure=required`; the log is not accepted as a voltage measurement.",
    "adc": "`adc_raw_mean=... calibrated_mv=... calibrated=<0|1> dmm_mv=RECORD`.",
    "uart": "`uart_rx=7 frame=ACCEPT seq=...` for correct loopback and `frame=REJECT` for the baud mismatch.",
    "i2c": "an address scan ACK at the wired address, TMP117 ID `0x0117`, and an explicit NACK path.",
    "shift": "`shifted=0x.. visible=0x.. lsb_first=...` while one output advances.",
    "eeprom": "WEL/WIP status, no-WREN rejection, page-cross rejection, premature-read observation and matching CRCs.",
    "nor": "JEDEC ID `c2-20-16`, explicit write-gate state, both slot-valid flags and recovered generation.",
}

EXPECTED_CURRENT = {
    "01-know-your-breadboard": "No project current is predicted; only rail voltage and continuity are accepted.",
    "02-led-current": "Calculate `I = V_resistor / R_measured` for each resistor. No numeric current is accepted until LED and resistor voltages are measured.",
    "04-mosfet-load-switch": "Calculate bounded load current from the measured 1 kohm resistor voltage. The design intent is approximately 10 mA or less, not a measured claim.",
}

WHY_EXTRAS = {
    "09-spi-eeprom": """
## Write protection boundary

`WREN` controls the write-enable latch. `WP#` protects status-register writes only when the status
register's WPEN bit enables that behavior; tying WP# high does not replace bounds checks, page checks,
busy polling or readback. The v1 demo does not enable block-protection bits.
""",
    "10-spi-nor-mini-storage": """
## Immutable v1 object

The packed on-media header is little-endian for this ESP32-only v1 demonstration:

| Field | Width | Rule |
| --- | ---: | --- |
| magic | 32 bits | `0x455A4631` identifies this teaching record |
| schema version | 16 bits | exactly `1` |
| generation | 32 bits | monotonically selects the newest valid copy |
| payload length | 16 bits | at most 128 bytes in v1 |
| payload CRC32 | 32 bits | CRC-32 over exactly `payload length` bytes |
| header CRC32 | 32 bits | CRC-32 over fields from magic through payload CRC |
| commit state | 8 bits | `0x7F` prepared, then one-way programmed to `0x3F` committed |

Header and payload are verified before the commit byte changes. After commit, that record is immutable:
the next update erases and writes the other 4 KiB sector. Recovery accepts only committed copies whose
header and payload CRCs pass, then chooses the greater generation. A prepared higher generation is ignored.
This is a record demonstration, not a filesystem or a portable interchange format.
""",
}


def write(path: str | Path, content: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    raw = content.strip("\n")
    first = next((line for line in raw.splitlines() if line.strip()), "")
    margin = len(first) - len(first.lstrip(" "))
    prefix = " " * margin
    normalized = "\n".join(
        (line[margin:] if margin and line.startswith(prefix) else line).rstrip()
        for line in raw.splitlines()
    )
    target.write_text(normalized.strip() + "\n", encoding="utf-8")


def write_csv(path: str | Path, fieldnames: list[str], rows: list[dict]) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def source_list(keys: list[str]) -> str:
    return "\n".join(
        f"- {SOURCES[key][0]}, [{SOURCES[key][1]}]({SOURCES[key][2]}) "
        f"(retrieved {RETRIEVED})."
        for key in keys
    )


def project_path(project: dict) -> Path:
    return Path("projects") / project["group"] / project["id"]


def project_bom(project: dict) -> list[dict]:
    rows = []
    optional_parts = {"logic_analyzer", "usb_uart", "level_shifter", "flash_programmer"}
    quantity_overrides = {
        ("08-spi-shift-register", "led"): 8,
    }
    for index, key in enumerate(project["parts"], start=1):
        part = PARTS[key]
        rows.append(
            {
                "item_id": f"P{index:02d}",
                "category": part["category"],
                "description": part["description"],
                "manufacturer": part["manufacturer"],
                "manufacturer_part_number": part["mpn"],
                "package": part["package"],
                "quantity": quantity_overrides.get((project.get("id"), key), 1),
                "required_or_optional": "optional" if key in optional_parts else "required",
                "verified_or_suggested": part.get(
                    "status", "verified" if part["notes"].startswith("VERIFIED") else "suggested"
                ),
                "supply_voltage": part["voltage"],
                "india_search_name": part["search"],
                "substitution_rule": part["sub"],
                "source_url": part["url"],
                "retrieved_at": RETRIEVED,
                "notes": part["notes"],
            }
        )
    return rows


def svg_asset(project: dict, kind: str) -> str:
    rows = []
    y = 145
    for source, destination, colour, test_point in project["pins"]:
        rows.append(
            f'<line x1="280" y1="{y}" x2="650" y2="{y}" '
            f'stroke="{html.escape(colour if colour != "white" else "#777")}" '
            f'stroke-width="5" marker-end="url(#arrow)" />'
        )
        rows.append(
            f'<text x="35" y="{y + 6}" class="label">{html.escape(source)}</text>'
        )
        rows.append(
            f'<text x="675" y="{y + 6}" class="label">{html.escape(destination)}</text>'
        )
        rows.append(
            f'<text x="455" y="{y - 10}" class="tp">{html.escape(test_point)}</text>'
        )
        y += 62
    title = "Breadboard connection map" if kind == "breadboard" else "Electrical net schematic"
    description = (
        "Connection map; physical hole positions vary by breadboard. Verify every rail."
        if kind == "breadboard"
        else "Net-level schematic generated from pinmap.yaml. It is not a measured artifact."
    )
    box_height = max(330, y - 120)
    annotation_y = max(500, y + 10)
    decoupling_required = project["id"] in {
        "07-i2c-sensor", "08-spi-shift-register", "09-spi-eeprom",
        "10-spi-nor-mini-storage",
    }
    decoupling_text = (
        "C1 100 nF: place directly across target VCC-GND pins"
        if decoupling_required
        else "No external IC bypass capacitor in this primary circuit"
    )
    if kind == "breadboard":
        annotation = f"""
          <text x="35" y="{annotation_y}" class="section">Conceptual rail map — verify the real breadboard with continuity</text>
          <text x="35" y="{annotation_y + 38}" class="label">3V3 rail →</text>
          <line x1="145" y1="{annotation_y + 32}" x2="545" y2="{annotation_y + 32}" stroke="#dc2626" stroke-width="8" marker-end="url(#arrow)"/>
          <line x1="335" y1="{annotation_y + 20}" x2="350" y2="{annotation_y + 44}" stroke="#ffffff" stroke-width="12"/>
          <text x="270" y="{annotation_y + 64}" class="warn">possible split — bridge only after continuity test</text>
          <text x="35" y="{annotation_y + 102}" class="label">GND rail →</text>
          <line x1="145" y1="{annotation_y + 96}" x2="545" y2="{annotation_y + 96}" stroke="#111827" stroke-width="8" marker-end="url(#arrow)"/>
          <line x1="335" y1="{annotation_y + 84}" x2="350" y2="{annotation_y + 108}" stroke="#ffffff" stroke-width="12"/>
          <rect x="690" y="{annotation_y + 12}" width="255" height="100" rx="10" class="box"/>
          <path d="M790 {annotation_y + 12} a28 20 0 0 0 56 0" fill="none" stroke="#0f172a" stroke-width="2"/>
          <circle cx="710" cy="{annotation_y + 92}" r="7" fill="#b45309"/>
          <text x="720" y="{annotation_y + 96}" class="tp">pin 1 / polarity mark</text>
          <text x="965" y="{annotation_y + 42}" class="label">orientation: notch/dot</text>
          <text x="965" y="{annotation_y + 67}" class="label">must match datasheet</text>
          <text x="690" y="{annotation_y + 145}" class="label">{html.escape(decoupling_text)}</text>
        """
    else:
        annotation = f"""
          <text x="35" y="{annotation_y}" class="section">Schematic rules carried into the physical build</text>
          <text x="35" y="{annotation_y + 38}" class="label">→ arrow: named source to named destination; it does not imply current direction</text>
          <text x="35" y="{annotation_y + 70}" class="label">3V3 and GND are explicit nets; every signal is referenced to the shared return</text>
          <text x="35" y="{annotation_y + 102}" class="label">{html.escape(decoupling_text)}</text>
          <text x="35" y="{annotation_y + 134}" class="label">TP labels must match pinmap.yaml; verify package notch/dot before numbering pins</text>
        """
    footer_y = annotation_y + 190
    return f"""\
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 {footer_y + 45}"
         role="img" aria-labelledby="title desc">
      <title id="title">{html.escape(project['title'])}: {title}</title>
      <desc id="desc">{html.escape(description)}</desc>
      <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="context-stroke"/>
        </marker>
      </defs>
      <style>
        .title {{ font: 700 28px system-ui; fill: #0a1220; }}
        .sub {{ font: 16px system-ui; fill: #334155; }}
        .section {{ font: 700 18px system-ui; fill: #0f172a; }}
        .label {{ font: 14px ui-monospace, monospace; fill: #0f172a; }}
        .tp {{ font: 700 13px ui-monospace, monospace; fill: #b45309; }}
        .warn {{ font: 13px system-ui; fill: #b45309; }}
        .box {{ fill: #f8fafc; stroke: #0f172a; stroke-width: 2; }}
      </style>
      <rect width="100%" height="100%" fill="#ffffff"/>
      <text x="35" y="45" class="title">{html.escape(project['title'])}</text>
      <text x="35" y="75" class="sub">{title}. 3.3 V only. Power off before rewiring.</text>
      <rect x="25" y="105" width="250" height="{box_height}" rx="12" class="box"/>
      <rect x="665" y="105" width="595" height="{box_height}" rx="12" class="box"/>
      {''.join(rows)}
      {annotation}
      <text x="35" y="{footer_y}" class="sub">Wire colour is a convention, never evidence. Confirm nodes with continuity and voltage measurements.</text>
    </svg>
    """


def make_research() -> None:
    write(
        "docs/research/electronics-from-zero-repository-audit.md",
        f"""
        # Electronics From Zero Repository Audit

        Audit date: {RETRIEVED}
        Baseline: `main` at `35ec1a63c818eb75c5a2dce1a7b452db046e35a9`

        The live GitHub repository was inspected. No electronics ZIP or BCA learning ZIP was attached to
        this execution, so neither is represented as reviewed evidence.

        ## Repository map

        | Area | Existing evidence | Reuse decision |
        | --- | --- | --- |
        | ESP32 | ESP-IDF peripheral dossiers, examples, firmware and validation matrix | Preserve; link after the breadboard ladder |
        | Storage firmware | NAND HAL, bad-block handling, FTL journal/checkpoint/recovery | Preserve as the controller destination |
        | SSD simulator | deterministic NAND, ECC, faults, power loss and property tests | Preserve; use for safe fault injection |
        | Hardware | W25N01JW 1.8 V fixture schema, power tree and validation gates | Preserve; prohibit beginner wiring until prerequisites |
        | Evidence | evidence schema, hashing and report tools | Reuse the fact/expected/measured separation |
        | Learning | broad Beginner/Intermediate/Advanced indexes | Link from the new action-first track |

        ## Baseline validation

        - `tools/check_repository.py --strict`: PASS.
        - W25N01JW platform validation: PASS.
        - evidence validation: PASS with `real_pass_count=0`.
        - engineering-document validation: PASS.
        - full `tools/verify.sh`: BLOCKED before compilation because `cmake` is not installed in the Work Mode runtime.
        - simulator tests: BLOCKED because the pinned Python dependencies, including `pytest`, are not installed.
        - no physical hardware evidence was available. No build or measurement is represented as completed.

        ## Missing prerequisites

        - No human-facing start page.
        - No measured breadboard progression before peripheral architecture.
        - No repeated physical project contract with safety, failure and evidence files.
        - No shared beginner purchasing system.
        - No beginner SPI EEPROM or NOR implementation connecting buses to storage semantics.

        ## Duplicate or weak areas

        The peripheral dossiers intentionally repeat a six-file production structure. They are not deleted.
        Existing `learning/Beginner.md` is a broad index rather than a physical ladder. The new track links to
        it instead of replacing it. Several example folders are documentation-only; the audit does not claim
        that every example builds.

        ## Unsupported or unresolved claims

        - Physical current, ADC error, timing, signal integrity and power-up success remain UNKNOWN.
        - The W25N01JW fixture is `DESIGN_RULES_PASSED`, not bench verified.
        - Breadboard internal topology varies by product and must be measured per unit.
        - Marketplace module labels are insufficient evidence for electrical compatibility.

        ## Reuse plan

        The new learner path ends at existing `projects/ssd_lab`, `simulator/ssd`, `firmware/storage`,
        `hardware/platforms/w25n01jw_lab`, and ESP32 peripheral references. Advanced material remains
        intact. New implementation is additive, apart from navigation and validation integration.

        ## Exit condition

        Repository map and reuse plan: SATISFIED. Architecture changes may proceed after this audit.
        """,
    )
    write(
        "docs/research/electronics-from-zero-source-ledger.md",
        f"""
        # Electronics From Zero Source Ledger

        Retrieval date: {RETRIEVED}

        Primary sources were used for electrical limits, protocols and SDK behaviour. Distributor or
        open-hardware pages are used only to verify package, breakout topology or availability.

        | Authority | Source | Decision supported |
        | --- | --- | --- |
        {chr(10).join(f"| {vendor} | [{title}]({url}) | {key.replace('_', ' ')} |" for key, (vendor, title, url) in SOURCES.items())}

        ## Claim rules

        - **FACT**: traceable to a source above or repository code.
        - **EXPECTED**: calculated or predicted for a stated circuit and tolerance.
        - **MEASURED**: recorded from real hardware with instrument and evidence metadata.
        - **UNKNOWN**: not yet verified.

        Search results and marketplace descriptions are discovery aids only. No current price or stock
        claim is frozen into v1.
        """,
    )
    component_rows = []
    for key, part in PARTS.items():
        component_rows.append(
            f"| {key} | {part['manufacturer']} | {part['mpn']} | {part['package']} | "
            f"{part['voltage']} | {part['url'] or 'learner-selected; verify datasheet'} | "
            f"{part['notes']} | no |"
        )
    write(
        "docs/research/component-selection-ledger.md",
        f"""
        # Component Selection Ledger

        Retrieval date: {RETRIEVED}
        Physical test status for all v1 components: **not tested in this repository change**.

        | Key | Manufacturer | Exact part/reference | Form | Supply/logic boundary | Primary source | Status | Physically tested |
        | --- | --- | --- | --- | --- | --- | --- | --- |
        {chr(10).join(component_rows)}

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
        """,
    )
    write(
        "docs/research/curriculum-dependency-graph.md",
        """
        # Curriculum Dependency Graph

        ```mermaid
        flowchart TD
          A[Electricity] --> B[Breadboard]
          B --> C[Measurement]
          C --> D[GPIO and switching]
          D --> E[Analog measurement]
          E --> F[UART]
          F --> G[I2C]
          G --> H[SPI]
          H --> I[EEPROM]
          I --> J[NOR flash]
          J --> K[Integrity]
          K --> L[Crash safety]
          L --> M[Raw NAND]
          M --> N[ECC and mapping]
          N --> O[Storage controller]
        ```

        No NAND, PCIe or controller RTL entry path bypasses power, measurement, synchronous buses,
        integrity and recovery. The first ten projects stop at crash-safe NOR; the existing SSD lab
        continues through NAND, ECC, FTL and controller behaviour.
        """,
    )
    write(
        "docs/research/safety-boundary.md",
        """
        # Electronics From Zero Safety Boundary

        ## Allowed v1 energy boundary

        - USB-powered ESP32 development board and a single 3.3 V project rail.
        - Safe extra-low-voltage, current-bounded resistive or LED loads.
        - Power removed before wiring, continuity or resistance measurements.
        - Current mode is optional and used only after a separate fuse/jack/range check.

        ## Prohibited

        Mains electricity, lithium-cell experiments, high-current short circuits, deliberate overheating,
        reverse powering, operation beyond absolute maximum ratings, exposed inductive loads without
        protection, unknown external supplies, and destructive NAND access outside an authorized scratch
        range.

        ## Power-up gate

        Supply measured; GND continuity confirmed; no VCC-GND short; common ground present; logic levels
        compatible; polarity and orientation checked; current bounded; decoupling installed; test points
        identified. A failed check blocks power-up.

        ## Measurement boundary

        Put the black lead on project GND before probing with the red lead. Use insulated probe tips where
        possible. Never change the meter into current mode while it remains connected across a voltage
        source. Wire colour is not proof of a node.
        """,
    )
    write(
        "docs/research/board-selection-decision.md",
        f"""
        # Primary Board Selection Decision

        ## Decision

        Select **{BOARD}** and **{SDK}** for v1.

        ## Comparison

        | Criterion | ESP32-DevKitC V4 | RP2040 board |
        | --- | --- | --- |
        | Existing repository implementation | extensive ESP-IDF code and dossiers | roadmap page only |
        | Indian availability | exact Espressif reference can be searched by MPN through authorized Indian storefronts | boards are available, but adopting one would not reuse current firmware |
        | 3.3 V buses | yes | yes |
        | Official documentation | board, SoC, module and SDK manuals | strong, but not reused by current code |
        | Firmware reproducibility | pinned ESP-IDF target can extend existing examples | second toolchain would duplicate v1 |
        | ADC | calibration and nonlinearity must be taught explicitly | different limitations; future port |
        | Debug entry | USB-UART, boot/reset, optional JTAG | SWD; separate setup |
        | Storage progression | existing ESP32 SPI and storage work | future cartridge/controller port |
        | Deterministic bus control | official low-level ESP-IDF drivers and existing repository patterns | capable PIO/SPI path, but no current repository implementation to preserve |

        ## Exact variant and installation

        Board ordering reference: `ESP32-DEVKITC-32E`, module `ESP32-WROOM-32E`. Install the official
        ESP-IDF v5.2.3 toolchain and run `idf.py set-target esp32`. Use the board's Micro-USB port for power,
        flashing and console.

        ## Frozen pin policy

        GPIO27 button; GPIO25 switch; GPIO34 ADC1_CH6; UART1 TX GPIO17 to UART2 RX GPIO16; I2C GPIO21/22; SPI MOSI23,
        MISO19, SCLK18 and per-project latch/CS GPIO32. GPIO6-11 are prohibited because they serve module
        flash. Reset strapping pins are not used for learner-controlled bus signals.

        ## Limitations

        - ESP32 GPIO is 3.3 V logic and is not 5 V tolerant.
        - ADC voltage accuracy is not assumed; ADC1, averaging and calibration evidence are required.
        - GPIO16/17 loopback is approved only for the selected WROOM-32E variant, not WROVER/PSRAM boards.
        - Many marketplace “ESP32 DevKit V1” products are not the selected Espressif board.
        - A wide board may consume breadboard columns; two breadboards or header jumpers are acceptable.

        ## RP2040 path

        RP2040 learners complete the no-firmware Projects 01-02, then follow the same electrical and evidence
        contract. Firmware ports are future work; do not translate pin numbers or SDK APIs by assumption.

        {source_list(["devkit", "module", "soc", "gpio", "adc"])}
        """,
    )


def make_start() -> None:
    write(
        "START-HERE.md",
        f"""
        # You have an ESP32 or RP2040, a breadboard and some wires. Start here.

        Pick the first statement that matches you. You do not need to understand the repository structure.

        ## I have these parts

        | You have | Start |
        | --- | --- |
        | Breadboard + multimeter, no MCU confidence | Path A |
        | Arduino-level wiring experience | Path B |
        | SPI memory or a logic analyzer | Path C |
        | Cartridge goal and ESP32/RP2040 experience | Path D |
        | FPGA goal | Path E, but complete its prerequisites |

        ## Path A — I have never used a breadboard

        **Need:** breadboard, jumper wires, DMM, USB cable and the selected 3.3 V board. Buy Kit 00 once.
        **Install:** nothing for the first project. **Build first:** [Know Your Breadboard](projects/breadboard/01-know-your-breadboard/PROJECT.md).
        **Success:** you can prove which holes connect, find a split rail and measure 3.3 V.
        **Common mistake:** trusting coloured rail markings. **Next:** LED Current.
        **Effort:** 60 minutes. **Safety:** power off for continuity; 3.3 V only; do not connect
        batteries, mains, motors or loose memory ICs yet. **Tools:** DMM and insulated jumper wires.

        ## Path B — I know Arduino-level electronics

        This repository replaces copy-paste success with measured evidence. Review Projects 01-03 quickly,
        then begin [Analog Voltage](projects/breadboard/05-analog-voltage/PROJECT.md) or
        [UART](projects/buses/06-uart-conversation/PROJECT.md). GPIO assumptions become blocking voltage,
        current, boot-pin and evidence constraints.

        **Need:** Kits 00-01. **Install:** {SDK}. **Build first:** Project 05 for analog or Project 06
        for buses. **Success:** firmware output agrees with a physical measurement.
        **Common mistake:** treating serial output as proof of electrical correctness. **Next:** UART →
        I2C → SPI. **Effort:** 4-8 hours for the review path. **Safety:** complete every power-up gate.
        **Tools:** DMM, serial terminal and logic analyzer when bus timing is the question.

        ## Path C — I want to understand storage hardware

        Follow: shift register → SPI EEPROM → SPI NOR → page program → erase → CRC → interrupted write →
        metadata → raw NAND → ECC → logical-to-physical mapping. Storage is not simply “saving bytes.”

        **Need:** Kits 00-02. **Install:** {SDK} and a serial terminal. **Build first:**
        [SPI Shift Register](projects/buses/08-spi-shift-register/PROJECT.md). **Success:** you can explain
        each bus phase and reject corrupt or uncommitted data. **Next:** existing SSD lab.
        **Common mistake:** treating a successful read as proof that write, erase and recovery are safe.
        **Effort:** 10-20 hours. **Safety:** only erase reserved addresses on dedicated lab memories.
        **Tools:** DMM, serial terminal and a documented 3.3 V logic analyzer.

        ## Path D — I want to build the Sovereign Cartridge

        First prove 3.3 V power, decoupling, SPI identification, page program, erase, CRC, immutable records,
        power-loss recovery, connector pin ownership and test points. Complete Project 10, then continue to
        [`hardware/platforms/w25n01jw_lab`](hardware/platforms/w25n01jw_lab/README.md) and the cartridge
        work. A custom PCB comes after breadboard evidence.

        **Need:** Kits 00-03. **Install:** {SDK} and the repository's existing validation dependencies.
        **Build first:** Project 10 only after Projects 08-09.
        **Success:** last-known-good recovery survives an intentionally uncommitted record.
        **Common mistake:** jumping from JEDEC ID to a product protocol. **Next:** the W25N01JW lab
        platform, then carrier design. **Effort:** multi-day. **Safety:** do not connect a 1.8 V NAND
        directly to 3.3 V or buy a connector before its power-pin contract freezes. **Tools:** DMM,
        current-limited supply, logic analyzer and test clips.

        ## Path E — I want to reach FPGA and controller design

        Required sequence: digital logic → synchronous state machines → timing → SPI → buffering → CRC →
        ECC → NAND → DMA → simulation → hardware verification → FPGA. PCIe and NAND controller RTL are
        not beginner entry points.

        **Need:** Kits 00-02 now; FPGA hardware later. **Install:** ESP-IDF, then simulation tools when the
        storage-controller track asks. **Build first:** Project 08. **Success:** software and captured timing
        agree on every state transition. **Common mistake:** beginning PCIe or NAND-controller RTL before
        bus timing, integrity and recovery are evidenced. **Next:** [`projects/ssd_lab`](projects/ssd_lab/README.md).
        **Effort:** several weeks across the full ladder. **Safety:** simulation does not waive the hardware
        power-up gates. **Tools:** DMM and logic analyzer first; simulator and FPGA toolchain only when the
        linked track requires them.

        ## Shared purchasing

        Start with [`hardware/kits/README.md`](hardware/kits/README.md). Do not buy a full kit per project.
        Exact substitutions require datasheet checks, not matching product titles.

        ## The rule used everywhere

        FACT → EXPECTED → MEASURED → UNKNOWN. If no hardware was tested, the repository gives a procedure
        and blank evidence table instead of inventing a successful result.
        """,
    )


def make_learning() -> None:
    index_rows = []
    for number, lesson in enumerate(LESSONS):
        slug, title, problem, prereq, components, project, success = lesson
        next_lesson = (
            f"[{LESSONS[number + 1][1]}]({LESSONS[number + 1][0]}.md)"
            if number + 1 < len(LESSONS)
            else "[Existing SSD lab](../../projects/ssd_lab/README.md)"
        )
        refs = ["devkit", "soc"]
        if "ADC" in title:
            refs.append("adc")
        if title == "UART":
            refs.append("uart")
        if title == "I2C":
            refs.extend(["i2c", "i2c_spec", "tmp117"])
        if title == "SPI":
            refs.extend(["spi", "hc595"])
        if "EEPROM" in title:
            refs.extend(["spi", "eeprom"])
        if "NOR" in title or "Power-Loss" in title:
            refs.extend(["spi", "nor"])
        linked = next((p for p in PROJECTS if project.lower().replace("project ", "").split()[0].zfill(2) in p["id"][:2]), None)
        linked_path = (
            f"../../{project_path(linked)}/PROJECT.md" if linked else "../../projects/ssd_lab/README.md"
        )
        write(
            Path("learning-tracks/electronics-from-zero") / f"{slug}.md",
            f"""
            # {title}

            ## 1. Physical problem this lesson solves

            This lesson solves how to **{problem}**.

            ## 2. What you need to know first

            {prereq}.

            ## 3. Components required

            {components}. Power policy: 3.3 V only; power off before rewiring.

            ## 4. What you will build

            The physical circuit in [{project}]({linked_path}).

            ## 5. What you will measure

            Use the project measurement plan. Identify supply, ground, orientation, decoupling and test
            points before power. Measure the named physical quantity before accepting firmware output.

            ## 6. Minimum theory

            Voltage is a difference between nodes; current needs a closed path; logic thresholds are ranges,
            not perfect numbers. Protocols add timing and state rules to those electrical facts. Storage adds
            geometry, integrity and recovery rules to protocols.

            ## 7. Physical explanation

            Trace the path with a finger while power is off: source → controlled element → return. Then trace
            the information path separately. If the two paths are not clear, do not power the circuit.

            ## 8. Common misconceptions

            - Wire colour proves nothing.
            - A successful build does not validate an absolute rating.
            - A package name does not prove a pinout.
            - A firmware log does not prove supply integrity.

            ## 9. Common wiring mistakes

            - Mirrored IC orientation, split rails and missing common ground are checked first.

            ## 10. Linked project

            [{project}]({linked_path})

            ## 11. Success condition

            {success}. Save evidence using the linked project template.

            ## 12. Next lesson

            {next_lesson}

            ## 13. Primary references

            {source_list(list(dict.fromkeys(refs)))}

            ## 14. Facts, expected results and required measurements

            - **FACT:** only values linked to a primary source.
            - **EXPECTED:** calculate for the exact circuit and state assumptions.
            - **MEASURED:** enter only instrument output from real hardware.
            - **UNKNOWN:** leave unknown until evidence exists.
            """,
        )
        index_rows.append(f"{number}. [{title}]({slug}.md) — {problem}.")
    write(
        "learning-tracks/electronics-from-zero/README.md",
        "# Electronics From Zero\n\n"
        "Begin at `START-HERE.md`. Complete lessons in order unless an entry path explicitly permits a review.\n\n"
        + "\n".join(index_rows)
        + "\n\nAdvanced destinations: [`projects/ssd_lab`](../../projects/ssd_lab/README.md), "
        "[`firmware/storage`](../../firmware/storage/) and "
        "[`hardware/platforms/w25n01jw_lab`](../../hardware/platforms/w25n01jw_lab/README.md).\n",
    )


TEMPLATE_FILES = {
    "PROJECT.md": "# {{TITLE}}\n\nBuild: {{BUILD}}\n\nVisible or measurable result: {{MEASURE}}.\n\nWhy useful: {{WHY}}.\n\nTime: {{MINUTES}} minutes.\n\nRequired knowledge: {{PREREQUISITES}}.\n\nSuccess: {{SUCCESS}}\n",
    "WHY.md": "# Why\n\nState the engineering lesson, not only the visible object.\n",
    "BUY.md": "# Buy\n\nUse shared kits. List required and optional rows with exact MPN, package, voltage, India search term, substitution/prohibition, source, retrieval date and VERIFIED/SUGGESTED status.\n",
    "WIRING.md": "# Wiring\n\nProvide exact pins, physical orientation, mapped rails, wire-colour convention, decoupling, power/ground paths, idle voltages, test points, mirrored/common errors and linked breadboard/schematic SVGs.\n",
    "BUILD.md": "# Build\n\n1. Power off.\n2. Verify each step independently.\n3. Pass the power-up gate.\n4. Measure before accepting output.\n",
    "CODE/README.md": "# Code\n\nPin the official SDK and document build, flash, monitor and failure modes.\n",
    "EXPECTED.md": "# Expected\n\nSeparate FACT, EXPECTED, MEASURED and UNKNOWN. State serial/output pattern, voltage and defensible current ranges, logic levels, transitions, failure output, assumptions and tolerances.\n",
    "BEFORE-YOU-POWER.md": "# Before You Power\n\n- [ ] Supply voltage measured\n- [ ] GND continuity confirmed\n- [ ] No VCC-to-GND short\n- [ ] MCU and peripheral share ground\n- [ ] Logic voltage compatible\n- [ ] Polarized parts oriented correctly\n- [ ] Current limit configured\n- [ ] Correct chip orientation\n- [ ] Decoupling capacitor installed\n- [ ] Test points identified\n- [ ] Project-specific blocking checks added\n",
    "BREAK-IT.md": "# Break It Safely\n\nUse only reversible, within-rating failures.\n",
    "DEBUG.md": "# Debug\n\nPower → ground → orientation → continuity → idle voltage → clock → data → protocol → firmware → output.\n",
    "MEASURE.md": "# Measure\n\nSpecify instrument, range, points, expected range, uncertainty and evidence filename.\n",
    "WHAT-YOU-LEARNED.md": "# What You Learned\n\nClose the physical and engineering learning outcomes.\n",
    "NEXT.md": "# Next\n\nLink the next physical project.\n",
    "project.yaml": "schemaVersion: 1\nprojectId: template\ntitle: \"{{TITLE}}\"\ndifficulty: beginner\nestimatedMinutes: 0\nprimaryBoard: \"{{BOARD}}\"\nsupplyVoltage: 3.3 V\nrequiredTools: []\nrequiredKits: []\ninterfaces: []\nprerequisites: []\nlearningOutcomes: []\nblockingSafetyChecks: [supply, ground, short, logic-level, orientation, decoupling]\nsourceReferences: []\nhardwareValidationStatus: HARDWARE_VALIDATION_REQUIRED\n",
    "bom.csv": "item_id,category,description,manufacturer,manufacturer_part_number,package,quantity,required_or_optional,verified_or_suggested,supply_voltage,india_search_name,substitution_rule,source_url,retrieved_at,notes\n",
    "pinmap.yaml": "schemaVersion: 1\nnets: []\n",
    "constraints.yaml": "schemaVersion: 1\nconstraints: []\n",
    "decisions/README.md": "# Decisions\n\nRecord alternatives, evidence, choice and consequences.\n",
    "validation/checklist.md": "# Validation Checklist\n\n- [ ] Structure complete\n- [ ] Hardware evidence status explicit\n",
    "validation/expected-results.json": '{"schemaVersion":1,"results":[]}\n',
    "evidence/README.md": "# Evidence\n\nNever place fabricated evidence here.\n",
    "evidence/measurement-template.csv": "timestamp_utc,instrument,range,test_point,state,expected,measured,unit,uncertainty,operator,notes\n",
}


def make_template() -> None:
    for name, content in TEMPLATE_FILES.items():
        write(Path("templates/physical-project") / name, content)


def make_kits() -> None:
    write(
        "hardware/kits/README.md",
        """
        # Shared Electronics Kits

        Buy shared tools and passives once. Project BOMs reference these kits and list only additional parts.

        | Kit | Projects | Boundary |
        | --- | --- | --- |
        | 00 Basic Electronics | 01-05 | breadboard, measurement, GPIO, ADC |
        | 01 Digital Buses | 06-08 | UART, I2C, SPI and capture |
        | 02 Storage Lab | 09-10 and later NAND | EEPROM, NOR, logic capture |
        | 03 Cartridge Prototype | after Project 10 | carrier, connector, protection and fixtures |

        Search authorized Indian distributor sites by exact manufacturer part number. Current price and stock
        are intentionally not recorded as permanent facts.
        """,
    )
    fields = [
        "item_id", "category", "description", "manufacturer", "manufacturer_part_number",
        "package", "quantity", "required_or_optional", "verified_or_suggested", "supply_voltage",
        "india_search_name", "substitution_rule", "source_url", "retrieved_at", "notes",
    ]
    kit_map = {
        "kit-00-basic-electronics.csv": [
            "board", "breadboard", "dmm", "jumper", "led", "resistors", "caps", "button",
            "pot", "bjt", "mosfet", "buzzer", "usb_cable"
        ],
        "kit-01-digital-buses.csv": [
            "jumper", "usb_uart", "tmp117", "level_shifter", "hc595", "resistors", "caps",
            "logic_analyzer", "test_clips"
        ],
        "kit-02-storage-lab.csv": [
            "eeprom", "nor", "nand_fixture", "caps", "resistors", "logic_analyzer",
            "usb_meter", "test_clips", "breadboard", "flash_programmer"
        ],
        "kit-03-cartridge-prototype.csv": [
            "carrier", "nor", "connector", "protection", "caps", "debug_header",
            "logic_analyzer", "test_fixture"
        ],
    }
    for filename, keys in kit_map.items():
        dummy = {"parts": keys}
        write_csv(Path("hardware/kits") / filename, fields, project_bom(dummy))
    write(
        "hardware/kits/substitutions.md",
        """
        # Substitutions

        **VERIFIED** means authoritative documentation confirms supply, thresholds, package, pinout and the
        project requirement. **SUGGESTED** means plausible but not yet verified for the learner's exact item.

        A safe equivalent matches voltage range, input thresholds, pin function, package orientation, timing,
        current and protocol geometry. A matching product title is not enough. Reject 5 V-only logic, 1.8 V
        memories without a validated translator, mismatched DIP/SOP packages, MOSFETs lacking RDS(on) data
        at 2.5-3.3 V gate drive, and untraceable flash.

        Clone boards may change regulator, USB bridge, pin count and labels. Compare the received board to
        the official schematic before power. Record any seller, currency, stock date, tax and shipping only in
        a time-stamped purchasing record, never as a permanent repository price.
        """,
    )


def firmware_sources() -> dict[str, str]:
    common = '#include <stdbool.h>\n#include <stdio.h>\n#include "freertos/FreeRTOS.h"\n#include "freertos/task.h"\n'
    return {
        "button": common + r'''
#include "driver/gpio.h"
#define BUTTON GPIO_NUM_27
void app_main(void) {
    gpio_config_t c = {.pin_bit_mask=1ULL<<BUTTON,.mode=GPIO_MODE_INPUT,
        .pull_up_en=GPIO_PULLUP_ENABLE,.pull_down_en=GPIO_PULLDOWN_DISABLE,.intr_type=GPIO_INTR_DISABLE};
    gpio_config(&c);
    int raw=gpio_get_level(BUTTON), stable=raw, candidate=raw, count=0;
    printf("button raw=%d stable=%d active_low=1\n", raw, stable);
    while (1) {
        raw=gpio_get_level(BUTTON);
        if (raw != candidate) { candidate=raw; count=1; printf("raw=%d\n",raw); }
        else if (count && ++count >= 3) {
            count=0;
            if (stable != candidate) { stable=candidate; printf("debounced=%d\n",stable); }
        }
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
''',
        "mosfet": common + r'''
#include "driver/gpio.h"
#define GATE GPIO_NUM_25
void app_main(void) {
    gpio_config_t c={.pin_bit_mask=1ULL<<GATE,.mode=GPIO_MODE_OUTPUT};
    gpio_config(&c); gpio_set_level(GATE,0);
    while (1) {
        gpio_set_level(GATE,1); printf("gate_command=ON expected_vgs_near_3v3 measure=required\n");
        vTaskDelay(pdMS_TO_TICKS(1500));
        gpio_set_level(GATE,0); printf("gate_command=OFF expected_vgs_near_0 measure=required\n");
        vTaskDelay(pdMS_TO_TICKS(1500));
    }
}
''',
        "adc": common + r'''
#include "esp_adc/adc_oneshot.h"
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"
void app_main(void) {
    adc_oneshot_unit_handle_t unit;
    adc_oneshot_unit_init_cfg_t u={.unit_id=ADC_UNIT_1};
    adc_oneshot_new_unit(&u,&unit);
    adc_oneshot_chan_cfg_t c={.atten=ADC_ATTEN_DB_11,.bitwidth=ADC_BITWIDTH_12};
    adc_oneshot_config_channel(unit,ADC_CHANNEL_6,&c);
    adc_cali_handle_t cal=NULL;
    adc_cali_line_fitting_config_t lc={.unit_id=ADC_UNIT_1,.atten=ADC_ATTEN_DB_11,
        .bitwidth=ADC_BITWIDTH_12,.default_vref=0};
    bool calibrated=(adc_cali_create_scheme_line_fitting(&lc,&cal)==ESP_OK);
    while (1) {
        int sum=0, raw=0, mv=-1;
        for(int i=0;i<64;i++){ adc_oneshot_read(unit,ADC_CHANNEL_6,&raw); sum+=raw; }
        raw=sum/64;
        if(calibrated) adc_cali_raw_to_voltage(cal,raw,&mv);
        printf("adc_raw_mean=%d calibrated_mv=%d calibrated=%d dmm_mv=RECORD\n",raw,mv,calibrated);
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
''',
        "uart": common + r'''
#include <stdint.h>
#include <string.h>
#include "driver/uart.h"
#define TX_PORT UART_NUM_1
#define RX_PORT UART_NUM_2
#define TX_BAUD 115200
#define RX_BAUD 115200
static uint8_t crc8(const uint8_t *p,size_t n){uint8_t c=0;while(n--){c^=*p++;for(int i=0;i<8;i++)c=c&0x80?(c<<1)^0x07:c<<1;}return c;}
void app_main(void){
    uart_config_t txc={.baud_rate=TX_BAUD,.data_bits=UART_DATA_8_BITS,.parity=UART_PARITY_DISABLE,
        .stop_bits=UART_STOP_BITS_1,.flow_ctrl=UART_HW_FLOWCTRL_DISABLE,.source_clk=UART_SCLK_DEFAULT};
    uart_config_t rxc=txc;rxc.baud_rate=RX_BAUD;
    ESP_ERROR_CHECK(uart_driver_install(TX_PORT,256,0,0,NULL,0));
    ESP_ERROR_CHECK(uart_driver_install(RX_PORT,256,0,0,NULL,0));
    ESP_ERROR_CHECK(uart_param_config(TX_PORT,&txc));ESP_ERROR_CHECK(uart_param_config(RX_PORT,&rxc));
    ESP_ERROR_CHECK(uart_set_pin(TX_PORT,GPIO_NUM_17,UART_PIN_NO_CHANGE,UART_PIN_NO_CHANGE,UART_PIN_NO_CHANGE));
    ESP_ERROR_CHECK(uart_set_pin(RX_PORT,UART_PIN_NO_CHANGE,GPIO_NUM_16,UART_PIN_NO_CHANGE,UART_PIN_NO_CHANGE));
    uint8_t seq=0,rx[32];
    while(1){
        uint8_t f[]={0xA5,seq++,3,'S','P','I',0}; f[6]=crc8(f,6);
        uart_write_bytes(TX_PORT,f,sizeof(f));
        int n=uart_read_bytes(RX_PORT,rx,sizeof(rx),pdMS_TO_TICKS(100));
        bool ok=n==7&&rx[0]==0xA5&&rx[2]==3&&crc8(rx,6)==rx[6];
        printf("tx_baud=%d rx_baud=%d uart_rx=%d frame=%s seq=%u\n",
            TX_BAUD,RX_BAUD,n,ok?"ACCEPT":"REJECT",n>1?rx[1]:0);
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}
''',
        "i2c": common + r'''
#include <stdint.h>
#include "driver/i2c_master.h"
#include "driver/gpio.h"
#include "esp_rom_sys.h"
#define SDA GPIO_NUM_21
#define SCL GPIO_NUM_22
static esp_err_t read16(i2c_master_dev_handle_t d,uint8_t reg,uint16_t *out){
    uint8_t b[2]={0}; esp_err_t e=i2c_master_transmit_receive(d,&reg,1,b,2,100);
    *out=((uint16_t)b[0]<<8)|b[1]; return e;
}
static void recover(void){
    gpio_config_t c={.pin_bit_mask=(1ULL<<SDA)|(1ULL<<SCL),.mode=GPIO_MODE_INPUT_OUTPUT_OD,
        .pull_up_en=GPIO_PULLUP_ENABLE}; gpio_config(&c); gpio_set_level(SDA,1);
    for(int i=0;i<9;i++){gpio_set_level(SCL,0);esp_rom_delay_us(5);gpio_set_level(SCL,1);esp_rom_delay_us(5);}
    gpio_set_level(SDA,0);gpio_set_level(SCL,1);esp_rom_delay_us(5);gpio_set_level(SDA,1);
}
void app_main(void){
    recover();
    i2c_master_bus_handle_t bus; i2c_master_dev_handle_t dev;
    i2c_master_bus_config_t bc={.i2c_port=I2C_NUM_0,.sda_io_num=SDA,.scl_io_num=SCL,
        .clk_source=I2C_CLK_SRC_DEFAULT,.glitch_ignore_cnt=7,.flags.enable_internal_pullup=false};
    ESP_ERROR_CHECK(i2c_new_master_bus(&bc,&bus));
    for(int a=8;a<0x78;a++)if(i2c_master_probe(bus,a,20)==ESP_OK)printf("i2c_ack=0x%02x\n",a);
    i2c_device_config_t dc={.dev_addr_length=I2C_ADDR_BIT_LEN_7,.device_address=0x48,.scl_speed_hz=100000};
    ESP_ERROR_CHECK(i2c_master_bus_add_device(bus,&dc,&dev));
    uint16_t id=0,temp=0;
    esp_err_t e1=read16(dev,0x0F,&id),e2=read16(dev,0x00,&temp);
    printf("tmp117 id=0x%04x id_status=%s\n",id,(e1==ESP_OK&&id==0x0117)?"VALID":"REJECT");
    if(e2==ESP_OK)printf("raw_temp=0x%04x temp_c_x1000=%ld\n",temp,(long)((int16_t)temp*78125/10000));
    else printf("temperature_read=NACK value=UNKNOWN\n");
}
''',
        "shift": common + r'''
#include <stdint.h>
#include "driver/spi_master.h"
#include "driver/gpio.h"
#define LATCH GPIO_NUM_32
#define SHIFT_LSB_FIRST 0
static uint8_t reverse8(uint8_t x){x=(x&0xF0)>>4|(x&0x0F)<<4;x=(x&0xCC)>>2|(x&0x33)<<2;return (x&0xAA)>>1|(x&0x55)<<1;}
void app_main(void){
    spi_bus_config_t b={.mosi_io_num=GPIO_NUM_23,.miso_io_num=-1,.sclk_io_num=GPIO_NUM_18,
        .quadwp_io_num=-1,.quadhd_io_num=-1,.max_transfer_sz=1};
    spi_device_interface_config_t d={.clock_speed_hz=1000000,.mode=0,.spics_io_num=-1,.queue_size=1};
    spi_device_handle_t dev; ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST,&b,SPI_DMA_DISABLED));
    ESP_ERROR_CHECK(spi_bus_add_device(SPI2_HOST,&d,&dev)); gpio_set_direction(LATCH,GPIO_MODE_OUTPUT);
    while(1)for(int i=0;i<8;i++){
        uint8_t v=1u<<i,tx=SHIFT_LSB_FIRST?reverse8(v):v;
        spi_transaction_t t={.length=8,.tx_buffer=&tx}; gpio_set_level(LATCH,0);
        ESP_ERROR_CHECK(spi_device_polling_transmit(dev,&t)); gpio_set_level(LATCH,1);
        printf("shifted=0x%02x visible=0x%02x lsb_first=%d\n",tx,v,SHIFT_LSB_FIRST);
        vTaskDelay(pdMS_TO_TICKS(350));
    }
}
''',
        "eeprom": common + r'''
#include <stdint.h>
#include <string.h>
#include "driver/spi_master.h"
#define CS GPIO_NUM_32
static spi_device_handle_t dev;
static esp_err_t xfer(const void *tx,void *rx,size_t n){spi_transaction_t t={.length=n*8,.tx_buffer=tx,.rx_buffer=rx};return spi_device_polling_transmit(dev,&t);}
static uint8_t status(void){uint8_t tx[2]={0x05,0},rx[2]={0};xfer(tx,rx,2);return rx[1];}
static void wren(void){uint8_t c=0x06;xfer(&c,NULL,1);}
static void wrdi(void){uint8_t c=0x04;xfer(&c,NULL,1);}
static bool wait_ready(void){for(int i=0;i<100;i++){if(!(status()&1))return true;vTaskDelay(pdMS_TO_TICKS(1));}return false;}
static uint32_t crc32(const uint8_t*p,size_t n){uint32_t c=~0u;while(n--){c^=*p++;for(int i=0;i<8;i++)c=c&1?(c>>1)^0xEDB88320:c>>1;}return~c;}
static esp_err_t write_page(uint16_t a,const uint8_t*p,size_t n){
    if(!n||n>64||((a&63)+n)>64||(uint32_t)a+n>32768)return ESP_ERR_INVALID_ARG;
    uint8_t tx[67]={0x02,a>>8,a};memcpy(tx+3,p,n);wren();esp_err_t e=xfer(tx,NULL,n+3);
    return e==ESP_OK&&wait_ready()?ESP_OK:ESP_ERR_TIMEOUT;
}
static esp_err_t start_write_no_wait(uint16_t a,const uint8_t*p,size_t n){
    if(!n||n>64||((a&63)+n)>64||(uint32_t)a+n>32768)return ESP_ERR_INVALID_ARG;
    uint8_t tx[67]={0x02,a>>8,a};memcpy(tx+3,p,n);wren();return xfer(tx,NULL,n+3);
}
static void read_bytes(uint16_t a,uint8_t*p,size_t n){uint8_t tx[67]={0x03,a>>8,a},rx[67]={0};xfer(tx,rx,n+3);memcpy(p,rx+3,n);}
static void write_without_wren(uint16_t a,const uint8_t*p,size_t n){uint8_t tx[67]={0x02,a>>8,a};memcpy(tx+3,p,n);wrdi();xfer(tx,NULL,n+3);}
void app_main(void){
    spi_bus_config_t b={.mosi_io_num=GPIO_NUM_23,.miso_io_num=GPIO_NUM_19,.sclk_io_num=GPIO_NUM_18,
        .quadwp_io_num=-1,.quadhd_io_num=-1,.max_transfer_sz=80};
    spi_device_interface_config_t d={.clock_speed_hz=1000000,.mode=0,.spics_io_num=CS,.queue_size=1};
    ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST,&b,SPI_DMA_CH_AUTO));ESP_ERROR_CHECK(spi_bus_add_device(SPI2_HOST,&d,&dev));
    uint8_t status_initial=status();wren();uint8_t status_wren=status();wrdi();uint8_t status_wrdi=status();
    printf("status_initial=%02x status_after_wren=%02x wel_after_wren=%u status_after_wrdi=%02x\n",
        status_initial,status_wren,(status_wren&2)!=0,status_wrdi);
    uint8_t payload[]="EEPROM-PAGE-OK",rx[sizeof(payload)]={0};
    esp_err_t cross=write_page(63,payload,sizeof(payload));
    ESP_ERROR_CHECK(write_page(0x0100,payload,sizeof(payload)));read_bytes(0x0100,rx,sizeof(rx));
    uint8_t before[4],after[4],blocked[4]={0x11,0x22,0x33,0x44};read_bytes(0x0140,before,4);
    write_without_wren(0x0140,blocked,4);vTaskDelay(pdMS_TO_TICKS(10));read_bytes(0x0140,after,4);
    uint8_t pending[4]={0xA5,0x5A,0xC3,0x3C},early[4]={0},final[4]={0};
    ESP_ERROR_CHECK(start_write_no_wait(0x0180,pending,sizeof(pending)));uint8_t early_status=status();
    read_bytes(0x0180,early,sizeof(early));ESP_ERROR_CHECK(wait_ready()?ESP_OK:ESP_ERR_TIMEOUT);read_bytes(0x0180,final,sizeof(final));
    printf("no_wren=%s page_cross=%s premature_wip=%u premature_match=%u final_match=%u crc_write=%08lx crc_read=%08lx verify=%s\n",
        memcmp(before,after,4)?"UNEXPECTED_CHANGE":"REJECT",
        cross==ESP_ERR_INVALID_ARG?"REJECT":"BUG",(early_status&1)!=0,!memcmp(early,pending,sizeof(early)),
        !memcmp(final,pending,sizeof(final)),(unsigned long)crc32(payload,sizeof(payload)),
        (unsigned long)crc32(rx,sizeof(rx)),memcmp(payload,rx,sizeof(rx))?"FAIL":"PASS");
}
''',
        "nor": common + r'''
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include "driver/spi_master.h"
#define CS GPIO_NUM_32
#define SECTOR 4096u
#define SLOT0 0x000000u
#define SLOT1 0x001000u
#define PREPARED 0x7Fu
#define COMMITTED 0x3Fu
#define RUN_RESERVED_SECTOR_WRITE_DEMO 0
typedef struct __attribute__((packed)){uint32_t magic;uint16_t schema;uint32_t generation;uint16_t length;uint32_t payload_crc;uint32_t header_crc;uint8_t commit;} record_t;
static spi_device_handle_t dev;
static uint32_t crc32(const uint8_t*p,size_t n){uint32_t c=~0u;while(n--){c^=*p++;for(int i=0;i<8;i++)c=c&1?(c>>1)^0xEDB88320:c>>1;}return~c;}
static esp_err_t xfer(const void*tx,void*rx,size_t n){spi_transaction_t t={.length=n*8,.tx_buffer=tx,.rx_buffer=rx};return spi_device_polling_transmit(dev,&t);}
static uint8_t sr(void){uint8_t tx[2]={0x05,0},rx[2]={0};xfer(tx,rx,2);return rx[1];}
static void wren(void){uint8_t c=0x06;xfer(&c,NULL,1);}
static bool ready(const char*op,int ms){for(int i=0;i<ms;i++){if(!(sr()&1)){printf("%s_busy_polls=%d\n",op,i);return true;}vTaskDelay(pdMS_TO_TICKS(1));}return false;}
static void readn(uint32_t a,void*out,size_t n){uint8_t tx[300]={0x03,a>>16,a>>8,a},rx[300]={0};xfer(tx,rx,n+4);memcpy(out,rx+4,n);}
static bool erase4k(uint32_t a){
    if(a%SECTOR)return false;uint8_t c[4]={0x20,a>>16,a>>8,a};wren();if(!(sr()&2))return false;
    return xfer(c,NULL,4)==ESP_OK&&ready("erase",5000);
}
static bool program(uint32_t a,const void*p,size_t n){
    if(!n||n>256||((a&255)+n)>256)return false;uint8_t tx[260]={0x02,a>>16,a>>8,a};memcpy(tx+4,p,n);
    wren();if(!(sr()&2))return false;return xfer(tx,NULL,n+4)==ESP_OK&&ready("program",100);
}
static bool valid(uint32_t a,record_t*h,uint8_t*p){
    readn(a,h,sizeof(*h));if(h->magic!=0x455A4631||h->schema!=1||h->length>128||h->commit!=COMMITTED)return false;
    uint32_t saved=h->header_crc;h->header_crc=0;
    bool hh=crc32((uint8_t*)h,offsetof(record_t,header_crc))==saved;h->header_crc=saved;
    readn(a+sizeof(*h),p,h->length);return hh&&crc32(p,h->length)==h->payload_crc;
}
static bool stage(uint32_t a,uint32_t gen,const uint8_t*p,uint16_t n,bool commit){
    if(!n||n>128)return false;
    record_t h={.magic=0x455A4631,.schema=1,.generation=gen,.length=n,.payload_crc=crc32(p,n),.header_crc=0,.commit=PREPARED};
    h.header_crc=crc32((uint8_t*)&h,offsetof(record_t,header_crc));
    if(!erase4k(a)||!program(a,&h,sizeof(h))||!program(a+sizeof(h),p,n))return false;
    uint8_t verify[128];record_t rh;readn(a,&rh,sizeof(rh));readn(a+sizeof(rh),verify,n);
    uint32_t saved=rh.header_crc;rh.header_crc=0;
    bool header_ok=rh.magic==h.magic&&rh.schema==h.schema&&rh.generation==h.generation&&rh.length==n&&
        crc32((uint8_t*)&rh,offsetof(record_t,header_crc))==saved;
    if(!header_ok||rh.payload_crc!=crc32(verify,n))return false;
    if(!commit)return true;
    return program(a+offsetof(record_t,commit),&(uint8_t){COMMITTED},1);
}
void app_main(void){
    spi_bus_config_t b={.mosi_io_num=GPIO_NUM_23,.miso_io_num=GPIO_NUM_19,.sclk_io_num=GPIO_NUM_18,
        .quadwp_io_num=-1,.quadhd_io_num=-1,.max_transfer_sz=300};
    spi_device_interface_config_t d={.clock_speed_hz=1000000,.mode=0,.spics_io_num=CS,.queue_size=1};
    ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST,&b,SPI_DMA_CH_AUTO));ESP_ERROR_CHECK(spi_bus_add_device(SPI2_HOST,&d,&dev));
    uint8_t idtx[4]={0x9F,0,0,0},idrx[4]={0};xfer(idtx,idrx,4);
    printf("jedec=%02x-%02x-%02x status_initial=%02x expected_macronix_mfr=c2\n",idrx[1],idrx[2],idrx[3],sr());
    if(idrx[1]!=0xC2||idrx[2]!=0x20||idrx[3]!=0x16){printf("device=REJECT expected=c2-20-16\n");return;}
    record_t a,bh;uint8_t pa[128],pb[128];bool va=valid(SLOT0,&a,pa),vb=valid(SLOT1,&bh,pb);
    if(!RUN_RESERVED_SECTOR_WRITE_DEMO){
        printf("write_demo=BLOCKED set RUN_RESERVED_SECTOR_WRITE_DEMO=1 only for a dedicated lab part\n");
        printf("slot0_valid=%d slot1_valid=%d\n",va,vb);return;
    }
    if(!va&&!vb){uint8_t p[]="generation-one";ESP_ERROR_CHECK(stage(SLOT0,1,p,sizeof(p),true)?ESP_OK:ESP_FAIL);va=valid(SLOT0,&a,pa);}
    if(va&&!vb){uint8_t p[]="generation-two";ESP_ERROR_CHECK(stage(SLOT1,a.generation+1,p,sizeof(p),true)?ESP_OK:ESP_FAIL);vb=valid(SLOT1,&bh,pb);}
    uint32_t winner=(vb&&(!va||bh.generation>a.generation))?SLOT1:SLOT0;
    uint32_t generation=winner==SLOT1?bh.generation:a.generation;
    uint32_t loser=winner==SLOT1?SLOT0:SLOT1;uint8_t interrupted[]="prepared-not-committed";
    ESP_ERROR_CHECK(stage(loser,generation+1,interrupted,sizeof(interrupted),false)?ESP_OK:ESP_FAIL);
    va=valid(SLOT0,&a,pa);vb=valid(SLOT1,&bh,pb);
    uint32_t recovered=(vb&&(!va||bh.generation>a.generation))?bh.generation:(va?a.generation:0);
    printf("slot0_valid=%d slot1_valid=%d recovery_generation=%lu\n",va,vb,(unsigned long)recovered);
}
''',
    }


def make_project(project: dict, next_project: dict | None) -> None:
    base = project_path(project)
    bom_data = project_bom(project)
    kit_names = ["kit-00-basic-electronics"]
    if project["group"] == "buses":
        kit_names.append("kit-01-digital-buses")
    if project["group"] == "storage":
        kit_names.extend(["kit-01-digital-buses", "kit-02-storage-lab"])
    project_source_keys = ["devkit", "module", "gpio"]
    source_by_firmware = {
        "adc": ["adc"],
        "uart": ["uart"],
        "i2c": ["i2c", "i2c_spec", "tmp117", "tmp117_breakout"],
        "shift": ["spi", "hc595"],
        "eeprom": ["spi", "eeprom"],
        "nor": ["spi", "nor", "nor_status"],
        "mosfet": ["mosfet"],
    }
    project_source_keys.extend(source_by_firmware.get(project["firmware"], []))
    pin_rows = "\n".join(
        f"| {source} | {destination} | {colour} | {tp} |"
        for source, destination, colour, tp in project["pins"]
    )
    buy_rows = "\n".join(
        f"| {row['required_or_optional']} / {row['verified_or_suggested']} | "
        f"{row['manufacturer']} `{row['manufacturer_part_number']}` | {row['package']} | "
        f"{row['supply_voltage']} | {row['india_search_name']} | {row['substitution_rule']} | "
        f"{('[source](' + row['source_url'] + ')') if row['source_url'] else 'learner must verify'} |"
        for row in bom_data
    )
    safety_rows = "\n".join(
        f"- [ ] {check}" for check in PROJECT_SAFETY_CHECKS[project["id"]]
    )
    serial_expectation = (
        EXPECTED_SERIAL[project["firmware"]]
        if project["firmware"]
        else "Not applicable: this project intentionally has no firmware."
    )
    current_expectation = EXPECTED_CURRENT.get(
        project["id"],
        "No numeric current range is asserted without a complete load model and physical measurement.",
    )
    write(
        base / "PROJECT.md",
        f"""
        # {project['title']}

        **Question:** {project['question']}

        **Build:** {project['build']}

        **Visible or measurable result:** {project['measure']}

        **Why useful:** {project['why']}

        **Estimated time:** {project['minutes']} minutes. **Difficulty:** {project['difficulty']}.

        **Required knowledge:** {", ".join(project['prereqs'])}. Read `BEFORE-YOU-POWER.md`.

        **Success:** {project['success']}

        Hardware status: **HARDWARE_VALIDATION_REQUIRED**. Documentation and firmware are not physical proof.
        """,
    )
    write(
        base / "WHY.md",
        f"# Why\n\n{project['why']}\n\n{WHY_EXTRAS.get(project['id'], '')}",
    )
    write(
        base / "BUY.md",
        f"""
        # Buy

        Use shared kits; do not repurchase common parts. The machine-readable copy is `bom.csv`.

        | Need/status | Exact part or reference | Package/form | Voltage boundary | India-friendly search | Substitution/prohibition | Source |
        | --- | --- | --- | --- | --- | --- | --- |
        {buy_rows}

        India-friendly search terms are provided without price or stock claims. Prefer authorized distributors.
        `verified` means the named part's documented electrical properties fit this circuit; it does not mean
        the received item or physical build was tested. Sources were retrieved {RETRIEVED}.
        """,
    )
    write(
        base / "WIRING.md",
        f"""
        # Wiring

        Power off before changing a connection. Orient the ESP32 USB connector toward you and confirm board
        labels; orient IC pin 1 by its notch/dot and datasheet, never by an online photo.

        | Source | Destination | Colour convention | Test point |
        | --- | --- | --- | --- |
        {pin_rows}

        Power path begins at ESP32 3V3 and returns only through ESP32 GND. Add 100 nF at each external IC.
        Expected idle supply is near 3.3 V but must be measured. The mirrored-IC error swaps pin numbers and is
        blocking. A missing common ground, a reversed source/destination assumption or a jumper one row away
        is also wrong even when its wire colour looks correct.

        Assets: [`breadboard.svg`](../../../assets/projects/{project['id']}/breadboard.svg) and
        [`schematic.svg`](../../../assets/projects/{project['id']}/schematic.svg). The SVG is a connection map,
        not a photograph.
        """,
    )
    common_steps = [
        "Disconnect USB and all other power.",
        "Map breadboard rail continuity and mark any split.",
        "Place components; verify package orientation against the exact datasheet.",
        "Add GND, then 3.3 V, then signal wires one at a time.",
        "Add each required 100 nF decoupling capacitor at external IC supply pins.",
        "Check continuity from every source to destination in `pinmap.yaml`.",
        "Complete every blocking item in `BEFORE-YOU-POWER.md`.",
    ]
    all_steps = common_steps + PROJECT_STEPS[project["id"]] + [
        "Record results in `evidence/measurement-template.csv`; expected values never enter measured fields."
    ]
    build_steps = "\n".join(f"{number}. {step}" for number, step in enumerate(all_steps, start=1))
    write(base / "BUILD.md", f"# Build\n\n{build_steps}\n")
    write(
        base / "BEFORE-YOU-POWER.md",
        f"""
        # Before You Power

        - [ ] Supply voltage measured or source confirmed before connection
        - [ ] GND continuity confirmed
        - [ ] No VCC-to-GND short
        - [ ] MCU and peripheral share ground
        - [ ] Logic voltage compatible
        - [ ] Polarized parts oriented correctly
        - [ ] Current limit or resistor configured
        - [ ] Correct chip orientation
        - [ ] 100 nF decoupling installed at each external IC
        - [ ] Test points identified
        - [ ] Only the documented 3.3 V rail is used
        - [ ] No mains, battery or external high-current source is connected

        ## Project-specific blocking checks

        {safety_rows}

        Any unchecked item blocks power-up.
        """,
    )
    write(
        base / "EXPECTED.md",
        f"""
        # Expected

        ## FACT

        Electrical limits and protocol behaviour come from the exact sources in `project.yaml` and `bom.csv`.

        ## EXPECTED

        {project['expected']}

        - **Serial/output pattern:** {serial_expectation}
        - **Voltage and logic range:** the project rail is 3.3 V nominal. Signal nodes are expected between
          project GND and the measured rail; low is near GND and high is near the rail. Exact thresholds and
          supply limits remain the authoritative device-datasheet constraints.
        - **Current:** {current_expectation}
        - **State transition:** {project['success']}
        - **Calculation assumptions:** exact MPNs and wiring in `bom.csv`/`pinmap.yaml`, 3.3 V nominal rail,
          measured resistor values, correct package orientation and no unlisted external load.
        - **Tolerance:** resistor tolerance, supply variation, device thresholds, temperature, breadboard
          resistance and instrument accuracy widen predictions. Record instrument uncertainty; do not turn
          a nominal value into a measured result.

        ## MEASURED

        UNKNOWN until a learner records real instrument results under `evidence/`.

        ## Failure output

        The controlled failure in `BREAK-IT.md` must produce an explicit changed or rejected state, never a
        fabricated screenshot.
        """,
    )
    write(
        base / "BREAK-IT.md",
        f"""
        # Break It Safely

        {project['break']}

        Stay inside ratings. Do not short supplies, reverse power, overheat a component, abuse a battery, use
        mains, or intentionally exceed an absolute maximum.
        """,
    )
    write(
        base / "DEBUG.md",
        """
        # Debug

        Use this order and stop when a stage is wrong:

        Power → ground → orientation → continuity → idle voltage → clock → data → protocol → firmware → output

        | Symptom | Check first | Evidence |
        | --- | --- | --- |
        | no output | 3.3 V and common GND | TP supply measurement |
        | unstable output | floating pin, split rail, loose jumper | continuity and idle voltage |
        | wrong device/data | mirrored IC, wrong address/CS, pin mismatch | pin 1 photo requirement and capture |
        | firmware log but no physical action | load path and GPIO voltage | GPIO/load measurements |
        | intermittent bus | decoupling, ground lead, pull-up/clock timing | supply and logic capture |
        """,
    )
    write(
        base / "MEASURE.md",
        f"""
        # Measure

        Set the DMM to DC voltage above 3.3 V. Connect black to project GND first. Probe only named test points
        with the red lead and avoid adjacent pins.

        **Quantity:** {project['measure']}

        Record instrument model, range, resolution, uncertainty if known, exact test point, state and timestamp.
        Expected values belong in the expected column; actual readings belong only in measured.

        {MEASURE_NOTES.get(project['id'], 'Record the supply first and preserve raw instrument output.')}

        Evidence filename: `{project['id']}-measurements-YYYYMMDD.csv`.
        """,
    )
    write(
        base / "WHAT-YOU-LEARNED.md",
        f"# What You Learned\n\n{project['why']}\n\nCompletion proof: {project['success']}\n",
    )
    if next_project:
        next_link = f"../../{next_project['group']}/{next_project['id']}/PROJECT.md"
        next_text = f"[{next_project['title']}]({next_link})"
    else:
        next_text = "[SSD Lab](../../ssd_lab/README.md)"
    write(base / "NEXT.md", f"# Next\n\nContinue to {next_text} only after the success condition is evidenced.\n")
    write(
        base / "project.yaml",
        f"""
        schemaVersion: 1
        projectId: {project['id']}
        title: "{project['title']}"
        difficulty: {project['difficulty']}
        estimatedMinutes: {project['minutes']}
        primaryBoard: "ESP32-DEVKITC-32E"
        supplyVoltage: "3.3 V"
        requiredTools: [{", ".join(project['tools'])}]
        requiredKits: [{", ".join(kit_names)}]
        interfaces: [{", ".join(project['interfaces'])}]
        prerequisites: [{", ".join(project['prereqs'])}]
        learningOutcomes: ["{project['success']}"]
        blockingSafetyChecks: [supply, ground, short, logic-level, orientation, decoupling]
        sourceReferences: [{", ".join(SOURCES[k][2] for k in project_source_keys)}]
        hardwareValidationStatus: HARDWARE_VALIDATION_REQUIRED
        """,
    )
    fields = [
        "item_id", "category", "description", "manufacturer", "manufacturer_part_number",
        "package", "quantity", "required_or_optional", "verified_or_suggested", "supply_voltage",
        "india_search_name", "substitution_rule", "source_url", "retrieved_at", "notes",
    ]
    write_csv(base / "bom.csv", fields, bom_data)
    nets = "\n".join(
        f"  - source: \"{source}\"\n    destination: \"{destination}\"\n"
        f"    colourConvention: {colour}\n    testPoint: {tp}"
        for source, destination, colour, tp in project["pins"]
    )
    write(base / "pinmap.yaml", f"schemaVersion: 1\nprojectId: {project['id']}\nnets:\n{nets}\n")
    address_constraint = ""
    if project["id"] == "09-spi-eeprom":
        address_constraint = """
          - id: eeprom-demo-range
            category: storage
            severity: blocking
            statement: The default bounded tests use only addresses 0x0100 through 0x0183 on a dedicated lab EEPROM.
        """
    if project["id"] == "10-spi-nor-mini-storage":
        address_constraint = """
          - id: nor-demo-range
            category: storage
            severity: blocking
            statement: Only dedicated external NOR sectors 0 and 1 may be erased by the demo.
          - id: explicit-write-gate
            category: safety
            severity: blocking
            statement: RUN_RESERVED_SECTOR_WRITE_DEMO remains zero until the learner confirms a dedicated lab part.
        """
    write(
        base / "constraints.yaml",
        f"""
        schemaVersion: 1
        constraints:
          - id: project-rail
            category: electrical
            severity: blocking
            statement: All learner-wired circuits use the ESP32 3.3 V rail.
            expected: {{operator: equal, unit: V, value: 3.3}}
          - id: power-off-rewire
            category: safety
            severity: blocking
            statement: USB and all power are disconnected before rewiring or continuity tests.
          - id: evidence-separation
            category: validation
            severity: blocking
            statement: Expected values are never recorded as measured values.
        {address_constraint}
        """,
    )
    write(
        base / "decisions/README.md",
        f"""
        # Decisions

        - Board: {BOARD}; selected once for v1 to avoid duplicate firmware paths.
        - Supply: 3.3 V only.
        - Project choice: {project['why']}
        - Hardware execution: not performed; evidence remains required.
        """,
    )
    write(
        base / "validation/checklist.md",
        f"""
        # Validation Checklist

        - [x] Required project-contract files present
        - [x] Pin table represented in `pinmap.yaml` and both SVGs
        - [x] Expected result labelled EXPECTED
        - [x] Controlled failure remains within ratings
        - [x] Hardware validation status explicit
        - [ ] Firmware built with {SDK}
        - [ ] Circuit assembled and photographed
        - [ ] Supply and signal measurements recorded
        - [ ] Controlled failure physically executed and recovered
        """,
    )
    expected_json = {
        "schemaVersion": 1,
        "projectId": project["id"],
        "hardwareValidationStatus": "HARDWARE_VALIDATION_REQUIRED",
        "results": [
            {"id": "power", "classification": "EXPECTED", "expectation": "3.3 V project rail; measure actual", "measured": None},
            {"id": "success", "classification": "EXPECTED", "expectation": project["success"], "measured": None},
        ],
    }
    write(base / "validation/expected-results.json", json.dumps(expected_json, indent=2))
    write(
        base / "evidence/README.md",
        f"""
        # Evidence

        No physical evidence is included. Required files:

        - `{project['id']}-measurements-YYYYMMDD.csv`
        - `{project['id']}-assembled-front-YYYYMMDD.jpg`
        - `{project['id']}-assembled-top-YYYYMMDD.jpg`
        - bus projects: `{project['id']}-logic-YYYYMMDD.png`
        {"- `breadboard-map-template.csv` with breadboard model, continuity pairs, split position and measured rail voltage." if project['id'] == "01-know-your-breadboard" else ""}

        Record operator, board/module marking, component lot, instrument, probe map, settings and timestamp.
        """,
    )
    write_csv(
        base / "evidence/measurement-template.csv",
        ["timestamp_utc", "instrument", "range", "test_point", "state", "expected", "measured", "unit", "uncertainty", "operator", "notes"],
        [],
    )
    if project["id"] == "01-know-your-breadboard":
        write_csv(
            base / "evidence/breadboard-map-template.csv",
            [
                "breadboard_manufacturer", "breadboard_model", "tested_hole_a", "tested_hole_b",
                "continuity_result", "identified_split_position", "rail_name", "measured_rail_voltage_v",
                "instrument", "timestamp_utc", "operator", "photo_filename", "notes",
            ],
            [],
        )
    write(
        base / "HARDWARE-VALIDATION-REQUIRED.md",
        f"""
        # Hardware Validation Required

        The circuit, firmware and expected values have not been executed on physical hardware in this change.
        Required gate: assemble exactly, photograph both angles, measure every named point, run normal and
        controlled-failure cases, save raw evidence, and update `hardwareValidationStatus` only after review.
        """,
    )
    code_dir = base / "CODE"
    write(
        code_dir / "README.md",
        f"""
        # Code

        Toolchain: {SDK}. Install the official SDK, then from this directory run:

        ```sh
        idf.py set-target esp32
        idf.py build
        idf.py -p PORT flash monitor
        ```

        Build status in Work Mode: **NOT RUN** because ESP-IDF is not installed. Project firmware is absent
        only where the physical experiment does not require it.
        """,
    )
    if project["firmware"]:
        component_requires = "driver esp_adc" if project["firmware"] == "adc" else "driver"
        write(
            code_dir / "CMakeLists.txt",
            f"""
            cmake_minimum_required(VERSION 3.16)
            include($ENV{{IDF_PATH}}/tools/cmake/project.cmake)
            project(efz_{project['id'].replace('-', '_')})
            """,
        )
        write(
            code_dir / "main/CMakeLists.txt",
            f'idf_component_register(SRCS "main.c" INCLUDE_DIRS "." REQUIRES {component_requires})\n',
        )
        write(code_dir / "main/main.c", firmware_sources()[project["firmware"]])
        write(code_dir / "sdkconfig.defaults", "CONFIG_IDF_TARGET=\"esp32\"\nCONFIG_ESP_CONSOLE_UART_BAUDRATE=115200\n")

    asset_base = Path("assets/projects") / project["id"]
    write(asset_base / "breadboard.svg", svg_asset(project, "breadboard"))
    write(asset_base / "schematic.svg", svg_asset(project, "schematic"))
    write(
        asset_base / "PHOTO-REQUIRED.md",
        f"""
        # Physical Photos Required

        Required evidence filenames:

        - `{project['id']}-assembled-front-YYYYMMDD.jpg`
        - `{project['id']}-assembled-top-YYYYMMDD.jpg`

        Camera checklist:

        - [ ] Front angle is level with the breadboard; board/module marking, USB orientation, IC pin
          1/polarity mark, 3.3 V rail and GND rail are readable.
        - [ ] Top angle is perpendicular to the breadboard; every jumper endpoint, rail split/bridge,
          decoupling capacitor and named test point is unobscured.
        - [ ] Neutral diffuse lighting shows wire endpoints without glare, deep shadow or a hand in frame.
        - [ ] Project ID, TP labels and rail labels are physically present and readable.
        - [ ] Both photos were checked against `pinmap.yaml` and `WIRING.md`.
        """,
    )
    write(
        asset_base / "CAPTURE-REQUIRED.md",
        f"""
        # Instrument Capture Required

        Do not fabricate `logic-capture.png` or `meter-reading.jpg`. Capture real hardware only.

        - Meter evidence: `{project['id']}-meter-reading-YYYYMMDD.jpg`.
        - Bus evidence when the project has a digital bus: `{project['id']}-logic-YYYYMMDD.png`.
        - Include probe-to-test-point map, sample rate or meter range, threshold, trigger, timebase, board
          state and timestamp.
        - Confirm the capture agrees with `pinmap.yaml`; keep raw analyzer data alongside the exported image.
        - For projects without a digital bus, a logic capture is not required; the measurement CSV and
          meter evidence remain required.
        """,
    )


def make_projects() -> None:
    for index, project in enumerate(PROJECTS):
        make_project(project, PROJECTS[index + 1] if index + 1 < len(PROJECTS) else None)
    write(
        "projects/breadboard/README.md",
        "# Breadboard Projects\n\n" + "\n".join(
            f"- [{p['title']}]({p['id']}/PROJECT.md)" for p in PROJECTS if p["group"] == "breadboard"
        ),
    )
    write(
        "projects/buses/README.md",
        "# Bus Projects\n\n" + "\n".join(
            f"- [{p['title']}]({p['id']}/PROJECT.md)" for p in PROJECTS if p["group"] == "buses"
        ),
    )
    write(
        "projects/storage/README.md",
        "# Storage Projects\n\n" + "\n".join(
            f"- [{p['title']}]({p['id']}/PROJECT.md)" for p in PROJECTS if p["group"] == "storage"
        )
        + "\n\nContinue to [`projects/ssd_lab`](../ssd_lab/README.md).\n",
    )


def main() -> None:
    make_research()
    make_start()
    make_learning()
    make_template()
    make_kits()
    make_projects()
    print(f"generated Electronics From Zero v1 under {ROOT}")


if __name__ == "__main__":
    main()
