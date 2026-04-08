# yt-dlp GUI 使用说明

这份文档专门说明项目内图形界面 [`yt_dlp/gui.py`](/Users/x/code/yt-dlp/yt_dlp/gui.py) 的各个选项，目标是让你不看命令行帮助也能知道每个控件大概做什么、什么时候该开、什么时候别开。

## 启动方式

推荐在项目虚拟环境里启动：

```bash
source .venv/bin/activate
python -m yt_dlp.gui
```

也可以用：

```bash
python yt-dlp-gui.py
```

## 界面总体结构

GUI 由四部分组成：

1. 顶部输入区  
   填视频 URL、批量文件、语言，以及几个快捷按钮。

2. 中间页签区  
   按功能分类配置 `yt-dlp` 参数。

3. 底部输出控制台  
   显示运行日志、错误信息、下载进度。

4. 状态栏  
   显示当前是否在下载、是否报错。

## 顶部区域

### `Language`

- 切换 GUI 语言。
- 只影响界面文本，不影响下载结果。

### `Video URL(s)`

- 输入单个视频、播放列表、频道、合集、直播等地址。
- 如果同时填了这里和批量文件，程序优先使用批量文件。

### `Or Batch File`

- 选择一个文本文件，里面每行一个 URL。
- 适合批量下载多个地址。

### 快捷按钮

#### `Download`

- 用当前 GUI 配置真正执行下载。

#### `List Formats`

- 相当于执行 `yt-dlp -F URL`。
- 用来查看站点实际提供的格式编号、清晰度、编码、音轨等。
- 当前实现里，这个按钮主要只带 URL，不会完整套用全部 GUI 配置。

#### `Extract Info`

- 相当于执行 `yt-dlp --dump-json URL`。
- 用来查看元数据、字段名、可用于输出模板或筛选的字段。
- 当前实现里，这个按钮也主要只带 URL，不会完整套用全部 GUI 配置。

#### `Load Config`

- 从 JSON 文件载入 GUI 保存过的配置。

#### `Save Config`

- 把当前 GUI 配置导出成 JSON 文件。

## 配置保存机制

- GUI 会自动把当前状态保存到 `~/.yt-dlp-gui-config.json`
- 重新打开时会恢复上次的大多数选项
- 也可以手动导入导出 JSON 配置

## General 页签

这一页放“通用行为控制”。

### `Ignore errors (--ignore-errors)`

- 某个条目失败时继续往后跑。
- 批量下载、播放列表下载时很常用。

### `Ignore warnings (--no-warnings)`

- 不显示警告。
- 只建议在你已经知道警告内容、嫌日志太吵时使用。

### `Abort on error (--abort-on-error)`

- 遇到错误立刻停止整个任务。
- 和 `Ignore errors` 是相反思路，二选一更合理。

### `Download only video, not playlist (--no-playlist)`

- 当 URL 同时包含单视频和播放列表信息时，只下当前视频，不展开整个列表。
- 例如 YouTube `watch?v=...&list=...` 常用这个。

### `Download playlist (--yes-playlist)`

- 明确要求按播放列表处理。
- 适合你输入的是某个视频页，但想把整个列表都下下来。

### `Include private/unavailable videos in YouTube playlists`

- 控制是否把 YouTube 播放列表里的私有视频、地区受限视频、已失效视频等一并纳入列表识别。
- 默认开启，保持 `yt-dlp` 当前默认行为。
- 关闭后，GUI 会加上 `--compat-options no-youtube-unavailable-videos`。
- 这只是“是否把这些条目纳入列表处理”，不是绕过权限。
- 真正能不能下载私有视频，仍取决于你当前账号是否有权限。

### `Mark videos as watched (--mark-watched)`

- 下载后把视频标记成“已观看”。
- 主要对支持该行为的网站有意义。

### `Do not mark videos as watched (--no-mark-watched)`

- 显式禁止标记已观看。

### `Default search prefix`

