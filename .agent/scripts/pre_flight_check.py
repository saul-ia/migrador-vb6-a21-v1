#!/usr/bin/env python3
import sys
import shutil
import subprocess
import os
from pathlib import Path

def check_command(command, min_version=None):
    """Check if a command exists and optionally check its version."""
    path = shutil.which(command)
    if not path:
        print(f"❌ {command} not found in PATH")
        return False
    
    version_output = ""
    try:
        if command == "node":
            version_output = subprocess.check_output([command, "--version"], text=True).strip()
        elif command == "npm":
            version_output = subprocess.check_output([command, "--version"], text=True).strip()
        elif command == "python":
            version_output = subprocess.check_output([command, "--version"], text=True).strip()
        elif command == "pip":
             version_output = subprocess.check_output([command, "--version"], text=True).strip()
             
        print(f"✅ {command} found: {version_output} ({path})")
        return True
    except Exception as e:
        print(f"⚠️  {command} found but failed to get version: {e}")
        return True

def main():
    print("🚀 Pre-flight Checks initiating...")
    
    checks = [
        "node",
        "npm", 
        "python",
        "pip"
    ]
    
    failed = False
    for cmd in checks:
        if not check_command(cmd):
            failed = True
            
    # Check for required directories
    required_dirs = [".agent"]
    for d in required_dirs:
        if not os.path.exists(d):
             print(f"❌ Required directory missing: {d}")
             failed = True
        else:
             print(f"✅ Directory exists: {d}")

    if failed:
        print("\n❌ Pre-flight checks FAILED. Please fix the issues above.")
        sys.exit(1)
    else:
        print("\n✅ All systems GO! Ready for takeoff. ✈️")
        sys.exit(0)

if __name__ == "__main__":
    main()
