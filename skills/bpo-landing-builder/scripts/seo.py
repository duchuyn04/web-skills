"""Search and share metadata for a built page: the <head> tags, JSON-LD, favicon, robots.txt and sitemap.xml.
Rules and the measurements behind them: references/seo.md (85 real BPO homepages, scripts/research/seo_probe.py).

build.py calls check(ctx, top, sections) before rendering and head(...) / files(...) after.
"""
import hashlib
import html
import json
import re
import struct
from datetime import date
from urllib.parse import urljoin, urlsplit

SPEC = {"type": "object", "required": False, "fields": {
    "url": {"type": "text", "min": 12, "max": 200, "required": False},
    "image": {"type": "image", "required": False},
    "image_alt": {"type": "text", "min": 10, "max": 120, "required": False},
    "icon": {"type": "image", "required": False},
    "locale": {"type": "text", "min": 5, "max": 5, "required": False},
    "index": {"type": "bool", "default": True},
    # content of the verification meta tags that Google Search Console and Bing Webmaster Tools hand out
    "google_verification": {"type": "text", "min": 10, "max": 100, "required": False},
    "bing_verification": {"type": "text", "min": 10, "max": 100, "required": False},
    # the same page in other languages, this one included: {"lang": "vi", "url": "https://.../vi/"}; "x-default" allowed
    "alternates": {"type": "list", "min": 2, "max": 10, "required": False, "item": {"type": "object", "fields": {
        "lang": {"type": "text", "min": 2, "max": 9},
        "url": {"type": "text", "min": 12, "max": 200},
    }}},
}}

LOCALES = {"en": "en_US", "vi": "vi_VN", "ja": "ja_JP", "ko": "ko_KR", "de": "de_DE", "fr": "fr_FR",
           "es": "es_ES", "pt": "pt_BR", "zh": "zh_CN"}
LOCALE_RE = re.compile(r"^[a-z]{2}_[A-Z]{2}$")
HREFLANG_RE = re.compile(r"^([a-z]{2})(-[A-Z]{2})?$|^x-default$")
# Google sets no length limit for titles or descriptions; it cuts them to the device width. The limits are the
# upper quartile of 85 measured BPO homepages (titles median 54, p75 61; descriptions median 151, p75 161).
TITLE_MAX = 60
DESC_MAX = 160
IMG_MIN_W = 600  # Facebook and LinkedIn show a small card below 600 px wide; Meta asks for 1200 x 630
LOGO_MIN = 112   # Google: an Organization logo is at least 112 x 112 px
FAVICON_PX = 192  # Google Search: a square PNG or ICO, larger than 48 px; SVG favicons are not shown in results
SAMPLE_RE = re.compile(r"\[|\bexample\.(com|org|net)\b|\.example\b", re.I)
IMG_SRC_RE = re.compile(r'<img\b[^>]*\bsrc="(assets/img/[^"]+)"')
POSTER_RE = re.compile(r'<video\b[^>]*\bposter="(assets/img/[^"]+)"')  # a video hero's still frame
BG_SRC_RE = re.compile(r"url\((?:'|&#39;|\")?(assets/img/[^'\")&]+)")


