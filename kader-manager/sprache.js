/* Kader-Manager – Oberflächentexte. Sprache: ?lang=uk|de vor gemerkter Wahl (localStorage) vor team.language.
   Spielernamen: Feld nameUk (ukrainische Schreibweise) wird in der ukrainischen Ansicht verwendet, sonst name.
   Positionen: die vier Standardpositionen werden übersetzt, andere stehen so in den Daten wie eingetragen. */
export const TEXTE = {
  de: {
    saison: 'Saison', laden: 'Kader wird geladen …', keineSpieler: 'Keine Spieler im Kader.', ladefehler: 'Kader konnte nicht geladen werden',
    antippen: 'Trikot antippen', alle: 'Alle', kaderBlatt: 'Kader<br>Blatt', zurueck: 'Zurück zur Stange', vorher: 'Vorheriger Spieler', weiter: 'Nächster Spieler',
    einklappen: 'Details einklappen', ausklappen: 'Details ausklappen', linkKopieren: 'Link kopieren', kopiert: 'Kopiert', nationalitaet: 'Nationalität',
    status: 'Status', jahrgang: 'Jahrgang', spiele: 'Spiele', tore: 'Tore', assists: 'Assists', strafzeiten: 'Strafzeiten', profil: 'Profil',
    rueckennummer: 'Rückennummer', foto: 'Foto von', trikotOeffnen: 'Trikot öffnen', nummer: 'Nummer', links: 'Trikots nach links bewegen', rechts: 'Trikots nach rechts bewegen',
    positionFilter: 'Nach Position filtern', heim: 'Heim', auswaerts: 'Auswärts', trikotwahl: 'Trikot', lokal: 'Lokale Admin-Änderungen, noch nicht veröffentlicht.', veroeffentlicht: 'Veröffentlichten Stand zeigen',
    admin: 'Admin-Bereich', sprache: 'Sprache', statusWerte: { active: 'Aktiv', injured: 'Verletzt', inactive: 'Deaktiviert' },
    positionen: { Torwart: 'Torwart', Verteidiger: 'Verteidiger', Center: 'Center', 'Stürmer': 'Stürmer' }
  },
  uk: {
    saison: 'Сезон', laden: 'Завантаження складу …', keineSpieler: 'У складі немає гравців.', ladefehler: 'Не вдалося завантажити склад',
    antippen: 'Торкніться футболки', alle: 'Усі', kaderBlatt: 'Склад<br>команди', zurueck: 'Назад до вішалки', vorher: 'Попередній гравець', weiter: 'Наступний гравець',
    einklappen: 'Згорнути деталі', ausklappen: 'Розгорнути деталі', linkKopieren: 'Копіювати посилання', kopiert: 'Скопійовано', nationalitaet: 'Громадянство',
    status: 'Статус', jahrgang: 'Рік народження', spiele: 'Матчі', tore: 'Голи', assists: 'Передачі', strafzeiten: 'Штрафні хвилини', profil: 'Профіль',
    rueckennummer: 'Ігровий номер', foto: 'Фото', trikotOeffnen: 'Відкрити футболку', nummer: 'Номер', links: 'Прокрутити вліво', rechts: 'Прокрутити вправо',
    positionFilter: 'Фільтр за позицією', heim: 'Домашня', auswaerts: 'Виїзна', trikotwahl: 'Футболка', lokal: 'Локальні зміни адміністратора, ще не опубліковані.', veroeffentlicht: 'Показати опубліковану версію',
    admin: 'Адміністрування', sprache: 'Мова', statusWerte: { active: 'Активний', injured: 'Травмований', inactive: 'Деактивований' },
    positionen: { Torwart: 'Воротар', Verteidiger: 'Захисник', Center: 'Центральний', 'Stürmer': 'Нападник' }
  }
};
export const SPRACHEN = [['de', 'DE', 'Deutsch'], ['uk', 'UK', 'Українська']];
const MERKER = 'kaderManager.sprache';

export function spracheWaehlen(team) {
  const wunsch = new URLSearchParams(location.search).get('lang');
  let gemerkt = null;
  try { gemerkt = localStorage.getItem(MERKER); } catch { /* kein Speicher */ }
  const code = TEXTE[wunsch] ? wunsch : (TEXTE[gemerkt] ? gemerkt : (TEXTE[team?.language] ? team.language : 'de'));
  document.documentElement.lang = code;
  return { code, t: TEXTE[code] };
}

/** Sprache merken und die Seite mit ?lang= neu laden (Hash mit #spieler= bleibt erhalten). */
export function spracheSetzen(code) {
  if (!TEXTE[code]) return;
  try { localStorage.setItem(MERKER, code); } catch { /* kein Speicher */ }
  const url = new URL(location.href);
  url.searchParams.set('lang', code);
  location.href = url.href;
}

/** Anzeigename eines Spielers in der gewählten Sprache. Ohne eingetragenes nameUk wird der lateinische
    Name automatisch in ukrainische Schreibweise umgesetzt. */
export function anzeigeName(spieler, code) {
  if (code !== 'uk') return spieler.name;
  return spieler.nameUk || transliterieren(spieler.name, spieler.nationality);
}

/* ---------- Automatische Umschrift Lateinisch → Ukrainisch (kyrillisch) ----------
   Standardweg: Umkehrung der amtlichen ukrainischen Romanisierung (Kabinettsbeschluss 2010), z. B.
   Oleh → Олег, Yurii → Юрій, Polishchuk → Поліщук, Kravets → Кравець, Vasyl → Василь.
   Bei Nationalität DE/AT/CH gelten deutsche Leseregeln, z. B. Jan Jenner → Ян Єннер, Schmidt → Шмідт.
   Es ist ein Vorschlag: die Schreibweise, die ein Spieler selbst verwendet, hat Vorrang (Feld nameUk). */
