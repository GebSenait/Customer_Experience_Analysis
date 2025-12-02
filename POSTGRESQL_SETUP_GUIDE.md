# PostgreSQL Setup Guide for Task 3

## Issue Detected

The Task 3 script attempted to connect to PostgreSQL but received a connection refused error. This means PostgreSQL is either:
- Not installed
- Not running
- Running on a different port/host

## Quick Fix Options

### Option 1: Check if PostgreSQL Service is Running (Windows)

1. **Check Service Status:**
   ```powershell
   Get-Service -Name "*postgres*"
   ```

2. **Start PostgreSQL Service:**
   ```powershell
   # Find the service name first
   Get-Service -Name "*postgres*" | Select-Object Name
   
   # Then start it (replace with actual service name)
   Start-Service -Name "postgresql-x64-XX"  # Replace XX with version
   ```

   Or use Services GUI:
   - Press `Win + R`, type `services.msc`
   - Find "postgresql" service
   - Right-click → Start

### Option 2: Install PostgreSQL (If Not Installed)

1. **Download PostgreSQL:**
   - Visit: https://www.postgresql.org/download/windows/
   - Download the Windows installer

2. **Install:**
   - Run the installer
   - Remember the password you set for the `postgres` user
   - Default port is 5432 (keep this)
   - Install as a Windows service (recommended)

3. **Verify Installation:**
   ```powershell
   # Check if psql is available
   psql --version
   
   # Or check service
   Get-Service -Name "*postgres*"
   ```

### Option 3: Use Different Connection Settings

If PostgreSQL is installed but on a different host/port, you can specify it:

```bash
python src/task3_main.py --host YOUR_HOST --port YOUR_PORT --user YOUR_USER
```

## After PostgreSQL is Running

Once PostgreSQL is running, set the password (if needed) and run Task 3:

```powershell
# Set password environment variable (if needed)
$env:POSTGRES_PASSWORD="your_password"

# Run Task 3
.\venv\Scripts\python.exe src\task3_main.py
```

## Verify PostgreSQL is Working

Test the connection manually:

```powershell
# If psql is in PATH
psql -U postgres -c "SELECT version();"

# Or use Python to test
.\venv\Scripts\python.exe -c "import psycopg2; conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='your_password', database='postgres'); print('Connection successful!'); conn.close()"
```

## Common PostgreSQL Service Names (Windows)

- `postgresql-x64-16`
- `postgresql-x64-15`
- `postgresql-x64-14`
- `PostgreSQL` (generic)

## Next Steps

1. ✅ Install PostgreSQL (if not installed)
2. ✅ Start PostgreSQL service
3. ✅ Verify connection works
4. ✅ Run Task 3: `python src/task3_main.py`

## Need Help?

- Check PostgreSQL logs (usually in `C:\Program Files\PostgreSQL\XX\data\log\`)
- Verify firewall isn't blocking port 5432
- Check if another application is using port 5432

