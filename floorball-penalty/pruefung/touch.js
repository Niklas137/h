// Touch-Prüfung auf emuliertem Smartphone (Pixel 7 quer): Joystick links, Zielen/Schießen rechts, Tricks per Knopf, Parade per Tipp
const { devices } = require('playwright');
const { start } = require('./lib');
(async () => {
  const { b, p, logs } = await start({ ctx: { ...devices['Pixel 7 landscape'] }, einst: { tutorial: true, wiederholung: false } });
  const cdp = await p.context().newCDPSession(p);
  const touch = (type, punkte) => cdp.send('Input.dispatchTouchEvent', { type, touchPoints: punkte.map(([x, y, id]) => ({ x, y, id })) });
  const screenOf = (z, y) => p.evaluate(([z, y]) => { const F = window.__fps; F.kamera.updateMatrixWorld(); const v = new F.V3(16.5, y, z).project(F.kamera); return { x: (v.x + 1) / 2 * innerWidth, y: (1 - v.y) / 2 * innerHeight + 70 }; }, [z, y]);
  const info = await p.evaluate(() => ({ quali: window.__fps.Config.grafik.qualitaet, breite: innerWidth, hoehe: innerHeight, dpr: devicePixelRatio, effekte: window.__fps.Bild.effekte, spiegel: window.__fps.Bild.spiegel }));
  console.log('Gerät', JSON.stringify(info));
  await p.tap('[data-m="training"]'); await p.waitForTimeout(300); await p.tap('[data-art="schiessen"]');
  await p.waitForFunction(() => window.__fps.Spiel.zustand === 'anlauf' && window.__fps.Spiel.schuetze.zustand === 'lauf', null, { timeout: 30000 });
  // Joystick: linker Daumen zieht nach rechts oben (laufen), gleichzeitig zielt der rechte Finger
  const p0 = await p.evaluate(() => window.__fps.Spiel.schuetze.pos.toArray());
  const simWarten = async (sek) => { const t0 = await p.evaluate(() => window.__fps.Spiel.simZeit); await p.waitForFunction(([t0, sek]) => window.__fps.Spiel.simZeit >= t0 + sek, [t0, sek], { timeout: 30000 }); };
  await touch('touchStart', [[140, 300, 1]]); await touch('touchMove', [[140, 240, 1]]); await simWarten(0.7);
  const joy = await p.evaluate(() => ({ joy: !!window.__fps.Eingabe.joy, sichtbar: !document.getElementById('joystick').classList.contains('versteckt'), lenk: window.__fps.Eingabe.lenkung(), pos: window.__fps.Spiel.schuetze.pos.toArray(), knoepfe: document.querySelectorAll('.trickKnopf').length }));
  let s = await screenOf(0.5, 0.8); await touch('touchStart', [[140, 240, 1], [s.x, s.y, 2]]);
  for (let i = 0; i < 40; i++) { s = await screenOf(0.5, 0.8); await touch('touchMove', [[140, 240, 1], [s.x + (i % 2), s.y, 2]]); await p.waitForTimeout(90); if (await p.evaluate(() => window.__fps.Spiel.schuetze.power > 0.5 || !!window.__fps.Spiel.versuch.ergebnis)) break; }
  await touch('touchEnd', []);
  await p.waitForFunction(() => window.__fps.Spiel.versuch.ergebnis, null, { timeout: 20000 });
  const sch = await p.evaluate(() => { const S = window.__fps.Spiel; return { erg: S.versuch.ergebnis.code, ziel: S.schussInfo && [+S.schussInfo.ziel.z.toFixed(2), +S.schussInfo.ziel.y.toFixed(2)], cursor: [+S.zielCursor.z.toFixed(2), +S.zielCursor.y.toFixed(2)] }; });
  console.log('Joystick', JSON.stringify({ aktiv: joy.joy, sichtbar: joy.sichtbar, lenk: joy.lenk, vorher: p0.map(x => +x.toFixed(2)), nachher: joy.pos.map(x => +x.toFixed(2)), trickKnoepfe: joy.knoepfe }));
  console.log('Touch-Schuss', JSON.stringify(sch));
  // Trick per Knopf im nächsten Versuch
  await p.waitForFunction(() => window.__fps.Spiel.zustand === 'anlauf' && window.__fps.Spiel.schuetze.zustand === 'lauf' && window.__fps.Spiel.schuetze.pos.x > 1, null, { timeout: 40000 });
  await p.evaluate(() => { const S = window.__fps.Spiel; S.schuetze.daten = Object.assign({}, S.schuetze.daten, { technik: 100 }); });
  await p.tap('.trickKnopf:nth-child(2)'); await simWarten(0.1);
  console.log('Trick-Knopf', await p.evaluate(() => { const s = window.__fps.Spiel.schuetze; return s.trick ? s.trick.name : 'kein Trick'; }));
  await p.tap('#btnPause'); await p.waitForTimeout(200); await p.tap('[data-p="menue"]'); await p.waitForTimeout(300);
  // Halten: Tipp auf den Zielpunkt nach dem Schuss
  await p.tap('[data-m="training"]'); await p.waitForTimeout(200); await p.tap('[data-art="halten"]');
  await p.waitForFunction(() => window.__fps.Spiel.zustand === 'anlauf' && window.__fps.Spiel.menschHaelt && window.__fps.Spiel.versuch.geschossen, null, { timeout: 60000 });
  const ziel = await p.evaluate(() => window.__fps.Spiel.schussInfo.ziel); const sc = await screenOf(ziel.z, ziel.y); await p.touchscreen.tap(sc.x, sc.y - 70);
  await p.waitForTimeout(150);
  await p.waitForFunction(() => window.__fps.Spiel.versuch.ergebnis, null, { timeout: 20000 });
  console.log('Touch-Parade', await p.evaluate(() => { const S = window.__fps.Spiel; return (S.torwart.aktion ? S.torwart.aktion.typ : '-') + ' → ' + S.versuch.ergebnis.code + ', Raus-Knopf: ' + document.querySelectorAll('.trickKnopf.raus').length; }));
  console.log(logs.slice(0, 6).join('\n') || 'keine Konsolenmeldungen');
  await b.close();
})().catch(e => { console.log('ABBRUCH', e.message.split('\n')[0]); process.exit(2); });
