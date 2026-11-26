// Grundprüfung nach Regel 3 des Auftrags: Spiel startet, ein Tor fällt, Zeitlupe läuft, Konsole sauber, Penalty-Modus intakt.
import { oeffne, starteMatch, bullyGewinnen, erzwingeTor, bis, warte, fps, zeichenlast, foto } from './tb.mjs';
const out = process.argv[2] || 'shots';
const { browser, p, fehler } = await oeffne({ pads: 1 });
const ok = (b, t) => console.log((b ? 'OK   ' : 'FEHLT') + ' ' + t);
await starteMatch(p);
ok(true, 'Match gestartet: ' + await p.evaluate(() => window.__fps.Match.zustand));
await bullyGewinnen(p);
ok(await p.evaluate(() => window.__fps.Match.zustand === 'spiel'), 'Bully gewonnen, Spiel läuft');
await foto(p, out + '/01-spiel.png'); console.log('     Zeichenlast:', JSON.stringify(await zeichenlast(p)));
await erzwingeTor(p, 'A');
await bis(p, () => window.__fps.Match.zustand === 'tor', null, 30000).catch(() => {});
ok(await p.evaluate(() => window.__fps.Match.tore.A === 1), 'Tor gefallen: ' + JSON.stringify(await p.evaluate(() => window.__fps.Match.tore)));
await bis(p, () => window.__fps.Match.zustand === 'replay', null, 60000).catch(() => {});
ok(await p.evaluate(() => window.__fps.Match.zustand === 'replay'), 'Zeitlupe läuft');
await warte(1200); await foto(p, out + '/02-zeitlupe.png');
await bis(p, () => window.__fps.Match.zustand === 'bully', null, 90000).catch(() => {});
ok(await p.evaluate(() => window.__fps.Match.zustand === 'bully'), 'nach der Zeitlupe wieder Bully');
// Penalty-Modus
await p.evaluate(() => { const F = window.__fps; F.Match.zumMenue(); const L = F.TeamDB.liste; F.Spiel.starteMatch(L[2], L[3], null); });
const zust = new Set(); for (let i = 0; i < 40; i++) { zust.add(await p.evaluate(() => window.__fps.Spiel.zustand)); await warte(500); }
ok(zust.has('anlauf') || zust.has('auswertung'), 'Penalty-Modus läuft: ' + [...zust].join(' → '));
await foto(p, out + '/03-penalty.png');
ok(fehler.length === 0, 'Konsole ohne Fehler' + (fehler.length ? ': ' + fehler.slice(0, 5).join(' | ') : ''));
await browser.close();
