"""Texte der PDF-Berichte in Deutsch, Englisch, Ukrainisch und Russisch.

Deutsch ist die Quelle. Englisch, Ukrainisch und Russisch sind Erstübersetzungen
und sollten vor dem ersten Kundenversand von einer sprachkundigen Person gegengelesen werden.
"""
from __future__ import annotations

TEXTE: dict[str, dict[str, str]] = {
    "de": {
        "titel_pruef": "Prüfbericht",
        "titel_fach": "Fachbericht",
        "untertitel_pruef": "Interner Bericht für das Prüfteam",
        "untertitel_fach": "Bericht für den Auftraggeber",
        "dokument": "Dokument",
        "datum": "Datum der Prüfung",
        "geprueft_von": "Geprüft von",
        "regelsaetze": "Regelsätze",
        "bewertung": "Suchscore",
        "ampel": "Ampel",
        "aufwand": "Geschätzter Aufwand",
        "stunden": "h",
        "funde_anzahl": "Prüfhinweise",
        "fazit": "Fazit der Vorprüfung",
        "todo": "To-do-Liste (CE-Konformität)",
        "massnahmen": "Empfohlene Maßnahmen",
        "funde": "Prüfergebnisse im Einzelnen",
        "keine_funde": "Keine weiteren automatischen Hinweise. Die fachliche Prüfung bleibt offen.",
        "keine_todos": "Keine zusätzlichen CE-Suchhinweise. Daraus folgt keine Aussage zur CE-Konformität.",
        "keine_massnahmen": "Keine zusätzlichen Maßnahmen aus der Suchprüfung. Fachliche Maßnahmen bleiben zu prüfen.",
        "sp_id": "ID",
        "sp_normlogik": "Normlogik",
        "sp_bereich": "Bereich",
        "sp_pflicht": "Pflicht",
        "sp_klasse": "Fehlerklasse",
        "sp_bewertung": "Bewertung",
        "sp_fundstelle": "Fundstelle",
        "sp_empfehlung": "Empfehlung",
        "sp_gewichtung": "Gew.",
        "sp_minuten": "Min.",
        "sp_massnahme": "Maßnahme",
        "sp_prioritaet": "Priorität",
        "sp_aufwand_h": "Aufwand (h)",
        "ampel_gruen": "Altbewertung · erneut prüfen",
        "ampel_gelb": "Gelb · fachlich offen",
        "ampel_rot": "Rot · dringender Prüfbedarf",
        "fazit_rot": "Kritische oder umfangreiche Prüfhinweise sind offen. Eine fachliche Bewertung ist erforderlich.",
        "fazit_gelb": "Die automatische Vorprüfung ist abgeschlossen. Die fachliche Bewertung bleibt offen.",
        "fazit_gruen": "Historische Bewertung. Bitte erneut prüfen; eine fachliche Freigabe ist daraus nicht ableitbar.",
        "kritisch_1": "1 als kritisch eingestufter Prüfhinweis ist offen.",
        "kritisch_n": "{n} als kritisch eingestufte Prüfhinweise sind offen.",
        "schwer_1": "1 als schwerwiegend eingestufter Prüfhinweis ist offen.",
        "schwer_n": "{n} als schwerwiegend eingestufte Prüfhinweise sind offen.",
        "ce_1": "1 CE-Suchhinweis ist fachlich zu prüfen.",
        "ce_n": "{n} CE-Suchhinweise sind fachlich zu prüfen.",
        "klasse_Kritisch": "Kritisch",
        "klasse_Schwer": "Schwer",
        "klasse_Mittel": "Mittel",
        "klasse_Gering": "Gering",
        "bew_nicht_gefunden": "Suchwort nicht gefunden",
        "bew_nicht_nachweisbar": "Suchwort nicht gefunden; fachlich prüfen",
        "bew_satz": "Sätze zu lang ({n} gefunden)",
        "emp_satz": "{n} Sätze mit mehr als 25 Wörtern gefunden",
        "fund_nicht_vorhanden": "Nicht vorhanden",
        "fund_nicht_gefunden": "Nicht gefunden",
        "pflicht_ja": "Ja",
        "pflicht_produkt": "Produktabhängig",
        "prio_Hoch": "Hoch",
        "prio_Mittel": "Mittel",
        "norm_basis": "Basisprüfung",
        "norm_din": "DIN 82079-1",
        "norm_ce": "CE / EU-Konformität",
        "hinweis_intern": "Interner Bericht. Enthält Gewichtungen und Aufwandsschätzungen und ist nicht zur Weitergabe an den Auftraggeber bestimmt.",
        "hinweis_fach": "Dieser Bericht fasst die Ergebnisse der Dokumentenprüfung für den Auftraggeber zusammen.",
        "seite": "Seite {n} von {m}",
        "erstellt_mit": "Erstellt mit dem Dokumentenprüfer",
        "sprache": "Sprache des Berichts",
        "bereich_Zielgruppe": "Zielgruppe",
        "bereich_Gliederung": "Gliederung",
        "bereich_Sicherheit": "Sicherheit",
        "bereich_Symbole": "Symbole",
        "bereich_Illustrationen": "Illustrationen",
        "bereich_Sprache": "Sprache",
        "bereich_Formatierung": "Formatierung",
        "bereich_Format": "Format",
        "bereich_Lesbarkeit": "Lesbarkeit",
        "hinweis_vorpruefung": "Automatische Schlüsselwortsuche: Suchtreffer sind kein Erfüllungsnachweis. Auch 100 Punkte belegen keine Vollständigkeit, Richtigkeit oder Konformität. Fachliche Prüfung und Freigabe bleiben offen.",
        "ce_nicht_geprueft": "CE wurde in dieser Vorprüfung nicht ausgewählt und nicht geprüft.",
    },
    "en": {
        "titel_pruef": "Test report",
        "titel_fach": "Technical report",
        "untertitel_pruef": "Internal report for the review team",
        "untertitel_fach": "Report for the client",
        "dokument": "Document",
        "datum": "Date of review",
        "geprueft_von": "Reviewed by",
        "regelsaetze": "Rule sets",
        "bewertung": "Search score",
        "ampel": "Traffic light",
        "aufwand": "Estimated effort",
        "stunden": "h",
        "funde_anzahl": "Review flags",
        "fazit": "Preliminary review",
        "todo": "To-do list (CE conformity)",
        "massnahmen": "Recommended actions",
        "funde": "Detailed findings",
        "keine_funde": "No further automated flags. Professional review remains outstanding.",
        "keine_todos": "No additional CE search flags. This does not establish CE conformity.",
        "keine_massnahmen": "No additional actions from the keyword search. Professional assessment of actions is still required.",
        "sp_id": "ID",
        "sp_normlogik": "Rule logic",
        "sp_bereich": "Area",
        "sp_pflicht": "Mandatory",
        "sp_klasse": "Severity",
        "sp_bewertung": "Assessment",
        "sp_fundstelle": "Location",
        "sp_empfehlung": "Recommendation",
        "sp_gewichtung": "Wt.",
        "sp_minuten": "Min.",
        "sp_massnahme": "Action",
        "sp_prioritaet": "Priority",
        "sp_aufwand_h": "Effort (h)",
        "ampel_gruen": "Previous assessment · review again",
        "ampel_gelb": "Yellow · review outstanding",
        "ampel_rot": "Red · urgent review needed",
        "fazit_rot": "Critical or extensive review flags remain open. Professional assessment is required.",
        "fazit_gelb": "The automated preliminary review is complete. Professional assessment remains outstanding.",
        "fazit_gruen": "Previous assessment. Review again; this result does not establish approval.",
        "kritisch_1": "1 review flag classified as critical remains open.",
        "kritisch_n": "{n} review flags classified as critical remain open.",
        "schwer_1": "1 review flag classified as serious remains open.",
        "schwer_n": "{n} review flags classified as serious remain open.",
        "ce_1": "1 CE search flag requires professional review.",
        "ce_n": "{n} CE search flags require professional review.",
        "klasse_Kritisch": "Critical",
        "klasse_Schwer": "Serious",
        "klasse_Mittel": "Medium",
        "klasse_Gering": "Minor",
        "bew_nicht_gefunden": "Keyword not found",
        "bew_nicht_nachweisbar": "Keyword not found; review required",
        "bew_satz": "Sentences too long ({n} found)",
        "emp_satz": "{n} sentences with more than 25 words found",
        "fund_nicht_vorhanden": "Not present",
        "fund_nicht_gefunden": "Not found",
        "pflicht_ja": "Yes",
        "pflicht_produkt": "Product-dependent",
        "prio_Hoch": "High",
        "prio_Mittel": "Medium",
        "norm_basis": "Basic check",
        "norm_din": "DIN 82079-1",
        "norm_ce": "CE / EU conformity",
        "hinweis_intern": "Internal report. Contains weights and effort estimates and is not intended for distribution to the client.",
        "hinweis_fach": "This report summarises the results of the document review for the client.",
        "seite": "Page {n} of {m}",
        "erstellt_mit": "Created with the document checker",
        "sprache": "Report language",
        "bereich_Zielgruppe": "Target group",
        "bereich_Gliederung": "Structure",
        "bereich_Sicherheit": "Safety",
        "bereich_Symbole": "Symbols",
        "bereich_Illustrationen": "Illustrations",
        "bereich_Sprache": "Language",
        "bereich_Formatierung": "Formatting",
        "bereich_Format": "Format",
        "bereich_Lesbarkeit": "Readability",
        "hinweis_vorpruefung": "Automated keyword search: matches are not evidence that requirements are met. Even 100 points do not establish completeness, accuracy or conformity. Professional review and approval remain outstanding.",
        "ce_nicht_geprueft": "CE was not selected and was not checked in this preliminary review.",
    },
    "uk": {
        "titel_pruef": "Протокол перевірки",
        "titel_fach": "Фаховий звіт",
        "untertitel_pruef": "Внутрішній звіт для групи перевірки",
        "untertitel_fach": "Звіт для замовника",
        "dokument": "Документ",
        "datum": "Дата перевірки",
        "geprueft_von": "Перевірку виконав(-ла)",
        "regelsaetze": "Набори правил",
        "bewertung": "Пошуковий бал",
        "ampel": "Світлофор",
        "aufwand": "Орієнтовні витрати часу",
        "stunden": "год",
        "funde_anzahl": "Пункти для перевірки",
        "fazit": "Попередній висновок",
        "todo": "Перелік завдань (відповідність CE)",
        "massnahmen": "Рекомендовані заходи",
        "funde": "Детальні результати перевірки",
        "keine_funde": "Додаткових автоматичних зауважень немає. Фахова перевірка ще потрібна.",
        "keine_todos": "Додаткових зауважень пошуку CE немає. Це не підтверджує відповідність CE.",
        "keine_massnahmen": "Додаткових заходів за результатами пошуку немає. Заходи ще потребують фахової оцінки.",
        "sp_id": "ID",
        "sp_normlogik": "Логіка норм",
        "sp_bereich": "Розділ",
        "sp_pflicht": "Обов'язково",
        "sp_klasse": "Клас помилки",
        "sp_bewertung": "Оцінка",
        "sp_fundstelle": "Місце",
        "sp_empfehlung": "Рекомендація",
        "sp_gewichtung": "Вага",
        "sp_minuten": "Хв",
        "sp_massnahme": "Захід",
        "sp_prioritaet": "Пріоритет",
        "sp_aufwand_h": "Час (год)",
        "ampel_gruen": "Попередня оцінка · перевірити знову",
        "ampel_gelb": "Жовтий · потрібна фахова перевірка",
        "ampel_rot": "Червоний · потрібна термінова перевірка",
        "fazit_rot": "Критичні або численні пункти перевірки залишаються відкритими. Потрібна фахова оцінка.",
        "fazit_gelb": "Автоматичну попередню перевірку завершено. Фахова оцінка ще потрібна.",
        "fazit_gruen": "Попередня оцінка. Перевірте знову; цей результат не підтверджує затвердження.",
        "kritisch_1": "1 пункт перевірки, класифікований як критичний, залишається відкритим.",
        "kritisch_n": "{n} пунктів перевірки, класифікованих як критичні, залишаються відкритими.",
        "schwer_1": "1 пункт перевірки, класифікований як суттєвий, залишається відкритим.",
        "schwer_n": "{n} пунктів перевірки, класифікованих як суттєві, залишаються відкритими.",
        "ce_1": "1 зауваження пошуку CE потребує фахової перевірки.",
        "ce_n": "{n} зауважень пошуку CE потребують фахової перевірки.",
        "klasse_Kritisch": "Критичний",
        "klasse_Schwer": "Серйозний",
        "klasse_Mittel": "Середній",
        "klasse_Gering": "Незначний",
        "bew_nicht_gefunden": "Ключове слово не знайдено",
        "bew_nicht_nachweisbar": "Ключове слово не знайдено; потрібна перевірка",
        "bew_satz": "Занадто довгі речення (знайдено: {n})",
        "emp_satz": "Знайдено речень довших за 25 слів: {n}",
        "fund_nicht_vorhanden": "Відсутнє",
        "fund_nicht_gefunden": "Не знайдено",
        "pflicht_ja": "Так",
        "pflicht_produkt": "Залежить від продукту",
        "prio_Hoch": "Високий",
        "prio_Mittel": "Середній",
        "norm_basis": "Базова перевірка",
        "norm_din": "DIN 82079-1",
        "norm_ce": "CE / відповідність ЄС",
        "hinweis_intern": "Внутрішній звіт. Містить вагові коефіцієнти та оцінки витрат часу й не призначений для передачі замовнику.",
        "hinweis_fach": "Цей звіт підсумовує результати перевірки документа для замовника.",
        "seite": "Сторінка {n} з {m}",
        "erstellt_mit": "Створено за допомогою Перевірника документів",
        "sprache": "Мова звіту",
        "bereich_Zielgruppe": "Цільова група",
        "bereich_Gliederung": "Структура",
        "bereich_Sicherheit": "Безпека",
        "bereich_Symbole": "Символи",
        "bereich_Illustrationen": "Ілюстрації",
        "bereich_Sprache": "Мова",
        "bereich_Formatierung": "Форматування",
        "bereich_Format": "Формат",
        "bereich_Lesbarkeit": "Читабельність",
        "hinweis_vorpruefung": "Автоматичний пошук ключових слів: збіги не є доказом виконання вимог. Навіть 100 балів не підтверджують повноту, правильність або відповідність. Фахова перевірка та затвердження залишаються відкритими.",
        "ce_nicht_geprueft": "CE не було вибрано та не перевірялося під час цієї попередньої перевірки.",
    },
    "ru": {
        "titel_pruef": "Протокол проверки",
        "titel_fach": "Экспертный отчёт",
        "untertitel_pruef": "Внутренний отчёт для группы проверки",
        "untertitel_fach": "Отчёт для заказчика",
        "dokument": "Документ",
        "datum": "Дата проверки",
        "geprueft_von": "Проверку выполнил(-а)",
        "regelsaetze": "Наборы правил",
        "bewertung": "Поисковый балл",
        "ampel": "Светофор",
        "aufwand": "Оценочные трудозатраты",
        "stunden": "ч",
        "funde_anzahl": "Пункты проверки",
        "fazit": "Предварительный вывод",
        "todo": "Перечень задач (соответствие CE)",
        "massnahmen": "Рекомендуемые меры",
        "funde": "Детальные результаты проверки",
        "keine_funde": "Дополнительных автоматических замечаний нет. Профессиональная проверка ещё требуется.",
        "keine_todos": "Дополнительных замечаний поиска CE нет. Это не подтверждает соответствие CE.",
        "keine_massnahmen": "Дополнительных мер по результатам поиска нет. Меры ещё требуют профессиональной оценки.",
        "sp_id": "ID",
        "sp_normlogik": "Логика норм",
        "sp_bereich": "Раздел",
        "sp_pflicht": "Обязательно",
        "sp_klasse": "Класс ошибки",
        "sp_bewertung": "Оценка",
        "sp_fundstelle": "Место",
        "sp_empfehlung": "Рекомендация",
        "sp_gewichtung": "Вес",
        "sp_minuten": "Мин",
        "sp_massnahme": "Мера",
        "sp_prioritaet": "Приоритет",
        "sp_aufwand_h": "Время (ч)",
        "ampel_gruen": "Предыдущая оценка · проверить снова",
        "ampel_gelb": "Жёлтый · требуется проверка",
        "ampel_rot": "Красный · требуется срочная проверка",
        "fazit_rot": "Критические или многочисленные пункты проверки остаются открытыми. Требуется профессиональная оценка.",
        "fazit_gelb": "Автоматическая предварительная проверка завершена. Профессиональная оценка ещё требуется.",
        "fazit_gruen": "Предыдущая оценка. Проверьте снова; этот результат не подтверждает утверждение.",
        "kritisch_1": "1 пункт проверки, отнесённый к критическим, остаётся открытым.",
        "kritisch_n": "{n} пунктов проверки, отнесённых к критическим, остаются открытыми.",
        "schwer_1": "1 пункт проверки, отнесённый к серьёзным, остаётся открытым.",
        "schwer_n": "{n} пунктов проверки, отнесённых к серьёзным, остаются открытыми.",
        "ce_1": "1 замечание поиска CE требует профессиональной проверки.",
        "ce_n": "{n} замечаний поиска CE требуют профессиональной проверки.",
        "klasse_Kritisch": "Критический",
        "klasse_Schwer": "Серьёзный",
        "klasse_Mittel": "Средний",
        "klasse_Gering": "Незначительный",
        "bew_nicht_gefunden": "Ключевое слово не найдено",
        "bew_nicht_nachweisbar": "Ключевое слово не найдено; требуется проверка",
        "bew_satz": "Слишком длинные предложения (найдено: {n})",
        "emp_satz": "Найдено предложений длиннее 25 слов: {n}",
        "fund_nicht_vorhanden": "Отсутствует",
        "fund_nicht_gefunden": "Не найдено",
        "pflicht_ja": "Да",
        "pflicht_produkt": "Зависит от продукта",
        "prio_Hoch": "Высокий",
        "prio_Mittel": "Средний",
        "norm_basis": "Базовая проверка",
        "norm_din": "DIN 82079-1",
        "norm_ce": "CE / соответствие ЕС",
        "hinweis_intern": "Внутренний отчёт. Содержит весовые коэффициенты и оценки трудозатрат и не предназначен для передачи заказчику.",
        "hinweis_fach": "Этот отчёт обобщает результаты проверки документа для заказчика.",
        "seite": "Страница {n} из {m}",
        "erstellt_mit": "Создано с помощью Проверщика документов",
        "sprache": "Язык отчёта",
        "bereich_Zielgruppe": "Целевая группа",
        "bereich_Gliederung": "Структура",
        "bereich_Sicherheit": "Безопасность",
        "bereich_Symbole": "Символы",
        "bereich_Illustrationen": "Иллюстрации",
        "bereich_Sprache": "Язык",
        "bereich_Formatierung": "Форматирование",
        "bereich_Format": "Формат",
        "bereich_Lesbarkeit": "Читаемость",
        "hinweis_vorpruefung": "Автоматический поиск ключевых слов: совпадения не доказывают выполнение требований. Даже 100 баллов не подтверждают полноту, правильность или соответствие. Профессиональная проверка и утверждение остаются открытыми.",
        "ce_nicht_geprueft": "CE не было выбрано и не проверялось в ходе этой предварительной проверки.",
    },
}

