/* Kader-Manager – gemeinsame Datenschicht für Kaderseite und Admin.
   Quelle: daten/kader.json. Änderungen aus dem Admin liegen im localStorage,
   bis sie als JSON exportiert und committet werden (statische Seite, kein Backend).
   Für ein Backend genügt es, laden() und speichern() auf fetch/POST umzustellen. */

export const DATEN_URL = new URL('./daten/kader.json', import.meta.url).href;
export const SPEICHER_SCHLUESSEL = 'kaderManager.daten.v1';

export const STATUS = {
  active:   { label: 'Aktiv',       oeffentlich: true },
  injured:  { label: 'Verletzt',    oeffentlich: true },
  inactive: { label: 'Deaktiviert', oeffentlich: false }
};

export const STATISTIK_FELDER = [
  ['games', 'Spiele'],
  ['goals', 'Tore'],
  ['assists', 'Assists'],
  ['penaltyMinutes', 'Strafzeiten']
];

/** Lädt die Kaderdaten. Lokale Admin-Änderungen haben Vorrang, außer bei nurDatei=true. */
export async function laden({ nurDatei = false } = {}) {
  if (!nurDatei) {
    const lokal = lokalLesen();
    if (lokal) return { daten: lokal, quelle: 'lokal' };
  }
  const antwort = await fetch(DATEN_URL, { cache: 'no-store' });
  if (!antwort.ok) throw new Error(`Kaderdaten nicht ladbar (${antwort.status})`);
  const daten = pruefen(await antwort.json());
  return { daten, quelle: 'datei' };
}

export function lokalLesen() {
  try {
    const roh = localStorage.getItem(SPEICHER_SCHLUESSEL);
    return roh ? pruefen(JSON.parse(roh)) : null;
  } catch { return null; }
}

export function lokalSchreiben(daten) {
  localStorage.setItem(SPEICHER_SCHLUESSEL, JSON.stringify(pruefen(daten), null, 2));
}

export function lokalLoeschen() {
  localStorage.removeItem(SPEICHER_SCHLUESSEL);
}

/** Prüft die Grundstruktur und normalisiert Felder. Wirft bei unbrauchbaren Daten. */
export function pruefen(daten) {
  if (!daten || typeof daten !== 'object' || !Array.isArray(daten.players)) {
    throw new Error('Kaderdaten: Feld "players" fehlt oder ist keine Liste.');
  }
  const team = Object.assign({ name: 'Kader', short: '', season: '' }, daten.team || {});
  team.name = String(team.name || 'Kader').slice(0, 80);
  team.language = team.language === 'uk' ? 'uk' : 'de';
  team.short = String(team.short || '').slice(0, 12);
  team.season = String(team.season || '').slice(0, 20);
  team.colors = farbenPruefen(team.colors);
  team.tilt = zahl(team.tilt, 30, 85, 50);   // Schrägstellung der Trikots an der Stange in Grad
  if (team.jerseyAlternatives && typeof team.jerseyAlternatives === 'object') {
    const alt = {};
    for (const [k, v] of Object.entries(team.jerseyAlternatives)) { const j = trikotKonfigPruefen(v); if (j) alt[k] = j; }
    team.jerseyAlternatives = alt;
  } else {
    delete team.jerseyAlternatives;
  }
  const jersey = trikotKonfigPruefen(team.jersey);
  if (jersey) team.jersey = jersey; else delete team.jersey;

  const players = daten.players.map(spielerNormalisieren);
  // Jeder Datensatz muss für sich gültig sein, IDs müssen eindeutig sein (A06)
  const fehler = [];
  const ids = new Set();
  players.forEach((p, i) => {
    const f = spielerFehler(p, players);
    if (!/^[a-z0-9][a-z0-9-]{0,60}$/.test(p.id)) f.push(`ID „${p.id}“ ist ungültig (nur a–z, 0–9, Bindestrich).`);
    if (ids.has(p.id)) f.push(`ID „${p.id}“ ist doppelt.`);
    ids.add(p.id);
    if (f.length) fehler.push(`Spieler ${i + 1} (${p.name || 'ohne Namen'}): ${f.join(' ')}`);
  });
  if (fehler.length) throw new Error('Kaderdaten ungültig. ' + fehler.join(' | '));
  return { team, players };
}

