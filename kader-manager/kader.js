/* Kader-Manager – Kaderseite „Kleiderstange“, Ablauf nach der Video-Referenz.
   Tipp → Trikot dreht sich an Ort und Stelle nach vorn, die Kamera fährt heran, dann schiebt
   sich die Datenkarte ein. Wechsel → Kamera schwenkt zum Nachbarn. Zurück → Karte raus,
   Kamera zurück, Trikot wieder seitlich.
   Zustände: geschlossen | oeffnend | offen | schliessend. Jede Aktion erhöht die Vorgangs-
   kennung; verzögerte Schritte (Timer, Animationsframes) prüfen sie und verfallen sonst (A01).
   Nur transform und opacity werden animiert; die Übergänge stehen in kader.css. */
import { laden, teamfarbenSetzen, trikotWaehlen, trikotSvg, escapeHtml, statusLabel, STATUS } from './kader-daten.js';
import { spracheWaehlen } from './sprache.js';

const modul = document.getElementById('inhalt');
const szene = document.getElementById('szene');
const stange = document.getElementById('stange');
const innen = document.getElementById('stange-innen');
const karte = document.getElementById('karte');
const karteKoerper = document.getElementById('karte-koerper');
const leisteSpieler = document.getElementById('leiste-spieler');
const leisteHinweis = document.getElementById('leiste-hinweis');
const zahlen = document.getElementById('zahlen');
const filterLeiste = document.getElementById('kader-filter');
const hinweis = document.getElementById('kader-hinweis');
const pfeilLinks = document.getElementById('stange-links');
const pfeilRechts = document.getElementById('stange-rechts');
const reduziert = matchMedia('(prefers-reduced-motion: reduce)');
const desktop = matchMedia('(min-width: 900px)');

let daten = { team: null, players: [] };
let T = null;                 // Oberflächentexte der gewählten Sprache
let trikotSchluessel = 'heim';
let liste = [];               // sichtbare, gefilterte Spieler in Stangenreihenfolge
let aktiverFilter = 'alle';
let zustand = 'geschlossen';  // geschlossen | oeffnend | offen | schliessend
let gewaehlt = null;          // Spieler der offenen (oder gerade öffnenden) Karte
let aktuell = null;           // Spieler in der Mitte der Stange (Leiste)
let vorgang = 0;              // Kennung des jüngsten Vorgangs; ältere verzögerte Schritte verfallen
let zuletztFokussiert = null;
let scrollTimer = 0;

init().catch(f => { hinweis.hidden = false; hinweis.textContent = `${T ? T.ladefehler : 'Kader konnte nicht geladen werden'}: ${f.message}`; });

/* Schrägstellung der hängenden Trikots: Standard 50°, einstellbar über team.tilt in daten/kader.json (30–85).
   Der Abstand der Bügel folgt der sichtbaren Trikotbreite (cos der Neigung). */
function neigungAnwenden() {
  const grad = daten.team?.tilt ?? 50;
  stange.style.setProperty('--neigung', `${grad}deg`);
  const breite = parseFloat(getComputedStyle(stange).getPropertyValue('--haenger-breite')) || 330;
  const schritt = Math.max(56, Math.round(breite * Math.cos(grad * Math.PI / 180) * 0.62));
  stange.style.setProperty('--haenger-schritt', `${schritt}px`);
}

async function init() {
  const ergebnis = await laden({ nurDatei: new URLSearchParams(location.search).has('datei') });
  daten = ergebnis.daten;
  T = spracheWaehlen(daten.team).t;
  texteAnwenden();
  neigungAnwenden();
  if (daten.team.jersey && !(await bildLadbar(daten.team.jersey.back))) {
    console.warn(`Trikotbild „${daten.team.jersey.back}“ nicht ladbar, gezeichnetes Trikot wird verwendet.`);
    delete daten.team.jersey;
  }
  teamfarbenSetzen(daten.team);
  document.getElementById('kader-titel').textContent = daten.team.name || 'Kader';
  document.getElementById('kader-saison').textContent = daten.team.season ? `${T.saison} ${daten.team.season}` : '';
  document.getElementById('karte-team').textContent = [daten.team.name, daten.team.season].filter(Boolean).join(' · ');
  document.title = `Kader – ${daten.team.name}`;
  if (ergebnis.quelle === 'lokal') {
    const q = document.getElementById('kader-quelle');
    q.hidden = false;
    q.innerHTML = `${T.lokal} <a href="?datei">${T.veroeffentlicht}</a>`;
  }
  hinweis.hidden = true;
  trikotwahlAufbauen();
  filterAufbauen();
  stangeZeichnen();
  ausHashOeffnen();
  addEventListener('hashchange', ausHashOeffnen);
  addEventListener('resize', () => {
    neigungAnwenden();
    if (zustand === 'geschlossen') { if (aktuell) zurMitteRollen(aktuell, false); }
    else if (gewaehlt) kameraAuf(gewaehlt);
  });
}

