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
| `server.py`, `.env.example` | Kleiner Server ohne Abhängigkeiten: statische Dateien plus geschützte Anmeldung (`POST /api/anmelden`), Veröffentlichen (`PUT /api/kader`) und Foto-Upload (`POST /api/foto`) |
| `UMSETZUNG_Pruefbericht_2026-10-08.md` | Status aller Befunde aus dem Prüfbericht vom 08.10.2026 |
| `kader.css` | Umkleideraum-Optik, Glaskarte, Animation (nur `transform` und `opacity`), `prefers-reduced-motion`; Admin hell/dunkel |
| `daten/kader.json` | Kaderdaten (Beispiel) |
| `fotos/` | KFK-Trikots (freigestellt); Spielerfotos aus dem Admin-Upload in `fotos/spieler/`, Pfad im Feld `photo` |
| `kader-einbettung.js`, `kader-vorlage.js`, `kader-einbettung.css`, `einbettung.html` | Einhängbares Modul, Markup-Vorlage, begrenztes Stylesheet und Vorschau der Ansicht im Manager |
| `einbau-ladoteam/` | Anbindung an KFK LadoTeam: Übergabenotiz für Falk und die neue Schnittstellendatei `route.ts` |
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
- Optional: `nationality` (Länderkürzel), `photo`, `birthYear`, `bio` (Profiltext), `stats` mit `games`, `goals`, `assists`, `penaltyMinutes`,
  `numbers` (Rückennummer je Trikot, z. B. `{"weiss": 31}`), `positionDetail` (Zusatz zur Position).
- Status: `active`, `recovery` (Im Aufbau), `injured`, `inactive` (nicht auf der Seite).
- Zweisprachig: `nameUk` (Name in ukrainischer Schreibweise) und `bioUk` (Profiltext ukrainisch). In der ukrainischen
  Ansicht stehen sie auf Trikot, Karte, Leiste und in den Vorlesetexten; fehlt `nameUk`, wird `name` gezeigt.
- Es wird nur angezeigt, was vorhanden ist. Spieler mit `status: "inactive"` erscheinen nicht auf der Kaderseite.
- `team.colors` steuert die Trikotfarben; Nummer und Name auf dem Trikot kommen aus `number` und `name`.

## Ablauf der Animation (nach dem Referenzvideo, Trikots an der Stange)

Ausgangsbild: dunkler Umkleideraum, eine Stange, daran hängen alle Trikots mit Rückennummer
und Name, schräg gedreht (50°, einstellbar über `team.tilt` in `daten/kader.json`, 30–85; der Bügelabstand folgt der Neigung), waagerecht scrollbar. Unter der Szene: aktueller Spieler
(Nummer, Name, Position, „Trikot antippen“), Nummernband zum Springen, Positionsfilter mit Anzahl. Die Stange lässt sich mit den Pfeilen links und rechts,
den Pfeiltasten, per Wischen (Finger) oder Ziehen (Maus) bewegen. Nach dem Wischen rastet das nächste
Trikot mittig ein.

Wischgesten am Handy bei offener Karte: nach links wischen (auf Trikot oder Karte) zeigt den nächsten
Spieler, nach rechts den vorherigen; die Kamera schwenkt wie im Video. Den Kartenkopf nach unten wischen
schließt die Karte. Tippen auf ein Nachbartrikot wechselt ebenfalls, Tippen auf „Zurück zur Stange“ schließt.

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

### Anmeldung

Die Admin-Seite öffnet zuerst ein Anmeldefenster. Mit `server.py` wird das eingegebene Admin-Passwort
(= `KADER_ADMIN_TOKEN`) per `POST /api/anmelden` am Server geprüft; erst dann erscheint die Kaderverwaltung.
Das Passwort bleibt nur für die Browsersitzung gemerkt (`sessionStorage`), landet nie in den Daten und
wird mit „Abmelden“ oder dem Schließen des Tabs verworfen. Fehlversuche bremst der Server mit 0,5 s.
Ohne Server (statische Seite, Vorschau) gibt es zwei Fälle:

