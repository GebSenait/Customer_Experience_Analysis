# PostgreSQL Installation Guide - PowerShell

## Quick Install (Recommended)

Run the installation script:

```powershell
# Run as Administrator (Right-click PowerShell → Run as Administrator)
.\install_postgresql.ps1
```

The script will:
1. ✅ Check for existing installations
2. ✅ Download PostgreSQL installer
3. ✅ Launch the installer
4. ✅ Verify installation
5. ✅ Test connection

## Manual Installation Steps

If you prefer to install manually:

### Step 1: Download PostgreSQL

```powershell
# Option A: Use the script to download
.\install_postgresql.ps1

# Option B: Download manually
# Visit: https://www.postgresql.org/download/windows/
# Or use PowerShell:
$url = "https://get.enterprisedb.com/postgresql/postgresql-16-1-windows-x64.exe"
$output = "$env:TEMP\postgresql-installer.exe"
Invoke-WebRequest -Uri $url -OutFile $output
Start-Process $output
```

### Step 2: Run Installer

Follow these steps in the installer:

1. **Welcome**: Click "Next"
2. **Installation Directory**: 
   - Default: `C:\Program Files\PostgreSQL\16`
   - Click "Next"
3. **Select Components**: 
   - ✅ PostgreSQL Server
   - ✅ pgAdmin 4 (optional but recommended)
   - ✅ Stack Builder (optional)
   - ✅ Command Line Tools
   - Click "Next"
4. **Data Directory**: 
   - Default: `C:\Program Files\PostgreSQL\16\data`
   - Click "Next"
5. **Password**: 
   - **Set password for 'postgres' user**
   - ⚠️ **REMEMBER THIS PASSWORD!**
   - Click "Next"
6. **Port**: 
   - Default: `5432`
   - Keep default, click "Next"
7. **Advanced Options**: 
   - Locale: Default
   - Click "Next"
8. **Pre Installation Summary**: 
   - Review settings
   - Click "Next"
9. **Ready to Install**: 
   - Click "Next" to begin
   - Wait for installation (2-5 minutes)
10. **Completing**: 
    - Uncheck "Launch Stack Builder" (optional)
    - Click "Finish"

### Step 3: Verify Installation

```powershell
# Check if service is running
Get-Service -Name "*postgres*"

# Check PostgreSQL version
psql --version

# Test connection (will prompt for password)
psql -U postgres -c "SELECT version();"
```

### Step 4: Set Environment Variable

```powershell
# Set password for current session
$env:POSTGRES_PASSWORD="your_password"

# Or set permanently (requires restart)
[System.Environment]::SetEnvironmentVariable("POSTGRES_PASSWORD", "your_password", "User")
```

### Step 5: Run Task 3

```powershell
# Make sure password is set
$env:POSTGRES_PASSWORD="your_password"

# Run Task 3
.\venv\Scripts\python.exe src\task3_main.py
```

## Troubleshooting

### Service Won't Start

```powershell
# Check service status
Get-Service -Name "*postgres*"

# Start service manually
Start-Service -Name "postgresql-x64-16"  # Replace with your version

# Check service logs
Get-EventLog -LogName Application -Source "PostgreSQL" -Newest 10
```

### Port 5432 Already in Use

```powershell
# Check what's using port 5432
Get-NetTCPConnection -LocalPort 5432

# Stop the process (if safe to do so)
Stop-Process -Id <ProcessID>
```

### psql Not Found

```powershell
# Add PostgreSQL bin to PATH (current session)
$env:PATH += ";C:\Program Files\PostgreSQL\16\bin"

# Or add permanently
[System.Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";C:\Program Files\PostgreSQL\16\bin", "User")
```

### Connection Refused

```powershell
# Check if service is running
Get-Service -Name "*postgres*"

# Check if port is listening
Test-NetConnection -ComputerName localhost -Port 5432

# Check firewall
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*PostgreSQL*"}
```

### Forgot Password

If you forgot the password:

1. **Option 1**: Edit `pg_hba.conf` to allow local connections without password
2. **Option 2**: Reset password using pg_ctl
3. **Option 3**: Reinstall PostgreSQL

## Silent Installation (Advanced)

For automated/silent installation:

```powershell
# Download installer
$url = "https://get.enterprisedb.com/postgresql/postgresql-16-1-windows-x64.exe"
$installer = "$env:TEMP\postgresql-installer.exe"
Invoke-WebRequest -Uri $url -OutFile $installer

# Run silent install (requires response file)
# Note: Silent install is complex, manual install is recommended
.\install_postgresql.ps1 -Silent
```

## Verification Checklist

After installation, verify:

- [ ] PostgreSQL service is running
- [ ] `psql --version` works
- [ ] Can connect: `psql -U postgres -c "SELECT 1;"`
- [ ] Port 5432 is listening
- [ ] Environment variable `POSTGRES_PASSWORD` is set

## Next Steps

Once PostgreSQL is installed:

1. ✅ Set password: `$env:POSTGRES_PASSWORD="your_password"`
2. ✅ Run Task 3: `.\venv\Scripts\python.exe src\task3_main.py`
3. ✅ Verify database: `psql -U postgres -d bank_reviews -c "SELECT COUNT(*) FROM reviews;"`

## Support

- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Windows Installation Guide: https://www.postgresql.org/docs/current/install-windows.html
- Stack Overflow: https://stackoverflow.com/questions/tagged/postgresql

---

**Script**: `install_postgresql.ps1`  
**Run**: `.\install_postgresql.ps1` (as Administrator)

