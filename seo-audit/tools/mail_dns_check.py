#!/usr/bin/env python3
"""Prüft die E-Mail-DNS-Einträge (SPF, DMARC, DKIM, MX) beider FSH-Domains gegen die Sollwerte.

Aufruf:  python3 seo-audit/tools/mail_dns_check.py [--json]
Quelle:  dns.google (DNS-over-HTTPS), keine lokale Auflösung nötig.
Sollwerte: website/google-und-email-dns.md, Abschnitt 1. Exit-Code 0 = alles gesetzt, 1 = Abweichung.
"""
import json
import sys
import urllib.parse
import urllib.request

RUA = "mailto:niklas.heinzmann@fsh-documentation.de"
CHECKS = [
    # (Name, Typ, Beschreibung, Prüffunktion)
    ("fsh-documentation.de", "TXT", "SPF .de",
     lambda v: any(x.startswith("v=spf1") and "include:_spf.strato.com" in x and x.rstrip().endswith("-all") for x in v)),
    ("_dmarc.fsh-documentation.de", "TXT", "DMARC .de",
     lambda v: any("v=DMARC1" in x and "p=reject" in x.replace(" ", "") and RUA in x for x in v)),
    ("strato-dkim-0002._domainkey.fsh-documentation.de", "TXT", "DKIM .de (STRATO RSA)",
     lambda v: any("v=DKIM1" in x and "p=" in x for x in v)),
    ("fsh-documentation.de", "MX", "MX .de (STRATO)",
     lambda v: any("rzone.de" in x for x in v)),
    ("fsh-documentation.com", "TXT", "SPF .com (kein Versand)",
     lambda v: any(x.replace(" ", "") == "v=spf1-all" for x in v)),
    ("_dmarc.fsh-documentation.com", "TXT", "DMARC .com",
     lambda v: any("v=DMARC1" in x and "p=reject" in x.replace(" ", "") and RUA in x for x in v)),
    ("fsh-documentation.com._report._dmarc.fsh-documentation.de", "TXT", "Berichtsfreigabe .com → .de",
     lambda v: any(x.replace(" ", "").startswith("v=DMARC1") for x in v)),
]


def resolve(name, rtype):
    url = "https://dns.google/resolve?" + urllib.parse.urlencode({"name": name, "type": rtype})
    with urllib.request.urlopen(url, timeout=15) as r:
        d = json.load(r)
    return [a["data"].strip('"').replace('" "', "") for a in d.get("Answer", []) if a.get("type") in (16, 15)]


def main():
    as_json = "--json" in sys.argv
    rows, ok_all = [], True
    for name, rtype, label, test in CHECKS:
        try:
            values = resolve(name, rtype)
            ok = bool(values) and test(values)
            status = "OK" if ok else ("FEHLT" if not values else "ABWEICHUNG")
        except Exception as e:  # dns.google nicht erreichbar
            values, ok, status = [], False, f"NICHT PRÜFBAR ({e.__class__.__name__})"
        ok_all &= ok
        rows.append({"eintrag": label, "name": name, "typ": rtype, "status": status, "ist": values})
    if as_json:
        print(json.dumps({"alle_gesetzt": ok_all, "eintraege": rows}, ensure_ascii=False, indent=2))
    else:
        for r in rows:
            ist = "; ".join(x[:70] + ("…" if len(x) > 70 else "") for x in r["ist"]) or "(kein Eintrag)"
            print(f"{r['status']:<12} {r['eintrag']:<30} {ist}")
        print("\nErgebnis:", "alle Einträge gesetzt, B12 kann auf erledigt" if ok_all else "offen, siehe Zeilen ohne OK")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
