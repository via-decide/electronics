#!/usr/bin/env python3
"""Validate the frozen Sovereign Cartridge Proto-0 topology.

The validator intentionally uses the Python standard library so the topology
gate runs before repository dependencies are installed.
"""

from __future__ import annotations

import argparse
import copy
import csv
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
PLATFORM = ROOT / "hardware/platforms/sovereign_cartridge_proto0"
DEFAULT_TOPOLOGY = PLATFORM / "topology.json"
SCHEMA = PLATFORM / "topology.schema.json"
BOM = PLATFORM / "bom/bom.csv"
ARCHITECTURE = PLATFORM / "architecture.svg"
ASSUMPTIONS = PLATFORM / "assumptions.md"

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "topology_id",
    "product",
    "revision",
    "status",
    "evidence_status",
    "invariant",
    "blocks",
    "connections",
    "power_domains",
    "interfaces",
    "required_test_nets",
    "physical_boundaries",
    "authorization",
    "phase_gates",
    "deferred_decisions",
    "sources",
}
REQUIRED_BLOCKS = {
    "service_port": ("usb_c_service", "DEFERRED_TO_TASK_05"),
    "input_power": ("power_conditioning", "DEFERRED_TO_TASK_03"),
    "controller": ("microcontroller", "RP2354A"),
    "boot_flash": ("boot_nor", "W25Q16JVWI_IN_PACKAGE"),
    "payload_flash": ("payload_nor", "W25Q256JVEIQ"),
    "debug_access": ("swd_debug", "SM03B-SRSS-TB"),
    "test_access": ("test_points", "FOOTPRINTS_DEFERRED_TO_TASK_02"),
}
REQUIRED_TEST_NETS = {
    "VBUS_5V",
    "3V3",
    "1V1",
    "GND",
    "RUN",
    "BOOTSEL_QSPI_SS",
    "SWDIO",
    "SWCLK",
    "USB_DP",
    "USB_DM",
    "PAYLOAD_SPI_SCK",
    "PAYLOAD_SPI_COPI",
    "PAYLOAD_SPI_CIPO",
    "PAYLOAD_SPI_CS_N",
}
ALLOWED_SOURCE_HOSTS = {
    "pip.raspberrypi.com",
    "www.raspberrypi.com",
    "www.winbond.com",
    "www.usb.org",
}
BOM_COLUMNS = [
    "item_id",
    "role",
    "manufacturer",
    "manufacturer_part_number",
    "package",
    "quantity",
    "freeze_status",
    "source_url",
    "selection_basis",
    "procurement_gate",
]
FROZEN_BOM = {
    "U1": "RP2354A A4",
    "U2": "W25Q256JVEIQ",
    "Y1": "ABM8-272-T3",
    "L1": "AOTA-B201610S3R3-101-T",
    "J2": "SM03B-SRSS-TB",
}
BLOCKED_BOM = {"J1", "U3", "U4"}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    return value


def by_id(items: object, label: str, errors: list[str]) -> dict[str, dict]:
    if not isinstance(items, list):
        errors.append(f"{label} must be an array")
        return {}
    result: dict[str, dict] = {}
    for index, item in enumerate(items):
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            errors.append(f"{label}[{index}] must be an object with a string id")
            continue
        if item["id"] in result:
            errors.append(f"{label} contains duplicate id {item['id']}")
        result[item["id"]] = item
    return result


