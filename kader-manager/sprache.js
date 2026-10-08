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

/** Anzeigename eines Spielers in der gewählten Sprache. */
export function anzeigeName(spieler, code) {
  return (code === 'uk' && spieler.nameUk) ? spieler.nameUk : spieler.name;
}
/** Position in der gewählten Sprache (Standardpositionen übersetzt, sonst unverändert). */
export function anzeigePosition(position, code) {
  return TEXTE[code]?.positionen?.[position] ?? position;
}
/** Profiltext in der gewählten Sprache. */
export function anzeigeBio(spieler, code) {
  return (code === 'uk' && spieler.bioUk) ? spieler.bioUk : spieler.bio;
}
