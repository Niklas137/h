"""Versand des Verifizierungscodes. Ohne SMTP-Zugang wird der Code nur protokolliert."""
from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from . import config

log = logging.getLogger("dokumentenpruefer.mail")


def smtp_konfiguriert() -> bool:
    return bool(config.SMTP_HOST and config.SMTP_ABSENDER)


def code_senden(empfaenger: str, code: str, name: str = "") -> bool:
    """Schickt den Code per E-Mail. Gibt True zurück, wenn wirklich gesendet wurde."""
    betreff = "Dein Verifizierungscode für den Dokumentenprüfer"
    anrede = f"Hallo {name}," if name else "Hallo,"
    text = (
        f"{anrede}\n\n"
        f"dein Code für die Erstanmeldung lautet: {code}\n"
        f"Er gilt {config.CODE_MINUTEN} Minuten.\n\n"
        "Wenn du dich nicht gerade anmeldest, ignoriere diese Nachricht.\n\n"
        f"{config.BERICHT_KOPF}"
    )
    if not smtp_konfiguriert():
        log.warning("Kein SMTP konfiguriert. Code für %s: %s", empfaenger, code)
        protokoll = config.DATEN / "codes.log"
        with protokoll.open("a", encoding="utf-8") as f:
            f.write(f"{empfaenger}\t{code}\n")
        return False
    nachricht = EmailMessage()
    nachricht["Subject"] = betreff
    nachricht["From"] = config.SMTP_ABSENDER
    nachricht["To"] = empfaenger
    nachricht.set_content(text)
    with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=20) as server:
        server.starttls()
        if config.SMTP_USER:
            server.login(config.SMTP_USER, config.SMTP_PASSWORT)
        server.send_message(nachricht)
    return True
