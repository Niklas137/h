#!/usr/bin/env python3
"""Erzeugt aus einer Bericht-JSON die beiden PDFs des SEO-Audits.

Aufruf:
    python3 seo-audit/tools/render_report.py seo-audit/berichte/JJJJ-MM-TT-lauf.json --out seo-audit
    python3 seo-audit/tools/render_report.py <json> --check        # nur prüfen, nichts schreiben
    python3 seo-audit/tools/render_report.py <json> --out DIR --html-only   # HTML statt PDF (Fehlersuche)

Ergebnis in --out:
    SEO-Audit-FSH-Documentation.pdf              A4 hoch, mehrseitiger Bericht
    SEO-Audit-FSH-Documentation-Kurzfassung.pdf  A4 quer, eine Seite

Voraussetzungen: Python 3 (nur Standardbibliothek), Node mit dem Paket playwright und ein
Chromium, wie es die Claude-Code-Umgebung mitbringt (PLAYWRIGHT_BROWSERS_PATH). Den Pfad zu den
Node-Modulen setzt SEO_AUDIT_NODE_MODULES, Standard /opt/node22/lib/node_modules.

Felder der JSON (alle Texte deutsch, keine HTML-Tags):
    domain, firma, stand (JJJJ-MM-TT), uhrzeit (optional, "07:30"), lauf (manuell | freitag-0730 |
    freitag-1600), art (Teilprüfung | Vollprüfung), untertitel, ergebnis_kurz,
    zusammenfassung [Absätze], veraenderungen [Zeilen, optional], pruefstatus [{bereich, status
    (geprueft | teilweise | offen), ergebnis}], pruefumfang [Absätze], befunde [{id, titel,
    prioritaet (hoch | mittel | niedrig), beleg, empfehlung, entwicklung (optional: neu |
    unverändert | verbessert | erledigt)}], massnahmen [{nr, text, prioritaet, aufwand}],
    offene_pruefpunkte [{gruppe, punkte []}] (leer bei Vollprüfung), dafuer_noetig [Zeilen],
    quellen_hinweis, quellen [{text, url (optional), beschreibung (optional)}],
    kurzfassung {untertitel, befunde [ids, höchstens 4], naechste_schritte [{titel, text}] (3)}
"""
import argparse
import html
import json
import os
import subprocess
import sys
import tempfile
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")
ACCENT = "#1F5F6B"
MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August",
          "September", "Oktober", "November", "Dezember"]
LAUF_TEXT = {"manuell": "Manueller Lauf", "freitag-0730": "Wochenaudit Fr 7:30",
             "freitag-1600": "Zwischenstand Fr 16:00"}
STATUS_CHIP = {"geprueft": ("Geprüft", "#DDEBDD", "#2E5E3A"),
               "teilweise": ("Teilweise", "#F5E6C8", "#7A4E00"),
               "offen": ("Offen", "#E7E4DC", "#4A4842")}
PRIO_CHIP = {"hoch": ("Hoch", "#F6DED8", "#8C2B1F"),
             "mittel": ("Mittel", "#F5E6C8", "#7A4E00"),
             "niedrig": ("Niedrig", "#DDEBDD", "#2E5E3A")}
PRIO_ORDER = {"hoch": 0, "mittel": 1, "niedrig": 2}
ENTWICKLUNG = {"neu", "unverändert", "verbessert", "erledigt"}
BERICHT_PDF = "SEO-Audit-FSH-Documentation.pdf"
KURZ_PDF = "SEO-Audit-FSH-Documentation-Kurzfassung.pdf"


def e(text):
    return html.escape(str(text), quote=True)


# ---------------------------------------------------------------- Prüfung

