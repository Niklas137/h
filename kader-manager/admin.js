/* Kader-Manager – Admin: Anmeldung, Spieler anlegen, bearbeiten, deaktivieren, löschen; Fotos importieren;
   JSON import/export. Speichert im localStorage (statische Seite); mit server.py zusätzlich Veröffentlichen
   und Foto-Upload, beides nur mit Admin-Passwort (KADER_ADMIN_TOKEN, geprüft am Server). */
import { laden, lokalSchreiben, lokalLoeschen, pruefen, spielerNormalisieren, spielerFehler, idAus, teamfarbenSetzen, trikotSvg, escapeHtml, statusLabel, STATISTIK_FELDER } from './kader-daten.js';
import { transliterieren } from './sprache.js';

const bereich = document.getElementById('admin-bereich');
const tbody = document.querySelector('#admin-tabelle tbody');
const dialog = document.getElementById('spieler-dialog');
const formular = document.getElementById('spieler-formular');
const fehlerFeld = document.getElementById('formular-fehler');
const vorschau = document.getElementById('vorschau-trikot');
const fotoVorschau = document.getElementById('foto-vorschau');
const fotoMeldung = document.getElementById('foto-meldung');
const anmeldeDialog = document.getElementById('anmelde-dialog');
const anmeldeFormular = document.getElementById('anmelde-formular');
const anmeldeFehler = document.getElementById('anmelde-fehler');
const anmeldeHinweis = document.getElementById('anmelde-hinweis');
const serverMeldung = document.getElementById('server-meldung');
const TOKEN_SCHLUESSEL = 'kaderManager.token';
const FOTO_BREITE = 480, FOTO_HOEHE = 640, FOTO_MAX_BYTES = 12_000_000;

let daten;
let bearbeiteId = null;

/* ---------- Eigene Rückfragen und Meldungen (statt confirm/alert, die in Einbettungen gesperrt sein können) ---------- */
function bestaetigen(text, { titel = 'Bitte bestätigen', ok = 'OK', gefahr = false } = {}) {
  const d = document.getElementById('frage-dialog');
  document.getElementById('frage-titel').textContent = titel;
  document.getElementById('frage-text').textContent = text;
  const ja = document.getElementById('frage-ja');
  ja.textContent = ok;
  ja.classList.toggle('gefahr', gefahr); ja.classList.toggle('primaer', !gefahr);
  return new Promise(res => {
    const ende = wert => { d.removeEventListener('close', beimSchliessen); res(wert); };
    const beimSchliessen = () => ende(d.returnValue === 'ja');
    d.addEventListener('close', beimSchliessen);
    document.getElementById('frage-nein').onclick = () => d.close('nein');
    d.querySelector('form').onsubmit = e => { e.preventDefault(); d.close('ja'); };
    d.returnValue = 'nein';
    d.showModal();
    ja.focus();
  });
}
function melden(text, titel = 'Hinweis') {
  const d = document.getElementById('meldung-dialog');
  document.getElementById('meldung-titel').textContent = titel;
  document.getElementById('meldung-text').textContent = text;
  d.showModal();
}
async function sha256Hex(text) {
  if (!crypto?.subtle) throw new Error('Dieser Browser kann hier keine Prüfsumme bilden (unsichere Verbindung?).');
  const bytes = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
  return [...new Uint8Array(bytes)].map(b => b.toString(16).padStart(2, '0')).join('');
}
let server = false;          // server.py erreichbar (/api/kader antwortet)
let token = '';              // nur im Speicher und in sessionStorage, nie in den Daten

init().catch(f => { anmeldeHinweis.textContent = `Daten nicht ladbar: ${f.message}`; });

