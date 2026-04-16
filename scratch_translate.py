import re

with open("yt_dlp/gui.py", "r", encoding="utf-8") as f:
    text = f.read()

# I am adding ONLY the exact translations that we injected safely in 033685969, 
# ensuring they go directly into the correct language blocks without syntax error.

def inject_dict(lang, entries):
    global text
    # find the dictionary for this lang
    # e.g. 'ru': {
    target = f"    '{lang}': {{\n"
    if target in text:
        # insert right after
        text = text.replace(target, target + entries + "\n")
        print(f"Injected into {lang}")

ru_entries = """        "Write thumbnail image (--write-thumbnail)": "Write thumbnail image (--write-thumbnail)",
        "List available thumbnails (--list-thumbnails)": "List available thumbnails (--list-thumbnails)",
        "Username:": "Username:",
        "Password:": "Password:",
        "Extract audio (--extract-audio)": "Extract audio (--extract-audio)",
        "Audio format:": "Audio format:",
        "Quiet mode (-q, --quiet)": "Quiet mode (-q, --quiet)",
        "Verbose output (-v, --verbose)": "Verbose output (-v, --verbose)","""
ja_entries = """        "Write thumbnail image (--write-thumbnail)": "サムネイル画像を保存",
        "List available thumbnails (--list-thumbnails)": "利用可能なサムネイルを表示",
        "Username:": "ユーザー名:",
        "Password:": "パスワード:",
        "Extract audio (--extract-audio)": "音声を抽出",
        "Audio format:": "音声形式:",
        "Quiet mode (-q, --quiet)": "クワイエットモード",
        "Verbose output (-v, --verbose)": "詳細を出力","""
ko_entries = """        "Write thumbnail image (--write-thumbnail)": "썸네일 이미지 저장",
        "List available thumbnails (--list-thumbnails)": "사용 가능한 썸네일 목록",
        "Username:": "사용자 이름:",
        "Password:": "비밀번호:",
        "Extract audio (--extract-audio)": "오디오만 추출",
        "Audio format:": "오디오 출력 형식:",
        "Quiet mode (-q, --quiet)": "정적 모드",
        "Verbose output (-v, --verbose)": "상세 출력","""
es_entries = """        "Write thumbnail image (--write-thumbnail)": "Write thumbnail image (--write-thumbnail)",
        "List available thumbnails (--list-thumbnails)": "List available thumbnails (--list-thumbnails)",
        "Username:": "Username:",
        "Password:": "Password:",
        "Extract audio (--extract-audio)": "Extract audio (--extract-audio)",
        "Audio format:": "Audio format:",
        "Quiet mode (-q, --quiet)": "Quiet mode (-q, --quiet)",
        "Verbose output (-v, --verbose)": "Verbose output (-v, --verbose)","""
fr_entries = """        "Write thumbnail image (--write-thumbnail)": "Write thumbnail image (--write-thumbnail)",
        "List available thumbnails (--list-thumbnails)": "List available thumbnails (--list-thumbnails)",
        "Username:": "Username:",
        "Password:": "Password:",
        "Extract audio (--extract-audio)": "Extract audio (--extract-audio)",
        "Audio format:": "Audio format:",
        "Quiet mode (-q, --quiet)": "Quiet mode (-q, --quiet)",
        "Verbose output (-v, --verbose)": "Verbose output (-v, --verbose)","""
de_entries = """        "Write thumbnail image (--write-thumbnail)": "Write thumbnail image (--write-thumbnail)",
        "List available thumbnails (--list-thumbnails)": "List available thumbnails (--list-thumbnails)",
        "Username:": "Username:",
        "Password:": "Password:",
        "Extract audio (--extract-audio)": "Extract audio (--extract-audio)",
        "Audio format:": "Audio format:",
        "Quiet mode (-q, --quiet)": "Quiet mode (-q, --quiet)",
        "Verbose output (-v, --verbose)": "Verbose output (-v, --verbose)","""
zh_entries = """        "Extract audio (--extract-audio)": "仅提取音频","""

inject_dict('ru', ru_entries)
inject_dict('ja', ja_entries)
inject_dict('ko', ko_entries)
inject_dict('es', es_entries)
inject_dict('fr', fr_entries)
inject_dict('de', de_entries)
inject_dict('zh', zh_entries)

with open("yt_dlp/gui.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Finished.")