const FARBE = /^#[0-9a-f]{3}([0-9a-f]{3})?([0-9a-f]{2})?$/i;
function farbe(wert, standard) { return typeof wert === 'string' && FARBE.test(wert.trim()) ? wert.trim() : standard; }
function farbenPruefen(c) {
  c = c && typeof c === 'object' ? c : {};
  return { primary: farbe(c.primary, '#0B3D91'), secondary: farbe(c.secondary, '#F2C230'), text: farbe(c.text, '#FFFFFF') };
}
function zahl(wert, min, max, standard) {
  const n = typeof wert === 'number' ? wert : Number(wert);
  return Number.isFinite(n) && n >= min && n <= max ? n : standard;
}
/** Trikotbild-Konfiguration: nur geprüfte Zahlen, Farben und ein harmloser relativer Bildpfad (A03). */
export function trikotKonfigPruefen(j) {
  if (!j || typeof j !== 'object' || typeof j.back !== 'string') return null;
  const back = j.back.trim();
  if (!/^[\w./-]{1,200}$/.test(back) || back.includes('..')) return null;
  return {
    back,
    nameY: zahl(j.nameY, 0, 440, 190),
    numberY: zahl(j.numberY, 0, 440, 345),
    nameSize: zahl(j.nameSize, 8, 120, 30),
    numberSize: zahl(j.numberSize, 20, 320, 150),
    nameColor: farbe(j.nameColor, ''),
    numberColor: farbe(j.numberColor, '')
  };
}

export function spielerNormalisieren(p) {
  const s = {
    id: String(p.id || idAus(p.name, p.number)).trim().toLowerCase(),
    name: String(p.name || '').trim().slice(0, 60),
    number: Number.parseInt(p.number, 10),
    position: String(p.position || '').trim(),
    status: STATUS[p.status] ? p.status : 'active',
    nationality: String(p.nationality || '').trim().toUpperCase(),
    photo: String(p.photo || '').trim()
  };
  if (p.bio && String(p.bio).trim()) s.bio = String(p.bio).trim();
  if (p.birthYear !== undefined && p.birthYear !== '' && p.birthYear !== null) {
    const j = Number.parseInt(p.birthYear, 10);
    if (Number.isFinite(j)) s.birthYear = j;
  }
  if (p.stats && typeof p.stats === 'object') {
    const stats = {};
    for (const [feld] of STATISTIK_FELDER) {
      const w = p.stats[feld];
      if (w === undefined || w === null || w === '') continue;
      const n = Number.parseInt(w, 10);
      if (Number.isFinite(n)) stats[feld] = n;
    }
    if (Object.keys(stats).length) s.stats = stats;
  }
  return s;
}

/** Fehlerliste für einen Spieler; leer = gültig. andere = restliche Spieler (für die Nummernprüfung). */
export function spielerFehler(s, andere = []) {
  const fehler = [];
  if (!s.name) fehler.push('Name fehlt.');
  if (!Number.isInteger(s.number) || s.number < 0 || s.number > 99) fehler.push('Rückennummer muss zwischen 0 und 99 liegen.');
  if (andere.some(a => a.id !== s.id && a.number === s.number && a.status !== 'inactive' && s.status !== 'inactive')) {
    fehler.push(`Rückennummer ${s.number} ist bei einem aktiven Spieler schon vergeben.`);
  }
  if (!s.position) fehler.push('Position fehlt.');
  if (s.nationality && !/^[A-Z]{2,3}$/.test(s.nationality)) fehler.push('Nationalität als Länderkürzel (z. B. UA, DE).');
  const jahr = new Date().getFullYear();
  if (s.birthYear !== undefined && (s.birthYear < 1900 || s.birthYear > jahr)) fehler.push('Geburtsjahr unplausibel.');
  for (const [feld, label] of STATISTIK_FELDER) {
    if (s.stats && s.stats[feld] !== undefined && s.stats[feld] < 0) fehler.push(`${label}: keine negativen Werte.`);
  }
  return fehler;
}

export function idAus(name, number) {
  const basis = String(name || 'spieler').toLowerCase()
    .replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue').replace(/ß/g, 'ss')
    .normalize('NFD').replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  return number !== undefined && number !== '' ? `${basis}-${number}` : basis;
}

