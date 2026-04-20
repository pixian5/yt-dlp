#!/usr/bin/env python3
"""
GUI Panel for yt-dlp - Graphical User Interface for configuring and running yt-dlp

This module provides a comprehensive GUI interface using tkinter for easy configuration
of all yt-dlp options without needing to remember command-line arguments.
"""

import json
import locale
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import subprocess
import os
import signal
import shutil
import tempfile
import atexit


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


TRANSLATIONS = {
    'zh': {
        'Extract audio (--extract-audio)': '仅提取音频',
        'yt-dlp GUI - Video Downloader Configuration': 'yt-dlp 图形界面 - 视频下载配置',
        'Language:': '语言：',
        'Paste Link:': '粘贴链接：',
        'Stop': '停止',
        'Download stopped. Would you like to delete partially downloaded files?': '下载已停止。是否要删除未下载完的临时文件？',
        'Video URL(s):': '视频 URL：',
        'Or Batch File:': '或批量文件：',
        'Browse...': '浏览...',
        'Download': '下载',
        'List Formats': '列出格式',
        'Extract Info': '提取信息',
        'Load Config': '加载配置',
        'Save Config': '保存配置',
        'Parse Playlist': '解析播放列表',
        'Exclude private videos': '隐藏私有视频',
        'Reverse order': '播放列表倒序',
        'Output Console': '输出控制台',
        'Ready': '就绪',
        'Clipboard is empty.': '剪贴板为空。',
        'Pasted link from clipboard.': '已从剪贴板粘贴链接。',
        'Paste': '粘贴',
        'Pasted into batch text box.': '已粘贴到批量文本框。',
        'Paste Playlist': '粘贴播放列表',
        'Batch Download': '批量下载',
        'Playlist': '播放列表',
        'Batch file path:': '批量文件路径：',
        'Batch URLs (one per line):': '批量 URL (每行一个):',
        'Parse': '解析',
        'Parse All': '全部解析',
        'Bulk Paste': '批量粘贴',
        'Parse Batch': '解析批量',
        'Clear Pool': '清空列表',
        'General': '常规',
        'Network': '网络',
        'Geo-restriction': '地区限制',
        'Video Selection': '视频筛选',
        'Filesystem': '文件系统',
        'Video Format': '视频格式',
        'Subtitles': '字幕',
        'Authentication': '认证',
        'Post-processing': '后处理',
        'Thumbnail': '缩略图',
        'Verbosity/Simulation': '输出/模拟',
        'Workarounds': '兼容方案',
        'SponsorBlock': '广告拦截',
        'Extractor': '提取器',
        'Advanced': '高级',
        'Configuration file:': '配置文件：',
        'Default search prefix:': '默认搜索前缀：',
        'Flat playlist extraction:': '平铺播放列表提取：',
        'Age limit (years):': '年龄限制（岁）：',
        'Download archive file:': '下载归档文件：',
        'Max downloads:': '最大下载数：',
        'Proxy URL:': '代理 URL：',
        'Socket timeout (seconds):': '套接字超时（秒）：',
        'Source address (bind to):': '源地址（绑定到）：',
        'Sleep interval (seconds):': '休眠间隔（秒）：',
        'Max sleep interval (seconds):': '最大休眠间隔（秒）：',
        'Sleep interval for requests (seconds):': '请求休眠间隔（秒）：',
        'Sleep interval for subtitles (seconds):': '字幕休眠间隔（秒）：',
        'Rate limit (e.g., "50K" or "4.2M"):': '限速（例如“50K”或“4.2M”）：',
        'Throttled rate (minimum rate):': '节流速率（最小速率）：',
        'Retries:': '重试次数：',
        'Fragment retries:': '分片重试次数：',
        'Geo verification proxy:': '地区校验代理：',
        'Geo bypass country:': '地区绕过国家：',
        'Geo bypass IP block:': '地区绕过 IP 段：',
        'Playlist items:': '播放列表项目：',
        'Playlist start:': '播放列表起始：',
        'Playlist end:': '播放列表结束：',
        'Match title (regex):': '匹配标题（正则）：',
        'Reject title (regex):': '排除标题（正则）：',
        'Min filesize (e.g., 50k or 1M):': '最小文件大小（例如 50k 或 1M）：',
        'Max filesize (e.g., 50M or 1G):': '最大文件大小（例如 50M 或 1G）：',
        'Date (YYYYMMDD):': '日期（YYYYMMDD）：',
        'Date before (YYYYMMDD):': '此前日期（YYYYMMDD）：',
        'Date after (YYYYMMDD):': '此后日期（YYYYMMDD）：',
        'Min views:': '最小观看数：',
        'Max views:': '最大观看数：',
        'Match filter:': '匹配筛选器：',
        'Concurrent fragments:': '并发分片数：',
        'Limit download rate:': '限制下载速率：',
        'Buffer size:': '缓冲区大小：',
        'HTTP chunk size:': 'HTTP 分块大小：',
        'External downloader:': '外部下载器：',
        'External downloader args:': '外部下载器参数：',
        'Output template:': '输出模板：',
        'Output directory:': '输出目录：',
        'Paths configuration:': '路径配置：',
        'Load info JSON:': '加载信息 JSON：',
        'Cache directory:': '缓存目录：',
        'Format selection:': '格式选择：',
        'Format sort:': '格式排序：',
        'Merge output format:': '合并输出格式：',
        'Video multistreams:': '视频多流：',
        'Audio multistreams:': '音频多流：',
        'Subtitle format:': '字幕格式：',
        'Subtitle languages:': '字幕语言：',
        'Username:': '用户名：',
        'Password:': '密码：',
        'Two-factor code:': '双重验证码：',
        'Video password:': '视频密码：',
        'Adobe Pass MSO:': 'Adobe Pass MSO 提供商：',
        'Adobe Pass username:': 'Adobe Pass 用户名：',
        'Adobe Pass password:': 'Adobe Pass 密码：',
        'Client certificate:': '客户端证书：',
        'Client certificate key:': '客户端证书密钥：',
        'Client certificate password:': '客户端证书密码：',
        'Audio format:': '音频格式：',
        'Audio quality:': '音频质量：',
        'Recode video format:': '视频转码格式：',
        'Remux video format:': '视频重封装格式：',
        'Metadata fields:': '元数据字段：',
        'Parse metadata:': '解析元数据：',
        'FFmpeg location:': 'FFmpeg 位置：',
        'Post-processor args:': '后处理参数：',
        'Convert thumbnails format:': '转换缩略图格式为：',
        'Progress template:': '进度条模板：',
        'Metadata language:': '元数据语言：',
        'Default (Auto)': '默认（自动）',
        'Encoding:': '编码：',
        'User agent:': '用户代理 (User Agent)：',
        'Referer:': '引用页 (Referer)：',
        'Add header:': '添加请求头：',
        'Sleep before requests:': '请求前休眠：',
        "SponsorBlock categories to remove:": "要移除的广告拦截分类：",
        "SponsorBlock categories to mark:": "要标记的广告拦截分类：",
        "SponsorBlock chapter title:": "广告拦截章节标题：",
        "SponsorBlock API URL:": "广告拦截 API URL：",
        'Extractor arguments:': '提取器参数：',
        'Extractor retries:': '提取器重试次数：',
        'Cookies from browser:': '从浏览器导入 Cookie：',
        'Cookies file:': 'Cookie 文件：',
        'Raw command-line arguments:': '原始命令行参数：',
        'Generated command:': '生成的命令：',
        'Generate Command': '生成命令',
        'Copy to Clipboard': '复制到剪贴板',
        'Running: yt-dlp ': '正在运行: yt-dlp ',
        'Downloading...': '下载中...',
        'Download completed successfully!': '下载完成！',
        'Process exited with code ': '进程退出，退出码 ',
        'ERROR: yt-dlp not found. Please make sure yt-dlp is installed and in your PATH.': '错误：未找到 yt-dlp。请确保已安装并添加到环境变量。',
        'ERROR: ': '错误：',
        'Command copied to clipboard!': '命令已复制到剪贴板！',
        'No URL': '无 URL',
        'Please enter a URL or batch file to download.': '请输入要下载的 URL 或批量文件。',
        'Please enter a URL.': '请输入 URL。',
        'Error': '错误',
        'Success': '成功',
        'Failed to save configuration: ': '保存配置失败: ',
        'Failed to load configuration: ': '加载配置失败: ',
        'Configuration loaded successfully!': '配置加载成功！',
        'Configuration saved successfully!': '配置保存成功！',
        'Load Configuration': '加载配置',
        'Save Configuration': '保存配置',
        'Select Batch File': '选择批量文件',
        'Select Config File': '选择配置文件',
        'Select Archive File': '选择归档文件',
        'Select Output Directory': '选择输出目录',
        'Select Info JSON': '选择信息 JSON',
        'Select Cache Directory': '选择缓存目录',
        'Select Client Certificate': '选择客户端证书',
        'Select Client Certificate Key': '选择证书密钥',
        'Select FFmpeg Binary': '选择 FFmpeg 二进制文件',
        'Select Cookies File': '选择 Cookie 文件',
        'Text Files': '文本文件',
        'All Files': '所有文件',
        'Config Files': '配置文件',
        'JSON Files': 'JSON 文件',
        'PEM Files': 'PEM 文件',
        'Key Files': '密钥文件',
        'Executable Files': '可执行文件',
        ')': '（逗号分隔，如 "en,fr,de"）',
        '(ISO 3166-2 code)': '（ISO 3166-2 代码）',
        '(CIDR notation)': '（CIDR 表示法）',
        '(e.g., "50K" or "4.2M")': '（如 "50K" 或 "4.2M"）',
        '(comma-separated)': '（逗号分隔）',
        '(key:val[,val] format)': '（key:val[,val] 格式）',
        '(One argument per line or space-separated)': '（每行一个参数或空格分隔）',
        '(0-10, 0 = best)': '（0-10, 0 = 最佳）',
        'Ignore errors (--ignore-errors)': '忽略错误 (--ignore-errors)',
        'Ignore warnings (--no-warnings)': '忽略警告 (--no-warnings)',
        'Abort on error (--abort-on-error)': '出错时终止 (--abort-on-error)',
        'Download only video, not playlist (--no-playlist)': '仅下载视频，不下载播放列表 (--no-playlist)',
        'Download playlist (--yes-playlist)': '下载播放列表 (--yes-playlist)',
        'Include private/unavailable videos in YouTube playlists': '包括 YouTube 播放列表中的私有/不可用视频',
        'Mark videos as watched (--mark-watched)': '将视频标记为已看 (--mark-watched)',
        'Do not mark videos as watched (--no-mark-watched)': '不要将视频标记为已看 (--no-mark-watched)',
        'Force IPv4 (--force-ipv4)': '强制使用 IPv4 (--force-ipv4)',
        'Force IPv6 (--force-ipv6)': '强制使用 IPv6 (--force-ipv6)',
        'Enable file:// URLs (--enable-file-urls)': '启用 file:// URL (--enable-file-urls)',
        'Bypass geo restriction (--geo-bypass)': '绕过地理限制 (--geo-bypass)',
        'Do not bypass geo restriction (--no-geo-bypass)': '不绕过地理限制 (--no-geo-bypass)',
        'Break on existing (--break-on-existing)': '遇到现有文件时停止 (--break-on-existing)',
        'Break on reject (--break-on-reject)': '遇到拒绝时停止 (--break-on-reject)',
        'No break on existing (--no-break-on-existing)': '遇到现有文件时不停止 (--no-break-on-existing)',
        'Do not resize buffer (--no-resize-buffer)': '不调整缓冲区大小 (--no-resize-buffer)',
        'Test mode - do not download (--test)': '测试模式 - 不进行下载 (--test)',
        'Prefer native HLS downloader (--hls-prefer-native)': '首选原生 HLS 下载器 (--hls-prefer-native)',
        'Prefer ffmpeg for HLS (--hls-prefer-ffmpeg)': 'HLS 首选 ffmpeg (--hls-prefer-ffmpeg)',
        'Use MPEG-TS container for HLS (--hls-use-mpegts)': 'HLS 使用 MPEG-TS 容器 (--hls-use-mpegts)',
        'Restrict filenames to ASCII (--restrict-filenames)': '限制文件名为 ASCII 字符 (--restrict-filenames)',
        'Allow Unicode in filenames (--no-restrict-filenames)': '允许文件名中使用 Unicode (--no-restrict-filenames)',
        'Create playlist subfolder for playlist downloads': '为播放列表下载创建子文件夹',
        'Force Windows-compatible filenames (--windows-filenames)': '强制使用 Windows 兼容文件名 (--windows-filenames)',
        'Do not overwrite files (--no-overwrites)': '不覆盖文件 (--no-overwrites)',
        'Force overwrite files (--force-overwrites)': '强制覆盖文件 (--force-overwrites)',
        'Continue partially downloaded files (--continue)': '继续下载未完成的文件 (--continue)',
        'Do not continue downloads (--no-continue)': '不继续下载 (--no-continue)',
        'Do not use .part files (--no-part)': '不使用 .part 文件 (--no-part)',
        'Do not use Last-modified header (--no-mtime)': '不使用“上次修改”标头 (--no-mtime)',
        'Write description to .description file (--write-description)': '将描述写入 .description 文件 (--write-description)',
        'Write metadata to .info.json file (--write-info-json)': '将元数据写入 .info.json 文件 (--write-info-json)',
        'Write annotations to .annotations.xml (--write-annotations)': '将注释写入 .annotations.xml (--write-annotations)',
        'Write comments to .comments.json (--write-comments)': '将评论写入 .comments.json (--write-comments)',
        'Disable filesystem caching (--no-cache-dir)': '禁用文件系统缓存 (--no-cache-dir)',
        'Delete cache directory contents (--rm-cache-dir)': '删除缓存目录内容 (--rm-cache-dir)',
        'Prefer free formats (--prefer-free-formats)': '首选免费格式 (--prefer-free-formats)',
        'Check available formats (--check-formats)': '检查可用格式 (--check-formats)',
        'Write subtitle file (--write-subs)': '写入字幕文件 (--write-subs)',
        'Write automatic subtitle file (--write-auto-subs)': '写入自动生成字幕文件 (--write-auto-subs)',
        'List available subtitles (--list-subs)': '列出可用字幕 (--list-subs)',
        'Embed subtitles (--embed-subs)': '嵌入字幕 (--embed-subs)',
        'Do not embed subtitles (--no-embed-subs)': '不嵌入字幕 (--no-embed-subs)',
        'Embed thumbnail (--embed-thumbnail)': '嵌入缩略图 (--embed-thumbnail)',
        'Do not embed thumbnail (--no-embed-thumbnail)': '不嵌入缩略图 (--no-embed-thumbnail)',
        'Use .netrc authentication (--netrc)': '使用 .netrc 身份验证 (--netrc)',
        'Extract audio (-x, --extract-audio)': '提取音频 (-x, --extract-audio)',
        'Keep video file after conversion (--keep-video)': '转换后保留视频文件 (--keep-video)',
        'Do not keep video file (--no-keep-video)': '不保留视频文件 (--no-keep-video)',
        'Embed metadata (--embed-metadata)': '嵌入元数据 (--embed-metadata)',
        'Embed chapter markers (--embed-chapters)': '嵌入章节标记 (--embed-chapters)',
        'Embed info.json (--embed-info-json)': '嵌入 info.json (--embed-info-json)',
        'Add metadata to file (--add-metadata)': '向文件添加元数据 (--add-metadata)',
        'Write thumbnail image (--write-thumbnail)': '写入缩略图文件 (--write-thumbnail)',
        'Write all thumbnail formats (--write-all-thumbnails)': '写入所有格式的缩略图 (--write-all-thumbnails)',
        'List available thumbnails (--list-thumbnails)': '列出可用缩略图 (--list-thumbnails)',
        'Quiet mode (-q, --quiet)': '静默模式 (-q, --quiet)',
        'No warnings (--no-warnings)': '无警告 (--no-warnings)',
        'Verbose output (-v, --verbose)': '详细输出 (-v, --verbose)',
        'Simulate, do not download (-s, --simulate)': '模拟，不下载 (-s, --simulate)',
        'Skip download (--skip-download)': '跳过下载 (--skip-download)',
        'Get title (--get-title)': '获取标题 (--get-title)',
        'Get ID (--get-id)': '获取 ID (--get-id)',
        'Get URL (--get-url)': '获取 URL (--get-url)',
        'Get thumbnail URL (--get-thumbnail)': '获取缩略图 URL (--get-thumbnail)',
        'Get description (--get-description)': '获取描述 (--get-description)',
        'Get duration (--get-duration)': '获取时长 (--get-duration)',
        'Get filename (--get-filename)': '获取文件名 (--get-filename)',
        'Get format (--get-format)': '获取格式 (--get-format)',
        'Dump JSON info (--dump-json)': '转储 JSON 信息 (--dump-json)',
        'Dump single JSON (--dump-single-json)': '转储单个 JSON (--dump-single-json)',
        'Print JSON info (--print-json)': '打印 JSON 信息 (--print-json)',
        'Show progress (--progress)': '显示进度 (--progress)',
        'Hide progress (--no-progress)': '隐藏进度 (--no-progress)',
        'Display progress in console title (--console-title)': '在控制台标题中显示进度 (--console-title)',
        'Skip SSL certificate validation (--no-check-certificate)': '跳过 SSL 证书验证 (--no-check-certificate)',
        'Prefer insecure connections (--prefer-insecure)': '首选不安全连接 (--prefer-insecure)',
        'Bidirectional text workaround (--bidi-workaround)': '双向文本解决方法 (--bidi-workaround)',
        'Use legacy server connect (--legacy-server-connect)': '使用旧版服务器连接 (--legacy-server-connect)',
        'Mark SponsorBlock chapters (--sponsorblock-mark)': '标记广告拦截章节 (--sponsorblock-mark)',
        'Remove SponsorBlock segments (--sponsorblock-remove)': '删除广告拦截片段 (--sponsorblock-remove)',
        'Disable SponsorBlock (--no-sponsorblock)': '禁用广告拦截 (--no-sponsorblock)',
        'Allow dynamic MPD manifests (--allow-dynamic-mpd)': '允许动态 MPD 清单 (--allow-dynamic-mpd)',
        'Ignore dynamic MPD manifests (--ignore-dynamic-mpd)': '忽略动态 MPD 清单 (--ignore-dynamic-mpd)',
        'Split HLS segments on discontinuity (--hls-split-discontinuity)': '在不连续处拆分 HLS 片段 (--hls-split-discontinuity)',
        'Select All / Deselect All': '全选 / 取消全选',
        'Quick Select Resolution:': '快速选择分辨率：',
        'Best (Auto)': '最佳',
        '4K (2160p)': '4K (2160p)',
        '2K (1440p)': '2K (1440p)',
        '1080p 60fps': '1080p 60帧',
        '1080p': '1080p',
        '720p 60fps': '720p 60帧',
        '720p': '720p',
        '480p': '480p',
        '360p': '360p',
        "sponsor": "赞助商广告",
        "intro": "开场/介绍",
        "outro": "片尾/结束",
        "selfpromo": "自我推广",
        "preview": "预告",
        "filler": "填充内容/废话",
        "interaction": "互动提示 (关注/订阅)",
        "music_offtopic": "音乐: 非相关部分",
        "poi_highlight": "精华/亮点",
        "chapter": "章节",
        "Select All": "全选",
        "Deselect All": "取消全选",
        "Invert Select": "反选",
        "720p 60fps": "720p 60帧",
    },
    'ru': {
        "Extract audio (--extract-audio)": "Извлечь аудио (--extract-audio)",
        "yt-dlp GUI - Video Downloader Configuration": "yt-dlp GUI - Настройка загрузчика видео",
        "Language:": "Язык:",
        "Paste Link:": "Вставить ссылку:",
        "Stop": "Стоп",
        "Download stopped. Would you like to delete partially downloaded files?": "Загрузка остановлена. Удалить частично загруженные файлы?",
        "Video URL(s):": "URL видео:",
        "Or Batch File:": "Или пакетный файл:",
        "Browse...": "Обзор...",
        "Download": "Скачать",
        "List Formats": "Список форматов",
        "Extract Info": "Извлечь инфо",
        "Load Config": "Загрузить конфиг",
        "Save Config": "Сохранить конфиг",
        "Parse Playlist": "Разбор плейлиста",
        "Exclude private videos": "Исключить приватные видео",
        "Reverse order": "Обратный порядок",
        "Output Console": "Консоль вывода",
        "Ready": "Готово",
        "Clipboard is empty.": "Буфер обмена пуст.",
        "Pasted link from clipboard.": "Ссылка вставлена из буфера обмена.",
        "Paste": "Вставить",
        "Pasted into batch text box.": "Вставлено в текстовое поле пакета.",
        "Paste Playlist": "Вставить плейлист",
        "Batch Download": "Пакетная загрузка",
        "Playlist": "Плейлист",
        "Batch file path:": "Путь к пакетному файлу:",
        "Batch URLs (one per line):": "Ссылки для пакета (по одной на строку):",
        "Parse": "Разобрать",
        "Parse All": "Разобрать все",
        "Bulk Paste": "Массовая вставка",
        "Parse Batch": "Разобрать пакет",
        "Clear Pool": "Очистить список",
        "General": "Общие",
        "Network": "Сеть",
        "Geo-restriction": "Гео-ограничения",
        "Video Selection": "Выбор видео",
        "Filesystem": "Файловая система",
        "Video Format": "Формат видео",
        "Subtitles": "Субтитры",
        "Authentication": "Аутентификация",
        "Post-processing": "Пост-обработка",
        "Thumbnail": "Миниатюры",
        "Verbosity/Simulation": "Подробности/Симуляция",
        "Workarounds": "Обходные пути",
        "SponsorBlock": "SponsorBlock",
        "Extractor": "Экстрактор",
        "Advanced": "Расширенные",
        "Configuration file:": "Файл конфигурации:",
        "Default search prefix:": "Префикс поиска по умолчанию:",
        "Flat playlist extraction:": "Плоское извлечение плейлиста:",
        "Age limit (years):": "Ограничение по возрасту (лет):",
        "Download archive file:": "Файл архива загрузок:",
        "Max downloads:": "Макс. загрузок:",
        "Proxy URL:": "Proxy URL:",
        "Socket timeout (seconds):": "Тайм-аут сокета (сек):",
        "Source address (bind to):": "Адрес источника (привязать к):",
        "Sleep interval (seconds):": "Интервал сна (сек):",
        "Max sleep interval (seconds):": "Макс. интервал сна (сек):",
        "Sleep interval for requests (seconds):": "Интервал сна для запросов (сек):",
        "Sleep interval for subtitles (seconds):": "Интервал сна для субтитров (сек):",
        "Rate limit (e.g., '50K' or '4.2M'):": "Лимит скорости (напр., '50K' или '4.2M'):",
        "Throttled rate (minimum rate):": "Минимальная скорость:",
        "Retries:": "Попыток:",
        "Fragment retries:": "Попыток фрагмента:",
        "Geo verification proxy:": "Прокси гео-верификации:",
        "Geo bypass country:": "Страна обхода гео:",
        "Geo bypass IP block:": "IP блок обхода гео:",
        "Playlist items:": "Элементы плейлиста:",
        "Playlist start:": "Начало плейлиста:",
        "Playlist end:": "Конец плейлиста:",
        "Match title (regex):": "Совпадение заголовка (regex):",
        "Reject title (regex):": "Исключение заголовка (regex):",
        "Min filesize (e.g., 50k or 1M):": "Мин. размер (напр., 50k или 1M):",
        "Max filesize (e.g., 50M or 1G):": "Макс. размер (напр., 50M или 1G):",
        "Date (YYYYMMDD):": "Дата (ГГГГММДД):",
        "Date before (YYYYMMDD):": "Дата до (ГГГГММДД):",
        "Date after (YYYYMMDD):": "Дата после (ГГГГММДД):",
        "Min views:": "Мин. просмотров:",
        "Max views:": "Макс. просмотров:",
        "Match filter:": "Фильтр совпадений:",
        "Concurrent fragments:": "Параллельных фрагментов:",
        "Limit download rate:": "Ограничить скорость:",
        "Buffer size:": "Размер буфера:",
        "HTTP chunk size:": "Размер чанка HTTP:",
        "External downloader:": "Внешний загрузчик:",
        "External downloader args:": "Аргументы внешнего загрузчика:",
        "Output template:": "Шаблон вывода:",
        "Output directory:": "Директория вывода:",
        "Paths configuration:": "Настройка путей:",
        "Load info JSON:": "Загрузить инфо JSON:",
        "Cache directory:": "Директория кэша:",
        "Format selection:": "Выбор формата:",
        "Format sort:": "Сортировка форматов:",
        "Merge output format:": "Формат слияния:",
        "Video multistreams:": "Видео мультипотоки:",
        "Audio multistreams:": "Аудио мультипотоки:",
        "Subtitle format:": "Формат субтитров:",
        "Subtitle languages:": "Языки субтитров:",
        "Username:": "Имя пользователя:",
        "Password:": "Пароль:",
        "Two-factor code:": "Код 2FA:",
        "Video password:": "Пароль к видео:",
        "Adobe Pass MSO:": "Провайдер Adobe Pass MSO:",
        "Adobe Pass username:": "Пользователь Adobe Pass:",
        "Adobe Pass password:": "Пароль Adobe Pass:",
        "Client certificate:": "Клиентский сертификат:",
        "Client certificate key:": "Ключ сертификата:",
        "Client certificate password:": "Пароль сертификата:",
        "Audio format:": "Формат аудио:",
        "Audio quality:": "Качество аудио:",
        "Recode video format:": "Перекодировать видео в:",
        "Remux video format:": "Ремуксить видео в:",
        "Metadata fields:": "Поля метаданных:",
        "Parse metadata:": "Парсить метаданные:",
        "FFmpeg location:": "Путь к FFmpeg:",
        "Post-processor args:": "Аргументы пост-процессора:",
        "Convert thumbnails format:": "Конвертировать миниатюры:",
        "Progress template:": "Шаблон прогресса:",
        "Metadata language:": "Язык метаданных:",
        "Default (Auto)": "По умолчанию (Авто)",
        "Encoding:": "Кодировка:",
        "User agent:": "User Agent:",
        "Referer:": "Referer:",
        "Add header:": "Добавить заголовок:",
        "Sleep before requests:": "Сон перед запросами:",
        "SponsorBlock categories to remove:": "Категории SponsorBlock для удаления:",
        "SponsorBlock categories to mark:": "Категории SponsorBlock для отметки:",
        "SponsorBlock chapter title:": "Заголовок глав SponsorBlock:",
        "SponsorBlock API URL:": "SponsorBlock API URL:",
        "Extractor arguments:": "Аргументы экстрактора:",
        "Extractor retries:": "Попыток экстрактора:",
        "Cookies from browser:": "Куки из браузера:",
        "Cookies file:": "Файл куки:",
        "Raw command-line arguments:": "Сырые аргументы командной строки:",
        "Generated command:": "Сгенерированная команда:",
        "Generate Command": "Создать команду",
        "Copy to Clipboard": "Скопировать",
        "Running: yt-dlp ": "Запуск: yt-dlp ",
        "Downloading...": "Загрузка...",
        "Download completed successfully!": "Загрузка успешно завершена!",
        "Process exited with code ": "Процесс завершен с кодом ",
        "ERROR: yt-dlp not found. Please make sure yt-dlp is installed and in your PATH.": "ОШИБКА: yt-dlp не найден.",
        "ERROR: ": "ОШИБКА: ",
        "Command copied to clipboard!": "Команда скопирована!",
        "No URL": "Нет ссылки",
        "Please enter a URL or batch file to download.": "Введите ссылку или выберите пакетный файл.",
        "Please enter a URL.": "Пожалуйста, введите ссылку.",
        "Error": "Ошибка",
        "Success": "Успех",
        "Failed to save configuration: ": "Ошибка сохранения конфига: ",
        "Failed to load configuration: ": "Ошибка загрузки конфига: ",
        "Configuration loaded successfully!": "Конфигурация загружена!",
        "Configuration saved successfully!": "Конфигурация сохранена!",
        "Load Configuration": "Загрузить конфиг",
        "Save Configuration": "Сохранить конфиг",
        "Select Batch File": "Выбрать пакетный файл",
        "Select Config File": "Выбрать файл конфига",
        "Select Archive File": "Выбрать файл архива",
        "Select Output Directory": "Выбрать директорию вывода",
        "Select Info JSON": "Выбрать инфо JSON",
        "Select Cache Directory": "Выбрать директорию кэша",
        "Select Client Certificate": "Выбрать сертификат",
        "Select Client Certificate Key": "Выбрать ключ",
        "Select FFmpeg Binary": "Выбрать FFmpeg",
        "Select Cookies File": "Выбрать файл куки",
        "Select All / Deselect All": "Выбрать все / Снять выделение",
        "Quick Select Resolution:": "Быстри разрешения:",
        "Best (Auto)": "Лучшее (Авто)",
        "4K (2160p)": "4K (2160p)",
        "2K (1440p)": "2K (1440p)",
        "1080p 60fps": "1080p 60к/с",
        "1080p": "1080p",
        "720p 60fps": "720p 60к/с",
        "720p": "720p",
        "480p": "480p",
        "360p": "360p",
        "sponsor": "Спонсор",
        "intro": "Вступление",
        "outro": "Концовка",
        "selfpromo": "Самореклама",
        "preview": "Превью",
        "filler": "Филлер",
        "interaction": "Взаимодействие",
        "music_offtopic": "Музыка: Оффтоп",
        "poi_highlight": "Лучший момент",
        "chapter": "Глава",
        "Select All": "Выбрать все",
        "Deselect All": "Снять все",
        "Invert Select": "Инвертировать",
        "720p 60fps": "720p 60к/с",
    },
    'ja': {
        "Extract audio (--extract-audio)": "音声のみ抽出 (--extract-audio)",
        "yt-dlp GUI - Video Downloader Configuration": "yt-dlp GUI - 動画ダウンローダー設定",
        "Language:": "言語:",
        "Paste Link:": "リンクを貼り付け:",
        "Stop": "停止",
        "Download stopped. Would you like to delete partially downloaded files?": "ダウンロードが停止しました。一時ファイルを削除しますか？",
        "Video URL(s):": "動画 URL:",
        "Or Batch File:": "または一括ファイル:",
        "Browse...": "参照...",
        "Download": "ダウンロード",
        "List Formats": "形式一覧",
        "Extract Info": "情報を抽出",
        "Load Config": "設定を読み込む",
        "Save Config": "設定を保存",
        "Parse Playlist": "プレイリスト解析",
        "Exclude private videos": "非公開動画を除外",
        "Reverse order": "逆順",
        "Output Console": "出力コンソール",
        "Ready": "準備完了",
        "Clipboard is empty.": "クリップボードが空です。",
        "Pasted link from clipboard.": "クリップボードからリンクを貼り付けました。",
        "Paste": "貼り付け",
        "Pasted into batch text box.": "バッチテキストボックスに貼り付けました。",
        "Paste Playlist": "プレイリストを貼り付け",
        "Batch Download": "一括ダウンロード",
        "Playlist": "プレイリスト",
        "Batch file path:": "ファイルパス:",
        "Batch URLs (one per line):": "URL一覧 (1行に1件):",
        "Parse": "解析",
        "Parse All": "すべて解析",
        "Bulk Paste": "一括貼り付け",
        "Parse Batch": "一括解析",
        "Clear Pool": "リストをクリア",
        "General": "一般",
        "Network": "ネットワーク",
        "Geo-restriction": "地域制限",
        "Video Selection": "動画選択",
        "Filesystem": "ファイルシステム",
        "Video Format": "動画形式",
        "Subtitles": "字幕",
        "Authentication": "認証",
        "Post-processing": "後処理",
        "Thumbnail": "サムネイル",
        "Verbosity/Simulation": "ログ出⼒/シミュレーション",
        "Workarounds": "回避策",
        "SponsorBlock": "広告ブロック",
        "Extractor": "抽出器",
        "Advanced": "詳細設定",
        "Configuration file:": "設定ファイル:",
        "Default search prefix:": "デフォルト検索プレフィックス:",
        "Flat playlist extraction:": "フラットなプレイリスト抽出:",
        "Age limit (years):": "年齢制限 (年):",
        "Download archive file:": "ダウンロードアーカイブファイル:",
        "Max downloads:": "最大ダウンロード数:",
        "Proxy URL:": "プロキシ URL:",
        "Socket timeout (seconds):": "ソケットタイムアウト (秒):",
        "Source address (bind to):": "ソースアドレス (バインド先):",
        "Sleep interval (seconds):": "スリープ間隔 (秒):",
        "Max sleep interval (seconds):": "最大スリープ間隔 (秒):",
        "Sleep interval for requests (seconds):": "リクエスト間のスリープ (秒):",
        "Sleep interval for subtitles (seconds):": "字幕のスリープ間隔 (秒):",
        "Rate limit (e.g., '50K' or '4.2M'):": "速度制限 (例: '50K' または '4.2M'):",
        "Throttled rate (minimum rate):": "最小速度:",
        "Retries:": "リトライ回数:",
        "Fragment retries:": "フラグメントリトライ回数:",
        "Geo verification proxy:": "地域検証プロキシ:",
        "Geo bypass country:": "地域バイパス国:",
        "Geo bypass IP block:": "地域バイパス IP ブロック:",
        "Playlist items:": "プレイリスト項目:",
        "Playlist start:": "プレイリスト開始位置:",
        "Playlist end:": "プレイリスト終了位置:",
        "Match title (regex):": "タイトル一致 (正規表現):",
        "Reject title (regex):": "タイトル拒否 (正規表現):",
        "Min filesize (e.g., 50k or 1M):": "最小ファイルサイズ:",
        "Max filesize (e.g., 50M or 1G):": "最大ファイルサイズ:",
        "Date (YYYYMMDD):": "日付 (YYYYMMDD):",
        "Date before (YYYYMMDD):": "以前の日付 (YYYYMMDD):",
        "Date after (YYYYMMDD):": "以降の日付 (YYYYMMDD):",
        "Min views:": "最小再生数:",
        "Max views:": "最大再生数:",
        "Match filter:": "一致フィルタ:",
        "Concurrent fragments:": "並行フラグメント数:",
        "Limit download rate:": "ダウンロード速度を制限:",
        "Buffer size:": "バッファサイズ:",
        "HTTP chunk size:": "HTTP チャンクサイズ:",
        "External downloader:": "外部ダウンローダー:",
        "External downloader args:": "外部ダウンローダー引数:",
        "Output template:": "出力テンプレート:",
        "Output directory:": "出力ディレクトリ:",
        "Paths configuration:": "パス設定:",
        "Load info JSON:": "情報 JSON を読み込む:",
        "Cache directory:": "キャッシュディレクトリ:",
        "Format selection:": "形式選択:",
        "Format sort:": "形式ソート:",
        "Merge output format:": "マージ出力形式:",
        "Video multistreams:": "動画マルチストリーム:",
        "Audio multistreams:": "音声マルチストリーム:",
        "Subtitle format:": "字幕形式:",
        "Subtitle languages:": "字幕言語:",
        "Username:": "ユーザー名:",
        "Password:": "パスワード:",
        "Two-factor code:": "2段階認証コード:",
        "Video password:": "動画パスワード:",
        "Adobe Pass MSO:": "Adobe Pass MSO プロバイダー:",
        "Adobe Pass username:": "Adobe Pass ユーザー名:",
        "Adobe Pass password:": "Adobe Pass パスワード:",
        "Client certificate:": "クライアント証明書:",
        "Client certificate key:": "証明書キー:",
        "Client certificate password:": "証明書パスワード:",
        "Audio format:": "音声形式:",
        "Audio quality:": "音質:",
        "Recode video format:": "動画形式を再エンコード:",
        "Remux video format:": "動画形式をリマック:",
        "Metadata fields:": "メタデータフィールド:",
        "Parse metadata:": "メタデータを解析:",
        "FFmpeg location:": "FFmpeg の場所:",
        "Post-processor args:": "後処理引数:",
        "Convert thumbnails format:": "サムネイル形式を変換:",
        "Progress template:": "進捗テンプレート:",
        "Metadata language:": "メタデータ言語:",
        "Default (Auto)": "デフォルト (自動)",
        "Encoding:": "エンコーディング:",
        "User agent:": "User Agent:",
        "Referer:": "Referer:",
        "Add header:": "ヘッダーを追加:",
        "Sleep before requests:": "リクエスト前にスリープ:",
        "SponsorBlock categories to remove:": "削除する SponsorBlock カテゴリ:",
        "SponsorBlock categories to mark:": "マークする SponsorBlock カテゴリ:",
        "SponsorBlock chapter title:": "SponsorBlock チャプタータイトル:",
        "SponsorBlock API URL:": "SponsorBlock API URL:",
        "Extractor arguments:": "抽出器引数:",
        "Extractor retries:": "抽出器リトライ回数:",
        "Cookies from browser:": "ブラウザからクッキーを取得:",
        "Cookies file:": "クッキーファイル:",
        "Raw command-line arguments:": "生のコマンドライン引数:",
        "Generated command:": "生成されたコマンド:",
        "Generate Command": "コマンドを生成",
        "Copy to Clipboard": "クリップボードにコピー",
        "Running: yt-dlp ": "実行中: yt-dlp ",
        "Downloading...": "ダウンロード中...",
        "Download completed successfully!": "ダウンロードが完了しました！",
        "Process exited with code ": "プロセスが終了しました。コード: ",
        "ERROR: yt-dlp not found. Please make sure yt-dlp is installed and in your PATH.": "エラー: yt-dlp が見つかりません。",
        "ERROR: ": "エラー: ",
        "Command copied to clipboard!": "コマンドをコピーしました！",
        "No URL": "URL なし",
        "Please enter a URL or batch file to download.": "ダウンロードする URL またはファイルを選択してください。",
        "Please enter a URL.": "URL を入力してください。",
        "Error": "エラー",
        "Success": "成功",
        "Failed to save configuration: ": "設定の保存に失敗しました: ",
        "Failed to load configuration: ": "設定の読み込みに失敗しました: ",
        "Select Config File": "設定ファイルを選択",
        "Select Archive File": "アーカイブファイルを選択",
        "Select Output Directory": "出力ディレクトリを選択",
        "Select Info JSON": "情報 JSON を選択",
        "Select Cache Directory": "キャッシュディレクトリを選択",
        "Select Client Certificate": "証明書を選択",
        "Select Client Certificate Key": "キーファイルを選択",
        "Select FFmpeg Binary": "FFmpeg を選択",
        "Select Cookies File": "クッキーファイルを選択",
        "Select All / Deselect All": "すべて選択 / 選択解除",
        "Quick Select Resolution:": "解像度をクイック選択:",
        "Best (Auto)": "最高 (自動)",
        "4K (2160p)": "4K (2160p)",
        "2K (1440p)": "2K (1440p)",
        "1080p 60fps": "1080p 60fps",
        "1080p": "1080p",
        "720p 60fps": "720p 60fps",
        "720p": "720p",
        "480p": "480p",
        "360p": "360p",
        "sponsor": "スポンサー",
        "intro": "イントロ",
        "outro": "アウトロ",
        "selfpromo": "自己宣伝",
        "preview": "プレビュー",
        "filler": "フィラー",
        "interaction": "インタラクション",
        "music_offtopic": "音楽：オフトピック",
        "poi_highlight": "ハイライト",
        "chapter": "チャプター",
        "Select All": "すべて選択",
        "Deselect All": "すべて解除",
        "Invert Select": "選択反転",
        "720p 60fps": "720p 60fps",
    },
    'ko': {
        "Extract audio (--extract-audio)": "오디오만 추출 (--extract-audio)",
        "yt-dlp GUI - Video Downloader Configuration": "yt-dlp GUI - 비디오 다운로더 설정",
        "Language:": "언어:",
        "Paste Link:": "링크 붙여넣기:",
        "Stop": "정지",
        "Download stopped. Would you like to delete partially downloaded files?": "다운로드가 중지되었습니다. 일부 다운로드된 파일을 삭제하시겠습니까?",
        "Video URL(s):": "비디오 URL:",
        "Or Batch File:": "또는 배치 파일:",
        "Browse...": "찾아보기...",
        "Download": "다운로드",
        "List Formats": "형식 목록",
        "Extract Info": "정보 추출",
        "Load Config": "설정 불러오기",
        "Save Config": "설정 저장",
        "Parse Playlist": "재생목록 분석",
        "Exclude private videos": "비공개 비디오 제외",
        "Reverse order": "역순 정렬",
        "Output Console": "출력 콘솔",
        "Ready": "준비됨",
        "Clipboard is empty.": "클립보드가 비어 있습니다.",
        "Pasted link from clipboard.": "클립보드에서 링크를 붙여넣었습니다.",
        "Paste": "붙여넣기",
        "Pasted into batch text box.": "배치 텍스트 상자에 붙여넣었습니다.",
        "Paste Playlist": "재생목록 붙여넣기",
        "Batch Download": "배치 다운로드",
        "Playlist": "재생목록",
        "Batch file path:": "배치 파일 경로:",
        "Batch URLs (one per line):": "배치 URL (한 줄에 하나):",
        "Parse": "분석",
        "Parse All": "전체 분석",
        "Bulk Paste": "일괄 붙여넣기",
        "Parse Batch": "배치 분석",
        "Clear Pool": "목록 비우기",
        "General": "일반",
        "Network": "네트워크",
        "Geo-restriction": "지역 제한",
        "Video Selection": "비디오 선택",
        "Filesystem": "파일 시스템",
        "Video Format": "비디오 형식",
        "Subtitles": "자막",
        "Authentication": "인증",
        "Post-processing": "후처리",
        "Thumbnail": "썸네일",
        "Verbosity/Simulation": "로그/시뮬레이션",
        "Workarounds": "호환성 설정",
        "SponsorBlock": "광고 제거 (SponsorBlock)",
        "Extractor": "추출기",
        "Advanced": "고급",
        "Configuration file:": "설정 파일:",
        "Default search prefix:": "기본 검색 접두사:",
        "Flat playlist extraction:": "플랫 재생목록 추출:",
        "Age limit (years):": "연령 제한(세):",
        "Download archive file:": "다운로드 보관 파일:",
        "Max downloads:": "최대 다운로드 수:",
        "Proxy URL:": "프록시 URL:",
        "Socket timeout (seconds):": "소켓 타임아웃(초):",
        "Source address (bind to):": "소스 주소(바인딩):",
        "Sleep interval (seconds):": "재시도 간격(초):",
        "Max sleep interval (seconds):": "최대 재시도 간격(초):",
        "Sleep interval for requests (seconds):": "요청 간 대기 시간(초):",
        "Sleep interval for subtitles (seconds):": "자막 대기 시간(초):",
        "Rate limit (e.g., '50K' or '4.2M'):": "속도 제한 (예: '50K' 또는 '4.2M'):",
        "Throttled rate (minimum rate):": "최소 속도:",
        "Retries:": "재시도 횟수:",
        "Fragment retries:": "프래그먼트 재시도 횟수:",
        "Geo verification proxy:": "지역 인증 프록시:",
        "Geo bypass country:": "지역 우회 국가:",
        "Geo bypass IP block:": "지역 우회 IP 블록:",
        "Playlist items:": "재생목록 항목:",
        "Playlist start:": "재생목록 시작:",
        "Playlist end:": "재생목록 종료:",
        "Match title (regex):": "제목 일치(정규식):",
        "Reject title (regex):": "제목 제외(정규식):",
        "Min filesize (e.g., 50k or 1M):": "최소 파일 크기:",
        "Max filesize (e.g., 50M or 1G):": "최대 파일 크기:",
        "Date (YYYYMMDD):": "날짜 (YYYYMMDD):",
        "Date before (YYYYMMDD):": "이전 날짜 (YYYYMMDD):",
        "Date after (YYYYMMDD):": "이후 날짜 (YYYYMMDD):",
        "Min views:": "최소 조회수:",
        "Max views:": "최대 조회수:",
        "Match filter:": "일치 필터:",
        "Concurrent fragments:": "병렬 프래그먼트 수:",
        "Limit download rate:": "다운로드 속도 제한:",
        "Buffer size:": "버퍼 크기:",
        "HTTP chunk size:": "HTTP 청크 크기:",
        "External downloader:": "외부 다운로더:",
        "External downloader args:": "외부 다운로더 인수:",
        "Output template:": "출력 템플릿:",
        "Output directory:": "출력 디렉토리:",
        "Paths configuration:": "경로 설정:",
        "Load info JSON:": "정보 JSON 불러오기:",
        "Cache directory:": "캐시 디렉토리:",
        "Format selection:": "형식 선택:",
        "Format sort:": "형식 정렬:",
        "Merge output format:": "출력 형식 합치기:",
        "Video multistreams:": "비디오 멀티스트림:",
        "Audio multistreams:": "오디오 멀티스트림:",
        "Subtitle format:": "자막 형식:",
        "Subtitle languages:": "자막 언어:",
        "Username:": "사용자 이름:",
        "Password:": "비밀번호:",
        "Two-factor code:": "2단계 인증 코드:",
        "Video password:": "비디오 비밀번호:",
        "Adobe Pass MSO:": "Adobe Pass MSO 제공자:",
        "Adobe Pass username:": "Adobe Pass 사용자 이름:",
        "Adobe Pass password:": "Adobe Pass 비밀번호:",
        "Client certificate:": "클라이언트 인증서:",
        "Client certificate key:": "인증서 키:",
        "Client certificate password:": "인증서 비밀번호:",
        "Audio format:": "오디오 형식:",
        "Audio quality:": "오디오 품질:",
        "Recode video format:": "비디오 포맷 재인코딩:",
        "Remux video format:": "비디오 포맷 리먹싱:",
        "Metadata fields:": "메타데이터 필드:",
        "Parse metadata:": "메타데이터 분석:",
        "Copy to Clipboard": "클립보드에 복사",
        "Running: yt-dlp ": "실행 중: yt-dlp ",
        "Downloading...": "다운로드 중...",
        "Download completed successfully!": "다운로드가 완료되었습니다!",
        "Process exited with code ": "프로세스가 종료되었습니다. 코드: ",
        "ERROR: yt-dlp not found. Please make sure yt-dlp is installed and in your PATH.": "오류: yt-dlp를 찾을 수 없습니다.",
        "ERROR: ": "오류: ",
        "Command copied to clipboard!": "명령이 클립보드에 복사되었습니다!",
        "No URL": "URL 없음",
        "Please enter a URL or batch file to download.": "다운로드할 URL 또는 배치 파일을 입력하십시오.",
        "Please enter a URL.": "URL을 입력하십시오.",
        "Select Cache Directory": "캐시 디렉토리 선택",
        "Select Client Certificate": "클라이언트 인증서 선택",
        "Select Client Certificate Key": "인증서 키 선택",
        "Select FFmpeg Binary": "FFmpeg 실행 파일 선택",
        "Select Cookies File": "쿠키 파일 선택",
        "Select All / Deselect All": "모두 선택 / 선택 해제",
        "Quick Select Resolution:": "해상도 빠른 선택:",
        "Best (Auto)": "최고 (자동)",
        "4K (2160p)": "4K (2160p)",
        "2K (1440p)": "2K (1440p)",
        "1080p 60fps": "1080p 60fps",
        "1080p": "1080p",
        "720p 60fps": "720p 60fps",
        "720p": "720p",
        "480p": "480p",
        "360p": "360p",
        "sponsor": "스폰서",
        "intro": "인트로",
        "outro": "아웃트로",
        "selfpromo": "자가 홍보",
        "preview": "미리보기",
        "filler": "필러",
        "interaction": "상호작용",
        "music_offtopic": "음악: 주제와 상관없는 부분",
        "poi_highlight": "하이라이트",
        "chapter": "챕터",
        "Select All": "모두 선택",
        "Deselect All": "모두 해제",
        "Invert Select": "선택 반전",
        "720p 60fps": "720p 60fps",
    },
    'es': {
        "Extract audio (--extract-audio)": "Extraer audio (--extract-audio)",
        "yt-dlp GUI - Video Downloader Configuration": "yt-dlp GUI - Configuración del descargador de vídeos",
        "Language:": "Idioma:",
        "Paste Link:": "Pegar enlace:",
        "Stop": "Detener",
        "Download stopped. Would you like to delete partially downloaded files?": "Descarga detenida. ¿Desea eliminar los archivos parcialmente descargados?",
        "Video URL(s):": "URL(s) del vídeo:",
        "Or Batch File:": "O archivo por lotes:",
        "Browse...": "Explorar...",
        "Download": "Descargar",
        "List Formats": "Listar formatos",
        "Extract Info": "Extraer info",
        "Load Config": "Cargar config",
        "Save Config": "Guardar config",
        "Parse Playlist": "Analizar lista",
        "Exclude private videos": "Excluir vídeos privados",
        "Reverse order": "Orden inverso",
        "Output Console": "Consola de salida",
        "Ready": "Listo",
        "Clipboard is empty.": "El portapapeles está vacío.",
        "Pasted link from clipboard.": "Enlace pegado desde el portapapeles.",
        "Paste Playlist": "Pegar lista de reproducción",
        "Batch Download": "Descarga por lotes",
        "Playlist": "Lista de reproducción",
        "Batch file path:": "Ruta del archivo por lotes:",
        "Batch URLs (one per line):": "URLs por lotes (una por línea):",
        "Parse": "Analizar",
        "Bulk Paste": "Pegar en masa",
        "Parse Batch": "Analizar lote",
        "Clear Pool": "Limpiar lista",
        "General": "General",
        "Network": "Red",
        "Geo-restriction": "Geo-restricción",
        "Video Selection": "Selección de vídeo",
        "Filesystem": "Sistema de archivos",
        "Video Format": "Formato de vídeo",
        "Subtitles": "Subtítulos",
        "Authentication": "Autenticación",
        "Post-processing": "Post-procesamiento",
        "Thumbnail": "Miniatura",
        "Verbosity/Simulation": "Verbosidad/Simulación",
        "Workarounds": "Soluciones alternativas",
        "SponsorBlock": "Bloqueo de publicidad",
        "Extractor": "Extractor",
        "Advanced": "Avanzado",
        "Configuration file:": "Archivo de configuración:",
        "Default search prefix:": "Prefijo de búsqueda por defecto:",
        "Flat playlist extraction:": "Extracción de lista plana:",
        "Age limit (years):": "Límite de edad (años):",
        "Download archive file:": "Archivo de registro de descargas:",
        "Max downloads:": "Máximo de descargas:",
        "Proxy URL:": "URL del proxy:",
        "Socket timeout (seconds):": "Tiempo de espera del socket (seg):",
        "Source address (bind to):": "Dirección de origen (vincular a):",
        "Sleep interval (seconds):": "Intervalo de espera (seg):",
        "Max sleep interval (seconds):": "Intervalo máximo de espera (seg):",
        "Sleep interval for requests (seconds):": "Espera entre solicitudes (seg):",
        "Sleep interval for subtitless (seconds):": "Espera para subtítulos (seg):",
        "Rate limit (e.g., '50K' or '4.2M'):": "Límite de velocidad (ej. '50K' o '4.2M'):",
        "Throttled rate (minimum rate):": "Velocidad mínima:",
        "Retries:": "Reintentos:",
        "Fragment retries:": "Reintentos de fragmento:",
        "Geo verification proxy:": "Proxy de verificación geográfica:",
        "Geo bypass country:": "País de bypass geográfico:",
        "Geo bypass IP block:": "Bloque IP de bypass geográfico:",
        "Playlist items:": "Elementos de la lista:",
        "Playlist start:": "Inicio de la lista:",
        "Playlist end:": "Fin de la lista:",
        "Match title (regex):": "Coincidir título (regex):",
        "Reject title (regex):": "Excluir título (regex):",
        "Min filesize (e.g., 50k or 1M):": "Tamaño mín. (ej. 50k o 1M):",
        "Max filesize (e.g., 50M or 1G):": "Tamaño máx. (ej. 50M o 1G):",
        "Date (YYYYMMDD):": "Fecha (AAAAMMDD):",
        "Date before (YYYYMMDD):": "Fecha anterior a (AAAAMMDD):",
        "Date after (YYYYMMDD):": "Fecha posterior a (AAAAMMDD):",
        "Min views:": "Mínimo de vistas:",
        "Max views:": "Máximo de vistas:",
        "Match filter:": "Filtro de coincidencia:",
        "Concurrent fragments:": "Fragmentos concurrentes:",
        "Limit download rate:": "Limitar velocidad de descarga:",
        "Buffer size:": "Tamaño del búfer:",
        "HTTP chunk size:": "Tamaño de bloque HTTP:",
        "External downloader:": "Descargador externo:",
        "External downloader args:": "Argumentos del descargador externo:",
        "Output template:": "Plantilla de salida:",
        "Output directory:": "Directorio de salida:",
        "Paths configuration:": "Configuración de rutas:",
        "Load info JSON:": "Cargar info JSON:",
        "Cache directory:": "Directorio de caché:",
        "Format selection:": "Selección de formato:",
        "Format sort:": "Orden de formato:",
        "Merge output format:": "Formato de mezcla:",
        "Video multistreams:": "Flujos de vídeo múltiples:",
        "Audio multistreams:": "Flujos de audio múltiples:",
        "Subtitle format:": "Formato de subtítulos:",
        "Subtitle languages:": "Idiomas de subtítulos:",
        "Username:": "Usuario:",
        "Password:": "Contraseña:",
        "Two-factor code:": "Código 2FA:",
        "Video password:": "Contraseña del vídeo:",
        "Adobe Pass MSO:": "Proveedor Adobe Pass MSO:",
        "Adobe Pass username:": "Usuario Adobe Pass:",
        "Adobe Pass password:": "Contraseña Adobe Pass:",
        "Client certificate:": "Certificado de cliente:",
        "Client certificate key:": "Clave del certificado:",
        "Client certificate password:": "Contraseña del certificado:",
        "Audio format:": "Formato de audio:",
        "Audio quality:": "Calidad de audio:",
        "Recode video format:": "Recodificar formato de vídeo:",
        "Remux video format:": "Remezclar formato de vídeo:",
        "Metadata fields:": "Campos de metadatos:",
        "Parse metadata:": "Analizar metadatos:",
        "FFmpeg location:": "Ubicación de FFmpeg:",
        "Post-processor args:": "Argumentos del post-procesador:",
        "Convert thumbnails format:": "Convertir miniaturas a:",
        "Progress template:": "Plantilla de progreso:",
        "Metadata language:": "Idioma de metadatos:",
        "Default (Auto)": "Por defecto (Auto)",
        "Encoding:": "Codificación:",
        "User agent:": "User-Agent:",
        "Referer:": "Referer:",
        "Add header:": "Añadir cabecera:",
        "Sleep before requests:": "Espera antes de solicitudes:",
        "SponsorBlock categories to remove:": "Categorías de SponsorBlock para eliminar:",
        "SponsorBlock categories to mark:": "Categorías de SponsorBlock para marcar:",
        "SponsorBlock chapter title:": "Título de capítulo de SponsorBlock:",
        "SponsorBlock API URL:": "URL de la API de SponsorBlock:",
        "Extractor arguments:": "Argumentos del extractor:",
        "Extractor retries:": "Reintentos del extractor:",
        "Cookies from browser:": "Cookies del navegador:",
        "Cookies file:": "Archivo de cookies:",
        "Raw command-line arguments:": "Argumentos de línea de comandos puros:",
        "Generated command:": "Comando generado:",
        "Generate Command": "Generar comando",
        "Copy to Clipboard": "Copiar al portapapeles",
        "Running: yt-dlp ": "Ejecutando: yt-dlp ",
        "Downloading...": "Descargando...",
        "Download completed successfully!": "¡Descarga completada!",
        "Process exited with code ": "Proceso finalizado con código: ",
        "ERROR: yt-dlp not found. Please make sure yt-dlp is installed and in your PATH.": "ERROR: yt-dlp no encontrado.",
        "ERROR: ": "ERROR: ",
        "Command copied to clipboard!": "¡Comando copiado!",
        "No URL": "Sin URL",
        "Please enter a URL or batch file to download.": "Introduzca una URL o archivo por lotes.",
        "Please enter a URL.": "Por favor, introduzca una URL.",
        "Error": "Error",
        "Success": "Éxito",
        "Failed to save configuration: ": "Error al guardar configuración: ",
        "Failed to load configuration: ": "Error al cargar configuración: ",
        "Configuration loaded successfully!": "¡Configuración cargada!",
        "Configuration saved successfully!": "¡Configuración guardada!",
        "Load Configuration": "Cargar configuración",
        "Save Configuration": "Guardar configuración",
        "Select Batch File": "Seleccionar archivo por lotes",
        "Select Config File": "Seleccionar configuración",
        "Select Archive File": "Seleccionar archivo de registro",
        "Select Output Directory": "Seleccionar directorio de salida",
        "Select Info JSON": "Seleccionar info JSON",
        "Select Cache Directory": "Seleccionar directorio de caché",
        "Select Client Certificate": "Seleccionar certificado",
        "Select Client Certificate Key": "Seleccionar clave de certificado",
        "Select FFmpeg Binary": "Seleccionar FFmpeg",
        "Select Cookies File": "Seleccionar cookies",
        "Test mode - do not download (--test)": "Modo prueba, no descargar (--test)",
        "Prefer native HLS downloader (--hls-prefer-native)": "Preferir descargador HLS nativo (--hls-prefer-native)",
        "Prefer ffmpeg for HLS (--hls-prefer-ffmpeg)": "Preferir ffmpeg para HLS (--hls-prefer-ffmpeg)",
        "Use MPEG-TS container for HLS (--hls-use-mpegts)": "Usar MPEG-TS para HLS (--hls-use-mpegts)",
        "Restrict filenames to ASCII (--restrict-filenames)": "Restringir nombres a ASCII (--restrict-filenames)",
        "Allow Unicode in filenames (--no-restrict-filenames)": "Permitir Unicode en nombres (--no-restrict-filenames)",
        "Create playlist subfolder for playlist downloads": "Crear subcarpeta para listas",
        "Force Windows-compatible filenames (--windows-filenames)": "Forzar nombres compatibles con Windows (--windows-filenames)",
        "Do not overwrite files (--no-overwrites)": "No sobrescribir archivos (--no-overwrites)",
        "Force overwrite files (--force-overwrites)": "Forzar sobrescritura (--force-overwrites)",
        "Continue partially downloaded files (--continue)": "Continuar descargas parciales (--continue)",
        "Do not continue downloads (--no-continue)": "No continuar descargas (--no-continue)",
        "Do not use .part files (--no-part)": "No usar archivos .part (--no-part)",
        "Do not use Last-modified header (--no-mtime)": "No usar cabecera Last-modified (--no-mtime)",
        "Write description to .description file (--write-description)": "Escribir descripción a archivo (--write-description)",
        "Write metadata to .info.json file (--write-info-json)": "Escribir metadatos a .json (--write-info-json)",
        "Write annotations to .annotations.xml (--write-annotations)": "Escribir anotaciones (--write-annotations)",
        "Write comments to .comments.json (--write-comments)": "Escribir comentarios (--write-comments)",
        "Disable filesystem caching (--no-cache-dir)": "Desactivar caché de archivos (--no-cache-dir)",
        "Delete cache directory contents (--rm-cache-dir)": "Borrar contenido de caché (--rm-cache-dir)",
        "Prefer free formats (--prefer-free-formats)": "Preferir formatos libres (--prefer-free-formats)",
        "Check available formats (--check-formats)": "Comprobar formatos disponibles (--check-formats)",
        "Write subtitle file (--write-subs)": "Escribir archivo de subtítulos (--write-subs)",
        "Write automatic subtitle file (--write-auto-subs)": "Escribir subtítulos automáticos (--write-auto-subs)",
        "List available subtitles (--list-subs)": "Listar subtítulos disponibles (--list-subs)",
        "Embed subtitles (--embed-subs)": "Incrustar subtítulos (--embed-subs)",
        "Do not embed subtitles (--no-embed-subs)": "No incrustar subtítulos (--no-embed-subs)",
        "Embed thumbnail (--embed-thumbnail)": "Incrustar miniatura (--embed-thumbnail)",
        "Do not embed thumbnail (--no-embed-thumbnail)": "No incrustar miniatura (--no-embed-thumbnail)",
        "Use .netrc authentication (--netrc)": "Usar autenticación .netrc (--netrc)",
        "Extract audio (-x, --extract-audio)": "Extraer audio (-x, --extract-audio)",
        "Keep video file after conversion (--keep-video)": "Mantener vídeo tras conversión (--keep-video)",
        "Do not keep video file (--no-keep-video)": "No mantener vídeo original (--no-keep-video)",
        "Embed metadata (--embed-metadata)": "Incrustar metadatos (--embed-metadata)",
        "Embed chapter markers (--embed-chapters)": "Incrustar marcadores de capítulo (--embed-chapters)",
        "Embed info.json (--embed-info-json)": "Incrustar info.json (--embed-info-json)",
        "Add metadata to file (--add-metadata)": "Añadir metadatos al archivo (--add-metadata)",
        "Write thumbnail image (--write-thumbnail)": "Escribir miniatura a disco (--write-thumbnail)",
        "Write all thumbnail formats (--write-all-thumbnails)": "Escribir todos los formatos de miniatura (--write-all-thumbnails)",
        "List available thumbnails (--list-thumbnails)": "Listar miniaturas disponibles (--list-thumbnails)",
        "Quiet mode (-q, --quiet)": "Modo silencioso (-q, --quiet)",
        "No warnings (--no-warnings)": "Sin avisos (--no-warnings)",
        "Verbose output (-v, --verbose)": "Salida detallada (-v, --verbose)",
        "Simulate, do not download (-s, --simulate)": "Simular, no descargar (-s, --simulate)",
        "Skip download (--skip-download)": "Saltar descarga (--skip-download)",
        "Get title (--get-title)": "Obtener título (--get-title)",
        "Get ID (--get-id)": "Obtener ID (--get-id)",
        "Get URL (--get-url)": "Obtener URL (--get-url)",
        "Get thumbnail URL (--get-thumbnail)": "Obtener URL de miniatura (--get-thumbnail)",
        "Get description (--get-description)": "Obtener descripción (--get-description)",
        "Get duration (--get-duration)": "Obtener duración (--get-duration)",
        "Get filename (--get-filename)": "Obtener nombre de archivo (--get-filename)",
        "Get format (--get-format)": "Obtener formato (--get-format)",
        "Dump JSON info (--dump-json)": "Volcar info JSON (--dump-json)",
        "Dump single JSON (--dump-single-json)": "Volcar JSON único (--dump-single-json)",
        "Print JSON info (--print-json)": "Imprimir info JSON (--print-json)",
        "Show progress (--progress)": "Mostrar progreso (--progress)",
        "Hide progress (--no-progress)": "Ocultar progreso (--no-progress)",
        "Display progress in console title (--console-title)": "Mostrar progreso en título de consola (--console-title)",
        "Skip SSL certificate validation (--no-check-certificate)": "Saltar validación de certificado SSL (--no-check-certificate)",
        "Prefer insecure connections (--prefer-insecure)": "Preferir conexiones inseguras (--prefer-insecure)",
        "Bidirectional text workaround (--bidi-workaround)": "Arreglo para texto bidireccional (--bidi-workaround)",
        "Use legacy server connect (--legacy-server-connect)": "Usar conexión de servidor legada (--legacy-server-connect)",
        "Mark SponsorBlock chapters (--sponsorblock-mark)": "Marcar capítulos de bloqueo publicitario (--sponsorblock-mark)",
        "Remove SponsorBlock segments (--sponsorblock-remove)": "Eliminar segmentos de bloqueo publicitario (--sponsorblock-remove)",
        "Disable SponsorBlock (--no-sponsorblock)": "Desactivar bloqueo publicitario (--no-sponsorblock)",
        "Allow dynamic MPD manifests (--allow-dynamic-mpd)": "Autorizar manifestaciones MPD dinámicas (--allow-dynamic-mpd)",
        "Ignore dynamic MPD manifests (--ignore-dynamic-mpd)": "Ignorar manifestaciones MPD dinámicas (--ignore-dynamic-mpd)",
        "Split HLS segments on discontinuity (--hls-split-discontinuity)": "Dividir segmentos HLS en discontinuidades (--hls-split-discontinuity)",
        "Select All / Deselect All": "Seleccionar todo / Deseleccionar todo",
        "Quick Select Resolution:": "Seleccion rápida de resolución:",
        "Best (Auto)": "Mejor (Auto)",
        "4K (2160p)": "4K (2160p)",
        "2K (1440p)": "2K (1440p)",
        "1080p 60fps": "1080p 60fps",
        "1080p": "1080p",
        "720p": "720p",
        "480p": "480p",
        "360p": "360p",
        "720p 60fps": "720p 60fps",
        "sponsor": "Publicidad del patrocinador",
        "intro": "Introducción",
        "outro": "Final",
        "selfpromo": "Autopromoción",
        "preview": "Avance",
        "filler": "Relleno",
        "interaction": "Interacción",
        "music_offtopic": "Música: Fuera de tema",
        "poi_highlight": "Punto de interés",
        "chapter": "Capítulo",
        "Select All": "Seleccionar todo",
        "Deselect All": "Deseleccionar todo",
        "Invert Select": "Invertir selección",
    },
    'fr': {
        "Extract audio (--extract-audio)": "Extraire l'audio (--extract-audio)",
        "yt-dlp GUI - Video Downloader Configuration": "yt-dlp GUI - Configuration du téléchargeur vidéo",
        "Language:": "Langue :",
        "Paste Link:": "Coller le lien :",
        "Stop": "Arrêter",
        "Download stopped. Would you like to delete partially downloaded files?": "Téléchargement arrêté. Voulez-vous supprimer les fichiers partiellement téléchargés ?",
        "Video URL(s):": "URL du vidéo :",
        "Or Batch File:": "Ou fichier par lots :",
        "Browse...": "Parcourir...",
        "Download": "Télécharger",
        "List Formats": "Lister les formats",
        "Extract Info": "Extraire les infos",
        "Load Config": "Charger la config",
        "Save Config": "Sauvegarder la config",
        "Parse Playlist": "Analyser la liste",
        "Exclude private videos": "Exclure les vidéos privées",
        "Reverse order": "Ordre inverse",
        "Output Console": "Console de sortie",
        "Ready": "Prêt",
        "Clipboard is empty.": "Le presse-papiers est vide.",
        "Pasted link from clipboard.": "Lien collé depuis le presse-papiers.",
        "Paste Playlist": "Coller la liste de lecture",
        "General": "Général",
        "Network": "Réseau",
        "Geo-restriction": "Géo-restriction",
        "Video Selection": "Sélection Vidéo",
        "Filesystem": "Système de fichiers",
        "Video Format": "Format Vidéo",
        "Subtitles": "Sous-titres",
        "Authentication": "Authentification",
        "Post-processing": "Post-traitement",
        "Thumbnail": "Miniature",
        "Verbosity/Simulation": "Verbosité/Simulation",
        "Workarounds": "Contournements",
        "SponsorBlock": "Blocage Pub",
        "Extractor": "Extracteur",
        "Advanced": "Avancé",
        "Configuration file:": "Fichier de configuration :",
        "Default search prefix:": "Préfixe de recherche par défaut :",
        "Flat playlist extraction:": "Extraction de liste plate :",
        "Age limit (years):": "Limite d'âge (ans) :",
        "Download archive file:": "Fichier d'archive de téléchargement :",
        "Max downloads:": "Nombre max de téléchargements :",
        "Proxy URL:": "URL du proxy :",
        "Socket timeout (seconds):": "Délai d'attente du socket (sec) :",
        "Source address (bind to):": "Adresse source (lier à) :",
        "Sleep interval (seconds):": "Intervalle de sommeil (sec) :",
        "Max sleep interval (seconds):": "Intervalle de sommeil max (sec) :",
        "Sleep interval for requests (seconds):": "Sommeil entre requêtes (sec) :",
        "Sleep interval for subtitles (seconds):": "Sommeil pour les sous-titres (sec) :",
        "Rate limit (e.g., '50K' or '4.2M'):": "Limite de débit (ex: '50K' ou '4.2M') :",
        "Throttled rate (minimum rate):": "Débit minimum :",
        "Retries:": "Tentatives :",
        "Fragment retries:": "Tentatives de fragment :",
        "Geo verification proxy:": "Proxy de vérification géo :",
        "Geo bypass country:": "Pays de contournement géo :",
        "Geo bypass IP block:": "Bloc IP de contournement géo :",
        "Playlist items:": "Éléments de la liste :",
        "Playlist start:": "Début de la liste :",
        "Playlist end:": "Fin de la liste :",
        "Match title (regex):": "Titre correspondant (regex) :",
        "Reject title (regex) :": "Titre rejeté (regex) :",
        "Min filesize (e.g., 50k or 1M) :": "Taille de fichier min (ex: 50k ou 1M) :",
        "Max filesize (e.g., 50M or 1G) :": "Taille de fichier max (ex: 50M ou 1G) :",
        "Date (YYYYMMDD) :": "Date (AAAAMMDD) :",
        "Date before (YYYYMMDD) :": "Date avant (AAAAMMDD) :",
        "Date after (YYYYMMDD) :": "Date après (AAAAMMDD) :",
        "Min views :": "Vues min :",
        "Max views :": "Vues max :",
        "Match filter :": "Filtre de correspondance :",
        "Concurrent fragments :": "Fragments simultanés :",
        "Limit download rate :": "Limiter le débit de téléchargement :",
        "Buffer size :": "Taille du tampon :",
        "HTTP chunk size :": "Taille du bloc HTTP :",
        "External downloader :": "Téléchargeur externe :",
        "External downloader args :": "Arguments du téléchargeur externe :",
        "Output template :": "Modèle de sortie :",
        "Output directory :": "Répertoire de sortie :",
        "Paths configuration :": "Configuration des chemins :",
        "Load info JSON :": "Charger les infos JSON :",
        "Cache directory :": "Répertoire de cache :",
        "Format selection :": "Sélection du format :",
        "Format sort :": "Tri du format :",
        "Merge output format :": "Format de fusion de sortie :",
        "Video multistreams :": "Flux vidéo multiples :",
        "Audio multistreams :": "Flux audio multiples :",
        "Subtitle format :": "Format des sous-titres :",
        "Subtitle languages :": "Langues des sous-titres :",
        "Username :": "Nom d'utilisateur :",
        "Password :": "Mot de passe :",
        "Two-factor code :": "Code 2FA :",
        "Video password :": "Mot de passe vidéo :",
        "Adobe Pass MSO :": "Fournisseur Adobe Pass MSO :",
        "Adobe Pass username :": "Utilisateur Adobe Pass :",
        "Adobe Pass password :": "Mot de passe Adobe Pass :",
        "Client certificate :": "Certificat client :",
        "Client certificate key :": "Clé du certificat client :",
        "Client certificate password :": "Mot de passe du certificat :",
        "Audio format :": "Format audio :",
        "Audio quality :": "Qualité audio :",
        "Recode video format :": "Recoder le format vidéo :",
        "Remux video format :": "Remuxer le format vidéo :",
        "Metadata fields :": "Champs de métadonnées :",
        "Parse metadata :": "Analyser les métadonnées :",
        "FFmpeg location :": "Emplacement de FFmpeg :",
        "Post-processor args :": "Arguments du post-processeur :",
        "Convert thumbnails format :": "Convertir les miniatures vers :",
        "Progress template :": "Modèle de progression :",
        "Metadata language :": "Langue des métadonnées :",
        "Default (Auto)": "Par défaut (Auto)",
        "Encoding :": "Encodage :",
        "User agent :": "User-Agent :",
        "Referer :": "Referer :",
        "Add header :": "Ajouter un en-tête :",
        "Sleep before requests :": "Sommeil avant les requêtes :",
        "SponsorBlock categories to remove:": "Catégories de blocage pub à supprimer :",
        "SponsorBlock categories to mark:": "Catégories de blocage pub à marquer :",
        "SponsorBlock chapter title:": "Titre du chapitre de blocage pub :",
        "SponsorBlock API URL:": "URL de l'API de blocage pub :",
        "Extractor arguments :": "Arguments de l'extracteur :",
        "Extractor retries :": "Tentatives de l'extracteur :",
        "Cookies from browser :": "Cookies du navigateur :",
        "Cookies file :": "Fichier de cookies :",
        "Raw command-line arguments :": "Arguments de ligne de commande bruts :",
        "Generated command :": "Commande générée :",
        "Generate Command": "Générer la commande",
        "Copy to Clipboard": "Copier dans le presse-papiers",
        "Running: yt-dlp ": "Exécution : yt-dlp ",
        "Downloading...": "Téléchargement...",
        "Download completed successfully!": "Téléchargement réussi !",
        "Process exited with code ": "Le processus s'est terminé avec le code : ",
        "ERROR: yt-dlp not found. Please make sure yt-dlp is installed and in your PATH.": "ERREUR : yt-dlp introuvable.",
        "ERROR: ": "ERREUR : ",
        "Command copied to clipboard!": "Commande copiée !",
        "No URL": "Pas d'URL",
        "Please enter a URL or batch file to download.": "Veuillez entrer une URL ou un fichier par lots.",
        "Please enter a URL.": "Veuillez entrer une URL.",
        "Error": "Erreur",
        "Success": "Succès",
        "Failed to save configuration: ": "Échec de sauvegarde de config : ",
        "Failed to load configuration: ": "Échec de chargement de config : ",
        "Configuration loaded successfully!": "Configuration chargée !",
        "Configuration saved successfully!": "Configuration enregistrée !",
        "Load Configuration": "Charger la configuration",
        "Save Configuration": "Sauvegarder la configuration",
        "Select Batch File": "Sélectionner le fichier par lots",
        "Select Config File": "Sélectionner la configuration",
        "Select Archive File": "Sélectionner le fichier d'archive",
        "Select Output Directory": "Sélectionner le dossier de sortie",
        "Select Info JSON": "Sélectionner le JSON d'info",
        "Select Cache Directory": "Sélectionner le dossier de cache",
        "Select Client Certificate": "Sélectionner le certificat",
        "Select Client Certificate Key": "Sélectionner la clé de certificat",
        "Select FFmpeg Binary": "Sélectionner FFmpeg",
        "Select Cookies File": "Sélectionner les cookies",
        "Text Files": "Fichiers texte",
        "All Files": "Tous les fichiers",
        "Config Files": "Fichiers de configuration",
        "JSON Files": "Fichiers JSON",
        "PEM Files": "Fichiers PEM",
        "Key Files": "Fichiers de clé",
        "Executable Files": "Fichiers exécutables",
        ")": "(séparé par des virgules, ex: 'en,fr,de')",
        "(ISO 3166-2 code)": "(code ISO 3166-2)",
        "(CIDR notation)": "(notation CIDR)",
        "(e.g., 50K or 4.2M)": "(ex: 50K ou 4.2M)",
        "(comma-separated)": "(séparé par des virgules)",
        "(key:val[,val] format)": "(format clé:val)",
        "(One argument per line or space-separated)": "(Un argument par ligne ou séparé par des espaces)",
        "(0-10, 0 = best)": "(0-10, 0 = le meilleur)",
        "Ignore errors (--ignore-errors)": "Ignorer les erreurs (--ignore-errors)",
        "Ignore warnings (--no-warnings)": "Ignorer les avertissements (--no-warnings)",
        "Abort on error (--abort-on-error)": "Abandonner sur erreur (--abort-on-error)",
        "Download only video, not playlist (--no-playlist)": "Vidéo seule, pas de liste (--no-playlist)",
        "Download playlist (--yes-playlist)": "Télécharger la liste (--yes-playlist)",
        "Include private/unavailable videos in YouTube playlists": "Inclure vidéos privées/non dispo",
        "Mark videos as watched (--mark-watched)": "Marquer comme vu (--mark-watched)",
        "Do not mark videos as watched (--no-mark-watched)": "Ne pas marquer comme vu (--no-mark-watched)",
        "Force IPv4 (--force-ipv4)": "Forcer IPv4 (--force-ipv4)",
        "Force IPv6 (--force-ipv6)": "Forcer IPv6 (--force-ipv6)",
        "Enable file:// URLs (--enable-file-urls)": "Activer les URL file:// (--enable-file-urls)",
        "Bypass geo restriction (--geo-bypass)": "Contourner géo-restriction (--geo-bypass)",
        "Do not bypass geo restriction (--no-geo-bypass)": "Ne pas contourner géo (--no-geo-bypass)",
        "Break on existing (--break-on-existing)": "Arrêter si existe déjà (--break-on-existing)",
        "Break on reject (--break-on-reject)": "Arrêter si rejeté (--break-on-reject)",
        "No break on existing (--no-break-on-existing)": "Ne pas arrêter si existe déjà (--no-break-on-existing)",
        "Do not resize buffer (--no-resize-buffer)": "Ne pas redimensionner tampon (--no-resize-buffer)",
        "Test mode - do not download (--test)": "Mode test, ne pas télécharger (--test)",
        "Prefer native HLS downloader (--hls-prefer-native)": "Préférer téléchargeur HLS natif (--hls-prefer-native)",
        "Prefer ffmpeg for HLS (--hls-prefer-ffmpeg)": "Préferer ffmpeg pour HLS (--hls-prefer-ffmpeg)",
        "Use MPEG-TS container for HLS (--hls-use-mpegts)": "Utiliser MPEG-TS pour HLS (--hls-use-mpegts)",
        "Restrict filenames to ASCII (--restrict-filenames)": "Noms de fichier ASCII uniquement (--restrict-filenames)",
        "Allow Unicode in filenames (--no-restrict-filenames)": "Autoriser Unicode dans les noms (--no-restrict-filenames)",
        "Create playlist subfolder for playlist downloads": "Créer sous-dossier pour les listes",
        "Force Windows-compatible filenames (--windows-filenames)": "Forcer noms fichiers Windows (--windows-filenames)",
        "Do not overwrite files (--no-overwrites)": "Ne pas écraser les fichiers (--no-overwrites)",
        "Force overwrite files (--force-overwrites)": "Forcer l'écrasement (--force-overwrites)",
        "Continue partially downloaded files (--continue)": "Reprendre téléchargements partiels (--continue)",
        "Do not continue downloads (--no-continue)": "Ne pas reprendre téléchargements (--no-continue)",
        "Do not use .part files (--no-part)": "Ne pas utiliser fichiers .part (--no-part)",
        "Do not use Last-modified header (--no-mtime)": "Ne pas utiliser l'en-tête Last-modified (--no-mtime)",
        "Write description to .description file (--write-description)": "Écrire description dans fichier (--write-description)",
        "Write metadata to .info.json file (--write-info-json)": "Écrire métadonnées dans .json (--write-info-json)",
        "Write annotations to .annotations.xml (--write-annotations)": "Écrire annotations (--write-annotations)",
        "Write comments to .comments.json (--write-comments)": "Écrire commentaires (--write-comments)",
        "Disable filesystem caching (--no-cache-dir)": "Désactiver cache système (--no-cache-dir)",
        "Delete cache directory contents (--rm-cache-dir)": "Vider le dossier de cache (--rm-cache-dir)",
        "Prefer free formats (--prefer-free-formats)": "Préférer formats libres (--prefer-free-formats)",
        "Check available formats (--check-formats)": "Vérifier formats dispos (--check-formats)",
        "Write subtitle file (--write-subs)": "Écrire fichier sous-titres (--write-subs)",
        "Write automatic subtitle file (--write-auto-subs)": "Écrire sous-titres auto (--write-auto-subs)",
        "List available subtitles (--list-subs)": "Lister sous-titres dispos (--list-subs)",
        "Embed subtitles (--embed-subs)": "Incruster sous-titres (--embed-subs)",
        "Do not embed subtitles (--no-embed-subs)": "Ne pas incruster sous-titres (--no-embed-subs)",
        "Embed thumbnail (--embed-thumbnail)": "Incruster miniature (--embed-thumbnail)",
        "Do not embed thumbnail (--no-embed-thumbnail)": "Ne pas incruster miniature (--no-embed-thumbnail)",
        "Use .netrc authentication (--netrc)": "Utiliser authentification .netrc (--netrc)",
        "Extract audio (-x, --extract-audio)": "Extraire l'audio (-x, --extract-audio)",
        "Keep video file after conversion (--keep-video)": "Garder la vidéo après conversion (--keep-video)",
        "Do not keep video file (--no-keep-video)": "Ne pas garder la vidéo convertie (--no-keep-video)",
        "Embed metadata (--embed-metadata)": "Incruster métadonnées (--embed-metadata)",
        "Embed chapter markers (--embed-chapters)": "Incruster marqueurs chapitre (--embed-chapters)",
        "Embed info.json (--embed-info-json)": "Incruster info.json (--embed-info-json)",
        "Add metadata to file (--add-metadata)": "Ajouter métadonnées au fichier (--add-metadata)",
        "Write thumbnail image (--write-thumbnail)": "Écrire miniature sur disque (--write-thumbnail)",
        "Write all thumbnail formats (--write-all-thumbnails)": "Écrire tous les formats miniature (--write-all-thumbnails)",
        "List available thumbnails (--list-thumbnails)": "Lister miniatures dispos (--list-thumbnails)",
        "Quiet mode (-q, --quiet)": "Mode discret (-q, --quiet)",
        "No warnings (--no-warnings)": "Pas d'avertissements (--no-warnings)",
        "Verbose output (-v, --verbose)": "Sortie détaillée (-v, --verbose)",
        "Simulate, do not download (-s, --simulate)": "Simuler, ne pas télécharger (-s, --simulate)",
        "Skip download (--skip-download)": "Sauter le téléchargement (--skip-download)",
        "Get title (--get-title)": "Obtenir titre (--get-title)",
        "Get ID (--get-id)": "Obtenir ID (--get-id)",
        "Get URL (--get-url)": "Obtenir URL (--get-url)",
        "Get thumbnail URL (--get-thumbnail)": "Obtenir URL miniature (--get-thumbnail)",
        "Get description (--get-description)": "Obtenir description (--get-description)",
        "Get duration (--get-duration)": "Obtenir durée (--get-duration)",
        "Get filename (--get-filename)": "Obtenir nom fichier (--get-filename)",
        "Get format (--get-format)": "Obtenir format (--get-format)",
        "Dump JSON info (--dump-json)": "Dump info JSON (--dump-json)",
        "Dump single JSON (--dump-single-json)": "Dump single JSON (--dump-single-json)",
        "Print JSON info (--print-json)": "Imprimer info JSON (--print-json)",
        "Show progress (--progress)": "Afficher la progression (--progress)",
        "Hide progress (--no-progress)": "Masquer la progression (--no-progress)",
        "Display progress in console title (--console-title)": "Progression en titre de console (--console-title)",
        "Skip SSL certificate validation (--no-check-certificate)": "Sauter validation SSL (--no-check-certificate)",
        "Prefer insecure connections (--prefer-insecure)": "Préférer connexions non sécurisées (--prefer-insecure)",
        "Bidirectional text workaround (--bidi-workaround)": "Arreglo de texte bidirectionnel (--bidi-workaround)",
        "Use legacy server connect (--legacy-server-connect)": "Utiliser connexion serveur héritée (--legacy-server-connect)",
        "Mark SponsorBlock chapters (--sponsorblock-mark)": "Marquer les chapitres de blocage pub (--sponsorblock-mark)",
        "Remove SponsorBlock segments (--sponsorblock-remove)": "Supprimer les segments de blocage pub (--sponsorblock-remove)",
        "Disable SponsorBlock (--no-sponsorblock)": "Désactiver le blocage pub (--no-sponsorblock)",
        "360p": "360p",
        "720p 60fps": "720p 60fps",
        "sponsor": "Publicité sponsorisée",
        "intro": "Introduction",
        "outro": "Fin",
        "selfpromo": "Auto-promotion",
        "preview": "Aperçu",
        "filler": "Remplissage",
        "interaction": "Interaction",
        "music_offtopic": "Musique : Hors sujet",
        "poi_highlight": "Moment fort",
        "chapter": "Chapitre",
        "Select All": "Tout sélectionner",
        "Deselect All": "Tout désélectionner",
        "Invert Select": "Inverser la sélection",
        "Allow dynamic MPD manifests (--allow-dynamic-mpd)": "Autoriser les manifestes MPD dynamiques (--allow-dynamic-mpd)",
        "Ignore dynamic MPD manifests (--ignore-dynamic-mpd)": "Ignorer les manifestes MPD dynamiques (--ignore-dynamic-mpd)",
    },
    'de': {
        'Language:': 'Sprache:',
        'Paste Link:': 'Link einfügen:',
        'Stop': 'Stopp',
        'Download stopped. Would you like to delete partially downloaded files?': 'Download gestoppt. Teilweise heruntergeladene Dateien löschen?',
        'Video URL(s):': 'Video-URLs:',
        'Or Batch File:': 'Oder Batch-Datei:',
        'Browse...': 'Durchsuchen...',
        'Download': 'Herunterladen',
        'List Formats': 'Formate auflisten',
        'Extract Info': 'Info extrahieren',
        'Load Config': 'Konfig laden',
        'Save Config': 'Konfig speichern',
        'Parse Playlist': 'Wiedergabeliste parsen',
        'Exclude private videos': 'Private Videos ausschließen',
        'Reverse order': 'Umgekehrte Reihenfolge',
        'Output Console': 'Ausgabekonsole',
        'Ready': 'Bereit',
        'Clipboard is empty.': 'Zwischenablage ist leer.',
        'Pasted link from clipboard.': 'Link aus Zwischenablage eingefügt.',
        'Paste Playlist': 'Playlist einfügen',
        'Batch Download': 'Stapel-Download',
        'Playlist': 'Wiedergabeliste',
        'Batch file path:': 'Batch-Dateipfad:',
        'Batch URLs (one per line):': 'Batch-URLs (eine pro Zeile):',
        'Parse': 'Parsen',
        'Bulk Paste': 'Massen-Einfügen',
        'Parse Batch': 'Stapel parsen',
        'Clear Pool': 'Liste leeren',
        "General": "Allgemein",
        "Network": "Netzwerk",
        "Geo-restriction": "Geo-Beschränkung",
        "Video Selection": "Video-Auswahl",
        "Filesystem": "Dateisystem",
        "Video Format": "Videoformat",
        "Subtitles": "Untertitel",
        "Authentication": "Authentifizierung",
        "Post-processing": "Nachbearbeitung",
        "Thumbnail": "Miniaturbild",
        "Verbosity/Simulation": "Ausführlichkeit/Simulation",
        "Workarounds": "Workarounds",
        "SponsorBlock": "Werbeblocker",
        "Extractor": "Extraktor",
        "Advanced": "Erweitert",
        "Configuration file:": "Konfigurationsdatei:",
        "Default search prefix:": "Standard-Suchpräfix:",
        "Flat playlist extraction:": "Einfache Playlist-Extraktion:",
        "Age limit (years):": "Altersbeschränkung (Jahre):",
        "Download archive file:": "Archivdatei für Downloads:",
        "Max downloads:": "Maximale Downloads:",
        "Proxy URL:": "Proxy-URL:",
        "Socket timeout (seconds):": "Socket-Timeout (Sekunden):",
        "Source address (bind to):": "Quelladresse (binden an):",
        "Sleep interval (seconds):": "Schlafintervall (Sekunden):",
        "Max sleep interval (seconds):": "Max. Schlafintervall (Sekunden):",
        "Sleep interval for requests (seconds):": "Schlafintervall für Anfragen (Sekunden):",
        "Sleep interval for subtitles (seconds):": "Schlafintervall für Untertitel (Sekunden):",
        "Rate limit (e.g., '50K' or '4.2M'):": "Geschwindigkeitsbegrenzung (z.B. '50K' oder '4.2M'):",
        "Throttled rate (minimum rate):": "Gedrosselte Rate (Mindestrate):",
        "Retries:": "Wiederholungsversuche:",
        "Fragment retries:": "Fragment-Wiederholungsversuche:",
        "Geo verification proxy:": "Geo-Verifizierungs-Proxy:",
        "Geo bypass country:": "Geo-Bypass-Land:",
        "Geo bypass IP block:": "Geo-Bypass-IP-Block:",
        "Playlist items:": "Playlist-Elemente:",
        "Playlist start:": "Playlist-Start:",
        "Playlist end:": "Playlist-Ende:",
        "Match title (regex):": "Titel abgleichen (Regex):",
        "Reject title (regex):": "Titel ablehnen (Regex):",
        "Min filesize (e.g., 50k or 1M):": "Min. Dateigröße (z.B. 50k oder 1M):",
        "Max filesize (e.g., 50M or 1G):": "Max. Dateigröße (z.B. 50M oder 1G):",
        "Date (YYYYMMDD):": "Datum (JJJJMMTT):",
        "Date before (YYYYMMDD):": "Datum vor (JJJJMMTT):",
        "Date after (YYYYMMDD):": "Datum nach (JJJJMMTT):",
        "Min views:": "Min. Aufrufe:",
        "Max views:": "Max. Aufrufe:",
        "Match filter:": "Abgleich-Filter:",
        "Concurrent fragments:": "Gleichzeitige Fragmente:",
        "Limit download rate:": "Download-Rate begrenzen:",
        "Buffer size:": "Puffergröße:",
        "HTTP chunk size:": "HTTP-Chunk-Größe:",
        "External downloader:": "Externer Downloader:",
        "External downloader args:": "Argumente für externen Downloader:",
        "Output template:": "Ausgabevorlage:",
        "Output directory:": "Ausgabeverzeichnis:",
        "Paths configuration:": "Pfadkonfiguration:",
        "Load info JSON:": "Info-JSON laden:",
        "Cache directory:": "Cache-Verzeichnis:",
        "Format selection:": "Formatauswahl:",
        "Format sort:": "Formatsortierung:",
        "Merge output format:": "Ausgabeformat zusammenführen:",
        "Video multistreams:": "Video-Multistreams:",
        "Audio multistreams:": "Audio-Multistreams:",
        "Subtitle format:": "Untertitelformat:",
        "Subtitle languages:": "Untertitelsprachen:",
        "Username:": "Benutzername:",
        "Password:": "Passwort:",
        "Two-factor code:": "Zwei-Faktor-Code:",
        "Video password:": "Video-Passwort:",
        "Adobe Pass MSO:": "Adobe Pass MSO-Anbieter:",
        "Adobe Pass username:": "Adobe Pass Benutzername:",
        "Adobe Pass password:": "Adobe Pass Passwort:",
        "Client certificate:": "Client-Zertifikat:",
        "Client certificate key:": "Client-Zertifikatschlüssel:",
        "Client certificate password:": "Zertifikatspasswort:",
        "Audio format:": "Audioformat:",
        "Audio quality:": "Audioqualität:",
        "Recode video format:": "Videoformat neu kodieren:",
        "Remux video format:": "Videoformat umverpacken:",
        "Metadata fields:": "Metadatenfelder:",
        "Parse metadata:": "Metadaten parsen:",
        "FFmpeg location:": "FFmpeg-Speicherort:",
        "Post-processor args:": "Post-Prozessor-Argumente:",
        "Convert thumbnails format:": "Vorschaubilder konvertieren in:",
        "Progress template:": "Fortschrittsvorlage:",
        "Metadata language:": "Metadatensprache:",
        "Default (Auto)": "Standard (Auto)",
        "Encoding:": "Kodierung:",
        "User agent:": "User-Agent:",
        "Referer:": "Referer:",
        "Add header:": "Header hinzufügen:",
        "Sleep before requests:": "Warten vor Anfragen:",
        "SponsorBlock categories to remove:": "Zu entfernende Werbeblocker-Kategorien:",
        "SponsorBlock categories to mark:": "Zu markierende Werbeblocker-Kategorien:",
        "SponsorBlock chapter title:": "Werbeblocker-Kapiteltitel:",
        "SponsorBlock API URL:": "Werbeblocker-API-URL:",
        "Extractor arguments:": "Extraktor-Argumente:",
        "Extractor retries:": "Extraktor-Wiederholungsversuche:",
        "Cookies from browser:": "Cookies vom Browser:",
        "Cookies file:": "Cookie-Datei:",
        "Raw command-line arguments:": "Rohe Befehlszeilenargumente:",
        "Generated command:": "Generierter Befehl:",
        "Generate Command": "Befehl generieren",
        "Copy to Clipboard": "In Zwischenablage kopieren",
        "Running: yt-dlp ": "Läuft: yt-dlp ",
        "Downloading...": "Herunterladen...",
        "Download completed successfully!": "Download erfolgreich abgeschlossen!",
        "Process exited with code ": "Prozess beendet mit Code: ",
        "ERROR: yt-dlp not found. Please make sure yt-dlp is installed and in your PATH.": "FEHLER: yt-dlp nicht gefunden.",
        "ERROR: ": "FEHLER: ",
        "Command copied to clipboard!": "Befehl kopiert!",
        "No URL": "Keine URL",
        "Please enter a URL or batch file to download.": "Bitte URL oder Batch-Datei eingeben.",
        "Please enter a URL.": "Bitte geben Sie eine URL ein.",
        "Error": "Fehler",
        "Success": "Erfolg",
        "Failed to save configuration: ": "Konfigurationsspeicherung fehlgeschlagen: ",
        "Failed to load configuration: ": "Konfigurationsladung fehlgeschlagen: ",
        "Configuration loaded successfully!": "Konfiguration erfolgreich geladen!",
        "Configuration saved successfully!": "Konfiguration erfolgreich gespeichert!",
        "Load Configuration": "Konfiguration laden",
        "Save Configuration": "Konfiguration speichern",
        "Select Batch File": "Batch-Datei auswählen",
        "Select Config File": "Konfig-Datei auswählen",
        "Select Archive File": "Archivdatei auswählen",
        "Select Output Directory": "Ausgabeverzeichnis auswählen",
        "Select Info JSON": "Info-JSON auswählen",
        "Select Cache Directory": "Cache-Verzeichnis auswählen",
        "Select Client Certificate": "Zertifikat auswählen",
        "Select Client Certificate Key": "Zertifikatsschlüssel auswählen",
        "Select FFmpeg Binary": "FFmpeg auswählen",
        "Select Cookies File": "Cookies auswählen",
        "Text Files": "Textdateien",
        "All Files": "Alle Dateien",
        "Config Files": "Konfigurationsdateien",
        "JSON Files": "JSON-Dateien",
        "PEM Files": "PEM-Dateien",
        "Key Files": "Schlüsseldateien",
        "Executable Files": "Ausführbare Dateien",
        ")": "(Komma-getrennt, z.B. 'en,fr,de')",
        "(ISO 3166-2 code)": "(ISO 3166-2 Code)",
        "(CIDR notation)": "(CIDR-Notation)",
        "(e.g., 50K or 4.2M)": "(z.B. 50K oder 4.2M)",
        "(comma-separated)": "(Komma-getrennt)",
        "(key:val[,val] format)": "(Schlüssel:Wert-Format)",
        "(One argument per line or space-separated)": "(Ein Argument pro Zeile oder Leerzeichen-getrennt)",
        "(0-10, 0 = best)": "(0-10, 0 = am besten)",
        "Ignore errors (--ignore-errors)": "Fehler ignorieren (--ignore-errors)",
        "Ignore warnings (--no-warnings)": "Warnungen ignorieren (--no-warnings)",
        "Abort on error (--abort-on-error)": "Abbruch bei Fehler (--abort-on-error)",
        "Download only video, not playlist (--no-playlist)": "Nur Video, keine Playlist (--no-playlist)",
        "Download playlist (--yes-playlist)": "Playlist herunterladen (--yes-playlist)",
        "Include private/unavailable videos in YouTube playlists": "Private/nicht verfügbare Videos einbeziehen",
        "Mark videos as watched (--mark-watched)": "Als gesehen markieren (--mark-watched)",
        "Do not mark videos as watched (--no-mark-watched)": "Nicht als gesehen markieren (--no-mark-watched)",
        "Force IPv4 (--force-ipv4)": "IPv4 erzwingen (--force-ipv4)",
        "Force IPv6 (--force-ipv6)": "IPv6 erzwingen (--force-ipv6)",
        "Enable file:// URLs (--enable-file-urls)": "file:// URLs aktivieren (--enable-file-urls)",
        "Bypass geo restriction (--geo-bypass)": "Geo-Einschränkung umgehen (--geo-bypass)",
        "Do not bypass geo restriction (--no-geo-bypass)": "Geo-Einschränkung nicht umgehen (--no-geo-bypass)",
        "Break on existing (--break-on-existing)": "Abbruch bei Existenz (--break-on-existing)",
        "Break on reject (--break-on-reject)": "Abbruch bei Ablehnung (--break-on-reject)",
        "No break on existing (--no-break-on-existing)": "Kein Abbruch bei Existenz (--no-break-on-existing)",
        "Do not resize buffer (--no-resize-buffer)": "Puffer nicht anpassen (--no-resize-buffer)",
        "Test mode - do not download (--test)": "Testmodus, nicht herunterladen (--test)",
        "Prefer native HLS downloader (--hls-prefer-native)": "Nativen HLS-Downloader bevorzugen (--hls-prefer-native)",
        "Prefer ffmpeg for HLS (--hls-prefer-ffmpeg)": "ffmpeg für HLS bevorzugen (--hls-prefer-ffmpeg)",
        "Use MPEG-TS container for HLS (--hls-use-mpegts)": "MPEG-TS für HLS nutzen (--hls-use-mpegts)",
        "Restrict filenames to ASCII (--restrict-filenames)": "Dateinamen auf ASCII beschränken (--restrict-filenames)",
        "Allow Unicode in filenames (--no-restrict-filenames)": "Unicode in Dateinamen erlauben (--no-restrict-filenames)",
        "Create playlist subfolder for playlist downloads": "Unterordner für Playlists erstellen",
        "Force Windows-compatible filenames (--windows-filenames)": "Windows-kompatible Namen erzwingen (--windows-filenames)",
        "Do not overwrite files (--no-overwrites)": "Dateien nicht überschreiben (--no-overwrites)",
        "Force overwrite files (--force-overwrites)": "Überschreiben erzwingen (--force-overwrites)",
        "Continue partially downloaded files (--continue)": "Teilweise Downloads fortsetzen (--continue)",
        "Do not continue downloads (--no-continue)": "Downloads nicht fortsetzen (--no-continue)",
        "Do not use .part files (--no-part)": "Keine .part-Dateien verwenden (--no-part)",
        "Do not use Last-modified header (--no-mtime)": "Kein Last-modified-Header verwenden (--no-mtime)",
        "Write description to .description file (--write-description)": "Beschreibung in Datei schreiben (--write-description)",
        "Write metadata to .info.json file (--write-info-json)": "Metadaten in .json schreiben (--write-info-json)",
        "Write annotations to .annotations.xml (--write-annotations)": "Anmerkungen schreiben (--write-annotations)",
        "Write comments to .comments.json (--write-comments)": "Kommentare schreiben (--write-comments)",
        "Disable filesystem caching (--no-cache-dir)": "Dateisystem-Caching deaktivieren (--no-cache-dir)",
        "Delete cache directory contents (--rm-cache-dir)": "Cache-Inhalt löschen (--rm-cache-dir)",
        "Prefer free formats (--prefer-free-formats)": "Freie Formate bevorzugen (--prefer-free-formats)",
        "Check available formats (--check-formats)": "Verfügbare Formate prüfen (--check-formats)",
        "Write subtitle file (--write-subs)": "Untertiteldatei schreiben (--write-subs)",
        "Write automatic subtitle file (--write-auto-subs)": "Automatische Untertitel schreiben (--write-auto-subs)",
        "List available subtitles (--list-subs)": "Verfügbare Untertitel auflisten (--list-subs)",
        "Embed subtitles (--embed-subs)": "Untertitel einbetten (--embed-subs)",
        "Do not embed subtitles (--no-embed-subs)": "Untertitel nicht einbetten (--no-embed-subs)",
        "Embed thumbnail (--embed-thumbnail)": "Vorschaubild einbetten (--embed-thumbnail)",
        "Do not embed thumbnail (--no-embed-thumbnail)": "Vorschaubild nicht einbetten (--no-embed-thumbnail)",
        "Use .netrc authentication (--netrc)": ".netrc-Authentifizierung nutzen (--netrc)",
        "Extract audio (-x, --extract-audio)": "Audio extrahieren (-x, --extract-audio)",
        "Keep video file after conversion (--keep-video)": "Video nach Konvertierung behalten (--keep-video)",
        "Do not keep video file (--no-keep-video)": "Video nach Konvertierung löschen (--no-keep-video)",
        "Embed metadata (--embed-metadata)": "Metadaten einbetten (--embed-metadata)",
        "Embed chapter markers (--embed-chapters)": "Kapitelmarken einbetten (--embed-chapters)",
        "Embed info.json (--embed-info-json)": "info.json einbetten (--embed-info-json)",
        "Add metadata to file (--add-metadata)": "Metadaten zur Datei hinzufügen (--add-metadata)",
        "Write thumbnail image (--write-thumbnail)": "Vorschaubild speichern (--write-thumbnail)",
        "Write all thumbnail formats (--write-all-thumbnails)": "Alle Vorschaubildformate speichern (--write-all-thumbnails)",
        "List available thumbnails (--list-thumbnails)": "Verfügbare Vorschaubilder auflisten (--list-thumbnails)",
        "Quiet mode (-q, --quiet)": "Stiller Modus (-q, --quiet)",
        "No warnings (--no-warnings)": "Keine Warnungen (--no-warnings)",
        "Verbose output (-v, --verbose)": "Ausführliche Ausgabe (-v, --verbose)",
        "Simulate, do not download (-s, --simulate)": "Simulieren, nicht herunterladen (-s, --simulate)",
        "Skip download (--skip-download)": "Download überspringen (--skip-download)",
        "Get title (--get-title)": "Titel abrufen (--get-title)",
        "Get ID (--get-id)": "ID abrufen (--get-id)",
        "Get URL (--get-url)": "URL abrufen (--get-url)",
        "Get thumbnail URL (--get-thumbnail)": "Vorschaubild-URL abrufen (--get-thumbnail)",
        "Get description (--get-description)": "Beschreibung abrufen (--get-description)",
        "Get duration (--get-duration)": "Dauer abrufen (--get-duration)",
        "Get filename (--get-filename)": "Dateiname abrufen (--get-filename)",
        "Get format (--get-format)": "Format abrufen (--get-format)",
        "Dump JSON info (--dump-json)": "Info-JSON ausgeben (--dump-json)",
        "Dump single JSON (--dump-single-json)": "Einzelne JSON ausgeben (--dump-single-json)",
        "Print JSON info (--print-json)": "Info-JSON drucken (--print-json)",
        "Show progress (--progress)": "Fortschritt anzeigen (--progress)",
        "Hide progress (--no-progress)": "Fortschritt verbergen (--no-progress)",
        "Display progress in console title (--console-title)": "Fortschritt im Konsolentitel (--console-title)",
        "Skip SSL certificate validation (--no-check-certificate)": "SSL-Prüfung überspringen (--no-check-certificate)",
        "Prefer insecure connections (--prefer-insecure)": "Unsichere Verbindungen bevorzugen (--prefer-insecure)",
        "Bidirectional text workaround (--bidi-workaround)": "Workaround für bidirektionalen Text (--bidi-workaround)",
        "Use legacy server connect (--legacy-server-connect)": "Veraltetes Server-Connect nutzen (--legacy-server-connect)",
        "Mark SponsorBlock chapters (--sponsorblock-mark)": "Werbeblocker-Kapitel markieren (--sponsorblock-mark)",
        "Remove SponsorBlock segments (--sponsorblock-remove)": "Werbeblocker-Segmente entfernen (--sponsorblock-remove)",
        "Disable SponsorBlock (--no-sponsorblock)": "Werbeblocker deaktivieren (--no-sponsorblock)",
        "Allow dynamic MPD manifests (--allow-dynamic-mpd)": "允许动态 MPD 清单（--allow-dynamic-mpd）",
        "Ignore dynamic MPD manifests (--ignore-dynamic-mpd)": "忽略动态 MPD 清单（--ignore-dynamic-mpd）",
        "Split HLS segments on discontinuity (--hls-split-discontinuity)": "HLS-Segmente bei Diskontinuität aufteilen (--hls-split-discontinuity)",
        "Select All / Deselect All": "Alle auswählen / Auswahl aufheben",
        "Quick Select Resolution:": "Schnellauswahl Auflösung:",
        "Best (Auto)": "Beste (Auto)",
        "4K (2160p)": "4K (2160p)",
        "2K (1440p)": "2K (1440p)",
        "1080p 60fps": "1080p 60fps",
        "1080p": "1080p",
        "720p": "720p",
        "480p": "480p",
        "360p": "360p",
        "720p 60fps": "720p 60fps",
        "sponsor": "Sponsorenwerbung",
        "intro": "Intro",
        "outro": "Outro",
        "selfpromo": "Eigenwerbung",
        "preview": "Vorschau",
        "filler": "Füllmaterial",
        "interaction": "Interaktion",
        "music_offtopic": "Musik: Nicht zum Thema gehörend",
        "poi_highlight": "Highlight",
        "chapter": "Kapitel",
        "Select All": "Alle auswählen",
        "Deselect All": "Keine auswählen",
        "Invert Select": "Auswahl umkehren",
        "Allow dynamic MPD manifests (--allow-dynamic-mpd)": "Dynamische MPD-Manifeste zulassen (--allow-dynamic-mpd)",
        "Ignore dynamic MPD manifests (--ignore-dynamic-mpd)": "Dynamische MPD-Manifeste ignorieren (--ignore-dynamic-mpd)",
    },
}


