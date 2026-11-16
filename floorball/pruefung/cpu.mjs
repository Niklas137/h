// Rechenzeit je Spielbild (Simulation + Animation, ohne GPU) bei 4-fach gedrosselter CPU als Näherung für ein Mittelklasse-Handy
import { oeffne, starteMatch, bullyGewinnen } from './tb.mjs';
const { browser, p, fehler } = await oeffne({ pads: 1, mobil: process.argv[2] === 'mobil' });
await starteMatch(p); await bullyGewinnen(p);
const cdp = await p.context().newCDPSession(p); await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
const r = await p.evaluate(() => { const M = window.__fps.Match, E = window.__fps.Eingabe, ms = []; for (let i = 0; i < 150; i++) { const t = performance.now(); E.pollen(); M.frame(1 / 60); ms.push(performance.now() - t); } ms.sort((a, b) => a - b); return { median: +ms[75].toFixed(2), p95: +ms[142].toFixed(2), spar: M.spar }; });
console.log('Rechenzeit je Bild (ms, CPU /4):', JSON.stringify(r)); console.log(fehler.join('\n') || 'keine JS-Fehler'); await browser.close();
