#!/bin/bash
# Setup script for Flask Log Management System (Linux/macOS)
# This script sets up the virtual environment and installs dependencies

echo -e "\033[0;36mFlask Log Management System - Setup Script\033[0m"
echo -e "\033[0;36m==========================================\033[0m"
echo ""

# Check if Python is available
echo -e "\033[0;33mChecking Python installation...\033[0m"
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    PYTHON_VERSION=$(python3 --version)
    echo -e "\033[0;32mFound: $PYTHON_VERSION\033[0m"
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
    PYTHON_VERSION=$(python --version)
    echo -e "\033[0;32mFound: $PYTHON_VERSION\033[0m"
else
    echo -e "\033[0;31mERROR: Python is not installed or not in PATH\033[0m"
    exit 1
fi

# Remove existing .venv if it exists
if [ -d ".venv" ]; then
    echo -e "\033[0;33mRemoving existing .venv directory...\033[0m"
    rm -rf .venv
fi

# Create virtual environment
echo -e "\033[0;33mCreating virtual environment (.venv)...\033[0m"
$PYTHON_CMD -m venv .venv
if [ $? -ne 0 ]; then
    echo -e "\033[0;31mERROR: Failed to create virtual environment\033[0m"
    exit 1
fi
echo -e "\033[0;32mVirtual environment created successfully\033[0m"

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo -e "\033[0;33mInstalling dependencies...\033[0m"
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "\033[0;31mERROR: Failed to install dependencies\033[0m"
    exit 1
fi
echo -e "\033[0;32mDependencies installed successfully\033[0m"

# Clean up old database and CSV files
echo -e "\033[0;33mCleaning up old data files...\033[0m"
rm -f data.db logs.csv
echo -e "\033[0;32mCleanup complete\033[0m"

echo ""
echo -e "\033[0;32mSetup complete!\033[0m"
echo ""
echo -e "\033[0;36mTo start the application, run:\033[0m"
echo -e "  source .venv/bin/activate"
echo -e "  python3 app.py"
echo ""
echo -e "\033[0;36mTo run tests, run:\033[0m"
echo -e "  ./run_tests.sh"
echo ""