def pruefe(d):
    fehler = []

    def need(key, typ, nonempty=True):
        if key not in d:
            fehler.append(f"Feld fehlt: {key}")
            return False
        if not isinstance(d[key], typ):
            fehler.append(f"Feld {key}: erwartet {typ.__name__}")
            return False
        if nonempty and not d[key]:
            fehler.append(f"Feld {key} ist leer")
            return False
        return True

    for k in ("domain", "firma", "stand", "lauf", "art", "untertitel", "ergebnis_kurz", "quellen_hinweis"):
        need(k, str)
    for k in ("zusammenfassung", "pruefstatus", "pruefumfang", "befunde", "massnahmen", "quellen"):
        need(k, list)
    for k in ("veraenderungen", "offene_pruefpunkte", "dafuer_noetig"):
        if k in d and not isinstance(d[k], list):
            fehler.append(f"Feld {k}: erwartet list")
    if "stand" in d:
        try:
            date.fromisoformat(d["stand"])
        except Exception:
            fehler.append("stand muss JJJJ-MM-TT sein")
    if d.get("lauf") not in LAUF_TEXT:
        fehler.append(f"lauf muss eines von {sorted(LAUF_TEXT)} sein")
    for i, s in enumerate(d.get("pruefstatus") or []):
        if not isinstance(s, dict) or s.get("status") not in STATUS_CHIP or not s.get("bereich") or not s.get("ergebnis"):
            fehler.append(f"pruefstatus[{i}]: bereich, status (geprueft|teilweise|offen), ergebnis")
    ids = []
    for i, b in enumerate(d.get("befunde") or []):
        if not isinstance(b, dict):
            fehler.append(f"befunde[{i}] ist kein Objekt")
            continue
        for k in ("id", "titel", "beleg", "empfehlung"):
            if not b.get(k):
                fehler.append(f"befunde[{i}]: {k} fehlt")
        if b.get("prioritaet") not in PRIO_CHIP:
            fehler.append(f"befunde[{i}]: prioritaet muss hoch|mittel|niedrig sein")
        if b.get("entwicklung") and b["entwicklung"] not in ENTWICKLUNG:
            fehler.append(f"befunde[{i}]: entwicklung muss {sorted(ENTWICKLUNG)} sein")
        ids.append(b.get("id"))
    if len(ids) != len(set(ids)):
        fehler.append("Befund-IDs sind nicht eindeutig")
    for i, m in enumerate(d.get("massnahmen") or []):
        if not isinstance(m, dict) or not m.get("text") or m.get("prioritaet") not in PRIO_CHIP or not m.get("aufwand"):
            fehler.append(f"massnahmen[{i}]: text, prioritaet (hoch|mittel|niedrig), aufwand")
    for i, g in enumerate(d.get("offene_pruefpunkte") or []):
        if not isinstance(g, dict) or not g.get("gruppe") or not isinstance(g.get("punkte"), list):
            fehler.append(f"offene_pruefpunkte[{i}]: gruppe, punkte []")
    for i, q in enumerate(d.get("quellen") or []):
        if not isinstance(q, dict) or not q.get("text"):
            fehler.append(f"quellen[{i}]: text fehlt")
    k = d.get("kurzfassung")
    if not isinstance(k, dict):
        fehler.append("kurzfassung fehlt")
    else:
        if not k.get("untertitel"):
            fehler.append("kurzfassung.untertitel fehlt")
        ns = k.get("naechste_schritte")
        if not isinstance(ns, list) or not 1 <= len(ns) <= 3 or any(not (isinstance(x, dict) and x.get("titel")) for x in ns):
            fehler.append("kurzfassung.naechste_schritte: 1 bis 3 Einträge mit titel (und text)")
        kb = k.get("befunde")
        if kb is not None and (not isinstance(kb, list) or len(kb) > 4 or any(x not in ids for x in kb)):
            fehler.append("kurzfassung.befunde: höchstens 4 vorhandene Befund-IDs")
    return fehler


# ---------------------------------------------------------------- Bausteine

def datum_lang(iso):
    d = date.fromisoformat(iso)
    return f"{d.day}. {MONATE[d.month - 1]} {d.year}"


def datum_kurz(iso):
    d = date.fromisoformat(iso)
    return f"{d.day:02d}.{d.month:02d}.{d.year}"


