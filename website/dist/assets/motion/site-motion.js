/* FSH-Documentation – seitenweite Bewegungsschicht. Keine Abhängigkeiten.
   1 Vorbereitung, 2 Held-Wörter, 3 Scroll-Reveal, 4 Zahlen hochzählen, 5 Kopf/Fortschritt, 6 Seitenwechsel. */
(function () {
  'use strict';
  var reduziert = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s, k) { return Array.prototype.slice.call((k || document).querySelectorAll(s)); };

  /* ---------- 1 Vorbereitung: Reveal-Marker setzen ---------- */
  function markiere(selektor, art, gestaffelt) {
    $(selektor).forEach(function (el) {
      if (el.hasAttribute('data-mo')) { return; }
      el.setAttribute('data-mo', art || 'hoch');
      if (gestaffelt) {
        var i = 0, g = el;
        while ((g = g.previousElementSibling)) { i++; }
        el.style.setProperty('--i', Math.min(i, 8));
      }
    });
  }
  markiere('.abschnitt-kopf', 'hoch');
  markiere('.raster > .karte', 'hoch', true);
  markiere('.raster > .schritt', 'hoch', true);
  markiere('.schritte-huelle', 'rahmen');            /* nur Beobachter für die Verbindungskurve, kein Ausblenden */
  $('.nav a').forEach(function (a, i) { a.style.setProperty('--i', i); });
  markiere('.zahl-block', 'hoch', true);
  markiere('.band-raster > *', 'hoch', true);
  markiere('.punkte > *', 'links', true);
  markiere('.fliess > *', 'hoch', true);
  markiere('.ueber-text', 'rechts');
  markiere('.portraet', 'bild');
  markiere('.bild-breit', 'bild');
  markiere('.kontakt-karte', 'zoom');
  markiere('.referenz-hinweis', 'hoch');
  markiere('.links-liste', 'hoch');
  markiere('.fuss-spalten > *', 'hoch', true);
  markiere('.fuss-klein', 'hoch');
  $('.held .chip').forEach(function (c, i) { c.style.setProperty('--i', i); });

  /* ---------- 2 Held: Überschrift wortweise ---------- */
  var h1 = document.querySelector('.held h1');
  if (h1 && !reduziert && h1.children.length === 0) {
    var woerter = h1.textContent.split(/(\s+)/);
    h1.textContent = '';
    var n = 0;
    woerter.forEach(function (w) {
      if (!w) { return; }
      if (/^\s+$/.test(w)) { h1.appendChild(document.createTextNode(' ')); return; }
      var a = document.createElement('span'); a.className = 'mo-wort';
      var b = document.createElement('span'); b.textContent = w; b.style.setProperty('--i', n++);
      a.appendChild(b); h1.appendChild(a);
    });
  }

  /* ---------- 3 Scroll-Reveal ---------- */
  var ziele = $('[data-mo]');
  if (reduziert || !('IntersectionObserver' in window)) {
    ziele.forEach(function (el) { el.classList.add('mo-sichtbar'); });
  } else {
    var io = new IntersectionObserver(function (eintraege) {
      eintraege.forEach(function (e) {
        if (!e.isIntersecting) { return; }
        e.target.classList.add('mo-sichtbar');
        io.unobserve(e.target);
        if (e.target.classList.contains('zahl-block')) { zaehle(e.target.querySelector('.zahl')); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });
    ziele.forEach(function (el) { io.observe(el); });
  }

  /* ---------- 4 Zahlen hochzählen ("15+", "10.000+", "24 h") ---------- */
  function zaehle(el) {
    if (!el || reduziert) { return; }
    var text = el.textContent, m = text.match(/^([^\d]*)([\d.]+)(.*)$/);
    if (!m) { return; }
    var vor = m[1], nach = m[3], roh = m[2], ziel = parseInt(roh.replace(/\./g, ''), 10);
    if (isNaN(ziel)) { return; }
    var punkt = roh.indexOf('.') >= 0, start = null, dauer = 1400;
    function fmt(v) { v = Math.round(v); return punkt ? v.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.') : String(v); }
    function schritt(t) {
      if (start === null) { start = t; }
      var p = Math.min((t - start) / dauer, 1), e = 1 - Math.pow(1 - p, 3);
      el.textContent = vor + fmt(ziel * e) + nach;
      if (p < 1) { requestAnimationFrame(schritt); } else { el.textContent = text; }
    }
    el.textContent = vor + fmt(0) + nach;
    requestAnimationFrame(schritt);
  }

  /* ---------- 5 Kopf (Schatten nach Scroll), Fortschrittsbalken ---------- */
  var kopf = document.querySelector('.kopf'), balken = document.createElement('div');
  balken.className = 'mo-fortschritt'; balken.setAttribute('aria-hidden', 'true'); document.body.appendChild(balken);
  var tick = false;
  function beiScroll() {
    if (tick) { return; } tick = true;
    requestAnimationFrame(function () {
      var y = window.scrollY || document.documentElement.scrollTop;
      if (kopf) { kopf.classList.toggle('mo-gescrollt', y > 8); }
      var max = document.documentElement.scrollHeight - window.innerHeight;
      balken.style.transform = 'scaleX(' + (max > 0 ? Math.min(y / max, 1) : 0) + ')';
      tick = false;
    });
  }
  window.addEventListener('scroll', beiScroll, { passive: true });
  beiScroll();

  /* ---------- 5c Parallax (ab 900 px): Held-Karte und Breitbild driften minimal gegen den Scroll ---------- */
  var parallaxZiele = $('.held-karte, .bild-breit img');
  var breit = window.matchMedia('(min-width: 900px)');
  function parallax() {
    if (!breit.matches || reduziert) { parallaxZiele.forEach(function (el) { el.style.removeProperty('--py'); }); return; }
    var mitte = window.innerHeight / 2;
    parallaxZiele.forEach(function (el) {
      var r = el.getBoundingClientRect();
      if (r.bottom < 0 || r.top > window.innerHeight) { return; }
      var abstand = (r.top + r.height / 2 - mitte) / window.innerHeight;   /* -0.5 … 0.5 */
      el.style.setProperty('--py', (abstand * -22).toFixed(1));
    });
  }
  if (parallaxZiele.length && !reduziert) {
    var pTick = false;
    window.addEventListener('scroll', function () { if (pTick) { return; } pTick = true; requestAnimationFrame(function () { parallax(); pTick = false; }); }, { passive: true });
    window.addEventListener('resize', parallax, { passive: true });
    parallax();
  }

  /* ---------- 5d Weicher Farbübergang beim Thema-Wechsel ---------- */
  if (!reduziert && 'MutationObserver' in window) {
    var themaTimer;
    new MutationObserver(function () {
      document.documentElement.classList.add('mo-thema-wechsel');
      clearTimeout(themaTimer);
      themaTimer = setTimeout(function () { document.documentElement.classList.remove('mo-thema-wechsel'); }, 500);
    }).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  }

  /* ---------- 6 Seitenwechsel: kurzes Ausblenden bei internen Links ---------- */
  if (!reduziert) {
    document.addEventListener('click', function (ev) {
      var a = ev.target.closest && ev.target.closest('a[href]');
      if (!a || ev.defaultPrevented || ev.button !== 0 || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) { return; }
      if (a.target && a.target !== '_self') { return; }
      if (a.hasAttribute('download') || /^(mailto|tel):/i.test(a.getAttribute('href'))) { return; }
      var url;
      try { url = new URL(a.href, location.href); } catch (e) { return; }
      if (url.origin !== location.origin) { return; }
      if (url.pathname === location.pathname && url.hash) { return; }
      ev.preventDefault();
      document.body.classList.add('mo-verlassen');
      setTimeout(function () { location.href = url.href; }, 260);
    });
    window.addEventListener('pageshow', function (e) { if (e.persisted) { document.body.classList.remove('mo-verlassen'); } });
  }
})();
