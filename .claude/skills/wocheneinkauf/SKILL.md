---
name: wocheneinkauf
description: Wöchentliche Einkaufsliste für Niklas (Penny/Rewe Teltow, 60 € Budget) mit 2–3 Gerichten und einem Frühstück. Verwenden, wenn der Nutzer „Wocheneinkauf" schreibt, eine Einkaufsliste oder einen Wochenplan will, einen Kassenbon abgleichen möchte oder eine Geschäftsreise/Dienstreise ankündigt.
argument-hint: "[optional: Geschäftsreise Di–Do | Kassenbon: 57,80 € | neu]"
allowed-tools: Read, Glob, Grep, Write, Edit, Bash(date:*), Bash(python3 wocheneinkauf/summe.py:*), Bash(git add:*), Bash(git commit:*), Bash(git push:*)
---

# Wocheneinkauf für Niklas

Du erstellst die Einkaufsliste für die kommende Woche plus 2–3 Gerichte und ein Frühstück.
Alle Parameter stehen fest. Nicht nachfragen – die einzige Ausnahme ist der Geschäftsreise-Modus.

## Dateien (vor jeder Liste lesen)

| Datei | Inhalt |
|---|---|
| `wocheneinkauf/README.md` | feste Parameter, Ernährungsregeln, Feiertage, Referenzwoche |
| `wocheneinkauf/preise.md` | Richtpreise Penny / Rewe „ja!" – Quelle für alle Preise |
| `wocheneinkauf/gerichte.md` | Gerichte- und Frühstückspool mit Spalte „Zuletzt" |
| `wocheneinkauf/verlauf.md` | bisherige Wochen, Proteine, geschätzter Vorrat |
| `wocheneinkauf/wochen/` | eine Datei pro Woche (`JJJJ-MM-TT-woche-NN.md`) |
| `wocheneinkauf/summe.py` | Summen- und Regelprüfung für eine Wochen-Datei |

## Ablauf

1. **Datum bestimmen:** `TZ=Europe/Berlin date "+%F %A"`. Einkaufstag = nächster Samstag
   (ist heute Samstag, dann heute). Fällt der Samstag auf einen Feiertag (Tabelle im README),
   wird der Freitag davor zum Einkaufstag. Sonntag nie – Penny ist geschlossen.
2. **Wochennummer:** letzte Nummer in `verlauf.md` + 1. Existiert schon eine Datei für den
   Einkaufstag: den vorhandenen Plan unverändert ausgeben (wie Schritt 9) und darauf hinweisen,
   dass „Wocheneinkauf neu" ihn neu erstellt. Nicht nachfragen, der Lauf ist meist unbeaufsichtigt.
   Das gilt auch, wenn die Datei keine Preise hat (Referenzwoche 1) oder `summe.py` sie nicht
   prüfen kann: nichts umbauen, nichts committen, Schritte 4 bis 8 überspringen. Nur das Wort
   „neu" im Auftrag erzeugt einen neuen Plan.
3. **Modus prüfen:** Nennt der Nutzer eine Reise (Geschäftsreise, Dienstreise, unterwegs,
   Hotel), gilt der Abschnitt *Geschäftsreise-Modus*. Nennt er Kassenbon-Preise oder eine
   Kassenbon-Summe, gilt *Kassenbon-Abgleich*. Sonst normale Woche.
