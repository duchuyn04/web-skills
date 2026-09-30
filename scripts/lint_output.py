#!/usr/bin/env python3
"""Mechanical audit of a built page against the house copy rules (see references/content-rules.md) plus structural rules.
Standard library only.

Usage:
    python lint_output.py dist

Exit code 0 = clean, 1 = errors found. Warnings never fail the run.
Fix copy problems in page.json and rebuild. Never patch dist/ by hand.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rules  # noqa: E402

TEXT_ATTRS = {"alt", "title", "aria-label", "placeholder", "content", "value"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
CUSTOM_PROP_STYLE = re.compile(r"^\s*(--[\w-]+\s*:\s*[^;]+;?\s*)+$")


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

    def add(level, where, code, msg):
        (errors if level == "error" else warns).append("%s [%s] %s" % (where, code, msg))

    src = index.read_text(encoding="utf-8")
    page = Page()
    page.feed(src)

    # 1. Copy rules on visible text and text attributes.
    for line, text in page.texts:
        for f in rules.check_text(text):
            add(f.level, "index.html:%d" % line, f.code, "%s (near: \"%s\")" % (f.message, f.excerpt))
    for line, tag, name, value in page.attrs:
        if name == "content" and tag != "meta":
            continue
        for f in rules.check_text(value):
            add(f.level, "index.html:%d <%s %s>" % (line, tag, name), f.code, "%s (near: \"%s\")" % (f.message, f.excerpt))

    # 2. Characters that must not appear anywhere, code and comments included.
    files = [index] + sorted((dist / "assets").rglob("*.css")) + sorted((dist / "assets").rglob("*.js"))
    for f in files:
        for line, fnd in rules.check_raw_file(f.read_text(encoding="utf-8")):
            add("error", "%s:%d" % (f.relative_to(dist), line), fnd.code, "%s (near: \"%s\")" % (fnd.message, fnd.excerpt))
    if "<!--" in src:
        add("error", "index.html", "comment", "HTML comments left in output (their '-->' reads as a text arrow). Rebuild with build.py.")

    # 3. Structure.
    tags = page.tags
    h1 = [t for t in tags if t[1] == "h1"]
    if len(h1) != 1:
        add("error", "index.html", "h1", "expected exactly one <h1>, found %d" % len(h1))
    ids = {}
    for line, tag, a in tags:
        if "id" in a:
            if a["id"] in ids:
                add("error", "index.html:%d" % line, "dup-id", "id \"%s\" also used on line %d" % (a["id"], ids[a["id"]]))
            ids.setdefault(a["id"], line)
    for line, tag, a in tags:
        where = "index.html:%d" % line
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
    for f in sorted((dist / "assets").rglob("*.css")):
        _check_gradients(f.read_text(encoding="utf-8"), str(f.relative_to(dist)), add)
    _check_gradients("\n".join(re.findall(r"<style[^>]*>(.*?)</style>", src, re.S)), "index.html <style>", add)
    css_all = "\n".join(f.read_text(encoding="utf-8") for f in sorted((dist / "assets").rglob("*.css")))
    css_all += "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", src, re.S))
    _check_design_css(css_all, add)
    _check_design_html(src, add)

    for w in warns:
        print("WARN  " + w)
    for e in errors:
        print("ERROR " + e)
    print("\nChecked %d text nodes, %d attributes, %d files." % (len(page.texts), len(page.attrs), len(files)))
    if errors:
        print("LINT FAILED with %d error(s). Fix page.json (or the template for structural errors), rebuild, lint again." % len(errors))
        return 1
    print("LINT PASSED (%d warning(s))." % len(warns))
    return 0


# Gradient policy (references/color-system.md, "Gradients"): flat surfaces; gradients only for scrims, edge fades,
# one-hue shading and hard-stop patterns.
GRADIENT_RE = re.compile(r"(?:repeating-)?(?:linear|radial|conic)-gradient\(")
COLOR_FAMILIES = (
    ("second accent", re.compile(r"var\(--(?:c-accent-2|accent-2-ink|c-accent-blend(?:-deep)?)\b")),
    ("accent", re.compile(r"var\(--(?:c-accent(?:-on-dark|-soft)?|accent-ink)\)")),
    ("primary", re.compile(r"var\(--c-primary\)")),
)
RAW_COLOR_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)")


def _balanced(css, start):
    """Index just past the parenthesis that closes the one opened right before start."""
    depth = 1
    i = start
    while i < len(css) and depth:
        depth += {"(": 1, ")": -1}.get(css[i], 0)
        i += 1
    return i


def _split_top(s):
    parts, depth, cur = [], 0, ""
    for ch in s:
        if ch == "," and depth == 0:
            parts.append(cur.strip())
            cur = ""
            continue
        depth += {"(": 1, ")": -1}.get(ch, 0)
        cur += ch
    parts.append(cur.strip())
    return parts


def _raw_chromatic(value):
    v = value.lower()
    if v.startswith("#"):
        h = v[1:]
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h[:3])
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    else:
        nums = re.findall(r"[\d.]+", v)
        if len(nums) < 3:
            return None
        r, g, b = (float(n) for n in nums[:3])
    # greys and very dark tones (slate shadows) count as neutral
    return None if max(r, g, b) - min(r, g, b) < 24 or max(r, g, b) < 72 else "#%02x%02x%02x" % (int(r), int(g), int(b))


def _families(text):
    found = set()
    for name, rx in COLOR_FAMILIES:
        if rx.search(text):
            found.add(name)
    for m in RAW_COLOR_RE.finditer(text):
        c = _raw_chromatic(m.group())
        if c:
            found.add("colour " + c)
    return found


def _hard_stops(args):
    """True when every stop ends where the next begins (split fills, stripes), so no colors blend."""
    stops = []
    for a in args:
        # drop the leading colour; what is left are the stop positions (numbers, calc() or var())
        rest = re.sub(r"^(?:var\([^()]*\)|color-mix\((?:[^()]|\([^()]*\))*\)|rgba?\([^)]*\)|#[0-9a-fA-F]{3,8}|[a-zA-Z]+)\s*", "", a.strip())
        pos = re.findall(r"calc\((?:[^()]|\([^()]*\))*\)|var\([^()]*\)|\S+", rest)
        if not pos:
            return False
        stops.append(pos)
    def same(a, b):
        if a == b:
            return True
        pa, pb = re.match(r"(-?[\d.]+)%$", a), re.match(r"(-?[\d.]+)%$", b)
        return bool(pa and pb and abs(float(pa.group(1)) - float(pb.group(1))) <= 2)
    return len(stops) > 1 and all(same(stops[i][-1], stops[i + 1][0]) for i in range(len(stops) - 1))


def _check_gradients(css, where, add):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    for block in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        selector, body = block.group(1).strip(), block.group(2)
        at = "%s %s" % (where, selector[:60])
        if re.search(r"background-clip\s*:\s*text", body) and GRADIENT_RE.search(body):
            add("error", at, "gradient", "gradient text; headings and highlights use one flat colour (references/color-system.md, Gradients)")
        m = re.search(r"(?<![-\w])filter\s*:[^;]*blur\((\d+(?:\.\d+)?)px", body)
        if m and float(m.group(1)) >= 24:
            add("error", at, "gradient", "blur(%spx) makes a glow blob; drop the decoration (references/color-system.md, Gradients)" % m.group(1))
        for g in GRADIENT_RE.finditer(body):
            end = _balanced(body, g.end())
            inner = body[g.end():end - 1]
            if re.search(r"(?:mask|mask-image)\s*:[^;]*$", body[:g.start()].rsplit(";", 1)[-1]):
                continue  # masks fade shapes, they paint no colour
            fams = _families(inner)
            brand = fams - {"primary"}
            if not (len(fams) >= 2 or brand):
                continue  # neutral or primary-only: scrims, shadows, shading
            args = _split_top(inner)
            if args and re.match(r"(?:to |in |from |at |circle|ellipse|closest|farthest|-?[\d.]+(?:deg|turn|rad|px|%)?\b)", args[0]):
                args = args[1:]  # direction, shape or colour space, not a stop
            if _hard_stops(args):
                continue  # stripes, dots, split fills
            what = ("blends %s" % " and ".join(sorted(fams))) if len(fams) >= 2 else ("fades the %s colour out, which reads as a glow" % sorted(brand)[0].replace("colour ", ""))
            add("error", at, "gradient", "gradient %s; use one flat colour. Gradients are only for photo scrims, edge fades, neutral or primary shading and hard-stop patterns (references/color-system.md, Gradients)" % what)


# Design tells of generated pages (references/anti-slop.md).
DURATION_RE = re.compile(r"(?<![\w-])(\d*\.?\d+)(ms|s)\b")
CHROME_SELECTORS = re.compile(r"header|nav|menu|mega|drawer|dialog|modal|backdrop|fab|exit|toast|sticky|toggle|bl-glass")
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
        if re.search(r"text-transform\s*:\s*uppercase", body):
            m = re.search(r"letter-spacing\s*:\s*(-?[\d.]+)em", body)
            if m and not 0.05 <= float(m.group(1)) <= 0.12:
                once("caps-tracking", "uppercase text tracked %sem; caps need 0.05-0.12em" % m.group(1))
        if re.search(r"text-align\s*:\s*justify", body):
            once("justify", "justified text leaves uneven gaps between words (WCAG 1.4.8); align left")
        if "[data-reveal]" in selector or ":hover" in selector:
            for prop in re.findall(r"(?:transition|animation)(?:-duration)?\s*:\s*([^;]+)", body):
                longest = max((_seconds(v, u) for v, u in DURATION_RE.findall(prop.split("calc(")[0])), default=0)
                if longest > 0.5:
                    once("slow-motion", "%.2fs on a reveal or hover; interface motion stays within 0.1-0.5s" % longest)
        for sh in re.findall(r"box-shadow\s*:\s*([^;]+)", body):
            for layer in _split_top(sh):
                if "inset" in layer:
                    continue
                if not (_families(layer) - {"primary"}):
                    continue
                lengths = re.findall(r"(-?[\d.]+)(?:px|rem|em)", re.sub(r"color-mix\((?:[^()]|\([^()]*\))*\)|var\([^()]*\)", " ", layer))
                blur = float(lengths[2]) if len(lengths) >= 3 else 0
                if blur >= 16:
                    once("glow", "shadow in the brand colour with a %gpx blur reads as a glow; use a neutral shadow" % blur)
        if re.search(r"(?<!-)backdrop-filter\s*:", body) and not CHROME_SELECTORS.search(selector):
            once("glass", "frosted glass on content; keep backdrop-filter to the header, menus, dialogs and floating controls", "warn")


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
        add("warn", "index.html", "cta-arrows", "%d of %d buttons and links carry an arrow; keep arrows for text links that go somewhere" % (arrows, ctas))


def _check_buttons(src, add):
    for m in re.finditer(r"<button\b([^>]*)>(.*?)</button>", src, re.S):
        attrs, inner = m.group(1), m.group(2)
        text = re.sub(r"<svg.*?</svg>", "", inner, flags=re.S)
        text = re.sub(r"<[^>]+>", "", text).strip()
        if not text and "aria-label" not in attrs:
            line = src.count("\n", 0, m.start()) + 1
            add("error", "index.html:%d" % line, "button-name", "button has no text and no aria-label")


def _check_headings(tags, add):
    last = 0
    for line, tag, _ in tags:
        if re.fullmatch(r"h[1-6]", tag):
            lvl = int(tag[1])
            if last and lvl > last + 1:
                add("warn", "index.html:%d" % line, "heading-order", "<%s> follows <h%d>; a level is skipped" % (tag, last))
            last = lvl


if __name__ == "__main__":
    sys.exit(main())
