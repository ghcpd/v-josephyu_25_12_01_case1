# PowerShell setup script for Windows
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# initialize DB
python app.py --init-db
Write-Host "Environment setup complete. Activate with: .\.venv\Scripts\Activate.ps1"
