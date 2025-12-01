#!/usr/bin/env bash
set -euo pipefail

RECREATE=0
if [[ "${1-}" == "--recreate" ]]; then RECREATE=1; fi

PYTHON=$(command -v python3 || command -v python || true)
if [[ -z "$PYTHON" ]]; then
  echo "Python 3 is required but was not found on PATH." >&2
  exit 1
fi

if [[ $RECREATE -eq 1 && -d .venv ]]; then
  echo "Recreating virtual environment..."
  rm -rf .venv
fi

if [[ ! -d .venv ]]; then
  echo "Creating virtual environment .venv..."
  "$PYTHON" -m venv .venv
fi

VENV_PY=".venv/bin/python"
"$VENV_PY" -m pip install --upgrade pip
"$VENV_PY" -m pip install -r requirements.txt

echo "Environment ready. Activate with: source .venv/bin/activate"
