# Primary Board Selection Decision

## Decision

Select **Espressif ESP32-DevKitC V4 with ESP32-WROOM-32E** and **ESP-IDF v5.2.3** for v1.

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

- Espressif, [ESP32-DevKitC V4 User Guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html) (retrieved 2026-07-25).
- Espressif, [ESP32-WROOM-32E/32UE Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32e_esp32-wroom-32ue_datasheet_en.pdf) (retrieved 2026-07-25).
- Espressif, [ESP32 Series Datasheet](https://documentation.espressif.com/esp32_datasheet_en.pdf) (retrieved 2026-07-25).
- Espressif, [ESP-IDF GPIO Driver](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/gpio.html) (retrieved 2026-07-25).
- Espressif, [ESP-IDF ADC Oneshot Driver](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/adc/adc_oneshot.html) (retrieved 2026-07-25).
