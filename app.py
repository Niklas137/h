import streamlit as st
from docx import Document
import pandas as pd
import json
import re
from io import BytesIO

# PDF libraries
try:
    from PyPDF2 import PdfReader
    HAS_PYPDF2 = True
except Exception:
    HAS_PYPDF2 = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except Exception:
    HAS_PDFPLUMBER = False

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

st.set_page_config(page_title="Dokumentenprüfer", layout="wide")
st.title("Lokaler Dokumentenprüfer")

# -------------------------
# File readers
# -------------------------

def read_docx(file):
    try:
        doc = Document(file)
    except Exception as e:
        st.error(f"Fehler beim Laden der Word-Datei: {e}")
        return None

    structured = []
    current_heading = "Unbekannt"
    try:
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            style = getattr(para, 'style', None)
            name = getattr(style, 'name', '') if style is not None else ''
            if name.startswith('Heading'):
                current_heading = text
            structured.append({"text": text, "heading": current_heading})
    except Exception as e:
        st.error(f"Fehler beim Parsen der Word-Datei: {e}")
        return None

    return structured if structured else None


def read_pdf(uploaded_file):
    uploaded_file.seek(0)
    # Try PyPDF2 first
    if HAS_PYPDF2:
        try:
            reader = PdfReader(uploaded_file)
            structured = []
            for i, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                if not text:
                    continue
                for line in text.splitlines():
                    line = line.strip()
                    if line:
                        structured.append({"text": line, "heading": f"Seite {i}"})
            if structured:
                return structured
        except Exception:
            pass

    # Fallback to pdfplumber if available
    if HAS_PDFPLUMBER:
        try:
            uploaded_file.seek(0)
            with pdfplumber.open(uploaded_file) as pdf:
                structured = []
                for i, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    if not text:
                        continue
                    for line in text.split('\n'):
                        line = line.strip()
                        if line:
                            structured.append({"text": line, "heading": f"Seite {i}"})
                if structured:
                    return structured
        except Exception as e:
            st.error(f"Fehler beim Lesen der PDF: {e}")
            return None

    st.error('PDF-Support nicht verfügbar. Bitte PyPDF2 oder pdfplumber installieren.')
    return None

# -------------------------
# Loaders (cached)
# -------------------------