for _lang in ('ru', 'ko', 'es', 'fr', 'de'):
    _progress_path = os.path.expanduser(f'~/.vscode/tmp/tmp_vscode_1/{_lang}_progress.json')
    if not os.path.exists(_progress_path):
        continue
    try:
        with open(_progress_path, 'r', encoding='utf-8') as _progress_file:
            _progress_translations = json.load(_progress_file)
        if isinstance(_progress_translations, dict):
            TRANSLATIONS[_lang].update(_progress_translations)
    except Exception:
        pass


TRANSLATIONS['ru']['Adobe Pass MSO:'] = 'Adobe Pass MSO-поставщик:'
TRANSLATIONS['es']['General'] = 'Opciones generales'
TRANSLATIONS['es']['Extractor'] = 'Extractor de contenido'
TRANSLATIONS['es']['Error'] = 'Error:'
TRANSLATIONS['es']['Adobe Pass MSO:'] = 'Proveedor Adobe Pass MSO:'
TRANSLATIONS['de']['SponsorBlock'] = 'SponsorBlock-Funktion'
TRANSLATIONS['de']['Adobe Pass MSO:'] = 'Adobe Pass MSO-Anbieter:'


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
        try:
            self.root.iconname('yt-dlp')
        except Exception:
            pass

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
            if lang: candidates.append(lang)
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
            except:
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
        # PERFORMANCE OPTIMIZATION: Skip recursion for the bulk list container
        # This prevents O(N) traversals on thousands of widgets during every localization pass.
        if hasattr(self, 'bulk_scroll_frame') and widget == self.bulk_scroll_frame:
            return

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
            
        print(f"[LANG] on_language_changed triggered. Value: {display_val}")
        
        raw_code = self.get_language_code_from_display(display_val)
        new_language = raw_code
        
        if raw_code == 'auto':
            new_language = self.detect_system_language()
            print(f"[LANG] Auto-detected: {new_language}")

        # Check if actually changed to avoid redundant refreshes
        if getattr(self, 'current_language', None) == new_language:
            # Still update config in case raw_code changed (e.g. from specific to 'auto')
            self.config['language'] = raw_code
            self.persist_language_preference()
            return

        self.log_message(f'[EVENT] Switching language to: {new_language} (Choice: {display_val})')
        print(f"[LANG] Setting current_language to {new_language}")

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
        print("[LANG] Language change completed.")

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

        try:
            self.root.state('normal')
        except tk.TclError:
            pass

        self.root.geometry(f'{target_width}x{target_height}+{target_x}+{target_y}')
        self.root.deiconify()
        self.root.lift()

    def bring_to_front(self):
        """Request focus and foreground status, especially on macOS."""
        self.root.update_idletasks()
        self.root.deiconify()
        self.root.lift()

        try:
            self.root.focus_force()
        except tk.TclError:
            pass

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
        # EXEMPTION: Never unload tabs containing complex dynamic list data
        is_playlist = (hasattr(self, 'playlist_tab_frame') and frame == self.playlist_tab_frame)
        is_batch = (hasattr(self, 'batch_tab_frame') and frame == self.batch_tab_frame)
        
        if frame not in self._built_tabs or is_playlist or is_batch:
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
            # EXEMPTION: Never unload tabs with dynamic list data
            is_playlist = (hasattr(self, 'playlist_tab_frame') and previous_frame == self.playlist_tab_frame)
            is_batch = (hasattr(self, 'batch_tab_frame') and previous_frame == self.batch_tab_frame)
            
            if not is_playlist and not is_batch:
                self.unload_tab(previous_frame)
                
        self.ensure_tab_built(frame)
        self._active_tab_frame = frame
        
        # Update scrollregion once after a slight delay if switching into it, 
        # but avoid heavy update_idletasks on every switch.
        if hasattr(self, 'playlist_tab_frame') and frame == self.playlist_tab_frame:
            pass # Treeview handles sizing automatically

    
    def trigger_autosave(self, *args):
        """Request an autosave with a short debouncing delay."""
        if hasattr(self, '_autosave_timer') and self._autosave_timer:
            self.root.after_cancel(self._autosave_timer)
        self._autosave_timer = self.root.after(500, lambda: self.save_config(silent=True))

    def ensure_all_tabs_built(self):
        """Build all tabs before full-state serialization."""
        if not hasattr(self, 'notebook'):
            return
        # Force building of all lazy tabs
        for tab_id in list(self._tab_builders.keys()):
            tab_frame = self._tab_controls.get(tab_id)
            if tab_frame:
                self.ensure_tab_built(tab_frame)
    
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
        self.batch_tab_frame = self.add_lazy_tab('batch', 'Batch Download', self.create_batch_download_tab)

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
        
        self.ensure_tab_built(self.batch_tab_frame)
        self._active_tab_frame = self.batch_tab_frame

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

        header_row = ttk.Frame(frame)
        header_row.pack(fill=tk.X, pady=(0, 5))
        
        lbl_list = ttk.Label(header_row, text=self.tr('Batch URLs (one per line):'))
        lbl_list.pack(side=tk.LEFT)
        self.register_translatable_widget(lbl_list, 'Batch URLs (one per line):')
        
        btn_paste_batch = ttk.Button(header_row, text=self.tr('Paste'), command=self.paste_to_batch_text)
        btn_paste_batch.pack(side=tk.LEFT, padx=(8, 2))
        self.register_translatable_widget(btn_paste_batch, 'Paste')

        btn_parse_batch = ttk.Button(header_row, text=self.tr('Parse All'), command=self.parse_batch_text)
        btn_parse_batch.pack(side=tk.LEFT, padx=2)
        self.register_translatable_widget(btn_parse_batch, 'Parse All')
        
        # Keep clear pool in header row to the right
        btn_clear = ttk.Button(header_row, text=self.tr('Clear Pool'), command=self.clear_all_bulk_rows)
        btn_clear.pack(side=tk.RIGHT)
        self.register_translatable_widget(btn_clear, 'Clear Pool')

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
        
        # Restore URLs from config if present
        bulk_urls = self.config.get('bulk_urls', [])
        if bulk_urls:
            self.bulk_scroll_frame.unbind('<Configure>')
            
            # Hybrid approach for "Instant" feel:
            # 1. Load first 40 rows synchronously (instant enough)
            first_chunk = bulk_urls[:40]
            remaining = bulk_urls[40:]
            
            for url in first_chunk:
                self.add_bulk_row(url, localize=False, register=False)
            
            # Initial layout update
            self.bulk_canvas.configure(scrollregion=self.bulk_canvas.bbox('all'))
            self.bulk_canvas.yview_moveto(0)
            
            # 2. Background load the rest if any
            if remaining:
                def _bg_load(idx):
                    chunk_size = 60
                    end = min(idx + chunk_size, len(remaining))
                    for i in range(idx, end):
                        self.add_bulk_row(remaining[i], localize=False, register=False)
                    
                    if end < len(remaining):
                        self.root.after(1, lambda: _bg_load(end))
                    else:
                        # Final re-bind and layout
                        self.bulk_scroll_frame.bind(
                            '<Configure>',
                            lambda e: self.bulk_canvas.configure(scrollregion=self.bulk_canvas.bbox('all')))
                        self.bulk_canvas.configure(scrollregion=self.bulk_canvas.bbox('all'))

                self.root.after(10, lambda: _bg_load(0))
            else:
                self.bulk_scroll_frame.bind(
                    '<Configure>',
                    lambda e: self.bulk_canvas.configure(scrollregion=self.bulk_canvas.bbox('all')))
        else:
            self.add_bulk_row()

        return frame

    def add_bulk_row(self, initial_text='', localize=True, register=True):
        # Use stylized raw tk widgets for "Instant" speed (10x faster than ttk on macOS)
        # We manually style them to look "Premium"
        bg_col = self.root.cget('bg')
        row = tk.Frame(self.bulk_scroll_frame, bg=bg_col)
        row.pack(fill=tk.X, pady=2)
        
        # Plain entry without StringVar overhead for bulk items
        entry = tk.Entry(row, highlightthickness=1, borderwidth=0, relief='flat')
        entry.insert(0, initial_text)
        # Use a nice border color that matches macOS aesthetics
        entry.config(highlightbackground='#d1d1d1', highlightcolor='#007aff')
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=2)
        
        # Bind change event to autosave (equivalent to trace)
        entry.bind('<KeyRelease>', lambda e: self.trigger_autosave())
        
        # Use localized text immediately 
        parse_text = self.tr('Parse')
        btn_parse = ttk.Button(row, text=parse_text, width=8, command=lambda e=entry: self._parse_single_row_url(e.get()))
        btn_parse.pack(side=tk.LEFT, padx=2)
        
        if register:
            self.register_translatable_widget(btn_parse, 'Parse')
        
        if len(self.bulk_rows) == 0:
            btn_add = ttk.Button(row, text='+', width=3, command=self.add_bulk_row)
            btn_add.pack(side=tk.LEFT)
        else:
            btn_remove = ttk.Button(row, text='-', width=3, command=lambda r=row: self.remove_bulk_row(r))
            btn_remove.pack(side=tk.LEFT)
            
        # Store widget for later access instead of var
        self.bulk_rows.append({'frame': row, 'entry': entry})
        
        if localize:
            self.localize_widget_tree(row)

    def remove_bulk_row(self, frame):
        frame.destroy()
        self.bulk_rows = [r for r in self.bulk_rows if r['frame'] != frame]
        if not self.bulk_rows:
            self.add_bulk_row()
        self.trigger_autosave()

    def get_bulk_urls(self):
        """Unified method to get all non-empty URLs from the dynamic row list."""
        urls = []
        for row in getattr(self, 'bulk_rows', []):
            entry = row.get('entry')
            if entry:
                value = entry.get().strip()
                if value:
                    urls.append(value)
        return urls

    def clear_all_bulk_rows(self):
        """Clear all batch URLs from the dynamic list."""
        for row in self.bulk_rows[1:]:
            row['frame'].destroy()
        if self.bulk_rows:
            self.bulk_rows = self.bulk_rows[:1]
            entry = self.bulk_rows[0].get('entry')
            if entry:
                entry.delete(0, tk.END)
        self.trigger_autosave()

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
                with open(file_path, 'r', encoding='utf-8') as f:
                    urls.extend([line.strip() for line in f if line.strip() and not line.strip().startswith('#')])
            except Exception as e:
                self.log_message(self.translate_concat('Error reading batch file: ', str(e)))


        for url in self.get_bulk_urls():
            if url:
                urls.append(url)

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
        btn_sel_all = ttk.Button(top_ctrl, text="Select All", command=lambda: self._on_playlist_select_all('all'))
        btn_sel_all.pack(side=tk.LEFT, padx=(0, 2))
        self.register_translatable_widget(btn_sel_all, 'Select All')
        
        btn_sel_none = ttk.Button(top_ctrl, text="Deselect All", command=lambda: self._on_playlist_select_all('none'))
        btn_sel_none.pack(side=tk.LEFT, padx=2)
        self.register_translatable_widget(btn_sel_none, 'Deselect All')
        
        btn_sel_inv = ttk.Button(top_ctrl, text="Invert Select", command=lambda: self._on_playlist_select_all('invert'))
        btn_sel_inv.pack(side=tk.LEFT, padx=2)
        self.register_translatable_widget(btn_sel_inv, 'Invert Select')

        # Restore playlist option checkboxes (deduplicated) so they are visible once
        # again in the playlist tab. Keep behavior consistent with internal vars.
        self.playlist_reverse_var = tk.BooleanVar(value=False)
        cb_rev = ttk.Checkbutton(
            top_ctrl,
            text="Reverse order",
            variable=self.playlist_reverse_var,
            command=self._on_playlist_option_changed
        )
        cb_rev.pack(side=tk.LEFT, padx=(20, 0))
        self.register_translatable_widget(cb_rev, 'Reverse order')

        self.playlist_exclude_private_var = tk.BooleanVar(value=True)
        cb_priv = ttk.Checkbutton(
            top_ctrl,
            text="Exclude private videos",
            variable=self.playlist_exclude_private_var,
            command=self._on_playlist_option_changed
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
            if event.num == 4: # Linux scroll up
                self.playlist_tree.yview_scroll(-1, "units")
            elif event.num == 5: # Linux scroll down
                self.playlist_tree.yview_scroll(1, "units")
            else: # Windows/Mac
                self.playlist_tree.yview_scroll(int(-1*(event.delta)), "units")

    def _on_playlist_option_changed(self):
        if hasattr(self, 'playlist_entries_data') and self.playlist_entries_data:
            self.root.after(0, self._show_playlist_tab, "Playlist")

    def create_general_tab(self, frame=None):
        """Create General Options tab"""
        frame = frame or ttk.Frame(self.notebook, padding='10')

        # Scrollable frame
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
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
        self.register_translatable_widget(self.res_selector, 'Quick Select Resolution Selector') # Placeholder to trigger refresh
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
            width=20
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
        
        btn_rm_all = ttk.Button(rem_ctrl, text="Select All", command=lambda: self._set_sb_group('remove', True))
        btn_rm_all.pack(side=tk.LEFT, padx=2)
        self.register_translatable_widget(btn_rm_all, 'Select All')
        
        btn_rm_none = ttk.Button(rem_ctrl, text="Deselect All", command=lambda: self._set_sb_group('remove', False))
        btn_rm_none.pack(side=tk.LEFT, padx=2)
        self.register_translatable_widget(btn_rm_none, 'Deselect All')
        
        btn_rm_inv = ttk.Button(rem_ctrl, text="Invert Select", command=lambda: self._set_sb_group('remove', 'invert'))
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
        
        btn_mk_all = ttk.Button(mark_ctrl, text="Select All", command=lambda: self._set_sb_group('mark', True))
        btn_mk_all.pack(side=tk.LEFT, padx=2)
        self.register_translatable_widget(btn_mk_all, 'Select All')
        
        btn_mk_none = ttk.Button(mark_ctrl, text="Deselect All", command=lambda: self._set_sb_group('mark', False))
        btn_mk_none.pack(side=tk.LEFT, padx=2)
        self.register_translatable_widget(btn_mk_none, 'Deselect All')
        
        btn_mk_inv = ttk.Button(mark_ctrl, text="Invert Select", command=lambda: self._set_sb_group('mark', 'invert'))
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
        ttk.Label(frame, text='(One argument per line or space-separated)').grid(row=row+1, column=1, sticky=tk.W, padx=5)
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

    def paste_to_batch_text(self):
        try:
            content = self.root.clipboard_get().strip()
        except tk.TclError:
            content = ''

        if not content:
            self.log_message(self.tr('Clipboard is empty.'))
            return

        lines = [l.strip() for l in content.splitlines() if 'http' in l.lower()]
        if not lines:
            self.log_message(self.tr('No URLs found in clipboard.'))
            return

        imported_count = 0
        # If the first row is empty, fill it. Otherwise add new rows.
        first_entry = self.bulk_rows[0].get('entry') if self.bulk_rows else None
        if len(self.bulk_rows) == 1 and first_entry and not first_entry.get().strip():
            first_entry.delete(0, tk.END)
            first_entry.insert(0, lines[0])
            lines = lines[1:]
            imported_count += 1
        
        if lines:
            # PERFORMANCE OPTIMIZATION: Unbind during bulk paste
            self.bulk_scroll_frame.unbind('<Configure>')
            
            for line in lines:
                self.add_bulk_row(line, localize=False, register=False)
            
            # Re-bind and update once
            self.bulk_scroll_frame.bind(
                '<Configure>',
                lambda e: self.bulk_canvas.configure(scrollregion=self.bulk_canvas.bbox('all')))
            
            self.bulk_canvas.configure(scrollregion=self.bulk_canvas.bbox('all'))
            
        self.trigger_autosave()
        self.log_message(self.tr('Imported {} URLs into pool.').replace('{}', str(len(lines) + imported_count)))

    def parse_batch_text(self):
        """Parse all URLs in the pool bulk rows."""
        urls = self.get_bulk_urls()
        if not urls:
            self.log_message(self.tr('No URLs to parse.'))
            return
        
        for url in urls:
            self._parse_single_row_url(url)
        
        self.log_message(f'Parsed {len(urls)} URLs from batch pool.')

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
        except:
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
            'Indonesian (id)'
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
            'de': 'de'
        }
        gui_lang_code = getattr(self, 'current_language', 'zh')
        lang_to_use = lang_map.get(gui_lang_code, 'zh-CN')

        if hasattr(self, 'metadata_lang') and self.metadata_lang.get() and self.metadata_lang.get() != self.tr('Default (Auto)'):
            lang_to_use = self.metadata_lang.get().split('(')[-1].split(')')[0]
            
        args.extend(['--extractor-args', f'youtube:lang={lang_to_use}'])
        # SHOTGUN APPROACH: Inject HTTP header to force server response language
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
        if self.sub_langs.get():
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
            extractor_args.append(f'youtube:lang={self.metadata_lang.get()}')
        
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
                    args.extend(['-a', batch_file]) # Fallback
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
        cmd = [sys.executable, '-m', 'yt_dlp'] + args
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
                self.log_message(self.translate_concat(f'[{i+1}/{total}] Download Task: Index ', idx))
                self.root.after(0, lambda: self.status_var.set(f'{self.tr("Downloading")} {i+1}/{total}'))

                full_cmd = [sys.executable, '-m', 'yt_dlp', '--remote-components', 'ejs:github'] + args
                
                self.current_process = subprocess.Popen(
                    full_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1,
                    preexec_fn=os.setpgrp # Create process group for easy mass-kill
                )
                process = self.current_process

                if process.stdout:
                    for line in process.stdout:
                        if line:
                            self.log_message(line.rstrip())

                process.wait()
                
                if process.returncode != 0 and process.returncode not in (15, -15):
                    self.log_message(self.translate_concat('Task failed with code ', process.returncode))
                    if "n challenge solving failed" in "".join(self.console.get("1.0", tk.END)):
                        self.log_message("\n[!] 提示：检测到 JavaScript 运行环境缺失。")
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
            self.current_process = None # Signal to stop loop
            self.log_message(self.tr('Stopping download...'))
            
            try:
                # Kill the entire process group (including child processes like ffmpeg)
                os.killpg(os.getpgid(p.pid), signal.SIGTERM)
                p.terminate()
                p.kill()
            except Exception as e:
                self.log_message(f"[DEBUG] Stop error: {e}")
            
            # Popup for cleanup
            msg = self.tr('Download stopped. Would you like to delete partially downloaded files?')
            if messagebox.askyesno(self.tr("Stop"), msg):
                self.cleanup_partial_files()
        else:
            self.log_message(self.tr('No download currently running.'))

    def cleanup_partial_files(self):
        """Scan output directory and remove .part, .ytdl and temporary fragment files."""
        output_dir = self.output_dir.get().strip()
        if not output_dir or not os.path.exists(output_dir):
            return
            
        count = 0
        self.log_message(self.tr("Cleaning up partial files..."))
        try:
            for filename in os.listdir(output_dir):
                # yt-dlp partial files usually end with .part, .ytdl 
                # or have fragments like .f137.part
                if filename.endswith('.part') or filename.endswith('.ytdl') or '.f' in filename and '.part' in filename:
                    file_path = os.path.join(output_dir, filename)
                    if os.path.isfile(file_path):
                        try:
                            os.remove(file_path)
                            count += 1
                        except Exception as e:
                            self.log_message(f"Failed to remove {filename}: {e}")
            self.log_message(f"Cleanup finished. Removed {count} files.")
        except Exception as e:
            self.log_message(f"Error during cleanup: {e}")

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
                    visual_idx = int(vals[1])
                    gui_title = str(vals[2]) # Defined here!
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
                        if arg == url: # Don't add the main URL yet
                            continue
                        task_args.append(arg)
                    
                    # Always use the specific playlist URL for individual tasks
                    task_args.append(url)
                    filename_tpl = f'{visual_idx:03d} - {gui_title}.%(ext)s'
                    # Remove unsave characters
                    filename_tpl = "".join([c for c in filename_tpl if c not in '<>:"/\\|?*']).strip()
                    
                    # Handle playlist subfolder
                    final_output_dir = output_dir
                    if self.playlist_subdir.get() and getattr(self, 'current_playlist_metadata_title', None):
                        folder_name = "".join([c for c in self.current_playlist_metadata_title if c not in '<>:"/\\|?*']).strip()
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
            self.url_var.set(url)
        
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
            self.log_message(self.tr("Checking if URL is a playlist..."))
            # ADDED --no-cache-dir to ensure we get fresh language-specific metadata
            cmd = [sys.executable, '-m', 'yt_dlp', '-J', '--flat-playlist', '--no-cache-dir']
            
            # MAP GUI Language to Metadata Language
            lang_map = {'zh': 'zh-CN', 'en': 'en', 'ru': 'ru', 'ja': 'ja', 'ko': 'ko', 'es': 'es', 'fr': 'fr', 'de': 'de'}
            gui_lang_code = getattr(self, 'current_language', 'zh')
            lang_to_use = lang_map.get(gui_lang_code, 'zh-CN')
            
            self.log_message(f'[DEBUG] Parsing playlist metadata using interface-linked language: {lang_to_use}')
            cmd.extend(['--extractor-args', f'youtube:lang={lang_to_use}'])
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
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
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
                    self.log_message(self.tr("Not a playlist or no entries found."))
            else:
                self.log_message(f'[ERROR] Parsing failed: {stderr.strip()}')
                self.log_message(self.tr("Failed to parse playlist."))
        except Exception as e:
            self.log_message(self.translate_concat('Error checking playlist: ', str(e)))
        self.status_var.set(self.tr('Ready'))

    def _show_playlist_tab(self, temp_title):
        self.log_message(self.tr("Playlist detected. Please select videos to download."))
        self.status_var.set(self.tr('Playlist detected'))
        if hasattr(self, 'playlist_tree'):
            self.notebook.select(self.playlist_tab_frame)
            self.playlist_tree.delete(*self.playlist_tree.get_children())
            
            entries = self.playlist_entries_data
            filtered_entries = []
            for i, entry in enumerate(entries):
                title = entry.get('title') or entry.get('id') or f'Video {i+1}'
                availability = entry.get('availability', '')
                is_private = (
                    title in ('[Private video]', '[私享视频]', '[私有视频]', '[Deleted video]', '[已删除的视频]') or 
                    availability == 'private' or
                    entry.get('title') is None
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
        except Exception: # queue.Empty
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
                with open(self.config_file, 'r', encoding='utf-8') as f:
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
                with open(filename, 'r', encoding='utf-8') as f:
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

        bulk_urls = self.get_bulk_urls()

        return {
            'config_version': 1,
            'language': self.current_language,
            'language_initialized': True,
            'gui_state': gui_state,
            'bulk_urls': bulk_urls,
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
        
        # Restore bulk URLs
        bulk_urls = self.config.get('bulk_urls', [])
        if bulk_urls:
            # First ensure create_batch_download_tab was called or build it
            self.ensure_tab_built_by_id('batch')
            if hasattr(self, 'bulk_rows'):
                self.clear_all_bulk_rows()
                if bulk_urls:
                    entry = self.bulk_rows[0].get('entry')
                    if entry:
                        entry.delete(0, tk.END)
                        entry.insert(0, bulk_urls[0])
                    for url in bulk_urls[1:]:
                        self.add_bulk_row(url)

        self.apply_localization()
        self.apply_pending_gui_state()
        self.status_var.set(self.tr('Ready'))

    def ensure_tab_built_by_id(self, tab_id):
        """Building specific tab if it's currently lazy."""
        if not hasattr(self, 'notebook'):
            return
        # Find which index this tab ID belongs to
        # Mapping depends on how tabs were added
        # Just use the ensure_tab_built on the stored frames
        frame = self._tab_controls.get(tab_id)
        if frame:
            self.ensure_tab_built(frame)


def main():
    """Main entry point for the GUI"""
    try:
        root = tk.Tk()
        # Set theme and window style for macOS
        style = ttk.Style(root)
        if sys.platform == 'darwin':
            style.theme_use('aqua')
        
        app = YtDlpGUI(root)
        root.mainloop()
    except Exception as e:
        import traceback
        print(f"FATAL ERROR during GUI startup:\n{traceback.format_exc()}")



if __name__ == "__main__":
    main()