/* ---------- Anmeldung ---------- */
async function init() {
  daten = (await laden()).daten;
  teamfarbenSetzen(daten.team);
  document.getElementById('anmelde-team').textContent = [daten.team.name, daten.team.season].filter(Boolean).join(' · ') || 'Kader-Manager';
  server = await serverErkennen();
  if (!anmeldeDialog.open) anmeldeDialog.showModal();
  if (server) {
    anmeldeHinweis.textContent = 'Bitte mit dem Admin-Passwort anmelden. Es wird am Server geprüft und nirgends gespeichert.';
    document.getElementById('anmelde-felder').hidden = false;
    const gemerkt = sessionStorage.getItem(TOKEN_SCHLUESSEL);
    if (gemerkt && await tokenPruefen(gemerkt)) { anmelden(gemerkt); return; }
    sessionStorage.removeItem(TOKEN_SCHLUESSEL);
    anmeldeFormular.elements.token.focus();
  } else {
    anmeldeDialogVorbereiten();
    if (daten.team.adminPasswordHash && sessionStorage.getItem(TOKEN_SCHLUESSEL) === daten.team.adminPasswordHash) { anmelden(''); return; }
    if (daten.team.adminPasswordHash) anmeldeFormular.elements.token.focus();
  }
}

/* Anmeldefenster ohne Server: Passwortfeld, wenn eine Prüfsumme gesetzt ist, sonst „Lokal weiterarbeiten“ */
function anmeldeDialogVorbereiten() {
  const mitPasswort = !!daten.team.adminPasswordHash;
  anmeldeHinweis.textContent = mitPasswort
    ? 'Bitte mit dem Admin-Passwort anmelden. Ohne Server bleiben Änderungen in diesem Browser, bis die exportierte Datei daten/kader.json übernommen wird.'
    : 'Kein Server erreichbar (statische Seite oder Vorschau) und kein Admin-Passwort gesetzt. Änderungen und Fotos bleiben in diesem Browser, bis die exportierte Datei daten/kader.json übernommen wird. Ein Passwort lässt sich oben rechts unter „Passwort“ festlegen.';
  document.getElementById('anmelde-felder').hidden = !mitPasswort;
  document.getElementById('anmelde-lokal').hidden = mitPasswort;
}

async function serverErkennen() {
  try {
    const r = await fetch('/api/kader', { method: 'GET', cache: 'no-store' });
    return r.ok && (r.headers.get('Content-Type') || '').includes('application/json');
  } catch { return false; }
}

async function tokenPruefen(t) {
  try {
    const r = await fetch('/api/anmelden', { method: 'POST', headers: { 'X-Admin-Token': t }, cache: 'no-store' });
    return r.status === 204;
  } catch { return false; }
}

anmeldeFormular.addEventListener('submit', async e => {
  e.preventDefault();
  const eingabe = anmeldeFormular.elements.token.value.trim();
  anmeldeFehler.textContent = '';
  if (!eingabe) { anmeldeFehler.textContent = 'Bitte das Admin-Passwort eingeben.'; return; }
  const knopf = document.getElementById('knopf-anmelden');
  knopf.disabled = true;
  let ok = false;
  try {
    if (server) ok = await tokenPruefen(eingabe);
    else { await new Promise(r => setTimeout(r, 400)); ok = (await sha256Hex(eingabe)) === daten.team.adminPasswordHash; }
  } catch (f) { anmeldeFehler.textContent = f.message; knopf.disabled = false; return; }
  knopf.disabled = false;
  if (!ok) { anmeldeFehler.textContent = server ? 'Passwort falsch oder Server ohne gesetztes KADER_ADMIN_TOKEN.' : 'Passwort falsch.'; anmeldeFormular.elements.token.select(); return; }
  if (!server) sessionStorage.setItem(TOKEN_SCHLUESSEL, daten.team.adminPasswordHash);   // nur die Prüfsumme, für diese Sitzung
  anmelden(server ? eingabe : '');
});
anmeldeDialog.addEventListener('cancel', e => e.preventDefault());     // Escape schließt das Anmeldefenster nicht
document.getElementById('knopf-lokal').addEventListener('click', () => anmelden(''));

