#!/usr/bin/env bash
set -euo pipefail
manifest="artifacts/build-manifest.json"
clean=0
while [[ $# -gt 0 ]]; do case "$1" in --emit-manifest) manifest="$2"; shift 2;; --clean) clean=1; shift;; --profile) shift 2;; *) echo "unknown $1"; exit 2;; esac; done
[[ $clean == 1 ]] && rm -rf build artifacts
mkdir -p "$(dirname "$manifest")"
python3 tools/check_repository.py --strict
python3 tools/validate_platform.py hardware/platforms/w25n01jw_lab/platform.yaml --strict
python3 tools/validate_hardware_evidence.py assets/evidence --strict
cmake --preset host
cmake --build --preset host
ctest --preset host --output-on-failure
python3 -m pytest simulator/ssd/tests
python3 tools/generate_hardware_report.py --platform hardware/platforms/w25n01jw_lab/platform.yaml --evidence assets/evidence --out artifacts/hardware-report.json
python3 tools/check_repository.py --emit-manifest "$manifest" build/host artifacts/hardware-report.json
