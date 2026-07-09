# LoRa references

## Purpose

This page records LoRa engineering knowledge for production firmware and hardware validation. It must be kept traceable to source code, examples, benchmarks, reports, and primary references.

## Established engineering practice

- State physical assumptions, equations, timing budgets, loading, signal-integrity constraints, and measurement uncertainty before implementation claims.
- Treat unspecified electrical or timing values as unknown until confirmed from a datasheet, reference manual, standard, or measured validation report.

## Vendor recommendation

- Insert vendor-specific guidance only with an exact primary-source link and reviewed device family.
- Cross-check errata before accepting nominal behavior.

## Daxini implementation decision

- Link the driver, example, task, validation procedure, benchmark record, and production-risk entry that implement this LoRa policy.

## Future proposal

- List improvements separately from shipped behavior so roadmap ideas are not confused with validated production support.

## Validation and production checklist

- Define instruments, firmware revision, board revision, wiring, environmental conditions, pass/fail limits, repeatability, and artifact storage.
- Capture failure modes, recovery procedure, and manufacturing-screen coverage.

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

