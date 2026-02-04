#!/bin/bash

# Flask Log Management System - Linux/macOS Test Runner
# This script runs the pytest test suite

set -e

VERBOSE=false
COVERAGE=false
TEST_FILE="test_app.py"

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        --test-file)
            TEST_FILE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "Flask Log Management System - Test Runner (Linux/macOS)"
echo "======================================================="
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "ERROR: Virtual environment not found"
    echo "Please run setup.sh first"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate
echo ""

# Build pytest command
PYTEST_ARGS=("$TEST_FILE")

if [ "$VERBOSE" = true ]; then
    PYTEST_ARGS+=("-v")
    echo "Running tests in verbose mode..."
else
    echo "Running tests..."
fi

if [ "$COVERAGE" = true ]; then
    PYTEST_ARGS+=("--cov=.")
    PYTEST_ARGS+=("--cov-report=html")
    PYTEST_ARGS+=("--cov-report=term-missing")
    echo "Coverage reporting enabled"
fi

echo ""

# Run pytest
python -m pytest "${PYTEST_ARGS[@]}"
EXIT_CODE=$?

echo ""
echo "======================================================="

if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ All tests passed!"
else
    echo "✗ Tests failed with exit code: $EXIT_CODE"
fi

if [ "$COVERAGE" = true ] && [ $EXIT_CODE -eq 0 ]; then
    echo "✓ Coverage report generated: htmlcov/index.html"
fi

echo "======================================================="
echo ""

exit $EXIT_CODE
