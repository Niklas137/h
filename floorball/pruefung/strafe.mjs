// Aufgabe 6: Strafen
import { oeffne, starteMatch, bullyGewinnen, vorspulen, foto, erzwingeTor, bis } from './tb.mjs';
const out = process.argv[2] || 'shots';
const { browser, p, fehler } = await oeffne({ pads: 1, breite: 1280, hoehe: 720 });
const ok = (b, t) => console.log((b ? 'OK   ' : 'FEHLT') + ' ' + t);
const st = () => p.evaluate(() => { const M = window.__fps.Match; return { a: M.A.length, b: M.B.length, sb: M.strafbank.map(q => ({ t: q.team, ab: q.abgang, x: +q.pos.x.toFixed(2), z: +q.pos.z.toFixed(2), rest: +q.strafe.rest.toFixed(1) })), hud: M.el.strafen.textContent, ban: M.el.banner.textContent, schutz: M.ball.schutz, freiTeam: M.frei && M.frei.team, stat: { fA: M.stat.foulA, fB: M.stat.foulB, mA: M.stat.minA, mB: M.stat.minB }, z: M.zustand }; });
await starteMatch(p); await bullyGewinnen(p);
console.log('Strafdauer bei', await p.evaluate(() => window.__fps.M_OPT.drittel), 'Min.-Drittel:', await p.evaluate(() => window.__fps.Match.strafDauer()), 's');
const vorFrei = await p.evaluate(() => { const M = window.__fps.Match; const f = M.frei ? M.frei.grund || 'Freischlag' : null; M.frei = null; M.foulCd = 0; M.foul(M.B[1], M.A[0], 'Stockschlag', true); return f; }); if (vorFrei) console.log('     (vorher lief ein Freischlag: ' + vorFrei + ')');
await vorspulen(p, 0.05); let s = await st(); console.log(JSON.stringify(s));
ok(s.a === 5 && s.b === 4 && s.sb.length === 1 && /2 Minuten/.test(s.ban) && /Überzahl 5:4/.test(s.hud) && (s.schutz === 'A' || s.freiTeam === 'A'), '2 Minuten: B mit 4, Anzeige Überzahl, Freischlag A');
await vorspulen(p, 5);
s = await st(); ok(!s.sb[0].ab && s.sb[0].z < -10.5 && Math.abs(s.sb[0].x - 0.65) < 0.05, 'Bestrafter sitzt auf der Strafbank ' + JSON.stringify(s.sb[0]));
await p.evaluate(() => { const M = window.__fps.Match; M.zustand = 'spiel'; M.strafbank[0].strafe.rest = 0.4; });
await vorspulen(p, 1.5);
s = await st(); ok(s.b === 5 && s.sb.length === 0 && s.hud === '', 'nach Ablauf zurück, wieder 5:5');
// Überzahltor beendet die Strafe
await vorspulen(p, 2);
await p.evaluate(() => { const M = window.__fps.Match; M.zustand = 'spiel'; M.foulCd = 0; M.frei = null; M.foul(M.B[2], M.A[1], 'Stoßen', true); });
await vorspulen(p, 4); await p.evaluate(() => { const M = window.__fps.Match; M.zustand = 'spiel'; });
await foto(p, out + '/08-strafbank.png', 4);
await erzwingeTor(p, 'A'); await bis(p, () => window.__fps.Match.zustand === 'tor', null, 30000).catch(() => {});
s = await st(); ok(s.sb.length === 1 && s.sb[0].rest === 0, 'Überzahltor: Strafe beendet (Rest 0)');
await p.evaluate(() => { const M = window.__fps.Match; M.zustand = 'spiel'; M.torInfo = null; M.bullyStart(true); });
await vorspulen(p, 0.1);
s = await st(); ok(s.b === 5 && s.sb.length === 0, 'beim Bully wieder vollzählig');
// Stockcheck des Menschen von hinten: wiederholt → Foul
await bullyGewinnen(p);
const f1 = await p.evaluate(() => { const M = window.__fps.Match, c = M.B[0], k = M.kon, R = Math.random; M.foulCd = 0; M.gibBall(c); c.immun = 0; c.yaw = 0; c.pos.set(0, 0, 0); k.pos.set(0, 0, -0.8); Math.random = () => 0.7; let n = 0; for (; n < 8 && M.stat.foulA === 0; n++) M.stossVersuch(k); Math.random = R; return { n, foul: M.stat.foulA, schutz: M.ball.schutz }; });
ok(f1.foul === 1 && f1.schutz === 'B', 'Stockschlag von hinten nach wiederholten Checks: Foul, Freischlag B ' + JSON.stringify(f1));
// Körperfoul: Anrennen gegen den Ballführer
await vorspulen(p, 2);
const f2 = await p.evaluate(() => { const M = window.__fps.Match, c = M.B[0], k = M.kon, R = Math.random; M.zustand = 'spiel'; M.foulCd = 0; M.frei = null; const vor = M.stat.foulA; M.gibBall(c); c.pos.set(3, 0, 0); k.pos.set(2.6, 0, 0); k.vel.set(6.8, 0, 0); Math.random = () => 0.1; M.trennen(); Math.random = R; return { foul: M.stat.foulA - vor, min: M.stat.minA, a: M.A.length }; });
ok(f2.foul === 1 && f2.min === 2 && f2.a === 4, 'Stoßen mit hohem Tempo: 2 Minuten für A ' + JSON.stringify(f2));
// höchstens zwei Bestrafte je Team
const f3 = await p.evaluate(() => { const M = window.__fps.Match; for (let i = 0; i < 3; i++) { M.zustand = 'spiel'; M.foulCd = 0; M.frei = null; M.foul(M.B[0], M.A[0], 'Halten', true); } return { b: M.B.length, sbB: M.strafbank.filter(q => q.team === 'B').length }; });
ok(f3.b === 3 && f3.sbB === 2, 'höchstens zwei Spieler je Team auf der Strafbank ' + JSON.stringify(f3));
s = await st(); console.log('     HUD:', s.hud);
// Linienwechsel in Unterzahl
const lw = await p.evaluate(() => { const M = window.__fps.Match; M.zustand = 'spiel'; M.frei = null; for (const q of M.B) q.aktion = null; M.ball.besitzer = null; const ok = M.linienWechsel('B'); return { ok, b: M.B.length, r: M.reserven.B.length }; });
ok(lw.ok && lw.b === 3 && lw.r === 5, 'Linienwechsel in Unterzahl ' + JSON.stringify(lw));
// Abbau räumt Strafbank-Figuren weg
const weg = await p.evaluate(() => { const F = window.__fps, M = F.Match, figs = M.strafbank.map(q => q.fig.objekt); M.zumMenue(); return figs.every(o => !o.parent); });
ok(weg, 'Matchende entfernt auch die Strafbank-Figuren');
ok(fehler.length === 0, 'Konsole ohne Fehler' + (fehler.length ? ': ' + fehler.slice(0, 5).join(' | ') : ''));
await browser.close();