- 给非 URL 文本自动补搜索前缀。
- 例如填 `ytsearch5:` 后，输入关键词时就会按 YouTube 搜索前 5 条。

### `Configuration file`

- 指定额外的 `yt-dlp` 配置文件路径。
- 适合你已有长期维护的命令行配置。

### `Flat playlist extraction`

- 控制播放列表是否只取“平铺信息”。
- 空白：正常提取。
- `in_playlist`：在播放列表里尽量只取平铺结果，速度更快。
- `discard_in_playlist`：更偏向丢弃详细展开，适合只看目录结构时用。

### `Age limit`

- 只处理符合年龄限制的视频。

### `Download archive file`

- 指定“下载归档”文件。
- 已记录过的 ID 下次会跳过。
- 长期增量下载非常有用。

### `Max downloads`

- 限制本次最多下载多少个条目。

## Network 页签

这一页主要影响连接、超时、速率、重试。

### `Proxy URL`

- 设置代理，如 `http://127.0.0.1:7890`。
- 遇到地区限制、公司网络限制、访问不稳定时常用。

### `Socket timeout (seconds)`

- 设置网络超时时间。

### `Source address (bind to)`

- 指定本机发起连接使用的源地址。
- 多网卡环境才常用。

### `Force IPv4 (--force-ipv4)`

- 强制 IPv4。
- 某些网络 IPv6 很差时可开。

### `Force IPv6 (--force-ipv6)`

- 强制 IPv6。

### `Enable file:// URLs (--enable-file-urls)`

- 允许把 `file://` 形式的本地路径当输入。

### `Sleep interval`

- 每次下载前额外等待的秒数。
- 用于降低请求频率。

### `Max sleep interval`

- 与 `Sleep interval` 组合使用，做随机等待上限。

### `Sleep interval for requests`

- 针对网络请求的等待间隔。

### `Sleep interval for subtitles`

- 字幕请求单独的等待时间。

### `Rate limit`

- 总下载速率上限。
- 例如 `500K`、`4.2M`。

### `Throttled rate`

- 把低于此速度视为“被节流”。
- 某些站点限速场景下可辅助重试逻辑。

### `Retries`

- 整体重试次数。

### `Fragment retries`

- 分片下载的重试次数。
- 对 HLS、DASH 等流媒体更常用。

## Geo-restriction 页签

这一页处理地区限制相关行为。

### `Geo verification proxy`

- 专门用于地区验证的代理。

### `Bypass geo restriction (--geo-bypass)`

- 尝试绕过地区限制。

### `Do not bypass geo restriction (--no-geo-bypass)`

- 显式关闭绕过。

### `Geo bypass country`

- 指定伪装国家代码。

### `Geo bypass IP block`

- 指定伪装 IP 段，CIDR 格式。

## Video Selection 页签

这一页决定“挑哪些视频下载”。

### `Playlist items`

- 只下载播放列表中的指定编号。
- 例如 `1-5,10,15-20`。

### `Playlist start`

- 从第几个开始。

### `Playlist end`

- 到第几个结束。

### `Match title (regex)`

- 只下载标题匹配正则的条目。

### `Reject title (regex)`

- 排除标题匹配正则的条目。

### `Min filesize`

- 只下载大于这个大小的文件。

### `Max filesize`

- 只下载小于这个大小的文件。

### `Date`

- 只下载指定日期的内容。
- 格式 `YYYYMMDD`。

### `Date before`

- 只下载该日期之前的内容。

### `Date after`

- 只下载该日期之后的内容。

### `Min views`

- 最低播放量门槛。

### `Max views`

- 最高播放量门槛。

### `Match filter`

- 高级筛选表达式。
- 适合熟悉 `yt-dlp --match-filter` 的用户。

### `Break on existing (--break-on-existing)`

- 一旦遇到已存在文件就停止后续处理。

### `Break on reject (--break-on-reject)`

- 一旦有条目被筛选条件排除，就停止任务。

### `No break on existing (--no-break-on-existing)`

- 显式允许遇到已存在文件时继续。

## Download 页签

