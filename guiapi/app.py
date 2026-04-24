#!/usr/bin/env python3
"""
Main GUI application for yt-dlp
"""

import contextlib
import json
import locale
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import subprocess
import signal
import tempfile
import atexit

from guiapi.constants import LANGUAGE_OPTIONS, SB_CATEGORIES, GUI_DEFAULT_STATE
from guiapi.translations import TRANSLATIONS


class YtDlpGUI:
    """Main GUI application for yt-dlp configuration and downloading"""

    def __init__(self, root):
        # Ensure Homebrew binaries (node, ffmpeg, etc.) are on PATH for subprocesses
        homebrew_bin = '/opt/homebrew/bin'
        if homebrew_bin not in os.environ.get('PATH', ''):
            os.environ['PATH'] = homebrew_bin + ':' + os.environ.get('PATH', '')

        self.root = root
        self.base_title = 'yt-dlp GUI - Video Downloader Configuration'
        self._translatable_widgets = {}
        self._notebook_tab_texts = {}
        self._tab_builders = {}
        self._built_tabs = set()
        self._tab_controls = {}
        self._stateful_controls = {}
        self._pending_gui_state = {}
        self._active_tab_frame = None

        self.current_language = 'en'  # Default for very early calls

        # Configuration storage
        self.config = {}
        self.config_file = os.path.expanduser('~/.yt-dlp-gui-config.json')
        self.load_config()
        # Thread-safe logging initialization
        import queue
        self.log_queue = queue.Queue()
        self._start_log_watcher()

        # Variables and state tracking
        self.batch_file_var = tk.StringVar()
        self.reverse_order = tk.BooleanVar(value=False)
        self.exclude_private = tk.BooleanVar(value=True)
        self.batch_urls_text = None
        self.bulk_rows = []

        # Language selection variable with trace
        self.language_var = tk.StringVar()
        self.language_var.trace_add('write', self.on_language_changed_trace)

        # Create main container
        self.create_widgets()

        # Initialize language values AFTER widgets are created
        self.initialize_language()

        # Ensure the selector matches initial state without triggering trace loop
        pref = self.config.get('language', 'auto')
        self.language_var.set(self.get_language_display(pref))

        self.apply_localization()
        self.apply_config()
        self.unify_languages()

        self.root.after(50, self.present_window)
        self.root.protocol('WM_DELETE_WINDOW', self.on_window_close)

        # Set window icon (if available)
        with contextlib.suppress(Exception):
            self.root.iconname('yt-dlp')

    def tr(self, text):
        """Translate UI text with English fallback."""
        if not text:
            return text
        lang = getattr(self, 'current_language', 'en')
        translations = TRANSLATIONS.get(lang, {})
        result = translations.get(text)
        if result is None:
            # If not found in current language, it returns the key itself
            return text
        return result

    def translate_concat(self, prefix, value):
        """Translate a message prefix while preserving dynamic data."""
        return f'{self.tr(prefix)}{value}'

    def detect_system_language(self):
        """Detect the preferred system language and map it to a supported locale."""
        candidates = []

        # 1. First priority: macOS system defaults (Most reliable for user)
        if sys.platform == 'darwin':
            try:
                # Get the AppleLanguages array (e.g. ("zh-Hans-US", "en-US"))
                output = subprocess.check_output(['defaults', 'read', '-g', 'AppleLanguages'],
                                                 stderr=subprocess.DEVNULL, text=True)
                import re
                matches = re.findall(r'"([^"]+)"', output)
                candidates.extend(matches)
            except Exception:
                pass

        # 2. Local environment variables
        for env_name in ('LC_ALL', 'LC_MESSAGES', 'LANG'):
            value = os.environ.get(env_name)
            if value:
                candidates.append(value)

        # 3. Python standard locale
        try:
            lang, _ = locale.getlocale()
            if lang:
                candidates.append(lang)
        except Exception:
            pass

        for candidate in candidates:
            normalized = candidate.replace('-', '_').lower()
            prefix = normalized.split('_', 1)[0]
            self.log_message(f'[DETECTION] Trying candidate: {candidate} -> prefix: {prefix}')
            if prefix in LANGUAGE_OPTIONS:
                self.log_message(f'[DETECTION] SUCCESS! Matched system language: {prefix}')
                return prefix
        self.log_message('[DETECTION] FAILED. Defaulting to: en')
        return 'en'

    def initialize_language(self):
        """Initialize UI language from config; handle 'auto' by resolving to system language."""
        configured_language = self.config.get('language')

        # If it's auto or not set, always perform fresh detection for the session
        if not configured_language or configured_language == 'auto':
            detected = self.detect_system_language()
            self.current_language = detected
            # Return 'auto' if that was the preference, so the caller knows the mode
            return configured_language if configured_language == 'auto' else detected

        if configured_language in LANGUAGE_OPTIONS:
            self.current_language = configured_language
            return configured_language

        detected = self.detect_system_language()
        self.current_language = detected
        return detected

    def write_config_to_disk(self, config):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

    def persist_language_preference(self):
        """Persist only language-related fields for instant switch without heavy full-state save."""
        try:
            self.config['language'] = self.current_language
            self.config['language_initialized'] = True
            self.write_config_to_disk(self.config)
        except Exception as e:
            self.log_message(self.translate_concat('Failed to save configuration: ', str(e)))

    def get_language_display(self, code):
        return LANGUAGE_OPTIONS.get(code, LANGUAGE_OPTIONS['en'])

    def get_language_code_from_display(self, display_name):
        for code, name in LANGUAGE_OPTIONS.items():
            if name == display_name:
                return code
        return 'en'

    def register_translatable_widget(self, widget, text):
        self._translatable_widgets[widget] = text
        return widget

    def apply_localization(self):
        """Refresh translated text on widgets that expose a text property."""
        # self.log_message(f"[LOCALIZE] Starting UI localization to: {self.current_language}")
        self.root.title(self.tr(self.base_title))

        if hasattr(self, 'language_label'):
            self.language_label.config(text=self.tr('Language:'))
        if hasattr(self, 'language_selector'):
            # Use the raw config preference (e.g. 'auto') for the selector display
            pref = self.config.get('language', 'auto')
            self.language_selector.set(self.get_language_display(pref))

        # Force refresh status if it's a known state
        if hasattr(self, 'status_var'):
            self.status_var.set(self.tr('Ready'))

        self.localize_widget_tree(self.root)
        self.localize_notebook_tabs()

        # Explicit treeview heading localization
        if hasattr(self, 'playlist_tree'):
            self.playlist_tree.heading('status', text=' ')
            self.playlist_tree.heading('index', text=self.tr('#'))
            self.playlist_tree.heading('title', text=self.tr('Title'))

        # Refresh resolution selector values if it exists
        if hasattr(self, 'res_selector'):
            res_options = ['Best (Auto)', '4K (2160p)', '2K (1440p)', '1080p 60fps', '1080p', '720p 60fps', '720p', '480p', '360p']
            self.res_selector.config(values=[self.tr(opt) for opt in res_options])

        # self.log_message("[LOCALIZE] UI localization complete.")
        self.drain_log_queue()

    def drain_log_queue(self):
        """Force process all pending log messages immediately."""
        if not hasattr(self, 'log_queue'):
            return
        while not self.log_queue.empty():
            try:
                msg = self.log_queue.get_nowait()
                self._log_message_internal(msg)
            except Exception:
                break

    def localize_widget_tree(self, widget):
        try:
            text = widget.cget('text')
        except tk.TclError:
            text = None

        if text is not None and text.strip():
            # IMPORTANT: We MUST use the original key.
            # If not in registry, WE DO NOT AUTO-REGISTER if it's not likely English.
            # This prevents capturing already-translated text as a new key.
            if widget not in self._translatable_widgets:
                # Only auto-register if the text looks like an English key (contains ASCII/standard symbols)
                try:
                    text.encode('ascii')
                    self._translatable_widgets[widget] = text
                except UnicodeEncodeError:
                    # If it's already non-ASCII, it's likely already translated.
                    # We can't safely use it as a key unless we find it in TRANSLATIONS backwards.
                    pass

            if widget in self._translatable_widgets:
                key = self._translatable_widgets[widget]
                translated = self.tr(key)
                if translated != text:
                    # self.log_message(f"[LOCALIZE] Widget {widget}: Key='{key}' -> Translated='{translated}'")
                    widget.config(text=translated)

        if isinstance(widget, tk.Canvas):
            for item in widget.find_all():
                if widget.type(item) == 'window':
                    sub_widget = widget.nametowidget(widget.itemcget(item, 'window'))
                    self.localize_widget_tree(sub_widget)
        for child in widget.winfo_children():
            self.localize_widget_tree(child)

    def localize_notebook_tabs(self):
        if not hasattr(self, 'notebook'):
            return
        for tab_id in self.notebook.tabs():
            child = self.root.nametowidget(tab_id)
            if child not in self._notebook_tab_texts:
                self._notebook_tab_texts[child] = self.notebook.tab(tab_id, 'text')

            key = self._notebook_tab_texts[child]
            translated = self.tr(key)
            # self.log_message(f"[LOCALIZE] Tab {child}: Key='{key}' -> Translated='{translated}'")
            self.notebook.tab(tab_id, text=translated)

    def on_language_changed_trace(self, *args):
        """Wrapper to handle language change from variable trace."""
        # Use root.after to ensure we are outside the trace update cycle if needed
        self.root.after(1, self.on_language_changed)

    def on_language_changed(self, _event=None):
        display_val = self.language_var.get()
        if not display_val:
            return

        print(f'[LANG] on_language_changed triggered. Value: {display_val}')

        raw_code = self.get_language_code_from_display(display_val)
        new_language = raw_code

        if raw_code == 'auto':
            new_language = self.detect_system_language()
            print(f'[LANG] Auto-detected: {new_language}')

        # Check if actually changed to avoid redundant refreshes
        if getattr(self, 'current_language', None) == new_language:
            # Still update config in case raw_code changed (e.g. from specific to 'auto')
            self.config['language'] = raw_code
            self.persist_language_preference()
            return

        self.log_message(f'[EVENT] Switching language to: {new_language} (Choice: {display_val})')
        print(f'[LANG] Setting current_language to {new_language}')

        # 1. Update state
        self.config['language'] = raw_code
        self.current_language = new_language
        self.persist_language_preference()

        # 2. Apply translations
        self.apply_localization()

        # 3. Explicitly re-localize everything again with a fresh tree traversal
        self.localize_widget_tree(self.root)

        # 4. Sync other components
        self.unify_languages()

        # 5. Force update
        self.root.update_idletasks()
        self.drain_log_queue()
        print('[LANG] Language change completed.')

    def maximize_window(self):
        """Open the window in a maximized state with a geometry fallback."""
        self.root.update_idletasks()
        screen_width, screen_height = self.get_effective_screen_size()

        try:
            self.root.state('zoomed')
            self.root.update_idletasks()
            if (self.root.winfo_width() >= int(screen_width * 0.6)
                    and self.root.winfo_height() >= int(screen_height * 0.6)):
                return
        except tk.TclError:
            pass

        try:
            self.root.attributes('-zoomed', True)
            self.root.update_idletasks()
            if (self.root.winfo_width() >= int(screen_width * 0.6)
                    and self.root.winfo_height() >= int(screen_height * 0.6)):
                return
        except tk.TclError:
            pass

        self.root.geometry(f'{screen_width}x{screen_height}+0+0')

    def get_effective_screen_size(self):
        """Return a usable screen size, with a sensible fallback when Tk reports 0x0."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        if screen_width <= 1 or screen_height <= 1:
            return 1440, 900
        return screen_width, screen_height

    def ensure_window_visible(self):
        """Ensure the window is visible on-screen and has a sane minimum size."""
        self.root.update_idletasks()

        screen_width, screen_height = self.get_effective_screen_size()
        width = max(1, self.root.winfo_width())
        height = max(1, self.root.winfo_height())
        x = self.root.winfo_x()
        y = self.root.winfo_y()

        too_small = width < 900 or height < 600
        offscreen = (
            x <= -(width // 2)
            or y <= -(height // 2)
            or x >= screen_width - 80
            or y >= screen_height - 80
        )

        if not too_small and not offscreen:
            return

        target_width = min(screen_width, max(1100, int(screen_width * 0.9)))
        target_height = min(screen_height, max(720, int(screen_height * 0.85)))
        target_x = max(0, (screen_width - target_width) // 2)
        target_y = max(0, (screen_height - target_height) // 3)

        with contextlib.suppress(tk.TclError):
            self.root.state('normal')

        self.root.geometry(f'{target_width}x{target_height}+{target_x}+{target_y}')
        self.root.deiconify()
        self.root.lift()

    def bring_to_front(self):
        """Request focus and foreground status, especially on macOS."""
        self.root.update_idletasks()
        self.root.deiconify()
        self.root.lift()

        with contextlib.suppress(tk.TclError):
            self.root.focus_force()

        try:
            self.root.attributes('-topmost', True)
            self.root.after(300, lambda: self.root.attributes('-topmost', False))
        except tk.TclError:
            pass

        if sys.platform == 'darwin':
            try:
                script = (
                    'tell application "System Events"\n'
                    f'    set frontmost of the first process whose unix id is {os.getpid()} to true\n'
                    'end tell'
                )
                subprocess.run(
                    ['osascript', '-e', script],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL)
            except Exception:
                pass

    def present_window(self):
        """Maximize and foreground the window on launch."""
        self.maximize_window()
        self.bring_to_front()
        self.root.after(200, self.ensure_window_visible)
        self.root.after(800, self.ensure_window_visible)

    def add_lazy_tab(self, key, title, builder):
        """Register a notebook tab whose contents are built on first access."""
        frame = ttk.Frame(self.notebook, padding='10')
        self.notebook.add(frame, text=title)
        self._tab_builders[key] = (frame, builder, title)
        self._notebook_tab_texts[frame] = title
        return frame

    def ensure_tab_built(self, frame):
        """Build a tab's contents only once."""
        if frame in self._built_tabs:
            return
        for _key, (tab_frame, builder, _title) in self._tab_builders.items():
            if tab_frame == frame:
                before_names = set(self.__dict__)
                builder(frame)
                new_names = self._tab_controls.get(frame) or (set(self.__dict__) - before_names)
                self.register_stateful_controls(new_names)
                self._tab_controls[frame] = new_names
                self._built_tabs.add(frame)
                self.localize_widget_tree(frame)
                self.apply_pending_gui_state()
                return

    def snapshot_control_value(self, widget):
        if isinstance(widget, tk.BooleanVar):
            return bool(widget.get())
        if isinstance(widget, (ttk.Entry, ttk.Combobox)):
            return widget.get()
        if isinstance(widget, scrolledtext.ScrolledText):
            return widget.get('1.0', tk.END).rstrip('\n')
        return None

    def unload_tab(self, frame):
        """Destroy inactive tab contents while preserving their GUI state."""
        # EXEMPTION: Never unload the Playlist tab because it contains dynamic list data
        if frame not in self._built_tabs or (hasattr(self, 'playlist_tab_frame') and frame == self.playlist_tab_frame):
            return

        for name in self._tab_controls.get(frame, set()):
            widget = self._stateful_controls.pop(name, None)
            if widget is None:
                continue
            value = self.snapshot_control_value(widget)
            if value is not None:
                self._pending_gui_state[name] = value

        for child in frame.winfo_children():
            child.destroy()

        self._built_tabs.discard(frame)

    def on_tab_changed(self, _event=None):
        if not hasattr(self, 'notebook'):
            return
        selected = self.notebook.select()
        if not selected:
            return
        frame = self.root.nametowidget(selected)
        previous_frame = self._active_tab_frame

        if previous_frame is not None and previous_frame != frame:
            # EXEMPTION: Never unload the Playlist tab
            is_playlist = (hasattr(self, 'playlist_tab_frame') and previous_frame == self.playlist_tab_frame)
            if not is_playlist:
                self.unload_tab(previous_frame)

        self.ensure_tab_built(frame)
        self._active_tab_frame = frame

        # Update scrollregion once after a slight delay if switching into it,
        # but avoid heavy update_idletasks on every switch.
        if hasattr(self, 'playlist_tab_frame') and frame == self.playlist_tab_frame:
            pass  # Treeview handles sizing automatically

    def trigger_autosave(self, *args):
        """Request an autosave with a short debouncing delay."""
        if hasattr(self, '_autosave_timer') and self._autosave_timer:
            self.root.after_cancel(self._autosave_timer)
        self._autosave_timer = self.root.after(500, lambda: self.save_config(silent=True))

    def ensure_all_tabs_built(self):
        """Build all tabs before full-state serialization."""
        if not hasattr(self, 'notebook'):
            return
        for tab_id in self.notebook.tabs():
            frame = self.root.nametowidget(tab_id)
            self.ensure_tab_built(frame)

    def register_stateful_controls(self, attribute_names):
        """Track GUI-only controls so they can be serialized independently and trigger autosave."""
        for name in attribute_names:
            value = getattr(self, name, None)
            if isinstance(value, (tk.BooleanVar, ttk.Entry, ttk.Combobox, scrolledtext.ScrolledText)):
                self._stateful_controls[name] = value

                # Setup autosave triggers
                if isinstance(value, tk.Variable):
                    value.trace_add('write', self.trigger_autosave)
                elif isinstance(value, (ttk.Entry, ttk.Combobox)):
                    value.bind('<KeyRelease>', self.trigger_autosave)
                    if isinstance(value, ttk.Combobox):
                        value.bind('<<ComboboxSelected>>', self.trigger_autosave)
                elif isinstance(value, scrolledtext.ScrolledText):
                    value.bind('<KeyRelease>', self.trigger_autosave)

    def _set_entry_value(self, widget, value):
        if isinstance(widget, ttk.Combobox):
            widget.set(value)
            return
        widget.delete(0, tk.END)
        if value:
            widget.insert(0, value)

    def _set_text_value(self, widget, value):
        prior_state = str(widget.cget('state'))
        if prior_state == tk.DISABLED:
            widget.config(state=tk.NORMAL)
        widget.delete('1.0', tk.END)
        if value:
            widget.insert('1.0', value)
        if prior_state == tk.DISABLED:
            widget.config(state=tk.DISABLED)

    def apply_pending_gui_state(self):
        """Apply saved GUI-only state to controls that already exist."""
        if not self._pending_gui_state:
            return
        for name, value in list(self._pending_gui_state.items()):
            widget = self._stateful_controls.get(name)
            if widget is None:
                continue
            if isinstance(widget, tk.BooleanVar):
                widget.set(bool(value))
            elif isinstance(widget, (ttk.Entry, ttk.Combobox)):
                self._set_entry_value(widget, value or '')
            elif isinstance(widget, scrolledtext.ScrolledText):
                self._set_text_value(widget, value or '')
            del self._pending_gui_state[name]

    def on_window_close(self):
        """Persist GUI-only state on close and then exit."""
        self.save_config(silent=True)
        self.root.destroy()

    def on_url_changed(self, *args):
        """Reset playlist status when URL is manually changed by user."""
        current_url = self.url_var.get().strip()
        if getattr(self, 'playlist_parsed_url', None) and current_url != self.playlist_parsed_url:
            self.playlist_parsed_url = None
            if hasattr(self, 'playlist_tree'):
                self.playlist_tree.delete(*self.playlist_tree.get_children())
            self.status_var.set(self.tr('Ready'))

    def create_widgets(self):
        """Create all GUI widgets"""
        before_names = set(self.__dict__)
        # Top frame for URL input and quick actions
        top_frame = ttk.Frame(self.root, padding='10')
        top_frame.pack(fill=tk.X, side=tk.TOP)

        self.language_label = ttk.Label(top_frame, text='Language:')
        self.language_label.grid(row=0, column=2, sticky=tk.E, pady=5, padx=(20, 5))
        self.language_selector = ttk.Combobox(
            top_frame,
            width=16,
            textvariable=self.language_var,
            values=list(LANGUAGE_OPTIONS.values()),
            state='readonly')
        self.language_selector.grid(row=0, column=3, sticky=tk.W, pady=5)
        # The trace handles the change, but keeping bind for compatibility
        self.language_selector.bind('<<ComboboxSelected>>', self.on_language_changed)

        # URL input
        url_btn_frame = ttk.Frame(top_frame)
        url_btn_frame.grid(row=0, column=0, sticky=tk.W, pady=5)

        self.paste_url_btn = ttk.Button(url_btn_frame, text='Paste Link:', command=self.paste_url_from_clipboard)
        self.paste_url_btn.pack(side=tk.LEFT)
        self.register_translatable_widget(self.paste_url_btn, 'Paste Link:')

        self.playlist_btn = ttk.Button(url_btn_frame, text='Parse Playlist', command=self.parse_playlist, width=15)
        self.playlist_btn.pack(side=tk.LEFT, padx=(5, 0))
        self.register_translatable_widget(self.playlist_btn, 'Parse Playlist')

        self.url_var = tk.StringVar()
        self.url_var.trace_add('write', self.on_url_changed)
        self.url_entry = ttk.Entry(top_frame, width=80, textvariable=self.url_var)
        self.url_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        top_frame.columnconfigure(1, weight=1)

        # Batch file option (removed UI entry as requested). Provide a minimal
        # dummy entry object so existing code calling .get/.delete/.insert won't crash.
        class _NullEntry:
            def delete(self, *a, **k):
                return None

            def insert(self, *a, **k):
                return None

            def get(self):
                return ''

            def focus_set(self):
                return None

        self.batch_file_entry = _NullEntry()

        # Quick action buttons
        button_frame = ttk.Frame(top_frame)
        # Move up since the intermediate batch row was removed
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        self.download_btn = ttk.Button(button_frame, text='Download', command=self.on_download_btn_click, width=15)
        self.download_btn.pack(side=tk.LEFT, padx=5)
        self.register_translatable_widget(self.download_btn, 'Download')

        btn_open_folder = ttk.Button(button_frame, text='Open Output Folder', command=self.open_output_folder, width=15)
        btn_open_folder.pack(side=tk.LEFT, padx=5)
        self.register_translatable_widget(btn_open_folder, 'Open Output Folder')

        btn_list = ttk.Button(button_frame, text='List Formats', command=self.list_formats, width=15)
        btn_list.pack(side=tk.LEFT, padx=5)
        self.register_translatable_widget(btn_list, 'List Formats')

        btn_ext = ttk.Button(button_frame, text='Extract Info', command=self.extract_info, width=15)
        btn_ext.pack(side=tk.LEFT, padx=5)
        self.register_translatable_widget(btn_ext, 'Extract Info')

        btn_load = ttk.Button(button_frame, text='Load Config', command=self.load_config_dialog, width=15)
        btn_load.pack(side=tk.LEFT, padx=5)
        self.register_translatable_widget(btn_load, 'Load Config')

        btn_save = ttk.Button(button_frame, text='Save Config', command=self.save_config_dialog, width=15)
        btn_save.pack(side=tk.LEFT, padx=5)
        self.register_translatable_widget(btn_save, 'Save Config')

        # Separator
        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=5)

        # Notebook for tabbed options
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)

        # Register tabs for lazy creation
        batch_frame = self.add_lazy_tab('batch', 'Batch Download', self.create_batch_download_tab)

        # Insert Playlist tab so it appears before the General tab
        self.playlist_tab_frame = self.create_playlist_tab()
        if self.playlist_tab_frame is None:
            self.playlist_tab_frame = ttk.Frame(self.notebook, padding='10')
            self.create_playlist_tab(self.playlist_tab_frame)
        self.notebook.add(self.playlist_tab_frame, text='Playlist')
        self._built_tabs.add(self.playlist_tab_frame)
        self._notebook_tab_texts[self.playlist_tab_frame] = 'Playlist'

        # General tab comes after Playlist now
        self.add_lazy_tab('general', 'General', self.create_general_tab)
        self.add_lazy_tab('network', 'Network', self.create_network_tab)
        # ... rest of lazy tabs
        self.add_lazy_tab('geo', 'Geo-restriction', self.create_geo_restriction_tab)
        self.add_lazy_tab('video_selection', 'Video Selection', self.create_video_selection_tab)
        self.add_lazy_tab('download', 'Download', self.create_download_tab)
        self.add_lazy_tab('filesystem', 'Filesystem', self.create_filesystem_tab)
        self.add_lazy_tab('video_format', 'Video Format', self.create_video_format_tab)
        self.add_lazy_tab('subtitles', 'Subtitles', self.create_subtitle_tab)
        self.add_lazy_tab('authentication', 'Authentication', self.create_authentication_tab)
        self.add_lazy_tab('postprocessing', 'Post-processing', self.create_postprocessing_tab)
        self.add_lazy_tab('thumbnail', 'Thumbnail', self.create_thumbnail_tab)
        self.add_lazy_tab('verbosity', 'Verbosity/Simulation', self.create_verbosity_tab)
        self.add_lazy_tab('workarounds', 'Workarounds', self.create_workarounds_tab)
        self.add_lazy_tab('sponsorblock', 'SponsorBlock', self.create_sponsorblock_tab)
        self.add_lazy_tab('extractor', 'Extractor', self.create_extractor_tab)
        self.add_lazy_tab('advanced', 'Advanced', self.create_advanced_tab)

        self.ensure_tab_built(batch_frame)
        self._active_tab_frame = batch_frame

        # Output console at bottom
        console_frame = ttk.LabelFrame(self.root, text='Output Console', padding='5')
        console_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=(0, 10), ipady=5)

        self.console = scrolledtext.ScrolledText(console_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.console.pack(fill=tk.BOTH, expand=True)

        # Status bar
        # Status bar with dual panes (Status | Progress)
        status_frame = ttk.Frame(self.root, relief=tk.SUNKEN)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_var = tk.StringVar(value='Ready')
        status_label = ttk.Label(status_frame, textvariable=self.status_var, anchor=tk.W)
        status_label.pack(side=tk.LEFT, padx=5, pady=2)

        self.progress_var = tk.StringVar(value='')
        # Using a distinct color and larger font for progress
        self.progress_label = ttk.Label(status_frame, textvariable=self.progress_var, anchor=tk.E, font=('TkDefaultFont', 11, 'bold'), foreground='#0056b3')
        self.progress_label.pack(side=tk.RIGHT, padx=10, pady=2)

        self.status_var.set(self.tr('Ready'))
        self.register_stateful_controls(set(self.__dict__) - before_names)

        # Apply initial localization based on detected/configured language
        self.apply_localization()

    def create_batch_download_tab(self, frame=None):
        """Create Batch Download tab."""
        frame = frame or ttk.Frame(self.notebook, padding='10')

        file_row = ttk.Frame(frame)
        file_row.pack(fill=tk.X, pady=(0, 8))
        lbl_file = ttk.Label(file_row, text=self.tr('Batch file path:'))
        lbl_file.pack(side=tk.LEFT)
        self.register_translatable_widget(lbl_file, 'Batch file path:')

        self.batch_file_var = tk.StringVar()
        self.batch_file_var.trace_add('write', self.trigger_autosave)
        self.batch_file_input = ttk.Entry(file_row, textvariable=self.batch_file_var)
        self.batch_file_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 5))
        btn_browse = ttk.Button(file_row, text=self.tr('Browse...'), command=self.browse_batch_file)
        btn_browse.pack(side=tk.LEFT)
        self.register_translatable_widget(btn_browse, 'Browse...')

        list_row = ttk.Frame(frame)
        list_row.pack(fill=tk.BOTH, expand=False, pady=(0, 8))

        header_row = ttk.Frame(list_row)
        header_row.pack(fill=tk.X, pady=(0, 5))

        lbl_list = ttk.Label(header_row, text=self.tr('Batch URLs (one per line):'))
        lbl_list.pack(side=tk.LEFT)
        self.register_translatable_widget(lbl_list, 'Batch URLs (one per line):')

        # Control buttons will be placed below the batch URLs text area (added after the text widget)

        # Keep clear pool in header row to the right
        btn_clear = ttk.Button(header_row, text=self.tr('Clear Pool'), command=self.clear_all_bulk_rows)
        btn_clear.pack(side=tk.RIGHT)
        self.register_translatable_widget(btn_clear, 'Clear Pool')

        self.batch_urls_text = scrolledtext.ScrolledText(list_row, height=5, wrap=tk.WORD)
        self.batch_urls_text.pack(fill=tk.X, expand=True)
        self.batch_urls_text.bind('<KeyRelease>', self.trigger_autosave)

        # NOTE: Controls row for paste/parse will be placed after the dynamic rows

        dyn_container = ttk.Frame(frame)
        dyn_container.pack(fill=tk.BOTH, expand=True)
        self.bulk_canvas = tk.Canvas(dyn_container, highlightthickness=0)
        vsb = ttk.Scrollbar(dyn_container, orient='vertical', command=self.bulk_canvas.yview)
        self.bulk_scroll_frame = ttk.Frame(self.bulk_canvas)
        self.bulk_scroll_frame.bind(
            '<Configure>',
            lambda e: self.bulk_canvas.configure(scrollregion=self.bulk_canvas.bbox('all')))
        c_win = self.bulk_canvas.create_window((0, 0), window=self.bulk_scroll_frame, anchor='nw')
        self.bulk_canvas.bind('<Configure>', lambda e: self.bulk_canvas.itemconfig(c_win, width=e.width))
        self.bulk_canvas.configure(yscrollcommand=vsb.set)
        self.bulk_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Controls row removed: Bulk Paste and Parse Batch buttons were intentionally deleted
        # per user request. Keep dynamic rows and clear button intact.
        self.bulk_rows = []
        self.add_bulk_row()

        return frame

    def add_bulk_row(self, initial_text=''):
        row = ttk.Frame(self.bulk_scroll_frame)
        row.pack(fill=tk.X, pady=2)
        var = tk.StringVar(value=initial_text)
        var.trace_add('write', self.trigger_autosave)
        entry = ttk.Entry(row, textvariable=var)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        # USE PLAIN ENGLISH FOR REGISTRATION - TRANSLATION HAPPENS IN apply_localization
        btn_parse = ttk.Button(row, text=self.tr('Parse'), width=8, command=lambda v=var: self._parse_single_row_url(v.get()))
        btn_parse.pack(side=tk.LEFT, padx=2)
        self.register_translatable_widget(btn_parse, 'Parse')

        if len(self.bulk_rows) == 0:
            btn_add = ttk.Button(row, text='+', width=3, command=self.add_bulk_row)
            btn_add.pack(side=tk.LEFT)
        else:
            btn_remove = ttk.Button(row, text='-', width=3, command=lambda r=row: self.remove_bulk_row(r))
            btn_remove.pack(side=tk.LEFT)
        self.bulk_rows.append({'frame': row, 'var': var})

        # Immediate sync for this newly added row
        self.localize_widget_tree(row)

    def remove_bulk_row(self, frame):
        frame.destroy()
        self.bulk_rows = [r for r in self.bulk_rows if r['frame'] != frame]
        if not self.bulk_rows:
            self.add_bulk_row()

    def remove_batch_row(self, frame):
        """Compatibility alias for previous function name."""
        self.remove_bulk_row(frame)

    def paste_bulk_urls_smart(self):
        """Smartly detect and distribute URLs from clipboard."""
        try:
            raw = self.root.clipboard_get()
            lines = [l.strip() for l in raw.splitlines() if l.strip()]
            if not lines:
                return
            if self.bulk_rows and not self.bulk_rows[0]['var'].get().strip():
                self.bulk_rows[0]['var'].set(lines[0])
                lines = lines[1:]
            for line in lines:
                self.add_bulk_row(line)
            self.log_message(self.tr('Imported {} URLs into pool.').replace('{}', str(len(lines) + 1)))
        except Exception as e:
            self.log_message(f'Paste failed: {e}')

    def clear_all_bulk_rows(self):
        for row in self.bulk_rows[1:]:
            row['frame'].destroy()
        if self.bulk_rows:
            self.bulk_rows = self.bulk_rows[:1]
            self.bulk_rows[0]['var'].set('')
        if hasattr(self, 'batch_urls_text') and self.batch_urls_text is not None:
            self.batch_urls_text.delete('1.0', tk.END)

    def _parse_single_row_url(self, url):
        url = (url or '').strip()
        if not url:
            return
        self.url_var.set(url)
        self.parse_playlist()

    def parse_single_url(self, url):
        """Compatibility alias for previous function name."""
        self._parse_single_row_url(url)

    def parse_batch(self):
        """Parse all batch inputs and normalize them into the main batch input box."""
        thread = threading.Thread(target=self._parse_batch_worker, daemon=True)
        thread.start()

    def _parse_batch_worker(self):
        urls = []

        file_path = ''
        if hasattr(self, 'batch_file_var'):
            file_path = self.batch_file_var.get().strip()
        if file_path and os.path.isfile(file_path):
            try:
                with open(file_path, encoding='utf-8') as f:
                    urls.extend([line.strip() for line in f if line.strip() and not line.strip().startswith('#')])
            except Exception as e:
                self.log_message(self.translate_concat('Error reading batch file: ', str(e)))

        if hasattr(self, 'batch_urls_text') and self.batch_urls_text is not None:
            text_urls = [line.strip() for line in self.batch_urls_text.get('1.0', tk.END).splitlines() if line.strip()]
            urls.extend(text_urls)

        for row in getattr(self, 'bulk_rows', []):
            value = row['var'].get().strip()
            if value:
                urls.append(value)

        seen = set()
        normalized = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                normalized.append(url)

        if not normalized:
            self.log_message('No valid batch URLs found.')
            self.root.after(0, lambda: self.status_var.set(self.tr('Ready')))
            return

        content = '\n'.join(normalized)
        self.root.after(0, lambda: self.batch_file_entry.delete(0, tk.END))
        self.root.after(0, lambda: self.batch_file_entry.insert(0, content))
        self.log_message(f'Batch parsed: {len(normalized)} URL(s) ready.')
        self.root.after(0, lambda: self.status_var.set(self.tr('Ready')))

    def create_playlist_tab(self, frame=None):
        """Create Playlist Select tab using efficient Treeview"""
        frame = frame or ttk.Frame(self.notebook, padding='10')

        # Top control frame
        top_ctrl = ttk.Frame(frame)
        top_ctrl.pack(fill=tk.X, pady=(0, 5))

        # Use three buttons for better control
        btn_sel_all = ttk.Button(top_ctrl, text='Select All', command=lambda: self._on_playlist_select_all('all'))
        btn_sel_all.pack(side=tk.LEFT, padx=(0, 2))
        self.register_translatable_widget(btn_sel_all, 'Select All')

        btn_sel_none = ttk.Button(top_ctrl, text='Deselect All', command=lambda: self._on_playlist_select_all('none'))
        btn_sel_none.pack(side=tk.LEFT, padx=2)
        self.register_translatable_widget(btn_sel_none, 'Deselect All')

        btn_sel_inv = ttk.Button(top_ctrl, text='Invert Select', command=lambda: self._on_playlist_select_all('invert'))
        btn_sel_inv.pack(side=tk.LEFT, padx=2)
        self.register_translatable_widget(btn_sel_inv, 'Invert Select')

        # Restore playlist option checkboxes (deduplicated) so they are visible once
        # again in the playlist tab. Keep behavior consistent with internal vars.
        self.playlist_reverse_var = tk.BooleanVar(value=False)
        cb_rev = ttk.Checkbutton(
            top_ctrl,
            text='Reverse order',
            variable=self.playlist_reverse_var,
            command=self._on_playlist_option_changed,
        )
        cb_rev.pack(side=tk.LEFT, padx=(20, 0))
        self.register_translatable_widget(cb_rev, 'Reverse order')

        self.playlist_exclude_private_var = tk.BooleanVar(value=True)
        cb_priv = ttk.Checkbutton(
            top_ctrl,
            text='Exclude private videos',
            variable=self.playlist_exclude_private_var,
            command=self._on_playlist_option_changed,
        )
        cb_priv.pack(side=tk.LEFT, padx=(20, 0))
        self.register_translatable_widget(cb_priv, 'Exclude private videos')

        # TREEVIEW for heavy listing
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ('status', 'index', 'title')
        self.playlist_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', selectmode='extended')

        # Define headings
        self.playlist_tree.heading('status', text=' ', anchor=tk.CENTER)
        self.playlist_tree.heading('index', text='#')
        self.playlist_tree.heading('title', text='Title')

        # Define columns
        self.playlist_tree.column('status', width=40, anchor=tk.CENTER, stretch=False)
        self.playlist_tree.column('index', width=60, anchor=tk.CENTER, stretch=False)
        self.playlist_tree.column('title', width=400, anchor=tk.W)

        # Scrollbar
        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.playlist_tree.yview)
        self.playlist_tree.configure(yscrollcommand=tree_scroll.set)

        self.playlist_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind events for interaction
        self.playlist_tree.bind('<ButtonRelease-1>', self._on_tree_click)
        self.playlist_tree.bind('<space>', self._on_tree_space)

        return frame

    def _on_tree_click(self, event):
        item = self.playlist_tree.identify_row(event.y)
        if item:
            self._toggle_tree_item(item)

    def _on_tree_space(self, event):
        items = self.playlist_tree.selection()
        if items:
            for item in items:
                self._toggle_tree_item(item)

    def _toggle_tree_item(self, item):
        values = list(self.playlist_tree.item(item, 'values'))
        if values:
            values[0] = '☐' if values[0] == '☑' else '☑'
            self.playlist_tree.item(item, values=values)

    def _on_playlist_select_all(self, mode='all'):
        for item in self.playlist_tree.get_children():
            values = list(self.playlist_tree.item(item, 'values'))
            if mode == 'all':
                values[0] = '☑'
            elif mode == 'none':
                values[0] = '☐'
            elif mode == 'invert':
                values[0] = '☐' if values[0] == '☑' else '☑'
            self.playlist_tree.item(item, values=values)

    def _on_playlist_mousewheel(self, event):
        # Only scroll if the playlist tab is active
        if self.notebook.select() == str(self.playlist_tab_frame):
            if event.num == 4:  # Linux scroll up
                self.playlist_tree.yview_scroll(-1, 'units')
            elif event.num == 5:  # Linux scroll down
                self.playlist_tree.yview_scroll(1, 'units')
            else:  # Windows/Mac
                self.playlist_tree.yview_scroll(int(-1 * (event.delta)), 'units')

    def _on_playlist_option_changed(self):
        if hasattr(self, 'playlist_entries_data') and self.playlist_entries_data:
            self.root.after(0, self._show_playlist_tab, 'Playlist')

    def create_general_tab(self, frame=None):
        """Create General Options tab"""
        frame = frame or ttk.Frame(self.notebook, padding='10')

        # Scrollable frame
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all')),
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # General options
        row = 0

        self.ignore_errors = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Ignore errors (--ignore-errors)',
                        variable=self.ignore_errors).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.no_warnings = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Ignore warnings (--no-warnings)',
                        variable=self.no_warnings).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.abort_on_error = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Abort on error (--abort-on-error)',
                        variable=self.abort_on_error).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.no_playlist = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Download only video, not playlist (--no-playlist)',
                        variable=self.no_playlist).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.yes_playlist = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Download playlist (--yes-playlist)',
                        variable=self.yes_playlist).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.include_private_videos = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            scrollable_frame,
            text='Include private/unavailable videos in YouTube playlists',
            variable=self.include_private_videos,
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.mark_watched = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Mark videos as watched (--mark-watched)',
                        variable=self.mark_watched).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.no_mark_watched = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Do not mark videos as watched (--no-mark-watched)',
                        variable=self.no_mark_watched).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Default search prefix:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.default_search = ttk.Entry(scrollable_frame, width=40)
        self.default_search.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(scrollable_frame, text='(e.g., "ytsearch5:")').grid(row=row, column=2, sticky=tk.W, pady=5)
        row += 1

        ttk.Label(scrollable_frame, text='Configuration file:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        config_frame = ttk.Frame(scrollable_frame)
        config_frame.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=5)
        self.config_location = ttk.Entry(config_frame, width=40)
        self.config_location.pack(side=tk.LEFT)
        ttk.Button(config_frame, text='Browse...', command=self.browse_config_file).pack(side=tk.LEFT, padx=(5, 0))
        row += 1

        ttk.Label(scrollable_frame, text='Flat playlist extraction:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.extract_flat = ttk.Combobox(scrollable_frame, width=20,
                                         values=['', 'in_playlist', 'discard_in_playlist'],
                                         state='readonly')
        self.extract_flat.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Age limit (years):').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.age_limit = ttk.Entry(scrollable_frame, width=10)
        self.age_limit.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Download archive file:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        archive_frame = ttk.Frame(scrollable_frame)
        archive_frame.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=5)
        self.download_archive = ttk.Entry(archive_frame, width=40)
        self.download_archive.pack(side=tk.LEFT)
        ttk.Button(archive_frame, text='Browse...', command=self.browse_archive_file).pack(side=tk.LEFT, padx=(5, 0))
        row += 1

        ttk.Label(scrollable_frame, text='Max downloads:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.max_downloads = ttk.Entry(scrollable_frame, width=10)
        self.max_downloads.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

    def create_network_tab(self, frame=None):
        """Create Network Options tab"""
        frame = frame or ttk.Frame(self.notebook, padding='10')

        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        row = 0

        ttk.Label(scrollable_frame, text='Proxy URL:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.proxy = ttk.Entry(scrollable_frame, width=50)
        self.proxy.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Socket timeout (seconds):').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.socket_timeout = ttk.Entry(scrollable_frame, width=10)
        self.socket_timeout.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Source address (bind to):').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.source_address = ttk.Entry(scrollable_frame, width=30)
        self.source_address.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        self.force_ipv4 = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Force IPv4 (--force-ipv4)',
                        variable=self.force_ipv4).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.force_ipv6 = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Force IPv6 (--force-ipv6)',
                        variable=self.force_ipv6).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.enable_file_urls = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Enable file:// URLs (--enable-file-urls)',
                        variable=self.enable_file_urls).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Sleep interval (seconds):').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.sleep_interval = ttk.Entry(scrollable_frame, width=10)
        self.sleep_interval.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Max sleep interval (seconds):').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.max_sleep_interval = ttk.Entry(scrollable_frame, width=10)
        self.max_sleep_interval.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Sleep interval for requests (seconds):').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.sleep_interval_requests = ttk.Entry(scrollable_frame, width=10)
        self.sleep_interval_requests.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Sleep interval for subtitles (seconds):').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.sleep_interval_subtitles = ttk.Entry(scrollable_frame, width=10)
        self.sleep_interval_subtitles.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Rate limit (e.g., "50K" or "4.2M"):').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.rate_limit = ttk.Entry(scrollable_frame, width=15)
        self.rate_limit.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Throttled rate (minimum rate):').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.throttled_rate = ttk.Entry(scrollable_frame, width=15)
        self.throttled_rate.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Retries:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.retries = ttk.Entry(scrollable_frame, width=10)
        self.retries.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Fragment retries:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.fragment_retries = ttk.Entry(scrollable_frame, width=10)
        self.fragment_retries.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

    def create_geo_restriction_tab(self, frame=None):
        """Create Geo-restriction tab"""
        frame = frame or ttk.Frame(self.notebook, padding='10')

        row = 0

        ttk.Label(frame, text='Geo verification proxy:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.geo_verification_proxy = ttk.Entry(frame, width=50)
        self.geo_verification_proxy.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        self.geo_bypass = tk.BooleanVar()
        ttk.Checkbutton(frame, text='Bypass geo restriction (--geo-bypass)',
                        variable=self.geo_bypass).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.no_geo_bypass = tk.BooleanVar()
        ttk.Checkbutton(frame, text='Do not bypass geo restriction (--no-geo-bypass)',
                        variable=self.no_geo_bypass).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Label(frame, text='Geo bypass country:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.geo_bypass_country = ttk.Entry(frame, width=10)
        self.geo_bypass_country.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(frame, text='(ISO 3166-2 code)').grid(row=row, column=2, sticky=tk.W, pady=5)
        row += 1

        ttk.Label(frame, text='Geo bypass IP block:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.geo_bypass_ip_block = ttk.Entry(frame, width=30)
        self.geo_bypass_ip_block.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(frame, text='(CIDR notation)').grid(row=row, column=2, sticky=tk.W, pady=5)
        row += 1

    def create_video_selection_tab(self, frame=None):
        """Create Video Selection tab"""
        frame = frame or ttk.Frame(self.notebook, padding='10')

        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        row = 0

        ttk.Label(scrollable_frame, text='Playlist items:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.playlist_items = ttk.Entry(scrollable_frame, width=30)
        self.playlist_items.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(scrollable_frame, text='(e.g., "1-5,10,15-20")').grid(row=row, column=2, sticky=tk.W, pady=5)
        row += 1

        ttk.Label(scrollable_frame, text='Playlist start:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.playlist_start = ttk.Entry(scrollable_frame, width=10)
        self.playlist_start.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Playlist end:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.playlist_end = ttk.Entry(scrollable_frame, width=10)
        self.playlist_end.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Match title (regex):').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.match_title = ttk.Entry(scrollable_frame, width=40)
        self.match_title.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Reject title (regex):').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.reject_title = ttk.Entry(scrollable_frame, width=40)
        self.reject_title.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Min filesize (e.g., 50k or 1M):').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.min_filesize = ttk.Entry(scrollable_frame, width=15)
        self.min_filesize.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Max filesize (e.g., 50M or 1G):').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.max_filesize = ttk.Entry(scrollable_frame, width=15)
        self.max_filesize.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Date (YYYYMMDD):').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.date = ttk.Entry(scrollable_frame, width=15)
        self.date.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Date before (YYYYMMDD):').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.datebefore = ttk.Entry(scrollable_frame, width=15)
        self.datebefore.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Date after (YYYYMMDD):').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.dateafter = ttk.Entry(scrollable_frame, width=15)
        self.dateafter.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Min views:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.min_views = ttk.Entry(scrollable_frame, width=15)
        self.min_views.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Max views:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.max_views = ttk.Entry(scrollable_frame, width=15)
        self.max_views.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Match filter:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.match_filter = ttk.Entry(scrollable_frame, width=40)
        self.match_filter.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=5)
        row += 1

        self.break_on_existing = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Break on existing (--break-on-existing)',
                        variable=self.break_on_existing).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.break_on_reject = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Break on reject (--break-on-reject)',
                        variable=self.break_on_reject).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.no_break_on_existing = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='No break on existing (--no-break-on-existing)',
                        variable=self.no_break_on_existing).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

    def create_download_tab(self, frame=None):
        """Create Download Options tab"""
        frame = frame or ttk.Frame(self.notebook, padding='10')

        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        row = 0

        ttk.Label(scrollable_frame, text='Concurrent fragments:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.concurrent_fragments = ttk.Entry(scrollable_frame, width=10)
        self.concurrent_fragments.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Limit download rate:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.limit_rate = ttk.Entry(scrollable_frame, width=15)
        self.limit_rate.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(scrollable_frame, text='(e.g., 50K or 4.2M)').grid(row=row, column=2, sticky=tk.W, pady=5)
        row += 1

        ttk.Label(scrollable_frame, text='Buffer size:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.buffer_size = ttk.Entry(scrollable_frame, width=15)
        self.buffer_size.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='HTTP chunk size:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.http_chunk_size = ttk.Entry(scrollable_frame, width=15)
        self.http_chunk_size.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        self.no_resize_buffer = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Do not resize buffer (--no-resize-buffer)',
                        variable=self.no_resize_buffer).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.test = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Test mode - do not download (--test)',
                        variable=self.test).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='External downloader:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.external_downloader = ttk.Combobox(scrollable_frame, width=20,
                                                values=['', 'aria2c', 'avconv', 'axel', 'curl', 'ffmpeg', 'httpie', 'wget'],
                                                state='readonly')
        self.external_downloader.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='External downloader args:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.external_downloader_args = ttk.Entry(scrollable_frame, width=40)
        self.external_downloader_args.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=5)
        row += 1

        self.hls_prefer_native = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Prefer native HLS downloader (--hls-prefer-native)',
                        variable=self.hls_prefer_native).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.hls_prefer_ffmpeg = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Prefer ffmpeg for HLS (--hls-prefer-ffmpeg)',
                        variable=self.hls_prefer_ffmpeg).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.hls_use_mpegts = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Use MPEG-TS container for HLS (--hls-use-mpegts)',
                        variable=self.hls_use_mpegts).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

    def create_filesystem_tab(self, frame=None):
        """Create Filesystem Options tab"""
        frame = frame or ttk.Frame(self.notebook, padding='10')

        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        row = 0

        ttk.Label(scrollable_frame, text='Output template:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.output_template = ttk.Entry(scrollable_frame, width=50)
        self.output_template.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=5)
        ttk.Label(scrollable_frame, text='(e.g., "%(title)s.%(ext)s")').grid(row=row, column=3, sticky=tk.W, pady=5)
        row += 1

        ttk.Label(scrollable_frame, text='Output directory:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        output_frame = ttk.Frame(scrollable_frame)
        output_frame.grid(row=row, column=1, columnspan=3, sticky=tk.W, pady=5, padx=5)
        self.output_dir = ttk.Entry(output_frame, width=50)
        self.output_dir.pack(side=tk.LEFT)
        ttk.Button(output_frame, text='Browse...', command=self.browse_output_dir).pack(side=tk.LEFT, padx=(5, 0))
        row += 1

        ttk.Label(scrollable_frame, text='Paths configuration:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.paths = ttk.Entry(scrollable_frame, width=50)
        self.paths.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=5)
        row += 1

        self.restrict_filenames = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Restrict filenames to ASCII (--restrict-filenames)',
                        variable=self.restrict_filenames).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.no_restrict_filenames = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Allow Unicode in filenames (--no-restrict-filenames)',
                        variable=self.no_restrict_filenames).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.playlist_subdir = tk.BooleanVar()
        ttk.Checkbutton(
            scrollable_frame,
            text='Create playlist subfolder for playlist downloads',
            variable=self.playlist_subdir,
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.windows_filenames = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Force Windows-compatible filenames (--windows-filenames)',
                        variable=self.windows_filenames).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.no_overwrites = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Do not overwrite files (--no-overwrites)',
                        variable=self.no_overwrites).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.force_overwrites = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Force overwrite files (--force-overwrites)',
                        variable=self.force_overwrites).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.continue_dl = tk.BooleanVar(value=True)
        ttk.Checkbutton(scrollable_frame, text='Continue partially downloaded files (--continue)',
                        variable=self.continue_dl).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.no_continue = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Do not continue downloads (--no-continue)',
                        variable=self.no_continue).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.no_part = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Do not use .part files (--no-part)',
                        variable=self.no_part).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.no_mtime = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Do not use Last-modified header (--no-mtime)',
                        variable=self.no_mtime).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.write_description = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Write description to .description file (--write-description)',
                        variable=self.write_description).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.write_info_json = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Write metadata to .info.json file (--write-info-json)',
                        variable=self.write_info_json).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.write_annotations = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Write annotations to .annotations.xml (--write-annotations)',
                        variable=self.write_annotations).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.write_comments = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Write comments to .comments.json (--write-comments)',
                        variable=self.write_comments).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Load info JSON:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        load_frame = ttk.Frame(scrollable_frame)
        load_frame.grid(row=row, column=1, columnspan=3, sticky=tk.W, pady=5, padx=5)
        self.load_info_json = ttk.Entry(load_frame, width=50)
        self.load_info_json.pack(side=tk.LEFT)
        ttk.Button(load_frame, text='Browse...', command=self.browse_info_json).pack(side=tk.LEFT, padx=(5, 0))
        row += 1

        ttk.Label(scrollable_frame, text='Cache directory:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        cache_frame = ttk.Frame(scrollable_frame)
        cache_frame.grid(row=row, column=1, columnspan=3, sticky=tk.W, pady=5, padx=5)
        self.cache_dir = ttk.Entry(cache_frame, width=50)
        self.cache_dir.pack(side=tk.LEFT)
        ttk.Button(cache_frame, text='Browse...', command=self.browse_cache_dir).pack(side=tk.LEFT, padx=(5, 0))
        row += 1

        self.no_cache_dir = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Disable filesystem caching (--no-cache-dir)',
                        variable=self.no_cache_dir).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.rm_cache_dir = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Delete cache directory contents (--rm-cache-dir)',
                        variable=self.rm_cache_dir).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

    def create_video_format_tab(self, frame=None):
        """Create Video Format Options tab"""
        frame = frame or ttk.Frame(self.notebook, padding='10')

        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        row = 0

        ttk.Label(scrollable_frame, text='Format selection:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.format = ttk.Entry(scrollable_frame, width=50)
        self.format.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=5)
        ttk.Label(scrollable_frame, text='(e.g., "bestvideo+bestaudio")').grid(row=row, column=3, sticky=tk.W, pady=5)
        row += 1

        ttk.Label(scrollable_frame, text='Quick Select Resolution:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.res_var = tk.StringVar()
        res_options = ['Best (Auto)', '4K (2160p)', '2K (1440p)', '1080p 60fps', '1080p', '720p 60fps', '720p', '480p', '360p']
        self.res_selector = ttk.Combobox(scrollable_frame, textvariable=self.res_var, width=30,
                                         values=[self.tr(opt) for opt in res_options], state='readonly')
        self.res_selector.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        self.res_selector.bind('<<ComboboxSelected>>', self._on_res_selected)
        self.register_translatable_widget(self.res_selector, 'Quick Select Resolution Selector')  # Placeholder to trigger refresh
        row += 1

        ttk.Label(scrollable_frame, text='Format sort:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.format_sort = ttk.Entry(scrollable_frame, width=50)
        self.format_sort.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=5)
        row += 1

        self.prefer_free_formats = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Prefer free formats (--prefer-free-formats)',
                        variable=self.prefer_free_formats).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.check_formats = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Check available formats (--check-formats)',
                        variable=self.check_formats).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Merge output format:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.merge_output_format = ttk.Combobox(scrollable_frame, width=15,
                                                values=['', 'mkv', 'mp4', 'ogg', 'webm', 'flv'],
                                                state='readonly')
        self.merge_output_format.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Video multistreams:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.video_multistreams = ttk.Combobox(scrollable_frame, width=15,
                                               values=['', 'yes', 'no'],
                                               state='readonly')
        self.video_multistreams.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Audio multistreams:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.audio_multistreams = ttk.Combobox(scrollable_frame, width=15,
                                               values=['', 'yes', 'no'],
                                               state='readonly')
        self.audio_multistreams.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

    def _on_res_selected(self, event=None):
        val = self.res_var.get()
        # Find original key from translated value
        original_key = None
        res_options = ['Best (Auto)', '4K (2160p)', '2K (1440p)', '1080p 60fps', '1080p', '720p 60fps', '720p', '480p', '360p']
        for opt in res_options:
            if self.tr(opt) == val:
                original_key = opt
                break

        if not original_key:
            return

        mapping = {
            'Best (Auto)': 'bestvideo+bestaudio/best',
            '4K (2160p)': 'bv*[height<=2160]+ba',
            '2K (1440p)': 'bv*[height<=1440]+ba',
            '1080p 60fps': 'bv*[height<=1080][fps<=60]+ba',
            '1080p': 'bv*[height<=1080]+ba',
            '720p 60fps': 'bv*[height<=720][fps<=60]+ba',
            '720p': 'bv*[height<=720]+ba',
            '480p': 'bv*[height<=480]+ba',
            '360p': 'bv*[height<=360]+ba',
        }
        res_code = mapping.get(original_key)
        if res_code:
            self.format.delete(0, tk.END)
            self.format.insert(0, res_code)

    def create_subtitle_tab(self, frame=None):
        """Create Subtitle Options tab"""
        frame = frame or ttk.Frame(self.notebook, padding='10')

        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        row = 0

        self.write_subs = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Write subtitle file (--write-subs)',
                        variable=self.write_subs).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.write_auto_subs = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Write automatic subtitle file (--write-auto-subs)',
                        variable=self.write_auto_subs).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.list_subs = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='List available subtitles (--list-subs)',
                        variable=self.list_subs).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Subtitle format:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.sub_format = ttk.Combobox(scrollable_frame, width=20,
                                       values=['', 'srt', 'vtt', 'ass', 'lrc'],
                                       state='readonly')
        self.sub_format.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Subtitle languages:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.sub_langs = ttk.Entry(scrollable_frame, width=40)
        self.sub_langs.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=5)
        ttk.Label(scrollable_frame, text='(comma-separated, e.g., "en,fr,de")').grid(row=row, column=3, sticky=tk.W, pady=5)
        row += 1

        self.smart_zh_subs = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='智能下载中文字幕（优先手动字幕，否则自动翻译）',
                        variable=self.smart_zh_subs).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.embed_subs = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Embed subtitles (--embed-subs)',
                        variable=self.embed_subs).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.no_embed_subs = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Do not embed subtitles (--no-embed-subs)',
                        variable=self.no_embed_subs).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.embed_thumbnail = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Embed thumbnail (--embed-thumbnail)',
                        variable=self.embed_thumbnail).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.no_embed_thumbnail = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Do not embed thumbnail (--no-embed-thumbnail)',
                        variable=self.no_embed_thumbnail).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

    def create_authentication_tab(self, frame=None):
        """Create Authentication Options tab"""
        frame = frame or ttk.Frame(self.notebook, padding='10')

        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        row = 0

        ttk.Label(scrollable_frame, text='Username:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.username = ttk.Entry(scrollable_frame, width=30)
        self.username.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Password:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.password = ttk.Entry(scrollable_frame, width=30, show='*')
        self.password.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Two-factor code:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.twofactor = ttk.Entry(scrollable_frame, width=20)
        self.twofactor.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        self.netrc = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Use .netrc authentication (--netrc)',
                        variable=self.netrc).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Video password:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.video_password = ttk.Entry(scrollable_frame, width=30, show='*')
        self.video_password.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Adobe Pass MSO:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.ap_mso = ttk.Entry(scrollable_frame, width=30)
        self.ap_mso.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Adobe Pass username:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.ap_username = ttk.Entry(scrollable_frame, width=30)
        self.ap_username.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Adobe Pass password:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.ap_password = ttk.Entry(scrollable_frame, width=30, show='*')
        self.ap_password.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Client certificate:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        cert_frame = ttk.Frame(scrollable_frame)
        cert_frame.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=5)
        self.client_certificate = ttk.Entry(cert_frame, width=40)
        self.client_certificate.pack(side=tk.LEFT)
        ttk.Button(cert_frame, text='Browse...', command=self.browse_client_cert).pack(side=tk.LEFT, padx=(5, 0))
        row += 1

        ttk.Label(scrollable_frame, text='Client certificate key:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        key_frame = ttk.Frame(scrollable_frame)
        key_frame.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=5)
        self.client_certificate_key = ttk.Entry(key_frame, width=40)
        self.client_certificate_key.pack(side=tk.LEFT)
        ttk.Button(key_frame, text='Browse...', command=self.browse_client_key).pack(side=tk.LEFT, padx=(5, 0))
        row += 1

        ttk.Label(scrollable_frame, text='Client certificate password:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.client_certificate_password = ttk.Entry(scrollable_frame, width=30, show='*')
        self.client_certificate_password.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

    def create_postprocessing_tab(self, frame=None):
        """Create Post-processing Options tab"""
        frame = frame or ttk.Frame(self.notebook, padding='10')

        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        row = 0

        self.extract_audio = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Extract audio (-x, --extract-audio)',
                        variable=self.extract_audio).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Audio format:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.audio_format = ttk.Combobox(scrollable_frame, width=15,
                                         values=['', 'best', 'aac', 'm4a', 'mp3', 'opus', 'vorbis', 'wav', 'flac', 'alac'],
                                         state='readonly')
        self.audio_format.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Audio quality:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.audio_quality = ttk.Entry(scrollable_frame, width=10)
        self.audio_quality.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(scrollable_frame, text='(0-10, 0 = best)').grid(row=row, column=2, sticky=tk.W, pady=5)
        row += 1

        ttk.Label(scrollable_frame, text='Recode video format:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.recode_video = ttk.Combobox(scrollable_frame, width=15,
                                         values=['', 'mp4', 'flv', 'ogg', 'webm', 'mkv', 'avi'],
                                         state='readonly')
        self.recode_video.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Remux video format:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.remux_video = ttk.Combobox(scrollable_frame, width=15,
                                        values=['', 'mp4', 'flv', 'ogg', 'webm', 'mkv', 'avi', 'mov'],
                                        state='readonly')
        self.remux_video.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        self.keep_video = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Keep video file after conversion (--keep-video)',
                        variable=self.keep_video).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.no_keep_video = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Do not keep video file (--no-keep-video)',
                        variable=self.no_keep_video).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.embed_metadata = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Embed metadata (--embed-metadata)',
                        variable=self.embed_metadata).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.embed_chapters = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Embed chapter markers (--embed-chapters)',
                        variable=self.embed_chapters).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.embed_info_json = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Embed info.json (--embed-info-json)',
                        variable=self.embed_info_json).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.add_metadata = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Add metadata to file (--add-metadata)',
                        variable=self.add_metadata).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Metadata fields:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.metadata_from_title = ttk.Entry(scrollable_frame, width=40)
        self.metadata_from_title.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Parse metadata:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.parse_metadata = ttk.Entry(scrollable_frame, width=40)
        self.parse_metadata.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='FFmpeg location:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        ffmpeg_frame = ttk.Frame(scrollable_frame)
        ffmpeg_frame.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=5)
        self.ffmpeg_location = ttk.Entry(ffmpeg_frame, width=40)
        self.ffmpeg_location.pack(side=tk.LEFT)
        ttk.Button(ffmpeg_frame, text='Browse...', command=self.browse_ffmpeg).pack(side=tk.LEFT, padx=(5, 0))
        row += 1

        ttk.Label(scrollable_frame, text='Post-processor args:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.postprocessor_args = ttk.Entry(scrollable_frame, width=50)
        self.postprocessor_args.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=5)
        row += 1

    def create_thumbnail_tab(self, frame=None):
        """Create Thumbnail Options tab"""
        frame = frame or ttk.Frame(self.notebook, padding='10')

        row = 0

        self.write_thumbnail = tk.BooleanVar()
        ttk.Checkbutton(frame, text='Write thumbnail image (--write-thumbnail)',
                        variable=self.write_thumbnail).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.write_all_thumbnails = tk.BooleanVar()
        ttk.Checkbutton(frame, text='Write all thumbnail formats (--write-all-thumbnails)',
                        variable=self.write_all_thumbnails).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.list_thumbnails = tk.BooleanVar()
        ttk.Checkbutton(frame, text='List available thumbnails (--list-thumbnails)',
                        variable=self.list_thumbnails).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Label(frame, text='Convert thumbnails format:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.convert_thumbnails = ttk.Combobox(frame, width=15,
                                               values=['', 'jpg', 'png', 'webp'],
                                               state='readonly')
        self.convert_thumbnails.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

    def create_verbosity_tab(self, frame=None):
        """Create Verbosity and Simulation tab"""
        frame = frame or ttk.Frame(self.notebook, padding='10')

        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        row = 0

        self.quiet = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Quiet mode (-q, --quiet)',
                        variable=self.quiet).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.no_warnings = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='No warnings (--no-warnings)',
                        variable=self.no_warnings).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.verbose = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Verbose output (-v, --verbose)',
                        variable=self.verbose).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.simulate = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Simulate, do not download (-s, --simulate)',
                        variable=self.simulate).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.skip_download = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Skip download (--skip-download)',
                        variable=self.skip_download).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.get_title = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Get title (--get-title)',
                        variable=self.get_title).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.get_id = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Get ID (--get-id)',
                        variable=self.get_id).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.get_url = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Get URL (--get-url)',
                        variable=self.get_url).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.get_thumbnail = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Get thumbnail URL (--get-thumbnail)',
                        variable=self.get_thumbnail).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.get_description = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Get description (--get-description)',
                        variable=self.get_description).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.get_duration = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Get duration (--get-duration)',
                        variable=self.get_duration).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.get_filename = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Get filename (--get-filename)',
                        variable=self.get_filename).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.get_format = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Get format (--get-format)',
                        variable=self.get_format).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.dump_json = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Dump JSON info (--dump-json)',
                        variable=self.dump_json).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.dump_single_json = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Dump single JSON (--dump-single-json)',
                        variable=self.dump_single_json).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.print_json = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Print JSON info (--print-json)',
                        variable=self.print_json).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.progress = tk.BooleanVar(value=True)
        ttk.Checkbutton(scrollable_frame, text='Show progress (--progress)',
                        variable=self.progress).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.no_progress = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Hide progress (--no-progress)',
                        variable=self.no_progress).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.console_title = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Display progress in console title (--console-title)',
                        variable=self.console_title).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        row += 1

        before = set(self.__dict__)
        self.progress_template = ttk.Entry(scrollable_frame, width=50)
        ttk.Label(scrollable_frame, text=self.tr('Progress template:')).grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.progress_template.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        self.register_stateful_controls(set(self.__dict__) - before)
        row += 1

        before2 = set(self.__dict__)
        ttk.Label(scrollable_frame, text=self.tr('Metadata language:')).grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.metadata_lang = ttk.Combobox(
            scrollable_frame,
            values=[self.tr('Default (Auto)'), 'zh-CN', 'zh-TW', 'zh-HK', 'en', 'ja', 'ko'],
            state='readonly',
            width=20,
        )
        self.metadata_lang.set('zh-CN')
        self.metadata_lang.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        self.register_stateful_controls(set(self.__dict__) - before2)
        row += 1

    def create_workarounds_tab(self, frame=None):
        """Create Workarounds tab"""
        frame = frame or ttk.Frame(self.notebook, padding='10')

        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        row = 0

        ttk.Label(scrollable_frame, text='Encoding:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.encoding = ttk.Entry(scrollable_frame, width=20)
        self.encoding.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        self.no_check_certificate = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Skip SSL certificate validation (--no-check-certificate)',
                        variable=self.no_check_certificate).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.prefer_insecure = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Prefer insecure connections (--prefer-insecure)',
                        variable=self.prefer_insecure).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='User agent:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.user_agent = ttk.Entry(scrollable_frame, width=50)
        self.user_agent.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Referer:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.referer = ttk.Entry(scrollable_frame, width=50)
        self.referer.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Add header:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.add_header = ttk.Entry(scrollable_frame, width=50)
        self.add_header.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=5)
        row += 1

        self.bidi_workaround = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Bidirectional text workaround (--bidi-workaround)',
                        variable=self.bidi_workaround).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Label(scrollable_frame, text='Sleep before requests:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.sleep_requests = ttk.Entry(scrollable_frame, width=10)
        self.sleep_requests.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        self.legacy_server_connect = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text='Use legacy server connect (--legacy-server-connect)',
                        variable=self.legacy_server_connect).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

    def create_sponsorblock_tab(self, frame=None):
        """Create SponsorBlock Options tab with category checkboxes and selection controls"""
        frame = frame or ttk.Frame(self.notebook, padding='10')

        # Scrollable container for many options
        canvas = tk.Canvas(frame, highlightthickness=0)
        vsb = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        scroll_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        c_win = canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(c_win, width=e.width))
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        row = 0

        # Main switches
        self.sponsorblock_mark = tk.BooleanVar()
        cb_m = ttk.Checkbutton(scroll_frame, text='Mark SponsorBlock chapters (--sponsorblock-mark)', variable=self.sponsorblock_mark)
        cb_m.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        self.register_translatable_widget(cb_m, 'Mark SponsorBlock chapters (--sponsorblock-mark)')
        row += 1

        self.sponsorblock_remove = tk.BooleanVar()
        cb_r = ttk.Checkbutton(scroll_frame, text='Remove SponsorBlock segments (--sponsorblock-remove)', variable=self.sponsorblock_remove)
        cb_r.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        self.register_translatable_widget(cb_r, 'Remove SponsorBlock segments (--sponsorblock-remove)')
        row += 1

        self.no_sponsorblock = tk.BooleanVar()
        cb_nosb = ttk.Checkbutton(scroll_frame, text='Disable SponsorBlock (--no-sponsorblock)', variable=self.no_sponsorblock)
        cb_nosb.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        self.register_translatable_widget(cb_nosb, 'Disable SponsorBlock (--no-sponsorblock)')
        row += 1

        ttk.Separator(scroll_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky='ew', pady=10)
        row += 1

        # Categories to REMOVE
        rem_lf = ttk.LabelFrame(scroll_frame, text='SponsorBlock categories to remove:', padding=10)
        rem_lf.grid(row=row, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        self.register_translatable_widget(rem_lf, 'SponsorBlock categories to remove:')

        # Selection buttons for Remove group
        rem_ctrl = ttk.Frame(rem_lf)
        rem_ctrl.pack(fill=tk.X, pady=(0, 5))

        btn_rm_all = ttk.Button(rem_ctrl, text='Select All', command=lambda: self._set_sb_group('remove', True))
        btn_rm_all.pack(side=tk.LEFT, padx=2)
        self.register_translatable_widget(btn_rm_all, 'Select All')

        btn_rm_none = ttk.Button(rem_ctrl, text='Deselect All', command=lambda: self._set_sb_group('remove', False))
        btn_rm_none.pack(side=tk.LEFT, padx=2)
        self.register_translatable_widget(btn_rm_none, 'Deselect All')

        btn_rm_inv = ttk.Button(rem_ctrl, text='Invert Select', command=lambda: self._set_sb_group('remove', 'invert'))
        btn_rm_inv.pack(side=tk.LEFT, padx=2)
        self.register_translatable_widget(btn_rm_inv, 'Invert Select')

        rem_grid = ttk.Frame(rem_lf)
        rem_grid.pack(fill=tk.X)
        self.sb_remove_vars = {}
        for idx, cat in enumerate(SB_CATEGORIES):
            var = tk.BooleanVar()
            self.sb_remove_vars[cat] = var
            self._stateful_controls[f'sb_remove_{cat}'] = var
            cb = ttk.Checkbutton(rem_grid, text=cat, variable=var)
            cb.grid(row=idx // 2, column=idx % 2, sticky=tk.W, padx=10, pady=2)
            self.register_translatable_widget(cb, cat)
        row += 1

        # Categories to MARK
        mark_lf = ttk.LabelFrame(scroll_frame, text='SponsorBlock categories to mark:', padding=10)
        mark_lf.grid(row=row, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        self.register_translatable_widget(mark_lf, 'SponsorBlock categories to mark:')

        # Selection buttons for Mark group
        mark_ctrl = ttk.Frame(mark_lf)
        mark_ctrl.pack(fill=tk.X, pady=(0, 5))

        btn_mk_all = ttk.Button(mark_ctrl, text='Select All', command=lambda: self._set_sb_group('mark', True))
        btn_mk_all.pack(side=tk.LEFT, padx=2)
        self.register_translatable_widget(btn_mk_all, 'Select All')

        btn_mk_none = ttk.Button(mark_ctrl, text='Deselect All', command=lambda: self._set_sb_group('mark', False))
        btn_mk_none.pack(side=tk.LEFT, padx=2)
        self.register_translatable_widget(btn_mk_none, 'Deselect All')

        btn_mk_inv = ttk.Button(mark_ctrl, text='Invert Select', command=lambda: self._set_sb_group('mark', 'invert'))
        btn_mk_inv.pack(side=tk.LEFT, padx=2)
        self.register_translatable_widget(btn_mk_inv, 'Invert Select')

        mark_grid = ttk.Frame(mark_lf)
        mark_grid.pack(fill=tk.X)
        self.sb_mark_vars = {}
        for idx, cat in enumerate(SB_CATEGORIES):
            var = tk.BooleanVar()
            self.sb_mark_vars[cat] = var
            self._stateful_controls[f'sb_mark_{cat}'] = var
            cb = ttk.Checkbutton(mark_grid, text=cat, variable=var)
            cb.grid(row=idx // 2, column=idx % 2, sticky=tk.W, padx=10, pady=2)
            self.register_translatable_widget(cb, cat)
        row += 1

        # Other SB settings
        ttk.Label(scroll_frame, text='SponsorBlock chapter title:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.sponsorblock_chapter_title = ttk.Entry(scroll_frame, width=40)
        self.sponsorblock_chapter_title.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        self.register_translatable_widget(scroll_frame.grid_slaves(row=row, column=0)[0], 'SponsorBlock chapter title:')
        row += 1

        ttk.Label(scroll_frame, text='SponsorBlock API URL:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.sponsorblock_api = ttk.Entry(scroll_frame, width=50)
        self.sponsorblock_api.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        self.register_translatable_widget(scroll_frame.grid_slaves(row=row, column=0)[0], 'SponsorBlock API URL:')
        row += 1

    def _set_sb_group(self, group, state):
        vars_dict = self.sb_remove_vars if group == 'remove' else self.sb_mark_vars
        for var in vars_dict.values():
            if state == 'invert':
                var.set(not var.get())
            else:
                var.set(state)

    def create_extractor_tab(self, frame=None):
        """Create Extractor Options tab"""
        frame = frame or ttk.Frame(self.notebook, padding='10')

        row = 0

        ttk.Label(frame, text='Extractor arguments:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.extractor_args = ttk.Entry(frame, width=60)
        self.extractor_args.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=5)
        ttk.Label(frame, text='(key:val[,val] format)').grid(row=row, column=3, sticky=tk.W, pady=5)
        row += 1

        ttk.Label(frame, text='Extractor retries:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.extractor_retries = ttk.Entry(frame, width=10)
        self.extractor_retries.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        self.allow_dynamic_mpd = tk.BooleanVar()
        ttk.Checkbutton(frame, text='Allow dynamic MPD manifests (--allow-dynamic-mpd)',
                        variable=self.allow_dynamic_mpd).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.ignore_dynamic_mpd = tk.BooleanVar()
        ttk.Checkbutton(frame, text='Ignore dynamic MPD manifests (--ignore-dynamic-mpd)',
                        variable=self.ignore_dynamic_mpd).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.hls_split_discontinuity = tk.BooleanVar()
        ttk.Checkbutton(frame, text='Split HLS segments on discontinuity (--hls-split-discontinuity)',
                        variable=self.hls_split_discontinuity).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Label(frame, text='Cookies from browser:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.cookies_from_browser = ttk.Combobox(frame, width=20,
                                                 values=['', 'chrome', 'firefox', 'safari', 'edge', 'opera', 'brave', 'chromium', 'vivaldi'],
                                                 state='readonly')
        self.cookies_from_browser.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(frame, text='Cookies file:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        cookies_frame = ttk.Frame(frame)
        cookies_frame.grid(row=row, column=1, columnspan=3, sticky=tk.W, pady=5, padx=5)
        self.cookies = ttk.Entry(cookies_frame, width=50)
        self.cookies.pack(side=tk.LEFT)
        ttk.Button(cookies_frame, text='Browse...', command=self.browse_cookies).pack(side=tk.LEFT, padx=(5, 0))
        row += 1

    def create_advanced_tab(self, frame=None):
        """Create Advanced Options tab"""
        frame = frame or ttk.Frame(self.notebook, padding='10')

        row = 0

        ttk.Label(frame, text='Raw command-line arguments:').grid(row=row, column=0, sticky=tk.NW, pady=5, padx=5)
        self.raw_args = scrolledtext.ScrolledText(frame, width=80, height=10, wrap=tk.WORD)
        self.raw_args.grid(row=row, column=1, sticky=tk.EW, pady=5, padx=5)
        ttk.Label(frame, text='(One argument per line or space-separated)').grid(row=row + 1, column=1, sticky=tk.W, padx=5)
        row += 2

        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=10)
        row += 1

        ttk.Label(frame, text='Generated command:').grid(row=row, column=0, sticky=tk.NW, pady=5, padx=5)
        self.generated_cmd = scrolledtext.ScrolledText(frame, width=80, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.generated_cmd.grid(row=row, column=1, sticky=tk.EW, pady=5, padx=5)
        row += 1

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=row, column=1, pady=10)
        ttk.Button(button_frame, text='Generate Command', command=self.generate_command).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='Copy to Clipboard', command=self.copy_command).pack(side=tk.LEFT, padx=5)
        row += 1

    # File browser methods
    def browse_batch_file(self):
        filename = filedialog.askopenfilename(
            title=self.tr('Select Batch File'),
            filetypes=[(self.tr('Text Files'), '*.txt'), (self.tr('All Files'), '*.*')])
        if filename:
            self.batch_file_entry.delete(0, tk.END)
            self.batch_file_entry.insert(0, filename)
            if hasattr(self, 'batch_file_var'):
                self.batch_file_var.set(filename)

    def paste_url_from_clipboard(self):
        try:
            clipboard_text = self.root.clipboard_get().strip()
        except tk.TclError:
            clipboard_text = ''

        if not clipboard_text:
            self.log_message(self.tr('Clipboard is empty.'))
            return

        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, clipboard_text)
        self.url_entry.focus_set()
        self.log_message(self.tr('Pasted link from clipboard.'))

    def paste_playlist_from_clipboard(self):
        try:
            clipboard_text = self.root.clipboard_get().strip()
        except tk.TclError:
            clipboard_text = ''

        if not clipboard_text:
            self.log_message(self.tr('Clipboard is empty.'))
            return

        self.batch_file_entry.delete(0, tk.END)
        self.batch_file_entry.insert(0, clipboard_text)
        self.batch_file_entry.focus_set()

        # If it's a single URL and the main URL entry is empty, duplicate it there for convenience
        lines = [l.strip() for l in clipboard_text.splitlines() if l.strip()]
        if len(lines) == 1 and lines[0].startswith('http') and not self.url_entry.get().strip():
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, lines[0])

        self.log_message(self.tr('Pasted playlist from clipboard.'))

    def browse_config_file(self):
        filename = filedialog.askopenfilename(
            title=self.tr('Select Config File'),
            filetypes=[(self.tr('Config Files'), '*.conf'), (self.tr('All Files'), '*.*')])
        if filename:
            self.config_location.delete(0, tk.END)
            self.config_location.insert(0, filename)

    def browse_archive_file(self):
        filename = filedialog.asksaveasfilename(
            title=self.tr('Select Archive File'),
            defaultextension='.txt',
            filetypes=[(self.tr('Text Files'), '*.txt'), (self.tr('All Files'), '*.*')])
        if filename:
            self.download_archive.delete(0, tk.END)
            self.download_archive.insert(0, filename)

    def unify_languages(self):
        """Force metadata language choice to match current GUI language."""
        if not hasattr(self, 'current_language') or not hasattr(self, 'metadata_lang'):
            return

        lang_to_tag = {'zh': 'zh-CN', 'en': 'en', 'ja': 'ja', 'ko': 'ko', 'ru': 'ru', 'es': 'es', 'fr': 'fr', 'de': 'de'}
        target_code = lang_to_tag.get(self.current_language, 'zh-CN')
        self.refresh_metadata_lang_values(force_code=target_code)

    def refresh_metadata_lang_values(self, force_code=None):
        """Update metadata_lang combobox values based on current language translation."""
        if not hasattr(self, 'metadata_lang'):
            return

        current_val = self.metadata_lang.get()
        # Logic: If it's the first value (Default), we consider it "Auto"
        is_auto = False
        try:
            if current_val == self.metadata_lang['values'][0]:
                is_auto = True
        except Exception:
            is_auto = True

        # Keep track of which one was selected
        sel_code = force_code
        if not sel_code and not is_auto and '(' in current_val:
            sel_code = current_val.split('(')[-1].split(')')[0]

        new_values = [
            self.tr('Default (Auto)'),
            'Chinese (Simplified) (zh-CN)',
            'Chinese (Traditional) (zh-TW)',
            'English (en)',
            'Japanese (ja)',
            'Korean (ko)',
            'Russian (ru)',
            'Spanish (es)',
            'French (fr)',
            'German (de)',
            'Portuguese (pt)',
            'Turkish (tr)',
            'Italian (it)',
            'Arabic (ar)',
            'Hindi (hi)',
            'Vietnamese (vi)',
            'Thai (th)',
            'Indonesian (id)',
        ]
        self.metadata_lang['values'] = new_values

        if sel_code:
            for val in new_values:
                if f'({sel_code})' in val:
                    self.metadata_lang.set(val)
                    return

        # If auto or nothing matched
        self.metadata_lang.set(new_values[0])

    def browse_output_dir(self):
        dirname = filedialog.askdirectory(title=self.tr('Select Output Directory'))
        if dirname:
            self.output_dir.delete(0, tk.END)
            self.output_dir.insert(0, dirname)

    def open_output_folder(self):
        output_dir = self.output_dir.get().strip()
        if not output_dir:
            messagebox.showwarning(self.tr('Warning'), self.tr('Please set an output directory first'))
            return
        if not os.path.exists(output_dir):
            messagebox.showwarning(self.tr('Warning'), self.tr('Output directory does not exist'))
            return
        # Open folder using platform-specific command
        import platform
        system = platform.system()
        try:
            if system == 'Darwin':  # macOS
                subprocess.run(['open', output_dir])
            elif system == 'Windows':
                subprocess.run(['explorer', output_dir])
            else:  # Linux
                subprocess.run(['xdg-open', output_dir])
        except Exception as e:
            messagebox.showerror(self.tr('Error'), f"{self.tr('Failed to open folder')}:\n{e}")

    def browse_info_json(self):
        filename = filedialog.askopenfilename(
            title=self.tr('Select Info JSON'),
            filetypes=[(self.tr('JSON Files'), '*.json'), (self.tr('All Files'), '*.*')])
        if filename:
            self.load_info_json.delete(0, tk.END)
            self.load_info_json.insert(0, filename)

    def browse_cache_dir(self):
        dirname = filedialog.askdirectory(title=self.tr('Select Cache Directory'))
        if dirname:
            self.cache_dir.delete(0, tk.END)
            self.cache_dir.insert(0, dirname)

    def browse_client_cert(self):
        filename = filedialog.askopenfilename(
            title=self.tr('Select Client Certificate'),
            filetypes=[(self.tr('PEM Files'), '*.pem'), (self.tr('All Files'), '*.*')])
        if filename:
            self.client_certificate.delete(0, tk.END)
            self.client_certificate.insert(0, filename)

    def browse_client_key(self):
        filename = filedialog.askopenfilename(
            title=self.tr('Select Client Certificate Key'),
            filetypes=[
                (self.tr('PEM Files'), '*.pem'),
                (self.tr('Key Files'), '*.key'),
                (self.tr('All Files'), '*.*')])
        if filename:
            self.client_certificate_key.delete(0, tk.END)
            self.client_certificate_key.insert(0, filename)

    def browse_ffmpeg(self):
        filename = filedialog.askopenfilename(
            title=self.tr('Select FFmpeg Binary'),
            filetypes=[(self.tr('Executable Files'), '*.exe'), (self.tr('All Files'), '*.*')])
        if filename:
            self.ffmpeg_location.delete(0, tk.END)
            self.ffmpeg_location.insert(0, filename)

    def browse_cookies(self):
        filename = filedialog.askopenfilename(
            title=self.tr('Select Cookies File'),
            filetypes=[(self.tr('Text Files'), '*.txt'), (self.tr('All Files'), '*.*')])
        if filename:
            self.cookies.delete(0, tk.END)
            self.cookies.insert(0, filename)

    def build_command_args(self):
        """Build yt-dlp command arguments from GUI settings"""
        self.ensure_all_tabs_built()
        args = []

        # Map GUI internal language codes to metadata language codes
        lang_map = {
            'zh': 'zh-CN',
            'en': 'en',
            'ru': 'ru',
            'ja': 'ja',
            'ko': 'ko',
            'es': 'es',
            'fr': 'fr',
            'de': 'de',
        }
        gui_lang_code = getattr(self, 'current_language', 'zh')
        lang_to_use = lang_map.get(gui_lang_code, 'zh-CN')

        if hasattr(self, 'metadata_lang') and self.metadata_lang.get() and self.metadata_lang.get() != self.tr('Default (Auto)'):
            lang_to_use = self.metadata_lang.get().split('(')[-1].split(')')[0]
            args.extend(['--extractor-args', f'youtube:lang={lang_to_use}'])

        args.extend(['--add-header', f'Accept-Language:{lang_to_use},zh;q=0.9,en-US;q=0.8,en;q=0.7'])

        # URL or batch file
        url = self.url_entry.get().strip()
        batch_file = self.batch_file_entry.get().strip()

        # General options
        if self.ignore_errors.get():
            args.append('--ignore-errors')
        if self.no_warnings.get():
            args.append('--no-warnings')
        if self.abort_on_error.get():
            args.append('--abort-on-error')
        if self.no_playlist.get():
            args.append('--no-playlist')
        if self.yes_playlist.get():
            args.append('--yes-playlist')
        if not self.include_private_videos.get():
            args.extend(['--compat-options', 'no-youtube-unavailable-videos'])
        if self.mark_watched.get():
            args.append('--mark-watched')
        if self.no_mark_watched.get():
            args.append('--no-mark-watched')

        if self.default_search.get():
            args.extend(['--default-search', self.default_search.get()])
        if self.config_location.get():
            args.extend(['--config-location', self.config_location.get()])
        if self.extract_flat.get():
            args.extend(['--flat-playlist', self.extract_flat.get()])
        if self.age_limit.get():
            args.extend(['--age-limit', self.age_limit.get()])
        if self.download_archive.get():
            args.extend(['--download-archive', self.download_archive.get()])
        if self.max_downloads.get():
            args.extend(['--max-downloads', self.max_downloads.get()])

        # Network options
        if self.proxy.get():
            args.extend(['--proxy', self.proxy.get()])
        if self.socket_timeout.get():
            args.extend(['--socket-timeout', self.socket_timeout.get()])
        if self.source_address.get():
            args.extend(['--source-address', self.source_address.get()])
        if self.force_ipv4.get():
            args.append('--force-ipv4')
        if self.force_ipv6.get():
            args.append('--force-ipv6')
        if self.enable_file_urls.get():
            args.append('--enable-file-urls')
        if self.sleep_interval.get():
            args.extend(['--sleep-interval', self.sleep_interval.get()])
        if self.max_sleep_interval.get():
            args.extend(['--max-sleep-interval', self.max_sleep_interval.get()])
        if self.sleep_interval_requests.get():
            args.extend(['--sleep-requests', self.sleep_interval_requests.get()])
        if self.sleep_interval_subtitles.get():
            args.extend(['--sleep-subtitles', self.sleep_interval_subtitles.get()])
        if self.rate_limit.get():
            args.extend(['--limit-rate', self.rate_limit.get()])
        if self.throttled_rate.get():
            args.extend(['--throttled-rate', self.throttled_rate.get()])
        if self.retries.get():
            args.extend(['--retries', self.retries.get()])
        if self.fragment_retries.get():
            args.extend(['--fragment-retries', self.fragment_retries.get()])

        # Geo-restriction
        if self.geo_verification_proxy.get():
            args.extend(['--geo-verification-proxy', self.geo_verification_proxy.get()])
        if self.geo_bypass.get():
            args.append('--geo-bypass')
        if self.no_geo_bypass.get():
            args.append('--no-geo-bypass')
        if self.geo_bypass_country.get():
            args.extend(['--geo-bypass-country', self.geo_bypass_country.get()])
        if self.geo_bypass_ip_block.get():
            args.extend(['--geo-bypass-ip-block', self.geo_bypass_ip_block.get()])

        # Video selection
        if self.playlist_items.get():
            args.extend(['--playlist-items', self.playlist_items.get()])
        if self.playlist_start.get():
            args.extend(['--playlist-start', self.playlist_start.get()])
        if self.playlist_end.get():
            args.extend(['--playlist-end', self.playlist_end.get()])
        if self.match_title.get():
            args.extend(['--match-title', self.match_title.get()])
        if self.reject_title.get():
            args.extend(['--reject-title', self.reject_title.get()])
        if self.min_filesize.get():
            args.extend(['--min-filesize', self.min_filesize.get()])
        if self.max_filesize.get():
            args.extend(['--max-filesize', self.max_filesize.get()])
        if self.date.get():
            args.extend(['--date', self.date.get()])
        if self.datebefore.get():
            args.extend(['--datebefore', self.datebefore.get()])
        if self.dateafter.get():
            args.extend(['--dateafter', self.dateafter.get()])
        if self.min_views.get():
            args.extend(['--min-views', self.min_views.get()])
        if self.max_views.get():
            args.extend(['--max-views', self.max_views.get()])
        if self.match_filter.get():
            args.extend(['--match-filter', self.match_filter.get()])
        if self.break_on_existing.get():
            args.append('--break-on-existing')
        if self.break_on_reject.get():
            args.append('--break-on-reject')
        if self.no_break_on_existing.get():
            args.append('--no-break-on-existing')

        # Download options
        if self.concurrent_fragments.get():
            args.extend(['--concurrent-fragments', self.concurrent_fragments.get()])
        if self.limit_rate.get():
            args.extend(['--limit-rate', self.limit_rate.get()])
        if self.buffer_size.get():
            args.extend(['--buffer-size', self.buffer_size.get()])
        if self.http_chunk_size.get():
            args.extend(['--http-chunk-size', self.http_chunk_size.get()])
        if self.no_resize_buffer.get():
            args.append('--no-resize-buffer')
        if self.test.get():
            args.append('--test')
        if self.external_downloader.get():
            args.extend(['--external-downloader', self.external_downloader.get()])
        if self.external_downloader_args.get():
            args.extend(['--external-downloader-args', self.external_downloader_args.get()])
        if self.hls_prefer_native.get():
            args.append('--hls-prefer-native')
        if self.hls_prefer_ffmpeg.get():
            args.append('--hls-prefer-ffmpeg')
        if self.hls_use_mpegts.get():
            args.append('--hls-use-mpegts')

        # Filesystem options
        output_template = self.output_template.get()
        output_dir = self.output_dir.get()
        if output_template and self.playlist_subdir.get() and '%(playlist)s/' not in output_template and '%(playlist)s\\' not in output_template:
            # Avoid duplicating the playlist folder if the user already encoded it in the template path.
            output_template = os.path.join('%(playlist)s', output_template)
        if output_dir and output_template:
            args.extend(['-o', os.path.join(output_dir, output_template)])
        elif output_template:
            args.extend(['-o', output_template])
        elif output_dir:
            args.extend(['-P', output_dir])

        if self.paths.get():
            args.extend(['--paths', self.paths.get()])
        if self.restrict_filenames.get():
            args.append('--restrict-filenames')
        if self.no_restrict_filenames.get():
            args.append('--no-restrict-filenames')
        if self.windows_filenames.get():
            args.append('--windows-filenames')
        if self.no_overwrites.get():
            args.append('--no-overwrites')
        if self.force_overwrites.get():
            args.append('--force-overwrites')
        if self.continue_dl.get():
            args.append('--continue')
        if self.no_continue.get():
            args.append('--no-continue')
        if self.no_part.get():
            args.append('--no-part')
        if self.no_mtime.get():
            args.append('--no-mtime')
        if self.write_description.get():
            args.append('--write-description')
        if self.write_info_json.get():
            args.append('--write-info-json')
        if self.write_annotations.get():
            args.append('--write-annotations')
        if self.write_comments.get():
            args.append('--write-comments')
        if self.load_info_json.get():
            args.extend(['--load-info-json', self.load_info_json.get()])
        if self.cache_dir.get():
            args.extend(['--cache-dir', self.cache_dir.get()])
        if self.no_cache_dir.get():
            args.append('--no-cache-dir')
        if self.rm_cache_dir.get():
            args.append('--rm-cache-dir')

        # Video format options
        if self.format.get():
            args.extend(['-f', self.format.get()])
        if self.format_sort.get():
            args.extend(['--format-sort', self.format_sort.get()])
        if self.prefer_free_formats.get():
            args.append('--prefer-free-formats')
        if self.check_formats.get():
            args.append('--check-formats')
        if self.merge_output_format.get():
            args.extend(['--merge-output-format', self.merge_output_format.get()])
        if self.video_multistreams.get():
            args.extend(['--video-multistreams', self.video_multistreams.get()])
        if self.audio_multistreams.get():
            args.extend(['--audio-multistreams', self.audio_multistreams.get()])

        # Subtitle options
        if self.write_subs.get():
            args.append('--write-subs')
        if self.write_auto_subs.get():
            args.append('--write-auto-subs')
        if self.list_subs.get():
            args.append('--list-subs')
        if self.sub_format.get():
            args.extend(['--sub-format', self.sub_format.get()])
        if self.smart_zh_subs.get():
            # 智能下载中文字幕：优先手动字幕，然后尝试从各种常见语言自动翻译的中文字幕
            if not self.sub_langs.get():
                args.extend(['--sub-langs', 'zh,zh-CN,zh-TW,zh-Hans,zh-Hant,en-zh,ja-zh,ko-zh,fr-zh,de-zh,es-zh,ru-zh'])
            if not self.write_auto_subs.get():
                args.append('--write-auto-subs')
            if not self.write_subs.get():
                args.append('--write-subs')
        elif self.sub_langs.get():
            args.extend(['--sub-langs', self.sub_langs.get()])
        if self.embed_subs.get():
            args.append('--embed-subs')
        if self.no_embed_subs.get():
            args.append('--no-embed-subs')
        if self.embed_thumbnail.get():
            args.append('--embed-thumbnail')
        if self.no_embed_thumbnail.get():
            args.append('--no-embed-thumbnail')

        # Authentication options
        if self.username.get():
            args.extend(['--username', self.username.get()])
        if self.password.get():
            args.extend(['--password', self.password.get()])
        if self.twofactor.get():
            args.extend(['--twofactor', self.twofactor.get()])
        if self.netrc.get():
            args.append('--netrc')
        if self.video_password.get():
            args.extend(['--video-password', self.video_password.get()])
        if self.ap_mso.get():
            args.extend(['--ap-mso', self.ap_mso.get()])
        if self.ap_username.get():
            args.extend(['--ap-username', self.ap_username.get()])
        if self.ap_password.get():
            args.extend(['--ap-password', self.ap_password.get()])
        if self.client_certificate.get():
            args.extend(['--client-certificate', self.client_certificate.get()])
        if self.client_certificate_key.get():
            args.extend(['--client-certificate-key', self.client_certificate_key.get()])
        if self.client_certificate_password.get():
            args.extend(['--client-certificate-password', self.client_certificate_password.get()])

        # Post-processing options
        if self.extract_audio.get():
            args.append('-x')
        if self.audio_format.get():
            args.extend(['--audio-format', self.audio_format.get()])
        if self.audio_quality.get():
            args.extend(['--audio-quality', self.audio_quality.get()])
        if self.recode_video.get():
            args.extend(['--recode-video', self.recode_video.get()])
        if self.remux_video.get():
            args.extend(['--remux-video', self.remux_video.get()])
        if self.keep_video.get():
            args.append('--keep-video')
        if self.no_keep_video.get():
            args.append('--no-keep-video')
        if self.embed_metadata.get():
            args.append('--embed-metadata')
        if self.embed_chapters.get():
            args.append('--embed-chapters')
        if self.embed_info_json.get():
            args.append('--embed-info-json')
        if self.add_metadata.get():
            args.append('--add-metadata')
        if self.metadata_from_title.get():
            args.extend(['--metadata-from-title', self.metadata_from_title.get()])
        if self.parse_metadata.get():
            args.extend(['--parse-metadata', self.parse_metadata.get()])
        if self.ffmpeg_location.get():
            args.extend(['--ffmpeg-location', self.ffmpeg_location.get()])
        if self.postprocessor_args.get():
            args.extend(['--postprocessor-args', self.postprocessor_args.get()])

        # Thumbnail options
        if self.write_thumbnail.get():
            args.append('--write-thumbnail')
        if self.write_all_thumbnails.get():
            args.append('--write-all-thumbnails')
        if self.list_thumbnails.get():
            args.append('--list-thumbnails')
        if self.convert_thumbnails.get():
            args.extend(['--convert-thumbnails', self.convert_thumbnails.get()])

        # Verbosity options
        if self.quiet.get():
            args.append('--quiet')
        if self.verbose.get():
            args.append('--verbose')
        if self.simulate.get():
            args.append('--simulate')
        if self.skip_download.get():
            args.append('--skip-download')
        if self.get_title.get():
            args.append('--get-title')
        if self.get_id.get():
            args.append('--get-id')
        if self.get_url.get():
            args.append('--get-url')
        if self.get_thumbnail.get():
            args.append('--get-thumbnail')
        if self.get_description.get():
            args.append('--get-description')
        if self.get_duration.get():
            args.append('--get-duration')
        if self.get_filename.get():
            args.append('--get-filename')
        if self.get_format.get():
            args.append('--get-format')
        if self.dump_json.get():
            args.append('--dump-json')
        if self.dump_single_json.get():
            args.append('--dump-single-json')
        if self.print_json.get():
            args.append('--print-json')
        if self.no_progress.get():
            args.append('--no-progress')
        if self.console_title.get():
            args.append('--console-title')
        if self.progress_template.get():
            args.extend(['--progress-template', self.progress_template.get()])

        # Workarounds
        if self.encoding.get():
            args.extend(['--encoding', self.encoding.get()])
        if self.no_check_certificate.get():
            args.append('--no-check-certificate')
        if self.prefer_insecure.get():
            args.append('--prefer-insecure')
        if self.user_agent.get():
            args.extend(['--user-agent', self.user_agent.get()])
        if self.referer.get():
            args.extend(['--referer', self.referer.get()])
        if self.add_header.get():
            args.extend(['--add-header', self.add_header.get()])
        if self.bidi_workaround.get():
            args.append('--bidi-workaround')
        if self.sleep_requests.get():
            args.extend(['--sleep-requests', self.sleep_requests.get()])
        if self.legacy_server_connect.get():
            args.append('--legacy-server-connect')

        # SponsorBlock options
        if self.sponsorblock_mark.get():
            args.append('--sponsorblock-mark')
        if self.sponsorblock_remove.get():
            args.append('--sponsorblock-remove')

        # Collect categories from checkboxes
        selected_remove_cats = [cat for cat, var in self.sb_remove_vars.items() if var.get()]
        if selected_remove_cats:
            args.extend(['--sponsorblock-remove', ','.join(selected_remove_cats)])

        selected_mark_cats = [cat for cat, var in self.sb_mark_vars.items() if var.get()]
        if selected_mark_cats:
            args.extend(['--sponsorblock-mark', ','.join(selected_mark_cats)])

        if self.sponsorblock_chapter_title.get():
            args.extend(['--sponsorblock-chapter-title', self.sponsorblock_chapter_title.get()])
        if self.no_sponsorblock.get():
            args.append('--no-sponsorblock')
        if self.sponsorblock_api.get():
            args.extend(['--sponsorblock-api', self.sponsorblock_api.get()])

        # Extractor options
        extractor_args = []
        if hasattr(self, 'metadata_lang') and self.metadata_lang.get() and self.metadata_lang.get() != self.tr('Default (Auto)'):
            lang_code = self.metadata_lang.get().split('(')[-1].split(')')[0] if '(' in self.metadata_lang.get() else self.metadata_lang.get()
            if not url.startswith('https://www.youtube.com/playlist'):
                extractor_args.append(f'youtube:lang={lang_code}')
        if self.extractor_args.get():
            extractor_args.append(self.extractor_args.get())

        if extractor_args:
            args.extend(['--extractor-args', '; '.join(extractor_args)])

        if self.extractor_retries.get():
            args.extend(['--extractor-retries', self.extractor_retries.get()])
        if self.allow_dynamic_mpd.get():
            args.append('--allow-dynamic-mpd')
        if self.ignore_dynamic_mpd.get():
            args.append('--ignore-dynamic-mpd')
        if self.hls_split_discontinuity.get():
            args.append('--hls-split-discontinuity')
        if self.cookies_from_browser.get():
            args.extend(['--cookies-from-browser', self.cookies_from_browser.get()])
        if self.cookies.get():
            args.extend(['--cookies', self.cookies.get()])

        # Raw arguments
        raw_args_text = self.raw_args.get('1.0', tk.END).strip()
        if raw_args_text:
            import shlex
            try:
                raw_args_list = shlex.split(raw_args_text)
                args.extend(raw_args_list)
            except ValueError:
                # If shlex fails, try splitting by whitespace
                args.extend(raw_args_text.split())

        # Batch file or URL
        if batch_file:
            if batch_file.startswith('http') and '\n' not in batch_file:
                # Single URL in batch field
                args.append(batch_file)
            elif '\n' in batch_file or (not os.path.exists(batch_file) and batch_file.startswith('http')):
                # Multi-line URLs or non-existent path that looks like URL/list
                try:
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tf:
                        tf.write(batch_file)
                        temp_path = tf.name
                    args.extend(['-a', temp_path])
                    # Register for cleanup
                    if not hasattr(self, '_temp_batch_files'):
                        self._temp_batch_files = []
                        atexit.register(self._cleanup_temp_files)
                    self._temp_batch_files.append(temp_path)
                except Exception as e:
                    self.log_message(f'Error creating temporary batch file: {e}')
                    args.extend(['-a', batch_file])  # Fallback
            else:
                args.extend(['-a', batch_file])
        elif url:
            args.append(url)

        return args

    def _cleanup_temp_files(self):
        if hasattr(self, '_temp_batch_files'):
            for f in self._temp_batch_files:
                try:
                    if os.path.exists(f):
                        os.remove(f)
                except Exception:
                    pass
            self._temp_batch_files.clear()

    def generate_command(self):
        """Generate and display the yt-dlp command"""
        args = self.build_command_args()
        cmd = [sys.executable, '-m', 'yt_dlp', *args]
        cmd_str = ' '.join(f'"{arg}"' if ' ' in arg else arg for arg in cmd)

        self.generated_cmd.config(state=tk.NORMAL)
        self.generated_cmd.delete('1.0', tk.END)
        self.generated_cmd.insert('1.0', cmd_str)
        self.generated_cmd.config(state=tk.DISABLED)

    def copy_command(self):
        """Copy generated command to clipboard"""
        self.generate_command()
        cmd_text = self.generated_cmd.get('1.0', tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(cmd_text)
        self.log_message('Command copied to clipboard!')

    def run_ytdlp(self, tasks):
        """Run a list of yt-dlp tasks (args sets) sequentially"""
        try:
            total = len(tasks)
            for i, (idx, args) in enumerate(tasks):
                self.log_message(self.translate_concat(f'[{i + 1}/{total}] Download Task: Index ', idx))
                self.root.after(0, lambda: self.status_var.set(f'{self.tr("Downloading")} {i + 1}/{total}'))

                full_cmd = [sys.executable, '-m', 'yt_dlp', '--remote-components', 'ejs:github', *args]

                # 设置环境变量，确保能找到 deno
                env = os.environ.copy()
                env['PATH'] = '/opt/homebrew/bin:/usr/local/bin:' + env.get('PATH', '')

                popen_kwargs = {
                    'stdout': subprocess.PIPE,
                    'stderr': subprocess.STDOUT,
                    'universal_newlines': True,
                    'bufsize': 1,
                    'env': env,
                }
                if os.name == 'nt':
                    popen_kwargs['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP
                else:
                    popen_kwargs['start_new_session'] = True
                self.current_process = subprocess.Popen(full_cmd, **popen_kwargs)
                process = self.current_process

                if process.stdout:
                    for line in process.stdout:
                        if line:
                            self.log_message(line.rstrip())

                process.wait()

                if process.returncode != 0 and process.returncode not in (15, -15):
                    self.log_message(self.translate_concat('Task failed with code ', process.returncode))
                    if 'n challenge solving failed' in ''.join(self.console.get('1.0', tk.END)):
                        self.log_message('\n[!] 提示：检测到 JavaScript 运行环境缺失。')
                        self.log_message("[!] 请在终端运行 'brew install node' 以修复此下载报错。")
                    # We continue even if one fails

                if not hasattr(self, 'current_process') or self.current_process is None:
                    # User likely clicked Stop
                    break

            self.log_message(self.tr('All tasks processed.'))
            self.root.after(0, lambda: self.status_var.set(self.tr('Ready')))

        except Exception as e:
            self.log_message(self.translate_concat('ERROR in runner: ', str(e)))
            self.root.after(0, lambda: self.status_var.set(self.tr('Error')))
        finally:
            self.current_process = None
            self.root.after(0, self._restore_download_button)

    def _restore_download_button(self):
        if hasattr(self, 'download_btn'):
            self.download_btn.config(text=self.tr('Download'))
            self._translatable_widgets[self.download_btn] = 'Download'

    def on_download_btn_click(self):
        if hasattr(self, 'current_process') and self.current_process:
            self.stop_download()
        else:
            self.start_download()

    def stop_download(self):
        if hasattr(self, 'current_process') and self.current_process:
            p = self.current_process
            self.current_process = None  # Signal to stop loop
            self.log_message(self.tr('Stopping download...'))

            try:
                # Kill the entire process group (including child processes like ffmpeg)
                if os.name != 'nt':
                    with contextlib.suppress(ProcessLookupError, OSError):
                        os.killpg(os.getpgid(p.pid), signal.SIGTERM)
                with contextlib.suppress(ProcessLookupError):
                    p.terminate()
                    p.kill()
            except Exception as e:
                self.log_message(f'[DEBUG] Stop error: {e}')

            # Popup for cleanup
            msg = self.tr('Download stopped. Would you like to delete partially downloaded files?')
            if messagebox.askyesno(self.tr('Stop'), msg):
                self.cleanup_partial_files()
        else:
            self.log_message(self.tr('No download currently running.'))

    def cleanup_partial_files(self):
        """Scan output directory and remove .part, .ytdl and temporary fragment files."""
        output_dir = self.output_dir.get().strip()
        if not output_dir or not os.path.exists(output_dir):
            return

        count = 0
        self.log_message(self.tr('Cleaning up partial files...'))
        try:
            for filename in os.listdir(output_dir):
                # yt-dlp partial files usually end with .part, .ytdl
                # or have fragments like .f137.part
                if filename.endswith(('.part', '.ytdl')) or ('.f' in filename and '.part' in filename):
                    file_path = os.path.join(output_dir, filename)
                    if os.path.isfile(file_path):
                        try:
                            os.remove(file_path)
                            count += 1
                        except Exception as e:
                            self.log_message(f'Failed to remove {filename}: {e}')
            self.log_message(f'Cleanup finished. Removed {count} files.')
        except Exception as e:
            self.log_message(f'Error during cleanup: {e}')

    def start_download(self):
        """Start download in a separate thread"""
        self.log_message('[DEBUG] start_download called')
        url = self.url_entry.get().strip()
        self.log_message(f'[DEBUG] url={url!r}')
        try:
            base_args = self.build_command_args()
            self.log_message(f'[DEBUG] base_args count={len(base_args) if base_args else 0}')
        except Exception as e:
            import traceback
            self.log_message(f'[DEBUG] build_command_args CRASHED: {e}')
            self.log_message(traceback.format_exc())
            self._restore_download_button()
            return

        if not base_args or (not url and not self.batch_file_entry.get().strip()):
            self.log_message('[DEBUG] No URL or args — showing warning')
            messagebox.showwarning(self.tr('No URL'), self.tr('Please enter a URL or batch file to download.'))
            return

        # Change button to Stop
        self.download_btn.config(text=self.tr('Stop'))
        self._translatable_widgets[self.download_btn] = 'Stop'

        output_dir = self.output_dir.get().strip()
        self.log_message(f'[DEBUG] output_dir={output_dir!r}')

        playlist_parsed_url = getattr(self, 'playlist_parsed_url', None)
        self.log_message(f'[DEBUG] URL match check: Input="{url}", Parsed="{playlist_parsed_url}"')

        tasks = []
        # ONLY use playlist tasks if the URL matches what we parsed!
        if hasattr(self, 'playlist_tree') and playlist_parsed_url and url == playlist_parsed_url:
            items = self.playlist_tree.get_children()
            # SIMPLICITY: Just follow the tree from TOP TO BOTTOM as shown in GUI.
            vis_to_orig_map = getattr(self, 'vis_to_orig', {})
            for item in items:
                vals = self.playlist_tree.item(item, 'values')
                checked = vals[0] == '☑'
                visual_idx = int(vals[1])

                if checked:
                    gui_title = str(vals[2])
                    original_idx = vis_to_orig_map.get(visual_idx, visual_idx)
                    task_args = []
                    skip = False
                    for arg in base_args:
                        if skip:
                            skip = False
                            continue
                        # EXCLUDE batch file and redundant playlist items from individual tasks
                        if arg in ('--playlist-items', '--playlist-reverse', '--no-playlist-reverse',
                                   '-o', '-P', '--paths', '-a', '--batch-file'):
                            if arg in ('--playlist-items', '-o', '-P', '--paths', '-a', '--batch-file'):
                                skip = True
                            continue
                        if arg == url:  # Don't add the main URL yet
                            continue
                        task_args.append(arg)

                    # Always use the specific playlist URL for individual tasks
                    task_args.append(url)
                    filename_tpl = f'{visual_idx:03d} - {gui_title}.%(ext)s'
                    # Remove unsafe characters
                    filename_tpl = ''.join([c for c in filename_tpl if c not in '<>:"/\\|?*']).strip()

                    # Handle playlist subfolder
                    final_output_dir = output_dir
                    if self.playlist_subdir.get() and getattr(self, 'current_playlist_metadata_title', None):
                        folder_name = ''.join([c for c in self.current_playlist_metadata_title if c not in '<>:"/\\|?*']).strip()
                        if folder_name:
                            final_output_dir = os.path.join(output_dir, folder_name)
                            if not os.path.exists(final_output_dir):
                                os.makedirs(final_output_dir, exist_ok=True)

                    out_path = os.path.join(final_output_dir, filename_tpl) if final_output_dir else filename_tpl
                    task_args.extend(['--playlist-items', str(original_idx)])
                    task_args.extend(['-o', out_path])
                    tasks.append((visual_idx, task_args))

        # If no playlist tasks were built (not a playlist or nothing checked), treat as single/batch
        if not tasks:
            tasks.append(('Single', base_args))

        self.console.config(state=tk.NORMAL)
        self.console.delete('1.0', tk.END)
        self.console.config(state=tk.DISABLED)

        thread = threading.Thread(target=self.run_ytdlp, args=(tasks,), daemon=True)
        thread.start()

    def parse_playlist(self):
        url = self.url_entry.get().strip()
        batch = self.batch_file_entry.get().strip()

        # If main URL is empty but batch has a URL, use it
        if not url and batch.startswith('http') and '\n' not in batch:
            url = batch
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, url)

        if not url:
            messagebox.showwarning(self.tr('No URL'), self.tr('Please enter a URL.'))
            return

        self.console.config(state=tk.NORMAL)
        self.console.delete('1.0', tk.END)
        self.console.config(state=tk.DISABLED)
        self.status_var.set(self.tr('Checking URL...'))
        thread = threading.Thread(target=self._parse_playlist_only, args=(url,), daemon=True)
        thread.start()

    def _parse_playlist_only(self, url):
        try:
            self.ensure_all_tabs_built()
            self.log_message(self.tr('Checking if URL is a playlist...'))
            # ADDED --no-cache-dir to ensure we get fresh language-specific metadata
            # ADDED --remote-components for JS challenge solving (deno)
            cmd = [sys.executable, '-m', 'yt_dlp', '-J', '--flat-playlist', '--no-cache-dir', '--remote-components', 'ejs:github']

            # MAP GUI Language to Metadata Language
            lang_map = {'zh': 'zh-CN', 'en': 'en', 'ru': 'ru', 'ja': 'ja', 'ko': 'ko', 'es': 'es', 'fr': 'fr', 'de': 'de'}
            gui_lang_code = getattr(self, 'current_language', 'zh')
            lang_to_use = lang_map.get(gui_lang_code, 'zh-CN')

            self.log_message(f'[DEBUG] Parsing playlist metadata using interface-linked language: {lang_to_use}')
            cmd.extend(['--add-header', f'Accept-Language:{lang_to_use},zh-CN;q=0.9,zh;q=0.8'])
            cmd.extend(['--geo-bypass'])

            # Keep playlist parsing aligned with the actual download/auth context.
            # Otherwise YouTube may reject the preflight parse while normal downloads
            # would have succeeded with the user's browser session.
            if self.cookies_from_browser.get():
                cmd.extend(['--cookies-from-browser', self.cookies_from_browser.get()])
            if self.cookies.get():
                cmd.extend(['--cookies', self.cookies.get()])
            if self.user_agent.get():
                cmd.extend(['--user-agent', self.user_agent.get()])
            if self.referer.get():
                cmd.extend(['--referer', self.referer.get()])
            if self.add_header.get():
                cmd.extend(['--add-header', self.add_header.get()])

            cmd.append(url)

            # 设置环境变量，确保能找到 deno
            env = os.environ.copy()
            env['PATH'] = '/opt/homebrew/bin:/usr/local/bin:' + env.get('PATH', '')

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1,
                env=env,
            )
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                info = json.loads(stdout)
                if info.get('_type') in ('playlist', 'multi_video') and 'entries' in info:
                    self.playlist_parsed_url = url
                    self.playlist_entries_data = info['entries']
                    self.current_playlist_metadata_title = info.get('title', 'Playlist')
                    self.root.after(0, self._show_playlist_tab, self.current_playlist_metadata_title)
                    return
                else:
                    self.log_message(self.tr('Not a playlist or no entries found.'))
            else:
                self.log_message(f'[ERROR] Parsing failed: {stderr.strip()}')
                self.log_message(self.tr('Failed to parse playlist.'))
        except Exception as e:
            self.log_message(self.translate_concat('Error checking playlist: ', str(e)))
        self.status_var.set(self.tr('Ready'))

    def _show_playlist_tab(self, temp_title):
        self.log_message(self.tr('Playlist detected. Please select videos to download.'))
        self.status_var.set(self.tr('Playlist detected'))
        if hasattr(self, 'playlist_tree'):
            self.notebook.select(self.playlist_tab_frame)
            self.playlist_tree.delete(*self.playlist_tree.get_children())

            entries = self.playlist_entries_data
            filtered_entries = []
            for i, entry in enumerate(entries):
                title = entry.get('title') or entry.get('id') or f'Video {i + 1}'
                availability = entry.get('availability', '')
                is_private = (
                    title in ('[Private video]', '[私享视频]', '[私有视频]', '[Deleted video]', '[已删除的视频]')
                    or availability == 'private'
                    or entry.get('title') is None
                )
                if is_private and self.playlist_exclude_private_var.get():
                    continue
                filtered_entries.append((i + 1, title))

            if getattr(self, 'playlist_reverse_var', None) and self.playlist_reverse_var.get():
                filtered_entries = list(reversed(filtered_entries))

            total_visible = len(filtered_entries)
            self.vis_to_orig = {}
            for j, (original_idx, title) in enumerate(filtered_entries):
                # FIXED LOGIC: Top row gets the max number, Bottom row gets 1.
                # Top row is ALWAYS downloaded first.
                visual_idx = total_visible - j
                self.vis_to_orig[visual_idx] = original_idx
                self.playlist_tree.insert('', tk.END, values=('☑', visual_idx, title))

            # Reset headers
            self.playlist_tree.heading('status', text=' ')
            self.playlist_tree.heading('index', text='#')
            self.playlist_tree.heading('title', text=self.tr('Title'))

    def list_formats(self):
        """List available formats for the video"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning(self.tr('No URL'), self.tr('Please enter a URL.'))
            return

        self.console.config(state=tk.NORMAL)
        self.console.delete('1.0', tk.END)
        self.console.config(state=tk.DISABLED)

        thread = threading.Thread(target=self.run_ytdlp, args=(['-F', url],), daemon=True)
        thread.start()

    def extract_info(self):
        """Extract video information"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning(self.tr('No URL'), self.tr('Please enter a URL.'))
            return

        self.console.config(state=tk.NORMAL)
        self.console.delete('1.0', tk.END)
        self.console.config(state=tk.DISABLED)

        thread = threading.Thread(target=self.run_ytdlp, args=(['--dump-json', url],), daemon=True)
        thread.start()

    def _start_log_watcher(self):
        """Poll the log queue and update the UI from the main thread"""
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self._log_message_internal(msg)
        except Exception:  # queue.Empty
            pass
        self.root.after(100, self._start_log_watcher)

    def _log_message_internal(self, message):
        """Internal method to update the console text widget and redirect progress to status bar"""
        clean_msg = message.strip()

        # Redirect [download] progress to the status bar instead of the console
        # Typically looks like: [download]  1.2% of 10.00MiB at ...
        if clean_msg.startswith('[download]') and '%' in clean_msg:
            # Strip '[download]' prefix for a cleaner look as requested
            display_msg = clean_msg.replace('[download]', '').strip()
            self.progress_var.set(display_msg)
            # Clear progress bar once finished or moved to next stage
            if '100%' in clean_msg:
                self.root.after(3000, lambda: self.progress_var.set('') if '100%' in self.progress_var.get() else None)
            return

        self.console.config(state=tk.NORMAL)
        # Check if we were already at the bottom before adding content
        at_bottom = self.console.yview()[1] == 1.0
        self.console.insert(tk.END, message + '\n')
        if at_bottom:
            self.console.see(tk.END)
        self.console.config(state=tk.DISABLED)

    def log_message(self, message):
        """Add message to the thread-safe queue and stdout for debugging."""
        msg_str = str(message)
        # Always output to terminal for visibility if GUI logs are failing or slow
        print(msg_str)

        if hasattr(self, 'log_queue'):
            self.log_queue.put(msg_str)

    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f'Error loading config: {e}')

    def save_config(self, silent=False):
        """Save current configuration to file"""
        try:
            self.config = self.get_current_config()
            self.write_config_to_disk(self.config)
        except Exception as e:
            if not silent:
                messagebox.showerror(self.tr('Error'), self.translate_concat('Failed to save configuration: ', e))

    def load_config_dialog(self):
        """Load configuration from a file dialog"""
        filename = filedialog.askopenfilename(
            title=self.tr('Load Configuration'),
            filetypes=[(self.tr('JSON Files'), '*.json'), (self.tr('All Files'), '*.*')])
        if filename:
            try:
                with open(filename, encoding='utf-8') as f:
                    self.config = json.load(f)
                self.apply_config()
                messagebox.showinfo(self.tr('Success'), self.tr('Configuration loaded successfully!'))
            except Exception as e:
                messagebox.showerror(self.tr('Error'), self.translate_concat('Failed to load configuration: ', e))

    def save_config_dialog(self):
        """Save configuration to a file dialog"""
        filename = filedialog.asksaveasfilename(
            title=self.tr('Save Configuration'),
            defaultextension='.json',
            filetypes=[(self.tr('JSON Files'), '*.json'), (self.tr('All Files'), '*.*')])
        if filename:
            try:
                self.config = self.get_current_config()
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=2)
                messagebox.showinfo(self.tr('Success'), self.tr('Configuration saved successfully!'))
            except Exception as e:
                messagebox.showerror(self.tr('Error'), self.translate_concat('Failed to save configuration: ', e))

    def get_current_config(self):
        """Get current configuration from GUI"""
        self.ensure_all_tabs_built()

        gui_state = {}
        for name, widget in self._stateful_controls.items():
            if name in {'language_selector', 'console', 'generated_cmd'}:
                continue
            if isinstance(widget, tk.BooleanVar):
                gui_state[name] = bool(widget.get())
            elif isinstance(widget, (ttk.Entry, ttk.Combobox)):
                gui_state[name] = widget.get()
            elif isinstance(widget, scrolledtext.ScrolledText):
                gui_state[name] = widget.get('1.0', tk.END).rstrip('\n')

        return {
            'config_version': 1,
            'language': self.current_language,
            'language_initialized': True,
            'gui_state': gui_state,
        }

    def apply_config(self):
        """Apply loaded configuration to GUI"""
        language = self.config.get('language', self.current_language)
        if language not in LANGUAGE_OPTIONS:
            language = 'en'
        self.current_language = language
        gui_state = dict(self.config.get('gui_state', {}))
        for key, value in GUI_DEFAULT_STATE.items():
            if not gui_state.get(key):
                gui_state[key] = value
        self._pending_gui_state = gui_state
        if hasattr(self, 'language_var'):
            self.language_var.set(self.get_language_display(language))
        self.apply_localization()
        self.apply_pending_gui_state()
        self.status_var.set(self.tr('Ready'))


def main():
    """Main entry point for the GUI"""
    try:
        root = tk.Tk()
        # Set theme and window style for macOS
        style = ttk.Style(root)
        if sys.platform == 'darwin':
            style.theme_use('aqua')

        _app = YtDlpGUI(root)
        root.mainloop()
    except Exception:
        import traceback
        print(f'FATAL ERROR during GUI startup:\n{traceback.format_exc()}')


if __name__ == '__main__':
    main()
