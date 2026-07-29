# Task 5 Evidence Status

Retrieval date: 2026-07-29  
Physical execution: not performed

## FACT

- A sink-only USB-C receptacle requires independent pull-down terminations on
  CC1 and CC2. Proto-0 has no reason to advertise source current or negotiate
  USB Power Delivery.
- RP2350's USB 2.0 PHY uses 27 ohm series resistors close to the controller.
  Raspberry Pi's hardware guidance calls for a 90 ohm differential pair over
  a continuous ground reference.
- The selected GCT receptacle exposes the USB 2.0 pins without SuperSpeed
  pairs. The selected TI data protector is a two-channel, low-capacitance
  device; the VBUS protector is rated for a 5.5 V working voltage.
- USB configuration power is declared in 2 mA units. A 300 mA declaration is
  therefore encoded as `bMaxPower = 150`.

## DECISION

- Proto-0 is bus-powered, USB 2.0 full-speed, UFP/device and sink only.
  CC1 and CC2 each use a separate 5.1 kohm, 1% pull-down to ground.
- The normal service personality exposes CDC-ACM only. It does not expose
  mass storage, HID, vendor bulk, WebUSB or runtime DFU.
- The device targets at most 100 mA before configuration and declares 300 mA
  after configuration. Task 3 still provides the absolute 500 mA configured
  ceiling and the 300 mA 3V3 engineering allocation.
- One `USB_SERVICE_TASK` owns stack/event processing. Interrupts only post
  events. USB clients can reach payload storage only through typed
  `PAYLOAD_STORAGE_SERVICE` requests.
- Storage requests require `SERVICE_READY`. Mutations additionally require
  configured-current qualification and Task 3 power-safe state.
- Normal USB traffic cannot reboot into the ROM bootloader. Recovery remains
  physical BOOTSEL/RUN or SWD until a signed update policy exists.

## EXPECTED

- CDC-ACM is expected to provide a low-complexity development service path
  without granting a host block-level access that could bypass future commit
  and recovery semantics.
- A 300 mA configuration declaration is expected to cover the Task 3
  worst-case input calculation while remaining below the USB 2.0 500 mA
  configured ceiling.
- Independent CC pull-downs are expected to attach correctly in either plug
  orientation.

Expected statements are design predictions, not USB compliance or bench
evidence.

## MEASURED

`NONE`.

No enumeration, descriptor, current, inrush, suspend, waveform, impedance,
ESD, EMC, host-compatibility, detach, reset or recovery behavior has been
measured.

## UNKNOWN

- Exact assembled-board draw before configuration, when configured and while
  suspended.
- Effective eFuse current-limit tolerance and margin over every operating
  mode.
- Connector footprint correctness, shell return inductance, protection
  parasitics and final differential-pair geometry.
- Enumeration and CDC behavior on supported Windows, macOS and Linux hosts.
- Behavior during detach, reset and suspend at every storage operation phase.
- Production VID/PID, serial-number format and signed-update policy.
- Every physical result.

## Gate

Task 5 remains open. The electrical and service contract, policy owner and
negative host suite provide design and software evidence only. Editable
schematic capture, target-stack binding, descriptor regression, physical
current/waveform evidence and Task 6 procurement review remain blocking.
