"""PDF-Berichte: Prüfbericht (intern) und Fachbericht (Kunde), je in einer Berichtssprache.

Schrift: IBM Plex Sans (OFL) aus app/static/fonts, damit auch Ukrainisch und Russisch gesetzt werden.
Fehlt die Schrift, fällt der Bericht auf DejaVu Sans (Linux) oder Helvetica zurück.
"""
from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .. import config
from . import texte

GOLD = colors.HexColor("#dda440")
INK = colors.HexColor("#241f1a")
MUTED = colors.HexColor("#5e564b")
LINIE = colors.HexColor("#d9cfbc")
KOPFFLAECHE = colors.HexColor("#e6ddcd")
AMPEL_FARBEN = {"gruen": colors.HexColor("#2f6b3f"), "gelb": colors.HexColor("#8a4f06"), "rot": colors.HexColor("#a32020")}

# Seitenrand links und rechts; die Tabellen füllen die Breite dazwischen.
RAND = 16 * mm
BREITE = A4[0] - 2 * RAND

_SCHRIFT: dict[str, str] = {}


def _schriften() -> dict[str, str]:
    """Registriert die Schriften einmal und gibt die Namen für normal und fett zurück."""
    if _SCHRIFT:
        return _SCHRIFT
    kandidaten = [
        ("PlexSans", config.FONTS / "IBMPlexSans-Regular.ttf", "PlexSansSemiBold", config.FONTS / "IBMPlexSans-SemiBold.ttf"),
        ("DejaVuSans", Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"), "DejaVuSans-Bold", Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")),
    ]
    for normal, pfad_n, fett, pfad_f in kandidaten:
        if pfad_n.exists() and pfad_f.exists():
            try:
                pdfmetrics.registerFont(TTFont(normal, str(pfad_n)))
                pdfmetrics.registerFont(TTFont(fett, str(pfad_f)))
                _SCHRIFT.update({"normal": normal, "fett": fett, "unicode": "1"})
                return _SCHRIFT
            except Exception:
                continue
    _SCHRIFT.update({"normal": "Helvetica", "fett": "Helvetica-Bold", "unicode": "0"})
    return _SCHRIFT


def _stile() -> dict[str, ParagraphStyle]:
    s = _schriften()
    return {
        "titel": ParagraphStyle("titel", fontName=s["fett"], fontSize=22, leading=27, textColor=INK, spaceAfter=2),
        "untertitel": ParagraphStyle("untertitel", fontName=s["normal"], fontSize=11, leading=15, textColor=MUTED),
        "h2": ParagraphStyle("h2", fontName=s["fett"], fontSize=13, leading=17, textColor=INK, spaceBefore=10, spaceAfter=6),
        "text": ParagraphStyle("text", fontName=s["normal"], fontSize=10, leading=14, textColor=INK, alignment=TA_LEFT),
        "klein": ParagraphStyle("klein", fontName=s["normal"], fontSize=8.5, leading=11.5, textColor=INK, embeddedHyphenation=1),
        "kleinfett": ParagraphStyle("kleinfett", fontName=s["fett"], fontSize=8.5, leading=11.5, textColor=INK, embeddedHyphenation=1),
        # Fundtabelle mit acht Spalten: etwas kleiner, damit kein Wort mitten im Wort umbricht.
        "tab": ParagraphStyle("tab", fontName=s["normal"], fontSize=8, leading=10.5, textColor=INK, embeddedHyphenation=1),
        "tabfett": ParagraphStyle("tabfett", fontName=s["fett"], fontSize=8, leading=10.5, textColor=INK, embeddedHyphenation=1),
        "muted": ParagraphStyle("muted", fontName=s["normal"], fontSize=9, leading=12.5, textColor=MUTED),
        "label": ParagraphStyle("label", fontName=s["normal"], fontSize=8.5, leading=11, textColor=MUTED),
        "wert": ParagraphStyle("wert", fontName=s["fett"], fontSize=11, leading=14, textColor=INK),
    }