这一页管“下载过程本身”。

### `Concurrent fragments`

- 分片并发数。
- 对 HLS、DASH 下载可提速，但太高可能更容易触发限流。

### `Limit download rate`

- 下载速率上限。

### `Buffer size`

- 下载缓冲区大小。

### `HTTP chunk size`

- HTTP 分块大小。
- 某些服务器在较小块大小时更稳定。

### `Do not resize buffer (--no-resize-buffer)`

- 禁止自动调整缓冲区。

### `Test mode - do not download (--test)`

- 测试模式，只下很小的一部分。
- 适合检查链路是否通畅。

### `External downloader`

- 指定外部下载器，如 `aria2c`、`curl`、`ffmpeg`。

### `External downloader args`

- 传给外部下载器的额外参数。

### `Prefer native HLS downloader (--hls-prefer-native)`

- HLS 优先用内置下载器。

### `Prefer ffmpeg for HLS (--hls-prefer-ffmpeg)`

- HLS 优先用 ffmpeg。
- 某些直播流、复杂流更稳。

### `Use MPEG-TS container for HLS (--hls-use-mpegts)`

- HLS 输出更偏向 MPEG-TS 容器。
- 某些直播、断流恢复场景更有帮助。

## Filesystem 页签

这一页控制文件名、目录、缓存、旁路元数据文件。

### `Output template`

- 输出文件命名模板。
- 例如 `%(title)s.%(ext)s`。
- 你当前默认是 `%(playlist_index)s-%(title)s.%(ext)s`，适合播放列表。

### `Output directory`

- 输出目录。

### `Paths configuration`

- 对不同类型输出路径做更细分配置。
- 适合高级用法。

### `Restrict filenames to ASCII (--restrict-filenames)`

- 文件名尽量只用 ASCII。
- 对跨平台兼容更友好，但标题可读性会下降。

### `Allow Unicode in filenames (--no-restrict-filenames)`

- 允许 Unicode 文件名。
- 中文、日文标题更自然。

### `Create playlist subfolder for playlist downloads`

- 勾选后，GUI 会在输出模板前自动补上 `%(playlist)s/`。
- 例如原模板是 `%(playlist_index)s-%(title)s.%(ext)s`，启用后实际效果会变成：
  `%(playlist)s/%(playlist_index)s-%(title)s.%(ext)s`
- 适合把每个播放列表自动放进自己的同名文件夹。
- 如果你的输出模板本来就已经手写了 `%(playlist)s/`，GUI 不会重复再套一层。

### `Force Windows-compatible filenames (--windows-filenames)`

- 文件名进一步兼容 Windows 保留字符规则。

### `Do not overwrite files (--no-overwrites)`

- 已有文件不覆盖。

### `Force overwrite files (--force-overwrites)`

- 强制覆盖已有文件。
- 使用前要确认目录里没有要保留的旧文件。

### `Continue partially downloaded files (--continue)`

- 继续未完成下载。
- 这是比较推荐的默认行为。

### `Do not continue downloads (--no-continue)`

- 不续传，从头开始。

### `Do not use .part files (--no-part)`

- 不生成临时 `.part` 文件。
- 简洁，但下载中断时恢复能力会差一些。

### `Do not use Last-modified header (--no-mtime)`

- 不用服务器返回的修改时间设置本地文件时间。

### `Write description to .description file (--write-description)`

- 额外保存描述文本。

### `Write metadata to .info.json file (--write-info-json)`

- 额外保存完整元数据 JSON。
- 排查问题、做二次处理非常有用。

### `Write annotations to .annotations.xml (--write-annotations)`

- 保存注释文件。
- 只有少数站点/场景还有意义。

### `Write comments to .comments.json (--write-comments)`

- 保存评论到 JSON 文件。

### `Load info JSON`

- 从已有 `info.json` 直接读取信息。
- 适合二次后处理。

### `Cache directory`

- 指定缓存目录。

### `Disable filesystem caching (--no-cache-dir)`

- 完全不用磁盘缓存。

