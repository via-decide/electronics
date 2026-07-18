#!/usr/bin/env bash
set -euo pipefail
if ! python3 -m pip install -r requirements.lock; then
  echo "warning: dependency installation failed; continuing with checked-in fallbacks and preinstalled tools" >&2
fi
cmake --version >/dev/null
python3 --version >/dev/null