function anmelden(t) {
  token = t;
  if (t) sessionStorage.setItem(TOKEN_SCHLUESSEL, t);
  anmeldeFormular.reset();
  anmeldeDialog.close();
  document.getElementById('admin-team').textContent = [daten.team.name, daten.team.season].filter(Boolean).join(' · ');
  document.getElementById('konto-stand').textContent = server ? 'Angemeldet als Admin' : (daten.team.adminPasswordHash ? 'Angemeldet (ohne Server, Passwort)' : 'Lokaler Modus (ohne Server)');
  document.getElementById('knopf-abmelden').hidden = !(server || daten.team.adminPasswordHash);
  document.getElementById('knopf-passwort').hidden = server;
  document.getElementById('server-bereich').hidden = !server;
  if (server) document.getElementById('admin-hinweis').textContent = 'Änderungen werden zuerst im Browser gespeichert und sind sofort auf der Kaderseite sichtbar. Mit „Veröffentlichen“ landen sie auf dem Server.';
  bereich.hidden = false;
  tabelleZeichnen();
}

document.getElementById('knopf-abmelden').addEventListener('click', () => {
  token = '';
  sessionStorage.removeItem(TOKEN_SCHLUESSEL);
  bereich.hidden = true;
  anmeldeFehler.textContent = '';
  if (!server) anmeldeDialogVorbereiten();
  anmeldeDialog.showModal();
  if (server || daten.team.adminPasswordHash) anmeldeFormular.elements.token.focus();
});

/* ---------- Admin-Passwort ohne Server: Prüfsumme in den Teamdaten ---------- */
const passwortDialog = document.getElementById('passwort-dialog');
const passwortFormular = document.getElementById('passwort-formular');
document.getElementById('knopf-passwort').addEventListener('click', () => {
  passwortFormular.reset();
  document.getElementById('passwort-fehler').textContent = '';
  document.getElementById('passwort-entfernen').hidden = !daten.team.adminPasswordHash;
  passwortDialog.showModal();
});
document.getElementById('passwort-abbrechen').addEventListener('click', () => passwortDialog.close());
passwortFormular.addEventListener('submit', async e => {
  e.preventDefault();
  const pw1 = passwortFormular.elements.pw1.value, pw2 = passwortFormular.elements.pw2.value;
  const fehler = document.getElementById('passwort-fehler');
  if (pw1.length < 8) { fehler.textContent = 'Mindestens 8 Zeichen.'; return; }
  if (pw1 !== pw2) { fehler.textContent = 'Die beiden Eingaben stimmen nicht überein.'; return; }
  try { daten.team.adminPasswordHash = await sha256Hex(pw1); } catch (f) { fehler.textContent = f.message; return; }
  passwortFormular.reset();
  speichern();
  sessionStorage.setItem(TOKEN_SCHLUESSEL, daten.team.adminPasswordHash);
  passwortDialog.close();
  anmelden('');
  melden('Passwort gesetzt. Es gilt ab jetzt in diesem Browser und nach „JSON exportieren“ überall, wo diese Datei als daten/kader.json liegt.', 'Passwort');
});
document.getElementById('passwort-entfernen').addEventListener('click', async () => {
  passwortDialog.close();
  if (!await bestaetigen('Admin-Passwort entfernen? Die Admin-Seite ist dann ohne Server frei zugänglich.', { ok: 'Entfernen', gefahr: true })) return;
  delete daten.team.adminPasswordHash;
  sessionStorage.removeItem(TOKEN_SCHLUESSEL);
  speichern();
  anmelden('');
});

/* ---------- Speichern und Tabelle ---------- */
function speichern() {
  try {
    daten = pruefen(daten);
    lokalSchreiben(daten);
  } catch (f) {
    melden(`Nicht gespeichert: ${f.message}`, 'Fehler');
  }
  tabelleZeichnen();
}

