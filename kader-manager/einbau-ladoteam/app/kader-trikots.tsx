'use client';
/* KFK LadoTeam – Ansicht „Trikots“: die Trikot-Animation des Kader-Moduls, gespeist aus dem Teamstand der App.
   Neue Datei. Benötigt die Dateien unter public/assets/kader/ (siehe UEBERGABE_FALK.md, Weg 3).
   Die Spieler kommen aus snap.state.players (Name, nameUk, white, black, position, status), die Sprache aus
   dem Sprachschalter der App. Das Modul schreibt keinen Hash und verändert keinen Zustand der App.
   Das Modul wird über ein <script type="module"> aus /assets/kader/ geladen (verträgt sich mit der
   Content-Security-Policy der App, kein eval). Ein Fehler in der Ansicht bleibt in der Ansicht (Error Boundary). */
import React, {useEffect, useRef, useState} from 'react';
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
declare global { interface Window { KaderTrikots?: Modul } }

let modulVersprechen: Promise<Modul> | null = null;
function modulLaden(): Promise<Modul> {
  if (window.KaderTrikots) return Promise.resolve(window.KaderTrikots);
  if (!modulVersprechen) {
    modulVersprechen = new Promise<Modul>((res, rej) => {
      const fertig = () => { if (window.KaderTrikots) res(window.KaderTrikots); else rej(new Error('Modul ohne Export')); };
      window.addEventListener('kader-trikots-bereit', fertig, {once: true});
      const s = document.createElement('script');
      s.type = 'module';
      s.src = BASIS + 'kader-global.js';
      s.onerror = () => rej(new Error('kader-global.js nicht ladbar'));
      document.head.appendChild(s);
      setTimeout(() => rej(new Error('Zeitüberschreitung beim Laden')), 15000);
    });
    modulVersprechen.catch(() => { modulVersprechen = null; });
  }
  return modulVersprechen;
}

class Schutz extends React.Component<{children: React.ReactNode}, {fehler: string}> {
  state = {fehler: ''};
  static getDerivedStateFromError(e: unknown) { return {fehler: e instanceof Error ? e.message : String(e)}; }
  render() { return this.state.fehler ? <div className="notice error" role="alert">Trikotansicht nicht verfügbar: {this.state.fehler}</div> : this.props.children; }
}

function Ansicht() {
  const {snap, lang} = useApp();
  const wurzel = useRef<HTMLDivElement>(null);
  const [fehler, setFehler] = useState('');
  // Nur die Felder, die die Ansicht braucht; Namen unlokalisiert, die Ansicht wählt selbst nach lang
  const spieler = JSON.stringify(snap.state.players.map(p => ({
    id: p.id, name: p.originalName || p.name, nameUk: p.nameUk || '', nameUkConfirmed: !!p.nameUkConfirmed,
    position: p.position, detail: p.detail, white: p.white, black: p.black, status: p.status,
  })));
  const teamName = snap.state.settings.teamName;   // Teamname aus den Einstellungen der App, keine Saison
  useEffect(() => {
    let instanz: {entfernen: () => void} | null = null, aktiv = true;
    const el = wurzel.current;
    if (!el) return;
    modulLaden().then(m => {
      if (!aktiv || !el.isConnected) return;
      const daten = m.pruefen({team: {...TEAM, name: teamName || TEAM.name, season: ''}, players: m.ausLadoTeam({format: 'kfk-kader', players: JSON.parse(spieler)})});
      instanz = m.kaderMounten(el, {daten, sprache: lang, hash: false});
      setFehler('');
    }).catch(e => { if (aktiv) setFehler(e instanceof Error ? e.message : String(e)); });
    return () => { aktiv = false; instanz?.entfernen(); };
  }, [spieler, lang, teamName]);
  return <>
    {fehler && <div className="notice error" role="alert">Trikotansicht nicht ladbar: {fehler}</div>}
    <div ref={wurzel} className="kader-wurzel" style={{borderRadius: 18, overflow: 'hidden', background: '#0e0b0a'}}/>
  </>;
}

export function KaderTrikots() {
  const {t} = useApp();
  return <section className="panel" aria-label={t('trikots')}>
    <link rel="stylesheet" href={BASIS + 'kader-einbettung.css'}/>
    <Schutz><Ansicht/></Schutz>
  </section>;
}
