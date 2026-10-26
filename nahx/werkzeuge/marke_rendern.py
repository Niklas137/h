"""Rendert die Rasterfassungen der Marke aus den SVG-Vektoren (Stand 2026-10-26, Mint).

    python3 nahx/werkzeuge/marke_rendern.py

Erzeugt in nahx/assets/img: og-nahx.jpg (1200 × 630), icon-512.png, apple-touch-icon.png (180),
favicon.ico (16 und 32). Braucht Playwright mit Chromium und Pillow.
"""
import base64
import io
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

IMG = Path(__file__).resolve().parent.parent / "assets" / "img"
FONTS = IMG.parent / "fonts"

OG = """<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Outfit;src:url(data:font/ttf;base64,{font})}}
html,body{{margin:0;width:1200px;height:630px;overflow:hidden;background:#030907}}
body{{background:radial-gradient(ellipse 620px 420px at 900px 230px,rgba(0,240,190,.20),rgba(0,240,190,0) 70%),
  radial-gradient(ellipse 700px 300px at 200px 700px,rgba(52,82,74,.45),rgba(52,82,74,0) 70%),#030907;position:relative}}
.linien{{position:absolute;inset:0;background:repeating-linear-gradient(90deg,rgba(232,255,247,.035) 0 1px,transparent 1px 120px)}}
img{{position:absolute;left:100px;top:150px;width:640px}}
p{{position:absolute;left:112px;top:432px;margin:0;font:400 27px Outfit;letter-spacing:.2em;color:#C2D1CB}}
</style></head><body><div class="linien"></div><img src="data:image/svg+xml;base64,{logo}"><p>TECHNIK VERSTEHEN. LÖSUNGEN SCHAFFEN.</p></body></html>"""

ICON = """<!doctype html><html><head><style>html,body{{margin:0;width:{n}px;height:{n}px;overflow:hidden;background:transparent}}
img{{display:block;width:{n}px;height:{n}px}}</style></head><body><img src="data:image/svg+xml;base64,{icon}"></body></html>"""


def main():
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        seite = b.new_page(viewport={"width": 1200, "height": 630})
        b64 = lambda f: base64.b64encode(f.read_bytes()).decode()
        seite.set_content(OG.format(font=b64(FONTS / "outfit-variable.ttf"), logo=b64(IMG / "nahx-logo.svg")), wait_until="networkidle")
        seite.wait_for_timeout(300)
        Image.open(io.BytesIO(seite.screenshot())).convert("RGB").save(IMG / "og-nahx.jpg", quality=88, optimize=True, progressive=True)
        bilder = {}
        for n in (512, 180, 32, 16):
            s = b.new_page(viewport={"width": n, "height": n})
            s.set_content(ICON.format(n=n, icon=b64(IMG / "favicon.svg")), wait_until="networkidle")
            bilder[n] = Image.open(io.BytesIO(s.screenshot(omit_background=True))).convert("RGBA")
        b.close()
    bilder[512].save(IMG / "icon-512.png", optimize=True)
    bilder[180].save(IMG / "apple-touch-icon.png", optimize=True)
    bilder[32].save(IMG / "favicon.ico", sizes=[(32, 32), (16, 16)], append_images=[bilder[16]])
    print("og-nahx.jpg, icon-512.png, apple-touch-icon.png, favicon.ico geschrieben")


if __name__ == "__main__":
    main()
