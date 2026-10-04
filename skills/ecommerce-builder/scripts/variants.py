"""Variant discovery and checks, shared by build.py, check_templates.py and variants_qa.py.

A variant is one template file in a part folder (see PART_DIRS). Adding a file adds a variant: nothing else
is registered. Rules every variant file must follow:

1. The first line is a comment {# ... #} saying what the variant is and when to pick it (it feeds --list and the catalog).
2. It keeps every hook in data/hooks.json for its part (store.js and qa.py read them). A variant that does not use a hook keeps the
   element, hidden.
3. Its css (assets/css/v/<part>-<name>.css, assets/css/v/section-<type>[-<variant>].css) uses colour tokens only, no hex colours,
   so it works under any preset including the dark one. A line may carry /* hex-ok: reason */ for art-like colours.
"""
import json
import re
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
TPL = SKILL / "templates"
DATA = SKILL / "data"

# part -> template folder; the file stems inside are the variants
PART_DIRS = {
    "header": "layout/headers", "hero": "sections/hero", "card": "partials/cards", "pdp": "pdp", "plp": "plp", "footer": "layout/footers",
    "cart": "cart", "checkout": "checkout", "thanks": "thanks", "account": "account/shells",
}
# defaults when a style does not name the part
PART_DEFAULT = {"cart": "split", "checkout": "onepage", "thanks": "receipt", "account": "sidebar"}
# how much a visitor notices each part; used to compare two shops
PART_WEIGHT = {"header": 3, "hero": 3, "card": 3, "pdp": 2, "plp": 2, "cart": 1, "checkout": 1, "thanks": 0.5, "account": 0.5, "footer": 1}

HEX_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b")
ATTR_RE = re.compile(r"\b(data-[a-z0-9-]+)")


def variants(part):
    d = TPL / PART_DIRS[part]
    return sorted(p.stem for p in d.glob("*.html") if not p.stem.startswith("_")) if d.exists() else []


def all_variants():
    return {part: variants(part) for part in PART_DIRS}


def part_file(part, name):
    return TPL / PART_DIRS[part] / (name + ".html")


def section_types():
    """Home section types: sections/<type>.html, or a folder sections/<type>/ of variants (hero)."""
    d = TPL / "sections"
    out = {p.stem for p in d.glob("*.html")} | {p.name for p in d.iterdir() if p.is_dir()}
    return sorted(out)


def section_variants(sec_type):
    d = TPL / "sections" / sec_type
    return sorted(p.stem for p in d.glob("*.html") if not p.stem.startswith("_")) if d.is_dir() else []


def describe(path):
    """The leading {# ... #} comment of a template, or None."""
    src = Path(path).read_text(encoding="utf-8").lstrip()
    m = re.match(r"\{#(.*?)#\}", src, re.S)
    return " ".join(m.group(1).split()) if m else None


def hooks(path):
    return sorted(set(ATTR_RE.findall(Path(path).read_text(encoding="utf-8"))))


def required_hooks(part):
    f = DATA / "hooks.json"
    return json.loads(f.read_text(encoding="utf-8")).get(part, []) if f.exists() else []


def freeze_hooks():
    """Write data/hooks.json: the hooks present in every current variant of each part (the contract new variants must keep)."""
    out = {}
    for part in PART_DIRS:
        sets = [set(hooks(part_file(part, v))) for v in variants(part)]
        if part == "hero":
            continue
        out[part] = sorted(set.intersection(*sets)) if sets else []
    (DATA / "hooks.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


def css_files_for(part, name):
    base = TPL / "assets/css/v"
    return [base / ("%s-%s.css" % (part, name))]


def check_css(path):
    """Hex colours in variant css, except on lines marked hex-ok."""
    errs = []
    p = Path(path)
    if not p.exists():
        return errs
    for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if "hex-ok" in line:
            continue
        code = re.sub(r"/\*.*?\*/", "", line)
        for m in HEX_RE.findall(code):
            errs.append("%s:%d hex colour %s: use a token (var(--c-...)) so the variant works under every preset; mark art-like colours with /* hex-ok: reason */" % (p.name, n, m))
            break
    return errs


def check_variant(part, name):
    errs = []
    f = part_file(part, name)
    if not f.exists():
        return ["%s variant '%s' does not exist" % (part, name)]
    if not describe(f):
        errs.append("%s/%s.html: the first line must be a comment {# what it is and when to pick it #}" % (PART_DIRS[part], name))
    have = set(hooks(f))
    missing = [h for h in required_hooks(part) if h not in have]
    if missing:
        errs.append("%s/%s.html: missing hooks %s (store.js and qa.py need them; keep the element, hidden if unused)" % (PART_DIRS[part], name, ", ".join(missing)))
    for cf in css_files_for(part, name):
        errs.extend(check_css(cf))
    return errs


def check_section(sec_type, variant=None):
    errs = []
    f = TPL / "sections" / (sec_type + ".html") if variant is None else TPL / "sections" / sec_type / (variant + ".html")
    if sec_type == "hero" and variant is None:
        return errs
    if f.exists() and not describe(f):
        errs.append("%s: the first line must be a comment {# what it is and when to pick it #}" % f.relative_to(TPL))
    suffix = sec_type if variant is None else "%s-%s" % (sec_type, variant)
    errs.extend(check_css(TPL / "assets/css/v" / ("section-%s.css" % suffix)))
    return errs


def check_all():
    errs = []
    for part in PART_DIRS:
        for v in variants(part):
            errs.extend(check_variant(part, v))
    for t in section_types():
        errs.extend(check_section(t))
        for v in section_variants(t):
            errs.extend(check_section(t, v))
    return errs


def catalog():
    lines = ["# Variant catalog", "", "Generated by `python scripts/make_catalog.py`; do not edit by hand. The text comes from the first-line comment of each template.", ""]
    for part, folder in PART_DIRS.items():
        lines += ["## %s (`templates/%s/`)" % (part, folder), ""]
        for v in variants(part):
            lines.append("- `%s`: %s" % (v, describe(part_file(part, v)) or "NO DESCRIPTION"))
        lines.append("")
    lines += ["## Home sections (`templates/sections/`)", ""]
    for t in section_types():
        f = TPL / "sections" / (t + ".html")
        vs = section_variants(t)
        if vs:
            lines.append("- `%s`, variants:" % t)
            for v in vs:
                lines.append("  - `%s`: %s" % (v, describe(TPL / "sections" / t / (v + ".html")) or "NO DESCRIPTION"))
        else:
            lines.append("- `%s`: %s" % (t, describe(f) or "NO DESCRIPTION"))
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    if "--freeze-hooks" in sys.argv:
        print(json.dumps(freeze_hooks(), indent=1))
    else:
        errs = check_all()
        for e in errs:
            print("ERROR " + e)
        print("TEMPLATE CHECK %s: %d problem(s)" % ("FAILED" if errs else "PASSED", len(errs)))
        sys.exit(1 if errs else 0)
