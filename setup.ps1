param(
    [switch]$Recreate
)

$ErrorActionPreference = 'Stop'

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command python3 -ErrorAction SilentlyContinue }
if (-not $python) { throw 'Python 3 is required but was not found on PATH.' }

if ($Recreate -and (Test-Path '.venv')) {
    Write-Host 'Recreating virtual environment...'
    Remove-Item -Recurse -Force '.venv'
}

if (-not (Test-Path '.venv')) {
    Write-Host 'Creating virtual environment .venv...'
    & $python.Source -m venv .venv
}

$venvPython = Join-Path (Resolve-Path '.venv').Path 'Scripts/python.exe'

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt

Write-Host "Environment ready. Activate with:`n .\\.venv\\Scripts\\Activate.ps1"
