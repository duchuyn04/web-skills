"""Flat style checks for CSS, shared by every skill (references/flat-style.md).

The same file ships in each skill's scripts/ folder so a skill installs on its own; tools/check_flat_css.py fails CI
when the copies differ, runs the self-test at the bottom and checks every skill's own stylesheets with it.

    import flat_css
    fams = flat_css.families([("accent", r"--c-accent\\b"), ("dark", r"--c-dark\\b", True)])
    for f in flat_css.check(css, fams):
        print(f.level, f.code, f.selector, f.message)

What a stylesheet is held to:
- gradient-text   no background-clip: text
- gradient        a soft gradient may not blend two colour families or fade a brand colour out; photo scrims, edge
                  fades, neutral or dark shading and hard-stop patterns (stripes, split fills, tracks) pass
- blur-blob       nothing blurred by 24px or more (glow blobs)
- glow            no shadow in a brand or other chromatic colour with a blur of 16px or more
- resting-shadow  a shadow larger than a hairline (blur over 4px or an offset over 2px) only on what floats above the
                  page: header, menus, popovers, tooltips, dialogs, drawers, sheets, toasts, floating buttons, fixed
                  or sticky bars; or a rule marked /* flat-ok: <reason> */ (a 3D object, a device drawing)
- hover-shadow    no shadow grows on hover; change the border or background colour instead
- hover-lift      nothing rises on hover (warning)
- glass           backdrop-filter only on what floats (warning)
"""
import re
from collections import namedtuple

Finding = namedtuple("Finding", "level code selector message")

DOC = "references/flat-style.md"
# Class names of layers that float above the page. Matched as whole words inside a selector (bl-mega__panel, catmenu-fly).
FLOATING_RE = re.compile(
    r"(?<![a-z0-9])(?:header|hdr|topbar|nav|menu|mega|dropdown|popover|pop|tooltip|tip|dialog|modal|drawer|sheet|toast|"
    r"snackbar|fab|suggest|flyout|fly|cmdk|palette|lightbox|bubble|teaser|notif|tray|buybar|savebar|mbar|bulk|exit|"
    r"assist|thumb|backdrop)(?![a-z0-9])|^dialog\b|\[popover\]|::backdrop|::-webkit-slider-thumb|::-moz-range-thumb", re.I)
FIXED_RE = re.compile(r"(?<![-\w])position\s*:\s*(?:fixed|sticky)\b")
MARK_RE = re.compile(r"/\*\s*flat-ok\b")
GRADIENT_RE = re.compile(r"(?:repeating-)?(?:linear|radial|conic)-gradient\(")
RAW_COLOR_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)")
COLOR_FN_RE = re.compile(r"color-mix\((?:[^()]|\([^()]*\))*\)|rgba?\([^)]*\)|hsla?\([^)]*\)|#[0-9a-fA-F]{3,8}\b")
VAR_RE = re.compile(r"var\(\s*(--[\w-]+)\s*(?:,[^()]*)?\)")
LENGTH_RE = re.compile(r"(?<![\w.#-])(-?\d*\.?\d+)(px|rem|em)?(?![\w%])")
HAIRLINE_BLUR, HAIRLINE_OFFSET = 4, 2


def families(spec):
    """[(name, token regex[, may stand alone])]: colour families of a skill's tokens. A family that may stand alone
    (a dark primary used for shading) passes in a gradient on its own but not mixed with another family."""
    return [(s[0], re.compile(r"var\(\s*(?:%s)" % s[1]), bool(s[2]) if len(s) > 2 else False) for s in spec]


def balanced(css, start):
    """Index just past the parenthesis that closes the one opened right before start."""
    depth, i = 1, start
    while i < len(css) and depth:
        depth += {"(": 1, ")": -1}.get(css[i], 0)
        i += 1
    return i


def split_top(s):
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