def check(ctx, top, sections, is_example):
    """Findings on the page's title, description and seo block. New fields fail when malformed; everything
    that a page built before could trip is a warning, so rules stay at 5."""
    site = top.get("site") or {}
    seo = top.get("seo") or {}
    title, desc, brand = site.get("title") or "", site.get("description") or "", site.get("brand") or ""
    if len(title) > TITLE_MAX:
        ctx.warn("site.title", "%d characters. Google cuts titles to the width of the screen, and three quarters of 85 BPO homepages stay within %d, so the end of this one may not show. Put the service and the brand first." % (len(title), TITLE_MAX))
    if brand and brand.lower() not in title.lower() and not SAMPLE_RE.search(brand):
        ctx.warn("site.title", "does not name the brand. 71 of 85 BPO homepages measured end the title with it, like \"Offshore accounting teams | %s\"." % brand)
    if len(desc) > DESC_MAX:
        ctx.warn("site.description", "%d characters. Google cuts snippets to the width of the screen, and three quarters of 85 BPO homepages stay near %d, so the last words may not show." % (len(desc), DESC_MAX))
    if title and desc and desc.lower().startswith(title.lower()):
        ctx.warn("site.description", "starts with the title. Search results show both, so the description should add what the title leaves out (services, location, who it is for).")
    url = seo.get("url")
    if url:
        parts = urlsplit(url)
        if parts.scheme != "https" or not parts.netloc or parts.query or parts.fragment:
            ctx.err("seo.url", "must be the page's live https address with no query or #fragment, like \"https://www.example.com/\".")
        elif not (parts.path in ("", "/") or parts.path.endswith("/") or parts.path.endswith(".html")):
            ctx.err("seo.url", "must end with / or .html (the address of the folder or file index.html is served from), so relative image paths resolve to the right place.")
    elif not is_example:
        ctx.warn("seo.url", "not set, so the page has no canonical link, og:url, sitemap.xml or robots.txt, and share images are relative. Add \"seo\": {\"url\": \"https://...\"} once the live address is known.")
    loc = seo.get("locale")
    if loc and not LOCALE_RE.match(loc):
        ctx.err("seo.locale", "must look like \"vi_VN\" or \"en_GB\" (a language code, then _ and a country code).")
    if seo.get("image") and seo["image"].lower().endswith(".svg"):
        ctx.err("seo.image", "social networks do not render SVG share images. Use a JPG or PNG, ideally 1200 x 630.")
    for k in ("google_verification", "bing_verification"):
        if seo.get(k) and not re.match(r"^[\w-]+$", seo[k]):
            ctx.err("seo." + k, "paste only the content value of the tag (letters, digits, - and _), not the whole <meta> tag.")
    if seo.get("image") and not seo.get("image_alt"):
        ctx.warn("seo.image_alt", "describe the share image in a sentence for screen readers on social sites.")
    if seo.get("icon") and seo["icon"].lower().endswith(".svg"):
        ctx.warn("seo.icon", "Google Search shows only BMP, GIF, ICO, PNG, JPEG, PPM or TIFF favicons, so this SVG icon works in browsers but not in search results. Give a square PNG of 192 px or more.")
    alts = seo.get("alternates") or []
    if alts:
        own = [a for a in alts if a["url"] == url]
        if not url:
            ctx.err("seo.alternates", "needs seo.url: every language version lists itself and the others by full address.")
        elif not own:
            ctx.err("seo.alternates", "must list this page too (%s). Google ignores hreflang links that are not returned from both sides." % url)
        elif own[0]["lang"].split("-")[0] != top.get("lang", "en"):
            ctx.err("seo.alternates", "lists this page as %r but the page language is %r." % (own[0]["lang"], top.get("lang", "en")))
        seen = set()
        for i, a in enumerate(alts):
            p = "seo.alternates[%d]" % i
            if not HREFLANG_RE.match(a["lang"]):
                ctx.err(p + ".lang", "must be a language code like \"en\" or \"vi\", optionally with a region (\"en-GB\"), or \"x-default\". Country codes alone do not work, and the UK is GB.")
            if not a["url"].startswith("https://") or "#" in a["url"]:
                ctx.err(p + ".url", "must be a full https address without a #fragment.")
            if a["lang"] in seen:
                ctx.err(p + ".lang", "%r is listed twice." % a["lang"])
            seen.add(a["lang"])


