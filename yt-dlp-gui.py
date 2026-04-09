#!/usr/bin/env python3
"""
yt-dlp GUI Launcher

This script launches the graphical user interface for yt-dlp.
It can be executed directly or via:
    python yt-dlp-gui.py
or
    python -m yt_dlp.gui
"""

import sys

if __name__ == '__main__':
    # Add the parent directory to the path if running as a standalone script
    import os.path
    if not getattr(sys, 'frozen', False):
        path = os.path.realpath(os.path.abspath(__file__))
        sys.path.insert(0, os.path.dirname(path))

    try:
        import yt_dlp
        # If called with -m yt_dlp (as used by the GUI subprocess), run the CLI main
        if len(sys.argv) > 2 and sys.argv[1:3] == ['-m', 'yt_dlp']:
            original_argv = sys.argv[:]
            sys.argv = [original_argv[0]] + original_argv[3:]
            yt_dlp.main()
        else:
            yt_dlp.main_gui()
    except ImportError:
        print('ERROR: Unable to import yt_dlp module.')
        print('Please make sure yt-dlp is properly installed.')
        sys.exit(1)
    except Exception as e:
        print(f'ERROR: Failed to launch GUI: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
