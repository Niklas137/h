"""Kommandozeile: Dokument prüfen und PDFs ablegen."""
import io
import json

from docx import Document

from app import cli


def _docx(pfad):
    doc = Document()
    doc.add_paragraph("Diese Anleitung richtet sich an die Zielgruppe der Benutzer.")
    puffer = io.BytesIO()
    doc.save(puffer)
    pfad.write_bytes(puffer.getvalue())


def test_cli_pruefen(tmp_path, capsys):
    datei = tmp_path / "Anleitung.docx"
    _docx(datei)
    ziel = tmp_path / "out"
    rc = cli.main(["pruefen", str(datei), "--sprachen", "de,uk", "--regelsaetze", "din", "--ausgabe", str(ziel), "--json"])
    assert rc == 0
    d = json.loads(capsys.readouterr().out)
    assert d["sprachen"] == ["de", "uk"] and d["funde"] >= 1 and d["ampel"] in ("gruen", "gelb", "rot")
    pdfs = sorted(p.name for p in ziel.glob("*.pdf"))
    assert len(pdfs) == 4
    assert any(n.endswith("_Pruefbericht_UK_v01.pdf") for n in pdfs)
    assert all(p.read_bytes()[:5] == b"%PDF-" for p in ziel.glob("*.pdf"))


def test_cli_fehler(tmp_path, capsys):
    assert cli.main(["pruefen", str(tmp_path / "fehlt.docx")]) == 2
    datei = tmp_path / "x.docx"
    _docx(datei)
    assert cli.main(["pruefen", str(datei), "--sprachen", "de,en,uk"]) == 2
    assert cli.main(["pruefen", str(datei), "--regelsaetze", "nix"]) == 2
    kaputt = tmp_path / "kaputt.docx"
    kaputt.write_bytes(b"kein zip")
    assert cli.main(["pruefen", str(kaputt), "--ausgabe", str(tmp_path)]) == 3