/** Setzt die Teamfarben als CSS-Variablen und merkt sich das Trikotbild des Teams. */
let trikotBild = null;
export function teamfarbenSetzen(team, wurzel = document.documentElement) {
  wurzel.style.setProperty('--team-1', team.colors.primary);
  wurzel.style.setProperty('--team-2', team.colors.secondary);
  wurzel.style.setProperty('--team-text', team.colors.text);
  trikotBild = trikotKonfigPruefen(team.jersey);
  wurzel.style.setProperty('--trikot-nummer', trikotBild?.numberColor || team.colors.secondary);
  wurzel.style.setProperty('--trikot-name', trikotBild?.nameColor || team.colors.text);
}

/** Trikot (Rückansicht) als SVG-Markup; Nummer und Name kommen aus den Spielerdaten.
    mitHaenger zeichnet Bügel und Haken darüber (für die Kleiderstange). */
export function trikotSvg(spieler, { mitName = true, beschriftung = true, mitHaenger = false } = {}) {
  const nummer = Number.isInteger(spieler.number) ? String(spieler.number) : '';
  const name = (spieler.name || '').toUpperCase();
  const basisNummer = trikotBild ? trikotBild.numberSize : 150;
  const basisName = trikotBild ? trikotBild.nameSize : 30;
  // Nummer: immer gleiche Höhe; zweistellige Nummern werden auf die Rückenbreite eingepasst (max. 220 von 400)
  // Nummer: immer gleiche Höhe, schlank gesetzt (Glyphen um ca. 15 % schmaler als die Schrift), max. 200 von 400 breit
  const nummerGroesse = basisNummer;
  const nummerBreite = Math.min(200, Math.round(nummer.length * basisNummer * 0.44));
  const nummerPassung = nummer ? ` textLength="${nummerBreite}" lengthAdjust="spacingAndGlyphs"` : '';
  // Name: immer gleiche Schriftgröße; lange Namen werden enger gesetzt (max. 236 von 400), nicht kleiner
  const nameGroesse = basisName;
  const nameBreite = Math.round(name.length * basisName * 0.6);
  const namePassung = nameBreite > 200 ? ` textLength="200" lengthAdjust="spacingAndGlyphs"` : '';
  const nameY = trikotBild ? trikotBild.nameY : 190;
  const nummerY = trikotBild ? trikotBild.numberY : (mitName ? 345 : 300);
  const titel = beschriftung ? `<title>Trikot ${escapeHtml(spieler.name)}, Nummer ${nummer}</title>` : '';
  const aria = beschriftung ? 'role="img"' : 'aria-hidden="true"';
  const id = String(spieler.id || 'x').replace(/[^a-z0-9-]/gi, '') || 'x';
  const viewBox = mitHaenger ? '0 -96 400 536' : '0 0 400 440';
  const haenger = mitHaenger ? `
    <g class="trikot-haenger-form">
      <path d="M200 -92 a14 14 0 1 1 0 28 a14 14 0 1 1 0 -28 M200 -64 V-40" fill="none" stroke="#9a9a9a" stroke-width="5" stroke-linecap="round"/>
      <path d="M200 -40 L96 30 Q200 10 304 30 Z" fill="#2b2622" stroke="#4a403a" stroke-width="3" stroke-linejoin="round"/>
    </g>` : '';
  return `<svg viewBox="${viewBox}" ${aria} focusable="false">${titel}
    <defs>
      <linearGradient id="stoff-${id}" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stop-color="#000" stop-opacity=".28"/>
        <stop offset=".18" stop-color="#000" stop-opacity="0"/>
        <stop offset=".5" stop-color="#fff" stop-opacity=".07"/>
        <stop offset=".82" stop-color="#000" stop-opacity="0"/>
        <stop offset="1" stop-color="#000" stop-opacity=".3"/>
      </linearGradient>
      <linearGradient id="licht-${id}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#fff" stop-opacity=".16"/>
        <stop offset=".35" stop-color="#fff" stop-opacity="0"/>
        <stop offset="1" stop-color="#000" stop-opacity=".22"/>
      </linearGradient>
      <linearGradient id="falten-${id}" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stop-color="#000" stop-opacity="0"/>
        <stop offset=".3" stop-color="#000" stop-opacity=".08"/>
        <stop offset=".34" stop-color="#000" stop-opacity="0"/>
        <stop offset=".62" stop-color="#000" stop-opacity=".07"/>
        <stop offset=".68" stop-color="#000" stop-opacity="0"/>
        <stop offset="1" stop-color="#000" stop-opacity="0"/>
      </linearGradient>
    </defs>
    ${haenger}
    ${trikotBild ? `<image class="trikot-bild" href="${escapeHtml(trikotBild.back)}" x="0" y="0" width="400" height="440" preserveAspectRatio="xMidYMid meet"/>` : `<g class="trikot-form">
      <path d="M118 36 L164 18 Q200 52 236 18 L282 36 L372 118 L326 166 L300 142 L300 412 Q300 424 288 424 L112 424 Q100 424 100 412 L100 142 L74 166 L28 118 Z" fill="var(--team-1)" stroke="rgba(0,0,0,.35)" stroke-width="3" stroke-linejoin="round"/>
      <path d="M118 36 L164 18 Q200 52 236 18 L282 36 L372 118 L326 166 L300 142 L300 412 Q300 424 288 424 L112 424 Q100 424 100 412 L100 142 L74 166 L28 118 Z" fill="url(#stoff-${id})"/>
      <path d="M118 36 L164 18 Q200 52 236 18 L282 36 L372 118 L326 166 L300 142 L300 412 Q300 424 288 424 L112 424 Q100 424 100 412 L100 142 L74 166 L28 118 Z" fill="url(#licht-${id})"/>
      <path d="M100 142 L300 142 L300 412 Q300 424 288 424 L112 424 Q100 424 100 412 Z" fill="url(#falten-${id})"/>
      <path d="M164 18 Q200 52 236 18 Q200 70 164 18 Z" fill="rgba(0,0,0,.28)"/>
      <path d="M160 20 Q200 56 240 20" fill="none" stroke="var(--team-2)" stroke-width="6" stroke-linecap="round"/>
      <path d="M28 118 L46 100 L92 148 L74 166 Z M372 118 L354 100 L308 148 L326 166 Z" fill="var(--team-2)" opacity=".95"/>
      <path d="M100 404 L300 404 L300 412 Q300 424 288 424 L112 424 Q100 424 100 412 Z" fill="var(--team-2)" opacity=".95"/>
      <path d="M118 36 L282 36" stroke="rgba(255,255,255,.12)" stroke-width="2"/>
    </g>`}
    <defs>
      <linearGradient id="druck-${id}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#fff" stop-opacity=".16"/>
        <stop offset=".5" stop-color="#fff" stop-opacity="0"/>
        <stop offset="1" stop-color="#000" stop-opacity=".26"/>
      </linearGradient>
    </defs>
    <g class="trikot-druck">
      <text class="trikot-nummer" x="200" y="${nummerY}" text-anchor="middle" font-size="${nummerGroesse}"${nummerPassung}>${escapeHtml(nummer)}</text>
      <text class="trikot-nummer trikot-licht" x="200" y="${nummerY}" text-anchor="middle" font-size="${nummerGroesse}"${nummerPassung} style="fill:url(#druck-${id})">${escapeHtml(nummer)}</text>
    </g>
    ${mitName ? `<g class="trikot-beschriftung">
      <text class="trikot-name" x="200" y="${nameY}" text-anchor="middle" font-size="${nameGroesse}"${namePassung}>${escapeHtml(name)}</text>
      <text class="trikot-name trikot-licht" x="200" y="${nameY}" text-anchor="middle" font-size="${nameGroesse}"${namePassung} style="fill:url(#druck-${id})">${escapeHtml(name)}</text>
    </g>` : ''}
  </svg>`;
}

export function escapeHtml(text) {
  return String(text ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

export function statusLabel(status, werte) {
  if (werte && werte[status]) return werte[status];
  return (STATUS[status] || STATUS.active).label;
}

/** Wechselt das aktive Trikotbild (Heim = team.jersey, sonst Schlüssel aus team.jerseyAlternatives). */
export function trikotWaehlen(team, schluessel, wurzel = document.documentElement) {
  const konfig = schluessel === 'heim' ? team.jersey : team.jerseyAlternatives?.[schluessel];
  trikotBild = trikotKonfigPruefen(konfig) || trikotKonfigPruefen(team.jersey);
  wurzel.style.setProperty('--trikot-nummer', trikotBild?.numberColor || team.colors.secondary);
  wurzel.style.setProperty('--trikot-name', trikotBild?.nameColor || team.colors.text);
}

export function flaggenText(kuerzel) {
  // Länderkürzel als Text; Flaggen-Emoji sind auf Windows nicht verfügbar, daher bewusst nur Kürzel.
  return kuerzel || '';
}