function texteAnwenden() {
  document.querySelectorAll('[data-t]').forEach(el => { el.innerHTML = T[el.dataset.t] ?? el.innerHTML; });
  hinweis.textContent = T.laden;
  pfeilLinks.setAttribute('aria-label', T.links); pfeilRechts.setAttribute('aria-label', T.rechts);
  document.getElementById('karte-vorher').setAttribute('aria-label', T.vorher);
  document.getElementById('karte-weiter').setAttribute('aria-label', T.weiter);
  document.getElementById('karte-teilen').setAttribute('aria-label', T.linkKopieren);
  document.getElementById('karte-teilen').title = T.linkKopieren;
  filterLeiste.setAttribute('aria-label', T.positionFilter);
}

/* Heim-/Auswärtstrikot, wenn Alternativen in den Daten stehen */
function trikotwahlAufbauen() {
  const wahl = document.getElementById('trikotwahl');
  const alternativen = Object.keys(daten.team.jerseyAlternatives || {});
  if (!daten.team.jersey || !alternativen.length) { wahl.hidden = true; return; }
  const label = k => k === 'heim' ? T.heim : (k === 'weiss' || k === 'auswaerts' ? T.auswaerts : k);
  wahl.hidden = false;
  wahl.setAttribute('aria-label', T.trikotwahl);
  wahl.innerHTML = ['heim', ...alternativen].map(k => `<button type="button" data-trikot="${escapeHtml(k)}" aria-pressed="${k === trikotSchluessel}">${escapeHtml(label(k))}</button>`).join('');
  wahl.addEventListener('click', e => {
    const b = e.target.closest('button[data-trikot]');
    if (!b || b.dataset.trikot === trikotSchluessel) return;
    trikotSchluessel = b.dataset.trikot;
    wahl.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
    trikotWaehlen(daten.team, trikotSchluessel);
    sofortSchliessen();
    stangeZeichnen();
  });
}

function bildLadbar(url) {
  return new Promise(res => { const b = new Image(); b.onload = () => res(true); b.onerror = () => res(false); b.src = new URL(url, location.href).href; });
}

const oeffentlich = () => daten.players.filter(p => STATUS[p.status]?.oeffentlich).sort((a, b) => a.number - b.number);
const haengerVon = spieler => spieler ? innen.querySelector(`.haenger[data-id="${CSS.escape(spieler.id)}"]`) : null;
const neuerVorgang = () => ++vorgang;
const spaeter = (kennung, ms, fn) => setTimeout(() => { if (kennung === vorgang) fn(); }, ms);
const naechsterFrame = (kennung, fn) => requestAnimationFrame(() => requestAnimationFrame(() => { if (kennung === vorgang) fn(); }));

/* ---------- Filter und Stange ---------- */
function filterAufbauen() {
  const alle = oeffentlich();
  const positionen = [...new Set(alle.map(p => p.position).filter(Boolean))];
  if (positionen.length < 2) { filterLeiste.hidden = true; return; }
  const chip = (pos, label, n) => `<button type="button" data-filter="${escapeHtml(pos)}" aria-pressed="${pos === aktiverFilter}">${escapeHtml(label)}<sup>${n}</sup></button>`;
  filterLeiste.innerHTML = chip('alle', T.alle, alle.length) + positionen.map(pos => chip(pos, pos, alle.filter(p => p.position === pos).length)).join('');
  filterLeiste.addEventListener('click', e => {
    const knopf = e.target.closest('button[data-filter]');
    if (!knopf) return;
    aktiverFilter = knopf.dataset.filter;
    filterLeiste.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b === knopf)));
    sofortSchliessen();            // alte Abläufe vollständig beenden, dann neu zeichnen
    stangeZeichnen();
  });
}

