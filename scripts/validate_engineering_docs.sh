#!/usr/bin/env bash
set -euo pipefail

required_paths=(
  docs/theory.md
  docs/implementation.md
  docs/debugging.md
  docs/production.md
  docs/benchmarks.md
  docs/references.md
  docs/documentation_generation.md
  examples/README.md
  examples/minimal
  examples/production
  examples/advanced
  tests/README.md
  tests/unit
  tests/integration
  tests/stress
  tests/hardware_validation
  diagrams/README.md
  diagrams/architecture
  diagrams/state_machine
  diagrams/data_flow
  diagrams/timing
  diagrams/pcb
  assets/README.md
  assets/images
  assets/oscilloscope
  assets/logic_analyzer
  assets/datasheets
  assets/captures
)

missing=0
for path in "${required_paths[@]}"; do
  if [[ ! -e "$path" ]]; then
    printf 'missing required engineering knowledge path: %s\n' "$path" >&2
    missing=1
  fi
done

required_markers=(
  engineering_learning_repository_structure_v1
  ENGINEERING_KNOWLEDGE_BASE_STANDARDIZED
)
for marker in "${required_markers[@]}"; do
  if ! rg -q "$marker" docs; then
    printf 'missing required documentation marker: %s\n' "$marker" >&2
    missing=1
  fi
done

exit "$missing"