4. **Gerichte wählen** (2–3 aus `gerichte.md`, sonst neu erfinden und in den Pool eintragen):
   - kein Gericht, das in den letzten 4 Wochen dran war (Spalte „Zuletzt" und `verlauf.md`)
   - drei verschiedene Proteine, z. B. Geflügel / Fisch / Hack oder Schwein
   - höchstens ein Gericht mit Hülsenfrüchten (Purin)
   - saisonales Gemüse bevorzugen (Saisontabelle in `gerichte.md`)
   - Frühstück: keins aus den letzten 3 Wochen
   - Snacks bleiben fest: Apfel vormittags, Magerquark nachmittags
5. **Liste bauen:** Mengen aus den Gerichten, dem Frühstück und den Snacks ableiten.
   Vorrat aus `verlauf.md` berücksichtigen: was noch da ist, nicht kaufen, aber unter
   „Annahmen" nennen (mit Preis, falls es doch fehlt). Preise nur aus `preise.md`.
   Ziel bei Penny: 55–60 €. Über 60 € → Vorratsartikel auf die Folgewoche schieben oder Mengen
   kürzen. Unter 50 € → Obst, Gemüse oder Vorrat auffüllen. Rewe-Schätzung = Penny + 10 %.
6. **Wochen-Datei schreiben:** `wocheneinkauf/wochen/JJJJ-MM-TT-woche-NN.md` nach der Vorlage
   unten. Jede Artikelzeile: `- [ ] Artikel Menge – 0,00 €`, optional danach `(Mo)` für die
   Montags-Tour.
7. **Prüfen (nur neue Dateien):** `python3 wocheneinkauf/summe.py wocheneinkauf/wochen/<datei>`. Die Summen in der
   Datei müssen mit der Ausgabe übereinstimmen, es darf keine Regel-Warnung geben. Sonst Datei
   korrigieren und erneut prüfen.
8. **Verlauf pflegen:** Zeile in `verlauf.md` ergänzen (Woche, Datum, Gerichte, Frühstück,
   Plansumme), Abschnitte „Proteine“ und „Vorrat“ aktualisieren, Spalte „Zuletzt" der benutzten
   Gerichte und des Frühstücks in `gerichte.md` setzen.
9. **Ausgabe im Chat:** vollständiger Plan im Ausgabeformat unten (nicht nur der Dateiname).
10. **Commit:** `Wocheneinkauf Woche NN (JJJJ-MM-TT)`. Pushen, wenn die Session auf einem
    Remote-Branch (`claude/…`) läuft oder der Nutzer es wünscht.

## Unbeaufsichtigter Lauf (Routine)

Die Freitags-Routine läuft ohne Menschen. Deshalb: keine Rückfragen, keine Optionen anbieten,
keine Bestätigung abwarten. Unklarheiten durch eine Annahme lösen und die Annahme im Plan
nennen. Rückfragen gibt es nur im Geschäftsreise-Modus, und nur wenn der Nutzer die Reise
selbst in dieser Session genannt hat. Schlägt ein Schritt fehl (Datei fehlt, Push abgelehnt),
den Plan trotzdem im Chat ausgeben und den Fehler am Ende klar benennen. Falls ein Werkzeug
für Push-Benachrichtigungen verfügbar ist, nach der Ausgabe eine kurze Nachricht mit
Einkaufstag, Gerichten und Summe senden.

## Ernährungsregeln (hart)

- Nie: Pilze, Innereien, Gorgonzola, Sardinen, Hering, Sardellen/Anchovis, Matjes.
- Jeden Tag Fleisch oder Fisch, ca. 100–150 g pro Person und Tag → pro Gerichtsportion
  100–150 g, eine Portion pro Person und Tag. Bei 1 Person: Hälfte einfrieren.
- Purinarm: keine Innereien, wenig Wurst (Salami, Schinken, Speck nur ausnahmsweise),
  Hülsenfrüchte höchstens einmal pro Woche, Hähnchenhaut abziehen.
- Vollkorn statt Weißmehl: Vollkornbrot, Vollkornnudeln, Naturreis, Bulgur, Haferflocken.
- Wenig Zucker: keine Süßigkeiten, Säfte, Limonade, gesüßte Joghurts; Obst als Snack.
- Salzarm: mit Kräutern, Zitrone, Knoblauch, Paprika, Kreuzkümmel würzen; Sojasoße und Brühe
  sparsam; keine Fertigsoßen.
- Hintergrund: Gicht, Blutzucker, Blutdruck.
- Homeoffice: mittags klein (halbe Beilage, mehr Gemüse) oder Brot/Quark/Salat.
- Trinken ist abgedeckt (2–3 l Wasser), nichts dazu planen.

## Logistik

- Penny, Lichterfelder Allee 7, 14513 Teltow. Mo–Sa 7–21 Uhr, So geschlossen.
- Rewe als Ausweichmarkt: ca. 8–12 % teurer, Basics als „ja!"-Eigenmarke.
- Zu Fuß, ca. 10 Min., Rucksack + 2 Taschen. Schweres (Kartoffeln, Zwiebeln, Karotten,
  Milch) in den Rucksack. Kühlware in eine Tasche, Druckempfindliches in die andere.
- Vorrat (Reis, Nudeln, Haferflocken, Linsen, Öl, Dosen) separat am Montag – in der Liste
  mit `(Mo)` markieren.
- Personen: 1–2. Für 2 planen, Hinweis für 1 Person ergänzen.

## Ausgabeformat (Chat und Datei)

1. Einkaufsliste nach Kategorien **Fleisch & Fisch / Obst & Gemüse / Kühlregal / Vorrat** mit
   Checkboxen, Mengen und Preisen
2. Summe pro Kategorie und gesamt, Penny und Rewe-Schätzung, Puffer zum Budget, Annahmen zum Vorrat
3. 2–3 Gerichte mit Portionen, Zutaten mit Mengen, kurzen Schritten, Mittags-Hinweis
4. 1 Frühstücksvorschlag
5. Snacks (fest) und Wochenplan-Vorschlag (Mittag klein / Abend), Transport-Aufteilung
6. Hinweis auf die nächste Liste (Freitag 9:30) und Feiertage, die den nächsten Einkauf betreffen

### Vorlage Wochen-Datei

```markdown
# Wocheneinkauf Woche NN – Sa TT.MM.JJJJ

Einkauf: Penny Teltow (Mo–Sa 7–21 Uhr) · Zeitraum: Sa TT.MM. – Fr TT.MM. · Personen: 2 · Budget: 60 €

## 1. Einkaufsliste

### Fleisch & Fisch
- [ ] Artikel Menge – 0,00 €

### Obst & Gemüse
### Kühlregal
### Vorrat
- [ ] Artikel Menge – 0,00 € (Mo)

## 2. Summe
| Kategorie | Penny |
|---|---|
| … | … |
| **Gesamt** | **0,00 €** |
Rewe-Schätzung, Puffer, Annahmen (noch vorhanden)

## Transport
## 3. Gerichte (je 4 Portionen)
## 4. Frühstück
## Snacks (fest)
## Wochenplan (Vorschlag)
## Nächste Liste
```

## Geschäftsreise-Modus

Nur wenn der Nutzer selbst eine Reise nennt. Dann keine Kochliste, sondern erst drei Rückfragen
in einer Nachricht:

1. Dauer der Reise (Abreise- und Rückreisetag)?
2. Hotel mit oder ohne Frühstück?
3. Kühlschrank und/oder Mikrowelle im Zimmer?

Nach der Antwort: Budget anteilig (60 € × Tage zu Hause / 7, aufgerundet auf volle Euro),
höchstens 2 Gerichte, nichts Verderbliches für die Reisetage kaufen, Reise-Snacks einplanen
(Äpfel, Walnüsse, Vollkorn-Knäcke). Ohne Hotelfrühstück: Haferflocken-Becher plus Nüsse;
mit Kühlschrank: Quark und Joghurt; mit Mikrowelle: Porridge. Woche im Verlauf als
„Woche NN (Reise)" eintragen. In der Kopfzeile der Wochen-Datei `Budget: NN €` (anteilig) und
`Tage zu Hause: N` angeben: `summe.py` prüft dann gegen das anteilige Budget und rechnet die
Fleischmenge auf die Tage zu Hause um. Fällt ein ganzer Einkaufstag in die Reise, entfällt die
Woche („Woche NN (Reise)", kein Einkauf); ein vorhandener Entwurf bleibt als Vorlage liegen.
Fehlt eine Antwort auf die Rückfragen, mit einer Annahme weitermachen und sie im Plan nennen.

## Kassenbon-Abgleich

Nennt der Nutzer echte Preise oder die Kassenbon-Summe:

- Einzelpreise in `preise.md` korrigieren (Spalte „Stand" mit Datum).
- Ist-Summe in `verlauf.md` in die Spalte „Kassenbon" eintragen.
- Weicht die Ist-Summe um mehr als 10 % von der Plansumme ab, in der nächsten Liste darauf
  hinweisen und die Mengen entsprechend anpassen.

## Checkliste vor der Ausgabe

- [ ] keine verbotene Zutat (Pilze, Innereien, Gorgonzola, Sardinen, Hering)
- [ ] jedes Gericht mit Fleisch oder Fisch, 100–150 g pro Portion
- [ ] Vollkorn, wenig Zucker, wenig Salz, höchstens ein Hülsenfrucht-Gericht
- [ ] Gerichte nicht aus den letzten 4 Wochen, Frühstück nicht aus den letzten 3
- [ ] Summe Penny 55–60 €, `summe.py` ohne Warnung und mit gleichen Zahlen wie die Datei
- [ ] Einkaufstag ist kein Sonntag und kein Feiertag
- [ ] Montags-Tour markiert, Rucksack für Schweres
- [ ] Verlauf, Vorrat und „Zuletzt" aktualisiert, Commit gemacht
