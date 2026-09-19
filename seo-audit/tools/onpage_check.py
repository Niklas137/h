#!/usr/bin/env python3
"""On-Page-Prüfung einer gespeicherten HTML-Seite (nur Standardbibliothek).

Aufruf:
    python3 seo-audit/tools/onpage_check.py <datei.html> [--url https://fsh-documentation.com/]

Gibt JSON aus: Title, Meta-Description, Robots, Canonical, Sprache, Viewport, hreflang,
Überschriften, Bilder ohne Alt-Text, interne/externe Links, JSON-LD-Typen, Open Graph,
Wortzahl und eine Liste automatischer Hinweise. Die Datei vorher z. B. so holen:
    curl -sS -L -m 25 -A "Mozilla/5.0 (compatible; FSH-SEO-Audit/1.0)" -o /tmp/seo/home.html \
         -w '%{http_code} %{url_effective} %{time_total}s\n' https://fsh-documentation.com/
"""
import json
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urlparse


class Seite(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.metas = []
        self.links = []
        self.lang = None
        self.headings = {"h1": [], "h2": [], "h3": []}
        self.images = []
        self.anchors = []
        self.jsonld = []
        self.text = []
        self._stack = []
        self._in = None
        self._script_jsonld = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "title":
            self._in = "title"
        elif tag == "meta":
            self.metas.append(a)
        elif tag == "link":
            self.links.append(a)
        elif tag in self.headings:
            self._in = tag
            self.headings[tag].append("")
        elif tag == "img":
            self.images.append(a)
        elif tag == "a":
            self.anchors.append(a.get("href", ""))
        elif tag == "script":
            self._script_jsonld = (a.get("type", "").strip().lower() == "application/ld+json")
            if self._script_jsonld:
                self.jsonld.append("")
            self._in = "script"
        elif tag == "style":
            self._in = "style"

    def handle_endtag(self, tag):
        if tag in ("title", "h1", "h2", "h3", "script", "style"):
            self._in = None
            self._script_jsonld = False

    def handle_data(self, data):
        if self._in == "title":
            self.title += data
        elif self._in in self.headings:
            self.headings[self._in][-1] += data
        elif self._in == "script":
            if self._script_jsonld:
                self.jsonld[-1] += data
        elif self._in == "style":
            pass
        else:
            self.text.append(data)


def meta(metas, key, value):
    for m in metas:
        if m.get(key, "").strip().lower() == value:
            return (m.get("content") or "").strip()
    return None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    path = sys.argv[1]
    url = None
    if "--url" in sys.argv:
        url = sys.argv[sys.argv.index("--url") + 1]
    host = urlparse(url).netloc.lower().removeprefix("www.") if url else None
    raw = open(path, "rb").read().decode("utf-8", errors="replace")
    p = Seite()
    p.feed(raw)

    title = re.sub(r"\s+", " ", p.title).strip()
    desc = meta(p.metas, "name", "description")
    robots = meta(p.metas, "name", "robots")
    viewport = meta(p.metas, "name", "viewport")
    og_title = meta(p.metas, "property", "og:title")
    og_desc = meta(p.metas, "property", "og:description")
    canonical = next((l.get("href") for l in p.links if "canonical" in (l.get("rel") or "").lower()), None)
    hreflang = [(l.get("hreflang"), l.get("href")) for l in p.links if l.get("hreflang")]

    intern, extern, beispiele = 0, 0, []
    for href in p.anchors:
        h = (href or "").strip()
        if not h or h.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        netloc = urlparse(h).netloc.lower().removeprefix("www.")
        if netloc and host and netloc != host:
            extern += 1
        else:
            intern += 1
            if len(beispiele) < 15 and h not in beispiele:
                beispiele.append(h)

    typen = []
    for blob in p.jsonld:
        try:
            data = json.loads(blob)
        except Exception:
            typen.append("(ungültiges JSON-LD)")
            continue
        items = data if isinstance(data, list) else [data]
        for it in items:
            if isinstance(it, dict):
                t = it.get("@type")
                if isinstance(t, list):
                    typen.extend(str(x) for x in t)
                elif t:
                    typen.append(str(t))
                for g in it.get("@graph", []) if isinstance(it.get("@graph"), list) else []:
                    if isinstance(g, dict) and g.get("@type"):
                        typen.append(str(g["@type"]))

    woerter = len(re.findall(r"\w+", " ".join(p.text)))
    h1 = [re.sub(r"\s+", " ", h).strip() for h in p.headings["h1"]]
    h2 = [re.sub(r"\s+", " ", h).strip() for h in p.headings["h2"]]
    ohne_alt = sum(1 for i in p.images if not (i.get("alt") or "").strip())

    hinweise = []
    if not title:
        hinweise.append("Title fehlt")
    elif len(title) > 60:
        hinweise.append(f"Title hat {len(title)} Zeichen (Richtwert bis 60)")
    if not desc:
        hinweise.append("Meta-Description fehlt")
    elif len(desc) > 160:
        hinweise.append(f"Meta-Description hat {len(desc)} Zeichen (Richtwert bis 160)")
    if robots and re.search(r"noindex|nofollow", robots, re.I):
        hinweise.append(f"Meta-Robots blockiert: {robots}")
    if not canonical:
        hinweise.append("Kein Canonical-Tag")
    if not p.lang:
        hinweise.append("Kein lang-Attribut am html-Element")
    if not viewport:
        hinweise.append("Kein Viewport-Meta (mobile Darstellung)")
    if len(h1) == 0:
        hinweise.append("Keine H1")
    elif len(h1) > 1:
        hinweise.append(f"{len(h1)} H1-Überschriften")
    if ohne_alt:
        hinweise.append(f"{ohne_alt} von {len(p.images)} Bildern ohne Alt-Text")
    if not typen:
        hinweise.append("Keine strukturierten Daten (JSON-LD)")
    if woerter < 300:
        hinweise.append(f"Nur etwa {woerter} Wörter sichtbarer Text")

    print(json.dumps({
        "datei": path, "url": url,
        "title": title, "title_laenge": len(title),
        "meta_description": desc, "description_laenge": len(desc or ""),
        "meta_robots": robots, "canonical": canonical, "lang": p.lang, "viewport": bool(viewport),
        "hreflang": [{"lang": l, "href": h} for l, h in hreflang],
        "h1": h1, "h2": h2, "h3_anzahl": len(p.headings["h3"]),
        "bilder": {"gesamt": len(p.images), "ohne_alt": ohne_alt},
        "links": {"intern": intern, "extern": extern, "beispiele_intern": beispiele},
        "json_ld_typen": typen,
        "open_graph": {"title": bool(og_title), "description": bool(og_desc)},
        "woerter": woerter,
        "hinweise": hinweise,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
