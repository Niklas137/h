# Trikot-Animation an KFK LadoTeam anbinden

Stand 09.10.2026, bezogen auf KFK LadoTeam Version 24 (Quellstand b5c6cdc…). An der App selbst wird nichts
verändert. Es gibt zwei Wege, die sich ergänzen.

## Weg 1: Export einspielen (keine Änderung an der App)

1. In KFK LadoTeam als Admin oder Developer die Team-JSON exportieren (`GET /api/export`, Format `kfk-backup`).
2. In der Admin-Seite des Trikot-Moduls (`admin.html`) auf „JSON importieren“ klicken und diese Datei wählen.
   Das Modul erkennt das Format und übernimmt nur Name, ukrainischen Namen, beide Rückennummern, Position
   und Status. E-Mails, Notizen, Mitglieder, Termine und Finanzen werden nicht gelesen und nicht gespeichert.
3. „JSON exportieren“ und das Ergebnis als `daten/kader.json` ablegen. Nur diese Datei wird veröffentlicht;
   die Exportdatei aus KFK LadoTeam bleibt privat und gehört in kein Repository.

Bei jeder Kaderänderung wiederholen.

## Weg 2: öffentliche Kader-Schnittstelle (eine neue Datei in der App)

`app/api/public/kader/route.ts` aus diesem Ordner nach `Quellcode/app/api/public/kader/route.ts` kopieren.
Bestehende Dateien bleiben unverändert. Die Datei nutzt `loadTeam()` aus `lib/server.ts` und liefert ohne
Anmeldung nur die Felder, die die Trikotseite braucht (siehe Kopf der Datei). Deaktivierte Spieler fehlen.

Vor dem Veröffentlichen:

- In `ERLAUBTE_HERKUNFT` die Domain der KFK-Website eintragen (Schema und Host, z. B.
  `https://www.beispiel.ua`), damit der Browser der Website die Antwort lesen darf (CORS).
- `npm test`, `node node_modules/typescript/bin/tsc --noEmit`, `npm run build` wie in der Übergabeanleitung,
  dann wie gewohnt veröffentlichen.
- Prüfen: `https://<app-domain>/api/public/kader` im Browser öffnen. Erwartet wird JSON mit
  `"format": "kfk-kader"` und der Spielerliste; `/api/state` muss weiterhin 401 ohne Anmeldung liefern.

Hinweis zur Entscheidung: Mit dieser Datei ist die Kaderliste (Namen, Nummern, Position, Status) öffentlich
lesbar. Das ist für eine Vereinswebsite üblich, sollte aber vom Team gewollt sein.

Danach im Trikot-Modul in `daten/kader.json` eintragen:

```json
"team": { "quelle": "https://<app-domain>/api/public/kader", ... }
```

Die Kaderseite lädt die Spieler dann live von dort. Ist die Schnittstelle nicht erreichbar, zeigt sie den
zuletzt gespeicherten Stand aus `daten/kader.json` (Hinweis in der Browserkonsole). Trikotbilder, Fotos,
Profiltexte, Geburtsjahr und Statistik bleiben im Trikot-Modul und werden über die Spieler-ID zugeordnet.

## Weg 3: Ansicht „Trikots“ im Manager (empfohlen für die Vorschau im Team)

Die Trikot-Animation läuft als eigene Ansicht in der App, für angemeldete Nutzer, mit den Spielern aus dem
Teamstand und dem Sprachschalter der App. Vorschau des Ergebnisses: `einbettung.html` im Trikot-Modul
(Oberfläche nachgebaut, Spieler aus `daten/beispiel-ladoteam.json`).

Dateien in die App kopieren (nichts davon ersetzt eine bestehende Datei):

```
Quellcode/app/kader-trikots.tsx                      ← einbau-ladoteam/app/kader-trikots.tsx
Quellcode/public/assets/kader/kader-einbettung.js    ← kader-einbettung.js
Quellcode/public/assets/kader/kader-vorlage.js       ← kader-vorlage.js
Quellcode/public/assets/kader/kader-daten.js         ← kader-daten.js
Quellcode/public/assets/kader/sprache.js             ← sprache.js
Quellcode/public/assets/kader/kader-einbettung.css   ← kader-einbettung.css
Quellcode/public/assets/kader/fonts/                 ← fonts/ (Oswald, OFL-Lizenz liegt bei)
Quellcode/public/assets/kader/fotos/                 ← fotos/trikot-kfk-schwarz.png, fotos/trikot-kfk-weiss.png
```

Drei kleine Ergänzungen in bestehenden Dateien, jeweils eine Zeile, nichts wird entfernt:

1. `lib/i18n.ts`, in die Liste der Paare: `trikots:["Trikots","Футболки"],`
2. `app/team-app.tsx`, Import und Navigationseintrag:
   `import {KaderTrikots} from './kader-trikots';` und in `navigation` nach `['team',Users]` den Eintrag
   `['trikots',Users]` (oder ein anderes Lucide-Symbol, z. B. `Shirt`).
3. `app/team-app.tsx`, in der Seitenwahl vor `page==='finance'`: `page==='trikots'?<KaderTrikots/>:`

Die Komponente lädt die Moduldateien zur Laufzeit aus `/assets/kader/` (am Bundler vorbei), hängt die Ansicht
in ein eigenes Element und räumt beim Wechsel der Ansicht oder Sprache wieder auf. Sie schreibt keinen Hash,
der Hash bleibt bei der App-Navigation. Alle Stilregeln sind auf `.kader-wurzel` begrenzt und ändern Farben
und Schriften der App nicht (geprüft: `--ink` und Hintergrund des Gastgebers bleiben).

Prüfen nach dem Einbau: `npm test`, `tsc --noEmit`, `npm run build`, dann in der App „Trikots“ öffnen, ein
Trikot antippen, Sprache umschalten, Heim/Auswärts wechseln (Koval zeigt 1 bzw. 31). Mit 390 px Breite ohne
waagerechten Überlauf. Was hier nicht nachgewiesen ist: der Lauf in der echten App (Node, Wrangler, D1, R2).
Die Moduldateien und die Einbettung sind mit dem Nachbau in Chromium geprüft.

## Feldzuordnung

| KFK LadoTeam | Trikot-Modul | Anmerkung |
|---|---|---|
| `id` | `id` | Kleinbuchstaben, nur a–z, 0–9, Bindestrich |
| `name`, `nameUk` | `name`, `nameUk` | fehlt `nameUk`, nutzt die Seite ihre automatische Umschrift |
| `black` | `number` | Heimtrikot (schwarz); fehlt sie, gilt `white` |
| `white` | `numbers.weiss` | nur gespeichert, wenn sie von `black` abweicht |
| `position` `goalie`/`defense`/`offense` | Torwart / Verteidiger / Stürmer | `detail` wird als Zusatz in der Karte gezeigt |
| `status` `active`/`recovery`/`injured`/`inactive` | gleich | `recovery` heißt „Im Aufbau“, `inactive` wird nicht angezeigt |
| `email`, `note`, Mitglieder, Termine, Finanzen | nicht übernommen | |

Was aus dieser Sitzung nicht nachgewiesen ist: Die Datei `route.ts` wurde nicht in einer laufenden
KFK-LadoTeam-Installation gestartet (die App läuft nur mit Node, Wrangler, D1 und R2). Die Feldlogik ist im
Trikot-Modul mit einem Beispiel in beiden Formaten geprüft; den Endpunkt selbst bitte nach dem Veröffentlichen
einmal aufrufen.