### `Delete cache directory contents (--rm-cache-dir)`

- 删除缓存目录内容。

## Video Format 页签

这一页决定“下什么格式”。

### `Format selection`

- 核心格式表达式。
- 例如：
  - `best`
  - `bv*+ba/b`
  - `bestvideo[height<=1080]+bestaudio/best[height<=1080]`

### `Format sort`

- 格式排序规则。
- 当多个格式候选都符合条件时，用它决定优先级。

### `Prefer free formats (--prefer-free-formats)`

- 更偏向开放格式。

### `Check available formats (--check-formats)`

- 下载前检查格式可用性。

### `Merge output format`

- 音视频分离下载后，最终合并成什么容器。
- 常用 `mp4`、`mkv`。

### `Video multistreams`

- 是否允许多个视频流。

### `Audio multistreams`

- 是否允许多个音频流。

## Subtitles 页签

这一页处理字幕和一部分嵌入选项。

### `Write subtitle file (--write-subs)`

- 下载普通字幕文件。

### `Write automatic subtitle file (--write-auto-subs)`

- 下载自动生成字幕。

### `List available subtitles (--list-subs)`

- 只列出可用字幕，不下载。

### `Subtitle format`

- 字幕保存格式，如 `srt`、`vtt`、`ass`、`lrc`。

### `Subtitle languages`

- 指定字幕语言，逗号分隔。
- 例如 `en,zh-Hans,ja`。

### `Embed subtitles (--embed-subs)`

- 把字幕嵌入视频容器。
- 一般需要 ffmpeg。

### `Do not embed subtitles (--no-embed-subs)`

- 显式不嵌入字幕。

### `Embed thumbnail (--embed-thumbnail)`

- 把缩略图嵌入媒体文件。
- 虽然这个开关位置在字幕页，但它本质上是封面嵌入选项。

### `Do not embed thumbnail (--no-embed-thumbnail)`

- 显式不嵌入封面。

## Authentication 页签

这一页最关键，很多会员视频、年龄限制视频、私有视频能否访问，都看这里。

### `Username`

- 站点登录用户名。

### `Password`

- 站点登录密码。

### `Two-factor code`

- 两步验证码。

### `Use .netrc authentication (--netrc)`

- 从 `.netrc` 读取登录信息。

### `Video password`

- 对“单视频密码保护”内容使用。

### `Adobe Pass MSO`

- Adobe Pass 电视运营商标识。

### `Adobe Pass username`

- Adobe Pass 用户名。

### `Adobe Pass password`

- Adobe Pass 密码。

### `Client certificate`

- 客户端证书文件。

### `Client certificate key`

- 客户端证书私钥文件。

### `Client certificate password`

- 客户端证书私钥密码。

## Post-processing 页签

这一页管下载后的转换、重封装、元数据写入。

### `Extract audio (-x, --extract-audio)`

- 只保留音频。

### `Audio format`

- 提取音频后的目标格式。
- 常用 `mp3`、`m4a`、`opus`、`flac`。

### `Audio quality`

- 音频质量参数。
- 数值越接近 `0` 越高。

### `Recode video format`

- 重新编码成指定视频格式。
- 这是“转码”，速度慢但兼容性强。

### `Remux video format`

- 只换封装，不重编码。
- 速度快，适合 `webm` 转 `mkv`、`m4a` 转 `mp4` 这类。

### `Keep video file after conversion (--keep-video)`

- 转换后保留原始文件。

### `Do not keep video file (--no-keep-video)`

- 转换后不保留原始文件。

### `Embed metadata (--embed-metadata)`

- 把元数据嵌入媒体文件。

### `Embed chapter markers (--embed-chapters)`

- 嵌入章节信息。

### `Embed info.json (--embed-info-json)`

- 把 `info.json` 嵌入媒体文件。

### `Add metadata to file (--add-metadata)`

- 把常见元数据字段写进文件标签。

### `Metadata fields`

- 从标题中提取元数据字段。

### `Parse metadata`

- 自定义元数据解析规则。

