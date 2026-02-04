# Flask Log Management System - Windows PowerShell Setup Script
# This script sets up the development environment on Windows

param(
    [switch]$SkipDB = $false
)

Write-Host "Flask Log Management System - Setup Script (Windows)" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.10 or later from https://www.python.org" -ForegroundColor Red
    exit 1
}

$pythonVersion = python --version 2>&1
Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Get the script directory
$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
Write-Host "Working directory: $scriptDir" -ForegroundColor Yellow
Write-Host ""

# Create virtual environment
Write-Host "Step 1: Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path ".\.venv") {
    Write-Host "Virtual environment already exists" -ForegroundColor Gray
} else {
    Write-Host "Creating .venv..."
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}
Write-Host ""

# Activate virtual environment
Write-Host "Step 2: Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Install requirements
Write-Host "Step 3: Installing requirements..." -ForegroundColor Yellow
pip install -q -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install requirements" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Requirements installed successfully" -ForegroundColor Green
Write-Host ""

# Initialize database
if ($SkipDB) {
    Write-Host "Step 4: Skipping database initialization (--SkipDB flag used)" -ForegroundColor Yellow
} else {
    Write-Host "Step 4: Initializing database..." -ForegroundColor Yellow
    python app.py --init-db
    if ($LASTEXITCODE -ne 0) {
        Write-Host "WARNING: Database initialization may not have completed cleanly" -ForegroundColor Yellow
    } else {
        Write-Host "✓ Database initialized" -ForegroundColor Green
    }
}
Write-Host ""

# Display next steps
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. To activate the virtual environment in future sessions:" -ForegroundColor Gray
Write-Host "   .\.venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. To start the development server:" -ForegroundColor Gray
Write-Host "   python app.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. To run tests:" -ForegroundColor Gray
Write-Host "   pytest test_app.py -v" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Server will be available at:" -ForegroundColor Gray
Write-Host "   http://127.0.0.1:5000" -ForegroundColor Cyan
Write-Host ""