def image_size(path):
    """(width, height) of a PNG, JPEG, GIF or WebP file, or None. Standard library only."""
    try:
        with open(path, "rb") as f:
            head = f.read(32)
            if head[:8] == b"\x89PNG\r\n\x1a\n":
                return struct.unpack(">II", head[16:24])
            if head[:6] in (b"GIF87a", b"GIF89a"):
                return struct.unpack("<HH", head[6:10])
            if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
                kind = head[12:16]
                if kind == b"VP8X":
                    return (1 + int.from_bytes(head[24:27], "little"), 1 + int.from_bytes(head[27:30], "little"))
                if kind == b"VP8 ":
                    f.seek(26)
                    w, h = struct.unpack("<HH", f.read(4))
                    return (w & 0x3FFF, h & 0x3FFF)
                if kind == b"VP8L":
                    b = head[21:25]
                    return (1 + (((b[1] & 0x3F) << 8) | b[0]), 1 + (((b[3] & 0xF) << 10) | (b[2] << 2) | ((b[1] & 0xC0) >> 6)))
                return None
            if head[:2] == b"\xff\xd8":
                f.seek(2)
                while True:
                    marker = f.read(2)
                    if len(marker) < 2 or marker[0] != 0xFF:
                        return None
                    if marker[1] in (0xD8, 0x01) or 0xD0 <= marker[1] <= 0xD7:
                        continue
                    seg = struct.unpack(">H", f.read(2))[0]
                    if 0xC0 <= marker[1] <= 0xCF and marker[1] not in (0xC4, 0xC8, 0xCC):
                        h, w = struct.unpack(">xHH", f.read(5))
                        return (w, h)
                    f.seek(seg - 2, 1)
    except (OSError, struct.error):
        return None
    return None


def share_image(ctx, seo, body):
    """The share image: seo.image, else the hero's first photo, else the first photo on the page."""
    if seo.get("image"):
        return seo["image"], seo.get("image_alt") or ""
    hero = next((m for g, m in body if g == "hero"), "")
    for markup in [hero] + [m for g, m in body if g not in ("hero", "header", "footer")]:
        for rx in (IMG_SRC_RE, POSTER_RE, BG_SRC_RE):
            m = rx.search(markup)
            if m and not m.group(1).lower().endswith(".svg"):
                alt = re.search(r'(?:alt|aria-label)="([^"]*)"', markup[m.start():m.start() + 400])
                return html.unescape(m.group(1)), html.unescape(alt.group(1)) if alt else ""
    return None, ""


def clean(value):
    """Structured data carries real facts only: placeholders and example.com addresses are dropped."""
    if not isinstance(value, str) or not value.strip() or SAMPLE_RE.search(value):
        return None
    return value.strip()


def gather(sections):
    """Contacts, social profiles, offices and FAQ items the page already shows."""
    out = {"phones": [], "emails": [], "same_as": [], "offices": [], "faq": []}
    for s in sections:
        d = s["data"] or {}
        for c in d.get("contacts") or []:
            href = (c or {}).get("href") or ""
            if href.startswith("tel:") and clean(c.get("label")):
                out["phones"].append(href[4:].strip())
            elif href.startswith("mailto:") and clean(href[7:]):
                out["emails"].append(href[7:].strip())
        for so in d.get("socials") or []:
            href = clean((so or {}).get("href"))
            if href and href.startswith("https://") and href not in out["same_as"]:
                out["same_as"].append(href)
        for o in d.get("offices") or []:
            addr = clean((o or {}).get("address"))
            if addr:
                out["offices"].append({"address": addr, "city": clean(o.get("city")), "phone": clean(o.get("phone")),
                                       "email": clean(o.get("email")), "name": clean(o.get("name"))})
        if s["variant"].get("group") == "faq":
            for it in d.get("items") or []:
                q, a = clean((it or {}).get("q")), clean((it or {}).get("a"))
                if q and a:
                    out["faq"].append((q, a))
    for k in ("phones", "emails"):
        out[k] = list(dict.fromkeys(out[k]))
    return out


def plain(text):
    """FAQ answers may carry *highlight* and **bold** markup; structured data takes the words only."""
    return re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", text)


