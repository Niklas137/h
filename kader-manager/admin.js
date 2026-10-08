/* Kader-Manager – Admin: Spieler anlegen, bearbeiten, deaktivieren, löschen; JSON import/export.
   Speichert im localStorage (statische Seite). Für ein Backend speichern() auf einen POST umstellen. */
import { laden, lokalSchreiben, lokalLoeschen, pruefen, spielerNormalisieren, spielerFehler, idAus, teamfarbenSetzen, trikotSvg, escapeHtml, statusLabel, STATISTIK_FELDER } from './kader-daten.js';

const tbody = document.querySelector('#admin-tabelle tbody');
const dialog = document.getElementById('spieler-dialog');
const formular = document.getElementById('spieler-formular');
const fehlerFeld = document.getElementById('formular-fehler');
const vorschau = document.getElementById('vorschau-trikot');
let daten;
let bearbeiteId = null;

init().catch(f => { document.getElementById('admin-hinweis').textContent = `Daten nicht ladbar: ${f.message}`; });

async function init() {
  daten = (await laden()).daten;
  serverErkennen();
  teamfarbenSetzen(daten.team);
  document.getElementById('admin-team').textContent = [daten.team.name, daten.team.season].filter(Boolean).join(' · ');
  tabelleZeichnen();
}

function speichern() {
  try {
    daten = pruefen(daten);
    lokalSchreiben(daten);
  } catch (f) {
    alert(`Nicht gespeichert: ${f.message}`);
  }
  tabelleZeichnen();
}

function tabelleZeichnen() {
  const liste = [...daten.players].sort((a, b) => a.number - b.number);
  tbody.innerHTML = liste.map(p => `
    <tr class="${p.status === 'inactive' ? 'inaktiv' : ''}" data-id="${escapeHtml(p.id)}">
      <td><strong>${p.number}</strong></td>
      <td>${escapeHtml(p.name)}</td>
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
    </tr>`).join('') || '<tr><td colspan="11">Noch keine Spieler.</td></tr>';
}

tbody.addEventListener('click', e => {
  const knopf = e.target.closest('button[data-aktion]');
  if (!knopf) return;
  const id = knopf.closest('tr').dataset.id;
  const spieler = daten.players.find(p => p.id === id);
  if (!spieler) return;
  if (knopf.dataset.aktion === 'bearbeiten') dialogOeffnen(spieler);
  if (knopf.dataset.aktion === 'status') {
    spieler.status = spieler.status === 'inactive' ? 'active' : 'inactive';
    const fehler = spielerFehler(spieler, daten.players);
    if (fehler.length) { spieler.status = spieler.status === 'inactive' ? 'active' : 'inactive'; alert(fehler.join('\n')); return; }
    speichern();
  }
  if (knopf.dataset.aktion === 'loeschen' && confirm(`${spieler.name} (#${spieler.number}) endgültig aus dem Kader löschen?`)) {
    daten.players = daten.players.filter(p => p.id !== id);
    speichern();
  }
});

document.getElementById('knopf-neu').addEventListener('click', () => dialogOeffnen(null));
document.getElementById('knopf-abbrechen').addEventListener('click', () => dialog.close());

function dialogOeffnen(spieler) {
  bearbeiteId = spieler?.id ?? null;
  document.getElementById('dialog-titel').textContent = spieler ? `${spieler.name} bearbeiten` : 'Neuer Spieler';
  formular.reset();
  fehlerFeld.textContent = '';
  if (spieler) {
    for (const feld of ['name', 'number', 'position', 'status', 'nationality', 'birthYear', 'photo', 'bio']) {
      formular.elements[feld].value = spieler[feld] ?? '';
    }
    for (const [feld] of STATISTIK_FELDER) formular.elements[feld].value = spieler.stats?.[feld] ?? '';
  }
  vorschauZeichnen();
  dialog.showModal();
}

formular.addEventListener('input', vorschauZeichnen);
function vorschauZeichnen() {
  vorschau.innerHTML = trikotSvg(ausFormular(), { beschriftung: false });
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
    if (!confirm(`${neu.players.length} Spieler aus „${datei.name}" übernehmen? Der aktuelle lokale Stand wird ersetzt.`)) return;
    daten = neu;
    teamfarbenSetzen(daten.team);
    speichern();
  } catch (f) {
    alert(`Datei nicht brauchbar: ${f.message}`);
  } finally {
    e.target.value = '';
  }
});

/* Veröffentlichen über server.py (nur wenn /api/kader antwortet) */
async function serverErkennen() {
  try {
    const r = await fetch('/api/kader', { method: 'GET', cache: 'no-store' });
    if (!r.ok) return;
    document.getElementById('server-bereich').hidden = false;
    document.getElementById('admin-token').value = sessionStorage.getItem('kaderManager.token') || '';
  } catch { /* kein Server, statischer Betrieb */ }
}
document.getElementById('knopf-veroeffentlichen').addEventListener('click', async () => {
  const token = document.getElementById('admin-token').value.trim();
  const meldung = document.getElementById('server-meldung');
  if (!token) { meldung.textContent = 'Bitte Admin-Token eingeben.'; return; }
  sessionStorage.setItem('kaderManager.token', token);
  let payload;
  try { payload = pruefen(daten); } catch (f) { meldung.textContent = `Nicht veröffentlicht: ${f.message}`; return; }
  meldung.textContent = 'Wird veröffentlicht …';
  try {
    const r = await fetch('/api/kader', { method: 'PUT', headers: { 'Content-Type': 'application/json', 'X-Admin-Token': token }, body: JSON.stringify(payload) });
    const antwort = await r.json().catch(() => ({}));
    if (!r.ok) { meldung.textContent = `Abgelehnt: ${antwort.fehler || r.status}`; return; }
    lokalLoeschen();
    meldung.textContent = `Veröffentlicht (${antwort.spieler} Spieler). Lokale Änderungen wurden übernommen.`;
  } catch (f) {
    meldung.textContent = `Fehler beim Senden: ${f.message}`;
  }
});

document.getElementById('knopf-zuruecksetzen').addEventListener('click', async () => {
  if (!confirm('Alle lokalen Änderungen verwerfen und den veröffentlichten Stand laden?')) return;
  lokalLoeschen();
  daten = (await laden({ nurDatei: true })).daten;
  teamfarbenSetzen(daten.team);
  tabelleZeichnen();
});
