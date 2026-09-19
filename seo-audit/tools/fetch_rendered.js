#!/usr/bin/env node
// Lädt eine Seite wie ein Browser (Chromium über Playwright), wartet auf Netzwerkruhe und speichert
// den gerenderten DOM als HTML, dazu Ladezeiten, Ressourcenzahl und optional einen Screenshot.
// Nötig für Websites, die ihren Inhalt erst per JavaScript aufbauen (Roh-HTML ohne Text).
//
// Vorher einmal je Container: bash seo-audit/tools/browser_setup.sh (Proxy-Zertifikat für Chromium).
// Aufruf: node seo-audit/tools/fetch_rendered.js <url> <ausgabe.html> [screenshot.png]
// Ausgabe: JSON mit Zeiten und Zählern auf stdout, gerendertes HTML in <ausgabe.html>.
const fs = require('fs');
let playwright;
try { playwright = require('playwright'); }
catch (e) { playwright = require(process.env.SEO_AUDIT_NODE_MODULES || '/opt/node22/lib/node_modules') + '/playwright'; }
if (typeof playwright === 'string') playwright = require(playwright);
(async () => {
  const [,, url, outHtml, outPng] = process.argv;
  if (!url || !outHtml) { console.error('Aufruf: fetch_rendered.js <url> <ausgabe.html> [screenshot.png]'); process.exit(2); }
  // Vollständiges Chromium statt Headless-Shell: nur das liest den NSS-Zertifikatspeicher (Proxy-CA).
  let browser;
  try { browser = await playwright.chromium.launch({ channel: 'chromium' }); }
  catch (e) {
    const root = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
    const dir = fs.readdirSync(root).filter(n => /^chromium-\d+$/.test(n)).sort().pop();
    if (!dir) throw e;
    browser = await playwright.chromium.launch({ executablePath: `${root}/${dir}/chrome-linux/chrome` });
  }
  const page = await browser.newPage({ viewport: { width: 1366, height: 900 }, userAgent: 'Mozilla/5.0 (compatible; FSH-SEO-Audit/1.0) Chrome/120' });
  const t0 = Date.now();
  const resp = await page.goto(url, { waitUntil: 'load', timeout: 60000 });
  await page.waitForLoadState('networkidle', { timeout: 30000 }).catch(() => {});
  await page.waitForTimeout(1500);
  const info = await page.evaluate(() => {
    const nav = performance.getEntriesByType('navigation')[0] || {};
    const res = performance.getEntriesByType('resource');
    const bytes = res.reduce((a, r) => a + (r.transferSize || 0), 0);
    const text = document.body ? document.body.innerText : '';
    const q = s => [...document.querySelectorAll(s)];
    return {
      dom_content_loaded_ms: Math.round(nav.domContentLoadedEventEnd || 0),
      load_event_ms: Math.round(nav.loadEventEnd || 0),
      html_transfer_bytes: Math.round(nav.transferSize || 0),
      resources: res.length,
      resources_transfer_bytes: bytes,
      woerter_sichtbar: text.split(/\s+/).filter(Boolean).length,
      h1: q('h1').map(e => e.innerText.trim()).filter(Boolean),
      h2: q('h2').map(e => e.innerText.trim()).filter(Boolean),
      h3: q('h3').length,
      links_gesamt: q('a[href]').length,
      links_mailto_tel: q('a[href^="mailto:"],a[href^="tel:"]').map(a => a.getAttribute('href')),
      links_extern: [...new Set(q('a[href^="http"]').map(a => a.href).filter(h => !h.includes(location.hostname)))].slice(0, 20),
      links_intern_anker: [...new Set(q('a[href]').map(a => a.getAttribute('href')).filter(h => h && (h.startsWith('#') || h.startsWith('/'))))].slice(0, 30),
      bilder: q('img').length,
      bilder_ohne_alt: q('img').filter(i => !(i.getAttribute('alt') || '').trim()).length,
      buttons: q('button').map(b => b.innerText.trim()).filter(Boolean).slice(0, 20),
      titel: document.title,
    };
  });
  info.http_status = resp ? resp.status() : null;
  info.gesamt_ms = Date.now() - t0;
  fs.writeFileSync(outHtml, await page.content(), 'utf8');
  if (outPng) await page.screenshot({ path: outPng, fullPage: true });
  console.log(JSON.stringify(info, null, 2));
  await browser.close();
})().catch(e => { console.error(String(e)); process.exit(1); });