### `FFmpeg location`

- 指定 ffmpeg 路径。
- 如果系统里没配 PATH，这里特别重要。

### `Post-processor args`

- 给后处理器传额外参数。

## Thumbnail 页签

### `Write thumbnail image (--write-thumbnail)`

- 下载缩略图。

### `Write all thumbnail formats (--write-all-thumbnails)`

- 下载全部缩略图版本。

### `List available thumbnails (--list-thumbnails)`

- 只列出缩略图，不下载。

### `Convert thumbnails format`

- 转换缩略图格式，如 `jpg`、`png`、`webp`。

## Verbosity/Simulation 页签

这一页是日志、调试和“只看信息不下载”。

### `Quiet mode (-q, --quiet)`

- 尽量减少输出。

### `No warnings (--no-warnings)`

- 不显示警告。
- 和 General 页里的同类选项本质一致。

### `Verbose output (-v, --verbose)`

- 输出更详细的调试信息。
- 出问题时建议开启。

### `Simulate, do not download (-s, --simulate)`

- 模拟执行，不下载。
- 用于先验证提取、格式、命名是否正确。

### `Skip download (--skip-download)`

- 跳过媒体下载，但仍可拿元数据、字幕等。

### `Get title / Get ID / Get URL / Get thumbnail / Get description / Get duration / Get filename / Get format`

- 这些都是“只输出某个字段”的快捷模式。
- 适合你想调试字段，或者想配合脚本拿数据。

### `Dump JSON info (--dump-json)`

- 每个视频输出 JSON 元数据。

### `Dump single JSON (--dump-single-json)`

- 对播放列表等，尽量输出单个整合 JSON。

### `Print JSON info (--print-json)`

- 打印 JSON 信息。

### `Show progress (--progress)`

- 显示进度。
- 当前 `yt-dlp` 默认就会显示进度，这个勾选更多是界面上的正向表达。

### `Hide progress (--no-progress)`

- 不显示进度。

### `Display progress in console title (--console-title)`

- 把进度写到控制台标题。

### `Progress template`

- 自定义进度展示模板。

## Workarounds 页签

这一页适合网络环境奇怪、证书异常、站点封锁严格时使用。

### `Encoding`

- 指定字符编码。

### `Skip SSL certificate validation (--no-check-certificate)`

- 跳过 SSL 证书校验。
- 只在证书真的有问题时临时使用，不建议长期默认开。

### `Prefer insecure connections (--prefer-insecure)`

- 优先使用不安全连接。

### `User agent`

- 自定义请求头里的 User-Agent。
- 某些站点很看这个。

### `Referer`

- 自定义 Referer。
- 防盗链场景常用。

### `Add header`

- 增加额外请求头。
- 通常格式类似 `Key:Value`。

### `Bidirectional text workaround (--bidi-workaround)`

- 处理双向文本显示问题。

### `Sleep before requests`

- 每次请求前等待。

### `Use legacy server connect (--legacy-server-connect)`

- 使用较旧的服务器连接方式。
- 很偏兼容性救急选项。

## SponsorBlock 页签

### `Mark SponsorBlock chapters (--sponsorblock-mark)`

- 把 SponsorBlock 片段标成章节。

### `Remove SponsorBlock segments (--sponsorblock-remove)`

- 直接移除 SponsorBlock 标记的片段。

### `SponsorBlock categories to remove`

- 指定要删除的分类。

### `SponsorBlock categories to mark`

- 指定只标记不删除的分类。

### `SponsorBlock chapter title`

- 自定义章节标题格式。

### `Disable SponsorBlock (--no-sponsorblock)`

- 完全关闭 SponsorBlock。

### `SponsorBlock API URL`

- 自定义 SponsorBlock API 地址。

## Extractor 页签

这一页最适合放“站点提取器细节”。

### `Extractor arguments`

- 给某个提取器传特定参数。
- 格式通常是 `提取器名:键=值` 或类似变体。
- 适合高级用户。

### `Extractor retries`

- 提取阶段的重试次数。

