"""Download execution logic using yt-dlp Python API"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any

import json
import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox

if TYPE_CHECKING:
    pass


class DownloaderMixin:
    """Mixin for download execution using YoutubeDL API. Requires YtDlpGUI base class."""

    if TYPE_CHECKING:
        # Core methods and attributes
        tr: Any
        translate_concat: Any
        status_var: Any
        progress_var: Any
        console: Any
        download_btn: Any
        _translatable_widgets: Any
        url_entry: Any
        batch_file_entry: Any
        output_dir: Any
        playlist_parsed_url: Any
        playlist_tree: Any
        vis_to_orig: Any
        current_playlist_metadata_title: Any
        playlist_subdir: Any
        ensure_all_tabs_built: Any
        root: Any
        url_var: Any
        save_config: Any
        current_language: Any
        # All GUI control variables (simplified - add more as needed)
        metadata_lang: Any
        ignore_errors: Any
        no_warnings: Any
        abort_on_error: Any
        no_playlist: Any
        yes_playlist: Any
        include_private_videos: Any
        mark_watched: Any
        no_mark_watched: Any
        default_search: Any
        config_location: Any
        extract_flat: Any
        age_limit: Any
        download_archive: Any
        max_downloads: Any
        proxy: Any
        socket_timeout: Any
        source_address: Any
        force_ipv4: Any
        force_ipv6: Any
        enable_file_urls: Any
        sleep_interval: Any
        max_sleep_interval: Any
        sleep_interval_requests: Any
        sleep_interval_subtitles: Any
        rate_limit: Any
        throttled_rate: Any
        retries: Any
        fragment_retries: Any
        geo_verification_proxy: Any
        geo_bypass: Any
        no_geo_bypass: Any
        geo_bypass_country: Any
        geo_bypass_ip_block: Any
        playlist_items: Any
        playlist_start: Any
        playlist_end: Any
        match_title: Any
        reject_title: Any
        min_filesize: Any
        max_filesize: Any
        date: Any
        datebefore: Any
        dateafter: Any
        min_views: Any
        max_views: Any
        match_filter: Any
        break_on_existing: Any
        break_on_reject: Any
        no_break_on_existing: Any
        concurrent_fragments: Any
        limit_rate: Any
        buffer_size: Any
        http_chunk_size: Any
        no_resize_buffer: Any
        test: Any
        external_downloader: Any
        external_downloader_args: Any
        hls_prefer_native: Any
        hls_prefer_ffmpeg: Any
        hls_use_mpegts: Any
        output_template: Any
        paths: Any
        restrict_filenames: Any
        no_restrict_filenames: Any
        windows_filenames: Any
        no_overwrites: Any
        force_overwrites: Any
        continue_dl: Any
        no_continue: Any
        no_part: Any
        no_mtime: Any
        write_description: Any
        write_info_json: Any
        write_annotations: Any
        # Video format options
        video_format: Any
        format_sort: Any
        video_quality: Any
        audio_quality: Any
        prefer_free_formats: Any
        all_formats: Any
        prefer_avc: Any
        # Subtitle options
        write_subtitles: Any
        write_auto_subs: Any
        subtitles_langs: Any
        subtitles_format: Any
        embed_subs: Any
        # Audio options
        extract_audio: Any
        audio_format: Any
        audio_quality: Any
        keep_video: Any
        # Post-processing options
        write_thumbnail: Any
        list_thumbnails: Any
        embed_thumbnail: Any
        add_metadata: Any
        parse_metadata: Any
        xattrs: Any
        fixup_policy: Any
        prefer_ffmpeg: Any
        ffmpeg_location: Any
        exec_before_dl: Any
        exec_after_dl: Any
        convert_subs: Any
        # Thumbnail options
        embed_thumbnail: Any
        # More...
        ffmpeg_location: Any
        preferred_hls: Any
        preferred_dash: Any
        remux_video: Any
        recode_video: Any
        sponsorblock_mark: Any
        sponsorblock_remove: Any
        sponsorblock_chapter_title: Any
        sponsorblock_api: Any
        no_sponsorblock: Any
        sb_remove_vars: Any
        sb_mark_vars: Any
        extractor_args: Any
        extractor_retries: Any
        allow_dynamic_mpd: Any
        ignore_dynamic_mpd: Any
        hls_split_discontinuity: Any
        cookies_from_browser: Any
        cookies: Any
        # Quiet/Verbose
        quiet: Any
        verbose: Any
        # Authentication
        username: Any
        password: Any
        twofactor: Any
        netrc: Any
        netrc_location: Any
        video_password: Any
        ap_username: Any
        ap_password: Any
        ap_mso: Any
        client_certificate: Any
        client_certificate_key: Any
        client_certificate_password: Any

    def __init__(self):
        self._ydl = None
        self._stop_requested = False

    def build_ydl_opts(self) -> dict:
        """Build yt-dlp options dictionary from GUI settings"""
        self.ensure_all_tabs_built()
        opts = {}

        # 1. 统一语言映射逻辑
        lang_map = {
            'zh': 'zh-CN', 'en': 'en', 'ru': 'ru', 'ja': 'ja', 
            'ko': 'ko', 'es': 'es', 'fr': 'fr', 'de': 'de'
        }
        gui_lang_code = getattr(self, 'current_language', 'zh')
        lang_to_use = lang_map.get(gui_lang_code, 'zh-CN')

        # 2. 从界面选择中提取语言代码
        if hasattr(self, 'metadata_lang') and self.metadata_lang.get():
            val = self.metadata_lang.get()
            if val and val != self.tr('Default (Auto)'):
                lang_to_use = val.split('(')[-1].split(')')[0] if '(' in val else val

        # 3. 构建 extractor_args
        # 修复：同时为 youtube 和 youtube:tab (播放列表) 设置语言
        final_extractor_args = {}
        
        if lang_to_use:
            # 确保使用完整的语言代码，并包装在列表中，防止 yt-dlp 将其迭代为单个字符(如 'z')
            final_extractor_args['youtube'] = {'lang': [lang_to_use]}
            final_extractor_args['youtube:tab'] = {'lang': [lang_to_use]}


        if hasattr(self, 'extractor_args') and hasattr(self.extractor_args, 'get'):
            raw_args = self.extractor_args.get().strip()
            # 格式解析：extractor:param=val
            if raw_args:
                for pair in raw_args.split():
                    if ':' in pair:
                        ext_key, remainder = pair.split(':', 1)
                        if ext_key not in final_extractor_args:
                            final_extractor_args[ext_key] = {}
                        
                        if '=' in remainder:
                            param_key, param_val = remainder.split('=', 1)
                            # yt-dlp API 期望参数值是一个列表
                            if param_key not in final_extractor_args[ext_key]:
                                final_extractor_args[ext_key][param_key] = []
                            if isinstance(final_extractor_args[ext_key][param_key], list):
                                final_extractor_args[ext_key][param_key].append(param_val)
                            else:
                                # Fallback if it was already set by lang logic as a single-element list
                                final_extractor_args[ext_key][param_key] = [param_val]
                        else:
                            # 只有 key:param 形式，没有 =val
                            final_extractor_args[ext_key][remainder] = [True]
        
        if final_extractor_args:
            opts['extractor_args'] = final_extractor_args

        # HTTP headers
        opts['http_headers'] = {'Accept-Language': f'{lang_to_use},zh;q=0.9,en-US;q=0.8,en;q=0.7'}

        # General options
        if self.ignore_errors.get():
            opts['ignoreerrors'] = True
        if self.no_warnings.get():
            opts['no_warnings'] = True
        if self.abort_on_error.get():
            opts['abort_on_error'] = True
        if self.no_playlist.get():
            opts['noplaylist'] = True
        if self.yes_playlist.get():
            opts['yesplaylist'] = True
        if not self.include_private_videos.get():
            opts['compat_opts'] = ['no-youtube-unavailable-videos']
        if self.mark_watched.get():
            opts['mark_watched'] = True
        if self.no_mark_watched.get():
            opts['mark_watched'] = False

        if self.default_search.get():
            opts['default_search'] = self.default_search.get()
        if self.extract_flat.get():
            opts['extract_flat'] = self.extract_flat.get()
        if self.age_limit.get():
            opts['age_limit'] = int(self.age_limit.get())
        if self.download_archive.get():
            opts['download_archive'] = self.download_archive.get()
        if self.max_downloads.get():
            opts['max_downloads'] = int(self.max_downloads.get())

        # Network options
        if self.proxy.get():
            opts['proxy'] = self.proxy.get()
        if self.socket_timeout.get():
            opts['socket_timeout'] = int(self.socket_timeout.get())
        if self.source_address.get():
            opts['source_address'] = self.source_address.get()
        if self.force_ipv4.get():
            opts['force_ipv4'] = True
        if self.force_ipv6.get():
            opts['force_ipv6'] = True
        if self.enable_file_urls.get():
            opts['enable_file_urls'] = True
        if self.sleep_interval.get():
            opts['sleep_interval'] = int(self.sleep_interval.get())
        if self.max_sleep_interval.get():
            opts['max_sleep_interval'] = int(self.max_sleep_interval.get())
        if self.sleep_interval_requests.get():
            opts['sleep_interval_requests'] = int(self.sleep_interval_requests.get())
        if self.sleep_interval_subtitles.get():
            opts['sleep_interval_subtitles'] = int(self.sleep_interval_subtitles.get())
        if self.rate_limit.get():
            opts['ratelimit'] = self.rate_limit.get()
        if self.throttled_rate.get():
            opts['throttledratelimit'] = self.throttled_rate.get()
        if self.retries.get():
            opts['retries'] = self.retries.get()
        if self.fragment_retries.get():
            opts['fragment_retries'] = self.fragment_retries.get()

        # Geo-restriction
        if self.geo_verification_proxy.get():
            opts['geo_verification_proxy'] = self.geo_verification_proxy.get()
        if self.geo_bypass.get():
            opts['geo_bypass'] = True
        if self.no_geo_bypass.get():
            opts['geo_bypass'] = False
        if self.geo_bypass_country.get():
            opts['geo_bypass_country'] = self.geo_bypass_country.get()
        if self.geo_bypass_ip_block.get():
            opts['geo_bypass_ip_block'] = self.geo_bypass_ip_block.get()

        # Video selection
        if self.playlist_items.get():
            opts['playlist_items'] = self.playlist_items.get()
        if self.playlist_start.get():
            opts['playliststart'] = int(self.playlist_start.get())
        if self.playlist_end.get():
            opts['playlistend'] = int(self.playlist_end.get())
        if self.match_title.get():
            opts['matchtitle'] = self.match_title.get()
        if self.reject_title.get():
            opts['rejecttitle'] = self.reject_title.get()
        if self.min_filesize.get():
            opts['min_filesize'] = self.min_filesize.get()
        if self.max_filesize.get():
            opts['max_filesize'] = self.max_filesize.get()
        if self.date.get():
            from yt_dlp.utils import DateRange
            opts['daterange'] = DateRange(self.date.get(), self.date.get())
        if self.datebefore.get():
            opts['datebefore'] = self.datebefore.get()
        if self.dateafter.get():
            opts['dateafter'] = self.dateafter.get()
        if self.min_views.get():
            opts['min_views'] = int(self.min_views.get())
        if self.max_views.get():
            opts['max_views'] = int(self.max_views.get())
        if self.match_filter.get():
            opts['match_filter'] = self.match_filter.get()
        if self.break_on_existing.get():
            opts['break_on_existing'] = True
        if self.break_on_reject.get():
            opts['break_on_reject'] = True

        # Download options
        if self.concurrent_fragments.get():
            opts['concurrent_fragment_downloads'] = int(self.concurrent_fragments.get())
        if self.limit_rate.get():
            opts['ratelimit'] = self.limit_rate.get()
        if self.buffer_size.get():
            opts['buffersize'] = self.buffer_size.get()
        if self.http_chunk_size.get():
            opts['http_chunk_size'] = self.http_chunk_size.get()
        if self.no_resize_buffer.get():
            opts['noresizebuffer'] = True
        if self.test.get():
            opts['test'] = True
        if self.external_downloader.get():
            opts['external_downloader'] = self.external_downloader.get()
        if self.external_downloader_args.get():
            opts['external_downloader_args'] = self.external_downloader_args.get()

        # Filesystem options
        output_template = self.output_template.get() if hasattr(self, 'output_template') else ''
        output_dir = self.output_dir.get() if hasattr(self, 'output_dir') else ''
        if output_template and self.playlist_subdir.get() and '%(playlist)s/' not in output_template and '%(playlist)s\\' not in output_template:
            output_template = os.path.join('%(playlist)s', output_template)
        if output_dir and output_template:
            opts['outtmpl'] = os.path.join(output_dir, output_template)
        elif output_template:
            opts['outtmpl'] = output_template
        elif output_dir:
            opts['paths'] = {'home': output_dir}

        if self.paths.get() if hasattr(self, 'paths') else False:
            opts['paths'] = {'home': self.paths.get()}
        if self.restrict_filenames.get() if hasattr(self, 'restrict_filenames') else False:
            opts['restrictfilenames'] = True
        if self.no_restrict_filenames.get() if hasattr(self, 'no_restrict_filenames') else False:
            opts['restrictfilenames'] = False
        if self.windows_filenames.get() if hasattr(self, 'windows_filenames') else False:
            opts['windowsfilenames'] = True
        if self.no_overwrites.get() if hasattr(self, 'no_overwrites') else False:
            opts['nooverwrites'] = True
        if self.force_overwrites.get() if hasattr(self, 'force_overwrites') else False:
            opts['overwrites'] = True
        if self.continue_dl.get() if hasattr(self, 'continue_dl') else False:
            opts['continuedl'] = True
        if self.no_continue.get() if hasattr(self, 'no_continue') else False:
            opts['continuedl'] = False
        if self.no_part.get() if hasattr(self, 'no_part') else False:
            opts['nopart'] = True
        if self.no_mtime.get() if hasattr(self, 'no_mtime') else False:
            opts['updatetime'] = False
        if self.write_description.get() if hasattr(self, 'write_description') else False:
            opts['writedescription'] = True
        if self.write_info_json.get() if hasattr(self, 'write_info_json') else False:
            opts['writeinfojson'] = True
        if self.write_annotations.get() if hasattr(self, 'write_annotations') else False:
            opts['writeannotations'] = True

        # Video format options
        if hasattr(self, 'video_format'):
            vf = self.video_format.get()
            if vf and vf != 'best':
                opts['format'] = vf
        if hasattr(self, 'format_sort') and self.format_sort.get():
            opts['format_sort'] = self.format_sort.get()
        if hasattr(self, 'prefer_free_formats') and self.prefer_free_formats.get():
            opts['prefer_free_formats'] = True
        if hasattr(self, 'all_formats') and self.all_formats.get():
            opts['allformats'] = True

        # Subtitle options
        if hasattr(self, 'write_subtitles') and self.write_subtitles.get():
            opts['writesubtitles'] = True
        if hasattr(self, 'write_auto_subs') and self.write_auto_subs.get():
            opts['writeautomaticsub'] = True
        if hasattr(self, 'subtitles_langs') and self.subtitles_langs.get():
            opts['subtitleslangs'] = self.subtitles_langs.get().split(',')
        if hasattr(self, 'subtitles_format') and self.subtitles_format.get():
            opts['subtitlesformat'] = self.subtitles_format.get()
        if hasattr(self, 'embed_subs') and self.embed_subs.get():
            opts['embedsubtitles'] = True

        # Audio options
        if hasattr(self, 'extract_audio') and self.extract_audio.get():
            opts['extractaudio'] = True
            if hasattr(self, 'audio_format') and self.audio_format.get():
                opts['audioformat'] = self.audio_format.get()
            if hasattr(self, 'audio_quality') and self.audio_quality.get():
                opts['audioquality'] = self.audio_quality.get()
        if hasattr(self, 'keep_video') and self.keep_video.get():
            opts['keepvideo'] = True

        # Post-processing options
        postprocessors = []
        if hasattr(self, 'write_thumbnail') and self.write_thumbnail.get():
            opts['writethumbnail'] = True
        if hasattr(self, 'list_thumbnails') and self.list_thumbnails.get():
            opts['listthumbnails'] = True
        if hasattr(self, 'embed_thumbnail') and self.embed_thumbnail.get():
            postprocessors.append({'key': 'EmbedThumbnail'})
        if hasattr(self, 'add_metadata') and self.add_metadata.get():
            postprocessors.append({'key': 'FFmpegMetadata'})
        if hasattr(self, 'xattrs') and self.xattrs.get():
            postprocessors.append({'key': 'XAttrMetadata'})
        if hasattr(self, 'convert_subs') and self.convert_subs.get():
            postprocessors.append({'key': 'FFmpegSubtitlesConvertor', 'format': self.convert_subs.get()})

        if postprocessors:
            opts['postprocessors'] = postprocessors

        if hasattr(self, 'fixup_policy') and self.fixup_policy.get():
            opts['fixup'] = self.fixup_policy.get()
        if hasattr(self, 'prefer_ffmpeg') and self.prefer_ffmpeg.get():
            opts['prefer_ffmpeg'] = True
        if hasattr(self, 'ffmpeg_location') and self.ffmpeg_location.get():
            opts['ffmpeg_location'] = self.ffmpeg_location.get()

        # SponsorBlock options
        if hasattr(self, 'no_sponsorblock') and self.no_sponsorblock.get():
            opts['no_sponsorblock'] = True
        elif hasattr(self, 'sponsorblock_remove') and self.sponsorblock_remove.get():
            remove_cats = [cat for cat, var in (self.sb_remove_vars or {}).items() if var.get()]
            if remove_cats:
                opts['sponsorblock_remove'] = remove_cats
        elif hasattr(self, 'sponsorblock_mark') and self.sponsorblock_mark.get():
            mark_cats = [cat for cat, var in (self.sb_mark_vars or {}).items() if var.get()]
            if mark_cats:
                opts['sponsorblock_mark'] = mark_cats
        if hasattr(self, 'sponsorblock_chapter_title') and self.sponsorblock_chapter_title.get():
            opts['sponsorblock_chapter_title'] = self.sponsorblock_chapter_title.get()
        if hasattr(self, 'sponsorblock_api') and self.sponsorblock_api.get():
            opts['sponsorblock_api'] = self.sponsorblock_api.get()

        # Cookies
        if hasattr(self, 'cookies_from_browser') and self.cookies_from_browser.get():
            opts['cookiesfrombrowser'] = (self.cookies_from_browser.get(), None, None, None)
        if hasattr(self, 'cookies') and self.cookies.get():
            opts['cookiefile'] = self.cookies.get()

        # Quiet/Verbose
        if hasattr(self, 'quiet') and self.quiet.get():
            opts['quiet'] = True
        if hasattr(self, 'verbose') and self.verbose.get():
            opts['verbose'] = True

        # Authentication
        if hasattr(self, 'username') and self.username.get():
            opts['username'] = self.username.get()
        if hasattr(self, 'password') and self.password.get():
            opts['password'] = self.password.get()
        if hasattr(self, 'twofactor') and self.twofactor.get():
            opts['twofactor'] = self.twofactor.get()
        if hasattr(self, 'netrc') and self.netrc.get():
            opts['usenetrc'] = True
        if hasattr(self, 'netrc_location') and self.netrc_location.get():
            opts['netrc_location'] = self.netrc_location.get()
        if hasattr(self, 'video_password') and self.video_password.get():
            opts['videopassword'] = self.video_password.get()
        if hasattr(self, 'ap_username') and self.ap_username.get():
            opts['ap_username'] = self.ap_username.get()
        if hasattr(self, 'ap_password') and self.ap_password.get():
            opts['ap_password'] = self.ap_password.get()
        if hasattr(self, 'ap_mso') and self.ap_mso.get():
            opts['ap_mso'] = self.ap_mso.get()
        if hasattr(self, 'client_certificate') and self.client_certificate.get():
            opts['client_certificate'] = self.client_certificate.get()
        if hasattr(self, 'client_certificate_key') and self.client_certificate_key.get():
            opts['client_certificate_key'] = self.client_certificate_key.get()

        # Progress hooks
        opts['progress_hooks'] = [self._progress_hook]
        opts['logger'] = self._ydl_logger()

        return opts

    def _progress_hook(self, d: dict):
        """Callback for download progress updates"""
        if self._stop_requested:
            raise Exception('Download stopped by user')

        status = d.get('status', '')
        info = ''

        if status == 'downloading':
            percent = d.get('percentage', 0)
            speed = d.get('speed', 0)
            eta = d.get('eta', 0)
            info = f"Downloading: {percent:.1f}% | Speed: {self._format_speed(speed)} | ETA: {eta}s"
        elif status == 'finished':
            info = f"Finished: {d.get('filename', '')}"
        elif status == 'error':
            info = f"Error: {d.get('error', 'Unknown error')}"

        if info:
            self.root.after(0, lambda: self.log_message(info))

    def _format_speed(self, speed):
        """Format speed in human readable format"""
        if speed is None:
            return 'N/A'
        if speed < 1024:
            return f'{speed:.1f} B/s'
        if speed < 1024 * 1024:
            return f'{speed / 1024:.1f} KiB/s'
        return f'{speed / (1024 * 1024):.1f} MiB/s'

    def _ydl_logger(self):
        """Create a logger for YoutubeDL"""
        class YDLLogger:
            def __init__(self, gui):
                self.gui = gui

            def debug(self, msg):
                if self.gui.verbose.get() if hasattr(self.gui, 'verbose') else False:
                    self.gui.root.after(0, lambda: self.gui.log_message(f'[DEBUG] {msg}'))

            def warning(self, msg):
                if not self.gui.no_warnings.get():
                    self.gui.root.after(0, lambda: self.gui.log_message(f'[WARN] {msg}'))

            def error(self, msg):
                self.gui.root.after(0, lambda: self.gui.log_message(f'[ERROR] {msg}'))

        return YDLLogger(self)

    def run_ytdlp(self, tasks):
        """Run a list of yt-dlp tasks using YoutubeDL API"""
        from yt_dlp import YoutubeDL

        try:
            total = len(tasks)
            for i, (idx, url) in enumerate(tasks):
                if self._stop_requested:
                    self.log_message(self.tr('Download stopped.'))
                    break

                self.log_message(self.translate_concat(f'[{i + 1}/{total}] Download Task: Index ', idx))
                self.root.after(0, lambda: self.status_var.set(f'{self.tr("Downloading")} {i + 1}/{total}'))

                opts = self.build_ydl_opts()
                opts['outtmpl'] = opts.get('outtmpl', '%(title)s.%(ext)s')

                try:
                    with YoutubeDL(opts) as ydl:
                        self._ydl = ydl
                        ydl.download([url])
                        self._ydl = None
                except Exception as e:
                    self.log_message(self.translate_concat('Task failed: ', str(e)))
                    if 'n challenge solving failed' in str(e):
                        self.log_message('\n[!] Tip: JavaScript runtime missing. Run "brew install node" to fix.')

            self.log_message(self.tr('All tasks processed.'))
            self.root.after(0, lambda: self.status_var.set(self.tr('Ready')))

        except Exception as e:
            self.log_message(self.translate_concat('ERROR in runner: ', str(e)))
            self.root.after(0, lambda: self.status_var.set(self.tr('Error')))
        finally:
            self._ydl = None
            self._stop_requested = False
            self.root.after(0, self._restore_download_button)

    def on_download_btn_click(self):
        if self._ydl is not None or self._stop_requested:
            self.stop_download()
        else:
            self.start_download()

    def stop_download(self):
        """Stop the current download"""
        self._stop_requested = True
        self.log_message(self.tr('Stopping download...'))

        if self._ydl:
            try:
                # YoutubeDL doesn't have a direct stop method,
                # but we can set a flag that the progress_hook checks
                pass
            except Exception as e:
                self.log_message(f'[DEBUG] Stop error: {e}')

        self._restore_download_button()

    def _restore_download_button(self):
        if hasattr(self, 'download_btn'):
            self.download_btn.config(text=self.tr('Download'))
            self._translatable_widgets[self.download_btn] = 'Download'

    def start_download(self):
        """Start download process using YoutubeDL API"""
        from yt_dlp.utils import DownloadError

        url = self.url_entry.get().strip()
        if not url and not self.batch_file_entry.get().strip():
            messagebox.showwarning(self.tr('Warning'), self.tr('Please enter a URL'))
            return

        if self.save_config:
            self.save_config()

        self.download_btn.config(text=self.tr('Stop'))
        self._translatable_widgets[self.download_btn] = 'Stop'

        self.console.delete('1.0', tk.END)
        self.log_message(self.tr('Starting download...'))
        self.status_var.set(self.tr('Preparing...'))

        # Collect URLs to download
        urls = []
        if url:
            urls.append((1, url))

        batch_file = self.batch_file_entry.get().strip()
        if batch_file:
            try:
                with open(batch_file, 'r') as f:
                    for i, line in enumerate(f, len(urls) + 1):
                        line = line.strip()
                        if line and not line.startswith('#'):
                            urls.append((i, line))
            except Exception as e:
                self.log_message(self.translate_concat('Error reading batch file: ', str(e)))

        if not urls:
            messagebox.showwarning(self.tr('Warning'), self.tr('No URLs to download'))
            return

        self._stop_requested = False
        thread = threading.Thread(target=self.run_ytdlp, args=(urls,), daemon=True)
        thread.start()

    def log_message(self, message):
        """Log a message to the console"""
        if hasattr(self, 'console'):
            self.console.insert(tk.END, str(message) + '\n')
            self.console.see(tk.END)

    def generate_command(self):
        """Generate equivalent command line (for display purposes)"""
        url = self.url_entry.get().strip()
        opts = self.build_ydl_opts()

        # Convert opts back to command line for display
        cmd_parts = ['yt-dlp']
        for key, val in opts.items():
            if key in ('progress_hooks', 'logger'):
                continue
            if val is True:
                cmd_parts.append(f'--{key.replace("_", "-")}')
            elif val is False:
                cmd_parts.append(f'--no-{key.replace("_", "-")}')
            elif isinstance(val, str):
                cmd_parts.extend([f'--{key.replace("_", "-")}', val])
            elif isinstance(val, list):
                cmd_parts.extend([f'--{key.replace("_", "-")}', ','.join(str(v) for v in val)])

        cmd_parts.append(url)
        return ' '.join(cmd_parts)

    def copy_command(self):
        """Copy generated command to clipboard"""
        import pyperclip
        cmd = self.generate_command()
        pyperclip.copy(cmd)
        self.log_message(self.tr('Command copied to clipboard.'))
