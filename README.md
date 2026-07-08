# via-decide Electronics

`via-decide/electronics` is an engineering knowledge base for embedded systems, electronics architecture, firmware design, validation, and production readiness. The repository is intended to be both a working implementation space and a learning handbook: every design should explain the engineering problem, the theoretical basis, the implementation architecture, the validation method, and the production risks.

## Engineering Philosophy

The repository follows a design-for-evidence model:

1. Define the physical or system problem before selecting an implementation.
2. Explain why naive approaches fail under real timing, power, memory, network, or manufacturing constraints.
3. Tie design decisions to equations, measurements, datasheets, standards, or official vendor documentation.
4. Keep time-critical firmware paths separated from network, storage, logging, and user-interface latency.
5. Treat debugging, benchmarks, calibration, telemetry, and production diagnostics as first-class engineering artifacts.

## Learning Roadmap

```text
Fundamentals
  ↓
Signal integrity, sampling theory, power integrity, timing, and RTOS concepts
  ↓
Platform implementation
  ↓
ESP-IDF drivers, peripheral ownership, DMA, timers, queues, NVS, OTA, MQTT
  ↓
Validation and debugging
  ↓
Oscilloscope, logic analyzer, UART logs, JTAG, stress tests, fault injection
  ↓
Production engineering
  ↓
Calibration, reliability, EMC, security, manufacturing, telemetry, field updates
```

Recommended entry order:

1. [`docs/theory.md`](docs/theory.md) for engineering principles and mathematical foundations.
2. [`docs/implementation.md`](docs/implementation.md) for architecture, APIs, state machines, and data flow.
3. [`docs/debugging.md`](docs/debugging.md) for instrumentation and root-cause workflows.
4. [`docs/benchmarks.md`](docs/benchmarks.md) for measurement methodology and benchmark records.
5. [`docs/production.md`](docs/production.md) for manufacturing, reliability, OTA, calibration, EMC, security, and certification concerns.
6. [`examples/README.md`](examples/README.md) for runnable reference implementations.
7. [`tests/README.md`](tests/README.md) for validation procedures and acceptance criteria.

## Supported Platforms

| Platform | Scope |
| --- | --- |
| ESP32 / ESP-IDF | ADC DMA sampling, FreeRTOS task isolation, MQTT telemetry, OTA rollback, NVS calibration, I2C recovery, deep sleep, timers, brownout diagnostics. |
| STM32 | Planned microcontroller examples and hardware-timed peripheral patterns. |
| Raspberry Pi | Planned Linux-adjacent hardware integration examples. |
| Linux | Planned host tooling, data capture, validation, and device-side service examples. |
| Power electronics | Planned measurement, conversion, thermal, and protection references. |

## Folder Overview

| Path | Responsibility |
| --- | --- |
| [`docs/`](docs/README.md) | Theory, implementation, debugging, production guidance, benchmarks, references, roadmap, glossary, and FAQ. |
| [`examples/`](examples/README.md) | Runnable platform and subsystem examples with wiring, build, output, validation, and failure-mode notes. |
| [`tests/`](tests/README.md) | Unit, integration, hardware, performance, and stress validation procedures. |
| [`diagrams/`](diagrams/README.md) | Editable architecture, timing, PCB, signal-flow, and state-machine diagrams. |
| [`assets/`](assets/README.md) | Measurement evidence, images, oscilloscope captures, logic-analyzer traces, thermal records, PCB assets, and photos. |
| [`firmware/`](firmware/) | Firmware implementation artifacts. |
| [`hardware/`](hardware/README.md) | Hardware notes, board interfaces, power trees, sensor wiring, and production hardware constraints. |
| [`projects/`](projects/README.md) | Complete project assemblies that combine firmware, hardware, validation, and documentation. |
| [`scripts/`](scripts/) | Repository automation and validation tools. |

## Development Workflow

1. Start from an engineering task and preserve its `TASK`, `CAUSATION`, `CONVERGENCE PROOF`, `STATE TOPOLOGY`, `CODE`, and `PASS CRITERIA` fields.
2. Implement the smallest production-relevant change.
3. Update the feature learning document and the relevant repository-level docs.
4. Add or update examples, validation procedures, diagrams, and assets when the change affects behavior or observability.
5. Run documentation validation with `./scripts/validate_engineering_docs.sh`.
6. Record benchmark methodology before claiming performance improvements.
7. Commit implementation and documentation together.

## Documentation Index

| Document | Purpose |
| --- | --- |
| [`docs/README.md`](docs/README.md) | Documentation hierarchy and navigation. |
| [`docs/theory.md`](docs/theory.md) | Principles, math, physics, trade-offs, and industry practices. |
| [`docs/implementation.md`](docs/implementation.md) | Architecture, APIs, configuration, components, state machines, and data flow. |
| [`docs/debugging.md`](docs/debugging.md) | Common failures, oscilloscope and logic-analyzer workflows, UART, GDB/OpenOCD, recovery, and root cause. |
| [`docs/production.md`](docs/production.md) | Manufacturing, reliability, OTA, calibration, EMC, thermal, security, and certification. |
| [`docs/benchmarks.md`](docs/benchmarks.md) | RAM, flash, CPU, timing, latency, throughput, power, boot, sampling, and network records. |
| [`docs/references.md`](docs/references.md) | Categorized primary references: official docs, datasheets, standards, books, and papers. |
| [`docs/roadmap.md`](docs/roadmap.md) | Repository roadmap and documentation maturity plan. |
| [`docs/glossary.md`](docs/glossary.md) | Terms and abbreviations. |
| [`docs/faq.md`](docs/faq.md) | Frequently asked engineering and repository questions. |

## Contribution Guide

Contributions should be reviewable as engineering changes, not only code changes. A complete contribution answers:

- What problem is solved?
- Why is this approach chosen?
- Why do alternatives fail?
- How is correctness validated?
- What are the production risks?
- Which standards, datasheets, or official references support the design?

## Task System

Tasks are preserved as traceability artifacts. A task captures design intent before implementation and must be linked to the resulting documentation, examples, tests, diagrams, and validation evidence. Future tasks should update [`docs/documentation_generation.md`](docs/documentation_generation.md) when the documentation generation rules evolve.

## Repository Roadmap

Near-term roadmap:

- Expand ESP32 feature documents for every firmware module.
- Add independently buildable ESP32 examples for ADC DMA, FreeRTOS, MQTT, OTA, deep sleep, I2C recovery, and timers.
- Add hardware validation procedures with oscilloscope and logic-analyzer capture templates.
- Add benchmark records for timing jitter, RAM, flash, CPU load, throughput, power, boot time, sampling accuracy, and network behavior.
- Add editable diagrams for boot flow, ADC pipeline, task topology, MQTT state machine, OTA lifecycle, memory layout, interrupt flow, DMA pipeline, power architecture, and signal path.

## License

This repository is licensed under the terms in [`LICENSE`](LICENSE).

## References

Primary references are maintained in [`docs/references.md`](docs/references.md). The repository prioritizes official vendor documentation, datasheets, standards, academic references, and books over blog-first references.
.
