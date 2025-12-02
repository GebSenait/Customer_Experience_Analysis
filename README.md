# Customer Experience Analysis - Banking App Reviews

## Project Overview

This project is part of Omega Consultancy's analysis pipeline for enhancing user satisfaction and retention for mobile banking apps of three Ethiopian banks:
- **Commercial Bank of Ethiopia (CBE)**
- **Bank of Abyssinia (BOA)**
- **Dashen Bank**

The pipeline collects, analyzes, and stores Google Play Store reviews to extract actionable insights for improving customer experience.

---

## Project Status

### ✅ Task 1: Data Collection & Preprocessing - **COMPLETED**

**Objective**: Collect and clean Google Play Store review data

**Implementation**:
- Automated scraper using `google-play-scraper` library
- Data preprocessing with duplicate removal, normalization, and validation
- Package ID finder and manual setup tools

**Key Results**:
- ✅ **Total Reviews**: ≥1,200 reviews collected
- ✅ **Data Quality**: <5% missing values
- ✅ **Per Bank**: ≥400 reviews per bank
- ✅ **Output**: Clean, analysis-ready CSV datasets

**Key Files**:
- `src/scraper.py` - Google Play Store review scraper
- `src/preprocessor.py` - Data cleaning and preprocessing
- `src/main.py` - Main execution script

**Output**:
- Raw data: `data/raw/reviews_raw_YYYYMMDD_HHMMSS.json`
- Processed data: `data/processed/reviews_cleaned_YYYYMMDD_HHMMSS.csv`

**Insights**:
- Standardized data format across all three banks
- High data quality with minimal missing values
- Ready for downstream NLP and sentiment analysis

---

### ✅ Task 2: Sentiment & Thematic Analysis - **COMPLETED**

**Objective**: Analyze sentiment and identify themes in customer reviews

**Implementation**:
- Sentiment analysis using DistilBERT model (HuggingFace)
- Thematic analysis with TF-IDF and keyword extraction
- NLP pipeline with spaCy and NLTK
- Optional comparison models (VADER, TextBlob)

**Key Results**:
- ✅ **Sentiment Scores**: Computed for ≥90% of reviews
- ✅ **Themes Identified**: ≥3 themes per bank
- ✅ **Analysis Coverage**: ≥400 reviews analyzed
- ✅ **Output**: Sentiment labels, scores, and identified themes

**Key Files**:
- `src/sentiment_analyzer.py` - Sentiment analysis engine
- `src/thematic_analyzer.py` - Theme identification
- `src/nlp_pipeline.py` - Text processing pipeline
- `src/task2_main.py` - Main execution script

**Output**:
- Analyzed data: `data/analyzed/sentiment_thematic_analysis_YYYYMMDD_HHMMSS.csv`
- Themes: `data/analyzed/themes_YYYYMMDD_HHMMSS.json`
- Insights: `data/analyzed/sentiment_insights_YYYYMMDD_HHMMSS.json`

**Insights**:
- Sentiment distribution across banks and ratings
- Common themes: Account Access, Transaction Speed, UI/UX, Customer Support
- Sentiment trends by bank and rating category
- Actionable themes for improvement prioritization

---

### ✅ Task 3: PostgreSQL Database Setup & ETL - **COMPLETED**

**Objective**: Create PostgreSQL database and ETL pipeline for review data storage

**Implementation**:
- PostgreSQL database setup with relational schema
- ETL pipeline with batch processing
- Data validation and integrity checks
- Comprehensive documentation

**Key Results**:
- ✅ **Database Connection**: Fully working PostgreSQL connection & ETL script
- ✅ **Data Population**: Supports ≥1,000 review entries (minimum: ≥400)
- ✅ **Schema**: SQL schema file committed to repository
- ✅ **Documentation**: Complete schema documentation in README

**Key Files**:
- `database/schema.sql` - Database schema definition
- `src/database_setup.py` - Database creation and setup
- `src/database_etl.py` - ETL pipeline with batch inserts
- `src/task3_main.py` - Main orchestration script
- `database/validation_queries.sql` - Data integrity queries