- Ohne gesetztes Passwort weist das Fenster auf den lokalen Modus hin, „Lokal weiterarbeiten“ öffnet die
  Verwaltung, Änderungen bleiben im eigenen Browser.
- Mit Passwort (oben rechts „Passwort“ festlegen, mindestens 8 Zeichen) fragt das Fenster danach. Gespeichert
  wird nur die SHA-256-Prüfsumme als `team.adminPasswordHash` in den Kaderdaten; sie wandert mit „JSON
  exportieren“ nach `daten/kader.json` und gilt dann überall, wo diese Datei liegt. Die Anmeldung hält für die
  Browsersitzung (Tab). Das ist eine Zugangshürde für die Admin-Oberfläche, kein Schutz der Daten: Wer die
  Datei lesen kann, sieht die Kaderdaten ohnehin, und Änderungen ohne Server bleiben im eigenen Browser.
  Echten Schutz gibt nur `server.py` mit `KADER_ADMIN_TOKEN`; dort wird das lokale Passwort nicht benutzt.

Rückfragen und Hinweise der Admin-Seite (Löschen, Import, Verwerfen, Fehler) laufen über eigene Dialoge auf
der Seite, nicht über `confirm()`/`alert()` des Browsers, weil Einbettungen und Vorschauen diese oft sperren.

### Spielerfotos importieren

Im Spielerdialog steht „Foto auswählen“ (JPG, PNG oder WebP, bis 12 MB). Das Bild wird im Browser auf
einen 3:4-Ausschnitt von 480 × 640 Pixel verkleinert (JPEG, etwa 30–80 KB) und dann

- mit `server.py`: per `POST /api/foto?spieler=<id>` nach `fotos/spieler/<id>.jpg` hochgeladen (Token nötig,
  Dateityp wird am Dateianfang geprüft, max. 3 MB, ID nur `a-z0-9-`); im Feld `photo` steht der Pfad mit
  Versionszusatz `?v=…`, damit ein neues Foto sofort sichtbar ist;
- ohne Server: als eingebettetes Bild (`data:image/jpeg;base64,…`) im Feld `photo` gespeichert; es wandert mit
  „JSON exportieren“ in `daten/kader.json`.

„Foto entfernen“ leert das Feld; die Datei auf dem Server bleibt liegen, bis ein neues Foto sie ersetzt.
Beim Server-Upload müssen Name und Rückennummer schon eingetragen sein, daraus entsteht die Spieler-ID.

Für ein eigenes Backend genügt es, `laden()` und `lokalSchreiben()` in `kader-daten.js` sowie das
Veröffentlichen in `admin.js` auf die eigene API umzustellen.

Weitere Funktionen der Kaderseite: Heim-/Auswärtstrikot-Umschalter (erscheint, wenn `jerseyAlternatives`
gesetzt ist), „Link kopieren“ in der Spielerkarte (Direktlink `#spieler=<id>`).

## Anbindung an KFK LadoTeam (Falks Kader-Manager)

Falks App bleibt unverändert; die Trikotseite liest ihre Spieler von dort. Zwei Wege, Details und die
Datei für Falk in `einbau-ladoteam/`:

- **Weg 1, Export einspielen:** Team-JSON aus KFK LadoTeam exportieren, im Admin „JSON importieren“ wählen.
  Das Modul erkennt das Format (`kfk-backup`), übernimmt nur Name, ukrainischen Namen, beide Rückennummern,
  Position und Status und behält Team, Trikots, Fotos und Profiltexte. Danach „JSON exportieren“ und als
  `daten/kader.json` ablegen. Die Exportdatei aus der App enthält E-Mails und Finanzen und bleibt privat.
- **Weg 2, live:** Falk nimmt `einbau-ladoteam/app/api/public/kader/route.ts` in seine App auf (eine neue
  Datei, Freigabe der Website-Domain eintragen, veröffentlichen). Dann in `daten/kader.json` unter `team`
  die Adresse eintragen: `"quelle": "https://<app-domain>/api/public/kader"`. Die Kaderseite lädt die
  Spieler bei jedem Aufruf von dort; ist die Adresse nicht erreichbar, zeigt sie den gespeicherten Stand.
  Fotos, Profiltexte, Geburtsjahr und Statistik bleiben im Modul und werden über die Spieler-ID zugeordnet.

