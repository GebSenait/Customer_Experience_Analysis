"""
PostgreSQL Installation Detection Script
Checks for PostgreSQL installation in common locations
"""

import os
import subprocess
import sys
from pathlib import Path

def check_directory(path):
    """Check if directory exists"""
    if os.path.exists(path):
        return True, list(os.listdir(path))
    return False, []

def check_command(cmd):
    """Check if command exists and is executable"""
    try:
        result = subprocess.run(
            [cmd, '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return False, None

def check_port(port=5432):
    """Check if port is listening"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False

def main():
    print("="*70)
    print("PostgreSQL Installation Detection")
    print("="*70)
    print()
    
    found = False
    
    # Check common installation directories
    print("Checking installation directories...")
    common_paths = [
        r"C:\Program Files\PostgreSQL",
        r"C:\Program Files (x86)\PostgreSQL",
        r"C:\PostgreSQL",
        os.path.expanduser(r"~\AppData\Local\Programs\PostgreSQL"),
        os.path.expanduser(r"~\PostgreSQL"),
    ]
    
    for path in common_paths:
        exists, contents = check_directory(path)
        if exists:
            print(f"  ✓ Found: {path}")
            if contents:
                print(f"    Contents: {', '.join(contents[:5])}")
                # Look for bin directory
                bin_path = os.path.join(path, contents[0] if contents else '', 'bin')
                if os.path.exists(bin_path):
                    print(f"    Bin directory: {bin_path}")
                    # Check for psql
                    psql_path = os.path.join(bin_path, 'psql.exe')
                    if os.path.exists(psql_path):
                        print(f"    ✓ psql.exe found: {psql_path}")
                        found = True
            found = True
        else:
            print(f"  ✗ Not found: {path}")
    
    print()
    
    # Check for psql in PATH
    print("Checking for PostgreSQL commands in PATH...")
    commands = ['psql', 'pg_ctl', 'pg_config']
    for cmd in commands:
        exists, version = check_command(cmd)
        if exists:
            print(f"  ✓ {cmd} found: {version}")
            found = True
        else:
            print(f"  ✗ {cmd} not found in PATH")
    
    print()
    
    # Check if port 5432 is listening
    print("Checking if PostgreSQL is running on port 5432...")
    if check_port(5432):
        print("  ✓ Port 5432 is listening (PostgreSQL may be running)")
        found = True
    else:
        print("  ✗ Port 5432 is not listening")
    
    print()
    
    # Check Windows services
    print("Checking Windows services...")
    try:
        result = subprocess.run(
            ['sc', 'query', 'type=', 'service', 'state=', 'all'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if 'postgres' in result.stdout.lower():
            print("  ✓ PostgreSQL service found in Windows services")
            found = True
        else:
            print("  ✗ No PostgreSQL service found")
    except:
        print("  ? Could not check Windows services")
    
    print()
    print("="*70)
    
    if found:
        print("RESULT: PostgreSQL appears to be installed but may not be running")
        print()
        print("Next steps:")
        print("1. Start PostgreSQL service:")
        print("   - Open Services (services.msc)")
        print("   - Find 'postgresql' service")
        print("   - Right-click → Start")
        print()
        print("2. Or start manually if you know the installation path:")
        print("   cd \"C:\\Program Files\\PostgreSQL\\XX\\bin\"")
        print("   pg_ctl start -D \"C:\\Program Files\\PostgreSQL\\XX\\data\"")
    else:
        print("RESULT: PostgreSQL does not appear to be installed")
        print()
        print("Next steps:")
        print("1. Download PostgreSQL from: https://www.postgresql.org/download/windows/")
        print("2. Install with default settings")
        print("3. Remember the password you set for 'postgres' user")
        print("4. Ensure 'Install as Windows service' is checked")
    
    print("="*70)

if __name__ == '__main__':
    main()

