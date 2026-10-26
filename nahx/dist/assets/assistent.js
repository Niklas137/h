/* NAHX-Assistent – Chat im Handy (ohne Bibliothek).
   Das Handy steht als HTML in der Seite (build.py, Abschnittstyp „assistent“ oder schwebend am Seitenende).
   Ohne Server-Adresse (site.json → assistent.api leer) läuft eine Demo mit vorbereiteten Antworten aus
   inhalt/<sprache>.json → assistent.demo; nichts verlässt den Browser. Mit Adresse spricht das Fenster dasselbe
   Protokoll wie der FSH-Assistent: GET api → {bereit}, POST api {sitzung, nachricht, sprache} → {antwort, kalender},
   GET api/termine?sprache= → {tage:[{datum, slots:[{zeit, text, frei}]}]}.
   Auf schmalen Bildschirmen öffnet sich das Handy bildschirmfüllend wie ein Messenger. */
(function () {
  var daten = document.getElementById('assistent-daten');
  var handy = document.querySelector('[data-assistent]');
  if (!daten || !handy) return;
  var D; try { D = JSON.parse(daten.textContent); } catch (e) { return; }
  var T = D.texte, SPEICHER = 'nahx-assistent-v1';
  var html = document.documentElement;
  var ruhig = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var schmal = window.matchMedia('(max-width: 699px)');
  var inline = !handy.classList.contains('schwebend');

  var verlaufEl = handy.querySelector('.chat-verlauf'), feld = handy.querySelector('.chat-feld'), form = handy.querySelector('.chat-eingabe');
  var sendenKnopf = handy.querySelector('.chat-senden'), vorschlaegeEl = handy.querySelector('.chat-vorschlaege');
  var unterEl = handy.querySelector('.chat-unter'), fussEl = handy.querySelector('.chat-fuss-text'), zurueck = handy.querySelector('.chat-zurueck');
  var neuKnopf = handy.querySelector('.chat-neu'), uhr = handy.querySelector('.handy-uhr');
  var starter = document.querySelector('.chat-knopf');
  var live = false, laeuft = false, offen = false;

  // ---------- Zustand (bleibt beim Seitenwechsel im selben Tab) ----------
  function neueSitzung() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    var a = new Uint8Array(16); (window.crypto || {getRandomValues: function (x) { for (var i = 0; i < x.length; i++) x[i] = Math.random() * 256; return x; }}).getRandomValues(a);
    return Array.prototype.map.call(a, function (b) { return ('0' + b.toString(16)).slice(-2); }).join('');
  }
  var zustand = {sitzung: neueSitzung(), verlauf: [], offen: false};
  try { var roh = sessionStorage.getItem(SPEICHER); if (roh) { var z = JSON.parse(roh); if (z && /^[A-Za-z0-9-]{16,64}$/.test(z.sitzung) && Array.isArray(z.verlauf)) zustand = z; } } catch (e) {}
  function merken() { try { sessionStorage.setItem(SPEICHER, JSON.stringify(zustand)); } catch (e) {} }

  // ---------- Text in Blasen: {{test:…}} wird als Testwert markiert, sonst reiner Text ----------
  function fuelle(ziel, text) {
    var teile = String(text).split(/(\{\{test:[^}]*\}\})/);
    teile.forEach(function (t) {
      var m = /^\{\{test:([^}]*)\}\}$/.exec(t);
      if (m) { var mk = document.createElement('mark'); mk.className = 'test'; mk.textContent = m[1]; ziel.appendChild(mk); }
      else if (t) ziel.appendChild(document.createTextNode(t));
    });
  }
  function nachUnten() { verlaufEl.scrollTop = verlaufEl.scrollHeight; }
  function blase(rolle, text, extra) {
    var b = document.createElement('div');
    b.className = 'blase ' + (rolle === 'user' ? 'ich' : 'bot') + (extra ? ' ' + extra : '');
    fuelle(b, text);
    verlaufEl.appendChild(b); nachUnten(); return b;
  }
  function zeichneVorschlaege(liste) {
    vorschlaegeEl.textContent = '';
    (liste || []).forEach(function (v) {
      var k = document.createElement('button'); k.type = 'button'; k.className = 'chip'; k.textContent = v;
      k.addEventListener('click', function () { oeffnen(); if (v === T.neu) neuStarten(); else schicke(v); });
      vorschlaegeEl.appendChild(k);
    });
    vorschlaegeEl.hidden = !(liste && liste.length);
  }
  function zeichneAlles() {
    verlaufEl.textContent = '';
    blase('bot', live ? T.gruss_live : T.gruss_demo);
    var n = zustand.verlauf.length;
    zustand.verlauf.forEach(function (m, i) {
      if (m.rolle === 'kalender') { if (i === n - 1) kalenderKarte(); return; }
      blase(m.rolle, m.text, m.fehler ? 'fehler' : '');
    });
    var letzte = zustand.verlauf[n - 1];
    zeichneVorschlaege(n === 0 ? T.vorschlaege : (letzte && letzte.chips) || []);
  }

  // ---------- Öffnen: Vollbild auf dem Handy, schwebend auf dem Desktop ----------
  function passeHoehe() {
    if (!handy.classList.contains('vollbild')) { handy.style.removeProperty('height'); handy.style.removeProperty('top'); return; }
    var vv = window.visualViewport;
    if (vv) { handy.style.height = vv.height + 'px'; handy.style.top = vv.offsetTop + 'px'; }
  }
  function oeffnen(fokus) {
    var voll = schmal.matches;
    if (inline && !voll) { if (fokus) feld.focus({preventScroll: true}); return; }
    if (offen) { if (fokus) feld.focus(); return; }
    offen = true; zustand.offen = true; merken();
    handy.hidden = false;
    handy.classList.toggle('vollbild', voll);
    handy.classList.toggle('offen', true);
    html.classList.toggle('chat-vollbild', voll);
    if (zurueck) zurueck.hidden = false;
    if (starter) starter.hidden = true;
    passeHoehe(); nachUnten();
    if (fokus !== false) setTimeout(function () { feld.focus(); }, 60);
  }
  function schliessen() {
    if (!offen) return;
    offen = false; zustand.offen = false; merken();
    handy.classList.remove('vollbild', 'offen'); html.classList.remove('chat-vollbild'); passeHoehe();
    if (!inline) handy.hidden = true;
    if (zurueck) zurueck.hidden = true;
    if (starter) { starter.hidden = false; starter.focus(); }
  }

  // ---------- Demo: vorbereitete Antworten nach Stichworten ----------
  function normal(s) { return ' ' + String(s).toLowerCase().replace(/[^a-z0-9äöüß€.\-]+/g, ' ') + ' '; }
  function treffer(text, wort) {
    if (wort.charAt(0) === '=') return text.indexOf(' ' + wort.slice(1) + ' ') >= 0;
    return text.indexOf(' ' + wort) >= 0;
  }
  function demoAntwort(text) {
    var n = normal(text), beste = null, punkte = 0;
    (D.demo.wissen || []).forEach(function (w) {
      var p = 0; w.stichworte.forEach(function (s) { if (treffer(n, s)) p += s.replace('=', '').length; });
      if (p > punkte) { punkte = p; beste = w; }
    });
    return beste || {antwort: D.demo.sonst, chips: T.vorschlaege};
  }
  function demoTage() {
    var tage = [], d = new Date(); d.setHours(12, 0, 0, 0);
    while (tage.length < 5) {
      d.setDate(d.getDate() + 1);
      var wt = d.getDay(); if (wt === 0 || wt === 6) continue;
      var i = tage.length, iso = d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2);
      var slots = D.demo.zeiten.map(function (zeit, j) {
        var tx = T.wt[wt] + ', ' + ('0' + d.getDate()).slice(-2) + '.' + ('0' + (d.getMonth() + 1)).slice(-2) + '., ' + zeit;
        return {zeit: zeit, text: tx, frei: (i + j) % 3 !== 0};
      });
      tage.push({datum: iso, slots: slots});
    }
    return tage;
  }

  // ---------- Klick-Kalender ----------
  function kalenderKarte() {
    var karte = document.createElement('div'); karte.className = 'kal'; karte.setAttribute('role', 'group'); karte.setAttribute('aria-label', T.kal_titel);
    var kopf = document.createElement('div'); kopf.className = 'kal-kopf';
    var st = document.createElement('strong'); st.textContent = T.kal_titel;
    var un = document.createElement('span'); un.textContent = live ? T.kal_unter_live : T.kal_unter_demo;
    kopf.append(st, un);
    var hinweis = document.createElement('div'); hinweis.className = 'kal-hinweis'; hinweis.textContent = T.kal_laden;
    karte.append(kopf, hinweis); verlaufEl.appendChild(karte); nachUnten();
    if (!live) { zeichneKalender(karte, hinweis, demoTage()); return; }
    fetch(D.api.replace(/\/$/, '') + '/termine?sprache=' + D.sprache, {headers: {Accept: 'application/json'}})
      .then(function (r) { return r.ok ? r.json() : Promise.reject(); })
      .then(function (d) { if (!d || !Array.isArray(d.tage) || !d.tage.length) throw 0; zeichneKalender(karte, hinweis, d.tage); })
      .catch(function () { hinweis.textContent = T.kal_fehler; });
  }
  function zeichneKalender(karte, hinweis, tage) {
    var tageEl = document.createElement('div'); tageEl.className = 'kal-tage';
    var zeitenEl = document.createElement('div'); zeitenEl.className = 'kal-zeiten';
    var gewaehlt = 0; tage.some(function (t, i) { if (t.slots.some(function (s) { return s.frei; })) { gewaehlt = i; return true; } return false; });
    var knoepfe = tage.map(function (t, i) {
      var p = t.datum.split('-').map(Number), wt = T.wt[new Date(Date.UTC(p[0], p[1] - 1, p[2])).getUTCDay()];
      var frei = t.slots.filter(function (s) { return s.frei; }).length;
      var k = document.createElement('button'); k.type = 'button'; k.className = 'kal-tag' + (frei ? '' : ' voll');
      k.setAttribute('aria-pressed', 'false'); k.setAttribute('aria-label', wt + ' ' + p[2] + '.' + p[1] + '.: ' + frei + ' ' + T.kal_frei);
      var a = document.createElement('span'); a.className = 'wt'; a.textContent = wt;
      var b = document.createElement('span'); b.className = 'dt'; b.textContent = ('0' + p[2]).slice(-2) + '.' + ('0' + p[1]).slice(-2) + '.';
      k.append(a, b); k.addEventListener('click', function () { waehle(i); });
      tageEl.appendChild(k); return k;
    });
    function waehle(i) {
      gewaehlt = i; knoepfe.forEach(function (k, j) { k.setAttribute('aria-pressed', String(j === i)); });
      zeitenEl.textContent = '';
      tage[i].slots.forEach(function (s) {
        var k = document.createElement('button'); k.type = 'button'; k.className = 'kal-zeit ' + (s.frei ? 'frei' : 'belegt'); k.textContent = s.zeit;
        k.setAttribute('aria-label', s.text + ': ' + (s.frei ? T.kal_frei : T.kal_belegt));
        if (!s.frei) k.disabled = true;
        else k.addEventListener('click', function () {
          if (laeuft) return;
          karte.classList.add('fertig'); karte.querySelectorAll('button').forEach(function (x) { x.disabled = true; }); k.classList.add('gewaehlt');
          zustand.verlauf = zustand.verlauf.filter(function (m) { return m.rolle !== 'kalender'; }); merken();
          schicke(T.waehle.replace('{t}', s.text), s.text);
        });
        zeitenEl.appendChild(k);
      });
      if (!tage[i].slots.some(function (s) { return s.frei; })) { var h = document.createElement('div'); h.className = 'kal-hinweis'; h.textContent = T.kal_keine; zeitenEl.appendChild(h); }
    }
    var legende = document.createElement('div'); legende.className = 'kal-legende';
    var l1 = document.createElement('span'); l1.className = 'l frei'; l1.textContent = T.kal_frei;
    var l2 = document.createElement('span'); l2.className = 'l belegt'; l2.textContent = T.kal_belegt;
    legende.append(l1, l2);
    hinweis.replaceWith(tageEl, zeitenEl, legende);
    waehle(gewaehlt); nachUnten();
  }

  // ---------- Senden ----------
  function tippt() {
    var t = document.createElement('div'); t.className = 'blase bot tippt'; t.setAttribute('aria-label', T.tippt);
    for (var i = 0; i < 3; i++) t.appendChild(document.createElement('i'));
    verlaufEl.appendChild(t); nachUnten(); return t;
  }
  function warte(ms) { return new Promise(function (r) { setTimeout(r, ruhig ? 250 : ms); }); }
  function schicke(text, terminText) {
    text = String(text || '').trim();
    if (!text || laeuft) return;
    laeuft = true; sendenKnopf.disabled = true; zeichneVorschlaege([]);
    zustand.verlauf.push({rolle: 'user', text: text}); merken(); blase('user', text);
    var t = tippt();
    var ergebnis = live ? liveAntwort(text) : warte(650 + Math.min(900, text.length * 12)).then(function () {
      if (terminText) return {antwort: T.bestaetigt_demo.replace('{t}', terminText), chips: [T.neu]};
      var w = demoAntwort(text);
      return {antwort: w.antwort, chips: w.chips || [], kalender: Boolean(w.kalender)};
    });
    ergebnis.then(function (r) {
      t.remove();
      zustand.verlauf.push({rolle: 'assistant', text: r.antwort, fehler: Boolean(r.fehler), chips: r.kalender ? [] : r.chips}); merken();
      blase('assistant', r.antwort, r.fehler ? 'fehler' : '');
      if (r.kalender) { zustand.verlauf.push({rolle: 'kalender'}); merken(); kalenderKarte(); }
      else zeichneVorschlaege(r.chips);
      laeuft = false; sendenKnopf.disabled = false;
      if (offen || !schmal.matches) feld.focus({preventScroll: true});
    });
  }
  function liveAntwort(text) {
    return fetch(D.api, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({sitzung: zustand.sitzung, nachricht: text, sprache: D.sprache})})
      .then(function (res) {
        return res.json().catch(function () { return {}; }).then(function (d) {
          if (res.status === 429) return {antwort: T.zu_viele, fehler: true};
          if (!res.ok || !d.antwort) return {antwort: T.netz, fehler: true};
          return {antwort: d.antwort, kalender: Boolean(d.kalender), fehler: Boolean(d.stoerung)};
        });
      })
      .catch(function () { return {antwort: T.netz, fehler: true}; });
  }
  function neuStarten() { zustand = {sitzung: neueSitzung(), verlauf: [], offen: offen}; merken(); zeichneAlles(); }

  // ---------- Ereignisse ----------
  form.addEventListener('submit', function (e) { e.preventDefault(); var v = feld.value; feld.value = ''; feld.style.height = ''; schicke(v); });
  feld.addEventListener('keydown', function (e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); if (form.requestSubmit) form.requestSubmit(); else form.dispatchEvent(new Event('submit', {cancelable: true})); } });
  feld.addEventListener('input', function () { feld.style.height = 'auto'; feld.style.height = Math.min(feld.scrollHeight, 110) + 'px'; });
  feld.addEventListener('focus', function () { if (inline && schmal.matches && !offen) oeffnen(true); });
  if (zurueck) zurueck.addEventListener('click', schliessen);
  if (neuKnopf) neuKnopf.addEventListener('click', function (e) { e.preventDefault(); neuStarten(); });
  handy.addEventListener('keydown', function (e) { if (e.key === 'Escape' && offen) schliessen(); });
  if (starter) starter.addEventListener('click', function () {
    if (inline && !schmal.matches) { handy.scrollIntoView({behavior: ruhig ? 'auto' : 'smooth', block: 'center'}); feld.focus({preventScroll: true}); return; }
    oeffnen(true);
  });
  if (window.visualViewport) { window.visualViewport.addEventListener('resize', passeHoehe); window.visualViewport.addEventListener('scroll', passeHoehe); }
  var wechsel = function () { if (offen) { var voll = schmal.matches; if (inline && !voll) schliessen(); else { handy.classList.toggle('vollbild', voll); html.classList.toggle('chat-vollbild', voll); passeHoehe(); } } };
  if (schmal.addEventListener) schmal.addEventListener('change', wechsel);

  function stelleUhr() { if (!uhr) return; var d = new Date(); uhr.textContent = d.getHours() + ':' + ('0' + d.getMinutes()).slice(-2); }
  stelleUhr(); setInterval(stelleUhr, 30000);

  function bereit(istLive) {
    live = istLive;
    handy.classList.toggle('ist-demo', !live);
    unterEl.textContent = live ? T.unter_live : T.unter_demo;
    if (fussEl) { fussEl.textContent = ''; fuelle(fussEl, live ? T.fuss_live : T.fuss_demo); }
    feld.disabled = false; sendenKnopf.disabled = false; feld.placeholder = T.platz;
    handy.classList.add('bereit');
    zeichneAlles();
    if (starter) starter.hidden = false;
    if (zustand.offen && (!inline || schmal.matches)) oeffnen(false);
  }
  if (D.api) {
    fetch(D.api, {headers: {Accept: 'application/json'}}).then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) { bereit(Boolean(d && d.bereit)); }).catch(function () { bereit(false); });
  } else bereit(false);
})();
