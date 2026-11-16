// Messstand Spielgefühl: Laufen, Sprint, Schuss, Pass, Torhüterquote je Schwierigkeit (Spielschritte synchron, ohne Rendering)
import { oeffne, starteMatch, bullyGewinnen } from './tb.mjs';
const stufen = (process.argv[2] || 'leicht,mittel,schwer').split(',');
const N = Number(process.argv[3] || 80);
const { browser, p, fehler } = await oeffne({ pads: 1 });
await starteMatch(p); await bullyGewinnen(p); await p.evaluate(() => { window.__fps.Match.uhr = 9999; });
const lauf = await p.evaluate(() => {
  const M = window.__fps.Match, k = M.kon, h = 1 / 60, r = {};
  const pad = window.__pad(0);
  const miss = (sprint, mitBall) => {
    k.pos.set(-10, 0, 0); k.vel.set(0, 0, 0); k.ausdauer = 1; k.aktion = null;
    if (mitBall) M.gibBall(k); else { M.ball.besitzer = null; M.ball.p.set(15, 0.036, 8); M.ball.v.set(0, 0, 0); }
    pad.axes[0] = 1; window.__knopf(0, 7, sprint);
    let t = 0, t90 = 0, vmax = 0; for (let i = 0; i < 180; i++) { (window.__fps.Eingabe.pollen(), M.frame(h)); t += h; const v = Math.hypot(k.vel.x, k.vel.z); if (v > vmax) vmax = v; }
    const ziel = vmax * 0.9; k.pos.set(-10, 0, 0); k.vel.set(0, 0, 0); if (mitBall) M.gibBall(k);
    for (let i = 0; i < 180; i++) { (window.__fps.Eingabe.pollen(), M.frame(h)); if (Math.hypot(k.vel.x, k.vel.z) >= ziel) { t90 = i * h; break; } }
    pad.axes[0] = 0; window.__knopf(0, 7, false);
    return { vmax: +vmax.toFixed(2), kmh: +(vmax * 3.6).toFixed(1), t90: +t90.toFixed(2) };
  };
  r.lauf = miss(false, false); r.sprint = miss(true, false); r.mitBall = miss(false, true); r.sprintBall = miss(true, true);
  // Wendigkeit: Richtungswechsel 180° bei voller Fahrt, Zeit bis wieder 90 % in Gegenrichtung
  k.pos.set(0, 0, 0); k.vel.set(5.5, 0, 0); M.ball.besitzer = null; pad.axes[0] = -1; let tw = 0; for (let i = 0; i < 120; i++) { (window.__fps.Eingabe.pollen(), M.frame(h)); if (k.vel.x < -5.0) { tw = i * h; break; } } pad.axes[0] = 0; r.wende180 = +tw.toFixed(2);
  return r;
});
console.log('Laufen', JSON.stringify(lauf));
const schuss = await p.evaluate(() => {
  const M = window.__fps.Match, k = M.kon, r = [];
  for (const kraft of [0.25, 0.5, 0.75, 1]) {
    M.zustand = "spiel"; M.torInfo = null; M.ball.imTor = 0; for (const q of M.spieler) q.jubel = 0; k.pos.set(5, 0, 0); k.vel.set(0, 0, 0); k.aktion = null; M.gibBall(k); M.ball.p.set(5.3, 0.036, 0);
    M.starteSchuss(k, kraft, 0, false); let v = 0; for (let i = 0; i < 40 && !v; i++) { (window.__fps.Eingabe.pollen(), M.frame(1 / 60)); if (!M.ball.besitzer) v = M.ball.v.length(); }
    r.push({ kraft, ms: +v.toFixed(1), kmh: Math.round(v * 3.6) });
  }
  // Ladezeit bis volle Kraft (Knopf X gehalten)
  k.pos.set(0, 0, 0); k.aktion = null; M.gibBall(k); window.__knopf(0, 2, true); let tl = 0; for (let i = 0; i < 120; i++) { (window.__fps.Eingabe.pollen(), M.frame(1 / 60)); if (k.power >= 0.999) { tl = (i + 1) / 60; break; } } window.__knopf(0, 2, false); for (let i = 0; i < 30; i++) (window.__fps.Eingabe.pollen(), M.frame(1 / 60));
  return { schuss: r, ladezeitVoll: +tl.toFixed(2), daten: k.daten.schuss };
});
console.log('Schuss', JSON.stringify(schuss));
const pass = await p.evaluate(() => {
  const M = window.__fps.Match, k = M.kon, m = M.A.find(x => x !== k), r = [];
  for (const d of [5, 10, 15]) {
    for (const g of M.B) g.pos.set(-15, 0, 9);
    k.pos.set(0, 0, 0); k.vel.set(0, 0, 0); k.aktion = null; m.pos.set(d, 0, 0); m.vel.set(0, 0, 0); M.gibBall(k);
    M.starteZuspiel(k, m, false); let v = 0, t = 0, an = 0;
    for (let i = 0; i < 300; i++) { (window.__fps.Eingabe.pollen(), M.frame(1 / 60)); t += 1 / 60; if (!v && !M.ball.besitzer) { v = M.ball.v.length(); an = t; } if (v && M.ball.besitzer === m) { r.push({ dist: d, ms: +v.toFixed(1), flugzeit: +(t - an).toFixed(2) }); break; } }
    if (r.length && r[r.length - 1].dist !== d) r.push({ dist: d, ms: +v.toFixed(1), flugzeit: 'nicht angenommen' });
  }
  return r;
});
console.log('Pass', JSON.stringify(pass));
// Torhüterserie: Schüsse aus dem Slot, ohne Verteidiger dazwischen
for (const stufe of stufen) {
  const erg = await p.evaluate(([stufe, N]) => {
    const M = window.__fps.Match; M.S = window.__fps.M_STUFEN[stufe];
    const zaehl = (team) => {
      const z = { tor: 0, gehalten: 0, vorbei: 0, abgewehrt: 0 }, L = team === 'A' ? M.A : M.B, tw = team === 'A' ? M.twB : M.twA, d = team === 'A' ? 1 : -1;
      for (let n = 0; n < N; n++) {
        const k = L[n % 5];
        for (const q of M.feld) if (q !== k) { q.pos.set(-d * 12, 0, (q.feld || 0)); q.vel.set(0, 0, 0); q.aktion = null; }
        M.uhr = 999; M.zustand = 'spiel'; M.torInfo = null; M.ball.imTor = 0; for (const q of M.spieler) q.jubel = 0;
        tw.pos.set(d * (window.__fps.Match.twB === tw ? 1 : 1) * (16.5 - 0.7), 0, 0); tw.vel.set(0, 0, 0); Object.assign(tw.gk, { zustand: 'grund', t: 0, reakt: -1, blockZ: 0, halten: 0, liegt: 0 }); tw.yaw = d > 0 ? -Math.PI / 2 : Math.PI / 2;
        const dist = 6 + Math.random() * 6, w = (Math.random() - 0.5) * 1.6;
        k.pos.set(d * (16.5 - Math.cos(w) * dist), 0, Math.sin(w) * dist); k.vel.set(0, 0, 0); k.aktion = null; k.sperre = 0; M.gibBall(k);
        for (let i = 0; i < 20; i++) (window.__fps.Eingabe.pollen(), M.frame(1 / 60));
        M.starteSchuss(k, 0.4 + Math.random() * 0.6, team === 'A' ? (Math.random() < 0.5 ? -0.62 : 0.62) : null, Math.random() < 0.35);
        let aus = 'vorbei', geschossen = false;
        for (let i = 0; i < 150; i++) {
          (window.__fps.Eingabe.pollen(), M.frame(1 / 60)); const b = M.ball;
          if (!geschossen && !b.besitzer) geschossen = true;
          if (M.zustand === 'tor') { aus = 'tor'; break; }
          if (geschossen && b.besitzer === tw) { aus = 'gehalten'; break; }
          if (geschossen && b.letzterTeam === tw.team && b.besitzer !== tw) { aus = 'abgewehrt'; break; }
          if (geschossen && Math.hypot(b.v.x, b.v.z) < 2) break;
        }
        z[aus]++;
        if (M.zustand === 'tor' || M.zustand === 'replay') { M.zustand = 'spiel'; M.torInfo = null; M.replay = null; }
        M.ball.imTor = 0; M.tore = { A: 0, B: 0 };
      }
      const aufsTor = z.tor + z.gehalten + z.abgewehrt; z.quote = aufsTor ? Math.round(100 * (z.gehalten + z.abgewehrt) / aufsTor) : 0; z.trefferAufsTor = Math.round(100 * aufsTor / N);
      return z;
    };
    return { stufe, menschSchiesstAufKI: zaehl('A'), kiSchiesstAufMensch: zaehl('B') };
  }, [stufe, N]);
  console.log('Torhüter', JSON.stringify(erg));
}
console.log(fehler.length ? 'FEHLER: ' + fehler.slice(0, 3).join(' | ') : 'keine JS-Fehler');
await browser.close();
