# Electronics From Zero Source Ledger

Retrieval date: 2026-07-25

Primary sources were used for electrical limits, protocols and SDK behaviour. Distributor or
open-hardware pages are used only to verify package, breakout topology or availability.

| Authority | Source | Decision supported |
| --- | --- | --- |
| Espressif | [ESP32-DevKitC V4 User Guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html) | devkit |
| Espressif | [ESP32-WROOM-32E/32UE Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32e_esp32-wroom-32ue_datasheet_en.pdf) | module |
| Espressif | [ESP32 Series Datasheet](https://documentation.espressif.com/esp32_datasheet_en.pdf) | soc |
| Espressif | [ESP-IDF GPIO Driver](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/gpio.html) | gpio |
| Espressif | [ESP-IDF ADC Oneshot Driver](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/adc/adc_oneshot.html) | adc |
| Espressif | [ESP-IDF UART Driver](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/uart.html) | uart |
| Espressif | [ESP-IDF I2C Driver](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/i2c.html) | i2c |
| Espressif | [ESP-IDF SPI Master Driver](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/spi_master.html) | spi |
| NXP | [UM10204 I2C-bus Specification and User Manual](https://www.nxp.com/documents/user_manual/UM10204.pdf) | i2c spec |
| Texas Instruments | [TMP117 Datasheet](https://www.ti.com/lit/gpn/TMP117) | tmp117 |
| Adafruit | [TMP117 Breakout Product 4821 and Open Hardware](https://github.com/adafruit/Adafruit-TMP117-PCB) | tmp117 breakout |
| Texas Instruments | [PCA9306 Dual Bidirectional I2C/SMBus Voltage-Level Translator Datasheet](https://www.ti.com/lit/gpn/PCA9306) | level shifter |
| Texas Instruments | [SN74HC595 Datasheet](https://www.ti.com/lit/ds/symlink/sn74hc595.pdf) | hc595 |
| Microchip | [25AA256/25LC256 Datasheet](https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/25AA256-25LC256-256K-SPI-Bus-Serial-EEPROM-20001822J.pdf) | eeprom |
| Macronix | [MX25L3233F Datasheet](https://www.macronix.com/Lists/Datasheet/Attachments/8933/MX25L3233F%2C%203V%2C%2032Mb%2C%20v1.7.pdf) | nor |
| Macronix | [Serial NOR Product Status](https://www.macronix.com/en-us/products/NOR-Flash/Serial-NOR-Flash/Pages/default.aspx) | nor status |
| Alpha & Omega Semiconductor | [AO3400A Datasheet](https://www.aosmd.com/res/data_sheets/AO3400A.pdf) | mosfet |
| onsemi | [P2N2222A Datasheet](https://www.onsemi.com/download/data-sheet/pdf/p2n2222a-d.pdf) | bjt |
| Same Sky | [CMI-1295IC-0385T Magnetic Buzzer Indicator Datasheet](https://www.sameskydevices.com/product/resource/cmi-1295ic-0385t.pdf) | buzzer |
| USB Implementers Forum | [USB 2.0 Specification and Micro-USB Documents](https://www.usb.org/document-library/usb-20-specification) | usb cable |
| Saleae | [Logic Analyzer Input Specifications](https://www.saleae.com/logic) | logic |
| Winbond | [W25N-JW QSPI NAND Product Page](https://www.winbond.com/hq/product/code-storage-flash/qspi-nand/w25n-jw/?__locale=en) | nand |
| Texas Instruments | [TPS7A20 Datasheet](https://www.ti.com/lit/ds/symlink/tps7a20.pdf) | ldo |
| Texas Instruments | [TPD4E05U06 Datasheet](https://www.ti.com/lit/ds/symlink/tpd4e05u06.pdf) | esd |
| Silicon Labs / Adafruit | [CP2102N Datasheet and Friend Open Hardware](https://www.silabs.com/documents/public/data-sheets/cp2102n-datasheet.pdf) | usb uart |

## Claim rules

- **FACT**: traceable to a source above or repository code.
- **EXPECTED**: calculated or predicted for a stated circuit and tolerance.
- **MEASURED**: recorded from real hardware with instrument and evidence metadata.
- **UNKNOWN**: not yet verified.

Search results and marketplace descriptions are discovery aids only. No current price or stock
claim is frozen into v1.
