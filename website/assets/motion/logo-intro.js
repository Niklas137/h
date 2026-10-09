/* FSH-Documentation – Logo-Intro beim Start. Übernahme des Skripts aus dem Artefakt „FSH-Documentation – Logo-Intro“
   (Lichtspur, Aufprall mit Glitch, Stoßwelle, Wabengitter, Funken, Name, Glanz, Abgang). Zeitplan: Objekt T. */
(() => {
  "use strict";
  const wurzel = document.getElementById("mo-logo-intro");
  if (!wurzel) return;
  if (!document.documentElement.classList.contains("mo-intro")) { wurzel.remove(); return; }
  const $ = id => wurzel.querySelector("#" + id);
  const buehne = $("buehne");
  /* Seite freigeben: Overlay ausblenden, Lade-Animationen der Seite starten */
  let freigegeben = false;
  function freigeben() {
    if (freigegeben) return; freigegeben = true;
    document.documentElement.classList.remove("mo-intro");
    wurzel.classList.add("mo-logo-aus");
    setTimeout(() => wurzel.remove(), 550);
  }
  const anker = $("anker"), koerper = $("koerper"), zeichen = $("zeichen");
  const spur = $("spur"), ringe = $("ringe"), scheibenBox = $("scheiben");
  const geistEis = $("geistEis"), geistGold = $("geistGold"), glanz = $("glanz");
  const nameBox = $("name"), wortmarke = $("wortmarke"), linie = $("linie"), unterzeile = $("unterzeile");
  const blitz = $("blitz"), raumlicht = $("raumlicht"), ueberspringen = $("ueberspringen");
  const funken = $("funken"), fx = funken.getContext("2d");
  const gitter = $("gitter"), gx = gitter.getContext("2d");
  const URI = zeichen.src;   /* aufgelöste Adresse, damit die Maske aus dem CSS heraus den richtigen Pfad findet */
  wurzel.style.setProperty("--zeichen", `url("${URI}")`);

  const RUHIG = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const NS = "http://www.w3.org/2000/svg";
  const GOLD = "#fbca5e", EIS = "#8fbfe6";

  /* ---------- Geometrie des Zeichens (Koordinaten der Logodatei 472 × 576) ---------- */
  const M = [236, 287];
  const HEX = [[236,6],[467,141],[467,432],[236,568],[5,432],[5,141],[236,6]];
  const HEX_INNEN = [[236,6],[5,141],[5,432],[236,568],[467,432],[467,141],[236,6]]
    .map(([x,y]) => [M[0] + (x-M[0])*.962, M[1] + (y-M[1])*.962]);
  const MONO = [
    [[237,129],[141,185],[141,436],[192,466]],
    [[189,276],[189,215],[286,163],[331,190],[331,248],[286,222],[235,249]],
    [[190,415],[190,335],[286,283],[332,308]],
    [[238,438],[238,364],[289,336]]
  ];
  const linienzug = pts => {
    const seg = []; let L = 0;
    for (let i = 1; i < pts.length; i++) {
      const [ax,ay] = pts[i-1], [bx,by] = pts[i];
      const l = Math.hypot(bx-ax, by-ay); seg.push({ax,ay,bx,by,l,s:L}); L += l;
    }
    return { seg, L, d: "M" + pts.map(p => p[0].toFixed(1)+","+p[1].toFixed(1)).join(" L") };
  };
  const punktBei = (z, p) => {
    const ziel = z.L * Math.min(Math.max(p,0),1);
    for (const s of z.seg) if (ziel <= s.s + s.l) {
      const u = (ziel - s.s) / s.l; return [s.ax + (s.bx-s.ax)*u, s.ay + (s.by-s.ay)*u];
    }
    const s = z.seg[z.seg.length-1]; return [s.bx, s.by];
  };
  const hexA = linienzug(HEX), hexB = linienzug(HEX_INNEN), monos = MONO.map(linienzug);

  /* ---------- SVG der Lichtspur ---------- */
  const el = (tag, attrs, parent) => {
    const n = document.createElementNS(NS, tag);
    for (const k in attrs) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n); return n;
  };
  const defs = el("defs", {}, spur);
  const filter = el("filter", {id:"leuchten", filterUnits:"userSpaceOnUse", x:-90, y:-90, width:652, height:756}, defs);
  el("feGaussianBlur", {in:"SourceGraphic", stdDeviation:9, result:"weit"}, filter);
  el("feGaussianBlur", {in:"SourceGraphic", stdDeviation:2.4, result:"nah"}, filter);
  const merge = el("feMerge", {}, filter);
  ["weit","nah","SourceGraphic"].forEach(n => el("feMergeNode", {in:n}, merge));
  const maske = el("mask", {id:"mono", maskUnits:"userSpaceOnUse", x:-60, y:-60, width:592, height:696}, defs);
  const maskeG = el("g", {fill:"none", "stroke-linecap":"round", "stroke-linejoin":"round"}, maske);
  const monoAussen = monos.map(z => el("path", {d:z.d, stroke:"#fff", "stroke-width":29}, maskeG));
  const monoInnen  = monos.map(z => el("path", {d:z.d, stroke:"#000", "stroke-width":21.5}, maskeG));

  const gEis = el("g", {filter:"url(#leuchten)", opacity:.9}, spur);
  const gGold = el("g", {filter:"url(#leuchten)"}, spur);
  const hexPfadEis = el("path", {d:hexB.d, fill:"none", stroke:EIS, "stroke-width":3.6, "stroke-linecap":"round", "stroke-linejoin":"round"}, gEis);
  el("g", {transform:"translate(7 5)"}, gEis).appendChild(el("rect", {x:-40, y:-40, width:552, height:656, fill:EIS, mask:"url(#mono)"}));
  const hexPfadGold = el("path", {d:hexA.d, fill:"none", stroke:GOLD, "stroke-width":4, "stroke-linecap":"round", "stroke-linejoin":"round"}, gGold);
  el("rect", {x:-40, y:-40, width:552, height:656, fill:GOLD, mask:"url(#mono)"}, gGold);

  const strich = (pfad, L, p) => {
    pfad.setAttribute("stroke-dasharray", `${L} ${L+40}`);
    pfad.setAttribute("stroke-dashoffset", (L * (1 - p)).toFixed(2));
    pfad.style.visibility = p > .002 ? "visible" : "hidden";
  };

  /* Stoßwelle: zwei Sechsecke */
  const ringGold = el("path", {d:hexA.d, stroke:GOLD, "vector-effect":"non-scaling-stroke"}, ringe);
  const ringEis  = el("path", {d:hexA.d, stroke:EIS,  "vector-effect":"non-scaling-stroke"}, ringe);

  /* Scheiben für den Glitch */
  const BAENDER = [0, 13, 24, 37, 49, 58, 71, 83, 100];
  const scheiben = [];
  for (let i = 0; i < BAENDER.length-1; i++) {
    const img = new Image(); img.src = URI; img.alt = ""; img.className = "scheibe"; img.draggable = false;
    img.style.clipPath = `inset(${BAENDER[i]}% 0 ${100-BAENDER[i+1]}% 0)`;
    scheibenBox.appendChild(img); scheiben.push(img);
  }

  /* ---------- Zeitplan (ms) ---------- */
  const T = {
    zuenden: 260,
    hex:   [340, 1180],
    mono:  [860, 760, 150],
    spannung: 1980,
    strahl: [1950, 300],
    aufprall: 2250,
    name:  [2850, 780],
    linie: [3380, 620],
    unter: [3640, 560],
    glanz: [4250, 950],
    abgang:[6200, 950]
  };
  T.ende = T.abgang[0] + T.abgang[1];
  const RUHIG_T = { zeichen:[100, 600], name:[600, 600], abgang:[3400, 500] };
  RUHIG_T.ende = RUHIG_T.abgang[0] + RUHIG_T.abgang[1];

  /* ---------- Hilfen ---------- */
  const k01 = v => v < 0 ? 0 : v > 1 ? 1 : v;
  const anteil = (t, [a, d]) => k01((t - a) / d);
  const eSine = p => -(Math.cos(Math.PI * p) - 1) / 2;
  const eInOut = p => p < .5 ? 4*p*p*p : 1 - Math.pow(-2*p + 2, 3) / 2;
  const eOut = p => 1 - Math.pow(1 - p, 3);
  const eIn = p => p*p*p;
  const zufall = n => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };

  /* ---------- Maße ---------- */
  let dpr = 1, vw = 0, vh = 0, rect = null;
  const abbilden = ([x, y]) => [rect.left + x * rect.width / 472, rect.top + y * rect.height / 576];
  function messen() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    vw = wurzel.clientWidth || innerWidth; vh = wurzel.clientHeight || innerHeight;
    for (const c of [funken, gitter]) { c.width = Math.round(vw * dpr); c.height = Math.round(vh * dpr); }
    fx.setTransform(dpr, 0, 0, dpr, 0, 0);
    gx.setTransform(dpr, 0, 0, dpr, 0, 0);
    rect = anker.getBoundingClientRect();
    const [cx, cy] = abbilden(M);
    gitter.style.setProperty("--cx", cx + "px"); gitter.style.setProperty("--cy", cy + "px");
    gitterZeichnen(cx, cy);
  }
  function gitterZeichnen(cx, cy) {
    gx.clearRect(0, 0, vw, vh);
    const r = rect.width / 4.6, w = Math.sqrt(3) * r, h = 1.5 * r;
    gx.strokeStyle = "rgba(212,185,140,.22)"; gx.lineWidth = 1;
    gx.beginPath();
    const zeilen = Math.ceil(vh / h) + 4, spalten = Math.ceil(vw / w) + 4;
    for (let j = -zeilen; j <= zeilen; j++) for (let i = -spalten; i <= spalten; i++) {
      const x = cx + i * w + (j & 1 ? w / 2 : 0), y = cy + j * h;
      if (x < -w || x > vw + w || y < -h || y > vh + h) continue;
      for (let s = 0; s < 6; s++) {
        const a = Math.PI / 180 * (60 * s - 90), b = Math.PI / 180 * (60 * (s+1) - 90);
        gx.moveTo(x + r * Math.cos(a), y + r * Math.sin(a));
        gx.lineTo(x + r * Math.cos(b), y + r * Math.sin(b));
      }
    }
    gx.stroke();
  }

  /* ---------- Funken ---------- */
  let teile = [];
  const ausstossen = (x, y, farbe, n, staerke = 1) => {
    for (let i = 0; i < n; i++) {
      const a = Math.random() * Math.PI * 2, v = (20 + Math.random() * 80) * staerke;
      teile.push({x, y, vx: Math.cos(a)*v, vy: Math.sin(a)*v - 10, life: 0, max: 260 + Math.random()*420, r: .7 + Math.random()*1.1, farbe, art:"punkt"});
    }
  };
  function aufprallFunken() {
    const [cx, cy] = abbilden(M), rad = rect.width * .42;
    for (let i = 0; i < 54; i++) {
      const a = Math.random() * Math.PI * 2, d = rad * (.5 + Math.random() * .6), v = 420 + Math.random() * 900;
      const z = Math.random();
      teile.push({x: cx + Math.cos(a)*d, y: cy + Math.sin(a)*d*1.1, vx: Math.cos(a)*v, vy: Math.sin(a)*v,
        life: 0, max: 380 + Math.random()*520, r: 1.1 + Math.random(), farbe: z < .68 ? GOLD : z < .93 ? EIS : "#fffaf0", art:"strich"});
    }
    for (let i = 0; i < 26; i++) {
      const a = Math.random() * Math.PI * 2, d = rad * (.3 + Math.random() * .9);
      teile.push({x: cx + Math.cos(a)*d, y: cy + Math.sin(a)*d, vx: (Math.random()-.5)*24, vy: -14 - Math.random()*26,
        life: 0, max: 1400 + Math.random()*1400, r: .6 + Math.random()*.9, farbe: Math.random() < .7 ? GOLD : EIS, art:"glut"});
    }
  }
  const kopfLicht = (x, y, farbe, r, a = 1) => {
    const g = fx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, `rgba(255,252,240,${a})`); g.addColorStop(.25, farbe); g.addColorStop(1, "rgba(0,0,0,0)");
    fx.globalAlpha = a; fx.fillStyle = g; fx.beginPath(); fx.arc(x, y, r, 0, Math.PI*2); fx.fill(); fx.globalAlpha = 1;
  };
  function funkenZeichnen(dt) {
    fx.globalCompositeOperation = "lighter";
    const reib = Math.pow(.9, dt / 16);
    teile = teile.filter(p => (p.life += dt) < p.max);
    for (const p of teile) {
      const s = dt / 1000;
      if (p.art === "strich") { p.vx *= reib; p.vy *= reib; } else { p.vy += (p.art === "glut" ? -6 : 60) * s; }
      p.x += p.vx * s; p.y += p.vy * s;
      const a = 1 - p.life / p.max;
      fx.globalAlpha = a; fx.strokeStyle = p.farbe; fx.fillStyle = p.farbe;
      if (p.art === "strich") {
        fx.lineWidth = p.r; fx.lineCap = "round"; fx.beginPath();
        fx.moveTo(p.x, p.y); fx.lineTo(p.x - p.vx * .035, p.y - p.vy * .035); fx.stroke();
      } else {
        fx.beginPath(); fx.arc(p.x, p.y, p.r * (p.art === "glut" ? 1 : a + .3), 0, Math.PI*2); fx.fill();
      }
    }
    fx.globalAlpha = 1;
  }
  function strahlZeichnen(p) {
    const [cx, cy] = abbilden(M);
    const dx = Math.cos(Math.PI/6), dy = -Math.sin(Math.PI/6);
    const D = Math.hypot(vw, vh) * .62;
    const sx = cx - dx * D, sy = cy - dy * D;
    const q = p * p * .85 + p * .15;
    const hx = sx + (cx - sx) * q, hy = sy + (cy - sy) * q;
    const lang = Math.min(300, D * q + 40);
    const tx = hx - dx * lang, ty = hy - dy * lang;
    for (const [b, al] of [[14, .22], [4, 1]]) {
      const g = fx.createLinearGradient(hx, hy, tx, ty);
      g.addColorStop(0, `rgba(255,250,232,${al})`); g.addColorStop(.25, `rgba(251,202,94,${al*.8})`); g.addColorStop(1, "rgba(251,202,94,0)");
      fx.strokeStyle = g; fx.lineWidth = b; fx.lineCap = "round";
      fx.beginPath(); fx.moveTo(hx, hy); fx.lineTo(tx, ty); fx.stroke();
    }
    kopfLicht(hx, hy, "rgba(251,202,94,.75)", 28, 1);
    ausstossen(hx, hy, GOLD, 2, 1.4);
  }

  /* ---------- Zustand je Zeitpunkt ---------- */
  let start = 0, letzte = 0, laeuft = false, aufprallGezeigt = false;

  function setzeEnde() {
    teile = [];
    freigeben();
  }

  function ruhigBild(t) {
    const z = eOut(anteil(t, RUHIG_T.zeichen)), n = eOut(anteil(t, RUHIG_T.name)), e = anteil(t, RUHIG_T.abgang);
    spur.style.opacity = 0;
    koerper.style.opacity = z * (1 - e); koerper.style.transform = "none"; zeichen.style.visibility = "visible";
    raumlicht.style.opacity = z;
    nameBox.style.opacity = n * (1 - e); linie.style.transform = `scaleX(${n})`; unterzeile.style.opacity = n;
    wortmarke.style.setProperty("--ls", ".2em");
    if (e > 0) freigeben();
    ueberspringen.style.opacity = t > 300 && e === 0 ? 1 : 0;
  }

  function bild(t, dt) {
    /* Raumlicht */
    const ph = anteil(t, T.hex);
    const nach = t - T.aufprall;
    raumlicht.style.opacity = nach < 0 ? .25 + .35 * ph : Math.min(1, .6 + nach / 300) * (.9 + .1 * Math.sin(t / 700));

    /* Lichtspur: Sechseck */
    const hp = eSine(ph);
    strich(hexPfadGold, hexA.L, hp);
    strich(hexPfadEis, hexB.L, hp);

    /* Lichtspur: Monogramm als Leuchtröhre */
    const mp = monos.map((z, i) => eInOut(k01((t - (T.mono[0] + i * T.mono[2])) / T.mono[1])));
    monos.forEach((z, i) => { strich(monoAussen[i], z.L, mp[i]); strich(monoInnen[i], z.L, mp[i]); });

    let so = nach < 0 ? 1 : 1 - k01(nach / 260);
    if (t > T.spannung && nach < 0) so *= .78 + .22 * Math.abs(Math.sin(t * .11));
    spur.style.opacity = so;

    /* Funken an den Lichtköpfen */
    fx.clearRect(0, 0, vw, vh);
    fx.globalCompositeOperation = "lighter";
    if (t > T.zuenden && t < T.hex[0] + 60) {
      const f = k01((t - T.zuenden) / 80);
      const [x, y] = abbilden(HEX[0]);
      kopfLicht(x, y, "rgba(251,202,94,.8)", 10 + 16 * f, f);
    }
    if (ph > 0 && ph < 1) {
      const [gx1, gy1] = abbilden(punktBei(hexA, hp)), [ex, ey] = abbilden(punktBei(hexB, hp));
      kopfLicht(gx1, gy1, "rgba(251,202,94,.8)", 16); kopfLicht(ex, ey, "rgba(143,191,230,.75)", 13);
      ausstossen(gx1, gy1, GOLD, 2); ausstossen(ex, ey, EIS, 1);
    }
    mp.forEach((p, i) => {
      if (p > 0 && p < 1) {
        const pt = punktBei(monos[i], p);
        const [x, y] = abbilden(pt), [x2, y2] = abbilden([pt[0] + 7, pt[1] + 5]);
        kopfLicht(x, y, "rgba(251,202,94,.8)", 13); kopfLicht(x2, y2, "rgba(143,191,230,.7)", 9, .8);
        ausstossen(x, y, GOLD, 1);
      }
    });
    const sp = anteil(t, T.strahl);
    if (sp > 0 && sp < 1) strahlZeichnen(sp);
    if (nach >= 0 && !aufprallGezeigt) { aufprallGezeigt = true; aufprallFunken(); }
    funkenZeichnen(dt);

    /* Zeichen springt auf */
    if (nach < 0) {
      koerper.style.opacity = 0;
    } else {
      const u = nach / 1000;
      let s = 1 - .24 * Math.exp(-6.2 * u) * Math.cos(15.5 * u);
      const ea = eIn(anteil(t, T.abgang));
      s *= 1 + 17 * ea;
      koerper.style.opacity = ea > .78 ? 1 - (ea - .78) / .22 : 1;
      koerper.style.transform = `scale(${s.toFixed(4)})`;
      koerper.style.filter = ea > .35 ? `blur(${((ea - .35) * 14).toFixed(2)}px)` : "none";

      /* Glitch in kurzen Takten */
      const takt = Math.floor(nach / 58);
      const glitch = nach < 400;
      zeichen.style.visibility = glitch ? "hidden" : "visible";
      scheiben.forEach((img, i) => {
        img.style.visibility = glitch ? "visible" : "hidden";
        if (glitch) {
          const r = zufall(takt * 17 + i * 3.7), stark = 1 - nach / 400;
          const dx = r > .42 ? (zufall(takt * 29 + i * 5.3) * 2 - 1) * rect.width * .09 * stark : 0;
          img.style.transform = `translateX(${dx.toFixed(1)}px)`;
        }
      });

      /* Farbversatz an den Kanten */
      const g = Math.exp(-nach / 210);
      const zit = nach < 400 ? (zufall(takt * 7.1) - .5) * 6 : 0;
      const off = rect.width * .055 * g;
      geistEis.style.opacity = Math.min(1, g * 1.4);
      geistGold.style.opacity = Math.min(1, g * 1.4);
      geistEis.style.transform = `translate(${(-off + zit).toFixed(1)}px, ${(off * .25).toFixed(1)}px)`;
      geistGold.style.transform = `translate(${(off - zit).toFixed(1)}px, ${(-off * .2).toFixed(1)}px)`;
    }

    /* Blitz */
    blitz.style.opacity = nach < 0 ? 0 : nach < 70 ? (nach / 70) * .8 : .8 * Math.exp(-(nach - 70) / 180);

    /* Stoßwelle */
    [[ringGold, 0, 2.5, 3], [ringEis, 90, 1.9, 2]].forEach(([ring, verz, weite, breite]) => {
      const d = nach - verz;
      if (d < 0 || d > 1050) { ring.style.opacity = 0; return; }
      const q = d / 1050, s = 1 + weite * eOut(q);
      ring.setAttribute("transform", `translate(${M[0]} ${M[1]}) scale(${s.toFixed(4)}) translate(${-M[0]} ${-M[1]})`);
      ring.setAttribute("stroke-width", (breite * (1 - q) + .5).toFixed(2));
      ring.style.opacity = (Math.pow(1 - q, 1.5) * .9).toFixed(3);
    });

    /* Wabengitter, vom Licht der Welle getroffen */
    if (nach >= 0) {
      const r = eOut(k01(nach / 1400)) * Math.hypot(vw, vh) * .8;
      gitter.style.setProperty("--r", r.toFixed(0) + "px");
      gitter.style.opacity = (1 - k01((nach - 450) / 950)).toFixed(3);
    } else gitter.style.opacity = 0;

    /* Name */
    const n = eOut(anteil(t, T.name));
    const ea2 = anteil(t, T.abgang);
    const weg = eOut(k01(ea2 * 2.6));
    nameBox.style.opacity = (n * (1 - weg)).toFixed(3);
    nameBox.style.transform = `translateY(${((1 - n) * 12 + weg * 10).toFixed(1)}px)`;
    wortmarke.style.setProperty("--ls", (.62 - .42 * n).toFixed(3) + "em");
    wortmarke.style.filter = n < 1 ? `blur(${((1 - n) * 14).toFixed(2)}px)` : (weg > 0 ? `blur(${(weg * 6).toFixed(2)}px)` : "none");
    const x = (1 - n) * 7;
    wortmarke.style.textShadow = n < 1 ? `${-x}px 0 rgba(143,191,230,${(.8 * (1 - n)).toFixed(2)}), ${x}px 0 rgba(251,202,94,${(.8 * (1 - n)).toFixed(2)})` : "none";
    linie.style.transform = `scaleX(${eInOut(anteil(t, T.linie)).toFixed(3)})`;
    const u2 = eOut(anteil(t, T.unter));
    unterzeile.style.opacity = u2.toFixed(3);
    unterzeile.style.transform = `translateY(${((1 - u2) * 6).toFixed(1)}px)`;

    /* Glanz über das Gold */
    const gq = anteil(t, T.glanz);
    glanz.style.opacity = gq > 0 && gq < 1 ? Math.sin(Math.PI * gq).toFixed(3) : 0;
    glanz.style.backgroundPosition = `${(140 - 180 * eInOut(gq)).toFixed(1)}% 0`;

    /* Übergang zur Seite */
    ueberspringen.style.opacity = t > 700 && ea2 === 0 ? 1 : 0;
    if (ea2 > .55) freigeben();   /* Seite erscheint hinter dem ausblendenden Intro */
  }

  function schleife(jetzt) {
    if (!laeuft) return;
    const t = jetzt - start, dt = Math.min(48, jetzt - letzte || 16); letzte = jetzt;
    if (RUHIG) {
      ruhigBild(t);
      if (t >= RUHIG_T.ende) { laeuft = false; setzeEnde(); return; }
    } else {
      bild(t, dt);
      if (t >= T.ende) { laeuft = false; setzeEnde(); return; }
    }
    requestAnimationFrame(schleife);
  }

  function abspielen() {
    teile = []; aufprallGezeigt = false;
    buehne.style.display = "flex";
    koerper.style.cssText = ""; nameBox.style.opacity = 0;
    messen();
    start = performance.now(); letzte = start; laeuft = true;
    requestAnimationFrame(schleife);
  }
  function ueberspringenJetzt() {
    if (!laeuft) return;
    laeuft = false; setzeEnde();
  }

  ueberspringen.addEventListener("click", ueberspringenJetzt);
  addEventListener("keydown", e => { if (e.key === "Escape" && laeuft) ueberspringenJetzt(); });
  setTimeout(() => { if (laeuft) ueberspringenJetzt(); else if (!freigegeben) freigeben(); }, 12000); /* Sicherheitsnetz */
  addEventListener("resize", () => { if (laeuft) messen(); });

  const los = () => (zeichen.decode ? zeichen.decode().catch(() => {}) : Promise.resolve()).then(abspielen);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(los); else los();
})();
