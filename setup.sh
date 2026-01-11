#!/usr/bin/env bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py --init-db
echo "Environment setup complete. Activate with: source .venv/bin/activate"