@st.cache_data
def load_checklist():
    try:
        with open('pruefkatalog.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error('pruefkatalog.json nicht gefunden')
        return []
    except json.JSONDecodeError as e:
        st.error(f'Fehler beim Laden von pruefkatalog.json: {e}')
        return []

@st.cache_data
def load_normlogik_82079():
    try:
        with open('normlogik_82079.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error('normlogik_82079.json nicht gefunden')
        return []
    except json.JSONDecodeError as e:
        st.error(f'Fehler beim Laden von normlogik_82079.json: {e}')
        return []

@st.cache_data
def load_ce_logik():
    try:
        with open('ce_logik.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error('ce_logik.json nicht gefunden')
        return []
    except json.JSONDecodeError as e:
        st.error(f'Fehler beim Laden von ce_logik.json: {e}')
        return []

# -------------------------
# Helpers
# -------------------------

def keyword_found(full_text, keywords):
    for keyword in keywords:
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        if re.search(pattern, full_text):
            return True
    return False


def deduplicate_findings(findings):
    txt_findings = [f for f in findings if f.get('ID') == 'TXT-001']
    other_findings = [f for f in findings if f.get('ID') != 'TXT-001']

    seen = set()
    deduped = []
    for f in other_findings:
        key = (f.get('ID'), f.get('Fundstelle', ''))
        if key not in seen:
            seen.add(key)
            deduped.append(f)

    if txt_findings:
        agg = txt_findings[0].copy()
        agg['Bewertung'] = f"Sätze zu lang ({len(txt_findings)} gefunden)"
        agg['Empfehlung'] = f"{len(txt_findings)} Sätze mit >25 Wörtern gefunden"
        deduped.append(agg)

    return deduped

# -------------------------
# Checks (unchanged logic)
# -------------------------

def check_document(structured_text):
    findings = []
    checklist = load_checklist()
    full_text = ' '.join([item['text'] for item in structured_text]).lower()

    for rule in checklist:
        if not keyword_found(full_text, rule.get('keywords', [])):
            findings.append({
                'ID': rule.get('id'),
                'Normlogik': 'Basisprüfung',
                'Bereich': rule.get('bereich'),
                'Pflicht': '-',
                'Fehlerklasse': rule.get('fehlerklasse'),
                'Bewertung': 'Nicht gefunden',
                'Fundstelle': 'Nicht vorhanden',
                'Empfehlung': rule.get('empfehlung'),
                'Gewichtung': rule.get('gewichtung', 1),
                'Zeitaufwand_min': rule.get('gewichtung', 1) * 12
            })

    for item in structured_text:
        sentence = item['text']
        if len(sentence.split()) > 25:
            findings.append({
                'ID': 'TXT-001',
                'Normlogik': 'Basisprüfung',
                'Bereich': 'Lesbarkeit',
                'Pflicht': '-',
                'Fehlerklasse': 'Mittel',
                'Bewertung': 'Satz zu lang',
                'Fundstelle': item.get('heading', ''),
                'Empfehlung': sentence[:150],
                'Gewichtung': 2,
                'Zeitaufwand_min': 15
            })
    return findings


def check_normlogik_82079(structured_text):
    findings = []
    rules = load_normlogik_82079()
    full_text = ' '.join([item['text'] for item in structured_text]).lower()

    for rule in rules:
        if not keyword_found(full_text, rule.get('keywords', [])):
            findings.append({
                'ID': rule.get('id'),
                'Normlogik': 'DIN 82079-1',
                'Bereich': rule.get('bereich'),
                'Pflicht': 'Ja' if rule.get('pflicht') else 'Produktabhängig',
                'Fehlerklasse': rule.get('fehlerklasse'),
                'Bewertung': 'Nicht ausreichend nachweisbar',
                'Fundstelle': 'Nicht gefunden',
                'Empfehlung': rule.get('empfehlung'),
                'Gewichtung': rule.get('gewichtung', 1),
                'Zeitaufwand_min': rule.get('gewichtung', 1) * 15
            })
    return findings


def check_ce_logik(structured_text):
    findings = []
    rules = load_ce_logik()
    full_text = ' '.join([item['text'] for item in structured_text]).lower()

    for rule in rules:
        if not keyword_found(full_text, rule.get('keywords', [])):
            findings.append({
                'ID': rule.get('id'),
                'Normlogik': 'CE / EU-Konformität',
                'Bereich': rule.get('bereich'),
                'Pflicht': 'Ja',
                'Fehlerklasse': rule.get('fehlerklasse'),
                'Bewertung': 'Nicht ausreichend nachweisbar',
                'Fundstelle': 'Nicht gefunden',
                'Empfehlung': rule.get('empfehlung'),
                'Gewichtung': rule.get('gewichtung', 1),
                'Zeitaufwand_min': rule.get('gewichtung', 1) * 18,
                'Priorität': 'Hoch' if rule.get('fehlerklasse') == 'Kritisch' else 'Mittel'
            })
    return findings

# -------------------------
# Reporting / UI
# -------------------------

def get_ampel(score):
    if score >= 80:
        return '🟢 GRÜN', 'Dokument grundsätzlich verwendbar.'
    elif score >= 60:
        return '🟡 GELB', 'Dokument überarbeitungsbedürftig.'
    else:
        return '🔴 ROT', 'Dokument kritisch / nicht abgabereif.'


def generate_fazit(findings, score):
    kritisch = [f for f in findings if f.get('Fehlerklasse') == 'Kritisch']
    schwer = [f for f in findings if f.get('Fehlerklasse') == 'Schwer']
    ce_fehler = [f for f in findings if f.get('Normlogik') == 'CE / EU-Konformität']

    text = []
    if score < 60:
        text.append('Das Dokument ist in der vorliegenden Form fachlich nicht abgabereif.')
    elif score < 80:
        text.append('Das Dokument weist relevante Mängel auf und ist überarbeitungsbedürftig.')
    else:
        text.append('Das Dokument ist grundsätzlich verwendbar, weist jedoch Optimierungspotenzial auf.')

    if kritisch:
        text.append(f'Es wurden {len(kritisch)} kritische Abweichungen festgestellt.')
    if schwer:
        text.append(f'Zusätzlich wurden {len(schwer)} schwerwiegende Defizite identifiziert.')
    if ce_fehler:
        text.append(f'Im Bereich CE wurden {len(ce_fehler)} Nachweislücken festgestellt.')

    return ' '.join(text)


def generate_todo_list(findings):
    todos = []
    for f in findings:
        if f.get('Normlogik') == 'CE / EU-Konformität':
            todos.append({
                'Bereich': f.get('Bereich'),
                'Maßnahme': f.get('Empfehlung'),
                'Priorität': f.get('Priorität', 'Mittel'),
                'Aufwand (h)': round(f.get('Zeitaufwand_min', 0) / 60, 1)
            })
    return sorted(todos, key=lambda x: x['Priorität'] == 'Mittel')


def create_pdf_report(findings, score, total_hours, fazit, ampel, todos):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph('Prüfbericht', styles['Title']))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f'Bewertung: {score} %', styles['Heading2']))
    story.append(Paragraph(f'Ampel: {ampel}', styles['Heading2']))
    story.append(Paragraph(f'Aufwand: {total_hours} h', styles['Heading2']))
    story.append(Spacer(1, 12))

    story.append(Paragraph('Fachliches Fazit', styles['Heading2']))
    story.append(Paragraph(fazit, styles['Normal']))
    story.append(Spacer(1, 20))

    story.append(Paragraph('CE-To-Do-Liste', styles['Heading2']))
    todo_data = [['Bereich', 'Maßnahme', 'Priorität', 'Aufwand (h)']]
    for t in todos:
        todo_data.append([t['Bereich'], t['Maßnahme'], t['Priorität'], str(t['Aufwand (h)'])])

    table = Table(todo_data)
    table.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
    story.append(table)

    doc.build(story)
    buffer.seek(0)
    return buffer

