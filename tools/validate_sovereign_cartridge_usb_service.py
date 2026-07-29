#!/usr/bin/env python3
"""Validate the Task 5 Sovereign Cartridge USB-C service contract.

This standard-library check verifies the electrical role, connector and
protection candidates, power/descriptor limits, exclusive service boundary,
physical-only recovery, evidence language and host policy implementation. It
does not claim native ERC, target USB firmware or physical USB compliance.
"""

from __future__ import annotations

import argparse
import copy
import csv
import json
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
PLATFORM = ROOT / "hardware/platforms/sovereign_cartridge_proto0"
USB = PLATFORM / "usb"
CONTRACT = USB / "usb-service.json"
COMPONENTS = USB / "component-policy.csv"
README = USB / "README.md"
ASSUMPTIONS = USB / "assumptions.md"
DIAGRAM = USB / "usb-service.svg"
CHECKLIST = USB / "validation/task-05-checklist.md"
TOPOLOGY = PLATFORM / "topology.json"
SCHEMATIC = PLATFORM / "schematics/schematic.json"
POWER = PLATFORM / "power/power-safety.json"
SERVICE_HEADER = ROOT / "firmware/usb/include/usb/usb_service.h"
SERVICE_SOURCE = ROOT / "firmware/usb/usb_service.c"
HOST_TEST = ROOT / "firmware/usb/tests/host/test_usb_service_negative.c"
USB_CMAKE = ROOT / "firmware/usb/CMakeLists.txt"
ROOT_CMAKE = ROOT / "CMakeLists.txt"

ALLOWED_SOURCE_HOSTS = {
    "www.usb.org",
    "pip.raspberrypi.com",
    "gct.co",
    "www.ti.com",
    "github.com",
}
REQUIRED_STATES = {
    "DETACHED",
    "ATTACHED_DEFAULT",
    "ENUMERATING",
    "CONFIGURED",
    "SERVICE_READY",
    "SUSPENDED",
    "RECOVERY",
    "FAULT_LOCKED",
}
REQUIRED_HEADINGS = {
    "## FACT",
    "## DECISION",
    "## EXPECTED",
    "## MEASURED",
    "## UNKNOWN",
}
REQUIRED_HOST_CASES = {
    "REJECT_INCOMPLETE_ADAPTER",
    "REJECT_CONFIGURATION_BEFORE_ATTACH",
    "REJECT_UNSUPPORTED_CONFIGURATION",
    "REJECT_STORAGE_BEFORE_SERVICE_READY",
    "REJECT_MUTATION_WITHOUT_CONFIGURED_CURRENT",
    "REJECT_MUTATION_WHEN_POWER_UNSAFE",
    "REJECT_STORAGE_WHILE_SUSPENDED",
    "REJECT_REMOTE_RECOVERY",
    "BUS_RESET_DROPS_SERVICE_READY",
    "DETACH_DROPS_SERVICE_READY",
    "REJECT_UNDECLARED_ENDPOINT",
    "PROPAGATE_STORAGE_REJECTION_WITHOUT_RETRY",
    "FAULT_LOCK_REJECTS_TRAFFIC",
}
COMPONENT_COLUMNS = [
    "logical_reference",
    "role",
    "manufacturer",
    "manufacturer_part_number",
    "package_or_value",
    "quantity",
    "status",
    "source_url",
    "placement_or_policy",
    "procurement_gate",
]


