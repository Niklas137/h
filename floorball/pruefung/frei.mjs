// Aufgabe 7: Freischlag mit Abstand
import { oeffne, starteMatch, bullyGewinnen, vorspulen, foto, knopf } from './tb.mjs';
const out = process.argv[2] || 'shots';
const { browser, p, fehler } = await oeffne({ pads: 1, breite: 1280, hoehe: 720 });
const ok = (b, t) => console.log((b ? 'OK   ' : 'FEHLT') + ' ' + t);
const st = () => p.evaluate(() => { const M = window.__fps.Match, b = M.ball, F = M.frei;
  const minAbst = F ? Math.min(...(F.team === 'A' ? M.B : M.A).map(g => Math.hypot(g.pos.x - b.p.x, g.pos.z - b.p.z))) : null;
  return { frei: !!F, team: F && F.team, hatte: F && F.hatte, ausfKon: F && F.ausf === M.kon, uhr: +M.uhr.toFixed(2), ball: [+b.p.x.toFixed(2), +b.p.z.toFixed(2)], bes: b.besitzer ? b.besitzer.team + b.besitzer.daten.nummer : null, minAbst: minAbst && +minAbst.toFixed(2), ausfPos: F && [+F.ausf.pos.x.toFixed(2), +F.ausf.pos.z.toFixed(2)], ring: M.freiRing.visible, ban: M.el.banner.textContent }; });
await starteMatch(p); await bullyGewinnen(p);
// B foult A in der Mitte
await p.evaluate(() => { const M = window.__fps.Match; M.foulCd = 0; for (const g of M.B) g.pos.set(1 + Math.random(), 0, Math.random() * 2 - 1); M.foul(M.B[0], M.A[1], 'Halten', false); });
let s0 = await st(); await vorspulen(p, 0.2); let s = await st(); console.log(JSON.stringify(s));
ok(s.frei && s.team === 'A' && s.ausfKon && /Freischlag/.test(s.ban), 'Foul: Freischlag A, Ausführender ist der gesteuerte Spieler');
ok(s.minAbst >= 2.99, 'Gegner sofort auf 3 m Abstand: ' + s.minAbst);
await vorspulen(p, 3); s = await st(); console.log(JSON.stringify(s));
ok(s.hatte && s.bes && s.bes.startsWith('A') && s.uhr === s0.uhr, 'Ausführender holt den Ball, Uhr steht');
// Mit Ball nicht dribbeln: Stick drücken, Position bleibt
await p.evaluate(() => { window.__pad(0).axes[0] = 1; });
await vorspulen(p, 1); const s2 = await st(); await p.evaluate(() => { window.__pad(0).axes[0] = 0; });
ok(Math.hypot(s2.ausfPos[0] - s.ausfPos[0], s2.ausfPos[1] - s.ausfPos[1]) < 0.3 && s2.frei, 'mit Ball keine Bewegung (nur schlagen) ' + JSON.stringify([s.ausfPos, s2.ausfPos]));
ok(s2.ring && s2.minAbst >= 2.99, '3-m-Kreis sichtbar, Abstand gehalten');
await foto(p, out + '/09-freischlag.png', 4);
// A drücken: Pass → Freischlag vorbei, Uhr läuft
await p.evaluate(() => { window.__knopf(0, 0, true); }); await vorspulen(p, 0.15); await p.evaluate(() => { window.__knopf(0, 0, false); }); await vorspulen(p, 1);
s = await st(); ok(!s.frei && s.uhr < s0.uhr, 'Pass gespielt: Freischlag beendet, Uhr läuft ' + s.uhr);
// Freischlag B: KI führt aus, Mensch versucht hinzulaufen
await p.evaluate(() => { const M = window.__fps.Match; M.foulCd = 0; M.frei = null; M.foul(M.A[2], M.B[1], 'Stockschlag', false); });
let minA = 9, kiZeit = null; for (let i = 0; i < 40; i++) { await p.evaluate(() => { const M = window.__fps.Match, k = M.kon, b = M.ball; const dx = b.p.x - k.pos.x, dz = b.p.z - k.pos.z, l = Math.hypot(dx, dz) || 1; window.__pad(0).axes[0] = dx / l; window.__pad(0).axes[1] = -dz / l; }); await vorspulen(p, 0.1); const q = await st(); if (q.frei && q.minAbst !== null) minA = Math.min(minA, q.minAbst); if (!q.frei) { kiZeit = i * 0.1; break; } }
await p.evaluate(() => { window.__pad(0).axes[0] = 0; window.__pad(0).axes[1] = 0; });
ok(minA >= 2.99, 'Mensch kommt nicht näher als 3 m: ' + minA.toFixed(2));
ok(kiZeit !== null && kiZeit < 4, 'KI führt den Freischlag aus nach ' + kiZeit + ' s');
// Einschlag nach Ausball
await p.evaluate(() => { const M = window.__fps.Match; M.frei = null; M.ball.besitzer = null; M.ball.letzterTeam = 'B'; M.ausball(); });
s = await st(); ok(s.frei && s.team === 'A' && /Einschlag/.test(s.ban), 'Ausball: Einschlag als Freischlag mit Abstand');
// Lage am Tor
const lage = await p.evaluate(() => { const M = window.__fps.Match, r = []; for (const [x, z] of [[15, 0.5], [18.0, 1.0], [-14.5, -2], [5, 3]]) { M.frei = null; M.freischlag('A', x, z, null); const b = M.ball.p; r.push([x, z, +b.x.toFixed(2), +b.z.toFixed(2), +Math.min(Math.hypot(b.x - 16.5, b.z), Math.hypot(b.x + 16.5, b.z)).toFixed(2)]); } M.frei = null; M.ball.schutz = null; return r; });
console.log('     Lage [x,z → bx,bz, Abstand Tor]:', JSON.stringify(lage));
ok(lage.every(l => l[4] >= 5.49) && lage[3][2] === 5 && lage[3][3] === 3, 'nie näher als 5,5 m am Tormittelpunkt, in der Mitte unverändert');
// Zeitablauf beim Menschen: nach 6 s automatischer Pass
await p.evaluate(() => { const M = window.__fps.Match; M.foulCd = 0; M.foul(M.B[0], M.A[0], 'Halten', false); });
let auto = null; for (let i = 0; i < 12; i++) { await vorspulen(p, 1); if (!(await st()).frei) { auto = i + 1; break; } }
ok(auto !== null && auto >= 6 && auto <= 10, 'Mensch wartet: automatische Ausführung nach ' + auto + ' s');
ok(fehler.length === 0, 'Konsole ohne Fehler' + (fehler.length ? ': ' + fehler.slice(0, 5).join(' | ') : ''));
await browser.close();
