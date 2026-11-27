#!/usr/bin/env python3
"""Erzeugt floorball-penalty/offline.html: wie index.html, aber Three.js ist eingebettet (kein CDN, kein Internet nötig).

Aufruf (aus dem Repository-Stamm):
    npm pack three@0.160.0 && tar xzf three-0.160.0.tgz package/build/three.module.min.js package/LICENSE
    python3 floorball-penalty/werkzeuge/offline_bauen.py package/build/three.module.min.js package/LICENSE
"""
import base64, hashlib, pathlib, re, sys

ORDNER = pathlib.Path(__file__).resolve().parent.parent
CDN = 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js'

def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    three = pathlib.Path(sys.argv[1]).read_bytes()
    lizenz = pathlib.Path(sys.argv[2]).read_text(encoding='utf-8').strip() if len(sys.argv) > 2 else 'MIT License, Copyright © 2010-2023 three.js authors'
    if not re.search(rb'(REVISION\s*=\s*|^const t=)["\']160["\']', three[:4000] if b'@license' in three[:200] else three, re.M):
        sys.exit('Falsche Three.js-Version: erwartet wird 0.160.0 (REVISION 160).')
    html = (ORDNER / 'index.html').read_text(encoding='utf-8')
    if html.count(CDN) != 1:
        sys.exit('CDN-Adresse in index.html nicht genau einmal gefunden.')
    daten = 'data:text/javascript;base64,' + base64.b64encode(three).decode('ascii')
    hinweis = ('<!-- Offline-Fassung: Three.js r160 ist eingebettet (sha256 ' + hashlib.sha256(three).hexdigest() + ').\n'
               + lizenz.replace('--', '- -') + '\n-->\n')
    html = html.replace(CDN, daten).replace('<!doctype html>', '<!doctype html>\n' + hinweis, 1)
    ziel = ORDNER / 'offline.html'
    ziel.write_text(html, encoding='utf-8')
    print(ziel, len(html), 'Zeichen')

if __name__ == '__main__':
    main()
