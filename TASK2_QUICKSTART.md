# Task 2 Quick Start Guide

## Quick Setup (5 minutes)

### 1. Install Dependencies

**Option A: Use Setup Script (Recommended)**
```bash
# Windows:
setup_task2.bat

# Linux/Mac:
chmod +x setup_task2.sh
./setup_task2.sh
```

**Option B: Manual Installation**
```bash
# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install base packages (spacy first)
pip install transformers spacy scikit-learn vaderSentiment textblob nltk

# Install torch separately (CPU version)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Download spaCy model (AFTER spacy is installed)
python -m spacy download en_core_web_sm
```

**Note**: If torch installation fails, try: `pip install torch` (without version constraint)

### 2. Run the Pipeline

```bash
python src/task2_main.py
```

That's it! The pipeline will:
- ✅ Load the most recent processed CSV
- ✅ Analyze sentiment for all reviews
- ✅ Identify themes per bank
- ✅ Generate output CSV with all required fields
- ✅ Save results to `data/analyzed/`

### 3. Check Results

Results will be saved in `data/analyzed/`:
- `sentiment_thematic_analysis_YYYYMMDD_HHMMSS.csv` - Main results
- `themes_YYYYMMDD_HHMMSS.json` - Theme details
- `sentiment_insights_YYYYMMDD_HHMMSS.json` - Sentiment statistics

## Expected Output

The main CSV will contain:
- `review_id` - Unique identifier
- `review_text` - Original review
- `sentiment_label` - positive/negative/neutral
- `sentiment_score` - Confidence (0-1)
- `identified_themes` - Semicolon-separated themes
- `primary_theme` - Main theme
- `bank`, `rating`, `date` - Metadata

## Troubleshooting

**Issue**: "spaCy model not found"
```bash
python -m spacy download en_core_web_sm
```

**Issue**: "No CSV files found"
- Make sure Task 1 preprocessing has been run
- Check `data/processed/` directory

**Issue**: Slow processing
- First run downloads models (~500MB)
- Subsequent runs are faster
- Consider using GPU if available (set `use_gpu=True` in code)

## Next Steps

1. Review the output CSV
2. Check theme JSON for theme details
3. Validate KPIs in console output
4. Proceed to Task 3 (if applicable)

---

For detailed documentation, see `TASK2_README.md`

