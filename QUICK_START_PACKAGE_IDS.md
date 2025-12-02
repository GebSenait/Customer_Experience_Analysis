# Quick Start: Setting Package IDs

## Fastest Way to Set Package IDs

### Option 1: Interactive Setup (Easiest)

```bash
python src/set_package_ids.py
```

This will:
1. Guide you through finding package IDs
2. Verify they work
3. Automatically update the scraper configuration

### Option 2: Direct Command Line (Fastest if you have the IDs)

```bash
# Set CBE package ID
python src/set_package_ids.py --cbe com.cbe.mobilebanking

# Set Dashen package ID  
python src/set_package_ids.py --dashen com.dashenbank.mobile

# Set both at once
python src/set_package_ids.py --cbe com.cbe.mobilebanking --dashen com.dashenbank.mobile
```

### Option 3: Test Current Package IDs

```bash
python src/set_package_ids.py --test
```

## Finding Package IDs

1. Go to [Google Play Store](https://play.google.com/store)
2. Search for the app (e.g., "Commercial Bank of Ethiopia mobile banking")
3. Click on the app
4. Look at the URL - it will be like:
   ```
   https://play.google.com/store/apps/details?id=com.example.app
   ```
5. Copy the part after `id=` (e.g., `com.example.app`)

## After Setting Package IDs

1. **Test the scraper:**
   ```bash
   python src/scrape_missing_banks.py
   ```

2. **Or run the full pipeline:**
   ```bash
   python src/main.py
   ```

3. **Verify KPIs are met:**
   ```bash
   python src/preprocessor.py
   ```

## Examples

### Example 1: Interactive Setup
```bash
$ python src/set_package_ids.py

Setting Package ID for Commercial Bank of Ethiopia (CBE)
Enter package ID: com.cbe.mobilebanking
[OK] Package ID is valid!
  Title: CBE Mobile Banking
  [OK] Successfully updated CBE package ID
```

### Example 2: Command Line
```bash
$ python src/set_package_ids.py --cbe com.cbe.mobilebanking --dashen com.dashenbank.mobile
[OK] Package IDs updated successfully!
```

## Troubleshooting

**Package ID not found?**
- Double-check the package ID from Google Play Store
- Make sure there are no extra spaces
- Try without country code restrictions

**Can't update automatically?**
- The script will show you what to edit manually
- Open `src/scraper.py` and find the `APP_CONFIGS` dictionary
- Update the `package_id` field for the bank

## Current Status

- ✅ **BOA**: Working (`com.bankofabyssinia.mobile`)
- ⚠️ **CBE**: Needs package ID
- ⚠️ **Dashen**: Needs package ID

