# ESP8266 engineering platform dossier

## Scope

This dossier is the traceability anchor for ESP8266 work. It distinguishes established engineering practice, vendor recommendations, Daxini implementation decisions, and future proposals. Do not add electrical limits, timing values, boot strapping requirements, memory sizes, radio behavior, or production-test limits unless the value is copied into a validation record with a primary reference.

## History

Record the product-family evolution, silicon revisions, ecosystem changes, and compatibility traps that affect firmware, PCB design, debug, or manufacturing.

## Architecture

Document core, bus fabric, memory map, clock tree, reset domains, interrupt controller, debug blocks, and boot ROM behavior. Link each block to a diagram in `diagrams/` and to the relevant reference-manual chapter.

## Memory

Capture volatile memory, nonvolatile memory, cache behavior, alignment constraints, linker-script ownership, bootloader partitions, calibration storage, and wear-out risks.

## Peripherals

Map GPIO, ADC, DAC, PWM/timers, UART, SPI, I2C, CAN, USB, Ethernet, radio, DMA, watchdog, RTC, and low-power peripherals to the peripheral dossiers under `docs/peripherals/`.

## Boot process

Describe reset sources, strap pins or option bytes, ROM loader behavior, bootloader handoff, image validation, rollback, security state, and factory recovery path.

## Clocks and power

Record clock sources, PLLs, dynamic-frequency changes, sleep modes, wake sources, brownout behavior, sequencing, decoupling assumptions, and measurement points.

## Interrupts and DMA

Define ISR ownership, priority policy, latency budget, DMA descriptor ownership, cache-coherency requirements, buffer lifetimes, and safe logging rules.

## Debugging

List supported probes, JTAG/SWD/UART boot modes, trace options, panic artifacts, logic-analyzer channels, and minimum captures required for regressions.

## Production

Define programming, serialization, calibration, functional test, boundary conditions, ESD handling, firmware version capture, lot traceability, and rework policy.

## Traceable references

- Espressif ESP32 hardware reference and linked TRM, datasheet, hardware design guidelines, and errata: https://docs.espressif.com/projects/esp-idf/en/stable/esp32/hw-reference/index.html
- STMicroelectronics STM32 documentation portal and reference manuals: https://www.st.com/en/microcontrollers-microprocessors/stm32-32-bit-arm-cortex-mcus/documentation.html
- Raspberry Pi RP2040 datasheet and hardware-design guide: https://pip.raspberrypi.com/documents/RP-008371-DS-rp2040-datasheet.pdf and https://pip.raspberrypi.com/documents/RP-008279-DS-hardware-design-with-rp2040.pdf
- Arm Cortex-M developer documentation and generic user guides: https://developer.arm.com/documentation/dui0553/b and https://developer.arm.com/community/arm-community-blogs/b/architectures-and-processors-blog/posts/cortex-m-resources
- Microchip 8-bit MCU documentation and datasheets: https://www.microchip.com/en-us/products/microcontrollers-and-microprocessors/8-bit-mcus
- RISC-V unprivileged and privileged ISA specifications: https://riscv.org/technical/specifications/
- IETF RFC index for Internet protocols: https://www.rfc-editor.org/
- IPC standards landing page for PCB design/manufacturing evidence: https://www.ipc.org/standards
- NIST cybersecurity and engineering publications: https://csrc.nist.gov/publications

Claims in this repository must cite the exact datasheet, reference-manual section, standard clause, application note, or measured report used during review.

