// Aufgabe 9: Animationen – Ballannahme, Zweikampf, Gruppenjubel, Torhüter-Auswurf
import { oeffne, starteMatch, bullyGewinnen, vorspulen, erzwingeTor } from './tb.mjs';
const out = process.argv[2] || 'shots';
const { browser, p, fehler } = await oeffne({ pads: 1, breite: 1280, hoehe: 720 });
const ok = (b, t) => console.log((b ? 'OK   ' : 'FEHLT') + ' ' + t);
// Nahaufnahme: Kamera fest auf einen Punkt, kurz mit echtem Rendering
async function nah(pfad, ziel, von) {
  await p.evaluate(([z, v]) => { const F = window.__fps, M = F.Match; M._kam = M.kamera; M.kamera = () => { F.kamera.position.set(v[0], v[1], v[2]); F.kamera.lookAt(z[0], z[1], z[2]); F.kamera.fov = 32; F.kamera.updateProjectionMatrix(); }; F.Bild.ohneRender = false; M.pausiert = true; }, [ziel, von]);
  await p.evaluate(() => new Promise(r => { let i = 0; const f = () => (++i >= 3 ? r() : requestAnimationFrame(f)); requestAnimationFrame(f); }));
  await p.screenshot({ path: pfad });
  await p.evaluate(() => { const F = window.__fps, M = F.Match; M.kamera = M._kam; F.Bild.ohneRender = true; M.pausiert = false; });
}
await starteMatch(p); await bullyGewinnen(p); await vorspulen(p, 0.5);
// 1 Ballannahme
const an = await p.evaluate(() => { const M = window.__fps.Match, a = M.A[0], m = M.A[1]; for (const g of M.B) g.pos.set(12, 0, 8); a.pos.set(-4, 0, 0); m.pos.set(4, 0, 0); a.aktion = null; m.aktion = null; a.vel.set(0, 0, 0); m.vel.set(0, 0, 0); M.gibBall(a); M.starteZuspiel(a, m, false);
  let namen = new Set(), bei = -1; for (let i = 0; i < 90; i++) { M.frame(1 / 30); if (M.ball.besitzer === m && bei < 0) bei = i; if (bei >= 0) namen.add(m.anim.name); if (bei >= 0 && i > bei + 15) break; }
  return { namen: [...namen], tief: true }; });
ok(an.namen.includes('annahme') && an.namen.includes('dribbel'), 'Ballannahme: annahme → dribbel ' + JSON.stringify(an.namen));
// 2 Zweikampf
const zk = await p.evaluate(() => { const M = window.__fps.Match, c = M.B[0], g = M.A[2]; for (const q of M.feld) if (q !== c && q !== g) q.pos.set(q.team === 'A' ? -12 : 12, 0, -8); c.pos.set(0, 0, 3); c.vel.set(0, 0, 0); c.yaw = Math.PI / 2; M.gibBall(c); c.immun = 9; c.aktion = null; g.pos.set(0.15, 0, 3.75); g.vel.set(0, 0, 0); g.aktion = null; M.kon = M.A[4];
  let wmax = 0, wcm = 0; for (let i = 0; i < 20; i++) { g.pos.set(0.15, 0, 3.75); c.pos.set(0, 0, 3); c.vel.set(0, 0, 0); g.vel.set(0, 0, 0); c.kiT = 99; M.frame(1 / 30); wmax = Math.max(wmax, g.kampfW || 0); wcm = Math.max(wcm, c.kampfW || 0); }
  const bk = g.fig.j.becken.getWorldPosition(new g.pos.constructor()); const dx = c.pos.x - g.pos.x, dz = c.pos.z - g.pos.z, l = Math.hypot(dx, dz); const shift = ((bk.x - g.pos.x) * dx + (bk.z - g.pos.z) * dz) / l;
  return { wmax: +wmax.toFixed(2), shift: +shift.toFixed(3), wc: +wcm.toFixed(2) }; });
