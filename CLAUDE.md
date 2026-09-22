# Hinweise für Claude Code

## Wocheneinkauf (Niklas)

Schreibt der Nutzer „Wocheneinkauf" (auch mit Zusatz wie „Geschäftsreise" oder „Kassenbon"),
den Skill `.claude/skills/wocheneinkauf/SKILL.md` ausführen. Daten, Preise, Gerichtepool und
Verlauf liegen unter `wocheneinkauf/`. Budget 60 € pro Woche ist fest, nicht nachfragen.

## Dokumentenprüfer

`app.py` ist eine Streamlit-App (lokaler Dokumentenprüfer, Regeln in `normlogik_82079.json`).
Sie hat nichts mit dem Wocheneinkauf zu tun.

## SEO-Audit (FSH-Documentation)

Schreibt der Nutzer „SEO-Audit" (auch mit Lauf-Kennung wie „freitag-0730"), den Skill
`.claude/skills/seo-audit/SKILL.md` ausführen. Berichte, PDFs, Verlauf und Werkzeuge liegen
unter `seo-audit/`. Die Website ist aus der Umgebung meist nicht abrufbar; dann nur Suchindex.

## Website-Relaunch (statisch)

Die neue Website liegt unter `website/`: Inhalte als JSON in `website/inhalt/`, Bau mit
`python3 website/build.py --pruefen`, fertige Dateien in `website/dist/`. Anleitung, Hosting-Wege und
offene Entscheidungen stehen in `website/README.md`. Rechtstexte dort sind keine Rechtsberatung.
