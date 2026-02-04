$ErrorActionPreference = 'Stop'

if (-not (Test-Path '.venv')) {
    Write-Host '.venv not found. Running setup.ps1...'
    ./setup.ps1
}

$venvPython = Join-Path (Resolve-Path '.venv').Path 'Scripts/python.exe'
& $venvPython -m pytest -q test_files
