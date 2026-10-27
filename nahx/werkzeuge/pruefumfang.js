/* Prüfumfang von 614 One (FSH DocumentCheck) für die NAHX-Produktseite lesen (2026-10-27).
 *
 * Lädt src/Code.js unverändert über die Testhilfe des Prüftool-Repos (vm-Kontext, Google-Dienste nachgebildet)
 * und schreibt nahx/inhalt/pruefumfang.json. Liest nur, ändert nichts am Prüftool.
 *
 *   node nahx/werkzeuge/pruefumfang.js /pfad/zu/fsh-documentcheck [commit]
 *
 * „belegt“ = Pilot-Dokumentart mit vollständigem und fehlerhaftem Referenzdokument (tests/pilot/, Handbuch §10).
 */
'use strict';
const fs = require('fs');
const path = require('path');

const repo = process.argv[2];
if (!repo) { console.error('Aufruf: node pruefumfang.js <fsh-documentcheck> [commit]'); process.exit(2); }
const { ladeCode } = require(path.join(repo, 'tests', 'hilfen', 'ladeCode.js'));
const c = ladeCode();
const w = (a) => c.wert(a);

const BELEGT = ['Betriebsanleitung', 'CE-Konformitätserklärung', 'Risikobeurteilung', 'Wartungsanleitung', 'Schaltplan / Elektrodokumentation'];
// Gegenprobe: zu jeder belegten Art liegen *_voll.txt und *_fehler.txt unter tests/pilot/
const pilot = fs.readdirSync(path.join(repo, 'tests', 'pilot'));
if (pilot.filter(f => /_(voll|fehler)\.txt$/.test(f)).length !== BELEGT.length * 2) throw new Error('Referenzdokumente passen nicht zu BELEGT');

const produktarten = w('PRODUCT_TYPES').slice();
const dokumentarten = w('DOCUMENT_TYPES').slice();
const KK = w('KAPITEL_KATALOG');
const CP = w('CHECK_PROFILES');
const NB = w('NORM_BASE');
const RB = w('RECHTSBEREICHE');

const dok = dokumentarten.map(name => {
  const p = c.rufe('profilFuer_', name);
  const kapitel = (p.kapitel || []).map(k => KK[k] || k);
  const bereiche = (p.regeln || []).filter(r => CP[r] && !CP[r].alwaysOn && !CP[r].ausgeblendet).map(r => CP[r].label);
  const normen = (p.normen || []).map(n => ({ quelle: n.quelle, ausgabe: n.ausgabe || null, relevanz: n.relevanz || '' }));
  const basisDok = NB[name] || [];
  return { name, kapitel, bereiche, normen, normbasis_dok: basisDok, belegt: BELEGT.includes(name), nur_vorpruefung: !(p.kapitel || []).length || name === 'Sonstiges' };
});

const normbasis = {};
produktarten.forEach(pa => { normbasis[pa] = Array.from(new Set([...(NB.generic || []), ...(NB[pa] || [])])); });

const rechtsbereiche = RB.map(r => ({
  name: r.titel,
  produkte: produktarten.filter(pa => { try { return !!r.gilt(pa, ''); } catch (e) { return false; } }),
  auch_text: /text/.test(String(r.gilt)),
  nachweise: (r.nachweise || []).length
}));

const aus = {
  _hinweis: 'Erzeugt von nahx/werkzeuge/pruefumfang.js aus FSH DocumentCheck (Code.js, lokal geladen). Nicht von Hand ändern.',
  stand: { commit: process.argv[3] || '', datum: new Date().toISOString().slice(0, 10), quelle: 'FSH DocumentCheck src/Code.js' },
  produktarten, dokumentarten: dok, normbasis, rechtsbereiche,
  zaehler: { produktarten: produktarten.length, dokumentarten: dok.length, belegt: dok.filter(d => d.belegt).length,
             pruefbereiche_waehlbar: Object.values(CP).filter(x => !x.alwaysOn && !x.ausgeblendet).length, rechtsbereiche: RB.length }
};
const ziel = path.join(__dirname, '..', 'inhalt', 'pruefumfang.json');
fs.writeFileSync(ziel, JSON.stringify(aus, null, 2), 'utf8');
console.log(JSON.stringify(aus.zaehler), '→', ziel);
dok.filter(d => !d.normen.length).forEach(d => console.log('ohne Profilnormen:', d.name));
dok.filter(d => d.nur_vorpruefung).forEach(d => console.log('nur Vorprüfung:', d.name));
rechtsbereiche.forEach(r => console.log('Rechtsbereich', r.name, '→', r.produkte.length, 'Produktarten', r.auch_text ? '(auch per Text)' : ''));
