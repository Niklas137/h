// Aufgabe 5: Linienwechsel
import { oeffne, starteMatch, bullyGewinnen, vorspulen, knopf, foto, erzwingeTor, bis } from './tb.mjs';
const out = process.argv[2] || 'shots';
const { browser, p, fehler } = await oeffne({ pads: 1, breite: 1280, hoehe: 720 });
const ok = (b, t) => console.log((b ? 'OK   ' : 'FEHLT') + ' ' + t);
const nrs = (t) => p.evaluate((t) => window.__fps.Match[t].map(q => q.daten.nummer).join(','), t);
await p.evaluate(() => { window.__fps.M_OPT.linie = 'manuell'; });
await starteMatch(p); await bullyGewinnen(p);
const vorA = await nrs('A');
// Ball an A[2] geben, dann Knopf Steuerkreuz hoch
await p.evaluate(() => { const M = window.__fps.Match; for (const q of M.A) q.aktion = null; M.gibBall(M.A[2]); M.kon = M.A[2]; });
const halter = await p.evaluate(() => window.__fps.Match.A[2].daten.nummer);
await knopf(p, 0, 12);
await vorspulen(p, 0.1);
const nachA = await nrs('A');
const st = await p.evaluate(() => { const M = window.__fps.Match; return { linie: M.linie.A, ban: M.el.banner.textContent, abg: M.reserven.A.filter(q => q.abgang).length, feldBank: M.feld.some(q => q.bank), kon: M.kon.daten.nummer, konBank: M.kon.bank }; });
console.log('A vorher', vorA, '| nachher', nachA, JSON.stringify(st));
ok(vorA !== nachA && st.linie === 2 && /Linienwechsel/.test(st.ban), 'Knopf Steuerkreuz ↑: Linie 2 kommt');
ok(nachA.split(',').includes(String(halter)) && nachA.split(',').filter(n => vorA.split(',').includes(n)).length === 1, 'Ballführer bleibt auf dem Feld, vier wechseln');
ok(st.abg === 4 && !st.feldBank && !st.konBank, 'vier Spieler laufen zur Bank, Feld ohne Bankspieler');
await foto(p, out + '/07-wechsel-unterwegs.png', 4);
await vorspulen(p, 6);
const bank = await p.evaluate(() => { const M = window.__fps.Match; return M.reserven.A.map(q => ({ ab: q.abgang, z: +q.pos.z.toFixed(2), a: q.anim.name })); });
ok(bank.every(q => !q.ab && q.z < -10.5 && q.a === 'sitzen'), 'alle Ausgewechselten sitzen auf der Bank ' + JSON.stringify(bank.map(q => q.a + '@' + q.z)));
// Doppelter Wechsel gleich danach: neue Linie 1 mit frischen Leuten
const zweiter = await p.evaluate(() => { const M = window.__fps.Match; M.ball.besitzer = null; M.ball.empf = null; for (const q of M.A) q.aktion = null; return M.linienWechsel('A'); });
ok(zweiter === true && (await p.evaluate(() => window.__fps.Match.linie.A)) === 1, 'Rückwechsel möglich, sobald die alte Linie sitzt');
// Tastatur L
await vorspulen(p, 6);
await p.keyboard.down('KeyL'); await vorspulen(p, 0.1); await p.keyboard.up('KeyL');
const dbg = await p.evaluate(() => { const M = window.__fps.Match; return [M.zustand, !!M.frei, M.reserven.A.filter(q => q.abgang).length, M.stat.foulA + '/' + M.stat.foulB, JSON.stringify(M.tore)]; }); ok((await p.evaluate(() => window.__fps.Match.linie.A)) === 2, 'Taste L wechselt ' + dbg);
// Automatik Team B
const vorB = await nrs('B');
await p.evaluate(() => { const M = window.__fps.Match; for (const q of M.B) q.frische = 0.3; M.linieT.B = 40; M.ball.besitzer = null; M.ball.p.set(0, 0.036, 0); M.ball.v.set(0, 0, 0); });
await vorspulen(p, 1.2);
const nachB = await nrs('B');
ok(vorB !== nachB, 'KI-Team B wechselt automatisch bei müder Linie: ' + vorB + ' → ' + nachB);
const fr = await p.evaluate(() => { const M = window.__fps.Match; return { feld: +M.frischeVon('A').toFixed(2), bank: +(M.reserven.A.reduce((a, q) => a + q.frische, 0) / 5).toFixed(2) }; });
console.log('     Frische', JSON.stringify(fr));
// Beim Bully nach Tor wechselt B (Automatik), A nicht (manuell)
await vorspulen(p, 6);
await p.evaluate(() => { const M = window.__fps.Match; M.linieT.B = 30; for (const q of M.B) q.frische = 0.5; M.linieT.A = 30; for (const q of M.A) q.frische = 0.5; });
const vA = await nrs('A'), vB = await nrs('B');
await erzwingeTor(p, 'A'); await bis(p, () => window.__fps.Match.zustand === 'tor', null, 30000).catch(() => {});
await p.evaluate(() => { const M = window.__fps.Match; M.zustand = 'spiel'; M.torInfo = null; M.bullyStart(true); });
ok((await nrs('B')) !== vB && (await nrs('A')) === vA, 'beim Bully: B wechselt automatisch, A (manuell) nicht');
const pos = await p.evaluate(() => { const M = window.__fps.Match; return M.B.every(q => Math.abs(q.pos.z) < 9 && !q.bank) && M.reserven.B.every(q => q.pos.z < -10.5); });
ok(pos, 'nach Bully-Wechsel: alle Feldspieler aufgestellt, Bank sitzt');
ok(fehler.length === 0, 'Konsole ohne Fehler' + (fehler.length ? ': ' + fehler.slice(0, 5).join(' | ') : ''));
await browser.close();
