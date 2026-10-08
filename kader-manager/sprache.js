/* Kader-Manager – Oberflächentexte. Sprache kommt aus team.language in daten/kader.json ("de" oder "uk"),
   per ?lang=uk überschreibbar. Positionen und Namen stehen in den Daten und werden nicht übersetzt. */
export const TEXTE = {
  de: {
    saison: 'Saison', laden: 'Kader wird geladen …', keineSpieler: 'Keine Spieler im Kader.', ladefehler: 'Kader konnte nicht geladen werden',
    antippen: 'Trikot antippen', alle: 'Alle', kaderBlatt: 'Kader<br>Blatt', zurueck: 'Zurück zur Stange', vorher: 'Vorheriger Spieler', weiter: 'Nächster Spieler',
    einklappen: 'Details einklappen', ausklappen: 'Details ausklappen', linkKopieren: 'Link kopieren', kopiert: 'Kopiert', nationalitaet: 'Nationalität',
    status: 'Status', jahrgang: 'Jahrgang', spiele: 'Spiele', tore: 'Tore', assists: 'Assists', strafzeiten: 'Strafzeiten', profil: 'Profil',
    rueckennummer: 'Rückennummer', foto: 'Foto von', trikotOeffnen: 'Trikot öffnen', nummer: 'Nummer', links: 'Trikots nach links bewegen', rechts: 'Trikots nach rechts bewegen',
    positionFilter: 'Nach Position filtern', heim: 'Heim', auswaerts: 'Auswärts', trikotwahl: 'Trikot', lokal: 'Lokale Admin-Änderungen, noch nicht veröffentlicht.', veroeffentlicht: 'Veröffentlichten Stand zeigen',
    admin: 'Admin-Bereich', statusWerte: { active: 'Aktiv', injured: 'Verletzt', inactive: 'Deaktiviert' }
  },
  uk: {
    saison: 'Сезон', laden: 'Завантаження складу …', keineSpieler: 'У складі немає гравців.', ladefehler: 'Не вдалося завантажити склад',
    antippen: 'Торкніться футболки', alle: 'Усі', kaderBlatt: 'Склад<br>команди', zurueck: 'Назад до вішалки', vorher: 'Попередній гравець', weiter: 'Наступний гравець',
    einklappen: 'Згорнути деталі', ausklappen: 'Розгорнути деталі', linkKopieren: 'Копіювати посилання', kopiert: 'Скопійовано', nationalitaet: 'Громадянство',
    status: 'Статус', jahrgang: 'Рік народження', spiele: 'Матчі', tore: 'Голи', assists: 'Передачі', strafzeiten: 'Штрафні хвилини', profil: 'Профіль',
    rueckennummer: 'Ігровий номер', foto: 'Фото', trikotOeffnen: 'Відкрити футболку', nummer: 'Номер', links: 'Прокрутити вліво', rechts: 'Прокрутити вправо',
    positionFilter: 'Фільтр за позицією', heim: 'Домашня', auswaerts: 'Виїзна', trikotwahl: 'Футболка', lokal: 'Локальні зміни адміністратора, ще не опубліковані.', veroeffentlicht: 'Показати опубліковану версію',
    admin: 'Адміністрування', statusWerte: { active: 'Активний', injured: 'Травмований', inactive: 'Деактивований' }
  }
};

export function spracheWaehlen(team) {
  const wunsch = new URLSearchParams(location.search).get('lang');
  const code = TEXTE[wunsch] ? wunsch : (TEXTE[team?.language] ? team.language : 'de');
  document.documentElement.lang = code;
  return { code, t: TEXTE[code] };
}
