#!/usr/bin/env python3
"""
Entry point for guiapi - GUI for yt-dlp using Python API directly.

This script launches the GUI that uses yt-dlp's Python API instead of subprocess.
"""

import sys

# Ensure the current directory is in the path
sys.path.insert(0, '.')

from guiapi import main

if __name__ == '__main__':
    main()
