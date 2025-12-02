# Package ID Setup - Quick Guide

## ✅ Solution Ready!

I've created a simple script that lets you input package IDs directly. Here's how to use it:

## 🚀 Quick Start

### Method 1: Interactive Mode (Easiest)

```bash
python src/set_package_ids.py
```

This will:
- Guide you step-by-step
- Help you find package IDs
- Verify they work
- Automatically update the configuration

### Method 2: Direct Command Line (Fastest)

If you already have the package IDs from Google Play Store:

```bash
# Set CBE package ID
python src/set_package_ids.py --cbe com.cbe.mobilebanking

# Set Dashen package ID
python src/set_package_ids.py --dashen com.dashenbank.mobile

# Set both at once
python src/set_package_ids.py --cbe com.cbe.mobilebanking --dashen com.dashenbank.mobile
```

### Method 3: Test Current Package IDs

```bash
python src/set_package_ids.py --test
```

## 📋 How to Find Package IDs

1. **Go to Google Play Store:**
   - Visit: https://play.google.com/store

2. **Search for the app:**
   - Search: "Commercial Bank of Ethiopia mobile banking"
   - Search: "Dashen Bank mobile banking"

3. **Open the app page**

4. **Copy the package ID from the URL:**
   - URL looks like: `https://play.google.com/store/apps/details?id=com.example.app`
   - The package ID is the part after `id=`
   - Example: `com.example.app`

## ✨ Features

- ✅ **Automatic verification** - Tests package IDs before saving
- ✅ **Auto-updates configuration** - No manual file editing needed
- ✅ **Multiple input methods** - Interactive or command-line
- ✅ **Error handling** - Clear error messages if package IDs don't work
- ✅ **Test mode** - Check current package IDs anytime

## 📝 Example Usage

### Example 1: Interactive Setup
```
$ python src/set_package_ids.py

Setting Package ID for Commercial Bank of Ethiopia (CBE)
Enter package ID: com.cbe.mobilebanking

Verifying package ID: com.cbe.mobilebanking
[OK] Package ID is valid!
  Title: CBE Mobile Banking
  Developer: Commercial Bank of Ethiopia
  Installs: 1,000,000+
  Score: 4.2
  [OK] App title appears to match Commercial Bank of Ethiopia

Updating scraper.py...
[OK] Successfully updated CBE package ID to: com.cbe.mobilebanking
```

### Example 2: Command Line
```
$ python src/set_package_ids.py --cbe com.cbe.mobilebanking --dashen com.dashenbank.mobile

Setting package ID for CBE: com.cbe.mobilebanking
[OK] Package ID is valid!
  Title: CBE Mobile Banking
[OK] Successfully updated CBE package ID

Setting package ID for Dashen: com.dashenbank.mobile
[OK] Package ID is valid!
  Title: Dashen Bank Mobile
[OK] Successfully updated Dashen package ID

[OK] Package IDs updated successfully!
```

## 🔄 After Setting Package IDs

Once you've set the package IDs:

1. **Test the scraper:**
   ```bash
   python src/scrape_missing_banks.py
   ```

2. **Or run the full pipeline:**
   ```bash
   python src/main.py
   ```

3. **Verify KPIs:**
   ```bash
   python src/preprocessor.py
   ```

## 🛠️ Troubleshooting

### "Package ID not found" Error
- Double-check the package ID from Google Play Store
- Make sure there are no extra spaces
- Try the package ID in a browser first to verify it exists

### "Could not automatically update" Warning
- The script will show you exactly what to edit
- Open `src/scraper.py`
- Find the `APP_CONFIGS` dictionary
- Update the `package_id` field manually

### Need to Test Current Package IDs
```bash
python src/set_package_ids.py --test
```

## 📊 Current Status

- ✅ **BOA**: Working (`com.bankofabyssinia.mobile`)
- ⚠️ **CBE**: Needs package ID (use script above)
- ⚠️ **Dashen**: Needs package ID (use script above)

## 🎯 Next Steps

1. Find package IDs from Google Play Store
2. Run: `python src/set_package_ids.py`
3. Enter the package IDs when prompted
4. Run: `python src/scrape_missing_banks.py`
5. Verify data collection worked!

---

**That's it!** The script handles everything else automatically. 🎉

