"""
Helper script to find correct Google Play Store package IDs for bank apps
Tests multiple package ID variations and reports which ones work
"""

import sys
import os
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from google_play_scraper import app
except ImportError:
    print("Error: google-play-scraper not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


def test_package_id(package_id: str, expected_bank: str) -> Optional[dict]:
    """
    Test if a package ID exists and return app info if found
    
    Args:
        package_id: Package ID to test
        expected_bank: Expected bank name for verification
        
    Returns:
        App info dict if found, None otherwise
    """
    # Try different country codes
    countries = ['et', 'us', None]
    
    for country in countries:
        try:
            if country:
                app_info = app(package_id, lang='en', country=country)
            else:
                app_info = app(package_id, lang='en')
            
            return {
                'package_id': package_id,
                'title': app_info.get('title', 'Unknown'),
                'developer': app_info.get('developer', 'Unknown'),
                'installs': app_info.get('installs', 'Unknown'),
                'score': app_info.get('score', 0),
                'country': country or 'default'
            }
        except Exception as e:
            continue
    
    return None


def find_cbe_package():
    """Find CBE package ID"""
    print("\n" + "="*70)
    print("Searching for Commercial Bank of Ethiopia (CBE) app...")
    print("="*70)
    
    cbe_packages = [
        'com.cbe.mobilebanking',
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
    
    found = []
    for pkg in cbe_packages:
        result = test_package_id(pkg, 'CBE')
        if result:
            print(f"\n✓ FOUND: {pkg}")
            print(f"  Title: {result['title']}")
            print(f"  Developer: {result['developer']}")
            print(f"  Installs: {result['installs']}")
            print(f"  Score: {result['score']}")
            found.append(result)
        else:
            print(f"  ✗ {pkg}")
    
    if not found:
        print("\n✗ No valid package IDs found for CBE")
        print("  Please check Google Play Store manually and update the package ID")
    else:
        print(f"\n✓ Found {len(found)} valid package ID(s) for CBE")
    
    return found


def find_dashen_package():
    """Find Dashen Bank package ID"""
    print("\n" + "="*70)
    print("Searching for Dashen Bank app...")
    print("="*70)
    
    dashen_packages = [
        'com.dashenbank.mobile',
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
    
    found = []
    for pkg in dashen_packages:
        result = test_package_id(pkg, 'Dashen')
        if result:
            print(f"\n✓ FOUND: {pkg}")
            print(f"  Title: {result['title']}")
            print(f"  Developer: {result['developer']}")
            print(f"  Installs: {result['installs']}")
            print(f"  Score: {result['score']}")
            found.append(result)
        else:
            print(f"  ✗ {pkg}")
    
    if not found:
        print("\n✗ No valid package IDs found for Dashen Bank")
        print("  Please check Google Play Store manually and update the package ID")
    else:
        print(f"\n✓ Found {len(found)} valid package ID(s) for Dashen Bank")
    
    return found


if __name__ == '__main__':
    print("="*70)
    print("Package ID Finder for Ethiopian Bank Apps")
    print("="*70)
    
    cbe_results = find_cbe_package()
    dashen_results = find_dashen_package()
    
    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    print(f"CBE: {len(cbe_results)} package(s) found")
    print(f"Dashen: {len(dashen_results)} package(s) found")
    
    if cbe_results:
        print(f"\nRecommended CBE package ID: {cbe_results[0]['package_id']}")
    if dashen_results:
        print(f"Recommended Dashen package ID: {dashen_results[0]['package_id']}")

