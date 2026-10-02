# Referenzfreigabe: Vorlage für die Anfrage beim Kunden

Stand 01.10.2026. Wer einen Kunden namentlich auf der Website nennen will, braucht dessen schriftliche
Zustimmung; ohne sie bleibt die Referenz anonym („Energieversorger (DE)“). Die Vorlage ist so gebaut, dass
der Kunde nur ankreuzen und zurückschicken muss. Keine Rechtsberatung; bei Rahmenverträgen mit
Geheimhaltungsklausel vorher die Klausel lesen, sie geht vor.

## Was wir zeigen würden

Je Kunde genau eine Zeile im Abschnitt „Referenzen und Fallstudien“ der Startseite, nach dem Muster, das
dort heute anonym steht:

| Feld | Beispiel |
|---|---|
| Name | Musterwerk GmbH, Leipzig |
| Leistung | ST4-Einführung mit DE/EN-Workflow |
| Ergebnis | rund 40 % schnellere Inhaltserstellung |
| Logo | optional, nur wenn der Kunde es ausdrücklich freigibt |

Nicht gezeigt: Ansprechpartner, Vertragsvolumen, Laufzeit, interne Dokumente.

## Anschreiben (E-Mail, Betreff: „Referenznennung auf fsh-documentation.com“)

Sehr geehrte/r …,

wir überarbeiten unsere Website und würden unsere Zusammenarbeit gern als Referenz nennen. Vorgesehen ist
eine Zeile auf der Startseite mit Firmenname, Leistung und Ergebnis, zum Beispiel:

„[Firmenname], [Ort]: [Leistung]. Ergebnis: [Ergebnis].“

Bitte kreuzen Sie an, was für Sie in Ordnung ist, und schicken Sie uns die Antwort zurück. Sie können die
Zustimmung jederzeit mit einer kurzen Nachricht widerrufen; wir entfernen die Nennung dann innerhalb von
fünf Werktagen.

[ ] Nennung mit Firmenname und Ort, wie oben formuliert
[ ] Nennung nur der Branche, ohne Firmenname (zum Beispiel „Energieversorger (DE)“)
[ ] Zusätzlich das Firmenlogo (Logodatei bitte mitschicken)
[ ] Keine Nennung

Änderungswünsche am Wortlaut: ______________________________________________

Firma, Name, Funktion: ______________________________________________

Datum, Unterschrift oder Antwort per E-Mail von einer Firmenadresse: ______________________

Mit freundlichen Grüßen
Sascha Falk Heinzmann, Geschäftsführer
FSH-Documentation UG (haftungsbeschränkt), Bäckerstraße 2 D, 14513 Teltow

## Ablage

Antwort als PDF in `website/nachweise/` ablegen (Dateiname `referenz-<kunde>-JJJJ-MM-TT.pdf`). Erst danach den
Namen in `website/inhalt/start.json` eintragen und neu bauen. Widerruf: Nennung entfernen, Antwort in den
Nachweisen belassen, Datum des Widerrufs im Dateinamen ergänzen.
