"""
Google Play Store Review Scraper
Collects reviews for CBE, BOA, and Dashen Bank mobile banking apps
"""

import json
import os
import time
from datetime import datetime
from typing import List, Dict, Optional
import logging

try:
    from google_play_scraper import app, reviews, Sort
except ImportError:
    print("Error: google-play-scraper not installed. Run: pip install -r requirements.txt")
    raise

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/scraper_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PlayStoreScraper:
    """Scraper for Google Play Store reviews"""
    
    # App package IDs - these may need to be updated based on actual app IDs
    # Alternative: search by app name and extract package ID
    APP_CONFIGS = {
        'CBE': {
            'app_name': 'Commercial Bank of Ethiopia',
            'search_terms': ['Commercial Bank of Ethiopia', 'CBE Mobile', 'CBE Banking'],
            'package_id': 'com.cbe.mobilebanking'  # May need verification
        },
        'BOA': {
            'app_name': 'Bank of Abyssinia',
            'search_terms': ['Bank of Abyssinia', 'BOA Mobile', 'BOA Banking'],
            'package_id': 'com.bankofabyssinia.mobile'  # May need verification
        },
        'Dashen': {
            'app_name': 'Dashen Bank',
            'search_terms': ['Dashen Bank', 'Dashen Mobile', 'Dashen Banking'],
            'package_id': 'com.dashenbank.mobile'  # May need verification
        }
    }
    
    def __init__(self, min_reviews_per_bank: int = 400, output_dir: str = 'data/raw'):
        """
        Initialize the scraper
        
        Args:
            min_reviews_per_bank: Minimum number of reviews to collect per bank
            output_dir: Directory to save raw data
        """
        self.min_reviews_per_bank = min_reviews_per_bank
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
    def find_app_package(self, bank: str, search_term: str) -> Optional[str]:
        """
        Attempt to find app package ID by searching
        
        Args:
            bank: Bank identifier
            search_term: Search term for app
            
        Returns:
            Package ID if found, None otherwise
        """
        try:
            # Try using the configured package ID first
            config = self.APP_CONFIGS[bank]
            package_id = config.get('package_id')
            
            # Verify package exists by trying to fetch app info
            try:
                app_info = app(package_id, lang='en', country='et')
                logger.info(f"Found app for {bank}: {app_info.get('title', 'Unknown')}")
                return package_id
            except Exception as e:
                logger.warning(f"Package {package_id} not found for {bank}, trying search...")
                
            # If direct package fails, we'll need to use search
            # Note: google-play-scraper doesn't have direct search, so we'll try common variations
            common_packages = [
                f"com.{bank.lower().replace(' ', '')}.mobilebanking",
                f"com.{bank.lower().replace(' ', '')}.mobile",
                f"com.{bank.lower().replace(' ', '')}.banking",
                f"et.{bank.lower().replace(' ', '')}.mobile",
            ]
            
            for pkg in common_packages:
                try:
                    app_info = app(pkg, lang='en', country='et')
                    logger.info(f"Found app for {bank} via search: {app_info.get('title', 'Unknown')}")
                    return pkg
                except:
                    continue
                    
            return None
            
        except Exception as e:
            logger.error(f"Error finding package for {bank}: {str(e)}")
            return None
    
    def scrape_reviews(self, bank: str, package_id: str) -> List[Dict]:
        """
        Scrape reviews for a specific app
        
        Args:
            bank: Bank identifier
            package_id: Google Play Store package ID
            
        Returns:
            List of review dictionaries
        """
        all_reviews = []
        continuation_token = None
        max_attempts = 50  # Limit to prevent infinite loops
        attempt = 0
        
        logger.info(f"Starting review collection for {bank} (package: {package_id})")
        
        try:
            while len(all_reviews) < self.min_reviews_per_bank and attempt < max_attempts:
                try:
                    # Fetch reviews (200 per batch)
                    result, continuation_token = reviews(
                        package_id,
                        lang='en',
                        country='et',
                        sort=Sort.NEWEST,  # Get newest reviews first
                        count=200,
                        continuation_token=continuation_token
                    )
                    
                    if not result:
                        logger.warning(f"No more reviews available for {bank}")
                        break
                    
                    # Process reviews
                    for review in result:
                        review_data = {
                            'review': review.get('content', ''),
                            'rating': review.get('score', 0),
                            'date': review.get('at', '').strftime('%Y-%m-%d') if review.get('at') else '',
                            'app_name': self.APP_CONFIGS[bank]['app_name'],
                            'bank': bank,
                            'source': 'Google Play',
                            'review_id': review.get('reviewId', ''),
                            'thumbs_up': review.get('thumbsUpCount', 0),
                            'reviewer_name': review.get('userName', '')
                        }
                        all_reviews.append(review_data)
                    
                    logger.info(f"Collected {len(all_reviews)} reviews for {bank}...")
                    
                    # If no continuation token, we've reached the end
                    if not continuation_token:
                        logger.info(f"Reached end of reviews for {bank}")
                        break
                    
                    # Rate limiting - be respectful
                    time.sleep(2)
                    attempt += 1
                    
                except Exception as e:
                    logger.error(f"Error fetching reviews for {bank} (attempt {attempt}): {str(e)}")
                    attempt += 1
                    time.sleep(5)  # Wait longer on error
                    
        except Exception as e:
            logger.error(f"Critical error scraping {bank}: {str(e)}")
            
        logger.info(f"Completed collection for {bank}: {len(all_reviews)} reviews")
        return all_reviews
    
    def collect_all_reviews(self) -> Dict[str, List[Dict]]:
        """
        Collect reviews for all banks
        
        Returns:
            Dictionary mapping bank names to review lists
        """
        all_data = {}
        
        for bank, config in self.APP_CONFIGS.items():
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing {bank}")
            logger.info(f"{'='*60}")
            
            # Find package ID
            package_id = self.find_app_package(bank, config['app_name'])
            
            if not package_id:
                logger.error(f"Could not find package ID for {bank}. Skipping...")
                logger.error(f"Please manually verify the package ID and update APP_CONFIGS in scraper.py")
                all_data[bank] = []
                continue
            
            # Scrape reviews
            reviews = self.scrape_reviews(bank, package_id)
            all_data[bank] = reviews
            
            # Brief pause between banks
            time.sleep(3)
        
        return all_data
    
    def save_raw_data(self, data: Dict[str, List[Dict]], filename: Optional[str] = None):
        """
        Save raw scraped data to JSON file
        
        Args:
            data: Dictionary of bank reviews
            filename: Optional custom filename
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'reviews_raw_{timestamp}.json'
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Raw data saved to {filepath}")
        return filepath


def main():
    """Main execution function"""
    scraper = PlayStoreScraper(min_reviews_per_bank=400)
    
    logger.info("="*60)
    logger.info("Starting Google Play Store Review Collection")
    logger.info("="*60)
    
    # Collect all reviews
    all_reviews = scraper.collect_all_reviews()
    
    # Calculate totals
    total_reviews = sum(len(reviews) for reviews in all_reviews.values())
    
    logger.info("\n" + "="*60)
    logger.info("Collection Summary")
    logger.info("="*60)
    for bank, reviews in all_reviews.items():
        logger.info(f"{bank}: {len(reviews)} reviews")
    logger.info(f"Total: {total_reviews} reviews")
    logger.info("="*60)
    
    # Save raw data
    if total_reviews > 0:
        scraper.save_raw_data(all_reviews)
        logger.info("\n✓ Data collection completed successfully!")
    else:
        logger.error("\n✗ No reviews collected. Please check app package IDs.")
    
    return all_reviews


if __name__ == '__main__':
    main()

