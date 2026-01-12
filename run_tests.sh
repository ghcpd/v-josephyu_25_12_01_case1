#!/bin/bash
# Test runner script for Flask Log Management System (Linux/macOS)
# This script runs pytest tests with coverage reporting

echo -e "\033[0;36mFlask Log Management System - Test Runner\033[0m"
echo -e "\033[0;36m==========================================\033[0m"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "\033[0;31mERROR: Virtual environment not found. Run setup.sh first.\033[0m"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if pytest is installed
echo -e "\033[0;33mChecking pytest installation...\033[0m"
if command -v pytest &> /dev/null; then
    PYTEST_VERSION=$(pytest --version)
    echo -e "\033[0;32mFound: $PYTEST_VERSION\033[0m"
else
    echo -e "\033[0;31mERROR: pytest not installed. Run setup.sh first.\033[0m"
    exit 1
fi

# Clean up old test database
echo -e "\033[0;33mCleaning up old test files...\033[0m"
rm -f test_files/test_data.db
rm -f test_files/logs.csv
echo -e "\033[0;32mCleanup complete\033[0m"

# Run tests
echo ""
echo -e "\033[0;33mRunning tests...\033[0m"
echo ""

pytest test_files/ -v --tb=short --color=yes

TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "\033[0;32mAll tests passed!\033[0m"
else
    echo -e "\033[0;31mSome tests failed. See output above for details.\033[0m"
fi

# Clean up test artifacts
echo ""
echo -e "\033[0;33mCleaning up test artifacts...\033[0m"
rm -f test_files/test_data.db
rm -f test_files/logs.csv
rm -rf test_files/__pycache__
rm -rf test_files/.pytest_cache

echo ""
echo -e "\033[0;36mTest run complete!\033[0m"
echo ""

exit $TEST_EXIT_CODE