_NORM = {"Basisprüfung": "norm_basis", "DIN 82079-1": "norm_din", "CE / EU-Konformität": "norm_ce"}


def t(sprache: str, schluessel: str, **werte: object) -> str:
    tabelle = TEXTE.get(sprache) or TEXTE["de"]
    text = tabelle.get(schluessel) or TEXTE["de"].get(schluessel) or schluessel
    try:
        return text.format(**werte) if werte else text
    except (KeyError, IndexError):
        return text


def normlogik(sprache: str, wert: str | None) -> str:
    return t(sprache, _NORM[wert]) if wert in _NORM else (wert or "")


def klasse(sprache: str, wert: str | None) -> str:
    return t(sprache, f"klasse_{wert}") if wert else ""


def prioritaet(sprache: str, wert: str | None) -> str:
    return t(sprache, f"prio_{wert}") if wert else ""


def bereich(sprache: str, fund: dict) -> str:
    """Bereich aus der Regel in der Berichtssprache, sonst aus der Tabelle, sonst Deutsch."""
    eigen = fund.get(f"bereich_{sprache}")
    if eigen:
        return str(eigen)
    wert = fund.get("Bereich") or ""
    schluessel = f"bereich_{wert}"
    tabelle = TEXTE.get(sprache, {})
    return tabelle.get(schluessel, wert)