function tabelleZeichnen() {
  const liste = [...daten.players].sort((a, b) => a.number - b.number);
  tbody.innerHTML = liste.map(p => `
    <tr class="${p.status === 'inactive' ? 'inaktiv' : ''}" data-id="${escapeHtml(p.id)}">
      <td>${p.photo ? `<img class="tabelle-foto" src="${escapeHtml(p.photo)}" alt="">` : '<span class="tabelle-foto leer"></span>'}</td>
      <td><strong>${p.number}</strong></td>
      <td>${escapeHtml(p.name)}</td>
      <td lang="uk">${p.nameUk ? escapeHtml(p.nameUk) : `<span class="muted" title="automatisch">${escapeHtml(transliterieren(p.name, p.nationality))}</span>`}</td>
      <td>${escapeHtml(p.position)}</td>
      <td><span class="status-punkt" data-status="${escapeHtml(p.status)}"></span>${statusLabel(p.status)}</td>
      <td>${escapeHtml(p.nationality)}</td>
      <td>${p.birthYear ?? ''}</td>
      ${STATISTIK_FELDER.map(([f]) => `<td>${p.stats?.[f] ?? ''}</td>`).join('')}
      <td class="aktionen">
        <button type="button" class="knopf" data-aktion="bearbeiten">Bearbeiten</button>
        <button type="button" class="knopf" data-aktion="status">${p.status === 'inactive' ? 'Aktivieren' : 'Deaktivieren'}</button>
        <button type="button" class="knopf gefahr" data-aktion="loeschen">Löschen</button>
      </td>
    </tr>`).join('') || '<tr><td colspan="13">Noch keine Spieler.</td></tr>';
}

tbody.addEventListener('click', async e => {
  const knopf = e.target.closest('button[data-aktion]');
  if (!knopf) return;
  const id = knopf.closest('tr').dataset.id;
  const spieler = daten.players.find(p => p.id === id);
  if (!spieler) return;
  if (knopf.dataset.aktion === 'bearbeiten') dialogOeffnen(spieler);
  if (knopf.dataset.aktion === 'status') {
    spieler.status = spieler.status === 'inactive' ? 'active' : 'inactive';
    const fehler = spielerFehler(spieler, daten.players);
    if (fehler.length) { spieler.status = spieler.status === 'inactive' ? 'active' : 'inactive'; melden(fehler.join(' '), 'Nicht möglich'); return; }
    speichern();
  }
  if (knopf.dataset.aktion === 'loeschen' && await bestaetigen(`${spieler.name} (#${spieler.number}) endgültig aus dem Kader löschen?`, { titel: 'Spieler löschen', ok: 'Löschen', gefahr: true })) {
    daten.players = daten.players.filter(p => p.id !== id);
    speichern();
  }
});

/* ---------- Spielerdialog ---------- */
document.getElementById('knopf-neu').addEventListener('click', () => dialogOeffnen(null));
document.getElementById('knopf-abbrechen').addEventListener('click', () => dialog.close());

function dialogOeffnen(spieler) {
  bearbeiteId = spieler?.id ?? null;
  document.getElementById('dialog-titel').textContent = spieler ? `${spieler.name} bearbeiten` : 'Neuer Spieler';
  formular.reset();
  fehlerFeld.textContent = '';
  fotoMeldung.textContent = fotoMeldung.dataset.standard ??= fotoMeldung.textContent;
  if (spieler) {
    for (const feld of ['name', 'nameUk', 'number', 'position', 'status', 'nationality', 'birthYear', 'photo', 'bio', 'bioUk']) {
      formular.elements[feld].value = spieler[feld] ?? '';
    }
    for (const [feld] of STATISTIK_FELDER) formular.elements[feld].value = spieler.stats?.[feld] ?? '';
  }
  nameUkVonHand = !!spieler?.nameUk;
  if (!nameUkVonHand) nameUkAuto();
  fotoVorschauZeichnen();
  vorschauZeichnen();
  dialog.showModal();
}

/* Ukrainischer Name: automatisch aus dem lateinischen Namen, solange das Feld nicht von Hand geändert wurde */
let nameUkVonHand = false;
function nameUkAuto() {
  formular.elements.nameUk.value = transliterieren(formular.elements.name.value, formular.elements.nationality.value);
  nameUkVonHand = false;
}
formular.elements.nameUk.addEventListener('input', () => { nameUkVonHand = formular.elements.nameUk.value.trim() !== ''; });
for (const feld of ['name', 'nationality']) formular.elements[feld].addEventListener('input', () => { if (!nameUkVonHand) nameUkAuto(); });
document.getElementById('name-uk-neu').addEventListener('click', () => { nameUkAuto(); vorschauZeichnen(); });