function stangeZeichnen() {
  liste = oeffentlich().filter(p => aktiverFilter === 'alle' || p.position === aktiverFilter);
  hinweis.hidden = liste.length > 0;
  hinweis.textContent = liste.length ? '' : T.keineSpieler;
  innen.innerHTML = liste.map(p => `
    <li class="haenger" data-id="${escapeHtml(p.id)}">
      <button type="button" class="haenger-knopf" aria-label="${escapeHtml(p.name)}, ${T.nummer} ${p.number}, ${escapeHtml(p.position)}. ${T.trikotOeffnen}">
        <span class="trikot-haengend">${trikotSvg(p, { beschriftung: false, mitHaenger: true })}</span>
      </button>
    </li>`).join('');
  zahlen.innerHTML = liste.map(p => `<li><button type="button" data-id="${escapeHtml(p.id)}" aria-label="${T.nummer} ${p.number}, ${escapeHtml(p.name)}">${p.number}</button></li>`).join('');
  // Start wie im Video: Stange beginnt links; die Markierung gilt dem Trikot, das dann wirklich in der Mitte hängt.
  // Der Innenabstand erlaubt trotzdem, jedes Trikot (auch das erste und letzte) mittig einzurasten (A04).
  const rand = parseFloat(getComputedStyle(innen).paddingLeft) || 0;
  stange.scrollTo({ left: Math.max(0, rand - 12), behavior: 'auto' });
  aktuellSetzen(mittleresTrikot() || liste[0] || null);
}

function mittleresTrikot() {
  const mitte = stange.getBoundingClientRect().left + stange.clientWidth / 2;
  let best = null, abstand = Infinity;
  for (const li of innen.children) {
    const r = li.getBoundingClientRect();
    const d = Math.abs(r.left + r.width / 2 - mitte);
    if (d < abstand) { abstand = d; best = li; }
  }
  return best ? liste.find(p => p.id === best.dataset.id) : null;
}

innen.addEventListener('click', e => {
  const li = e.target.closest('.haenger');
  if (!li) return;
  e.stopPropagation();
  const spieler = liste.find(p => p.id === li.dataset.id);
  if (!spieler) return;
  if (zustand === 'geschlossen' || zustand === 'schliessend') oeffnen(spieler);
  else if (spieler !== gewaehlt) wechseln(spieler);
});
// Klick auf freie Fläche der Stange (nicht auf ein Trikot) schließt die offene Karte (A02)
stange.addEventListener('click', e => {
  if (zustand === 'geschlossen' || zustand === 'schliessend') return;
  if (e.target.closest('.haenger')) return;
  if (stange.classList.contains('zieht')) return;
  schliessen();
});

zahlen.addEventListener('click', e => {
  const knopf = e.target.closest('button[data-id]');
  if (!knopf) return;
  const spieler = liste.find(p => p.id === knopf.dataset.id);
  if (!spieler) return;
  if (zustand === 'geschlossen') { zurMitteRollen(spieler, true); aktuellSetzen(spieler); }
  else wechseln(spieler);
});

/* Leiste zeigt den Spieler, dessen Trikot gerade in der Mitte hängt */
stange.addEventListener('scroll', () => {
  if (zustand !== 'geschlossen') return;
  cancelAnimationFrame(scrollTimer);
  scrollTimer = requestAnimationFrame(() => { const m = mittleresTrikot(); if (m) aktuellSetzen(m); });
}, { passive: true });

function aktuellSetzen(spieler) {
  aktuell = spieler && liste.includes(spieler) ? spieler : null;
  pfeileAktualisieren();
  if (!aktuell) { leisteSpieler.textContent = ''; leisteHinweis.textContent = ''; return; }
  leisteSpieler.innerHTML = `<span class="leiste-nummer">${aktuell.number}</span> ${nameMarkup(aktuell.name)}`;
  leisteHinweis.textContent = `${aktuell.position} · ${zustand === 'geschlossen' ? T.antippen : statusLabel(aktuell.status, T.statusWerte)}`;
  zahlen.querySelectorAll('button').forEach(b => b.setAttribute('aria-current', b.dataset.id === aktuell.id ? 'true' : 'false'));
  innen.querySelectorAll('.haenger').forEach(li => li.classList.toggle('ist-mitte', li.dataset.id === aktuell.id));
}

