# yt-dlp GUI - Graphical User Interface

## Overview

This GUI provides a user-friendly graphical interface for configuring and running yt-dlp, making it easy to download videos without needing to remember complex command-line arguments.

## Features

The GUI includes comprehensive tabs for all major yt-dlp option categories:

### Main Tabs

1. **General** - Basic options like ignore errors, playlist handling, age limits, etc.
2. **Network** - Proxy settings, timeouts, rate limiting, retries, etc.
3. **Geo-restriction** - Bypass geo-restrictions with proxies and country settings
4. **Video Selection** - Playlist items, date ranges, file size filters, view count filters
5. **Download** - Concurrent fragments, rate limiting, external downloaders, HLS options
6. **Filesystem** - Output templates, directory settings, file naming, metadata files
7. **Video Format** - Format selection, quality preferences, merge options
8. **Subtitles** - Subtitle download, embedding, format, and language selection
9. **Authentication** - Username/password, two-factor, video passwords, certificates
10. **Post-processing** - Audio extraction, format conversion, metadata embedding, FFmpeg options
11. **Thumbnail** - Thumbnail download and conversion options
12. **Verbosity/Simulation** - Logging levels, simulation mode, info extraction
13. **Workarounds** - SSL certificates, user agents, encoding, headers
14. **SponsorBlock** - SponsorBlock integration for skipping sponsor segments
15. **Extractor** - Extractor-specific arguments, cookies, retry settings
16. **Advanced** - Raw command-line arguments and command generation

## Usage

### Launch from Command Line

You can launch the GUI in several ways:

```bash
# Method 1: Using the --gui flag
yt-dlp --gui

# Method 2: Using the GUI launcher script
python yt-dlp-gui.py

# Method 3: Using Python module
python -m yt_dlp.gui

# Method 4: From Python code
python -c "import yt_dlp; yt_dlp.main_gui()"
```

### Basic Workflow

1. **Enter URL**: Paste the video URL in the top input field, or select a batch file containing multiple URLs
2. **Configure Options**: Navigate through the tabs to configure download options as needed
3. **Quick Actions**:
   - **Download**: Start downloading with current settings
   - **List Formats**: View available video/audio formats for the URL
   - **Extract Info**: Get detailed JSON metadata about the video
   - **Load Config**: Load previously saved configuration
   - **Save Config**: Save current configuration for later use
4. **Monitor Progress**: Watch the output console at the bottom for real-time progress
5. **Advanced**: Use the "Advanced" tab to add custom command-line arguments or view the generated command

### Configuration Management

The GUI automatically saves your settings to `~/.yt-dlp-gui-config.json`. You can also:

- **Load Config**: Import configuration from a JSON file
- **Save Config**: Export current configuration to a JSON file
- Settings persist between sessions

### Command Generation

The "Advanced" tab allows you to:
- View the complete command that will be executed
- Add raw command-line arguments
- Copy the generated command to clipboard for use in scripts

## Requirements

- Python 3.10 or higher (same as yt-dlp)
- tkinter (usually included with Python)
  - On Debian/Ubuntu: `sudo apt-get install python3-tk`
  - On Fedora: `sudo dnf install python3-tkinter`
  - On macOS: Included with Python
  - On Windows: Included with Python

## Features Highlights

### Comprehensive Options
- All yt-dlp command-line options available through intuitive GUI
- Organized by category with tabs for easy navigation
- Tooltips and descriptions for each option

### Real-time Feedback
- Live output console showing download progress
- Status bar indicating current operation
- Error messages and warnings displayed clearly

### User-Friendly Design
- Clean, organized interface with scrollable option panels
- File/directory browsers for path selection
- Dropdown menus for predefined choices
- Checkbox toggles for boolean options

### Flexibility
- Mix GUI options with raw command-line arguments
- Generate and copy commands for scripting
- Load/save configurations for different use cases

## Examples

### Example 1: Simple Video Download
1. Paste URL in the "Video URL(s)" field
2. Click "Download"

### Example 2: Audio Only (MP3)
1. Enter video URL
2. Go to "Post-processing" tab
3. Check "Extract audio"
4. Select "mp3" from "Audio format" dropdown
5. Click "Download"

### Example 3: Download with Subtitles
1. Enter video URL
2. Go to "Subtitles" tab
3. Check "Write subtitle file"
4. Enter language codes (e.g., "en,fr,de")
5. Check "Embed subtitles" if desired
6. Click "Download"

### Example 4: Playlist with Quality Selection
1. Enter playlist URL
2. Go to "Video Selection" tab
3. Enter playlist items (e.g., "1-10")
4. Go to "Video Format" tab
5. Enter format (e.g., "bestvideo[height<=1080]+bestaudio/best[height<=1080]")
6. Go to "Filesystem" tab
7. Set output directory
8. Click "Download"

## Troubleshooting

### GUI Won't Launch
- Make sure tkinter is installed (see Requirements above)
- Check Python version: `python --version` (must be 3.10+)
- Try launching with verbose errors: `python -c "import yt_dlp; yt_dlp.main_gui()"`

### yt-dlp Not Found
- Ensure yt-dlp is installed: `pip install yt-dlp`
- Or install from source: `pip install -e .` from the repository directory
- Make sure yt-dlp is in your PATH

### Configuration Not Saving
- Check write permissions for home directory
- Configuration file location: `~/.yt-dlp-gui-config.json`
- You can manually edit this JSON file if needed

## Tips

1. **Save Frequently Used Settings**: Create configuration presets for different scenarios (e.g., "Audio Only", "Best Quality", "Quick Download")
2. **Use Batch Files**: For downloading multiple videos, create a text file with one URL per line and use the "Batch File" option
3. **Check Formats First**: Use "List Formats" before downloading to see available quality options
4. **Test with Simulate**: Check the "Simulate" option in Verbosity tab to test settings without downloading
5. **Command-Line Integration**: Generate commands in the Advanced tab and use them in scripts or cron jobs

## Contributing

If you encounter issues or have suggestions for improving the GUI:
1. Check existing issues at https://github.com/yt-dlp/yt-dlp/issues
2. Create a new issue with:
   - Description of the problem or feature request
   - Steps to reproduce (for bugs)
   - Your operating system and Python version
   - yt-dlp version

## License

The yt-dlp GUI is part of yt-dlp and is released under the same license (Unlicense).

## Notes

- The GUI is a frontend to yt-dlp; all actual downloading is done by the yt-dlp core
- Command-line options and GUI options are equivalent
- Some advanced options may require specific dependencies (e.g., FFmpeg for post-processing)
- GUI settings do not conflict with command-line configuration files
