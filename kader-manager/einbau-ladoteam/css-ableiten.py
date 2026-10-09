#!/usr/bin/env python3
"""Leitet kader-einbettung.css aus kader.css ab: globale Regeln (:root, html, body) werden auf die
Einbettungswurzel .kader-wurzel begrenzt, damit die Ansicht in einer fremden Seite (KFK LadoTeam) keine
Farben, Schriften oder Abstände des Gastgebers überschreibt. Aufruf aus dem Modulordner:
  python3 einbau-ladoteam/css-ableiten.py
"""
from pathlib import Path
quelle = Path(__file__).resolve().parent.parent / 'kader.css'
ziel = quelle.with_name('kader-einbettung.css')
css = quelle.read_text('utf-8')
ersetzungen = [
    (':root:not([data-theme="light"]){', '.kader-wurzel:not([data-theme="light"]){'),
    (':root[data-theme="dark"]{', '.kader-wurzel[data-theme="dark"]{'),
    (':root{', '.kader-wurzel{'),
    ('html{-webkit-text-size-adjust:100%}\n', ''),
    ('body{margin:0;background:var(--bg);color:var(--ink);font:400 17px/1.55 var(--schrift);overflow-x:hidden}',
     '.kader-wurzel{color:var(--ink);font:400 17px/1.55 var(--schrift);overflow-x:hidden}'),
    ('*,*::before,*::after{box-sizing:border-box}', '.kader-wurzel *,.kader-wurzel *::before,.kader-wurzel *::after{box-sizing:border-box}'),
    ('h1,h2,h3{font-family:var(--titel);margin:0;line-height:1.2}', '.kader-wurzel h1,.kader-wurzel h2,.kader-wurzel h3{font-family:var(--titel);margin:0;line-height:1.2}'),
    ('p{margin:0}', '.kader-wurzel p{margin:0}'),
    ('button{font:inherit;color:inherit}', '.kader-wurzel button{font:inherit;color:inherit}'),
    ('img{max-width:100%;display:block}', '.kader-wurzel img{max-width:100%;display:block}'),
    (':focus-visible{outline:3px solid var(--team-2);outline-offset:3px}', '.kader-wurzel :focus-visible{outline:3px solid var(--team-2);outline-offset:3px}'),
]
for alt, neu in ersetzungen:
    if alt not in css:
        raise SystemExit(f'Muster nicht gefunden: {alt[:50]}')
    css = css.replace(alt, neu)
kopf = '/* ABGELEITET aus kader.css durch einbau-ladoteam/css-ableiten.py – nicht von Hand ändern.\n   Für die Einbettung in eine fremde Seite: alle globalen Regeln auf .kader-wurzel begrenzt. */\n'
ziel.write_text(kopf + css, 'utf-8')
print(f'{ziel.name}: {len(css)} Zeichen')