def expect(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def close(actual: float, expected: float, tolerance: float = 1e-5) -> bool:
    return math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    return value


def validate_contract(data: dict, strict: bool = False) -> list[str]:
    errors: list[str] = []
    expect(data.get("schema_version") == 1, "schema_version must be 1", errors)
    expect(
        data.get("usb_service_id") == "sovereign-cartridge-proto0-task-05",
        "usb_service_id drifted",
        errors,
    )
    expect(data.get("product") == "Sovereign Cartridge", "product drifted", errors)
    expect(data.get("revision") == "PROTO-0", "revision drifted", errors)
    expect(
        data.get("status") == "USB_SERVICE_DESIGN_IN_PROGRESS",
        "Task 5 status must remain in progress",
        errors,
    )
    expect(
        data.get("evidence_status") == "DESIGN_ONLY",
        "evidence_status must remain DESIGN_ONLY",
        errors,
    )
    expect(
        data.get("phase_gate_passed") is False,
        "Task 5 phase gate must remain false",
        errors,
    )
    expect(
        data.get("invariant")
        == "Never expose incomplete or corrupted data as valid committed data.",
        "data-integrity invariant drifted",
        errors,
    )

    electrical = data.get("electrical_contract", {})
    connector = electrical.get("connector", {})
    expect(connector.get("reference") == "J1", "connector reference drifted", errors)
    expect(
        connector.get("manufacturer") == "GCT",
        "connector manufacturer drifted",
        errors,
    )
    expect(
        connector.get("part") == "USB4105-GF-A-120",
        "exact connector variant drifted",
        errors,
    )
    expect(
        connector.get("contact_count") == 16,
        "connector must remain USB2-only 16-contact",
        errors,
    )
    expect(
        connector.get("procurement_status")
        == "DESIGN_CANDIDATE_TASK_06_RELEASE_REQUIRED",
        "Task 5 cannot authorize procurement",
        errors,
    )

    roles = electrical.get("roles", {})
    expect(roles.get("data_role") == "UFP_DEVICE", "USB must remain device", errors)
    expect(roles.get("power_role") == "SINK", "USB must remain sink-only", errors)
    for key in (
        "host_enabled",
        "source_enabled",
        "power_delivery_enabled",
        "vconn_enabled",
    ):
        expect(roles.get(key) is False, f"{key} must remain false", errors)

    cc = electrical.get("configuration_channel", {})
    expect(cc.get("cc1_rd_ohms") == 5100, "CC1 Rd must be 5.1 kohm", errors)
    expect(cc.get("cc2_rd_ohms") == 5100, "CC2 Rd must be 5.1 kohm", errors)
    expect(
        cc.get("resistor_tolerance_percent") == 1,
        "CC Rd tolerance must be 1 percent",
        errors,
    )
    expect(
        cc.get("cc_pins_tied_together") is False,
        "CC1 and CC2 must never be tied together",
        errors,
    )
    expect(cc.get("controller_present") is False, "CC controller is out of scope", errors)

    usb2 = electrical.get("usb2_data", {})
    expect(usb2.get("speed") == "FULL_SPEED_12_MBPS", "USB speed drifted", errors)
    expect(
        set(usb2.get("connector_dp_pins", [])) == {"A6", "B6"},
        "D+ connector pins drifted",
        errors,
    )
    expect(
        set(usb2.get("connector_dm_pins", [])) == {"A7", "B7"},
        "D- connector pins drifted",
        errors,
    )
    expect(
        usb2.get("same_polarity_pins_joined_near_connector") is True,
        "same-polarity USB2 pins must join near J1",
        errors,
    )
    expect(
        usb2.get("differential_impedance_target_ohms") == 90,
        "USB pair target must be 90 ohms differential",
        errors,
    )
    expect(
        usb2.get("continuous_ground_reference_required") is True,
        "USB pair requires continuous ground reference",
        errors,
    )
    expect(
        usb2.get("series_resistor_ohms_per_line") == 27,
        "USB series resistors must remain 27 ohms",
        errors,
    )
    expect(
        usb2.get("unused_sbu_policy") == "NO_CONNECT",
        "SBU pins must remain no-connect",
        errors,
    )

    protection = electrical.get("protection", {})
    data_esd = protection.get("data_esd", {})
    expect(
        data_esd.get("part") == "TPD2EUSB30DRTR",
        "USB data ESD candidate drifted",
        errors,
    )
    expect(data_esd.get("channel_count") == 2, "data ESD needs two channels", errors)
    expect(
        float(data_esd.get("typical_io_capacitance_pf", 99)) <= 1.0,
        "data ESD capacitance must remain at or below 1 pF typical",
        errors,
    )
    expect(
        protection.get("vbus_esd", {}).get("part") == "TPD1E10B06DPYR",
        "VBUS ESD candidate drifted",
        errors,
    )
    expect(
        protection.get("shield", {}).get("default_connection")
        == "DIRECT_LOW_INDUCTANCE_TO_BOARD_GND",
        "shield return policy drifted",
        errors,
    )

    power = data.get("power_contract", {})
    preconfiguration_ma = int(power.get("pre_configuration_target_ma", -1))
    configuration_ma = int(power.get("configuration_max_power_ma", -1))
    bmax_units = int(power.get("configuration_descriptor_bMaxPower_units", -1))
    expect(preconfiguration_ma == 100, "pre-configuration target must be 100 mA", errors)
    expect(configuration_ma == 300, "configuration declaration must be 300 mA", errors)
    expect(
        bmax_units * 2 == configuration_ma,
        "bMaxPower units must encode the declared current exactly",
        errors,
    )
    expect(
        configuration_ma <= int(power.get("usb2_configured_ceiling_ma", -1)),
        "configuration declaration exceeds USB2 configured ceiling",
        errors,
    )
    expect(
        power.get("task_03_3v3_design_ceiling_ma") == 300,
        "Task 3 rail ceiling handoff drifted",
        errors,
    )
    expect(
        close(
            float(power.get("task_03_efuse_operating_limit_nominal_ma", 0)),
            296.667,
        ),
        "Task 3 eFuse nominal handoff drifted",
        errors,
    )
    expect(
        power.get("remote_wakeup_enabled") is False,
        "remote wakeup must remain disabled",
        errors,
    )
    for key in ("suspend_current_status", "attach_inrush_status"):
        expect(
            power.get(key) == "UNKNOWN_REQUIRES_BENCH",
            f"{key} must remain unmeasured",
            errors,
        )

    descriptor = data.get("descriptor_contract", {})
    expect(
        descriptor.get("endpoint_zero_max_packet_bytes") == 64,
        "EP0 packet size drifted",
        errors,
    )
    expect(
        descriptor.get("configuration_count") == 1
        and descriptor.get("configuration_value") == 1,
        "exactly configuration 1 must be exposed",
        errors,
    )
    interfaces = descriptor.get("interface_set", [])
    expect(len(interfaces) == 1, "exactly one USB function is allowed", errors)
    cdc = interfaces[0] if len(interfaces) == 1 else {}
    expect(cdc.get("function") == "CDC_ACM", "normal function must be CDC-ACM", errors)
    expect(
        (cdc.get("notification_endpoint"), cdc.get("data_out_endpoint"), cdc.get("data_in_endpoint"))
        == ("0x81", "0x02", "0x82"),
        "CDC endpoint set drifted",
        errors,
    )
    expect(cdc.get("bulk_max_packet_bytes") == 64, "CDC bulk packet size drifted", errors)
    for key in (
        "mass_storage_exposed",
        "hid_exposed",
        "vendor_bulk_exposed",
        "dfu_runtime_exposed",
    ):
        expect(descriptor.get(key) is False, f"{key} must remain false", errors)
    expect(
        descriptor.get("vid_pid_status") == "UNASSIGNED_BLOCKING_RELEASE",
        "VID/PID must not be invented",
        errors,
    )

    service = data.get("service_contract", {})
    expect(set(service.get("states", [])) == REQUIRED_STATES, "state set drifted", errors)
    expect(service.get("owner") == "USB_SERVICE_TASK", "USB owner drifted", errors)
    expect(
        service.get("isr_policy")
        == "POST_EVENTS_ONLY_NO_STORAGE_OR_PROTOCOL_EXECUTION",
        "ISR boundary drifted",
        errors,
    )
    storage = service.get("storage_boundary", {})
    expect(
        storage.get("only_target") == "PAYLOAD_STORAGE_SERVICE",
        "USB storage target drifted",
        errors,
    )
    for key in (
        "typed_requests_only",
        "new_requests_require_service_ready",
        "mutations_require_power_safe",
        "mass_storage_bypass_prohibited",
    ):
        expect(storage.get(key) is True, f"storage rule {key} must remain true", errors)
    for key in ("direct_spi_access", "automatic_mutation_replay"):
        expect(storage.get(key) is False, f"storage rule {key} must remain false", errors)
    diagnostics = service.get("diagnostics", {})
    expect(
        diagnostics.get("payload_bytes_logged") is False,
        "payload bytes must not be logged",
        errors,
    )
    expect(
        diagnostics.get("plaintext_mixed_with_protocol_frames") is False,
        "plaintext must not corrupt framed service traffic",
        errors,
    )

    recovery = data.get("recovery_contract", {})
    for key in (
        "normal_configuration_exposes_firmware_update",
        "remote_reboot_to_rom_bootloader_allowed",
    ):
        expect(recovery.get(key) is False, f"recovery rule {key} must remain false", errors)
    expect(recovery.get("physical_bootsel_allowed") is True, "BOOTSEL recovery required", errors)
    expect(recovery.get("swd_allowed") is True, "SWD recovery required", errors)

    suite = data.get("host_negative_suite", {})
    expect(
        set(suite.get("required_cases", [])) == REQUIRED_HOST_CASES,
        "negative host case set drifted",
        errors,
    )

    claims = data.get("evidence_claims", {})
    for status in ("FACT", "DECISION", "EXPECTED", "MEASURED", "UNKNOWN"):
        expect(bool(claims.get(status)), f"missing {status} evidence statement", errors)
    expect(claims.get("MEASURED") == "NONE", "Task 5 cannot claim measurements", errors)
    expect(
        len(data.get("blocking_validation", [])) >= 10,
        "Task 5 blocking validation is incomplete",
        errors,
    )

    sources = data.get("sources", [])
    expect(len(sources) >= 8, "at least eight primary sources are required", errors)
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            errors.append(f"sources[{index}] must be an object")
            continue
        parsed = urlparse(source.get("url", ""))
        expect(parsed.scheme == "https", f"sources[{index}] must use HTTPS", errors)
        if strict:
            expect(
                parsed.hostname in ALLOWED_SOURCE_HOSTS,
                f"sources[{index}] host is not approved: {parsed.hostname}",
                errors,
            )
        expect(
            source.get("retrieved") == "2026-07-29",
            f"sources[{index}] retrieval date drifted",
            errors,
        )
        expect(bool(source.get("supports")), f"sources[{index}] lacks scope", errors)
    return errors


def validate_artifacts() -> list[str]:
    errors: list[str] = []
    topology = read_json(TOPOLOGY)
    topology_usb = topology.get("interfaces", {}).get("usb_service", {})
    expect(topology_usb.get("data_role") == "UFP_DEVICE", "Task 1 USB role drifted", errors)
    expect(topology_usb.get("power_role") == "SINK", "Task 1 power role drifted", errors)
    for key in ("host_enabled", "source_enabled", "power_delivery_enabled"):
        expect(topology_usb.get(key) is False, f"Task 1 {key} drifted", errors)
    expect(
        topology.get("phase_gates", {}).get("task_05_usb_service_passed") is False,
        "Task 5 topology gate must remain false",
        errors,
    )

    schematic = read_json(SCHEMATIC)
    usb_connection = next(
        (
            item
            for item in schematic.get("controller", {}).get(
                "infrastructure_connections",
                [],
            )
            if item.get("pin_name") == "USB_DM_USB_DP"
        ),
        {},
    )
    expect(
        usb_connection.get("pins") == ["51", "52"],
        "Task 2 USB controller pins drifted",
        errors,
    )
    expect(
        "27 ohm" in usb_connection.get("support", ""),
        "Task 2 USB series-resistor handoff missing",
        errors,
    )
    j1 = next(
        (
            item
            for item in schematic.get("deferred_placeholders", [])
            if item.get("reference") == "J1"
        ),
        {},
    )
    expect(
        j1.get("dnp") is True and j1.get("owner_task") == 5,
        "J1 must remain a Task 5 DNP until editable capture",
        errors,
    )

    power = read_json(POWER)
    input_contract = power.get("input_contract", {})
    expect(
        input_contract.get("pre_configuration_target_ma") == 100,
        "Task 3 pre-configuration handoff drifted",
        errors,
    )
    expect(
        input_contract.get("configured_input_ceiling_ma") == 500,
        "Task 3 configured input ceiling drifted",
        errors,
    )
    expect(
        power.get("regulator", {}).get("design_output_ceiling_ma") == 300,
        "Task 3 rail ceiling drifted",
        errors,
    )
    expect(
        close(
            float(
                power.get("protection", {})
                .get("current_limit", {})
                .get("operating_mode_nominal_a", 0)
            ),
            0.296667,
        ),
        "Task 3 eFuse limit drifted",
        errors,
    )

    with COMPONENTS.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        expect(reader.fieldnames == COMPONENT_COLUMNS, "component columns drifted", errors)
        rows = {row["logical_reference"]: row for row in reader}
    expect(
        set(rows) == {"J1", "CC1_RD", "CC2_RD", "D_USB", "D_VBUS"},
        "component policy row set drifted",
        errors,
    )
    expect(
        rows.get("J1", {}).get("manufacturer_part_number") == "USB4105-GF-A-120",
        "component policy connector drifted",
        errors,
    )
    expect(
        rows.get("D_USB", {}).get("manufacturer_part_number")
        == "TPD2EUSB30DRTR",
        "component policy data ESD drifted",
        errors,
    )
    expect(
        rows.get("D_VBUS", {}).get("manufacturer_part_number")
        == "TPD1E10B06DPYR",
        "component policy VBUS ESD drifted",
        errors,
    )
    for logical_reference, row in rows.items():
        expect(
            row.get("procurement_gate", "").startswith("TASK_06_"),
            f"{logical_reference} lacks Task 6 procurement gate",
            errors,
        )

    ET.parse(DIAGRAM)
    diagram_text = DIAGRAM.read_text(encoding="utf-8")
    for token in (
        "DESIGN ONLY",
        "USB4105-GF-A-120",
        "5.1k",
        "TPD2EUSB30",
        "PAYLOAD_STORAGE_SERVICE",
    ):
        expect(token in diagram_text, f"USB diagram missing {token}", errors)

    assumptions = ASSUMPTIONS.read_text(encoding="utf-8")
    for heading in REQUIRED_HEADINGS:
        expect(heading in assumptions, f"assumptions missing {heading}", errors)
    expect("`NONE`" in assumptions, "assumptions must state no measurements", errors)

    readme = README.read_text(encoding="utf-8")
    checklist = CHECKLIST.read_text(encoding="utf-8")
    expect(
        "USB_SERVICE_DESIGN_IN_PROGRESS" in readme,
        "README must state open design status",
        errors,
    )
    expect(
        "`task_05_usb_service_passed` remains false" in checklist,
        "checklist must preserve the open gate",
        errors,
    )

    header = SERVICE_HEADER.read_text(encoding="utf-8")
    source = SERVICE_SOURCE.read_text(encoding="utf-8")
    host_test = HOST_TEST.read_text(encoding="utf-8")
    usb_cmake = USB_CMAKE.read_text(encoding="utf-8")
    root_cmake = ROOT_CMAKE.read_text(encoding="utf-8")
    for token in (
        "USB_SERVICE_PRECONFIGURATION_TARGET_MA 100u",
        "USB_SERVICE_CONFIGURATION_MAX_POWER_MA 300u",
        "USB_SERVICE_READY",
        "usb_service_submit_storage",
        "usb_service_request_recovery",
    ):
        expect(token in header, f"USB service header missing {token}", errors)
    for token in (
        "configured_current_available",
        "power_safe",
        "USB_SERVICE_E_REMOTE_RECOVERY_FORBIDDEN",
        "PAYLOAD_STORAGE_PROGRAM_PAGE",
        "PAYLOAD_STORAGE_ERASE_SECTOR",
        "PAYLOAD_STORAGE_ERASE_BLOCK_64K",
    ):
        expect(token in source, f"USB service source missing {token}", errors)
    for case in REQUIRED_HOST_CASES:
        test_name = "test_" + case.lower()
        expect(test_name in host_test, f"host suite missing {test_name}", errors)
    expect(
        "usb_service_host_tests" in usb_cmake,
        "USB host suite is not registered",
        errors,
    )
    expect(
        "add_subdirectory(firmware/usb)" in root_cmake,
        "USB firmware directory is not in the host build",
        errors,
    )
    return errors


def negative_self_tests(data: dict, strict: bool) -> list[str]:
    failures: list[str] = []
    cases: list[tuple[str, dict]] = []

    def mutated(label: str) -> dict:
        value = copy.deepcopy(data)
        cases.append((label, value))
        return value

    value = mutated("reject tied CC pins")
    value["electrical_contract"]["configuration_channel"]["cc_pins_tied_together"] = True
    value = mutated("reject source role")
    value["electrical_contract"]["roles"]["source_enabled"] = True
    value = mutated("reject Power Delivery")
    value["electrical_contract"]["roles"]["power_delivery_enabled"] = True
    value = mutated("reject descriptor arithmetic drift")
    value["power_contract"]["configuration_descriptor_bMaxPower_units"] = 151
    value = mutated("reject excessive configured current")
    value["power_contract"]["configuration_max_power_ma"] = 600
    value = mutated("reject mass storage")
    value["descriptor_contract"]["mass_storage_exposed"] = True
    value = mutated("reject runtime DFU")
    value["descriptor_contract"]["dfu_runtime_exposed"] = True
    value = mutated("reject direct SPI access")
    value["service_contract"]["storage_boundary"]["direct_spi_access"] = True
    value = mutated("reject mutation replay")
    value["service_contract"]["storage_boundary"]["automatic_mutation_replay"] = True
    value = mutated("reject remote bootloader")
    value["recovery_contract"]["remote_reboot_to_rom_bootloader_allowed"] = True
    value = mutated("reject measured claim")
    value["evidence_claims"]["MEASURED"] = "ENUMERATION_PASSED"
    value = mutated("reject closed physical gate")
    value["phase_gate_passed"] = True
    value = mutated("reject missing negative case")
    value["host_negative_suite"]["required_cases"].pop()

    for label, candidate in cases:
        if not validate_contract(candidate, strict=strict):
            failures.append(f"negative self-test failed: {label}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("contract", nargs="?", type=Path, default=CONTRACT)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        data = read_json(args.contract)
        errors = validate_contract(data, strict=args.strict)
        if args.contract.resolve() == CONTRACT.resolve():
            errors.extend(validate_artifacts())
        if args.self_test:
            errors.extend(negative_self_tests(data, strict=args.strict))
    except (OSError, ValueError, json.JSONDecodeError, ET.ParseError) as exc:
        print(exc)
        return 1

    if errors:
        print("\n".join(f"ERROR: {item}" for item in errors))
        return 1
    print(
        "Sovereign Cartridge USB service validation passed: "
        "USB2 UFP/sink, CDC-ACM, physical recovery, DESIGN_ONLY"
    )
    if args.self_test:
        print("negative self-tests passed: 13")
    return 0


if __name__ == "__main__":
    sys.exit(main())
