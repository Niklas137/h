"""Word- und PDF-Dateien in Textzeilen mit Überschrift oder Seitenangabe zerlegen.

Grundlage ist read_docx/read_pdf aus app.py. Ergänzt: Word-Tabellen werden mitgelesen,
und PDF-Seiten ohne Textebene (Scans) werden als Lesehinweis gemeldet statt still übergangen.
"""
from __future__ import annotations

import re
from collections import Counter
from io import BytesIO
from typing import IO

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

try:
    from PyPDF2 import PdfReader

    HAS_PYPDF2 = True
except Exception:  # pragma: no cover
    HAS_PYPDF2 = False

try:
    import pdfplumber

    HAS_PDFPLUMBER = True
except Exception:  # pragma: no cover
    HAS_PDFPLUMBER = False


class LeseFehler(Exception):
    """Die Datei konnte nicht gelesen werden oder enthält keinen Text."""


Struktur = list[dict[str, str]]
Hinweis = dict[str, object]  # {"art": "scan_seiten", "seiten": [2, 5], "gesamt": 7}


def _bytesio(daten: bytes | IO[bytes]) -> IO[bytes]:
    if isinstance(daten, (bytes, bytearray)):
        return BytesIO(daten)
    daten.seek(0)
    return daten


def docx_lesen(daten: bytes | IO[bytes]) -> Struktur:
    try:
        doc = Document(_bytesio(daten))
    except Exception as e:
        raise LeseFehler(f"Fehler beim Laden der Word-Datei: {e}") from e
    structured: Struktur = []
    current_heading = "Unbekannt"

    gruppen = 0

    def tabelle_lesen(table: Table, heading: str) -> None:
        nonlocal gruppen
        gesehen = set()
        for row in table.rows:
            gruppen += 1
            gruppe = str(gruppen)
            for cell in row.cells:
                # Auch vertikal verbundene Zellen nur einmal; XML-Objekte festhalten.
                if cell._tc in gesehen:
                    continue
                gesehen.add(cell._tc)
                # Absätze und innere Tabellen in ihrer tatsächlichen Reihenfolge lesen.
                for child in cell._tc.iterchildren():
                    tag = child.tag.rsplit("}", 1)[-1]
                    if tag == "p":
                        text = Paragraph(child, cell).text.strip()
                        if text:
                            structured.append({"text": text, "heading": f"{heading} (Tabelle)", "gruppe": gruppe})
                    elif tag == "tbl":
                        tabelle_lesen(Table(child, cell), heading)

    try:
        for child in doc.element.body.iterchildren():
            tag = child.tag.rsplit("}", 1)[-1]
            if tag == "p":
                para = Paragraph(child, doc)
                text = para.text.strip()
                if not text:
                    continue
                style = getattr(para, "style", None)
                name = getattr(style, "name", "") if style is not None else ""
                if name.startswith("Heading"):
                    current_heading = text
                structured.append({"text": text, "heading": current_heading,
                                   "typ": "ueberschrift" if name.startswith("Heading") else "absatz",
                                   "kontext": current_heading if current_heading != "Unbekannt" else ""})
            elif tag == "tbl":
                tabelle_lesen(Table(child, doc), current_heading)
    except Exception as e:
        raise LeseFehler(f"Fehler beim Parsen der Word-Datei: {e}") from e
    if not structured:
        raise LeseFehler("Keine Textinhalte erkannt.")
    return structured


def _seitentexte_pypdf2(f: IO[bytes]) -> list[str]:
    reader = PdfReader(f)
    return [page.extract_text() or "" for page in reader.pages]


def _seitentexte_pdfplumber(f: IO[bytes]) -> list[str]:
    f.seek(0)
    with pdfplumber.open(f) as pdf:
        return [page.extract_text() or "" for page in pdf.pages]


