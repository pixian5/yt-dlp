import sys, re
path = 'yt_dlp/gui.py'
content = open(path, 'r', encoding='utf-8').read()

matches = re.findall(r"(?:text)\s*=\s*(['\"])(.*?)\1", content)
lazy_tabs = re.findall(r"add_lazy_tab\([^,]+,\s*(['\"])(.*?)\1", content)

all_strings = set()
for m in matches: all_strings.add(m[1])
for m in lazy_tabs: all_strings.add(m[1])

zh_block = content[content.find("'zh': {"):content.find('}', content.find("'zh': {"))]

missing = set()
for m in all_strings:
    if len(m) > 1 and not m.startswith('$(') and not m.startswith('--'):
        if f"'{m}'" not in zh_block and f'"{m}"' not in zh_block:
            missing.add(m)

print('MISSING STRINGS:')
for m in sorted(list(missing)):
    print(m)
