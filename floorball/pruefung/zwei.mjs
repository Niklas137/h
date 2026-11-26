// Aufgabe 8: Zweiter Spieler am zweiten Controller
import { oeffne, starteMatch, vorspulen, foto, bis, warte } from './tb.mjs';
const out = process.argv[2] || 'shots';
const { browser, p, fehler } = await oeffne({ pads: 2, breite: 1280, hoehe: 720 });
const ok = (b, t) => console.log((b ? 'OK   ' : 'FEHLT') + ' ' + t);
const drueck = async (pad, b, s = 0.12) => { await p.evaluate(([i, b]) => window.__knopf(i, b, true), [pad, b]); await vorspulen(p, s); await p.evaluate(([i, b]) => window.__knopf(i, b, false), [pad, b]); await vorspulen(p, 1 / 30); };
// ohne Menüoption: B bleibt KI
await p.evaluate(() => { window.__fps.M_OPT.zwei = false; });
await starteMatch(p); await vorspulen(p, 0.1);
ok(await p.evaluate(() => !window.__fps.Match.zweiB), 'Option aus: Team B spielt die KI, auch mit zwei Controllern');
await p.evaluate(() => { window.__fps.Match.zumMenue(); window.__fps.M_OPT.zwei = true; });
await starteMatch(p); await vorspulen(p, 0.1);
let s = await p.evaluate(() => { const M = window.__fps.Match; return { zwei: M.zweiB, kon2: M.kon2 === M.B[0], ban: M.el.banner.textContent }; });
ok(s.zwei && s.kon2, '2. Controller steuert Team B ' + JSON.stringify(s));
// Bully: Spieler 2 drückt A nach dem Pfiff
await bis(p, () => window.__fps.Match.bully && window.__fps.Match.bully.gepfiffen, null, 60000).catch(() => {});
await p.evaluate(() => { const M = window.__fps.Match; if (!M.bully.gepfiffen) { M.bully.t = M.bully.pfiff; M.bully.gepfiffen = true; } M.bully.ki = 99; });
await drueck(1, 0);
s = await p.evaluate(() => { const M = window.__fps.Match, b = M.ball; return { z: M.zustand, team: (b.besitzer && b.besitzer.team) || (b.empf && b.empf.team), letzter: b.letzterTeam }; });
ok(s.z === 'spiel' && s.team === 'B' && s.letzter === 'B', 'Spieler 2 gewinnt das Bully (Ball zurück zum Mitspieler wie bei Spieler 1) ' + JSON.stringify(s));
// Laufen mit Stick (Pad 2), Ball bleibt (keine KI-Entscheidung)
const x0 = await p.evaluate(() => window.__fps.Match.kon2.pos.x);
await p.evaluate(() => { window.__pad(1).axes[0] = -1; }); await vorspulen(p, 1.0); await p.evaluate(() => { window.__pad(1).axes[0] = 0; });
s = await p.evaluate((x0) => { const M = window.__fps.Match; return { dx: +(M.kon2.pos.x - x0).toFixed(2), bes: M.ball.besitzer === M.kon2, konA: M.kon.team }; }, x0);
ok(s.dx < -2.5 && s.bes, 'Stick links: Spieler 2 läuft mit Ball nach links ' + JSON.stringify(s));
// Pass mit A (Pad 2): Steuerung springt zum Empfänger
const vorK = await p.evaluate(() => window.__fps.Match.kon2.daten.nummer);
await p.evaluate(() => { for (const g of window.__fps.Match.A) g.pos.z = 9; });
await drueck(1, 0); await vorspulen(p, 1.2);
s = await p.evaluate(() => { const M = window.__fps.Match; return { k2: M.kon2.daten.nummer, team: M.kon2.team, bes: M.ball.besitzer ? M.ball.besitzer.team + M.ball.besitzer.daten.nummer : null }; });
ok(s.k2 !== vorK && s.team === 'B', 'Pass von Spieler 2: Steuerung beim Empfänger ' + vorK + ' → ' + JSON.stringify(s));
// Schuss halten/loslassen
await p.evaluate(() => { const M = window.__fps.Match; M.gibBall(M.kon2); M.kon2.pos.set(-8, 0, 0); M.ball.p.set(-8.3, 0.036, 0); M.kon2.aktion = null; });
await p.evaluate(() => { for (const g of window.__fps.Match.A) g.pos.set(10, 0, 8); });
await p.evaluate(() => window.__knopf(1, 2, true)); await vorspulen(p, 0.5); const kraft = await p.evaluate(() => window.__fps.Match.kon2.power); await p.evaluate(() => window.__knopf(1, 2, false));
let vmax = 0; for (let i = 0; i < 10; i++) { await vorspulen(p, 1 / 30); vmax = Math.max(vmax, await p.evaluate(() => window.__fps.Match.ball.besitzer ? 0 : window.__fps.Match.ball.v.length())); }
ok(kraft > 0.6 && vmax > 20, 'Schuss halten/loslassen: Kraft ' + kraft.toFixed(2) + ', ' + Math.round(vmax * 3.6) + ' km/h');
await p.evaluate(() => { const M = window.__fps.Match; if (M.zustand !== 'spiel') { M.zustand = 'spiel'; M.torInfo = null; M.replay = null; } M.ball.imTor = 0; for (const q of M.spieler) q.jubel = 0; });
// LB: Spielerwechsel bei Team B
const vorW = await p.evaluate(() => { const M = window.__fps.Match; M.gibBall(M.A[0]); M.A[0].immun = 5; return M.kon2.daten.nummer; });
await drueck(1, 4);
const lbDbg = await p.evaluate(() => { const M = window.__fps.Match; return [M.zustand, M.frei ? 'frei:' + M.frei.team + (M.frei.ausf === M.kon2 ? '(kon2)' : '') : '-', M.kon2.jubel, M.ball.besitzer && M.ball.besitzer.team]; }); ok(await p.evaluate((v) => window.__fps.Match.kon2.daten.nummer !== v && window.__fps.Match.kon2.team === 'B', vorW), 'LB wechselt den gesteuerten Spieler von Team B ' + JSON.stringify(lbDbg));
// Stockcheck X durch Spieler 2
const sc = await p.evaluate(() => { const M = window.__fps.Match, c = M.A[0], k = M.kon2; c.immun = 0; M.gibBall(c); c.pos.set(0, 0, 0); k.pos.set(0.6, 0, 0.3); k.stossCd = 0; return true; });
await drueck(1, 2, 0.05);
ok(await p.evaluate(() => window.__fps.Match.kon2.stossT >= 0 || window.__fps.Match.kon2.stossCd > 0), 'X beim Verteidigen: Stockcheck von Spieler 2');
// Steuerkreuz hoch: Linienwechsel B (manuell)
await p.evaluate(() => { window.__fps.M_OPT.linie = 'manuell'; const M = window.__fps.Match; M.ball.besitzer = null; for (const q of M.B) q.aktion = null; });
await drueck(1, 12);
ok(await p.evaluate(() => window.__fps.Match.linie.B === 2), 'Steuerkreuz ↑ an Pad 2: Linienwechsel Team B');
await p.evaluate(() => { const M = window.__fps.Match; M.ball.besitzer = M.kon2; M.ball.p.copy(M.kon2.pos); M.ball.besitzer = null; });
await foto(p, out + '/10-zwei-spieler.png', 4);
ok(await p.evaluate(() => window.__fps.Match.ring2.visible), 'roter Ring markiert Spieler 2');
// Pad 2 trennen: KI übernimmt
await p.evaluate(() => { window.__pads[1] = null; }); await vorspulen(p, 0.1);
s = await p.evaluate(() => { const M = window.__fps.Match; return { zwei: M.zweiB, kon2: M.kon2, ban: M.el.banner.textContent }; });
ok(!s.zwei && s.kon2 === null && /KI/.test(s.ban), 'Controller 2 getrennt: KI übernimmt ' + s.ban);
await vorspulen(p, 3);
ok(fehler.length === 0, 'Konsole ohne Fehler' + (fehler.length ? ': ' + fehler.slice(0, 5).join(' | ') : ''));
await browser.close();
