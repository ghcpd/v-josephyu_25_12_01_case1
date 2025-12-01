# PowerShell run tests script
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

.\.venv\Scripts\Activate.ps1

python -m pytest -q
