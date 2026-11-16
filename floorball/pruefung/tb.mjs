// Prüfgerüst für floorball-match.html: Browser, emulierte Controller, Hilfen für Match und Penalty-Modus.
// Pfade über Umgebungsvariablen: PW_MODUL (playwright-core), CHROMIUM (Browser), FB_URL (Spielseite)
const { chromium } = await import(process.env.PW_MODUL || 'playwright-core');
export const URL = process.env.FB_URL || 'http://localhost:8790/floorball-match.html';
const PAD_INIT = () => {
  window.__pads = [null, null, null, null];
  const mk = (i) => ({ connected: true, id: 'Testpad ' + i, index: i, mapping: 'standard', timestamp: 0,
    buttons: Array.from({ length: 17 }, () => ({ pressed: false, touched: false, value: 0 })), axes: [0, 0, 0, 0] });
  window.__pad = (i = 0) => { if (!window.__pads[i]) window.__pads[i] = mk(i); return window.__pads[i]; };
  window.__knopf = (i, b, an) => { const g = window.__pad(i); g.buttons[b].pressed = an; g.buttons[b].value = an ? 1 : 0; };
  window.__achse = (i, a, v) => { window.__pad(i).axes[a] = v; };
  Object.defineProperty(Navigator.prototype, 'getGamepads', { configurable: true, value: () => window.__pads });
};
export async function oeffne({ mobil = false, pads = 0, breite = 960, hoehe = 540, url = URL, render = false } = {}) {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || undefined, args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'] });
  const ctx = await browser.newContext(mobil ? { viewport: { width: 844, height: 390 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 } : { viewport: { width: breite, height: hoehe } });
  const p = await ctx.newPage();
  const fehler = [];
  p.on('pageerror', e => fehler.push('pageerror: ' + e.message));
  p.on('console', m => { if (m.type() === 'error' && !/favicon|404/.test(m.text())) fehler.push('console: ' + m.text()); });
  await p.addInitScript(PAD_INIT);
  await p.goto(url);
  await p.waitForFunction(() => !!window.__fps && !document.getElementById('laden'), null, { timeout: 120000 });
  for (let i = 0; i < pads; i++) await p.evaluate((i) => window.__pad(i), i);
  // Prüfmodus: ohne Grafiklast simulieren; die Zeichenfläche wird nur geleert, damit der Browser weiter Animationsframes liefert
  await p.evaluate(() => { const F = window.__fps, B = F.Bild, z = B.zeichne.bind(B); B.zeichne = (dt) => { z(dt); if (B.ohneRender) { F.renderer.setRenderTarget(null); F.renderer.clear(); } }; });
  if (!render) await p.evaluate(() => { window.__fps.Bild.ohneRender = true; });
  return { browser, p, fehler };
}
export const warte = (ms) => new Promise(r => setTimeout(r, ms));
/** wartet, bis fn im Browser wahr ist (Spielzeit läuft je nach Software-Rendering langsam) */
export async function bis(p, fn, arg, ms = 60000) { return p.waitForFunction(fn, arg, { timeout: ms, polling: 100 }); }
export async function knopf(p, pad, b, ms = 120) { await p.evaluate(([i, b]) => window.__knopf(i, b, true), [pad, b]); await warte(ms); await p.evaluate(([i, b]) => window.__knopf(i, b, false), [pad, b]); }
export async function starteMatch(p, a = 0, b = 1) {
  await p.evaluate(([a, b]) => { const F = window.__fps, L = F.TeamDB.liste; F.Match.starte(L[a], L[b]); }, [a, b]);
  await bis(p, () => window.__fps.Match.aktiv && ['bully', 'spiel'].includes(window.__fps.Match.zustand), null, 60000);
}
/** Bully auflösen: A am Controller 0 drücken, bis gespielt wird */
export async function bullyGewinnen(p) {
  await bis(p, () => window.__fps.Match.zustand !== 'bully' || (window.__fps.Match.bully && window.__fps.Match.bully.gepfiffen), null, 60000);
  if (await p.evaluate(() => window.__fps.Match.zustand === 'bully')) await knopf(p, 0, 0);
  await bis(p, () => window.__fps.Match.zustand === 'spiel', null, 60000);
}
/** echtes Tor für Team A: Ball zum Stürmer vor dem Tor, Torhüter liegt am anderen Pfosten, Schuss */
export async function erzwingeTor(p, team = 'A') {
  // bis zu vier Versuche: Schuss aus dem Slot, Torhüter liegt am anderen Pfosten (Abschluss ist zufallsbehaftet, ca. 80 % Treffer)
  for (let versuch = 0; versuch < 4; versuch++) {
    const tor = await p.evaluate(([team, versuch]) => {
      const M = window.__fps.Match, L = team === 'A' ? M.A : M.B, tw = team === 'A' ? M.twB : M.twA;
      if (versuch > 0) { if (M.zustand === 'tor') return true; M.zustand = 'spiel'; M.frei = null; M.ball.imTor = 0; }
      const k = L.find(x => !x.bank) || L[0], d = k.d;
      k.pos.set(d * 11.5, 0, 0.3); k.vel.set(0, 0, 0); k.aktion = null; k.sperre = 0; M.gibBall(k); M.ball.p.set(d * 11.9, 0.036, 0.4);
      for (const g of M.gegner(k)) if (Math.abs(g.pos.x - d * 13) < 3 && Math.abs(g.pos.z) < 3) g.pos.z = 7;
      tw.pos.z = -0.75; tw.gk.zustand = 'liegt'; tw.gk.liegt = 4; tw.gk.blockZ = -0.75;
      M.starteSchuss(k, 0.85, 0.55, false);
      for (let i = 0; i < 45 && M.zustand !== 'tor'; i++) M.frame(1 / 30);
      return M.zustand === 'tor';
    }, [team, versuch]);
    if (tor) return true;
  }
  return false;
}
export async function fps(p, ms = 3000) {
  return p.evaluate((ms) => new Promise(res => { let n = 0; const t0 = performance.now(); const f = () => { n++; if (performance.now() - t0 < ms) requestAnimationFrame(f); else res(Math.round(n * 1000 / (performance.now() - t0) * 10) / 10); }; requestAnimationFrame(f); }), ms);
}
export async function zeichenlast(p) {
  return p.evaluate(() => { const r = window.__fps.renderer.info.render; return { calls: r.calls, dreiecke: r.triangles }; });
}

/** Foto mit kurz eingeschaltetem Rendering (Software-WebGL ist langsam) */
export async function foto(p, pfad, frames = 3) {
  const war = await p.evaluate(() => { const B = window.__fps.Bild, w = B.ohneRender; B.ohneRender = false; window.__fps.Match.pausiert = window.__fps.Match.aktiv ? true : window.__fps.Match.pausiert; return w; });
  await p.evaluate((n) => new Promise(r => { let i = 0; const f = () => (++i >= n ? r() : requestAnimationFrame(f)); requestAnimationFrame(f); }), frames);
  await p.screenshot({ path: pfad });
  await p.evaluate((w) => { window.__fps.Bild.ohneRender = w; if (window.__fps.Match.aktiv && !window.__fps.Match.ueberlagerung) window.__fps.Match.pausiert = false; }, war);
}
/** Spielzeit vorspulen: Match.frame mit festen Schritten, ohne auf den Bildtakt zu warten */
export async function vorspulen(p, sek, h = 1 / 30) {
  return p.evaluate(([sek, h]) => { const M = window.__fps.Match; const n = Math.round(sek / h); for (let i = 0; i < n && M.aktiv; i++) M.frame(h); return { z: M.zustand, uhr: M.uhr, tore: M.tore }; }, [sek, h]);
}
