"""Check pages built with the app-ui kit. Errors fail; warnings are things to fix or to explain in the report.

    python scripts/lint_ui.py <project folder>      every page that loads kit/app.css, and the CSS those pages load
    python scripts/lint_ui.py recipes               the skill's own recipes (kit found next to them)

What it holds a page to:
- colours, shadows and gradients live in kit/tokens.css only; project CSS reads var(--...)
- the project's kit/tokens.css and kit/app.css stay flat (scripts/flat_css.py, references/flat-style.md): shadows
  only on what floats, no gradient text, glows or colour-to-colour gradients
- every class on a page exists in the kit or in the project's own CSS; no <style> blocks, no inline style
  except a custom property or a width or height in percent (a progress bar)
- per state (body data-states): one <h1>, at most one primary button in the page and one in each dialog
- copy: no emoji, no arrows on buttons and links, no em or en dashes, no stock AI phrases, no Lorem
- images carry alt text; icon-only buttons carry aria-label
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
import flat_css  # noqa: E402

# colour families of the kit tokens (kit/tokens.css), for the flat checks on the project's copy of the kit
FLAT_FAMILIES = flat_css.families([
    ("accent", r"--(?:accent|accent-hover|accent-soft|accent-line|primary|primary-hover)\b"),
    ("status", r"--(?:ok|ok-soft|warn|warn-soft|bad|bad-hover|bad-soft)\b"),
])
COLOR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?|oklch|oklab|lab|lch|color)\(", re.I)
GRADIENT = re.compile(r"\b(?:linear|radial|conic)-gradient\(", re.I)
SIDE_STRIPE = re.compile(r"(?<![\w-])border-(?:left|right|inline-start|inline-end)\s*:\s*(?:[2-9]|\d{2,})px", re.I)
SHADOW = re.compile(r"\b(?:box-shadow|text-shadow)\s*:|drop-shadow\(", re.I)
SPACE_PROP = re.compile(r"\b(?:margin|padding|gap|row-gap|column-gap)(?:-[a-z]+)?\s*:\s*([^;}]+)", re.I)
SPACE_OK = {0, 1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 28, 32, 40, 48, 56, 64, 72, 80}
STYLE_OK = re.compile(r"^\s*(?:(?:--[\w-]+\s*:[^;]+|(?:width|height|min-width|max-width)\s*:\s*[\d.]+%)\s*;?\s*)+$")
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF\U0001F900-\U0001F9FF⭐⭕⌚-⌛⏩-⏳]")
ARROWS = re.compile(r"[←-⇿⟶⟵➔-➿»«]|->|<-")
DASHES = re.compile("[–—]")
STOCK = [
    "trải nghiệm tuyệt vời", "liền mạch", "mạnh mẽ", "giải pháp toàn diện", "nâng tầm", "khám phá ngay", "hành trình",
    "một cách dễ dàng", "tối ưu hoá trải nghiệm", "đột phá", "vượt trội", "hãy để chúng tôi", "chỉ với một cú nhấp",
    "seamless", "unlock", "elevate", "empower", "effortless", "supercharge", "robust", "game-changer", "delve",
]
PLACEHOLDER = re.compile(r"lorem ipsum|\blorem\b|\[cần điền\]|\[todo\]|xxx", re.I)


class Node:
    __slots__ = ("tag", "attrs", "children", "parent", "line", "text")

    def __init__(self, tag, attrs, parent, line):
        self.tag, self.attrs, self.parent, self.line = tag, dict(attrs), parent, line
        self.children, self.text = [], []

    def classes(self):
        return (self.attrs.get("class") or "").split()

    def all_text(self):
        out = list(self.text)
        for c in self.children:
            out.append(c.all_text())
        return " ".join(t for t in out if t).strip()

    def walk(self):
        yield self
        for c in self.children:
            yield from c.walk()


VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr", "use", "path", "circle", "rect", "line", "polyline", "polygon"}


class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", [], None, 1)
        self.cur = self.root
        self.styles = []

    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs, self.cur, self.getpos()[0])
        self.cur.children.append(n)
        if tag not in VOID:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, attrs, self.cur, self.getpos()[0]))

    def handle_endtag(self, tag):
        n = self.cur
        while n is not self.root and n.tag != tag:
            n = n.parent
        if n is not self.root:
            self.cur = n.parent

    def handle_data(self, data):
        if self.cur.tag == "style":
            self.styles.append((self.getpos()[0], data))
        elif self.cur.tag != "script" and data.strip():
            self.cur.text.append(data.strip())


def css_classes(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    sels = " ".join(m.group(1) for m in re.finditer(r"([^{}]+)\{", text))
    return set(re.findall(r"\.(-?[A-Za-z_][\w-]*)", sels))


def find_kit(root):
    for k in (root / "kit", root.parent / "kit"):
        if (k / "app.css").is_file():
            return k
    return None


def lint_css(path, errs, warns, rel):
    text = path.read_text(encoding="utf-8")
    body = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    for i, line in enumerate(body.splitlines(), 1):
        where = "%s:%d" % (rel, i)
        if GRADIENT.search(line):
            errs.append("%s: gradient. Surfaces are flat; use a token colour" % where)
        elif COLOR.search(line):
            errs.append("%s: colour written in CSS. Read a token: var(--ink), var(--accent), var(--line)..." % where)
        if SIDE_STRIPE.search(line):
            errs.append("%s: thick border on one side (a side stripe). Notices and cards are flat fills; use .notice" % where)
        if SHADOW.search(line):
            errs.append("%s: shadow. Only menus, dialogs and device frames float, and the kit draws them" % where)
        if re.search(r"--(?:accent|ink|bg|surface|line|ok|warn|bad|r|s\d|fs-[a-z]+)\s*:", line):
            warns.append("%s: redefines a kit token. Change it in kit/tokens.css (scripts/theme.py) so every page follows" % where)
        for m in SPACE_PROP.finditer(line):
            for px in re.findall(r"(-?\d+(?:\.\d+)?)px", m.group(1)):
                if abs(float(px)) not in SPACE_OK:
                    warns.append("%s: %spx is off the spacing scale; use var(--s1) ... var(--s9)" % (where, px))


def visible_in(node, state):
    """False when the node or an ancestor is drawn only in other states, or is hidden for good."""
    n = node
    while n is not None and n.tag != "#root":
        st = n.attrs.get("data-state")
        if st is not None and state not in st.split():
            return False
        if "hidden" in n.attrs and n.tag != "dialog" and not n.attrs.get("data-state"):
            return False
        n = n.parent
    return True


def in_dialog(node):
    n = node.parent
    while n is not None:
        if n.tag == "dialog":
            return n
        n = n.parent
    return None


def lint_html(path, known, errs, warns, rel):
    text = path.read_text(encoding="utf-8")
    t = Tree()
    t.feed(text)
    nodes = list(t.root.walk())
    body = next((n for n in nodes if n.tag == "body"), None)
    states = (body.attrs.get("data-states") or "default").split() if body else ["default"]
    if body is not None and "data-states" not in body.attrs:
        warns.append("%s: <body> has no data-states; list the states this page draws (default empty error ...)" % rel)
    hrefs = " ".join((n.attrs.get("href") or "") + " " + (n.attrs.get("src") or "") for n in nodes if n.tag in ("link", "script"))
    for need in ("tokens.css", "app.css", "icons.js", "app.js"):
        if need not in hrefs:
            errs.append("%s: does not load kit/%s" % (rel, need))
    for line, _ in t.styles:
        errs.append("%s:%d: <style> block. Put page CSS in a project .css file, where lint checks it" % (rel, line))

    for n in nodes:
        where = "%s:%d" % (rel, n.line)
        style = n.attrs.get("style")
        if style is not None and n.tag not in ("svg",) and not STYLE_OK.match(style):
            errs.append("%s: inline style \"%s\". Use kit classes; only custom properties and %% widths are allowed inline" % (where, style[:60]))
        for c in n.classes():
            if c not in known:
                errs.append("%s: class \"%s\" is not in the kit or the project CSS" % (where, c))
        if n.tag == "img" and "alt" not in n.attrs:
            errs.append("%s: <img> without alt (alt=\"\" for decoration)" % where)
        if n.tag in ("button", "a") and not n.all_text() and not n.attrs.get("aria-label") and not n.attrs.get("title"):
            if any(c.tag == "svg" for c in n.walk()):
                errs.append("%s: icon-only %s without aria-label" % (where, n.tag))
        own = " ".join(n.text)
        if own:
            if EMOJI.search(own):
                errs.append("%s: emoji in copy: \"%s\"" % (where, own[:50]))
            if DASHES.search(own):
                errs.append("%s: em or en dash in copy: \"%s\". Use a comma, a colon or two sentences" % (where, own[:50]))
            low = own.lower()
            for w in STOCK:
                if w in low:
                    warns.append("%s: stock phrase \"%s\". Say what happens instead" % (where, w))
            if PLACEHOLDER.search(own):
                warns.append("%s: placeholder copy \"%s\"" % (where, own[:40]))
        if n.tag in ("button", "a") and ARROWS.search(n.all_text()):
            errs.append("%s: arrow in a button or link label: \"%s\". The label names the action; no arrows" % (where, n.all_text()[:40]))

    for st in states:
        h1 = [n for n in nodes if n.tag == "h1" and visible_in(n, st) and not in_dialog(n)]
        if len(h1) != 1:
            errs.append("%s [state %s]: %d <h1>, a page has exactly one" % (rel, st, len(h1)))
        regions = {}
        for n in nodes:
            cl = n.classes()
            if "btn" in cl and "primary" in cl and visible_in(n, st):
                d = in_dialog(n)
                regions.setdefault(d.attrs.get("id", "dialog") if d is not None else "page", []).append(n)
        for region, btns in regions.items():
            if len(btns) > 1:
                labels = ", ".join("\"%s\" (line %d)" % (b.all_text()[:24], b.line) for b in btns[:4])
                errs.append("%s [state %s]: %d primary buttons in %s: %s. Keep one; the rest are outline" % (rel, st, len(btns), region, labels))


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    root = Path(sys.argv[1]).resolve()
    kit = find_kit(root)
    if not kit:
        sys.exit("No kit/app.css in %s or its parent. Run scripts/new.py first." % root)
    known = css_classes((kit / "app.css").read_text(encoding="utf-8"))
    linked = {(p.parent / h).resolve() for p in root.rglob("*.html") if kit not in p.parents
              for h in __import__("re").findall(r'href="([^"]+\.css)"', p.read_text(encoding="utf-8", errors="replace"))
              if "app.css" in p.read_text(encoding="utf-8", errors="replace") and not h.startswith("http")}
    css_files = [p for p in root.rglob("*.css") if kit not in p.parents and p.resolve() in linked]
    for p in css_files:
        known |= css_classes(p.read_text(encoding="utf-8"))
    errs, warns = [], []
    for p in css_files:
        lint_css(p, errs, warns, p.relative_to(root).as_posix())
    # the project's copy of the kit stays flat as well (references/flat-style.md); theme.py and hand edits change it
    kit_css = [(kit / n, (kit / n).read_text(encoding="utf-8")) for n in ("tokens.css", "app.css") if (kit / n).is_file()]
    tokens = {}
    for _, css in kit_css:
        tokens.update(flat_css.tokens_in(css))
    for p, css in kit_css:
        for f in flat_css.check(css, FLAT_FAMILIES, tokens):
            (errs if f.level == "error" else warns).append("kit/%s %s: %s %s" % (p.name, f.selector[:60], f.code, f.message))
    # only pages built with the kit: built sites, mockups and other HTML in the folder are not ours to judge
    pages = [p for p in sorted(root.rglob("*.html")) if kit not in p.parents and "app.css" in p.read_text(encoding="utf-8", errors="replace")]
    for p in pages:
        lint_html(p, known, errs, warns, p.relative_to(root).as_posix())
    for w in warns:
        print("WARN  " + w)
    for e in errs:
        print("ERROR " + e)
    if errs:
        print("\nLINT FAILED: %d error(s) in %d page(s)." % (len(errs), len(pages)))
        sys.exit(1)
    print("\nLINT PASSED: %d page(s), %d CSS file(s), %d warning(s)." % (len(pages), len(css_files), len(warns)))


if __name__ == "__main__":
    main()