def _esc(text: Any) -> str:
    return str(text if text is not None else "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _datum(iso: str | None) -> str:
    if not iso:
        return datetime.now().strftime("%d.%m.%Y")
    try:
        return datetime.fromisoformat(iso).strftime("%d.%m.%Y")
    except ValueError:
        return iso


def _kopf_fuss(sprache: str, art: str, gesamt: int | None):
    s = _schriften()

    def zeichnen(canvas, doc):
        canvas.saveState()
        breite, hoehe = A4
        canvas.setFillColor(GOLD)
        canvas.rect(0, hoehe - 6 * mm, breite, 6 * mm, stroke=0, fill=1)
        canvas.setFillColor(INK)
        canvas.setFont(s["fett"], 9)
        canvas.drawString(RAND, hoehe - 14 * mm, config.BERICHT_KOPF)
        canvas.setFont(s["normal"], 9)
        canvas.setFillColor(MUTED)
        canvas.drawRightString(breite - RAND, hoehe - 14 * mm, texte.t(sprache, "titel_pruef" if art == "pruef" else "titel_fach"))
        canvas.setStrokeColor(LINIE)
        canvas.setLineWidth(0.5)
        canvas.line(RAND, 16 * mm, breite - RAND, 16 * mm)
        canvas.setFont(s["normal"], 8)
        canvas.drawString(RAND, 11 * mm, f"{config.BERICHT_FUSS} · {texte.t(sprache, 'erstellt_mit')}")
        if gesamt is not None:
            canvas.drawRightString(breite - RAND, 11 * mm, texte.t(sprache, "seite", n=doc.page, m=gesamt))
        canvas.restoreState()

    return zeichnen


def _bauen(story: list, sprache: str, art: str) -> bytes:
    """Zwei Durchläufe: erst nur Seiten zählen, dann mit Kopf, Fuß und Gesamtzahl setzen."""

    def einmal(gesamt: int | None) -> tuple[bytes, int]:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=RAND,
            rightMargin=RAND,
            topMargin=24 * mm,
            bottomMargin=22 * mm,
            title=texte.t(sprache, "titel_pruef" if art == "pruef" else "titel_fach"),
            author=config.BERICHT_KOPF,
        )
        zaehler = {"n": 0}
        basis = _kopf_fuss(sprache, art, gesamt)

        def seite(canvas, d):
            zaehler["n"] = d.page
            if gesamt is not None:
                basis(canvas, d)

        doc.build([*story], onFirstPage=seite, onLaterPages=seite)
        return buffer.getvalue(), zaehler["n"]

    # Story-Objekte dürfen nicht zweimal gebaut werden, deshalb Fabrik über Kopie der Liste.
    _, seiten = einmal(None)
    daten, _ = einmal(seiten)
    return daten


