/* NAHX Technologies – Bewegung (ohne Bibliothek).
   Ein Scroll-Takt setzt je Szene den Fortschritt --p (0 = Szene kommt von unten, 1 = Szene ist oben weg).
   Alles weitere ist CSS. Inspektionslicht folgt dem Zeiger über Fotos (nur Zeigergeräte, nie bei reduzierter Bewegung).
   Zahlen zählen beim Erscheinen einmal hoch. Keine Dauerbewegung. */
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

  requestAnimationFrame(function () { html.classList.add('bereit'); });
})();
