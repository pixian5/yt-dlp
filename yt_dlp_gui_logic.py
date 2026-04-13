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


LANGUAGE_OPTIONS = {
    'en': 'English',
    'zh': '中文',
    'ru': 'Русский',
    'ja': '日本語',
    'ko': '한국어',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch',
}


GUI_DEFAULT_STATE = {
    'url_entry': 'https://www.youtube.com/watch?v=DtPmasWzmu4&list=PLqyUAJYG3AWzd2mRGVLgCNKXbFcE4mAAk',
    'cookies_from_browser': 'chrome',
    'format': 'bv*[height<=1080]+ba',
    'merge_output_format': 'mp4',
    'output_dir': '/Users/x/Documents/yt',
    'output_template': '%(playlist_index)s-%(title)s.%(ext)s',
    'include_private_videos': True,
    'playlist_subdir': False,
    'metadata_lang': 'zh-CN',
    'playlist_reverse_var': True,
}


TRANSLATIONS = {
    'zh': {
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
        'Stop': '停止',
        'Exclude private videos': '隐藏私有视频',
        'Reverse order': '播放列表倒序',
        'Output Console': '输出控制台',
        'Ready': '就绪',
        'Clipboard is empty.': '剪贴板为空。',
        'Pasted link from clipboard.': '已从剪贴板粘贴链接。',
        'General': '常规',
        'Network': '网络',
        'Geo-restriction': '地区限制',
        'Video Selection': '视频筛选',
        'Download': '下载',
        'Filesystem': '文件系统',
        'Video Format': '视频格式',
        'Subtitles': '字幕',
        'Authentication': '认证',
        'Post-processing': '后处理',
        'Thumbnail': '缩略图',
        'Verbosity/Simulation': '输出/模拟',
        'Workarounds': '兼容方案',
        'SponsorBlock': 'SponsorBlock',
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
        'Adobe Pass MSO:': 'Adobe Pass MSO：',
        'Adobe Pass username:': 'Adobe Pass 用户名：',
        'Adobe Pass password:': 'Adobe Pass 密码：',
        'Client certificate:': '客户端证书：',
        'Client certificate key:': '客户端证书密钥：',
        'Client certificate password:': '客户端证书密码：',
        'Audio format:': '音频格式：',
        'Audio quality:': '音频质量：',
        'Recode video format:': '重编码视频格式：',
        'Remux video format:': '封装转换视频格式：',
        'Metadata fields:': '元数据字段：',
        'Parse metadata:': '解析元数据：',
        'FFmpeg location:': 'FFmpeg 位置：',
        'Post-processor args:': '后处理器参数：',
        'Convert thumbnails format:': '转换缩略图格式：',
        'Progress template:': '进度模板：',
        'Metadata language:': '元数据语言：',
        'Default (Auto)': '默认（自动）',
        'Encoding:': '编码：',
        'User agent:': 'User-Agent：',
        'Referer:': 'Referer：',
        'Add header:': '添加请求头：',
        'Sleep before requests:': '请求前休眠：',
        'SponsorBlock categories to remove:': '要移除的 SponsorBlock 分类：',
        'SponsorBlock categories to mark:': '要标记的 SponsorBlock 分类：',
        'SponsorBlock chapter title:': 'SponsorBlock 章节标题：',
        'SponsorBlock API URL:': 'SponsorBlock API URL：',
        'Extractor arguments:': '提取器参数：',
        'Extractor retries:': '提取器重试次数：',
        'Cookies from browser:': '从浏览器读取 Cookies：',
        'Cookies file:': 'Cookies 文件：',
        'Raw command-line arguments:': '原始命令行参数：',
        'Generated command:': '生成的命令：',
        'Generate Command': '生成命令',
        'Copy to Clipboard': '复制到剪贴板',
        'Running: yt-dlp ': '正在运行：yt-dlp ',
        'Downloading...': '下载中...',
        'Download completed successfully!': '下载成功完成！',
        'Process exited with code ': '进程退出，代码：',
        'ERROR: yt-dlp not found. Please make sure yt-dlp is installed and in your PATH.': '错误：未找到 yt-dlp，请确认它已安装并且在 PATH 中。',
        'ERROR: ': '错误：',
        'Command copied to clipboard!': '命令已复制到剪贴板！',
        'No URL': '没有 URL',
        'Please enter a URL or batch file to download.': '请输入要下载的 URL 或批量文件。',
        'Please enter a URL.': '请输入 URL。',
        'Error': '错误',
        'Success': '成功',
        'Failed to save configuration: ': '保存配置失败：',
        'Failed to load configuration: ': '加载配置失败：',
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
        'Select Client Certificate Key': '选择客户端证书密钥',
        'Select FFmpeg Binary': '选择 FFmpeg 可执行文件',
        'Select Cookies File': '选择 Cookies 文件',
        'Text Files': '文本文件',
        'All Files': '所有文件',
        'Config Files': '配置文件',
        'JSON Files': 'JSON 文件',
        'PEM Files': 'PEM 文件',
        'Key Files': '密钥文件',
        'Executable Files': '可执行文件',
        '(e.g., "ytsearch5:")': '（例如“ytsearch5:”）',
        '(ISO 3166-2 code)': '（ISO 3166-2 代码）',
        '(CIDR notation)': '（CIDR 表示法）',
        '(e.g., "1-5,10,15-20")': '（例如“1-5,10,15-20”）',
        '(e.g., 50K or 4.2M)': '（例如 50K 或 4.2M）',
        '(e.g., "%(title)s.%(ext)s")': '（例如“%(title)s.%(ext)s”）',
        '(e.g., "bestvideo+bestaudio")': '（例如“bestvideo+bestaudio”）',
        '(comma-separated, e.g., "en,fr,de")': '（逗号分隔，例如“en,fr,de”）',
        '(comma-separated)': '（逗号分隔）',
        '(key:val[,val] format)': '（key:val[,val] 格式）',
        '(One argument per line or space-separated)': '（每行一个参数，或用空格分隔）',
        '(0-10, 0 = best)': '（0-10，0 为最佳）',
        'Ignore errors (--ignore-errors)': '忽略错误（--ignore-errors）',
        'Ignore warnings (--no-warnings)': '忽略警告（--no-warnings）',
        'Abort on error (--abort-on-error)': '出错时中止（--abort-on-error）',
        'Download only video, not playlist (--no-playlist)': '仅下载视频，不下载播放列表（--no-playlist）',
        'Download playlist (--yes-playlist)': '下载播放列表（--yes-playlist）',
        'Include private/unavailable videos in YouTube playlists': '包含 YouTube 播放列表中的私有/不可用视频',
        'Mark videos as watched (--mark-watched)': '将视频标记为已观看（--mark-watched）',
        'Do not mark videos as watched (--no-mark-watched)': '不要将视频标记为已观看（--no-mark-watched）',
        'Force IPv4 (--force-ipv4)': '强制使用 IPv4（--force-ipv4）',
        'Force IPv6 (--force-ipv6)': '强制使用 IPv6（--force-ipv6）',
        'Enable file:// URLs (--enable-file-urls)': '启用 file:// URL（--enable-file-urls）',
        'Bypass geo restriction (--geo-bypass)': '绕过地区限制（--geo-bypass）',
        'Do not bypass geo restriction (--no-geo-bypass)': '不绕过地区限制（--no-geo-bypass）',
        'Break on existing (--break-on-existing)': '遇到已存在文件时中断（--break-on-existing）',
        'Break on reject (--break-on-reject)': '遇到拒绝项时中断（--break-on-reject）',
        'No break on existing (--no-break-on-existing)': '遇到已存在文件时不中断（--no-break-on-existing）',
        'Do not resize buffer (--no-resize-buffer)': '不调整缓冲区大小（--no-resize-buffer）',
        'Test mode - do not download (--test)': '测试模式，不实际下载（--test）',
        'Prefer native HLS downloader (--hls-prefer-native)': '优先使用原生 HLS 下载器（--hls-prefer-native）',
        'Prefer ffmpeg for HLS (--hls-prefer-ffmpeg)': 'HLS 优先使用 ffmpeg（--hls-prefer-ffmpeg）',
        'Use MPEG-TS container for HLS (--hls-use-mpegts)': 'HLS 使用 MPEG-TS 容器（--hls-use-mpegts）',
        'Restrict filenames to ASCII (--restrict-filenames)': '将文件名限制为 ASCII（--restrict-filenames）',
        'Allow Unicode in filenames (--no-restrict-filenames)': '允许文件名使用 Unicode（--no-restrict-filenames）',
        'Create playlist subfolder for playlist downloads': '播放列表下载时创建同名文件夹',
        'Force Windows-compatible filenames (--windows-filenames)': '强制使用 Windows 兼容文件名（--windows-filenames）',
        'Do not overwrite files (--no-overwrites)': '不覆盖文件（--no-overwrites）',
        'Force overwrite files (--force-overwrites)': '强制覆盖文件（--force-overwrites）',
        'Continue partially downloaded files (--continue)': '继续下载未完成文件（--continue）',
        'Do not continue downloads (--no-continue)': '不要继续未完成下载（--no-continue）',
        'Do not use .part files (--no-part)': '不使用 .part 文件（--no-part）',
        'Do not use Last-modified header (--no-mtime)': '不使用 Last-Modified 头（--no-mtime）',
        'Write description to .description file (--write-description)': '将描述写入 .description 文件（--write-description）',
        'Write metadata to .info.json file (--write-info-json)': '将元数据写入 .info.json 文件（--write-info-json）',
        'Write annotations to .annotations.xml (--write-annotations)': '将注释写入 .annotations.xml（--write-annotations）',
        'Write comments to .comments.json (--write-comments)': '将评论写入 .comments.json（--write-comments）',
        'Disable filesystem caching (--no-cache-dir)': '禁用文件系统缓存（--no-cache-dir）',
        'Delete cache directory contents (--rm-cache-dir)': '删除缓存目录内容（--rm-cache-dir）',
        'Prefer free formats (--prefer-free-formats)': '优先自由格式（--prefer-free-formats）',
        'Check available formats (--check-formats)': '检查可用格式（--check-formats）',
        'Write subtitle file (--write-subs)': '写入字幕文件（--write-subs）',
        'Write automatic subtitle file (--write-auto-subs)': '写入自动字幕文件（--write-auto-subs）',
        'List available subtitles (--list-subs)': '列出可用字幕（--list-subs）',
        'Embed subtitles (--embed-subs)': '嵌入字幕（--embed-subs）',
        'Do not embed subtitles (--no-embed-subs)': '不嵌入字幕（--no-embed-subs）',
        'Embed thumbnail (--embed-thumbnail)': '嵌入缩略图（--embed-thumbnail）',
        'Do not embed thumbnail (--no-embed-thumbnail)': '不嵌入缩略图（--no-embed-thumbnail）',
        'Use .netrc authentication (--netrc)': '使用 .netrc 认证（--netrc）',
        'Extract audio (-x, --extract-audio)': '提取音频（-x, --extract-audio）',
        'Keep video file after conversion (--keep-video)': '转换后保留视频文件（--keep-video）',
        'Do not keep video file (--no-keep-video)': '转换后不保留视频文件（--no-keep-video）',
        'Embed metadata (--embed-metadata)': '嵌入元数据（--embed-metadata）',
        'Embed chapter markers (--embed-chapters)': '嵌入章节标记（--embed-chapters）',
        'Embed info.json (--embed-info-json)': '嵌入 info.json（--embed-info-json）',
        'Add metadata to file (--add-metadata)': '向文件添加元数据（--add-metadata）',
        'Write thumbnail image (--write-thumbnail)': '写入缩略图（--write-thumbnail）',
        'Write all thumbnail formats (--write-all-thumbnails)': '写入所有缩略图格式（--write-all-thumbnails）',
        'List available thumbnails (--list-thumbnails)': '列出可用缩略图（--list-thumbnails）',
        'Quiet mode (-q, --quiet)': '安静模式（-q, --quiet）',
        'No warnings (--no-warnings)': '不显示警告（--no-warnings）',
        'Verbose output (-v, --verbose)': '详细输出（-v, --verbose）',
        'Simulate, do not download (-s, --simulate)': '模拟模式，不下载（-s, --simulate）',
        'Skip download (--skip-download)': '跳过下载（--skip-download）',
        'Get title (--get-title)': '获取标题（--get-title）',
        'Get ID (--get-id)': '获取 ID（--get-id）',
        'Get URL (--get-url)': '获取 URL（--get-url）',
        'Get thumbnail URL (--get-thumbnail)': '获取缩略图 URL（--get-thumbnail）',
        'Get description (--get-description)': '获取描述（--get-description）',
        'Get duration (--get-duration)': '获取时长（--get-duration）',
        'Get filename (--get-filename)': '获取文件名（--get-filename）',
        'Get format (--get-format)': '获取格式（--get-format）',
        'Dump JSON info (--dump-json)': '导出 JSON 信息（--dump-json）',
        'Dump single JSON (--dump-single-json)': '导出单个 JSON（--dump-single-json）',
        'Print JSON info (--print-json)': '打印 JSON 信息（--print-json）',
        'Show progress (--progress)': '显示进度（--progress）',
        'Hide progress (--no-progress)': '隐藏进度（--no-progress）',
        'Display progress in console title (--console-title)': '在控制台标题显示进度（--console-title）',
        'Skip SSL certificate validation (--no-check-certificate)': '跳过 SSL 证书验证（--no-check-certificate）',
        'Prefer insecure connections (--prefer-insecure)': '优先不安全连接（--prefer-insecure）',
        'Bidirectional text workaround (--bidi-workaround)': '双向文本兼容处理（--bidi-workaround）',
        'Use legacy server connect (--legacy-server-connect)': '使用旧版服务器连接方式（--legacy-server-connect）',
        'Mark SponsorBlock chapters (--sponsorblock-mark)': '标记 SponsorBlock 章节（--sponsorblock-mark）',
        'Remove SponsorBlock segments (--sponsorblock-remove)': '移除 SponsorBlock 片段（--sponsorblock-remove）',
        'Disable SponsorBlock (--no-sponsorblock)': '禁用 SponsorBlock（--no-sponsorblock）',
        'Allow dynamic MPD manifests (--allow-dynamic-mpd)': '允许动态 MPD 清单（--allow-dynamic-mpd）',
        'Ignore dynamic MPD manifests (--ignore-dynamic-mpd)': '忽略动态 MPD 清单（--ignore-dynamic-mpd）',
        'Split HLS segments on discontinuity (--hls-split-discontinuity)': '在不连续处拆分 HLS 分片（--hls-split-discontinuity）',
    },
    'ru': {
        'yt-dlp GUI - Video Downloader Configuration': 'yt-dlp GUI - Настройка загрузки видео',
        'Language:': 'Язык:',
        'Video URL(s):': 'URL видео:',
        'Or Batch File:': 'Или пакетный файл:',
        'Browse...': 'Обзор...',
        'Download': 'Скачать',
        'List Formats': 'Список форматов',
        'Extract Info': 'Извлечь информацию',
        'Load Config': 'Загрузить конфиг',
        'Save Config': 'Сохранить конфиг',
        'Output Console': 'Консоль вывода',
        'Ready': 'Готово',
        'General': 'Общие',
        'Network': 'Сеть',
        'Geo-restriction': 'Гео-ограничения',
        'Video Selection': 'Выбор видео',
        'Filesystem': 'Файловая система',
        'Video Format': 'Формат видео',
        'Subtitles': 'Субтитры',
        'Authentication': 'Аутентификация',
        'Post-processing': 'Постобработка',
        'Thumbnail': 'Миниатюра',
        'Verbosity/Simulation': 'Вывод/Симуляция',
        'Workarounds': 'Обходные пути',
        'Extractor': 'Экстрактор',
        'Advanced': 'Дополнительно',
        'Generated command:': 'Сгенерированная команда:',
        'Generate Command': 'Сгенерировать команду',
        'Copy to Clipboard': 'Скопировать',
        'Running: yt-dlp ': 'Запуск: yt-dlp ',
        'Downloading...': 'Загрузка...',
        'Download completed successfully!': 'Загрузка успешно завершена!',
        'Process exited with code ': 'Процесс завершился с кодом ',
        'Command copied to clipboard!': 'Команда скопирована в буфер обмена!',
        'No URL': 'Нет URL',
        'Please enter a URL or batch file to download.': 'Введите URL или пакетный файл для загрузки.',
        'Please enter a URL.': 'Введите URL.',
        'Error': 'Ошибка',
        'Success': 'Успех',
        'Failed to save configuration: ': 'Не удалось сохранить конфигурацию: ',
        'Failed to load configuration: ': 'Не удалось загрузить конфигурацию: ',
        'Configuration loaded successfully!': 'Конфигурация успешно загружена!',
        'Configuration saved successfully!': 'Конфигурация успешно сохранена!',
        'Load Configuration': 'Загрузить конфигурацию',
        'Save Configuration': 'Сохранить конфигурацию',
        'Select Batch File': 'Выбрать пакетный файл',
        'Select Config File': 'Выбрать файл конфигурации',
        'Select Archive File': 'Выбрать файл архива',
        'Select Output Directory': 'Выбрать каталог вывода',
        'Select Info JSON': 'Выбрать Info JSON',
        'Select Cache Directory': 'Выбрать каталог кэша',
        'Select Client Certificate': 'Выбрать клиентский сертификат',
        'Select Client Certificate Key': 'Выбрать ключ клиентского сертификата',
        'Select FFmpeg Binary': 'Выбрать бинарник FFmpeg',
        'Select Cookies File': 'Выбрать файл cookies',
        'Text Files': 'Текстовые файлы',
        'All Files': 'Все файлы',
        'Config Files': 'Файлы конфигурации',
        'JSON Files': 'JSON файлы',
        'PEM Files': 'PEM файлы',
        'Key Files': 'Файлы ключей',
        'Executable Files': 'Исполняемые файлы',
    },
    'ja': {
        'yt-dlp GUI - Video Downloader Configuration': 'yt-dlp GUI - 動画ダウンロード設定',
        'Language:': '言語:',
        'Video URL(s):': '動画 URL:',
        'Or Batch File:': 'または一括ファイル:',
        'Browse...': '参照...',
        'Download': 'ダウンロード',
        'List Formats': '形式一覧',
        'Extract Info': '情報抽出',
        'Load Config': '設定読込',
        'Save Config': '設定保存',
        'Output Console': '出力コンソール',
        'Ready': '準備完了',
        'General': '一般',
        'Network': 'ネットワーク',
        'Geo-restriction': '地域制限',
        'Video Selection': '動画選択',
        'Filesystem': 'ファイルシステム',
        'Video Format': '動画形式',
        'Subtitles': '字幕',
        'Authentication': '認証',
        'Post-processing': '後処理',
        'Thumbnail': 'サムネイル',
        'Verbosity/Simulation': '出力/シミュレーション',
        'Workarounds': '回避策',
        'Extractor': '抽出',
        'Advanced': '詳細',
        'Generated command:': '生成コマンド:',
        'Generate Command': 'コマンド生成',
        'Copy to Clipboard': 'クリップボードにコピー',
        'Running: yt-dlp ': '実行中: yt-dlp ',
        'Downloading...': 'ダウンロード中...',
        'Download completed successfully!': 'ダウンロードが正常に完了しました！',
        'Process exited with code ': 'プロセス終了コード: ',
        'Command copied to clipboard!': 'コマンドをクリップボードにコピーしました！',
        'No URL': 'URL なし',
        'Please enter a URL or batch file to download.': 'ダウンロードする URL または一括ファイルを入力してください。',
        'Please enter a URL.': 'URL を入力してください。',
        'Error': 'エラー',
        'Success': '成功',
        'Failed to save configuration: ': '設定の保存に失敗しました: ',
        'Failed to load configuration: ': '設定の読み込みに失敗しました: ',
        'Configuration loaded successfully!': '設定を読み込みました！',
        'Configuration saved successfully!': '設定を保存しました！',
        'Text Files': 'テキストファイル',
        'All Files': 'すべてのファイル',
        'Config Files': '設定ファイル',
        'JSON Files': 'JSON ファイル',
        'PEM Files': 'PEM ファイル',
        'Key Files': '鍵ファイル',
        'Executable Files': '実行ファイル',
    },
    'ko': {
        'yt-dlp GUI - Video Downloader Configuration': 'yt-dlp GUI - 비디오 다운로드 설정',
        'Language:': '언어:',
        'Video URL(s):': '비디오 URL:',
        'Or Batch File:': '또는 배치 파일:',
        'Browse...': '찾아보기...',
        'Download': '다운로드',
        'List Formats': '포맷 목록',
        'Extract Info': '정보 추출',
        'Load Config': '설정 불러오기',
        'Save Config': '설정 저장',
        'Output Console': '출력 콘솔',
        'Ready': '준비됨',
        'General': '일반',
        'Network': '네트워크',
        'Geo-restriction': '지역 제한',
        'Video Selection': '비디오 선택',
        'Filesystem': '파일 시스템',
        'Video Format': '비디오 형식',
        'Subtitles': '자막',
        'Authentication': '인증',
        'Post-processing': '후처리',
        'Thumbnail': '썸네일',
        'Verbosity/Simulation': '출력/시뮬레이션',
        'Workarounds': '우회 설정',
        'Extractor': '추출기',
        'Advanced': '고급',
        'Generated command:': '생성된 명령:',
        'Generate Command': '명령 생성',
        'Copy to Clipboard': '클립보드에 복사',
        'Running: yt-dlp ': '실행 중: yt-dlp ',
        'Downloading...': '다운로드 중...',
        'Download completed successfully!': '다운로드가 성공적으로 완료되었습니다!',
        'Process exited with code ': '프로세스 종료 코드: ',
        'Command copied to clipboard!': '명령이 클립보드에 복사되었습니다!',
        'No URL': 'URL 없음',
        'Please enter a URL or batch file to download.': '다운로드할 URL 또는 배치 파일을 입력하세요.',
        'Please enter a URL.': 'URL을 입력하세요.',
        'Error': '오류',
        'Success': '성공',
        'Failed to save configuration: ': '설정 저장 실패: ',
        'Failed to load configuration: ': '설정 불러오기 실패: ',
        'Configuration loaded successfully!': '설정을 성공적으로 불러왔습니다!',
        'Configuration saved successfully!': '설정을 성공적으로 저장했습니다!',
        'Text Files': '텍스트 파일',
        'All Files': '모든 파일',
        'Config Files': '설정 파일',
        'JSON Files': 'JSON 파일',
        'PEM Files': 'PEM 파일',
        'Key Files': '키 파일',
        'Executable Files': '실행 파일',
    },
    'es': {
        'yt-dlp GUI - Video Downloader Configuration': 'yt-dlp GUI - Configuración de descarga de video',
        'Language:': 'Idioma:',
        'Video URL(s):': 'URL(s) de video:',
        'Or Batch File:': 'O archivo por lotes:',
        'Browse...': 'Examinar...',
        'Download': 'Descargar',
        'List Formats': 'Listar formatos',
        'Extract Info': 'Extraer información',
        'Load Config': 'Cargar config',
        'Save Config': 'Guardar config',
        'Output Console': 'Consola de salida',
        'Ready': 'Listo',
        'General': 'General',
        'Network': 'Red',
        'Geo-restriction': 'Restricción geográfica',
        'Video Selection': 'Selección de video',
        'Filesystem': 'Sistema de archivos',
        'Video Format': 'Formato de video',
        'Subtitles': 'Subtítulos',
        'Authentication': 'Autenticación',
        'Post-processing': 'Posprocesado',
        'Thumbnail': 'Miniatura',
        'Verbosity/Simulation': 'Salida/Simulación',
        'Workarounds': 'Soluciones',
        'Extractor': 'Extractor',
        'Advanced': 'Avanzado',
        'Generated command:': 'Comando generado:',
        'Generate Command': 'Generar comando',
        'Copy to Clipboard': 'Copiar al portapapeles',
        'Running: yt-dlp ': 'Ejecutando: yt-dlp ',
        'Downloading...': 'Descargando...',
        'Download completed successfully!': '¡Descarga completada con éxito!',
        'Process exited with code ': 'El proceso terminó con código ',
        'Command copied to clipboard!': '¡Comando copiado al portapapeles!',
        'No URL': 'Sin URL',
        'Please enter a URL or batch file to download.': 'Introduce una URL o un archivo por lotes para descargar.',
        'Please enter a URL.': 'Introduce una URL.',
        'Error': 'Error',
        'Success': 'Éxito',
        'Failed to save configuration: ': 'No se pudo guardar la configuración: ',
        'Failed to load configuration: ': 'No se pudo cargar la configuración: ',
        'Configuration loaded successfully!': '¡Configuración cargada correctamente!',
        'Configuration saved successfully!': '¡Configuración guardada correctamente!',
        'Text Files': 'Archivos de texto',
        'All Files': 'Todos los archivos',
        'Config Files': 'Archivos de configuración',
        'JSON Files': 'Archivos JSON',
        'PEM Files': 'Archivos PEM',
        'Key Files': 'Archivos de clave',
        'Executable Files': 'Archivos ejecutables',
    },
    'fr': {
        'yt-dlp GUI - Video Downloader Configuration': 'yt-dlp GUI - Configuration du telechargement video',
        'Language:': 'Langue :',
        'Video URL(s):': 'URL(s) video :',
        'Or Batch File:': 'Ou fichier batch :',
        'Browse...': 'Parcourir...',
        'Download': 'Telecharger',
        'List Formats': 'Lister les formats',
        'Extract Info': 'Extraire les infos',
        'Load Config': 'Charger la config',
        'Save Config': 'Enregistrer la config',
        'Output Console': 'Console de sortie',
        'Ready': 'Pret',
        'General': 'General',
        'Network': 'Reseau',
        'Geo-restriction': 'Restriction geo',
        'Video Selection': 'Selection video',
        'Filesystem': 'Systeme de fichiers',
        'Video Format': 'Format video',
        'Subtitles': 'Sous-titres',
        'Authentication': 'Authentification',
        'Post-processing': 'Post-traitement',
        'Thumbnail': 'Miniature',
        'Verbosity/Simulation': 'Sortie/Simulation',
        'Workarounds': 'Contournements',
        'Extractor': 'Extracteur',
        'Advanced': 'Avance',
        'Generated command:': 'Commande generee :',
        'Generate Command': 'Generer la commande',
        'Copy to Clipboard': 'Copier dans le presse-papiers',
        'Running: yt-dlp ': 'Execution : yt-dlp ',
        'Downloading...': 'Telechargement...',
        'Download completed successfully!': 'Telechargement termine avec succes !',
        'Process exited with code ': 'Le processus s est termine avec le code ',
        'Command copied to clipboard!': 'Commande copiée dans le presse-papiers !',
        'No URL': 'Pas d URL',
        'Please enter a URL or batch file to download.': 'Saisissez une URL ou un fichier batch a telecharger.',
        'Please enter a URL.': 'Saisissez une URL.',
        'Error': 'Erreur',
        'Success': 'Succes',
        'Failed to save configuration: ': 'Echec de l enregistrement de la configuration : ',
        'Failed to load configuration: ': 'Echec du chargement de la configuration : ',
        'Configuration loaded successfully!': 'Configuration chargee avec succes !',
        'Configuration saved successfully!': 'Configuration enregistree avec succes !',
        'Text Files': 'Fichiers texte',
        'All Files': 'Tous les fichiers',
        'Config Files': 'Fichiers de configuration',
        'JSON Files': 'Fichiers JSON',
        'PEM Files': 'Fichiers PEM',
        'Key Files': 'Fichiers de cle',
        'Executable Files': 'Fichiers executables',
    },
    'de': {
        'yt-dlp GUI - Video Downloader Configuration': 'yt-dlp GUI - Video-Download-Konfiguration',
        'Language:': 'Sprache:',
        'Video URL(s):': 'Video-URL(s):',
        'Or Batch File:': 'Oder Batch-Datei:',
        'Browse...': 'Durchsuchen...',
        'Download': 'Herunterladen',
        'List Formats': 'Formate auflisten',
        'Extract Info': 'Infos extrahieren',
        'Load Config': 'Konfig laden',
        'Save Config': 'Konfig speichern',
        'Output Console': 'Ausgabekonsole',
        'Ready': 'Bereit',
        'General': 'Allgemein',
        'Network': 'Netzwerk',
        'Geo-restriction': 'Geobeschraenkung',
        'Video Selection': 'Videoauswahl',
        'Filesystem': 'Dateisystem',
        'Video Format': 'Videoformat',
        'Subtitles': 'Untertitel',
        'Authentication': 'Authentifizierung',
        'Post-processing': 'Nachbearbeitung',
        'Thumbnail': 'Vorschaubild',
        'Verbosity/Simulation': 'Ausgabe/Simulation',
        'Workarounds': 'Workarounds',
        'Extractor': 'Extraktor',
        'Advanced': 'Erweitert',
        'Generated command:': 'Generierter Befehl:',
        'Generate Command': 'Befehl erzeugen',
        'Copy to Clipboard': 'In Zwischenablage kopieren',
        'Running: yt-dlp ': 'Wird ausgefuehrt: yt-dlp ',
        'Downloading...': 'Lade herunter...',
        'Download completed successfully!': 'Download erfolgreich abgeschlossen!',
        'Parse Playlist': 'Playlist parsen',
        'Stop': 'Stopp',
        'Process exited with code ': 'Prozess beendet mit Code ',
        'Command copied to clipboard!': 'Befehl in die Zwischenablage kopiert!',
        'No URL': 'Keine URL',
        'Please enter a URL or batch file to download.': 'Bitte gib eine URL oder Batch-Datei zum Herunterladen ein.',
        'Please enter a URL.': 'Bitte gib eine URL ein.',
        'Error': 'Fehler',
        'Success': 'Erfolg',
        'Failed to save configuration: ': 'Konfiguration konnte nicht gespeichert werden: ',
        'Failed to load configuration: ': 'Konfiguration konnte nicht geladen werden: ',
        'Configuration loaded successfully!': 'Konfiguration erfolgreich geladen!',
        'Configuration saved successfully!': 'Konfiguration erfolgreich gespeichert!',
        'Text Files': 'Textdateien',
        'All Files': 'Alle Dateien',
        'Config Files': 'Konfigurationsdateien',
        'JSON Files': 'JSON-Dateien',
        'PEM Files': 'PEM-Dateien',
        'Key Files': 'Schluesseldateien',
        'Executable Files': 'Ausfuehrbare Dateien',
    },
}


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

        # Configuration storage
        self.config = {}
        self.config_file = os.path.expanduser('~/.yt-dlp-gui-config.json')
        self.load_config()
        self.current_language = self.initialize_language()
        
        # Thread-safe logging initialization
        import queue
        self.log_queue = queue.Queue()
        self._start_log_watcher()

        # Create main container
        self.create_widgets()
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
        translations = TRANSLATIONS.get(self.current_language, {})
        return translations.get(text, text)

    def translate_concat(self, prefix, value):
        """Translate a message prefix while preserving dynamic data."""
        return f'{self.tr(prefix)}{value}'

    def detect_system_language(self):
        """Detect the preferred system language and map it to a supported locale."""
        candidates = []
        try:
            lang, _ = locale.getlocale()
            if lang:
                candidates.append(lang)
        except Exception:
            pass

        for env_name in ('LC_ALL', 'LC_MESSAGES', 'LANG'):
            value = os.environ.get(env_name)
            if value:
                candidates.append(value)

        for candidate in candidates:
            normalized = candidate.replace('-', '_').lower()
            prefix = normalized.split('_', 1)[0]
            if prefix in LANGUAGE_OPTIONS:
                return prefix
        return 'en'

    def initialize_language(self):
        """Detect and persist the initial language only on the first launch."""
        if self.config.get('language_initialized'):
            language = self.config.get('language', 'en')
            return language if language in LANGUAGE_OPTIONS else 'en'

        language = self.detect_system_language()
        self.config['language'] = language
        self.config['language_initialized'] = True
        self.write_config_to_disk(self.config)
        return language

    def write_config_to_disk(self, config):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

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
        self.root.title(self.tr(self.base_title))

        if hasattr(self, 'language_label'):
            self.language_label.config(text=self.tr('Language:'))
        if hasattr(self, 'language_selector'):
            self.language_selector.set(self.get_language_display(self.current_language))
        if hasattr(self, 'status_var') and not self.status_var.get():
            self.status_var.set(self.tr('Ready'))

        self.localize_widget_tree(self.root)
        self.localize_notebook_tabs()

    def localize_widget_tree(self, widget):
        try:
            text = widget.cget('text')
        except tk.TclError:
            text = None

        if text is not None:
            if widget not in self._translatable_widgets:
                self._translatable_widgets[widget] = text
            widget.config(text=self.tr(self._translatable_widgets[widget]))

        for child in widget.winfo_children():
            self.localize_widget_tree(child)

    def localize_notebook_tabs(self):
        if not hasattr(self, 'notebook'):
            return
        for tab_id in self.notebook.tabs():
            child = self.root.nametowidget(tab_id)
            if child not in self._notebook_tab_texts:
                self._notebook_tab_texts[child] = self.notebook.tab(tab_id, 'text')
            self.notebook.tab(tab_id, text=self.tr(self._notebook_tab_texts[child]))

    def on_language_changed(self, _event=None):
        new_language = self.get_language_code_from_display(self.language_var.get())
        if new_language == self.current_language:
            return
        self.log_message(f'[DEBUG] GUI Language changing to {new_language}')
        self.current_language = new_language
        
        # ABSOLUTE UNIFICATION
        self.unify_languages()
                
        self.apply_localization()
        self.status_var.set(self.tr('Ready'))
        self.save_config(silent=True)

    def maximize_window(self):
        """Open the window in a maximized state with a geometry fallback."""
        self.root.update_idletasks()
        try:
            self.root.state('zoomed')
            return
        except tk.TclError:
            pass

        try:
            self.root.attributes('-zoomed', True)
            return
        except tk.TclError:
            pass

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f'{screen_width}x{screen_height}+0+0')

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
            self.root.after(100, lambda: self.playlist_canvas.configure(scrollregion=self.playlist_canvas.bbox('all')))

    def register_stateful_controls(self, attribute_names):
        """Track GUI-only controls so they can be serialized independently."""
        for name in attribute_names:
            value = getattr(self, name, None)
            if isinstance(value, (tk.BooleanVar, ttk.Entry, ttk.Combobox, scrolledtext.ScrolledText)):
                self._stateful_controls[name] = value

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

    def create_widgets(self):
        """Create all GUI widgets"""
        before_names = set(self.__dict__)
        # Top frame for URL input and quick actions
        top_frame = ttk.Frame(self.root, padding='10')
        top_frame.pack(fill=tk.X, side=tk.TOP)

        self.language_var = tk.StringVar(value=self.get_language_display(self.current_language))
        self.language_label = ttk.Label(top_frame, text='Language:')
        self.language_label.grid(row=0, column=2, sticky=tk.E, pady=5, padx=(20, 5))
        self.language_selector = ttk.Combobox(
            top_frame,
            width=16,
            textvariable=self.language_var,
            values=list(LANGUAGE_OPTIONS.values()),
            state='readonly')
        self.language_selector.grid(row=0, column=3, sticky=tk.W, pady=5)
        self.language_selector.bind('<<ComboboxSelected>>', self.on_language_changed)

        # URL input
        self.paste_url_btn = ttk.Button(top_frame, text='Paste Link:', command=self.paste_url_from_clipboard)
        self.paste_url_btn.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(top_frame, width=80)
        self.url_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        top_frame.columnconfigure(1, weight=1)

        # Batch file option
        ttk.Label(top_frame, text='Or Batch File:').grid(row=1, column=0, sticky=tk.W, pady=5)
        batch_frame = ttk.Frame(top_frame)
        batch_frame.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        self.batch_file_entry = ttk.Entry(batch_frame)
        self.batch_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(batch_frame, text='Browse...', command=self.browse_batch_file).pack(side=tk.LEFT, padx=(5, 0))

        # Quick action buttons
        button_frame = ttk.Frame(top_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        self.download_btn = ttk.Button(button_frame, text='Download', command=self.on_download_btn_click, width=15)
        self.download_btn.pack(side=tk.LEFT, padx=5)
        self.playlist_btn = ttk.Button(button_frame, text='Parse Playlist', command=self.parse_playlist, width=15)
        self.playlist_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='List Formats', command=self.list_formats, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='Extract Info', command=self.extract_info, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='Load Config', command=self.load_config_dialog, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='Save Config', command=self.save_config_dialog, width=15).pack(side=tk.LEFT, padx=5)

        # Separator
        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=5)

        # Notebook for tabbed options
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)

        # Register tabs for lazy creation
        general_frame = self.add_lazy_tab('general', 'General', self.create_general_tab)
        self.playlist_tab_frame = self.create_playlist_tab()
        self.notebook.add(self.playlist_tab_frame, text='Playlist')
        self._built_tabs.add(self.playlist_tab_frame)
        self._notebook_tab_texts[self.playlist_tab_frame] = 'Playlist'
        
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
        
        self.ensure_tab_built(general_frame)
        self._active_tab_frame = general_frame

        # Output console at bottom
        console_frame = ttk.LabelFrame(self.root, text='Output Console', padding='5')
        console_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=(0, 10), ipady=5)

        self.console = scrolledtext.ScrolledText(console_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.console.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_var = tk.StringVar(value='Ready')
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_var.set(self.tr('Ready'))
        self.register_stateful_controls(set(self.__dict__) - before_names)

    def create_playlist_tab(self, frame=None):
        """Create Playlist Select tab using efficient Treeview"""
        frame = frame or ttk.Frame(self.notebook, padding='10')

        # Top control frame
        top_ctrl = ttk.Frame(frame)
        top_ctrl.pack(fill=tk.X, pady=(0, 5))
        
        self.playlist_select_all_var = tk.BooleanVar(value=True)
        self.playlist_all_btn = ttk.Checkbutton(
            top_ctrl, 
            text="Select All / Deselect All", 
            variable=self.playlist_select_all_var, 
            command=self._on_playlist_select_all
        )
        self.playlist_all_btn.pack(side=tk.LEFT)
        self.register_translatable_widget(self.playlist_all_btn, 'Select All / Deselect All')

        self.playlist_reverse_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            top_ctrl,
            text="Reverse order",
            variable=self.playlist_reverse_var,
            command=self._on_playlist_option_changed
        ).pack(side=tk.LEFT, padx=(20, 0))
        self.register_translatable_widget(top_ctrl.winfo_children()[1], 'Reverse order')

        self.playlist_exclude_private_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            top_ctrl,
            text="Exclude private videos",
            variable=self.playlist_exclude_private_var,
            command=self._on_playlist_option_changed
        ).pack(side=tk.LEFT, padx=(20, 0))
        self.register_translatable_widget(top_ctrl.winfo_children()[2], 'Exclude private videos')
        
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

    def _on_playlist_select_all(self):
        state = '☑' if self.playlist_select_all_var.get() else '☐'
        for item in self.playlist_tree.get_children():
            values = list(self.playlist_tree.item(item, 'values'))
            values[0] = state
            self.playlist_tree.item(item, values=values)

    def _on_playlist_mousewheel(self, event):
        # Only scroll if the playlist tab is active
        if self.notebook.select() == str(self.playlist_tab_frame):
            if event.num == 4: # Linux scroll up
                self.playlist_canvas.yview_scroll(-1, "units")
            elif event.num == 5: # Linux scroll down
                self.playlist_canvas.yview_scroll(1, "units")
            else: # Windows/Mac
                self.playlist_canvas.yview_scroll(int(-1*(event.delta)), "units")

    def _on_playlist_option_changed(self):
        if hasattr(self, 'playlist_entries_data') and self.playlist_entries_data:
            self.root.after(0, self._show_playlist_tab, "Playlist")

    def _on_playlist_select_all(self):
        state = self.playlist_select_all_var.get()
        if hasattr(self, 'playlist_video_vars'):
            for var in self.playlist_video_vars.values():
                var.set(state)

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
        """Create SponsorBlock Options tab"""
        frame = frame or ttk.Frame(self.notebook, padding='10')

        row = 0

        self.sponsorblock_mark = tk.BooleanVar()
        ttk.Checkbutton(frame, text='Mark SponsorBlock chapters (--sponsorblock-mark)',
                        variable=self.sponsorblock_mark).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        self.sponsorblock_remove = tk.BooleanVar()
        ttk.Checkbutton(frame, text='Remove SponsorBlock segments (--sponsorblock-remove)',
                        variable=self.sponsorblock_remove).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Label(frame, text='SponsorBlock categories to remove:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.sponsorblock_remove_cats = ttk.Entry(frame, width=50)
        self.sponsorblock_remove_cats.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(frame, text='(comma-separated)').grid(row=row, column=2, sticky=tk.W, pady=5)
        row += 1

        ttk.Label(frame, text='SponsorBlock categories to mark:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.sponsorblock_mark_cats = ttk.Entry(frame, width=50)
        self.sponsorblock_mark_cats.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(frame, text='(comma-separated)').grid(row=row, column=2, sticky=tk.W, pady=5)
        row += 1

        ttk.Label(frame, text='SponsorBlock chapter title:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.sponsorblock_chapter_title = ttk.Entry(frame, width=40)
        self.sponsorblock_chapter_title.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        self.no_sponsorblock = tk.BooleanVar()
        ttk.Checkbutton(frame, text='Disable SponsorBlock (--no-sponsorblock)',
                        variable=self.no_sponsorblock).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Label(frame, text='SponsorBlock API URL:').grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.sponsorblock_api = ttk.Entry(frame, width=50)
        self.sponsorblock_api.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

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
        self.log_message(f'[DEBUG] Unifying languages: GUI({self.current_language}) -> Metadata({target_code})')
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
        if self.sponsorblock_remove_cats.get():
            args.extend(['--sponsorblock-remove', self.sponsorblock_remove_cats.get()])
        if self.sponsorblock_mark_cats.get():
            args.extend(['--sponsorblock-mark', self.sponsorblock_mark_cats.get()])
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
            args.extend(['-a', batch_file])
        elif url:
            args.append(url)

        return args

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
        has_vars = hasattr(self, 'playlist_video_vars')
        self.log_message(f'[DEBUG] playlist_parsed_url={playlist_parsed_url!r}, url_match={playlist_parsed_url == url}, has_vars={has_vars}')
        
        tasks = []
        if hasattr(self, 'playlist_tree'):
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
                        if arg in ('--playlist-items', '--playlist-reverse', '--no-playlist-reverse', '-o', '-P', '--paths'):
                            if arg in ('--playlist-items', '-o', '-P', '--paths'):
                                skip = True
                            continue
                        task_args.append(arg)
                    filename_tpl = f'{visual_idx:03d} - {gui_title}.%(ext)s'
                    # Remove unsave characters
                    filename_tpl = "".join([c for c in filename_tpl if c not in '<>:"/\\|?*']).strip()
                    
                    out_path = os.path.join(output_dir, filename_tpl) if output_dir else filename_tpl
                    task_args.extend(['--playlist-items', str(original_idx)])
                    task_args.extend(['-o', out_path])
                    tasks.append((visual_idx, task_args))
            self.log_message(f'[DEBUG] tasks built: {len(tasks)} selected')
        else:
            self.log_message('[DEBUG] single video / batch mode')
            tasks.append(('Single', base_args))

        if not tasks:
            self.log_message('[DEBUG] no tasks — showing warning')
            messagebox.showwarning(self.tr('No Selection'), self.tr('Please select videos.'))
            self._restore_download_button()
            return

        self.log_message(f'[DEBUG] launching thread with {len(tasks)} tasks')
        self.console.config(state=tk.NORMAL)
        self.console.delete('1.0', tk.END)
        self.console.config(state=tk.DISABLED)

        thread = threading.Thread(target=self.run_ytdlp, args=(tasks,), daemon=True)
        thread.start()
        self.log_message('[DEBUG] thread started')

    def parse_playlist(self):
        url = self.url_entry.get().strip()
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
                    self.root.after(0, self._show_playlist_tab, info.get('title', 'Playlist'))
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
        """Internal method to update the console text widget"""
        self.console.config(state=tk.NORMAL)
        self.console.insert(tk.END, message + '\n')
        self.console.see(tk.END)
        self.console.config(state=tk.DISABLED)

    def log_message(self, message):
        """Add message to the thread-safe queue"""
        if hasattr(self, 'log_queue'):
            self.log_queue.put(str(message))
        else:
            # Fallback for early calls
            print(message)

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
    root = tk.Tk()
    app = YtDlpGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
