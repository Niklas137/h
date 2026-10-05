"""Die Prüfung selbst: drei Regelsätze, Score, Ampel, Fazit, To-do-Liste.

Die Rechenlogik (Score, Ampel, Fazit) ist 1:1 aus app.py übernommen, damit alte und neue
Ergebnisse vergleichbar bleiben. Die Regelsätze werden vor der Prüfung vollständig validiert.
Die Schlüsselwortsuche ist eine automatische Vorprüfung; die fachliche Freigabe bleibt bei FSH.
"""
from __future__ import annotations

import re
from typing import Any

from . import regeln as regelmodul
from . import texte

Fund = dict[str, Any]


def keyword_found(full_text: str, keywords: list[str]) -> bool:
    for keyword in keywords:
        pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
        if re.search(pattern, full_text):
            return True
    return False


def deduplicate_findings(findings: list[Fund]) -> list[Fund]:
    txt_findings = [f for f in findings if f.get("ID") == "TXT-001"]
    other_findings = [f for f in findings if f.get("ID") != "TXT-001"]

    seen: set[tuple[Any, Any]] = set()
    deduped: list[Fund] = []
    for f in other_findings:
        key = (f.get("ID"), f.get("Fundstelle", ""))
        if key not in seen:
            seen.add(key)
            deduped.append(f)

    if txt_findings:
        agg = txt_findings[0].copy()
        agg["Bewertung"] = f"Sätze zu lang ({len(txt_findings)} gefunden)"
        agg["Empfehlung"] = texte.empfehlung("de", {"Schluessel": "satz_zu_lang", "Anzahl": len(txt_findings)})
        agg["Anzahl"] = len(txt_findings)
        agg["Schluessel"] = "satz_zu_lang"
        deduped.append(agg)

    return deduped


def _volltext(structured_text: list[dict[str, str]]) -> str:
    return " ".join(item["text"] for item in structured_text).lower()


def _regel_felder(rule: dict[str, Any]) -> dict[str, Any]:
    """Übersetzungen aus der Regel mitnehmen, damit die Berichte sie nutzen können."""
    felder: dict[str, Any] = {}
    for k, v in rule.items():
        if k.startswith("empfehlung_") or k.startswith("bereich_"):
            felder[k] = v
    return felder


# Eingebauter Prüfpunkt der Basisprüfung: Satzlänge. Steht nicht in der Regeldatei, ist aber abwählbar.
SATZ_PUNKT = {"id": "TXT-001", "bereich": "Lesbarkeit", "fehlerklasse": "Mittel", "gewichtung": 2,
              "empfehlung": "Sätze mit mehr als 25 Wörtern vermeiden", "eingebaut": True,
              "bereich_en": "Readability", "bereich_uk": "Читабельність", "bereich_ru": "Читаемость",
              "empfehlung_en": "Avoid sentences with more than 25 words",
              "empfehlung_uk": "Уникайте речень довших за 25 слів",
              "empfehlung_ru": "Избегайте предложений длиннее 25 слов"}


def punkte(regelsatz: str) -> list[dict[str, Any]]:
    """Die wählbaren Prüfpunkte eines Regelsatzes (nur die Felder, die die Oberfläche braucht)."""
    liste = [
        {k: v for k, v in r.items() if k in ("id", "bereich", "fehlerklasse", "gewichtung", "empfehlung", "pflicht") or k.startswith(("bereich_", "empfehlung_"))}
        for r in regelmodul.laden(regelsatz)
    ]
    if regelsatz == "basis":
        liste.append(dict(SATZ_PUNKT))
    return liste


def check_document(structured_text: list[dict[str, str]], checklist: list[dict[str, Any]], satzlaenge: bool = True) -> list[Fund]:
    findings: list[Fund] = []
    full_text = _volltext(structured_text)

    for rule in checklist:
        if not keyword_found(full_text, rule.get("keywords", [])):
            findings.append(
                {
                    "ID": rule.get("id"),
                    "Normlogik": "Basisprüfung",
                    "Bereich": rule.get("bereich"),
                    "Pflicht": "-",
                    "Fehlerklasse": rule.get("fehlerklasse"),
                    "Bewertung": "Nicht gefunden",
                    "Fundstelle": "Nicht vorhanden",
                    "Empfehlung": rule.get("empfehlung"),
                    "Gewichtung": rule.get("gewichtung", 1),
                    "Zeitaufwand_min": rule.get("gewichtung", 1) * 12,
                    **_regel_felder(rule),
                }
            )

    for item in structured_text if satzlaenge else []:
        sentence = item["text"]
        if len(sentence.split()) > 25:
            findings.append(
                {
                    "ID": "TXT-001",
                    "Normlogik": "Basisprüfung",
                    "Bereich": "Lesbarkeit",
                    "Pflicht": "-",
                    "Fehlerklasse": "Mittel",
                    "Bewertung": "Satz zu lang",
                    "Fundstelle": item.get("heading", ""),
                    "Empfehlung": sentence[:150],
                    "Gewichtung": 2,
                    "Zeitaufwand_min": 15,
                }
            )
    return findings