Zuordnung: `black` → Heimnummer `number`, `white` → `numbers.weiss` (nur wenn abweichend; der Heim-/Auswärts-
Schalter zeigt die passende Nummer), `goalie`/`defense`/`offense` → Torwart/Verteidiger/Stürmer, `detail`
→ Zusatz in der Karte, Status `recovery` → „Im Aufbau“. Deaktivierte Spieler fehlen auf der Seite,
Spieler ohne Rückennummer werden mit Hinweis in der Konsole ausgelassen.

## Ansicht „Trikots“ im Manager (Einbettung)

Die Kaderseite ist seit 09.10.2026 ein einhängbares Modul: `kaderMounten(element, optionen)` in
`kader-einbettung.js` baut Markup (aus `kader-vorlage.js`), Stange, Karte und Leiste in ein beliebiges Element.
`index.html` nutzt es über `kader.js` ohne Optionen. Für die Einbettung in KFK LadoTeam: Optionen `daten`
(geprüftes `{team, players}`), `sprache` (`de`/`uk`, Sprachschalter des Moduls bleibt dann verborgen) und
`hash: false` (keine `#spieler=`-Links, der Gastgeber nutzt den Hash). `kader-einbettung.css` ist die auf
`.kader-wurzel` begrenzte Fassung von `kader.css` (abgeleitet mit `einbau-ladoteam/css-ableiten.py`, nach
jeder Änderung an `kader.css` neu erzeugen). Vorschau im Nachbau der Manager-Oberfläche: `einbettung.html`.
Die React-Komponente und die Einbauschritte für Falk stehen in `einbau-ladoteam/UEBERGABE_FALK.md`, Weg 3.

## Sprachen: Deutsch und Ukrainisch

Der Schalter „DE | UK“ im Kopf der Kaderseite stellt die ganze Seite um: Oberflächentexte (`sprache.js`),
die vier Standardpositionen (Torwart → Воротар, Verteidiger → Захисник, Center → Центральний,
Stürmer → Нападник), Spielernamen aus `nameUk` auf Trikot, Karte und Leiste sowie der Profiltext aus `bioUk`.
Reihenfolge der Sprachwahl: `?lang=uk|de` in der Adresse, dann die gemerkte Wahl im Browser, dann
`team.language` aus `daten/kader.json`. Der Direktlink `#spieler=<id>` bleibt beim Umschalten erhalten.
Andere Positionen als die vier Standardwerte erscheinen in beiden Sprachen so, wie sie eingetragen sind.
Die ukrainische Schreibweise der Namen entsteht automatisch (`transliterieren()` in `sprache.js`): Umkehrung der
amtlichen ukrainischen Romanisierung (Oleh → Олег, Yurii → Юрій, Polishchuk → Поліщук, Kravets → Кравець); bei
Nationalität DE, AT oder CH gelten deutsche Leseregeln (Jan Jenner → Ян Єннер, Schmidt → Шмідт). Im Admin wird
das Feld „Name ukrainisch“ beim Tippen vorausgefüllt, „Auto“ erzeugt es neu, eine Eingabe von Hand hat Vorrang.
Bleibt das Feld leer, nutzt die Kaderseite die automatische Umschrift. Grenze: Aus der lateinischen Form ist
nicht immer eindeutig, ob і oder и gemeint ist (Malinovskyi → Маліновський statt Малиновський); solche Fälle
im Admin von Hand setzen. Profiltexte werden nicht automatisch übersetzt; ohne `bioUk` erscheint der deutsche Text.

## Einbau in die bestehende Website

- `kader.css` an das Design anpassen: Farben und Schriften stehen als Variablen am Anfang der Datei.
- `index.html` liefert nur den Inhalt der Kaderseite; Kopf- und Fußzeile der Website außen herum setzen.
- `admin.html` in den geschützten Admin-Bereich übernehmen oder die Tabelle dort nachbauen und `kader-daten.js` weiterverwenden.
