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
        "bewertung": "Score",
        "ampel": "Ampel",
        "aufwand": "Geschätzter Aufwand",
        "stunden": "h",
        "funde_anzahl": "Funde",
        "fazit": "Fachliches Fazit",
        "todo": "To-do-Liste (CE-Konformität)",
        "massnahmen": "Empfohlene Maßnahmen",
        "funde": "Prüfergebnisse im Einzelnen",
        "keine_funde": "Keine Abweichungen festgestellt.",
        "keine_todos": "Keine CE-Maßnahmen erforderlich.",
        "keine_massnahmen": "Keine Maßnahmen erforderlich.",
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
        "ampel_gruen": "Grün · Dokument grundsätzlich verwendbar",
        "ampel_gelb": "Gelb · Dokument überarbeitungsbedürftig",
        "ampel_rot": "Rot · Dokument kritisch, nicht abgabereif",
        "fazit_rot": "Das Dokument ist in der vorliegenden Form fachlich nicht abgabereif.",
        "fazit_gelb": "Das Dokument weist relevante Mängel auf und ist überarbeitungsbedürftig.",
        "fazit_gruen": "Das Dokument ist grundsätzlich verwendbar, weist jedoch Optimierungspotenzial auf.",
        "kritisch_1": "Es wurde 1 kritische Abweichung festgestellt.",
        "kritisch_n": "Es wurden {n} kritische Abweichungen festgestellt.",
        "schwer_1": "Zusätzlich wurde 1 schwerwiegendes Defizit identifiziert.",
        "schwer_n": "Zusätzlich wurden {n} schwerwiegende Defizite identifiziert.",
        "ce_1": "Im Bereich CE wurde 1 Nachweislücke festgestellt.",
        "ce_n": "Im Bereich CE wurden {n} Nachweislücken festgestellt.",
        "klasse_Kritisch": "Kritisch",
        "klasse_Schwer": "Schwer",
        "klasse_Mittel": "Mittel",
        "klasse_Gering": "Gering",
        "bew_nicht_gefunden": "Nicht gefunden",
        "bew_nicht_nachweisbar": "Nicht ausreichend nachweisbar",
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
        "bewertung": "Score",
        "ampel": "Traffic light",
        "aufwand": "Estimated effort",
        "stunden": "h",
        "funde_anzahl": "Findings",
        "fazit": "Conclusion",
        "todo": "To-do list (CE conformity)",
        "massnahmen": "Recommended actions",
        "funde": "Detailed findings",
        "keine_funde": "No deviations found.",
        "keine_todos": "No CE actions required.",
        "keine_massnahmen": "No actions required.",
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
        "ampel_gruen": "Green · Document generally usable",
        "ampel_gelb": "Yellow · Document needs revision",
        "ampel_rot": "Red · Document critical, not ready for release",
        "fazit_rot": "In its current form, the document is not ready for release.",
        "fazit_gelb": "The document shows relevant deficiencies and needs revision.",
        "fazit_gruen": "The document is generally usable but has room for improvement.",
        "kritisch_1": "1 critical deviation was found.",
        "kritisch_n": "{n} critical deviations were found.",
        "schwer_1": "In addition, 1 serious deficiency was identified.",
        "schwer_n": "In addition, {n} serious deficiencies were identified.",
        "ce_1": "In the CE area, 1 gap in evidence was found.",
        "ce_n": "In the CE area, {n} gaps in evidence were found.",
        "klasse_Kritisch": "Critical",
        "klasse_Schwer": "Serious",
        "klasse_Mittel": "Medium",
        "klasse_Gering": "Minor",
        "bew_nicht_gefunden": "Not found",
        "bew_nicht_nachweisbar": "Not sufficiently evidenced",
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
        "bewertung": "Загальна оцінка",
        "ampel": "Світлофор",
        "aufwand": "Орієнтовні витрати часу",
        "stunden": "год",
        "funde_anzahl": "Зауваження",
        "fazit": "Фаховий висновок",
        "todo": "Перелік завдань (відповідність CE)",
        "massnahmen": "Рекомендовані заходи",
        "funde": "Детальні результати перевірки",
        "keine_funde": "Відхилень не виявлено.",
        "keine_todos": "Заходи щодо CE не потрібні.",
        "keine_massnahmen": "Заходи не потрібні.",
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
        "ampel_gruen": "Зелений · документ загалом придатний до використання",
        "ampel_gelb": "Жовтий · документ потребує доопрацювання",
        "ampel_rot": "Червоний · документ критичний, не готовий до здачі",
        "fazit_rot": "У поточному вигляді документ не готовий до здачі.",
        "fazit_gelb": "Документ має суттєві недоліки й потребує доопрацювання.",
        "fazit_gruen": "Документ загалом придатний до використання, але має потенціал для покращення.",
        "kritisch_1": "Виявлено 1 критичне відхилення.",
        "kritisch_n": "Виявлено критичних відхилень: {n}.",
        "schwer_1": "Додатково виявлено 1 серйозний недолік.",
        "schwer_n": "Додатково виявлено серйозних недоліків: {n}.",
        "ce_1": "У сфері CE виявлено 1 прогалину в доказах.",
        "ce_n": "У сфері CE виявлено прогалин у доказах: {n}.",
        "klasse_Kritisch": "Критичний",
        "klasse_Schwer": "Серйозний",
        "klasse_Mittel": "Середній",
        "klasse_Gering": "Незначний",
        "bew_nicht_gefunden": "Не знайдено",
        "bew_nicht_nachweisbar": "Недостатньо підтверджено",
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
        "bewertung": "Общая оценка",
        "ampel": "Светофор",
        "aufwand": "Оценочные трудозатраты",
        "stunden": "ч",
        "funde_anzahl": "Замечания",
        "fazit": "Экспертное заключение",
        "todo": "Перечень задач (соответствие CE)",
        "massnahmen": "Рекомендуемые меры",
        "funde": "Детальные результаты проверки",
        "keine_funde": "Отклонений не выявлено.",
        "keine_todos": "Меры по CE не требуются.",
        "keine_massnahmen": "Меры не требуются.",
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
        "ampel_gruen": "Зелёный · документ в целом пригоден к использованию",
        "ampel_gelb": "Жёлтый · документ требует доработки",
        "ampel_rot": "Красный · документ критичный, не готов к сдаче",
        "fazit_rot": "В текущем виде документ не готов к сдаче.",
        "fazit_gelb": "Документ имеет существенные недостатки и требует доработки.",
        "fazit_gruen": "Документ в целом пригоден к использованию, но имеет потенциал для улучшения.",
        "kritisch_1": "Выявлено 1 критическое отклонение.",
        "kritisch_n": "Выявлено критических отклонений: {n}.",
        "schwer_1": "Дополнительно выявлен 1 серьёзный недостаток.",
        "schwer_n": "Дополнительно выявлено серьёзных недостатков: {n}.",
        "ce_1": "В области CE выявлен 1 пробел в доказательствах.",
        "ce_n": "В области CE выявлено пробелов в доказательствах: {n}.",
        "klasse_Kritisch": "Критический",
        "klasse_Schwer": "Серьёзный",
        "klasse_Mittel": "Средний",
        "klasse_Gering": "Незначительный",
        "bew_nicht_gefunden": "Не найдено",
        "bew_nicht_nachweisbar": "Недостаточно подтверждено",
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
