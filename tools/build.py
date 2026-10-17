"""Build index.html from tools/template.html.

Usage (from the repo root):
    python3 tools/build.py

Embeds the sprite metadata, uses the bundled fonts in /fonts, and adds the
page head (icons, web app manifest) so the game works offline-friendly on Vercel.
"""
import json
import pathlib

root = pathlib.Path(__file__).resolve().parent.parent
template = (root / 'tools/template.html').read_text(encoding='utf-8')
sprites = json.loads((root / 'tools/sprites.json').read_text(encoding='utf-8'))

fonts = '''<style>
@font-face{font-family:"Lilita One";src:url(fonts/lilita-one-latin-400-normal.woff2) format("woff2");font-weight:400;font-display:swap}
@font-face{font-family:"Nunito";src:url(fonts/nunito-latin-600-normal.woff2) format("woff2");font-weight:600;font-display:swap}
@font-face{font-family:"Nunito";src:url(fonts/nunito-latin-800-normal.woff2) format("woff2");font-weight:800;font-display:swap}
@font-face{font-family:"Noto Sans Ethiopic";src:url(fonts/noto-sans-ethiopic-ethiopic-700-normal.woff2) format("woff2");font-weight:700;font-display:swap}
:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px);box-sizing:border-box;height:100%}
body{margin:0;font-size:14px}[hidden]{display:none!important}
</style>'''

head = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, user-scalable=no">
<meta name="description" content="A family running game: race across the Ethiopian highlands to Gashe and Emaye's house and learn the Fidel letters on the way.">
<meta name="theme-color" content="#1e0f08">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" href="icons/favicon.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
'''

page = template.replace('__META__', json.dumps(sprites, separators=(',', ':')))
page = page.replace('<!--FONTS-->', fonts)
page = page.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
split = page.index('<div id="wrap">')
html = head + page[:split] + '</head>\n<body>\n' + page[split:] + '\n</body>\n</html>\n'
(root / 'index.html').write_text(html, encoding='utf-8')
print(f'index.html written ({len(html):,} bytes)')