def raw_chromatic(value):
    """The colour as #rrggbb when it has visible hue; None for greys and very dark tones (slate shadows)."""
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
    return None if max(r, g, b) - min(r, g, b) < 24 or max(r, g, b) < 72 else "#%02x%02x%02x" % (int(r), int(g), int(b))


def found_families(text, fams):
    """Names of the colour families in text, and the names of those that may not stand alone."""
    found, strict = set(), set()
    for name, rx, alone in fams:
        if rx.search(text):
            found.add(name)
            if not alone:
                strict.add(name)
    for m in RAW_COLOR_RE.finditer(text):
        c = raw_chromatic(m.group())
        if c:
            found.add("colour " + c)
            strict.add("colour " + c)
    return found, strict


def hard_stops(args):
    """True when every stop ends where the next begins (split fills, stripes), so no colours blend."""
    stops = []
    for a in args:
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


def tokens_in(css):
    """Custom properties defined anywhere in css (the last definition wins), to read shadows set through a token."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return {m.group(1): m.group(2).strip() for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;{}]+)", css)}


def resolve(value, tokens, depth=0):
    if depth > 4:
        return value
    return VAR_RE.sub(lambda m: resolve(tokens[m.group(1)], tokens, depth + 1) if m.group(1) in tokens else m.group(0), value)


def shadow_layers(body, tokens):
    """(property, layer, resolved layer) for every box-shadow, text-shadow and filter drop-shadow in a rule body."""
    out = []
    for prop, value in re.findall(r"(?<![-\w])(box-shadow|text-shadow)\s*:\s*([^;]+)", body):
        for layer in split_top(value):
            # a token may hold several layers (--shadow-device: 0 1px 2px ..., 0 12px 32px ...)
            out += [(prop, layer, part) for part in split_top(resolve(layer, tokens))]
    for value in re.findall(r"(?<![-\w])filter\s*:\s*([^;]+)", body):
        for m in re.finditer(r"drop-shadow\(", value):
            layer = value[m.end():balanced(value, m.end()) - 1]
            out.append(("drop-shadow", layer, resolve(layer, tokens)))
    return out


def measure(layer):
    """(x, y, blur, spread) in px of one shadow layer, or None when it cannot be read (an unknown token)."""
    if layer.strip() in ("none", "unset", "initial", "inherit", "0"):
        return (0, 0, 0, 0)
    # a token left after resolve() is a colour (var(--c-accent)); lengths come through tokens the page defines
    plain = VAR_RE.sub(" ", COLOR_FN_RE.sub(" ", re.sub(r"\binset\b", " ", layer)))
    nums = [float(v) * (16 if u in ("rem", "em") else 1) for v, u in LENGTH_RE.findall(plain)]
    if len(nums) < 2:
        return None
    nums += [0, 0]
    return tuple(nums[:4])


def check(css, fams, tokens=None):
    """Findings for one stylesheet. tokens: custom properties defined elsewhere (another file of the same page)."""
    toks = dict(tokens or {})
    toks.update(tokens_in(css))
    css = re.sub(r"@keyframes[^{]*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}", "", css)
    out, seen = [], set()

    def add(level, code, sel, msg):
        if (code, sel) not in seen:
            seen.add((code, sel))
            out.append(Finding(level, code, sel, msg))
    for block in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        raw_sel, raw_body = block.group(1), block.group(2)
        marked = bool(MARK_RE.search(raw_sel) or MARK_RE.search(raw_body))
        selector = " ".join(re.sub(r"/\*.*?\*/", "", raw_sel, flags=re.S).split())
        body = re.sub(r"/\*.*?\*/", "", raw_body, flags=re.S)
        if not selector or selector.startswith("@"):
            continue
        sel = selector[:80]
        floating = marked or bool(FLOATING_RE.search(selector) or FIXED_RE.search(body))
        hover = ":hover" in selector

        if re.search(r"(?<![-\w])(?:-webkit-)?background-clip\s*:\s*text", body):
            add("error", "gradient-text", sel, "gradient text; set headings and highlights in one flat colour (%s)" % DOC)
        m = re.search(r"(?<![-\w])filter\s*:[^;]*blur\((\d+(?:\.\d+)?)px", body)
        if m and float(m.group(1)) >= 24:
            add("error", "blur-blob", sel, "blur(%spx) makes a glow blob; drop the decoration (%s)" % (m.group(1), DOC))
        for g in GRADIENT_RE.finditer(body):
            end = balanced(body, g.end())
            inner = body[g.end():end - 1]
            if re.search(r"(?:mask|mask-image)\s*:[^;]*$", body[:g.start()].rsplit(";", 1)[-1]):
                continue  # masks fade shapes, they paint no colour
            fams_in, strict = found_families(inner, fams)
            if not (len(fams_in) >= 2 or strict):
                continue  # neutral, or one shading family on its own: scrims, shadows, shading
            args = split_top(inner)
            if args and re.match(r"(?:to |in |from |at |circle|ellipse|closest|farthest|-?[\d.]+(?:deg|turn|rad|px|%)?\b)", args[0]):
                args = args[1:]  # direction, shape or colour space, not a stop
            if hard_stops(args):
                continue  # stripes, dots, split fills, progress tracks
            what = ("blends %s" % " and ".join(sorted(fams_in))) if len(fams_in) >= 2 else \
                ("fades the %s colour out, which reads as a glow" % sorted(strict)[0].replace("colour ", ""))
            add("error", "gradient", sel, "gradient %s; use one flat colour. Gradients are only for photo scrims, edge fades, "
                "neutral shading and hard-stop patterns (%s)" % (what, DOC))
        for prop, layer, value in shadow_layers(body, toks):
            if re.search(r"\binset\b", value):
                continue
            size = measure(value)
            _, strict = found_families(value, fams)
            if size and size[2] >= 16 and strict:
                add("error", "glow", sel, "%s in a brand colour with a %gpx blur reads as a glow; shadows are neutral (%s)" % (prop, size[2], DOC))
                continue
            if prop == "text-shadow" or floating:
                continue  # text shadows lift text off photos; floating layers may cast a shadow
            big = size is None or size[2] > HAIRLINE_BLUR or abs(size[0]) > HAIRLINE_OFFSET or abs(size[1]) > HAIRLINE_OFFSET
            if not big:
                continue
            shown = layer if len(layer) < 48 else layer[:45] + "..."
            if hover:
                add("error", "hover-shadow", sel, "a shadow (%s) appears on hover; change the border or background colour instead (%s)" % (shown, DOC))
            else:
                add("error", "resting-shadow", sel, "a %s (%s) on an element that does not float; separate it with a 1px border or a "
                    "surface tone, keep shadows for menus, dialogs, toasts and sticky bars, or mark a drawn 3D object "
                    "/* flat-ok: why */ (%s)" % (prop, shown, DOC))
        # a negative vertical move in px or rem; translate(-50%, -50%) only keeps a centred element in place
        if hover and not floating and re.search(r"translate(?:Y\(\s*|3d\([^,]*,\s*|\([^,)]*,\s*)-[\d.]+(?:px|r?em)", body):
            add("warn", "hover-lift", sel, "the element rises on hover; show the hover with a border, background or underline (%s)" % DOC)
        if re.search(r"(?<![-\w])(?:-webkit-)?backdrop-filter\s*:\s*(?!none)", body) and not floating:
            add("warn", "glass", sel, "frosted glass on content; keep backdrop-filter to the header, menus, dialogs and floating controls (%s)" % DOC)
    return out


def _self_test():
    fams = families([("accent", r"--c-accent\b"), ("second accent", r"--c-accent-2\b"), ("dark", r"--c-dark\b", True)])
    cases = [
        (".t{background:linear-gradient(90deg,#7c3aed,#ec4899);-webkit-background-clip:text;color:transparent}", {"gradient-text", "gradient"}),
        (".a{background:linear-gradient(120deg,var(--c-accent),var(--c-accent-2))}", {"gradient"}),
        (".a{background:linear-gradient(160deg,var(--c-accent),color-mix(in srgb,var(--c-accent) 55%,#fff))}", {"gradient"}),
        (".scrim::after{background:linear-gradient(180deg,rgba(0,0,0,0),rgba(10,6,14,.8))}", set()),
        (".dark{background:linear-gradient(180deg,var(--c-dark),transparent)}", set()),
        (".bar{background:linear-gradient(90deg,var(--c-accent) var(--p),var(--c-dark) var(--p))}", set()),
        (".fade{mask-image:linear-gradient(90deg,transparent,#000 10%)}", set()),
        (".blob{filter:blur(60px)}", {"blur-blob"}),
        (".btn{box-shadow:0 10px 30px color-mix(in srgb,var(--c-accent) 40%,transparent)}", {"glow"}),
        (".card{box-shadow:0 18px 40px rgba(60,30,10,.16)}", {"resting-shadow"}),
        (":root{--shadow-lg:0 24px 48px -24px rgba(15,23,42,.24)} .frame{box-shadow:var(--shadow-lg)}", {"resting-shadow"}),
        (":root{--sh:0 1px 2px rgba(0,0,0,.08),0 12px 32px rgba(0,0,0,.12)} .frame{box-shadow:var(--sh)}", {"resting-shadow"}),
        (".stack{box-shadow:-3px 3px 0 #fff,-4px 4px 0 #ddd}", {"resting-shadow"}),
        (".frame{box-shadow:var(--unknown)}", {"resting-shadow"}),
        (".art{filter:drop-shadow(0 18px 30px rgba(0,0,0,.25))}", {"resting-shadow"}),
        (".card:hover{box-shadow:0 10px 30px rgba(0,0,0,.12);transform:translateY(-4px)}", {"hover-shadow", "hover-lift"}),
        (".play:hover{transform:translate(-50%,-50%) scale(1.08)}", set()),
        (".card{box-shadow:0 1px 2px rgba(0,0,0,.06),0 0 0 1px #e4e7eb}", set()),
        (".opt:has(input:checked){box-shadow:0 0 0 1px var(--c-accent)}", set()),
        (".focus:focus{box-shadow:0 0 0 3px color-mix(in srgb,var(--c-accent) 20%,transparent)}", set()),
        (".tab[aria-selected=true]{box-shadow:inset 0 -2px 0 var(--c-accent)}", set()),
        (".menu{box-shadow:0 12px 32px rgba(0,0,0,.14)}", set()),
        (".bar-x{position:sticky;bottom:0;box-shadow:0 -6px 20px rgba(0,0,0,.12)}", set()),
        (".modal{box-shadow:0 20px 60px rgba(0,0,0,.25)}", set()),
        (".cube{/* flat-ok: 3D object */box-shadow:0 22px 40px -30px rgba(15,23,42,.35)}", set()),
        ("/* flat-ok: device drawing */\n.dev{box-shadow:0 12px 32px rgba(0,0,0,.12)}", set()),
        (".hero h1{text-shadow:0 2px 24px rgba(0,0,0,.25)}", set()),
        (".card{backdrop-filter:blur(12px)}", {"glass"}),
        (".hdr{backdrop-filter:blur(10px)}", set()),
        ("@keyframes ping{0%{box-shadow:0 0 0 0 rgba(0,0,0,.4)}100%{box-shadow:0 0 0 9px transparent}}", set()),
    ]
    bad = []
    for css, want in cases:
        got = {f.code for f in check(css, fams)}
        if got != want:
            bad.append("%s\n    want %s, got %s" % (css, sorted(want), sorted(got)))
    return bad


if __name__ == "__main__":
    import sys
    problems = _self_test()
    for p in problems:
        print("FAIL " + p)
    print("flat_css self-test: %s" % ("FAILED" if problems else "OK"))
    sys.exit(1 if problems else 0)
