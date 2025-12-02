# Quick PostgreSQL Installation

## 🚀 Fastest Way (3 Steps)

### Step 1: Run Installation Script

```powershell
# Right-click PowerShell and select "Run as Administrator"
.\install_postgresql.ps1
```

The script will:
- Download PostgreSQL installer
- Launch the installer
- Guide you through setup

### Step 2: During Installation

**Important settings:**
- ✅ Port: `5432` (default - keep this)
- ✅ Password: **Set a password for 'postgres' user** (remember it!)
- ✅ Install as Windows service: **Check this**

### Step 3: After Installation

```powershell
# Set password environment variable
$env:POSTGRES_PASSWORD="your_password"

# Run Task 3
.\venv\Scripts\python.exe src\task3_main.py
```

## ✅ Done!

That's it! The script handles everything else.

---

**Full Guide**: See `INSTALL_POSTGRESQL.md` for detailed instructions