function zurMitteRollen(spieler, weich) {
  const li = haengerVon(spieler);
  if (!li) return;
  const ziel = li.offsetLeft + li.offsetWidth / 2 - stange.clientWidth / 2;
  stange.scrollTo({ left: ziel, behavior: weich && !reduziert.matches ? 'smooth' : 'auto' });
}

/* ---------- Stange bewegen: Pfeile, Pfeiltasten, Ziehen mit der Maus (Touch wischt nativ) ---------- */
function nachbarRollen(richtung) {
  if (zustand !== 'geschlossen' || !aktuell) return;
  const i = liste.indexOf(aktuell) + richtung;
  if (i < 0 || i >= liste.length) return;
  zurMitteRollen(liste[i], true);
  aktuellSetzen(liste[i]);
}
pfeilLinks.addEventListener('click', () => nachbarRollen(-1));
pfeilRechts.addEventListener('click', () => nachbarRollen(1));

function pfeileAktualisieren() {
  const offen = zustand !== 'geschlossen';
  const i = aktuell ? liste.indexOf(aktuell) : -1;
  pfeilLinks.disabled = offen || i <= 0;                       // bei offener Karte für Maus und Tastatur aus (A07)
  pfeilRechts.disabled = offen || i < 0 || i >= liste.length - 1;
  pfeilLinks.setAttribute('aria-hidden', String(offen));
  pfeilRechts.setAttribute('aria-hidden', String(offen));
}

let zieh = null;
stange.addEventListener('pointerdown', e => {
  if (zustand !== 'geschlossen' || e.button !== 0 || e.pointerType !== 'mouse') return;
  zieh = { x: e.clientX, start: stange.scrollLeft, bewegt: false, id: e.pointerId };
});
stange.addEventListener('pointermove', e => {
  if (!zieh || e.pointerId !== zieh.id) return;
  const dx = e.clientX - zieh.x;
  if (!zieh.bewegt && Math.abs(dx) > 6) { zieh.bewegt = true; stange.classList.add('zieht'); stange.setPointerCapture(e.pointerId); }
  if (zieh.bewegt) stange.scrollLeft = zieh.start - dx;
});
const ziehEnde = () => {
  if (!zieh) return;
  const bewegt = zieh.bewegt;
  zieh = null;
  if (bewegt) {
    setTimeout(() => stange.classList.remove('zieht'), 0);   // der folgende Klick gilt noch als Zug
    if (aktuell) zurMitteRollen(aktuell, true);
  }
};
stange.addEventListener('pointerup', ziehEnde);
stange.addEventListener('pointercancel', ziehEnde);
innen.addEventListener('click', e => { if (stange.classList.contains('zieht')) { e.stopPropagation(); e.preventDefault(); } }, true);

/* ---------- Kamera: Stange um das gewählte Trikot vergrößern und verschieben ---------- */
function kameraAuf(spieler) {
  const li = haengerVon(spieler);
  if (!li) return;
  const zoom = parseFloat(getComputedStyle(stange).getPropertyValue('--kamera-zoom')) || 1.3;
  const breite = stange.clientWidth, hoehe = stange.clientHeight;
  const trikot = li.querySelector('.trikot-haengend');
  const hx = li.offsetLeft + li.offsetWidth / 2;
  const hy = li.offsetTop + trikot.offsetTop + trikot.offsetHeight * 0.42;
  const zielX = desktop.matches ? (breite - 440) / 2 : breite / 2;   // Desktop: Fläche links neben der Karte
  const zielY = desktop.matches ? hoehe * 0.47 : hoehe * 0.29;        // Mobil: obere Hälfte, Karte darunter
  innen.style.transform = `translate(${(zielX + stange.scrollLeft - hx * zoom).toFixed(1)}px, ${(zielY - hy * zoom).toFixed(1)}px) scale(${zoom})`;
}
function kameraZurueck() { innen.style.transform = ''; }

/* ---------- Öffnen ---------- */
function oeffnen(spieler) {
  const li = haengerVon(spieler);
  if (!li) return;
  const kennung = neuerVorgang();
  // Reste eines laufenden Schließens sofort beenden
  innen.querySelectorAll('.haenger.gewaehlt').forEach(h => h.classList.remove('gewaehlt'));
  zuletztFokussiert = li.querySelector('button');
  zustand = 'oeffnend';
  gewaehlt = spieler;
  szene.classList.add('offen');
  li.classList.add('gewaehlt');
  kameraAuf(spieler);
  karte.hidden = false;
  karteFuellen(spieler);
  history.replaceState(null, '', `#spieler=${encodeURIComponent(spieler.id)}`);
  aktuellSetzen(spieler);
  naechsterFrame(kennung, () => {
    szene.classList.add('aktiv');
    karte.classList.add('offen');
    document.getElementById('karte-zurueck').focus({ preventScroll: true });
    spaeter(kennung, reduziert.matches ? 150 : 900, () => { zustand = 'offen'; });
  });
}

