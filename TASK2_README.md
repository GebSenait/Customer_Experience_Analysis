# Task 2: Sentiment & Thematic Analysis

## Overview

This module implements a comprehensive sentiment and thematic analysis pipeline for customer reviews. It uses state-of-the-art NLP models to analyze sentiment and identify recurring themes across banking app reviews.

## Features

### 1. Sentiment Analysis
- **Primary Model**: `distilbert-base-uncased-finetuned-sst-2-english` (HuggingFace)
- **Output**: Sentiment labels (positive/negative/neutral) and confidence scores
- **Aggregation**: Insights by bank, rating, and category
- **Optional Comparison**: VADER and TextBlob models (configurable)

### 2. Thematic Analysis
- **Keyword Extraction**: TF-IDF and spaCy-based extraction
- **Theme Identification**: 3-5 themes per bank
- **Predefined Themes**:
  - Account Access Problems
  - Transaction Speed & Reliability
  - User Interface & Experience
  - Customer Support Responsiveness
  - Feature Requests
  - Security & Trust
  - App Performance & Stability
- **Clustering**: K-means clustering for additional theme discovery

### 3. NLP Pipeline
- **Text Normalization**: Lowercasing, whitespace cleanup
- **Tokenization**: spaCy or NLTK-based
- **Stop Word Removal**: Configurable stop word lists
- **Lemmatization**: WordNet-based lemmatization
- **Modular Design**: Each step can be enabled/disabled

## Installation

### Prerequisites

1. **Python 3.8+**
2. **Virtual Environment** (recommended)

### Step 1: Install Python Dependencies

**Recommended: Use Setup Script**

```bash
# Windows:
setup_task2.bat

# Linux/Mac:
chmod +x setup_task2.sh
./setup_task2.sh
```

**Manual Installation:**

```bash
# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install base packages (spacy, transformers, etc.)
pip install transformers spacy scikit-learn vaderSentiment textblob nltk pandas numpy tqdm

# Install torch separately (CPU version - recommended)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# If above fails, try:
pip install torch
```

### Step 2: Download spaCy Model

**Important**: Only run this AFTER spaCy is installed!

```bash
python -m spacy download en_core_web_sm
```

### Step 3: Download NLTK Data (automatic on first run)

The pipeline will automatically download required NLTK data on first run. If you encounter issues, run:

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
```

## Usage

### Basic Usage

Run the complete pipeline:

```bash
python src/task2_main.py
```

This will:
1. Load the most recent processed CSV file from `data/processed/`
2. Run sentiment analysis
3. Run thematic analysis
4. Process text through NLP pipeline
5. Save results to `data/analyzed/`

### Advanced Usage

#### Specify Input File

```bash
python src/task2_main.py --input data/processed/reviews_cleaned_20251202_092120.csv
```

#### Specify Output Directory

```bash
python src/task2_main.py --output-dir results/task2
```

### Programmatic Usage

```python
from src.task2_main import Task2Pipeline

# Initialize pipeline
pipeline = Task2Pipeline(
    input_file='data/processed/reviews_cleaned_20251202_092120.csv',
    output_dir='data/analyzed'
)

# Run complete pipeline
output_df, themes, insights = pipeline.run()
```

### Using Individual Modules

#### Sentiment Analysis Only

```python
from src.sentiment_analyzer import SentimentAnalyzer
import pandas as pd

# Load data
df = pd.read_csv('data/processed/reviews_cleaned_20251202_092120.csv')

# Initialize analyzer
analyzer = SentimentAnalyzer(compare_models=False)

# Analyze
df_with_sentiment = analyzer.analyze_dataframe(df, text_column='review')

# Get insights
insights = analyzer.aggregate_sentiment_insights(df_with_sentiment)
```

#### Thematic Analysis Only

```python
from src.thematic_analyzer import ThematicAnalyzer
import pandas as pd

# Load data
df = pd.read_csv('data/processed/reviews_cleaned_20251202_092120.csv')

# Initialize analyzer
analyzer = ThematicAnalyzer(n_themes=5)

# Analyze
df_with_themes, themes = analyzer.analyze_dataframe(df, text_column='review', bank_column='bank')
```

#### NLP Processing Only

```python
from src.nlp_pipeline import NLPipeline
import pandas as pd

# Load data
df = pd.read_csv('data/processed/reviews_cleaned_20251202_092120.csv')

# Initialize pipeline
nlp = NLPipeline(use_spacy=True, use_nltk=True)