def chip(kind_table, key):
    text, bg, fg = kind_table[key]
    return f'<span class="chip" style="background:{bg};color:{fg}">{e(text)}</span>'


def chip_grau(text):
    return f'<span class="chip" style="background:#E7E4DC;color:#4A4842">{e(text)}</span>'


def font_css():
    css = open(os.path.join(FONT_DIR, "fonts.css"), encoding="utf-8").read()
    return css.replace("url(./", "url(file://" + FONT_DIR + "/")


def stand_text(d):
    t = datum_lang(d["stand"])
    if d.get("uhrzeit"):
        t += f", {d['uhrzeit']} Uhr"
    return t


def label_text(d):
    return f"SEO-Audit · {d['art']} · {LAUF_TEXT[d['lauf']]} · Stand {datum_kurz(d['stand'])}"


def kurz_befunde(d):
    ids = (d.get("kurzfassung") or {}).get("befunde")
    by_id = {b["id"]: b for b in d["befunde"]}
    if ids:
        return [by_id[i] for i in ids]
    sortiert = sorted(d["befunde"], key=lambda b: PRIO_ORDER[b["prioritaet"]])
    return sortiert[:4]


BASE_CSS = """
html,body{margin:0;background:#FFFFFF}
body{font-family:'IBM Plex Sans','Liberation Sans',sans-serif;color:#1C1B18;-webkit-print-color-adjust:exact;print-color-adjust:exact}
a{color:ACCENT;text-decoration:none}
h1,h2,h3{text-wrap:balance}
p,li,td{text-wrap:pretty}
.mono{font-family:'IBM Plex Mono','Liberation Mono',monospace}
.label{font-family:'IBM Plex Mono','Liberation Mono',monospace;font-size:12px;line-height:18px;letter-spacing:.08em;text-transform:uppercase;font-weight:500;color:ACCENT}
.chip{display:inline-block;padding:2px 10px;border-radius:999px;font-family:'IBM Plex Mono','Liberation Mono',monospace;font-size:12px;line-height:18px;letter-spacing:.06em;text-transform:uppercase;font-weight:500;white-space:nowrap}
""".replace("ACCENT", ACCENT)

BERICHT_CSS = """
body{font-size:16px;line-height:1.55}
.kopf{padding-bottom:22px;border-bottom:2px solid ACCENT}
.kopf h1{margin:14px 0;font-family:'IBM Plex Serif',Georgia,serif;font-size:42px;line-height:1.12;font-weight:600}
.kopf p{margin:0;font-size:18px;line-height:1.5;color:#5B5850}
section{margin-top:36px}
.h2{display:flex;align-items:baseline;gap:14px;margin:0 0 16px;break-after:avoid}
.h2 .nr{font-family:'IBM Plex Mono','Liberation Mono',monospace;font-size:14px;font-weight:500;color:ACCENT}
.h2 h2{margin:0;font-family:'IBM Plex Serif',Georgia,serif;font-size:26px;line-height:1.25;font-weight:600}
p{margin:0 0 16px;orphans:3;widows:3}
p:last-child{margin-bottom:0}
table{width:100%;border-collapse:collapse;font-size:14px;line-height:1.45;margin-top:8px;break-inside:auto}
th{text-align:left;padding:8px 12px 8px 0;border-bottom:1.5px solid #1C1B18;font-weight:600}
th:last-child,td:last-child{padding-right:0}
td{padding:10px 12px 10px 0;border-bottom:1px solid #D9D5CB;vertical-align:top}
tr{break-inside:avoid}
thead{display:table-header-group}
td.nr,th.nr{text-align:right;padding-right:14px;font-family:'IBM Plex Mono','Liberation Mono',monospace}
td.fett{font-weight:500}
.aenderungen{margin:0;padding:0;list-style:none}
.aenderungen li{display:flex;gap:12px;margin-top:8px}
.aenderungen li:first-child{margin-top:0}
.aenderungen .punkt{font-family:'IBM Plex Mono','Liberation Mono',monospace;color:ACCENT;flex-shrink:0}
.befund{padding:20px 0 24px;border-top:1px solid #D9D5CB;break-inside:avoid}
.befund:last-child{padding-bottom:8px}
.befund .zeile{display:flex;align-items:center;gap:12px;margin-bottom:10px}
.befund .id{font-family:'IBM Plex Mono','Liberation Mono',monospace;font-size:13px;font-weight:500;color:ACCENT}
.befund h3{margin:0;font-family:'IBM Plex Serif',Georgia,serif;font-size:20px;line-height:1.3;font-weight:600;flex-grow:1}
.befund p{margin:0 0 10px}
.befund p:last-child{margin-bottom:0}
.block{break-inside:avoid}
.spalten{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px;font-size:14px;line-height:1.5;margin-top:16px}
.spalten .label{padding-bottom:6px;border-bottom:1px solid #D9D5CB}
.spalten ul{list-style:none;margin:0;padding:0}
.spalten li{margin-top:6px}
.box{margin-top:16px;padding:18px 20px;background:#F4F2EC;border:1px solid #D9D5CB;border-radius:8px;font-size:15px;line-height:1.5;break-inside:avoid}
.box .titel{font-weight:600}
.box .zeile{display:flex;gap:12px;margin-top:8px}
.box .buchstabe{font-family:'IBM Plex Mono','Liberation Mono',monospace;color:ACCENT;flex-shrink:0}
.hinweis{font-size:14px;color:#5B5850;margin:0 0 4px}
.quellen{font-size:14px;line-height:1.5}
.quellen div{margin-top:8px}
""".replace("ACCENT", ACCENT)

