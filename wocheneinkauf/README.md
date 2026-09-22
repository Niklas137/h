# Wocheneinkauf für Niklas

Wöchentliche Einkaufsliste plus 2–3 Gerichte und ein Frühstück, automatisiert mit Claude Code.
Auslöser ist das Wort **„Wocheneinkauf"** im Chat (oder `/wocheneinkauf`). Die Regeln stehen im
Skill `.claude/skills/wocheneinkauf/SKILL.md`, die Daten in diesem Ordner.

## So läuft eine Woche

1. Freitag 9:30 Uhr: Die Routine erstellt den Plan für den Samstag automatisch, speichert ihn
   unter `wochen/`, committet nach `main` und schickt eine Push-Nachricht (Aufbau siehe unten).
2. Bei Bedarf in der Session „Wocheneinkauf Niklas (Routine)" antworten, z. B.
   `Geschäftsreise Di–Do` oder `anderes Fischgericht`. Von Hand geht es jederzeit mit
   `Wocheneinkauf` in einer Claude-Code-Session mit diesem Repo.
3. Samstag: Einkauf bei Penny (Frisches). Montag: Vorrats-Tour (Schweres und Trockenes).
4. Optional nach dem Einkauf: `Kassenbon: 57,80 €` oder einzelne Preise melden. Claude
   korrigiert `preise.md` und trägt die Ist-Summe im Verlauf ein.

## Feste Parameter

- Budget: 60 € pro Woche (fest, wird nicht nachgefragt)
- Personen: 1–2, die zweite Person etwa die Hälfte der Tage (Planung für 2, Reste einfrieren)
- Einkauf: Penny (Lichterfelder Allee 7, 14513 Teltow) oder Rewe
  - Penny: Mo–Sa 7–21 Uhr, So geschlossen
  - Rewe: ca. 8–12 % teurer → Eigenmarke „ja!" bei Basics
- Transport: zu Fuß, ca. 10 Min., Rucksack + 2 Taschen
  - Schweres (Kartoffeln, Zwiebeln, Karotten, Milch) in den Rucksack
  - Vorrat (Reis, Nudeln, Haferflocken, Linsen, Öl) separat am Montag
- Trigger: Erinnerung freitags 9:30 Uhr → Nutzer schreibt „Wocheneinkauf"

## Ernährungsregeln

Persönliche Zielwerte stehen in `profil.md` (Stand 22.09.2026): 2100 kcal am Tag, Eiweiß 110–130 g,
langsam abnehmen, kein Frühstück, Mittagsteller, fester Nachmittagssnack, gekochtes Gericht am Abend.

- Nicht: Pilze, Innereien, Zunge, Gorgonzola, Hüttenkäse, Oktopus, Tintenfisch
- Fleisch oder Fisch nur im Abendessen, 125–150 g pro Portion, also 100–150 g pro Tag
- Purinarm: keine Innereien, Sardinen, Hering, Muscheln; wenig Wurst; täglich Quark oder Skyr
- Vollkorn statt Weißmehl, wenig Zucker, salzarm (unter 6 g)
- Alkohol höchstens 2 Gläser pro Woche, lieber Wein als Bier
- Grund: Gicht, Blutzucker, Blutdruck
- Homeoffice: Mittag vollwertig, Snack um 16 Uhr festgelegt (Quark oder Skyr, Beeren, Nüsse)
- Trinken ist abgedeckt (2–3 l Wasser pro Tag)

## Ausgabeformat

1. Liste nach Kategorien (Fleisch & Fisch / Obst & Gemüse / Kühlregal / Vorrat) mit Checkboxen,
   Mengen und Preisen
2. Summe ≈ 60 €
3. 2–3 Gerichte mit Mengenangaben (Portionen), kurze Schritte
4. 1 Frühstücksvorschlag
5. Jede Woche andere Gerichte

## Geschäftsreise-Modus

Der Nutzer sagt selbst Bescheid. Dann stellt Claude Rückfragen statt einer Kochliste:

- Dauer der Reise
- Hotel mit oder ohne Frühstück
- Kühlschrank / Mikrowelle vorhanden?

## Dateien

