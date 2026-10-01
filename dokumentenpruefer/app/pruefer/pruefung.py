"""Die Prüfung selbst: drei Regelsätze, Score, Ampel, Fazit, To-do-Liste.

Die Rechenlogik ist 1:1 aus app.py übernommen, damit alte und neue Ergebnisse
vergleichbar bleiben. Verbesserungen an der Prüfung kommen später als eigener Schritt.
"""
from __future__ import annotations

import re
from typing import Any

from . import regeln as regelmodul

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


def get_ampel(score: int) -> str:
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
    """Wortlaut wie in app.py, auf Deutsch, mit Einzahl bei genau einem Fund."""
    kritisch = [f for f in findings if f.get("Fehlerklasse") == "Kritisch"]
    schwer = [f for f in findings if f.get("Fehlerklasse") == "Schwer"]
    ce_fehler = [f for f in findings if f.get("Normlogik") == "CE / EU-Konformität"]
    text: list[str] = []
    if score < 60:
        text.append("Das Dokument ist in der vorliegenden Form fachlich nicht abgabereif.")
    elif score < 80:
        text.append("Das Dokument weist relevante Mängel auf und ist überarbeitungsbedürftig.")
    else:
        text.append("Das Dokument ist grundsätzlich verwendbar, weist jedoch Optimierungspotenzial auf.")
    if kritisch:
        text.append("Es wurde 1 kritische Abweichung festgestellt." if len(kritisch) == 1 else f"Es wurden {len(kritisch)} kritische Abweichungen festgestellt.")
    if schwer:
        text.append("Zusätzlich wurde 1 schwerwiegendes Defizit identifiziert." if len(schwer) == 1 else f"Zusätzlich wurden {len(schwer)} schwerwiegende Defizite identifiziert.")
    if ce_fehler:
        text.append("Im Bereich CE wurde 1 Nachweislücke festgestellt." if len(ce_fehler) == 1 else f"Im Bereich CE wurden {len(ce_fehler)} Nachweislücken festgestellt.")
    return " ".join(text)


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
    gewaehlt = set(regelsaetze or ["basis", "din", "ce"])
    findings: list[Fund] = []
    if "basis" in gewaehlt:
        findings.extend(check_document(structured_text, regelmodul.laden("basis")))
    if "din" in gewaehlt:
        findings.extend(check_normlogik_82079(structured_text, regelmodul.laden("din")))
    if "ce" in gewaehlt:
        findings.extend(check_ce_logik(structured_text, regelmodul.laden("ce")))
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
        "ampel": get_ampel(score),
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
