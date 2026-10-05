/* Browser-Abnahme mit ausschliesslich erzeugten Testdaten. Keine produktiven Konten. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const crypto = require('node:crypto');
const { spawn, spawnSync } = require('node:child_process');
const { chromium } = require('playwright');

const root = fs.mkdtempSync(path.join(os.tmpdir(), 'dp-browser-'));
const out = path.resolve('test-artifacts');
fs.mkdirSync(out, { recursive: true });
const python = process.env.DP_TEST_PYTHON || '.venv/bin/python';
const env = { ...process.env, DP_DATEN: path.join(root, 'daten'), DP_OUTPUT: path.join(root, 'output'),
  DP_DEV: '1', DP_VERIFIZIERUNG: 'code', DP_SMTP_HOST: '', PYTHONUNBUFFERED: '1', DP_TEST_ROOT: root };
const passwort = crypto.randomBytes(24).toString('base64') + 'A!';
const seed = spawnSync(python, ['-c', `
import io,json,os,sys
from pathlib import Path
from docx import Document
from reportlab.pdfgen import canvas
from app import auth,db
db.init_db()
with db.transaktion() as con:
    _,otp=auth.benutzer_anlegen(con,'admin@example.invalid','Browser Admin','admin')
    u,_=auth.benutzer_anlegen(con,'mitglied@example.invalid','Browser Mitglied','mitglied')
    auth.konto_abschliessen(con,u['id'],'Browser Mitglied',json.load(sys.stdin)['passwort'])
root=Path(os.environ['DP_TEST_ROOT'])
d=Document(); d.add_heading('Wartung',1); d.add_paragraph('Die Installation erfolgt durch die Zielgruppe der Fachkraefte.')
d.add_table(rows=1,cols=1).cell(0,0).text='Sicherheitshinweise und technische Daten'
kurz='Vor dem Start muss der Bediener alle vorhandenen Schutzeinrichtungen kontrollieren.'
d.add_paragraph(' '.join([kurz]*3))
d.save(root/'Testanleitung.docx')
lang=' '.join(['Pruefwort']*26)+'.'
d=Document(); d.add_heading('Satzlaenge',1); d.add_paragraph(lang+' '+lang); d.save(root/'Langsaetze.docx')
d=Document(); d.add_heading('Sicherheitshinweise',1); d.add_paragraph('Noch zu ergänzen.')
d.save(root/'LeeresKapitel.docx')
d=Document(); d.add_paragraph('Sicherheitshinweise fehlen vollständig.'); d.save(root/'FehlenderInhalt.docx')
c=canvas.Canvas(str(root/'Zeilenumbruch.pdf')); c.setFont('Helvetica',11)
c.drawString(72,750,' '.join(['Wort']*13)); c.drawString(72,736,' '.join(['Wort']*14)+'.'); c.save()
(root/'kaputt.docx').write_bytes(b'kein Word')
c=canvas.Canvas(str(root/'gemischt.pdf')); c.drawString(72,750,'Installation und Wartung'); c.showPage(); c.rect(72,72,100,100); c.showPage(); c.save()
print(json.dumps({'otp':otp}))
`], { env, input: JSON.stringify({ passwort }), encoding: 'utf8' });
assert.equal(seed.status, 0, 'Testdaten konnten nicht angelegt werden');
const otp = JSON.parse(seed.stdout).otp; // Bleibt nur im Speicher und wird niemals protokolliert.
const port = 18766;
const url = `http://127.0.0.1:${port}`;
const server = spawn(python, ['-m', 'app.start', '--ohne-browser', '--port', String(port)], { env, stdio: 'ignore' });
let browser, page;
const errors = [], checks = [];
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
async function visible(sel) { await page.locator(sel).waitFor({ state: 'visible', timeout: 10000 }); }
async function response(route, action) {
  const waiting = page.waitForResponse(r => r.url().endsWith(route) && r.request().method() !== 'GET');
  await action(); const r = await waiting; assert.equal(r.status(), 200, route); return r.json();
}
async function login(email) {
  await page.locator('#login-email').fill(email);
  await page.locator('#login-pwd').fill(passwort);
  await page.locator('#login-btn').click();
  await visible('#main');
}
async function checkFile(file) {
  await page.locator('#file').setInputFiles(path.join(root, file));
  await page.locator('#start-check').click();
  await visible('#result');
}

(async () => {
  for (let i = 0; i < 100; i++) {
    try { if ((await fetch(url + '/api/status')).ok) break; } catch (_) {}
    if (server.exitCode !== null) throw new Error('Testserver beendet');
    await sleep(100);
  }
  browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1365, height: 900 }, reducedMotion: 'reduce' });
  page = await context.newPage();
  page.on('pageerror', err => errors.push(err.message));
  await page.goto(url);
  await visible('#f-login');
  await page.locator('#gate [data-go=recht]').first().click(); await visible('#modal-recht');
  assert.match(await page.locator('#recht-inhalt').innerText(), /Datenschutzerklärung/);
  await page.locator('#recht-close').click();
  checks.push('Rechtliche Informationen vor der Anmeldung erreichbar');
  await page.locator('#to-erst').click();
  await page.locator('#erst-email').fill('admin@example.invalid');
  await page.locator('#erst-otp').fill(otp);
  const start = await response('/api/erstanmeldung/start', () => page.locator('#f-step1 button[type=submit]').click());
  await visible('#f-step2');
  await page.locator('#erst-code').fill(start.code);
  await page.locator('#f-step2 button[type=submit]').click();
  await visible('#f-step3');
  await page.locator('#erst-name').fill('Browser Admin');
  await page.locator('#erst-pwd').fill(passwort);
  await page.locator('#erst-pwd2').fill(passwort);
  await page.locator('#finish').click();
  await visible('#main');
  checks.push('Erstanmeldung mit Einmal-Passwort, Code und eigenem Passwort');

  await page.locator('#seg-run-lang2 button[data-v=en]').click();
  await checkFile('Testanleitung.docx');
  const adminResult = await (await context.request.get(url + '/api/pruefungen')).json();
  const pid = adminResult.pruefungen[0].id;
  assert.equal(await page.locator('#pdf-pruef a').count(), 2);
  assert.equal(await page.locator('#pdf-fach a').count(), 2);
  const result = await (await context.request.get(url + '/api/pruefung/' + pid)).json();
  assert.equal(result.funde.some(f => f.ID === 'TXT-001'), false,
    'Drei kurze Saetze im Absatz duerfen keinen Satzlaengenhinweis ausloesen');
  for (const p of result.pdfs) {
    const pdf = await context.request.get(url + p.url);
    assert.equal(pdf.status(), 200); assert.equal((await pdf.body()).subarray(0, 5).toString(), '%PDF-');
  }
  const zip = await context.request.get(url + result.zip);
  assert.equal(zip.status(), 200); assert.equal((await zip.body()).subarray(0, 2).toString(), 'PK');
  await response(`/api/pruefung/${pid}/ablegen`, () => page.locator('#act-store').click());
  checks.push('Word-Pruefung, vier PDFs, ZIP und Ablage');

  await checkFile('Langsaetze.docx');
  const langListe = await (await context.request.get(url + '/api/pruefungen')).json();
  const langId = langListe.pruefungen.find(p => p.dateiname === 'Langsaetze.docx').id;
  const langErgebnis = await (await context.request.get(url + '/api/pruefung/' + langId)).json();
  const langFunde = langErgebnis.funde.filter(f => f.ID === 'TXT-001');
  assert.equal(langFunde.length, 1);
  assert.equal(langFunde[0].Anzahl, 2, 'Zwei lange Saetze im Absatz muessen als zwei gezaehlt werden');
  checks.push('Satzlaenge: drei kurze Saetze ohne Fehlalarm und zwei lange Saetze richtig gezaehlt');

  for (const datei of ['LeeresKapitel.docx', 'FehlenderInhalt.docx', 'Zeilenumbruch.pdf']) {
    await checkFile(datei);
    const liste = await (await context.request.get(url + '/api/pruefungen')).json();
    const id = liste.pruefungen.find(p => p.dateiname === datei).id;
    const ergebnis = await (await context.request.get(url + '/api/pruefung/' + id)).json();
    const erwartet = datei.endsWith('.pdf') ? 'TXT-001' : 'CHK-002';
    assert.ok(ergebnis.funde.some(f => f.ID === erwartet), datei + ': Befund fehlt');
  }
  checks.push('Leere Kapitel, fehlende Inhalte und PDF-Satz ueber zwei Zeilen');

  await page.locator('#b-help').click(); await visible('#drawer');
  await page.locator('#drawer-close').click();
  await response('/api/ich/einstellungen', () => page.locator('#b-theme').click());
  assert.equal(await page.locator('html').getAttribute('data-theme'), 'light');
  await page.locator('#b-settings').click();
  await page.locator('[data-sec=erscheinung]').click();
  await page.locator('#seg-ts button[data-v=gross]').click();
  await response('/api/ich/einstellungen', () => page.locator('#save-top').click());
  await page.reload(); await visible('#main');
  assert.equal(await page.locator('html').getAttribute('data-theme'), 'light');
  assert.match(await page.locator('html').getAttribute('style'), /1\.12/);
  for (const size of [{width:390,height:844}, {width:320,height:740}, {width:844,height:390}]) {
    await page.setViewportSize(size);
    const overflow = await page.evaluate(() => ({ overflow: document.documentElement.scrollWidth > innerWidth + 1,
      elements: Array.from(document.querySelectorAll('body *')).filter(e => e.getBoundingClientRect().right > innerWidth + 1 && e.clientWidth).slice(0,12).map(e => e.id || e.className || e.tagName) }));
    assert.equal(overflow.overflow, false, `Seitenueberlauf bei ${size.width}px: ${overflow.elements.join(', ')}`);
    await page.screenshot({ path: path.join(out, `ansicht-${size.width}.png`), fullPage: true });
  }
  checks.push('Hilfe, Hell/Dunkel, grosse Schrift, Neuladen, 320/390px und Querformat');
  await page.setViewportSize({width:1365,height:900});
  await checkFile('gemischt.pdf');
  assert.match(await page.locator('#res-hinweise').innerText(), /Seite 2/);
  await page.screenshot({ path: path.join(out, 'gemischtes-pdf.png'), fullPage: true });
  await page.locator('#file').setInputFiles(path.join(root, 'kaputt.docx'));
  await page.locator('#start-check').click(); await visible('#check-err');
  assert.equal(await page.locator('#result').isVisible(), false);
  await checkFile('Testanleitung.docx');
  checks.push('Gemischtes PDF, defekte Datei, Fehleranzeige und erneute Pruefung');

  await page.locator('#b-settings').click(); await page.locator('#nav-verwaltung').click();
  await page.locator('#user-new').click();
  await page.locator('#u-name').fill('Zusaetzlicher Testnutzer');
  await page.locator('#u-email').fill('neu@example.invalid');
  await page.locator('#user-save').click(); await visible('#user-otp');
  assert.ok((await page.locator('#user-otp').innerText()).length > 10);
  await page.locator('#user-close').click(); await page.locator('#back-main').click();
  checks.push('Admin legt zusaetzliches Mitglied an');

  // Simulierte langsame Antwort nach einem echten Pruefrequest: keine Daten nach Logout zeigen.
  let release;
  const barrier = new Promise(resolve => { release = resolve; });
  let routed = false;
  await page.route('**/api/pruefung', async route => {
    routed = true;
    const answer = await route.fetch();
    await barrier;
    try { await route.fulfill({ response: answer }); } catch (_) {} // Transport kann bereits abgebrochen sein.
  });
  await page.locator('#file').setInputFiles(path.join(root, 'Testanleitung.docx'));
  await page.locator('#start-check').click(); await visible('#lauf');
  assert.equal(await page.locator('#start-check').isEnabled(), false);
  await page.locator('#b-help').click(); await visible('#drawer'); await page.locator('#drawer-close').click();
  await page.locator('#b-settings').click();
  await page.locator('[data-sec=profil]').click();
  await page.locator('#logout2').click(); await visible('#f-login');
  await login('mitglied@example.invalid');
  assert.ok(routed); release(); await page.unroute('**/api/pruefung'); await sleep(200);
  assert.equal(await page.locator('#result').isVisible(), false);
  assert.equal(await page.locator('#pop').isVisible(), false);
  assert.equal(await page.locator('#lauf').isVisible(), false);
  assert.equal((await context.request.get(url + `/api/pruefung/${pid}`)).status(), 404);
  assert.equal((await context.request.get(url + '/api/benutzer')).status(), 403);
  await page.locator('#b-settings').click();
  assert.equal(await page.locator('#nav-verwaltung').isVisible(), false);
  await page.locator('#back-main').click();
  await checkFile('Testanleitung.docx');
  checks.push('Langer Lauf, bedienbarer Header, Logout, spaete Antwort, Mitglied und Rechte');
  assert.deepEqual(errors, []);
  fs.writeFileSync(path.join(out, 'browser-ergebnis.json'), JSON.stringify({status:'bestanden', platform:process.platform, checks, javascriptErrors:errors}, null, 2));
  console.log(`Browser-Abnahme bestanden: ${checks.length} Ablaufsgruppen, keine JavaScript-Ausnahmen.`);
})().catch(async err => {
  if (page) await page.screenshot({ path: path.join(out, 'fehler.png'), fullPage: true }).catch(() => {});
  fs.writeFileSync(path.join(out, 'browser-ergebnis.json'), JSON.stringify({status:'fehlgeschlagen', checks, error:err.message, javascriptErrors:errors}, null, 2));
  console.error(err.message); process.exitCode = 1;
}).finally(async () => {
  if (browser) await browser.close();
  server.kill('SIGINT');
  await new Promise(resolve => { if (server.exitCode !== null) resolve(); else server.once('exit', resolve); });
  fs.rmSync(root, { recursive: true, force: true });
});
