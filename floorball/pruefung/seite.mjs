// Aufgabe 3: Seitenwechsel nach jedem Drittel
import { oeffne, starteMatch, bullyGewinnen, erzwingeTor, bis, vorspulen } from './tb.mjs';
const { browser, p, fehler } = await oeffne({ pads: 1 });
const ok = (b, t) => console.log((b ? 'OK   ' : 'FEHLT') + ' ' + t);
const stand = () => p.evaluate(() => { const M = window.__fps.Match; return { dr: M.drittel, seite: M.seite, dA: M.A[0].d, dB: M.B[0].d, twA: +M.twA.pos.x.toFixed(1), twB: +M.twB.pos.x.toFixed(1), twAd: M.twA.d, a0x: +M.A[0].pos.x.toFixed(1), b0x: +M.B[0].pos.x.toFixed(1), tore: { ...M.tore }, z: M.zustand }; });
await starteMatch(p);
let s = await stand(); console.log('1. Drittel', JSON.stringify(s));
ok(s.dA === 1 && s.twA < 0 && s.twB > 0, '1. Drittel: A greift nach +X an, TW A steht links');
for (const dr of [2, 3]) {
  await p.evaluate(() => { const M = window.__fps.Match; if (M.zustand === 'bully') M.zustand = 'spiel'; M.uhr = 0.05; });
  await vorspulen(p, 0.2);
  const ban = await p.evaluate(() => window.__fps.Match.el.banner.textContent);
  ok(/Seitenwechsel/.test(ban), 'Banner: ' + ban);
  await vorspulen(p, 4);
  s = await stand(); console.log(dr + '. Drittel', JSON.stringify(s));
  const r = dr === 2 ? -1 : 1;
  ok(s.dr === dr && s.dA === r && s.dB === -r && Math.sign(s.twA) === -r && Math.sign(s.twB) === r && s.twAd === r, `${dr}. Drittel: Seiten richtig (A Richtung ${r})`);
  await bullyGewinnen(p);
  const vor = s.tore;
  await erzwingeTor(p, 'A'); await bis(p, () => window.__fps.Match.zustand === 'tor', null, 30000).catch(() => {});
  let n = await stand(); ok(n.tore.A === vor.A + 1 && n.tore.B === vor.B, `${dr}. Drittel: Tor von A zählt für A ` + JSON.stringify(n.tore));
  await p.evaluate(() => { const M = window.__fps.Match; M.zustand = 'spiel'; M.torInfo = null; M.ball.imTor = 0; for (const q of M.spieler) q.jubel = 0; });
  await erzwingeTor(p, 'B'); await bis(p, () => window.__fps.Match.zustand === 'tor', null, 30000).catch(() => {});
  const n2 = await stand(); ok(n2.tore.B === n.tore.B + 1 && n2.tore.A === n.tore.A, `${dr}. Drittel: Tor von B zählt für B ` + JSON.stringify(n2.tore));
  await p.evaluate(() => { const M = window.__fps.Match; M.zustand = 'spiel'; M.torInfo = null; M.ball.imTor = 0; M.replay = null; for (const q of M.spieler) q.jubel = 0; });
}
// Neues Match beginnt wieder normal
await p.evaluate(() => { const F = window.__fps; F.Match.zumMenue(); });
await starteMatch(p); s = await stand(); ok(s.seite === 1 && s.dA === 1 && s.twA < 0, 'neues Match: wieder Ausgangsseite');
ok(fehler.length === 0, 'Konsole ohne Fehler' + (fehler.length ? ': ' + fehler.slice(0, 5).join(' | ') : ''));
await browser.close();
