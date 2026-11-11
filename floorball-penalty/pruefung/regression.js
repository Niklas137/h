// Regressionsprüfung: Laden, Regeltests, KI-Statistik, Kelle am Ball, Maus/Tastatur, Tricks, Torhüter, Turnier, Editor, Tuning, HUD
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
