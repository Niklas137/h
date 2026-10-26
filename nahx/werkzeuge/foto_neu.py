"""Neues Foto in die NAHX-Bildreihe aufnehmen (Stand 2026-10-27).

Nimmt ein Original (z. B. von Unsplash), färbt es in die Mint-Welt und schreibt die Breiten als JPEG und WebP nach
assets/img/foto/<name>-<breite>.{jpg,webp}. Den Eintrag in inhalt/site.json (Alt-Texte, Fotograf, Quelle) und die Zeile
in assets/img/foto/QUELLEN.md macht man von Hand.

    python3 nahx/werkzeuge/foto_neu.py ORIGINAL.jpg NAME --art mint     # Blau wird Mint (wie foto_mint.py)
    python3 nahx/werkzeuge/foto_neu.py ORIGINAL.jpg NAME --art chrom    # Grau/Chrom wird Mint-Duoton
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
from foto_mint import mint  # noqa: E402

FOTO = HIER.parent / "assets" / "img" / "foto"
BREITEN = (640, 1000, 1600, 2400)
# Verlauf für Chrom: Schwarz → Midnight Green → Teal → Mint → Soft Neon Mint → Mint Glow
STUFEN = [(0.00, (3, 9, 7)), (0.18, (6, 19, 15)), (0.42, (11, 61, 51)), (0.68, (0, 201, 154)), (0.86, (140, 255, 218)), (1.00, (232, 255, 247))]


def chrom(im: Image.Image) -> Image.Image:
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255.0
    l = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2])
    l = np.clip((l - 0.02) / 0.96, 0, 1) ** 1.08
    xs = np.array([s[0] for s in STUFEN]); out = np.zeros(a.shape, np.float32)
    for k in range(3):
        out[..., k] = np.interp(l, xs, np.array([s[1][k] for s in STUFEN], np.float32))
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("original"); ap.add_argument("name"); ap.add_argument("--art", choices=("mint", "chrom"), default="mint")
    a = ap.parse_args()
    im = Image.open(a.original).convert("RGB")
    im = mint(im) if a.art == "mint" else chrom(im)
    for w in BREITEN:
        if w > im.width:
            continue
        k = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        k.save(FOTO / f"{a.name}-{w}.jpg", quality=84, optimize=True, progressive=True)
        k.save(FOTO / f"{a.name}-{w}.webp", quality=80, method=6)
    print(a.name, im.size, "→", [w for w in BREITEN if w <= im.width])


if __name__ == "__main__":
    main()
