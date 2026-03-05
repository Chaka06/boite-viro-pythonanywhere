#!/usr/bin/env python3
"""
Télécharge les polices Noto nécessaires pour le rendu PDF multilingue.
Placer dans BASE_DIR/fonts/ avant de déployer sur PythonAnywhere.

Usage:
    python download_fonts.py
"""
import os
import sys
import urllib.request

FONTS_DIR = os.path.join(os.path.dirname(__file__), 'fonts')
os.makedirs(FONTS_DIR, exist_ok=True)

FONTS = {
    # Latin + Cyrillique (fr, en, es, it, de, pl, pt, ru)
    'NotoSans-Regular.ttf': (
        'https://github.com/notofonts/latin-greek-cyrillic/releases/download/'
        'NotoSans-v2.013/NotoSans-Regular.ttf'
    ),
    'NotoSans-Bold.ttf': (
        'https://github.com/notofonts/latin-greek-cyrillic/releases/download/'
        'NotoSans-v2.013/NotoSans-Bold.ttf'
    ),
    # Arabe (ar)
    'NotoNaskhArabic-Regular.ttf': (
        'https://github.com/notofonts/arabic/releases/download/'
        'NotoNaskhArabic-v2.014/NotoNaskhArabic-Regular.ttf'
    ),
    'NotoNaskhArabic-Bold.ttf': (
        'https://github.com/notofonts/arabic/releases/download/'
        'NotoNaskhArabic-v2.014/NotoNaskhArabic-Bold.ttf'
    ),
    # Chinois simplifié (zh)
    'NotoSansSC-Regular.ttf': (
        'https://github.com/notofonts/noto-cjk/releases/download/'
        'Sans2.004/NotoSansSC-Regular.ttf'
    ),
    'NotoSansSC-Bold.ttf': (
        'https://github.com/notofonts/noto-cjk/releases/download/'
        'Sans2.004/NotoSansSC-Bold.ttf'
    ),
}


def download(name, url):
    dest = os.path.join(FONTS_DIR, name)
    if os.path.exists(dest):
        print(f'  ok {name} (deja present)')
        return True
    print(f'  dl {name} ...', end=' ', flush=True)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp, \
             open(dest, 'wb') as f:
            f.write(resp.read())
        print('OK')
        return True
    except Exception as e:
        print(f'ERREUR: {e}')
        return False


if __name__ == '__main__':
    print(f'Telechargement des polices dans {FONTS_DIR}/\n')
    ok = all(download(name, url) for name, url in FONTS.items())
    print()
    if ok:
        print('Toutes les polices sont pretes.')
    else:
        print('Certaines polices ont echoue. Verifiez les URLs ou telechargez depuis:')
        print('  https://fonts.google.com/noto')
        sys.exit(1)