KURZ_CSS = """
html,body{background:#F7F6F2}
.blatt{width:297mm;height:209.5mm;box-sizing:border-box;display:flex;align-items:center;justify-content:center;overflow:hidden;background:#F7F6F2}
.board{zoom:.88;width:1200px;height:675px;box-sizing:border-box;padding:44px 56px 40px;display:flex;flex-direction:column;gap:20px;background:#F7F6F2;color:#1C1B18}
.kopf{display:flex;align-items:flex-end;justify-content:space-between;gap:32px;padding-bottom:18px;border-bottom:2px solid ACCENT}
.kopf .links{display:flex;flex-direction:column;gap:8px}
.kopf h1{margin:0;font-family:'IBM Plex Serif',Georgia,serif;font-size:38px;line-height:1.1;font-weight:600}
.kopf .sub{font-size:15px;line-height:1.4;color:#5B5850}
.kopf .rechts{display:flex;flex-direction:column;align-items:flex-end;gap:6px;text-align:right}
.kopf .rechts .label{color:#5B5850}
.kopf .ergebnis{font-family:'IBM Plex Serif',Georgia,serif;font-size:22px;line-height:1.25;font-weight:600;max-width:380px}
.mitte{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,1fr);gap:20px;flex-grow:1}
.karten{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));grid-template-rows:repeat(2,minmax(0,1fr));gap:14px}
.karte{display:flex;flex-direction:column;gap:8px;padding:16px 18px;background:#FFFFFF;border:1px solid #D9D5CB;border-radius:10px}
.karte .zeile{display:flex;align-items:center;gap:10px}
.karte .id{font-family:'IBM Plex Mono','Liberation Mono',monospace;font-size:13px;font-weight:500;color:ACCENT}
.karte .titel{font-family:'IBM Plex Serif',Georgia,serif;font-size:18px;line-height:1.25;font-weight:600}
.karte .text{font-size:14px;line-height:1.45;color:#3A3832}
.status{display:flex;flex-direction:column;padding:16px 18px 8px;background:#FFFFFF;border:1px solid #D9D5CB;border-radius:10px}
.status .label{padding-bottom:8px}
.status .zeile{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:9px 0;border-top:1px solid #EAE7DF;font-size:14px}
.schritte{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;padding-top:16px;border-top:1px solid #D9D5CB}
.schritt{display:flex;gap:12px;align-items:flex-start}
.schritt .nr{font-family:'IBM Plex Mono','Liberation Mono',monospace;font-size:22px;line-height:1;font-weight:500;color:ACCENT;flex-shrink:0}
.schritt .titel{font-size:15px;font-weight:600;line-height:1.3}
.schritt .text{font-size:13px;line-height:1.4;color:#5B5850;margin-top:2px}
.karte .chip,.status .chip{padding:1px 9px}
""".replace("ACCENT", ACCENT)