def bewertung(sprache: str, fund: dict) -> str:
    wert = fund.get("Bewertung") or ""
    if fund.get("Schluessel") == "satz_zu_lang":
        return t(sprache, "bew_satz", n=fund.get("Anzahl", 0))
    if wert == "Nicht gefunden":
        return t(sprache, "bew_nicht_gefunden")
    if wert == "Nicht ausreichend nachweisbar":
        return t(sprache, "bew_nicht_nachweisbar")
    return wert


def fundstelle(sprache: str, fund: dict) -> str:
    wert = fund.get("Fundstelle") or ""
    if wert == "Nicht vorhanden":
        return t(sprache, "fund_nicht_vorhanden")
    if wert == "Nicht gefunden":
        return t(sprache, "fund_nicht_gefunden")
    return wert


def empfehlung(sprache: str, fund: dict) -> str:
    if fund.get("Schluessel") == "satz_zu_lang":
        return t(sprache, "emp_satz", n=fund.get("Anzahl", 0))
    eigen = fund.get(f"empfehlung_{sprache}")
    if eigen:
        return str(eigen)
    return str(fund.get("Empfehlung") or "")


def pflicht(sprache: str, wert: str | None) -> str:
    if wert == "Ja":
        return t(sprache, "pflicht_ja")
    if wert == "Produktabhängig":
        return t(sprache, "pflicht_produkt")
    return wert or "-"


def fazit(sprache: str, teile: list) -> str:
    return " ".join(t(sprache, schluessel, **werte) for schluessel, werte in teile)


def ampel(sprache: str, wert: str) -> str:
    return t(sprache, f"ampel_{wert}")

