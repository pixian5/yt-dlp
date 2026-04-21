#!/usr/bin/env python3
"""
GUI Panel for yt-dlp - Graphical User Interface for configuring and running yt-dlp

This module provides a comprehensive GUI interface using tkinter for easy configuration
of all yt-dlp options without needing to remember command-line arguments.
"""

"""
guiapi - GUI for yt-dlp using Python API directly

This package provides a GUI interface that uses yt-dlp's Python API
instead of spawning subprocesses.
"""

from .app import YtDlpGUI, main
from .constants import LANGUAGE_OPTIONS, SB_CATEGORIES, GUI_DEFAULT_STATE
from .translations import TRANSLATIONS

__version__ = '1.0.0'
__all__ = [
    'GUI_DEFAULT_STATE',
    'LANGUAGE_OPTIONS',
    'SB_CATEGORIES',
    'TRANSLATIONS',
    'YtDlpGUI',
    'main',
    '__version__',
]