def _pdf_layout(f: IO[bytes]) -> list[Struktur]:
    """Nur nahe, gleich formatierte Zeilen derselben Spalte verbinden."""
    f.seek(0)
    seiten = []
    with pdfplumber.open(f) as pdf:
        for nummer, page in enumerate(pdf.pages, 1):
            groessen = Counter(round(c["size"], 1) for c in page.chars)
            normal = groessen.most_common(1)[0][0] if groessen else 11
            segmente = []
            for line in page.extract_text_lines():
                gruppe = []
                for char in line["chars"]:
                    if gruppe and char["x0"] - gruppe[-1]["x1"] > normal * 2:
                        segmente.append(gruppe)
                        gruppe = []
                    gruppe.append(char)
                if gruppe:
                    segmente.append(gruppe)
            result: Struktur = []
            vorher = None
            kontext = ""
            for chars in segmente:
                text = pdfplumber.utils.extract_text(chars, x_tolerance=1).strip()
                if not text:
                    continue
                size = max(c["size"] for c in chars)
                bold = all("bold" in c["fontname"].lower() for c in chars if c["text"].strip())
                typ = "absatz"
                if re.search(r"\.{3,}\s*\d+\s*$", text):
                    typ = "verzeichnis"
                elif size > normal * 1.15 or (bold and len(text.split()) < 16):
                    typ = "ueberschrift"
                x = min(c["x0"] for c in chars)
                top = min(c["top"] for c in chars)
                bottom = max(c["bottom"] for c in chars)
                bullet = bool(re.match(r"(?:[-•▪●]|\d+[.)])\s", text))
                if typ == "ueberschrift":
                    kontext = text
                verbinden = (vorher and typ == "absatz" and result[-1].get("typ") == "absatz"
                             and not bullet and abs(x - vorher[0]) < 3
                             and abs(size - vorher[3]) < .5
                             and 0 <= top - vorher[2] <= size * .6
                             and (not re.search(r"[.!?]$", result[-1]["text"])
                                  or bool(re.search(r"\b(?:bzw|ca|nr|vgl|usw|etc|z\.\s*b)\.$",
                                                    result[-1]["text"], re.I))))
                if verbinden:
                    result[-1]["text"] += " " + text
                else:
                    result.append({"text": text, "heading": f"Seite {nummer}",
                                   "typ": typ, "kontext": kontext})
                vorher = (x, top, bottom, size)
            seiten.append(result)
    return seiten


def pdf_lesen_mit_hinweisen(daten: bytes | IO[bytes]) -> tuple[Struktur, list[Hinweis]]:
    """Text je Seite; Seiten ohne Textebene werden gesammelt und als Hinweis gemeldet."""
    f = _bytesio(daten)
    seiten: list[str] = []
    fehler: Exception | None = None
    if HAS_PYPDF2:
        try:
            seiten = _seitentexte_pypdf2(f)
        except Exception as e:
            fehler = e
    if HAS_PDFPLUMBER and (not seiten or not any(s.strip() for s in seiten)):
        try:
            seiten = _seitentexte_pdfplumber(f)
        except Exception as e:
            raise LeseFehler(f"Fehler beim Lesen der PDF: {e}") from e
    elif HAS_PDFPLUMBER and any(not s.strip() for s in seiten):
        # Gemischte PDFs: leere Seiten noch einmal mit dem zweiten Leser versuchen.
        try:
            ersatz = _seitentexte_pdfplumber(f)
            seiten = [s if s.strip() else (ersatz[i] if i < len(ersatz) else "") for i, s in enumerate(seiten)]
        except Exception:
            pass
    if not seiten and fehler is not None:
        raise LeseFehler(f"Fehler beim Lesen der PDF: {fehler}") from fehler
    layout = []
    if HAS_PDFPLUMBER:
        try:
            layout = _pdf_layout(f)
        except Exception:
            pass  # Der Textleser bleibt als Rückfall erhalten.
    structured: Struktur = []
    leer: list[int] = []
    for i, text in enumerate(seiten, start=1):
        zeilen = [z.strip() for z in text.splitlines() if z.strip()]
        if not zeilen:
            leer.append(i)
            continue
        if i <= len(layout) and layout[i - 1]:
            structured.extend(layout[i - 1])
        else:
            structured.extend({"text": z, "heading": f"Seite {i}"} for z in zeilen)
    if not structured:
        raise LeseFehler("Keine Textinhalte erkannt. Vermutlich ein Scan ohne Textebene.")
    hinweise: list[Hinweis] = []
    if leer:
        hinweise.append({"art": "scan_seiten", "seiten": leer, "gesamt": len(seiten)})
    return structured, hinweise


def pdf_lesen(daten: bytes | IO[bytes]) -> Struktur:
    return pdf_lesen_mit_hinweisen(daten)[0]


def lesen_mit_hinweisen(dateiname: str, daten: bytes | IO[bytes]) -> tuple[Struktur, list[Hinweis]]:
    """Struktur plus Lesehinweise (strukturiert, Text je Sprache über texte.lesehinweis)."""
    name = dateiname.lower()
    if name.endswith(".pdf"):
        return pdf_lesen_mit_hinweisen(daten)
    if name.endswith(".docx"):
        return docx_lesen(daten), []
    raise LeseFehler("Nur Word (.docx) und PDF (.pdf) werden geprüft.")


def lesen(dateiname: str, daten: bytes | IO[bytes]) -> Struktur:
    return lesen_mit_hinweisen(dateiname, daten)[0]
