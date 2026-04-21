"""Constants for yt-dlp GUI"""

LANGUAGE_OPTIONS = {
    'auto': 'Auto Detect / 自动识别',
    'zh': '中文',
    'en': 'English',
    'ru': 'Русский',
    'ja': '日本語',
    'ko': '한국어',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch / German'
}


SB_CATEGORIES = [
    'sponsor', 'intro', 'outro', 'selfpromo', 'preview',
    'filler', 'interaction', 'music_offtopic', 'poi_highlight', 'chapter'
]


GUI_DEFAULT_STATE = {
    'language': 'auto',
    'url_entry': 'https://www.youtube.com/watch?v=DtPmasWzmu4&list=PLqyUAJYG3AWzd2mRGVLgCNKXbFcE4mAAk',
    'cookies_from_browser': 'chrome',
    'format': 'bv*[height<=1080]+ba',
}
