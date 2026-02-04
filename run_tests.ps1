# Flask Log Management System - Windows PowerShell Test Runner
# This script runs the pytest test suite

param(
    [switch]$Verbose = $false,
    [switch]$Coverage = $false,
    [string]$TestFile = "test_app.py"
)

Write-Host "Flask Log Management System - Test Runner (Windows)" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".\.venv")) {
    Write-Host "ERROR: Virtual environment not found" -ForegroundColor Red
    Write-Host "Please run setup.ps1 first" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"
Write-Host ""

# Build pytest command
$pytestArgs = @($TestFile)

if ($Verbose) {
    $pytestArgs += "-v"
    Write-Host "Running tests in verbose mode..." -ForegroundColor Yellow
} else {
    Write-Host "Running tests..." -ForegroundColor Yellow
}

if ($Coverage) {
    $pytestArgs += "--cov=." 
    $pytestArgs += "--cov-report=html"
    $pytestArgs += "--cov-report=term-missing"
    Write-Host "Coverage reporting enabled" -ForegroundColor Yellow
}

Write-Host ""

# Run pytest
python -m pytest @pytestArgs

$exitCode = $LASTEXITCODE

Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan

if ($exitCode -eq 0) {
    Write-Host "✓ All tests passed!" -ForegroundColor Green
} else {
    Write-Host "✗ Tests failed with exit code: $exitCode" -ForegroundColor Red
}

if ($Coverage -and $exitCode -eq 0) {
    Write-Host "✓ Coverage report generated: htmlcov/index.html" -ForegroundColor Green
}

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

exit $exitCode
