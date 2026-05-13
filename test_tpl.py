import yt_dlp

ydl = yt_dlp.YoutubeDL({'outtmpl': '%(playlist&{}/|)s%(title)s.%(ext)s'})
print(ydl.prepare_filename({'title': 'my_title', 'ext': 'mp4', 'playlist': None, 'id': '1'}))
print(ydl.prepare_filename({'title': 'my_title', 'ext': 'mp4', 'playlist': 'my_playlist', 'id': '2'}))
