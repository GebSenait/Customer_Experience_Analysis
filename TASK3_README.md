# Task 3: PostgreSQL Database Setup & ETL Pipeline

## Overview

This task implements a complete PostgreSQL database solution for storing and managing bank review data from Tasks 1 & 2. The implementation includes database schema design, ETL pipeline, and validation queries suitable for consulting-grade analytics.

## Objectives

1. **PostgreSQL Environment Setup**: Create and configure the `bank_reviews` database
2. **Database Schema Design**: Implement relational schema with Banks and Reviews tables
3. **Data Insertion Pipeline**: Build efficient ETL scripts for batch data insertion
4. **Data Integrity & Verification**: Create SQL queries for validation and quality checks

## Prerequisites

### PostgreSQL Installation

1. **Install PostgreSQL** (if not already installed):
   - **Windows**: Download from [PostgreSQL Downloads](https://www.postgresql.org/download/windows/)
   - **macOS**: `brew install postgresql` or download from [PostgreSQL Downloads](https://www.postgresql.org/download/macosx/)
   - **Linux**: `sudo apt-get install postgresql postgresql-contrib` (Ubuntu/Debian)

2. **Start PostgreSQL Service**:
   - **Windows**: Services → PostgreSQL → Start
   - **macOS/Linux**: `sudo service postgresql start` or `brew services start postgresql`

3. **Set Default Password** (if first-time setup):
   ```bash
   # Connect as postgres user
   psql -U postgres
   
   # Set password
   ALTER USER postgres PASSWORD 'your_password';
   ```

4. **Verify Installation**:
   ```bash
   psql --version
   psql -U postgres -c "SELECT version();"
   ```

### Python Dependencies

Install required Python packages:

```bash
# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Note**: The `psycopg2-binary` package is included in `requirements.txt` for PostgreSQL connectivity.

## Project Structure

```
Customer_Experience_Analysis/
├── database/
│   ├── schema.sql                    # Database schema definition
│   └── validation_queries.sql        # SQL validation queries
├── src/
│   ├── database_setup.py            # Database creation and schema setup
│   ├── database_etl.py              # ETL pipeline for data insertion
│   └── task3_main.py                # Main orchestration script
├── data/
│   ├── processed/                   # Task 1 cleaned data (input)
│   └── analyzed/                    # Task 2 sentiment data (optional input)
├── logs/                            # Execution logs
└── TASK3_README.md                  # This file
```

## Database Schema

### Banks Table

Stores metadata for the three Ethiopian banks:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `bank_id` | SERIAL | PRIMARY KEY | Auto-incrementing unique identifier |
| `bank_name` | VARCHAR(100) | NOT NULL, UNIQUE | Bank abbreviation (CBE, BOA, Dashen) |
| `app_name` | VARCHAR(200) | NOT NULL | Full mobile banking app name |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

### Reviews Table

Stores cleaned and processed review data:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `review_id` | SERIAL | PRIMARY KEY | Auto-incrementing unique identifier |
| `bank_id` | INTEGER | NOT NULL, FOREIGN KEY | References `banks.bank_id` |
| `review_text` | TEXT | NOT NULL | Cleaned review text from Task 1 |
| `rating` | INTEGER | NOT NULL, CHECK (1-5) | Star rating (1-5) |
| `review_date` | DATE | NOT NULL | Date when review was posted |
| `sentiment_label` | VARCHAR(20) | CHECK (positive/negative/neutral) | Sentiment classification from Task 2 |
| `sentiment_score` | DECIMAL(5,4) | NULL | Sentiment score from Task 2 |
| `source` | VARCHAR(50) | DEFAULT 'Google Play' | Data source |
| `app_name` | VARCHAR(200) | NULL | App name |
| `collection_date` | DATE | NULL | Data collection timestamp |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

### Indexes

Optimized indexes for efficient querying:
- `idx_reviews_bank_id`: Foreign key lookups
- `idx_reviews_review_date`: Time-based analytics
- `idx_reviews_sentiment_label`: Sentiment analysis queries
- `idx_reviews_rating`: Rating-based analytics
- `idx_reviews_bank_date`: Composite index for bank + date queries
- `idx_reviews_sentiment_date`: Composite index for sentiment trends

## Usage

### Quick Start

1. **Set PostgreSQL Password** (if needed):
   ```bash
   # Windows PowerShell
   $env:POSTGRES_PASSWORD="your_password"
   
   # Linux/Mac
   export POSTGRES_PASSWORD="your_password"
   ```

2. **Run Complete Pipeline**:
   ```bash
   python src/task3_main.py
   ```

This will:
- Create the `bank_reviews` database (if it doesn't exist)
- Create tables and indexes from `database/schema.sql`
- Load data from Task 1 processed CSV
- Optionally merge Task 2 sentiment data if available
- Insert data in batches
- Validate insertion and display summary

### Advanced Usage

#### Skip Database Setup

If the database already exists:

```bash
python src/task3_main.py --skip-setup
```

#### Custom Database Connection

```bash
python src/task3_main.py \
  --host localhost \
  --port 5432 \
  --user postgres \
  --password your_password \
  --db-name bank_reviews
```

#### Specify Input Files

```bash
python src/task3_main.py \
  --input data/processed/reviews_cleaned_20251202_092120.csv \
  --task2-input data/analyzed/sentiment_thematic_analysis_20251202_120000.csv
```

#### Individual Components

**Database Setup Only**:
```bash
python src/database_setup.py
```

**ETL Only** (database must exist):
```bash
python src/database_etl.py --input data/processed/reviews_cleaned_20251202_092120.csv
```

## Validation Queries

Run validation queries to verify data integrity:

```bash
# Connect to database
psql -U postgres -d bank_reviews

# Run validation queries
\i database/validation_queries.sql
```

Or execute individual queries:

```sql
-- Total reviews count
SELECT COUNT(*) AS total_reviews FROM reviews;

-- Reviews per bank
SELECT 
    b.bank_name,
    COUNT(r.review_id) AS review_count
FROM banks b
LEFT JOIN reviews r ON b.bank_id = r.bank_id
GROUP BY b.bank_id, b.bank_name
ORDER BY review_count DESC;

-- Average rating per bank
SELECT 
    b.bank_name,
    COUNT(r.review_id) AS review_count,
    ROUND(AVG(r.rating), 2) AS avg_rating
FROM banks b
LEFT JOIN reviews r ON b.bank_id = r.bank_id
GROUP BY b.bank_id, b.bank_name
ORDER BY avg_rating DESC;
```

## KPIs & Deliverables

### KPIs

- ✅ **Fully working PostgreSQL connection & ETL insert script**
- ✅ **Database populated with ≥ 1,000 review rows** (minimum essential: ≥ 400)
- ✅ **SQL schema committed to GitHub**
- ✅ **Schema aligns with consulting-grade standards** and supports downstream analytics

### Minimum Essential Deliverables

- ✅ PostgreSQL database created with both tables
- ✅ Python script that inserts ≥ 400 reviews
- ✅ Schema documented clearly in README.md

## Troubleshooting

### Connection Issues

**Error**: `FATAL: password authentication failed`

**Solution**: 
- Verify PostgreSQL password
- Set `POSTGRES_PASSWORD` environment variable
- Or use `--password` command-line argument

**Error**: `FATAL: database "bank_reviews" does not exist`

**Solution**: 
- Run database setup first: `python src/database_setup.py`
- Or run full pipeline: `python src/task3_main.py`

### Data Issues

**Error**: `Unknown bank: XYZ`

**Solution**: 
- Ensure bank names in CSV match: CBE, BOA, Dashen
- Check `database/schema.sql` for bank names

**Error**: `Missing required columns`

**Solution**: 
- Ensure CSV has columns: `review`, `rating`, `date`, `bank`
- Check Task 1 output format

### Performance Issues

**Slow inserts**: 
- Reduce batch size: `--batch-size 500`
- Check PostgreSQL configuration
- Ensure indexes are created after bulk insert

## Data Flow

```
Task 1 Processed CSV
    ↓
[Extract] Load CSV data
    ↓
[Transform] Map bank names → bank_ids
         Merge Task 2 sentiment data (if available)
         Validate and clean records
    ↓
[Load] Batch insert into PostgreSQL
    ↓
[Validate] Run integrity checks
    ↓
Database populated and ready for analytics
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_PASSWORD` | PostgreSQL password | None (prompt or CLI arg) |

## Running in Cursor AI IDE

1. **Open Terminal** in Cursor AI IDE
2. **Activate Virtual Environment**:
   ```bash
   # Windows
   .\venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Set Environment Variable** (if needed):
   ```bash
   # Windows PowerShell
   $env:POSTGRES_PASSWORD="your_password"
   
   # Linux/Mac
   export POSTGRES_PASSWORD="your_password"
   ```

4. **Run Pipeline**:
   ```bash
   python src/task3_main.py
   ```

5. **Check Logs**:
   - Console output for real-time progress
   - `logs/task3_YYYYMMDD.log` for detailed logs
   - `logs/database_setup.log` for setup logs
   - `logs/database_etl.log` for ETL logs

## Next Steps

After Task 3 completion, the database is ready for:

1. **Analytics Queries**: Sentiment trends, rating distributions, temporal analysis
2. **Dashboard Integration**: Connect BI tools (Tableau, Power BI, etc.)
3. **API Development**: Build REST APIs for data access
4. **Advanced Analytics**: Machine learning pipelines, predictive modeling

## Schema Documentation

The complete schema is defined in `database/schema.sql` with:
- Table definitions with constraints
- Indexes for query optimization
- Triggers for automatic timestamp updates
- Comments for maintainability
- Initial bank data insertion

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review validation queries in `database/validation_queries.sql`
3. Verify PostgreSQL service is running
4. Ensure all dependencies are installed

## License

Proprietary - Omega Consultancy

