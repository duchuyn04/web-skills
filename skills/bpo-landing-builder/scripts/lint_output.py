#!/usr/bin/env python3
"""Mechanical audit of a built page against the house copy rules (see references/content-rules.md) plus structural rules.
Standard library only.

Usage:
    python lint_output.py dist

Exit code 0 = clean, 1 = errors found. Warnings never fail the run.
Fix copy problems in page.json and rebuild. Never patch dist/ by hand.
"""
import json
import re
import sys
for _stream in (sys.stdout, sys.stderr):  # Vietnamese text must not crash printing on a cp1252 console or pipe
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import flat_css  # noqa: E402
import rules  # noqa: E402

TEXT_ATTRS = {"alt", "title", "aria-label", "placeholder", "content", "value"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
# Design checks and the rules version that added them. A site that build.py built with an older "rules" pin (see
# build-report.json) gets the newer ones as warnings; copy, accessibility and structure checks stay errors everywhere.
RULES_SINCE = {"gradient": 2, "caps-tracking": 2, "justify": 2, "slow-motion": 2, "glow": 2, "numbered-marker": 2, "dash-rule": 3}
CUSTOM_PROP_STYLE =re.compile(r"^\s*(--[\w-]+\s*:\s*[^;]+;?\s*)+$")


# a selector or at-rule followed by a declaration block, or a /* comment */, in visible text
STRAY_CODE = re.compile(r"/\*|(^|\s)[.#@][\w-][^{}\n]{0,160}\{[^{}]*:[^{}]*\}|\{\s*[\w-]+\s*:\s*[^;{}]+;[^{}]*\}")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.texts = []        # (line, text)
        self.attrs = []        # (line, tag, name, value)
        self.tags = []         # (line, tag, attrs dict)
        self.stack = []
        self.skip = 0          # inside script/style

    def handle_starttag(self, tag, attrs):
        line = self.getpos()[0]
        d = {k: (v if v is not None else "") for k, v in attrs}
        self.tags.append((line, tag, d))
        for k, v in d.items():
            if k in TEXT_ATTRS or k.startswith("data-") and k.endswith("label"):
                self.attrs.append((line, tag, k, v))
        if tag in ("script", "style"):
            self.skip += 1
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
        if tag in self.stack:
            while self.stack and self.stack.pop() != tag:
                pass

    def handle_data(self, data):
        if not self.skip and data.strip():
            self.texts.append((self.getpos()[0], data.strip()))


_PAGE = ["index.html"]  # the page being linted, for the file name in messages


def check_seo_head(src, tags, dist, add):
    """The head tags build.py writes (see references/seo.md). A page linted from an old dist fails until rebuilt."""
    head = src.split("</head>", 1)[0]
    metas = [a for _, t, a in tags if t == "meta"]

    def meta(attr, key):
        return [a.get("content", "") for a in metas if a.get(attr, "").lower() == key]
    html_tag = next((a for _, t, a in tags if t == "html"), {})
    if not html_tag.get("lang"):
        add("error", _PAGE[0], "seo-lang", "<html> has no lang attribute; search engines and screen readers read the language from it.")
    titles = re.findall(r"<title>(.*?)</title>", head, re.S)
    if len(titles) != 1 or not titles[0].strip():
        add("error", _PAGE[0], "seo-title", "expected one non-empty <title> in the head, found %d" % len(titles))
    if len([d for d in meta("name", "description") if d.strip()]) != 1:
        add("error", _PAGE[0], "seo-description", "expected one non-empty <meta name=\"description\">")
    for key in ("og:title", "og:description", "og:type"):
        if not meta("property", key):
            add("error", _PAGE[0], "seo-og", "missing <meta property=\"%s\">; shared links fall back to guesses without it" % key)
    if not meta("property", "og:image"):
        add("warn", _PAGE[0], "seo-og", "no og:image, so links shared on social sites show no picture")
    canon = [a.get("href", "") for _, t, a in tags if t == "link" and a.get("rel", "").lower() == "canonical"]
    if len(canon) > 1:
        add("error", _PAGE[0], "seo-canonical", "%d canonical links; a page carries at most one" % len(canon))
    if canon and not re.match(r"^https://[^/\s]+", canon[0]):
        add("error", _PAGE[0], "seo-canonical", "canonical %r must be an absolute https URL" % canon[0])
    icons = [a for _, t, a in tags if t == "link" and "icon" in a.get("rel", "").lower().split()]
    if not icons:
        add("error", _PAGE[0], "seo-favicon", "no <link rel=\"icon\">")
    elif all(a.get("href", "").lower().endswith(".svg") for a in icons):
        add("warn", _PAGE[0], "seo-favicon", "only an SVG favicon; Google Search shows BMP, GIF, ICO, PNG, JPEG, PPM or TIFF favicons only")
    for _, t, a in tags:
        if t == "link" and a.get("hreflang") and not re.match(r"^https://", a.get("href", "")):
            add("error", _PAGE[0], "seo-hreflang", "hreflang %s points to %r; alternates need full https addresses" % (a["hreflang"], a.get("href")))
    for blob in re.findall(r'<script type="application/ld\+json">(.*?)</script>', src, re.S):
        try:
            data = json.loads(blob)
        except ValueError as e:
            add("error", _PAGE[0], "json-ld", "structured data is not valid JSON: %s" % e)
            continue
        if not isinstance(data, dict) or "@context" not in data:
            add("error", _PAGE[0], "json-ld", "structured data has no @context")
    robots = " ".join(meta("name", "robots")).lower()
    sitemap = dist / "sitemap.xml"
    if sitemap.is_file():
        locs = re.findall(r"<loc>(.*?)</loc>", sitemap.read_text(encoding="utf-8"))
        listed = bool(canon) and canon[0] in locs if len(locs) > 1 else bool(locs)
        if "noindex" in robots and listed:
            add("error", "sitemap.xml", "seo-sitemap", "%s is noindex but the sitemap lists it; search consoles report the conflict" % _PAGE[0])
        if canon and locs and "noindex" not in robots and canon[0] not in locs:
            add("error", "sitemap.xml", "seo-sitemap", "does not list %s (the canonical link of %s)" % (canon[0], _PAGE[0]))
    # Headings that skip a level (h2 then h4) break the outline search engines and screen readers read.
    last = 0
    for line, t, _ in tags:
        if re.match(r"^h[1-6]$", t):
            level = int(t[1])
            if last and level > last + 1:
                add("warn", "%s:%d" % (_PAGE[0], line), "heading-skip", "<%s> follows <h%d>; use <h%d> or restyle it with CSS" % (t, last, last + 1))
            last = level



def lint_page(dist, path, add, files):
    """Every check on one built page. dist/index.html and, for a site, every other page next to it."""
    _PAGE[0] = path.name
    src = path.read_text(encoding="utf-8")
    page = Page()
    page.feed(src)

    # 1. Copy rules on visible text and text attributes.
    for line, text in page.texts:
        for f in rules.check_text(text):
            add(f.level, "%s:%d" % (_PAGE[0], line), f.code, "%s (near: \"%s\")" % (f.message, f.excerpt))
    for line, tag, name, value in page.attrs:
        if name == "content" and tag != "meta":
            continue
        for f in rules.check_text(value):
            add(f.level, "%s:%d <%s %s>" % (_PAGE[0], line, tag, name), f.code, "%s (near: \"%s\")" % (f.message, f.excerpt))

    # 1b. CSS or JS that slipped out of its file into the markup shows on the page as text (solution-panels in 4.1.0)
    for line, text in page.texts:
        if STRAY_CODE.search(text):
            add("error", "%s:%d" % (_PAGE[0], line), "stray-code", "visible text looks like CSS or a code comment (near: \"%s\"). A section template holds code outside <style> and <script>; move it into section.css or section.js." % text[:70])

    # 2. Characters that must not appear anywhere, code and comments included.
    for f in files:
        for line, fnd in rules.check_raw_file(f.read_text(encoding="utf-8")):
            add("error", "%s:%d" % (f.relative_to(dist), line), fnd.code, "%s (near: \"%s\")" % (fnd.message, fnd.excerpt))
    if "<!--" in src:
        add("error", _PAGE[0], "comment", "HTML comments left in output (their '-->' reads as a text arrow). Rebuild with build.py.")

    # 2b. Search and share metadata (scripts/seo.py writes it; references/seo.md).
    check_seo_head(src, page.tags, dist, add)

    # 3. Structure.
    tags = page.tags
    h1 = [t for t in tags if t[1] == "h1"]
    if len(h1) != 1:
        add("error", _PAGE[0], "h1", "expected exactly one <h1>, found %d" % len(h1))
    ids = {}
    for line, tag, a in tags:
        if "id" in a:
            if a["id"] in ids:
                add("error", "%s:%d" % (_PAGE[0], line), "dup-id", "id \"%s\" also used on line %d" % (a["id"], ids[a["id"]]))
            ids.setdefault(a["id"], line)
    for line, tag, a in tags:
        where = "%s:%d" % (_PAGE[0], line)
        if tag == "section" and not a.get("id"):
            add("error", where, "section-id", "<section> without id")
        if tag == "img":
            if "alt" not in a:
                add("error", where, "img-alt", "<img> without alt (use alt=\"\" only for decorative copies)")
        if tag == "svg" and a.get("aria-hidden") != "true" and a.get("role") != "img":
            add("error", where, "svg-a11y", "<svg> needs aria-hidden=\"true\" (decorative) or role=\"img\" with a label")
        if "style" in a and not CUSTOM_PROP_STYLE.match(a["style"]):
            add("error", where, "inline-style", "inline style \"%s\"; only CSS custom properties (--x: ...) are allowed inline" % a["style"][:60])
        if tag == "a":
            href = a.get("href", "")
            if href.startswith("#") and len(href) > 1 and href[1:] not in ids and href != "#top":
                add("error", where, "anchor", "link to %s but no element has that id" % href)
            if not href:
                add("error", where, "anchor", "<a> without href")
        if tag == "script" and a.get("src") and re.match(r"https?://", a["src"]):
            add("error", where, "external-script", "external script %s; all JS must be local" % a["src"])
        if tag == "link" and a.get("rel") == "stylesheet" and re.match(r"https?://", a.get("href", "")) and "fonts.googleapis.com" not in a["href"]:
            add("error", where, "external-css", "external stylesheet %s; only Google Fonts is allowed" % a["href"])
    _check_buttons(src, add)
    _check_headings(tags, add)
    # the stylesheets this page loads (a site writes one per page)
    own = [dist / h for _, t, a in page.tags if t == "link" and a.get("rel") == "stylesheet" for h in [a.get("href", "")] if h.startswith("assets/")]
    sheets = [(str(f.relative_to(dist)), f.read_text(encoding="utf-8")) for f in (own or sorted((dist / "assets").rglob("*.css"))) if f.is_file()]
    sheets.append((_PAGE[0] + " <style>", "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", src, re.S))))
    _check_flat(sheets, add)
    css_all = "\n".join(css for _, css in sheets)
    _check_design_css(css_all, add)
    _check_design_html(src, add)

    return page, ids


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    dist = Path(sys.argv[1]).resolve()
    index = dist / "index.html"
    if not index.is_file():
        print("No index.html in %s. Run build.py first." % dist)
        return 2
    errors, warns = [], []
    try:
        # the rules version build.py wrote; an older one means the site pins "rules" in page.json
        pinned = int(json.loads((dist / "build-report.json").read_text(encoding="utf-8")).get("rules", 99))
    except (OSError, ValueError, TypeError):
        pinned = 99

    def add(level, where, code, msg):
        if level == "error" and RULES_SINCE.get(code, 0) > pinned:
            level, msg = "warn", "[rules %d, not enforced] %s" % (pinned, msg)
        (errors if level == "error" else warns).append("%s [%s] %s" % (where, code, msg))

    pages = [index] + sorted(f for f in dist.glob("*.html") if f.name != "index.html")
    shared = sorted((dist / "assets").rglob("*.css")) + sorted((dist / "assets").rglob("*.js"))
    files = pages + shared
    texts = attrs = 0
    page_ids, links = {}, []
    for i, path in enumerate(pages):
        # assets are checked once, with the first page
        page, ids = lint_page(dist, path, add, [path] + (shared if i == 0 else []))
        texts, attrs = texts + len(page.texts), attrs + len(page.attrs)
        page_ids[path.name] = ids
        links += [(path.name, line, a.get("href", "")) for line, t, a in page.tags if t == "a"]
    # links between the pages of a site (about.html, contact.html#form); a single page may link to pages hosted elsewhere
    try:
        is_site = bool(json.loads((dist / "build-report.json").read_text(encoding="utf-8")).get("site"))
    except (OSError, ValueError, AttributeError):
        is_site = False
    for name, line, href in (links if is_site else []):
        m = re.match(r"^([\w-]+\.html)(?:#([A-Za-z][\w-]*))?$", href)
        if not m:
            continue
        if m.group(1) not in page_ids:
            add("error", "%s:%d" % (name, line), "page-link", "link to %s, which is not in %s" % (href, dist.name))
        elif m.group(2) and m.group(2) not in page_ids[m.group(1)] and m.group(2) != "top":
            add("error", "%s:%d" % (name, line), "page-link", "link to %s but %s has no element with that id" % (href, m.group(1)))

    for w in warns:
        print("WARN  " + w)
    for e in errors:
        print("ERROR " + e)
    print("\nChecked %d page(s): %d text nodes, %d attributes, %d files." % (len(pages), texts, attrs, len(files)))
    if errors:
        print("LINT FAILED with %d error(s). Fix page.json (or the template for structural errors), rebuild, lint again." % len(errors))
        return 1
    print("LINT PASSED (%d warning(s))." % len(warns))
    return 0


