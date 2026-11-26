// Regressionsprüfung: Laden, Regeltests, KI-Statistik, Kelle am Ball, Maus/Tastatur, Tricks, Torhüter, Parcours, freies Training, Spiel 5 gegen 5, Turnier, Editor, Tuning, HUD
// Aufruf: node regression.js [Filter]   (Filter = regulärer Ausdruck auf die Abschnittsnummer, z. B. "^(3|4)")
const { start } = require('./lib');
const fs = require('fs');
const erg = [];
const pruef = (name, ok, info = '') => { erg.push({ name, ok: !!ok, info }); console.log((ok ? 'OK   ' : 'FAIL ') + name + (info ? '  ' + info : '')); };
(async () => {
  const { b, p, logs } = await start({ w: 1280, h: 720, quali: 'niedrig', fans: 0.2, einst: { tutorial: true, wiederholung: false } });
  const st = () => p.evaluate(() => { const F = window.__fps, S = F.Spiel, s = S.schuetze, T = S.torwart; return { z: S.zustand, s: s.zustand, pos: [+s.pos.x.toFixed(2), +s.pos.z.toFixed(2)], vel: [+s.vel.x.toFixed(2), +s.vel.z.toFixed(2)], yaw: +s.yaw.toFixed(2), trick: s.trick && s.trick.name, zorro: s.zorro, kontrolle: s.kontrolle, power: +s.power.toFixed(2), ballY: +F.ball.p.y.toFixed(3), tw: T.zustand, twPos: [+T.pos.x.toFixed(2), +T.pos.z.toFixed(2)], erg: S.versuch && S.versuch.ergebnis && S.versuch.ergebnis.code }; });
  const screenOf = (z, y) => p.evaluate(([z, y]) => { const F = window.__fps; F.kamera.updateMatrixWorld(); const v = new F.V3(16.5, y, z).project(F.kamera); return { x: (v.x + 1) / 2 * innerWidth, y: (1 - v.y) / 2 * innerHeight }; }, [z, y]);
  const wf = (f, arg, ms = 30000) => p.waitForFunction(f, arg, { timeout: ms });
  const nur = process.argv[2] ? new RegExp(process.argv[2]) : null;
  const abschnitt = async (name, f) => { if (nur && !nur.test(name)) return; try { await f(); } catch (e) { let diag = ''; try { diag = await p.evaluate(() => { const F = window.__fps, a = document.activeElement, el = document.querySelector('#tuning [data-preset="arcade"]'), r = el.getBoundingClientRect(), o = document.elementFromPoint(r.left + 5, r.top + 5); return ' | aktiv=' + a.tagName + '#' + a.id + ' tuningOffen=' + F.TuningPanel.offen + ' klasse=' + document.getElementById('tuning').className + ' knopfX=' + Math.round(r.left) + ' oben=' + (o && (o.id || o.className || o.tagName)) + ' tasten=' + [...F.Eingabe.tasten].join(',') + ' zustand=' + F.Spiel.zustand; }); } catch (x) {} pruef(name + ' (Abbruch)', false, String(e.message).split('\n')[0] + diag); try { await p.evaluate(() => { const F = window.__fps; if (Math._r) Math.random = Math._r; F.Spiel.abbrechen(); if (F.TuningPanel.offen) F.TuningPanel.schliessen(); F.UI.hauptmenue(); }); } catch (x) {} } };
  // Auf simulierte Spielzeit warten statt auf die Uhr: im Headless-Browser setzt requestAnimationFrame gelegentlich über eine Sekunde aus
  const simWarten = async (sek) => { const t0 = await p.evaluate(() => window.__fps.Spiel.simZeit); await p.waitForFunction(([t0, sek]) => window.__fps.Spiel.simZeit >= t0 + sek || !!(window.__fps.Spiel.versuch && window.__fps.Spiel.versuch.ergebnis), [t0, sek], { timeout: 30000 }); };
  const zumMenue = async () => { await p.evaluate(() => { const F = window.__fps; F.Spiel.abbrechen(); F.UI.hauptmenue(); }); await p.waitForTimeout(150); };

  // 1) Regeltests
  await abschnitt('1) Regeltests', async () => {
  const rt = await p.evaluate(() => window.__fps.Regeltests.ausfuehren());
  pruef('Regeltests', rt.every(x => x.ok), `${rt.filter(x => x.ok).length}/${rt.length}` + rt.filter(x => !x.ok).map(x => ' ✘' + x.name + '=' + x.info).join(''));

  });
  // 2) KI gegen KI: Trefferquote und gültige Entscheidungen
  await abschnitt('2) KI gegen KI', async () => {
  const ki = await p.evaluate((N) => {
    const F = window.__fps, S = F.Spiel, L = F.TeamDB.liste, codes = {}; let n = 0, tore = 0, fehler = 0;
    const o = S.auswerten.bind(S); S.auswerten = (e) => { codes[e.code] = (codes[e.code] || 0) + 1; n++; if (e.tor) tore++; o(e); };
    for (let m = 0; m < N; m++) { S.starteMatch(L[m % L.length], L[(m + 5) % L.length], null); let k = 0; while (S.zustand !== 'ergebnis' && k < 120 * 500) { try { S.schritt(1 / 120); } catch (e) { fehler++; codes['EXC ' + e.message] = 1; break; } if (S.zustand === 'wiederholung') S.replayEnde(); k++; } }
    S.auswerten = o; return { n, tore, quote: tore / n, codes, fehler };
  }, 10);
  pruef('KI gegen KI', ki.fehler === 0 && ki.quote > 0.28 && ki.quote < 0.72, `${ki.n} Versuche, Quote ${(ki.quote * 100).toFixed(0)} %, ${JSON.stringify(ki.codes)}`);
  await zumMenue();

  });
  // 2b) Kelle am Ball: beim Abschuss liegt das Kellenblatt am Ball (auch bei Schlagschuss und Zorro)
  await abschnitt('2b) Kelle am Ball', async () => {
    const kb = await p.evaluate((N) => {
      const F = window.__fps, S = F.Spiel, L = F.TeamDB.liste, werte = [], typen = {}; const tmp = new F.V3(), ab = new F.V3();
      S.starteMatch(L[1], L[3], null); let vers = 0, k = 0, vorher = false;
      while (vers < N && k < 120 * 900) {
        S.schritt(1 / 120); k++; if (S.zustand === 'wiederholung') S.replayEnde(); if (S.zustand === 'ergebnis') S.starteMatch(L[(vers + 2) % 12], L[(vers + 7) % 12], null);
        const sch = S.schuetze, jetzt = sch.zustand === 'schuss' && sch.abgeschossen;
        if (jetzt && !vorher) { const f = sch.fig.ferse, bp = F.ball.pp; ab.copy(sch.fig.kelleDir).multiplyScalar(0.28); tmp.copy(bp).sub(f); const t = Math.max(0, Math.min(1, tmp.dot(ab) / ab.lengthSq())); tmp.copy(f).addScaledVector(ab, t); werte.push(tmp.distanceTo(bp) - 0.036); typen[sch.schuss.typ] = (typen[sch.schuss.typ] || 0) + 1; vers++; }
        vorher = jetzt;
      }
      return { n: werte.length, max: Math.max(...werte), mittel: werte.reduce((a, b) => a + b, 0) / werte.length, typen };
    }, 24);
    pruef('Kelle am Ball beim Abschuss', kb.n >= 20 && kb.max < 0.09, `${kb.n} Schüsse, Abstand Blatt–Ball: Mittel ${(kb.mittel * 100).toFixed(1)} cm, größter ${(kb.max * 100).toFixed(1)} cm, ${JSON.stringify(kb.typen)}`);
    await zumMenue();
  });

  // 3) Mensch schießt: W laufen, Maus zielt, halten/loslassen
  await abschnitt('3) Mensch schießt', async () => {
  await p.click('[data-m="training"]'); await p.waitForTimeout(200); await p.click('[data-art="schiessen"]');
  await wf(() => window.__fps.Spiel.zustand === 'anlauf' && window.__fps.Spiel.menschSchiesst);
  const s0 = await st(); await p.keyboard.down('KeyA'); await simWarten(0.6); const s1 = await st(); await p.keyboard.up('KeyA');
  await p.keyboard.down('KeyW'); await simWarten(0.5); const s2 = await st(); await p.keyboard.up('KeyW');
  pruef('WASD-Lauf', s1.pos[1] < s0.pos[1] - 0.4 && s1.vel[1] < -1.5 && s2.pos[0] > s1.pos[0] + 0.3 && s2.vel[0] > 1.5, JSON.stringify({ start: s0.pos, nachA: s1.pos, tempoA: s1.vel, nachW: s2.pos, tempoW: s2.vel }));
  let sc = await screenOf(-0.55, 0.25); await p.mouse.move(sc.x, sc.y); await p.waitForTimeout(120); await p.mouse.down();
  await wf(() => window.__fps.Spiel.schuetze.power > 0.45 || window.__fps.Spiel.versuch.ergebnis);
  sc = await screenOf(-0.55, 0.25); await p.mouse.move(sc.x, sc.y); await p.waitForTimeout(120);
  const sicht = await p.evaluate(() => { const S = window.__fps.Spiel; return { kraft: S.zielKraft.visible, streu: +S.zielStreu.scale.x.toFixed(3), bahn: S.bahn.visible, kreis: S.zielKreis.visible }; });
  await p.mouse.up();
  await wf(() => window.__fps.Spiel.schussInfo || window.__fps.Spiel.versuch.ergebnis);
  const si = await p.evaluate(() => { const S = window.__fps.Spiel; return S.schussInfo ? { ziel: [S.schussInfo.ziel.z, S.schussInfo.ziel.y], cur: [S.zielCursor.z, S.zielCursor.y], typ: S.schussInfo.typ, kmh: Math.round(S.schussInfo.speed * 3.6), tempo: document.getElementById('tempoAnzeige').textContent } : null; });
  pruef('Maus-Zielen', si && Math.abs(si.cur[0] + 0.55) < 0.08 && Math.abs(si.cur[1] - 0.25) < 0.08 && Math.abs(si.ziel[0] - si.cur[0]) < 0.25, JSON.stringify(si));
  pruef('Zielanzeige (Kraftbogen, Streukreis, Flugbahn)', sicht.kraft && sicht.kreis && sicht.bahn && sicht.streu > 0.15, JSON.stringify(sicht));
  await wf(() => window.__fps.Spiel.versuch.ergebnis); pruef('Schuss wird gewertet', true, (await st()).erg);

  });
  // 4) Tricks beim Anlauf
  await abschnitt('4) Tricks beim Anlauf', async () => {
  await wf(() => window.__fps.Spiel.zustand === 'anlauf' && window.__fps.Spiel.schuetze.zustand === 'lauf' && window.__fps.Spiel.schuetze.pos.x > 1, null, 40000);
  await p.evaluate(() => { const S = window.__fps.Spiel; S.schuetze.daten = Object.assign({}, S.schuetze.daten, { technik: 100 }); S.welt.druck = 0; Math._r = Math.random; Math.random = () => 0.3; });
  const ohneTrick = () => wf(() => !window.__fps.Spiel.schuetze.trick, null, 5000);
  await p.keyboard.press('KeyQ'); await simWarten(0.08); const tq = await st(); await ohneTrick();
  await p.keyboard.press('KeyE'); await simWarten(0.12); const te = await st(); await ohneTrick(); const te2 = await st();
  await p.keyboard.press('KeyR'); await wf(() => window.__fps.Spiel.schuetze.zorro || window.__fps.Spiel.versuch.ergebnis, null, 8000).catch(() => {}); await simWarten(0.2); const tr = await st();
  await p.evaluate(() => { Math.random = Math._r; });
  pruef('Tricks (Zieher, Drehung, Zorro)', tq.trick === 'zieher' && te.trick === 'drehung' && tr.zorro && tr.ballY > 0.2, JSON.stringify({ q: tq.trick, e: te.trick, yaw: [te.yaw, te2.yaw], zorro: tr.zorro, ballY: tr.ballY, erg: tr.erg }));
  await p.keyboard.press('Space'); await p.waitForTimeout(50);
  await zumMenue();

  });
  // 5) Mensch hält: Bewegung im Torraum, Raus (F), Parade per Klick
  await abschnitt('5) Mensch hält', async () => {
  await p.click('[data-m="training"]'); await p.waitForTimeout(200); await p.click('[data-art="halten"]');
  await wf(() => window.__fps.Spiel.zustand === 'anlauf' && window.__fps.Spiel.menschHaelt);
  // KI-Schütze für die Bewegungsprüfung ausbremsen: er läuft langsam vorwärts und schießt nicht
  await p.evaluate(() => { const S = window.__fps.Spiel, k = S.kiS, o = k.absicht.bind(k); k.plan.trick = null; k.plan.finteBei = -1; k.absicht = (dt, sch) => { const A = o(dt, sch); A.laden = false; A.finte = false; A.trick = null; A.tempo = 0.16; A.richtung.set(1, 0, 0); return A; }; });
  const g0 = await st(); await p.keyboard.down('KeyW'); await simWarten(1.3); await p.keyboard.up('KeyW'); const g1 = await st();
  await p.keyboard.down('KeyA'); await simWarten(0.8); await p.keyboard.up('KeyA'); const g2 = await st();
  pruef('Torhüter im Torraum', g1.twPos[0] < g0.twPos[0] - 0.8 && Math.abs(g2.twPos[1] - g1.twPos[1]) > 0.5 && g1.twPos[0] >= 16.5 - 3.35, JSON.stringify({ start: g0.twPos, nachW: g1.twPos, nachA: g2.twPos }));
  await p.keyboard.press('KeyF'); await simWarten(0.15); const g3 = await st();
  pruef('Torhüter Raus (F)', g3.tw === 'raus' || g3.tw === 'liegtVorn', g3.tw);
  await zumMenue();
  // Parade: neuer Versuch; der Klick auf den Zielpunkt wird im Augenblick des Schusses als Zeigerereignis ausgelöst (60 ms Reaktionszeit)
  await p.click('[data-m="training"]'); await p.waitForTimeout(200); await p.click('[data-art="halten"]');
  await wf(() => window.__fps.Spiel.zustand === 'anlauf' && window.__fps.Spiel.menschHaelt);
  await p.evaluate(() => { const F = window.__fps, S = F.Spiel, o = S.beiSchuss.bind(S); S.kiS.plan.trick = null;
    S.beiSchuss = (s, info) => { o(s, info); S.beiSchuss = o; F.kamera.updateMatrixWorld(); const v = info.ziel.clone().project(F.kamera), x = (v.x + 1) / 2 * innerWidth, y = (1 - v.y) / 2 * innerHeight, c = F.renderer.domElement;
      const ev = (typ) => new PointerEvent(typ, { clientX: x, clientY: y, pointerId: 7, pointerType: 'mouse', button: 0, bubbles: true }); window.__klick = [Math.round(x), Math.round(y)];
      setTimeout(() => { c.dispatchEvent(ev('pointerdown')); window.dispatchEvent(ev('pointerup')); }, 60); }; });
  await wf(() => window.__fps.Spiel.versuch.ergebnis, null, 60000);
  const g6 = await p.evaluate(() => { const S = window.__fps.Spiel; return { aktion: S.torwart.aktion && S.torwart.aktion.typ, erg: S.versuch.ergebnis.code, klick: window.__klick }; });
  pruef('Torhüter Parade per Klick', ['hecht', 'fuss', 'butterfly', 'fangen'].includes(g6.aktion), JSON.stringify(g6));
  await zumMenue();
  });

  // 5b) Parcours: Testfahrer steuert über die normale Eingabe durch alle Übungen, Schuss, Wertung
  await abschnitt('5b) Parcours', async () => {
    await p.click('[data-m="parcours"]');
    const pr = await p.evaluate(() => {
      const F = window.__fps, S = F.Spiel, E = F.Eingabe, PC = F.PARCOURS, W = [], alt = E.lenkung;
      S.pausiert = true; let i = 0; while (S.zustand !== 'anlauf' && i < 1200) { S.schritt(1 / 120); i++; }
      const start = { boden: F.halle.bodenArt, koerper: document.body.classList.contains('parcours'), gesperrt: S.welt.schussGesperrt };
      // Schuss vor den Übungen ist gesperrt
      E.tasten.add('Enter'); for (let k = 0; k < 60; k++) S.schritt(1 / 120); const frueh = S.schuetze.zustand; E.tasten.delete('Enter');
      PC.slalom.forEach((c, k) => { const s = k === 1 ? -c.seite : c.seite; W.push([c.x - 0.9, s * 0.9], [c.x + 0.4, s * 0.9]); });   // Hütchen 2 absichtlich auf der falschen Seite
      for (const c of PC.drehungen) { W.push([c.x - 1.6, c.z]); for (let k = 1; k <= 15; k++) { const a = Math.PI + k / 12 * Math.PI * 2; W.push([c.x + Math.cos(a) * 1.55, c.z + Math.sin(a) * 1.55]); } }
      for (const g of PC.tore) W.push([g.x - 1.3, g.z], [g.x + 0.5, g.z]);
      W.push([12.6, 0]);
      const ziel = new F.V3(); let wi = 0, halten = 0, geschossen = false, t = 0;
      E.lenkung = () => { if (wi >= W.length) return { x: 0, y: 0, quelle: 'keine' }; const sp = S.schuetze.pos; ziel.set(W[wi][0] - sp.x, 0, W[wi][1] - sp.z); if (ziel.length() < 0.45) { wi++; return E.lenkung(); } ziel.normalize(); const { r, f } = F.Kam.rechtsVorne(); return { x: ziel.dot(r), y: ziel.dot(f), quelle: 'pad' }; };
      const meld = []; const om = F.HUD.meldung.bind(F.HUD); F.HUD.meldung = (tx, a) => { if (tx) meld.push(tx); om(tx, a); };
      while (S.zustand === 'anlauf' && t < 70) { S.schritt(1 / 120); t += 1 / 120; const P = F.Parcours.z;
        if (P && P.uebung >= 3 && wi >= W.length && !geschossen) { S.zielCursor = { z: 0.6, y: 0.9 }; if (halten === 0) E.tasten.add('Enter'); halten += 1 / 120; if (halten > 0.55) { E.tasten.delete('Enter'); geschossen = true; } } }
      for (let k = 0; k < 900 && S.zustand !== 'ergebnis'; k++) { S.schritt(1 / 120); if (S.zustand === 'wiederholung') S.replayEnde(); }
      E.lenkung = alt; F.HUD.meldung = om; S.pausiert = false;
      const erg = document.querySelector('.parcoursErg');
      return { start, frueh, wege: wi + '/' + W.length, geschossen, zustand: S.zustand, meld, text: erg ? erg.innerText.replace(/\n+/g, ' | ') : '', best: localStorage.getItem('fps_parcours_v1') };
    });
    pruef('Parcours: Start (blauer Boden, Schuss gesperrt)', pr.start.boden === 'kunststoff' && pr.start.koerper && pr.start.gesperrt && pr.frueh === 'lauf', JSON.stringify(pr.start) + ' früher Schuss → ' + pr.frueh);
    pruef('Parcours: alle Übungen und Schuss', pr.wege.split('/')[0] === pr.wege.split('/')[1] && pr.geschossen && pr.zustand === 'ergebnis' && pr.meld.filter(m => m === 'Drehung!').length === 2 && pr.meld.some(m => m.startsWith('Falsche Seite')), pr.meld.join(' · '));
    pruef('Parcours: Wertung und Bestwert', /Punkte/.test(pr.text) && /Fehler [1-9]/.test(pr.text) && !!pr.best, pr.text.slice(0, 160) + ' | gespeichert ' + pr.best);
    await p.click('.parcoursErg [data-menue]'); await p.waitForTimeout(200);
    const weg = await p.evaluate(() => ({ boden: window.__fps.halle.bodenArt, koerper: document.body.classList.contains('parcours'), sichtbar: window.__fps.Parcours.gruppe.visible }));
    pruef('Parcours: Aufräumen beim Verlassen', weg.boden === 'parkett' && !weg.koerper && !weg.sichtbar, JSON.stringify(weg));
  });

  // 5c) Freies Training: kein Zeitlimit, keine Torhüterraum-Regel, beliebig viele Schüsse mit Ballrückgabe, Hütchen optional
  await abschnitt('5c) Freies Training', async () => {
    await p.click('[data-m="training"]'); await p.waitForTimeout(200); await p.click('[data-hut]'); await p.click('[data-art="frei"]');
    const fr = await p.evaluate(() => {
      const F = window.__fps, S = F.Spiel, E = F.Eingabe, alt = E.lenkung, ziel = new F.V3();
      S.pausiert = true; let i = 0; while (S.zustand !== 'anlauf' && i < 600) { S.schritt(1 / 120); i++; }
      const start = { modus: S.modus, huetchen: F.Parcours.gruppe.visible, info: document.getElementById('trainingInfo').textContent };
      for (let k = 0; k < 120 * 25; k++) S.schritt(1 / 120);                       // 25 s stehen: kein Zeitlimit
      const nachWarten = { zustand: S.zustand, ergebnis: S.versuch.ergebnis };
      const geh = (x, z, max = 1800) => { E.lenkung = () => { const sp = S.schuetze.pos; ziel.set(x - sp.x, 0, z - sp.z); if (ziel.length() < 0.3) return { x: 0, y: 0, quelle: 'keine' }; ziel.normalize(); const { r, f } = F.Kam.rechtsVorne(); return { x: ziel.dot(r), y: ziel.dot(f), quelle: 'pad' }; }; for (let k = 0; k < max; k++) S.schritt(1 / 120); E.lenkung = alt; };
      geh(15.2, 0.4);                                                               // in den Torhüterraum laufen
      const imRaum = { x: +S.schuetze.pos.x.toFixed(2), ergebnis: S.versuch.ergebnis, zustand: S.zustand };
      geh(9, 0, 900);
      const schuesse = [];
      for (let n = 0; n < 3; n++) {
        let w = 0; while (!(S.schuetze.kontrolle && S.zustand === 'anlauf' && S.freiWarte < 0) && w < 1200) { S.schritt(1 / 120); w++; }
        S.zielCursor = { z: n % 2 ? -0.55 : 0.55, y: 0.5 }; E.tasten.add('Enter'); for (let k = 0; k < 60; k++) S.schritt(1 / 120); E.tasten.delete('Enter');
        let k = 0; while (S.freiWarte < 0 && k < 1500) { S.schritt(1 / 120); k++; }
        schuesse.push(S.versuch.ergebnis ? S.versuch.ergebnis.code : 'liegt');
        k = 0; while (S.freiWarte >= 0 && k < 400) { S.schritt(1 / 120); k++; }
      }
      const ende = { kontrolle: S.schuetze.kontrolle, zustand: S.zustand, tr: Object.assign({}, S.training), info: document.getElementById('trainingInfo').textContent };
      S.pausiert = false; return { start, nachWarten, imRaum, schuesse, ende };
    });
    pruef('Freies Training: Start mit Hütchen', fr.start.modus === 'frei' && fr.start.huetchen && /Freies Training|FREIES TRAINING/i.test(fr.start.info), JSON.stringify(fr.start));
    pruef('Freies Training: kein Zeitlimit, kein Torhüterraum-Fehlversuch', fr.nachWarten.zustand === 'anlauf' && !fr.nachWarten.ergebnis && !fr.imRaum.ergebnis && fr.imRaum.zustand === 'anlauf' && fr.imRaum.x > 15, JSON.stringify({ nachWarten: fr.nachWarten, imRaum: fr.imRaum }));
    pruef('Freies Training: 3 Schüsse, Ball kommt zurück', fr.ende.tr.schuesse === 3 && fr.ende.kontrolle && fr.ende.zustand === 'anlauf', JSON.stringify({ schuesse: fr.schuesse, zaehler: fr.ende.tr, info: fr.ende.info }));
    await zumMenue();
    const weg = await p.evaluate(() => ({ koerper: document.body.className, huetchen: window.__fps.Parcours.gruppe.visible, ring: window.__fps.Parcours.spielerRing.visible }));
    pruef('Freies Training: Aufräumen', !/frei/.test(weg.koerper) && !weg.huetchen && !weg.ring, JSON.stringify(weg));
  });

  // 5d) Spiel 5 gegen 5: Start über das Menü, Laufen, Pass, Schuss, komplettes Spiel bis zum Endstand, Aufräumen
  await abschnitt('5d) Spiel 5 gegen 5', async () => {
    await p.click('[data-m="spiel5"]'); await p.waitForTimeout(250); await p.click('[data-dauer="1"]'); await p.click('[data-los]');
    const sp = await p.evaluate(() => {
      const F = window.__fps, S = F.Spiel, M = F.Match, E = F.Eingabe, alt = E.lenkung, erg = {};
      S.pausiert = true; let i = 0; while (M.phase !== 'spiel' && i < 600) { S.schritt(1 / 120); i++; }
      erg.start = { zustand: S.zustand, spieler: M.ents.length, torhueter: M.gks.length, steuer: !!M.steuer, zweiTore: F.ball.zweiTore, penaltyFiguren: S.figL.objekt.visible || S.figT.objekt.visible };
      // Laufen: gesteuerter Spieler bewegt sich mit der Eingabe
      M.steuer = M.ents[3]; M.eingabeT = 0; const p0 = M.steuer.s.pos.clone();
      E.lenkung = () => ({ x: 1, y: 0, quelle: 'tasten' }); for (let k = 0; k < 90; k++) S.schritt(1 / 120); E.lenkung = alt;
      erg.lauf = +M.steuer.s.pos.distanceTo(p0).toFixed(2);
      // Pass mit Leertaste
      // Gegner können in dieser Teilprüfung den Ball nicht erobern (geprüft wird die Pass- und Schussmechanik, nicht der Zufall)
      const sperre = () => M.ents.forEach(x => { if (x.team === 'B') x.s.ballSperre = 3; });
      sperre(); const ich = M.steuer; M.gibBall(ich); for (let k = 0; k < 20; k++) S.schritt(1 / 120);
      erg.vorPass = { steuerIch: M.steuer === ich, kontrolle: ich.s.kontrolle, phase: M.phase, zustand: ich.s.zustand };
      // In den 20 Schritten kann ein Gegner den Ball erobert oder der Auto-Wechsel die Steuerung verlegt haben
      M.steuer = ich; if (!ich.s.kontrolle) M.gibBall(ich);
      S.ereignis({ typ: 'finte' }); erg.passBewegung = M.besitzer && M.besitzer.s.zustand; const passZiel = M.passEmpfaenger; for (let k = 0; k < 40; k++) S.schritt(1 / 120); erg.pass = { besitzerNachPass: M.besitzer ? M.besitzer.team : null, empfaenger: !!passZiel && (M.passEmpfaenger === passZiel || M.besitzer === passZiel), steuerGewechselt: M.steuer !== ich };   // Ball unterwegs oder schon beim Empfänger
      // Schuss: Ball geben, Enter halten und loslassen
      let geschossen = null; const ob = M.beiSchuss.bind(M); M.beiSchuss = (s, info, team) => { geschossen = { team, kmh: Math.round(info.speed * 3.6) }; ob(s, info, team); };
      sperre(); M.gibBall(M.steuer); for (let k = 0; k < 20; k++) S.schritt(1 / 120); E.tasten.add('Enter'); for (let k = 0; k < 70; k++) S.schritt(1 / 120); E.tasten.delete('Enter'); for (let k = 0; k < 60; k++) S.schritt(1 / 120);
      M.beiSchuss = ob; erg.schuss = geschossen;
      // Rest des Spiels im Zeitraffer
      let n = 0, fehler = null; while (S.zustand === 'match' && n < 120 * 300) { try { S.schritt(1 / 120); } catch (e) { fehler = e.message; break; } n++; }
      erg.ende = { zustand: S.zustand, stand: M.stand, tore: M.tore.length, fehler, text: (document.querySelector('.parcoursErg') || {}).innerText || '' };
      S.pausiert = false; return erg;
    });
    pruef('Spiel 5 gegen 5: Start', sp.start.zustand === 'match' && sp.start.spieler === 10 && sp.start.torhueter === 2 && sp.start.steuer && sp.start.zweiTore && !sp.start.penaltyFiguren, JSON.stringify(sp.start));
    pruef('Spiel 5 gegen 5: Laufen, Pass, Schuss', sp.lauf > 0.8 && sp.passBewegung === 'schuss' && (sp.pass.empfaenger || sp.pass.besitzerNachPass === 'A') && sp.pass.steuerGewechselt && sp.schuss && sp.schuss.team === 'A', JSON.stringify({ lauf: sp.lauf, vorPass: sp.vorPass, schlag: sp.passBewegung, pass: sp.pass, schuss: sp.schuss }));
    pruef('Spiel 5 gegen 5: drei Drittel bis zum Endstand', sp.ende.zustand === 'ergebnis' && !sp.ende.fehler && /Endstand/.test(sp.ende.text) && /Revanche/.test(sp.ende.text) && (sp.ende.stand.A !== sp.ende.stand.B || /Penaltyschießen/.test(sp.ende.text)), JSON.stringify({ stand: sp.ende.stand, tore: sp.ende.tore, fehler: sp.ende.fehler }));
    await p.click('.parcoursErg [data-menue]'); await p.waitForTimeout(200);
    const weg = await p.evaluate(() => { const F = window.__fps; return { sichtbar: F.Match.sichtbar, zweiTore: F.ball.zweiTore, penalty: F.Spiel.figL.objekt.visible && F.Spiel.figT.objekt.visible, koerper: document.body.className }; });
    pruef('Spiel 5 gegen 5: Aufräumen', !weg.sichtbar && !weg.zweiTore && weg.penalty && !/match/.test(weg.koerper), JSON.stringify(weg));
  });

  // 5e) Laufstil: 25 s KI gegen KI, alle Feldspieler, jede Simulationsstufe (Füße, Knie, Rhythmus, Schräglage)
  await abschnitt('5e) Laufstil', async () => {
    const g = await p.evaluate(() => {
      const F = window.__fps, S = F.Spiel, M = F.Match, L = F.TeamDB.liste, V = F.THREE.Vector3, dt = 1 / 120;
      S.starteSpiel5(L[0], L[8], null); S.pausiert = true;
      const gleit = [], st = { n: 0, ik: 0, knie: 0, kreuz: 0, nan: 0, boden: 0, kurve: 0, innen: 0, sprintN: 0, sprintSchritte: 0, bremsP: 0, bremsN: 0, laufP: 0, laufN: 0 }, alt = new Map(), a = new V(), c = new V();
      for (let i = 0; i < 25 * 120 && S.zustand === 'match'; i++) {
        S.schritt(dt); if (M.phase !== 'spiel') { alt.clear(); continue; }
        for (const e of M.ents) {
          const s = e.s, fig = s.fig, J = fig.j, P = s.anim.letzte, o = alt.get(e) || {}; if (!P) continue;
          const wy = fig.wurzel.rotation.y, wc = Math.cos(wy), ws = Math.sin(wy), sp = s.speed, w = [];
          for (const [n, si] of [['L', 0], ['R', 1]]) {
            const pf = fig.planer.f[si], f = J['fuss' + n].getWorldPosition(new V()), kp = [-0.078, 0.03, 0.13].map(z => J['fuss' + n].localToWorld(new V(0, -0.08, z)));
            w.push(f); if (!isFinite(f.x + f.y + f.z)) st.nan++; if (f.y < 0.05) st.boden++;
            if (pf.ziel && f.distanceTo(pf.ziel) > 0.1) st.ik++;
            if (!pf.schwingt && o['s' + n] === false && o['k' + n] && pf.kt > 0.02) { const d = Math.min(...kp.map((q, j) => Math.hypot(q.x - o['k' + n][j].x, q.z - o['k' + n][j].z))); if (d < 0.2) gleit.push(d / dt); }
            if (pf.schwingt && o['s' + n] === false && s.zustand === 'lauf' && sp > 4.4) st.sprintSchritte++;
            o['k' + n] = kp; o['s' + n] = pf.schwingt;
            const h = J['huefte' + n].getWorldPosition(a), kn = J['knie' + n].getWorldPosition(new V()), m = c.copy(h).add(f).multiplyScalar(0.5);
            if ((kn.x - m.x) * ws + (kn.z - m.z) * wc < -0.01) st.knie++;
          }
          const dx = w[0].x - w[1].x, dz = w[0].z - w[1].z; if (dx * wc - dz * ws < -0.02) st.kreuz++;
          if (s.zustand === 'lauf') {
            if (sp > 4.4) st.sprintN++;
            if (Math.abs(s.neigS || 0) > 3) { st.kurve++; if (P.roll * s.neigS < 0) st.innen++; }
            if ((s.neigV || 0) < -4 && sp > 1.5) { st.bremsN++; st.bremsP += P.pitch; } else if (Math.abs(s.neigV || 0) < 1 && sp > 3) { st.laufN++; st.laufP += P.pitch; }
          }
          alt.set(e, o); st.n++;
        }
      }
      gleit.sort((x, y) => x - y);
      const r = { proben: st.n, gleitP99: +(gleit[Math.floor(gleit.length * 0.99)] || 0).toFixed(3), ikUeber10cm: st.ik, knieHinten: st.knie, beineGekreuzt: st.kreuz, nan: st.nan, unterBoden: st.boden,
        sprintSchritteProS: st.sprintN ? +(st.sprintSchritte / (st.sprintN / 120)).toFixed(2) : null, kurveInnen: st.kurve ? +(st.innen / st.kurve).toFixed(3) : null,
        vorlageBremsen: st.bremsN ? +(st.bremsP / st.bremsN).toFixed(3) : null, vorlageLauf: st.laufN ? +(st.laufP / st.laufN).toFixed(3) : null };
      S.pausiert = false; S.parcoursAufraeumen(); S.leerlauf(); F.UI.hauptmenue(); return r;
    });
    pruef('Laufstil: Füße bleiben stehen, Beine sauber', g.proben > 5000 && g.gleitP99 < 0.15 && g.ikUeber10cm === 0 && g.knieHinten === 0 && g.beineGekreuzt <= g.proben * 0.0004 &&   /* Grundrate gemessen ~0,01 % (Einzelbilder beim Umspringen) */ g.nan === 0 && g.unterBoden === 0, JSON.stringify({ proben: g.proben, gleitP99: g.gleitP99, ik: g.ikUeber10cm, knie: g.knieHinten, kreuz: g.beineGekreuzt, nan: g.nan, boden: g.unterBoden }));
    pruef('Laufstil: Rhythmus und Haltung', g.sprintSchritteProS > 3.4 && g.sprintSchritteProS < 4.6 && g.kurveInnen > 0.95 && g.vorlageBremsen < g.vorlageLauf - 0.1, JSON.stringify({ sprintSchritteProS: g.sprintSchritteProS, kurveInnen: g.kurveInnen, vorlageBremsen: g.vorlageBremsen, vorlageLauf: g.vorlageLauf }));
  });

  // 5f) Ballannahme: 180 s KI gegen KI – Blatt am Ball, weiches Abfedern, Passquote
  await abschnitt('5f) Ballannahme', async () => {
    const a = await p.evaluate(() => {
      const F = window.__fps, S = F.Spiel, M = F.Match, L = F.TeamDB.liste, ball = F.ball, dt = 1 / 120;
      const st = { passe: 0, ziel: 0, annahmen: 0, blatt: [], koerper: 0, ruck: [], fehler: null, erwartet: 0 };
      const np = new F.THREE.Vector3(), blattAbst = (e) => { const fe = e.s.fig.ferse, kd = e.s.fig.kelleDir, ab = kd.clone().multiplyScalar(0.28), t = Math.max(0, Math.min(1, ball.p.clone().sub(fe).dot(ab) / ab.lengthSq())); return np.copy(fe).addScaledVector(ab, t).distanceTo(ball.p); };
      const op = M.pass, og = M.gibBall; let beob = null, passZiel = null;
      M.pass = function (e, m) { st.passe++; passZiel = m; return op.call(this, e, m); };
      const osch = M.beiSchuss; M.beiSchuss = function (sch, info, team) { if (passZiel && passZiel.s === sch && sch.schuss && sch.schuss.direkt) { st.ziel++; passZiel = null; } return osch.call(this, sch, info, team); };   // Direktschuss = Pass ist angekommen
      M.gibBall = function (e) {
        if (!ball.kinematisch && ball.v.length() > 3 && M.phase === 'spiel') {
          const ausPass = passZiel === e && M.passEmpfaenger === e; passZiel = null;   // nur echte Pässe (keine Abwürfe, Abpraller, Blocks)
          if (ausPass) { st.ziel++; st.annahmen++; const d = blattAbst(e); st.blatt.push(d); if (d > 0.3) st.koerper++; if (e.s.annahmeW > 0.5) st.erwartet++; }
          const d = blattAbst(e);
          beob = d < 0.15 ? { e, n: 0, alt: ball.v.clone(), max: 0 } : null;
        }
        return og.call(this, e);
      };
      S.starteSpiel5(L[0], L[8], null); S.pausiert = true;
      for (let i = 0; i < 180 * 120 && S.zustand === 'match'; i++) {
        try { S.schritt(dt); } catch (e) { st.fehler = e.message; break; }
        if (beob) { if (M.besitzer !== beob.e || beob.e.s.zustand !== 'lauf') { if (beob.n > 2) st.ruck.push(beob.max); beob = null; } else { beob.max = Math.max(beob.max, ball.v.clone().sub(beob.alt).length() / dt); beob.alt = ball.v.clone(); if (++beob.n >= 36) { st.ruck.push(beob.max); beob = null; } } }
      }
      M.pass = op; M.gibBall = og; M.beiSchuss = osch;
      const q = (x, z) => { const s = x.slice().sort((u, v) => u - v); return s.length ? +s[Math.min(s.length - 1, Math.floor(s.length * z))].toFixed(3) : null; };
      S.pausiert = false; S.parcoursAufraeumen(); S.leerlauf(); F.UI.hauptmenue();
      return { passe: st.passe, quote: +(st.ziel / Math.max(1, st.passe)).toFixed(3), annahmen: st.annahmen, erwartet: +(st.erwartet / Math.max(1, st.annahmen)).toFixed(3), blattP50: q(st.blatt, 0.5), koerperAnteil: +(st.koerper / Math.max(1, st.annahmen)).toFixed(3), ruckP50: q(st.ruck, 0.5), ruckP90: q(st.ruck, 0.9), ruckN: st.ruck.length, fehler: st.fehler };
    });
    pruef('Ballannahme: Blatt geht zum Ball, kaum Annahmen mit dem Körper', a.annahmen >= 30 && a.erwartet > 0.6 && a.blattP50 < 0.1 && a.koerperAnteil < 0.15 && !a.fehler, JSON.stringify({ annahmen: a.annahmen, erwartet: a.erwartet, blattP50: a.blattP50, koerperAnteil: a.koerperAnteil, fehler: a.fehler }));
    pruef('Ballannahme: Ball wird weich abgefedert, Pässe kommen an', a.ruckN >= 30 && a.ruckP50 < 260 && a.ruckP90 < 700 && a.quote > 0.5   /* mit torseitiger Deckung fängt die Abwehr mehr ab (gemessen 0,60–0,70) */, JSON.stringify({ passe: a.passe, quote: a.quote, ruckP50: a.ruckP50, ruckP90: a.ruckP90, ruckN: a.ruckN }));
  });

  // 5g) Schusstäuschung und Direktschuss als Mensch (Penalty-Training und Spiel 5 gegen 5)
  await abschnitt('5g) Schusstäuschung und Direktschuss', async () => {
    await p.click('[data-m="training"]'); await p.waitForTimeout(200); await p.click('[data-art="schiessen"]');
    await wf(() => window.__fps.Spiel.zustand === 'anlauf' && window.__fps.Spiel.menschSchiesst);
    const pen = await p.evaluate(() => {
      const F = window.__fps, S = F.Spiel, E = F.Eingabe, alt = E.lenkung, sch = () => S.schuetze, erg = { ablauf: [] };
      const merke = () => { const z = sch().zustand; if (erg.ablauf[erg.ablauf.length - 1] !== z) erg.ablauf.push(z); };
      S.pausiert = true; E.lenkung = () => ({ x: 0, y: 1, quelle: 'tasten' });
      for (let k = 0; k < 90; k++) S.schritt(1 / 120);
      E.lenkung = alt; E.tasten.add('Enter');
      for (let k = 0; k < 200 && !(sch().zustand === 'laden' && sch().power > 0.35); k++) { S.schritt(1 / 120); merke(); }
      erg.kraftVorher = +sch().power.toFixed(2); S.ereignis({ typ: 'finte' });
      for (let k = 0; k < 30; k++) { S.schritt(1 / 120); merke(); }
      erg.inTaeuschung = sch().zustand; erg.ballDabei = sch().kontrolle;
      for (let k = 0; k < 40; k++) { S.schritt(1 / 120); merke(); }
      erg.nachTaeuschung = sch().zustand; erg.kraftNach = +sch().power.toFixed(2);
      E.tasten.delete('Enter');
      for (let k = 0; k < 120 && !S.schussInfo; k++) { S.schritt(1 / 120); merke(); }
      erg.schuss = !!S.schussInfo; S.pausiert = false; return erg;
    });
    pruef('Schusstäuschung (Penalty): Ausholen, Täuschung, weiter halten, Schuss', pen.inTaeuschung === 'taeuschung' && pen.ballDabei && pen.nachTaeuschung === 'laden' && pen.kraftNach > 0 && pen.kraftNach < pen.kraftVorher + 0.3 && pen.schuss, JSON.stringify(pen));
    await p.evaluate(() => { const F = window.__fps; F.Spiel.leerlauf(); F.UI.hauptmenue(); });
    const m = await p.evaluate(() => {
      const F = window.__fps, S = F.Spiel, M = F.Match, E = F.Eingabe, L = F.TeamDB.liste, erg = {};
      S.starteSpiel5(L[0], L[8], 'A'); S.pausiert = true; let i = 0; while (M.phase !== 'spiel' && i < 900) { S.schritt(1 / 120); i++; }
      const R = M.steuer, P = M.ents.find(e => e.team === 'A' && e !== R), TX = F.Spiel.welt ? 0 : 0;
      const stelle = () => { M.ents.forEach(e => { if (e.team === 'B') { e.s.ballSperre = 5; e.s.pos.set(12, 0, e.i % 2 ? 8 : -8); e.s.vel.set(0, 0, 0); e.s.fig.planer.bereit = false; } }); };
      // Direktschuss: Mitspieler passt, Mensch hält den Schuss gedrückt
      stelle(); const tx = 18.5 - 7.5;
      R.s.pos.set(tx, 0, 1.6); R.s.vel.set(0, 0, 0); R.s.yaw = Math.PI / 2; R.s.fig.planer.bereit = false; R.s.setzeZustand('lauf');
      P.s.pos.set(tx - 2.5, 0, -4.2); P.s.vel.set(0, 0, 0); P.s.yaw = 0.3; P.s.fig.planer.bereit = false; P.s.setzeZustand('lauf');
      M.gibBall(P); for (let k = 0; k < 6; k++) S.schritt(1 / 120);
      let geschossen = null; const ob = M.beiSchuss.bind(M); M.beiSchuss = (s, info, team) => { if (!geschossen) geschossen = { team, direkt: !!(s.schuss && s.schuss.direkt), kmh: Math.round(info.speed * 3.6), wer: s === R.s }; ob(s, info, team); };
      M.pass(P, R); E.tasten.add('Enter'); const ablauf = [];
      for (let k = 0; k < 150 && !geschossen; k++) { S.schritt(1 / 120); const z = R.s.zustand + (R.s.direkt ? '*' : ''); if (ablauf[ablauf.length - 1] !== z) ablauf.push(z); }
      E.tasten.delete('Enter'); erg.direkt = { ablauf, geschossen };
      // Schusstäuschung im Spiel: Ball am Schläger, ausholen, Leertaste, weiter halten, abziehen
      for (let k = 0; k < 40; k++) S.schritt(1 / 120);
      stelle(); M.steuer = R; R.s.pos.set(tx, 0, 0.8); R.s.vel.set(0, 0, 0); R.s.setzeZustand('lauf'); R.s.fig.planer.bereit = false; M.gibBall(R); geschossen = null;
      for (let k = 0; k < 10; k++) S.schritt(1 / 120);
      E.tasten.add('Enter'); const ab2 = [];
      for (let k = 0; k < 150 && !(R.s.zustand === 'laden' && R.s.power > 0.35); k++) S.schritt(1 / 120);
      S.ereignis({ typ: 'finte' });
      for (let k = 0; k < 140 && !geschossen; k++) { S.schritt(1 / 120); if (ab2[ab2.length - 1] !== R.s.zustand) ab2.push(R.s.zustand); if (k === 70) E.tasten.delete('Enter'); }
      E.tasten.delete('Enter'); M.beiSchuss = ob; erg.taeuschung = { ablauf: ab2, geschossen, taeuschungen: M.statistik.taeuschungen };
      S.pausiert = false; S.parcoursAufraeumen(); S.leerlauf(); F.UI.hauptmenue(); return erg;
    });
    pruef('Direktschuss (Spiel 5 gegen 5): Ausholen ohne Ball, Schlag trifft den Pass', m.direkt.ablauf.includes('laden*') && m.direkt.ablauf.includes('schuss*') && m.direkt.geschossen && m.direkt.geschossen.direkt && m.direkt.geschossen.wer, JSON.stringify(m.direkt));
    pruef('Schusstäuschung (Spiel 5 gegen 5): Leertaste beim Ausholen, danach Schuss', m.taeuschung.ablauf.includes('taeuschung') && m.taeuschung.geschossen && m.taeuschung.geschossen.wer && m.taeuschung.taeuschungen >= 1, JSON.stringify(m.taeuschung));
  });

  // 5h) Mimik und Statur: Ausdrücke folgen dem Spielgeschehen, Maske deckt nur das Gesicht, jeder Spieler hat seine Statur
  await abschnitt('5h) Mimik und Statur', async () => {
    const mm = await p.evaluate(() => {
      const F = window.__fps, S = F.Spiel, M = F.Match, L = F.TeamDB.liste, erg = {};
      S.starteSpiel5(L[0], L[8], null); S.pausiert = true; let i = 0; while (M.phase !== 'spiel' && i < 900) { S.schritt(1 / 120); i++; }
      const e = M.ents.find(x => x.team === 'A'), s = e.s, f = s.fig, lauf = (n) => { for (let k = 0; k < n; k++) S.schritt(1 / 120); };
      const zustand = () => ({ name: f.mimikName, deck: +f.mats.mimik.opacity.toFixed(2), sichtbar: f.mimikMesh.visible });
      erg.neutral = zustand();
      s.mimikEreignis = { name: 'freude', t: 1 }; lauf(90); erg.freude = zustand();
      s.mimikEreignis = { name: 'frust', t: 1 }; lauf(90); erg.frust = zustand();
      s.mimikEreignis = null; M.steuer = e; M.eingabeT = 0; M.ents.forEach(x => { if (x.team === 'B') x.s.ballSperre = 3; }); M.gibBall(e); F.Eingabe.tasten.add('Enter');   // Mensch hält den Schuss: Spieler bleibt im Ausholen
      for (let k = 0; k < 90; k++) S.schritt(1 / 120); erg.anstrengung = { ...zustand(), zustand: s.zustand }; F.Eingabe.tasten.delete('Enter');
      const g = f.mimikMesh.geometry, uv = g.getAttribute('uv'), ix = g.getIndex(); let uvOk = true; for (let k = 0; k < ix.count; k++) { const u = uv.getX(ix.getX(k)), v = uv.getY(ix.getX(k)); if (u < 0 || u > 1 || v < 0 || v > 1) { uvOk = false; break; } }
      erg.maske = { dreiecke: ix.count / 3, uvOk };
      const st = M.ents.map(x => x.s.fig.statur), morph = M.ents.every(x => x.s.fig.koerperMeshes.some(me => me.morphTargetInfluences && me.morphTargetInfluences[0] === x.s.fig.statur));
      erg.statur = { min: +Math.min(...st).toFixed(2), max: +Math.max(...st).toFixed(2), verschieden: new Set(st.map(v => v.toFixed(2))).size, morph };
      // Kleidung: über 4 Teams (40 Spieler) muss jedes Merkmal vorkommen und das sichtbare Material zum Aussehen passen
      let stimmt = true; const z = { unterzieher: 0, tights: 0, brille: 0, n: 0 };
      for (const [a, b] of [[0, 8], [1, 3]]) { if (a) { S.starteSpiel5(L[a], L[b], null); S.schritt(1 / 120); }
        for (const e of M.ents) { const f = e.s.fig, A = f.aussehen; z.n++; if (A.unterzieher) z.unterzieher++; if (A.tights) z.tights++; if (A.brille) z.brille++;
          if ((f.armMesh.material === f.mats.unterzieher) !== !!A.unterzieher || (f.beinMesh.material === f.mats.tights) !== !!A.tights || f.brille.visible !== !!A.brille) stimmt = false; } }
      erg.kleidung = { ...z, stimmt };
      S.pausiert = false; S.parcoursAufraeumen(); S.leerlauf(); F.UI.hauptmenue(); return erg;
    });
    pruef('Mimik: Freude, Frust und Anstrengung werden eingeblendet', !mm.neutral.sichtbar && mm.freude.name === 'freude' && mm.freude.deck > 0.9 && mm.frust.name === 'frust' && mm.frust.deck > 0.9 && mm.anstrengung.name === 'anstrengung' && mm.anstrengung.deck > 0.7, JSON.stringify({ neutral: mm.neutral, freude: mm.freude, frust: mm.frust, anstrengung: mm.anstrengung }));
    pruef('Mimik-Maske und Statur', mm.maske.dreiecke > 200 && mm.maske.uvOk && mm.statur.morph && mm.statur.verschieden >= 6 && mm.statur.min >= -0.45 && mm.statur.max <= 1 && mm.statur.max - mm.statur.min > 0.4, JSON.stringify({ maske: mm.maske, statur: mm.statur }));
    pruef('Kleidung: Unterzieher, Tights und Brille passend zum Aussehen', mm.kleidung.stimmt && mm.kleidung.unterzieher > 0 && mm.kleidung.tights > 0 && mm.kleidung.brille > 0 && mm.kleidung.unterzieher < mm.kleidung.n, JSON.stringify(mm.kleidung));
  });

  // 5i) Zweikampf: Stocherstoß statt Teleport, Abschirmen, Körperkontakt (180 s KI gegen KI)
  await abschnitt('5i) Zweikampf', async () => {
    const z = await p.evaluate(() => {
      const F = window.__fps, S = F.Spiel, M = F.Match, L = F.TeamDB.liste, ball = F.ball, V = F.THREE.Vector3, st = { fehler: null, ruck: [], ueberlapp: 0, proben: 0, frei: 0, stoss: 0, schutz: 0, besitzT: 0 };
      const os = M.stochern; M.stochern = function (e, B) { os.call(this, e, B); if (M.phase === 'freischlag') { st.gepfiffen = (st.gepfiffen || 0) + 1; return; } st.stoss++; if (M.besitzer === null && !ball.kinematisch && ball.v.length() > 1.5) st.frei++; };   // gepfiffener Stockschlag zählt nicht als Stoß
      S.starteSpiel5(L[1], L[3], null); S.pausiert = true; let letzt = null, wer = null, n = 0, max = 0, alt = ball.v.clone();
      for (let i = 0; i < 180 * 120 && S.zustand === 'match'; i++) {
        try { S.schritt(1 / 120); } catch (e) { st.fehler = e.message; break; }
        const b = M.besitzer, dv = ball.v.clone().sub(alt).length() * 120; alt = ball.v.clone();
        if (b && letzt && b.team !== letzt.team) { wer = b; n = 1; max = 0; } if (b) letzt = b;
        if (wer) { if (M.besitzer !== wer || wer.s.zustand !== 'lauf') { if (n > 3) st.ruck.push(max); wer = null; } else { if (n > 1) max = Math.max(max, dv); if (++n > 12) { st.ruck.push(max); wer = null; } } }   // Übernahmebild auslassen: dort kann noch der Schlag des Passgebers liegen
        if (b) { st.besitzT++; if (b.s.schutzW > 0.4) st.schutz++; }
        if (M.phase === 'spiel' && i % 6 === 0) { const E = M.ents; for (let x = 0; x < E.length; x++) for (let y = x + 1; y < E.length; y++) { st.proben++; if (M.welt(E[x], new V()).distanceTo(M.welt(E[y], new V())) < 0.5) st.ueberlapp++; } }
      }
      // Fester Ablauf: Verteidiger direkt am Ballführer, stochert mit Ausfallschritt – mindestens ein Stoß ist sicher
      if (S.zustand === 'match' && M.phase === 'spiel') {
        const T = M.ents.find(e => e.team === 'A'), D = M.ents.find(e => e.team === 'B'); M.gibBall(T);
        for (let k = 0; k < 360 && M.besitzer === T; k++) { T.s.pos.set(0, 0, 0); T.s.vel.set(0, 0, 0); T.s.yaw = Math.PI / 2; D.s.pos.set(-0.75, 0, -0.2); D.s.vel.set(0, 0, 0); D.lunge = 0.45; D.s.ballSperre = 0; S.schritt(1 / 120); }
      }
      M.stochern = os; st.ruck.sort((x, y) => x - y);
      const r = { stoesse: st.stoss, freiNachStoss: st.frei, gepfiffen: st.gepfiffen || 0, kontakte: M.statistik.kontakte, stolpern: M.statistik.stolpern, schutzAnteil: +(st.schutz / Math.max(1, st.besitzT)).toFixed(3), ueberlapp: st.ueberlapp, ruckP50: Math.round(st.ruck[Math.floor(st.ruck.length / 2)] || 0), ruckN: st.ruck.length, fehler: st.fehler };
      S.pausiert = false; S.parcoursAufraeumen(); S.leerlauf(); F.UI.hauptmenue(); return r;
    });
    pruef('Zweikampf: Stocherstoß macht den Ball frei, weicher Ballgewinn', z.stoesse >= 1 && z.freiNachStoss === z.stoesse && z.ruckN >= 10 && z.ruckP50 < 300 && !z.fehler, JSON.stringify(z));
    pruef('Zweikampf: Abschirmen, Körperkontakt, Straucheln selten, keine Überlappung', z.schutzAnteil > 0.05 && z.kontakte >= 10 && z.stolpern <= 30 && z.ueberlapp === 0, JSON.stringify({ schutzAnteil: z.schutzAnteil, kontakte: z.kontakte, stolpern: z.stolpern, ueberlapp: z.ueberlapp }));
  });

  // 5j) KI-Taktik: Freilaufen (freie Passlinien), Doppelpass, torseitige Manndeckung (180 s KI gegen KI)
  await abschnitt('5j) KI-Taktik', async () => {
    const k = await p.evaluate(() => {
      const F = window.__fps, S = F.Spiel, M = F.Match, L = F.TeamDB.liste, ball = F.ball, V = F.THREE.Vector3, st = { passe: 0, an: 0, zu: 0, angeboten: 0, deckProben: 0, torseitig: 0, nah: 0, fehler: null };
      // Deckungsprobe: Verteidiger (ohne Presser) – nächster Angreifer unter 3 m, torseitig (eigenes Tor im eigenen System bei −x)
      const deckProbe = (z) => { const team = M.besitzer.team === 'A' ? 'B' : 'A'; for (const v of M.ents) { if (v.team !== team || v === M.naechst[team]) continue; const w = M.inSicht(v, M.welt(v, new V()), new V()); let best = null, bd = 99;
        for (const o of M.ents) if (o.team !== team && o !== M.besitzer) { const q = M.inSicht(v, M.welt(o, new V()), new V()), d = Math.hypot(q.x - w.x, q.z - w.z); if (d < bd) { bd = d; best = q; } }
        z.deckProben++; if (bd < 3) z.nah++; if (best && w.x < best.x + 0.3) z.torseitig++; } };
      let pz = null; const op = M.pass, og = M.gibBall;
      M.pass = function (e, m) { st.passe++; pz = m; const q = M.welt(m, new V()), pa = M.welt(e, new V()), d = q.clone().sub(pa);
        for (const o of M.ents) if (o.team !== e.team) { const w = M.welt(o, new V()), t = Math.max(0, Math.min(1, w.clone().sub(pa).dot(d) / d.lengthSq())); if (t > 0.1 && t < 0.95 && pa.clone().addScaledVector(d, t).distanceTo(w) < 0.9) { st.zu++; break; } }
        const r = op.call(this, e, m); if (e.doppel) st.angeboten++; return r; };
      M.gibBall = function (e) { if (pz && !ball.kinematisch) { if (e === pz) st.an++; pz = null; } return og.call(this, e); };
      S.starteSpiel5(L[2], L[5], null); S.pausiert = true;
      for (let i = 0; i < 180 * 120 && S.zustand === 'match'; i++) {
        try { S.schritt(1 / 120); } catch (e) { st.fehler = e.message; break; }
        if (i % 30 === 0 && M.phase === 'spiel' && M.besitzer) deckProbe(st);
      }
      M.pass = op; M.gibBall = og;
      // Vergleich: gleiche Messung 120 s ohne Manndeckung (Formation)
      const od = M.deckung, ohne = { deckProben: 0, nah: 0, torseitig: 0 }; M.deckung = () => null; S.starteSpiel5(L[0], L[8], null); S.pausiert = true;
      for (let i = 0; i < 120 * 120 && S.zustand === 'match'; i++) { S.schritt(1 / 120); if (i % 30 === 0 && M.phase === 'spiel' && M.besitzer) deckProbe(ohne); }
      M.deckung = od;
      const r = { ohneNah: +(ohne.nah / Math.max(1, ohne.deckProben)).toFixed(3), passe: st.passe, quote: +(st.an / Math.max(1, st.passe)).toFixed(3), linieZu: +(st.zu / Math.max(1, st.passe)).toFixed(3), doppelAngeboten: st.angeboten, doppelGespielt: M.statistik.doppelpass, deckungNah: +(st.nah / Math.max(1, st.deckProben)).toFixed(3), deckungTorseitig: +(st.torseitig / Math.max(1, st.deckProben)).toFixed(3), fehler: st.fehler };
      S.pausiert = false; S.parcoursAufraeumen(); S.leerlauf(); F.UI.hauptmenue(); return r;
    });
    pruef('KI-Taktik: Freilaufen mit freien Passlinien, Doppelpass wird angeboten', k.passe >= 40 && k.quote > 0.55 && k.linieZu < 0.08 && k.doppelAngeboten >= 3 && !k.fehler, JSON.stringify(k));
    pruef('KI-Taktik: Manndeckung deutlich enger als Formation und überwiegend torseitig', k.deckungNah > k.ohneNah + 0.25 && k.deckungTorseitig > 0.6, JSON.stringify({ mitDeckungNah: k.deckungNah, ohneDeckungNah: k.ohneNah, torseitig: k.deckungTorseitig }));
  });

  // 5k) Regeln: Foul → Freischlag (3 m Abstand, Nehmer spielt), 2-Minuten-Strafe (Unterzahl, Anzeige, Ende durch Zeit und durch Gegentor)
  await abschnitt('5k) Regeln und Strafen', async () => {
    const rg = await p.evaluate(() => {
      const F = window.__fps, S = F.Spiel, M = F.Match, L = F.TeamDB.liste, V = F.THREE.Vector3, erg = {};
      S.starteSpiel5(L[0], L[8], null); S.pausiert = true; let i = 0; while (M.phase !== 'spiel' && i < 900) { S.schritt(1 / 120); i++; }
      const A = M.ents.find(e => e.team === 'A'), B = M.ents.find(e => e.team === 'B');
      // Foul von B an A → Freischlag A
      M.foul(B, A, 'stock', new V(2, 0, 1), false); erg.phase = M.phase; erg.team = M.fs && M.fs.team;
      let minAbst = 99; for (let k = 0; k < 600 && M.phase === 'freischlag'; k++) { S.schritt(1 / 120); if (M.phase === 'freischlag' && M.phaseT > 1.25) for (const e of M.ents) if (e.team === 'B') minAbst = Math.min(minAbst, M.welt(e, new V()).distanceTo(new V(M.fs.ort.x, 0, M.fs.ort.z))); }
      erg.danach = M.phase; erg.besitzer = M.besitzer && M.besitzer.team; erg.minAbstand = +minAbst.toFixed(2);
      // Freischlag am Torraum: Ort wird 3,5 m herausgeschoben
      M.foul(B, A, 'stock', new V(15.5, 0, 0.5), false); erg.ortX = M.fs && +M.fs.ort.x.toFixed(2); for (let k = 0; k < 900 && M.phase === 'freischlag'; k++) S.schritt(1 / 120);
      // Strafe: Unterzahl und Anzeige
      const vorher = M.ents.filter(e => e.team === 'B').length; M.strafe(B, 'stoss'); M.hudStand(true);
      erg.unterzahl = [vorher, M.ents.filter(e => e.team === 'B').length]; erg.anzeige = /⏱/.test(document.getElementById('hudInfo') ? document.getElementById('hudInfo').innerHTML : document.body.innerHTML);
      const dauer = M.strafen[0] && M.strafen[0].dauer;
      // Strafzeit läuft nur im laufenden Spiel; Unterbrechungen verlängern die Wartezeit (höchstens + 30 s)
      for (let k = 0; k < (dauer + 30) * 120 && M.strafen.some(x => x.e === B); k++) S.schritt(1 / 120);
      erg.nachZeit = { strafeVorbei: !M.strafen.some(x => x.e === B), zurueck: M.ents.includes(B), sichtbar: B.s.fig.objekt.visible };
      // Gegentor beendet sofort eine Strafe des Teams, das das Tor kassiert
      const C = M.ents.find(e => e.team === 'B'); M.strafen = M.strafen.filter(x => x.team !== 'B'); M.ents = M.ents.filter(e => e.team !== 'B' || M.alle.includes(e)); M.strafe(C, 'stock');
      const vorTor = M.ents.filter(e => e.team === 'B').length; M.tor('A'); erg.nachTor = { zurueck: M.ents.includes(C), feldVorher: vorTor, feld: M.ents.filter(e => e.team === 'B').length };
      S.pausiert = false; S.parcoursAufraeumen(); S.leerlauf(); F.UI.hauptmenue(); return erg;
    });
    pruef('Regeln: Foul führt zum Freischlag, Gegner 3 m entfernt, gefoultes Team spielt', rg.phase === 'freischlag' && rg.team === 'A' && rg.danach === 'spiel' && rg.besitzer === 'A' && rg.minAbstand >= 2.99 && rg.ortX <= 13.15 - 3.5 + 0.01, JSON.stringify(rg));
    pruef('Regeln: 2-Minuten-Strafe mit Unterzahl, endet nach Zeit und durch Gegentor', rg.unterzahl[0] === 5 && rg.unterzahl[1] === 4 && rg.anzeige && rg.nachZeit.strafeVorbei && rg.nachZeit.zurueck && rg.nachZeit.sichtbar && rg.nachTor.zurueck && rg.nachTor.feld === rg.nachTor.feldVorher + 1, JSON.stringify({ unterzahl: rg.unterzahl, anzeige: rg.anzeige, nachZeit: rg.nachZeit, nachTor: rg.nachTor }));
  });

  // 5l) Linien und Ermüdung: 180 s KI gegen KI – Wechsel beider Teams, Spielerzahl, Plätze, Bank hinter der Bande, Eiszeit beider Reihen
  await abschnitt('5l) Linien und Ermüdung', async () => {
    const li = await p.evaluate(() => {
      const F = window.__fps, S = F.Spiel, M = F.Match, L = F.TeamDB.liste, g = { fehler: null, zahlFalsch: 0, doppelt: 0, bankImFeld: 0, unsichtbar: 0, proben: 0, eMin: 1, eMax: 0 };
      S.starteSpiel5(L[4], L[6], null); S.pausiert = true;
      for (let i = 0; i < 180 * 120 && S.zustand === 'match'; i++) {
        try { S.schritt(1 / 120); } catch (e) { g.fehler = e.message; break; }
        if (i % 30 === 0) { g.proben++;
          for (const t of ['A', 'B']) { const ist = M.ents.filter(e => e.team === t); if (ist.length !== 5 - M.strafen.filter(x => x.team === t).length) g.zahlFalsch++; if (new Set(ist.map(e => e.i)).size !== ist.length) g.doppelt++; }
          for (const e of M.alle) { if (!e.s.fig.objekt.visible) g.unsichtbar++; if (!M.ents.includes(e) && Math.abs(e.s.fig.wurzel.position.z) < 10.2) g.bankImFeld++; g.eMin = Math.min(g.eMin, e.s.energie); g.eMax = Math.max(g.eMax, e.s.energie); } }
      }
      const eis = (r) => M.alle.filter(e => e.reihe === r).reduce((s, e) => s + e.eis, 0);
      const r = { ...g, wechselA: M.linie.A.anzahl, wechselB: M.linie.B.anzahl, eisReihe1: Math.round(eis(1)), eisReihe2: Math.round(eis(2)), eMin: +g.eMin.toFixed(2), eMax: +g.eMax.toFixed(2) };
      S.pausiert = false; S.parcoursAufraeumen(); S.leerlauf(); F.UI.hauptmenue(); return r;
    });
    pruef('Linien: beide Teams wechseln, beide Reihen spielen', li.wechselA >= 2 && li.wechselB >= 2 && li.eisReihe2 > li.eisReihe1 * 0.4 && !li.fehler, JSON.stringify({ wechselA: li.wechselA, wechselB: li.wechselB, eisReihe1: li.eisReihe1, eisReihe2: li.eisReihe2, fehler: li.fehler }));
    pruef('Linien: Spielerzahl, Plätze, Bank hinter der Bande, Energie im Rahmen', li.zahlFalsch === 0 && li.doppelt === 0 && li.bankImFeld === 0 && li.unsichtbar === 0 && li.eMin >= 0.15 && li.eMax <= 1, JSON.stringify({ zahlFalsch: li.zahlFalsch, doppelt: li.doppelt, bankImFeld: li.bankImFeld, unsichtbar: li.unsichtbar, eMin: li.eMin, eMax: li.eMax, proben: li.proben }));
  });

  // 5m) Saison: Spielplan (jeder gegen jeden, Rückrunde), Wertung 3/2/1/0, eigenes Spiel wird eingetragen, Speichern und Laden, Meister
  await abschnitt('5m) Saison', async () => {
    const sa = await p.evaluate(() => {
      const F = window.__fps, Sa = F.Saison, S = F.Spiel, M = F.Match, L = F.TeamDB.liste, ids = L.slice(0, 5).map(x => x.id), erg = {};
      Sa.neu(ids, ids[0], true);
      const sp = Sa.d.spiele, paare = new Map(); for (const x of sp) { const k = [x.heim, x.gast].sort().join('-'); paare.set(k, (paare.get(k) || 0) + 1); }
      erg.plan = { spiele: sp.length, runden: Sa.d.runden, jedesPaarZweimal: [...paare.values()].every(v => v === 2) && paare.size === 10, heimGetauscht: [...paare.keys()].every(k => { const [a, b] = k.split('-'); return sp.some(x => x.heim === a && x.gast === b) && sp.some(x => x.heim === b && x.gast === a); }), keinDoppelProRunde: [...Array(Sa.d.runden)].every((_, r) => { const t = sp.filter(x => x.runde === r + 1).flatMap(x => [x.heim, x.gast]); return new Set(t).size === t.length; }) };
      // Wertung: Sieg, Sieg nach Penaltyschießen
      const s0 = sp[0], s1 = sp[1];
      Sa.eintragen(s0.id, { th: 4, tg: 2, so: null, torschuetzen: [{ team: s0.heim, name: 'Testschütze' }, { team: s0.heim, name: 'Testschütze' }] });
      Sa.eintragen(s1.id, { th: 3, tg: 3, so: 'gast', torschuetzen: [] });
      const tb = Object.fromEntries(Sa.tabelle().map(z => [z.id, z]));
      erg.wertung = { sieger: tb[s0.heim].pkt, verlierer: tb[s0.gast].pkt, soSieger: tb[s1.gast].pkt, soVerlierer: tb[s1.heim].pkt, torjaeger: Sa.torjaeger()[0] && Sa.torjaeger()[0].tore };
      // eigenes Spiel: Saisonspiel starten, Ergebnis über das Spielende eintragen
      const meins = Sa.naechstesSpiel(); const n0 = sp.filter(x => x.erg).length;
      S.starteSpiel5(F.TeamDB.hole(meins.heim), F.TeamDB.hole(meins.gast), null, meins); M.stand = { A: 2, B: 1 }; M.tore = [{ team: 'A', name: 'X', zeit: '0:10', drittel: 1 }, { team: 'A', name: 'X', zeit: '0:20', drittel: 1 }, { team: 'B', name: 'Y', zeit: '0:30', drittel: 1 }]; M.phase = 'ende'; S.spiel5Ende();
      erg.eigenes = { eingetragen: sp.filter(x => x.erg).length === n0 + 1 && !!Sa.d.spiele.find(x => x.id === meins.id).erg, ergebnis: Sa.d.spiele.find(x => x.id === meins.id).erg, weiterKnopf: !!document.querySelector('[data-saison]') };
      // Speichern und Laden
      const kopie = JSON.stringify(Sa.d.spiele.map(x => x.erg)); Sa.d = null; Sa.laden(); erg.geladen = !!Sa.d && JSON.stringify(Sa.d.spiele.map(x => x.erg)) === kopie;
      // Rest simulieren: Meister = Tabellenerster, Punkte gesamt = 3 je Spiel
      let s; while ((s = Sa.naechstesSpiel())) Sa.eintragen(s.id, Sa.simuliere(s.heim, s.gast));
      const t2 = Sa.tabelle(); erg.ende = { meister: Sa.d.meister === t2[0].id, punkte: t2.reduce((a, z) => a + z.pkt, 0) === sp.length * 3, spiele: t2.reduce((a, z) => a + z.sp, 0) === sp.length * 2 };
      Sa.verwerfen(); S.leerlauf(); F.UI.hauptmenue(); return erg;
    });
    pruef('Saison: Spielplan jeder gegen jeden mit Rückrunde', sa.plan.spiele === 20 && sa.plan.runden === 10 && sa.plan.jedesPaarZweimal && sa.plan.heimGetauscht && sa.plan.keinDoppelProRunde, JSON.stringify(sa.plan));
    pruef('Saison: Wertung, eigenes Spiel, Speichern und Laden, Meister', sa.wertung.sieger === 3 && sa.wertung.verlierer === 0 && sa.wertung.soSieger === 2 && sa.wertung.soVerlierer === 1 && sa.wertung.torjaeger === 2 && sa.eigenes.eingetragen && sa.eigenes.ergebnis.th === 2 && sa.eigenes.ergebnis.tg === 1 && sa.eigenes.weiterKnopf && sa.geladen && sa.ende.meister && sa.ende.punkte && sa.ende.spiele, JSON.stringify({ wertung: sa.wertung, eigenes: sa.eigenes, geladen: sa.geladen, ende: sa.ende }));
  });

  // 6) Turnier: 8 Teams mit Gruppen, eigene Spiele als KI simuliert, bis zur Siegerehrung
  await abschnitt('6) Turnier', async () => {
  const tn = await p.evaluate(() => { const F = window.__fps, T = F.Turnier, L = F.TeamDB.liste.map(x => x.id); T.neu(L.slice(0, 8), L[0], true); let n = 0; let s; while ((s = T.naechstesSpiel()) && n < 200) { T.eintragen(s.id, T.simuliere(s.heim, s.gast, s.phase !== 'gruppe')); n++; } F.UI.turnierHub(); return { spiele: n, sieger: T.d.sieger, zustand: F.Spiel.zustand, beste: T.beste() }; });
  pruef('Turnier bis zur Siegerehrung', tn.sieger && tn.zustand === 'siegerehrung' && tn.spiele === 15, JSON.stringify({ spiele: tn.spiele, sieger: tn.sieger, zustand: tn.zustand, schuetze: tn.beste.sch && tn.beste.sch.name }));
  await p.evaluate(() => { for (let i = 0; i < 200; i++) window.__fps.Spiel.render(1 / 60, 0); });
  await p.click('[data-menue]'); await p.waitForTimeout(200);

  });
  // 7) Team-Editor und Import (mit bösartigen Werten)
  await abschnitt('7) Team-Editor und Import (mit bösartigen Werten)', async () => {
  await p.click('[data-m="teams"]'); await p.waitForTimeout(200); await p.click('[data-neu]'); await p.waitForTimeout(200);
  await p.fill('[data-t="name"]', 'Testteam <b>'); await p.fill('[data-t="kuerzel"]', 'tst'); await p.click('[data-save]'); await p.waitForTimeout(200);
  const ed = await p.evaluate(() => { const L = window.__fps.TeamDB.liste, x = L.find(t => t.name.startsWith('Testteam')); return { n: L.length, name: x && x.name, kz: x && x.kuerzel, html: document.querySelector('.teamRaster').innerHTML.includes('<b>') }; });
  pruef('Team-Editor speichert, HTML wird maskiert', ed.n === 13 && ed.kz === 'TST' && !ed.html, JSON.stringify(ed));
  fs.writeFileSync(require('path').join(require('os').tmpdir(), 'fps-import.json'), JSON.stringify({ teams: [{ id: '../x<script>', name: '<img src=x onerror=alert(1)>', kuerzel: 'toolong', primaer: 'javascript:1', sekundaer: '#12ab34', muster: 'böse', schuetzen: [{ name: 'A', nummer: 1e9, schuss: -5, technik: 'x', nerven: 500, hand: 'Q' }], torwart: { reflexe: null } }] }));
  const [fc] = await Promise.all([p.waitForEvent('filechooser'), p.click('[data-imp]')]); await fc.setFiles(require('path').join(require('os').tmpdir(), 'fps-import.json')); await p.waitForTimeout(400);
  const im = await p.evaluate(() => { const L = window.__fps.TeamDB.liste, x = L[L.length - 1]; return { n: L.length, id: x.id, name: x.name, kz: x.kuerzel, p: x.primaer, s: x.sekundaer, mu: x.muster, sp: x.schuetzen.length, s0: x.schuetzen[0], tw: x.torwart.reflexe, img: !!document.querySelector('.teamRaster img') }; });
  pruef('Import wird gesäubert', im.n === 14 && !im.img && im.p === '#3366cc' && im.s === '#12ab34' && im.mu === 'uni' && im.sp === 5 && im.s0.nummer === 99 && im.s0.schuss === 1 && im.s0.nerven === 100 && im.s0.hand === 'L' && !/[<>./]/.test(im.id), JSON.stringify(im));
  await p.click('[data-std]'); await p.waitForTimeout(200); await p.click('[data-zurueck]'); await p.waitForTimeout(150);

  });
  // 8) Tuning: Panel per T, Preset, Regeltests-Knopf, Live-Wert
  await abschnitt('8) Tuning', async () => {
  await p.keyboard.press('KeyT'); await p.waitForTimeout(350);
  await p.click('#tuning [data-preset="arcade"]'); const arc = await p.evaluate(() => window.__fps.Config.physik.maxSchuss);
  await p.evaluate(() => { document.querySelector('#tuning [data-tests]').closest('details').open = true; }); await p.click('#tuning [data-tests]'); const tt = await p.textContent('#testErgebnis');
  await p.click('#tuning [data-preset="realistisch"]'); const real = await p.evaluate(() => window.__fps.Config.physik.maxSchuss);
  pruef('Tuning-Panel', arc === 40 && real === 34 && /13\/13 bestanden/.test(tt), `arcade=${arc}, realistisch=${real}, ${tt.split('\n').pop()}`);
  await p.keyboard.press('KeyT');

  });
  // 9) Schnelles Spiel als Mensch: kompletter Versuch mit HUD-Texten, Pause, Einstellungen
  await abschnitt('9) Schnelles Spiel als Mensch', async () => {
  await p.click('[data-m="schnell"]'); await p.waitForTimeout(250); await p.click('[data-los]');
  await wf(() => window.__fps.Spiel.zustand === 'anlauf' && window.__fps.Spiel.menschSchiesst, null, 30000);
  const hud = await p.evaluate(() => ({ hinweis: document.getElementById('steuerHinweis').textContent, info: document.getElementById('hudInfo').textContent, stand: document.getElementById('hudStand').textContent, breit: document.getElementById('steuerHinweis').scrollWidth <= innerWidth }));
  pruef('HUD im Spiel', /Laufen/.test(hud.hinweis) && /Zorro/.test(hud.hinweis) && /Schütze/.test(hud.info) && hud.breit, JSON.stringify(hud).slice(0, 260));
  await p.keyboard.press('Escape'); await p.waitForTimeout(200); const pa = await p.evaluate(() => window.__fps.Spiel.pausiert && !!document.querySelector('[data-p="weiter"]'));
  await p.click('[data-p="weiter"]'); const pb = await p.evaluate(() => window.__fps.Spiel.pausiert);
  pruef('Pause', pa && !pb);
  await zumMenue();

  });
  pruef('Keine Konsolenfehler', logs.length === 0, logs.slice(0, 5).join(' || '));
  const fehl = erg.filter(x => !x.ok).length; console.log(`\n${erg.length - fehl}/${erg.length} Prüfungen bestanden`);
  await b.close(); process.exit(fehl ? 1 : 0);
})().catch(e => { console.log('ABBRUCH', e.message.split('\n')[0]); process.exit(2); });