def build(ctx, top, site, sections, body, preset, placeholders, prev_report=None):
    """Returns (head_html, files, record). files maps output names to text (robots.txt, sitemap.xml, favicon);
    record goes into build-report.json so the next build keeps the sitemap lastmod while the content is unchanged."""
    seo = top.get("seo") or {}
    lang = top.get("lang", "en")
    url = seo.get("url")
    index = seo.get("index", True) and not placeholders
    if seo.get("index", True) and placeholders:
        ctx.warn("seo.index", "the page still has %d placeholder(s), so it is built with noindex and without sitemap.xml. It becomes indexable once they are replaced with the client's facts." % len(placeholders))
    absolute = (lambda rel: urljoin(url, rel)) if url else (lambda rel: rel)
    files = {}
    tags = []

    def meta(attr, key, value):
        if value:
            tags.append('<meta %s="%s" content="%s">' % (attr, key, html.escape(str(value), quote=True)))

    meta("name", "robots", "index, follow, max-image-preview:large" if index else "noindex, nofollow")
    meta("name", "google-site-verification", seo.get("google_verification"))
    meta("name", "msvalidate.01", seo.get("bing_verification"))
    if url:
        tags.append('<link rel="canonical" href="%s">' % html.escape(url, quote=True))
    for a in seo.get("alternates") or []:
        tags.append('<link rel="alternate" hreflang="%s" href="%s">' % (html.escape(a["lang"], quote=True), html.escape(a["url"], quote=True)))
    img, img_alt = share_image(ctx, seo, body)
    size = None
    if img:
        src = ctx.images.get(img)
        size = image_size(src) if src else None
        if size and size[0] < IMG_MIN_W:
            ctx.warn("seo.image", "the share image %s is %d px wide; Facebook and LinkedIn show a small card below %d px. Use a 1200 x 630 photo." % (img, size[0], IMG_MIN_W))
    else:
        ctx.warn("seo.image", "no photo on the page to use as the share image, so links shared on social sites show no picture. Add \"seo\": {\"image\": \"...\"} (1200 x 630 JPG or PNG).")
    meta("property", "og:type", "website")
    meta("property", "og:site_name", site.get("brand"))
    meta("property", "og:locale", seo.get("locale") or LOCALES.get(lang))
    meta("property", "og:title", share_title(site.get("title") or "", site.get("brand") or ""))
    meta("property", "og:description", site.get("description"))
    if url:
        meta("property", "og:url", url)
    if img:
        meta("property", "og:image", absolute(img))
        if size:
            meta("property", "og:image:width", size[0])
            meta("property", "og:image:height", size[1])
        meta("property", "og:image:alt", img_alt)
    meta("name", "twitter:card", "summary_large_image" if img else "summary")

    # Favicon: the client's square icon, else a monogram in the page's dark colour, as SVG for browsers and as a
    # PNG, the format Google Search shows next to results.
    icon = seo.get("icon")
    if icon:
        isize = image_size(ctx.images.get(icon)) if ctx.images.get(icon) else None
        if isize and isize[0] != isize[1]:
            ctx.warn("seo.icon", "is %d x %d; Google Search and browsers need a square favicon." % isize)
        kind = "image/svg+xml" if icon.lower().endswith(".svg") else "image/png"
        tags.append('<link rel="icon" href="%s" type="%s">' % (html.escape(icon, quote=True), kind))
        if kind == "image/png":
            tags.append('<link rel="apple-touch-icon" href="%s">' % html.escape(icon, quote=True))
    else:
        color = (top.get("theme") or {}).get("primary") or preset["colors"]["primary"]
        mark = site.get("brand_mark") or ""
        files["assets/img/favicon.svg"] = monogram(mark, color)
        files["assets/img/favicon.png"] = monogram_png(mark, color, FAVICON_PX)
        tags.append('<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">')
        tags.append('<link rel="icon" href="assets/img/favicon.png" sizes="%dx%d" type="image/png">' % (FAVICON_PX, FAVICON_PX))
        tags.append('<link rel="apple-touch-icon" href="assets/img/favicon.png">')
    if site.get("logo") and ctx.images.get(site["logo"]):
        lsize = image_size(ctx.images[site["logo"]])
        if lsize and min(lsize) < LOGO_MIN:
            ctx.warn("site.logo", "is %d x %d; Google uses an Organization logo only when it is at least %d x %d px." % (lsize[0], lsize[1], LOGO_MIN, LOGO_MIN))

    tags.append('<script type="application/ld+json">%s</script>' % json_ld(site, top, sections, url, absolute, img, lang))
    digest = hashlib.sha256("\n".join([site.get("title") or "", site.get("description") or ""] + [m for _, m in body]).encode("utf-8")).hexdigest()[:16]
    prev = (prev_report or {}).get("seo") or {}
    lastmod = prev.get("lastmod") if prev.get("content") == digest and prev.get("lastmod") else date.today().isoformat()
    record = {"content": digest, "lastmod": lastmod, "index": bool(index), "url": url}
    if url and index:
        folder = urlsplit(url).path.rsplit("/", 1)[0] + "/"
        sitemap_url = urljoin(url, folder + "sitemap.xml")
        if folder == "/":
            files["robots.txt"] = "User-agent: *\nAllow: /\n\nSitemap: %s\n" % sitemap_url
        else:
            # robots.txt, the favicon in results and the site name only count at the root of the host
            ctx.warn("seo.url", "the page sits in %s, not at the root of %s. Crawlers read robots.txt only at the root, so none is written: add the line \"Sitemap: %s\" to the root robots.txt, and note that Google takes the favicon and site name from the root page." % (folder, urlsplit(url).netloc, sitemap_url))
        files["sitemap.xml"] = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                "  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n  </url>\n</urlset>\n" % (html.escape(url), lastmod))
    return "\n".join(tags), files, record


