"""
Script to scrape reviews for CBE and Dashen Bank only
Run this after finding the correct package IDs
"""

import sys
import os
from datetime import datetime
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper import PlayStoreScraper
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Scrape reviews for CBE and Dashen Bank only"""
    logger.info("="*70)
    logger.info("Scraping Reviews for CBE and Dashen Bank")
    logger.info("="*70)
    
    scraper = PlayStoreScraper(min_reviews_per_bank=400)
    
    # Scrape only CBE and Dashen
    banks_to_scrape = ['CBE', 'Dashen']
    all_reviews = scraper.collect_reviews_for_banks(banks_to_scrape)
    
    # Calculate totals
    total_reviews = sum(len(reviews) for reviews in all_reviews.values())
    
    logger.info("\n" + "="*70)
    logger.info("Collection Summary")
    logger.info("="*70)
    for bank, reviews in all_reviews.items():
        logger.info(f"{bank}: {len(reviews)} reviews")
    logger.info(f"Total: {total_reviews} reviews")
    logger.info("="*70)
    
    # Load existing data if it exists
    existing_file = None
    existing_data = {}
    
    # Find most recent raw data file
    raw_dir = 'data/raw'
    if os.path.exists(raw_dir):
        json_files = [f for f in os.listdir(raw_dir) if f.endswith('.json')]
        if json_files:
            existing_file = os.path.join(raw_dir, sorted(json_files)[-1])
            logger.info(f"\nLoading existing data from: {existing_file}")
            with open(existing_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
    
    # Merge new data with existing data
    for bank in banks_to_scrape:
        if bank in all_reviews and len(all_reviews[bank]) > 0:
            existing_data[bank] = all_reviews[bank]
            logger.info(f"Updated {bank} with {len(all_reviews[bank])} reviews")
        elif bank in existing_data:
            logger.info(f"Keeping existing {bank} data: {len(existing_data[bank])} reviews")
    
    # Save merged data
    if total_reviews > 0 or existing_data:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'reviews_raw_{timestamp}.json'
        filepath = scraper.save_raw_data(existing_data, filename)
        logger.info(f"\n✓ Data saved to: {filepath}")
        logger.info("\nNext step: Run preprocessing to clean the data")
        logger.info("  python src/preprocessor.py")
    else:
        logger.error("\n✗ No reviews collected. Please verify package IDs.")
        logger.error("  You may need to manually find the package IDs from Google Play Store")
        logger.error("  and update APP_CONFIGS in src/scraper.py")
    
    return all_reviews


if __name__ == '__main__':
    main()