# ---------------------------------------------------------------- Bericht

def bericht_html(d):
    out = []
    nr = [0]

    def h2(titel):
        nr[0] += 1
        return f'<div class="h2"><span class="nr">{nr[0]:02d}</span><h2>{e(titel)}</h2></div>'

    out.append(f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8"><title>SEO-Audit FSH-Documentation</title>
<style>{font_css()}{BASE_CSS}{BERICHT_CSS}</style></head><body>
<div class="kopf">
  <div class="label">{e(label_text(d))}</div>
  <h1>{e(d['domain'])}</h1>
  <p>{e(d['untertitel'])}</p>
</div>""")

    # 01 Zusammenfassung
    out.append(f"<section>{h2('Zusammenfassung')}")
    out.extend(f"<p>{e(a)}</p>" for a in d["zusammenfassung"])
    out.append('<table><thead><tr><th style="width:180px">Bereich</th><th style="width:110px">Status</th><th>Ergebnis</th></tr></thead><tbody>')
    for s in d["pruefstatus"]:
        out.append(f'<tr><td class="fett">{e(s["bereich"])}</td><td>{chip(STATUS_CHIP, s["status"])}</td><td>{e(s["ergebnis"])}</td></tr>')
    out.append("</tbody></table></section>")

    # Veränderungen (nur wenn vorhanden)
    if d.get("veraenderungen"):
        out.append(f'<section class="block">{h2("Veränderungen seit dem letzten Lauf")}<ul class="aenderungen">')
        for z in d["veraenderungen"]:
            out.append(f'<li><span class="punkt">–</span><span>{e(z)}</span></li>')
        out.append("</ul></section>")

    # Prüfumfang
    out.append(f"<section>{h2('Prüfumfang und Grenzen')}")
    out.extend(f"<p>{e(a)}</p>" for a in d["pruefumfang"])
    out.append("</section>")

    # Befunde
    out.append(f"<section>{h2('Befunde')}")
    for b in d["befunde"]:
        extra = chip_grau(b["entwicklung"]) if b.get("entwicklung") else ""
        out.append(f"""<div class="befund"><div class="zeile"><span class="id">{e(b['id'])}</span><h3>{e(b['titel'])}</h3>{extra}{chip(PRIO_CHIP, b['prioritaet'])}</div>
<p><strong>Beleg.</strong> {e(b['beleg'])}</p><p><strong>Empfehlung.</strong> {e(b['empfehlung'])}</p></div>""")
    out.append("</section>")

    # Maßnahmenplan
    out.append(f"<section>{h2('Maßnahmenplan')}")
    out.append('<table><thead><tr><th class="nr" style="width:28px">Nr.</th><th>Maßnahme</th><th style="width:84px">Priorität</th><th style="width:72px">Aufwand</th></tr></thead><tbody>')
    for i, m in enumerate(d["massnahmen"], start=1):
        out.append(f'<tr><td class="nr">{e(m.get("nr", i))}</td><td>{e(m["text"])}</td><td>{chip(PRIO_CHIP, m["prioritaet"])}</td><td>{e(str(m["aufwand"]).capitalize())}</td></tr>')
    out.append("</tbody></table></section>")

    # Offene Prüfpunkte (nur wenn vorhanden)
    gruppen = [g for g in d.get("offene_pruefpunkte") or [] if g.get("punkte")]
    if gruppen or d.get("dafuer_noetig"):
        out.append(f'<section><div class="block">{h2("Offene Prüfpunkte")}')
        out.append("<p>Diese Punkte gehören zu einem vollständigen Audit und konnten in diesem Lauf nicht bewertet werden.</p>")
        if gruppen:
            out.append('<div class="spalten">')
            for g in gruppen:
                out.append(f'<div><div class="label">{e(g["gruppe"])}</div><ul>')
                out.extend(f"<li>{e(p)}</li>" for p in g["punkte"])
                out.append("</ul></div>")
            out.append("</div>")
        out.append("</div>")
        if d.get("dafuer_noetig"):
            out.append('<div class="box"><div class="titel">Dafür nötig (eine Option genügt)</div>')
            for i, z in enumerate(d["dafuer_noetig"]):
                out.append(f'<div class="zeile"><span class="buchstabe">{"abcdefgh"[i % 8]}</span><span>{e(z)}</span></div>')
            out.append("</div>")
        out.append("</section>")

    # Quellen
    out.append(f'<section class="block">{h2("Quellen")}<p class="hinweis">{e(d["quellen_hinweis"])}</p><div class="quellen">')
    for q in d["quellen"]:
        text = f'<a href="{e(q["url"])}">{e(q["text"])}</a>' if q.get("url") else e(q["text"])
        if q.get("beschreibung"):
            text += f" – {e(q['beschreibung'])}"
        out.append(f"<div>{text}</div>")
    out.append("</div></section></body></html>")
    return "\n".join(out)


# ---------------------------------------------------------------- Kurzfassung

def kurz_html(d):
    k = d["kurzfassung"]
    out = [f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8"><title>SEO-Audit FSH-Documentation – Kurzfassung</title>
<style>{font_css()}{BASE_CSS}{KURZ_CSS}</style></head><body><div class="blatt"><div class="board">
<div class="kopf">
  <div class="links">
    <div class="label">SEO-Audit · Kurzfassung · {e(LAUF_TEXT[d['lauf']])} · Stand {e(datum_kurz(d['stand']))}{(' ' + e(d['uhrzeit'])) if d.get('uhrzeit') else ''}</div>
    <h1>FSH-Documentation</h1>
    <div class="sub">{e(k['untertitel'])}</div>
  </div>
  <div class="rechts"><div class="label">Ergebnis</div><div class="ergebnis">{e(d['ergebnis_kurz'])}</div></div>
</div>
<div class="mitte"><div class="karten">"""]
    for b in kurz_befunde(d):
        text = b.get("kurz") or b["beleg"]
        out.append(f"""<div class="karte"><div class="zeile"><span class="id">{e(b['id'])}</span>{chip(PRIO_CHIP, b['prioritaet'])}</div>
<div class="titel">{e(b['titel'])}</div><div class="text">{e(text)}</div></div>""")
    out.append('</div><div class="status"><div class="label">Prüfstatus</div>')
    for s in d["pruefstatus"]:
        out.append(f'<div class="zeile"><span>{e(s["bereich"])}</span>{chip(STATUS_CHIP, s["status"])}</div>')
    out.append('</div></div><div class="schritte">')
    for i, s in enumerate(k["naechste_schritte"], start=1):
        out.append(f'<div class="schritt"><span class="nr">{i}</span><div><div class="titel">{e(s["titel"])}</div><div class="text">{e(s.get("text", ""))}</div></div></div>')
    out.append("</div></div></div></body></html>")
    return "\n".join(out)


