/* Dokumentenprüfer: Oberfläche. Kein Framework, spricht mit /api/… */
(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };
  var LANGS = { de: 'Deutsch', en: 'English', uk: 'Українська', ru: 'Русский' };
  // Deutsche Namen für Sätze; LANGS bleibt für Knöpfe und Menü.
  var LANGS_DE = { de: 'Deutsch', en: 'Englisch', uk: 'Ukrainisch', ru: 'Russisch' };
  var LABEL = { name: 'Name', dark: 'Helligkeit', textSize: 'Textgröße', density: 'Dichte', language: 'Sprache', notifyPopup: 'Pop-up bei fertigem Bericht', notifyApp: 'Hinweise im Tool', notifyWeekly: 'Wöchentliche Zusammenfassung' };
  var KLASSE = { Kritisch: 'r', Schwer: 'y', Mittel: '', Gering: '' };
  var AMPEL = { gruen: ['g', 'Grün · verwendbar'], gelb: ['y', 'Gelb · überarbeiten'], rot: ['r', 'Rot · nicht abgabereif'] };

  var S = {
    status: null, user: null, saved: null, draft: null,
    screen: 'start', step: 1, erst: { email: '', einmal: '', verifizierung: true },
    section: 'profil', help: false, langMenu: false, sheet: false, remember: false, showPwd: false,
    run: { basis: true, din: true, ce: true }, lang2: 'none', files: [], result: null, laufErg: null, busy: false,
    toastTimer: null, popTimer: null,
    lauf: null, laufSichtbar: false, laufTimer: null
  };

  // ------------------------------------------------------------ API
  function api(method, url, body, isForm) {
    var opt = { method: method, credentials: 'same-origin', headers: {} };
    if (body !== undefined) {
      if (isForm) { opt.body = body; } else { opt.headers['Content-Type'] = 'application/json'; opt.body = JSON.stringify(body); }
    }
    return fetch(url, opt).then(function (r) {
      return r.text().then(function (t) {
        var d = {};
        try { d = t ? JSON.parse(t) : {}; } catch (e) { d = { fehler: 'Unerwartete Antwort vom Server.' }; }
        if (r.status === 401 && S.screen !== 'start' && S.screen !== 'erst' && !/anmelden|erstanmeldung|passwort/.test(url)) { abmelden(false); }
        if (!r.ok) { var err = new Error(d.fehler || ('Fehler ' + r.status + '. Bitte noch einmal versuchen.')); err.daten = d; err.status = r.status; throw err; }
        return d;
      });
    });
  }
  function zeigeFehler(id, text) { var el = $(id); el.textContent = text || ''; el.hidden = !text; }

  // ------------------------------------------------------------ Hilfen
  function initials(n) { var p = (n || '').trim().split(/\s+/); return ((p[0] ? p[0].charAt(0) : '') + (p[1] ? p[1].charAt(0) : '')).toUpperCase() || '–'; }
  function esc(s) { return String(s === null || s === undefined ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function fmtGroesse(b) { return b < 1024 * 1024 ? Math.max(1, Math.round(b / 1024)) + ' KB' : (b / 1024 / 1024).toFixed(1).replace('.', ',') + ' MB'; }
  function fmtDatum(iso) { if (!iso) return ''; var d = new Date(iso); if (isNaN(d)) return iso; return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' }); }
  function fmt(key, v) {
    if (typeof v === 'boolean') { if (key === 'dark') return v ? 'Dunkel' : 'Hell'; return v ? 'An' : 'Aus'; }
    if (key === 'textSize') return { klein: 'Klein', normal: 'Normal', gross: 'Groß' }[v] || v;
    if (key === 'density') return v === 'kompakt' ? 'Kompakt' : 'Normal';
    if (key === 'language') return LANGS_DE[v] || 'Deutsch';
    return String(v);
  }
  function changes() {
    if (!S.saved || !S.draft) return [];
    return Object.keys(LABEL).filter(function (k) { return S.draft[k] !== S.saved[k]; }).map(function (k) { return { key: k, label: LABEL[k], from: fmt(k, S.saved[k]), to: fmt(k, S.draft[k]) }; });
  }
  function setVal(id, v) { var el = $(id); if (document.activeElement !== el && el.value !== v) el.value = v; }
  function showToast(msg) { $('toast-txt').textContent = msg; $('toast').hidden = false; clearTimeout(S.toastTimer); S.toastTimer = setTimeout(function () { $('toast').hidden = true; }, 2200); }
  function showPop(msg, force) {
    if (!force && S.draft && !S.draft.notifyPopup) return;
    var p = $('pop'); $('pop-msg').textContent = msg; p.hidden = false; p.classList.remove('in');
    requestAnimationFrame(function () { p.classList.add('in'); });
    clearTimeout(S.popTimer); S.popTimer = setTimeout(hidePop, 9000);
  }
  function hidePop() { $('pop').hidden = true; $('pop').classList.remove('in'); }
  function pwdRegeln(pwd, pwd2) { return { len: pwd.length >= 14, upper: /[A-ZÄÖÜ]/.test(pwd), special: /[^A-Za-z0-9ÄÖÜäöüß]/.test(pwd), match: pwd.length > 0 && pwd === pwd2 }; }

  // ------------------------------------------------------------ Darstellung
  function applyTheme() {
    var d = S.draft || { dark: true, textSize: 'normal', density: 'normal' };
    var root = document.documentElement;
    root.dataset.theme = d.dark ? 'dark' : 'light';
    root.style.setProperty('--k', { klein: 0.9, normal: 1, gross: 1.12 }[d.textSize] || 1);
    root.style.setProperty('--pad', d.density === 'kompakt' ? '12px' : '16px');
    root.style.setProperty('--gap', d.density === 'kompakt' ? '16px' : '24px');
  }

  function render() {
    var inGate = S.screen === 'start' || S.screen === 'erst';
    applyTheme();
    $('gate').hidden = !inGate; $('app').hidden = inGate;
    $('pitch-start').hidden = S.screen !== 'start'; $('pitch-erst').hidden = S.screen !== 'erst';
    $('f-login').hidden = S.screen !== 'start';
    $('f-step1').hidden = !(S.screen === 'erst' && S.step === 1);
    $('f-step2').hidden = !(S.screen === 'erst' && S.step === 2);
    $('f-step3').hidden = !(S.screen === 'erst' && S.step === 3);
    $$('.step').forEach(function (el) { var n = +el.dataset.step; el.classList.toggle('active', n === S.step); el.classList.toggle('done', n < S.step); });
    $('email-shown').textContent = S.erst.email || 'deine E-Mail-Adresse'; $('erst-email2').value = S.erst.email;
    ['login-pwd', 'erst-pwd', 'erst-pwd2'].forEach(function (id) { $(id).type = S.showPwd ? 'text' : 'password'; });
    $('login-show').textContent = S.showPwd ? 'Verbergen' : 'Anzeigen'; $('erst-show').textContent = S.showPwd ? 'Verbergen' : 'Anzeigen';
    $('remember-cb').classList.toggle('on', S.remember);
    var ok = pwdRegeln($('erst-pwd').value, $('erst-pwd2').value);
    $$('#rules [data-rule]').forEach(function (el) { el.classList.toggle('ok', !!ok[el.dataset.rule]); });
    $('finish').disabled = !(ok.len && ok.upper && ok.special && ok.match && $('erst-name').value.trim().length > 1) || S.busy;
    var okp = pwdRegeln($('pwd-neu').value, $('pwd-neu2').value);
    $$('#rules-pwd [data-rule]').forEach(function (el) { el.classList.toggle('ok', !!okp[el.dataset.rule]); });
    $('pwd-save').disabled = !(okp.len && okp.upper && okp.special && okp.match && $('pwd-alt').value.length > 0) || S.busy;
    if (inGate || !S.user) return;

    var d = S.draft, u = S.user;
    $('main').hidden = S.screen !== 'main'; $('settings').hidden = S.screen !== 'settings';
    $('b-settings').classList.toggle('on', S.screen === 'settings');
    $('lang-code').textContent = (LANGS[d.language] ? d.language : 'de').toUpperCase();
    $('lang-menu').hidden = !S.langMenu;
    $$('#lang-menu [data-lang]').forEach(function (el) { el.classList.toggle('on', el.dataset.lang === d.language); });
    $('ic-sun').hidden = !d.dark; $('ic-moon').hidden = d.dark;
    var nm = d.name || u.name || '–', ini = initials(nm);
    $('user-name').textContent = nm; $('user-name2').textContent = nm; $('user-name3').textContent = nm;
    var rolleTxt = u.inhaber ? 'Admin · Inhaber' : (u.rolle === 'admin' ? 'Admin' : 'Mitglied');
    $('user-rolle').textContent = rolleTxt; $('rolle-badge').textContent = rolleTxt;
    $('avatar').textContent = ini; $('avatar2').textContent = ini;
    $('hello').textContent = 'Hallo ' + nm.trim().split(/\s+/)[0];
    $('s-email').value = u.email;
    $('grp-team').hidden = u.rolle !== 'admin'; $('nav-verwaltung').hidden = u.rolle !== 'admin';

    var nf = S.files.length;
    var baseLang = LANGS[d.language] ? d.language : 'de';
    $('rl-main').textContent = LANGS_DE[baseLang]; $('ui-side').textContent = LANGS_DE[baseLang];
    var extra = (S.lang2 !== 'none' && S.lang2 !== baseLang && LANGS[S.lang2]) ? S.lang2 : null;
    $('rl-side').textContent = extra ? LANGS_DE[extra] : 'Keine';
    var langs = extra ? [baseLang, extra] : [baseLang];
    $('report-plan').textContent = 'Erzeugt: Prüfbericht und Fachbericht in ' + langs.map(function (l) { return LANGS_DE[l]; }).join(' und ') + ' (' + (langs.length * 2) + ' PDFs' + (nf > 1 ? ' je Dokument, ' + (langs.length * 2 * nf) + ' insgesamt' : '') + ')';
    $$('#seg-run-lang2 button').forEach(function (b) { b.classList.toggle('on', b.dataset.v === S.lang2); });
    $$('[data-run]').forEach(function (el) { el.querySelector('.cb').classList.toggle('on', !!S.run[el.dataset.run]); });
    $('drop-text').textContent = nf === 0 ? 'Word (.docx) oder PDF hierher ziehen' : nf === 1 ? S.files[0].name : nf + ' Dateien ausgewählt';
    $('file-list').hidden = nf < 1;
    $('file-list').innerHTML = S.files.map(function (f, i) { return '<li><span class="t">' + esc(f.name) + '</span><span class="cap">' + fmtGroesse(f.size) + '</span>' + (S.busy ? '' : '<button type="button" class="btn-link" data-del="' + i + '">Entfernen</button>') + '</li>'; }).join('');
    $$('#file-list [data-del]').forEach(function (b) { b.addEventListener('click', function () { dateiEntfernen(+b.dataset.del); }); });
    var runs = Object.keys(S.run).filter(function (k) { return S.run[k]; });
    $('start-check').disabled = !nf || !runs.length || S.busy;
    $('start-check').innerHTML = S.busy ? '<span class="spinner"></span>Prüfung läuft' : (nf > 1 ? nf + ' Dokumente prüfen' : 'Prüfung starten');

    $$('.snav [data-sec]').forEach(function (el) { el.classList.toggle('on', el.dataset.sec === S.section); });
    $$('[data-pane]').forEach(function (el) { el.hidden = el.dataset.pane !== S.section; });
    setVal('s-name', d.name || '');
    $$('#seg-dark button').forEach(function (b) { b.classList.toggle('on', (b.dataset.v === '1') === !!d.dark); });
    $$('#seg-ts button').forEach(function (b) { b.classList.toggle('on', b.dataset.v === d.textSize); });
    $$('#seg-dens button').forEach(function (b) { b.classList.toggle('on', b.dataset.v === d.density); });
    $$('[data-sw]').forEach(function (el) { var o = !!d[el.dataset.sw]; el.classList.toggle('on', o); el.setAttribute('aria-checked', o ? 'true' : 'false'); });

    var ch = changes();
    var txt = ch.length === 1 ? '1 Änderung' : ch.length + ' Änderungen';
    $('bar').hidden = !(ch.length > 0 && S.screen === 'settings' && !S.sheet);
    $('bar-txt').textContent = txt;
    $('save-top').disabled = ch.length === 0 || S.busy;
    $('save-top').textContent = ch.length ? 'Speichern (' + ch.length + ')' : 'Speichern';
    $('modal').hidden = !S.sheet;
    $('dlg-sub').textContent = txt + (ch.length === 1 ? ' wird' : ' werden') + ' beim Speichern für dein Konto übernommen.';
    $('changes').innerHTML = ch.map(function (c) { return '<div><b>' + esc(c.label) + '</b><s>' + esc(c.from) + '</s><em>' + esc(c.to) + '</em></div>'; }).join('');
    $('drawer').hidden = !S.help;
    renderLauf();
  }

  function go(screen) { S.screen = screen; S.langMenu = false; S.help = false; window.scrollTo(0, 0); render(); }
  function goSection(id) { S.section = id; go('settings'); if (id === 'sicherheit') ladeSitzungen(); if (id === 'verwaltung') ladeBenutzer(); }

  // ------------------------------------------------------------ Start
  function boot() {
    api('GET', '/api/status').then(function (st) {
      S.status = st;
      ['version-foot', 'version-main'].forEach(function (id) { $(id).textContent = 'v' + st.version; });
      $('version-info').textContent = st.version;
      $('kopf-side').textContent = st.berichtKopf || 'FSH-Documentation';
      if (st.maxDateien) { MAX_DATEIEN = st.maxDateien; $('drop-hint').textContent = 'Bis zu ' + MAX_DATEIEN + ' Dateien je Prüfung, je bis 25 MB'; }
      $('info-verif').textContent = st.verifizierung === 'code' ? 'Code per E-Mail' : 'Nur Einmal-Passwort';
      if (st.support && st.support.adresse) $('help-adresse').textContent = st.support.adresse;
      if (st.support && (st.support.telefon || st.support.zeiten)) {
        $('help-kontakt').textContent = $('help-kontakt').textContent.replace('[Telefonnummer]', st.support.telefon || '[Telefonnummer]').replace('Montag bis Freitag von [8:00] bis [16:00] Uhr', st.support.zeiten || 'Montag bis Freitag von [8:00] bis [16:00] Uhr');
      }
      var fehlend = Object.keys(st.regeln || {}).filter(function (k) { return !st.regeln[k]; });
      var namen = { basis: 'pruefkatalog.json (Basisprüfung)', din: 'normlogik_82079.json (DIN 82079-1)', ce: 'ce_logik.json (CE)' };
      if (fehlend.length) { $('regeln-warn').hidden = false; $('regeln-warn').textContent = 'Regeldateien fehlen oder sind ungültig: ' + fehlend.map(function (k) { return namen[k]; }).join(', ') + '. Prüfungen mit diesen Regelsätzen werden abgebrochen. Bitte die Dateien korrigieren.'; }
      fehlend.forEach(function (k) { var h = $('hint-' + k); if (h) h.textContent = 'Regeldatei fehlt oder ist ungültig'; });
    }).catch(function () {});
    api('GET', '/api/ich').then(function (d) { anmeldungUebernehmen(d); go('main'); }).catch(function () { go('start'); });
  }

  function anmeldungUebernehmen(d) {
    S.user = d.benutzer; S.saved = Object.assign({}, d.einstellungen, { name: d.benutzer.name }); S.draft = Object.assign({}, S.saved);
    try { var l2 = localStorage.getItem('fsh-lang2'); if (l2 && (l2 === 'none' || LANGS[l2])) S.lang2 = l2; } catch (e) {}
    $('stand').textContent = 'Stand ' + new Date().toLocaleDateString('de-DE', { day: 'numeric', month: 'long', year: 'numeric' });
    ladePruefungen();
  }
  function abmelden(serverseitig) {
    var fertig = function () { S.user = null; S.saved = null; S.draft = null; S.result = null; S.laufErg = null; S.files = []; $('result').hidden = true; $('f-login').reset(); go('start'); };
    if (serverseitig === false) { fertig(); return; }
    api('POST', '/api/abmelden').then(fertig, fertig);
  }

  // ------------------------------------------------------------ Anmeldung
  $('f-login').addEventListener('submit', function (e) {
    e.preventDefault(); zeigeFehler('login-err', '');
    $('login-btn').disabled = true;
    api('POST', '/api/anmelden', { email: $('login-email').value.trim(), passwort: $('login-pwd').value, merken: S.remember })
      .then(function (d) { $('login-pwd').value = ''; anmeldungUebernehmen(d); go('main'); })
      .catch(function (err) { zeigeFehler('login-err', err.message); if (err.daten && err.daten.erstanmeldung) { S.erst.email = $('login-email').value.trim(); } })
      .then(function () { $('login-btn').disabled = false; });
  });
  $('to-erst').addEventListener('click', function () { S.step = 1; $('erst-email').value = S.erst.email || $('login-email').value.trim(); go('erst'); });
  $('back-start').addEventListener('click', function () { go('start'); });
  $('back-step1').addEventListener('click', function () { S.step = 1; render(); });
  $('login-show').addEventListener('click', function () { S.showPwd = !S.showPwd; render(); });
  $('erst-show').addEventListener('click', function () { S.showPwd = !S.showPwd; render(); });
  $('remember').addEventListener('click', function () { S.remember = !S.remember; render(); });

  function erstStart(erneut) {
    zeigeFehler('erst1-err', ''); zeigeFehler('erst2-err', '');
    S.erst.email = $('erst-email').value.trim(); S.erst.einmal = $('erst-otp').value.trim();
    return api('POST', '/api/erstanmeldung/start', { email: S.erst.email, einmalPasswort: S.erst.einmal }).then(function (d) {
      S.erst.verifizierung = !!d.verifizierung;
      if (d.verifizierung) {
        S.step = 2;
        var hint = $('erst2-hint');
        if (d.code) { hint.hidden = false; hint.textContent = 'Entwicklungsmodus: Der Code lautet ' + d.code + '.'; }
        else if (!d.gesendet) { hint.hidden = false; hint.textContent = 'Es ist kein E-Mail-Versand eingerichtet. Der Admin findet den Code in der Datei daten/codes.log.'; }
        else { hint.hidden = true; }
        if (erneut) showToast('Neuer Code gesendet');
      } else { S.step = 3; }
      render(); window.scrollTo(0, 0);
    }).catch(function (err) { zeigeFehler(S.step === 2 ? 'erst2-err' : 'erst1-err', err.message); });
  }
  $('f-step1').addEventListener('submit', function (e) { e.preventDefault(); erstStart(false); });
  $('code-again').addEventListener('click', function () { erstStart(true); });
  $('f-step2').addEventListener('submit', function (e) {
    e.preventDefault(); zeigeFehler('erst2-err', '');
    api('POST', '/api/erstanmeldung/code', { email: S.erst.email, code: $('erst-code').value.trim() })
      .then(function () { S.erst.code = $('erst-code').value.trim(); S.step = 3; render(); window.scrollTo(0, 0); })
      .catch(function (err) { zeigeFehler('erst2-err', err.message); });
  });
  $('f-step3').addEventListener('submit', function (e) {
    e.preventDefault(); if ($('finish').disabled) return; zeigeFehler('erst3-err', ''); S.busy = true; render();
    api('POST', '/api/erstanmeldung/abschluss', { email: S.erst.email, einmalPasswort: S.erst.einmal, code: S.erst.code || '', name: $('erst-name').value.trim(), passwort: $('erst-pwd').value, passwort2: $('erst-pwd2').value })
      .then(function (d) { S.busy = false; $('erst-pwd').value = ''; $('erst-pwd2').value = ''; $('erst-otp').value = ''; S.step = 1; anmeldungUebernehmen(d); go('main'); showToast('Willkommen, dein Konto ist eingerichtet'); })
      .catch(function (err) { S.busy = false; zeigeFehler('erst3-err', err.message); render(); });
  });
  ['erst-pwd', 'erst-pwd2', 'erst-name', 'pwd-alt', 'pwd-neu', 'pwd-neu2'].forEach(function (id) { $(id).addEventListener('input', render); });

  // ------------------------------------------------------------ Kopfleiste
  $('home').addEventListener('click', function () { go('main'); });
  $('logout').addEventListener('click', function () { abmelden(true); });
  $('logout2').addEventListener('click', function () { abmelden(true); });
  $('avatar').addEventListener('click', function () { goSection('profil'); });
  $('b-lang').addEventListener('click', function () { S.langMenu = !S.langMenu; render(); });
  $$('#lang-menu [data-lang]').forEach(function (el) { el.addEventListener('click', function () { sofort({ language: el.dataset.lang }); S.langMenu = false; render(); }); });
  $('b-theme').addEventListener('click', function () { sofort({ dark: !S.draft.dark }); });
  $('b-settings').addEventListener('click', function () { goSection(S.section); });
  $('b-help').addEventListener('click', function () { S.help = !S.help; S.langMenu = false; render(); });
  $('help-from-info').addEventListener('click', function () { S.help = true; render(); });
  $('drawer-close').addEventListener('click', function () { S.help = false; render(); });
  $('drawer-scrim').addEventListener('click', function () { S.help = false; render(); });
  $$('[data-go]').forEach(function (el) { el.addEventListener('click', function () { if (!S.user) { showGateHinweis(); return; } goSection(el.dataset.go); }); });
  function showGateHinweis() { alert && void 0; }

  function sofort(aenderung) {
    Object.assign(S.draft, aenderung); render();
    api('PATCH', '/api/ich/einstellungen', aenderung).then(function (d) { Object.assign(S.saved, d.einstellungen); Object.assign(S.draft, aenderung); render(); }).catch(function (err) { showToast(err.message); });
  }

  // ------------------------------------------------------------ Einstellungen
  $('back-main').addEventListener('click', function () { var n = changes().length; go('main'); if (n) showToast(n === 1 ? '1 Änderung noch nicht gespeichert' : n + ' Änderungen noch nicht gespeichert'); });
  $$('.snav [data-sec]').forEach(function (el) { el.addEventListener('click', function () { goSection(el.dataset.sec); el.scrollIntoView({ block: 'nearest', inline: 'center' }); }); });
  $('s-name').addEventListener('input', function () { S.draft.name = this.value; render(); });
  $$('#seg-dark button').forEach(function (b) { b.addEventListener('click', function () { S.draft.dark = b.dataset.v === '1'; render(); }); });
  $$('#seg-ts button').forEach(function (b) { b.addEventListener('click', function () { S.draft.textSize = b.dataset.v; render(); }); });
  $$('#seg-dens button').forEach(function (b) { b.addEventListener('click', function () { S.draft.density = b.dataset.v; render(); }); });
  $$('[data-sw]').forEach(function (el) { el.addEventListener('click', function () { S.draft[el.dataset.sw] = !S.draft[el.dataset.sw]; render(); }); });
  $('discard').addEventListener('click', function () { S.draft = Object.assign({}, S.saved); render(); });
  $('review').addEventListener('click', function () { S.sheet = true; render(); });
  $('dlg-close').addEventListener('click', function () { S.sheet = false; render(); });
  $('modal').addEventListener('click', function (e) { if (e.target === this) { S.sheet = false; render(); } });
  function speichern() {
    var ch = changes(); if (!ch.length || S.busy) return;
    var einst = {}, name = null;
    ch.forEach(function (c) { if (c.key === 'name') name = S.draft.name; else einst[c.key] = S.draft[c.key]; });
    S.busy = true; render();
    var p = Promise.resolve();
    if (Object.keys(einst).length) p = p.then(function () { return api('PATCH', '/api/ich/einstellungen', einst).then(function (d) { Object.assign(S.saved, d.einstellungen); }); });
    if (name !== null) p = p.then(function () { return api('PATCH', '/api/ich', { name: name }).then(function (d) { S.user = d.benutzer; S.saved.name = d.benutzer.name; }); });
    p.then(function () { S.busy = false; S.sheet = false; S.draft = Object.assign({}, S.saved); render(); showToast('Gespeichert'); })
     .catch(function (err) { S.busy = false; render(); showToast(err.message); });
  }
  $('save').addEventListener('click', speichern);
  $('save-top').addEventListener('click', speichern);

  // Passwort ändern
  $('pwd-open').addEventListener('click', function () { $('f-pwd').reset(); zeigeFehler('pwd-err', ''); $('modal-pwd').hidden = false; render(); $('pwd-alt').focus(); });
  $('pwd-close').addEventListener('click', function () { $('modal-pwd').hidden = true; });
  $('f-pwd').addEventListener('submit', function (e) {
    e.preventDefault(); if ($('pwd-save').disabled) return; zeigeFehler('pwd-err', ''); S.busy = true; render();
    api('POST', '/api/ich/passwort', { alt: $('pwd-alt').value, neu: $('pwd-neu').value, neu2: $('pwd-neu2').value })
      .then(function () { S.busy = false; $('modal-pwd').hidden = true; $('f-pwd').reset(); render(); showToast('Passwort geändert'); ladeSitzungen(); })
      .catch(function (err) { S.busy = false; render(); zeigeFehler('pwd-err', err.message); });
  });
  function ladeSitzungen() {
    api('GET', '/api/ich/sitzungen').then(function (d) {
      var el = $('sess-list');
      el.innerHTML = d.sitzungen.map(function (s) {
        return '<div class="sess"><div class="kv"><b class="sm" style="font-weight:500">' + esc(s.geraet || 'Unbekanntes Gerät') + '</b><span class="cap">Angemeldet ' + esc(fmtDatum(s.erstellt)) + ' · gültig bis ' + esc(fmtDatum(s.ablauf)) + '</span></div>' +
          (s.aktuell ? '<span class="cap" style="color:var(--success)">Diese Sitzung</span>' : '<button class="btn-link" data-sess="' + esc(s.id) + '">Abmelden</button>') + '</div>';
      }).join('') || '<span class="muted sm">Keine Sitzungen.</span>';
      $$('[data-sess]', el).forEach(function (b) { b.addEventListener('click', function () { api('DELETE', '/api/ich/sitzungen/' + b.dataset.sess).then(ladeSitzungen); }); });
    }).catch(function () {});
  }

  // Verwaltung
  function ladeBenutzer() {
    if (!S.user || S.user.rolle !== 'admin') return;
    api('GET', '/api/benutzer').then(function (d) {
      var st = { aktiv: ['g', 'Aktiv'], einmal: ['y', 'Erstanmeldung offen'], gesperrt: ['r', 'Gesperrt'] };
      $('users-tbody').innerHTML = d.benutzer.map(function (u) {
        var s = st[u.status] || ['', u.status];
        var selbst = u.id === S.user.id;
        var fremderInhaber = u.inhaber && !selbst;
        var aktion = fremderInhaber ? '<span class="cap">Nur der Inhaber selbst</span>' : '<button class="btn-link" data-otp="' + u.id + '">Neues Einmal-Passwort</button>' +
          (selbst || u.status === 'einmal' ? '' : ' · <button class="btn-link" data-status="' + u.id + '" data-neu="' + (u.status === 'gesperrt' ? 'aktiv' : 'gesperrt') + '">' + (u.status === 'gesperrt' ? 'Entsperren' : 'Sperren') + '</button>') +
          (S.user.inhaber && !selbst ? ' · <button class="btn-link" data-del-user="' + u.id + '" data-name="' + esc(u.name) + '" data-email="' + esc(u.email) + '" data-n="' + (u.pruefungen || 0) + '">Löschen</button>' : '');
        return '<tr><td data-l="Name" style="font-weight:500">' + esc(u.name) + (selbst ? ' <span class="cap">(du)</span>' : '') + '</td><td data-l="E-Mail" class="muted">' + esc(u.email) + '</td><td data-l="Rolle">' + (u.inhaber ? 'Admin · Inhaber' : u.rolle === 'admin' ? 'Admin' : 'Mitglied') + '</td><td data-l="Status"><span class="tick"><span class="dot ' + s[0] + '"></span>' + s[1] + '</span></td><td data-l="Aktion">' + aktion + '</td></tr>';
      }).join('');
      $('users-hint').textContent = S.user.inhaber ? 'Neue Konten bekommen ein Einmal-Passwort, das du persönlich weitergibst. Löschen kann nur der Inhaber, also du.' : 'Nur für Admins. Neue Konten bekommen ein Einmal-Passwort, das du persönlich weitergibst. Löschen kann nur der Inhaber.';
      $$('[data-del-user]').forEach(function (b) { b.addEventListener('click', function () {
        S.delUser = b.dataset.delUser; zeigeFehler('del-err', '');
        var n = +b.dataset.n;
        $('del-text').textContent = 'Konto von ' + b.dataset.name + ' (' + b.dataset.email + ') löschen? Sitzungen, Einstellungen und ' + (n === 1 ? '1 Prüfung' : n + ' Prüfungen') + ' mit Berichten werden gelöscht. Abgelegte Berichte im Ordner output bleiben. Das lässt sich nicht rückgängig machen.';
        $('modal-del').hidden = false;
      }); });
      $$('[data-otp]').forEach(function (b) { b.addEventListener('click', function () {
        api('POST', '/api/benutzer/' + b.dataset.otp + '/einmal-passwort').then(function (r) { zeigeOtp('Neues Einmal-Passwort. Alle Sitzungen dieser Person wurden beendet.', r.einmalPasswort); ladeBenutzer(); }).catch(function (err) { showToast(err.message); });
      }); });
      $$('[data-status]').forEach(function (b) { b.addEventListener('click', function () {
        api('PATCH', '/api/benutzer/' + b.dataset.status, { status: b.dataset.neu }).then(ladeBenutzer).catch(function (err) { showToast(err.message); });
      }); });
    }).catch(function (err) { showToast(err.message); });
  }
  function zeigeOtp(text, otp) { $('user-form').hidden = true; $('user-done').hidden = false; $('user-save').hidden = true; $('user-done-text').textContent = text; $('user-otp').textContent = otp; $('modal-user').hidden = false; }
  $('user-new').addEventListener('click', function () { $('f-user').reset(); zeigeFehler('user-err', ''); $('user-form').hidden = false; $('user-done').hidden = true; $('user-save').hidden = false; $('modal-user').hidden = false; $('u-name').focus(); });
  $('user-close').addEventListener('click', function () { $('modal-user').hidden = true; });
  $('del-close').addEventListener('click', function () { $('modal-del').hidden = true; });
  $('del-go').addEventListener('click', function () {
    if (!S.delUser) return; $('del-go').disabled = true;
    api('DELETE', '/api/benutzer/' + S.delUser).then(function (r) { $('modal-del').hidden = true; showToast('Konto von ' + r.geloescht.name + ' gelöscht'); ladeBenutzer(); })
      .catch(function (err) { zeigeFehler('del-err', err.message); })
      .then(function () { $('del-go').disabled = false; });
  });
  $('user-copy').addEventListener('click', function () { var t = $('user-otp').textContent; (navigator.clipboard ? navigator.clipboard.writeText(t) : Promise.reject()).then(function () { showToast('Kopiert'); }, function () { showToast('Bitte markieren und kopieren'); }); });
  $('f-user').addEventListener('submit', function (e) {
    e.preventDefault(); zeigeFehler('user-err', '');
    api('POST', '/api/benutzer', { name: $('u-name').value.trim(), email: $('u-email').value.trim(), rolle: $('u-rolle').value })
      .then(function (r) { zeigeOtp('Konto für ' + r.benutzer.name + ' angelegt. Das Einmal-Passwort gilt ' + r.gueltigTage + ' Tage:', r.einmalPasswort); ladeBenutzer(); })
      .catch(function (err) { zeigeFehler('user-err', err.message); });
  });

  // ------------------------------------------------------------ Prüfung
  var MAX_DATEIEN = 20;
  function setFiles(liste) {
    var neu = Array.prototype.slice.call(liste || []);
    if (!neu.length || S.busy) return;
    var abgelehnt = [];
    neu.forEach(function (f) {
      if (!/\.(docx|pdf)$/i.test(f.name)) { abgelehnt.push(f.name); return; }
      if (S.files.some(function (x) { return x.name === f.name && x.size === f.size; })) return;
      S.files.push(f);
    });
    if (abgelehnt.length) showToast('Nur Word (.docx) und PDF: ' + abgelehnt.join(', '));
    if (S.files.length > MAX_DATEIEN) { S.files = S.files.slice(0, MAX_DATEIEN); showToast('Höchstens ' + MAX_DATEIEN + ' Dateien je Prüfung'); }
    zeigeFehler('check-err', ''); render();
  }
  function dateiEntfernen(i) { if (S.busy) return; S.files.splice(i, 1); render(); }
  $('file').addEventListener('change', function () { setFiles(this.files); this.value = ''; });
  var drop = $('drop');
  ['dragenter', 'dragover'].forEach(function (ev) { drop.addEventListener(ev, function (e) { e.preventDefault(); drop.style.borderColor = 'var(--accent)'; }); });
  ['dragleave', 'drop'].forEach(function (ev) { drop.addEventListener(ev, function (e) { e.preventDefault(); drop.style.borderColor = ''; }); });
  drop.addEventListener('drop', function (e) { if (e.dataTransfer.files) setFiles(e.dataTransfer.files); });
  $$('[data-run]').forEach(function (el) { el.addEventListener('click', function () { S.run[el.dataset.run] = !S.run[el.dataset.run]; render(); }); });
  $$('#seg-run-lang2 button').forEach(function (b) { b.addEventListener('click', function () { S.lang2 = b.dataset.v; try { localStorage.setItem('fsh-lang2', S.lang2); } catch (e) {} render(); }); });

  // Statuspanel: erscheint erst nach 400 ms, damit kurze Prüfungen nicht aufblitzen.
  var PHASEN = ['lesen', 'pruefen', 'berichte'];
  function renderLauf() {
    var l = S.lauf;
    $('lauf').hidden = !(S.busy && S.laufSichtbar && l);
    if (!l) return;
    $('lauf-titel').textContent = l.dokumente > 1 ? 'Dokument ' + l.dokument + ' von ' + l.dokumente + ' wird geprüft' : 'Dokument wird geprüft';
    $('lauf-datei').textContent = l.datei || '';
    var idx = PHASEN.indexOf(l.phase);
    $$('.lauf-phasen li').forEach(function (li, i) {
      li.classList.toggle('fertig', idx > i || l.phase === 'fertig');
      li.classList.toggle('aktiv', idx === i);
    });
    $('lauf-berichte').textContent = (l.phase === 'berichte' && l.von) ? 'Bericht ' + l.n + ' von ' + l.von : '';
  }
  function laufStart(datei, anzahl) {
    S.lauf = { phase: 'lesen', datei: datei, dokument: 1, dokumente: anzahl || 1, n: 0, von: 0 }; S.laufSichtbar = false;
    clearTimeout(S.laufTimer);
    S.laufTimer = setTimeout(function () { S.laufSichtbar = true; renderLauf(); }, 400);
  }
  function laufEnde() { clearTimeout(S.laufTimer); S.laufTimer = null; S.lauf = null; S.laufSichtbar = false; }

  // Die Prüfung schickt ihren Fortschritt als Zeilen (eine JSON-Zeile je Phase, zuletzt Ergebnis oder Fehler).
  function pruefungStreamen(fd) {
    return fetch('/api/pruefung', { method: 'POST', credentials: 'same-origin', body: fd }).then(function (r) {
      if (r.status === 401) { abmelden(false); throw new Error('Bitte zuerst anmelden.'); }
      if (!r.ok) {
        return r.text().then(function (t) { var d = {}; try { d = JSON.parse(t); } catch (e) {} throw new Error(d.fehler || ('Fehler ' + r.status + '. Bitte noch einmal versuchen.')); });
      }
      var verarbeiten = function (zeile) {
        if (!zeile.trim()) return null;
        var e; try { e = JSON.parse(zeile); } catch (err) { return null; }
        if (e.phase === 'ergebnis') return null; // Ergebnis oder Fehler eines einzelnen Dokuments, der Lauf geht weiter
        if (e.fehler) { var fehler = new Error(e.fehler); fehler.status = e.status; throw fehler; }
        if (e.phase === 'fertig') return e.lauf;
        if (e.id && e.pdfs) return { lauf: null, dateien: 1, ergebnisse: [e], fehler: [], pdfAnzahl: e.pdfs.length, zip: e.zip, ablegen: null }; // älterer Server
        S.lauf = { phase: e.phase, datei: e.datei || (S.lauf ? S.lauf.datei : ''), dokument: e.dokument || 1, dokumente: e.dokumente || (S.lauf ? S.lauf.dokumente : 1), n: e.n || 0, von: e.von || 0 }; renderLauf();
        return null;
      };
      if (!r.body || !r.body.getReader) {
        return r.text().then(function (t) { var erg = null; t.split('\n').forEach(function (z) { var x = verarbeiten(z); if (x) erg = x; }); if (!erg) throw new Error('Unerwartete Antwort vom Server.'); return erg; });
      }
      var reader = r.body.getReader(), dec = new TextDecoder(), rest = '';
      return new Promise(function (resolve, reject) {
        function weiter() {
          reader.read().then(function (st) {
            try {
              if (st.done) {
                var x = verarbeiten(rest); if (x) { resolve(x); } else { reject(new Error('Unerwartete Antwort vom Server.')); }
                return;
              }
              rest += dec.decode(st.value, { stream: true });
              var teile = rest.split('\n'); rest = teile.pop();
              for (var i = 0; i < teile.length; i++) { var erg = verarbeiten(teile[i]); if (erg) { resolve(erg); reader.cancel(); return; } }
              weiter();
            } catch (err) { reject(err); reader.cancel(); }
          }, reject);
        }
        weiter();
      });
    });
  }

  $('start-check').addEventListener('click', function () {
    if (!S.files.length || S.busy) return;
    zeigeFehler('check-err', ''); S.result = null; S.laufErg = null; $('result').hidden = true; S.busy = true; laufStart(S.files[0].name, S.files.length); render();
    var fd = new FormData();
    S.files.forEach(function (f) { fd.append('datei', f); });
    fd.append('regelsaetze', Object.keys(S.run).filter(function (k) { return S.run[k]; }).join(','));
    fd.append('zusatzsprache', S.lang2 === 'none' ? '' : S.lang2);
    fd.append('fortschritt', '1');
    pruefungStreamen(fd).then(function (lauf) {
      laufEnde(); S.busy = false; render();
      if (!lauf.ergebnisse.length) { zeigeFehler('check-err', (lauf.fehler[0] && lauf.fehler[0].fehler) || 'Die Prüfung ist fehlgeschlagen. Bitte noch einmal versuchen.'); return; }
      S.laufErg = lauf; S.result = lauf.ergebnisse[0];
      zeigeLauf(lauf); zeigeErgebnis(S.result); ladePruefungen();
      showPop(laufSatz(lauf));
    }).catch(function (err) { laufEnde(); S.busy = false; render(); zeigeFehler('check-err', err.message); });
  });
  function laufSatz(lauf) {
    if (lauf.dateien === 1) { var r = lauf.ergebnisse[0]; var a = AMPEL[r.ampel] || ['', r.ampel]; return r.dateiname + ': ' + r.score + ' %, ' + a[1].split(' · ')[0] + '. ' + r.pdfs.length + ' PDFs liegen bereit.'; }
    var z = { gruen: 0, gelb: 0, rot: 0 }; lauf.ergebnisse.forEach(function (r) { if (z[r.ampel] !== undefined) z[r.ampel]++; });
    var s = lauf.ergebnisse.length + ' Dokumente geprüft: ' + z.gruen + ' Grün, ' + z.gelb + ' Gelb, ' + z.rot + ' Rot.';
    if (lauf.fehler.length) s += ' ' + lauf.fehler.length + (lauf.fehler.length === 1 ? ' Datei' : ' Dateien') + ' nicht lesbar.';
    return s + ' ' + lauf.pdfAnzahl + ' PDFs liegen bereit.';
  }
  function zeigeLauf(lauf) {
    var mehrere = lauf.dateien > 1;
    $('lauf-ergebnis').hidden = !mehrere;
    if (!mehrere) return;
    $('lauf-meta').textContent = lauf.ergebnisse.length + ' von ' + lauf.dateien + ' Dokumenten geprüft · ' + lauf.pdfAnzahl + ' PDFs';
    var zeilen = lauf.ergebnisse.map(function (r) {
      var a = AMPEL[r.ampel] || ['', r.ampel];
      return '<tr><td data-l="Dokument" style="font-weight:500">' + esc(r.dateiname) + '</td><td data-l="Score" class="mono">' + r.score + ' %</td><td data-l="Ampel"><span class="tick"><span class="dot ' + a[0] + '"></span>' + esc(a[1]) + '</span></td><td data-l="Funde">' + r.fundeAnzahl + '</td><td data-l="Aufwand" class="mono">' + String(r.stunden).replace('.', ',') + ' h</td><td data-l="Berichte"><button class="btn-link" data-zeige="' + esc(r.id) + '">Ansehen</button></td></tr>';
    }).concat(lauf.fehler.map(function (f) {
      return '<tr><td data-l="Dokument" style="font-weight:500">' + esc(f.datei) + '</td><td colspan="5" class="muted" data-l="Hinweis">Nicht geprüft: ' + esc(f.fehler) + '</td></tr>';
    }));
    $('lauf-tbody').innerHTML = zeilen.join('');
    $$('#lauf-tbody [data-zeige]').forEach(function (b) { b.addEventListener('click', function () { var r = lauf.ergebnisse.filter(function (x) { return x.id === b.dataset.zeige; })[0]; if (r) { S.result = r; zeigeErgebnis(r); } }); });
    $('lauf-zip').href = lauf.zip;
  }
  $('lauf-store').addEventListener('click', function () {
    if (!S.laufErg || !S.laufErg.ablegen) return;
    api('POST', S.laufErg.ablegen).then(function (r) { showToast(r.abgelegt.length + ' PDFs aus ' + r.dokumente + ' Dokumenten im Ordner ' + (String(r.ordner).split('/').pop() || 'output') + ' abgelegt'); }).catch(function (err) { showToast(err.message); });
  });

  function zeigeErgebnis(r) {
    var a = AMPEL[r.ampel] || ['', r.ampel];
    var namen = { basis: 'Basisprüfung', din: 'DIN 82079-1', ce: 'CE' };
    $('res-meta').textContent = r.dateiname + ' · ' + fmtDatum(r.erstellt);
    $('res-score').textContent = r.score + ' %';
    $('res-ampel').innerHTML = '<span class="dot ' + a[0] + '"></span>' + esc(a[1]);
    $('res-regeln').textContent = r.regelsaetze.map(function (k) { return namen[k] || k; }).join(', ');
    var kl = r.klassen || {};
    var teile = [];
    if (kl.Kritisch) teile.push(kl.Kritisch + ' kritisch'); if (kl.Schwer) teile.push(kl.Schwer + ' schwer'); if (kl.Mittel) teile.push(kl.Mittel + ' mittel'); if (kl.Gering) teile.push(kl.Gering + ' gering');
    $('res-funde').textContent = r.fundeAnzahl + (teile.length ? ' · ' + teile.join(', ') : '');
    $('res-aufwand').textContent = String(r.stunden).replace('.', ',') + ' h';
    $('res-langs').textContent = r.sprachen.map(function (l) { return LANGS_DE[l] || l; }).join(' und ');
    $('res-fazit').textContent = r.fazit;
    var hinweise = r.lesehinweise || [];
    $('res-hinweise').hidden = !hinweise.length; $('res-hinweise').textContent = hinweise.length ? 'Lesehinweis: ' + hinweise.join(' ') : '';
    var btn = function (art) { return r.pdfs.filter(function (p) { return p.bericht === art; }).map(function (p) { return '<a class="btn" href="' + esc(p.url) + '" target="_blank" rel="noopener">PDF ' + esc(LANGS[p.sprache] || p.sprache) + '</a>'; }).join(''); };
    $('pdf-pruef').innerHTML = btn('pruef'); $('pdf-fach').innerHTML = btn('fach');
    $('zip-label').textContent = r.pdfs.length + ' PDFs';
    $('act-zip').href = r.zip;
    $('res-n').textContent = r.fundeAnzahl;
    $('res-tbody').innerHTML = (r.funde || []).map(function (f) {
      var k = KLASSE[f.Fehlerklasse]; var kz = k ? '<span class="tick"><span class="dot ' + k + '"></span>' + esc(f.Fehlerklasse) + '</span>' : esc(f.Fehlerklasse);
      return '<tr><td data-l="ID" class="mono">' + esc(f.ID) + '</td><td data-l="Bereich">' + esc(f.Bereich) + '</td><td data-l="Klasse">' + kz + '</td><td data-l="Bewertung">' + esc(f.Bewertung) + '</td><td data-l="Empfehlung">' + esc(f.Empfehlung) + '</td></tr>';
    }).join('') || '<tr><td colspan="5" class="muted">Keine Abweichungen festgestellt.</td></tr>';
    $('result').hidden = false;
    (S.laufErg && S.laufErg.dateien > 1 ? $('res-detail') : $('result')).scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  function ladePruefungen() {
    api('GET', '/api/pruefungen').then(function (d) {
      $('list-tbody').innerHTML = d.pruefungen.map(function (p) {
        var a = AMPEL[p.ampel] || ['', p.ampel];
        return '<tr><td data-l="Datum" class="mono">' + esc(fmtDatum(p.erstellt)) + '</td><td data-l="Dokument">' + esc(p.dateiname) + '</td><td data-l="Score" class="mono">' + p.score + ' %</td><td data-l="Ampel"><span class="tick"><span class="dot ' + a[0] + '"></span>' + esc(a[1]) + '</span></td><td data-l="Berichte"><button class="btn-link" data-open="' + esc(p.id) + '">Öffnen</button></td></tr>';
      }).join('') || '<tr><td colspan="5" class="muted">Noch keine Prüfung.</td></tr>';
      $$('[data-open]').forEach(function (b) { b.addEventListener('click', function () { api('GET', '/api/pruefung/' + b.dataset.open).then(function (r) { S.result = r; S.laufErg = null; $('lauf-ergebnis').hidden = true; zeigeErgebnis(r); }).catch(function (err) { showToast(err.message); }); }); });
    }).catch(function () {});
  }
  $('pop-close').addEventListener('click', hidePop);
  $('pop-open').addEventListener('click', function () { hidePop(); if (S.result) { $('result').hidden = false; $('result').scrollIntoView({ behavior: 'smooth', block: 'start' }); } });
  $('pop-demo').addEventListener('click', function () { showPop('Beispiel.docx: 82 %, Grün. 4 PDFs liegen bereit.', true); });
  $('act-store').addEventListener('click', function () { if (!S.result) return; api('POST', '/api/pruefung/' + S.result.id + '/ablegen').then(function (r) { showToast(r.abgelegt.length + ' PDFs im Ordner ' + (String(r.ordner).split('/').pop() || 'output') + ' abgelegt'); }).catch(function (err) { showToast(err.message); }); });
  $('act-done').addEventListener('click', function () { S.result = null; S.laufErg = null; S.files = []; $('file').value = ''; $('result').hidden = true; $('lauf-ergebnis').hidden = true; render(); window.scrollTo({ top: 0, behavior: 'smooth' }); showToast('Prüfung abgeschlossen'); });
  $('act-mail').addEventListener('click', function () { if (!S.result) return; $('mail-sub').textContent = 'Fachbericht zu ' + S.result.dateiname + ' in ' + S.result.sprachen.map(function (l) { return LANGS_DE[l] || l; }).join(' und '); $('mail-text').hidden = true; $('mail-copy').hidden = true; zeigeFehler('mail-err', ''); $('modal-mail').hidden = false; });
  $('mail-close').addEventListener('click', function () { $('modal-mail').hidden = true; });
  $('mail-go').addEventListener('click', function () {
    api('POST', '/api/pruefung/' + S.result.id + '/mail-entwurf', { an: $('mail-an').value.trim() }).then(function (r) {
      if (r.entwurf === 'mail') { $('modal-mail').hidden = true; showToast('Entwurf in Apple Mail angelegt, ' + r.anhaenge.length + ' Anhänge'); }
      else { $('mail-text').hidden = false; $('mail-text').textContent = 'Betreff: ' + r.betreff + '\n\n' + r.text + '\n\nAnhänge: ' + r.anhaenge.join(', '); $('mail-copy').hidden = false; }
    }).catch(function (err) { zeigeFehler('mail-err', err.message); });
  });
  $('mail-copy').addEventListener('click', function () { var t = $('mail-text').textContent; (navigator.clipboard ? navigator.clipboard.writeText(t) : Promise.reject()).then(function () { showToast('Kopiert'); }, function () { showToast('Bitte markieren und kopieren'); }); });

  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { S.langMenu = false; S.help = false; S.sheet = false; $('modal-pwd').hidden = true; $('modal-user').hidden = true; $('modal-del').hidden = true; $('modal-mail').hidden = true; render(); } });
  document.addEventListener('click', function (e) { if (S.langMenu && !e.target.closest('.menu-wrap')) { S.langMenu = false; render(); } });

  boot();
})();
