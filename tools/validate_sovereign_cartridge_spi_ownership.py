#!/usr/bin/env python3
"""Validate the Task 4 Sovereign Cartridge SPI ownership contract.

This standard-library check verifies the controller mapping, single-owner
policy, command allowlist, bounds, timeout margins, recovery invariants,
evidence language and Task 2/3 handoffs. It does not claim firmware, timing or
physical fault-injection evidence.
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
SPI = PLATFORM / "spi"
CONTRACT = SPI / "spi-ownership.json"
COMMAND_POLICY = SPI / "command-policy.csv"
README = SPI / "README.md"
ASSUMPTIONS = SPI / "assumptions.md"
DIAGRAM = SPI / "spi-ownership.svg"
CHECKLIST = SPI / "validation/task-04-checklist.md"
TOPOLOGY = PLATFORM / "topology.json"
SCHEMATIC = PLATFORM / "schematics/schematic.json"
POWER = PLATFORM / "power/power-safety.json"

ALLOWED_SOURCE_HOSTS = {
    "pip.raspberrypi.com",
    "www.raspberrypi.com",
    "github.com",
    "www.winbond.com",
    "e2e.ti.com",
}
REQUIRED_STATES = {
    "UNINITIALIZED",
    "PROBING",
    "IDLE",
    "ACQUIRED",
    "WAIT_BUSY",
    "VERIFY",
    "RECOVER",
    "FAULT_LOCKED",
}
REQUIRED_HEADINGS = {
    "## FACT",
    "## DECISION",
    "## EXPECTED",
    "## MEASURED",
    "## UNKNOWN",
}
REQUIRED_SIGNALS = {
    "GPIO16": (
        "SPI0_RX",
        "SPI0_RX",
        "PAYLOAD_SPI_CIPO",
        "FLASH_TO_CONTROLLER",
    ),
    "GPIO17": (
        "SPI0_CSn",
        "SIO_GPIO_OUTPUT",
        "PAYLOAD_SPI_CS_N",
        "CONTROLLER_TO_FLASH",
    ),
    "GPIO18": (
        "SPI0_SCK",
        "SPI0_SCK",
        "PAYLOAD_SPI_SCK",
        "CONTROLLER_TO_FLASH",
    ),
    "GPIO19": (
        "SPI0_TX",
        "SPI0_TX",
        "PAYLOAD_SPI_COPI",
        "CONTROLLER_TO_FLASH",
    ),
}
REQUIRED_ALLOWED_COMMANDS = {
    "WRITE_ENABLE": (
        "06",
        "MUTATION_PREAMBLE",
        0,
        False,
        False,
        "CONFIRM_WEL_ONE",
    ),
    "WRITE_DISABLE": (
        "04",
        "RECOVERY_AND_CLEANUP",
        0,
        False,
        False,
        "CONFIRM_WEL_ZERO",
    ),
    "READ_STATUS_REGISTER_1": (
        "05",
        "STATUS",
        0,
        False,
        False,
        "CAPTURE_BUSY_AND_WEL",
    ),
    "READ_STATUS_REGISTER_2": (
        "35",
        "STATUS",
        0,
        False,
        False,
        "CAPTURE_QE_SUS_AND_SECURITY_STATE",
    ),
    "READ_STATUS_REGISTER_3": (
        "15",
        "STATUS",
        0,
        False,
        False,
        "CAPTURE_ADDRESS_MODE_AND_WPS_STATE",
    ),
    "READ_JEDEC_ID": (
        "9F",
        "PROBE",
        0,
        False,
        False,
        "REQUIRE_EF4019",
    ),
    "READ_DATA_4_BYTE": (
        "13",
        "READ",
        4,
        False,
        False,
        "RETURN_EXACT_REQUESTED_LENGTH",
    ),
    "PAGE_PROGRAM_4_BYTE": (
        "12",
        "PROGRAM",
        4,
        True,
        True,
        "POLL_BUSY_THEN_FULL_READ_BACK_VERIFY",
    ),
    "SECTOR_ERASE_4_BYTE": (
        "21",
        "ERASE_4K",
        4,
        True,
        True,
        "POLL_BUSY_THEN_VERIFY_ALL_FF",
    ),
    "BLOCK_ERASE_64K_4_BYTE": (
        "DC",
        "ERASE_64K",
        4,
        True,
        True,
        "POLL_BUSY_THEN_VERIFY_ALL_FF",
    ),
    "ENABLE_RESET": (
        "66",
        "RECOVERY_ONLY",
        0,
        False,
        False,
        "NEXT_COMMAND_MUST_BE_RESET_DEVICE",
    ),
    "RESET_DEVICE": (
        "99",
        "RECOVERY_ONLY",
        0,
        False,
        False,
        "WAIT_RESET_DELAY_THEN_REPROBE",
    ),
}
REQUIRED_FORBIDDEN_OPCODES = {
    "C7",
    "60",
    "03",
    "02",
    "20",
    "D8",
    "B7",
    "E9",
    "01",
    "31",
    "11",
    "32",
    "38",
}
REQUIRED_PUBLIC_OPERATIONS = {
    "PROBE",
    "READ",
    "PROGRAM_PAGE",
    "ERASE_SECTOR",
    "ERASE_BLOCK_64K",
    "GET_HEALTH",
}
REQUIRED_ERRORS = {
    "E_SPI_NOT_OWNER",
    "E_SPI_QUEUE_FULL",
    "E_SPI_POWER_UNSAFE",
    "E_SPI_ID_MISMATCH",
    "E_SPI_BUSY",
    "E_SPI_BOUNDS",
    "E_SPI_ALIGNMENT",
    "E_SPI_PAGE_CROSS",
    "E_SPI_WEL",
    "E_SPI_TIMEOUT",
    "E_SPI_VERIFY",
    "E_SPI_RESET_UNSAFE",
    "E_SPI_UNKNOWN_OUTCOME",
    "E_SPI_FAULT_LOCKED",
}


def expect(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def close(actual: float, expected: float, tolerance: float = 1e-6) -> bool:
    return math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    return value


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_metadata(data: dict, errors: list[str]) -> None:
    expect(data.get("schema_version") == 1, "schema_version must be 1", errors)
    expect(
        data.get("spi_ownership_id") == "sovereign-cartridge-proto0-task-04",
        "spi_ownership_id drifted",
        errors,
    )
    expect(data.get("product") == "Sovereign Cartridge", "product drifted", errors)
    expect(data.get("revision") == "PROTO-0", "revision drifted", errors)
    expect(
        data.get("status") == "SPI_OWNERSHIP_DESIGN_IN_PROGRESS",
        "Task 4 must remain in progress",
        errors,
    )
    expect(
        data.get("evidence_status") == "DESIGN_ONLY",
        "evidence_status must remain DESIGN_ONLY",
        errors,
    )
    expect(
        data.get("phase_gate_passed") is False,
        "Task 4 phase gate must remain false",
        errors,
    )
    expect(
        data.get("invariant")
        == "Never expose incomplete or corrupted data as valid committed data.",
        "data-integrity invariant drifted",
        errors,
    )


def validate_physical_contract(data: dict, errors: list[str]) -> None:
    physical = data.get("physical_contract", {})
    expect(physical.get("controller") == "SPI0", "controller must be SPI0", errors)
    expect(
        physical.get("controller_type") == "RP2350_PRIMECELL_SSP",
        "controller type drifted",
        errors,
    )
    expect(physical.get("role") == "CONTROLLER", "SPI role drifted", errors)
    expect(
        physical.get("payload_device") == "W25Q256JVEIQ",
        "payload device drifted",
        errors,
    )
    expect(
        physical.get("boot_xip_bus") == "IN_PACKAGE_BOOT_QSPI",
        "boot XIP boundary drifted",
        errors,
    )
    expect(
        physical.get("xip_bus_shared") is False,
        "payload SPI must not share the boot XIP bus",
        errors,
    )

    assignments = {}
    for item in physical.get("signal_map", []):
        if not isinstance(item, dict):
            continue
        assignments[item.get("gpio")] = (
            item.get("hardware_function"),
            item.get("runtime_mux"),
            item.get("net"),
            item.get("direction"),
        )
    expect(
        assignments == REQUIRED_SIGNALS,
        f"SPI0 signal map drifted: {assignments}",
        errors,
    )

    electrical = physical.get("electrical_format", {})
    for key, value in {
        "spi_mode": 0,
        "clock_polarity": 0,
        "clock_phase": 0,
        "bits_per_word": 8,
        "bit_order": "MSB_FIRST",
        "requested_clock_hz": 24000000,
        "actual_clock_rule": "ACTUAL_MUST_BE_NONZERO_AND_NOT_EXCEED_REQUESTED",
        "clock_idle": "LOW",
        "chip_select_active": "LOW",
        "chip_select_control": "OWNER_CONTROLLED_GPIO",
        "chip_select_idle": "HIGH",
        "minimum_chip_select_high_us": 1,
        "wp_io2_state": "HIGH",
        "hold_io3_state": "HIGH",
        "transfer_engine": "POLLED_BLOCKING_PROTO0",
    }.items():
        expect(
            electrical.get(key) == value,
            f"electrical_format.{key} drifted",
            errors,
        )


def validate_ownership(data: dict, errors: list[str]) -> None:
    ownership = data.get("ownership_contract", {})
    expect(
        ownership.get("resource") == "SPI0_GPIO16_GPIO17_GPIO18_GPIO19",
        "owned resource drifted",
        errors,
    )
    expect(
        ownership.get("exclusive_owner") == "PAYLOAD_STORAGE_SERVICE",
        "exclusive owner drifted",
        errors,
    )
    expect(
        ownership.get("access_model") == "SINGLE_OWNER_SERIAL_REQUEST_QUEUE",
        "access model drifted",
        errors,
    )
    expect(ownership.get("queue_depth") == 8, "queue depth drifted", errors)
    expect(
        ownership.get("maximum_inflight_requests") == 1,
        "only one request may be in flight",
        errors,
    )
    for key in (
        "direct_register_access_outside_owner",
        "direct_sdk_spi_access_outside_owner",
        "isr_may_start_transaction",
        "other_core_may_start_transaction",
        "automatic_mutation_retry",
    ):
        expect(ownership.get(key) is False, f"{key} must remain false", errors)
    expect(
        ownership.get("other_clients_submit_typed_requests_only") is True,
        "clients must use typed requests",
        errors,
    )
    expect(
        ownership.get("transfer_engine") == "POLLED_BLOCKING_PROTO0",
        "Task 4 transfer engine drifted",
        errors,
    )
    expect(
        ownership.get("dma_policy")
        == "DEFERRED_UNTIL_OWNERSHIP_AND_ABORT_PATH_ARE_PROVEN",
        "DMA must remain deferred",
        errors,
    )
    cancellation = ownership.get("cancellation", {})
    expect(
        cancellation.get("queued_request") == "ALLOWED",
        "queued cancellation policy drifted",
        errors,
    )
    expect(
        cancellation.get("after_chip_select_asserted") == "NOT_ALLOWED",
        "active frame must not be cancellable",
        errors,
    )
    expect(
        cancellation.get("after_write_enable_confirmed")
        == "NOT_ALLOWED_OWNER_MUST_SEND_WRITE_DISABLE_OR_CONTINUE_VALIDATED_MUTATION",
        "WEL-set cancellation policy drifted",
        errors,
    )
    expect(
        "UNKNOWN" in cancellation.get("after_mutating_opcode_accepted", ""),
        "accepted mutation cancellation lacks unknown-outcome boundary",
        errors,
    )


def validate_flash(data: dict, errors: list[str]) -> None:
    flash = data.get("flash_contract", {})
    for key, value in {
        "part": "W25Q256JVEIQ",
        "jedec_id_hex": "EF4019",
        "capacity_bytes": 33554432,
        "minimum_address": 0,
        "maximum_address": 33554431,
        "maximum_address_hex": "01FFFFFF",
        "page_size_bytes": 256,
        "sector_size_bytes": 4096,
        "block_size_bytes": 65536,
        "address_policy": "DEDICATED_4_BYTE_OPCODES_ONLY",
        "persistent_4_byte_mode": False,
        "quad_mode_enabled": False,
        "qpi_mode_enabled": False,
        "maximum_read_request_bytes": 4096,
        "bounds_check_rule": "CHECK_64_BIT_ADDRESS_PLUS_LENGTH_BEFORE_NARROWING",
        "page_program_rule": "ONE_TO_256_BYTES_AND_MUST_NOT_CROSS_256_BYTE_PAGE",
        "sector_erase_rule": "ADDRESS_ALIGNED_TO_4096",
        "block_erase_rule": "ADDRESS_ALIGNED_TO_65536",
    }.items():
        expect(flash.get(key) == value, f"flash_contract.{key} drifted", errors)
    expect(
        flash.get("maximum_address") == flash.get("capacity_bytes") - 1,
        "maximum address does not match capacity",
        errors,
    )
    preconditions = set(flash.get("mutation_preconditions", []))
    for requirement in (
        "POWER_SAFE_LATCHED",
        "OWNER_HELD",
        "DEVICE_ID_VERIFIED_FOR_RESET_GENERATION",
        "BUSY_ZERO",
        "WRITE_ENABLE_SENT",
        "WEL_ONE_CONFIRMED",
        "ADDRESS_AND_LENGTH_VALID",
    ):
        expect(
            requirement in preconditions,
            f"mutation precondition missing {requirement}",
            errors,
        )
    completion = set(flash.get("mutation_completion", []))
    for requirement in (
        "BUSY_ZERO_BEFORE_OPERATION_TIMEOUT",
        "WEL_ZERO_AFTER_COMPLETION",
        "FULL_TARGET_RANGE_READ_BACK_VERIFIED",
        "RESULT_REPORTED_TO_CALLER_WITHOUT_IMPLYING_HIGHER_LEVEL_COMMIT",
    ):
        expect(
            requirement in completion,
            f"mutation completion missing {requirement}",
            errors,
        )


def validate_commands(data: dict, errors: list[str]) -> None:
    commands = {}
    opcodes = set()
    for item in data.get("allowed_commands", []):
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        opcode = str(item.get("opcode_hex", "")).upper()
        commands[name] = (
            opcode,
            item.get("scope"),
            item.get("address_bytes"),
            item.get("mutating"),
            item.get("requires_wel"),
            item.get("completion"),
        )
        expect(bool(item.get("completion")), f"{name} lacks completion rule", errors)
        expect(opcode not in opcodes, f"duplicate allowed opcode {opcode}", errors)
        opcodes.add(opcode)
    expect(
        commands == REQUIRED_ALLOWED_COMMANDS,
        f"allowed command policy drifted: {commands}",
        errors,
    )

    forbidden = {}
    for item in data.get("forbidden_commands", []):
        if not isinstance(item, dict):
            continue
        opcode = str(item.get("opcode_hex", "")).upper()
        forbidden[opcode] = item
        expect(bool(item.get("reason")), f"forbidden opcode {opcode} lacks reason", errors)
    expect(
        set(forbidden) == REQUIRED_FORBIDDEN_OPCODES,
        f"forbidden command policy drifted: {set(forbidden)}",
        errors,
    )
    expect(
        opcodes.isdisjoint(forbidden),
        "allowed and forbidden opcode sets overlap",
        errors,
    )
    expect(
        {"C7", "60"}.issubset(forbidden),
        "both chip-erase opcodes must be forbidden",
        errors,
    )
    expect(
        {"03", "02", "20", "D8", "B7", "E9"}.issubset(forbidden),
        "24-bit and persistent-mode opcodes must remain forbidden",
        errors,
    )


def validate_timeouts(data: dict, errors: list[str]) -> None:
    timeouts = data.get("timeouts", {})
    pairs = (
        ("page_program_datasheet_max_ms", "page_program_operation_timeout_ms", 3, 5),
        ("sector_erase_datasheet_max_ms", "sector_erase_operation_timeout_ms", 400, 500),
        (
            "block_64k_erase_datasheet_max_ms",
            "block_64k_erase_operation_timeout_ms",
            2000,
            2500,
        ),
    )
    for maximum_key, timeout_key, maximum, timeout in pairs:
        expect(timeouts.get(maximum_key) == maximum, f"{maximum_key} drifted", errors)
        expect(timeouts.get(timeout_key) == timeout, f"{timeout_key} drifted", errors)
        expect(
            timeouts.get(timeout_key, 0) > timeouts.get(maximum_key, 0),
            f"{timeout_key} must exceed cited maximum",
            errors,
        )
    for key, value in {
        "read_transfer_timeout_us": 5000,
        "reset_datasheet_typical_us": 30,
        "reset_operation_timeout_us": 100,
        "power_up_read_delay_us": 20,
        "power_up_mutation_delay_ms": 5,
        "status_poll_interval_us": 100,
        "timeout_policy": "DEASSERT_CS_DISABLE_NEW_MUTATIONS_AND_ENTER_RECOVERY",
        "chip_erase_timeout": "NOT_DEFINED_COMMAND_FORBIDDEN",
    }.items():
        expect(timeouts.get(key) == value, f"timeouts.{key} drifted", errors)


def validate_state_and_recovery(data: dict, errors: list[str]) -> None:
    states = {
        item.get("state")
        for item in data.get("state_machine", [])
        if isinstance(item, dict)
    }
    expect(states == REQUIRED_STATES, f"state machine drifted: {states}", errors)
    for item in data.get("state_machine", []):
        if isinstance(item, dict):
            expect(bool(item.get("entry")), f"{item.get('state')} lacks entry", errors)
            expect(bool(item.get("action")), f"{item.get('state')} lacks action", errors)

    recovery = data.get("recovery_contract", {})
    startup = set(recovery.get("startup_sequence", []))
    for step in (
        "WAIT_20_US_BEFORE_FIRST_READ",
        "WAIT_5_MS_BEFORE_FIRST_MUTATION",
        "READ_JEDEC_ID_AND_REQUIRE_EF4019",
        "READ_STATUS_1_2_3",
        "IF_BUSY_WAIT_WITHIN_2500_MS_RECOVERY_BOUND",
        "REJECT_MUTATIONS_IF_QE_OR_ADDRESS_MODE_STATE_VIOLATES_POLICY",
    ):
        expect(step in startup, f"startup sequence missing {step}", errors)
    reset = recovery.get("software_reset_policy", {})
    expect(
        reset.get("normal_operation") == "FORBIDDEN",
        "software reset must be forbidden in normal operation",
        errors,
    )
    for key in (
        "recovery_only",
        "requires_busy_zero",
        "requires_suspend_zero",
        "requires_power_safe",
        "requires_owner_held",
    ):
        expect(reset.get(key) is True, f"software reset {key} must be true", errors)
    expect(reset.get("sequence") == ["66", "99"], "reset sequence drifted", errors)
    expect(
        recovery.get("reset_during_mutation_result")
        == "UNKNOWN_OPERATION_OUTCOME",
        "reset-during-mutation result drifted",
        errors,
    )
    expect(
        recovery.get("automatic_mutation_retry") is False,
        "recovery must not retry mutations automatically",
        errors,
    )
    expect(
        recovery.get("higher_layer_handoff")
        == "TASK_13_TRANSACTION_LAYER_DECIDES_COMMIT_ABORT_OR_REPAIR",
        "higher-layer recovery handoff drifted",
        errors,
    )
    power = recovery.get("power_fault_handoff", {})
    expect(
        power.get("source") == "TASK_03_POWER_SAFE_N_TO_RUN",
        "Task 3 power handoff drifted",
        errors,
    )
    expect(
        power.get("run_to_bus_quiet_budget_us") == 25,
        "RUN-to-bus-quiescent budget drifted",
        errors,
    )
    expect(
        power.get("evidence_status") == "UNKNOWN_REQUIRES_BENCH",
        "bus-quiescence cannot be claimed",
        errors,
    )


def validate_interfaces_and_evidence(
    data: dict, strict: bool, errors: list[str]
) -> None:
    operations = {
        item.get("operation")
        for item in data.get("public_request_contract", [])
        if isinstance(item, dict)
    }
    expect(
        operations == REQUIRED_PUBLIC_OPERATIONS,
        f"public request contract drifted: {operations}",
        errors,
    )
    for item in data.get("public_request_contract", []):
        if isinstance(item, dict):
            expect(
                bool(item.get("arguments")),
                f"{item.get('operation')} lacks arguments",
                errors,
            )
            expect(
                bool(item.get("success")),
                f"{item.get('operation')} lacks success boundary",
                errors,
            )
    expect(
        set(data.get("error_contract", [])) == REQUIRED_ERRORS,
        "error contract drifted",
        errors,
    )

    observability = data.get("observability_contract", {})
    expect(
        observability.get("payload_bytes_logged") is False,
        "payload bytes must not be logged",
        errors,
    )
    raw_rate = 24000000 / 8
    full_scan = 33554432 / raw_rate
    expect(
        close(
            float(observability.get("raw_clock_rate_bytes_per_second", 0)),
            raw_rate,
        ),
        "raw SPI rate calculation drifted",
        errors,
    )
    expect(
        close(
            float(observability.get("calculated_full_scan_seconds", 0)),
            full_scan,
        ),
        "full-scan calculation drifted",
        errors,
    )
    expect(
        observability.get("performance_evidence") == "EXPECTED_NOT_MEASURED",
        "performance must remain unmeasured",
        errors,
    )
    for field in (
        "request_sequence",
        "operation",
        "address",
        "length",
        "start_us",
        "end_us",
        "status_before",
        "status_after",
        "result",
        "reset_generation",
    ):
        expect(
            field in observability.get("per_request_fields", []),
            f"observability field missing {field}",
            errors,
        )

    claims = data.get("evidence_claims", {})
    for label in ("FACT", "DECISION", "EXPECTED", "MEASURED", "UNKNOWN"):
        expect(bool(claims.get(label)), f"missing {label} evidence claim", errors)
    expect(claims.get("MEASURED") == "NONE", "Task 4 cannot claim measurements", errors)
    expect(
        len(data.get("blocking_validation", [])) >= 10,
        "blocking validation list is incomplete",
        errors,
    )

    sources = data.get("sources", [])
    expect(len(sources) >= 5, "at least five primary sources are required", errors)
    for index, source in enumerate(sources):
        parsed = urlparse(source.get("url", ""))
        expect(parsed.scheme == "https", f"sources[{index}] must use HTTPS", errors)
        if strict:
            expect(
                parsed.hostname in ALLOWED_SOURCE_HOSTS,
                f"sources[{index}] host is not approved: {parsed.hostname}",
                errors,
            )
        expect(
            source.get("retrieved") == "2026-07-28",
            f"sources[{index}] retrieval date drifted",
            errors,
        )
        expect(bool(source.get("supports")), f"sources[{index}] lacks scope", errors)


def validate_contract(data: dict, strict: bool = False) -> list[str]:
    errors: list[str] = []
    validate_metadata(data, errors)
    validate_physical_contract(data, errors)
    validate_ownership(data, errors)
    validate_flash(data, errors)
    validate_commands(data, errors)
    validate_timeouts(data, errors)
    validate_state_and_recovery(data, errors)
    validate_interfaces_and_evidence(data, strict, errors)
    return errors


def validate_files(data: dict, errors: list[str]) -> None:
    rows = read_csv(COMMAND_POLICY)
    csv_commands = {}
    for row in rows:
        csv_commands[row["name"]] = (
            row["opcode_hex"].upper(),
            row["scope"],
            int(row["address_bytes"]),
            row["mutating"].lower() == "true",
            row["requires_wel"].lower() == "true",
            row["completion"],
        )
        expect(
            row["policy"] in {"ALLOWED", "RECOVERY_ONLY"},
            f"{row['name']} has invalid CSV policy",
            errors,
        )
        expect(bool(row["completion"]), f"{row['name']} lacks CSV completion", errors)
    expect(
        csv_commands == REQUIRED_ALLOWED_COMMANDS,
        "command-policy.csv does not match the JSON allowlist",
        errors,
    )

    assumptions = ASSUMPTIONS.read_text(encoding="utf-8")
    for heading in REQUIRED_HEADINGS:
        expect(heading in assumptions, f"assumptions missing {heading}", errors)
    expect("`NONE`" in assumptions, "assumptions must state no measurements", errors)
    expect(
        "Expected statements are design predictions" in assumptions,
        "assumptions lack expected-evidence boundary",
        errors,
    )

    checklist = CHECKLIST.read_text(encoding="utf-8")
    expect("Status: `OPEN`." in checklist, "Task 4 checklist must remain open", errors)
    expect(
        "cannot close the gate" in checklist,
        "Task 4 checklist lacks the physical-evidence gate",
        errors,
    )

    readme = README.read_text(encoding="utf-8")
    normalized_readme = " ".join(readme.split())
    for token in (
        "PAYLOAD_STORAGE_SERVICE",
        "software-controlled GPIO",
        "Chip erase",
        "never automatically",
        "DESIGN_IN_PROGRESS",
    ):
        expect(
            token in normalized_readme,
            f"Task 4 README missing {token}",
            errors,
        )

    try:
        tree = ET.parse(DIAGRAM)
        expect(tree.getroot().tag.endswith("svg"), "SPI diagram root must be SVG", errors)
    except ET.ParseError as exc:
        errors.append(f"SPI diagram SVG invalid: {exc}")
    diagram_text = DIAGRAM.read_text(encoding="utf-8")
    for token in (
        "DESIGN ONLY",
        "PAYLOAD_STORAGE_SERVICE",
        "RP2354A · SPI0",
        "W25Q256JV",
        "EF 40 19",
        "UNKNOWN_OPERATION_OUTCOME",
        "FAULT",
    ):
        expect(token in diagram_text, f"SPI diagram missing {token}", errors)

    topology = read_json(TOPOLOGY)
    topology_spi = topology.get("interfaces", {}).get("payload_spi", {})
    expect(
        topology_spi.get("physical_device") == "W25Q256JVEIQ",
        "Task 1 payload device handoff drifted",
        errors,
    )
    expect(
        topology_spi.get("controller_instance") == "DEFERRED_TO_TASK_04",
        "Task 1 must retain its Task 4 controller handoff",
        errors,
    )
    expect(
        topology_spi.get("ownership_policy") == "DEFERRED_TO_TASK_04",
        "Task 1 must retain its Task 4 ownership handoff",
        errors,
    )
    expect(
        topology_spi.get("xip_bus_shared") is False,
        "Task 1 XIP separation drifted",
        errors,
    )
    gates = topology.get("phase_gates", {})
    expect(
        gates.get("task_04_spi_ownership_passed") is False,
        "topology Task 4 gate must remain false",
        errors,
    )
    authorization = topology.get("authorization", {})
    expect(
        authorization.get("real_hardware_enabled") is False,
        "Task 4 cannot enable real hardware",
        errors,
    )
    expect(
        authorization.get("destructive_storage_writes_enabled") is False,
        "Task 4 cannot enable destructive writes",
        errors,
    )

    schematic = read_json(SCHEMATIC)
    payload = schematic.get("payload_spi", {})
    expect(
        payload.get("controller_instance") == "DEFERRED_TO_TASK_04",
        "Task 2 must retain its Task 4 controller handoff",
        errors,
    )
    expect(
        payload.get("ownership_policy") == "DEFERRED_TO_TASK_04",
        "Task 2 must retain its Task 4 ownership handoff",
        errors,
    )
    expect(payload.get("xip_bus_shared") is False, "Task 2 XIP separation drifted", errors)
    expect(
        payload.get("device", {}).get("cs_pullup_ohms") == 10000,
        "Task 2 payload CS pull-up handoff drifted",
        errors,
    )
    schematic_assignments = {}
    for item in payload.get("pin_assignment", []):
        schematic_assignments[item.get("gpio")] = (
            item.get("alternate_function"),
            item.get("net"),
        )
    contract_assignments = {
        gpio: (values[0], values[2]) for gpio, values in REQUIRED_SIGNALS.items()
    }
    expect(
        schematic_assignments == contract_assignments,
        "Task 2 and Task 4 signal maps do not match",
        errors,
    )

    power = read_json(POWER)
    hold_up = power.get("hold_up", {})
    expect(
        hold_up.get("run_to_bus_quiet_budget_us") == 25,
        "Task 3 RUN-to-bus-quiescent handoff drifted",
        errors,
    )
    expect(
        power.get("supervision", {})
        .get("payload_cs_fail_safe", {})
        .get("required_state_during_reset")
        == "HIGH_INACTIVE",
        "Task 3 payload-CS safe state drifted",
        errors,
    )
    recovery_power = data.get("recovery_contract", {}).get("power_fault_handoff", {})
    expect(
        recovery_power.get("run_to_bus_quiet_budget_us")
        == hold_up.get("run_to_bus_quiet_budget_us"),
        "Task 3 and Task 4 bus-quiescence budgets disagree",
        errors,
    )


def run_self_test(strict: bool) -> list[str]:
    baseline = read_json(CONTRACT)
    failures: list[str] = []
    mutations = [
        (
            "measurement claim",
            lambda value: value["evidence_claims"].update(MEASURED="passed"),
        ),
        ("premature gate", lambda value: value.update(phase_gate_passed=True)),
        (
            "shared XIP bus",
            lambda value: value["physical_contract"].update(xip_bus_shared=True),
        ),
        (
            "owner drift",
            lambda value: value["ownership_contract"].update(
                exclusive_owner="ARBITRARY_CALLER"
            ),
        ),
        (
            "direct SDK access",
            lambda value: value["ownership_contract"].update(
                direct_sdk_spi_access_outside_owner=True
            ),
        ),
        (
            "multiple inflight",
            lambda value: value["ownership_contract"].update(
                maximum_inflight_requests=2
            ),
        ),
        (
            "automatic mutation retry",
            lambda value: value["recovery_contract"].update(
                automatic_mutation_retry=True
            ),
        ),
        (
            "persistent four-byte mode",
            lambda value: value["flash_contract"].update(
                persistent_4_byte_mode=True
            ),
        ),
        (
            "chip erase allowed",
            lambda value: value["allowed_commands"].append(
                {
                    "name": "CHIP_ERASE",
                    "opcode_hex": "C7",
                    "scope": "ERASE_ALL",
                    "address_bytes": 0,
                    "mutating": True,
                    "requires_wel": True,
                    "completion": "POLL_BUSY",
                }
            ),
        ),
        (
            "unsafe software reset",
            lambda value: value["recovery_contract"]["software_reset_policy"].update(
                requires_busy_zero=False
            ),
        ),
        (
            "short erase timeout",
            lambda value: value["timeouts"].update(
                sector_erase_operation_timeout_ms=300
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
        COMMAND_POLICY,
        README,
        ASSUMPTIONS,
        DIAGRAM,
        CHECKLIST,
        TOPOLOGY,
        SCHEMATIC,
        POWER,
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        for path in missing:
            print(f"ERROR: missing {path}")
        return 1

    contract = read_json(CONTRACT)
    errors = validate_contract(contract, strict=arguments.strict)
    validate_files(contract, errors)
    if arguments.self_test:
        errors.extend(run_self_test(arguments.strict))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    mode = "strict" if arguments.strict else "standard"
    suffix = " with mutation self-test" if arguments.self_test else ""
    print(f"Task 4 SPI ownership design checks passed ({mode}{suffix}).")
    print("Firmware and physical evidence are absent; Task 4 phase gate remains false.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
