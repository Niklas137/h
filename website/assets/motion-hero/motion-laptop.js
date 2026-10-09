/* Motion-Laptop-Hero – Timeline, Partikel, Screen-Canvas. Keine Abhängigkeiten.
   Abschnitte: 1 Timeline, 2 Hintergrund-Partikel, 3 Screen 3 (Wellen), 4 Screen 6 (Funken), 5 Sichtbarkeit, 6 Start. */
(function () {
  'use strict';
  var reduziert = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- 0 Intro-Overlay (Startseite): läuft einmal je Sitzung, dann Seite freigeben ---------- */
  function beendeIntro(overlay, stopp) {
    if (!overlay || overlay.classList.contains('ml-intro-aus')) { return; }
    overlay.classList.add('ml-intro-aus');
    document.documentElement.classList.remove('mo-intro');   /* Lade-Animationen der Seite starten jetzt */
    setTimeout(function () { stopp(); overlay.remove(); }, 950);
  }

  Array.prototype.slice.call(document.querySelectorAll('.motion-laptop')).forEach(starte);

  function starte(wurzel) {
  var overlay = wurzel.closest('.ml-intro-overlay');
  if (overlay && (!document.documentElement.classList.contains('mo-intro') || reduziert)) { overlay.remove(); return; }

  /* ---------- 1 Timeline (Millisekunden ab Loop-Start, Loop = DAUER) ---------- */
  var DAUER = 16000;
  var AKZENT = (getComputedStyle(wurzel).getPropertyValue('--ml-akzent-rgb') || '67,174,232').trim();
  var HELL = '244,241,236';   /* FSH-Hellton statt Reinweiß */
  var TIMELINE = [            /* Screen-Wechsel: [Zeit, Screen-Index 0-5, Glow-Farbe für Gehäuse und Spiegelung] */
    [2500, 0, 'rgba(' + AKZENT + ',.14)'],
    [4000, 1, 'rgba(' + AKZENT + ',.45)'],
    [5800, 2, 'rgba(' + AKZENT + ',.22)'],
    [7500, 3, 'rgba(27,99,168,.45)'],
    [9000, 4, 'rgba(' + AKZENT + ',.20)'],
    [11000, 5, 'rgba(' + HELL + ',.16)'],
    [13000, 0, 'rgba(' + AKZENT + ',.14)']
  ];
  var screens = Array.prototype.slice.call(wurzel.querySelectorAll('.ml-screen'));
  var aktiv = -1, start = null, laeuft = true, sichtbar = true, zeitImLoop = 0;

  function zeige(i, glow) {
    if (i === aktiv) { return; }
    screens.forEach(function (s, k) {
      if (k === aktiv) { s.classList.remove('aktiv'); s.classList.add('raus'); }
      else if (k !== i) { s.classList.remove('raus'); }
    });
    var neu = screens[i];
    neu.classList.remove('raus');
    void neu.offsetWidth;           /* Reflow, damit die Transition von .96/blur startet */
    neu.classList.add('aktiv');
    wurzel.style.setProperty('--ml-screen-glow', glow);
    aktiv = i;
  }

  /* ---------- 2 Hintergrund-Partikel ---------- */
  var cv = wurzel.querySelector('.ml-partikel'), ctx = cv.getContext('2d');
  var dpr = Math.min(window.devicePixelRatio || 1, 2), B = 0, H = 0, teilchen = [];
  var ANZAHL = 70;
  function groesse() {
    B = wurzel.clientWidth; H = wurzel.clientHeight;
    cv.width = B * dpr; cv.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  function neuesTeilchen(t) {
    t = t || {};
    t.x = Math.random() * B; t.y = Math.random() * H;
    t.art = Math.random();                           /* <.55 Punkt, <.8 Strich, sonst Funke */
    t.orange = Math.random() < 0.45;
    t.r = 0.6 + Math.random() * 1.6;
    t.vx = 0.08 + Math.random() * 0.25; t.vy = -(0.05 + Math.random() * 0.18);
    t.alpha = 0.25 + Math.random() * 0.55;
    t.laenge = 6 + Math.random() * 14;
    return t;
  }
  for (var i = 0; i < ANZAHL; i++) { teilchen.push(neuesTeilchen()); }

  function malePartikel(tempo) {
    ctx.clearRect(0, 0, B, H);
    for (var i = 0; i < teilchen.length; i++) {
      var t = teilchen[i];
      t.x += t.vx * tempo; t.y += t.vy * tempo;
      if (t.x > B + 20 || t.y < -20) { neuesTeilchen(t); t.x = -10 + Math.random() * B * 0.3; t.y = H * (0.3 + Math.random() * 0.8); }
      var farbe = t.orange ? AKZENT : HELL;
      if (t.art < 0.55) {
        ctx.fillStyle = 'rgba(' + farbe + ',' + t.alpha + ')';
        ctx.beginPath(); ctx.arc(t.x, t.y, t.r, 0, 6.283); ctx.fill();
      } else {
        var l = t.laenge * (t.art > 0.8 ? 1.8 : 1) * Math.min(tempo, 4) * 0.6;
        var g = ctx.createLinearGradient(t.x, t.y, t.x - l, t.y - l * 0.6);
        g.addColorStop(0, 'rgba(' + farbe + ',' + t.alpha + ')'); g.addColorStop(1, 'rgba(' + farbe + ',0)');
        ctx.strokeStyle = g; ctx.lineWidth = t.art > 0.8 ? 1.4 : 0.8;
        ctx.beginPath(); ctx.moveTo(t.x, t.y); ctx.lineTo(t.x - l, t.y - l * 0.6); ctx.stroke();
      }
    }
  }

  /* ---------- 3 Screen 3: 3D-Wellen-Grid ---------- */
  var c3 = wurzel.querySelector('.ml-s3 canvas'), x3 = c3.getContext('2d');
  function groesse3() { c3.width = c3.clientWidth * dpr; c3.height = c3.clientHeight * dpr; x3.setTransform(dpr, 0, 0, dpr, 0, 0); }
  var FARBEN3 = ['67,174,232', '108,192,240', '27,99,168', '244,241,236'];
  function maleWellen(zeit) {
    var w = c3.clientWidth, h = c3.clientHeight; if (!w) { return; }
    x3.clearRect(0, 0, w, h);
    var spalten = 26, zeilen = 14, horizont = h * 0.28, ph = zeit / 900;
    for (var z = 0; z < zeilen; z++) {
      var tiefe = z / (zeilen - 1);                  /* 0 hinten, 1 vorn */
      var persp = 0.25 + tiefe * 0.75;
      var y0 = horizont + (h - horizont) * Math.pow(tiefe, 1.5);
      for (var s = 0; s < spalten; s++) {
        var u = s / (spalten - 1) - 0.5;
        var x = w / 2 + u * w * 1.3 * persp;
        var welle = Math.sin(u * 7 + ph) * Math.cos(tiefe * 5 - ph * 0.8) * 16 * persp;
        var y = y0 + welle;
        var r = 0.8 + persp * 2.2, a = 0.25 + persp * 0.6;
        x3.fillStyle = 'rgba(' + FARBEN3[(s + z) % FARBEN3.length] + ',' + a + ')';
        x3.beginPath(); x3.arc(x, y, r, 0, 6.283); x3.fill();
      }
    }
    var g = x3.createLinearGradient(0, 0, 0, h); g.addColorStop(0, 'rgba(11,17,25,.9)'); g.addColorStop(0.35, 'rgba(11,17,25,0)');
    x3.fillStyle = g; x3.fillRect(0, 0, w, h);
  }

  /* ---------- 4 Screen 6: Funken ---------- */
  var c6 = wurzel.querySelector('.ml-s6 canvas'), x6 = c6.getContext('2d'), funken = [];
  function groesse6() { c6.width = c6.clientWidth * dpr; c6.height = c6.clientHeight * dpr; x6.setTransform(dpr, 0, 0, dpr, 0, 0); }
  function neuerFunke(f) {
    f = f || {}; var w = c6.clientWidth, h = c6.clientHeight;
    f.x = Math.random() * w * 1.4 - w * 0.2; f.y = Math.random() * h * 1.4 - h * 0.2;
    var v = 4 + Math.random() * 9; f.vx = v; f.vy = -v * 0.55;
    f.l = 10 + Math.random() * 40; f.orange = Math.random() < 0.5; f.a = 0.3 + Math.random() * 0.7; return f;
  }
  for (var k = 0; k < 90; k++) { funken.push(neuerFunke()); }
  function maleFunken() {
    var w = c6.clientWidth, h = c6.clientHeight; if (!w) { return; }
    x6.fillStyle = 'rgba(11,17,25,.35)'; x6.fillRect(0, 0, w, h);
    for (var i = 0; i < funken.length; i++) {
      var f = funken[i]; f.x += f.vx; f.y += f.vy;
      if (f.x > w + 60 || f.y < -60) { neuerFunke(f); f.x = -40 - Math.random() * w * 0.3; f.y = h * (0.4 + Math.random() * 0.9); }
      var farbe = f.orange ? AKZENT : HELL;
      var g = x6.createLinearGradient(f.x, f.y, f.x - f.l, f.y + f.l * 0.55);
      g.addColorStop(0, 'rgba(' + farbe + ',' + f.a + ')'); g.addColorStop(1, 'rgba(' + farbe + ',0)');
      x6.strokeStyle = g; x6.lineWidth = f.orange ? 1.6 : 1;
      x6.beginPath(); x6.moveTo(f.x, f.y); x6.lineTo(f.x - f.l, f.y + f.l * 0.55); x6.stroke();
    }
  }

  /* ---------- 5 Sichtbarkeit (IntersectionObserver), Größe ---------- */
  function alleGroessen() { groesse(); groesse3(); groesse6(); }
  alleGroessen();
  var resizeTimer;
  window.addEventListener('resize', function () { clearTimeout(resizeTimer); resizeTimer = setTimeout(alleGroessen, 120); }, { passive: true });
  if (!overlay && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (e) {
      sichtbar = e[0].isIntersecting;
      wurzel.classList.toggle('ml-pausiert', !sichtbar);
      if (sichtbar && laeuft) { start = null; requestAnimationFrame(schritt); }
    }, { threshold: 0.05 }).observe(wurzel);
  }
  document.addEventListener('visibilitychange', function () {
    if (!document.hidden && sichtbar && laeuft) { start = null; requestAnimationFrame(schritt); }
  });

  /* ---------- 6 Hauptschleife ---------- */
  var letzterSchritt = 0;
  var introDauer = overlay ? parseInt(wurzel.getAttribute('data-intro') || '5600', 10) : 0, introStart = null;
  function stopp() { laeuft = false; sichtbar = false; }
  if (overlay) {
    var skip = overlay.querySelector('.ml-intro-skip');
    if (skip) { skip.addEventListener('click', function () { beendeIntro(overlay, stopp); }); }
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { beendeIntro(overlay, stopp); } });
    setTimeout(function () { beendeIntro(overlay, stopp); }, introDauer + 2500);   /* Sicherheitsnetz, falls rAF nicht läuft */
  }
  function schritt(jetzt) {
    if (!laeuft || !sichtbar || document.hidden) { return; }
    if (overlay) {
      if (introStart === null) { introStart = jetzt; }
      if (jetzt - introStart >= introDauer) { beendeIntro(overlay, stopp); return; }
    }
    if (start === null) { start = jetzt - zeitImLoop; letzterSchritt = jetzt; }
    zeitImLoop = (jetzt - start) % DAUER;
    var dt = Math.min((jetzt - letzterSchritt) / 16.67, 3); letzterSchritt = jetzt;
    for (var i = TIMELINE.length - 1; i >= 0; i--) {
      if (zeitImLoop >= TIMELINE[i][0]) { zeige(TIMELINE[i][1], TIMELINE[i][2]); break; }
    }
    if (zeitImLoop < TIMELINE[0][0] && aktiv !== 0 && aktiv !== -1) { zeige(0, TIMELINE[0][2]); }
    if (!reduziert) {
      malePartikel((aktiv === 5 ? 7 : 1) * dt);
      if (aktiv === 2) { maleWellen(jetzt); }
      if (aktiv === 5) { maleFunken(); }
    }
    requestAnimationFrame(schritt);
  }

  if (reduziert) {
    /* Reduzierte Bewegung: fester Zustand, Screen 5 (Analytics) als Inhalt sichtbar, kein Canvas. */
    zeige(4, 'rgba(' + AKZENT + ',.2)');
    malePartikel(0);
    return;
  }
  zeige(0, TIMELINE[0][2]);
  requestAnimationFrame(schritt);
  }
})();
