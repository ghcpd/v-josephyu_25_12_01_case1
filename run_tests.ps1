# PowerShell script to run pytest
Write-Host "Activating virtual environment and running tests..."
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    . .\.venv\Scripts\Activate.ps1
}
pytest -q
