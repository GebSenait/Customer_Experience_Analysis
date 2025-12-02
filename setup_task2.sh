#!/bin/bash
# Setup script for Task 2 dependencies (Linux/Mac)
# This script handles torch and spacy installation issues

echo "========================================"
echo "Task 2 Dependency Installation"
echo "========================================"
echo ""

# Activate virtual environment
echo "[1/5] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Could not activate virtual environment"
    echo "Make sure you're in the project root directory"
    exit 1
fi

# Install base dependencies (without torch first)
echo ""
echo "[2/5] Installing base dependencies (spacy, transformers, etc.)..."
pip install transformers spacy scikit-learn vaderSentiment textblob nltk pandas numpy tqdm python-dateutil openpyxl
if [ $? -ne 0 ]; then
    echo "WARNING: Some packages may have failed to install"
fi

# Install torch separately (CPU version)
echo ""
echo "[3/5] Installing PyTorch (CPU version)..."
pip install torch --index-url https://download.pytorch.org/whl/cpu
if [ $? -ne 0 ]; then
    echo ""
    echo "WARNING: PyTorch installation failed with CPU index"
    echo "Trying standard pip install..."
    pip install torch
fi

# Verify spacy installation
echo ""
echo "[4/5] Verifying spaCy installation..."
python -c "import spacy; print('spaCy installed successfully')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: spaCy not found. Reinstalling..."
    pip install --upgrade spacy
fi

# Download spacy model
echo ""
echo "[5/5] Downloading spaCy English model..."
python -m spacy download en_core_web_sm
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Could not download spaCy model"
    echo "Try manually: python -m spacy download en_core_web_sm"
fi

echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "To verify installation, run:"
echo "  python -c \"import torch; import spacy; nlp = spacy.load('en_core_web_sm'); print('All OK!')\""
echo ""