# Flat style (references/flat-style.md; the checks live in scripts/flat_css.py, the same file in every skill):
# gradients only for scrims, edge fades, one-hue shading and hard-stop patterns; neutral shadows, and only on what
# floats or on a drawn 3D object.
FLAT_FAMILIES = flat_css.families([
    ("second accent", r"--(?:c-accent-2|accent-2-ink|c-accent-blend(?:-deep)?)\b"),
    ("accent", r"--(?:c-accent(?:-on-dark|-soft)?|accent-ink)\)"),
    ("primary", r"--c-primary\)", True),
])
# flat_css codes as this skill reports them, and a level that overrides flat_css's. The shadow and hover checks came
# after rules 5 and stay warnings, so a custom section that built before still builds; the library itself passes
# tools/check_flat_css.py with none of them.
FLAT_CODES = {"gradient-text": ("gradient", None), "gradient": ("gradient", None), "blur-blob": ("gradient", None),
              "glow": ("glow", None), "glass": ("glass", "warn"), "resting-shadow": ("resting-shadow", "warn"),
              "hover-shadow": ("hover-shadow", "warn"), "hover-lift": ("hover-lift", "warn")}


def _check_flat(sheets, add):
    tokens = {}
    for _, css in sheets:
        tokens.update(flat_css.tokens_in(css))
    for where, css in sheets:
        for f in flat_css.check(css, FLAT_FAMILIES, tokens):
            code, level = FLAT_CODES.get(f.code, (f.code, None))
            add(level or f.level, "%s %s" % (where, f.selector[:60]), code, f.message)