/* ---------- Schließen: Karte raus, dann Kamera zurück und Trikot zurückdrehen ---------- */
function schliessen() {
  if (zustand === 'geschlossen' || zustand === 'schliessend') return;
  const kennung = neuerVorgang();
  const spieler = gewaehlt;
  const li = haengerVon(spieler);
  zustand = 'schliessend';
  karte.classList.remove('offen');
  szene.classList.remove('aktiv');
  if (location.hash.startsWith('#spieler=')) history.replaceState(null, '', location.pathname + location.search);
  const kamera = () => { li?.classList.remove('gewaehlt'); kameraZurueck(); };
  const fertig = () => {
    zustand = 'geschlossen';
    gewaehlt = null;
    szene.classList.remove('offen');
    karte.hidden = true;
    if (spieler) zurMitteRollen(spieler, false);
    aktuellSetzen(spieler);
    if (zuletztFokussiert?.isConnected) zuletztFokussiert.focus({ preventScroll: true });
  };
  if (reduziert.matches) { kamera(); fertig(); return; }
  spaeter(kennung, 140, kamera);
  spaeter(kennung, 140 + 600, fertig);
}

/* Ohne Animation in den Grundzustand (Filterwechsel, Fehlerfälle) */
function sofortSchliessen() {
  neuerVorgang();
  zustand = 'geschlossen';
  gewaehlt = null;
  karte.classList.remove('offen');
  karte.hidden = true;
  szene.classList.remove('aktiv', 'offen');
  innen.querySelectorAll('.haenger.gewaehlt').forEach(h => h.classList.remove('gewaehlt'));
  kameraZurueck();
  if (location.hash.startsWith('#spieler=')) history.replaceState(null, '', location.pathname + location.search);
}

/* ---------- Wechsel: Kamera schwenkt zum Nachbarn ---------- */
function wechseln(spieler) {
  if (zustand === 'geschlossen' || zustand === 'schliessend') { if (spieler) oeffnen(spieler); return; }
  const li = haengerVon(spieler);
  if (!li || spieler === gewaehlt) return;
  const kennung = neuerVorgang();
  haengerVon(gewaehlt)?.classList.remove('gewaehlt');
  gewaehlt = spieler;
  zustand = 'oeffnend';
  li.classList.add('gewaehlt');
  kameraAuf(spieler);
  history.replaceState(null, '', `#spieler=${encodeURIComponent(spieler.id)}`);
  aktuellSetzen(spieler);
  karteKoerper.classList.add('wechsel');
  spaeter(kennung, reduziert.matches ? 0 : 220, () => { karteFuellen(spieler); karteKoerper.classList.remove('wechsel'); });
  spaeter(kennung, reduziert.matches ? 150 : 700, () => { zustand = 'offen'; });
}

const nachbar = richtung => gewaehlt ? liste[(liste.indexOf(gewaehlt) + richtung + liste.length) % liste.length] : null;
document.getElementById('karte-zurueck').addEventListener('click', () => schliessen());
document.getElementById('karte-vorher').addEventListener('click', () => wechseln(nachbar(-1)));
document.getElementById('karte-weiter').addEventListener('click', () => wechseln(nachbar(1)));
document.getElementById('karte-klappen').addEventListener('click', e => {
  const zu = karte.classList.toggle('eingeklappt');
  e.currentTarget.setAttribute('aria-expanded', String(!zu));
  e.currentTarget.setAttribute('aria-label', zu ? T.ausklappen : T.einklappen);
});
/* Link zur offenen Spielerkarte kopieren */
document.getElementById('karte-teilen').addEventListener('click', async e => {
  if (!gewaehlt) return;
  const knopf = e.currentTarget;
  const url = `${location.origin}${location.pathname}#spieler=${encodeURIComponent(gewaehlt.id)}`;
  try {
    if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(url);
    else { const ta = Object.assign(document.createElement('textarea'), { value: url }); document.body.append(ta); ta.select(); document.execCommand('copy'); ta.remove(); }
    knopf.classList.add('kopiert'); knopf.title = T.kopiert;
    setTimeout(() => { knopf.classList.remove('kopiert'); knopf.title = T.linkKopieren; }, 1600);
  } catch { prompt(T.linkKopieren, url); }
});