**Database Schema**:
- **Banks Table**: bank_id (PK), bank_name, app_name, timestamps
- **Reviews Table**: review_id (PK), bank_id (FK), review_text, rating, review_date, sentiment_label, sentiment_score, source, etc.
- **Indexes**: Optimized for analytics queries (sentiment trends, temporal analysis)

**Output**:
- Database: `bank_reviews` (PostgreSQL)
- Tables: `banks`, `reviews`
- Validation queries for data integrity

**Insights**:
- Relational database structure supports complex analytics
- Efficient batch processing for large datasets
- Ready for BI tools and advanced analytics
- Data integrity ensured through constraints and validation

---

## Repository Structure

```
Customer_Experience_Analysis/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .gitignore
├── database/
│   ├── schema.sql              # Task 3: Database schema
│   └── validation_queries.sql  # Task 3: Validation queries
├── src/
│   ├── scraper.py              # Task 1: Data collection
│   ├── preprocessor.py         # Task 1: Data preprocessing
│   ├── main.py                 # Task 1: Main script
│   ├── sentiment_analyzer.py   # Task 2: Sentiment analysis
│   ├── thematic_analyzer.py    # Task 2: Theme identification
│   ├── nlp_pipeline.py         # Task 2: NLP processing
│   ├── task2_main.py           # Task 2: Main script
│   ├── database_setup.py       # Task 3: Database setup
│   ├── database_etl.py         # Task 3: ETL pipeline
│   └── task3_main.py           # Task 3: Main script
├── data/
│   ├── raw/                    # Task 1: Raw scraped data
│   ├── processed/              # Task 1: Cleaned data
│   └── analyzed/               # Task 2: Analysis results
└── logs/                       # Execution logs
```

---

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL (for Task 3)
- Virtual environment (recommended)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Customer_Experience_Analysis
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Pipeline

**Task 1: Data Collection & Preprocessing**
```bash
python src/main.py
```

**Task 2: Sentiment & Thematic Analysis**
```bash
python src/task2_main.py
```

**Task 3: Database Setup & ETL**
```bash
# Set PostgreSQL password
$env:POSTGRES_PASSWORD="your_password"  # PowerShell
# or
export POSTGRES_PASSWORD="your_password"  # Linux/Mac

# Run Task 3
python src/task3_main.py
```

---

## Key Findings & Insights

### Data Collection (Task 1)
- Successfully collected ≥1,200 reviews from three Ethiopian banks
- High data quality with <5% missing values
- Standardized format ready for analysis

### Sentiment Analysis (Task 2)
- Sentiment scores computed for ≥90% of reviews
- Identified sentiment distribution patterns across banks
- Correlation between ratings and sentiment scores

### Thematic Analysis (Task 2)
- ≥3 themes identified per bank
- Common themes: Account Access, Transaction Speed, UI/UX, Customer Support
- Theme distribution helps prioritize improvement areas

### Database Storage (Task 3)
- Relational database structure supports complex analytics
- Efficient batch processing for large datasets
- Ready for BI tools and advanced queries

---

## Documentation

- **Task 1**: See `README.md` (this file) - Data Collection section
- **Task 2**: See `TASK2_README.md` - Sentiment & Thematic Analysis
- **Task 3**: See `TASK3_README.md` - PostgreSQL Database Setup

---

## KPIs Summary

| Task | KPI | Status |
|------|-----|--------|
| **Task 1** | ≥1,200 total reviews | ✅ Met |
| **Task 1** | ≥400 reviews per bank | ✅ Met |
| **Task 1** | <5% missing data | ✅ Met |
| **Task 2** | ≥90% sentiment scores computed | ✅ Met |
| **Task 2** | ≥3 themes per bank | ✅ Met |
| **Task 2** | ≥400 reviews analyzed | ✅ Met |
| **Task 3** | Working database + ETL script | ✅ Met |
| **Task 3** | ≥1,000 review entries supported | ✅ Met |
| **Task 3** | Schema file committed | ✅ Met |

---

## Contributing

This project follows Omega Consultancy's data engineering standards:
- Clean, maintainable code
- Comprehensive documentation
- Reproducible results
- Version control best practices

---

## License

Proprietary - Omega Consultancy

---

## Contact

For questions or issues, contact the project team.
