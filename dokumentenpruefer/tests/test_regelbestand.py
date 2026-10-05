"""Übernahme des veröffentlichten Altbestands und technische Sollfälle je Regel.

Keine normativen Sollbefunde: Diese Fälle prüfen den vereinbarten Suchalgorithmus.
Die Referenz stammt aus dem öffentlichen Git-Commit in fixtures/originalregeln.json.
"""
import json
from pathlib import Path

import pytest

from app.pruefer import pruefung, regeln

REFERENZ = json.loads((Path(__file__).parent / 'fixtures/originalregeln.json').read_text())
FAELLE = [(satz, r) for satz, datei in regeln.DATEIEN.items()
          for r in REFERENZ['kataloge'][datei]]


@pytest.mark.parametrize('satz', regeln.DATEIEN)
def test_originalregelwerk_vollstaendig_uebernommen(satz):
    alt = REFERENZ['kataloge'][regeln.DATEIEN[satz]]
    neu = {r['id']: r for r in regeln.laden(satz)}
    assert set(neu) == {r['id'] for r in alt}
    for regel in alt:
        assert {k: neu[regel['id']][k] for k in regel} == regel


@pytest.mark.parametrize('satz,regel', FAELLE, ids=[r['id'] for _, r in FAELLE])
@pytest.mark.parametrize('vorhanden', [True, False])
def test_jede_regel_hat_einen_positiven_und_negativen_sollfall(satz, regel, vorhanden):
    text = regel['keywords'][0] + (': Angaben sind enthalten.' if vorhanden else ' ist nicht dokumentiert.')
    erg = pruefung.pruefen([{'text': text, 'heading': 'Probe'}], [satz])
    gefunden = next(r for r in erg['regelpruefungen'] if r['id'] == regel['id'])
    assert (gefunden['suchstatus'] == 'treffer') is vorhanden
    assert any(f['ID'] == regel['id'] for f in erg['funde']) is not vorhanden
    assert erg['freigabe'] is False


@pytest.mark.parametrize('satz,regel', FAELLE, ids=[r['id'] for _, r in FAELLE])
def test_ueberschrift_darf_negierten_absatz_nicht_aufwerten(satz, regel):
    titel = regel['keywords'][0]
    erg = pruefung.pruefen([
        {'text': titel, 'heading': titel, 'typ': 'ueberschrift'},
        {'text': titel + ' ist nicht dokumentiert.', 'heading': titel, 'kontext': titel},
    ], [satz])
    assert any(f['ID'] == regel['id'] for f in erg['funde'])