def check_normlogik_82079(structured_text: list[dict[str, str]], rules: list[dict[str, Any]]) -> list[Fund]:
    findings: list[Fund] = []
    full_text = _volltext(structured_text)
    for rule in rules:
        if not keyword_found(full_text, rule.get("keywords", [])):
            findings.append(
                {
                    "ID": rule.get("id"),
                    "Normlogik": "DIN 82079-1",
                    "Bereich": rule.get("bereich"),
                    "Pflicht": "Ja" if rule.get("pflicht") else "Produktabhängig",
                    "Fehlerklasse": rule.get("fehlerklasse"),
                    "Bewertung": "Nicht ausreichend nachweisbar",
                    "Fundstelle": "Nicht gefunden",
                    "Empfehlung": rule.get("empfehlung"),
                    "Gewichtung": rule.get("gewichtung", 1),
                    "Zeitaufwand_min": rule.get("gewichtung", 1) * 15,
                    **_regel_felder(rule),
                }
            )
    return findings


def check_ce_logik(structured_text: list[dict[str, str]], rules: list[dict[str, Any]]) -> list[Fund]:
    findings: list[Fund] = []
    full_text = _volltext(structured_text)
    for rule in rules:
        if not keyword_found(full_text, rule.get("keywords", [])):
            findings.append(
                {
                    "ID": rule.get("id"),
                    "Normlogik": "CE / EU-Konformität",
                    "Bereich": rule.get("bereich"),
                    "Pflicht": "Ja",
                    "Fehlerklasse": rule.get("fehlerklasse"),
                    "Bewertung": "Nicht ausreichend nachweisbar",
                    "Fundstelle": "Nicht gefunden",
                    "Empfehlung": rule.get("empfehlung"),
                    "Gewichtung": rule.get("gewichtung", 1),
                    "Zeitaufwand_min": rule.get("gewichtung", 1) * 18,
                    "Priorität": "Hoch" if rule.get("fehlerklasse") == "Kritisch" else "Mittel",
                    **_regel_felder(rule),
                }
            )
    return findings


def get_ampel(score: int, findings: list[Fund] | None = None) -> str:
    """Ampel nach Score, wie in app.py: Grün ab 80, Gelb ab 60, sonst Rot."""
    if score >= 80:
        return "gruen"
    if score >= 60:
        return "gelb"
    return "rot"


def fazit_teile(findings: list[Fund], score: int) -> list[tuple[str, dict[str, int]]]:
    """Das Fazit als Bausteine, damit die Berichte es in jeder Sprache setzen können."""
    kritisch = [f for f in findings if f.get("Fehlerklasse") == "Kritisch"]
    schwer = [f for f in findings if f.get("Fehlerklasse") == "Schwer"]
    ce_fehler = [f for f in findings if f.get("Normlogik") == "CE / EU-Konformität"]
    teile: list[tuple[str, dict[str, int]]] = []
    if score < 60:
        teile.append(("fazit_rot", {}))
    elif score < 80:
        teile.append(("fazit_gelb", {}))
    else:
        teile.append(("fazit_gruen", {}))
    if kritisch:
        teile.append(("kritisch_1" if len(kritisch) == 1 else "kritisch_n", {"n": len(kritisch)}))
    if schwer:
        teile.append(("schwer_1" if len(schwer) == 1 else "schwer_n", {"n": len(schwer)}))
    if ce_fehler:
        teile.append(("ce_1" if len(ce_fehler) == 1 else "ce_n", {"n": len(ce_fehler)}))
    return teile


def generate_fazit(findings: list[Fund], score: int) -> str:
    """API, Oberfläche und PDF verwenden dieselben vorsichtigen Aussagen."""
    return texte.fazit("de", fazit_teile(findings, score))


def generate_todo_list(findings: list[Fund]) -> list[dict[str, Any]]:
    todos: list[dict[str, Any]] = []
    for f in findings:
        if f.get("Normlogik") == "CE / EU-Konformität":
            todos.append(
                {
                    "Bereich": f.get("Bereich"),
                    "Maßnahme": f.get("Empfehlung"),
                    "Priorität": f.get("Priorität", "Mittel"),
                    "Aufwand (h)": round(f.get("Zeitaufwand_min", 0) / 60, 1),
                    "ID": f.get("ID"),
                }
            )
    return sorted(todos, key=lambda x: x["Priorität"] == "Mittel")


class AuswahlFehler(ValueError):
    """Die Auswahl der Prüfpunkte passt nicht zu den gewählten Regelsätzen."""

    def __init__(self, meldung: str, schluessel: str, **werte: object) -> None:
        super().__init__(meldung)
        self.schluessel = schluessel
        self.werte = werte


