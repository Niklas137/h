/* Dokumentenprüfer: Oberfläche. Kein Framework, spricht mit /api/… */
(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };
  var LANGS = { de: 'Deutsch', en: 'English', uk: 'Українська', ru: 'Русский' }; // Eigennamen für Knöpfe und Menü
  var UI = window.I18N || { de: {} };
  var LABEL_KEYS = { name: 'lbl_name', dark: 'set_dark', textSize: 'set_text', density: 'set_density', language: 'set_language', notifyPopup: 'set_popup', notifyApp: 'set_app', notifyWeekly: 'set_weekly' };
  var KLASSE = { Kritisch: 'r', Schwer: 'y', Mittel: '', Gering: '' };
  var AMPEL_FARBE = { gruen: 'g', gelb: 'y', rot: 'r' };

  var S = {
    status: null, user: null, saved: null, draft: null,
    screen: 'start', step: 1, erst: { email: '', einmal: '', verifizierung: true },
    section: 'profil', help: false, langMenu: false, sheet: false, remember: false, showPwd: false,
    run: { basis: true, din: true, ce: true }, reportLangs: ['de'], files: [], result: null, laufErg: null, busy: false,
    punkte: null, ohne: {}, punkteOffen: false,
    toastTimer: null, popTimer: null,
    lauf: null, laufSichtbar: false, laufTimer: null,
    gateLang: 'de', uebersetzt: null
  };
  try { var gl = localStorage.getItem('fsh-ui-lang') || (navigator.language || 'de').slice(0, 2).toLowerCase(); if (UI[gl]) S.gateLang = gl; } catch (e) {}

  // ------------------------------------------------------------ Sprache der Oberfläche
  function uiLang() { if (S.draft && UI[S.draft.language]) return S.draft.language; return UI[S.gateLang] ? S.gateLang : 'de'; }
  function t(key, vars) {
    var l = uiLang();
    var s = (UI[l] && UI[l][key] !== undefined) ? UI[l][key] : (UI.de[key] !== undefined ? UI.de[key] : key);
    if (vars) Object.keys(vars).forEach(function (k) { s = s.split('{' + k + '}').join(String(vars[k])); });
    return s;
  }
  function langName(code) { return t('sprache_' + code); }
  function ampel(a) { return AMPEL_FARBE[a] ? [AMPEL_FARBE[a], t('ampel_' + a)] : ['', a]; }
  function satzName(k) { return (S.punkte && S.punkte[k] && S.punkte[k].nameAnzeige) || { basis: t('satz_basis'), din: 'DIN 82079-1', ce: t('satz_ce') }[k] || k; }
  // Statische Texte der Seite: alle Elemente mit data-i18n bekommen den Text der aktuellen Sprache.
  function uebersetzen() {
    var l = uiLang(); if (S.uebersetzt === l) return; S.uebersetzt = l;
    document.documentElement.lang = l; document.documentElement.dataset.sprache = l; document.title = t('titel_seite');
    $$('[data-i18n]').forEach(function (el) { el.textContent = t(el.dataset.i18n); });
    $$('[data-i18n-ph]').forEach(function (el) { el.placeholder = t(el.dataset.i18nPh); });
    $$('[data-i18n-aria]').forEach(function (el) { el.setAttribute('aria-label', t(el.dataset.i18nAria)); });
  }
  function sprachWechsel() {
    // Serverseitig gelieferte Anzeigetexte neu holen, damit Listen und Ergebnis in der neuen Sprache stehen.
    ladePunkte(); ladePruefungen();
    if (S.screen === 'settings') { ladeSitzungen(); ladeBenutzer(); }
    if (S.laufErg && S.laufErg.lauf) { api('GET', '/api/lauf/' + S.laufErg.lauf).then(function (l) { S.laufErg = Object.assign({}, S.laufErg, l); zeigeLauf(S.laufErg, true); }).catch(function () {}); }
    if (S.result) { api('GET', '/api/pruefung/' + S.result.id).then(function (r) { S.result = r; zeigeErgebnis(r, true); }).catch(function () {}); }
  }

  // ------------------------------------------------------------ API
  function api(method, url, body, isForm) {
    var opt = { method: method, credentials: 'same-origin', headers: { 'X-Sprache': uiLang() } };
    if (body !== undefined) {
      if (isForm) { opt.body = body; } else { opt.headers['Content-Type'] = 'application/json'; opt.body = JSON.stringify(body); }
    }
    return fetch(url, opt).then(function (r) {
      return r.text().then(function (t) {
        var d = {};
        try { d = t ? JSON.parse(t) : {}; } catch (e) { d = { fehler: window.__t('unerwartet') }; }
        if (r.status === 401 && S.screen !== 'start' && S.screen !== 'erst' && !/anmelden|erstanmeldung|passwort/.test(url)) { abmelden(false); }
        if (!r.ok) { var err = new Error(d.fehler || window.__t('fehler_status', { status: r.status })); err.daten = d; err.status = r.status; throw err; }
        return d;
      });
    });
  }
  function zeigeFehler(id, text) { var el = $(id); el.textContent = text || ''; el.hidden = !text; }

  // ------------------------------------------------------------ Hilfen
  function initials(n) { var p = (n || '').trim().split(/\s+/); return ((p[0] ? p[0].charAt(0) : '') + (p[1] ? p[1].charAt(0) : '')).toUpperCase() || '–'; }
  function esc(s) { return String(s === null || s === undefined ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function fmtGroesse(b) { return b < 1024 * 1024 ? Math.max(1, Math.round(b / 1024)) + ' KB' : (b / 1024 / 1024).toFixed(1).replace('.', ',') + ' MB'; }
  function fmtDatum(iso) { if (!iso) return ''; var d = new Date(iso); if (isNaN(d)) return iso; return d.toLocaleDateString(t('locale'), { day: '2-digit', month: '2-digit', year: 'numeric' }); }
  function fmt(key, v) {
    if (typeof v === 'boolean') { if (key === 'dark') return t(v ? 'common.dark' : 'common.light'); return t(v ? 'common.on' : 'common.off'); }
    if (key === 'textSize') return t({ klein: 'common.small', normal: 'common.normal', gross: 'common.large' }[v] || 'common.normal');
    if (key === 'density') return t(v === 'kompakt' ? 'common.compact' : 'common.normal');
    if (key === 'language') return langName(UI[v] ? v : 'de');
    return String(v);
  }
  function changes() {
    if (!S.saved || !S.draft) return [];
    return Object.keys(LABEL_KEYS).filter(function (k) { return S.draft[k] !== S.saved[k]; }).map(function (k) { return { key: k, label: t(LABEL_KEYS[k]), from: fmt(k, S.saved[k]), to: fmt(k, S.draft[k]) }; });
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
    applyTheme(); uebersetzen();
    $$('[data-gate-lang]').forEach(function (b) { b.classList.toggle('on', b.dataset.gateLang === uiLang()); });
    if (S.status) {
      var st = S.status, sup = st.support || {};
      $('drop-hint').textContent = t('drop_hint', { n: MAX_DATEIEN });
      $('info-verif').textContent = t(st.verifizierung === 'code' ? 'app.set.info.verif' : 'app.set.info.verif');
      $('info-regeln').textContent = ['basis', 'din', 'ce'].map(satzName).join(', ');
      $('help-adresse').textContent = sup.adresse || t('app.help.contact.text');
      $('help-kontakt').textContent = t('app.help.contact.text', { telefon: sup.telefon || t('app.help.contact.text'), zeiten: sup.zeiten || t('app.help.contact.text') });
      var fehlend = Object.keys(st.regeln || {}).filter(function (k) { return !st.regeln[k]; });
      var dateien = { basis: 'pruefkatalog.json', din: 'normlogik_82079.json', ce: 'ce_logik.json' };
      $('regeln-warn').hidden = !fehlend.length;
      if (fehlend.length) $('regeln-warn').textContent = t('regeln_warn', { liste: fehlend.map(function (k) { return dateien[k] + ' (' + satzName(k) + ')'; }).join(', ') });
      fehlend.forEach(function (k) { $('hint-' + k).textContent = t('regel_fehlt'); });
    }
    $('gate').hidden = !inGate; $('app').hidden = inGate;
    $('pitch-start').hidden = S.screen !== 'start'; $('pitch-erst').hidden = S.screen !== 'erst';
    $('f-login').hidden = S.screen !== 'start';
    $('f-step1').hidden = !(S.screen === 'erst' && S.step === 1);
    $('f-step2').hidden = !(S.screen === 'erst' && S.step === 2);
    $('f-step3').hidden = !(S.screen === 'erst' && S.step === 3);
    $$('.step').forEach(function (el) { var n = +el.dataset.step; el.classList.toggle('active', n === S.step); el.classList.toggle('done', n < S.step); });
    $('erst2-text').innerHTML = t('s2_text', { email: '<b id="email-shown">' + esc(S.erst.email || t('deine_email')) + '</b>' }); $('erst-email2').value = S.erst.email;
    ['login-pwd', 'erst-pwd', 'erst-pwd2'].forEach(function (id) { $(id).type = S.showPwd ? 'text' : 'password'; });
    $('login-show').textContent = t(S.showPwd ? 'common.hide' : 'common.show'); $('erst-show').textContent = t(S.showPwd ? 'common.hide' : 'common.show');
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
    $('user-name').textContent = nm; $('user-name3').textContent = nm;
    var rolleTxt = t(u.inhaber ? 'rolle_inhaber' : (u.rolle === 'admin' ? 'rolle_admin' : 'rolle_mitglied'));
    $('settings-sub').textContent = t('settings_sub', { name: nm, rolle: rolleTxt }); $('rolle-badge').textContent = rolleTxt;
    $('avatar').textContent = ini; $('avatar2').textContent = ini;
    $('hello').textContent = t('hallo', { name: nm.trim().split(/\s+/)[0] });
    $('stand').textContent = t('stand', { datum: new Date().toLocaleDateString(t('locale'), { day: 'numeric', month: 'long', year: 'numeric' }) });
    $('s-email').value = u.email;
    $('grp-team').hidden = u.rolle !== 'admin'; $('nav-verwaltung').hidden = u.rolle !== 'admin';

    var nf = S.files.length;
    var baseLang = LANGS[d.language] ? d.language : 'de';
    $('ui-side').textContent = langName(baseLang);
    var langs = S.reportLangs.filter(function (l) { return LANGS[l]; });
    if (!langs.length) { langs = [baseLang]; S.reportLangs = langs.slice(); }
    $('rl-side').textContent = langs.map(langName).join(t('common.and'));
    var langsTxt = langs.map(langName).join(t('common.and'));
    $('report-plan').textContent = nf > 1 ? t('common.plan_mehr', { langs: langsTxt, n: langs.length * 2, gesamt: langs.length * 2 * nf }) : t('common.plan', { langs: langsTxt, n: langs.length * 2 });
    $$('#seg-report-langs button').forEach(function (b) { var on = langs.indexOf(b.dataset.v) >= 0; b.classList.toggle('on', on); b.setAttribute('aria-pressed', on ? 'true' : 'false'); });
    $$('[data-run]').forEach(function (el) { el.querySelector('.cb').classList.toggle('on', !!S.run[el.dataset.run]); });
    $('drop-text').textContent = nf === 0 ? t('drop_text') : nf === 1 ? S.files[0].name : t('drop_n', { n: nf });
    $('file-list').hidden = nf < 1;
    $('file-list').innerHTML = S.files.map(function (f, i) { return '<li><span class="t">' + esc(f.name) + '</span><span class="cap">' + fmtGroesse(f.size) + '</span>' + (S.busy ? '' : '<button type="button" class="btn-link" data-del="' + i + '">' + esc(t('entfernen')) + '</button>') + '</li>'; }).join('');
    $$('#file-list [data-del]').forEach(function (b) { b.addEventListener('click', function () { dateiEntfernen(+b.dataset.del); }); });
    var runs = Object.keys(S.run).filter(function (k) { return S.run[k]; });
    renderPunkte(runs);
    var leer = runs.filter(function (k) { return S.punkte && S.punkte[k] && S.punkte[k].punkte.length && S.punkte[k].punkte.every(function (p) { return S.ohne[p.id]; }); });
    $('start-check').disabled = !nf || !runs.length || S.busy || leer.length > 0;
    $('start-check').innerHTML = S.busy ? '<span class="spinner"></span>' + esc(t('app.check.busy')) : esc(nf > 1 ? t('common.start_n', { n: nf }) : t('app.check.btn'));

    $$('.snav [data-sec]').forEach(function (el) { el.classList.toggle('on', el.dataset.sec === S.section); });
    $$('[data-pane]').forEach(function (el) { el.hidden = el.dataset.pane !== S.section; });
    setVal('s-name', d.name || '');
    $$('#seg-dark button').forEach(function (b) { b.classList.toggle('on', (b.dataset.v === '1') === !!d.dark); });
    $$('#seg-ts button').forEach(function (b) { b.classList.toggle('on', b.dataset.v === d.textSize); });
    $$('#seg-dens button').forEach(function (b) { b.classList.toggle('on', b.dataset.v === d.density); });
    $$('[data-sw]').forEach(function (el) { var o = !!d[el.dataset.sw]; el.classList.toggle('on', o); el.setAttribute('aria-checked', o ? 'true' : 'false'); });

    var ch = changes();
    var txt = ch.length === 1 ? t('aenderung_1') : t('aenderung_n', { n: ch.length });
    $('bar').hidden = !(ch.length > 0 && S.screen === 'settings' && !S.sheet);
    $('bar-txt').textContent = txt;
    $('save-top').disabled = ch.length === 0 || S.busy;
    $('save-top').textContent = ch.length ? t('app.set.save_count', { n: ch.length }) : t('app.set.save');
    $('modal').hidden = !S.sheet;
    $('dlg-sub').textContent = ch.length === 1 ? t('common.save') : t('common.save');
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
      if (st.maxDateien) MAX_DATEIEN = st.maxDateien;
      render();
    }).catch(function () {});
    api('GET', '/api/ich').then(function (d) { anmeldungUebernehmen(d); go('main'); }).catch(function () { go('start'); });
  }

  function anmeldungUebernehmen(d) {
    S.user = d.benutzer; S.saved = Object.assign({}, d.einstellungen, { name: d.benutzer.name }); S.draft = Object.assign({}, S.saved);
    // Berichtssprachen: zuletzt gewählte aus dem Browser, sonst die Kontosprache. Unabhängig von der Oberfläche.
    S.reportLangs = [UI[S.saved.language] ? S.saved.language : 'de'];
    try { var rl = JSON.parse(localStorage.getItem('fsh-report-langs') || 'null'); if (Array.isArray(rl)) { rl = rl.filter(function (l) { return LANGS[l]; }).slice(0, 2); if (rl.length) S.reportLangs = rl; } } catch (e) {}
    if (UI[S.saved.language]) { S.gateLang = S.saved.language; try { localStorage.setItem('fsh-ui-lang', S.gateLang); } catch (e) {} }
    ladePruefungen(); ladePunkte();
  }
  function abmelden(serverseitig) {
    var fertig = function () { S.user = null; S.saved = null; S.draft = null; S.result = null; S.laufErg = null; S.files = []; S.punkte = null; S.ohne = {}; S.punkteOffen = false; $('result').hidden = true; $('f-login').reset(); go('start'); };
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
        if (d.code) { hint.hidden = false; hint.textContent = t('dev_code', { code: d.code }); }
        else if (!d.gesendet) { hint.hidden = false; hint.textContent = t('kein_versand'); }
        else { hint.hidden = true; }
        if (erneut) showToast(t('neuer_code'));
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
      .then(function (d) { S.busy = false; $('erst-pwd').value = ''; $('erst-pwd2').value = ''; $('erst-otp').value = ''; S.step = 1; anmeldungUebernehmen(d); go('main'); showToast(t('willkommen')); })
      .catch(function (err) { S.busy = false; zeigeFehler('erst3-err', err.message); render(); });
  });
  ['erst-pwd', 'erst-pwd2', 'erst-name', 'pwd-alt', 'pwd-neu', 'pwd-neu2'].forEach(function (id) { $(id).addEventListener('input', render); });

  // ------------------------------------------------------------ Kopfleiste
  $('home').addEventListener('click', function () { go('main'); });
  $('logout').addEventListener('click', function () { abmelden(true); });
  $('logout2').addEventListener('click', function () { abmelden(true); });
  $('avatar').addEventListener('click', function () { goSection('profil'); });
  $('b-lang').addEventListener('click', function () { S.langMenu = !S.langMenu; render(); });
  $$('#lang-menu [data-lang]').forEach(function (el) { el.addEventListener('click', function () { S.langMenu = false; sofort({ language: el.dataset.lang }, sprachWechsel); S.gateLang = el.dataset.lang; try { localStorage.setItem('fsh-ui-lang', el.dataset.lang); } catch (e) {} }); });
  $$('[data-gate-lang]').forEach(function (b) { b.addEventListener('click', function () { S.gateLang = b.dataset.gateLang; try { localStorage.setItem('fsh-ui-lang', S.gateLang); } catch (e) {} render(); }); });
  $('b-theme').addEventListener('click', function () { sofort({ dark: !S.draft.dark }); });
  $('b-settings').addEventListener('click', function () { goSection(S.section); });
  $('b-help').addEventListener('click', function () { S.help = !S.help; S.langMenu = false; render(); });
  $('help-from-info').addEventListener('click', function () { S.help = true; render(); });
  $('drawer-close').addEventListener('click', function () { S.help = false; render(); });
  $('drawer-scrim').addEventListener('click', function () { S.help = false; render(); });
  $$('[data-go]').forEach(function (el) { el.addEventListener('click', function () { if (!S.user) { showGateHinweis(); return; } goSection(el.dataset.go); }); });
  function showGateHinweis() { alert && void 0; }

  function sofort(aenderung, danach) {
    Object.assign(S.draft, aenderung); render();
    api('PATCH', '/api/ich/einstellungen', aenderung).then(function (d) { Object.assign(S.saved, d.einstellungen); Object.assign(S.draft, aenderung); render(); if (danach) danach(); }).catch(function (err) { showToast(err.message); });
  }

  // ------------------------------------------------------------ Einstellungen
  $('back-main').addEventListener('click', function () { var n = changes().length; go('main'); if (n) showToast(n === 1 ? t('nicht_gespeichert_1') : t('nicht_gespeichert_n', { n: n })); });
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
    p.then(function () { var neu = einst.language; S.busy = false; S.sheet = false; S.draft = Object.assign({}, S.saved); render(); showToast(t('gespeichert')); if (neu) { S.gateLang = neu; try { localStorage.setItem('fsh-ui-lang', neu); } catch (e) {} sprachWechsel(); } })
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
      .then(function () { S.busy = false; $('modal-pwd').hidden = true; $('f-pwd').reset(); render(); showToast(t('common.save')); ladeSitzungen(); })
      .catch(function (err) { S.busy = false; render(); zeigeFehler('pwd-err', err.message); });
  });
  function ladeSitzungen() {
    api('GET', '/api/ich/sitzungen').then(function (d) {
      var el = $('sess-list');
      el.innerHTML = d.sitzungen.map(function (s) {
        return '<div class="sess"><div class="kv"><b class="sm" style="font-weight:500">' + esc(s.geraet || t('unbekanntes_geraet')) + '</b><span class="cap">' + esc(t('angemeldet_bis', { von: fmtDatum(s.erstellt), bis: fmtDatum(s.ablauf) })) + '</span></div>' +
          (s.aktuell ? '<span class="cap" style="color:var(--success)">' + esc(t('diese_sitzung')) + '</span>' : '<button class="btn-link" data-sess="' + esc(s.id) + '">' + esc(t('abmelden')) + '</button>') + '</div>';
      }).join('') || '<span class="muted sm">' + esc(t('keine_sitzungen')) + '</span>';
      $$('[data-sess]', el).forEach(function (b) { b.addEventListener('click', function () { api('DELETE', '/api/ich/sitzungen/' + b.dataset.sess).then(ladeSitzungen); }); });
    }).catch(function () {});
  }

  // Verwaltung
  function ladeBenutzer() {
    if (!S.user || S.user.rolle !== 'admin') return;
    api('GET', '/api/benutzer').then(function (d) {
      var st = { aktiv: ['g', t('st_aktiv')], einmal: ['y', t('st_einmal')], gesperrt: ['r', t('st_gesperrt')] };
      $('users-tbody').innerHTML = d.benutzer.map(function (u) {
        var s = st[u.status] || ['', u.status];
        var selbst = u.id === S.user.id;
        var fremderInhaber = u.inhaber && !selbst;
        var aktion = fremderInhaber ? '<span class="cap">' + esc(t('common.owner_only')) + '</span>' : '<button class="btn-link" data-otp="' + u.id + '">' + esc(t('app.set.ver.otp')) + '</button>' +
          (selbst || u.status === 'einmal' ? '' : ' · <button class="btn-link" data-status="' + u.id + '" data-neu="' + (u.status === 'gesperrt' ? 'aktiv' : 'gesperrt') + '">' + esc(t(u.status === 'gesperrt' ? 'common.unlock' : 'common.lock')) + '</button>') +
          (S.user.inhaber && !selbst ? ' · <button class="btn-link" data-del-user="' + u.id + '" data-name="' + esc(u.name) + '" data-email="' + esc(u.email) + '" data-n="' + (u.pruefungen || 0) + '">' + esc(t('common.delete')) + '</button>' : '');
        var rolle = t(u.inhaber ? 'rolle_inhaber' : u.rolle === 'admin' ? 'rolle_admin' : 'rolle_mitglied');
        return '<tr><td data-l="' + esc(t('app.set.ver.table.name')) + '" style="font-weight:500">' + esc(u.name) + (selbst ? ' <span class="cap">' + esc(t('common.you')) + '</span>' : '') + '</td><td data-l="' + esc(t('app.set.ver.table.email')) + '" class="muted">' + esc(u.email) + '</td><td data-l="' + esc(t('app.set.ver.table.role')) + '">' + esc(rolle) + '</td><td data-l="' + esc(t('app.set.ver.table.status')) + '"><span class="tick"><span class="dot ' + s[0] + '"></span>' + esc(s[1]) + '</span></td><td data-l="' + esc(t('app.set.ver.table.act')) + '">' + aktion + '</td></tr>';
      }).join('');
      $('users-hint').textContent = t(S.user.inhaber ? 'app.set.ver.sub' : 'app.set.ver.sub');
      $$('[data-del-user]').forEach(function (b) { b.addEventListener('click', function () {
        S.delUser = b.dataset.delUser; zeigeFehler('del-err', '');
        var n = +b.dataset.n;
        $('del-text').textContent = t('common.delete_confirm', { name: b.dataset.name, email: b.dataset.email, pruefungen: n === 1 ? t('common.audit_1') : t('common.audit_n', { n: n }) });
        $('modal-del').hidden = false;
      }); });
      $$('[data-otp]').forEach(function (b) { b.addEventListener('click', function () {
        api('POST', '/api/benutzer/' + b.dataset.otp + '/einmal-passwort').then(function (r) { zeigeOtp(t('common.otp_new_text'), r.einmalPasswort); ladeBenutzer(); }).catch(function (err) { showToast(err.message); });
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
    api('DELETE', '/api/benutzer/' + S.delUser).then(function (r) { $('modal-del').hidden = true; showToast(t('konto_geloescht', { name: r.geloescht.name })); ladeBenutzer(); })
      .catch(function (err) { zeigeFehler('del-err', err.message); })
      .then(function () { $('del-go').disabled = false; });
  });
  $('user-copy').addEventListener('click', function () { var txt = $('user-otp').textContent; (navigator.clipboard ? navigator.clipboard.writeText(txt) : Promise.reject()).then(function () { showToast(t('kopiert')); }, function () { showToast(t('kopieren_hinweis')); }); });
  $('f-user').addEventListener('submit', function (e) {
    e.preventDefault(); zeigeFehler('user-err', '');
    api('POST', '/api/benutzer', { name: $('u-name').value.trim(), email: $('u-email').value.trim(), rolle: $('u-rolle').value })
      .then(function (r) { zeigeOtp(t('user_angelegt', { name: r.benutzer.name, tage: r.gueltigTage }), r.einmalPasswort); ladeBenutzer(); })
      .catch(function (err) { zeigeFehler('user-err', err.message); });
  });

  // ------------------------------------------------------------ Prüfung
  var SAETZE = ['basis', 'din', 'ce'];
  function ohneListe(runs) { return Object.keys(S.ohne).filter(function (id) { if (!S.ohne[id] || !S.punkte) return false; return runs.some(function (k) { return S.punkte[k] && S.punkte[k].punkte.some(function (p) { return p.id === id; }); }); }); }
  function renderPunkte(runs) {
    if (!S.punkte) return;
    var gesamt = 0, aktiv = 0;
    runs.forEach(function (k) { var ps = (S.punkte[k] || { punkte: [] }).punkte; gesamt += ps.length; aktiv += ps.filter(function (p) { return !S.ohne[p.id]; }).length; });
    var leer = runs.filter(function (k) { var ps = (S.punkte[k] || { punkte: [] }).punkte; return ps.length && ps.every(function (p) { return S.ohne[p.id]; }); });
    $('punkte-stand').textContent = leer.length ? t('app.check.loading.footer', { satz: leer.map(satzName).join(', ') }) : (aktiv === gesamt ? t('common.all', { n: gesamt }) : t('common.partial', { aktiv: aktiv, gesamt: gesamt, weg: gesamt - aktiv }));
    $('punkte-stand').style.color = leer.length ? 'var(--danger)' : '';
    $('punkte-toggle').textContent = t(S.punkteOffen ? 'common.close' : 'common.show');
    $('punkte').hidden = !S.punkteOffen;
    if (!S.punkteOffen) return;
    $('punkte').innerHTML = SAETZE.map(function (k) {
      var satz = S.punkte[k] || { punkte: [], vorhanden: false };
      var an = satz.punkte.filter(function (p) { return !S.ohne[p.id]; }).length;
      var zeilen = satz.punkte.map(function (p) {
        return '<button type="button" class="punkt" data-punkt="' + esc(p.id) + '" aria-pressed="' + (S.ohne[p.id] ? 'false' : 'true') + '"><span class="cb' + (S.ohne[p.id] ? '' : ' on') + '"><svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12l5 5 9-10"/></svg></span><span class="t"><span class="mono">' + esc(p.id) + '</span> ' + esc(p.bereichAnzeige || p.bereich) + ' <span class="cap">· ' + esc(p.klasseAnzeige || p.fehlerklasse) + ', ' + esc(t('common.weight', { n: p.gewichtung })) + '</span><br><span class="cap">' + esc(p.empfehlungAnzeige || p.empfehlung) + '</span></span></button>';
      }).join('');
      var kopf = '<div class="kopf"><b>' + esc(satzName(k)) + '</b><span class="cap">' + esc(satz.vorhanden ? t('common.of', { a: an, b: satz.punkte.length }) : t('common.file_missing')) + '</span></div>';
      var alle = satz.punkte.length ? '<div class="row" style="gap:8px"><button type="button" class="btn-link" data-alle="' + k + '" data-wert="1">' + esc(t('common.all_on')) + '</button><button type="button" class="btn-link" data-alle="' + k + '" data-wert="0">' + esc(t('common.all_off')) + '</button></div>' : '';
      return '<div class="satz' + (S.run[k] ? '' : ' aus') + '">' + kopf + zeilen + alle + '</div>';
    }).join('');
    $$('#punkte [data-punkt]').forEach(function (b) { b.addEventListener('click', function () { punktSetzen([b.dataset.punkt], !!S.ohne[b.dataset.punkt]); }); });
    $$('#punkte [data-alle]').forEach(function (b) { b.addEventListener('click', function () { punktSetzen(S.punkte[b.dataset.alle].punkte.map(function (p) { return p.id; }), b.dataset.wert === '1'); }); });
  }
  function punktSetzen(ids, aktiv) {
    ids.forEach(function (id) { if (aktiv) delete S.ohne[id]; else S.ohne[id] = true; });
    render();
    api('PUT', '/api/ich/pruefpunkte', { ausgelassen: Object.keys(S.ohne) }).catch(function (err) { showToast(err.message); });
  }
  function ladePunkte() {
    api('GET', '/api/regeln').then(function (d) {
      S.punkte = d.regelsaetze; S.ohne = {};
      (d.ausgelassen || []).forEach(function (id) { S.ohne[id] = true; });
      render();
    }).catch(function () {});
  }
  $('punkte-toggle').addEventListener('click', function () { S.punkteOffen = !S.punkteOffen; render(); });

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
    if (abgelehnt.length) showToast(t('common.only_docx', { liste: abgelehnt.join(', ') }));
    if (S.files.length > MAX_DATEIEN) { S.files = S.files.slice(0, MAX_DATEIEN); showToast(t('common.max_files', { n: MAX_DATEIEN })); }
    zeigeFehler('check-err', ''); render();
  }
  function dateiEntfernen(i) { if (S.busy) return; S.files.splice(i, 1); render(); }
  $('file').addEventListener('change', function () { setFiles(this.files); this.value = ''; });
  var drop = $('drop');
  ['dragenter', 'dragover'].forEach(function (ev) { drop.addEventListener(ev, function (e) { e.preventDefault(); drop.style.borderColor = 'var(--accent)'; }); });
  ['dragleave', 'drop'].forEach(function (ev) { drop.addEventListener(ev, function (e) { e.preventDefault(); drop.style.borderColor = ''; }); });
  drop.addEventListener('drop', function (e) { if (e.dataTransfer.files) setFiles(e.dataTransfer.files); });
  $$('[data-run]').forEach(function (el) { el.addEventListener('click', function () { S.run[el.dataset.run] = !S.run[el.dataset.run]; render(); }); });
  // Ein bis zwei Berichtssprachen: Klick schaltet um; bei zwei gewählten ersetzt die neue die ältere.
  $$('#seg-report-langs button').forEach(function (b) { b.addEventListener('click', function () {
    var v = b.dataset.v, i = S.reportLangs.indexOf(v);
    if (i >= 0) { if (S.reportLangs.length > 1) S.reportLangs.splice(i, 1); }
    else { S.reportLangs.push(v); if (S.reportLangs.length > 2) S.reportLangs.shift(); }
    try { localStorage.setItem('fsh-report-langs', JSON.stringify(S.reportLangs)); } catch (e) {}
    render();
  }); });

  // Statuspanel: erscheint erst nach 400 ms, damit kurze Prüfungen nicht aufblitzen.
  var PHASEN = ['lesen', 'pruefen', 'berichte'];
  function renderLauf() {
    var l = S.lauf;
    $('lauf').hidden = !(S.busy && S.laufSichtbar && l);
    if (!l) return;
    $('lauf-titel').textContent = l.dokumente > 1 ? t('lauf_titel_n', { i: l.dokument, n: l.dokumente }) : t('lauf_titel');
    $('lauf-datei').textContent = l.datei || '';
    var idx = PHASEN.indexOf(l.phase);
    $$('.lauf-phasen li').forEach(function (li, i) {
      li.classList.toggle('fertig', idx > i || l.phase === 'fertig');
      li.classList.toggle('aktiv', idx === i);
    });
    $('lauf-berichte').textContent = (l.phase === 'berichte' && l.von) ? t('bericht_n', { i: l.n, n: l.von }) : '';
  }
  function laufStart(datei, anzahl) {
    S.lauf = { phase: 'lesen', datei: datei, dokument: 1, dokumente: anzahl || 1, n: 0, von: 0 }; S.laufSichtbar = false;
    clearTimeout(S.laufTimer);
    S.laufTimer = setTimeout(function () { S.laufSichtbar = true; renderLauf(); }, 400);
  }
  function laufEnde() { clearTimeout(S.laufTimer); S.laufTimer = null; S.lauf = null; S.laufSichtbar = false; }

  // Die Prüfung schickt ihren Fortschritt als Zeilen (eine JSON-Zeile je Phase, zuletzt Ergebnis oder Fehler).
  function pruefungStreamen(fd) {
    return fetch('/api/pruefung', { method: 'POST', credentials: 'same-origin', headers: { 'X-Sprache': uiLang() }, body: fd }).then(function (r) {
      if (r.status === 401) { abmelden(false); throw new Error(t('common.login_missing')); }
      if (!r.ok) {
        return r.text().then(function (txt) { var d = {}; try { d = JSON.parse(txt); } catch (e) {} throw new Error(d.fehler || t('common.error_status', { status: r.status })); });
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
        return r.text().then(function (txt) { var erg = null; txt.split('\n').forEach(function (z) { var x = verarbeiten(z); if (x) erg = x; }); if (!erg) throw new Error(t('unerwartet')); return erg; });
      }
      var reader = r.body.getReader(), dec = new TextDecoder(), rest = '';
      return new Promise(function (resolve, reject) {
        function weiter() {
          reader.read().then(function (st) {
            try {
              if (st.done) {
                var x = verarbeiten(rest); if (x) { resolve(x); } else { reject(new Error(t('unerwartet'))); }
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
    var runs = Object.keys(S.run).filter(function (k) { return S.run[k]; });
    fd.append('regelsaetze', runs.join(','));
    fd.append('ausgelassen', ohneListe(runs).join(','));
    fd.append('sprachen', S.reportLangs.join(','));
    fd.append('fortschritt', '1');
    pruefungStreamen(fd).then(function (lauf) {
      laufEnde(); S.busy = false; render();
      if (!lauf.ergebnisse.length) { zeigeFehler('check-err', (lauf.fehler[0] && lauf.fehler[0].fehler) || t('common.audit_failed')); return; }
      S.laufErg = lauf; S.result = lauf.ergebnisse[0];
      zeigeLauf(lauf); zeigeErgebnis(S.result); ladePruefungen();
      showPop(laufSatz(lauf));
    }).catch(function (err) { laufEnde(); S.busy = false; render(); zeigeFehler('check-err', err.message); });
  });
  function laufSatz(lauf) {
    if (lauf.dateien === 1) { var r = lauf.ergebnisse[0]; return t('common.pop_done_1', { datei: r.dateiname, score: r.score, ampel: AMPEL_FARBE[r.ampel] ? t('common.short_' + r.ampel) : r.ampel, n: r.pdfs.length }); }
    var z = { gruen: 0, gelb: 0, rot: 0 }; lauf.ergebnisse.forEach(function (r) { if (z[r.ampel] !== undefined) z[r.ampel]++; });
    var s = t('common.pop_done_n', { n: lauf.ergebnisse.length, g: z.gruen, y: z.gelb, r: z.rot });
    if (lauf.fehler.length) s += ' ' + (lauf.fehler.length === 1 ? t('common.not_readable_1') : t('common.not_readable_n', { n: lauf.fehler.length }));
    return s + ' ' + t('common.pdfs_ready', { n: lauf.pdfAnzahl });
  }
  function zeigeLauf(lauf, nurNeuZeichnen) {
    var mehrere = lauf.dateien > 1;
    $('lauf-ergebnis').hidden = !mehrere;
    if (!mehrere) return;
    $('lauf-meta').textContent = t('common.audit_meta', { n: lauf.ergebnisse.length, gesamt: lauf.dateien, pdfs: lauf.pdfAnzahl });
    var zeilen = lauf.ergebnisse.map(function (r) {
      var a = ampel(r.ampel);
      return '<tr><td data-l="' + esc(t('app.res.funde.table.dokument')) + '" class="doc" style="font-weight:500">' + esc(r.dateiname) + '</td><td data-l="' + esc(t('app.res.funde.table.score')) + '" class="mono">' + r.score + ' %</td><td data-l="' + esc(t('app.res.funde.table.ampel')) + '"><span class="tick"><span class="dot ' + a[0] + '"></span>' + esc(a[1]) + '</span></td><td data-l="' + esc(t('app.res.funde.table.funde')) + '">' + r.fundeAnzahl + '</td><td data-l="' + esc(t('app.res.funde.table.aufwand')) + '" class="mono">' + String(r.stunden).replace('.', ',') + ' h</td><td data-l="' + esc(t('app.res.funde.table.berichte')) + '"><button class="btn-link" data-zeige="' + esc(r.id) + '">' + esc(t('common.view')) + '</button></td></tr>';
    }).concat(lauf.fehler.map(function (f) {
      return '<tr><td data-l="' + esc(t('app.res.funde.table.dokument')) + '" class="doc" style="font-weight:500">' + esc(f.datei) + '</td><td colspan="5" class="muted" data-l="' + esc(t('app.res.funde.table.hinweis')) + '">' + esc(t('common.not_audited', { grund: f.fehler })) + '</td></tr>';
    }));
    $('lauf-tbody').innerHTML = zeilen.join('');
    $$('#lauf-tbody [data-zeige]').forEach(function (b) { b.addEventListener('click', function () { var r = lauf.ergebnisse.filter(function (x) { return x.id === b.dataset.zeige; })[0]; if (r) { S.result = r; zeigeErgebnis(r); } }); });
    $('lauf-zip').href = lauf.zip;
  }
  $('lauf-store').addEventListener('click', function () {
    if (!S.laufErg || !S.laufErg.ablegen) return;
    api('POST', S.laufErg.ablegen).then(function (r) { showToast(t('abgelegt_lauf', { n: r.abgelegt.length, d: r.dokumente, ordner: String(r.ordner).split('/').pop() || 'output' })); }).catch(function (err) { showToast(err.message); });
  });

  function zeigeErgebnis(r, nurNeuZeichnen) {
    var a = ampel(r.ampel);
    $('res-meta').textContent = r.dateiname + ' · ' + fmtDatum(r.erstellt);
    $('res-score').textContent = r.score + ' %';
    $('res-ampel').innerHTML = '<span class="dot ' + a[0] + '"></span>' + esc(a[1]);
    $('res-regeln').textContent = r.regelsaetze.map(satzName).join(', ') + (r.punkteGesamt ? ' · ' + t('punkte_von', { a: r.punkteGeprueft, b: r.punkteGesamt }) : '');
    var weg = r.ausgelassen || [];
    $('res-ausgelassen').hidden = !weg.length; $('res-ausgelassen').textContent = weg.length ? t('ausgelassen_lbl', { liste: weg.map(function (x) { return x.id + ' ' + x.bereich; }).join(', ') }) : '';
    var kl = r.klassen || {};
    var teile = [];
    if (kl.Kritisch) teile.push(t('kl_kritisch', { n: kl.Kritisch })); if (kl.Schwer) teile.push(t('kl_schwer', { n: kl.Schwer })); if (kl.Mittel) teile.push(t('kl_mittel', { n: kl.Mittel })); if (kl.Gering) teile.push(t('kl_gering', { n: kl.Gering }));
    $('res-funde').textContent = r.fundeAnzahl + (teile.length ? ' · ' + teile.join(', ') : '');
    $('res-aufwand').textContent = String(r.stunden).replace('.', ',') + ' h';
    $('res-langs').textContent = r.sprachen.map(langName).join(t('common.and'));
    $('res-fazit').textContent = r.fazit;
    var hinweise = r.lesehinweise || [];
    $('res-hinweise').hidden = !hinweise.length; $('res-hinweise').textContent = hinweise.length ? t('lesehinweis', { text: hinweise.join(' ') }) : '';
    var btn = function (art) { return r.pdfs.filter(function (p) { return p.bericht === art; }).map(function (p) { return '<a class="btn" href="' + esc(p.url) + '" target="_blank" rel="noopener">' + esc(t('common.pdf', { lang: LANGS[p.sprache] || p.sprache })) + '</a>'; }).join(''); };
    $('pdf-pruef').innerHTML = btn('pruef'); $('pdf-fach').innerHTML = btn('fach');
    $('zip-label').textContent = t('common.n_pdfs', { n: r.pdfs.length });
    $('act-zip').href = r.zip;
    $('res-n').textContent = r.fundeAnzahl;
    $('res-tbody').innerHTML = (r.funde || []).map(function (f) {
      var k = KLASSE[f.Fehlerklasse]; var klasse = f.klasseAnzeige || f.Fehlerklasse; var kz = k ? '<span class="tick"><span class="dot ' + k + '"></span>' + esc(klasse) + '</span>' : esc(klasse);
      return '<tr><td data-l="' + esc(t('app.res.funde.table.id')) + '" class="mono">' + esc(f.ID) + '</td><td data-l="' + esc(t('app.res.funde.table.bereich')) + '">' + esc(f.bereichAnzeige || f.Bereich) + '</td><td data-l="' + esc(t('app.res.funde.table.klasse')) + '">' + kz + '</td><td data-l="' + esc(t('app.res.funde.table.bewertung')) + '">' + esc(f.bewertungAnzeige || f.Bewertung) + '</td><td data-l="' + esc(t('app.res.funde.table.empfehlung')) + '">' + esc(f.empfehlungAnzeige || f.Empfehlung) + '</td></tr>';
    }).join('') || '<tr><td colspan="5" class="muted">' + esc(t('app.res.funde.empty')) + '</td></tr>';
    $('result').hidden = false;
    if (!nurNeuZeichnen) (S.laufErg && S.laufErg.dateien > 1 ? $('res-detail') : $('result')).scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  function ladePruefungen() {
    api('GET', '/api/pruefungen').then(function (d) {
      $('list-tbody').innerHTML = d.pruefungen.map(function (p) {
        var a = ampel(p.ampel);
        return '<tr><td data-l="' + esc(t('th_datum')) + '" class="mono">' + esc(fmtDatum(p.erstellt)) + '</td><td data-l="' + esc(t('th_dokument')) + '" class="doc">' + esc(p.dateiname) + '</td><td data-l="' + esc(t('th_score')) + '" class="mono">' + p.score + ' %</td><td data-l="' + esc(t('th_ampel')) + '"><span class="tick"><span class="dot ' + a[0] + '"></span>' + esc(a[1]) + '</span></td><td data-l="' + esc(t('th_berichte')) + '"><button class="btn-link" data-open="' + esc(p.id) + '">' + esc(t('oeffnen')) + '</button></td></tr>';
      }).join('') || '<tr><td colspan="5" class="muted">' + esc(t('noch_keine')) + '</td></tr>';
      $$('[data-open]').forEach(function (b) { b.addEventListener('click', function () { api('GET', '/api/pruefung/' + b.dataset.open).then(function (r) { S.result = r; S.laufErg = null; $('lauf-ergebnis').hidden = true; zeigeErgebnis(r); }).catch(function (err) { showToast(err.message); }); }); });
    }).catch(function () {});
  }
  $('pop-close').addEventListener('click', hidePop);
  $('pop-open').addEventListener('click', function () { hidePop(); if (S.result) { $('result').hidden = false; $('result').scrollIntoView({ behavior: 'smooth', block: 'start' }); } });
  $('pop-demo').addEventListener('click', function () { showPop(t('pop_demo_text'), true); });
  $('act-store').addEventListener('click', function () { if (!S.result) return; api('POST', '/api/pruefung/' + S.result.id + '/ablegen').then(function (r) { showToast(t('abgelegt', { n: r.abgelegt.length, ordner: String(r.ordner).split('/').pop() || 'output' })); }).catch(function (err) { showToast(err.message); }); });
  $('act-done').addEventListener('click', function () { S.result = null; S.laufErg = null; S.files = []; $('file').value = ''; $('result').hidden = true; $('lauf-ergebnis').hidden = true; render(); window.scrollTo({ top: 0, behavior: 'smooth' }); showToast(t('pruefung_abgeschlossen')); });
  $('act-mail').addEventListener('click', function () { if (!S.result) return; $('mail-sub').textContent = t('mail_sub', { datei: S.result.dateiname, langs: S.result.sprachen.map(langName).join(t('und')) }); $('mail-text').hidden = true; $('mail-copy').hidden = true; zeigeFehler('mail-err', ''); $('modal-mail').hidden = false; });
  $('mail-close').addEventListener('click', function () { $('modal-mail').hidden = true; });
  $('mail-go').addEventListener('click', function () {
    api('POST', '/api/pruefung/' + S.result.id + '/mail-entwurf', { an: $('mail-an').value.trim() }).then(function (r) {
      if (r.entwurf === 'mail') { $('modal-mail').hidden = true; showToast(t('common.mail_ok', { n: r.anhaenge.length })); }
      else { $('mail-text').hidden = false; $('mail-text').textContent = t('common.subject') + r.betreff + '\n\n' + r.text + '\n\n' + t('common.attachments') + r.anhaenge.join(', '); $('mail-copy').hidden = false; }
    }).catch(function (err) { zeigeFehler('mail-err', err.message); });
  });
  $('mail-copy').addEventListener('click', function () { var txt = $('mail-text').textContent; (navigator.clipboard ? navigator.clipboard.writeText(txt) : Promise.reject()).then(function () { showToast(t('kopiert')); }, function () { showToast(t('kopieren_hinweis')); }); });

  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { S.langMenu = false; S.help = false; S.sheet = false; $('modal-pwd').hidden = true; $('modal-user').hidden = true; $('modal-del').hidden = true; $('modal-mail').hidden = true; render(); } });
  document.addEventListener('click', function (e) { if (S.langMenu && !e.target.closest('.menu-wrap')) { S.langMenu = false; render(); } });

  window.__t = t;
  boot();
})();
