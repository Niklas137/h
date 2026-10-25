/* NAHX Technologies – Live-Animation der Startseite (Canvas, ohne Bibliotheken).
   Eine gravierte Mechanik aus Zahnrädern, Ringen und Wellenlinien läuft dauerhaft und
   wird zusätzlich vom Scrollen gesteuert: jede Szene hat eine Kamera (Zoom, Drehung,
   Versatz, Tunnel, Helligkeit), zwischen den Szenen wird weich überblendet. */
(function () {
  var c = document.getElementById('welt');
  if (!c) { return; }
  var ctx = c.getContext('2d');
  var ruhig = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var W = 0, H = 0, dpr = 1;
  var CYAN = [34, 184, 224], DUNKEL = [7, 12, 18], HELL = [246, 245, 242], TINTE = [11, 22, 32];

  function size() {
    dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    W = window.innerWidth; H = window.innerHeight;
    c.width = Math.round(W * dpr); c.height = Math.round(H * dpr);
    c.style.width = W + 'px'; c.style.height = H + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  window.addEventListener('resize', size); size();

  var szenen = Array.prototype.slice.call(document.querySelectorAll('.szene'));
  // Kamera je Szene: zoom, rot (rad), x/y (Anteil der Breite/Höhe), tunnel 0..1, wellen 0..1, hell 0..1, dichte
  var K = szenen.map(function (s) {
    var d = s.dataset;
    return { zoom: +d.zoom || 1, rot: +d.rot || 0, x: +d.x || 0.5, y: +d.y || 0.5, tunnel: +d.tunnel || 0,
             wellen: +d.wellen || 0, hell: +d.hell || 0, dichte: +d.dichte || 1 };
  });
  if (!K.length) { return; }

  // Zahnräder der Welt (Einheiten relativ zur kürzeren Seite)
  var R = [
    { x: 0.62, y: 0.50, r: 0.34, z: 24, v: 1 },
    { x: 0.18, y: 0.22, r: 0.16, z: 14, v: -1.9 },
    { x: 0.22, y: 0.80, r: 0.12, z: 11, v: -2.4 },
    { x: 0.96, y: 0.12, r: 0.11, z: 10, v: 2.6 },
    { x: 1.02, y: 0.86, r: 0.18, z: 15, v: -1.7 },
    { x: 0.42, y: 0.08, r: 0.07, z: 8, v: 3.6 },
    { x: 0.80, y: 0.98, r: 0.09, z: 9, v: 3.1 }
  ];

  function glatt(t) { return t * t * (3 - 2 * t); }
  function mix(a, b, t) { return a + (b - a) * t; }
  function rgba(col, a) { return 'rgba(' + col[0] + ',' + col[1] + ',' + col[2] + ',' + a + ')'; }

  function kamera() {
    var y = window.scrollY + H * 0.5, i = 0;
    for (; i < szenen.length - 1; i++) {
      var s = szenen[i];
      if (y < s.offsetTop + s.offsetHeight) { break; }
    }
    var s = szenen[i];
    var f = Math.max(0, Math.min(1, (y - s.offsetTop) / s.offsetHeight));
    var a = K[i], b = K[Math.min(i + 1, K.length - 1)];
    // Überblendung in der zweiten Hälfte der Szene
    var t = glatt(Math.max(0, (f - 0.45) / 0.55));
    var th = glatt(Math.max(0, (f - 0.82) / 0.18)); // Helligkeit wechselt erst ganz am Ende
    var cam = {};
    for (var k in a) { cam[k] = mix(a[k], b[k], k === 'hell' ? th : t); }
    cam.p = i + f;
    return cam;
  }

  function zahnrad(x, y, r, z, ang, strich, alpha, dichte) {
    var i, w, rad, aussen = r, innen = r * 0.86;
    ctx.save();
    ctx.translate(x, y); ctx.rotate(ang);
    ctx.lineWidth = 1.2;
    ctx.strokeStyle = rgba(strich, alpha);
    // Zahnkranz
    ctx.beginPath();
    for (i = 0; i < z * 4; i++) {
      w = Math.PI * 2 * i / (z * 4);
      rad = (i % 4 < 2) ? aussen : innen;
      if (i === 0) { ctx.moveTo(rad * Math.cos(w), rad * Math.sin(w)); } else { ctx.lineTo(rad * Math.cos(w), rad * Math.sin(w)); }
    }
    ctx.closePath(); ctx.stroke();
    // Gravur: radiale Schraffur
    var n = Math.round(z * 6 * dichte);
    ctx.beginPath();
    for (i = 0; i < n; i++) {
      w = Math.PI * 2 * i / n;
      var r1 = r * (i % 3 === 0 ? 0.48 : 0.58), r2 = r * 0.80;
      ctx.moveTo(r1 * Math.cos(w), r1 * Math.sin(w));
      ctx.lineTo(r2 * Math.cos(w), r2 * Math.sin(w));
    }
    ctx.strokeStyle = rgba(strich, alpha * 0.45); ctx.lineWidth = 0.8; ctx.stroke();
    // Ringe
    ctx.setLineDash([2, 4]);
    ctx.strokeStyle = rgba(strich, alpha * 0.7); ctx.lineWidth = 1;
    ctx.beginPath(); ctx.arc(0, 0, r * 0.84, 0, Math.PI * 2); ctx.stroke();
    ctx.beginPath(); ctx.arc(0, 0, r * 0.44, 0, Math.PI * 2); ctx.stroke();
    ctx.setLineDash([]);
    ctx.beginPath(); ctx.arc(0, 0, r * 0.16, 0, Math.PI * 2); ctx.stroke();
    // Speichen
    ctx.beginPath();
    for (i = 0; i < 6; i++) {
      w = Math.PI * 2 * i / 6;
      ctx.moveTo(r * 0.16 * Math.cos(w), r * 0.16 * Math.sin(w));
      ctx.lineTo(r * 0.44 * Math.cos(w), r * 0.44 * Math.sin(w));
    }
    ctx.strokeStyle = rgba(strich, alpha * 0.9); ctx.lineWidth = 1.4; ctx.stroke();
    ctx.restore();
  }

  function tunnel(cx, cy, t, staerke, strich, alpha, zeit) {
    // Ringe, die aus der Tiefe kommen; t läuft mit dem Scroll weiter
    var basis = Math.min(W, H) * 0.06, n = 14, i;
    for (i = 0; i < n; i++) {
      var k = (i + t) % n;
      var r = basis * Math.pow(1.22, k);
      var a = alpha * staerke * Math.min(1, k / 4) * (1 - k / n * 0.6);
      zahnrad(cx, cy, r, 10 + i, zeit * (i % 2 ? 0.08 : -0.06) + i, strich, a, 0.5);
    }
  }

  function wellen(staerke, strich, alpha, zeit) {
    var reihen = 9, i, x, y;
    ctx.lineWidth = 1;
    for (i = 0; i < reihen; i++) {
      var yb = H * (0.55 + i * 0.05);
      ctx.strokeStyle = rgba(strich, alpha * staerke * (0.25 + i / reihen * 0.6));
      ctx.beginPath();
      for (x = 0; x <= W; x += 6) {
        y = yb + Math.sin(x * 0.012 + zeit * 0.9 + i * 0.7) * (6 + i * 2) + Math.sin(x * 0.03 - zeit * 0.5) * 3;
        if (x === 0) { ctx.moveTo(x, y); } else { ctx.lineTo(x, y); }
      }
      ctx.stroke();
    }
  }

  var start = performance.now();
  function frame(now) {
    var zeit = (now - start) / 1000, cam = kamera();
    var hell = cam.hell;
    var bg = [mix(DUNKEL[0], HELL[0], hell), mix(DUNKEL[1], HELL[1], hell), mix(DUNKEL[2], HELL[2], hell)];
    var strich = [mix(CYAN[0], TINTE[0], hell), mix(CYAN[1], TINTE[1], hell), mix(CYAN[2], TINTE[2], hell)];
    ctx.fillStyle = rgba(bg, 1); ctx.fillRect(0, 0, W, H);
    // Lichtschein
    var g = ctx.createRadialGradient(W * cam.x, H * cam.y, 0, W * cam.x, H * cam.y, Math.max(W, H) * 0.7);
    g.addColorStop(0, rgba(CYAN, 0.16 * (1 - hell))); g.addColorStop(1, rgba(CYAN, 0));
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);

    var alpha = 0.9 - hell * 0.5;
    var s = Math.min(W, H);
    ctx.save();
    ctx.translate(W * cam.x, H * cam.y);
    ctx.rotate(cam.rot + window.scrollY * 0.0004);
    ctx.scale(cam.zoom, cam.zoom);
    ctx.translate(-W * 0.5, -H * 0.5);
    var tiefe = 1 - cam.tunnel;
    for (var i = 0; i < R.length; i++) {
      var z = R[i];
      var ang = zeit * 0.12 * z.v + window.scrollY * 0.0015 * z.v;
      zahnrad(W * z.x, H * z.y, s * z.r, z.z, ang, strich, alpha * tiefe * (i === 0 ? 1 : 0.75), cam.dichte);
    }
    ctx.restore();
    if (cam.tunnel > 0.01) { tunnel(W * 0.5, H * 0.5, (cam.p * 6 + zeit * 0.3) % 14, cam.tunnel, strich, alpha, zeit); }
    if (cam.wellen > 0.01) { wellen(cam.wellen, strich, alpha, zeit); }
    // leichte Vignette
    var v = ctx.createRadialGradient(W / 2, H / 2, s * 0.3, W / 2, H / 2, s * 1.1);
    v.addColorStop(0, rgba(bg, 0)); v.addColorStop(1, rgba(bg, 0.75));
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
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (!e.isIntersecting) { return; }
      var el = e.target; io.unobserve(el);
      el.classList.add('an');
      var zeilen = el.querySelectorAll('.tippe');
      var warte = 0;
      zeilen.forEach(function (z) {
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
})();
