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
