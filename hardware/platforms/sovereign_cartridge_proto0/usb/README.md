# Task 5 USB-C Service

Status: `USB_SERVICE_DESIGN_IN_PROGRESS`.

This directory freezes the first reviewable USB-C electrical, descriptor,
power, ownership and recovery contract for Sovereign Cartridge Proto-0. It
also includes a transport-independent C policy owner and negative host suite.
It does not close Task 5: editable KiCad capture, target USB-stack binding,
descriptor snapshots and physical USB evidence remain open.

## Frozen boundary

| Area | Proto-0 decision |
| --- | --- |
| Connector | GCT `USB4105-GF-A-120`, USB 2.0-only Type-C receptacle candidate |
| Roles | UFP/device and sink only; no host, source, VCONN or PD |
| CC | Independent 5.1 kohm, 1% Rd from CC1 and CC2 to GND |
| Data | Full speed; 27 ohm per line at RP2354A; 90 ohm differential target |
| Protection | `TPD2EUSB30DRTR` on D+/D- and `TPD1E10B06DPYR` on VBUS |
| Power | <=100 mA before configuration; 300 mA configuration declaration |
| Service | One CDC-ACM function; no MSC, HID, vendor bulk or runtime DFU |
| Recovery | Physical BOOTSEL/RUN or SWD only |
| Owner | One `USB_SERVICE_TASK`; ISR posts events only |
| Storage | Typed requests to `PAYLOAD_STORAGE_SERVICE` only |

The 300 mA descriptor is a maximum input declaration, not a measured draw.
Task 3's 300 mA rail allocation corresponds to a lower calculated VBUS input
current after conversion loss, but eFuse tolerance and actual current still
require bench validation.

## Data and protection path

The two connector D+ contacts join near J1, as do the two D- contacts. The
joined pair passes the low-capacitance ESD device, then the existing R7/R8
27-ohm series resistors placed close to RP2354A. SBU pins remain unconnected.
The shield returns directly to board ground with a short, stitched path.

VBUS ESD sits at the connector before the Task 3 eFuse. Protection placement
and routing must minimize the discharge path; a selected part alone is not
evidence of ESD performance.

## Service and recovery

The host-visible service is CDC-ACM because it preserves a framed,
transactional application boundary. USB mass storage is prohibited: exposing
the payload NOR as a host block device would bypass the single storage owner
and future immutable-object/commit semantics.

The policy owner accepts storage traffic only in `SERVICE_READY`. Mutations
also require configured-current qualification and a power-safe callback.
Reset, suspend and detach remove readiness, block new work and never turn an
unknown mutation outcome into success.

Normal USB traffic cannot enter the ROM bootloader. Until identity, protocol,
authorization and signed-update policy are designed, recovery requires a
physical BOOTSEL/RUN action or SWD.

## Artifacts

- [`usb-service.json`](usb-service.json) is the machine-readable contract.
- [`component-policy.csv`](component-policy.csv) records selected design
  candidates without authorizing procurement.
- [`assumptions.md`](assumptions.md) separates facts, decisions, expectations,
  measurements and unknowns.
- [`usb-service.svg`](usb-service.svg) shows the electrical and ownership
  boundary.
- [`validation/task-05-checklist.md`](validation/task-05-checklist.md) defines
  the open software and physical gate.

Validate with:

```sh
python3 tools/validate_sovereign_cartridge_usb_service.py --strict --self-test
cmake --preset host
cmake --build --preset host
ctest --preset host --output-on-failure
```

Do not set `task_05_usb_service_passed` until schematic, firmware, descriptor,
host-matrix, current, waveform, fault-injection and sourcing evidence pass.