ok(zk.wmax > 0.8 && zk.wc > 0.8, 'Zweikampf: beide gehen in die Kontaktpose ' + JSON.stringify(zk));
ok(zk.shift > 0.02, 'Zweikampf: Becken des Verteidigers zum Gegner verschoben (' + zk.shift + ' m)');
await nah(out + '/11-zweikampf.png', [0.1, 0.8, 3.3], [3.5, 2.2, 7.5]);
await p.evaluate(() => { const M = window.__fps.Match; M.B[0].immun = 0; M.kon = M.A[0]; });
// 3 Gruppenjubel
await erzwingeTor(p, 'A');
await vorspulen(p, 3.4);
const gj = await p.evaluate(() => { const M = window.__fps.Match, s = M.torInfo && M.torInfo.schuetze; if (!s) return null; const L = M.A.filter(q => q !== s);
  return { z: M.zustand, namen: L.map(q => q.anim.name), dist: L.map(q => +q.pos.distanceTo(s.pos).toFixed(2)), blick: L.map(q => { let d = Math.atan2(s.pos.x - q.pos.x, s.pos.z - q.pos.z) - q.yaw; while (d > Math.PI) d -= 2 * Math.PI; while (d < -Math.PI) d += 2 * Math.PI; return +Math.abs(d).toFixed(2); }), schuetze: s.anim.name, sp: [s.pos.x, s.pos.z] }; });
console.log('     ', JSON.stringify(gj));
ok(gj && gj.namen.filter(n => n === 'gruppe').length >= 3 && gj.schuetze === 'jubel', 'Gruppenjubel: Mitspieler im Kreis (gruppe), Schütze jubelt');
ok(gj && gj.blick.filter((b, i) => gj.namen[i] === 'gruppe').every(b => b < 0.6), 'Gruppenjubel: alle im Kreis schauen zum Schützen');
if (gj) await nah(out + '/12-gruppenjubel.png', [gj.sp[0], 1.0, gj.sp[1]], [gj.sp[0] - 4.5, 2.6, gj.sp[1] + 5]);
await p.evaluate(() => { const M = window.__fps.Match; M.zustand = 'spiel'; M.torInfo = null; M.replay = null; M.ball.imTor = 0; for (const q of M.spieler) q.jubel = 0; M.bullyStart(true); M.zustand = 'spiel'; });
// 4 Torhüter-Auswurf
const aw = await p.evaluate(() => { const M = window.__fps.Match, g = M.twA, b = M.ball; M.uhr = 999; b.besitzer = g; b.letzterTeam = 'A'; g.gk.zustand = 'fangen'; g.gk.halten = 0.05; g.anim.setze('fangen', null, 0.1);
  const r = { zust: [], hoeheMax: 0, los: -1, empf: null, ende: null };
  for (let i = 0; i < 40; i++) { M.frame(1 / 30); r.zust.push(g.gk.zustand[0] + ':' + g.anim.name); if (b.besitzer === g && g.gk.zustand === 'wurf') r.hoeheMax = Math.max(r.hoeheMax, b.p.y); if (r.los < 0 && b.besitzer !== g) { r.los = +(i / 30).toFixed(2); r.empf = b.empf && b.empf.team; } }
  r.ende = g.gk.zustand; r.zust = [...new Set(r.zust)]; return r; });
console.log('     ', JSON.stringify(aw));
ok(aw.zust.some(z => z === 'w:auswurf'), 'Auswurf: Torhüter geht in die Wurfbewegung');
ok(aw.hoeheMax > 1.1, 'Auswurf: Ball in der Wurfhand beim Ausholen (Höhe ' + aw.hoeheMax.toFixed(2) + ' m)');
ok(aw.los >= 0.35 && aw.los < 0.6 && aw.empf === 'A', 'Auswurf: Abwurf nach ' + aw.los + ' s zum eigenen Spieler');
ok(aw.ende === 'grund', 'Auswurf: danach wieder Grundstellung');
// Foto mitten im Ausholen
await p.evaluate(() => { const M = window.__fps.Match, g = M.twA, b = M.ball; b.besitzer = g; g.gk.zustand = 'fangen'; g.gk.halten = 0.01; for (let i = 0; i < 9; i++) M.frame(1 / 30); });
const gp = await p.evaluate(() => [window.__fps.Match.twA.pos.x, window.__fps.Match.twA.pos.z]);
await nah(out + '/13-auswurf.png', [gp[0], 1.0, gp[1]], [gp[0] + 3.5, 2.0, gp[1] + 4.5]);
ok(fehler.length === 0, 'Konsole ohne Fehler' + (fehler.length ? ': ' + fehler.slice(0, 5).join(' | ') : ''));
await browser.close();