const VOKALE = 'aeiouy';
const UK_REGELN = [
  ['tskyi', 'цький'], ['skyi', 'ський'], ['shch', 'щ'], ['zgh', 'зг'], ['kh', 'х'], ['ts', 'ц'], ['ch', 'ч'], ['sh', 'ш'], ['zh', 'ж'],
  ['yu', 'ю'], ['ya', 'я'], ['ye', 'є'], ['yi', 'ї'], ['iu', 'ю'], ['ia', 'я'], ['ie', 'є'],
  ['a', 'а'], ['b', 'б'], ['v', 'в'], ['h', 'г'], ['g', 'ґ'], ['d', 'д'], ['e', 'е'], ['z', 'з'], ['y', 'и'], ['i', 'і'],
  ['k', 'к'], ['l', 'л'], ['m', 'м'], ['n', 'н'], ['o', 'о'], ['p', 'п'], ['r', 'р'], ['s', 'с'], ['t', 'т'], ['u', 'у'], ['f', 'ф'],
  ['w', 'в'], ['x', 'кс'], ['c', 'к'], ['j', 'й'], ['q', 'к'], ["'", ''], ['’', '']
];
const DE_REGELN = [
  ['tsch', 'ч'], ['sch', 'ш'], ['tz', 'ц'], ['ck', 'к'], ['ch', 'х'], ['ph', 'ф'], ['th', 'т'], ['qu', 'кв'], ['ss', 'с'], ['ß', 'с'],
  ['ei', 'ай'], ['ai', 'ай'], ['eu', 'ой'], ['äu', 'ой'], ['ie', 'і'], ['ja', 'я'], ['je', 'є'], ['jo', 'йо'], ['ju', 'ю'], ['ä', 'е'], ['ö', 'е'], ['ü', 'ю'],
  ['a', 'а'], ['b', 'б'], ['c', 'к'], ['d', 'д'], ['e', 'е'], ['f', 'ф'], ['g', 'ґ'], ['h', 'г'], ['i', 'і'], ['j', 'й'], ['k', 'к'], ['l', 'л'], ['m', 'м'],
  ['n', 'н'], ['o', 'о'], ['p', 'п'], ['r', 'р'], ['s', 'з'], ['t', 'т'], ['u', 'у'], ['v', 'ф'], ['w', 'в'], ['x', 'кс'], ['y', 'і'], ['z', 'ц']
];
export function transliterieren(name, nationalitaet = '') {
  const deutsch = /^(DE|AT|CH)$/i.test(nationalitaet || '');
  const regeln = deutsch ? DE_REGELN : UK_REGELN;
  return String(name || '').split(/(\s+|-)/).map(wort => /^(\s+|-)$/.test(wort) ? wort : wortUmsetzen(wort, regeln, deutsch)).join('');
}
function wortUmsetzen(wort, regeln, deutsch) {
  const klein = wort.toLowerCase();
  let aus = '';
  for (let i = 0; i < klein.length;) {
    const rest = klein.slice(i);
    const treffer = regeln.find(([lat]) => rest.startsWith(lat));
    if (!treffer) { aus += wort[i]; i += 1; continue; }
    let [lat, kyr] = treffer;
    const davor = klein[i - 1] || '', danach = klein[i + lat.length] || '';
    const amAnfang = i === 0, amEnde = i + lat.length >= klein.length;
    if (!deutsch) {
      if (lat === 'y' && amAnfang && VOKALE.includes(danach)) kyr = 'й';                       // Yosyp → Йосип
      if (lat === 'i' && davor && VOKALE.includes(davor) && (amEnde || !VOKALE.includes(danach))) kyr = 'й';   // Andrii → Андрій, Mykhailo → Михайло
      if (lat === 'yi' && !amAnfang) kyr = 'ий';                                                 // Zabarnyi → Забарний
      if (lat === 'l' && danach === 'l') kyr = 'л';                                               // Illia → Ілля
      if (lat === 'e' && amAnfang) kyr = 'е';
      if (lat === 'l' && (amEnde || (danach && !VOKALE.includes(danach) && danach !== 'l' && danach !== "'" && danach !== '’'))) kyr = 'ль';   // Vasyl, Melnyk
      if (lat === 'ts' && amEnde && davor === 'e') kyr = 'ць';                                 // Kravets → Кравець
      if (lat === 's' && amEnde && (davor === 'ы' || false)) kyr = 'с';
    } else {
      if (lat === 's' && (amEnde || (danach && !VOKALE.includes(danach)))) kyr = 'с';          // Hans, Jens
      if (lat === 'h' && !amAnfang && VOKALE.includes(davor)) kyr = '';                        // Dehnungs-h: Kahl → Каль wird unten
      if (lat === 'l' && amEnde) kyr = 'ль';                                                   // Kahl → Каль
      if (lat === 'e' && amEnde && klein.length > 3) kyr = 'е';
      if (lat === 'ie' && amEnde) kyr = 'і';
      if (lat === 'eu' && amAnfang) kyr = 'ой';
    }
    // Großschreibung übernehmen (nur erster Buchstabe des Treffers)
    if (wort[i] !== klein[i] && kyr) kyr = kyr[0].toUpperCase() + kyr.slice(1);
    aus += kyr;
    i += lat.length;
  }
  return aus;
}
/** Position in der gewählten Sprache (Standardpositionen übersetzt, sonst unverändert). */
export function anzeigePosition(position, code) {
  return TEXTE[code]?.positionen?.[position] ?? position;
}
/** Profiltext in der gewählten Sprache. */
export function anzeigeBio(spieler, code) {
  return (code === 'uk' && spieler.bioUk) ? spieler.bioUk : spieler.bio;
}
