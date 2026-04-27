"""
build_exe.py — Run this on a Windows machine to produce setup.exe
Requires: pip install pyinstaller
"""
import subprocess
import sys
import os

# The script that becomes the .exe
SOURCE = "install.py"

cmd = [
    sys.executable, "-m", "PyInstaller",
    "--noconfirm",
    "--onefile",                    # single .exe file
    "--console",                    # show terminal (needed for input() prompts)
    "--name", "setup",              # output: dist/setup.exe
    "--icon", "icon.ico",           # optional — remove if no icon.ico
    "--add-data", ".env;.",         # bundle .env if it exists
    SOURCE
]

# Remove --icon line if icon.ico doesn't exist
if not os.path.exists("icon.ico"):
    cmd = [c for c in cmd if c not in ["--icon", "icon.ico"]]

print(f"Building setup.exe from {SOURCE}...")
subprocess.run(cmd)
print("\nDone! Find it at: dist/setup.exe")
