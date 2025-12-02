# ============================================================================
# PostgreSQL Installation Script for Windows
# Omega Consultancy - Task 3 Setup
# ============================================================================

param(
    [string]$Version = "16",
    [string]$InstallPath = "C:\Program Files\PostgreSQL\$Version",
    [string]$DataPath = "C:\Program Files\PostgreSQL\$Version\data",
    [string]$Port = "5432",
    [string]$Password = "",
    [switch]$Silent = $false
)

$ErrorActionPreference = "Stop"

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "PostgreSQL Installation Script" -ForegroundColor Cyan
Write-Host "Omega Consultancy - Task 3 Setup" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "WARNING: Not running as Administrator. Some operations may fail." -ForegroundColor Yellow
    Write-Host "Right-click PowerShell and select 'Run as Administrator' for full installation." -ForegroundColor Yellow
    Write-Host ""
}

# Check if PostgreSQL is already installed
Write-Host "[1/5] Checking for existing PostgreSQL installation..." -ForegroundColor Green
$existingService = Get-Service -Name "*postgres*" -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Host "  Found existing PostgreSQL service: $($existingService.Name)" -ForegroundColor Yellow
    $response = Read-Host "  Do you want to continue anyway? (y/n)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "Installation cancelled." -ForegroundColor Yellow
        exit 0
    }
}

# Check if port 5432 is in use
Write-Host "[2/5] Checking if port $Port is available..." -ForegroundColor Green
$portInUse = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "  WARNING: Port $Port is already in use!" -ForegroundColor Red
    Write-Host "  Process: $($portInUse.OwningProcess)" -ForegroundColor Red
    Write-Host "  You may need to stop the service using this port first." -ForegroundColor Yellow
}

# Download PostgreSQL installer
Write-Host "[3/5] Downloading PostgreSQL installer..." -ForegroundColor Green

$downloadUrl = "https://get.enterprisedb.com/postgresql/postgresql-$Version-1-windows-x64.exe"
$installerPath = "$env:TEMP\postgresql-$Version-installer.exe"

Write-Host "  Download URL: $downloadUrl" -ForegroundColor Gray
Write-Host "  Saving to: $installerPath" -ForegroundColor Gray

try {
    # Check if file already exists
    if (Test-Path $installerPath) {
        $response = Read-Host "  Installer already exists. Re-download? (y/n)"
        if ($response -eq "y" -or $response -eq "Y") {
            Remove-Item $installerPath -Force
        } else {
            Write-Host "  Using existing installer." -ForegroundColor Green
        }
    }
    
    if (-not (Test-Path $installerPath)) {
        Write-Host "  Downloading (this may take a few minutes)..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath -UseBasicParsing
        Write-Host "  [OK] Download complete!" -ForegroundColor Green
    } else {
        Write-Host "  [OK] Using existing installer." -ForegroundColor Green
    }
} catch {
    Write-Host "  [ERROR] Download failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternative: Manual download" -ForegroundColor Yellow
    Write-Host "1. Visit: https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
    Write-Host "2. Download PostgreSQL $Version installer" -ForegroundColor Yellow
    Write-Host "3. Run the installer manually" -ForegroundColor Yellow
    exit 1
}

# Installation instructions
Write-Host ""
Write-Host "[4/5] Installation Instructions" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The PostgreSQL installer will now open. Please follow these steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Click 'Next' through the welcome screens" -ForegroundColor White
Write-Host "2. Installation Directory: $InstallPath" -ForegroundColor White
Write-Host "3. Select Components: Keep all defaults (PostgreSQL Server, pgAdmin, Command Line Tools)" -ForegroundColor White
Write-Host "4. Data Directory: $DataPath" -ForegroundColor White
Write-Host "5. Password: Set a password for the 'postgres' superuser" -ForegroundColor White
Write-Host "   [IMPORTANT] REMEMBER THIS PASSWORD - you'll need it for Task 3!" -ForegroundColor Red
Write-Host "6. Port: $Port (default - keep this)" -ForegroundColor White
Write-Host "7. Advanced Options: Keep defaults" -ForegroundColor White
Write-Host "8. Pre Installation Summary: Review and click 'Next'" -ForegroundColor White
Write-Host "9. Ready to Install: Click 'Next' to begin installation" -ForegroundColor White
Write-Host "10. Completing: Check 'Launch Stack Builder' if you want, then 'Finish'" -ForegroundColor White
Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Prompt for password (for reference, not used in silent install)
if ([string]::IsNullOrEmpty($Password)) {
    Write-Host "Please enter the password you will use for the 'postgres' user:" -ForegroundColor Yellow
    $securePassword = Read-Host "Password" -AsSecureString
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
    $Password = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
    Write-Host ""
}

