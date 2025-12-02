-- ============================================================================
-- Bank Reviews Database Schema
-- Omega Consultancy - Customer Experience Analysis
-- Task 3: PostgreSQL Database Setup
-- ============================================================================

-- Create database (run this separately as superuser)
-- CREATE DATABASE bank_reviews;
-- \c bank_reviews;

-- ============================================================================
-- BANKS TABLE
-- Stores metadata for the three Ethiopian banks
-- ============================================================================

CREATE TABLE IF NOT EXISTS banks (
    bank_id SERIAL PRIMARY KEY,
    bank_name VARCHAR(100) NOT NULL UNIQUE,
    app_name VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- REVIEWS TABLE
-- Stores cleaned and processed review data from Task 1 & Task 2
-- ============================================================================

CREATE TABLE IF NOT EXISTS reviews (
    review_id SERIAL PRIMARY KEY,
    bank_id INTEGER NOT NULL REFERENCES banks(bank_id) ON DELETE CASCADE,
    review_text TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_date DATE NOT NULL,
    sentiment_label VARCHAR(20),
    sentiment_score DECIMAL(5, 4),
    source VARCHAR(50) DEFAULT 'Google Play',
    app_name VARCHAR(200),
    collection_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for efficient querying
    CONSTRAINT valid_sentiment_label CHECK (sentiment_label IN ('positive', 'negative', 'neutral', NULL))
);

-- ============================================================================
-- INDEXES
-- Optimize queries for analytics (sentiment trends, theme distributions, etc.)
-- ============================================================================

-- Index on bank_id for foreign key lookups
CREATE INDEX IF NOT EXISTS idx_reviews_bank_id ON reviews(bank_id);

-- Index on review_date for time-based analytics
CREATE INDEX IF NOT EXISTS idx_reviews_review_date ON reviews(review_date);

-- Index on sentiment_label for sentiment analysis queries
CREATE INDEX IF NOT EXISTS idx_reviews_sentiment_label ON reviews(sentiment_label);

-- Index on rating for rating-based analytics
CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(rating);

-- Composite index for bank + date queries
CREATE INDEX IF NOT EXISTS idx_reviews_bank_date ON reviews(bank_id, review_date);

-- Composite index for sentiment trends
CREATE INDEX IF NOT EXISTS idx_reviews_sentiment_date ON reviews(sentiment_label, review_date);

-- ============================================================================
-- TRIGGERS
-- Auto-update updated_at timestamp
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_banks_updated_at BEFORE UPDATE ON banks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reviews_updated_at BEFORE UPDATE ON reviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL DATA
-- Insert bank metadata
-- ============================================================================

INSERT INTO banks (bank_name, app_name) VALUES
    ('CBE', 'Commercial Bank of Ethiopia'),
    ('BOA', 'Bank of Abyssinia'),
    ('Dashen', 'Dashen Bank')
ON CONFLICT (bank_name) DO NOTHING;

-- ============================================================================
-- COMMENTS
-- Document schema for maintainability
-- ============================================================================

COMMENT ON TABLE banks IS 'Stores metadata for the three Ethiopian banks';
COMMENT ON TABLE reviews IS 'Stores cleaned and processed review data with sentiment analysis';

COMMENT ON COLUMN banks.bank_id IS 'Primary key, auto-incrementing';
COMMENT ON COLUMN banks.bank_name IS 'Bank abbreviation (CBE, BOA, Dashen)';
COMMENT ON COLUMN banks.app_name IS 'Full mobile banking app name';

COMMENT ON COLUMN reviews.review_id IS 'Primary key, auto-incrementing';
COMMENT ON COLUMN reviews.bank_id IS 'Foreign key to banks table';
COMMENT ON COLUMN reviews.review_text IS 'Cleaned review text from Task 1';
COMMENT ON COLUMN reviews.rating IS 'Star rating (1-5)';
COMMENT ON COLUMN reviews.review_date IS 'Date when review was posted';
COMMENT ON COLUMN reviews.sentiment_label IS 'Sentiment classification from Task 2 (positive/negative/neutral)';
COMMENT ON COLUMN reviews.sentiment_score IS 'Sentiment score from Task 2 (typically -1 to 1)';
COMMENT ON COLUMN reviews.source IS 'Data source (Google Play)';