def expect(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_contract(data: dict, strict: bool = False) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_TOP_LEVEL - set(data)
    expect(not missing, f"topology missing fields: {sorted(missing)}", errors)
    expect(data.get("schema_version") == 1, "schema_version must be 1", errors)
    expect(
        data.get("topology_id") == "sovereign-cartridge-proto0",
        "topology_id drifted",
        errors,
    )
    expect(data.get("product") == "Sovereign Cartridge", "product drifted", errors)
    expect(data.get("revision") == "PROTO-0", "revision must be PROTO-0", errors)
    expect(
        data.get("status") == "TOPOLOGY_FROZEN",
        "status must be TOPOLOGY_FROZEN",
        errors,
    )
    expect(
        data.get("evidence_status") == "DESIGN_ONLY",
        "evidence_status must remain DESIGN_ONLY",
        errors,
    )
    expect(
        data.get("invariant")
        == "Never expose incomplete or corrupted data as valid committed data.",
        "data-integrity invariant drifted",
        errors,
    )

    blocks = by_id(data.get("blocks"), "blocks", errors)
    for block_id, (block_type, part) in REQUIRED_BLOCKS.items():
        block = blocks.get(block_id, {})
        expect(bool(block), f"missing block {block_id}", errors)
        expect(block.get("type") == block_type, f"{block_id} type drifted", errors)
        expect(block.get("part") == part, f"{block_id} part drifted", errors)
    controller = blocks.get("controller", {})
    expect(
        controller.get("silicon_stepping") == "A4",
        "controller must require A4 stepping",
        errors,
    )
    expect(
        controller.get("package") == "QFN-60_7X7",
        "controller package must remain QFN-60 7x7",
        errors,
    )
    expect(
        blocks.get("boot_flash", {}).get("capacity_bytes") == 2 * 1024 * 1024,
        "boot flash must be 2 MiB",
        errors,
    )
    expect(
        blocks.get("payload_flash", {}).get("capacity_bytes") == 32 * 1024 * 1024,
        "payload flash must be 32 MiB",
        errors,
    )

    connections = data.get("connections")
    connection_set: set[tuple[str, str, str]] = set()
    if not isinstance(connections, list):
        errors.append("connections must be an array")
    else:
        for index, item in enumerate(connections):
            if not isinstance(item, dict):
                errors.append(f"connections[{index}] must be an object")
                continue
            edge = (item.get("from"), item.get("to"), item.get("kind"))
            if not all(isinstance(value, str) for value in edge):
                errors.append(f"connections[{index}] has invalid edge fields")
                continue
            connection_set.add(edge)  # type: ignore[arg-type]
            if edge[0] not in blocks or edge[1] not in blocks:
                errors.append(f"connection references unknown block: {edge}")
    for edge in {
        ("controller", "boot_flash", "IN_PACKAGE_QSPI"),
        ("controller", "payload_flash", "DEDICATED_USER_SPI"),
        ("service_port", "controller", "USB2_DP_DM"),
        ("service_port", "input_power", "VBUS_5V"),
    }:
        expect(edge in connection_set, f"missing frozen connection {edge}", errors)

    rails = by_id(data.get("power_domains"), "power_domains", errors)
    for rail_id, voltage in {"VBUS_5V": 5.0, "3V3": 3.3, "1V1": 1.1}.items():
        expect(rail_id in rails, f"missing rail {rail_id}", errors)
        expect(
            rails.get(rail_id, {}).get("nominal_voltage_v") == voltage,
            f"{rail_id} nominal voltage drifted",
            errors,
        )
    expect(
        rails.get("VBUS_5V", {}).get("current_budget") == "DEFERRED_TO_TASK_03",
        "Task 1 must not invent a current budget",
        errors,
    )

    interfaces = data.get("interfaces", {})
    if not isinstance(interfaces, dict):
        errors.append("interfaces must be an object")
        interfaces = {}
    usb = interfaces.get("usb_service", {})
    expect(usb.get("data_role") == "UFP_DEVICE", "USB must remain UFP/device", errors)
    expect(usb.get("power_role") == "SINK", "USB must remain sink-only", errors)
    for key in ("host_enabled", "source_enabled", "power_delivery_enabled"):
        expect(usb.get(key) is False, f"USB {key} must remain false", errors)
    spi = interfaces.get("payload_spi", {})
    expect(
        spi.get("physical_device") == "W25Q256JVEIQ",
        "payload SPI device drifted",
        errors,
    )
    expect(spi.get("xip_bus_shared") is False, "payload NOR must not share XIP", errors)
    expect(
        spi.get("pin_assignment") == "DEFERRED_TO_TASK_02",
        "Task 1 must not pre-empt schematic pin assignment",
        errors,
    )
    expect(
        spi.get("ownership_policy") == "DEFERRED_TO_TASK_04",
        "Task 1 must not pre-empt SPI ownership",
        errors,
    )

    test_nets = data.get("required_test_nets", [])
    expect(isinstance(test_nets, list), "required_test_nets must be an array", errors)
    if isinstance(test_nets, list):
        expect(
            len(test_nets) == len(set(test_nets)),
            "required_test_nets contains duplicates",
            errors,
        )
        expect(
            REQUIRED_TEST_NETS.issubset(set(test_nets)),
            f"missing test nets: {sorted(REQUIRED_TEST_NETS - set(test_nets))}",
            errors,
        )

    boundaries = data.get("physical_boundaries", {})
    expected_boundaries = {
        "single_board": True,
        "boot_and_payload_flash_are_separate_devices": True,
        "removable_flash_socket": False,
        "raw_nand_present": False,
        "fpga_present": False,
        "battery_present": False,
        "wireless_present": False,
    }
    for key, value in expected_boundaries.items():
        expect(boundaries.get(key) is value, f"physical boundary {key} drifted", errors)

    authorization = data.get("authorization", {})
    for key in (
        "real_hardware_enabled",
        "destructive_storage_writes_enabled",
        "manufacturing_release_enabled",
    ):
        expect(authorization.get(key) is False, f"{key} must remain false", errors)
    gates = data.get("phase_gates", {})
    expect(gates.get("task_01_topology_frozen") is True, "Task 1 gate must pass", errors)
    for key, value in gates.items():
        if key != "task_01_topology_frozen":
            expect(value is False, f"downstream gate {key} must remain false", errors)

    deferred = data.get("deferred_decisions", [])
    deferred_tasks = {
        item.get("task")
        for item in deferred
        if isinstance(item, dict) and isinstance(item.get("task"), int)
    }
    expect(
        {2, 3, 4, 5, 6}.issubset(deferred_tasks),
        "Tasks 2-6 must own downstream decisions",
        errors,
    )

    sources = data.get("sources", [])
    if not isinstance(sources, list) or len(sources) < 6:
        errors.append("at least six authoritative sources are required")
    else:
        for index, source in enumerate(sources):
            if not isinstance(source, dict):
                errors.append(f"sources[{index}] must be an object")
                continue
            url = source.get("url", "")
            parsed = urlparse(url)
            expect(parsed.scheme == "https", f"sources[{index}] must use HTTPS", errors)
            if strict:
                expect(
                    parsed.hostname in ALLOWED_SOURCE_HOSTS,
                    f"sources[{index}] is not an allowed primary host: {parsed.hostname}",
                    errors,
                )
            expect(bool(source.get("supports")), f"sources[{index}] lacks scope", errors)
            expect(
                source.get("retrieved_at") == "2026-07-25",
                f"sources[{index}] retrieval date drifted",
                errors,
            )
    return errors


def validate_artifacts() -> list[str]:
    errors: list[str] = []
    try:
        schema = load_json(SCHEMA)
        expect(
            schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema",
            "schema must declare draft 2020-12",
            errors,
        )
        expect(
            set(schema.get("required", [])) == REQUIRED_TOP_LEVEL,
            "schema required fields drifted from validator",
            errors,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(str(exc))

    try:
        ET.parse(ARCHITECTURE)
    except (OSError, ET.ParseError) as exc:
        errors.append(f"architecture SVG invalid: {exc}")

    try:
        with BOM.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            expect(reader.fieldnames == BOM_COLUMNS, "BOM columns drifted", errors)
            rows = {row["item_id"]: row for row in reader}
        for item_id, mpn in FROZEN_BOM.items():
            row = rows.get(item_id, {})
            expect(bool(row), f"BOM missing {item_id}", errors)
            expect(
                row.get("manufacturer_part_number") == mpn,
                f"BOM {item_id} MPN drifted",
                errors,
            )
            expect(row.get("freeze_status") == "FROZEN", f"BOM {item_id} not frozen", errors)
        for item_id in BLOCKED_BOM:
            row = rows.get(item_id, {})
            expect(bool(row), f"BOM missing deferred item {item_id}", errors)
            expect(
                row.get("freeze_status") == "BLOCKED",
                f"BOM {item_id} must remain blocked",
                errors,
            )
            expect(
                row.get("procurement_gate", "").startswith("DO_NOT_PURCHASE"),
                f"BOM {item_id} must prohibit premature purchase",
                errors,
            )
    except OSError as exc:
        errors.append(str(exc))

    try:
        ledger = ASSUMPTIONS.read_text(encoding="utf-8")
        for heading in ("## FACT", "## DECISION", "## EXPECTED", "## UNKNOWN / blocking"):
            expect(heading in ledger, f"assumption ledger missing {heading}", errors)
        expect("## MEASURED" not in ledger, "Task 1 must not claim measured results", errors)
        expect(
            "BENCH_VERIFIED`" in ledger,
            "ledger must state the BENCH_VERIFIED prohibition",
            errors,
        )
    except OSError as exc:
        errors.append(str(exc))
    return errors


def negative_self_tests(data: dict, strict: bool) -> list[str]:
    failures: list[str] = []
    cases: list[tuple[str, dict]] = []

    case = copy.deepcopy(data)
    case["blocks"][2]["silicon_stepping"] = "A2"
    cases.append(("reject A2 controller", case))

    case = copy.deepcopy(data)
    case["interfaces"]["usb_service"]["source_enabled"] = True
    cases.append(("reject USB source role", case))

    case = copy.deepcopy(data)
    case["interfaces"]["payload_spi"]["xip_bus_shared"] = True
    cases.append(("reject XIP sharing", case))

    case = copy.deepcopy(data)
    case["authorization"]["destructive_storage_writes_enabled"] = True
    cases.append(("reject destructive authorization", case))

    for label, candidate in cases:
        if not validate_contract(candidate, strict=strict):
            failures.append(f"negative self-test failed: {label}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("topology", nargs="?", type=Path, default=DEFAULT_TOPOLOGY)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        data = load_json(args.topology)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(exc)
        return 1

    errors = validate_contract(data, strict=args.strict)
    if args.topology.resolve() == DEFAULT_TOPOLOGY.resolve():
        errors.extend(validate_artifacts())
    if args.self_test:
        errors.extend(negative_self_tests(data, strict=args.strict))
    if errors:
        print("\n".join(f"ERROR: {item}" for item in errors))
        return 1
    print(
        "Sovereign Cartridge topology validation passed: "
        "PROTO-0, RP2354A A4, W25Q256JVEIQ, DESIGN_ONLY"
    )
    if args.self_test:
        print("negative self-tests passed: 4")
    return 0


if __name__ == "__main__":
    sys.exit(main())