def _kopfblock(ergebnis: dict[str, Any], meta: dict[str, Any], sprache: str, art: str, st: dict) -> list:
    titel = texte.t(sprache, "titel_pruef" if art == "pruef" else "titel_fach")
    untertitel = texte.t(sprache, "untertitel_pruef" if art == "pruef" else "untertitel_fach")
    story: list = [Paragraph(_esc(titel), st["titel"]), Paragraph(_esc(untertitel), st["untertitel"]), Spacer(1, 8 * mm)]

    regel_namen = {"basis": texte.t(sprache, "norm_basis"), "din": texte.t(sprache, "norm_din"), "ce": texte.t(sprache, "norm_ce")}
    regeln = ", ".join(regel_namen[r] for r in ergebnis.get("regelsaetze", []) if r in regel_namen)
    zellen = [
        (texte.t(sprache, "dokument"), meta.get("dateiname", "")),
        (texte.t(sprache, "datum"), _datum(meta.get("erstellt"))),
        (texte.t(sprache, "geprueft_von"), meta.get("pruefer", "")),
        (texte.t(sprache, "regelsaetze"), regeln),
    ]
    if ergebnis.get("punkteGesamt"):
        satz = texte.t(sprache, "punkte_satz", n=ergebnis.get("punkteGeprueft", 0), von=ergebnis["punkteGesamt"])
        weg = ergebnis.get("ausgelassen", [])
        if weg:
            liste = ", ".join(f"{a['id']} {texte.bereich(sprache, {'Bereich': a.get('bereich', ''), **a})}" for a in weg)
            satz += ". " + texte.t(sprache, "punkte_ausgelassen", liste=liste)
        zellen.append((texte.t(sprache, "pruefpunkte"), satz))
    daten = [[Paragraph(_esc(k), st["label"]), Paragraph(_esc(v), st["text"])] for k, v in zellen]
    tab = Table(daten, colWidths=[45 * mm, BREITE - 45 * mm])
    tab.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOTTOMPADDING", (0, 0), (-1, -1), 3), ("TOPPADDING", (0, 0), (-1, -1), 3)]))
    story.append(tab)
    story.append(Spacer(1, 6 * mm))

    ampel = ergebnis.get("ampel", "rot")
    kacheln = [
        [Paragraph(_esc(texte.t(sprache, "bewertung")), st["label"]), Paragraph(f"{ergebnis.get('score', 0)} %", st["wert"])],
        [Paragraph(_esc(texte.t(sprache, "ampel")), st["label"]), Paragraph(_esc(texte.ampel(sprache, ampel)), ParagraphStyle("ampel", parent=st["wert"], textColor=AMPEL_FARBEN.get(ampel, INK)))],
        [Paragraph(_esc(texte.t(sprache, "funde_anzahl")), st["label"]), Paragraph(str(len(ergebnis.get("funde", []))), st["wert"])],
    ]
    if art == "pruef":
        kacheln.append([Paragraph(_esc(texte.t(sprache, "aufwand")), st["label"]), Paragraph(f"{str(ergebnis.get('stunden', 0)).replace('.', ',')} {texte.t(sprache, 'stunden')}", st["wert"])])
    zeile = [[k[0] for k in kacheln], [k[1] for k in kacheln]]
    breite = BREITE / len(kacheln)
    kt = Table(zeile, colWidths=[breite] * len(kacheln))
    kt.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), KOPFFLAECHE),
                ("BOX", (0, 0), (-1, -1), 0.5, LINIE),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, LINIE),
                ("TOPPADDING", (0, 0), (-1, 0), 6),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(kt)
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(_esc(texte.t(sprache, "hinweis_intern" if art == "pruef" else "hinweis_fach")), st["muted"]))
    story.append(Paragraph(_esc(texte.t(sprache, "hinweis_vorpruefung", firma=config.BERICHT_KOPF)), st["muted"]))
    for hinweis in ergebnis.get("lesehinweise", []):
        story.append(Paragraph(_esc(texte.t(sprache, "lesehinweis") + " " + texte.lesehinweis(sprache, hinweis)), st["muted"]))
    return story


def _fazitblock(ergebnis: dict[str, Any], sprache: str, st: dict) -> list:
    text = texte.fazit(sprache, [tuple(x) for x in ergebnis.get("fazitTeile", [])]) or ergebnis.get("fazit", "")
    return [Paragraph(_esc(texte.t(sprache, "fazit")), st["h2"]), Paragraph(_esc(text), st["text"])]


