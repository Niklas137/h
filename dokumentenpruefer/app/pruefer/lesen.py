"""Word- und PDF-Dateien in Textzeilen mit Überschrift oder Seitenangabe zerlegen.

Unverändert übernommen aus app.py (read_docx, read_pdf), nur ohne Streamlit.
"""
from __future__ import annotations

from io import BytesIO
from typing import IO

from docx import Document

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
    try:
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            style = getattr(para, "style", None)
            name = getattr(style, "name", "") if style is not None else ""
            if name.startswith("Heading"):
                current_heading = text
            structured.append({"text": text, "heading": current_heading})
    except Exception as e:
        raise LeseFehler(f"Fehler beim Parsen der Word-Datei: {e}") from e
    if not structured:
        raise LeseFehler("Keine Textinhalte erkannt.")
    return structured


def pdf_lesen(daten: bytes | IO[bytes]) -> Struktur:
    f = _bytesio(daten)
    if HAS_PYPDF2:
        try:
            reader = PdfReader(f)
            structured: Struktur = []
            for i, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                if not text:
                    continue
                for line in text.splitlines():
                    line = line.strip()
                    if line:
                        structured.append({"text": line, "heading": f"Seite {i}"})
            if structured:
                return structured
        except Exception:
            pass
    if HAS_PDFPLUMBER:
        try:
            f.seek(0)
            with pdfplumber.open(f) as pdf:
                structured = []
                for i, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    if not text:
                        continue
                    for line in text.split("\n"):
                        line = line.strip()
                        if line:
                            structured.append({"text": line, "heading": f"Seite {i}"})
                if structured:
                    return structured
        except Exception as e:
            raise LeseFehler(f"Fehler beim Lesen der PDF: {e}") from e
    raise LeseFehler("Keine Textinhalte erkannt. Vermutlich ein Scan ohne Textebene.")


def lesen(dateiname: str, daten: bytes | IO[bytes]) -> Struktur:
    name = dateiname.lower()
    if name.endswith(".pdf"):
        return pdf_lesen(daten)
    if name.endswith(".docx"):
        return docx_lesen(daten)
    raise LeseFehler("Nur Word (.docx) und PDF (.pdf) werden geprüft.")
