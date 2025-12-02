"""
Manual Package ID Setup Script
Use this if automatic package ID detection fails.
Allows you to manually input package IDs for CBE and Dashen Bank.
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper import PlayStoreScraper
from google_play_scraper import app
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def verify_package_id(package_id: str, expected_bank: str) -> bool:
    """Verify if a package ID is valid and matches the expected bank"""
    try:
        app_info = app(package_id, lang='en', country='et')
        title = app_info.get('title', '')
        logger.info(f"\nPackage ID: {package_id}")
        logger.info(f"App Title: {title}")
        logger.info(f"Developer: {app_info.get('developer', 'Unknown')}")
        
        # Check if title contains bank-related keywords
        if any(keyword in title.lower() for keyword in ['cbe', 'commercial', 'dashen', 'bank']):
            logger.info(f"[OK] This appears to be the {expected_bank} app!")
            return True
        else:
            logger.warning(f"[WARNING] Title doesn't clearly match {expected_bank}")
            response = input("Use this package ID anyway? (y/n): ").strip().lower()
            return response == 'y'
    except Exception as e:
        logger.error(f"[ERROR] Package ID not found: {str(e)}")
        return False


def update_scraper_config(bank: str, package_id: str):
    """Update the scraper configuration with the new package ID"""
    scraper_file = os.path.join(os.path.dirname(__file__), 'scraper.py')
    
    with open(scraper_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the package_id for the bank
    pattern = f"'{bank}': {{"
    if pattern in content:
        # Update the primary package_id
        old_pattern = f"'package_id': 'com.{bank.lower()}"
        # This is a simple replacement - in production, you'd want more robust parsing
        logger.info(f"\nTo update the package ID, edit src/scraper.py and change:")
        logger.info(f"  For {bank}: 'package_id': '{package_id}'")
        logger.info(f"\nOr run the scraper with the manual package ID using the script below.")


def main():
    """Interactive script to set up package IDs"""
    print("="*70)
    print("Manual Package ID Setup for CBE and Dashen Bank")
    print("="*70)
    print("\nThis script helps you manually find and verify package IDs.")
    print("To find a package ID:")
    print("1. Go to Google Play Store (play.google.com)")
    print("2. Search for the bank's mobile banking app")
    print("3. Open the app page")
    print("4. Look at the URL - it will contain 'id=' followed by the package ID")
    print("   Example: play.google.com/store/apps/details?id=com.example.app")
    print("   Package ID would be: com.example.app")
    print("="*70)
    
    banks = {
        'CBE': {
            'name': 'Commercial Bank of Ethiopia',
            'package_id': None
        },
        'Dashen': {
            'name': 'Dashen Bank',
            'package_id': None
        }
    }
    
    for bank_key, bank_info in banks.items():
        print(f"\n{'='*70}")
        print(f"Setting up {bank_info['name']} ({bank_key})")
        print("="*70)
        
        while True:
            package_id = input(f"\nEnter package ID for {bank_info['name']} (or 'skip' to skip): ").strip()
            
            if package_id.lower() == 'skip':
                logger.info(f"Skipping {bank_key}")
                break
            
            if not package_id:
                print("Please enter a valid package ID or 'skip'")
                continue
            
            # Verify the package ID
            if verify_package_id(package_id, bank_info['name']):
                banks[bank_key]['package_id'] = package_id
                break
            else:
                retry = input("Try another package ID? (y/n): ").strip().lower()
                if retry != 'y':
                    break
    
    # Summary
    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    for bank_key, bank_info in banks.items():
        if bank_info['package_id']:
            print(f"{bank_key}: {bank_info['package_id']} [OK]")
        else:
            print(f"{bank_key}: Not set")
    
    # Test scraping with the new package IDs
    if any(b['package_id'] for b in banks.values()):
        test = input("\nTest scraping with these package IDs? (y/n): ").strip().lower()
        if test == 'y':
            scraper = PlayStoreScraper(min_reviews_per_bank=10)  # Small number for testing
            
            for bank_key, bank_info in banks.items():
                if bank_info['package_id']:
                    print(f"\nTesting {bank_key} with package ID: {bank_info['package_id']}")
                    try:
                        reviews = scraper.scrape_reviews(bank_key, bank_info['package_id'])
                        print(f"[OK] Successfully scraped {len(reviews)} reviews for {bank_key}")
                    except Exception as e:
                        print(f"[ERROR] Failed to scrape {bank_key}: {str(e)}")
    
    # Instructions for permanent update
    print("\n" + "="*70)
    print("To permanently update the package IDs:")
    print("="*70)
    print("Edit src/scraper.py and update the APP_CONFIGS dictionary:")
    for bank_key, bank_info in banks.items():
        if bank_info['package_id']:
            print(f"  '{bank_key}': {{")
            print(f"      'package_id': '{bank_info['package_id']}',")
            print(f"      ...")
            print(f"  }},")
    
    return banks


if __name__ == '__main__':
    main()

