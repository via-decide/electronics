# Electronics From Zero Safety Boundary

## Allowed v1 energy boundary

- USB-powered ESP32 development board and a single 3.3 V project rail.
- Safe extra-low-voltage, current-bounded resistive or LED loads.
- Power removed before wiring, continuity or resistance measurements.
- Current mode is optional and used only after a separate fuse/jack/range check.

## Prohibited

Mains electricity, lithium-cell experiments, high-current short circuits, deliberate overheating,
reverse powering, operation beyond absolute maximum ratings, exposed inductive loads without
protection, unknown external supplies, and destructive NAND access outside an authorized scratch
range.

## Power-up gate

Supply measured; GND continuity confirmed; no VCC-GND short; common ground present; logic levels
compatible; polarity and orientation checked; current bounded; decoupling installed; test points
identified. A failed check blocks power-up.

## Measurement boundary

Put the black lead on project GND before probing with the red lead. Use insulated probe tips where
possible. Never change the meter into current mode while it remains connected across a voltage
source. Wire colour is not proof of a node.
