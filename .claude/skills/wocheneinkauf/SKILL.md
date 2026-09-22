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
| `wocheneinkauf/profil.md` | Körperdaten, Kalorienziel, Mahlzeitenstruktur, Portionen, Gewichtsverlauf |
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
   - Snack bleibt fest: Quark oder Skyr mit Beeren und Nüsse um 16 Uhr; Apfel vormittags optional
5. **Liste bauen:** Mengen aus den Gerichten, den Mittagstellern und dem Snack ableiten,
   Wochenmengen aus `profil.md` als Richtschnur.
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

Die Zahlen kommen aus `wocheneinkauf/profil.md` (Stand 22.09.2026): Rekomposition (Bauchfett weg,
moderat Muskeln), Ziel 2100 kcal am Ruhetag und 2300 kcal am Trainingstag, Eiweiß 140–160 g,
2 Mahlzeiten und 1 Snack.

- Nie: Pilze, Innereien, Zunge, Gorgonzola, Hüttenkäse, Oktopus, Tintenfisch, Sardinen, Hering,
  Sardellen/Anchovis, Matjes, Muscheln. Garnelen selten.
- **Mahlzeitenstruktur:** kein Frühstück. Mittag 12–13 Uhr vollwertig (800–900 kcal, nicht klein),
  fester Nachmittagssnack 16 Uhr (250–300 kcal, eiweißreich), Abendessen 19–20 Uhr das gekochte
  Gericht (900–1000 kcal). Vormittags höchstens 1 Apfel.
- **Fleisch oder Fisch nur im Abendessen:** 150 g pro Portion, also 100–150 g pro Person und
  Tag. Mittags kommt das Eiweiß aus Eiern, Quark, Skyr, Feta; abends 150 g Skyr oder Joghurt als
  Dip oder Dessert dazu. Jede Mahlzeit mindestens 35 g Eiweiß. Bei 1 Person die Hälfte einfrieren.
- **Portionen pro Person und Hauptmahlzeit:** Beilage 75 g Reis, Nudeln oder Bulgur trocken oder
  300 g Kartoffeln oder 2 Scheiben Vollkornbrot; Gemüse mindestens 250 g; 1 EL Öl; Nüsse 20–25 g am
  Tag. **Trainingstag:** zusätzlich 1 Banane vor dem Training oder Beilage 100 g statt 75 g. Nennt
  der Nutzer seine Trainingstage (`Training: Di Do Sa`), im Wochenplan dort eintragen.
- Purinarm: keine Innereien, wenig Wurst (Salami, Schinken, Speck nur ausnahmsweise),
  Hülsenfrüchte höchstens einmal pro Woche, Hähnchenhaut abziehen, täglich Quark oder Skyr.
- Vollkorn statt Weißmehl: Vollkornbrot, Vollkornnudeln, Naturreis, Bulgur, Haferflocken.
- Wenig Zucker: keine Süßigkeiten, Säfte, Limonade, gesüßte Joghurts, Trockenobst; Obst als
  Snack, Bananen höchstens 3 pro Woche.
- Salzarm, unter 6 g am Tag: mit Kräutern, Zitrone, Knoblauch, Paprika, Kreuzkümmel würzen;
  höchstens ½ TL Salz auf 4 Portionen; Sojasoße und Brühe sparsam; keine Fertigsoßen; Brot
  höchstens 3 Scheiben am Tag.
- Alkohol: höchstens 2 Gläser pro Woche, lieber Wein als Bier, nie an zwei Tagen nacheinander;
  an dem Tag die Beilage am Abend halbieren. Kein Bier in der Liste.
- Gemüse 3,5–4 kg pro Person und Woche, Obst 2 Portionen am Tag, Eier 18–22 pro Woche,
  Quark/Skyr/Joghurt 2–2,5 kg pro Woche (Wochenmengen in `profil.md`).
- Hintergrund: Gicht, Blutzucker, Blutdruck. Moderates Defizit, keine ausgelassenen Mahlzeiten,
  viel trinken (2–3 l Wasser, abgedeckt).
- Kochzeit ist keine Grenze: auch Aufläufe und Schmorgerichte sind erlaubt, Niklas nimmt sich Zeit.
- Meldet der Nutzer Gewicht oder Taille (`Gewicht: 87,4`, `Taille: 91`), in `profil.md` unter
  Gewichtsverlauf eintragen. Bei mehr als 3 kg oder 3 cm Änderung Grundumsatz und Ziel neu rechnen.
  Stehen Gewicht und Taille 3 Wochen still, 100 kcal vom Ruhetag abziehen und das im Plan nennen.

## Logistik

- Penny, Lichterfelder Allee 7, 14513 Teltow. Mo–Sa 7–21 Uhr, So geschlossen.
- Rewe als Ausweichmarkt: ca. 8–12 % teurer, Basics als „ja!"-Eigenmarke.
- Zu Fuß, ca. 10 Min., Rucksack + 2 Taschen. Schweres (Kartoffeln, Zwiebeln, Karotten,
  Milch) in den Rucksack. Kühlware in eine Tasche, Druckempfindliches in die andere.
- Vorrat (Reis, Nudeln, Haferflocken, Linsen, Öl, Dosen) separat am Montag – in der Liste
  mit `(Mo)` markieren.
- Personen: 1–2, die zweite Person isst etwa die Hälfte der Tage mit. Für 2 planen (4 Portionen
  pro Gericht), Reste einfrieren, Hinweis für 1 Person ergänzen.

## Ausgabeformat (Chat und Datei)

1. Einkaufsliste nach Kategorien **Fleisch & Fisch / Obst & Gemüse / Kühlregal / Vorrat** mit
   Checkboxen, Mengen und Preisen
2. Summe pro Kategorie und gesamt, Penny und Rewe-Schätzung, Puffer zum Budget, Annahmen zum Vorrat
3. 2–3 Gerichte mit Portionen, Zutaten mit Mengen, kurzen Schritten, Mittags-Hinweis
4. 2–3 Mittagsteller aus `gerichte.md` (erste Mahlzeit, 800–900 kcal) und 1 optionales Frühstück
   für das Wochenende oder die zweite Person
5. Nachmittagssnack (fest) und Wochenplan-Vorschlag (Mittagsteller / Abend), Transport-Aufteilung
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
## 4. Mittagsteller und Frühstück (optional)
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
- [ ] jedes Gericht mit Fleisch oder Fisch, 125–150 g pro Portion, nur im Abendessen
- [ ] Mittagsteller und Snack laut `profil.md`, Portionen und Wochenmengen eingehalten
- [ ] Vollkorn, wenig Zucker, wenig Salz, höchstens ein Hülsenfrucht-Gericht
- [ ] Gerichte nicht aus den letzten 4 Wochen, Frühstück nicht aus den letzten 3
- [ ] Summe Penny 55–60 €, `summe.py` ohne Warnung und mit gleichen Zahlen wie die Datei
- [ ] Einkaufstag ist kein Sonntag und kein Feiertag
- [ ] Montags-Tour markiert, Rucksack für Schweres
- [ ] Verlauf, Vorrat und „Zuletzt" aktualisiert, Commit gemacht
