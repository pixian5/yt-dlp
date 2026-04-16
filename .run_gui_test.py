import tkinter as tk
import sys

# Minimal runner: instantiate GUI and destroy after short delay
try:
    from yt_dlp.gui import YtDlpGUI
except Exception as e:
    print('IMPORT_ERROR:', e)
    sys.exit(2)

try:
    root = tk.Tk()
    app = YtDlpGUI(root)
    print('GUI_INIT_OK')
    sys.stdout.flush()
    # Destroy after short delay
    root.after(1000, root.destroy)
    root.mainloop()
    print('GUI_EXIT_OK')
except Exception as e:
    print('RUN_ERROR:', e)
    sys.exit(3)
