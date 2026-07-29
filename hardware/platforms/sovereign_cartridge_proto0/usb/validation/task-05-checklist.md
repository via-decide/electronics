# Task 5 USB-C Service Checklist

Status: `OPEN`.

## Repository contract

- [x] USB 2.0 full-speed UFP/device and sink-only roles are explicit.
- [x] The USB-C receptacle design candidate and exact mounting variant are
  selected.
- [x] Independent CC1/CC2 5.1 kohm pull-downs are explicit.
- [x] D+/D-, VBUS and shield protection/routing policies are explicit.
- [x] Pre-configuration and configured power limits cross-check Task 3.
- [x] The descriptor interface and endpoint set is bounded to CDC-ACM.
- [x] Mass storage, remote DFU, host/source, PD and VCONN are prohibited.
- [x] One USB task, ISR and payload-storage ownership boundaries are explicit.
- [x] Facts, decisions, expectations, measurements and unknowns are separated.

## Firmware proof

- [x] Implement a transport-independent USB service policy owner.
- [x] Reject invalid lifecycle transitions and unsupported configurations.
- [x] Reject storage traffic before service readiness and while suspended.
- [x] Gate mutations on configured current and Task 3 power-safe state.
- [x] Reject remote recovery and permit only an explicit physical origin.
- [x] Drop readiness on bus reset and detach.
- [x] Restrict traffic to the declared CDC endpoint set.
- [x] Propagate storage-owner rejection without automatic retry.
- [x] Add negative host tests for every rule above.
- [ ] Bind the owner to the RP2354A device controller and reviewed USB stack.
- [ ] Freeze generated descriptors and compare them byte-for-byte in CI.
- [ ] Allocate a production VID/PID and Task 7 serial-number source.

## Schematic and layout proof

- [ ] Replace the J1 Task 5 DNP placeholder in editable KiCad source.
- [ ] Capture both independent CC pull-downs and verify both cable
  orientations.
- [ ] Capture data and VBUS ESD with reviewed symbols and footprints.
- [ ] Run native KiCad ERC and independent connector pinout review.
- [ ] Route D+/D- to the 90 ohm differential target over continuous ground.
- [ ] Place R7/R8 close to RP2354A and ESD close to J1.
- [ ] Review shield return and ESD discharge paths.

## Physical evidence

- [ ] Measure attach inrush at both cable orientations.
- [ ] Measure pre-configuration input current at or below 100 mA.
- [ ] Measure configured draw at or below the 300 mA declaration.
- [ ] Measure suspend current against the applicable USB requirement.
- [ ] Capture enumeration and sustained-transfer D+/D- waveforms.
- [ ] Run reset, suspend, resume and detach on supported host operating
  systems.
- [ ] Inject reset, suspend and detach during each storage operation.
- [ ] Demonstrate physical BOOTSEL/RUN and SWD recovery.
- [ ] Complete Task 6 source, lifecycle, derating and footprint review.

## Gate rule

`task_05_usb_service_passed` remains false until every firmware, schematic,
layout and physical-evidence item above passes. Design artifacts and host
tests cannot close the gate.
