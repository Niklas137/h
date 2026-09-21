#!/usr/bin/env python3
"""Setzt eine Markdown-Datei (zum Beispiel ein Maßnahmenpaket) als A4-PDF im Stil der Audit-Berichte.

Aufruf:
    python3 seo-audit/tools/md_to_pdf.py seo-audit/massnahmen/JJJJ-MM-TT-phase-2.md [--out <pdf>] [--fusszeile "Text"]

Die erste Überschrift der Datei wird zum Dokumenttitel. Tabellen, Listen, Codeblöcke und
Zitate werden unterstützt (Python-Paket markdown mit den Erweiterungen tables, fenced_code,
sane_lists). Rendering über render_report.py (Chromium/Playwright, mitgelieferte Schriften).
"""
import argparse
import html
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render_report as rr  # noqa: E402

try:
    import markdown
except ImportError:
    sys.exit("Python-Paket markdown fehlt: python3 -m pip install markdown")

MD_CSS = """
body{font-size:15px;line-height:1.55}
h1{margin:0 0 6px;font-family:'IBM Plex Serif',Georgia,serif;font-size:34px;line-height:1.15;font-weight:600}
.kopf{padding-bottom:18px;border-bottom:2px solid ACCENT;margin-bottom:28px}
.kopf .meta{font-size:15px;color:#5B5850;margin-top:8px}
h2{margin:34px 0 12px;font-family:'IBM Plex Serif',Georgia,serif;font-size:24px;line-height:1.25;font-weight:600;break-after:avoid}
h3{margin:22px 0 8px;font-family:'IBM Plex Serif',Georgia,serif;font-size:18px;line-height:1.3;font-weight:600;break-after:avoid}
h4{margin:16px 0 6px;font-size:15px;font-weight:600;break-after:avoid}
p{margin:0 0 12px;orphans:3;widows:3}
ul,ol{margin:0 0 12px;padding-left:22px}
li{margin:3px 0}
table{width:100%;border-collapse:collapse;font-size:12.5px;line-height:1.4;margin:6px 0 16px;break-inside:auto}
th{text-align:left;padding:6px 10px 6px 0;border-bottom:1.5px solid #1C1B18;font-weight:600;vertical-align:bottom}
td{padding:7px 10px 7px 0;border-bottom:1px solid #D9D5CB;vertical-align:top}
th:last-child,td:last-child{padding-right:0}
tr{break-inside:avoid}
thead{display:table-header-group}
code{font-family:'IBM Plex Mono','Liberation Mono',monospace;font-size:12.5px;background:#F1EFE9;padding:1px 4px;border-radius:3px}
pre{margin:0 0 14px;padding:12px 14px;background:#F4F2EC;border:1px solid #D9D5CB;border-radius:6px;font-size:12px;line-height:1.45;white-space:pre-wrap;word-break:break-word;break-inside:avoid}
pre code{background:none;padding:0;font-size:12px}
blockquote{margin:0 0 12px;padding:8px 16px;border-left:3px solid #D9D5CB;color:#3A3832}
hr{border:0;border-top:1px solid #D9D5CB;margin:24px 0}
strong{font-weight:600}
""".replace("ACCENT", rr.ACCENT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("markdown")
    ap.add_argument("--out", help="Ziel-PDF (Standard: gleicher Name mit .pdf)")
    ap.add_argument("--fusszeile", help="Text links in der Fußzeile")
    a = ap.parse_args()
    src = open(a.markdown, encoding="utf-8").read()
    m = re.search(r"^#\s+(.+)$", src, flags=re.M)
    titel = m.group(1).strip() if m else os.path.basename(a.markdown)
    body_md = src[:m.start()] + src[m.end():] if m else src
    body = markdown.markdown(body_md, extensions=["tables", "fenced_code", "sane_lists"], output_format="html5")
    page = f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><title>{html.escape(titel)}</title>
<style>{rr.font_css()}{rr.BASE_CSS}{MD_CSS}</style></head><body>
<div class="kopf"><div class="label">FSH-Documentation · SEO</div><h1>{html.escape(titel)}</h1></div>
{body}</body></html>"""
    out = a.out or os.path.splitext(a.markdown)[0] + ".pdf"
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "doc.html")
        open(p, "w", encoding="utf-8").write(page)
        rr.render_pdfs([{"kind": "bericht", "html": p, "pdf": os.path.abspath(out), "footer": a.fusszeile or titel}])


if __name__ == "__main__":
    main()
