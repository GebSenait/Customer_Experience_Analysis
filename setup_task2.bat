@echo off
REM Setup script for Task 2 dependencies
REM This script handles torch and spacy installation issues

echo ========================================
echo Task 2 Dependency Installation
echo ========================================
echo.

REM Activate virtual environment
echo [1/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Could not activate virtual environment
    echo Make sure you're in the project root directory
    pause
    exit /b 1
)

REM Install base dependencies (without torch first)
echo.
echo [2/5] Installing base dependencies (spacy, transformers, etc.)...
pip install transformers spacy scikit-learn vaderSentiment textblob nltk pandas numpy tqdm python-dateutil openpyxl
if errorlevel 1 (
    echo WARNING: Some packages may have failed to install
)

REM Install torch separately (CPU version)
echo.
echo [3/5] Installing PyTorch (CPU version)...
pip install torch --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 (
    echo.
    echo WARNING: PyTorch installation failed with CPU index
    echo Trying standard pip install...
    pip install torch
)

REM Verify spacy installation
echo.
echo [4/5] Verifying spaCy installation...
python -c "import spacy; print('spaCy installed successfully')" 2>nul
if errorlevel 1 (
    echo ERROR: spaCy not found. Reinstalling...
    pip install --upgrade spacy
)

REM Download spacy model
echo.
echo [5/5] Downloading spaCy English model...
python -m spacy download en_core_web_sm
if errorlevel 1 (
    echo.
    echo ERROR: Could not download spaCy model
    echo Try manually: python -m spacy download en_core_web_sm
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To verify installation, run:
echo   python -c "import torch; import spacy; nlp = spacy.load('en_core_web_sm'); print('All OK!')"
echo.
pause

