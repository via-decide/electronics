# Diagrams

Diagrams preserve architecture and timing knowledge in reviewable form. Prefer editable source formats such as Mermaid, draw.io XML, or SVG over only exported images.

| Directory | Diagram type |
| --- | --- |
| `architecture/` | System and subsystem block diagrams. |
| `timing/` | Sampling, ISR, task, bus, and power timing diagrams. |
| `pcb/` | Board-level topology, connector maps, power trees, and layout notes. |
| `signal-flow/` | Analog and data signal paths. |
| `signal_flow/` | Compatibility path for signal-flow diagrams using underscore naming. |
| `state-machines/` | Boot, recovery, OTA, telemetry, and fault state machines. |
| `state_machine/` | Compatibility path for state-machine diagrams using singular underscore naming. |
| `data_flow/` | Sensor, DMA, queues, telemetry, storage, and cloud data paths. |

Required diagram topics include boot flow, ADC pipeline, FreeRTOS task topology, MQTT state machine, OTA lifecycle, memory layout, interrupt flow, DMA pipeline, power architecture, and signal path.
