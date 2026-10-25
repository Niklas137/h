/* NAHX Technologies – Live-Animation „Aus Komplexität wird Struktur“ (Canvas, ohne Bibliotheken).
   Ein Feld aus Lichtpunkten und Leiterbahnen: anfangs chaotisch, beim Scrollen ordnet es sich zu einem
   klaren Raster. Signale laufen als Lichtimpulse über die Bahnen. Jede Szene hat eine Kamera
   (zoom, rot, x, y, ordnung, hubs, fluss, hell), zwischen den Szenen wird weich überblendet.
   Ohne Szenen (Unterseiten) läuft eine ruhige, geordnete Fassung hinter dem Inhalt. */
(function () {
  var c = document.getElementById('welt');
  if (!c) { return; }
  var ctx = c.getContext('2d');
  var ruhig = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var W = 0, H = 0, dpr = 1, S = 1;
  function cssRgb(name, fallback) {
    var v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    if (!v) { return fallback; }
    var t = v.split(/[\s,]+/).map(Number);
    return t.length === 3 && !t.some(isNaN) ? t : fallback;
  }
  var CYAN = cssRgb('--akzent-rgb', [34, 184, 224]), WEISS = cssRgb('--punkt-rgb', [238, 241, 239]),
      DUNKEL = cssRgb('--welt-dunkel-rgb', [7, 12, 18]), HELL = cssRgb('--welt-hell-rgb', [246, 245, 242]), TINTE = cssRgb('--welt-tinte-rgb', [11, 22, 32]);

  function size() {
    dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    W = window.innerWidth; H = window.innerHeight; S = Math.max(W, H);
    c.width = Math.round(W * dpr); c.height = Math.round(H * dpr);
    c.style.width = W + 'px'; c.style.height = H + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  window.addEventListener('resize', size); size();

  // deterministischer Zufall, damit das Bild bei jedem Laden gleich ist
  var seed = 7;
  function zufall() { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }

  var lesen = function (el, fallback) {
    var d = el ? el.dataset : {};
    return { zoom: +d.zoom || fallback.zoom, rot: +d.rot || fallback.rot, x: +d.x || fallback.x, y: +d.y || fallback.y,
             ordnung: d.ordnung !== undefined ? +d.ordnung : fallback.ordnung, hubs: +d.hubs || 0, fluss: +d.fluss || 0, hell: +d.hell || 0, alpha: +d.alpha || fallback.alpha };
  };
  var basis = { zoom: 1, rot: 0, x: 0.5, y: 0.5, ordnung: 0.75, alpha: 1 };
  var szenen = Array.prototype.slice.call(document.querySelectorAll('.szene'));
  var K = szenen.map(function (s) { return lesen(s, basis); });
  var fest = szenen.length ? null : lesen(document.querySelector('main'), { zoom: 1.15, rot: 0.12, x: 0.78, y: 0.35, ordnung: 0.8, alpha: 0.5 });

  // Punkte: Chaos-Lage und Ordnungs-Lage (Raster), Einheiten 0..1 relativ zur längeren Seite
  var N = 150, P = [], i, j;
  var SP = 10, ZE = 15;
  for (i = 0; i < N; i++) {
    var gx = i % SP, gy = Math.floor(i / SP);
    P.push({
      cx: zufall() * 1.3 - 0.15, cy: zufall() * 1.3 - 0.15,
      ox: 0.08 + gx * 0.84 / (SP - 1) + (zufall() - 0.5) * 0.015, oy: 0.06 + gy * 0.88 / (ZE - 1) + (zufall() - 0.5) * 0.015,
      ph: zufall() * Math.PI * 2, f: 0.3 + zufall() * 0.5, groesse: 1 + zufall() * 1.6, gx: gx, gy: gy
    });
  }
  // Kanten der Ordnung: Rasternachbarn, ein Teil davon weggelassen, einige Diagonalen (45°-Bahnen)
  var KO = [];
  for (i = 0; i < N; i++) {
    var p = P[i];
    if (p.gx < SP - 1 && zufall() < 0.7) { KO.push([i, i + 1]); }
    if (p.gy < ZE - 1 && zufall() < 0.55) { KO.push([i, i + SP]); }
    if (p.gx < SP - 1 && p.gy < ZE - 1 && zufall() < 0.12) { KO.push([i, i + SP + 1]); }
  }
  // Kanten des Chaos: nächste Nachbarn
  var KC = [];
  for (i = 0; i < N; i++) {
    var best = [];
    for (j = 0; j < N; j++) {
      if (i === j) { continue; }
      var dx = P[i].cx - P[j].cx, dy = P[i].cy - P[j].cy, d = dx * dx + dy * dy;
      if (d < 0.02) { best.push([d, j]); }
    }
    best.sort(function (a, b) { return a[0] - b[0]; });
    for (j = 0; j < Math.min(2, best.length); j++) { if (best[j][1] > i) { KC.push([i, best[j][1]]); } }
  }
  // Impulse: laufen auf Ordnungskanten
  var IMP = [];
  for (i = 0; i < 26; i++) { IMP.push({ k: Math.floor(zufall() * KO.length), t: zufall(), v: 0.25 + zufall() * 0.5 }); }
  // Knoten für die Leistungen (drei Hubs)
  var HUBS = [[0.25, 0.5], [0.5, 0.5], [0.75, 0.5]];

  function glatt(t) { return t * t * (3 - 2 * t); }
  function mix(a, b, t) { return a + (b - a) * t; }
  function rgba(col, a) { return 'rgba(' + col[0] + ',' + col[1] + ',' + col[2] + ',' + Math.max(0, Math.min(1, a)) + ')'; }
  function farbe(a, b, t) { return [mix(a[0], b[0], t), mix(a[1], b[1], t), mix(a[2], b[2], t)]; }

  function kamera() {
    if (fest) { var k = {}; for (var q in fest) { k[q] = fest[q]; } k.p = 0; return k; }
    var y = window.scrollY + H * 0.5, i = 0;
    for (; i < szenen.length - 1; i++) { var s0 = szenen[i]; if (y < s0.offsetTop + s0.offsetHeight) { break; } }
    var s = szenen[i];
    var f = Math.max(0, Math.min(1, (y - s.offsetTop) / s.offsetHeight));
    var a = K[i], b = K[Math.min(i + 1, K.length - 1)];
    var t = glatt(Math.max(0, (f - 0.45) / 0.55));
    // Helligkeit folgt der nächsten Szene: sie hellt erst auf, wenn diese von unten ins Bild rollt
    var naechste = szenen[Math.min(i + 1, szenen.length - 1)];
    var th = glatt(Math.max(0, Math.min(1, (window.scrollY + H * 0.85 - naechste.offsetTop) / (H * 0.35))));
    if (i === szenen.length - 1) { th = 1; }
    var cam = {};
    for (var k2 in a) { cam[k2] = mix(a[k2], b[k2], k2 === 'hell' ? th : t); }
    cam.p = i + f;
    return cam;
  }

  var lage = new Array(N);
  function lagen(cam, zeit) {
    var o = glatt(cam.ordnung), drift = (1 - o) * 0.03 + 0.004;
    for (var i = 0; i < N; i++) {
      var p = P[i];
      var x = mix(p.cx, p.ox, o) + Math.sin(zeit * p.f + p.ph) * drift;
      var y = mix(p.cy, p.oy, o) + Math.cos(zeit * p.f * 0.8 + p.ph) * drift;
      lage[i] = [x * S, y * S];
    }
  }

  var start = performance.now();
  function frame(now) {
    var zeit = (now - start) / 1000, cam = kamera();
    var hell = cam.hell, o = glatt(cam.ordnung);
    var bg = farbe(DUNKEL, HELL, hell), strich = farbe(CYAN, TINTE, hell), punkt = farbe(WEISS, TINTE, hell);
    ctx.fillStyle = rgba(bg, 1); ctx.fillRect(0, 0, W, H);
    var g = ctx.createRadialGradient(W * cam.x, H * cam.y, 0, W * cam.x, H * cam.y, S * 0.6);
    g.addColorStop(0, rgba(CYAN, 0.14 * (1 - hell) * cam.alpha)); g.addColorStop(1, rgba(CYAN, 0));
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);

    lagen(cam, zeit);
    var A = cam.alpha * (1 - hell * 0.55);
    ctx.save();
    ctx.translate(W * cam.x, H * cam.y);
    ctx.rotate(cam.rot + (fest ? 0 : window.scrollY * 0.00015));
    ctx.scale(cam.zoom, cam.zoom);
    ctx.translate(-S * 0.5, -S * 0.5);

    // Chaos-Kanten (verblassen mit der Ordnung)
    var i, k, a2, b2;
    if (o < 0.98) {
      ctx.lineWidth = 0.8; ctx.strokeStyle = rgba(strich, 0.35 * (1 - o) * A);
      ctx.beginPath();
      for (i = 0; i < KC.length; i++) { k = KC[i]; a2 = lage[k[0]]; b2 = lage[k[1]]; ctx.moveTo(a2[0], a2[1]); ctx.lineTo(b2[0], b2[1]); }
      ctx.stroke();
    }
    // Ordnungs-Kanten als Leiterbahnen (erscheinen mit der Ordnung)
    if (o > 0.02) {
      ctx.lineWidth = 1; ctx.strokeStyle = rgba(strich, 0.5 * o * A);
      ctx.beginPath();
      for (i = 0; i < KO.length; i++) { k = KO[i]; a2 = lage[k[0]]; b2 = lage[k[1]]; ctx.moveTo(a2[0], a2[1]); ctx.lineTo(b2[0], b2[1]); }
      ctx.stroke();
      // Lichtimpulse
      for (i = 0; i < IMP.length; i++) {
        var im = IMP[i];
        if (!ruhig) { im.t += im.v * 0.016; }
        if (im.t > 1) { im.t = 0; im.k = Math.floor(zufall() * KO.length); }
        k = KO[im.k]; a2 = lage[k[0]]; b2 = lage[k[1]];
        var x = mix(a2[0], b2[0], im.t), y = mix(a2[1], b2[1], im.t);
        var rg = ctx.createRadialGradient(x, y, 0, x, y, 14);
        rg.addColorStop(0, rgba(punkt, 0.9 * o * A)); rg.addColorStop(0.3, rgba(CYAN, 0.6 * o * A)); rg.addColorStop(1, rgba(CYAN, 0));
        ctx.fillStyle = rg; ctx.beginPath(); ctx.arc(x, y, 14, 0, Math.PI * 2); ctx.fill();
      }
    }
    // Punkte
    for (i = 0; i < N; i++) {
      var p = P[i], l = lage[i];
      var r = p.groesse * (0.8 + 0.4 * Math.sin(zeit * 1.3 + p.ph));
      ctx.fillStyle = rgba(punkt, (0.45 + 0.4 * o) * A);
      ctx.beginPath(); ctx.arc(l[0], l[1], r, 0, Math.PI * 2); ctx.fill();
      if (o > 0.5 && (p.gx + p.gy) % 4 === 0) { // Lötpunkte mit Ring
        ctx.strokeStyle = rgba(strich, 0.7 * (o - 0.5) * 2 * A); ctx.lineWidth = 1;
        ctx.beginPath(); ctx.arc(l[0], l[1], 5, 0, Math.PI * 2); ctx.stroke();
      }
    }
    // Hubs: drei leuchtende Knoten mit Umlaufbahnen
    if (cam.hubs > 0.01) {
      for (i = 0; i < 3; i++) {
        var hx = HUBS[i][0] * S, hy = HUBS[i][1] * S, rr = S * 0.07;
        var hg = ctx.createRadialGradient(hx, hy, 0, hx, hy, rr * 2.2);
        hg.addColorStop(0, rgba(CYAN, 0.28 * cam.hubs * A)); hg.addColorStop(1, rgba(CYAN, 0));
        ctx.fillStyle = hg; ctx.beginPath(); ctx.arc(hx, hy, rr * 2.2, 0, Math.PI * 2); ctx.fill();
        ctx.strokeStyle = rgba(strich, 0.9 * cam.hubs * A); ctx.lineWidth = 1.2;
        ctx.beginPath(); ctx.arc(hx, hy, rr, 0, Math.PI * 2); ctx.stroke();
        ctx.setLineDash([3, 6]); ctx.lineWidth = 0.8;
        ctx.beginPath(); ctx.arc(hx, hy, rr * 1.45, zeit * 0.3 + i, zeit * 0.3 + i + Math.PI * 1.5); ctx.stroke();
        ctx.setLineDash([]);
        var sx = hx + Math.cos(zeit * 0.6 + i * 2) * rr * 1.45, sy = hy + Math.sin(zeit * 0.6 + i * 2) * rr * 1.45;
        ctx.fillStyle = rgba(punkt, 0.95 * cam.hubs * A); ctx.beginPath(); ctx.arc(sx, sy, 3, 0, Math.PI * 2); ctx.fill();
      }
    }
    // Fluss: waagerechte Bahnen mit laufenden Signalen (Ablauf)
    if (cam.fluss > 0.01) {
      for (i = 0; i < 5; i++) {
        var fy = S * (0.3 + i * 0.1);
        ctx.strokeStyle = rgba(strich, 0.35 * cam.fluss * A); ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(0, fy); ctx.lineTo(S, fy); ctx.stroke();
        for (j = 0; j < 3; j++) {
          var fx = ((zeit * (0.06 + i * 0.015) + j / 3 + i * 0.1) % 1) * S;
          var fg = ctx.createLinearGradient(fx - 90, 0, fx, 0);
          fg.addColorStop(0, rgba(CYAN, 0)); fg.addColorStop(1, rgba(punkt, 0.9 * cam.fluss * A));
          ctx.strokeStyle = fg; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(fx - 90, fy); ctx.lineTo(fx, fy); ctx.stroke();
        }
      }
    }
    ctx.restore();
    var v = ctx.createRadialGradient(W / 2, H / 2, S * 0.25, W / 2, H / 2, S * 0.95);
    v.addColorStop(0, rgba(bg, 0)); v.addColorStop(1, rgba(bg, 0.7));
    ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
    document.documentElement.style.setProperty('--welt-hell', hell.toFixed(3));
    if (!ruhig && !document.hidden) { requestAnimationFrame(frame); }
  }
  if (ruhig) { frame(start); window.addEventListener('scroll', function () { frame(performance.now()); }, { passive: true }); }
  else {
    requestAnimationFrame(frame);
    document.addEventListener('visibilitychange', function () { if (!document.hidden) { requestAnimationFrame(frame); } });
  }

  // Schreibmaschine je Szene
  if (szenen.length && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) { return; }
        var el = e.target; io.unobserve(el); el.classList.add('an');
        var warte = 0;
        el.querySelectorAll('.tippe').forEach(function (z) {
          var txt = z.getAttribute('data-text');
          if (ruhig) { z.textContent = txt; z.classList.add('fertig'); return; }
          z.textContent = '';
          setTimeout(function () {
            z.classList.add('tippt'); var i = 0;
            (function tick() {
              z.textContent = txt.slice(0, i);
              if (i++ < txt.length) { setTimeout(tick, 22 + (txt[i - 1] === '.' ? 180 : 0)); }
              else { z.classList.remove('tippt'); z.classList.add('fertig'); }
            })();
          }, warte);
          warte += txt.length * 24 + 350;
        });
      });
    }, { threshold: 0.45 });
    szenen.forEach(function (s) { io.observe(s); });
  } else { szenen.forEach(function (s) { s.classList.add('an'); }); }
})();
