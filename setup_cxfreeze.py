#!/usr/bin/env python3
"""
Setup script for building GhostCaller.py into a Windows executable using cx_Freeze.
"""

import sys
from cx_Freeze import setup, Executable

# Base selection: 'Console' for console application (use 'Win32GUI' for GUI apps)
BASE = 'Console'

# Target executable name
TARGET_NAME = 'GhostCaller.exe'

# Main script to build
SCRIPT_PATH = 'GhostCaller/GhostCaller.py'

# Build options
build_exe_options = {
    # Include additional files and directories
    'include_files': [
        'GhostCaller/sip_config.ini',
        'GhostCaller/README.md',
    ],
    # Exclude unnecessary packages to reduce size
    'excludes': [
        'tkinter',
        'test',
        'email',
        'http',
        'urllib',
        'xml',
        'html',
    ],
    # Set the build directory
    'build_exe': 'build',
}

# Create the executable
GhostCaller = Executable(
    script=SCRIPT_PATH,
    target=TARGET_NAME,
    base=BASE,
    # Optional: add an icon if available
    # icon='GhostCaller/icon.ico',
    compress=True,  # Compress the executable
)

# Setup configuration
setup(
    name='GhostCaller',
    version='1.0.0',
    description='GhostCaller Application',
    author='GhostCaller Team',
    options={'build_exe': build_exe_options},
    executables=[GhostCaller],
)