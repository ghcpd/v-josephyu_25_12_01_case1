# PowerShell setup script for the Flask Log Management System
# Run from project root

# Allow script execution for this session
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# Create and activate venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Initialize DB
python app.py --init-db

Write-Host "Setup complete. Run the app with: python app.py"