# -------------------------
# UI
# -------------------------

file_types = ['docx', 'pdf']
label = 'Word-Dokument (.docx) oder PDF (.pdf) hochladen'

st.info('PDF-Support: ' + ('verfügbar (PyPDF2/pdfplumber)' if (HAS_PYPDF2 or HAS_PDFPLUMBER) else 'nicht installiert. Bitte PyPDF2 installieren.'))

uploaded_file = st.file_uploader(label, type=file_types)

if uploaded_file is not None:
    name = uploaded_file.name.lower()
    if name.endswith('.pdf'):
        structured = read_pdf(uploaded_file)
    else:
        structured = read_docx(uploaded_file)

    if not structured:
        st.warning('Keine Textinhalte erkannt oder Datei konnte nicht gelesen werden.')
    else:
        findings = []
        findings.extend(check_document(structured))
        findings.extend(check_normlogik_82079(structured))
        findings.extend(check_ce_logik(structured))
        findings = deduplicate_findings(findings)

        df = pd.DataFrame(findings)
        st.subheader('Prüfergebnisse')
        st.dataframe(df, use_container_width=True)

        deduction = sum(f.get('Gewichtung', 0) for f in findings)
        score = max(0, round(100 - deduction))
        total_minutes = sum(f.get('Zeitaufwand_min', 0) for f in findings)
        total_hours = round(total_minutes / 60, 1)

        ampel, _ = get_ampel(score)
        c1, c2, c3 = st.columns(3)
        c1.metric('Score', f"{score}%")
        c2.metric('Ampel', ampel)
        c3.metric('Aufwand', f"{total_hours} h")

        st.divider()
        fazit = generate_fazit(findings, score)
        st.subheader('Fachliches Fazit')
        st.write(fazit)

        st.subheader('To-Do-Liste (CE-Konformität)')
        todos = generate_todo_list(findings)
        if todos:
            st.dataframe(pd.DataFrame(todos), use_container_width=True)
        else:
            st.info('Keine CE-Maßnahmen erforderlich')

        st.divider()
        pdf = create_pdf_report(findings, score, total_hours, fazit, ampel, todos)
        st.download_button('📄 PDF herunterladen', data=pdf, file_name='pruefbericht.pdf', mime='application/pdf')