/* Tastatur: nur wenn der Fokus im Modul oder auf der Seite selbst liegt (kein Einfluss auf andere Bereiche) */
addEventListener('keydown', e => {
  const ziel = e.target;
  if (ziel instanceof Element && !(ziel === document.body || modul.contains(ziel))) return;
  if (ziel instanceof Element && ziel.matches('input, textarea, select')) return;
  if (zustand === 'geschlossen') {
    if (e.key === 'ArrowRight') { e.preventDefault(); nachbarRollen(1); }
    if (e.key === 'ArrowLeft') { e.preventDefault(); nachbarRollen(-1); }
    return;
  }
  if (e.key === 'Escape') schliessen();
  if (e.key === 'ArrowRight') { e.preventDefault(); wechseln(nachbar(1)); }
  if (e.key === 'ArrowLeft') { e.preventDefault(); wechseln(nachbar(-1)); }
});

/* Direktlink #spieler=<id>: gleicher Weg wie die normale Bedienung (A05) */
function ausHashOeffnen() {
  if (!location.hash.startsWith('#spieler=')) { if (zustand !== 'geschlossen') schliessen(); return; }
  let id;
  try { id = decodeURIComponent(location.hash.slice('#spieler='.length)); } catch { return; }
  const spieler = liste.find(p => p.id === id);
  if (!spieler) return;                                   // unbekannt, inaktiv oder weggefiltert: keine Änderung
  if (zustand === 'geschlossen' || zustand === 'schliessend') oeffnen(spieler);
  else if (spieler !== gewaehlt) wechseln(spieler);
}

/* ---------- Karte ---------- */
function nameMarkup(name) {
  const teile = name.trim().split(/\s+/);
  if (teile.length < 2) return `<strong>${escapeHtml(name)}</strong>`;
  const nach = teile.pop();
  return `${escapeHtml(teile.join(' '))} <strong>${escapeHtml(nach)}</strong>`;
}

function karteFuellen(p) {
  document.getElementById('karte-zaehler').textContent = `${liste.indexOf(p) + 1} / ${liste.length}`;
  const zeilen = [];
  if (p.nationality) zeilen.push([T.nationalitaet, escapeHtml(p.nationality)]);
  zeilen.push([T.status, `<span class="status-punkt" data-status="${escapeHtml(p.status)}"></span>${statusLabel(p.status, T.statusWerte)}`]);
  if (p.birthYear) zeilen.push([T.jahrgang, String(p.birthYear)]);
  if (p.stats) {
    const s = p.stats;
    if (s.games !== undefined) zeilen.push([T.spiele, `<b>${s.games}</b>${s.goals !== undefined ? ` · ${s.goals} ${T.tore}` : ''}`]);
    else if (s.goals !== undefined) zeilen.push([T.tore, `<b>${s.goals}</b>`]);
    if (s.assists !== undefined) zeilen.push([T.assists, `<b>${s.assists}</b>`]);
    if (s.penaltyMinutes !== undefined) zeilen.push([T.strafzeiten, `<b>${s.penaltyMinutes}</b>`]);
  }
  karteKoerper.innerHTML = `
    <div class="karte-spieler">
      ${p.photo ? `<img class="karte-foto" src="${escapeHtml(p.photo)}" alt="${T.foto} ${escapeHtml(p.name)}">` : ''}
      <span class="karte-nat" aria-hidden="true">${escapeHtml(p.nationality)}</span>
      <span class="karte-position">${escapeHtml(p.position)}</span>
      <span class="karte-nummer" aria-label="${T.rueckennummer} ${p.number}">${p.number}</span>
      <h2 class="karte-name" id="karte-name">${nameMarkup(p.name)}</h2>
    </div>
    <dl class="karte-zeilen">${zeilen.map(([k, v], i) => `<div style="--stufe:${i}"><dt>${k}</dt><dd>${v}</dd></div>`).join('')}</dl>
    ${p.bio ? `<section class="karte-profil"><h3>${T.profil}</h3><p>${escapeHtml(p.bio)}</p></section>` : ''}`;
}
