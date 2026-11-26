// Gemeinsame Hilfen für die Prüfskripte (Playwright, Chromium mit Software-Rendering)
const { chromium } = require('playwright');
const DATEI = 'file://' + require('path').resolve(__dirname, '..', 'index.html');
async function start(opt = {}) {
  const b = await chromium.launch({ args: ['--enable-unsafe-swiftshader', '--use-angle=swiftshader', '--ignore-gpu-blocklist'] });
  const ctx = await b.newContext(Object.assign({ viewport: { width: opt.w || 1280, height: opt.h || 720 }, deviceScaleFactor: opt.dsf || 1 }, opt.ctx || {}));
  const p = await ctx.newPage();
  const logs = [];
  p.on('console', m => { if (['error', 'warning'].includes(m.type()) && !/GPU stall due to ReadPixels/.test(m.text())) logs.push(m.type() + ': ' + m.text().slice(0, 400)); });
  p.on('pageerror', e => logs.push('PAGEERROR: ' + e.message + ' | ' + String(e.stack).split('\n').slice(0, 3).join(' | ')));
  // Einstellungen vor dem Laden setzen: Qualität, Zuschauerdichte, Tutorial aus; Grafik zunächst abgeschaltet (Simulation läuft trotzdem)
  await p.addInitScript((o) => { try { if (!localStorage.getItem('__test_init')) { localStorage.setItem('__test_init', '1'); localStorage.setItem('fps_config_v1', JSON.stringify({ grafik: { qualitaet: o.quali || 'hoch', zuschauer: o.fans === undefined ? 1 : o.fans, schatten: true, spiegelung: true, boden: o.boden || 'parkett', fps: false } })); localStorage.setItem('fps_einst_v1', JSON.stringify(Object.assign({ tutorial: true }, o.einst || {}))); } } catch (e) {} }, opt);
  await p.goto(DATEI);
  await p.waitForFunction(() => window.__fps, null, { timeout: 200000 });
  // Ton in den Prüfungen aus: die Simulation wird teils im Zeitraffer geschaltet, das würde tausende Klänge auf einmal auslösen
  await p.evaluate((o) => { const F = window.__fps; F.Bild.regeln = () => {}; F.Bild.ohneRender = !o.mitRender; if (!o.mitTon) F.Ton.init = () => {}; }, opt);
  return { b, p, logs };
}
/** Ein Bild sauber zeichnen lassen (GPU synchronisieren) und speichern. */
async function foto(p, name, opt = {}) {
  await p.evaluate(async () => { const F = window.__fps, gl = F.renderer.getContext(), px = new Uint8Array(4); const alt = F.Bild.ohneRender; F.Bild.ohneRender = false;
    for (let i = 0; i < 2; i++) { await new Promise(r => requestAnimationFrame(r)); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); }
    F.Bild.ohneRender = alt; });
  await p.screenshot(Object.assign({ path: name, timeout: 120000 }, opt));
}
/** Freie Kamera für Nahaufnahmen (Spiel pausiert). */
async function blick(p, pos, ziel, fov = 50, menueWeg = true) {
  await p.evaluate(([pos, ziel, fov, menueWeg]) => { const F = window.__fps; F.Spiel.pausiert = true; if (!F.Kam._alt) { F.Kam._alt = F.Kam.update; } F.Kam.update = () => {}; const k = F.kamera; k.position.set(...pos); k.lookAt(...ziel); k.fov = fov; k.updateProjectionMatrix(); if (menueWeg) document.getElementById('menues').style.display = 'none'; }, [pos, ziel, fov, menueWeg]);
}
module.exports = { start, foto, blick, DATEI };
