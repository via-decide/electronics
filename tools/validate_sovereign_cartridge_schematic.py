#!/usr/bin/env python3
"""Validate the Task 2 Sovereign Cartridge schematic contract.

This standard-library check is a repository structural ERC. It validates the
machine-readable contract, pin maps, evidence language, review rendering and
selected facts in the KiCad source. It does not replace native KiCad ERC.
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
SCHEMATICS = (
    ROOT / "hardware/platforms/sovereign_cartridge_proto0/schematics"
)
CONTRACT = SCHEMATICS / "schematic.json"
PINMAP = SCHEMATICS / "pinmap.csv"
TEST_ACCESS = SCHEMATICS / "test-access.csv"
ASSUMPTIONS = SCHEMATICS / "assumptions.md"
RENDERED = SCHEMATICS / "rendered-schematic.svg"
REPORT = SCHEMATICS / "erc-report.json"
KICAD = (
    SCHEMATICS
    / "kicad"
    / "sovereign_cartridge_proto0.kicad_sch"
)
SOURCE = SCHEMATICS / "kicad/SOURCE.md"

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
PAYLOAD_ASSIGNMENT = {
    "GPIO16": ("27", "SPI0_RX", "PAYLOAD_SPI_CIPO", "2"),
    "GPIO17": ("28", "SPI0_CSn", "PAYLOAD_SPI_CS_N", "1"),
    "GPIO18": ("29", "SPI0_SCK", "PAYLOAD_SPI_SCK", "6"),
    "GPIO19": ("31", "SPI0_TX", "PAYLOAD_SPI_COPI", "5"),
}
INFRASTRUCTURE_PINS = {
    "1",
    "6",
    "11",
    "20",
    "21",
    "22",
    "23",
    "24",
    "25",
    "26",
    "30",
    "38",
    "39",
    "44",
    "45",
    "46",
    "47",
    "48",
    "49",
    "50",
    "51",
    "52",
    "53",
    "54",
    "55",
    "56",
    "57",
    "58",
    "59",
    "60",
    "61",
}
ALLOWED_SOURCE_HOSTS = {
    "pip.raspberrypi.com",
    "pip-assets.raspberrypi.com",
    "www.winbond.com",
    "docs.kicad.org",
}


def expect(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    return value


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def balanced_sexpression(text: str) -> bool:
    """Return true when parentheses balance outside quoted KiCad strings."""

    depth = 0
    in_string = False
    escaped = False
    for character in text:
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
        elif character == '"':
            in_string = True
        elif character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0 and not in_string


def validate_contract(data: dict, strict: bool = False) -> list[str]:
    errors: list[str] = []
    expect(data.get("schema_version") == 1, "schema_version must be 1", errors)
    expect(
        data.get("schematic_id") == "sovereign-cartridge-proto0-task-02",
        "schematic_id drifted",
        errors,
    )
    expect(
        data.get("status") == "SCHEMATIC_CAPTURE_IN_PROGRESS",
        "Task 2 must remain in progress until native ERC passes",
        errors,
    )
    expect(
        data.get("evidence_status") == "DESIGN_ONLY",
        "evidence_status must remain DESIGN_ONLY",
        errors,
    )
    expect(
        data.get("phase_gate_passed") is False,
        "Task 2 phase gate must remain false",
        errors,
    )
    expect(
        data.get("invariant")
        == "Never expose incomplete or corrupted data as valid committed data.",
        "data-integrity invariant drifted",
        errors,
    )

    controller = data.get("controller", {})
    expect(controller.get("part") == "RP2354A", "controller part drifted", errors)
    expect(
        controller.get("silicon_stepping") == "A4",
        "controller stepping must be A4",
        errors,
    )
    expect(
        controller.get("package") == "QFN-60_7X7_EP",
        "controller package drifted",
        errors,
    )
    boot = controller.get("boot_flash", {})
    expect(boot.get("location") == "IN_PACKAGE", "boot flash must be in-package", errors)
    expect(
        boot.get("capacity_bytes") == 2 * 1024 * 1024,
        "boot flash must be 2 MiB",
        errors,
    )
    expect(
        boot.get("external_boot_nor_present") is False,
        "external boot NOR must remain absent",
        errors,
    )

    captured_infrastructure: set[str] = set()
    infrastructure = controller.get("infrastructure_connections", [])
    if not isinstance(infrastructure, list):
        errors.append("infrastructure_connections must be an array")
    else:
        for item in infrastructure:
            if not isinstance(item, dict):
                errors.append("infrastructure connection must be an object")
                continue
            captured_infrastructure.update(item.get("pins", []))
            expect(bool(item.get("net")), "infrastructure connection lacks net", errors)
            expect(
                bool(item.get("support")),
                "infrastructure connection lacks support circuit",
                errors,
            )
    expect(
        INFRASTRUCTURE_PINS.issubset(captured_infrastructure),
        f"missing infrastructure pins: {sorted(INFRASTRUCTURE_PINS - captured_infrastructure)}",
        errors,
    )

    payload = data.get("payload_spi", {})
    device = payload.get("device", {})
    expect(
        device.get("part") == "W25Q256JVEIQ",
        "payload NOR identity drifted",
        errors,
    )
    expect(
        device.get("capacity_bytes") == 32 * 1024 * 1024,
        "payload NOR must be 32 MiB",
        errors,
    )
    expect(device.get("mode") == "SINGLE_SPI", "payload NOR mode drifted", errors)
    expect(device.get("wp_io2_net") == "3V3", "WP#/IO2 must be defined high", errors)
    expect(
        device.get("hold_io3_net") == "3V3",
        "HOLD#/IO3 must be defined high",
        errors,
    )
    expect(device.get("cs_pullup_ohms") == 10000, "payload CS pull-up drifted", errors)
    expect(payload.get("xip_bus_shared") is False, "payload NOR must not share XIP", errors)
    expect(
        payload.get("controller_instance") == "DEFERRED_TO_TASK_04",
        "controller instance must remain Task 4",
        errors,
    )
    expect(
        payload.get("ownership_policy") == "DEFERRED_TO_TASK_04",
        "ownership policy must remain Task 4",
        errors,
    )
    assignments = {
        item.get("gpio"): (
            item.get("controller_pin"),
            item.get("alternate_function"),
            item.get("net"),
            item.get("flash_pin"),
        )
        for item in payload.get("pin_assignment", [])
        if isinstance(item, dict)
    }
    expect(
        assignments == PAYLOAD_ASSIGNMENT,
        f"payload assignment drifted: {assignments}",
        errors,
    )

    placeholders = {
        item.get("reference"): item
        for item in data.get("deferred_placeholders", [])
        if isinstance(item, dict)
    }
    for reference, task in {"U2": 3, "J1": 5}.items():
        item = placeholders.get(reference, {})
        expect(item.get("owner_task") == task, f"{reference} owner task drifted", errors)
        expect(item.get("dnp") is True, f"{reference} must remain DNP", errors)

    native = data.get("native_kicad_erc", {})
    expect(
        native.get("status") == "BLOCKED_TOOL_UNAVAILABLE",
        "native KiCad ERC must not be claimed without output",
        errors,
    )
    expect(
        native.get("required_before_phase_gate") is True,
        "native ERC must gate Task 2",
        errors,
    )
    structural = data.get("structural_erc", {})
    expect(structural.get("status") == "PASSED", "structural ERC must pass", errors)
    expect(
        structural.get("engine") == "repository-structural-erc-v1",
        "structural ERC engine drifted",
        errors,
    )

    claims = data.get("evidence_claims", {})
    expect(claims.get("MEASURED") == "NONE", "Task 2 cannot claim measurements", errors)
    for status in ("FACT", "EXPECTED", "MEASURED", "UNKNOWN"):
        expect(bool(claims.get(status)), f"missing {status} evidence statement", errors)

    sources = data.get("sources", [])
    expect(len(sources) >= 5, "at least five primary sources are required", errors)
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
            source.get("retrieved") == "2026-07-25",
            f"sources[{index}] retrieval date missing",
            errors,
        )
        expect(bool(source.get("supports")), f"sources[{index}] lacks scope", errors)
    return errors


def validate_files(errors: list[str]) -> None:
    pin_rows = read_csv(PINMAP)
    expect(len(pin_rows) == 61, "pinmap must enumerate pins 1-61", errors)
    expect(
        {row["pin"] for row in pin_rows} == {str(pin) for pin in range(1, 62)},
        "pinmap pin numbers must be exactly 1-61",
        errors,
    )
    pin_by_name = {row["pin_name"]: row for row in pin_rows}
    for gpio, (pin, _function, net, _flash_pin) in PAYLOAD_ASSIGNMENT.items():
        row = pin_by_name.get(gpio, {})
        expect(row.get("pin") == pin, f"{gpio} physical pin drifted", errors)
        expect(row.get("net") == net, f"{gpio} net drifted", errors)

    test_rows = read_csv(TEST_ACCESS)
    expect(len(test_rows) == 14, "test-access must assign TP1-TP14", errors)
    actual_test_nets = {row["net"] for row in test_rows}
    expect(
        actual_test_nets == REQUIRED_TEST_NETS,
        f"test access net set drifted: {sorted(actual_test_nets)}",
        errors,
    )
    for row in test_rows:
        expect(
            row["footprint"] == "TestPoint:TestPoint_Plated_Hole_D1.0mm",
            f"{row['reference']} footprint drifted",
            errors,
        )
        expect(
            row["status"] == "CONTRACT_ASSIGNED_SOURCE_CAPTURE_PENDING",
            f"{row['reference']} must not be claimed captured yet",
            errors,
        )

    assumptions = ASSUMPTIONS.read_text(encoding="utf-8")
    for heading in ("## FACT", "## DECISION", "## EXPECTED", "## MEASURED", "## UNKNOWN"):
        expect(heading in assumptions, f"assumptions missing {heading}", errors)
    expect("`NONE`" in assumptions, "assumptions must state no measurements", errors)

    source_text = SOURCE.read_text(encoding="utf-8")
    expect(
        "RP-008295-DS-1" in source_text,
        "KiCad source provenance is incomplete",
        errors,
    )

    kicad_text = KICAD.read_text(encoding="utf-8")
    expect(balanced_sexpression(kicad_text), "KiCad S-expression is unbalanced", errors)
    for token in (
        "RP2354A A4",
        "W25Q256JVEIQ",
        "PAYLOAD_SPI_CIPO",
        "PAYLOAD_SPI_CS_N",
        "PAYLOAD_SPI_SCK",
        "PAYLOAD_SPI_COPI",
        "BOOTSEL_QSPI_SS",
        "SWDIO",
        "SWCLK",
        "USB_DP",
        "USB_DM",
        "3V3_REGULATOR_TASK3_PLACEHOLDER",
        "USB_C_UFP_TASK5_PLACEHOLDER",
    ):
        expect(token in kicad_text, f"KiCad source missing {token}", errors)
    expect(
        '(property "Value" "10k"' in kicad_text,
        "KiCad source lacks payload CS pull-up value",
        errors,
    )
    expect(
        '(property "Value" "0"' in kicad_text
        and '(property "Value" "DNF"' in kicad_text,
        "KiCad source lacks payload-CS link selection",
        errors,
    )

    report = read_json(REPORT)
    expect(
        report.get("engine") == "repository-structural-erc-v1",
        "ERC report engine drifted",
        errors,
    )
    expect(report.get("status") == "PASSED", "structural ERC report must pass", errors)
    expect(report.get("error_count") == 0, "structural ERC report has errors", errors)
    expect(
        report.get("native_kicad_erc") == "BLOCKED_TOOL_UNAVAILABLE",
        "ERC report must expose native ERC blocker",
        errors,
    )
    expect(
        report.get("phase_gate_passed") is False,
        "ERC report cannot close Task 2",
        errors,
    )

    tree = ET.parse(RENDERED)
    root = tree.getroot()
    expect(root.tag.endswith("svg"), "rendered schematic root must be SVG", errors)
    svg_text = RENDERED.read_text(encoding="utf-8")
    for token in (
        "DESIGN ONLY",
        "RP2354A",
        "W25Q256JVEIQ",
        "PAYLOAD_SPI_SCK",
        "BOOTSEL",
        "Native KiCad ERC: BLOCKED",
    ):
        expect(token in svg_text, f"rendered schematic missing {token}", errors)


def run_self_test(strict: bool) -> list[str]:
    baseline = read_json(CONTRACT)
    failures: list[str] = []
    mutations = [
        ("shared XIP", lambda value: value["payload_spi"].update(xip_bus_shared=True)),
        (
            "measurement claim",
            lambda value: value["evidence_claims"].update(MEASURED="voltage passed"),
        ),
        (
            "premature gate",
            lambda value: value.update(phase_gate_passed=True),
        ),
        (
            "payload pin drift",
            lambda value: value["payload_spi"]["pin_assignment"][0].update(
                controller_pin="28"
            ),
        ),
    ]
    for label, mutate in mutations:
        candidate = copy.deepcopy(baseline)
        mutate(candidate)
        if not validate_contract(candidate, strict=strict):
            failures.append(f"self-test failed to reject {label}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()

    required = [
        CONTRACT,
        PINMAP,
        TEST_ACCESS,
        ASSUMPTIONS,
        RENDERED,
        REPORT,
        KICAD,
        SOURCE,
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        for path in missing:
            print(f"ERROR: missing {path}")
        return 1

    data = read_json(CONTRACT)
    errors = validate_contract(data, strict=arguments.strict)
    validate_files(errors)
    if arguments.self_test:
        errors.extend(run_self_test(arguments.strict))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    mode = "strict" if arguments.strict else "standard"
    suffix = " with mutation self-test" if arguments.self_test else ""
    print(f"Task 2 structural ERC passed ({mode}{suffix}).")
    print("Native KiCad ERC remains BLOCKED_TOOL_UNAVAILABLE; phase gate is false.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
