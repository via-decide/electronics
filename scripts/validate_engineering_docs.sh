#!/usr/bin/env bash
set -euo pipefail

required_paths=(
  README.md
  docs/README.md
  docs/theory.md
  docs/implementation.md
  docs/debugging.md
  docs/production.md
  docs/benchmarks.md
  docs/references.md
  docs/roadmap.md
  docs/glossary.md
  docs/faq.md
  docs/documentation_generation.md
  docs/esp32/master_architecture_validation.md
  examples/README.md
  examples/esp32
  examples/esp32/adc_dma/README.md
  examples/esp32/freertos/README.md
  examples/esp32/mqtt/README.md
  examples/esp32/ota/README.md
  examples/esp32/deep_sleep/README.md
  examples/esp32/i2c/README.md
  examples/esp32/timers/README.md
  examples/stm32/README.md
  examples/raspberry-pi/README.md
  examples/linux/README.md
  examples/power-electronics/README.md
  tests/README.md
  tests/unit/README.md
  tests/integration/README.md
  tests/hardware/README.md
  tests/hardware-validation/README.md
  tests/performance/README.md
  tests/stress/README.md
  diagrams/README.md
  diagrams/architecture/README.md
  diagrams/architecture/esp32_platform_architecture.md
  diagrams/timing/README.md
  diagrams/timing/interrupt_to_worker_timing.md
  diagrams/pcb/README.md
  diagrams/pcb/power_architecture.md
  diagrams/signal-flow/README.md
  diagrams/signal-flow/adc_dma_pipeline.md
  diagrams/state-machines/README.md
  diagrams/state-machines/ota_lifecycle.md
  assets/README.md
  assets/images/README.md
  assets/oscilloscope/README.md
  assets/logic-analyzer/README.md
  assets/thermal/README.md
  assets/pcb/README.md
  assets/photos/README.md
  hardware/README.md
  projects/README.md
  tasks/esp32/README.md
  tasks/esp32/validation_matrix.yaml
  tasks/esp32/run_master_validation.sh
  reports/esp32_master_validation.md
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
  if ! rg -q "$marker" docs README.md; then
    printf 'missing required documentation marker: %s\n' "$marker" >&2
    missing=1
  fi
done

if find examples tests diagrams assets -name .gitkeep -print -quit | rg -q .; then
  printf 'placeholder .gitkeep files remain under examples/tests/diagrams/assets; use meaningful README.md files instead\n' >&2
  missing=1
fi

exit "$missing"
