import { oeffne, starteMatch, bullyGewinnen } from './tb.mjs';
const mobil = process.argv[2] === 'mobil';
const { browser, p, fehler } = await oeffne({ pads: 1, mobil, render: true });
await starteMatch(p);
await p.evaluate(() => { window.__fps.Bild.regeln = () => {}; });           // keine automatische Absenkung während der Messung
await p.evaluate(() => new Promise(r => { let i = 0; const f = () => (++i >= 4 ? r() : requestAnimationFrame(f)); requestAnimationFrame(f); }));
const r = await p.evaluate(() => {
  const F = window.__fps, M = F.Match, info = F.renderer.info.render, tri = (o) => { let n = 0; o.traverse(m => { if (m.isMesh && m.visible) { const g = m.geometry, c = g.index ? g.index.count : g.attributes.position.count; n += (m.isInstancedMesh ? m.count : 1) * c / 3; } }); return n; };
  const fig = M.spieler.map(s => tri(s.fig.objekt)), figMeshes = M.spieler.reduce((a, s) => { let n = 0; s.fig.objekt.traverse(m => { if (m.isMesh && m.visible) n++; }); return a + n; }, 0);
  let schattenWerfer = 0; F.szene.traverse(m => { if (m.isMesh && m.visible && m.castShadow) schattenWerfer++; });
  return { quali: F.Config.grafik.qualitaet, spiegel: F.Bild.spiegel, effekte: F.Bild.effekte, pr: F.renderer.getPixelRatio(), aufrufe: info.calls, dreiecke: info.triangles,
    figurenDreieckeJe: Math.round(fig[0]), figurenDreieckeGesamt: Math.round(fig.reduce((a, b) => a + b, 0)), figurenMeshes: figMeshes, schattenWerfer,
    zuschauer: F.halle.zuschauer.mesh.count, halleDreiecke: Math.round(tri(F.halle.gruppe || F.szene) - fig.reduce((a, b) => a + b, 0)) };
});
console.log(mobil ? 'MOBIL' : 'DESKTOP', JSON.stringify(r)); console.log(fehler.join('\n') || 'keine JS-Fehler'); await browser.close();
