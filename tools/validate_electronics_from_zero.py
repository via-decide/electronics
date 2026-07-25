#!/usr/bin/env python3
"""Validate the Electronics From Zero curriculum without external packages."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRACK = ROOT / "learning-tracks/electronics-from-zero"
PROJECT_ROOTS = [ROOT / "projects/breadboard", ROOT / "projects/buses", ROOT / "projects/storage"]
EXPECTED_PROJECTS = {
    "01-know-your-breadboard",
    "02-led-current",
    "03-button-input",
    "04-mosfet-load-switch",
    "05-analog-voltage",
    "06-uart-conversation",
    "07-i2c-sensor",
    "08-spi-shift-register",
    "09-spi-eeprom",
    "10-spi-nor-mini-storage",
}
FIRMWARE_PROJECTS = EXPECTED_PROJECTS - {"01-know-your-breadboard", "02-led-current"}
CONTRACT = {
    "PROJECT.md",
    "WHY.md",
    "BUY.md",
    "WIRING.md",
    "BUILD.md",
    "CODE/README.md",
    "EXPECTED.md",
    "BEFORE-YOU-POWER.md",
    "BREAK-IT.md",
    "DEBUG.md",
    "MEASURE.md",
    "WHAT-YOU-LEARNED.md",
    "NEXT.md",
    "project.yaml",
    "bom.csv",
    "pinmap.yaml",
    "constraints.yaml",
    "decisions/README.md",
    "validation/checklist.md",
    "validation/expected-results.json",
    "evidence/README.md",
    "evidence/measurement-template.csv",
    "HARDWARE-VALIDATION-REQUIRED.md",
}
BOM_COLUMNS = [
    "item_id",
    "category",
    "description",
    "manufacturer",
    "manufacturer_part_number",
    "package",
    "quantity",
    "required_or_optional",
    "verified_or_suggested",
    "supply_voltage",
    "india_search_name",
    "substitution_rule",
    "source_url",
    "retrieved_at",
    "notes",
]
PROJECT_KEYS = {
    "schemaVersion",
    "projectId",
    "title",
    "difficulty",
    "estimatedMinutes",
    "primaryBoard",
    "supplyVoltage",
    "requiredTools",
    "requiredKits",
    "interfaces",
    "prerequisites",
    "learningOutcomes",
    "blockingSafetyChecks",
    "sourceReferences",
    "hardwareValidationStatus",
}
PATH_LABELS = {
    "**Need:**",
    "**Install:**",
    "**Build first:**",
    "**Success:**",
    "**Common mistake:**",
    "**Next:**",
    "**Effort:**",
    "**Safety:**",
    "**Tools:**",
}
LESSON_HEADINGS = {
    "## 1. Physical problem this lesson solves",
    "## 2. What you need to know first",
    "## 3. Components required",
    "## 4. What you will build",
    "## 5. What you will measure",
    "## 6. Minimum theory",
    "## 7. Physical explanation",
    "## 8. Common misconceptions",
    "## 9. Common wiring mistakes",
    "## 10. Linked project",
    "## 11. Success condition",
    "## 12. Next lesson",
    "## 13. Primary references",
    "## 14. Facts, expected results and required measurements",
}


def yaml_top_keys(text: str) -> set[str]:
    return {
        match.group(1)
        for line in text.splitlines()
        if (match := re.match(r"^([A-Za-z][A-Za-z0-9_-]*):", line))
    }


def project_dirs() -> list[Path]:
    return sorted(
        path
        for root in PROJECT_ROOTS
        if root.exists()
        for path in root.iterdir()
        if path.is_dir() and re.match(r"^\d\d-", path.name)
    )


def validate() -> list[str]:
    errors: list[str] = []
    start = (ROOT / "START-HERE.md").read_text(encoding="utf-8")
    if not start.startswith("# You have an ESP32 or RP2040, a breadboard and some wires. Start here."):
        errors.append("START-HERE.md does not begin with the frozen learner-facing sentence")
    path_sections = re.split(r"^## Path [A-E] — ", start, flags=re.MULTILINE)[1:]
    if len(path_sections) != 5:
        errors.append(f"START-HERE.md must contain five entry paths, found {len(path_sections)}")
    for label, section in zip("ABCDE", path_sections):
        missing_labels = {item for item in PATH_LABELS if item not in section}
        if missing_labels:
            errors.append(f"START-HERE.md Path {label} missing labels: {sorted(missing_labels)}")
    for path_name in [
        "docs/research/electronics-from-zero-repository-audit.md",
        "docs/research/electronics-from-zero-source-ledger.md",
        "docs/research/component-selection-ledger.md",
        "docs/research/curriculum-dependency-graph.md",
        "docs/research/safety-boundary.md",
        "docs/research/board-selection-decision.md",
    ]:
        if not (ROOT / path_name).is_file():
            errors.append(f"missing research file: {path_name}")

    lessons = sorted(TRACK.glob("[0-2][0-9]-*.md"))
    if len(lessons) != 21:
        errors.append(f"expected 21 numbered lessons, found {len(lessons)}")
    for lesson in lessons:
        text = lesson.read_text(encoding="utf-8")
        missing = LESSON_HEADINGS - set(text.splitlines())
        if missing:
            errors.append(f"{lesson.relative_to(ROOT)} missing lesson sections: {sorted(missing)}")

    template = ROOT / "templates/physical-project"
    template_missing = [name for name in CONTRACT - {"HARDWARE-VALIDATION-REQUIRED.md"} if not (template / name).is_file()]
    if template_missing:
        errors.append(f"physical-project template missing files: {template_missing}")
    template_project = (template / "project.yaml").read_text(encoding="utf-8")
    template_keys = PROJECT_KEYS - yaml_top_keys(template_project)
    if template_keys:
        errors.append(f"physical-project template project.yaml missing {sorted(template_keys)}")

    kit_expectations = {
        "kit-00-basic-electronics.csv": {
            "ESP32-DEVKITC-32E", "P2N2222AG", "AO3400A", "CMI-1295IC-0385T",
        },
        "kit-01-digital-buses.csv": {
            "CP2102N Friend, Adafruit product 5335", "TMP117AIDRVR on Adafruit product 4821",
            "PCA9306DCTR", "SN74HC595N",
        },
        "kit-02-storage-lab.csv": {
            "25LC256-I/P", "MX25L3233FM2I-08G", "W25N01JWZEIQ + TPS7A20-1V8",
        },
        "kit-03-cartridge-prototype.csv": {
            "MX25L3233FM2I-08G", "TPD4E05U06DQAR",
        },
    }
    for kit_name, expected_mpns in kit_expectations.items():
        kit_path = ROOT / "hardware/kits" / kit_name
        if not kit_path.is_file():
            errors.append(f"missing shared kit: {kit_name}")
            continue
        with kit_path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != BOM_COLUMNS:
                errors.append(f"{kit_path.relative_to(ROOT)} has wrong columns")
                continue
            actual_mpns = {row["manufacturer_part_number"] for row in reader}
            if not expected_mpns.issubset(actual_mpns):
                errors.append(
                    f"{kit_path.relative_to(ROOT)} missing exact parts: "
                    f"{sorted(expected_mpns-actual_mpns)}"
                )

    projects = project_dirs()
    actual_names = {path.name for path in projects}
    if actual_names != EXPECTED_PROJECTS:
        errors.append(
            f"project set mismatch; missing={sorted(EXPECTED_PROJECTS-actual_names)} "
            f"extra={sorted(actual_names-EXPECTED_PROJECTS)}"
        )
    for project in projects:
        missing = [name for name in CONTRACT if not (project / name).is_file()]
        if missing:
            errors.append(f"{project.relative_to(ROOT)} missing contract files: {missing}")
            continue
        project_yaml = (project / "project.yaml").read_text(encoding="utf-8")
        missing_keys = PROJECT_KEYS - yaml_top_keys(project_yaml)
        if missing_keys:
            errors.append(f"{project.relative_to(ROOT)}/project.yaml missing {sorted(missing_keys)}")
        if "hardwareValidationStatus: HARDWARE_VALIDATION_REQUIRED" not in project_yaml:
            errors.append(f"{project.relative_to(ROOT)} does not preserve hardware evidence status")
        for markdown in project.rglob("*.md"):
            text = markdown.read_text(encoding="utf-8")
            unresolved = re.findall(r"\{[a-z_][a-z0-9_]*\}", text)
            if unresolved:
                errors.append(
                    f"{markdown.relative_to(ROOT)} has unresolved generator fields: {sorted(set(unresolved))}"
                )
        before_power = (project / "BEFORE-YOU-POWER.md").read_text(encoding="utf-8")
        if "## Project-specific blocking checks" not in before_power:
            errors.append(f"{project.relative_to(ROOT)} missing project-specific power checks")
        expected_text = (project / "EXPECTED.md").read_text(encoding="utf-8")
        for required in [
            "## FACT", "## EXPECTED", "## MEASURED", "**Serial/output pattern:**",
            "**Voltage and logic range:**", "**Current:**", "**State transition:**",
            "**Calculation assumptions:**", "**Tolerance:**",
        ]:
            if required not in expected_text:
                errors.append(f"{project.relative_to(ROOT)}/EXPECTED.md missing {required}")

        with (project / "bom.csv").open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != BOM_COLUMNS:
                errors.append(f"{project.relative_to(ROOT)}/bom.csv has wrong columns")
            for row in reader:
                if row["source_url"] and not row["source_url"].startswith("https://"):
                    errors.append(f"{project.relative_to(ROOT)}/bom.csv contains non-HTTPS source")
                if row["verified_or_suggested"] not in {"verified", "suggested"}:
                    errors.append(f"{project.relative_to(ROOT)}/bom.csv has invalid selection status")

        result = json.loads(
            (project / "validation/expected-results.json").read_text(encoding="utf-8")
        )
        if result.get("hardwareValidationStatus") != "HARDWARE_VALIDATION_REQUIRED":
            errors.append(f"{project.relative_to(ROOT)} expected result fabricates validation")
        if any(item.get("measured") is not None for item in result.get("results", [])):
            errors.append(f"{project.relative_to(ROOT)} contains fabricated measured result")

        pinmap = (project / "pinmap.yaml").read_text(encoding="utf-8")
        test_points = set(re.findall(r"testPoint:\s*(TP\d+)", pinmap))
        asset = ROOT / "assets/projects" / project.name
        for svg_name in ["breadboard.svg", "schematic.svg"]:
            svg = (asset / svg_name).read_text(encoding="utf-8")
            if not test_points or not test_points.issubset(set(re.findall(r"TP\d+", svg))):
                errors.append(f"{asset.relative_to(ROOT)}/{svg_name} disagrees with pinmap test points")
        for fake in ["assembled-front.jpg", "assembled-top.jpg", "logic-capture.png", "meter-reading.jpg"]:
            if (asset / fake).exists():
                errors.append(f"fabricated or unreviewed physical asset exists: {asset/fake}")
        if not (asset / "PHOTO-REQUIRED.md").is_file():
            errors.append(f"{asset.relative_to(ROOT)} missing PHOTO-REQUIRED.md")
        if not (asset / "CAPTURE-REQUIRED.md").is_file():
            errors.append(f"{asset.relative_to(ROOT)} missing CAPTURE-REQUIRED.md")

        if project.name in FIRMWARE_PROJECTS:
            for code_file in ["CODE/CMakeLists.txt", "CODE/main/CMakeLists.txt", "CODE/main/main.c"]:
                if not (project / code_file).is_file():
                    errors.append(f"{project.relative_to(ROOT)} missing firmware {code_file}")
        if project.name == "01-know-your-breadboard" and not (
            project / "evidence/breadboard-map-template.csv"
        ).is_file():
            errors.append(f"{project.relative_to(ROOT)} missing breadboard mapping evidence template")

    link_roots = [
        ROOT / "START-HERE.md",
        ROOT / "learning-tracks/electronics-from-zero",
        ROOT / "projects/breadboard",
        ROOT / "projects/buses",
        ROOT / "projects/storage",
        ROOT / "hardware/kits",
        ROOT / "docs/research",
    ]
    markdown_files: list[Path] = []
    for item in link_roots:
        markdown_files.extend([item] if item.is_file() else item.rglob("*.md"))
    for markdown in markdown_files:
        text = markdown.read_text(encoding="utf-8")
        for raw_link in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
            link = raw_link.split()[0].split("#", 1)[0]
            if not link or link.startswith(("https://", "http://", "mailto:")):
                continue
            target = (markdown.parent / link).resolve()
            if not target.exists():
                errors.append(
                    f"{markdown.relative_to(ROOT)} has broken relative link: {raw_link}"
                )

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Electronics From Zero validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        "Electronics From Zero validation passed: "
        "21 lessons, 10 projects, contract/schema/assets/evidence checks complete"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
