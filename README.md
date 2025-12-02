# Customer Experience Analysis - Task 1: Data Collection & Preprocessing

## Project Overview

This project is part of Omega Consultancy's analysis pipeline for enhancing user satisfaction and retention for mobile banking apps of three Ethiopian banks:
- **Commercial Bank of Ethiopia (CBE)**
- **Bank of Abyssinia (BOA)**
- **Dashen Bank**

## Objective

Collect, clean, and prepare Google Play Store review data to support downstream analysis including:
- Sentiment analysis
- Theme extraction
- Complaint clustering
- User retention insights
- Feature improvement recommendations

## Repository Structure

```
Customer_Experience_Analysis/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── scraper.py          # Google Play Store review scraper
│   ├── preprocessor.py     # Data cleaning and preprocessing
│   └── main.py             # Main execution script
├── data/
│   ├── raw/                # Raw scraped data (gitignored)
│   └── processed/          # Cleaned datasets (gitignored)
└── logs/                   # Execution logs (gitignored)
```

## Installation

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

## Data Collection Methodology

### Scraping Approach

We use the `google-play-scraper` library to collect reviews from Google Play Store. The scraper:

1. **Identifies App Packages:**
   - Searches for each bank's mobile banking app using app names
   - Extracts package IDs for accurate review collection

2. **Review Collection:**
   - Collects reviews with pagination support
   - Targets minimum 400 reviews per bank (≥1,200 total)
   - Captures: review text, rating, date, app name, source

3. **Data Fields Collected:**
   - `review`: Full review text
   - `rating`: Star rating (1-5)
   - `date`: Review submission date
   - `app_name`: Name of the mobile banking app
   - `bank`: Bank identifier (CBE, BOA, Dashen)
   - `source`: Data source ("Google Play")

### App Identification

The scraper uses the following app identifiers:
- **CBE**: "Commercial Bank of Ethiopia" / "CBE Mobile Banking"
- **BOA**: "Bank of Abyssinia" / "BOA Mobile Banking"
- **Dashen**: "Dashen Bank" / "Dashen Mobile Banking"

## Preprocessing Steps

### 1. Data Cleaning
- **Duplicate Removal**: Identifies and removes duplicate reviews based on review text and date
- **Missing Value Handling**: 
  - Drops rows with missing review text (critical field)
  - Fills missing ratings with median value
  - Removes rows with missing dates

### 2. Data Normalization
- **Date Formatting**: Converts all dates to YYYY-MM-DD format
- **Text Normalization**: 
  - Removes extra whitespace
  - Standardizes encoding (UTF-8)
- **Rating Validation**: Ensures ratings are between 1-5

### 3. Metadata Addition
- Adds consistent metadata fields:
  - `bank`: Bank identifier
  - `source`: "Google Play"
  - `collection_date`: Date when data was collected

### 4. Data Quality Checks
- Validates minimum review count (≥400 per bank)
- Checks missing data percentage (<5%)
- Ensures date format consistency
- Validates rating ranges

## Usage

### Running the Complete Pipeline

Execute the main script to run both scraping and preprocessing:

```bash
python src/main.py
```

### Running Individual Components

**Scraping only:**
```bash
python src/scraper.py
```

**Preprocessing only:**
```bash
python src/preprocessor.py
```

## Output

### Raw Data
- Location: `data/raw/reviews_raw_YYYYMMDD_HHMMSS.json`
- Format: JSON with all scraped reviews

### Processed Data
- Location: `data/processed/reviews_cleaned_YYYYMMDD_HHMMSS.csv`
- Format: CSV with standardized columns:
  - `review`: Review text
  - `rating`: Star rating (1-5)
  - `date`: Review date (YYYY-MM-DD)
  - `bank`: Bank name (CBE, BOA, Dashen)
  - `app_name`: Mobile app name
  - `source`: "Google Play"
  - `collection_date`: Data collection timestamp

## Data Quality Metrics

The preprocessing script outputs:
- Total reviews collected
- Reviews per bank
- Missing data percentage
- Duplicate count
- Final cleaned dataset size

## KPIs

- ✅ **Total Reviews**: ≥1,200 reviews
- ✅ **Missing Data**: <5% missing values
- ✅ **Per Bank**: ≥400 reviews per bank
- ✅ **Data Quality**: Clean, analysis-ready dataset

## Next Steps

This cleaned dataset supports:
1. **Task 2**: Sentiment Analysis
2. **Task 3**: Theme Extraction
3. **Task 4**: Complaint Clustering
4. **Task 5**: Database Ingestion (PostgreSQL)

## Troubleshooting

### Common Issues

1. **Rate Limiting**: If scraping fails due to rate limits, the script includes delays between requests
2. **App Not Found**: Verify app names/packages are correct for each bank
3. **Missing Reviews**: Ensure sufficient reviews exist on Google Play Store

### Logs

Check `logs/` directory for detailed execution logs and error messages.

## Contributing

This project follows Omega Consultancy's data engineering standards:
- Clean, maintainable code
- Comprehensive documentation
- Reproducible results
- Version control best practices

## License

Proprietary - Omega Consultancy

## Contact

For questions or issues, contact the project team.

