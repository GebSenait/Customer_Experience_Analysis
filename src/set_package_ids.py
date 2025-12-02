"""
Direct Package ID Input Script
Quickly set package IDs for CBE and Dashen Bank apps
"""

import sys
import os
import re
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from google_play_scraper import app
except ImportError:
    print("Error: google-play-scraper not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


def verify_package_id(package_id: str) -> Optional[dict]:
    """Verify if a package ID is valid and return app info"""
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
        except Exception:
            continue
    
    return None


def update_scraper_file(bank: str, package_id: str) -> bool:
    """Update the package_id in scraper.py file"""
    scraper_file = os.path.join(os.path.dirname(__file__), 'scraper.py')
    
    try:
        with open(scraper_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find the line with package_id for this bank
        in_bank_block = False
        updated = False
        bank_indent = None
        
        for i, line in enumerate(lines):
            # Check if we're entering the bank's block
            if f"'{bank}':" in line or f'"{bank}":' in line:
                in_bank_block = True
                # Get the indentation level
                bank_indent = len(line) - len(line.lstrip())
                continue
            
            if in_bank_block:
                # Check if we're leaving the bank's block
                current_indent = len(line) - len(line.lstrip()) if line.strip() else None
                
                # If we hit a line with same or less indent that's not part of this block, we've left
                if current_indent is not None and current_indent <= bank_indent:
                    if line.strip() and not any(key in line for key in ['app_name', 'search_terms', 'package_id', 'alternative_packages', '#']):
                        # This might be the next bank or closing brace
                        if not line.strip().startswith('}'):
                            in_bank_block = False
                            continue
                
                # Look for package_id line
                if "'package_id':" in line or '"package_id":' in line:
                    # Extract the current package ID and replace it
                    # Pattern: 'package_id': 'old_id',  or  "package_id": "old_id",
                    # Handle both single and double quotes, and with/without trailing comma
                    patterns = [
                        (r"(['\"]package_id['\"]:\s*['\"])([^'\"]+)(['\"][,\s]*)", rf"\1{package_id}\3"),
                        (r"(['\"]package_id['\"]:\s*['\"])([^'\"]+)(['\"])", rf"\1{package_id}\3"),
                    ]
                    
                    for pattern, replacement in patterns:
                        new_line = re.sub(pattern, replacement, line)
                        if new_line != line:
                            lines[i] = new_line
                            updated = True
                            break
                    
                    if updated:
                        break
        
        if updated:
            with open(scraper_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True
        else:
            print(f"\nWarning: Could not automatically update {bank} package_id in scraper.py")
            print(f"Please manually edit scraper.py and find:")
            print(f"  '{bank}': {{")
            print(f"      'package_id': '...',  # <-- Change this to: '{package_id}'")
            return False
            
    except Exception as e:
        print(f"Error updating scraper.py: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def set_package_id_interactive(bank: str, bank_display_name: str):
    """Interactive function to set package ID for a bank"""
    print(f"\n{'='*70}")
    print(f"Setting Package ID for {bank_display_name} ({bank})")
    print("="*70)
    print("\nTo find the package ID:")
    print("1. Go to Google Play Store: https://play.google.com/store")
    print("2. Search for the app")
    print("3. Open the app page")
    print("4. Look at the URL - it will be like:")
    print("   https://play.google.com/store/apps/details?id=com.example.app")
    print("5. The package ID is the part after 'id=' (e.g., com.example.app)")
    print("\n" + "-"*70)
    
    while True:
        package_id = input(f"\nEnter package ID for {bank_display_name} (or 'skip' to skip, 'test' to test existing): ").strip()
        
        if not package_id:
            print("Please enter a valid package ID, 'skip', or 'test'")
            continue
        
        if package_id.lower() == 'skip':
            print(f"Skipping {bank}")
            return None
        
        if package_id.lower() == 'test':
            # Test the current package ID from scraper.py
            from scraper import PlayStoreScraper
            scraper = PlayStoreScraper()
            config = scraper.APP_CONFIGS.get(bank, {})
            current_id = config.get('package_id', 'Not set')
            print(f"Current package ID: {current_id}")
            if current_id and current_id != 'Not set':
                result = verify_package_id(current_id)
                if result:
                    print(f"[OK] Package ID is valid!")
                    print(f"  Title: {result['title']}")
                    print(f"  Developer: {result['developer']}")
                else:
                    print(f"[ERROR] Package ID is not valid")
            continue
        
        # Verify the package ID
        print(f"\nVerifying package ID: {package_id}")
        result = verify_package_id(package_id)
        
        if result:
            print(f"\n[OK] Package ID is valid!")
            print(f"  Title: {result['title']}")
            print(f"  Developer: {result['developer']}")
            print(f"  Installs: {result['installs']}")
            print(f"  Score: {result['score']}")
            
            # Check if it seems like the right app
            title_lower = result['title'].lower()
            if any(keyword in title_lower for keyword in ['cbe', 'commercial', 'dashen', 'bank', 'banking']):
                print(f"  [OK] App title appears to match {bank_display_name}")
            else:
                print(f"  [WARNING] App title doesn't clearly match {bank_display_name}")
                confirm = input("  Use this package ID anyway? (y/n): ").strip().lower()
                if confirm != 'y':
                    continue
            
            # Update the scraper file
            print(f"\nUpdating scraper.py...")
            if update_scraper_file(bank, package_id):
                print(f"[OK] Successfully updated {bank} package ID to: {package_id}")
            else:
                print(f"[WARNING] Could not auto-update. Please manually edit scraper.py")
            
            return package_id
        else:
            print(f"[ERROR] Package ID '{package_id}' not found on Google Play Store")
            retry = input("Try another package ID? (y/n): ").strip().lower()
            if retry != 'y':
                return None


def set_package_id_from_args(bank: str, package_id: str) -> bool:
    """Set package ID from command line arguments"""
    print(f"\nSetting package ID for {bank}: {package_id}")
    
    # Verify the package ID
    result = verify_package_id(package_id)
    
    if result:
        print(f"[OK] Package ID is valid!")
        print(f"  Title: {result['title']}")
        print(f"  Developer: {result['developer']}")
        
        # Update the scraper file
        if update_scraper_file(bank, package_id):
            print(f"[OK] Successfully updated {bank} package ID")
            return True
        else:
            print(f"[WARNING] Could not auto-update. Please manually edit scraper.py")
            return False
    else:
        print(f"[ERROR] Package ID '{package_id}' not found on Google Play Store")
        return False


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Set Google Play Store package IDs for CBE and Dashen Bank apps',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (recommended)
  python src/set_package_ids.py
  
  # Set CBE package ID directly
  python src/set_package_ids.py --cbe com.cbe.mobilebanking
  
  # Set Dashen package ID directly
  python src/set_package_ids.py --dashen com.dashenbank.mobile
  
  # Set both at once
  python src/set_package_ids.py --cbe com.cbe.mobilebanking --dashen com.dashenbank.mobile
        """
    )
    
    parser.add_argument('--cbe', type=str, help='Package ID for Commercial Bank of Ethiopia (CBE)')
    parser.add_argument('--dashen', type=str, help='Package ID for Dashen Bank')
    parser.add_argument('--test', action='store_true', help='Test current package IDs')
    
    args = parser.parse_args()
    
    print("="*70)
    print("Package ID Setup for Ethiopian Bank Apps")
    print("="*70)
    
    # Test mode
    if args.test:
        print("\nTesting current package IDs...")
        from scraper import PlayStoreScraper
        scraper = PlayStoreScraper()
        
        for bank in ['CBE', 'Dashen']:
            config = scraper.APP_CONFIGS.get(bank, {})
            package_id = config.get('package_id', 'Not set')
            print(f"\n{bank}: {package_id}")
            if package_id and package_id != 'Not set':
                result = verify_package_id(package_id)
                if result:
                    print(f"  [OK] Valid - {result['title']}")
                else:
                    print(f"  [ERROR] Invalid package ID")
        return
    
    # Command line arguments mode
    if args.cbe or args.dashen:
        success = True
        if args.cbe:
            success = set_package_id_from_args('CBE', args.cbe) and success
        if args.dashen:
            success = set_package_id_from_args('Dashen', args.dashen) and success
        
        if success:
            print("\n" + "="*70)
            print("[OK] Package IDs updated successfully!")
            print("="*70)
            print("\nNext steps:")
            print("1. Test the scraper: python src/scrape_missing_banks.py")
            print("2. Or run full pipeline: python src/main.py")
        else:
            print("\n" + "="*70)
            print("[ERROR] Some package IDs could not be set")
            print("="*70)
        
        return
    
    # Interactive mode
    print("\nInteractive Mode - Enter package IDs when prompted")
    print("You can also use command-line arguments:")
    print("  python src/set_package_ids.py --cbe <package_id> --dashen <package_id>")
    
    results = {}
    
    # Set CBE
    cbe_id = set_package_id_interactive('CBE', 'Commercial Bank of Ethiopia')
    if cbe_id:
        results['CBE'] = cbe_id
    
    # Set Dashen
    dashen_id = set_package_id_interactive('Dashen', 'Dashen Bank')
    if dashen_id:
        results['Dashen'] = dashen_id
    
    # Summary
    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    if results:
        print("\nPackage IDs set:")
        for bank, pkg_id in results.items():
            print(f"  {bank}: {pkg_id}")
        print("\nNext steps:")
        print("1. Test the scraper: python src/scrape_missing_banks.py")
        print("2. Or run full pipeline: python src/main.py")
    else:
        print("\nNo package IDs were set.")
        print("You can run this script again or set them manually in src/scraper.py")


if __name__ == '__main__':
    main()