def json_ld(site, top, sections, url, absolute, img, lang):
    base = ("%s://%s/" % (urlsplit(url).scheme, urlsplit(url).netloc)) if url else ""
    page = url or ""
    facts = gather(sections)
    org = {"@type": "Organization", "@id": base + "#organization", "name": site["brand"], "description": site.get("description")}
    if base:
        org["url"] = base
    if site.get("logo"):
        org["logo"] = {"@type": "ImageObject", "url": absolute(site["logo"])}
    if facts["same_as"]:
        org["sameAs"] = facts["same_as"]
    if facts["phones"]:
        org["telephone"] = facts["phones"][0]
    if facts["emails"]:
        org["email"] = facts["emails"][0]
    if facts["offices"]:
        org["address"] = [dict({"@type": "PostalAddress", "streetAddress": o["address"]}, **({"addressLocality": o["city"]} if o["city"] else {}))
                          for o in facts["offices"]]
    graph = [org,
             {"@type": "WebSite", "@id": base + "#website", "name": site["brand"], "inLanguage": lang, "publisher": {"@id": base + "#organization"}},
             {"@type": "WebPage", "@id": page + "#webpage", "name": site.get("title"), "description": site.get("description"), "inLanguage": lang,
              "isPartOf": {"@id": base + "#website"}, "about": {"@id": base + "#organization"}}]
    if base:
        graph[1]["url"] = base
        graph[2]["url"] = page
    if img:
        graph[2]["primaryImageOfPage"] = {"@type": "ImageObject", "url": absolute(img)}
    if facts["faq"]:
        graph.append({"@type": "FAQPage", "@id": page + "#faq", "isPartOf": {"@id": page + "#webpage"}, "mainEntity": [
            {"@type": "Question", "name": plain(q), "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for q, a in facts["faq"]]})
    text = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    return text.replace("</", "<\\/").replace("<!--", "<\\!--")


def monogram(mark, color):
    """A square SVG favicon: the brand mark in white (or ink on a light colour) on the page's dark colour."""
    r, g, b = (int(color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    ink = "#0b0f19" if lum > 0.55 else "#ffffff"
    size = 34 if len(mark) <= 1 else 28 if len(mark) == 2 else 21
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
            '<rect width="64" height="64" rx="14" fill="%s"/>'
            '<text x="32" y="33" text-anchor="middle" dominant-baseline="central" fill="%s" '
            'font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="%d" font-weight="700">%s</text></svg>\n'
            % (color, ink, size, html.escape(mark)))


def share_title(title, brand):
    """og:title without the brand: Meta asks for the title "without any branding such as your site name", and
    og:site_name already carries it."""
    if not brand:
        return title
    b = re.escape(brand)
    short = re.sub(r"\s*[|:\-]\s*%s\s*$" % b, "", title, flags=re.I)
    short = re.sub(r"^\s*%s\s*[|:\-]\s*" % b, "", short, flags=re.I)
    return short if len(short) >= 10 else title


FONT_FILES = ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
              "/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/Library/Fonts/Arial Bold.ttf"]
# 5 x 7 capitals and digits for machines without Pillow; each glyph is 7 rows of 5 bits.
GLYPHS = {
    "A": "01110100011000111111100011000110001", "B": "11110100011000111110100011000111110",
    "C": "01110100011000010000100001000101110", "D": "11110100011000110001100011000111110",
    "E": "11111100001000011110100001000011111", "F": "11111100001000011110100001000010000",
    "G": "01110100011000010111100011000101111", "H": "10001100011000111111100011000110001",
    "I": "01110001000010000100001000010001110", "J": "00111000100001000010000101001001100",
    "K": "10001100101010011000101001001010001", "L": "10000100001000010000100001000011111",
    "M": "10001110111010110101100011000110001", "N": "10001100011100110101100111000110001",
    "O": "01110100011000110001100011000101110", "P": "11110100011000111110100001000010000",
    "Q": "01110100011000110001101011001001101", "R": "11110100011000111110101001001010001",
    "S": "01111100001000001110000010000111110", "T": "11111001000010000100001000010000100",
    "U": "10001100011000110001100011000101110", "V": "10001100011000110001100010101000100",
    "W": "10001100011000110101101011010101010", "X": "10001100010101000100010101000110001",
    "Y": "10001100010101000100001000010000100", "Z": "11111000010001000100010001000011111",
    "0": "01110100011001110101110011000101110", "1": "00100011000010000100001000010001110",
    "2": "01110100010000100010001000100011111", "3": "11111000100010000010000011000101110",
    "4": "00010001100101010010111110001000010", "5": "11111100001111000001000011000101110",
    "6": "00110010001000011110100011000101110", "7": "11111000010001000100010000100001000",
    "8": "01110100011000101110100011000101110", "9": "01110100011000101111000010001001100",
}


def _ink(color):
    r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    return (r, g, b), ((11, 15, 25) if (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255 > 0.55 else (255, 255, 255))


def monogram_png(mark, color, size):
    """The monogram as a square PNG (Google Search does not show SVG favicons). Pillow with a bold system font when
    available, else a pure-Python 5 x 7 bitmap face."""
    bg, ink = _ink(color)
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io
        font_file = next((f for f in FONT_FILES if __import__("os").path.isfile(f)), None)
        s = size * 4
        img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((0, 0, s - 1, s - 1), radius=int(s * 14 / 64), fill=bg + (255,))
        px = int(s * (0.53 if len(mark) <= 1 else 0.44 if len(mark) == 2 else 0.33))
        font = ImageFont.truetype(font_file, px) if font_file else ImageFont.load_default(px)
        d.text((s / 2, s / 2), mark, font=font, fill=ink + (255,), anchor="mm")
        buf = io.BytesIO()
        img.resize((size, size), Image.LANCZOS).save(buf, "PNG", optimize=True)
        return buf.getvalue()
    except (ImportError, OSError, TypeError, ValueError):
        return _bitmap_png(mark, bg, ink, size)


def _bitmap_png(mark, bg, ink, size):
    import zlib
    chars = [c for c in mark.upper() if c in GLYPHS][:3] or ["?"]
    chars = [c for c in chars if c in GLYPHS]
    scale = max(1, int(size * (0.62 if len(chars) <= 1 else 0.7 if len(chars) == 2 else 0.8) / (6 * len(chars) - 1)))
    scale = min(scale, int(size * 0.5 / 7))
    w, h = (6 * len(chars) - 1) * scale, 7 * scale
    x0, y0 = (size - w) // 2, (size - h) // 2
    rad = size * 14 / 64
    rows = []
    for y in range(size):
        row = bytearray([0])
        for x in range(size):
            # anti-aliased rounded square: distance from the pixel centre to the inner rectangle
            cx, cy = min(max(x + 0.5, rad), size - rad), min(max(y + 0.5, rad), size - rad)
            dist = ((x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2) ** 0.5 - rad
            a = int(255 * min(1.0, max(0.0, 0.5 - dist)))
            col = bg
            gx, gy = (x - x0), (y - y0)
            if chars and 0 <= gx < w and 0 <= gy < h:
                ci, cx_ = divmod(gx // scale, 6)
                if cx_ < 5 and GLYPHS[chars[ci]][(gy // scale) * 5 + cx_] == "1":
                    col = ink
            row += bytes(col) + bytes([a])
        rows.append(bytes(row))

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(b"".join(rows), 9)) + chunk(b"IEND", b""))
