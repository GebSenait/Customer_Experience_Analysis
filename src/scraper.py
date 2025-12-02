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
            'search_terms': ['Commercial Bank of Ethiopia', 'CBE Mobile', 'CBE Banking', 'CBE'],
            'package_id': 'com.cbe.mobilebanking',  # Primary - will try alternatives if fails
            'alternative_packages': [
                'com.cbe.mobile',
                'com.cbe.banking',
                'com.commercialbank.ethiopia',
                'com.commercialbankethiopia.mobile',
                'com.commercialbankethiopia.mobilebanking',
                'et.com.cbe.mobile',
                'com.cbe.ethiopia.mobile',
                'com.cbe.cbemobile',
                'com.cbe.mobilebanking.ethiopia',
                'com.combanketh.mobile',
                'com.cbe.digitalbanking',
                'com.cbe.app',
                'com.cbe.cbe',
                'com.cbe.ethiopia',
                'com.commercialbankethiopia',
                'com.cbe.mbanking',
                'com.cbe.digital',
                'com.cbe.online',
                'com.cbe.mobile.app',
                'com.cbe.bank.mobile',
                'com.cbe.bank.ethiopia',
                'com.cbe.mobile.banking',
                'com.cbe.mobilebanking.app',
                'com.cbe.ethiopia.banking',
                'com.cbe.ethiopia.mobilebanking'
            ]
        },
        'BOA': {
            'app_name': 'Bank of Abyssinia',
            'search_terms': ['Bank of Abyssinia', 'BOA Mobile', 'BOA Banking'],
            'package_id': 'com.bankofabyssinia.mobile',  # This one works
            'alternative_packages': []
        },
        'Dashen': {
            'app_name': 'Dashen Bank',
            'search_terms': ['Dashen Bank', 'Dashen Mobile', 'Dashen Banking', 'Dashen'],
            'package_id': 'com.dashenbank.mobile',  # Primary - will try alternatives if fails
            'alternative_packages': [
                'com.dashenbank.mobilebanking',
                'com.dashen.bank',
                'com.dashen.bank.mobile',
                'com.dashenbank.banking',
                'com.dashen.mobile',
                'et.com.dashenbank.mobile',
                'com.dashenbank.digital',
                'com.dashenbank.app',
                'com.dashen.banking',
                'com.dashenbank.ethiopia.mobile',
                'com.dashen.mobilebanking',
                'com.dashenbank.mobile.app',
                'com.dashen.bank.app',
                'com.dashenbank.superapp',
                'com.dashen.superapp',
                'com.dashenbank.dashen',
                'com.dashen.dashen',
                'com.dashenbank.ethiopia',
                'com.dashen.ethiopia',
                'com.dashenbank.mobile.banking',
                'com.dashenbank.online',
                'com.dashen.online',
                'com.dashenbank.digital.banking'
            ]
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
        Attempt to find app package ID by trying multiple variations
        
        Args:
            bank: Bank identifier
            search_term: Search term for app
            
        Returns:
            Package ID if found, None otherwise
        """
        try:
            config = self.APP_CONFIGS[bank]
            
            # Build list of packages to try
            packages_to_try = [config.get('package_id')]
            
            # Add alternative packages if they exist
            if 'alternative_packages' in config:
                packages_to_try.extend(config['alternative_packages'])
            
            # Also try dynamic variations based on bank name
            bank_lower = bank.lower().replace(' ', '').replace('of', '')
            dynamic_packages = [
                f"com.{bank_lower}.mobilebanking",
                f"com.{bank_lower}.mobile",
                f"com.{bank_lower}.banking",
                f"et.com.{bank_lower}.mobile",
                f"com.{bank_lower}.app",
            ]
            
            # Add dynamic packages that aren't already in the list
            for pkg in dynamic_packages:
                if pkg not in packages_to_try:
                    packages_to_try.append(pkg)
            
            logger.info(f"Trying {len(packages_to_try)} package ID variations for {bank}...")
            
            # Try each package ID with different country codes
            countries_to_try = ['et', 'us', None]  # Try Ethiopia, US, and default
            
            for package_id in packages_to_try:
                if not package_id:
                    continue
                
                for country in countries_to_try:
                    try:
                        logger.info(f"  Trying: {package_id} (country: {country or 'default'})")
                        
                        # Try with country if specified
                        if country:
                            app_info = app(package_id, lang='en', country=country)
                        else:
                            app_info = app(package_id, lang='en')
                        
                        app_title = app_info.get('title', 'Unknown')
                        
                        # Verify it's the right app by checking title
                        if any(term.lower() in app_title.lower() for term in config['search_terms'] + [bank]):
                            logger.info(f"[OK] Found app for {bank}: {app_title} (package: {package_id})")
                            return package_id
                        else:
                            logger.warning(f"  Package {package_id} exists but title '{app_title}' doesn't match {bank}")
                            # Still return it if it seems close (contains bank-related keywords)
                            if any(keyword in app_title.lower() for keyword in ['bank', 'banking', 'mobile', 'cbe', 'dashen']):
                                logger.info(f"  Package seems related, using: {package_id}")
                                return package_id
                        
                        # If we got here with a valid app, break country loop
                        break
                        
                    except Exception as e:
                        # Package not found with this country, try next country
                        continue
            
            logger.error(f"X Could not find valid package ID for {bank} after trying {len(packages_to_try)} variations")
            logger.error(f"  Please manually find the package ID from Google Play Store and update APP_CONFIGS")
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
    
    def collect_reviews_for_banks(self, banks: Optional[List[str]] = None) -> Dict[str, List[Dict]]:
        """
        Collect reviews for specified banks (or all if None)
        
        Args:
            banks: List of bank identifiers to scrape. If None, scrapes all banks.
        
        Returns:
            Dictionary mapping bank names to review lists
        """
        all_data = {}
        
        banks_to_scrape = banks if banks else list(self.APP_CONFIGS.keys())
        
        for bank in banks_to_scrape:
            if bank not in self.APP_CONFIGS:
                logger.warning(f"Unknown bank: {bank}. Skipping...")
                continue
                
            config = self.APP_CONFIGS[bank]
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
    
    def collect_all_reviews(self) -> Dict[str, List[Dict]]:
        """
        Collect reviews for all banks
        
        Returns:
            Dictionary mapping bank names to review lists
        """
        return self.collect_reviews_for_banks()
    
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

