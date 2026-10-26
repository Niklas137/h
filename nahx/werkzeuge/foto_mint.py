"""Farbstimmung „Mint“ für die NAHX-Fotos (Stand 2026-10-26).

Blaue Töne werden gezielt zu Mint verschoben, Schatten bekommen einen leichten Mint-Grünton
(Midnight Green), Spitzlichter bleiben unverändert. Quelle ist jeweils die größte vorhandene Breite;
daraus werden alle Breiten als JPEG und WebP neu geschrieben.

    python3 nahx/werkzeuge/foto_mint.py            # alle Fotos aus site.json
    python3 nahx/werkzeuge/foto_mint.py --vorschau ZIEL.jpg   # nur Übersicht, nichts überschreiben

Läuft nur einmal auf den Originalen; ein zweiter Lauf würde die Wirkung verdoppeln.
Am 2026-10-26 einmal angewendet. „lichtleiter“ ist die gespiegelte Fassung von „faser“ (nach dem Einfärben).
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

HIER = Path(__file__).resolve().parent.parent
FOTO = HIER / "assets" / "img" / "foto"


def glatt(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def rgb_hsv(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx = rgb.max(-1); mn = rgb.min(-1); d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-6
    rr = m & (mx == r); gg = m & (mx == g) & ~rr; bb = m & ~rr & ~gg
    h[rr] = ((g - b)[rr] / d[rr]) % 6
    h[gg] = (b - r)[gg] / d[gg] + 2
    h[bb] = (r - g)[bb] / d[bb] + 4
    h *= 60
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0)
    return h, s, mx


def hsv_rgb(h, s, v):
    h = (h % 360) / 60
    i = np.floor(h).astype(int) % 6
    f = h - np.floor(h)
    p = v * (1 - s); q = v * (1 - s * f); t = v * (1 - s * (1 - f))
    wahl = [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)]
    out = np.zeros(h.shape + (3,))
    for k, (a, b, c) in enumerate(wahl):
        m = i == k
        out[m, 0] = a[m]; out[m, 1] = b[m]; out[m, 2] = c[m]
    return out


# Fotos, deren Blau ein Himmel ist: dort Blau entsättigen statt nach Mint drehen (kein grüner Himmel)
HIMMEL: set[str] = set()  # 2026-10-26: Gebäudefoto „kopenhagen“ entfernt (Wunsch Niklas: ohne Gebäude)


def mint(im: Image.Image, himmel: bool = False) -> Image.Image:
    x = np.asarray(im.convert("RGB")).astype(np.float64) / 255
    h, s, v = rgb_hsv(x)
    # Blau/Violett-Blau (ca. 185–270°) nach Mint (164°), weicher Übergang an den Rändern
    w = glatt(172, 196, h) * (1 - glatt(262, 292, h)) * glatt(0.08, 0.22, s)
    if himmel:
        w = glatt(172, 196, h) * (1 - glatt(300, 330, h))
        h2 = h
        s2 = s * (1 - 0.8 * w)
    else:
        h2 = h + w * (164 - h)
        s2 = s * (1 - 0.06 * w)
    y = hsv_rgb(h2, s2, v)
    # Schatten leicht nach Midnight Green (#06130F) ziehen, Spitzlichter unberührt
    lum = 0.2126 * y[..., 0] + 0.7152 * y[..., 1] + 0.0722 * y[..., 2]
    a = (0.30 * (1 - lum) ** 2.4)[..., None]
    ton = np.array([0.0, 0.16, 0.12])
    y = y * (1 - a) + ton * a * (0.35 + lum[..., None])
    # Warme Töne minimal zurücknehmen, damit Mint führt
    hh, ss, vv = rgb_hsv(np.clip(y, 0, 1))
    warm = glatt(5, 20, hh) * (1 - glatt(45, 70, hh))
    y = hsv_rgb(hh, ss * (1 - 0.12 * warm), vv)
    return Image.fromarray((np.clip(y, 0, 1) * 255 + 0.5).astype(np.uint8))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vorschau")
    arg = ap.parse_args()
    site = json.loads((HIER / "inhalt" / "site.json").read_text(encoding="utf-8"))
    fotos = site["fotos"]
    if arg.vorschau:
        kacheln = []
        for name, f in fotos.items():
            if f.get("variante_von"):
                continue
            q = Image.open(FOTO / f"{name}-{f['breiten'][1]}.jpg")
            for bild in (q, mint(q, name in HIMMEL)):
                b = bild.copy(); b.thumbnail((420, 420)); kacheln.append(b)
        H = max(k.height for k in kacheln)
        blatt = Image.new("RGB", (420 * 4, H * ((len(kacheln) + 3) // 4)), (12, 12, 12))
        for i, k in enumerate(kacheln):
            blatt.paste(k, ((i % 4) * 420, (i // 4) * H))
        blatt.save(arg.vorschau, quality=82)
        return
    for name, f in fotos.items():
        if f.get("variante_von"):
            continue  # abgeleitete Variante (z. B. gespiegelt), wird nicht erneut eingefärbt
        breiten = sorted(f["breiten"])
        quelle = mint(Image.open(FOTO / f"{name}-{breiten[-1]}.jpg"), name in HIMMEL)
        for w in breiten:
            b = quelle if w == quelle.width else quelle.resize((w, round(quelle.height * w / quelle.width)), Image.LANCZOS)
            b.save(FOTO / f"{name}-{w}.jpg", quality=82, optimize=True, progressive=True)
            b.save(FOTO / f"{name}-{w}.webp", quality=80, method=6)
        print(name, breiten)


if __name__ == "__main__":
    main()