formular.addEventListener('input', vorschauZeichnen);
function vorschauZeichnen() {
  vorschau.innerHTML = trikotSvg(ausFormular(), { beschriftung: false });
}
function fotoVorschauZeichnen() {
  const pfad = formular.elements.photo.value;
  fotoVorschau.innerHTML = pfad ? `<img src="${escapeHtml(pfad)}" alt="Spielerfoto">` : '<span class="muted">Kein Foto</span>';
  document.getElementById('foto-entfernen').disabled = !pfad;
}

function ausFormular() {
  const fd = new FormData(formular);
  const roh = Object.fromEntries(fd.entries());
  const stats = {};
  for (const [feld] of STATISTIK_FELDER) { stats[feld] = roh[feld]; delete roh[feld]; }
  roh.stats = stats;
  roh.id = bearbeiteId ?? idAus(roh.name, roh.number);
  return spielerNormalisieren(roh);
}

formular.addEventListener('submit', e => {
  e.preventDefault();
  const spieler = ausFormular();
  if (!bearbeiteId && daten.players.some(p => p.id === spieler.id)) spieler.id = `${spieler.id}-${Date.now().toString(36)}`;
  const fehler = spielerFehler(spieler, daten.players);
  if (fehler.length) { fehlerFeld.textContent = fehler.join(' '); return; }
  const index = daten.players.findIndex(p => p.id === bearbeiteId);
  if (index >= 0) daten.players[index] = spieler; else daten.players.push(spieler);
  speichern();
  dialog.close();
});

/* ---------- Fotoimport ---------- */
document.getElementById('foto-datei').addEventListener('change', async e => {
  const datei = e.target.files[0];
  e.target.value = '';
  if (!datei) return;
  fotoMeldung.textContent = 'Foto wird verarbeitet …';
  try {
    if (!/^image\/(jpeg|png|webp)$/.test(datei.type)) throw new Error('Nur JPG, PNG oder WebP.');
    if (datei.size > FOTO_MAX_BYTES) throw new Error('Datei größer als 12 MB.');
    const blob = await fotoVerkleinern(datei);
    if (server && token) {
      const kennung = bearbeiteId ?? ausFormular().id;
      if (!kennung || kennung === 'spieler') throw new Error('Bitte zuerst Name und Rückennummer eintragen, dann das Foto wählen.');
      const r = await fetch(`/api/foto?spieler=${encodeURIComponent(kennung)}`, { method: 'POST', headers: { 'Content-Type': 'image/jpeg', 'X-Admin-Token': token }, body: blob });
      const antwort = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(antwort.fehler || `Server antwortet ${r.status}`);
      formular.elements.photo.value = antwort.pfad;
      fotoMeldung.textContent = `Hochgeladen nach ${antwort.pfad.split('?')[0]} (${Math.round(blob.size / 1024)} KB).`;
    } else {
      formular.elements.photo.value = await alsDataUrl(blob);
      fotoMeldung.textContent = `Foto übernommen (${Math.round(blob.size / 1024)} KB, wird mit den Daten gespeichert).`;
    }
    fotoVorschauZeichnen();
  } catch (f) {
    fotoMeldung.textContent = `Foto nicht übernommen: ${f.message}`;
  }
});
document.getElementById('foto-entfernen').addEventListener('click', () => {
  formular.elements.photo.value = '';
  fotoMeldung.textContent = 'Foto entfernt. Wird beim Speichern übernommen.';
  fotoVorschauZeichnen();
});

