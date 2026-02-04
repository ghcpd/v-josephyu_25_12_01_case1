#!/bin/bash

# Flask Log Management System - Linux/macOS Setup Script
# This script sets up the development environment on Linux/macOS

set -e  # Exit on error

SKIP_DB=false

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-db)
            SKIP_DB=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "Flask Log Management System - Setup Script (Linux/macOS)"
echo "========================================================"
echo ""

# Check if Python is installed
echo "Checking Python installation..." 
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed"
    echo "Please install Python 3.10 or later"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
echo "✓ Found: $PYTHON_VERSION"
echo ""

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Working directory: $SCRIPT_DIR"
echo ""

cd "$SCRIPT_DIR"

# Create virtual environment
echo "Step 1: Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "Virtual environment already exists"
else
    echo "Creating .venv..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Step 2: Activating virtual environment..."
source .venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install requirements
echo "Step 3: Installing requirements..."
pip install -q -r requirements.txt
echo "✓ Requirements installed successfully"
echo ""

# Initialize database
if [ "$SKIP_DB" = true ]; then
    echo "Step 4: Skipping database initialization (--skip-db flag used)"
else
    echo "Step 4: Initializing database..."
    python3 app.py --init-db || true
    echo "✓ Database initialized"
fi
echo ""

# Display next steps
echo "========================================================"
echo "Setup Complete!"
echo "========================================================"
echo ""
echo "Next steps:"
echo "1. To activate the virtual environment in future sessions:"
echo "   source .venv/bin/activate"
echo ""
echo "2. To start the development server:"
echo "   python3 app.py"
echo ""
echo "3. To run tests:"
echo "   pytest test_app.py -v"
echo ""
echo "4. Server will be available at:"
echo "   http://127.0.0.1:5000"
echo ""
