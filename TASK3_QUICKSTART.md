# Task 3 Quick Start Guide

## Prerequisites Checklist

- [ ] PostgreSQL installed and running
- [ ] PostgreSQL password known (or set in environment)
- [ ] Python virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)

## Quick Start (3 Steps)

### Step 1: Setup Environment

**Windows:**
```bash
.\setup_task3.bat
```

**Linux/Mac:**
```bash
chmod +x setup_task3.sh
./setup_task3.sh
```

### Step 2: Set PostgreSQL Password (if needed)

**Windows PowerShell:**
```powershell
$env:POSTGRES_PASSWORD="your_password"
```

**Linux/Mac:**
```bash
export POSTGRES_PASSWORD="your_password"
```

### Step 3: Run Pipeline

```bash
python src/task3_main.py
```

## What It Does

1. **Creates Database**: `bank_reviews` database (if doesn't exist)
2. **Creates Schema**: Banks and Reviews tables with indexes
3. **Loads Data**: Inserts reviews from Task 1 processed CSV
4. **Merges Sentiment**: Optionally includes Task 2 sentiment data
5. **Validates**: Runs integrity checks and displays summary

## Expected Output

```
============================================================
Task 3: PostgreSQL Database Setup & ETL Pipeline
Omega Consultancy
============================================================

[EXTRACT] Loading data...
Loaded 1200 reviews from data/processed/reviews_cleaned_*.csv

[TRANSFORM] Transforming data...
Transformed 1200 records for insertion

[LOAD] Inserting 1200 reviews...
  Batch 1/2: Inserted 1000 reviews
  Batch 2/2: Inserted 200 reviews
✓ Successfully inserted 1200 reviews

[VALIDATE] Validating insertion...
Total reviews inserted: 1200
Reviews per bank:
  CBE: 400
  BOA: 400
  Dashen: 400
```

## Verify Database

```bash
# Connect to database
psql -U postgres -d bank_reviews

# Run validation queries
\i database/validation_queries.sql

# Or quick check
SELECT COUNT(*) FROM reviews;
SELECT bank_name, COUNT(*) FROM banks b 
JOIN reviews r ON b.bank_id = r.bank_id 
GROUP BY bank_name;
```

## Troubleshooting

**Connection Error?**
- Check PostgreSQL is running: `psql -U postgres -c "SELECT 1;"`
- Verify password is correct
- Check host/port settings

**No Data Inserted?**
- Check input file exists: `data/processed/reviews_cleaned_*.csv`
- Verify CSV has required columns: `review`, `rating`, `date`, `bank`
- Check logs: `logs/database_etl.log`

**Database Already Exists?**
```bash
python src/task3_main.py --skip-setup
```

## Files Created

- `database/schema.sql` - Database schema
- `database/validation_queries.sql` - Validation queries
- `src/database_setup.py` - Database setup script
- `src/database_etl.py` - ETL pipeline
- `src/task3_main.py` - Main orchestration script

## Next Steps

After successful completion:
1. Review validation queries: `database/validation_queries.sql`
2. Connect BI tools for analytics
3. Build APIs for data access
4. Run advanced analytics queries

For detailed documentation, see `TASK3_README.md`

