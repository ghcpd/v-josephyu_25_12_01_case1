#!/usr/bin/env bash
set -euo pipefail

if [[ ! -d .venv ]]; then
  echo ".venv not found. Running setup.sh..."
  chmod +x setup.sh
  ./setup.sh
fi

. .venv/bin/activate
pytest -q test_files
