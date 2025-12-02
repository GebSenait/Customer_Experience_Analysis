#!/bin/bash
# Task 3 Setup Script for Linux/Mac
# Omega Consultancy - Customer Experience Analysis

echo "============================================================"
echo "Task 3: PostgreSQL Database Setup"
echo "Omega Consultancy"
echo "============================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies"
    exit 1
fi

echo ""
echo "============================================================"
echo "Setup completed successfully!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Ensure PostgreSQL is installed and running"
echo "2. Set PostgreSQL password (if needed):"
echo "   export POSTGRES_PASSWORD=your_password"
echo "3. Run the pipeline:"
echo "   python src/task3_main.py"
echo ""

