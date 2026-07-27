#!/usr/bin/env python3
"""Validate the Task 3 Sovereign Cartridge power-safety contract.

This standard-library check verifies the design equations, fail-stop
invariants, evidence language and repository handoffs. It does not replace
native ERC, electrical simulation or physical power-cut measurements.
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
POWER = PLATFORM / "power"
CONTRACT = POWER / "power-safety.json"
BUDGET = POWER / "power-budget.csv"
COMPONENTS = POWER / "component-candidates.csv"
ASSUMPTIONS = POWER / "assumptions.md"
DIAGRAM = POWER / "power-safety.svg"
CHECKLIST = POWER / "validation/task-03-checklist.md"
TOPOLOGY = PLATFORM / "topology.json"
SCHEMATIC = PLATFORM / "schematics/schematic.json"

ALLOWED_SOURCE_HOSTS = {
    "www.ti.com",
    "pip.raspberrypi.com",
    "www.winbond.com",
}
REQUIRED_STATES = {"OFF", "QUALIFY", "RUN", "FAULT_STOP", "RECOVERY"}
REQUIRED_HEADINGS = {
    "## FACT",
    "## DECISION",
    "## EXPECTED",
    "## MEASURED",
    "## UNKNOWN",
}


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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_contract(data: dict, strict: bool = False) -> list[str]:
    errors: list[str] = []
    expect(data.get("schema_version") == 1, "schema_version must be 1", errors)
    expect(
        data.get("power_safety_id") == "sovereign-cartridge-proto0-task-03",
        "power_safety_id drifted",
        errors,
    )
    expect(data.get("product") == "Sovereign Cartridge", "product drifted", errors)
    expect(data.get("revision") == "PROTO-0", "revision drifted", errors)
    expect(
        data.get("status") == "POWER_SAFETY_DESIGN_IN_PROGRESS",
        "Task 3 must remain in progress",
        errors,
    )
    expect(
        data.get("evidence_status") == "DESIGN_ONLY",
        "evidence_status must remain DESIGN_ONLY",
        errors,
    )
    expect(
        data.get("phase_gate_passed") is False,
        "Task 3 phase gate must remain false",
        errors,
    )
    expect(
        data.get("invariant")
        == "Never expose incomplete or corrupted data as valid committed data.",
        "data-integrity invariant drifted",
        errors,
    )

    input_contract = data.get("input_contract", {})
    expect(input_contract.get("source_net") == "VBUS_5V", "input net drifted", errors)
    expect(input_contract.get("usb_role") == "SINK_ONLY", "USB role drifted", errors)
    expect(
        input_contract.get("usb_power_delivery_enabled") is False,
        "USB-PD must remain disabled",
        errors,
    )
    expect(
        input_contract.get("configured_input_ceiling_ma") == 500,
        "configured USB ceiling must be 500 mA",
        errors,
    )
    expect(
        input_contract.get("pre_configuration_target_ma") == 100,
        "pre-configuration target must be 100 mA",
        errors,
    )
    expect(
        input_contract.get("pre_configuration_current_status")
        == "UNKNOWN_REQUIRES_BENCH",
        "pre-configuration current cannot be claimed",
        errors,
    )

    protection = data.get("protection", {})
    expect(
        protection.get("part") == "TPS25942ARVCR",
        "eFuse candidate drifted",
        errors,
    )
    expect(
        protection.get("reverse_current_blocking") is True,
        "hold-up node requires reverse-current blocking",
        errors,
    )
    expect(
        protection.get("mode") == "AUTO_RETRY_NON_IDEAL_DIODE",
        "eFuse must use non-ideal-diode mode",
        errors,
    )
    expect(
        protection.get("dmode_net") == "VBUS_HOLD",
        "DMODE must remain high while hold-up energy remains",
        errors,
    )
    current_limit = protection.get("current_limit", {})
    resistance = float(current_limit.get("program_resistor_kohm", 0))
    normal_limit = float(current_limit.get("normal_mode_nominal_a", 0))
    mode_multiplier = float(current_limit.get("non_ideal_diode_multiplier", 0))
    operating_limit = float(current_limit.get("operating_mode_nominal_a", 0))
    expect(resistance > 0, "current-limit resistor must be positive", errors)
    if resistance > 0:
        expect(
            close(normal_limit, 89.0 / resistance),
            "eFuse normal-mode current-limit equation drifted",
            errors,
        )
    expect(
        close(mode_multiplier, 0.5),
        "eFuse non-ideal-diode multiplier drifted",
        errors,
    )
    expect(
        close(operating_limit, normal_limit * mode_multiplier),
        "eFuse operating-mode current limit drifted",
        errors,
    )
    expect(
        0.25 < operating_limit < 0.5,
        "eFuse operating current limit must stay below the 500 mA USB envelope",
        errors,
    )

    divider = protection.get("uvlo_ovp_divider", {})
    r1 = float(divider.get("r1_kohm", 0))
    r2 = float(divider.get("r2_kohm", 0))
    r3 = float(divider.get("r3_kohm", 0))
    resistor_total = r1 + r2 + r3
    if min(r1, r2, r3) <= 0:
        errors.append("UVLO/OVP divider resistors must be positive")
    else:
        expected_uvlo = 0.99 * resistor_total / (r2 + r3)
        expected_power_fail = 0.92 * resistor_total / (r2 + r3)
        expected_ovp = 0.99 * resistor_total / r3
        expected_ovp_falling = 0.92 * resistor_total / r3
        for key, expected_value in {
            "uvlo_rising_v": expected_uvlo,
            "power_fail_falling_v": expected_power_fail,
            "ovp_rising_v": expected_ovp,
            "ovp_falling_v": expected_ovp_falling,
        }.items():
            expect(
                close(float(divider.get(key, 0)), expected_value),
                f"{key} equation drifted",
                errors,
            )
    expect(
        4.4 < float(divider.get("uvlo_rising_v", 0)) < 4.75,
        "UVLO rising point must accept a valid 5 V USB input",
        errors,
    )
    expect(
        5.5 < float(divider.get("ovp_rising_v", 0)) < 6.0,
        "OVP rising point must protect the 5.5 V buck input boundary",
        errors,
    )

    inrush = protection.get("inrush", {})
    dvdt_f = float(inrush.get("dvdt_capacitance_nf", 0)) * 1e-9
    hold_f = float(inrush.get("hold_capacitance_nominal_uf", 0)) * 1e-6
    ramp_s = 8.3e4 * 5.0 * dvdt_f
    expected_inrush_a = hold_f * 5.0 / ramp_s if ramp_s > 0 else math.inf
    expect(
        close(float(inrush.get("nominal_ramp_ms", 0)), ramp_s * 1e3),
        "eFuse ramp calculation drifted",
        errors,
    )
    expect(
        close(
            float(inrush.get("capacitor_only_inrush_ma", 0)),
            expected_inrush_a * 1e3,
        ),
        "capacitor-only inrush calculation drifted",
        errors,
    )
    expect(
        expected_inrush_a < operating_limit,
        "capacitor-only inrush exceeds the DMODE eFuse current limit",
        errors,
    )

    regulator = data.get("regulator", {})
    expect(
        regulator.get("part") == "TLV62569PDDCR",
        "buck candidate drifted",
        errors,
    )
    expect(regulator.get("output_net") == "3V3", "buck output net drifted", errors)
    expect(
        regulator.get("design_output_ceiling_ma") == 300,
        "3V3 design ceiling must be 300 mA",
        errors,
    )
    expect(
        regulator.get("rated_output_current_a", 0) * 1000
        > regulator.get("design_output_ceiling_ma", 0),
        "buck rating must exceed the design current ceiling",
        errors,
    )
    feedback = regulator.get("feedback", {})
    top = float(feedback.get("top_kohm", 0))
    bottom = float(feedback.get("bottom_kohm", 0))
    output_v = 0.6 * (1 + top / bottom) if bottom > 0 else 0
    expect(
        close(float(feedback.get("nominal_output_v", 0)), output_v),
        "buck feedback equation drifted",
        errors,
    )
    expect(3.25 < output_v < 3.4, "buck output target is outside 3V3 range", errors)
    expect(
        regulator.get("output_capacitance_uf", 0) <= 47,
        "buck output capacitance exceeds the cited stable range",
        errors,
    )
    expect(
        regulator.get("power_good", {}).get("wired_to_run") is True,
        "buck power-good must participate in fail-stop reset",
        errors,
    )

    supervision = data.get("supervision", {})
    expect(supervision.get("run_net") == "RUN", "reset net drifted", errors)
    expect(
        supervision.get("run_policy") == "WIRED_AND_OPEN_DRAIN",
        "reset sources must be wired-AND open drain",
        errors,
    )
    supervisors = supervision.get("sources", [])
    parts = {
        item.get("part"): item
        for item in supervisors
        if isinstance(item, dict)
    }
    for part, net, threshold in (
        ("TLV803EA43DBZR", "VBUS_HOLD", 4.38),
        ("TLV803EA30DBZR", "3V3", 3.08),
    ):
        item = parts.get(part, {})
        expect(bool(item), f"missing supervisor {part}", errors)
        expect(item.get("monitored_net") == net, f"{part} net drifted", errors)
        expect(
            item.get("falling_threshold_nominal_v") == threshold,
            f"{part} threshold drifted",
            errors,
        )
        expect(
            item.get("assertion_delay_max_us") == 50,
            f"{part} assertion budget drifted",
            errors,
        )
        expect(
            item.get("release_delay_nominal_ms") == 200,
            f"{part} release delay drifted",
            errors,
        )
    expect(
        supervision.get("rp2354_internal_bod", {}).get("required_enabled") is True,
        "RP2354 internal BOD must remain enabled",
        errors,
    )
    cs = supervision.get("payload_cs_fail_safe", {})
    expect(cs.get("net") == "PAYLOAD_SPI_CS_N", "payload CS net drifted", errors)
    expect(cs.get("pullup_ohms") == 10000, "payload CS pull-up drifted", errors)
    expect(
        cs.get("required_state_during_reset") == "HIGH_INACTIVE",
        "payload CS reset state must be inactive",
        errors,
    )

    hold_up = data.get("hold_up", {})
    capacitance_f = float(hold_up.get("minimum_effective_capacitance_uf", 0)) * 1e-6
    v_start = float(hold_up.get("supervisor_threshold_worst_low_v", 0))
    v_end = float(hold_up.get("buck_input_floor_v", 0))
    rail_current_a = float(hold_up.get("rail_current_ceiling_ma", 0)) * 1e-3
    rail_voltage_v = float(hold_up.get("rail_voltage_v", 0))
    efficiency = float(hold_up.get("efficiency_floor", 0))
    energy_j = 0.5 * capacitance_f * (v_start**2 - v_end**2)
    input_power_w = rail_voltage_v * rail_current_a / efficiency
    hold_s = energy_j / input_power_w if input_power_w > 0 else 0
    fail_stop_us = float(hold_up.get("total_fail_stop_budget_us", 0))
    expected_budget = float(hold_up.get("supervisor_assertion_budget_us", 0))
    expected_budget += float(hold_up.get("run_to_bus_quiet_budget_us", 0))
    expect(v_start > v_end, "hold-up voltage window must be positive", errors)
    expect(
        close(float(hold_up.get("available_energy_uj", 0)), energy_j * 1e6),
        "hold-up energy calculation drifted",
        errors,
    )
    expect(
        close(float(hold_up.get("calculated_hold_up_us", 0)), hold_s * 1e6),
        "hold-up time calculation drifted",
        errors,
    )
    expect(
        close(fail_stop_us, expected_budget),
        "fail-stop budget components do not sum",
        errors,
    )
    margin = hold_s * 1e6 / fail_stop_us if fail_stop_us > 0 else 0
    expect(
        close(float(hold_up.get("calculated_margin_ratio", 0)), margin, 1e-3),
        "hold-up margin calculation drifted",
        errors,
    )
    expect(margin >= 2.0, "calculated hold-up margin must be at least 2x", errors)
    expect(
        hold_up.get("claim_boundary")
        == "ENERGY_FOR_FAIL_STOP_ONLY_NOT_FLASH_PROGRAM_OR_ERASE_COMPLETION",
        "hold-up claim boundary drifted",
        errors,
    )

    states = {
        item.get("state")
        for item in data.get("state_machine", [])
        if isinstance(item, dict)
    }
    expect(states == REQUIRED_STATES, f"state machine drifted: {states}", errors)
    firmware = data.get("firmware_contract", [])
    expect(
        any("committed" in item for item in firmware),
        "firmware contract lacks commit-integrity rule",
        errors,
    )
    expect(
        any("brownout detector" in item for item in firmware),
        "firmware contract lacks BOD rule",
        errors,
    )

    claims = data.get("evidence_claims", {})
    for label in ("FACT", "DECISION", "EXPECTED", "MEASURED", "UNKNOWN"):
        expect(bool(claims.get(label)), f"missing {label} evidence claim", errors)
    expect(claims.get("MEASURED") == "NONE", "Task 3 cannot claim measurements", errors)
    expect(
        len(data.get("blocking_validation", [])) >= 8,
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
            source.get("retrieved") == "2026-07-27",
            f"sources[{index}] retrieval date drifted",
            errors,
        )
        expect(bool(source.get("supports")), f"sources[{index}] lacks scope", errors)
    return errors


def validate_files(errors: list[str]) -> None:
    budget_rows = read_csv(BUDGET)
    total_rows = [row for row in budget_rows if row["consumer"] == "TOTAL"]
    detail_rows = [row for row in budget_rows if row["consumer"] != "TOTAL"]
    expect(len(total_rows) == 1, "power budget must contain one TOTAL row", errors)
    detail_total = sum(int(row["allocation_ma"]) for row in detail_rows)
    declared_total = int(total_rows[0]["allocation_ma"]) if total_rows else 0
    expect(detail_total == 300, "power budget details must total 300 mA", errors)
    expect(declared_total == detail_total, "power budget TOTAL does not reconcile", errors)
    for row in budget_rows:
        expect(
            row["evidence_status"] == "DECISION",
            f"{row['consumer']} must remain a design decision",
            errors,
        )
        expect(bool(row["validation"]), f"{row['consumer']} lacks validation", errors)

    component_rows = read_csv(COMPONENTS)
    component_parts = {row["manufacturer_part_number"] for row in component_rows}
    for part in (
        "TPS25942ARVCR",
        "TLV62569PDDCR",
        "TLV803EA43DBZR",
        "TLV803EA30DBZR",
    ):
        expect(part in component_parts, f"component candidates missing {part}", errors)
    for row in component_rows:
        expect(
            row["status"] != "FROZEN",
            f"{row['reference']} cannot be procurement-frozen in Task 3",
            errors,
        )
        expect(
            row["procurement_gate"].startswith(("DO_NOT_PURCHASE", "VERIFY_", "SELECT_")),
            f"{row['reference']} lacks a procurement gate",
            errors,
        )

    assumptions = ASSUMPTIONS.read_text(encoding="utf-8")
    for heading in REQUIRED_HEADINGS:
        expect(heading in assumptions, f"assumptions missing {heading}", errors)
    expect("`NONE`" in assumptions, "assumptions must state no measurements", errors)

    checklist = CHECKLIST.read_text(encoding="utf-8")
    expect("Status: `OPEN`." in checklist, "Task 3 checklist must remain open", errors)
    expect(
        "cannot close the gate" in checklist,
        "Task 3 checklist lacks the evidence gate",
        errors,
    )

    try:
        tree = ET.parse(DIAGRAM)
        expect(tree.getroot().tag.endswith("svg"), "power diagram root must be SVG", errors)
    except ET.ParseError as exc:
        errors.append(f"power diagram SVG invalid: {exc}")
    diagram_text = DIAGRAM.read_text(encoding="utf-8")
    for token in (
        "DESIGN ONLY",
        "TPS25942A",
        "VBUS_HOLD",
        "TLV62569P",
        "RP2354A",
        "W25Q256JVEIQ",
        "2.35x",
    ):
        expect(token in diagram_text, f"power diagram missing {token}", errors)

    topology = read_json(TOPOLOGY)
    gates = topology.get("phase_gates", {})
    expect(
        gates.get("task_03_power_safety_passed") is False,
        "topology Task 3 gate must remain false",
        errors,
    )
    authorization = topology.get("authorization", {})
    expect(
        authorization.get("real_hardware_enabled") is False,
        "Task 3 cannot enable real hardware",
        errors,
    )
    expect(
        authorization.get("destructive_storage_writes_enabled") is False,
        "Task 3 cannot enable destructive writes",
        errors,
    )

    schematic = read_json(SCHEMATIC)
    payload = schematic.get("payload_spi", {}).get("device", {})
    expect(
        payload.get("cs_pullup_ohms") == 10000,
        "Task 2 payload CS pull-up handoff drifted",
        errors,
    )
    placeholders = {
        item.get("reference"): item
        for item in schematic.get("deferred_placeholders", [])
        if isinstance(item, dict)
    }
    expect(
        placeholders.get("U2", {}).get("dnp") is True,
        "U2 must remain DNP until Task 3 KiCad capture",
        errors,
    )


def run_self_test(strict: bool) -> list[str]:
    baseline = read_json(CONTRACT)
    failures: list[str] = []
    mutations = [
        ("measurement claim", lambda value: value["evidence_claims"].update(MEASURED="passed")),
        ("premature gate", lambda value: value.update(phase_gate_passed=True)),
        (
            "lost reverse blocking",
            lambda value: value["protection"].update(reverse_current_blocking=False),
        ),
        (
            "insufficient hold-up",
            lambda value: value["hold_up"].update(
                minimum_effective_capacitance_uf=20.0
            ),
        ),
        (
            "unsafe flash select",
            lambda value: value["supervision"]["payload_cs_fail_safe"].update(
                required_state_during_reset="LOW_ACTIVE"
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
        BUDGET,
        COMPONENTS,
        ASSUMPTIONS,
        DIAGRAM,
        CHECKLIST,
        TOPOLOGY,
        SCHEMATIC,
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        for path in missing:
            print(f"ERROR: missing {path}")
        return 1

    contract = read_json(CONTRACT)
    errors = validate_contract(contract, strict=arguments.strict)
    validate_files(errors)
    if arguments.self_test:
        errors.extend(run_self_test(arguments.strict))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    mode = "strict" if arguments.strict else "standard"
    suffix = " with mutation self-test" if arguments.self_test else ""
    print(f"Task 3 power-safety design checks passed ({mode}{suffix}).")
    print("Physical evidence is absent; Task 3 phase gate remains false.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
