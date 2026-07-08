#!/usr/bin/env bash
set -euo pipefail

repo="via-decide/electronics"
board="esp32"
framework="arduino,esp-idf"
domains="core,peripherals,rtos,power,dma,networking,security,industrial,edge"
matrix="tasks/esp32/validation_matrix.yaml"
report="reports/esp32_master_validation.md"

for arg in "$@"; do
  case "$arg" in
    --repo=*) repo="${arg#*=}" ;;
    --board=*) board="${arg#*=}" ;;
    --framework=*) framework="${arg#*=}" ;;
    --domains=*) domains="${arg#*=}" ;;
    --validation_matrix=*) matrix="${arg#*=}" ;;
    --report=*) report="${arg#*=}" ;;
    *) printf 'unknown argument: %s\n' "$arg" >&2; exit 2 ;;
  esac
done

if [[ ! -f "$matrix" ]]; then
  printf 'validation matrix not found: %s\n' "$matrix" >&2
  exit 1
fi

mkdir -p "$(dirname "$report")"

python3 - "$repo" "$board" "$framework" "$domains" "$matrix" "$report" <<'PY'
from __future__ import annotations
import re
import sys
from pathlib import Path

repo, board, framework, domains, matrix_path, report_path = sys.argv[1:]
root = Path('.')
text = Path(matrix_path).read_text()
master = re.search(r'^validation_id: (.+)$', text, re.M).group(1)
status = re.search(r'^status: (.+)$', text, re.M).group(1)

entries = []
parts = re.split(r'\n    - id: ', text)
for part in parts[1:]:
    entry = {'id': part.split('\n', 1)[0].strip()}
    for key in ('phase', 'source_files', 'task_file', 'test_method', 'required_hardware', 'pass_metric'):
        m = re.search(rf'\n      {key}: (.*)', part)
        if not m:
            raise SystemExit(f"missing {key} for {entry['id']}")
        entry[key] = m.group(1).strip()
    raw_sources = entry['source_files'].strip()
    if not (raw_sources.startswith('[') and raw_sources.endswith(']')):
        raise SystemExit(f"invalid source_files for {entry['id']}: {raw_sources}")
    entry['source_list'] = [item.strip().strip('\"\'') for item in raw_sources[1:-1].split(',') if item.strip()]
    entries.append(entry)

failures = []
for entry in entries:
    if not (root / entry['task_file']).is_file():
        failures.append(f"missing task file for {entry['id']}: {entry['task_file']}")
    for src in entry['source_list']:
        if not (root / src).exists():
            failures.append(f"missing mapped source for {entry['id']}: {src}")

required_docs = [
    'README.md', 'docs/README.md', 'docs/theory.md', 'docs/implementation.md',
    'docs/debugging.md', 'docs/production.md', 'docs/benchmarks.md',
    'docs/references.md', 'docs/roadmap.md', 'docs/glossary.md', 'docs/faq.md',
]
for doc in required_docs:
    if not (root / doc).is_file():
        failures.append(f"missing repository documentation: {doc}")

report = []
report.append('# ESP32 Master Architecture Validation Report')
report.append('')
report.append(f'- Repository: `{repo}`')
report.append(f'- Board: `{board}`')
report.append(f'- Frameworks: `{framework}`')
report.append(f'- Domains: `{domains}`')
report.append(f'- Validation matrix: `{matrix_path}`')
report.append(f'- Validation ID: `{master}`')
report.append(f'- Status: `{status}`')
report.append(f'- Task count: `{len(entries)}`')
report.append(f'- Matrix consistency: `{"FAIL" if failures else "PASS"}`')
report.append('')
report.append('## Validation Matrix')
report.append('')
report.append('| Phase | Validation ID | Task file | Source mapping | Test method | Pass metric |')
report.append('| --- | --- | --- | --- | --- | --- |')
for entry in entries:
    sources = '<br>'.join(f'`{src}`' for src in entry['source_list'])
    report.append(f"| {entry['phase']} | `{entry['id']}` | `{entry['task_file']}` | {sources} | {entry['test_method']} | {entry['pass_metric']} |")
report.append('')
report.append('## Consistency Checks')
report.append('')
if failures:
    for failure in failures:
        report.append(f'- FAIL: {failure}')
else:
    report.append('- PASS: every validation ID has a task file.')
    report.append('- PASS: every mapped source/documentation path exists.')
    report.append('- PASS: repository-level documentation hierarchy exists.')
report.append('')
report.append('## Hardware Execution Status')
report.append('')
report.append('This generated report verifies repository structure and validation traceability. Hardware execution remains pending until the required boards, instruments, networks, credentials, displays, motor fixtures, CAN bus, and audio/ML fixtures are attached and each task procedure is executed.')

Path(report_path).write_text('\n'.join(report) + '\n')
if failures:
    raise SystemExit('\n'.join(failures))
PY

printf 'generated %s\n' "$report"
