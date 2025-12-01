# Test runner script for Flask Log Management System (Windows PowerShell)
# This script runs pytest tests with coverage reporting

Write-Host "Flask Log Management System - Test Runner" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "ERROR: Virtual environment not found. Run setup.ps1 first." -ForegroundColor Red
    exit 1
}

# Check if pytest is installed
Write-Host "Checking pytest installation..." -ForegroundColor Yellow
try {
    $pytestVersion = .\.venv\Scripts\pytest.exe --version 2>&1
    Write-Host "Found: $pytestVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: pytest not installed. Run setup.ps1 first." -ForegroundColor Red
    exit 1
}

# Clean up old test database
Write-Host "Cleaning up old test files..." -ForegroundColor Yellow
Remove-Item -ErrorAction SilentlyContinue test_files\test_data.db
Remove-Item -ErrorAction SilentlyContinue test_files\logs.csv
Write-Host "Cleanup complete" -ForegroundColor Green

# Run tests
Write-Host ""
Write-Host "Running tests..." -ForegroundColor Yellow
Write-Host ""

.\.venv\Scripts\pytest.exe test_files\ -v --tb=short --color=yes

$testExitCode = $LASTEXITCODE

Write-Host ""
if ($testExitCode -eq 0) {
    Write-Host "All tests passed!" -ForegroundColor Green
} else {
    Write-Host "Some tests failed. See output above for details." -ForegroundColor Red
}

# Clean up test artifacts
Write-Host ""
Write-Host "Cleaning up test artifacts..." -ForegroundColor Yellow
Remove-Item -ErrorAction SilentlyContinue test_files\test_data.db
Remove-Item -ErrorAction SilentlyContinue test_files\logs.csv
Remove-Item -ErrorAction SilentlyContinue -Recurse test_files\__pycache__
Remove-Item -ErrorAction SilentlyContinue -Recurse test_files\.pytest_cache

Write-Host ""
Write-Host "Test run complete!" -ForegroundColor Cyan
Write-Host ""

exit $testExitCode
