@echo off
REM Task 3 Setup Script for Windows
REM Omega Consultancy - Customer Experience Analysis

echo ============================================================
echo Task 3: PostgreSQL Database Setup
echo Omega Consultancy
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo.
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Setup completed successfully!
echo ============================================================
echo.
echo Next steps:
echo 1. Ensure PostgreSQL is installed and running
echo 2. Set PostgreSQL password (if needed):
echo    set POSTGRES_PASSWORD=your_password
echo 3. Run the pipeline:
echo    python src\task3_main.py
echo.
pause