# ---------------------------------------------------------------- PDF

NODE_SCRIPT = r"""
const fs = require('fs');
const playwright = require('playwright');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  let browser;
  const args = ['--allow-file-access-from-files'];
  try { browser = await playwright.chromium.launch({ args }); }
  catch (e) {
    const root = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
    const dir = fs.readdirSync(root).filter(n => /^chromium-\d+$/.test(n)).sort().pop();
    if (!dir) throw e;
    browser = await playwright.chromium.launch({ executablePath: `${root}/${dir}/chrome-linux/chrome`, args });
  }
  for (const job of jobs) {
    const page = await browser.newPage();
    await page.goto('file://' + job.html, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    const loaded = await page.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').length);
    if (job.kind === 'bericht') {
      await page.pdf({ path: job.pdf, format: 'A4', printBackground: true, preferCSSPageSize: false,
        margin: { top: '17mm', right: '19mm', bottom: '20mm', left: '19mm' },
        displayHeaderFooter: true, headerTemplate: '<span></span>',
        footerTemplate: `<div style="width:100%;box-sizing:border-box;padding:0 19mm;display:flex;justify-content:space-between;font-family:'DejaVu Sans Mono','Liberation Mono',monospace;font-size:8px;color:#5B5850;"><span>${job.footer}</span><span>Seite <span class="pageNumber"></span> von <span class="totalPages"></span></span></div>` });
    } else {
      await page.pdf({ path: job.pdf, format: 'A4', landscape: true, printBackground: true, preferCSSPageSize: false,
        margin: { top: '0', right: '0', bottom: '0', left: '0' }, displayHeaderFooter: false });
    }
    console.log(`${job.kind}: ${job.pdf} (Schriften geladen: ${loaded})`);
    await page.close();
  }
  await browser.close();
})().catch(err => { console.error(err); process.exit(1); });
"""


