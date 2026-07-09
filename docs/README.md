# Documentation

The documentation tree is the primary learning interface for the repository. It separates first principles, implementation details, debugging, production, benchmarks, and references so engineers can move from theory to validation without searching through commits or issues.

## Hierarchy

| Document | Responsibility |
| --- | --- |
| `theory.md` | Engineering principles, mathematics, hardware limitations, trade-offs, and industry practices. |
| `implementation.md` | Architecture, APIs, configuration, component selection, design decisions, state machines, and data flow. |
| `debugging.md` | Common failures, instruments, UART logs, GDB/OpenOCD, recovery, and root-cause checklists. |
| `production.md` | Manufacturing, reliability, OTA, calibration, EMC, thermal design, security, and certification. |
| `benchmarks.md` | RAM, flash, CPU, timing, latency, throughput, power, boot time, sampling accuracy, and network performance. |
| `references.md` | Categorized primary sources: standards, datasheets, official docs, books, and papers. |
| `roadmap.md` | Documentation and engineering maturity roadmap. |
| `glossary.md` | Shared terms and abbreviations. |
| `faq.md` | Frequently asked repository and engineering questions. |

## Feature Documents

Feature-specific documents live below platform directories such as `docs/esp32/`. They should teach the engineering principles behind the implementation, preserve the original task, and link to examples, tests, diagrams, benchmarks, and references.
