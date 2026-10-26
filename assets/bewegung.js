/* NAHX Technologies – Bewegung (ohne Bibliothek).
   Ein Scroll-Takt setzt je Szene den Fortschritt --p (0 = Szene kommt von unten, 1 = Szene ist oben weg).
   Alles weitere ist CSS. Inspektionslicht folgt dem Zeiger über Fotos (nur Zeigergeräte, nie bei reduzierter Bewegung).
   Zahlen zählen beim Erscheinen einmal hoch. Keine Dauerbewegung. Startseite: Flug durch A-Portale (3D, scrollgesteuert). */
(function () {
  var html = document.documentElement;
  var ruhig = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fein = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  // Menü
  var m = document.querySelector('.menue-schalter'), n = document.getElementById('nav'), K = document.querySelector('.kopf');
  if (m && n) {
    m.addEventListener('click', function () { var o = n.classList.toggle('offen'); m.setAttribute('aria-expanded', o ? 'true' : 'false'); K.classList.toggle('kopf-offen', o); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && n.classList.contains('offen')) { n.classList.remove('offen'); m.setAttribute('aria-expanded', 'false'); K.classList.remove('kopf-offen'); m.focus(); } });
  }

  // Einblenden (einmalig) und Zähler
  var R = document.querySelectorAll('.reveal');
  function zaehle(el) {
    var ziel = el.getAttribute('data-zahl'); if (ziel === null) return;
    var z = parseInt(ziel, 10), t0 = null, dauer = 1100, pad = ziel.length;
    function schritt(t) { if (!t0) t0 = t; var f = Math.min(1, (t - t0) / dauer); f = 1 - Math.pow(1 - f, 3); var v = String(Math.round(z * f)); while (v.length < pad) v = '0' + v; el.textContent = v; if (f < 1) requestAnimationFrame(schritt); }
    requestAnimationFrame(schritt);
  }
  function zeige(el) { el.classList.add('sichtbar'); el.querySelectorAll('[data-zahl]').forEach(function (z) { if (ruhig) z.textContent = z.getAttribute('data-zahl'); else zaehle(z); }); }
  // Zahlen stehen im HTML richtig (auch ohne JavaScript); nur wenn hochgezählt wird, vorher auf 0 setzen
  if (!ruhig && 'IntersectionObserver' in window) { document.querySelectorAll('[data-zahl]').forEach(function (z) { z.textContent = z.getAttribute('data-zahl').replace(/\d/g, '0'); }); }
  if (ruhig || !('IntersectionObserver' in window)) { R.forEach(zeige); }
  else { var io = new IntersectionObserver(function (es) { es.forEach(function (x) { if (x.isIntersecting) { zeige(x.target); io.unobserve(x.target); } }); }, { rootMargin: '0px 0px -10% 0px', threshold: 0.12 }); R.forEach(function (e) { io.observe(e); }); }

  // Scroll-Takt: Fortschritt je Szene, Kopfzustand
  var S = document.querySelectorAll('.szene'), T = document.querySelectorAll('[data-tempo]');
  var tick = false;
  function lauf() {
    tick = false;
    var vh = window.innerHeight, y = window.scrollY;
    if (K) K.classList.toggle('kopf-fest', y > 40);
    if (ruhig) return;
    for (var i = 0; i < S.length; i++) {
      var r = S[i].getBoundingClientRect();
      if (r.bottom < -vh || r.top > vh * 2) continue;
      var p = (vh - r.top) / (vh + r.height);           // 0 unten einlaufend … 1 oben ausgelaufen
      S[i].style.setProperty('--p', Math.max(0, Math.min(1, p)).toFixed(4));
      if (S[i].classList.contains('held')) {           // festgeklemmter Aufmacher: wie weit ist die nächste Szene darüber geschoben
        var q = Math.max(0, Math.min(1, y / Math.max(1, r.height)));   // sticky: rect.top bleibt 0, also über scrollY
        S[i].style.setProperty('--q', q.toFixed(4));
      }
    }
    for (var j = 0; j < T.length; j++) {
      var el = T[j], s = el.closest('section') || el.parentElement, rr = s.getBoundingClientRect();
      if (rr.bottom < -vh || rr.top > 2 * vh) continue;
      var f = (rr.top + rr.height / 2 - vh / 2) / vh;
      el.style.setProperty('--ty', (f * parseFloat(el.dataset.tempo) * -70).toFixed(1) + 'px');
    }
  }
  window.addEventListener('scroll', function () { if (!tick) { tick = true; requestAnimationFrame(lauf); } }, { passive: true });
  window.addEventListener('resize', lauf);
  lauf();

  // Inspektionslicht: weiche Klarstelle folgt dem Zeiger über Fotoszenen
  if (fein && !ruhig) {
    document.querySelectorAll('.licht').forEach(function (sz) {
      var aktiv = false, mx = 50, my = 50, tx = 50, ty = 50, raf = 0;
      function glatt() { mx += (tx - mx) * .14; my += (ty - my) * .14; sz.style.setProperty('--mx', mx.toFixed(2) + '%'); sz.style.setProperty('--my', my.toFixed(2) + '%'); if (Math.abs(tx - mx) + Math.abs(ty - my) > .05) raf = requestAnimationFrame(glatt); else raf = 0; }
      sz.addEventListener('pointermove', function (e) { var r = sz.getBoundingClientRect(); tx = (e.clientX - r.left) / r.width * 100; ty = (e.clientY - r.top) / r.height * 100; if (!aktiv) { aktiv = true; sz.classList.add('licht-an'); } if (!raf) raf = requestAnimationFrame(glatt); }, { passive: true });
      sz.addEventListener('pointerleave', function () { aktiv = false; sz.classList.remove('licht-an'); });
    });
    // Collage: leichte Neigung zum Zeiger
    document.querySelectorAll('.collage-bild').forEach(function (b) {
      b.addEventListener('pointermove', function (e) { var r = b.getBoundingClientRect(); var x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5; b.style.setProperty('--rx', (-y * 6).toFixed(2) + 'deg'); b.style.setProperty('--ry', (x * 8).toFixed(2) + 'deg'); }, { passive: true });
      b.addEventListener('pointerleave', function () { b.style.setProperty('--rx', '0deg'); b.style.setProperty('--ry', '0deg'); });
    });
  }


  // Flug durch die A-Portale (Startseite): Scrollen fährt die Kamera in die Tiefe, sanft nachgeführt (Schweben).
  var F = document.querySelector('.flug');
  if (F && !ruhig && window.CSS && CSS.supports('transform-style', 'preserve-3d')) {
    F.classList.add('flug-3d');
    var welt = F.querySelector('.flug-welt'), kam = F.querySelector('.flug-kamera');
    var D = parseFloat(F.dataset.tiefe) || 1800;
    var szenen = F.querySelectorAll('.flug-szene'), N = szenen.length;
    var hudNr = F.querySelector('.flug-hud-nr'), hudName = F.querySelector('.flug-hud-name'), hud = F.querySelector('.flug-hud');
    var wei = F.querySelector('.flug-weiter');
    var schmal = window.matchMedia('(max-width: 899px)').matches;
    // Sichtfenster je Ebenenart: [einblenden ab, voll ab, voll bis, weg bei] als Abstand zur Kamera (px, positiv = vor uns)
    var FENSTER = { text: [1350, 700, -70, -330], foto: [2800, 1500, -160, -560], portal: [4800, 2900, -420, -830],
      deko: [4800, 2900, -420, -830], staub: [3600, 1800, -500, -900], licht: [5200, 1800, -99999, -99999] };
    var E = [];
    F.querySelectorAll('.flug-el').forEach(function (el) {
      var art = el.dataset.art; if (!FENSTER[art]) return;
      var sz = el.closest('.flug-szene');
      E.push({ el: el, z: parseFloat(el.style.getPropertyValue('--z')) || 0, f: FENSTER[art], art: art, o: -1, b: -1 });
    });
    var cam = 0, ziel = 0, rx = 0, ry = 0, zrx = 0, zry = 0, laeuft = false, szAkt = -1, fp = 0;
    function klemm(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
    function weich(t) { return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
    function zielAusScroll() {
      var r = F.getBoundingClientRect(), gesamt = F.offsetHeight - window.innerHeight;
      fp = klemm(-r.top / Math.max(1, gesamt));
      var seg = fp * (N - 1), i = Math.min(N - 2, Math.floor(seg)), t = seg - i;
      ziel = (i + .62 * weich(t) + .38 * t) * D;   // verweilt an jeder Szene, schwebt dazwischen zügiger
    }
    function zeichne() {
      laeuft = false;
      cam += (ziel - cam) * .12; if (Math.abs(ziel - cam) < .4) cam = ziel;
      rx += (zrx - rx) * .08; ry += (zry - ry) * .08;
      welt.style.transform = 'translate3d(0,0,' + cam.toFixed(1) + 'px)';
      kam.style.transform = 'rotateX(' + rx.toFixed(3) + 'deg) rotateY(' + ry.toFixed(3) + 'deg)';
      for (var k = 0; k < E.length; k++) {
        var e = E[k], rel = e.z - cam, w = e.f;
        var o = klemm((w[0] - rel) / (w[0] - w[1])) * klemm((rel - w[3]) / (w[2] - w[3]));
        if (Math.abs(o - e.o) > .004) { e.el.style.opacity = o.toFixed(3); e.o = o; e.el.classList.toggle('aktiv', o > .5); }
        if (e.art === 'foto' && !schmal) {           // Tiefenunschärfe für entfernte Foto-Tafeln
          var b = Math.round(Math.max(0, Math.min(6, (rel - 380) / 260)) * 2) / 2;
          if (b !== e.b) { e.el.style.filter = b ? 'blur(' + b + 'px)' : 'none'; e.b = b; }
        }
      }
      var s = Math.round(cam / D);
      if (s !== szAkt && szenen[s]) { szAkt = s; hudNr.textContent = ('0' + (s + 1)).slice(-2); hudName.textContent = szenen[s].dataset.label || ''; }
      hud.style.setProperty('--fp', fp.toFixed(4));
      if (wei) wei.style.opacity = klemm(1 - fp * 18).toFixed(3);
      if (Math.abs(ziel - cam) > .4 || Math.abs(zrx - rx) + Math.abs(zry - ry) > .002) los();
    }
    function los() { if (!laeuft) { laeuft = true; requestAnimationFrame(zeichne); } }
    window.addEventListener('scroll', function () { zielAusScroll(); los(); }, { passive: true });
    window.addEventListener('resize', function () { schmal = window.matchMedia('(max-width: 899px)').matches; zielAusScroll(); los(); });
    // Keine Neigung mit dem Zeiger (Wunsch 2026-10-26: das Logo bewegt sich ohne Einfluss des Zeigers)
    // Flug überspringen: direkt hinter den Flug, ohne durch alle Szenen zu fahren
    var skip = F.querySelector('.flug-skip');
    if (skip) skip.addEventListener('click', function (e) { e.preventDefault(); window.scrollTo({ top: F.getBoundingClientRect().top + window.scrollY + F.offsetHeight, behavior: 'instant' }); var n = F.nextElementSibling && F.nextElementSibling.nextElementSibling; var h = n && n.querySelector('h2'); if (h) { h.setAttribute('tabindex', '-1'); h.focus({ preventScroll: true }); } });
    // Tastatur: ein Fokus in einer Szene fährt die Kamera dorthin
    F.addEventListener('focusin', function (e) {
      var sz = e.target.closest('.flug-szene'); if (!sz) return;
      var i = parseInt(sz.dataset.szene, 10) || 0, gesamt = F.offsetHeight - window.innerHeight;
      window.scrollTo(0, F.getBoundingClientRect().top + window.scrollY + gesamt * i / (N - 1));
    });
    zielAusScroll(); cam = ziel; zeichne();
  }

  requestAnimationFrame(function () { html.classList.add('bereit'); });
})();
