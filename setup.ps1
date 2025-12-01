# Setup script for Flask Log Management System (Windows PowerShell)
# This script sets up the virtual environment and installs dependencies

Write-Host "Flask Log Management System - Setup Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Remove existing .venv if it exists
if (Test-Path ".venv") {
    Write-Host "Removing existing .venv directory..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force .venv
}

# Create virtual environment
Write-Host "Creating virtual environment (.venv)..." -ForegroundColor Yellow
python -m venv .venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
    exit 1
}
Write-Host "Virtual environment created successfully" -ForegroundColor Green

# Check execution policy
$executionPolicy = Get-ExecutionPolicy -Scope CurrentUser
if ($executionPolicy -eq "Restricted" -or $executionPolicy -eq "AllSigned") {
    Write-Host "WARNING: Execution policy is restrictive. Attempting to change..." -ForegroundColor Yellow
    try {
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Write-Host "Execution policy updated successfully" -ForegroundColor Green
    } catch {
        Write-Host "WARNING: Could not change execution policy. You may need to run:" -ForegroundColor Yellow
        Write-Host "  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    }
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
.\.venv\Scripts\pip.exe install --upgrade pip
.\.venv\Scripts\pip.exe install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "Dependencies installed successfully" -ForegroundColor Green

# Clean up old database and CSV files
Write-Host "Cleaning up old data files..." -ForegroundColor Yellow
Remove-Item -ErrorAction SilentlyContinue data.db
Remove-Item -ErrorAction SilentlyContinue logs.csv
Write-Host "Cleanup complete" -ForegroundColor Green

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To start the application, run:" -ForegroundColor Cyan
Write-Host "  .\.venv\Scripts\python.exe app.py" -ForegroundColor White
Write-Host ""
Write-Host "To run tests, run:" -ForegroundColor Cyan
Write-Host "  .\run_tests.ps1" -ForegroundColor White
Write-Host ""