def pruefen(structured_text: list[dict[str, str]], regelsaetze: list[str] | None = None, ausgelassen: list[str] | None = None) -> dict[str, Any]:
    """Führt die gewählten Regelsätze aus und liefert das vollständige Ergebnis.

    ausgelassen: IDs einzelner Prüfpunkte, die bewusst nicht geprüft werden. Sie stehen im Ergebnis
    unter „ausgelassen“ und zählen nicht in den Score. Ein Regelsatz ohne aktiven Punkt ist ein Fehler.
    """
    gewaehlt = set(["basis", "din", "ce"] if regelsaetze is None else regelsaetze)
    if not gewaehlt or not gewaehlt.issubset(regelmodul.DATEIEN):
        raise regelmodul.RegelFehler("Regelsatz-Auswahl ist leer oder ungültig.")
    # Erst alle ausgewählten Regeln prüfen. Kein Teilergebnis bei Regeldefekten.
    kataloge = {k: regelmodul.laden(k) for k in sorted(gewaehlt)}
    regel_ids = [r["id"] for rs in kataloge.values() for r in rs]
    if len(set(regel_ids)) != len(regel_ids):
        raise regelmodul.RegelFehler("Regelsatz-Auswahl enthält doppelte Regel-IDs. Prüfung abgebrochen.")

    ohne = set(ausgelassen or [])
    alle_punkte = {k: [dict(r) for r in rs] + ([dict(SATZ_PUNKT)] if k == "basis" else []) for k, rs in kataloge.items()}
    bekannt = {p["id"] for ps in alle_punkte.values() for p in ps}
    unbekannt = sorted(ohne - bekannt)
    if unbekannt:
        raise AuswahlFehler(f"Unbekannter Prüfpunkt für die gewählten Regelsätze: {', '.join(unbekannt)}.", "punkt_unbekannt_satz", ids=", ".join(unbekannt))
    for k, ps in alle_punkte.items():
        if all(p["id"] in ohne for p in ps):
            raise AuswahlFehler(f"Regelsatz {k} hat keinen aktiven Prüfpunkt. Regelsatz abwählen oder Punkte einschalten.", "satz_leer", satz=k)
    kataloge = {k: [r for r in rs if r["id"] not in ohne] for k, rs in kataloge.items()}
    ausgelassen_liste = [
        {"id": p["id"], "regelsatz": k, "bereich": p.get("bereich", ""), **_regel_felder(p)}
        for k, ps in alle_punkte.items() for p in ps if p["id"] in ohne
    ]
    punkte_gesamt = sum(len(ps) for ps in alle_punkte.values())
    volltext = _volltext(structured_text)
    regelpruefungen = [
        {"id": r["id"], "regelsatz": k, "fachlich": "offen",
         "suchstatus": "treffer" if keyword_found(volltext, r["keywords"]) else "nicht_gefunden"}
        for k, rs in kataloge.items() for r in rs
    ]
    findings: list[Fund] = []
    if "basis" in gewaehlt:
        findings.extend(check_document(structured_text, kataloge["basis"], satzlaenge="TXT-001" not in ohne))
    if "din" in gewaehlt:
        findings.extend(check_normlogik_82079(structured_text, kataloge["din"]))
    if "ce" in gewaehlt:
        findings.extend(check_ce_logik(structured_text, kataloge["ce"]))
    findings = deduplicate_findings(findings)

    deduction = sum(f.get("Gewichtung", 0) for f in findings)
    score = max(0, round(100 - deduction))
    total_minutes = sum(f.get("Zeitaufwand_min", 0) for f in findings)
    total_hours = round(total_minutes / 60, 1)
    klassen = {"Kritisch": 0, "Schwer": 0, "Mittel": 0, "Gering": 0}
    for f in findings:
        k = f.get("Fehlerklasse")
        if k in klassen:
            klassen[k] += 1

    return {
        "funde": findings,
        "score": score,
        "ampel": get_ampel(score, findings),
        "pruefstatus": "fachlich_offen",
        "freigabe": False,
        "bewertungsart": "schluesselwortsuche",
        "regelpruefungen": regelpruefungen,
        "suchtrefferAnzahl": sum(r["suchstatus"] == "treffer" for r in regelpruefungen),
        "stunden": total_hours,
        "minuten": total_minutes,
        "fazit": generate_fazit(findings, score),
        "fazitTeile": fazit_teile(findings, score),
        "todos": generate_todo_list(findings),
        "klassen": klassen,
        "regelsaetze": sorted(gewaehlt, key=["basis", "din", "ce"].index),
        "ausgelassen": ausgelassen_liste,
        "punkteGesamt": punkte_gesamt,
        "punkteGeprueft": punkte_gesamt - len(ausgelassen_liste),
        "regelnVorhanden": regelmodul.vorhanden(),
        "zeilen": len(structured_text),
    }
