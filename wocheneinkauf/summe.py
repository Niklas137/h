#!/usr/bin/env python3
"""Summen- und Regelprüfung für eine Wochen-Datei des Wocheneinkaufs.

Aufruf:
    python3 wocheneinkauf/summe.py wocheneinkauf/wochen/2026-09-26-woche-02.md

Liest alle Artikelzeilen der Form
    - [ ] Artikel Menge – 1,99 €          (optional danach z. B. "(Mo)")
unterhalb von "### Kategorie"-Überschriften, summiert pro Kategorie und gesamt,
schätzt den Rewe-Preis (+10 %), vergleicht mit der in der Datei genannten
Gesamtsumme und warnt bei Zutaten, die gegen die Ernährungsregeln verstoßen.
Steht in der Kopfzeile "Budget: 26 €" und "Tage zu Hause: 3" (Geschäftsreise),
gelten das anteilige Budget und die Tage zu Hause für die Fleischmenge.
Nur Standardbibliothek. Exit-Code 1 bei Verstoß oder Budgetüberschreitung.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

BUDGET = 60.00
ZIEL_MIN = 55.00
WARN_MIN = 50.00
REWE_AUFSCHLAG = 0.10
FLEISCH_ZIEL = (100, 150)  # g pro Person und Tag

ARTIKEL = re.compile(
    r"^\s*-\s*\[[ xX]\]\s*(?P<artikel>.+?)\s*[–—-]\s*(?P<preis>\d{1,3},\d{2})\s*€(?P<rest>.*)$"
)
KATEGORIE = re.compile(r"^###\s+(?P<name>.+?)\s*$")
GEWICHT = re.compile(
    r"(?:(?P<anzahl>\d+)\s*[x×]\s*)?(?P<zahl>\d+(?:,\d+)?)\s*(?P<einheit>kg|g)\b"
)
GESAMT = re.compile(r"Gesamt.*?(?P<preis>\d{1,3},\d{2})\s*€")
# Kopfzeile der Wochen-Datei: "Budget: 26 €" und "Tage zu Hause: 3" (Geschäftsreise-Modus).
KOPF_BUDGET = re.compile(r"Budget:\s*(?P<wert>\d{1,3}(?:,\d{2})?)\s*€")
KOPF_TAGE = re.compile(r"Tage zu Hause:\s*(?P<tage>\d{1,2})\b")

# Darf in der ganzen Datei nicht vorkommen (Liste und Rezepte).
# Teilstring-Suche in der ganzen Datei, damit auch Zusammensetzungen wie "Hähnchenleber"
# oder "Bismarckhering" erkannt werden. "niere" braucht einen Sonderfall, weil sonst
# "marinieren", "panieren" oder "garnieren" als Innereien gelten würden.
VERBOTEN = {
    "Pilze": ("pilz", "champignon", "pfifferling", "shiitake", "kräuterseitling"),
    "Innereien": ("leber", "niere", "innereien", "kutteln", "bries", "zunge"),
    "Gorgonzola": ("gorgonzola",),
    "purinreicher Fisch": ("sardine", "sardelle", "anchovis", "hering", "matjes", "sprotte"),
}
NIERE = re.compile(
    r"\bniere"                                  # Niere, Nieren, Nierenragout
    r"|niere(?!n\b)"                            # Schweineniere, nicht marinieren
    r"|(kalbs|schweine|rinder|lamm|hühner|geflügel|hähnchen|puten)nieren?\b"
)


def verboten_enthalten(wort: str, text_lc: str) -> bool:
    if wort == "niere":
        return NIERE.search(text_lc) is not None
    return wort in text_lc


# Nur Hinweise, geprüft auf Artikelzeilen (wenig Wurst, Vollkorn, wenig Zucker).
HINWEIS = {
    "Wurst (wenig)": ("salami", "schinken", "speck", "wurst", "wiener"),
    "Weißmehl": ("weißbrot", "toastbrot", "baguette", "brötchen", "semmel", "ciabatta", "weizenmehl"),
    "Zucker": ("zucker", "marmelade", "honig", "schokolade", "limonade", "cola", "saft", "nutella", "kekse"),
}


def euro(wert: float) -> str:
    return f"{wert:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def gramm(artikel: str) -> float | None:
    """Erstes Gewicht im Artikeltext in Gramm, sonst None."""
    m = GEWICHT.search(artikel)
    if not m:
        return None
    zahl = float(m.group("zahl").replace(",", "."))
    if m.group("einheit") == "kg":
        zahl *= 1000
    if m.group("anzahl"):
        zahl *= int(m.group("anzahl"))
    return zahl


def main(pfad: str) -> int:
    text = Path(pfad).read_text(encoding="utf-8")
    zeilen = text.splitlines()

    # Budget und Tage aus der Kopfzeile; Standard 60 € und 7 Tage. Bei einem anteiligen
    # Budget (Geschäftsreise) werden Ziel- und Warnschwelle im selben Verhältnis verkleinert.
    budget = BUDGET
    m = KOPF_BUDGET.search(text)
    if m:
        budget = float(m.group("wert").replace(",", "."))
    faktor = budget / BUDGET
    ziel_min = round(ZIEL_MIN * faktor, 2)
    warn_min = round(WARN_MIN * faktor, 2)
    tage = 7
    m = KOPF_TAGE.search(text)
    if m:
        tage = int(m.group("tage"))

    kategorien: dict[str, list[tuple[str, float, str]]] = {}
    aktuell = "(ohne Kategorie)"
    for zeile in zeilen:
        k = KATEGORIE.match(zeile)
        if k:
            aktuell = k.group("name")
            continue
        a = ARTIKEL.match(zeile)
        if a:
            preis = float(a.group("preis").replace(",", "."))
            kategorien.setdefault(aktuell, []).append((a.group("artikel"), preis, a.group("rest")))

    probleme: list[str] = []
    hinweise: list[str] = []

    if not kategorien:
        print(f"Keine Artikelzeilen in {pfad} gefunden (Format: '- [ ] Artikel Menge – 1,99 €').")
        return 1

    gesamt = 0.0
    fleisch_g = 0.0
    montag: list[tuple[str, float]] = []
    breite = max(len(k) for k in kategorien) + 2

    print(f"Datei: {pfad}\n")
    print(f"{'Kategorie':<{breite}}{'Artikel':>8}{'Summe':>12}")
    for name, artikel in kategorien.items():
        summe = sum(p for _, p, _ in artikel)
        gesamt += summe
        print(f"{name:<{breite}}{len(artikel):>8}{euro(summe):>12}")
        for bezeichnung, preis, rest in artikel:
            if "(mo" in rest.lower():
                montag.append((bezeichnung, preis))
            if "fleisch" in name.lower() or "fisch" in name.lower():
                g = gramm(bezeichnung)
                if g is None:
                    hinweise.append(f"Kein Gewicht erkannt: {bezeichnung}")
                else:
                    fleisch_g += g
            zeile_lc = bezeichnung.lower()
            for gruppe, woerter in HINWEIS.items():
                if gruppe == "Weißmehl" and "vollkorn" in zeile_lc:
                    continue
                if any(w in zeile_lc for w in woerter):
                    hinweise.append(f"{gruppe}: {bezeichnung}")

    print(f"{'Gesamt (Penny)':<{breite}}{sum(len(a) for a in kategorien.values()):>8}{euro(gesamt):>12}")
    print(f"{'Rewe-Schätzung (+10 %)':<{breite}}{'':>8}{euro(gesamt * (1 + REWE_AUFSCHLAG)):>12}")
    budget_text = "Budget" if budget == BUDGET else f"Budget (anteilig, {tage} Tage zu Hause)"
    print(f"{budget_text:<{breite}}{'':>8}{euro(budget):>12}")
    print(f"{'Puffer':<{breite}}{'':>8}{euro(budget - gesamt):>12}")

    if montag:
        print(f"\nMontags-Tour: {len(montag)} Artikel, {euro(sum(p for _, p in montag))}")
    if fleisch_g:
        pro_tag_2 = fleisch_g / (2 * tage)
        print(
            f"Fleisch & Fisch: {fleisch_g:.0f} g auf {tage} Tage → 2 Personen {pro_tag_2:.0f} g/Tag, "
            f"1 Person {fleisch_g / tage:.0f} g/Tag (Ziel {FLEISCH_ZIEL[0]}–{FLEISCH_ZIEL[1]} g)"
        )
        if pro_tag_2 < FLEISCH_ZIEL[0] * 0.8:
            hinweise.append("Fleisch/Fisch für 2 Personen unter 80 g/Tag")
        if pro_tag_2 > FLEISCH_ZIEL[1]:
            hinweise.append("Fleisch/Fisch für 2 Personen über 150 g/Tag")

    # Gesamtsumme in der Datei mit der Rechnung vergleichen.
    g = GESAMT.search(text)
    if g:
        genannt = float(g.group("preis").replace(",", "."))
        if abs(genannt - gesamt) > 0.005:
            probleme.append(f"Gesamtsumme in der Datei ({euro(genannt)}) ≠ berechnet ({euro(gesamt)})")
    else:
        hinweise.append("Keine Gesamtsumme ('Gesamt … €') in der Datei gefunden")

    if gesamt > budget:
        probleme.append(f"Über Budget: {euro(gesamt)} > {euro(budget)}")
    elif gesamt < warn_min:
        probleme.append(f"Deutlich unter Ziel: {euro(gesamt)} < {euro(warn_min)}")
    elif gesamt < ziel_min:
        hinweise.append(f"Unter Zielbereich: {euro(gesamt)} < {euro(ziel_min)} (Vorrat auffüllen?)")

    text_lc = text.lower()
    for gruppe, woerter in VERBOTEN.items():
        treffer = sorted({w for w in woerter if verboten_enthalten(w, text_lc)})
        if treffer:
            probleme.append(f"Verbotene Zutat ({gruppe}): {', '.join(treffer)}")

    print()
    if probleme:
        print("PROBLEME:")
        for p in probleme:
            print(f"  ✗ {p}")
    if hinweise:
        print("Hinweise:")
        for h in hinweise:
            print(f"  · {h}")
    if not probleme and not hinweise:
        print("Keine Warnungen.")
    return 1 if probleme else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