def _todoblock(ergebnis: dict[str, Any], sprache: str, st: dict, mit_aufwand: bool) -> list:
    story: list = [Paragraph(_esc(texte.t(sprache, "todo")), st["h2"])]
    if "ce" not in ergebnis.get("regelsaetze", []):
        story.append(Paragraph(_esc(texte.t(sprache, "ce_nicht_geprueft")), st["text"]))
        return story
    todos = ergebnis.get("todos", [])
    if not todos:
        story.append(Paragraph(_esc(texte.t(sprache, "keine_todos")), st["text"]))
        return story
    funde_index = {f.get("ID"): f for f in ergebnis.get("funde", [])}
    kopf = [texte.t(sprache, "sp_bereich"), texte.t(sprache, "sp_massnahme"), texte.t(sprache, "sp_prioritaet")]
    if mit_aufwand:
        kopf.append(texte.t(sprache, "sp_aufwand_h"))
    zeilen = [[Paragraph(_esc(k), st["kleinfett"]) for k in kopf]]
    for todo in todos:
        fund = funde_index.get(todo.get("ID"), {})
        zeile = [
            Paragraph(_esc(texte.bereich(sprache, fund) if fund else todo.get("Bereich")), st["klein"]),
            Paragraph(_esc(texte.empfehlung(sprache, fund) if fund else todo.get("Maßnahme")), st["klein"]),
            Paragraph(_esc(texte.prioritaet(sprache, todo.get("Priorität"))), st["klein"]),
        ]
        if mit_aufwand:
            zeile.append(Paragraph(str(todo.get("Aufwand (h)", "")).replace(".", ","), st["klein"]))
        zeilen.append(zeile)
    breiten = [37 * mm, BREITE - 77 * mm, 22 * mm, 18 * mm] if mit_aufwand else [42 * mm, BREITE - 68 * mm, 26 * mm]
    tab = Table(zeilen, colWidths=breiten, repeatRows=1)
    tab.setStyle(_tabellenstil())
    story.append(tab)
    return story


def _massnahmenblock(ergebnis: dict[str, Any], sprache: str, st: dict) -> list:
    """Fachbericht: Empfehlungen je Fund ohne Gewichtung und Aufwand."""
    story: list = [Paragraph(_esc(texte.t(sprache, "massnahmen")), st["h2"])]
    funde = [f for f in ergebnis.get("funde", []) if f.get("Normlogik") != "CE / EU-Konformität"]
    if not funde:
        story.append(Paragraph(_esc(texte.t(sprache, "keine_massnahmen")), st["text"]))
        return story
    kopf = [texte.t(sprache, "sp_bereich"), texte.t(sprache, "sp_klasse"), texte.t(sprache, "sp_empfehlung")]
    zeilen = [[Paragraph(_esc(k), st["kleinfett"]) for k in kopf]]
    for f in funde:
        zeilen.append(
            [
                Paragraph(_esc(texte.bereich(sprache, f)), st["klein"]),
                Paragraph(_esc(texte.klasse(sprache, f.get("Fehlerklasse"))), st["klein"]),
                Paragraph(_esc(texte.empfehlung(sprache, f)), st["klein"]),
            ]
        )
    tab = Table(zeilen, colWidths=[37 * mm, 26 * mm, BREITE - 63 * mm], repeatRows=1)
    tab.setStyle(_tabellenstil())
    story.append(tab)
    return story


