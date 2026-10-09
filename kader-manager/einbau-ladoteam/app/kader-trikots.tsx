'use client';
/* KFK LadoTeam – Ansicht „Trikots“: die Trikot-Animation des Kader-Moduls, gespeist aus dem Teamstand der App.
   Neue Datei. Benötigt die Dateien unter public/assets/kader/ (siehe UEBERGABE_FALK.md, Weg 3).
   Die Spieler kommen aus snap.state.players (Name, nameUk, white, black, position, status), die Sprache aus
   dem Sprachschalter der App. Das Modul schreibt keinen Hash und verändert keinen Zustand der App. */
import React, {useEffect, useRef} from 'react';
import {useApp} from './ui';

const BASIS = '/assets/kader/';
const TEAM = {
  name: 'КФК', short: 'KFK', season: '', tilt: 50,
  colors: {primary: '#C9A24A', secondary: '#C9A24A', text: '#FFFFFF'},
  jersey: {back: BASIS + 'fotos/trikot-kfk-schwarz.png', nameY: 102, numberY: 268, nameSize: 30, numberSize: 150, nameColor: '#B28A47', numberColor: '#B28A47'},
  jerseyAlternatives: {weiss: {back: BASIS + 'fotos/trikot-kfk-weiss.png', nameY: 102, numberY: 268, nameSize: 30, numberSize: 150, nameColor: '#161616', numberColor: '#161616'}},
};

type Modul = {
  kaderMounten: (wurzel: HTMLElement, optionen: {daten: unknown; sprache: string; hash: boolean}) => {entfernen: () => void};
  pruefen: (daten: unknown) => unknown;
  ausLadoTeam: (quelle: unknown, bisher?: unknown[]) => unknown[];
};
let modulVersprechen: Promise<Modul> | null = null;
function modulLaden(): Promise<Modul> {
  // Das Modul liegt als fertige ES-Module-Dateien unter /assets/kader/ und wird am Bundler vorbei geladen.
  if (!modulVersprechen) {
    const laden = new Function('u', 'return import(u)') as (u: string) => Promise<any>;
    modulVersprechen = Promise.all([laden(BASIS + 'kader-einbettung.js'), laden(BASIS + 'kader-daten.js')])
      .then(([e, d]) => ({kaderMounten: e.kaderMounten, pruefen: d.pruefen, ausLadoTeam: d.ausLadoTeam}));
  }
  return modulVersprechen;
}

export function KaderTrikots() {
  const {snap, lang, t} = useApp();
  const wurzel = useRef<HTMLDivElement>(null);
  // Nur die Felder, die die Ansicht braucht; Namen hier unlokalisiert, die Ansicht wählt selbst nach lang
  const spieler = JSON.stringify(snap.state.players.map(p => ({
    id: p.id, name: p.originalName || p.name, nameUk: p.nameUk || '', position: p.position, detail: p.detail,
    white: p.white, black: p.black, status: p.status,
  })));
  useEffect(() => {
    let instanz: {entfernen: () => void} | null = null, aktiv = true;
    const el = wurzel.current;
    if (!el) return;
    modulLaden().then(m => {
      if (!aktiv || !el.isConnected) return;
      const daten = m.pruefen({team: {...TEAM, season: snap.state.settings.teamName}, players: m.ausLadoTeam({format: 'kfk-kader', players: JSON.parse(spieler)})});
      instanz = m.kaderMounten(el, {daten, sprache: lang, hash: false});
    }).catch(e => { if (el) el.textContent = 'Trikotansicht nicht ladbar: ' + (e instanceof Error ? e.message : String(e)); });
    return () => { aktiv = false; instanz?.entfernen(); };
  }, [spieler, lang, snap.state.settings.teamName]);
  return <section className="panel" aria-label={t('trikots')}>
    <link rel="stylesheet" href={BASIS + 'kader-einbettung.css'}/>
    <div ref={wurzel} className="kader-wurzel" style={{borderRadius: 18, overflow: 'hidden', background: '#0e0b0a'}}/>
  </section>;
}
