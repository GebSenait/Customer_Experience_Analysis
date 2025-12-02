# Fix: PostgreSQL Password Issue

## Problem

You're getting this error:
```
fe_sendauth: no password supplied
```

This means PostgreSQL is installed and running, but the password environment variable is not set.

## Quick Fix

### Step 1: Set the Password

**In PowerShell:**
```powershell
$env:POSTGRES_PASSWORD="your_postgres_password"
```

Replace `your_postgres_password` with the password you set during PostgreSQL installation.

### Step 2: Verify It's Set

```powershell
echo $env:POSTGRES_PASSWORD
```

### Step 3: Run Task 3 Again

```powershell
.\venv\Scripts\python.exe src\task3_main.py
```

## Alternative: Pass Password as Argument

You can also pass the password directly:

```powershell
.\venv\Scripts\python.exe src\task3_main.py --password your_postgres_password
```

## Permanent Solution (Optional)

To set the password permanently for your user:

```powershell
[System.Environment]::SetEnvironmentVariable("POSTGRES_PASSWORD", "your_postgres_password", "User")
```

Then restart your terminal/PowerShell.

## What Was Fixed

1. ✅ Unicode encoding errors fixed (replaced ✓/✗ with [OK]/[ERROR])
2. ✅ Better error messages that tell you exactly what to do
3. ✅ Password validation with helpful instructions

## Still Having Issues?

1. **Forgot your password?**
   - Check if you saved it during installation
   - Or reset it in PostgreSQL

2. **Password not working?**
   - Verify PostgreSQL is running: `Get-Service -Name "*postgres*"`
   - Test connection: `psql -U postgres -c "SELECT 1;"`
   - Check if password is correct

3. **Environment variable not persisting?**
   - Set it in the same PowerShell session where you run the script
   - Or use the `--password` argument instead

