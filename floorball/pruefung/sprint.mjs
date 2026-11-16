import { oeffne, starteMatch, bullyGewinnen } from './tb.mjs';
const { browser, p } = await oeffne({ pads: 1 });
await starteMatch(p); await bullyGewinnen(p); await p.evaluate(() => { window.__fps.Match.uhr = 9999; });
console.log(await p.evaluate(() => {
  const M = window.__fps.Match, k = M.kon, h = 1 / 60, pad = window.__pad(0), out = [];
  for (const [sprint, mitBall] of [[false, false], [true, false], [false, true], [true, true]]) {
    M.frei = null; M.foulCd = 999; k.pos.set(-10, 0, 0); k.vel.set(0, 0, 0); k.ausdauer = 1; k.aktion = null;
    if (mitBall) M.gibBall(k); else { M.ball.besitzer = null; M.ball.p.set(15, 0.036, 8); M.ball.v.set(0, 0, 0); }
    pad.axes[0] = 1; window.__knopf(0, 7, sprint); let vmax = 0, konWeg = -1, nichtMensch = -1, inA = true;
    for (let i = 0; i < 180; i++) { window.__fps.Eingabe.pollen(); M.frame(h); const v = Math.hypot(k.vel.x, k.vel.z); if (v > vmax) vmax = v; if (konWeg < 0 && M.kon !== k) konWeg = i; if (nichtMensch < 0 && !M.istMensch(k)) nichtMensch = i; if (!M.A.includes(k)) inA = false; }
    pad.axes[0] = 0; window.__knopf(0, 7, false);
    out.push({ sprint, mitBall, kmh: +(vmax * 3.6).toFixed(1), konWeg, nichtMensch, inA, frische: +k.frische.toFixed(2), I: M.I.sprint, z: M.zustand, frei: !!M.frei, bes: M.ball.besitzer && M.ball.besitzer.daten.nummer });
  }
  // Wendigkeit: 180° bei voller Fahrt, Zeit bis wieder 5 m/s in Gegenrichtung
  M.frei = null; M.ball.besitzer = null; M.ball.p.set(15, 0.036, 8); k.pos.set(0, 0, 0); k.vel.set(5.5, 0, 0); k.aktion = null; pad.axes[0] = -1; let tw = -1;
  for (let i = 0; i < 120; i++) { window.__fps.Eingabe.pollen(); M.frame(h); if (k.vel.x < -5.0) { tw = +(i * h).toFixed(2); break; } } pad.axes[0] = 0;
  out.push({ wende180: tw, mensch: M.istMensch(k) });
  return JSON.stringify(out, null, 0);
}));
await browser.close();
