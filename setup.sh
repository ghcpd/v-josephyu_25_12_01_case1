#!/usr/bin/env bash
# Bash setup script for Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py --init-db

echo "Database initialized: data.db in application directory"