### `Allow dynamic MPD manifests (--allow-dynamic-mpd)`

- 允许动态 MPD。

### `Ignore dynamic MPD manifests (--ignore-dynamic-mpd)`

- 忽略动态 MPD。

### `Split HLS segments on discontinuity (--hls-split-discontinuity)`

- HLS 遇到 discontinuity 时拆分处理。

### `Cookies from browser`

- 从浏览器读取登录态。
- 对 YouTube、Bilibili、需要登录的站点最常用。
- 如果要下载你自己账号可见的私有内容，这通常是首选。

### `Cookies file`

- 从文本 cookies 文件读取登录态。
- 适合导出的 Netscape cookies 文件。

## Advanced 页签

### `Raw command-line arguments`

- 手动追加原始命令行参数。
- 一行一个参数或者直接写成一串都可以。
- 当 GUI 还没暴露某个选项时，这里是兜底方案。

### `Generated command`

- 展示 GUI 最终拼出来的命令。
- 很适合排查“为什么这个选项没生效”。

### `Generate Command`

- 刷新并显示当前命令。

### `Copy to Clipboard`

- 把命令复制到剪贴板。

## 常见组合建议

### 下载 YouTube 播放列表，保存为 MP4

建议：

- `General`
  - 勾选 `Download playlist`
  - 保持 `Include private/unavailable videos in YouTube playlists` 开启
- `Extractor`
  - `Cookies from browser = chrome`
- `Video Format`
  - `Format selection = bv*+ba/b`
  - `Merge output format = mp4`
- `Filesystem`
  - 输出目录设到目标文件夹
  - 勾选 `Create playlist subfolder for playlist downloads`
  - 输出模板设为 `%(playlist_index)s-%(title)s.%(ext)s`

### 只下载音频并转 MP3

建议：

- `Post-processing`
  - 勾选 `Extract audio`
  - `Audio format = mp3`

### 只测试不实际下载

建议：

- `Verbosity/Simulation`
  - 勾选 `Simulate`
- 或者：
  - `Download`
  - 勾选 `Test mode`

## 关于私有视频

要区分三件事：

1. 是否在播放列表里显示私有/不可用条目  
   由 `Include private/unavailable videos in YouTube playlists` 控制。

2. 是否能识别出该条目是私有视频  
   只要列表接口能返回，通常能识别。

3. 是否能真正下载私有视频  
   取决于你的登录态是否有权限。

因此，如果你想下载你自己账号能访问的私有视频，通常应这样配：

- `Extractor -> Cookies from browser = chrome`
- Chrome 中登录正确的 YouTube 账号
- `General -> Include private/unavailable videos in YouTube playlists` 保持开启

## 注意事项

### 1. GUI 是 `yt-dlp` 的前端

- 真正下载逻辑仍然是 `yt-dlp` 核心在执行。
- GUI 只是帮你拼参数、展示日志。

### 2. 某些选项互相冲突时，以最终命令和 `yt-dlp` 行为为准

例如：

- `--no-playlist` 和 `--yes-playlist`
- `--continue` 和 `--no-continue`
- `--embed-subs` 和 `--no-embed-subs`

这类最好不要同时勾。

### 3. 很多后处理功能依赖 ffmpeg

例如：

- 合并音视频
- 转码
- 嵌入字幕
- 嵌入封面
- 嵌入章节

如果相关功能没生效，先检查 ffmpeg。

### 4. 生成命令是排查问题的第一入口

当你怀疑 GUI 没按预期工作时，先看 `Advanced` 页里的生成命令，再对照 `yt-dlp` 命令行行为排查。

## 文件位置

- GUI 主代码：[`yt_dlp/gui.py`](/Users/x/code/yt-dlp/yt_dlp/gui.py)
- GUI 启动脚本：[`yt-dlp-gui.py`](/Users/x/code/yt-dlp/yt-dlp-gui.py)
- 当前文档：[`GUI-README.md`](/Users/x/code/yt-dlp/GUI-README.md)
