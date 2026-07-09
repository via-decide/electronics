# Engineering index

This index links component knowledge from theory to production evidence. A component is not considered production-ready until every column has a reviewed artifact.

| Component | Theory | Implementation | Example | Benchmark | Validation | Reports | Source code | References |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ESP32 | docs/platforms/esp32/README.md | docs/implementation.md | examples/esp32/README.md | docs/benchmarks.md | tests/hardware_validation/README.md | reports/esp32_master_validation.md | examples/esp32/ | docs/references.md |
| ADC | docs/peripherals/adc/theory.md | docs/peripherals/adc/implementation.md | examples/esp32/adc_dma/README.md | benchmarks/README.md | docs/peripherals/adc/validation.md | reports/electrical-validation/README.md | tasks/esp32/ | docs/peripherals/adc/references.md |
| SPI DMA | docs/peripherals/spi/implementation.md | docs/peripherals/dma/implementation.md | examples/esp32/spi_dma/README.md | benchmarks/README.md | docs/peripherals/spi/validation.md | reports/benchmark-summary/README.md | examples/esp32/spi_dma/ | docs/peripherals/spi/references.md |
| OTA | docs/peripherals/ota/theory.md | docs/peripherals/ota/implementation.md | examples/esp32/ota/README.md | benchmarks/README.md | docs/peripherals/ota/validation.md | reports/firmware-validation/README.md | examples/esp32/ota/ | docs/peripherals/ota/references.md |

## Decision classification

Every major engineering decision must be labelled as one of:

- **Established engineering practice**: supported by textbooks, standards, mathematical derivation, or repeated measured evidence.
- **Vendor recommendation**: supported by device vendor datasheets, reference manuals, application notes, design guidelines, or errata.
- **Daxini implementation decision**: a repository-specific architecture, coding, validation, or production choice.
- **Future proposal**: intentionally unimplemented or unvalidated work.