# Launch installer
Write-Host "[5/5] Launching PostgreSQL installer..." -ForegroundColor Green
Write-Host ""

try {
    Start-Process -FilePath $installerPath -Wait
    Write-Host "[OK] Installer completed!" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to launch installer: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual installation:" -ForegroundColor Yellow
    Write-Host "  Run: $installerPath" -ForegroundColor White
    exit 1
}

# Verify installation
Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "Verifying Installation" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

Start-Sleep -Seconds 3

# Check service
Write-Host "Checking PostgreSQL service..." -ForegroundColor Green
$service = Get-Service -Name "*postgres*" -ErrorAction SilentlyContinue
if ($service) {
    Write-Host "  [OK] Service found: $($service.Name)" -ForegroundColor Green
    Write-Host "  Status: $($service.Status)" -ForegroundColor Gray
    
    if ($service.Status -ne "Running") {
        Write-Host "  Starting service..." -ForegroundColor Yellow
        try {
            Start-Service -Name $service.Name
            Start-Sleep -Seconds 2
            Write-Host "  [OK] Service started!" -ForegroundColor Green
        } catch {
            Write-Host "  [ERROR] Could not start service. You may need to start it manually." -ForegroundColor Red
        }
    }
} else {
    Write-Host "  [ERROR] Service not found. Installation may have failed." -ForegroundColor Red
}

# Check if psql is available
Write-Host ""
Write-Host "Checking PostgreSQL commands..." -ForegroundColor Green
$psqlPath = Get-Command psql -ErrorAction SilentlyContinue
if ($psqlPath) {
    Write-Host "  [OK] psql found: $($psqlPath.Source)" -ForegroundColor Green
    try {
        $version = & psql --version 2>&1
        Write-Host "  Version: $version" -ForegroundColor Gray
    } catch {
        Write-Host "  Could not get version" -ForegroundColor Gray
    }
} else {
    Write-Host "  [WARNING] psql not in PATH. You may need to add PostgreSQL bin to PATH." -ForegroundColor Yellow
    Write-Host "  Typical path: C:\Program Files\PostgreSQL\$Version\bin" -ForegroundColor Gray
}

# Test connection
Write-Host ""
Write-Host "Testing connection..." -ForegroundColor Green
if (-not [string]::IsNullOrEmpty($Password)) {
    try {
        $env:PGPASSWORD = $Password
        $testResult = & psql -U postgres -h localhost -p $Port -c "SELECT version();" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK] Connection successful!" -ForegroundColor Green
        } else {
            Write-Host "  [ERROR] Connection failed. Error:" -ForegroundColor Red
            Write-Host "  $testResult" -ForegroundColor Red
        }
        $env:PGPASSWORD = ""
    } catch {
        Write-Host "  [WARNING] Could not test connection. You can test manually with:" -ForegroundColor Yellow
        Write-Host "  psql -U postgres -c 'SELECT version();'" -ForegroundColor Gray
    }
} else {
    Write-Host "  [SKIP] Password not set, skipping connection test" -ForegroundColor Yellow
}

# Final instructions
Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Green
Write-Host ""
Write-Host "1. Set PostgreSQL password environment variable:" -ForegroundColor White
Write-Host '   $env:POSTGRES_PASSWORD="' -NoNewline -ForegroundColor Cyan
Write-Host "$Password" -NoNewline -ForegroundColor Cyan
Write-Host '"' -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Run Task 3 pipeline:" -ForegroundColor White
Write-Host "   .\venv\Scripts\python.exe src\task3_main.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Verify database:" -ForegroundColor White
Write-Host '   psql -U postgres -d bank_reviews -c "SELECT COUNT(*) FROM reviews;"' -ForegroundColor Cyan
Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan

