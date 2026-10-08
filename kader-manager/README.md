# Kader-Manager – Spieler-/Trikot-Animation

Eigenständiges Web-Modul (HTML, CSS, JavaScript, JSON), ohne Bibliotheken, ohne Build-Schritt.
Gedacht zur Übernahme in die bestehende Floorball-Website. Alle Spielerdaten kommen aus
`daten/kader.json`; es gibt keine fest eingetragenen Spieler im Code.

## Dateien

| Datei | Aufgabe |
|---|---|
| `index.html`, `kader.js` | Kaderseite „Kleiderstange“: hängende Trikots, Auswahl, Trikot-Animation, Datenkarte, Nummernband, Positionsfilter |
| `admin.html`, `admin.js` | Admin: Spieler anlegen, bearbeiten, deaktivieren, löschen, Nummer/Position/Foto/Status ändern, JSON exportieren und importieren |
| `kader-daten.js` | Gemeinsame Datenschicht: laden, prüfen (Pflichtfelder, eindeutige IDs, Trikotparameter), Trikot als SVG erzeugen |
| `sprache.js` | Oberflächentexte Deutsch und Ukrainisch (`team.language` in kader.json, `?lang=uk` zum Testen) |
| `server.py`, `.env.example` | Kleiner Server ohne Abhängigkeiten: statische Dateien plus geschütztes Veröffentlichen (`PUT /api/kader`) |
| `UMSETZUNG_Pruefbericht_2026-10-08.md` | Status aller Befunde aus dem Prüfbericht vom 08.10.2026 |
| `kader.css` | Umkleideraum-Optik, Glaskarte, Animation (nur `transform` und `opacity`), `prefers-reduced-motion`; Admin hell/dunkel |
| `daten/kader.json` | Kaderdaten (Beispiel) |
| `fotos/` | KFK-Trikots (freigestellt) und Spielerfotos, Pfad im Feld `photo` |
| `fonts/` | Oswald 700 für den Aufdruck (OFL-Lizenz liegt bei) |

## Lokal starten

Die Seite lädt `daten/kader.json` per `fetch`, deshalb ist ein kleiner Webserver nötig:

```
cd kader-manager
python3 -m http.server 8000
```

Dann `http://localhost:8000/` (Kader) und `http://localhost:8000/admin.html` (Admin) öffnen.

## Datenmodell

```json
{
  "team": { "name": "…", "short": "FEH", "season": "2026/27",
            "colors": { "primary": "#0B3D91", "secondary": "#F2C230", "text": "#FFFFFF" } },
  "players": [
    { "id": "jan-jenner", "name": "Jan Jenner", "number": 18, "position": "Stürmer",
      "status": "active", "nationality": "DE", "photo": "fotos/jan-jenner.jpg",
      "birthYear": 1998, "stats": { "games": 14, "goals": 9, "assists": 6, "penaltyMinutes": 4 } }
  ]
}
```

- Pflicht: `id`, `name`, `number` (0–99), `position`, `status` (`active`, `injured`, `inactive`).
- Optional: `nationality` (Länderkürzel), `photo`, `birthYear`, `bio` (Profiltext), `stats` mit `games`, `goals`, `assists`, `penaltyMinutes`.
- Es wird nur angezeigt, was vorhanden ist. Spieler mit `status: "inactive"` erscheinen nicht auf der Kaderseite.
- `team.colors` steuert die Trikotfarben; Nummer und Name auf dem Trikot kommen aus `number` und `name`.

## Ablauf der Animation (nach dem Referenzvideo, Trikots an der Stange)

Ausgangsbild: dunkler Umkleideraum, eine Stange, daran hängen alle Trikots mit Rückennummer
und Name, schräg gedreht (50°, einstellbar über `team.tilt` in `daten/kader.json`, 30–85; der Bügelabstand folgt der Neigung), waagerecht scrollbar. Unter der Szene: aktueller Spieler
(Nummer, Name, Position, „Trikot antippen“), Nummernband zum Springen, Positionsfilter mit Anzahl. Die Stange lässt sich mit den Pfeilen links und rechts,
den Pfeiltasten, per Wischen (Finger) oder Ziehen (Maus) bewegen.

1. Tipp auf ein Trikot: Das Trikot dreht sich an Ort und Stelle nach vorn (0,42 s), die Nachbarn
   bleiben hängen. Gleichzeitig fährt die Kamera heran: die ganze Stange wird um das Trikot herum
   vergrößert und verschoben (0,56 s, Desktop 1,3-fach, mobil 1,22-fach), der Raum wird leicht dunkler.
2. Kurz danach (0,26 s) schiebt sich die Glaskarte „Kader-Blatt“ ein: mobil von unten, Desktop von rechts.
   Kopf mit Team, Saison und Zähler „8 / 12“; darunter Nationalität, Position, Nummer, Name,
   dann die Datenzeilen nacheinander, optional der Profiltext.
3. Danach bleibt die Ansicht statisch.
4. Pfeile, Pfeiltasten oder Tipp auf ein Nachbartrikot: die Kamera schwenkt entlang der Stange zum
   nächsten Trikot, das alte dreht sich zurück, das neue nach vorn, die Karte blendet um.
5. „Zurück zur Stange“, Escape oder Tipp daneben: Karte fährt raus, dann fährt die Kamera zurück
   und das Trikot dreht sich wieder seitlich.

Technik: nur `transform` und `opacity`; die Kamera ist ein `translate` + `scale` auf der Trikotliste,
die Drehung ein `rotateY` je Trikot (`kader.css`, Funktion `kameraAuf()` in `kader.js`).

Bei `prefers-reduced-motion: reduce` entfallen Drehung und Kamerafahrt; Trikot und Karte blenden
nur kurz ein. Alle Funktionen bleiben erhalten. Direktlink: `index.html#spieler=jan-jenner`.

## KFK-Trikots

Beide Trikots liegen freigestellt in `fotos/` (Rückansicht, PNG mit Transparenz, Aufdruck entfernt):
`trikot-kfk-schwarz.png` (Heim, schwarz-gold) und `trikot-kfk-weiss.png` (weiß-gold). Quelle sind die
beiden Kit-Vorlagen von Niklas; die Rückansicht wurde aus der rechten Hälfte gespiegelt, damit die
Shorts der Vorlage nicht hineinragen.

Aktiv ist das schwarze Trikot, eingestellt in `daten/kader.json` beim Team:

```json
"jersey": { "back": "fotos/trikot-kfk-schwarz.png",
            "nameY": 100, "numberY": 268, "nameSize": 34, "numberSize": 165,
            "nameColor": "#C9A24A", "numberColor": "#C9A24A" }
```

Nummer und Name werden aus den Spielerdaten darübergelegt, nichts ist im Bild fest. Alle Namen haben dieselbe
Schriftgröße; lange Namen werden enger gesetzt (SVG `textLength`), nicht kleiner. Nummern haben immer dieselbe Höhe,
zweistellige werden auf die Rückenbreite eingepasst. Für das weiße
Trikot den Block aus `jerseyAlternatives.weiss` nach `jersey` kopieren (Beschriftung dann schwarz).
Lage und Größe gelten im 400 × 440-Raster des Trikots. Ohne `jersey` wird eine gezeichnete Form genutzt.

Schrift der Rückennummer und des Namens: Oswald 700 (schmale Blockschrift, SIL Open Font License,
Dateien in `fonts/`), lokal eingebunden, kein Aufruf externer Server. Der Aufdruck bekommt in
`kader-daten.js` einen Lichtverlauf, eine leichte Stoffwölbung und einen hauchdünnen Schatten,
damit er auf dem Stoff liegt statt darüber zu schweben. Wenn die Druckerei eine andere Schrift nennt,
`--druck` in `kader.css` anpassen.

## Admin und Veröffentlichung

Zwei Betriebsarten:

1. **Statisch** (z. B. GitHub Pages, einfacher Webspace): Die Admin-Seite speichert Änderungen im Browser
   (`localStorage`); die Kaderseite zeigt sie sofort mit Hinweis „lokale Änderungen“. Veröffentlicht wird durch
   „JSON exportieren“ und Ersetzen von `daten/kader.json`.
2. **Mit `server.py`** (Python 3, keine Abhängigkeiten): `KADER_ADMIN_TOKEN='geheim' python3 server.py 8000`.
   Die Admin-Seite erkennt den Server und zeigt „Veröffentlichen“: Mit dem Token wird der geprüfte Stand nach
   `daten/kader.json` geschrieben, davor landet eine Sicherung in `daten/sicherung/`. Ohne gültigen Token
   lehnt der Server ab (403), ungültige Daten ebenfalls (422). Der Token steht nur in der Umgebungsvariable,
   siehe `.env.example`; die Sicherungen sind nicht abrufbar.

Für ein eigenes Backend genügt es, `laden()` und `lokalSchreiben()` in `kader-daten.js` sowie das
Veröffentlichen in `admin.js` auf die eigene API umzustellen.

Weitere Funktionen der Kaderseite: Heim-/Auswärtstrikot-Umschalter (erscheint, wenn `jerseyAlternatives`
gesetzt ist), „Link kopieren“ in der Spielerkarte (Direktlink `#spieler=<id>`), Sprache Deutsch oder
Ukrainisch über `team.language` (`"de"` oder `"uk"`).

## Einbau in die bestehende Website

- `kader.css` an das Design anpassen: Farben und Schriften stehen als Variablen am Anfang der Datei.
- `index.html` liefert nur den Inhalt der Kaderseite; Kopf- und Fußzeile der Website außen herum setzen.
- `admin.html` in den geschützten Admin-Bereich übernehmen oder die Tabelle dort nachbauen und `kader-daten.js` weiterverwenden.
