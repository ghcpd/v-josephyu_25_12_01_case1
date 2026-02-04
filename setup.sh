#!/usr/bin/env bash
set -e

# Create and activate venv
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Initialize DB
python3 app.py --init-db

echo "Setup complete. Run the app with: python3 app.py"
