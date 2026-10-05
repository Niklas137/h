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


def test_cli_mehrere_dateien(tmp_path, capsys):
    """Mehrere Dateien in einem Aufruf: jede bekommt Berichte, eine kaputte ändert nur den Exit-Code."""
    a, b, kaputt = tmp_path / "A.docx", tmp_path / "B.docx", tmp_path / "Kaputt.docx"
    _docx(a)
    _docx(b)
    kaputt.write_bytes(b"kein zip")
    ziel = tmp_path / "out"
    rc = cli.main(["pruefen", str(a), str(b), str(kaputt), "--regelsaetze", "din", "--ausgabe", str(ziel), "--json"])
    assert rc == 3
    out, err = capsys.readouterr()
    liste = json.loads(out)
    assert [d["datei"] for d in liste] == ["A.docx", "B.docx"]
    assert "Kaputt.docx" in err
    assert len(list(ziel.glob("*.pdf"))) == 4
    rc = cli.main(["pruefen", str(a), str(b), "--regelsaetze", "din", "--ausgabe", str(ziel)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "2 von 2 Dokumenten geprüft." in out and out.count("Fazit:") == 2


def test_cli_ohne_pruefpunkte(tmp_path, capsys):
    datei = tmp_path / "Ohne.docx"
    _docx(datei)
    rc = cli.main(["pruefen", str(datei), "--regelsaetze", "din", "--ohne", "DIN-008,DIN-004", "--ausgabe", str(tmp_path / "o"), "--json"])
    assert rc == 0
    d = json.loads(capsys.readouterr().out)
    assert d["ausgelassen"] == ["DIN-004", "DIN-008"]
    assert cli.main(["pruefen", str(datei), "--regelsaetze", "din", "--ohne", "CHK-001"]) == 2
    assert "--ohne" in capsys.readouterr().err
