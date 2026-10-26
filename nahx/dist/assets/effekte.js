/* NAHX Technologies – Effekte nach Art der StringTune-Demo, in Mint und mit dem NAHX-A (ohne Bibliothek, 2026-10-26).
   1. Pixel-Schrift: Überschriften setzen sich beim Erscheinen aus Mint-Pixeln zusammen, ein paar Pixel stieben weg.
   2. Wort-Bühne: das A fährt beim Scrollen mit und dreht sich, die Leitwörter gehen weich ineinander über.
   3. Wellen-Schrift: große Zeilen verziehen sich je nach Scroll-Tempo und federn zurück.
   4. Pixel-Übergang: Fotoszenen werden beim Hereinscrollen kachelweise freigelegt.
   5. Fortschrittslinie oben, Kicker entschlüsseln sich einmal.
   Alles nur 2D (leicht genug für Handys). Bei prefers-reduced-motion bleibt alles ruhig und sofort lesbar. */
(function () {
  var html = document.documentElement;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var leicht = window.matchMedia('(max-width: 899px), (pointer: coarse)').matches;
  html.classList.add('fx');
  var zufall = (function () { var s = 20261026; return function () { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; }; })();

  // ---------- Zerlegen in Zeichen (Elemente wie <em>, <br> bleiben erhalten, Wörter brechen nicht) ----------
  function zerlege(el, klasse) {
    var n = 0, text = el.textContent.replace(/\s+/g, ' ').trim();
    if (!el.hasAttribute('aria-label')) el.setAttribute('aria-label', text);
    (function lauf(knoten) {
      Array.prototype.slice.call(knoten.childNodes).forEach(function (k) {
        if (k.nodeType === 3) {
          var frag = document.createDocumentFragment();
          k.textContent.split(/(\s+)/).forEach(function (teil) {
            if (!teil) return;
            if (/^\s+$/.test(teil)) { frag.appendChild(document.createTextNode(' ')); return; }
            var w = document.createElement('span'); w.className = 'fx-w'; w.setAttribute('aria-hidden', 'true');
            Array.from(teil).forEach(function (c) { var z = document.createElement('span'); z.className = klasse; z.style.setProperty('--i', n++); z.textContent = c; w.appendChild(z); });
            frag.appendChild(w);
          });
          k.replaceWith(frag);
        } else if (k.nodeType === 1 && k.tagName !== 'BR') lauf(k);
      });
    })(el);
    return n;
  }

  // ---------- 1. Pixel-Schrift ----------
  var pxZiele = document.querySelectorAll('main .abschnitt-kopf h2, main .assistent-text h2, main .marke-innen h2, main .ablauf-text h2, main .gl-kopf h2, main .st-kopf h2, main .ab-innen h2');
  var pxIO = 'IntersectionObserver' in window ? new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('px-an'); pxIO.unobserve(e.target); } });
  }, {rootMargin: '0px 0px -12% 0px', threshold: 0.2}) : null;
  var pxOffen = [];
  pxZiele.forEach(function (h) {
    if (h.closest('.flug') || !pxIO) return;
    pxOffen.push(h);
    var n = zerlege(h, 'px-z');
    h.classList.add('px-text');
    var staub = leicht ? 5 : 9;
    for (var i = 0; i < staub; i++) {
      var p = document.createElement('span'); p.className = 'px-staub'; p.setAttribute('aria-hidden', 'true');
      p.style.left = (zufall() * 100).toFixed(1) + '%'; p.style.top = (10 + zufall() * 80).toFixed(1) + '%';
      p.style.setProperty('--g', (4 + Math.round(zufall() * 8)) + 'px');
      p.style.setProperty('--dx', ((zufall() - .5) * 120).toFixed(0) + 'px'); p.style.setProperty('--dy', ((zufall() - .5) * 70).toFixed(0) + 'px');
      p.style.setProperty('--d', Math.round(zufall() * Math.min(600, n * 14)) + 'ms');
      h.appendChild(p);
    }
    pxIO.observe(h);
  });

  // ---------- 5b. Kicker entschlüsseln ----------
  var ZEICHEN = 'NAHX01<>/+=#*';
  var kIO = 'IntersectionObserver' in window ? new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (!e.isIntersecting) return; kIO.unobserve(e.target);
      var el = e.target, ziel = el.textContent, t0 = null, dauer = 650;
      el.setAttribute('aria-label', ziel);
      function schritt(t) {
        if (!t0) t0 = t; var f = Math.min(1, (t - t0) / dauer), fest = Math.floor(f * ziel.length), s = '';
        for (var i = 0; i < ziel.length; i++) s += i < fest || ziel[i] === ' ' ? ziel[i] : ZEICHEN[(Math.random() * ZEICHEN.length) | 0];
        el.textContent = s; if (f < 1) requestAnimationFrame(schritt); else el.textContent = ziel;
      }
      requestAnimationFrame(schritt);
    });
  }, {threshold: 0.6}) : null;
  if (kIO) document.querySelectorAll('main .kicker').forEach(function (k) { if (!k.closest('.flug') && !k.children.length && k.textContent.length < 48) kIO.observe(k); });

  // ---------- 2. Wort-Bühne ----------
  var buehnen = Array.prototype.map.call(document.querySelectorAll('[data-wortbuehne]'), function (b) {
    b.classList.add('wb-an');
    return {el: b, woerter: b.querySelectorAll('.wb-wort'), objekt: b.querySelector('.wb-objekt'), streif: b.querySelector('.wb-streif'), balken: b.querySelector('.wb-fortschritt i'), p: -1};
  });
  function klemm(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
  function wortbuehnen() {
    var vh = window.innerHeight;
    buehnen.forEach(function (b) {
      var r = b.el.getBoundingClientRect(); if (r.bottom < -vh || r.top > vh * 1.5) return;
      var p = klemm(-r.top / Math.max(1, r.height - vh)); if (Math.abs(p - b.p) < 0.0005) return; b.p = p;
      var n = b.woerter.length;
      for (var k = 0; k < n; k++) {
        var t = p * n - k, o = klemm((0.5 - Math.abs(t - 0.5)) * 4.2);
        if (k === 0 && t < 0.5) o = 1; if (k === n - 1 && t > 0.5) o = 1;   // erstes und letztes Wort bleiben stehen
        var w = b.woerter[k];
        w.style.setProperty('--o', o.toFixed(3)); w.style.setProperty('--t', (t - 0.5).toFixed(3));
        w.classList.toggle('aktiv', o > 0.5);
      }
      var rot = -26 + p * 52, x = Math.sin(p * Math.PI * 1.6) * (leicht ? 10 : 16), y = Math.cos(p * Math.PI * 1.2) * 5, s = 0.86 + Math.sin(p * Math.PI) * 0.2;
      b.objekt.style.transform = 'translate(-50%,-50%) translate(' + x.toFixed(2) + 'vw,' + y.toFixed(2) + 'vh) rotate(' + rot.toFixed(2) + 'deg) scale(' + s.toFixed(3) + ')';
      if (b.streif) b.streif.style.transform = 'translate(-50%,-50%) rotate(' + (-38 + p * 76).toFixed(2) + 'deg) scaleX(' + (0.4 + p * 0.6).toFixed(3) + ')';
      if (b.balken) b.balken.style.transform = 'scaleX(' + p.toFixed(4) + ')';
    });
  }

  // ---------- 3. Wellen-Schrift ----------
  var wellen = [];
  document.querySelectorAll('main .band-text h2, main [data-welle]').forEach(function (h) {
    zerlege(h, 'wl-z'); h.classList.add('wl-text');
    var w = {el: h, z: h.querySelectorAll('.wl-z'), sicht: false}; wellen.push(w);
    if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { w.sicht = es[0].isIntersecting; }).observe(h);
  });
  var tempo = 0, letzteY = window.scrollY, letzteZ = performance.now(), wellenLauf = false, phase = 0;
  function welle(t) {
    tempo *= 0.9; phase += 0.08;
    var amp = Math.max(-1, Math.min(1, tempo / 2.2)) * (leicht ? 9 : 16);
    var v = Math.max(-1, Math.min(1, tempo / 3)) * (leicht ? 5 : 10);
    for (var j = 0; j < schmier.length; j++) schmier[j].style.setProperty('--v', Math.abs(v) < 0.2 ? '0' : v.toFixed(2));
    wellen.forEach(function (w) {
      if (!w.sicht) return;
      for (var i = 0; i < w.z.length; i++) {
        var y = Math.sin(i * 0.42 + phase) * amp;
        w.z[i].style.transform = Math.abs(amp) < 0.15 ? '' : 'translateY(' + y.toFixed(2) + 'px) skewX(' + (-amp * 0.7).toFixed(2) + 'deg)';
      }
    });
    if (Math.abs(amp) >= 0.15) requestAnimationFrame(welle); else wellenLauf = false;
  }

  // ---------- 4. Pixel-Übergang für Fotoszenen ----------
  document.querySelectorAll('main .buehne, main .band-mit-foto, main .ablauf').forEach(function (sz) {
    var cols = leicht ? 7 : 14, rows = leicht ? 11 : 8, m = document.createElement('div');
    m.className = 'mosaik'; m.setAttribute('aria-hidden', 'true'); m.style.setProperty('--c', cols); m.style.setProperty('--r', rows);
    for (var i = 0; i < cols * rows; i++) {
      var c = document.createElement('i'), s = zufall();
      c.style.setProperty('--s', s.toFixed(3)); if (s < 0.07) c.className = 'm';
      m.appendChild(c);
    }
    var foto = sz.querySelector('.buehne-foto, .band-foto, .ablauf-foto');
    if (foto) foto.appendChild(m);
  });

  // ---------- 6. Szenen nach dem FORGE-Video: Bild wird Karte, Galerie seitlich, Tafeln, Abschluss ----------
  var karten = Array.prototype.map.call(document.querySelectorAll('[data-bildkarte]'), function (el) { el.classList.add('bk-an'); return {el: el, z: -1}; });
  var galerien = Array.prototype.map.call(document.querySelectorAll('[data-galerie]'), function (el) {
    el.classList.add('gl-an'); return {el: el, spur: el.querySelector('.gl-spur'), balken: el.querySelector('.gl-fortschritt i'), weg: 0, p: -1};
  });
  function galerieMass() {
    galerien.forEach(function (g) {
      g.spur.style.transform = '';
      g.weg = Math.max(0, g.spur.scrollWidth - g.spur.clientWidth);
      g.el.style.height = (window.innerHeight + g.weg) + 'px'; g.p = -1;
    });
  }
  galerieMass();
  var tafeln = Array.prototype.slice.call(document.querySelectorAll('.st-tafel'));
  var abschluesse = Array.prototype.slice.call(document.querySelectorAll('[data-abschluss]'));
  var schmier = Array.prototype.slice.call(document.querySelectorAll('main .fx-schmier'));
  function szenen() {
    var vh = window.innerHeight;
    karten.forEach(function (k) {
      var r = k.el.getBoundingClientRect(); if (r.bottom < 0 || r.top > vh) return;
      var z = klemm(-r.top / Math.max(1, (r.height - vh) * 0.8)); if (Math.abs(z - k.z) < 0.001) return; k.z = z;
      k.el.style.setProperty('--z', z.toFixed(4));
    });
    galerien.forEach(function (g) {
      var r = g.el.getBoundingClientRect(); if (r.bottom < 0 || r.top > vh) return;
      var p = klemm(-r.top / Math.max(1, g.weg)); if (Math.abs(p - g.p) < 0.0005) return; g.p = p;
      g.spur.style.transform = 'translateX(' + (-p * g.weg).toFixed(1) + 'px)';
      if (g.balken) g.balken.style.transform = 'scaleX(' + p.toFixed(4) + ')';
    });
    for (var i = 0; i < tafeln.length - 1; i++) {
      var t = tafeln[i], n = tafeln[i + 1], oben = parseFloat(getComputedStyle(n).top) || 0, nt = n.getBoundingClientRect().top;
      t.style.setProperty('--d', klemm(1 - (nt - oben) / Math.max(1, vh - oben)).toFixed(3));
    }
    abschluesse.forEach(function (a) {
      var r = a.getBoundingClientRect(); if (r.bottom < 0 || r.top > vh) return;
      a.style.setProperty('--a', klemm((vh - r.top) / vh).toFixed(3));
    });
  }

  // ---------- 5a. Fortschrittslinie ----------
  var linie = document.createElement('div'); linie.className = 'fx-linie'; linie.setAttribute('aria-hidden', 'true'); document.body.appendChild(linie);

  var tick = false;
  function lauf() {
    tick = false;
    var max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
    linie.style.transform = 'scaleX(' + klemm(window.scrollY / max).toFixed(4) + ')';
    wortbuehnen(); szenen();
    // Sicherheitsnetz für Sprünge (Anker, große Scrollwege): sichtbare Überschriften sofort einblenden
    if (pxOffen.length) {
      var vh = window.innerHeight;
      pxOffen = pxOffen.filter(function (h) {
        if (h.classList.contains('px-an')) return false;
        var r = h.getBoundingClientRect();
        if (r.top < vh * 0.92 && r.bottom > 0) { h.classList.add('px-an'); return false; }
        return true;
      });
    }
  }
  window.addEventListener('scroll', function () {
    var jetzt = performance.now(), dy = window.scrollY - letzteY, dt = Math.max(8, jetzt - letzteZ);
    letzteY = window.scrollY; letzteZ = jetzt;
    tempo = tempo * 0.6 + (dy / dt) * 0.4;
    if ((wellen.length || schmier.length) && !wellenLauf && Math.abs(tempo) > 0.05) { wellenLauf = true; requestAnimationFrame(welle); }
    if (!tick) { tick = true; requestAnimationFrame(lauf); }
  }, {passive: true});
  window.addEventListener('resize', function () { buehnen.forEach(function (b) { b.p = -1; }); karten.forEach(function (k) { k.z = -1; }); galerieMass(); lauf(); });
  window.addEventListener('load', function () { galerieMass(); lauf(); });
  lauf();
})();
