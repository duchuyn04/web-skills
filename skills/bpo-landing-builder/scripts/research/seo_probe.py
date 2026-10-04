"""Probe the SEO head of real BPO homepages: title and description length, canonical, robots, Open Graph, Twitter card,
hreflang, favicon, JSON-LD types, h1 count, image alt and lazy loading. The results behind references/seo-research.md.
Standard library only; reads the server HTML (no scripts run), which is what crawlers index first.

python scripts/research/seo_probe.py OUT.json [blueprint ids...]
"""
import json
import re
import sys
import concurrent.futures as cf
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

BLUEPRINTS = Path(__file__).resolve().parents[2] / "templates" / "blueprints"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"


class Head(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta, self.links, self.ld, self.imgs = [], [], [], []
        self.title, self.h1, self.html_lang = "", 0, ""
        self._in = None
        self._buf = []

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "html":
            self.html_lang = a.get("lang", "")
        elif tag == "meta":
            self.meta.append(a)
        elif tag == "link":
            self.links.append(a)
        elif tag == "img":
            self.imgs.append(a)
        elif tag == "h1":
            self.h1 += 1
        elif tag == "title" and not self.title:
            self._in, self._buf = "title", []
        elif tag == "script" and a.get("type", "").lower() == "application/ld+json":
            self._in, self._buf = "ld", []

    def handle_endtag(self, tag):
        if self._in == "title" and tag == "title":
            self.title = " ".join("".join(self._buf).split())
            self._in = None
        elif self._in == "ld" and tag == "script":
            self.ld.append("".join(self._buf))
            self._in = None

    def handle_data(self, data):
        if self._in:
            self._buf.append(data)


def ld_types(blobs):
    types = []

    def walk(x):
        if isinstance(x, dict):
            t = x.get("@type")
            for v in (t if isinstance(t, list) else [t]):
                if isinstance(v, str):
                    types.append(v)
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    for b in blobs:
        try:
            walk(json.loads(b))
        except ValueError:
            types.append("(invalid)")
    return types


def probe(bp):
    url = bp["source"]["url"]
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en,vi;q=0.8"})
        with urllib.request.urlopen(req, timeout=25) as r:
            raw = r.read(3_000_000)
            enc = r.headers.get_content_charset() or "utf-8"
            final = r.geturl()
    except Exception as e:  # noqa: BLE001 - a research probe records every failure and moves on
        return {"id": bp["id"], "url": url, "error": str(e)[:160]}
    p = Head()
    try:
        p.feed(raw.decode(enc, errors="replace"))
    except Exception as e:  # noqa: BLE001
        return {"id": bp["id"], "url": url, "error": "parse: %s" % e}

    def meta(key, attr="name"):
        for m in p.meta:
            if m.get(attr, "").lower() == key:
                return m.get("content", "")
        return None

    rels = [(l.get("rel", "").lower(), l) for l in p.links]
    desc = meta("description")
    return {
        "id": bp["id"], "url": url, "final": final, "lang": p.html_lang,
        "title": p.title, "title_len": len(p.title),
        "desc_len": len(desc) if desc is not None else None,
        "canonical": next((l.get("href") for r, l in rels if r == "canonical"), None),
        "robots": meta("robots"),
        "viewport": meta("viewport") is not None,
        "theme_color": meta("theme-color") is not None,
        "og": sorted({m.get("property", "").lower() for m in p.meta if m.get("property", "").lower().startswith("og:")}),
        "twitter": sorted({m.get("name", "").lower() for m in p.meta if m.get("name", "").lower().startswith("twitter:")}),
        "twitter_card": meta("twitter:card"),
        "hreflang": sum(1 for r, l in rels if r == "alternate" and l.get("hreflang")),
        "icon": any("icon" in r for r, _ in rels),
        "apple_icon": any(r == "apple-touch-icon" for r, _ in rels),
        "manifest": any(r == "manifest" for r, _ in rels),
        "preload": sum(1 for r, _ in rels if r == "preload"),
        "ld_types": ld_types(p.ld),
        "h1": p.h1,
        "imgs": len(p.imgs),
        "imgs_no_alt": sum(1 for i in p.imgs if "alt" not in i),
        "imgs_lazy": sum(1 for i in p.imgs if i.get("loading") == "lazy"),
        "imgs_sized": sum(1 for i in p.imgs if i.get("width") and i.get("height")),
    }


def main():
    out = Path(sys.argv[1])
    only = set(sys.argv[2:])
    bps = [json.loads(f.read_text(encoding="utf-8")) for f in sorted(BLUEPRINTS.glob("*.json"))]
    bps = [b for b in bps if b.get("source", {}).get("url") and (not only or b["id"] in only)]
    with cf.ThreadPoolExecutor(12) as ex:
        rows = list(ex.map(probe, bps))
    out.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
    print("probed %d sites, %d failed, wrote %s" % (len(rows), sum(1 for r in rows if "error" in r), out))


if __name__ == "__main__":
    main()
