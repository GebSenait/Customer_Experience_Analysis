-- ============================================================================
-- Database Validation Queries
-- Omega Consultancy - Customer Experience Analysis
-- Task 3: Data Integrity & Verification
-- ============================================================================

-- ============================================================================
-- BASIC COUNTS
-- ============================================================================

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
    ROUND(AVG(r.rating), 2) AS avg_rating,
    MIN(r.rating) AS min_rating,
    MAX(r.rating) AS max_rating
FROM banks b
LEFT JOIN reviews r ON b.bank_id = r.bank_id
GROUP BY b.bank_id, b.bank_name
ORDER BY avg_rating DESC;

-- ============================================================================
-- DATA QUALITY CHECKS
-- ============================================================================

-- Check for nulls in critical fields
SELECT 
    'review_text' AS field_name,
    COUNT(*) AS null_count,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM reviews) AS null_percentage
FROM reviews
WHERE review_text IS NULL OR review_text = ''

UNION ALL

SELECT 
    'rating' AS field_name,
    COUNT(*) AS null_count,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM reviews) AS null_percentage
FROM reviews
WHERE rating IS NULL

UNION ALL

SELECT 
    'review_date' AS field_name,
    COUNT(*) AS null_count,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM reviews) AS null_percentage
FROM reviews
WHERE review_date IS NULL

UNION ALL

SELECT 
    'bank_id' AS field_name,
    COUNT(*) AS null_count,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM reviews) AS null_percentage
FROM reviews
WHERE bank_id IS NULL;

-- Check for mismatched foreign keys
SELECT 
    r.review_id,
    r.bank_id,
    'Orphaned review - bank_id does not exist' AS issue
FROM reviews r
LEFT JOIN banks b ON r.bank_id = b.bank_id
WHERE b.bank_id IS NULL;

-- Check for invalid ratings
SELECT 
    review_id,
    rating,
    'Invalid rating - must be between 1 and 5' AS issue
FROM reviews
WHERE rating < 1 OR rating > 5;

-- Check for invalid sentiment labels
SELECT 
    review_id,
    sentiment_label,
    'Invalid sentiment label' AS issue
FROM reviews
WHERE sentiment_label IS NOT NULL 
  AND sentiment_label NOT IN ('positive', 'negative', 'neutral');

-- ============================================================================
-- SENTIMENT ANALYSIS STATISTICS
-- ============================================================================

-- Sentiment distribution (if Task 2 data is available)
SELECT 
    sentiment_label,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM reviews WHERE sentiment_label IS NOT NULL), 2) AS percentage
FROM reviews
WHERE sentiment_label IS NOT NULL
GROUP BY sentiment_label
ORDER BY count DESC;

-- Sentiment by bank
SELECT 
    b.bank_name,
    r.sentiment_label,
    COUNT(*) AS count,
    ROUND(AVG(r.sentiment_score), 4) AS avg_sentiment_score
FROM banks b
JOIN reviews r ON b.bank_id = r.bank_id
WHERE r.sentiment_label IS NOT NULL
GROUP BY b.bank_name, r.sentiment_label
ORDER BY b.bank_name, count DESC;

-- Average sentiment score per bank
SELECT 
    b.bank_name,
    COUNT(r.review_id) AS reviews_with_sentiment,
    ROUND(AVG(r.sentiment_score), 4) AS avg_sentiment_score,
    MIN(r.sentiment_score) AS min_score,
    MAX(r.sentiment_score) AS max_score
FROM banks b
JOIN reviews r ON b.bank_id = r.bank_id
WHERE r.sentiment_score IS NOT NULL
GROUP BY b.bank_name
ORDER BY avg_sentiment_score DESC;

-- ============================================================================
-- TEMPORAL ANALYSIS
-- ============================================================================

-- Reviews by date (last 30 days)
SELECT 
    review_date,
    COUNT(*) AS review_count
FROM reviews
WHERE review_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY review_date
ORDER BY review_date DESC;

-- Reviews per month
SELECT 
    DATE_TRUNC('month', review_date) AS month,
    COUNT(*) AS review_count
FROM reviews
GROUP BY DATE_TRUNC('month', review_date)
ORDER BY month DESC;

-- Rating trends over time
SELECT 
    DATE_TRUNC('month', review_date) AS month,
    ROUND(AVG(rating), 2) AS avg_rating,
    COUNT(*) AS review_count
FROM reviews
GROUP BY DATE_TRUNC('month', review_date)
ORDER BY month DESC;

-- ============================================================================
-- DATA INTEGRITY SUMMARY
-- ============================================================================

-- Overall data quality summary
SELECT 
    (SELECT COUNT(*) FROM reviews) AS total_reviews,
    (SELECT COUNT(*) FROM reviews WHERE sentiment_label IS NOT NULL) AS reviews_with_sentiment,
    (SELECT COUNT(*) FROM reviews WHERE sentiment_score IS NOT NULL) AS reviews_with_score,
    (SELECT COUNT(DISTINCT bank_id) FROM reviews) AS banks_with_reviews,
    (SELECT MIN(review_date) FROM reviews) AS earliest_review,
    (SELECT MAX(review_date) FROM reviews) AS latest_review;

