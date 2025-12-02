"""
Main Execution Script
Orchestrates data collection and preprocessing pipeline
"""

import sys
import os
from datetime import datetime
import logging

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper import PlayStoreScraper
from preprocessor import DataPreprocessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/main_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main pipeline execution"""
    logger.info("="*70)
    logger.info("Customer Experience Analysis - Task 1: Data Collection & Preprocessing")
    logger.info("Omega Consultancy")
    logger.info("="*70)
    
    try:
        # Step 1: Data Collection
        logger.info("\n" + "="*70)
        logger.info("STEP 1: Data Collection")
        logger.info("="*70)
        
        scraper = PlayStoreScraper(min_reviews_per_bank=400)
        raw_data = scraper.collect_all_reviews()
        
        # Save raw data
        raw_filepath = scraper.save_raw_data(raw_data)
        
        # Step 2: Data Preprocessing
        logger.info("\n" + "="*70)
        logger.info("STEP 2: Data Preprocessing")
        logger.info("="*70)
        
        preprocessor = DataPreprocessor()
        cleaned_df = preprocessor.preprocess(input_file=raw_filepath)
        
        # Save processed data
        processed_filepath = preprocessor.save_processed_data(cleaned_df)
        
        # Final Summary
        logger.info("\n" + "="*70)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("="*70)
        logger.info(f"Raw data: {raw_filepath}")
        logger.info(f"Processed data: {processed_filepath}")
        logger.info(f"Total reviews: {len(cleaned_df)}")
        logger.info("="*70)
        
        return cleaned_df
        
    except Exception as e:
        logger.error(f"\n✗ Pipeline failed with error: {str(e)}", exc_info=True)
        raise


if __name__ == '__main__':
    main()

