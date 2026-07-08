# Engineering Theory Knowledge Base

## Purpose

This document defines the theory layer for the electronics repository. It preserves the engineering reasoning behind firmware, hardware, validation, and production decisions so the repository functions as both a production codebase and an Embedded Systems Engineering Handbook.

## Repository Knowledge Model

Validation marker: `engineering_learning_repository_structure_v1`

Status: `ENGINEERING_KNOWLEDGE_BASE_STANDARDIZED`

```text
Engineering task
    ↓
Theory and first principles
    ↓
Implementation architecture
    ↓
Examples and validation
    ↓
Debugging and benchmarks
    ↓
Production guidance
    ↓
References and long-term knowledge preservation
```

The knowledge base separates concepts by responsibility instead of mixing all information into a single README. This reduces onboarding time, improves review quality, and makes each engineering decision traceable.

## Engineering Principles

Every feature document should explain the physical, mathematical, and architectural principles that make the implementation necessary:

| Principle | Required explanation |
| --- | --- |
| Physics | Sensor behavior, analog limits, noise, thermal drift, signal integrity, power integrity, EMC/EMI coupling. |
| Mathematics | Sampling, latency, queue depth, bandwidth, error budgets, timing bounds, reliability estimates. |
| Hardware | Peripheral ownership, electrical interfaces, ADC/I2C/SPI/UART behavior, memory and DMA constraints. |
| Firmware | Driver contracts, ISR rules, RTOS scheduling, watchdog policy, persistence, telemetry boundaries. |
| Production | Calibration, diagnostics, field update safety, manufacturing variation, observability, traceability. |

## Mathematical Reasoning Standard

Engineering claims should be tied to equations where possible. Examples include:

```text
Nyquist condition:       F_s > 2 · F_max
Sample period:          T_s = 1 / F_s
Queue residence time:   T_queue = Q_depth / event_rate
Throughput margin:      margin = consumer_rate - producer_rate
Average current:        I_avg = ((I_active · T_active) + (I_sleep · T_sleep)) / (T_active + T_sleep)
Timing validity:        deadline_met = C_exec + Jitter < T_period
```

Equations are not decorative; they define acceptance criteria and explain why a design fails or succeeds under load.

## Task-to-Documentation Rule

Every new engineering task must add or update the following documentation areas:

1. `docs/theory.md` for principles and design motivation.
2. `docs/implementation.md` for firmware and hardware architecture.
3. `docs/debugging.md` for failure diagnosis.
4. `docs/production.md` for deployment and field constraints.
5. `docs/benchmarks.md` for measurement methodology and reproducible results.
6. `docs/references.md` for primary sources.
7. `examples/` for runnable usage patterns when implementation code exists.
8. `tests/` for separated validation categories.
9. `diagrams/` for architecture, state, data-flow, timing, and PCB context.
10. `assets/` for supporting captures, measurements, images, and datasheets.

## Naive Documentation Failure Modes

| Naive approach | Failure mechanism |
| --- | --- |
| Put everything in `README.md` | Theory, debugging, production, examples, and validation become intermixed and hard to maintain. |
| Document only APIs | Contributors learn how to call code but not why the design is safe or how to validate it. |
| Keep measurements in issues | Benchmark context disappears from the repository history and cannot be reproduced. |
| Store diagrams ad hoc | Architecture knowledge becomes inconsistent and difficult to review. |
| Omit references | Designs cannot be audited against official datasheets, standards, or vendor guidance. |

## Required Feature Learning Document Shape

Feature-specific learning documents, such as ESP32 ADC/DMA material, should follow a complete teaching order:

```text
Title → Overview → Engineering Problem → Why Naive Approaches Fail
→ Engineering Principles → Mathematical Foundation → Hardware Architecture
→ Firmware Architecture → State Machine → Data Flow → ESP-IDF Components
→ Memory Model → RTOS Interaction → Performance Analysis → Design Trade-offs
→ Failure Modes → Debugging Strategy → Testing Methodology
→ Production Considerations → Related Topics → Implementation Task → Key Takeaways
```

This order teaches first principles before implementation details and preserves the original task as an engineering exercise.
