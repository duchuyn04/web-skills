"""Check a built shop (dist/) against the house copy rules: no emoji, text arrows, em or en dashes, curly
quotes, banned AI words or chatbot phrases in any shipped file or visible text. Stylesheets are held to the flat
style (references/flat-style.md): no gradient text, no colour-to-colour gradients or glows, shadows only on what floats.

    python scripts/lint_output.py sites/<slug>/dist
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
import rules  # noqa: E402

# Colour families of the --c-* tokens build.py writes; dark and header fills may shade on their own.
FLAT_FAMILIES = flat_css.families([
    ("accent", r"--c-(?:accent|accent-ink|accent-soft|accent-text|btn|btn-hover|link|price|sale|soft|soft-ink|header-soft)\b"),
    ("second accent", r"--c-accent-2\b"),
    ("status", r"--c-(?:bad|ok|warn)\b"),
    ("dark", r"--c-(?:dark|header)\b", True),
])


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "svg"):
            self.skip += 1
        for k, v in attrs:
            if k in ("alt", "title", "placeholder", "aria-label") and v:
                self.parts.append(v)

    def handle_endtag(self, tag):
        if tag in ("script", "style", "svg") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip and data.strip():
            self.parts.append(data.strip())


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: lint_output.py <dist>")
    dist = Path(sys.argv[1])
    errors, warns = [], []
    sheets = []
    for f in sorted(dist.rglob("*")):
        if f.suffix == ".css" and "qa" not in f.parts:
            sheets.append((f.relative_to(dist).as_posix(), f.read_text(encoding="utf-8")))
        elif f.suffix == ".html" and "qa" not in f.parts:
            inline = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", f.read_text(encoding="utf-8"), re.S))
            if inline.strip():
                sheets.append((f.relative_to(dist).as_posix() + " <style>", inline))
    tokens = {}
    for _, css in sheets:
        tokens.update(flat_css.tokens_in(css))
    for where, css in sheets:
        for fd in flat_css.check(css, FLAT_FAMILIES, tokens):
            (errors if fd.level == "error" else warns).append("%s %s: %s %s" % (where, fd.selector[:60], fd.code, fd.message))
    for f in sorted(dist.rglob("*")):
        if f.suffix not in (".html", ".css", ".js") or "qa" in f.parts:
            continue
        rel = f.relative_to(dist).as_posix()
        src = f.read_text(encoding="utf-8")
        for line, fd in rules.check_raw_file(src):
            errors.append("%s:%d %s (%s)" % (rel, line, fd.message, fd.excerpt))
        if f.suffix == ".html":
            p = Text()
            p.feed(src)
            seen = set()
            for t in p.parts:
                if t in seen:
                    continue
                seen.add(t)
                for fd in rules.check_text(t):
                    (errors if fd.level == "error" else warns).append("%s: %s (%s)" % (rel, fd.message, fd.excerpt))
    for w in warns:
        print("WARN  " + w)
    for e in errors:
        print("ERROR " + e)
    if errors:
        print("\nLINT FAILED: %d error(s)." % len(errors))
        sys.exit(1)
    print("LINT PASSED (%d warning(s))." % len(warns))


if __name__ == "__main__":
    main()