def _fundeblock(ergebnis: dict[str, Any], sprache: str, st: dict) -> list:
    story: list = [Paragraph(_esc(texte.t(sprache, "funde")), st["h2"])]
    funde = ergebnis.get("funde", [])
    if not funde:
        story.append(Paragraph(_esc(texte.t(sprache, "keine_funde")), st["text"]))
        return story
    kopf = [
        texte.t(sprache, "sp_id"),
        texte.t(sprache, "sp_normlogik"),
        texte.t(sprache, "sp_bereich"),
        texte.t(sprache, "sp_klasse"),
        texte.t(sprache, "sp_bewertung"),
        texte.t(sprache, "sp_empfehlung"),
        texte.t(sprache, "sp_gewichtung"),
        texte.t(sprache, "sp_minuten"),
    ]
    zeilen = [[Paragraph(_esc(k), st["tabfett"]) for k in kopf]]
    for f in funde:
        zeilen.append(
            [
                Paragraph(_esc(f.get("ID")), st["tab"]),
                Paragraph(_esc(texte.normlogik(sprache, f.get("Normlogik"))), st["tab"]),
                Paragraph(_esc(texte.bereich(sprache, f)), st["tab"]),
                Paragraph(_esc(texte.klasse(sprache, f.get("Fehlerklasse"))), st["tab"]),
                Paragraph(_esc(texte.bewertung(sprache, f)), st["tab"]),
                Paragraph(_esc(texte.empfehlung(sprache, f)), st["tab"]),
                Paragraph(str(f.get("Gewichtung", "")), st["tab"]),
                Paragraph(str(f.get("Zeitaufwand_min", "")), st["tab"]),
            ]
        )
    tab = Table(zeilen, colWidths=[15 * mm, 21 * mm, 32 * mm, 25.5 * mm, 23 * mm, BREITE - 134.5 * mm, 9.5 * mm, 8.5 * mm], repeatRows=1)
    tab.setStyle(_tabellenstil())
    story.append(tab)
    return story


def _tabellenstil() -> TableStyle:
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), KOPFFLAECHE),
            ("LINEBELOW", (0, 0), (-1, 0), 0.75, GOLD),
            ("LINEBELOW", (0, 1), (-1, -1), 0.3, LINIE),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ]
    )


def pruefbericht(ergebnis: dict[str, Any], meta: dict[str, Any], sprache: str) -> bytes:
    st = _stile()
    story = _kopfblock(ergebnis, meta, sprache, "pruef", st)
    story += _fazitblock(ergebnis, sprache, st)
    story += _todoblock(ergebnis, sprache, st, mit_aufwand=True)
    story += _fundeblock(ergebnis, sprache, st)
    return _bauen(story, sprache, "pruef")


def fachbericht(ergebnis: dict[str, Any], meta: dict[str, Any], sprache: str) -> bytes:
    st = _stile()
    story = _kopfblock(ergebnis, meta, sprache, "fach", st)
    story += _fazitblock(ergebnis, sprache, st)
    story += _todoblock(ergebnis, sprache, st, mit_aufwand=False)
    story += _massnahmenblock(ergebnis, sprache, st)
    return _bauen(story, sprache, "fach")


def erzeugen(art: str, ergebnis: dict[str, Any], meta: dict[str, Any], sprache: str) -> bytes:
    if art == "pruef":
        return pruefbericht(ergebnis, meta, sprache)
    if art == "fach":
        return fachbericht(ergebnis, meta, sprache)
    raise ValueError(f"Unbekannte Berichtsart: {art}")


def freier_dateiname(ordner: Path, art: str, dokument: str, sprache: str, erstellt: str | None, inhalt: bytes | None = None) -> Path:
    """Nächster freier Name im Ordner: v01, v02, ... Ein vorhandener, byte-gleicher Bericht wird wiederverwendet."""
    for version in range(1, 1000):
        pfad = ordner / dateiname(art, dokument, sprache, erstellt, version)
        if not pfad.exists():
            return pfad
        if inhalt is not None and pfad.read_bytes() == inhalt:
            return pfad
    raise RuntimeError("Kein freier Dateiname gefunden.")


def dateiname(art: str, dokument: str, sprache: str, erstellt: str | None = None, version: int = 1) -> str:
    """Schema: JJJJ-MM-TT_Dokument_Pruefbericht_DE_v01.pdf"""
    tag = (erstellt or datetime.now().isoformat())[:10]
    stamm = Path(dokument).stem
    stamm = "".join(c if c.isalnum() or c in "-_" else "_" for c in stamm)[:60] or "Dokument"
    bericht = "Pruefbericht" if art == "pruef" else "Fachbericht"
    return f"{tag}_{stamm}_{bericht}_{sprache.upper()}_v{version:02d}.pdf"
