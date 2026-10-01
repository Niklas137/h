"""Die Prüfung selbst: drei Regelsätze, Score, Ampel, Fazit, To-do-Liste.

Score, Ampel und Fazit folgen app.py. Die Satzlänge wird je Satz innerhalb eines eingelesenen
Textabschnitts geprüft. Die Regelsätze werden vor der Prüfung vollständig validiert.
Die Schlüsselwortsuche ist eine automatische Vorprüfung; die fachliche Freigabe bleibt bei FSH.
"""
from __future__ import annotations

import re
from typing import Any

from . import regeln as regelmodul
from . import texte

Fund = dict[str, Any]


def _saetze(text: str) -> list[str]:
    """Heuristische Satzgrenzen im Textabschnitt; kein sprachliches Vollmodell.

    Punkte in üblichen Abkürzungen und deutschen Ordinalzahlen bleiben im Satz.
    Dezimalzahlen, Versionen und URLs werden ohne folgendes Leerzeichen nicht getrennt.
    Eingelesene Abschnitte werden nicht verbunden, damit Überschriften, Listen und
    Tabellenzellen nicht versehentlich zu einem Satz zusammenlaufen.
    """
    geschuetzt: set[int] = set()
    muster = (
        r"\b(?:(?:[a-zäöü]\.\s*)+[a-zäöü]\.|"
        r"(?:abs|abb|art|bzw|ca|dr|prof|nr|kap|pos|tab|vgl)\.)(?=\s|$)"
    )
    for treffer in re.finditer(muster, text, flags=re.IGNORECASE):
        geschuetzt.update(i for i in range(treffer.start(), treffer.end()) if text[i] == ".")
    # Beispielsweise „am 3. Oktober“ oder „im 2. Schritt“.
    ordinal = (
        r"\b\d+\.(?=\s+(?:[a-zäöüß]|(?:Januar|Februar|März|April|Mai|Juni|Juli|"
        r"August|September|Oktober|November|Dezember|Schritt|Abschnitt|Kapitel|"
        r"Seite|Stufe|Teil|Quartal)\b))"
    )
    for treffer in re.finditer(ordinal, text):
        geschuetzt.add(treffer.end() - 1)

    saetze: list[str] = []
    start = 0
    for grenze in re.finditer(r"[.!?]+[\"'”’»«“\)\]]*(?:\s+|$)", text):
        if grenze.start() in geschuetzt:
            continue
        satz = text[start:grenze.end()].strip()
        if satz:
            saetze.append(satz)
        start = grenze.end()
    rest = text[start:].strip()
    if rest:
        saetze.append(rest)
    return saetze


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
        agg["Empfehlung"] = f"{len(txt_findings)} Sätze mit mehr als 25 Wörtern gefunden"
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


def check_document(structured_text: list[dict[str, str]], checklist: list[dict[str, Any]]) -> list[Fund]:
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

    for item in structured_text:
        for sentence in _saetze(item["text"]):
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


def pruefen(structured_text: list[dict[str, str]], regelsaetze: list[str] | None = None) -> dict[str, Any]:
    """Führt die gewählten Regelsätze aus und liefert das vollständige Ergebnis."""
    gewaehlt = set(["basis", "din", "ce"] if regelsaetze is None else regelsaetze)
    if not gewaehlt or not gewaehlt.issubset(regelmodul.DATEIEN):
        raise regelmodul.RegelFehler("Regelsatz-Auswahl ist leer oder ungültig.")
    # Erst alle ausgewählten Regeln prüfen. Kein Teilergebnis bei Regeldefekten.
    kataloge = {k: regelmodul.laden(k) for k in sorted(gewaehlt)}
    regel_ids = [r["id"] for rs in kataloge.values() for r in rs]
    if len(set(regel_ids)) != len(regel_ids):
        raise regelmodul.RegelFehler("Regelsatz-Auswahl enthält doppelte Regel-IDs. Prüfung abgebrochen.")
    volltext = _volltext(structured_text)
    regelpruefungen = [
        {"id": r["id"], "regelsatz": k, "fachlich": "offen",
         "suchstatus": "treffer" if keyword_found(volltext, r["keywords"]) else "nicht_gefunden"}
        for k, rs in kataloge.items() for r in rs
    ]
    findings: list[Fund] = []
    if "basis" in gewaehlt:
        findings.extend(check_document(structured_text, kataloge["basis"]))
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
        "regelnVorhanden": regelmodul.vorhanden(),
        "zeilen": len(structured_text),
    }