| Datei | Zweck |
|---|---|
| `README.md` | diese Übersicht, feste Parameter, Feiertage |
| `profil.md` | Körperdaten, Kalorienziel, Mahlzeitenstruktur, Wochenmengen, Gewichtsverlauf |
| `preise.md` | Richtpreise Penny / Rewe „ja!", per Kassenbon gepflegt |
| `gerichte.md` | Gerichte- und Frühstückspool mit Rotation („Zuletzt") und Saisontabelle |
| `verlauf.md` | Log aller Wochen, Proteine, geschätzter Vorrat |
| `wochen/` | eine Datei pro Woche: `JJJJ-MM-TT-woche-NN.md` |
| `summe.py` | prüft eine Wochen-Datei: Summen, Budget, verbotene Zutaten, Fleischmenge |

Prüfung von Hand:

```bash
python3 wocheneinkauf/summe.py wocheneinkauf/wochen/2026-09-26-woche-02.md
```

## Freitags-Routine (automatisch)

Aufbau der Automatisierung, Stand 19.09.2026:

- **Session „Wocheneinkauf Niklas (Routine)"** in Claude Code: dauerhafte Session mit dem Repo
  auf `main`, pusht direkt nach `main`. Sie ist das Gedächtnis der Routine. Rückmeldungen
  (Geschäftsreise, Änderungswünsche, Kassenbon) gehören in diese Session.
- **Routine „Wocheneinkauf Niklas (Fr 9:30)"**: schickt jeden Freitag um 9:30 Uhr Berlin das
  Wort „Wocheneinkauf" mit den Laufanweisungen in diese Session. Cron in UTC: `30 7 * * 5`
  (Sommerzeit) bzw. `30 8 * * 5` (Winterzeit, 26.10.2026 bis 27.03.2027). Die Umstellung am
  26.10.2026 ist als Erinnerung hinterlegt; bleibt sie aus, den Cron von Hand ändern.
- **Benachrichtigung**: Die Session sendet nach dem Lauf eine Push-Nachricht mit Einkaufstag,
  Gerichten und Summe. Der vollständige Plan steht im Chat der Session und in `wochen/`.
- **Voraussetzung**: Der Skill muss auf `main` liegen, also PR #1 gemerged sein. Solange nicht,
  meldet der Lauf nur „PR #1 noch nicht gemerged" und erstellt keinen Plan.
- **Von Hand starten**: In der Session „Wocheneinkauf Niklas (Routine)" einfach `Wocheneinkauf`
  schreiben. Nicht „Jetzt ausführen" der Routine benutzen: Ein erzwungener Lauf startet eine
  neue Session ohne Repository (am 19.09.2026 so beobachtet). Termin-Läufe kommen dagegen
  zuverlässig in der Routine-Session an.

Test des Geschäftsreise-Modus am 19.09.2026: Reise 22.09. bis 02.10. durchgespielt, danach als Test
zurückgesetzt. Die Routine läuft regulär weiter, nächster Lauf Fr 25.09. für Woche 2.

Warum keine frische Session pro Lauf: Über die API angelegte Routinen starten ohne
Repository-Quelle. Eine dauerhafte Session bringt Repo, Branch und Push-Rechte mit.

Testläufe am 19.09.2026: (1) Auf dem PR-Branch Woche 3 unbeaufsichtigt erzeugt, geprüft und als
Commit 2568f64 gepusht, Push-Benachrichtigung angefordert, keine Rückfragen, keine verweigerten
Berechtigungen. (2) Ein Termin-Lauf in die Routine-Session auf `main`: Repo ausgecheckt, Skill
noch nicht vorhanden erkannt, Push-Nachricht gesendet, sauber beendet.

## Feiertage Brandenburg (Penny geschlossen)

Fällt der Samstag auf einen Feiertag, wird am Freitag eingekauft. Am 24.12. und 31.12.
schließen die Märkte meist um 14 Uhr.

| Datum | Feiertag | Folge für den Einkauf |
|---|---|---|
| Sa 03.10.2026 | Tag der Deutschen Einheit | Einkauf Fr 02.10. |
| Sa 31.10.2026 | Reformationstag | Einkauf Fr 30.10. |
| Fr 25.12.2026 | 1. Weihnachtstag | Einkauf Do 24.12. bis 14 Uhr |
| Sa 26.12.2026 | 2. Weihnachtstag | Einkauf Do 24.12. oder Mo 28.12. |
| Fr 01.01.2027 | Neujahr | Sa 02.01. offen |
| Fr 26.03.2027 | Karfreitag | Sa 27.03. offen |
| Mo 29.03.2027 | Ostermontag | Vorrats-Tour auf Di 30.03. |
| Sa 01.05.2027 | Tag der Arbeit | Einkauf Fr 30.04. |
| Do 06.05.2027 | Christi Himmelfahrt | keine |
| Mo 17.05.2027 | Pfingstmontag | Vorrats-Tour auf Di 18.05. |
| So 03.10.2027 | Tag der Deutschen Einheit | keine |
| So 31.10.2027 | Reformationstag | keine |
| Sa 25.12.2027 | 1. Weihnachtstag | Einkauf Fr 24.12. bis 14 Uhr |

## Woche 1 (Sa 19.09.2026)

Ursprünglich im Chat ohne Preise geplant, am Sa 19.09.2026 mit „Wocheneinkauf neu" durch einen
vollständigen Plan ersetzt. Datei: `wochen/2026-09-19-woche-01.md`, Summe 58,11 €. Einkauf auf
Wunsch am Mo 21.09. in einem Gang, Zeitraum bis Fr 25.09.

Gerichte: Ofen-Hähnchen mit Rosmarinkartoffeln und grünen Bohnen, Gefüllte Paprika mit Hack und
Reis, Lachs-Spinat-Nudeln. Frühstück: Quark-Bowl mit Haferflocken, Apfel und Zimt.
