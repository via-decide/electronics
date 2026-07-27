# You have an ESP32 or RP2040, a breadboard and some wires. Start here.

Pick the first statement that matches you. You do not need to understand the repository structure.

If you already know what you want to build, use the
[visual project catalog](projects/README.md) to preview the wiring, open the
code and enter the full validation path.

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

**Need:** Kits 00-01. **Install:** ESP-IDF v5.2.3. **Build first:** Project 05 for analog or Project 06
for buses. **Success:** firmware output agrees with a physical measurement.
**Common mistake:** treating serial output as proof of electrical correctness. **Next:** UART →
I2C → SPI. **Effort:** 4-8 hours for the review path. **Safety:** complete every power-up gate.
**Tools:** DMM, serial terminal and logic analyzer when bus timing is the question.

## Path C — I want to understand storage hardware

Follow: shift register → SPI EEPROM → SPI NOR → page program → erase → CRC → interrupted write →
metadata → raw NAND → ECC → logical-to-physical mapping. Storage is not simply “saving bytes.”

**Need:** Kits 00-02. **Install:** ESP-IDF v5.2.3 and a serial terminal. **Build first:**
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

**Need:** Kits 00-03. **Install:** ESP-IDF v5.2.3 and the repository's existing validation dependencies.
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