def render_pdfs(jobs):
    env = dict(os.environ)
    env["NODE_PATH"] = os.environ.get("SEO_AUDIT_NODE_MODULES", "/opt/node22/lib/node_modules")
    with tempfile.TemporaryDirectory() as tmp:
        script = os.path.join(tmp, "render.js")
        jobfile = os.path.join(tmp, "jobs.json")
        open(script, "w", encoding="utf-8").write(NODE_SCRIPT)
        json.dump(jobs, open(jobfile, "w", encoding="utf-8"))
        r = subprocess.run(["node", script, jobfile], env=env, capture_output=True, text=True)
        if r.stdout:
            print(r.stdout.strip())
        if r.returncode != 0:
            sys.exit(f"PDF-Erzeugung fehlgeschlagen:\n{r.stderr.strip()}")


def main():
    ap = argparse.ArgumentParser(description="SEO-Audit: JSON → PDF")
    ap.add_argument("json")
    ap.add_argument("--out", help="Zielordner für die PDFs (Standard: Ordner der JSON)")
    ap.add_argument("--check", action="store_true", help="nur prüfen")
    ap.add_argument("--html-only", action="store_true", help="HTML statt PDF schreiben")
    a = ap.parse_args()

    try:
        d = json.load(open(a.json, encoding="utf-8"))
    except Exception as ex:
        sys.exit(f"JSON nicht lesbar: {ex}")
    fehler = pruefe(d)
    if fehler:
        print("Prüfung fehlgeschlagen:")
        for f in fehler:
            print(" -", f)
        sys.exit(1)
    print(f"JSON in Ordnung: {len(d['befunde'])} Befunde, {len(d['massnahmen'])} Maßnahmen, Stand {d['stand']} ({d['lauf']})")
    if a.check:
        return

    out = a.out or os.path.dirname(os.path.abspath(a.json))
    os.makedirs(out, exist_ok=True)
    if a.html_only:
        for name, text in (("bericht.html", bericht_html(d)), ("kurzfassung.html", kurz_html(d))):
            open(os.path.join(out, name), "w", encoding="utf-8").write(text)
            print("HTML:", os.path.join(out, name))
        return

    with tempfile.TemporaryDirectory() as tmp:
        b_html = os.path.join(tmp, "bericht.html")
        k_html = os.path.join(tmp, "kurzfassung.html")
        open(b_html, "w", encoding="utf-8").write(bericht_html(d))
        open(k_html, "w", encoding="utf-8").write(kurz_html(d))
        footer = f"SEO-Audit FSH-Documentation · Stand {datum_kurz(d['stand'])}" + (f" {d['uhrzeit']}" if d.get("uhrzeit") else "")
        render_pdfs([
            {"kind": "bericht", "html": b_html, "pdf": os.path.abspath(os.path.join(out, BERICHT_PDF)), "footer": footer},
            {"kind": "kurz", "html": k_html, "pdf": os.path.abspath(os.path.join(out, KURZ_PDF))},
        ])


if __name__ == "__main__":
    main()