# Process
df_processed = nlp.process_dataframe(df, text_column='review', processed_column='processed_text')
```

## Output Files

### 1. Main Results CSV

**File**: `data/analyzed/sentiment_thematic_analysis_YYYYMMDD_HHMMSS.csv`

**Columns**:
- `review_id`: Unique identifier for each review
- `review_text`: Original review text
- `sentiment_label`: Sentiment classification (positive/negative/neutral)
- `sentiment_score`: Confidence score (0-1)
- `identified_themes`: Semicolon-separated list of themes
- `primary_theme`: Main theme for the review
- `bank`: Bank name
- `rating`: Star rating (1-5)
- `date`: Review date

### 2. Themes JSON

**File**: `data/analyzed/themes_YYYYMMDD_HHMMSS.json`

Contains theme information for each bank:
```json
{
  "BOA": {
    "Account Access Problems": {
      "keywords": ["login", "password", "account", ...],
      "keyword_scores": {...},
      "review_count": 45,
      "logic": "Matched 8 keywords related to account access problems"
    },
    ...
  }
}
```

### 3. Sentiment Insights JSON

**File**: `data/analyzed/sentiment_insights_YYYYMMDD_HHMMSS.json`

Contains aggregated sentiment statistics:
```json
{
  "overall": {"positive": 650, "negative": 350},
  "overall_pct": {"positive": 65.0, "negative": 35.0},
  "avg_sentiment_score": 0.7234,
  "by_bank": {...},
  "by_rating": {...}
}
```

## KPIs & Validation

The pipeline automatically validates KPIs:

### Required KPIs
- ✅ Sentiment scores computed for ≥ 90% of reviews
- ✅ ≥ 3 themes per bank with example keywords & logic
- ✅ Clean, modular NLP pipeline code

### Minimum Essential Deliverables
- ✅ Sentiment scores for ≥ 400 reviews
- ✅ ≥ 2 themes per bank, derived via keywords
- ✅ Sentiment & thematic analysis script committed to repo

## Module Structure

```
src/
├── sentiment_analyzer.py    # Sentiment analysis using DistilBERT
├── thematic_analyzer.py      # Theme identification and clustering
├── nlp_pipeline.py          # Text preprocessing pipeline
└── task2_main.py            # Main orchestration script
```

## Configuration

### Sentiment Analyzer

```python
SentimentAnalyzer(
    model_name="distilbert-base-uncased-finetuned-sst-2-english",
    use_gpu=False,  # Set to True if GPU available
    compare_models=False  # Set to True to compare with VADER/TextBlob
)
```

### Thematic Analyzer

```python
ThematicAnalyzer(
    n_themes=5,  # Number of themes per bank
    use_spacy=True,  # Use spaCy for advanced NLP
    min_keyword_freq=3,  # Minimum keyword frequency
    max_keywords_per_theme=10  # Max keywords per theme
)
```

### NLP Pipeline

```python
NLPipeline(
    use_spacy=True,  # Use spaCy
    use_nltk=True    # Use NLTK
)
```

## Theme-Grouping Logic

Themes are identified using a combination of:

1. **Keyword Matching**: Extracted keywords are matched against predefined theme keywords
2. **TF-IDF Scoring**: Keywords are ranked by importance using TF-IDF
3. **spaCy Extraction**: Advanced NLP extraction of nouns, adjectives, and phrases
4. **K-means Clustering**: Additional themes discovered through clustering
5. **Review Classification**: Each review is classified into themes based on keyword presence

### Example Theme Logic

**Account Access Problems**:
- Matches keywords: "login", "password", "account", "access", "unable", "error", "otp", "verification"
- Logic: "Matched 8 keywords related to account access problems"

## Troubleshooting

### Issue: spaCy model not found

**Solution**:
```bash
python -m spacy download en_core_web_sm
```

### Issue: NLTK data missing

**Solution**: The pipeline will auto-download on first run. If issues persist:
```python
import nltk
nltk.download('all')
```

### Issue: CUDA/GPU errors

**Solution**: Set `use_gpu=False` in SentimentAnalyzer initialization

### Issue: Memory errors with large datasets

**Solution**: Process in batches by modifying batch_size parameter:
```python
analyzer.analyze_dataframe(df, text_column='review', batch_size=16)
```

## Performance

- **Sentiment Analysis**: ~2-5 seconds per 100 reviews (CPU)
- **Thematic Analysis**: ~1-3 seconds per 100 reviews
- **NLP Processing**: ~0.5-1 second per 100 reviews

*Note: First run will be slower due to model downloads*

## Dependencies

See `requirements.txt` for complete list. Key dependencies:

- `transformers==4.36.2` - HuggingFace transformers
- `torch==2.1.2` - PyTorch
- `spacy==3.7.2` - spaCy NLP library
- `scikit-learn==1.3.2` - Machine learning utilities
- `vaderSentiment==3.3.2` - VADER sentiment analyzer
- `textblob==0.17.1` - TextBlob sentiment analyzer
- `nltk==3.8.1` - NLTK toolkit

## Git Workflow

This code is developed in the `task-2-sentiment-analysis` branch:

```bash
# Check current branch
git branch

# Switch to task-2 branch (if needed)
git checkout task-2-sentiment-analysis

# Commit changes
git add .
git commit -m "Add sentiment and thematic analysis pipeline"

# Push to remote
git push origin task-2-sentiment-analysis
```

## Consulting Deliverables

This pipeline produces clean, production-ready code suitable for consulting deliverables:

- ✅ Modular, well-documented code
- ✅ Comprehensive logging
- ✅ KPI validation
- ✅ Structured output formats
- ✅ Error handling
- ✅ Performance optimization

## Next Steps

1. **Review Results**: Check output CSV and JSON files
2. **Validate KPIs**: Ensure all KPIs are met
3. **Customize Themes**: Adjust theme keywords in `thematic_analyzer.py`
4. **Integrate**: Use results for downstream analysis (Task 3+)

## Support

For issues or questions:
1. Check logs in `logs/task2_YYYYMMDD.log`
2. Review error messages in console output
3. Validate input data format
4. Ensure all dependencies are installed

---

**Omega Consultancy** - Customer Experience Analysis Project