# Design tells of generated pages (references/anti-slop.md).
DURATION_RE = re.compile(r"(?<![\w-])(\d*\.?\d+)(ms|s)\b")
VAGUE_LABELS = {"submit", "learn more", "read more", "click here", "more", "details"}


def _seconds(v, unit):
    return float(v) / 1000 if unit == "ms" else float(v)


def _check_design_css(css, add):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"@keyframes[^{]*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}", "", css)
    seen = set()
    for block in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        selector, body = " ".join(block.group(1).split()), block.group(2)
        if selector.startswith("@"):
            continue
        at = selector[:70]

        def once(code, msg, level="error"):
            key = (code, at)
            if key not in seen:
                seen.add(key)
                add(level, "css " + at, code, msg)
        if re.search(r"::?(before|after)\b", selector) and re.search(r"content\s*:\s*(\"\"|'')", body) and "absolute" not in body:
            h = re.search(r"(?<![-\w])height\s*:\s*([\d.]+)px", body)
            w = re.search(r"(?<![-\w])width\s*:\s*([\d.]+)(rem|em|px)", body)
            if h and w and float(h.group(1)) <= 3:
                wpx = float(w.group(1)) * (16 if w.group(2) != "px" else 1)
                if 8 <= wpx <= 64:
                    once("dash-rule", "a short line drawn in front of or after text (%s wide, %spx high) reads as a dash; drop it or use spacing" % (w.group(1) + w.group(2), h.group(1)))
        if re.search(r"text-transform\s*:\s*uppercase", body):
            m = re.search(r"letter-spacing\s*:\s*(-?[\d.]+)em", body)
            if m and not 0.05 <= float(m.group(1)) <= 0.12:
                once("caps-tracking", "uppercase text tracked %sem; caps need 0.05-0.12em" % m.group(1))
        if re.search(r"text-align\s*:\s*justify", body):
            once("justify", "justified text leaves uneven gaps between words (WCAG 1.4.8); align left")
        if "[data-reveal]" in selector or ":hover" in selector:
            for prop in re.findall(r"(?:transition|animation)(?:-duration)?\s*:\s*([^;]+)", body):
                longest = max((_seconds(v, u) for v, u in DURATION_RE.findall(prop.split("calc(")[0])), default=0)
                # hovers answer the pointer (0.1-0.5s); scroll entrances on real BPO sites run 0.6-1s (references/motion-research.md)
                limit = 0.5 if ":hover" in selector else 1.2
                if longest > limit:
                    once("slow-motion", "%.2fs on a %s; %s" % (longest, "hover" if limit == 0.5 else "scroll reveal",
                         "hover motion stays within 0.1-0.5s" if limit == 0.5 else "entrances stay within 1.2s"))