/** Verkleinert und beschneidet das Bild auf 3:4 (480 × 640), Ausgabe als JPEG. */
async function fotoVerkleinern(datei) {
  const bild = await bildLaden(datei);
  const quelle = Math.min(bild.width, bild.height * FOTO_BREITE / FOTO_HOEHE);       // größter 3:4-Ausschnitt
  const quellHoehe = quelle * FOTO_HOEHE / FOTO_BREITE;
  const sx = (bild.width - quelle) / 2, sy = Math.max(0, (bild.height - quellHoehe) * 0.3);   // Gesicht eher oben
  const breite = Math.min(FOTO_BREITE, Math.round(quelle)), hoehe = Math.round(breite * FOTO_HOEHE / FOTO_BREITE);
  const leinwand = document.createElement('canvas');
  leinwand.width = breite; leinwand.height = hoehe;
  const ctx = leinwand.getContext('2d');
  ctx.imageSmoothingQuality = 'high';
  ctx.drawImage(bild, sx, sy, quelle, quellHoehe, 0, 0, breite, hoehe);
  if (bild.close) bild.close();
  const blob = await new Promise(res => leinwand.toBlob(res, 'image/jpeg', 0.86));
  if (!blob) throw new Error('Bild konnte nicht umgewandelt werden.');
  return blob;
}
async function bildLaden(datei) {
  if ('createImageBitmap' in window) {
    try { return await createImageBitmap(datei, { imageOrientation: 'from-image' }); } catch { /* unten der Rückweg */ }
  }
  return new Promise((res, rej) => {
    const url = URL.createObjectURL(datei);
    const img = new Image();
    img.onload = () => { URL.revokeObjectURL(url); res(img); };
    img.onerror = () => { URL.revokeObjectURL(url); rej(new Error('Bild nicht lesbar.')); };
    img.src = url;
  });
}
const alsDataUrl = blob => new Promise((res, rej) => { const r = new FileReader(); r.onload = () => res(r.result); r.onerror = () => rej(new Error('Bild nicht lesbar.')); r.readAsDataURL(blob); });

/* ---------- Export, Import, Veröffentlichen ---------- */
document.getElementById('knopf-export').addEventListener('click', () => {
  const blob = new Blob([JSON.stringify(pruefen(daten), null, 2) + '\n'], { type: 'application/json' });
  const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob), download: 'kader.json' });
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
});

document.getElementById('datei-import').addEventListener('change', async e => {
  const datei = e.target.files[0];
  if (!datei) return;
  try {
    const neu = pruefen(JSON.parse(await datei.text()));
    if (!await bestaetigen(`${neu.players.length} Spieler aus „${datei.name}“ übernehmen? Der aktuelle lokale Stand wird ersetzt.`, { titel: 'JSON importieren', ok: 'Übernehmen' })) return;
    daten = neu;
    teamfarbenSetzen(daten.team);
    speichern();
  } catch (f) {
    melden(`Datei nicht brauchbar: ${f.message}`, 'Import');
  } finally {
    e.target.value = '';
  }
});

document.getElementById('knopf-veroeffentlichen').addEventListener('click', async () => {
  if (!token) { serverMeldung.textContent = 'Bitte zuerst anmelden.'; return; }
  let payload;
  try { payload = pruefen(daten); } catch (f) { serverMeldung.textContent = `Nicht veröffentlicht: ${f.message}`; return; }
  serverMeldung.textContent = 'Wird veröffentlicht …';
  try {
    const r = await fetch('/api/kader', { method: 'PUT', headers: { 'Content-Type': 'application/json', 'X-Admin-Token': token }, body: JSON.stringify(payload) });
    const antwort = await r.json().catch(() => ({}));
    if (r.status === 403) { serverMeldung.textContent = 'Anmeldung abgelaufen, bitte neu anmelden.'; document.getElementById('knopf-abmelden').click(); return; }
    if (!r.ok) { serverMeldung.textContent = `Abgelehnt: ${antwort.fehler || r.status}`; return; }
    lokalLoeschen();
    serverMeldung.textContent = `Veröffentlicht (${antwort.spieler} Spieler). Lokale Änderungen wurden übernommen.`;
  } catch (f) {
    serverMeldung.textContent = `Fehler beim Senden: ${f.message}`;
  }
});

document.getElementById('knopf-zuruecksetzen').addEventListener('click', async () => {
  if (!await bestaetigen('Alle lokalen Änderungen verwerfen und den veröffentlichten Stand laden?', { titel: 'Lokale Änderungen verwerfen', ok: 'Verwerfen', gefahr: true })) return;
  lokalLoeschen();
  daten = (await laden({ nurDatei: true })).daten;
  teamfarbenSetzen(daten.team);
  tabelleZeichnen();
});
