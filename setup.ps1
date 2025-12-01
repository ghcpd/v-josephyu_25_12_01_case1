# PowerShell setup script for Windows
# Creates virtual env, installs dependencies, initializes DB

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py --init-db
Write-Host "Database initialized: data.db in application directory"