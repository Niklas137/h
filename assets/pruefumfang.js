/* Prüfumfang von 614 One: Auswahl Produktart und Dokumentart (2026-10-27).
   Daten aus inhalt/pruefumfang.json, eingebettet von build.py. Markup wie Bau.pu_panel in build.py –
   bei Änderungen beide anpassen. Ohne JavaScript zeigt die Seite die Startauswahl. */
(function () {
  'use strict';
  var esc = function (s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  };
  // Texte aus den Inhaltsdateien dürfen <mark>, <em>, <strong> und <br> enthalten (wie frag() in build.py)
  var frag = function (s) { return String(s == null ? '' : s).replace(/&(?!#?\w+;)/g, '&amp;'); };

  function liste(items, L, klasse) {
    if (!items.length) return '<p class="pu-leer">' + esc(L.keine) + '</p>';
    return '<ul class="' + (klasse || '') + '">' + items.map(function (x) { return '<li>' + x + '</li>'; }).join('') + '</ul>';
  }

  function panel(pu, L, produkt, dokument) {
    var d = pu.dokumentarten.filter(function (x) { return x.name === dokument; })[0];
    if (!d) return '';
    var basis = (pu.normbasis[produkt] || []).concat(d.normbasis_dok || []).filter(function (x, i, a) { return a.indexOf(x) === i; });
    var rbText = pu.rechtsbereiche.filter(function (r) { return r.auch_text && r.produkte.indexOf(produkt) < 0; }).map(function (r) { return r.name; });
    var rb = pu.rechtsbereiche.filter(function (r) { return r.produkte.indexOf(produkt) >= 0; }).map(function (r) { return esc(r.name); });
    var normen = d.normen.map(function (n) {
      return esc(n.quelle) + ' <span class="pu-ausgabe">' + esc(n.ausgabe ? n.ausgabe : L.ohne_ausgabe) + '</span>' + (n.relevanz ? '<small>' + esc(n.relevanz) + '</small>' : '');
    });
    var kap = d.kapitel;
    var kapHtml = liste(kap.slice(0, 8).map(esc), L, 'pu-kapitel');
    if (kap.length > 8) {
      kapHtml += '<details class="pu-mehr"><summary>' + esc(L.alle_kapitel.replace('{n}', kap.length)) + '</summary>' + liste(kap.slice(8).map(esc), L, 'pu-kapitel') + '</details>';
    }
    var beleg = '<span class="pu-beleg' + (d.belegt ? ' pu-beleg-ja' : '') + '">' + esc(d.belegt ? L.belegt : L.nicht_belegt) + '</span>';
    var grenzen = L.grenzen.slice();
    if (d.nur_vorpruefung) grenzen.push(L.nur_vorpruefung);
    return '<div class="pu-kopf"><h3>' + esc(dokument) + ' <span>· ' + esc(produkt) + '</span></h3>' + beleg + '</div>\n' +
      '<div class="pu-raster">\n' +
      '  <div class="pu-block"><h4>' + esc(L.kapitel) + ' <span class="pu-zahl">' + kap.length + '</span></h4>' + kapHtml + '</div>\n' +
      '  <div class="pu-block"><h4>' + esc(L.bereiche) + ' <span class="pu-zahl">' + d.bereiche.length + '</span></h4>' + liste(d.bereiche.map(esc), L) + '</div>\n' +
      '  <div class="pu-block"><h4>' + esc(L.normen) + '</h4>' + liste(normen, L, 'pu-normen') + '<h4 class="pu-unter">' + esc(L.normbasis) + '</h4>' + liste(basis.map(esc), L) + '</div>\n' +
      '  <div class="pu-block"><h4>' + esc(L.rechtsbereiche) + '</h4>' + liste(rb, L) + (rbText.length ? '<p class="pu-text">' + esc(L.text_hinweis) + ' ' + esc(rbText.join('; ')) + '</p>' : '') + '<h4 class="pu-unter">' + esc(L.ergebnis) + '</h4>' + liste(L.ergebnisse.map(frag), L) +
      '<h4 class="pu-unter">' + esc(L.grenzen_titel) + '</h4>' + liste(grenzen.map(frag), L, 'pu-grenzen') + '</div>\n' +
      '</div>';
  }

  function start(box) {
    var quelle = box.querySelector('[data-pu-daten]');
    if (!quelle) return;
    var daten;
    try { daten = JSON.parse(quelle.textContent); } catch (e) { return; }
    var p = box.querySelector('[data-pu-produkt]');
    var d = box.querySelector('[data-pu-dokument]');
    var ziel = box.querySelector('[data-pu-ergebnis]');
    var neu = function () {
      ziel.innerHTML = panel(daten.pu, daten.L, p.value, d.value);
      ziel.classList.remove('pu-neu'); void ziel.offsetWidth; ziel.classList.add('pu-neu');
    };
    p.addEventListener('change', neu);
    d.addEventListener('change', neu);
  }

  function los() { Array.prototype.forEach.call(document.querySelectorAll('[data-pu]'), start); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', los); else los();
})();
