# Package ID Setup Instructions for CBE and Dashen Bank

## Problem
The automatic package ID detection could not find valid Google Play Store package IDs for:
- **Commercial Bank of Ethiopia (CBE)**
- **Dashen Bank**

## Solution Options

### Option 1: Manual Package ID Setup (Recommended)

1. **Find the Package IDs Manually:**
   - Go to [Google Play Store](https://play.google.com/store)
   - Search for each bank's mobile banking app:
     - "Commercial Bank of Ethiopia mobile banking"
     - "Dashen Bank mobile banking"
   - Open the app page
   - Look at the URL - it contains the package ID
   - Example: `https://play.google.com/store/apps/details?id=com.example.app`
   - The package ID is the part after `id=`

2. **Use the Manual Setup Script:**
   ```bash
   python src/manual_package_setup.py
   ```
   This script will:
   - Prompt you to enter package IDs
   - Verify they are valid
   - Test scraping with a small sample
   - Show you how to update the configuration

3. **Update the Scraper Configuration:**
   Edit `src/scraper.py` and update the `APP_CONFIGS` dictionary:
   ```python
   'CBE': {
       'app_name': 'Commercial Bank of Ethiopia',
       'package_id': 'YOUR_CBE_PACKAGE_ID_HERE',  # Update this
       ...
   },
   'Dashen': {
       'app_name': 'Dashen Bank',
       'package_id': 'YOUR_DASHEN_PACKAGE_ID_HERE',  # Update this
       ...
   }
   ```

### Option 2: Direct Package ID Input

If you know the package IDs, you can directly update `src/scraper.py`:

1. Open `src/scraper.py`
2. Find the `APP_CONFIGS` dictionary (around line 36)
3. Update the `package_id` field for CBE and Dashen
4. Save the file
5. Run the scraper:
   ```bash
   python src/scrape_missing_banks.py
   ```

### Option 3: Alternative Data Sources

If the apps are not available on Google Play Store, consider:
- Checking if the apps are available on other app stores
- Contacting the banks directly for API access
- Using alternative data collection methods

## Testing

After updating the package IDs, test with:
```bash
python src/find_package_ids.py
```

This will verify the package IDs are correct.

## Current Status

- ✅ **BOA (Bank of Abyssinia)**: Working - Package ID: `com.bankofabyssinia.mobile`
- ❌ **CBE**: Package ID not found (tried 26+ variations)
- ❌ **Dashen Bank**: Package ID not found (tried 26+ variations)

## Next Steps

1. Find the correct package IDs using Option 1 above
2. Update the configuration
3. Run the scraper: `python src/scrape_missing_banks.py`
4. Run preprocessing: `python src/preprocessor.py`
5. Verify KPIs are met

## Notes

- The scraper has been updated to try multiple package ID variations automatically
- It also tries different country codes (Ethiopia, US, default)
- If automatic detection fails, manual setup is required
- All code is ready - we just need the correct package IDs