def _check_design_html(src, add):
    # numbered markers only in sections that are a sequence
    for sec in re.finditer(r"<section\b([^>]*)>(.*?)</section>", src, re.S):
        if "data-sequence" in sec.group(1):
            continue
        m = re.search(r'class="[^"]*__(?:num|n)\b[^"]*"[^>]*>\s*0\d\s*<', sec.group(2))
        if m:
            sid = re.search(r'id="([^"]+)"', sec.group(1))
            add("error", "section #%s" % (sid.group(1) if sid else "?"), "numbered-marker",
                "01/02 markers on content that is not a sequence; number only process steps and timelines (add data-sequence to such a section)")
    # CTA labels and arrows
    links = re.findall(r"<(a|button)\b([^>]*)>(.*?)</\1>", src, re.S)
    ctas = arrows = 0
    by_text = {}
    for tag, attrs, inner in links:
        cls = re.search(r'class="([^"]*)"', attrs)
        cls = cls.group(1) if cls else ""
        label = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", inner)).strip()
        if re.search(r"\bbl-(?:btn|link)\b", cls):
            ctas += 1
            if "arrow-icon" in inner:
                arrows += 1
            if label.lower() in VAGUE_LABELS and "aria-label" not in attrs:
                add("warn", "<%s> %s" % (tag, label), "cta-label", "the label does not say what happens; name the action or the destination (\"Get a quote\", \"See case studies\")")
        href = re.search(r'href="([^"#][^"]*|#[^"]+)"', attrs)
        if tag == "a" and href and label and len(label) < 40:
            by_text.setdefault(label.lower(), set()).add(href.group(1))
    for label, hrefs in by_text.items():
        if len(hrefs) > 1 and label in VAGUE_LABELS:
            add("warn", "links \"%s\"" % label, "cta-label", "the same link text points to %d places; give each its own label" % len(hrefs))
    if ctas >= 6 and arrows > ctas / 2:
        add("warn", _PAGE[0], "cta-arrows", "%d of %d buttons and links carry an arrow; keep arrows for text links that go somewhere" % (arrows, ctas))


def _check_buttons(src, add):
    for m in re.finditer(r"<button\b([^>]*)>(.*?)</button>", src, re.S):
        attrs, inner = m.group(1), m.group(2)
        text = re.sub(r"<svg.*?</svg>", "", inner, flags=re.S)
        text = re.sub(r"<[^>]+>", "", text).strip()
        if not text and "aria-label" not in attrs:
            line = src.count("\n", 0, m.start()) + 1
            add("error", "%s:%d" % (_PAGE[0], line), "button-name", "button has no text and no aria-label")


def _check_headings(tags, add):
    last = 0
    for line, tag, _ in tags:
        if re.fullmatch(r"h[1-6]", tag):
            lvl = int(tag[1])
            if last and lvl > last + 1:
                add("warn", "%s:%d" % (_PAGE[0], line), "heading-order", "<%s> follows <h%d>; a level is skipped" % (tag, last))
            last = lvl


if __name__ == "__main__":
    sys.exit(main())
