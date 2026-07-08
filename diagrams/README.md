# Diagrams

Diagrams preserve architecture and timing knowledge in reviewable form.

| Directory | Diagram type |
| --- | --- |
| `architecture/` | System and subsystem block diagrams. |
| `state_machine/` | Boot, recovery, OTA, telemetry, and fault state machines. |
| `data_flow/` | Sensor, DMA, queues, telemetry, storage, and cloud data paths. |
| `timing/` | Sampling, ISR, task, bus, and power timing diagrams. |
| `pcb/` | Board-level topology, connector maps, power trees, and layout notes. |

Use consistent names such as `<feature>_architecture.md`, `<feature>_state_machine.md`, and `<feature>_timing.md`.
