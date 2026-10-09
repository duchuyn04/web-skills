#!/usr/bin/env python3
"""Build a BPO landing page from a page.json config. Python standard library only.

Usage:
    python build.py page.json --out dist
    python build.py --list            print archetypes, presets, variants, icons, images, cities

The model writes page.json. This script owns layout, spacing, colors, animation and markup.
Every error names the JSON path and says how to fix it.
"""
import argparse
import datetime
import html
import hashlib
import json
import math
import re
import shutil
import sys
import urllib.parse
for _stream in (sys.stdout, sys.stderr):  # Vietnamese text must not crash printing on a cp1252 console or pipe
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rules  # noqa: E402
import seo  # noqa: E402

SKILL = HERE.parent
# Version of the content rules. Bump it when a new check can fail a page that built before, and add a CHANGELOG.md
# entry. A site built under an older version keeps building with "rules": "<that version>" (see rules_pin in main).
RULES_VERSION = 6
TPL = SKILL / "templates"
SECTIONS_DIR = TPL / "sections"
IMAGES_DIR = TPL / "assets" / "images"

ARROW_SVG = ('<svg class="arrow-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" '
             'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"></line>'
             '<polyline points="12 5 19 12 12 19"></polyline></svg>')
MAP_LAT_TOP, MAP_LAT_BOTTOM = 80.0, -55.0  # matches the 54 rows x 2.5 deg in partials/world-dots.html


class Safe(str):
    """Already-escaped HTML."""


def load_json(path):
    # utf-8-sig: Notepad and PowerShell 5.1 save UTF-8 with a byte order mark
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


# --------------------------------------------------------------------------- colors
def parse_hex(value):
    v = value.strip().lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", v):
        return None
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))


def to_hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(c))) for c in rgb)


def mix(a, b, t):
    return tuple(a[i] * (1 - t) + b[i] * t for i in range(3))


def luminance(rgb):
    def ch(c):
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def ink_for(color, bg, target=4.5):
    """Shift color toward white or black until it reaches target contrast on bg."""
    if contrast(color, bg) >= target:
        return color
    goal = (255, 255, 255) if luminance(bg) < 0.4 else (0, 0, 0)
    for step in range(1, 26):
        c = mix(color, goal, step * 0.04)
        if contrast(c, bg) >= target:
            return c
    return goal


# --------------------------------------------------------------------------- perceptual colour (OKLab / OKLCH)
# Conversion matrices from Bjorn Ottosson's OKLab definition, the same ones CSS Color 4 uses for oklab()/oklch().
def _lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _gam(c):
    c = 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055
    return c * 255.0


def to_oklch(rgb):
    r, g, b = (_lin(c) for c in rgb)
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    a = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    bb = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return L, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360


def _oklch_raw(L, C, h):
    a, b = C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)


def from_oklch(L, C, h):
    """OKLCH to sRGB 0-255. Out-of-gamut colours keep L and h and lose chroma until they fit (CSS Color 4 gamut mapping idea)."""
    L = min(max(L, 0.0), 1.0)
    lo, hi = 0.0, C
    rgb = _oklch_raw(L, C, h)
    if min(rgb) < -1e-4 or max(rgb) > 1 + 1e-4:
        for _ in range(24):
            mid = (lo + hi) / 2
            t = _oklch_raw(L, mid, h)
            if min(t) < -1e-4 or max(t) > 1 + 1e-4:
                hi = mid
            else:
                lo = mid
        rgb = _oklch_raw(L, lo, h)
    return tuple(min(max(_gam(min(max(c, 0.0), 1.0)), 0.0), 255.0) for c in rgb)


def hue_distance(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def ensure_contrast(color, bgs, target=4.5):
    """Move colour lightness in OKLCH (hue kept) until it reaches target contrast on every background in bgs.
    Goes darker on light backgrounds and lighter on dark ones; returns the original colour when it already passes."""
    if all(contrast(color, bg) >= target for bg in bgs):
        return color
    L0, C, h = to_oklch(color)
    worst = lambda c: min(contrast(c, bg) for bg in bgs)
    # Try both directions: a mid-tone ground (teal, orange) often only works with light text.
    found = []
    for step in (-0.01, 0.01):
        L = L0
        for _ in range(100):
            L += step
            if L <= 0 or L >= 1:
                break
            c = from_oklch(L, C, h)
            if worst(c) >= target:
                found.append((abs(L - L0), c))
                break
    if found:
        return min(found, key=lambda x: x[0])[1]
    return max(((0, 0, 0), (255, 255, 255)), key=worst)


# --------------------------------------------------------------------------- template engine
TOKEN_RE = re.compile(r"\{\{\s*([#^/>]?)\s*(.*?)\s*\}\}")


def parse_template(src, name):
    root = []
    stack = [(None, root)]
    pos = 0
    for m in TOKEN_RE.finditer(src):
        if m.start() > pos:
            stack[-1][1].append(("text", src[pos:m.start()]))
        kind, key = m.group(1), m.group(2)
        if kind in ("#", "^"):
            node = ("section", key, [], kind == "^")
            stack[-1][1].append(node)
            stack.append((key, node[2]))
        elif kind == "/":
            if stack[-1][0] != key:
                raise SystemExit("Template error in %s: {{/%s}} closes {{#%s}}" % (name, key, stack[-1][0]))
            stack.pop()
        elif kind == ">":
            stack[-1][1].append(("partial", key))
        else:
            stack[-1][1].append(("var", key))
        pos = m.end()
    if len(stack) != 1:
        raise SystemExit("Template error in %s: {{#%s}} is never closed" % (name, stack[-1][0]))
    root.append(("text", src[pos:]))
    return root


class Renderer:
    def __init__(self, icons, flags):
        self.icons = icons
        self.flags = flags
        self.partials = {}
        self.cache = {}

    def template(self, path):
        path = Path(path)
        if path not in self.cache:
            self.cache[path] = parse_template(path.read_text(encoding="utf-8"), str(path))
        return self.cache[path]

    def lookup(self, key, stack):
        if key == ".":
            return stack[-1]
        parts = key.split(".")
        for frame in reversed(stack):
            if isinstance(frame, dict) and parts[0] in frame:
                val = frame[parts[0]]
                for p in parts[1:]:
                    if isinstance(val, dict):
                        val = val.get(p)
                    elif isinstance(val, list) and p.isdigit() and int(p) < len(val):
                        val = val[int(p)]
                    else:
                        val = None
                return val
        return None

    def icon(self, name, cls="bl-icon"):
        body = self.icons.get(name)
        if body is None:
            return ""
        return ('<svg class="%s" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
                'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>' % (cls, body))

    def flag(self, code):
        f = self.flags.get((code or "").lower())
        if not f:
            return ""
        return '<svg class="bl-flag" viewBox="0 0 24 16" aria-hidden="true">%s</svg>' % f["svg"]

    def render_nodes(self, nodes, stack):
        out = []
        for node in nodes:
            kind = node[0]
            if kind == "text":
                out.append(node[1])
            elif kind == "var":
                out.append(self.render_var(node[1], stack))
            elif kind == "partial":
                out.append(self.render_nodes(self.template(TPL / "partials" / (node[1] + ".html")), stack))
            else:
                _, key, children, inverted = node
                val = self.lookup(key, stack)
                empty = val is None or val is False or val == "" or val == [] or val == {}
                if inverted:
                    if empty:
                        out.append(self.render_nodes(children, stack))
                    continue
                if empty:
                    continue
                if isinstance(val, list):
                    n = len(val)
                    for i, item in enumerate(val):
                        meta = {"@index": i, "@num": "%02d" % (i + 1), "@n": i + 1, "@first": i == 0, "@last": i == n - 1}
                        out.append(self.render_nodes(children, stack + [meta, item]))
                elif isinstance(val, dict):
                    out.append(self.render_nodes(children, stack + [val]))
                else:
                    out.append(self.render_nodes(children, stack))
        return "".join(out)

    def render_var(self, key, stack):
        if key == "arrow":
            return ARROW_SVG
        if key.startswith("icon:"):
            spec = key[5:].split()
            name = spec[0]
            if name.startswith("$"):
                name = self.lookup(name[1:], stack) or ""
            return self.icon(name, " ".join(["bl-icon"] + spec[1:]))
        if key.startswith("flag:"):
            code = key[5:]
            if code.startswith("$"):
                code = self.lookup(code[1:], stack) or ""
            return self.flag(code)
        if key.startswith("urlq:"):
            # a value inside a URL query, for example a map search: {{urlq:address}}
            return html.escape(urllib.parse.quote_plus(str(self.lookup(key[5:], stack) or "")), quote=True)
        if key.startswith("json:"):
            return html.escape(json.dumps(self.lookup(key[5:], stack), ensure_ascii=False), quote=True)
        val = self.lookup(key, stack)
        if val is None:
            return ""
        if isinstance(val, Safe):
            return val
        if isinstance(val, bool):
            return "true" if val else "false"
        if isinstance(val, (int, float)):
            return str(val)
        if isinstance(val, (dict, list)):
            return html.escape(json.dumps(val, ensure_ascii=False), quote=True)
        return html.escape(str(val), quote=True)

    def render_file(self, path, stack):
        return self.render_nodes(self.template(path), stack)


# --------------------------------------------------------------------------- validation
class Ctx:
    def __init__(self, page_dir, out_dir, lib):
        self.errors = []
        self.warnings = []
        self.page_dir = page_dir
        self.out_dir = out_dir
        self.lib = lib
        self.images = {}
        self.anchors = []
        self.placeholders = []
        self.soft = False

    def err(self, path, msg):
        if self.soft:
            self.warnings.append("%s: [rules %s, not enforced] %s" % (path, self.soft, msg))
        else:
            self.errors.append("%s: %s" % (path, msg))

    def warn(self, path, msg):
        self.warnings.append("%s: %s" % (path, msg))


PLACEHOLDER_RE = re.compile(r"^\[[^\]]{1,40}\]$")
MARKUP_RE = re.compile(r"\*([^*]+)\*")
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
HREF_RE = re.compile(r"^(#[A-Za-z][\w-]*|#|https?://\S+|mailto:\S+|tel:[+\d][\d\s-]*|[\w./-]+\.(html|pdf))$")
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def check_copy(ctx, path, text):
    for f in rules.check_text(text):
        (ctx.err if f.level == "error" else ctx.warn)(path, "%s (near: \"%s\")" % (f.message, f.excerpt))
    for m in re.finditer(r"\[[^\]]{1,40}\]", text):
        ctx.placeholders.append("%s: %s" % (path, m.group()))


def text_len(s):
    return len(MARKUP_RE.sub(r"\1", BOLD_RE.sub(r"\1", s)))


def plain(s):
    return MARKUP_RE.sub(r"\1", BOLD_RE.sub(r"\1", s))


def validate(ctx, value, spec, path):
    t = spec.get("type", "text")
    if t in ("text", "markup", "email", "phone"):
        if not isinstance(value, str):
            ctx.err(path, "must be a string, got %s" % type(value).__name__)
            return ""
        value = value.strip()
        n = text_len(value)
        lo, hi = spec.get("min", 1), spec.get("max", 400)
        if n < lo:
            ctx.err(path, "too short (%d chars, minimum %d). Write a fuller line." % (n, lo))
        if n > hi:
            ctx.err(path, "too long (%d chars, maximum %d). Cut it to fit the layout; do not shrink the font." % (n, hi))
        if t != "markup" and "*" in value:
            ctx.err(path, "'*' accent markup is only allowed in markup fields (titles). Remove the asterisks.")
        if t == "email" and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", value, re.I):
            ctx.err(path, "not a valid email address")
        check_copy(ctx, path, value)
        if t == "markup":
            if value.count("*") % 2:
                ctx.err(path, "odd number of '*'. Wrap accent words as *like this*.")
            esc = BOLD_RE.sub(r"<strong>\1</strong>", html.escape(value, quote=False))
            return Safe(MARKUP_RE.sub(r'<span class="bl-hl">\1</span>', esc))
        return value
    if t == "number":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            ctx.err(path, "must be a number (no quotes, no units). Put units in prefix/suffix fields.")
            return 0
        if "min" in spec and value < spec["min"]:
            ctx.err(path, "must be >= %s" % spec["min"])
        if "max" in spec and value > spec["max"]:
            ctx.err(path, "must be <= %s" % spec["max"])
        return value
    if t == "stat":
        if isinstance(value, str) and PLACEHOLDER_RE.match(value.strip()):
            ctx.warn(path, "placeholder %s. Ask the client for the real figure before launch." % value)
            ctx.placeholders.append("%s: %s" % (path, value))
            return {"placeholder": value.strip()}
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            ctx.err(path, "must be a number like 1500 or 99.4, or a placeholder like \"[KPI]\". Never invent a figure.")
            return {"placeholder": "[KPI]"}
        return {"number": value}
    if t == "bool":
        if not isinstance(value, bool):
            ctx.err(path, "must be true or false")
            return False
        return value
    if t == "enum":
        if value not in spec["values"]:
            ctx.err(path, "must be one of %s, got %r" % (spec["values"], value))
            return spec["values"][0]
        return value
    if t == "icon":
        if value not in ctx.lib["icons"]:
            ctx.err(path, "unknown icon %r. Pick one of: %s" % (value, ", ".join(sorted(ctx.lib["icons"]))))
        return value
    if t == "flag":
        v = str(value).lower()
        if v not in ctx.lib["flags"]:
            ctx.err(path, "unknown flag %r. Use a lowercase ISO country code from: %s" % (value, ", ".join(sorted(ctx.lib["flags"]))))
        return v
    if t == "color":
        if not isinstance(value, str) or not HEX_RE.match(value):
            ctx.err(path, "must be a 6-digit hex color like \"#0a1128\"")
            return None
        return value.lower()
    if t == "href":
        if not isinstance(value, str) or not HREF_RE.match(value.strip()):
            ctx.err(path, "invalid link %r. Use \"#section-id\", \"https://...\", \"mailto:...\" or \"tel:...\"." % value)
            return "#"
        if value.startswith("#") and len(value) > 1:
            ctx.anchors.append((path, value[1:]))
        return value.strip()
    if t == "image":
        return resolve_image(ctx, value, path)
    if t == "video":
        return resolve_video(ctx, value, path)
    if t == "embed":
        return resolve_embed(ctx, value, path)
    if t == "audio":
        return resolve_file(ctx, value, path, "assets/audio/", (".mp3", ".m4a", ".ogg", ".wav", ".webm"))
    if t == "city":
        return resolve_city(ctx, value, path)
    if t == "list":
        if not isinstance(value, list):
            ctx.err(path, "must be a list [...]")
            return []
        lo, hi = spec.get("min", 0), spec.get("max", 99)
        if spec.get("counts") and len(value) not in spec["counts"]:
            ctx.err(path, "needs %s items, got %d. Other counts leave gaps in the grid. Do not pad the list with items the brief does not support; if the client has fewer, use another variant for this slot or drop the section." %
                    (" or ".join(str(c) for c in spec["counts"]), len(value)))
        elif not lo <= len(value) <= hi:
            ctx.err(path, "needs %s items, got %d. The grid is designed for this count; add or remove items." %
                    (("exactly %d" % lo) if lo == hi else "%d to %d" % (lo, hi), len(value)))
        item_spec = spec["item"]
        return [validate(ctx, v, item_spec, "%s[%d]" % (path, i)) for i, v in enumerate(value)]
    if t == "object":
        return validate_object(ctx, value, spec, path)
    ctx.err(path, "schema bug: unknown type %r" % t)
    return value


def validate_object(ctx, value, spec, path):
    if not isinstance(value, dict):
        ctx.err(path, "must be an object {...}")
        return {}
    fields = spec["fields"]
    out = {}
    for k in value:
        if k not in fields and not k.startswith("_"):
            ctx.err("%s.%s" % (path, k), "unknown field. Allowed fields here: %s" % ", ".join(fields))
    for k, fs in fields.items():
        p = "%s.%s" % (path, k)
        if k in value and value[k] is not None:
            out[k] = validate(ctx, value[k], fs, p)
            if fs.get("type") == "markup" and isinstance(value[k], str):
                out[k + "_plain"] = plain(value[k].strip())
        elif "default" in fs:
            out[k] = fs["default"]
        elif fs.get("required", True):
            ctx.err(p, "missing required field (%s)" % describe(fs))
        else:
            out[k] = None
    return out


def describe(fs):
    t = fs.get("type", "text")
    if t in ("text", "markup"):
        return "%s, %d-%d chars" % (t, fs.get("min", 1), fs.get("max", 400))
    if t == "list":
        return "list of %d-%d items" % (fs.get("min", 0), fs.get("max", 99))
    if t == "enum":
        return "one of %s" % fs["values"]
    return t


def resolve_image(ctx, value, path):
    if not isinstance(value, str) or not value:
        ctx.err(path, "must be an image key or a file path")
        return ""
    if value.startswith(("http://", "https://")):
        ctx.warn(path, "remote image %s. Download it into the project so the page works offline." % value)
        return value
    lib = ctx.lib["images"]
    if value in lib:
        src = lib[value]
    else:
        src = (ctx.page_dir / value).resolve()
        if not src.is_file():
            ctx.err(path, "image %r not found. Use a library key (%s) or a path relative to page.json." % (value, ", ".join(sorted(lib))))
            return ""
    rel = "assets/img/" + src.name
    ctx.images[rel] = src
    return rel


def resolve_video(ctx, value, path):
    lib = ctx.lib["videos"]
    if isinstance(value, str) and value in lib:
        rel = "assets/video/" + lib[value].name
        ctx.images[rel] = lib[value]
        return rel
    return resolve_file(ctx, value, path, "assets/video/", (".mp4", ".webm"))


YOUTUBE_RE = re.compile(r"^https?://(?:www\.)?(?:youtube\.com/watch\?(?:.*&)?v=|youtu\.be/|youtube\.com/embed/)([\w-]{11})")
VIMEO_RE = re.compile(r"^https?://(?:www\.)?(?:vimeo\.com/|player\.vimeo\.com/video/)(\d+)")


def resolve_embed(ctx, value, path):
    """Turn a YouTube or Vimeo page URL into a privacy-friendly embed URL. The iframe is only created on click."""
    v = str(value).strip()
    m = YOUTUBE_RE.match(v)
    if m:
        return "https://www.youtube-nocookie.com/embed/%s?autoplay=1&rel=0" % m.group(1)
    m = VIMEO_RE.match(v)
    if m:
        return "https://player.vimeo.com/video/%s?autoplay=1&dnt=1" % m.group(1)
    ctx.err(path, "embed must be a YouTube or Vimeo video URL, got %r" % value)
    return ""


def resolve_file(ctx, value, path, folder, exts):
    src = (ctx.page_dir / str(value)).resolve()
    if not src.is_file() or src.suffix.lower() not in exts:
        ctx.err(path, "file %r not found next to page.json (allowed types: %s)" % (value, ", ".join(exts)))
        return ""
    rel = folder + src.name
    ctx.images[rel] = src
    return rel


def resolve_city(ctx, value, path):
    cities = ctx.lib["cities"]
    if isinstance(value, str):
        c = cities.get(value)
        if not c:
            ctx.err(path, "unknown city %r. Use a key from templates/data/cities.json (%s) or an object {name, country, lat, lon}." %
                    (value, ", ".join(sorted(k for k in cities if not k.startswith("_")))))
            return {}
        c = dict(c, key=value)
    elif isinstance(value, dict) and {"name", "country", "lat", "lon"} <= set(value):
        c = dict(value, key=re.sub(r"[^a-z0-9]+", "-", value["name"].lower()))
    else:
        ctx.err(path, "city must be a key like \"manila\" or {name, country, lat, lon}")
        return {}
    c["x"] = round((c["lon"] + 180) / 360 * 100, 2)
    c["y"] = round((MAP_LAT_TOP - c["lat"]) / (MAP_LAT_TOP - MAP_LAT_BOTTOM) * 100, 2)
    c["tip"] = "end" if c["x"] > 80 else ("start" if c["x"] < 20 else "center")
    c["flag_code"] = c["country"]
    c["country_name"] = ctx.lib["flags"].get(c["country"], {}).get("name", c["country"].upper())
    return c


def enrich_stats(obj):
    """Turn stat fields into display strings plus counter attributes; add initials and tel: links."""
    if isinstance(obj, dict) and isinstance(obj.get("phone"), str):
        obj["phone_href"] = "tel:" + re.sub(r"[^\d+]", "", obj["phone"])
    if isinstance(obj, dict) and isinstance(obj.get("name"), str) and "avatar" in obj:
        words = re.findall(r"[^\W\d_]+", obj["name"])
        obj["initials"] = "".join(w[0] for w in words[:2]).upper() or "?"
    if isinstance(obj, list):
        for v in obj:
            enrich_stats(v)
        return
    if not isinstance(obj, dict):
        return
    for k, v in list(obj.items()):
        if isinstance(v, dict) and ("number" in v or "placeholder" in v) and len(v) == 1:
            if "placeholder" in v:
                obj[k] = {"display": v["placeholder"], "count": None}
            else:
                num = v["number"]
                dec = obj.get("decimals")
                if dec is None:
                    dec = len(str(num).split(".")[1]) if isinstance(num, float) and "." in str(num) else 0
                pre, suf = obj.get("prefix") or "", obj.get("suffix") or ""
                if len(suf) >= 3 and suf[0].isalpha():
                    suf = " " + suf  # a word unit ("2 weeks", "5 năm"); short units stay attached ("10k", "3x", "5bn")
                if isinstance(num, int) and 1900 <= num <= 2099 and not pre and not suf:
                    # A year: no thousands separator and no count-up from zero.
                    obj[k] = {"display": str(num), "count": None}
                    continue
                shown = format(num, ",.%df" % dec)
                obj[k] = {"display": "%s%s%s" % (pre, shown, suf), "count": num, "decimals": dec, "prefix": pre, "suffix": suf}
        else:
            enrich_stats(v)


# --------------------------------------------------------------------------- library
def load_library():
    icons = {k: v for k, v in load_json(TPL / "data" / "icons.json").items() if not k.startswith("_")}
    flags = {k: v for k, v in load_json(TPL / "data" / "flags.json").items() if not k.startswith("_")}
    cities = load_json(TPL / "data" / "cities.json")
    presets = {p.stem: load_json(p) for p in sorted((TPL / "presets").glob("*.json"))}
    archetypes = load_json(TPL / "archetypes.json")
    defs = load_json(TPL / "data" / "schema-defs.json")
    variants = {}
    for d in sorted(SECTIONS_DIR.iterdir()):
        if (d / "schema.json").is_file():
            variants[d.name] = dict(resolve_refs(load_json(d / "schema.json"), defs), _dir=d)
    images = {p.stem: p for p in sorted(IMAGES_DIR.glob("*")) if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp", ".svg")}
    videos = {p.stem: p for p in sorted((TPL / "assets" / "video").glob("*")) if p.suffix.lower() in (".mp4", ".webm")}
    blueprints = {p.stem: load_json(p) for p in sorted((TPL / "blueprints").glob("*.json"))} if (TPL / "blueprints").is_dir() else {}
    return {"icons": icons, "flags": flags, "cities": cities, "presets": presets,
            "archetypes": {k: v for k, v in archetypes.items() if not k.startswith("_")},
            "variants": variants, "images": images, "videos": videos, "blueprints": blueprints}


def resolve_refs(node, defs):
    if isinstance(node, dict):
        if "$ref" in node:
            base = json.loads(json.dumps(defs[node["$ref"]]))
            base.update({k: v for k, v in node.items() if k != "$ref"})
            return resolve_refs(base, defs)
        return {k: resolve_refs(v, defs) for k, v in node.items()}
    if isinstance(node, list):
        return [resolve_refs(v, defs) for v in node]
    return node


def print_library(lib):
    print("ARCHETYPES")
    for k, a in lib["archetypes"].items():
        print("  %-18s %s" % (k, a["use_for"]))
        print("  %-18s slots: %s" % ("", " | ".join(("%s%s" % (s["slot"], "" if s.get("required") else "?")) for s in a["slots"])))
    print("\nPRESETS")
    for k, p in lib["presets"].items():
        print("  %-18s %s" % (k, p["use_for"]))
    print("\nVARIANTS")
    for k, v in lib["variants"].items():
        print("  %-22s %s" % (k, v["summary"]))
    print("\nICONS\n  " + ", ".join(sorted(lib["icons"])))
    print("\nFLAGS\n  " + ", ".join(sorted(lib["flags"])))
    print("\nIMAGES\n  " + ", ".join(sorted(lib["images"])))
    print("\nVIDEOS\n  " + (", ".join(sorted(lib["videos"])) or "(none)"))
    print("\nCITIES\n  " + ", ".join(sorted(k for k in lib["cities"] if not k.startswith("_"))))


# --------------------------------------------------------------------------- theme
def resolve_color(expr, colors):
    expr = expr.strip()
    if expr.startswith("$"):
        return colors[expr[1:]]
    m = re.fullmatch(r"mix\(([^,]+),([^,]+),([\d.]+)\)", expr.replace(" ", ""))
    if m:
        return to_hex(mix(parse_hex(resolve_color(m.group(1), colors)), parse_hex(resolve_color(m.group(2), colors)), float(m.group(3))))
    return expr


def fill_for_white_text(color, target=4.5, margin=0.05):
    """Darken at constant OKLCH hue until white text passes (research note ui-color-system.md, 3.6)."""
    white = (255, 255, 255)
    if contrast(color, white) >= target + margin:
        return color
    L0, C0, H0 = to_oklch(color)
    lo, hi = 0.0, L0
    for _ in range(40):
        mid = (lo + hi) / 2
        if contrast(from_oklch(mid, C0, H0), white) >= target + margin:
            lo = mid
        else:
            hi = mid
    out = parse_hex(to_hex(from_oklch(lo, C0, H0)))
    return out if contrast(out, white) >= target else ensure_contrast(out, [white], target)


def tint_neutral(rgb, hue, cap):
    """Keep a neutral's lightness, move its hue to the brand hue and cap its chroma (rules 14-15).
    Neutrals under 0.01 chroma have no readable hue and stay as they are."""
    L, C, h = to_oklch(rgb)
    if C < 0.01 or hue_distance(h, hue) <= 45 and C <= cap:
        return rgb
    return from_oklch(L, min(C, cap), hue)


def theme_css(preset, overrides, ctx):
    """Colour tokens. Rules come from docs/research/ui-color-system.md (see references/color-system.md):
    white button labels at 4.5:1 by darkening the accent at constant hue, accent_2 kept analogous,
    neutrals tinted toward the accent hue, every text token checked on bg, surface and surface_2,
    input borders and focus rings at 3:1, no glows or gradients between clashing hues."""
    colors = dict(preset["colors"])
    given = set()
    for k in ("primary", "accent", "accent_2"):
        if overrides.get(k):
            colors[k] = overrides[k]
            given.add(k)
    # A light, coloured primary with no accent is the logo colour put in the wrong key: it becomes the accent.
    if "primary" in given and "accent" not in given:
        Lp, Cp, Hp = to_oklch(parse_hex(colors["primary"]))
        if Lp > 0.40 and Cp >= 0.05:
            ctx.warn("theme.primary", "primary %s is a light brand colour, so it is used as theme.accent (buttons, links, highlights) and dark sections keep a dark colour. Put the logo colour in theme.accent next time." % colors["primary"])
            colors["accent"] = colors["primary"]
            colors["primary"] = preset["colors"]["primary"]
            given.discard("primary")
            given.add("accent")
    white, ink = (255, 255, 255), (11, 15, 25)

    # Accent: the button fill. White label at 4.5:1 (rules 2-4).
    brand = parse_hex(colors["accent"])
    L0, C0, H0 = to_oklch(brand)
    accent = brand
    if contrast(brand, white) >= 4.5:
        on_accent = white
    elif L0 >= 0.80:
        on_accent = ensure_contrast(from_oklch(0.22, min(C0 * 0.2, 0.03), H0), [brand], 4.5)
    else:
        accent = fill_for_white_text(brand)
        on_accent = white
        L1, _, H1 = to_oklch(accent)
        ctx.warn("theme.accent", "accent %s gives white button text only %.2f:1, so buttons use %s (same hue, white text %.2f:1). %s"
                 % (to_hex(brand), contrast(brand, white), to_hex(accent), contrast(accent, white),
                    "The original stays as accent_2 for glows and highlights." if "accent_2" not in given else "Set a darker accent yourself to choose the shade."))
        if L0 - L1 > 0.20:
            ctx.warn("theme.accent", "the accent had to lose %.2f of its lightness to carry white text; check that %s still reads as the brand." % (L0 - L1, to_hex(accent)))
        if "accent_2" not in given:
            colors["accent_2"] = to_hex(brand)
    colors["accent"] = to_hex(accent)

    # Primary paints dark sections and the footer, so it must be dark. A mid or light brand colour there is a mistake.
    if "primary" in given:
        Lp, Cp, Hp = to_oklch(parse_hex(colors["primary"]))
        if Lp > 0.40:
            dark = to_hex(from_oklch(0.24, min(Cp, 0.04), Hp))
            ctx.warn("theme.primary", "primary %s is too light for dark sections and the footer (OKLCH L %.2f), so they use %s, a dark shade of the same hue. %s"
                     % (colors["primary"], Lp, dark, "A logo colour belongs in theme.accent." if "accent" not in given else "Give a dark brand colour, or leave primary out."))
            colors["primary"] = dark
    # Primary: a warm brand given without a dark colour gets a brand-tinted dark, not the preset navy (rule 16).
    if "accent" in given and "primary" not in given and C0 >= 0.03 and 20 <= H0 <= 100 and hue_distance(to_oklch(parse_hex(colors["primary"]))[2], H0) > 90:
        colors["primary"] = to_hex(from_oklch(0.24, min(0.03, 0.2 * C0), H0))
        ctx.warn("theme.primary", "warm accent with the preset's cool dark colour: dark sections now use %s, a dark tint of the accent hue. Set theme.primary to keep another colour." % colors["primary"])

    # accent_2: analogous (within 60 degrees) unless the client supplied it (rules 9-10).
    a2 = parse_hex(colors["accent_2"])
    La2, Ca2, Ha2 = to_oklch(a2)
    spread = hue_distance(H0, Ha2) if Ca2 >= 0.03 and C0 >= 0.03 else 0
    if spread > 60 and "accent_2" not in given:
        a2 = from_oklch(min(L0 + 0.15, 0.85), 0.8 * C0, (H0 + 25) % 360)
        colors["accent_2"] = to_hex(a2)
        spread = 25
    elif spread > 90:
        ctx.warn("theme.accent_2", "accent and accent_2 are %d degrees apart; glows and gradients use shades of the accent only, so the two never mix into grey." % spread)
    # Colour that may be blended with the accent in glows and gradients.
    blend = a2 if spread <= 90 else from_oklch(min(L0 + 0.15, 0.85), C0, H0)
    # Gradient end behind on-accent text must still carry that text (rule 13).
    blend_deep = ensure_contrast(blend, [on_accent], 4.5)

    lines = [":root {",
             "  --font-heading: '%s', system-ui, sans-serif;" % preset["fonts"]["heading"],
             "  --font-body: '%s', system-ui, sans-serif;" % preset["fonts"]["body"],
             "  --font-mono: '%s', ui-monospace, monospace;" % preset["fonts"]["mono"],
             "  --heading-weight: %s;" % preset["type"]["heading_weight"],
             "  --heading-tracking: %s;" % preset["type"]["heading_tracking"],
             "  --vi-head-lh: %s;" % VI_HEAD_LH.get(preset["fonts"]["heading"], 1.25),
             "  --c-primary: %s;" % colors["primary"],
             "  --c-accent: %s;" % colors["accent"],
             "  --c-accent-2: %s;" % colors["accent_2"],
             "  --c-accent-blend: %s;" % to_hex(blend),
             "  --c-accent-blend-deep: %s;" % to_hex(blend_deep),
             "  --c-on-accent: %s;" % to_hex(on_accent),
             # Accent text or marks placed on a --c-primary block inside a light section.
             "  --c-accent-on-dark: %s;" % to_hex(ensure_contrast(accent, [parse_hex(colors["primary"]), mix(parse_hex(colors["primary"]), white, 0.06)]))]
    for k, v in preset["shape"].items():
        lines.append("  --%s: %s;" % (k.replace("_", "-"), v))
    lines.append("}")

    primary = parse_hex(colors["primary"])
    for tone, spec in preset["tones"].items():
        vals = {k: resolve_color(v, colors) if isinstance(v, str) else v for k, v in spec.items()}
        dark = vals["is_dark"]
        # Neutrals follow the accent hue at low chroma (rules 14-15); values tied to the brand ($primary) stay.
        for key, cap in (("bg", 0.012), ("surface", 0.012), ("surface_2", 0.015), ("text", 0.02), ("text_muted", 0.02)):
            raw = spec.get(key)
            c = parse_hex(vals[key]) if isinstance(vals[key], str) else None
            if c and not (isinstance(raw, str) and "$" in raw):
                vals[key] = to_hex(tint_neutral(c, H0, cap))
        bg = parse_hex(vals["bg"])
        surf = parse_hex(vals["surface"]) or bg
        surf2 = parse_hex(vals["surface_2"]) or surf
        grounds = [bg, surf, surf2]
        strong = parse_hex(vals["text_strong"])
        # Text on every ground it sits on (rule 6).
        for key in ("text_strong", "text", "text_muted"):
            c = parse_hex(vals[key])
            if c:
                vals[key] = to_hex(ensure_contrast(c, grounds))
        # Accent text: also on the accent-tinted chip ground (rule 5).
        soft = [mix(g, accent, 0.14) for g in grounds]
        accent_ink = ensure_contrast(accent, grounds + soft)
        accent2_ink = ensure_contrast(a2, grounds, 3.0)
        border_strong = to_hex(mix(bg, strong, 0.22 if not dark else 0.28))
        border_input = ensure_contrast(parse_hex(border_strong), [bg, surf], 3.0)
        focus = ensure_contrast(accent, [bg, surf], 3.0)
        lines += [".bl-tone-%s {" % tone,
                  "  color-scheme: %s;" % ("dark" if dark else "light"),
                  "  --bg: %s;" % vals["bg"],
                  "  --surface: %s;" % vals["surface"],
                  "  --surface-2: %s;" % vals["surface_2"],
                  "  --text: %s;" % vals["text"],
                  "  --text-strong: %s;" % vals["text_strong"],
                  "  --text-muted: %s;" % vals["text_muted"],
                  "  --border: %s;" % vals["border"],
                  "  --border-strong: %s;" % border_strong,
                  "  --border-input: %s;" % to_hex(border_input),
                  "  --focus-ring: %s;" % to_hex(focus),
                  "  --accent-ink: %s;" % to_hex(accent_ink),
                  "  --accent-2-ink: %s;" % to_hex(accent2_ink),
                  "  --glass: %s;" % ("rgba(%d, %d, %d, 0.62)" % tuple(int(c) for c in surf) if dark else "rgba(255, 255, 255, 0.74)"),
                  "  --glass-border: %s;" % ("rgba(255, 255, 255, 0.12)" if dark else "rgba(255, 255, 255, 0.9)"),
                  "  --shadow-lg: %s;" % ("0 24px 48px -20px rgba(0, 0, 0, 0.65)" if dark else "0 24px 48px -24px rgba(15, 23, 42, 0.24)"),
                  "}"]

    # Accent tone: sections painted in the brand colour (hero-gradient). Text uses the button text colour.
    on = on_accent
    txt = mix(on, accent, 0.10)
    if contrast(txt, accent) < 4.5:
        txt = on
    muted = mix(on, accent, 0.22)
    if contrast(muted, accent) < 4.5:
        muted = txt
    a_dark = luminance(accent) < 0.4
    lines += [".bl-tone-accent {",
              "  color-scheme: %s;" % ("dark" if a_dark else "light"),
              "  --bg: %s;" % to_hex(accent),
              "  --surface: %s;" % to_hex(mix(accent, on, 0.10)),
              "  --surface-2: %s;" % to_hex(mix(accent, on, 0.16)),
              "  --text: %s;" % to_hex(txt),
              "  --text-strong: %s;" % to_hex(on),
              "  --text-muted: %s;" % to_hex(muted),
              "  --border: rgba(%d, %d, %d, 0.28);" % tuple(int(c) for c in on),
              "  --border-strong: rgba(%d, %d, %d, 0.55);" % tuple(int(c) for c in on),
              "  --border-input: rgba(%d, %d, %d, 0.75);" % tuple(int(c) for c in on),
              "  --focus-ring: %s;" % to_hex(on),
              "  --accent-ink: %s;" % to_hex(on),
              "  --accent-2-ink: %s;" % to_hex(on),
              "  --glass: rgba(%d, %d, %d, 0.16);" % tuple(int(c) for c in on),
              "  --glass-border: rgba(%d, %d, %d, 0.3);" % tuple(int(c) for c in on),
              "  --shadow-lg: 0 24px 48px -24px rgba(0, 0, 0, 0.35);",
              "}"]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- page structure
YOU_RE = {"en": re.compile(r"\byou(?:r|rs)?\b", re.I), "vi": re.compile(r"\bbạn\b", re.I)}
EVERY_RE = re.compile(r"\b(?:every|each) (?:call|contact|ticket|agent|hire|batch|program|interaction|step)\b", re.I)


def all_strings(sections):
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k not in ("href", "src", "image", "icon", "flag", "city"):
                    yield from walk(v)
        elif isinstance(o, list):
            for v in o:
                yield from walk(v)
        elif isinstance(o, str):
            yield o
    for s in sections:
        yield from walk(s["data"])


_EXAMPLE_TEXT = None
NUMBER_WORDS = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7", "eight": "8",
                "nine": "9", "ten": "10", "twelve": "12", "fifteen": "15", "twenty": "20", "thirty": "30"}
NUMBER_TERM_RE = re.compile(r"\b(\d[\d,.]*|%s)[\s-]+(minutes?|hours?|days?|business days?|working days?|weeks?|months?|years?|seats?|agents?|people|items?|contacts?|rings?)\b" % "|".join(NUMBER_WORDS), re.I)


def number_terms(text):
    """'30 days notice' and 'thirty-day' both give {'30 day'}: numbers with units, normalised."""
    out = set()
    for n, unit in NUMBER_TERM_RE.findall(text):
        n = NUMBER_WORDS.get(n.lower(), n.replace(",", ""))
        out.add("%s %s" % (n, unit.lower().rstrip("s").replace("business day", "day").replace("working day", "day")))
    return out


def _example_sentences():
    """Word sets of every long string in the example pages, loaded once."""
    global _EXAMPLE_TEXT
    if _EXAMPLE_TEXT is None:
        _EXAMPLE_TEXT = []
        for f in sorted((SKILL / "examples").rglob("*.page.json")):
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
            except ValueError:
                continue
            for t in all_strings([{"data": s.get("data", {})} for s in d.get("sections", [])]):
                w = set(re.findall(r"\w+", plain(t).lower()))
                if len(t) >= 45 and len(w) >= 7:
                    _EXAMPLE_TEXT.append((w, f.name, t))
    return _EXAMPLE_TEXT


NUM_RE = re.compile(r"\d[\d,.:]*\d|\d")
NUM_SKIP_KEYS = {"href", "src", "image", "icon", "flag", "city", "sizes", "label_min", "decimals", "min", "max", "start", "display"}


def page_numbers(o, path, out, key=""):
    """(path, number) for every number in visible copy and stat values."""
    if isinstance(o, dict):
        for k, v in o.items():
            if k not in NUM_SKIP_KEYS and not k.startswith("_"):
                page_numbers(v, "%s.%s" % (path, k), out, k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            page_numbers(v, "%s[%d]" % (path, i), out, key)
    elif isinstance(o, bool):
        return
    elif isinstance(o, (int, float)):
        out.append((path, ("%g" % o)))
    elif isinstance(o, str) and not o.startswith(("mailto:", "tel:", "http")):
        for m in NUM_RE.findall(o):
            out.append((path, m))


def norm_num(n):
    n = n.replace(",", "")
    if ":" not in n and "." in n and n.replace(".", "").isdigit() and len(n.split(".")[-1]) == 3:
        n = n.replace(".", "")  # 1.200 written Vietnamese style
    return n.rstrip(".")


def check_numbers(ctx, sections, brief):
    """Every figure must come from the brief. Figures that also appear in the examples are sample data."""
    allowed = {norm_num(n) for n in NUM_RE.findall(brief)}
    for part in re.findall(r"\d+\s*-\s*\d+", brief):
        allowed.update(x.strip() for x in part.split("-"))
    # Years in business follow from a founding year; the current and last year may date the figures.
    this_year = datetime.date.today().year
    allowed.update({str(this_year), str(this_year - 1)})
    for y in re.findall(r"\b(?:19|20)\d\d\b", brief):
        if int(y) < this_year:
            allowed.update({str(this_year - int(y)), str(this_year - 1 - int(y))})
    example_nums = set()
    for _, _, et in _example_sentences():
        example_nums.update(norm_num(n) for n in NUM_RE.findall(et))
    for f in sorted((SKILL / "examples").rglob("*.page.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        found = []
        page_numbers([s.get("data", {}) for s in d.get("sections", [])], "", found)
        example_nums.update(norm_num(n) for _, n in found)
    unknown = []
    for s in sections:
        found = []
        page_numbers(s["data"], s["path"] + ".data", found)
        for path, n in found:
            v = norm_num(n)
            if v in allowed or len(v.replace(".", "")) < 2 or re.fullmatch(r"(19|20)\d\d", v) and v in brief:
                continue
            if v in ("24", "7") and "24/7" in brief:
                continue
            if ".form." in path:
                continue  # team-size choices in a form are options, not claims
            if v in example_nums:
                ctx.err(path, "the figure %s is not in the brief but appears in the example pages, where it is sample data. Use the client's figure, write \"[KPI]\", or remove it." % n)
            else:
                ctx.err(path, "the figure %s is not in the brief. Every number on the page (stats, salaries, prices, counts) must be the client's own; write \"[KPI]\" where the section allows placeholders, or remove it." % n)


def check_copied(ctx, sections, brief=""):
    """Fail when a sentence is (almost) the same as one in an example page.

    The examples describe fictional companies. Their numbers, time frames, guarantees and contract
    terms are sample data; kept on a client page they become invented facts, and repeated example
    wording is what makes generated pages look alike.
    """
    ex = _example_sentences()
    for s in sections:
        def walk(o, path):
            if isinstance(o, dict):
                for k, v in o.items():
                    if k not in ("href", "src", "image", "icon", "flag", "city", "alt") and not k.endswith("_plain"):
                        walk(v, "%s.%s" % (path, k))
            elif isinstance(o, list):
                for i, v in enumerate(o):
                    walk(v, "%s[%d]" % (path, i))
            elif isinstance(o, str) and len(o) >= 45:
                w = set(re.findall(r"\w+", plain(o).lower()))
                if len(w) < 7:
                    return
                terms = number_terms(o) - number_terms(brief)
                for ew, fname, et in ex:
                    j = len(w & ew) / len(w | ew)
                    if j >= 0.6:
                        ctx.err(path, "this sentence is copied from examples/%s (\"%s\"). Example facts, times and terms are made up for a fictional company. Rewrite it from the client's brief, or drop it if the brief does not cover it." % (fname, et[:70]))
                        return
                    shared = terms & number_terms(et)
                    if shared and j >= 0.2:
                        ctx.err(path, "'%s' comes from examples/%s, where it is sample data for a fictional company. Keep a number, time frame or contract term only if the client's brief states it; otherwise write the sentence without it." % ("', '".join(sorted(shared)), fname))
                        return
        walk(s["data"], s["path"] + ".data")


# Library photos that show the same person; one page must not use two of them.
SAME_PERSON = [{"portrait-man-desk", "portrait-man-desk-wood"}]



# --------------------------------------------------------------------------- facts the brief must contain
# Proof blocks name real people and companies: each name, company and quote must appear in the brief.
PROOF_FIELDS = {
    "logo-marquee": ("logos", ("name",)),
    "logo-wall": ("logos", ("name",)),
    "testimonials": ("items", ("name", "company", "quote")),
    "testimonials-drift": ("items", ("name", "company", "quote")),
    "testimonials-rated": ("items", ("name", "company", "quote")),
    "quote-spotlight": ("quotes", ("name", "company", "quote")),
    "case-slider": ("cases", ("client",)),
    "case-filter": ("cases", ("client",)),
    "proof-book": ("cases", ("client",)),
    "team-coverflow": ("members", ("name",)),
}
# Claims a weak model tends to add from habit: certifications, regulations, tools, guarantees, languages, recordings.
CLAIM_RE = re.compile(
    r"\b(ISO\s?\d{4,5}|SOC\s?[12]|PCI(?:[\s-]DSS)?|HIPAA|GDPR|CCPA|CMMI|COPC|ISAE\s?\d+|SSAE\s?\d+|FedRAMP|"
    r"Zendesk|Gorgias|Intercom|Freshdesk|Salesforce|HubSpot|ServiceNow|Kustomer|Five9|Genesys|Talkdesk|Aircall|Twilio|"
    r"QuickBooks|Xero|NetSuite|Workday|Jira|Slack|Microsoft Teams|"
    r"Clutch|Gartner|Forrester|Everest Group|Great Place to Work|award[- ]winning|"
    r"guarantee[ds]?|money[- ]back|no extra cost|at no cost|free of charge|free trial|risk[- ]free|replacement|backup bench|"
    r"call recordings?|recorded calls|24/7|"
    r"setup fees?|hidden (?:fees?|charges?|costs?)|per (?:agent|seat|hour|FTE)|fixed monthly (?:fee|price)|"
    r"never share|background[- ]check(?:s|ed)?|encrypt(?:ed|ion)?|time ?zones?|"
    r"WhatsApp|Messenger|Instagram|Viber|VDI|virtual desktops?|"
    r"month[- ]to[- ]month|lock[- ]in|long[- ]term contracts?|cancel any ?time|notice period|no minimum|minimum term|"
    r"English|Spanish|Tagalog|Japanese|Vietnamese|French|German|Mandarin|Cantonese|Korean|Portuguese|Italian|Arabic|Thai|Bahasa)\b",
    re.I)

# Tech stacks and platforms. Case-sensitive, so the verb "react" or the adjective "swift" never match.
TECH_RE = re.compile(
    r"\b(React(?: Native)?|Vue(?:\.js)?|Angular|Next\.js|Node(?:\.js)?|Python|Java|JavaScript|TypeScript|PHP|Laravel|"
    r"Django|Ruby on Rails|Flutter|Swift|Kotlin|iOS|Android|AWS|Azure|Google Cloud|GCP|Kubernetes|Docker|"
    r"Selenium|Cypress|Playwright|Appium|JMeter|Postman|Shopify|Magento|WordPress|SAP|Oracle|Sage|MYOB|Gusto|ADP|Dext|Hubdoc)\b")

TIER_RE = re.compile(r"\b(?:tier|level|step|phase|stage|grade)\s+\d+", re.I)


# A quoted passage in the brief ('...' or "...") is a client's words about one project, not a promise to every client.
QUOTED_RE = re.compile(r"(?:(?<=\s)|(?<=:)|^)['\"\u201c\u2018]([^'\"\u201d\u2019]{15,}?)['\"\u201d\u2019](?=[\s.,;:]|$)")


# Industry and audience lists: each name must come from the brief. Generic nouns are ignored, so "Accounting firms"
# passes when the brief says "accounting firms" or "accounting practices", while "E-commerce and retail" does not.
AUDIENCE_FIELDS = {"industries-rows": "items", "industries-slats": "tiles", "industries-tiles": "tiles", "audience-cards": "cards"}
AUDIENCE_GENERIC = set("""and the for with of to our your from who that need needs sized size small mid large growing
companies company firms firm businesses business teams team industry industries sector sectors services service
clients client providers provider organisations organizations organisation organization brands brand enterprises
enterprise groups group practices practice operators operator vendors vendor startups startup scaleups""".split())


def check_audience(ctx, sections, nb):
    for s in sections:
        key = AUDIENCE_FIELDS.get(s["type"])
        if not key:
            continue
        for i, item in enumerate(s["data"].get(key) or []):
            title = item.get("title")
            if not isinstance(title, str):
                continue
            words = [w for w in norm_text(title).split() if len(w) > 2 and w not in AUDIENCE_GENERIC]
            missing = [w for w in words if (" " + w[:5]) not in nb]
            if missing:
                ctx.err("%s.data.%s[%d].title" % (s["path"], key, i), "\"%s\": the brief does not name this industry or audience (%s). List only the client groups the brief gives, even if that leaves 2; never pad the list. With fewer items than this variant needs, use audience-cards or industries-tiles." % (title, ", ".join(missing)))


def norm_text(s):
    return re.sub(r"\s+", " ", re.sub(r"[^0-9a-z]+", " ", s.lower())).strip()


def check_evidence(ctx, sections, brief):
    """Rule 2 of SKILL.md as a check: proof names and quotes, certifications, tools, guarantees, languages
    and time promises on the page must all come from the brief."""
    nb = " " + norm_text(brief) + " "
    for s in sections:
        spec = PROOF_FIELDS.get(s["type"])
        if not spec:
            continue
        key, fields = spec
        for i, item in enumerate(s["data"].get(key) or []):
            for f in fields:
                v = item.get(f)
                if not isinstance(v, str):
                    continue
                path = "%s.data.%s[%d].%s" % (s["path"], key, i, f)
                if "[" in v and "]" in v:
                    ctx.err(path, "placeholder in a proof item. Clients, people, companies and quotes are never placeholders: drop the item, and drop the section if too few real items are left.")
                elif (" " + norm_text(v) + " ") not in nb:
                    what = "quote" if f == "quote" else "name"
                    ctx.err(path, "this %s is not in the brief (\"%s\"). Proof must be real: use only clients, people and quotes the client supplied, word for word. Never add, shorten or reword a quote; drop the item or the section instead." % (what, v[:60]))
    check_audience(ctx, sections, nb)
    for s in sections:
        for path, url in _form_actions(s["data"], s["path"] + ".data"):
            if url.startswith(("http://", "https://")) and url.split("#")[0].rstrip("/") not in brief:
                ctx.err(path, "the form posts to %s, which the brief does not give, so every enquiry would fail. Leave \"action\" out: the form then shows its thank-you message until the client supplies their own form endpoint." % url)
    # Figures inside quoted passages may appear only inside that quote on the page (checked word for word above).
    allowed_terms = number_terms(QUOTED_RE.sub(" ", brief))
    this_year = datetime.date.today().year
    for y in re.findall(r"\b(?:19|20)\d\d\b", brief):
        if int(y) < this_year:
            allowed_terms.update({"%d year" % (this_year - int(y)), "%d year" % (this_year - 1 - int(y))})
    seen = set()
    for s in sections:
        for path, text in _strings_with_paths(s["data"], s["path"] + ".data"):
            if s["type"] in PROOF_FIELDS and path.endswith(".quote"):
                continue
            for m in list(CLAIM_RE.finditer(text)) + list(TECH_RE.finditer(text)):
                term = m.group(1)
                t = norm_text(term)
                # "No call recordings", "without GDPR": the brief rules the claim out.
                neg = r"(?:^| )(?:no|not|without|never|don t have|do not have)(?: [a-z0-9]+){0,2} " + re.escape(t) + r"(?: |$)"
                if re.search(neg, nb):
                    if re.search(neg, norm_text(text)):
                        continue  # the page repeats the brief's "no setup fee"
                    key = (path, "not:" + t)
                    if key not in seen:
                        seen.add(key)
                        ctx.err(path, "\"%s\": the brief says the client does not have this. Remove it." % term)
                    continue
                if t in nb or t[:6] in nb and len(t) > 6:
                    continue
                if (path, t) in seen:
                    continue
                seen.add((path, t))
                ctx.err(path, "\"%s\" is a claim the brief does not make (certification, tool, tech stack, guarantee, contract term, language, recording or hours). Remove it or reword without it; only the client's brief can add it." % term)
            if ".form." in path:
                continue  # team-size choices in a form are options, not claims
            # "tier 2 agents", "step 3" name a level, not a quantity
            plain_text = TIER_RE.sub("", text)
            for term in number_terms(plain_text) - allowed_terms:
                if (path, term) in seen:
                    continue
                seen.add((path, term))
                ctx.err(path, "\"%s\" is a time, size or duration the brief does not give. Remove it, or write the sentence without the number." % term)


def _form_actions(o, path):
    if isinstance(o, dict):
        for k, v in o.items():
            p = "%s.%s" % (path, k)
            if k == "action" and isinstance(v, str):
                yield p, v.strip()
            else:
                yield from _form_actions(v, p)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from _form_actions(v, "%s[%d]" % (path, i))


def _strings_with_paths(o, path):
    if isinstance(o, dict):
        for k, v in o.items():
            if k not in ("href", "src", "image", "icon", "flag", "city", "avatar", "logo", "photo", "action"):
                yield from _strings_with_paths(v, "%s.%s" % (path, k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from _strings_with_paths(v, "%s[%d]" % (path, i))
    elif isinstance(o, str):
        yield path, o


# How elements arrive on scroll (base.js, base.css). Measured on 92 real BPO homepages: see references/motion-research.md.
# The share is how often build.py picks the style for a page that does not set theme.motion_style.
MOTION_STYLES = {"rise": 0.35, "slide": 0.25, "fade": 0.25, "mask": 0.15}


def motion_style(theme, preset, seed):
    style = theme.get("motion_style") or preset.get("design", {}).get("motion_style")
    if style:
        return style
    x, acc = float(seed["e"]), 0.0
    for name, share in MOTION_STYLES.items():
        acc += share
        if x < acc:
            return name
    return "rise"


def brand_seed(text, count=8):
    """Same FNV-1a + mulberry32 generator as scene3d.js and stage3d.js, so CSS-only 3D variants get the brand's
    numbers at build time (templates read {{site.seed.a}} ... {{site.seed.h}}, each 0-1, and {{site.seed.sign}}, 1 or -1)."""
    h = 2166136261
    for ch in text or "":
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF

    def imul(a, b):
        return (a * b) & 0xFFFFFFFF
    out = {}
    for key in "abcdefgh"[:count]:
        h = (h + 0x6D2B79F5) & 0xFFFFFFFF
        t = h
        t = imul(t ^ (t >> 15), t | 1)
        t ^= (t + imul(t ^ (t >> 7), t | 61)) & 0xFFFFFFFF
        out[key] = "%.3f" % (((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296)
    out["sign"] = "1" if float(out["a"]) >= 0.5 else "-1"
    return out


def check_images(ctx, sections):
    used = set()

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, str):
            used.add(o)
            used.add(o.replace("\\", "/").rsplit("/", 1)[-1].rsplit(".", 1)[0])
    for sec in sections:
        walk(sec["data"])
    for group in SAME_PERSON:
        both = sorted(group & used)
        if len(both) > 1:
            ctx.warn("sections", "%s show the same person; readers will notice. Keep one." % " and ".join(both))


def _library_photos(o, path, keys, out):
    """(path, key, alt) for each library photo in the raw page data."""
    if isinstance(o, dict):
        src = o.get("src")
        if isinstance(src, str) and src in keys:
            out.append((path, src, o.get("alt") if isinstance(o.get("alt"), str) else ""))
        for k, v in o.items():
            if k in ("src", "alt"):
                continue
            p = "%s.%s" % (path, k)
            if isinstance(v, str) and v in keys:
                out.append((p, v, ""))
            else:
                _library_photos(v, p, keys, out)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            _library_photos(v, "%s[%d]" % (path, i), keys, out)
    return out


def check_stock_photos(ctx, raw_sections, brand):
    """A weak model reaches the photo share by repeating the same pictures, and captions stock photos as the
    client's team or office. Library photos appear once per page and their alt text says what the picture shows."""
    found = []
    for i, sec in enumerate(raw_sections if isinstance(raw_sections, list) else []):
        if isinstance(sec, dict):
            _library_photos(sec.get("data"), "sections[%d].data" % i, ctx.lib["images"], found)
    nbrand = norm_text(brand or "")
    names = {nbrand} if nbrand else set()
    if nbrand and len(nbrand.split()[0]) >= 4:
        names.add(nbrand.split()[0])
    first = {}
    for path, key, alt in found:
        if path.endswith(".avatar"):
            ctx.err(path, "%r is a stock face. Next to a real client's name and quote it makes the review look fake. Leave \"avatar\" out (the initials show instead) or use a photo file the client supplied." % key)
            continue
        if key in first:
            ctx.err(path, "photo %r is already used at %s. Each library photo appears once on a page: pick another key from references/assets.md, use the client's own photos, or drop this one." % (key, first[key]))
        else:
            first[key] = path
        na = " " + norm_text(alt) + " "
        if any(" %s " % n in na for n in names) or re.search(r" (?:our|we|us) ", na):
            ctx.err(path + ".alt", "\"%s\": %r is a stock photo, not a picture of %s or its people. Describe what the picture shows (\"Two people checking invoices at a desk\") without the company's name or \"our\". Only the client's own photo files may name them." % (alt, key, brand or "the client"))


PEOPLE_SECTIONS = {"team-grid", "team-coverflow", "quote-spotlight", "testimonials", "testimonials-drift", "testimonials-rated"}


def check_named_faces(ctx, raw_sections):
    """Team and review sections put a photo next to a person's name: a library portrait there is a stranger
    presented as that person."""
    for i, sec in enumerate(raw_sections if isinstance(raw_sections, list) else []):
        if not isinstance(sec, dict) or sec.get("type") not in PEOPLE_SECTIONS:
            continue
        data = sec.get("data")
        for k, items in (data or {}).items():
            for j, it in enumerate(items if isinstance(items, list) else []):
                if not (isinstance(it, dict) and isinstance(it.get("name"), str)):
                    continue
                for f in ("photo", "image"):
                    v = it.get(f)
                    key = v.get("src") if isinstance(v, dict) else v
                    if isinstance(key, str) and key in ctx.lib["images"]:
                        ctx.err("sections[%d].data.%s[%d].%s" % (i, k, j, f), "%r is a stock portrait shown as %s. People on the page need their own photo: use a file the client supplied, or choose a variant without portraits (team-grid and team-coverflow need photos, so drop the section)." % (key, it["name"]))


def check_legal(ctx, sections, brand):
    for s in sections:
        legal = s["data"].get("legal") if s["type"] in ("footer-columns", "footer-matrix") else None
        if isinstance(legal, str) and (re.match(r"\s*(?:\u00a9|\(c\)|copyright)", legal, re.I)):
            ctx.err(s["path"] + ".data.legal", "the footer already prints \"\u00a9 <year> %s.\" before this text. Write only what follows, for example \"All rights reserved.\"" % (brand or "<brand>"))


# Design tells of generated pages (docs/research/ui-anti-slop.md in the job repo, references/anti-slop.md).
DEFAULT_HEADING_FONTS = {"inter", "roboto", "arial", "helvetica", "open sans", "lato", "system-ui", "space grotesk"}
EYEBROW_STOP = set("""the and for with our your you we of in on to a an at by from how what why who is are
services service team teams""".split())
TIMER_VARIANTS = {"hero-cycler-centered": "the rotating headline phrases", "hero-deck": "every role card but the front one"}
PINNED_VARIANTS = {"services-stack", "process-sticky", "process-layers"}


def _eyebrow(d):
    e = d.get("eyebrow")
    if not isinstance(e, str):
        e = (d.get("head") or {}).get("eyebrow") if isinstance(d.get("head"), dict) else None
    return e if isinstance(e, str) and e.strip() else None


def _hero_copy(d):
    """Title and lead of a hero; hero-slides keeps them on its first slide."""
    slides = d.get("slides") if isinstance(d.get("slides"), list) else []
    first = slides[0] if slides and isinstance(slides[0], dict) else {}
    title = d.get("title") if isinstance(d.get("title"), str) else first.get("title")
    lead = d.get("lead") if isinstance(d.get("lead"), str) else first.get("lead")
    return (title if isinstance(title, str) else None, lead if isinstance(lead, str) else "")


def _title(d):
    t = d.get("title")
    if not isinstance(t, str) and isinstance(d.get("head"), dict):
        t = d["head"].get("title")
    return t if isinstance(t, str) else None


PHOTO_KEYS = ("photo", "image", "photos", "images", "poster", "video")
PHOTO_SHARE = 0.4  # real BPO homepages: median 33%, p75 44% of sections carry a photo (92 blueprints)
PHOTO_MIN_SECTIONS = 6  # short demo pages are left alone


def _has_photo(o):
    if isinstance(o, dict):
        return any((k in PHOTO_KEYS and v) or _has_photo(v) for k, v in o.items())
    if isinstance(o, list):
        return any(_has_photo(x) for x in o)
    return False


def _photo_fields(fields, prefix=""):
    """Paths of the optional photo fields a variant schema offers, such as "image" or "steps[].photo"."""
    out = []
    for k, f in (fields or {}).items():
        if not isinstance(f, dict):
            continue
        if f.get("type") in ("image", "video") or f.get("$ref") == "photo" or k in ("photo", "image"):
            out.append(prefix + k)
        elif f.get("type") == "object":
            out += _photo_fields(f.get("fields"), prefix + k + ".")
        elif f.get("type") == "list" and isinstance(f.get("item"), dict):
            it = f["item"]
            if it.get("type") == "image" or it.get("$ref") == "photo":
                out.append(prefix + k + "[]")
            elif it.get("type") == "object":
                out += _photo_fields(it.get("fields"), prefix + k + "[].")
    return [x for x in out if not x.endswith(("avatar", "logo", "src"))]


def check_photos(ctx, sections, override=None):
    """A page built only from text blocks and icon cards reads as generated. Real BPO homepages show people, offices
    and the work: at least PHOTO_SHARE of the content sections carry a photo.
    override (page "override_photos"): the client chose sections without photos; the shortfall prints as a warning."""
    body = [s for s in sections if s["variant"].get("group") not in ("header", "footer", "floating", "exit", None)]
    if len(body) < PHOTO_MIN_SECTIONS:
        return
    with_photo = [s for s in body if _has_photo(s["data"])]
    need = -(-int(PHOTO_SHARE * 100) * len(body) // 100)
    if len(with_photo) >= need:
        return
    tips = []
    for s in body:
        if s in with_photo:
            continue
        fields = _photo_fields(s["variant"].get("fields"))
        if fields:
            tips.append("%s (%s): add %s" % (s["path"], s["type"], " or ".join(fields)))
    report = ctx.warn if override else ctx.err
    if override:
        ctx.warn("page.override_photos", "fewer photos than real BPO homepages show, on purpose: %s" % override["reason"])
        return
    report("sections", "%d of %d content sections carry a photo; a page this long needs at least %d. Real BPO homepages show the team, the offices and the work (median 33%%, top quarter 44%% of sections). %s. Client photos first, then library photos from references/assets.md that fit the section (never a photo of a different industry)."
            % (len(with_photo), len(body), need, ("Sections that take a photo: " + "; ".join(tips)) if tips else "Swap a text-only section for a photo variant (feature-rows, image-cards, services-tabs, banner-image, case-slider)"))


def check_design(ctx, sections, site, preset, theme, photos_override=None):
    heads, accented, icon_sections = [], [], []
    for s in sections:
        d = s["data"] if isinstance(s["data"], dict) else {}
        g = s["variant"].get("group")
        title = _title(d)
        if g == "hero":
            title_h, lead = _hero_copy(d)
            text = plain(lead or title_h or title or "")
            if site.get("brand") and site["brand"].lower() not in text.lower():
                ctx.err(s["path"] + ".data.lead", "the hero lead does not name the company. Start it with \"%s\" so the first screen could not belong to another brand (references/anti-slop.md)." % site["brand"])
            if s["type"] in TIMER_VARIANTS:
                ctx.warn(s["path"], "%s advances on a timer, so %s is hidden most of the time. Put anything a buyer must read in the lead as well." % (s["type"], TIMER_VARIANTS[s["type"]]))
            continue
        if g in ("header", "footer", "floating", "exit", None) or not title:
            continue
        brow = _eyebrow(d)
        heads.append((s["path"], brow))
        if "*" in title:
            accented.append(s["path"])
        if brow:
            tw = {w for w in norm_text(plain(title)).split() if len(w) > 2 and w not in EYEBROW_STOP}
            same = [w for w in norm_text(brow).split() if w in tw]
            if same:
                ctx.err(s["path"] + ".data.head.eyebrow", "the label \"%s\" repeats \"%s\" from its title. A label above a title must add something the title does not say (a region, a service line, a date), or be left out." % (brow, same[0]))
        for v in d.values():
            if isinstance(v, list) and len(v) >= 3 and all(isinstance(x, dict) and x.get("icon") for x in v):
                icon_sections.append(s["path"])
                break
    with_brow = [p for p, b in heads if b]
    allowed = max(1, len(heads) // 3)
    if len(with_brow) > allowed:
        ctx.err("sections", "%d of %d section titles have a label (eyebrow) above them; at most %d may. A label above every heading is the most common tell of a generated page. Keep a label only where it adds something the title does not say (a region, a year, a service line) and delete the rest: %s." % (len(with_brow), len(heads), allowed, ", ".join(with_brow)))
    if len(accented) > 1:
        ctx.warn("sections", "%d section titles below the hero have *accent* words (%s). Accent the hero title only; one coloured word in every heading reads as generated." % (len(accented), ", ".join(accented[:4])))
    if len(icon_sections) > 2:
        ctx.err("sections", "%d sections put an icon on every item (%s). Rows of icon cards make a page read as text and templates; keep icons in at most two sections and give the others photos (see the photo rule below) or plain lists." % (len(icon_sections), ", ".join(icon_sections)))
    check_photos(ctx, sections, photos_override)
    pinned = [s["path"] for s in sections if s["type"] in PINNED_VARIANTS]
    if len(pinned) > 1:
        ctx.warn("sections", "%d pinned scroll sections (%s). Scrolling that holds the page still is tiring after the first one; keep one." % (len(pinned), ", ".join(pinned)))

    fonts = preset.get("fonts", {})
    if not theme.get("fonts") and str(fonts.get("heading", "")).lower() in DEFAULT_HEADING_FONTS:
        ctx.warn("preset.fonts.heading", "headings use %s, a default family of generated pages. Pick a preset with its own heading face, unless it is the client's brand font." % fonts["heading"])
    # default colour looks, only when the colours come from the preset
    if not theme.get("accent"):
        colors = preset.get("colors", {})
        acc = colors.get("accent")
        tones = preset.get("tones", {})
        light_bg = (tones.get("light") or {}).get("bg", "#ffffff")
        if acc:
            L, C, H = to_oklch(parse_hex(acc) or (0, 0, 0))
            if preset.get("hero_tone", "light") == "light" and 270 <= H <= 320 and C > 0.12:
                ctx.warn("preset.colors.accent", "violet accent on a light page, the default look of generated sites. Use the client's colour in theme.accent or another preset.")
            try:
                Lb, Cb, Hb = to_oklch(parse_hex(light_bg))
                Lc, Cc, Hc = to_oklch(parse_hex("#f4f1ea"))
                cream = abs(Lb - Lc) < 0.03 and abs(Cb - Cc) < 0.02
            except Exception:
                cream = False
            if cream and 25 <= H <= 50:
                ctx.warn("preset.colors", "cream background with a terracotta accent, a look generated pages converge on. Use the client's colours in theme.")


# Default palette colours of CSS frameworks. A model that has no brand colour reaches for these, and they are what
# makes a page look generated (a Bootstrap "danger" red accent on navy). Allowed only when the brief or logo has them.
FRAMEWORK_COLORS = {
    "#d9534f": "Bootstrap 3 danger red", "#dc3545": "Bootstrap danger red", "#337ab7": "Bootstrap 3 primary blue",
    "#007bff": "Bootstrap 4 primary blue", "#0d6efd": "Bootstrap 5 primary blue", "#28a745": "Bootstrap success green",
    "#198754": "Bootstrap 5 success green", "#5cb85c": "Bootstrap 3 success green", "#f0ad4e": "Bootstrap 3 warning orange",
    "#ffc107": "Bootstrap warning yellow", "#17a2b8": "Bootstrap info teal", "#0dcaf0": "Bootstrap 5 info cyan",
    "#5bc0de": "Bootstrap 3 info blue", "#6f42c1": "Bootstrap purple", "#e83e8c": "Bootstrap pink",
    "#fd7e14": "Bootstrap orange", "#20c997": "Bootstrap teal", "#6610f2": "Bootstrap indigo",
    "#ef4444": "Tailwind red-500", "#dc2626": "Tailwind red-600", "#f97316": "Tailwind orange-500", "#ea580c": "Tailwind orange-600",
    "#f59e0b": "Tailwind amber-500", "#d97706": "Tailwind amber-600", "#22c55e": "Tailwind green-500", "#16a34a": "Tailwind green-600",
    "#10b981": "Tailwind emerald-500", "#059669": "Tailwind emerald-600", "#14b8a6": "Tailwind teal-500", "#0d9488": "Tailwind teal-600",
    "#06b6d4": "Tailwind cyan-500", "#0891b2": "Tailwind cyan-600", "#0ea5e9": "Tailwind sky-500", "#0284c7": "Tailwind sky-600",
    "#3b82f6": "Tailwind blue-500", "#2563eb": "Tailwind blue-600", "#6366f1": "Tailwind indigo-500", "#4f46e5": "Tailwind indigo-600",
    "#8b5cf6": "Tailwind violet-500", "#7c3aed": "Tailwind violet-600", "#a855f7": "Tailwind purple-500", "#9333ea": "Tailwind purple-600",
    "#ec4899": "Tailwind pink-500", "#db2777": "Tailwind pink-600",
}
LOGO_HUE_TOLERANCE = 25  # degrees of OKLCH hue between theme.accent and the nearest logo colour


def check_brand_colors(ctx, top, page_dir, brief, raw_site):
    """theme.accent is the logo colour. With a logo file: fail when the accent (given or from the preset) is not one of
    the logo's hues. Always: fail on a framework default colour the brief and logo do not have."""
    import logo_colors
    theme = top.get("theme") or {}
    logo = raw_site.get("logo") if isinstance(raw_site, dict) else None  # as written, before it is copied to assets
    hues = None
    if logo and not re.match(r"^https?://", logo):
        hues = logo_colors.logo_hues(page_dir / logo, to_oklch)
        if hues is None:
            ctx.warn("site.logo", "could not read the colours of %s (use PNG or SVG, or install Pillow), so theme.accent was not checked against it." % logo)
    listed = ", ".join("%s (%d%%)" % (h, round(s * 100)) for h, _, s in (hues or [])[:3])

    def from_logo(hex_):
        if not hues:
            return False
        L, C, H = to_oklch(parse_hex(hex_))
        return C >= 0.04 and any(hue_distance(H, hh) <= LOGO_HUE_TOLERANCE for _, hh, _ in hues)

    brief_up = (brief or "").lower()
    for key in ("accent", "accent_2", "primary"):
        val = theme.get(key)
        if not val:
            continue
        name = FRAMEWORK_COLORS.get(val.lower())
        if name and val.lower() not in brief_up and not from_logo(val):
            ctx.err("page.theme." + key, "%s is the %s default, not a brand colour. Use the client's colour: the logo's main hue in theme.accent%s, or leave the field out when the client gave none." % (val, name, " (%s)" % listed if listed else ""))
    if hues:
        acc = theme.get("accent")
        if not acc:
            ctx.err("page.theme.accent", "the logo is coloured (%s) but theme.accent is not set, so the page uses the preset's accent. Put the logo's main colour, %s, in theme.accent." % (listed, hues[0][0]))
        elif not from_logo(acc):
            ctx.err("page.theme.accent", "theme.accent %s is not a colour of the logo (%s). The accent is the logo colour; build.py derives the button and highlight shades from it. Use %s." % (acc, listed, hues[0][0]))
    elif theme.get("accent") and hues is None and not logo and theme["accent"].lower() not in brief_up:
        ctx.warn("page.theme.accent", "theme.accent %s is not in the brief and the page has no logo to check it against. If the client gave no colour, leave theme.accent out and let the preset choose." % theme["accent"])


# Families on Google Fonts that ship a Vietnamese subset (checked 2026-09-30 against the css2 API). A preset whose
# fonts are not all here must carry "fonts_vi", which build.py uses for "lang": "vi".
# Smallest heading line-height (bold, mixed case) before Vietnamese stacked marks (ẫ, ệ, ữ) touch the descenders
# of the line above: (height of "ẫ" + depth of "g") / font size + 0,05, measured in Edge on 2026-10-07. Display
# headings at 1,06-1,12 collided in Plus Jakarta Sans and Bricolage Grotesque. base.css applies it on lang="vi" pages.
VI_HEAD_LH = {"Archivo": 1.2, "Barlow": 1.15, "Be Vietnam Pro": 1.25, "Bricolage Grotesque": 1.4, "Encode Sans": 1.25,
              "Epilogue": 1.2, "IBM Plex Sans": 1.2, "Inter": 1.25, "Josefin Sans": 1.15, "Lexend": 1.25, "Libre Franklin": 1.2,
              "Lora": 1.25, "Manrope": 1.25, "Montserrat": 1.15, "Mulish": 1.15, "Noto Serif": 1.25, "Nunito Sans": 1.15,
              "Onest": 1.35, "Plus Jakarta Sans": 1.3, "Public Sans": 1.15, "Raleway": 1.15, "Roboto": 1.2,
              "Source Sans 3": 1.15, "Source Serif 4": 1.15, "Space Grotesk": 1.2, "Work Sans": 1.25}
VI_FONTS = {"Archivo", "Barlow", "Be Vietnam Pro", "Bricolage Grotesque", "Encode Sans", "Epilogue", "IBM Plex Sans", "Inter",
            "JetBrains Mono", "Josefin Sans", "Lexend", "Libre Franklin", "Lora", "Manrope", "Montserrat", "Mulish",
            "Noto Serif", "Nunito Sans", "Onest", "Plus Jakarta Sans", "Public Sans", "Raleway", "Roboto",
            "Source Sans 3", "Source Serif 4", "Space Grotesk", "Work Sans"}
# every Vietnamese heading font needs its measured line-height
assert VI_FONTS - {"JetBrains Mono"} <= set(VI_HEAD_LH), sorted(VI_FONTS - {"JetBrains Mono"} - set(VI_HEAD_LH))


def check_voice(ctx, sections, lang, bp=None):
    """Page-level voice checks measured against 113 real BPO homepages (references/industry-voice.md).

    Real sites: hero titles have a median of 5 words and 15% address the reader; 12% of section headings
    say you/your and 35% are short labels such as "How we help" or "Industries we serve".
    """
    you = YOU_RE.get(lang)
    heads = []
    body = []
    for s in sections:
        d = s["data"] if isinstance(s["data"], dict) else {}
        g = s["variant"].get("group")
        title = d.get("title") if isinstance(d.get("title"), str) else (d.get("head") or {}).get("title")
        if g == "hero":
            title = _hero_copy(d)[0] or title
        if g == "hero" and title:
            t = plain(title)
            n = len(t.split())
            if lang == "en" and n > 10:
                ctx.warn(s["path"] + ".data.title", "hero title has %d words. Real BPO hero titles are 3-8 words (median 5): name what the company is or does, for example \"Customer support teams in Manila and Bogota\"." % n)
            if you and you.search(t) and re.search(r"\b(that|who)\b", t, re.I):
                ctx.warn(s["path"] + ".data.title", "hero title follows the '[people] who/that [verb] your [thing]' formula that AI copy overuses (half of AI-written heroes, 11% of real ones). Say what the company is: \"Offshore accounting teams for US CPA firms\".")
        elif g not in ("header", "footer", "floating", "exit", None) and title:
            heads.append((s["path"], plain(title)))
        for k in ("lead", "text"):
            v = d.get(k) or (d.get("head") or {}).get(k)
            if isinstance(v, str):
                body.append(v)
    if you and len(heads) >= 4:
        n_you = [p for p, t in heads if you.search(t)]
        share = len(n_you) / len(heads)
        msg = ("%d of %d section headings address the reader (%s). On real BPO sites about 1 in 8 do. Turn most of them into plain labels "
               "(\"Services\", \"Industries we serve\", \"How it works\", \"Why %s\") or statements about the company." % (len(n_you), len(heads), ", ".join(p for p in n_you[:4]), "<brand>"))
        if share > 0.4:
            ctx.err("sections", msg)
        elif share > 0.25:
            ctx.warn("sections", msg)
    if lang in ("en", "vi") and len(heads) >= 5:
        pron = r"\b(you|your|we|our)\b" if lang == "en" else r"\bbạn\b"
        limit = 4 if lang == "en" else 6
        labels = [t for p, t in heads if len(t.split()) <= limit and not re.search(pron, t, re.I)]
        if not labels:
            ctx.warn("sections", "no section heading is a short label. A third of real BPO headings are 1-4 word labels (\"Our services\", \"Case studies\", \"Awards and certifications\"); a page where every heading is a crafted sentence reads as AI-written.")
    types = {s["type"] for s in sections}
    # a blueprint without a metrics or awards slot (IRIS) cannot take one, so the warning would only nag
    bp_room = bp is None or any(x.get("role") in ("metrics", "awards") for x in bp.get("sections", []))
    if bp_room and not types & {"metrics-counter", "metrics-panel", "metrics-rings", "metrics-bars3d", "metrics-tiles", "compliance-badges"}:
        ctx.warn("sections", "the page has no metrics or certification section. 58% of real BPO homepages show big numbers (staff, clients, years) and many show certifications; if the brief has such figures, add metrics-counter or compliance-badges.")
    riders = sum(t.count(", with ") for t in all_strings(sections))
    if lang == "en" and riders > 3:
        ctx.warn("sections", "%d sentences hang an extra clause on with ', with ...'. Real BPO sites do this about once per 150 sentences; split them into two sentences." % riders)
    every = [m.group() for t in [t for _, t in heads] + body for m in EVERY_RE.finditer(t)]
    if len(every) > 2:
        ctx.warn("sections", "'every/each call, contact, agent...' appears %d times (%s). AI copy leans on it; keep one." % (len(every), ", ".join(dict.fromkeys(e.lower() for e in every))))
    check_repeats(ctx, sections, heads)


def check_repeats(ctx, sections, heads):
    """Repetition a client read as machine-written (Smart Outsourcing review, 2026-10-09): the hero slogan reused as a
    section heading, one phrase in three or four sentences, and six button labels for the same action."""
    key = lambda t: re.sub(r"[^\w ]+", "", re.sub(r"<[^>]+>", "", plain(t)).lower()).strip()
    hero = next((s for s in sections if s["variant"].get("group") == "hero" and isinstance(s["data"], dict)), None)
    hero_t = key(_hero_copy(hero["data"])[0] or "") if hero else ""
    for p, t in heads:
        if hero_t and key(t) == hero_t:
            ctx.warn(p, "the heading \"%s\" repeats the hero title. A slogan used twice reads as filler; give the section its own heading (\"Led by UK-qualified accountants\", \"About us\")." % t)
    # five-word runs shared by three or more sentences ("inside your systems, with your review steps")
    grams = {}
    def prose(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k not in ("alt", "href", "src", "image", "icon", "keys", "meta"):
                    yield from prose(v)
        elif isinstance(o, list):
            for v in o:
                yield from prose(v)
        elif isinstance(o, str):
            yield o
    # the build keeps a rendered copy next to some fields (a title with its highlight markup): each text once per section
    texts = [t for s in sections for t in {re.sub(r"<[^>]+>", "", plain(t)) for t in prose(s["data"])}]
    for t in texts:
        words = re.findall(r"[\w']+", t)
        if len(words) >= 8:
            # lower-case runs only: place and brand names ("Hanoi, Da Nang and Ho Chi Minh City") may recur
            for g in {" ".join(words[i:i + 5]) for i in range(len(words) - 4) if all(w.islower() for w in words[i:i + 5])}:
                grams[g] = grams.get(g, 0) + 1
    picked = []
    for g, n in sorted(grams.items(), key=lambda x: -x[1]):
        if n >= 3 and not any(len(set(g.split()) & set(o.split())) >= 3 for o, _ in picked):
            picked.append((g, n))
    if picked:
        ctx.warn("sections", "the same words recur in several sentences: %s. Repeated phrasing is what makes a page read as generated; keep each phrase once and say something specific in the other places." % "; ".join("\"%s...\" %d times" % (g, n) for g, n in picked[:3]))
    # one in-page target reached by many different buttons (cta fields outside lists; nav, card and plan links name
    # their item, and "view all" links stand in for pages the site does not have yet)
    targets = {}
    for s in sections:
        d = s["data"] if isinstance(s["data"], dict) else {}
        for o in [d, d.get("head") if isinstance(d.get("head"), dict) else {}]:
            for k, v in o.items():
                if (k in ("cta", "secondary") or k.endswith("_cta")) and isinstance(v, dict) and isinstance(v.get("label"), str) and str(v.get("href", "")).startswith("#") and len(v["href"]) > 1:
                    targets.setdefault(v["href"], set()).add(v["label"].strip().lower())
    for href, labels in sorted(targets.items()):
        if len(labels) >= 4:
            ctx.warn("sections", "%d different labels lead to %s (%s). Give one action one or two labels across the page, such as \"Get a quote\" for the main button." % (len(labels), href, ", ".join(sorted(labels))))


# Sections that draw each figure (ring arc, column height): a placeholder leaves an empty shape.
DRAWN_FIGURES = {"metrics-rings", "metrics-bars3d"}
PLACEHOLDER_RE = re.compile(r"\[[^\]]{1,24}\]")


# English words, plus the Vietnamese a brief uses when the client asks for a 3D or animation-led page
# ("hieu ung 3D", "nhieu hieu ung", "sinh dong", "chuyen dong manh")
# The footer wordmark (the brand name set edge to edge in huge type) is off unless the brief asks for it: users read it
# as a template flourish (SoGlobal review, 2026-09-30).
WORDMARK_RE = re.compile(r"wordmark|(large|big|giant|huge) (brand name|logo type)|brand name in (large|big|huge) (type|letters)|chữ thương hiệu (lớn|cỡ lớn)", re.I)
MATRIX_RE = re.compile(r"dot[- ]matrix|led (dots|panel|sign|display)|pixel (logo|monogram|display)|ma trận (chấm|điểm)|bảng (đèn )?led|chấm (led|sáng)", re.I)
EXPRESSIVE_RE = re.compile(r"\b(3d|webgl|immersive|expressive|animation[- ]led|(rich|heavy|bold|lots of) (animation|animations|motion|effects))\b|nhiều hiệu ứng|hiệu ứng mạnh|sinh động|chuyển động mạnh", re.I)


def is_expressive(s):
    """An expressive variant (3D object, WebGL scene, particles, folding paper) or a band with a WebGL "visual" backdrop."""
    return s["variant"].get("tier") == "expressive" or bool((s["data"] or {}).get("visual"))


def check_figures(ctx, sections):
    """Rings draw percentages; a figure shown twice in two metric sections is padding."""
    seen = {}
    for s in sections:
        if s["variant"].get("group") != "metrics":
            continue
        items = s["data"].get("items") or []
        for i, it in enumerate(items):
            if not isinstance(it, dict):
                continue
            v = it.get("value")
            num = (v.get("count") if v.get("count") is not None else v.get("number")) if isinstance(v, dict) else v
            if s["type"] == "metrics-rings":
                try:
                    over = float(str(num).replace(",", "")) > 100
                except ValueError:
                    over = False
                if it.get("suffix", "%") != "%" or over:
                    ctx.err("%s.data.items[%d]" % (s["path"], i), "metrics-rings draws each figure as a share of a full ring, so it takes percentages only. Put counts (agents, years, clients) in metrics-counter or the hero stats.")
        figs = {(it["value"].get("display") if isinstance(it.get("value"), dict) else str(it.get("value"))) for it in items if isinstance(it, dict)}
        for other, ofigs in seen.items():
            same = figs & ofigs
            if len(same) >= 2:
                ctx.err(s["path"], "repeats %d figures already shown in %s. Show each figure once; drop this section if it has nothing new." % (len(same), other))
        seen[s["path"]] = figs


def check_motion(ctx, sections, archetype, lib, motion, brief=""):
    """BPO buyers judge trust first, so pages are calm by default: photos, reveals, counters, carousels, maps and at
    most one contextual piece in the hero. Expressive variants (3D objects, WebGL scenes, particles, folding paper) and
    band "visual" backdrops need "motion": "expressive", which is allowed only when the brief asks for a 3D or
    animation-led page."""
    for s in sections:
        if s["type"] not in DRAWN_FIGURES:
            continue
        data = {k: v for k, v in s["data"].items() if k != "head"}
        holes = [p for p, t in _strings_with_paths(data, s["path"] + ".data") if PLACEHOLDER_RE.search(t)]
        if holes:
            ctx.err(holes[0], "%s draws each figure as a shape, so a placeholder shows an empty ring or column. Use it only with the client's real figures; otherwise use metrics-counter (placeholders allowed there) or drop the section." % s["type"])
    for s in sections:
        if s["type"] == "hero-prism":
            title = norm_text(re.sub(r"<[^>]+>", " ", s["data"].get("title", "")))
            last = title.split()[-1:] or [""]
            for c in s["data"].get("cycle") or []:
                # "Outsourced teams for custom development" + "web development" repeats the noun as well
                if norm_text(c) and (norm_text(c) in title or norm_text(c).split()[-1] == last[0]):
                    ctx.err(s["path"] + ".data.title", "the title already ends the sentence the way the cycle phrase '%s' does, so the headline reads as two endings. End the title where the phrases begin: title 'Outsourced teams for', cycle 'web development', 'QA and testing'." % c)
                    break
    if motion == "signature":
        motion = "expressive"  # the old name of the mode
    if motion == "expressive":
        if brief and not EXPRESSIVE_RE.search(brief):
            ctx.err("page.motion", "\"motion\": \"expressive\" is for clients who ask for a 3D or animation-led page, and this brief does not. Remove the field: BPO buyers judge trust first, so pages stay calm (photos, reveals, counters, carousels, maps). python scripts/variety.py --blueprint <key> lists the calm variants first.")
        return
    for s in sections:
        if not is_expressive(s):
            continue
        if s["variant"].get("tier") != "expressive":
            ctx.err(s["path"] + ".data.visual", "the WebGL \"visual\" backdrop is an expressive effect. Remove the field; a calm page keeps its bands flat. It is allowed only with \"motion\": \"expressive\", for a brief that asks for a 3D or animation-led page.")
            continue
        same = fitting_variants(s["bp_slot"], lib) if s.get("bp_slot") else [k for k, v in lib["variants"].items() if v.get("group") == s["variant"].get("group")]
        calm = [v for v in same if lib["variants"][v].get("tier") != "expressive"]
        ctx.err(s["path"], "%s is an expressive variant (3D object, WebGL scene or folding effect). Professional BPO pages keep motion quiet, with at most one contextual piece in the hero. Use a calm variant for this slot: %s. Expressive variants are allowed only with \"motion\": \"expressive\", for a brief that asks for a 3D or animation-led page."
                % (s["type"], ", ".join(calm) or "drop the section"))


def check_hero_ground(ctx, sections, top):
    """Rules 6: the hero is a photo ground (hero-fullbleed with the client's photo or a film of their photos, or
    hero-mosaic) unless the client picked another one (override_hero) or the brief asked for a 3D page and the hero
    is an expressive one."""
    hero = next((s for s in sections if s["variant"].get("group") == "hero"), None)
    if not hero or hero["type"] in PHOTO_GROUND or hero["type"].startswith("custom:") or top.get("override_hero"):
        return
    if top.get("motion") in ("expressive", "signature") and hero["variant"].get("tier") == "expressive":
        return
    ctx.err(hero["path"] + ".type", "%s has no photo or video behind the copy. Clients rated every such hero (cards over a photo, service cards, globes, forms, 3D objects) as template work. Use hero-fullbleed with the client's photo, or a film of their photos made with python scripts/make_film.py <page.json> loop, or hero-mosaic with 6 or more of their photos. Another hero only when the client picks it: \"override_hero\": {\"reference\": ..., \"reason\": ...}." % hero["type"])


def hero_look(sections):
    """What makes two photo heroes look different: the variant, the layout, the alignment, a film or a still,
    and the photo itself."""
    h = next((s for s in sections if isinstance(s, dict) and str(s.get("type", "")).startswith("hero")), None)
    if not h:
        return None
    d = h.get("data") or {}
    return (h.get("type"), d.get("layout", "overlay"), d.get("align", "left"), bool(d.get("video")), d.get("tint", "brand"), str(d.get("image") or ""))


def check_unique_hero(ctx, page, page_path, sections, archetype, lib, motion="calm"):
    """Warn when a sibling site already opens with the same hero. A warning, not an error: the build must not
    depend on which other sites sit next to the page."""
    import variety
    hero = next((s["type"] for s in sections if s["variant"].get("group") == "hero"), None)
    if not hero or not archetype:
        return
    if hero in PHOTO_GROUND:
        # only two photo heroes, so they are told apart by layout, alignment, film or still and the photo
        mine = hero_look(page.get("sections") or [])
        same = [path.parent.name for path, other in variety.find_pages(page_path.parent.parent, skip=page_path)
                if hero_look(other.get("sections") or []) and hero_look(other.get("sections") or [])[:5] == mine[:5]]
        if same:
            ctx.warn("sections", "the hero looks like the one on %s (%s, same layout, alignment and %s). Change one of them: \"layout\": \"frame\" or \"overlay\", \"align\", a film of the client's photos instead of a still (scripts/make_film.py), or hero-mosaic." % (", ".join(same), hero, "film" if mine[3] else "still photo"))
        return
    arch = variety.archetypes()
    taken = {}
    for path, other in variety.find_pages(page_path.parent.parent, skip=page_path):
        h = variety.look(other, arch).get("hero")
        if h:
            taken.setdefault(h, []).append(path.parent.name)
    if hero not in taken:
        return
    slot = next((s for s in archetype["slots"] if s["slot"] == "hero"), {"variants": []})
    free = [v for v in slot["variants"] if v not in taken and (motion in ("expressive", "signature") or lib["variants"].get(v, {}).get("tier") != "expressive")]
    msg = "the hero %s is already used by %s" % (hero, ", ".join(taken[hero]))
    if free:
        ctx.warn("sections", msg + ". If one of these fits the business as well, use it so the sites look different: %s." % ", ".join(free))


def check_variety(ctx, page, page_path):
    """Warn when a sibling site (sites/*/page.json) uses nearly the same preset and variants."""
    import variety
    arch = variety.archetypes()
    others = variety.find_pages(page_path.parent.parent, skip=page_path)
    for path, score, shared in variety.compare(page, others, arch)[:3]:
        tips = "; ".join("%s: %s" % (slot, ", ".join(opts)) for slot, opts in variety.swaps(page, shared, others, arch).items() if opts)
        ctx.warn("sections", "this page shares %d%% of its look with %s (%s). Pages built from the same library should not look alike: swap some of these for less-used variants (%s), or pick another preset. python scripts/variety.py --archetype %s lists every slot, least used first." %
                 (score * 100, path.parent.name, ", ".join(shared), tips or "no other variant in these slots", page.get("archetype")))


# Blueprints (templates/blueprints/*.json): the layout of one real BPO homepage, section by section.
# A page that names a blueprint follows its order, layout forms and tones; it differs in colours and 3D visuals.
CHROME_GROUPS = ("header", "footer", "floating", "exit")
ROLE_GROUPS = {
    "hero": {"hero"},
    "services": {"services", "features", "solutions", "cards", "compare"},
    "industries": {"industries", "audience", "cards"},
    "about": {"about", "intro", "features", "team"},
    "intro": {"intro", "about", "features"},
    "metrics": {"metrics"},
    "cases": {"proof", "cards"},
    "testimonial": {"proof"},
    "clients": {"logos", "ticker"},
    "awards": {"awards", "compliance"},
    "process": {"process", "features"},
    "team": {"team", "cards"},
    "locations": {"locations"},
    "news": {"cards", "proof"},
    "careers": {"careers", "banner"},
    "faq": {"faq"},
    "cta": {"cta", "banner"},
    "pricing": {"pricing", "compare", "calculator"},
    "compare": {"compare", "pricing"},
    "tools": {"tools", "logos"},
}
# Heroes built around the client's own work (a call card in its languages, its paperwork, a support chat, its real
# service panels). They may stand in for a blueprint's hero composition when they fit the business.
BUSINESS_HEROES = {"hero-voice", "hero-ledger", "hero-chat", "hero-dashboard", "hero-form"}
# Heroes whose copy sits on the client's own photo or video under a dark shade. They keep the dark tone whatever the
# blueprint slot says: a light slot tone (an "override_hero" in place of a split hero) set dark text on a dark video.
# They are also the default hero (rules 6): a client reviewing three versions of a page (Smart Outsourcing,
# 2026-10-09) rejected every other hero (white card over a photo, service cards, a dotted globe, a form, a 3D deck, a
# sundial) as template work and kept only full photo grounds, turning them into HyperFrames films of their photos.
PHOTO_GROUND = {"hero-fullbleed", "hero-mosaic"}
# Sections that need the client's own proof are left out when the brief has none, whatever the blueprint says
PROOF_ROLES = {"testimonial", "cases", "clients", "awards", "news", "team", "careers", "locations"}


def slot_optional(slot):
    return bool(slot.get("optional")) or slot.get("role") in PROOF_ROLES


# Forms whose shape already says what they hold: any variant of the form fits, whatever the slot's role
FORM_LED = {"metrics", "logo-strip", "faq-accordion", "testimonial-block", "form", "locations-map", "video-block", "icon-strip", "cta-band"}


def slot_accepts(slot, variant):
    """A variant fits a slot when it builds the slot's layout form and can carry its content: its group suits the
    role, the form itself fixes the content, or the variant is "open" (generic title, text, picture and link fields)."""
    forms = variant.get("forms") or []
    if slot["form"] not in forms or variant.get("reshape"):
        return False  # "reshape" variants change the section's geometry, so they cannot stand in for a real layout
    g = variant.get("group")
    role = slot.get("role", "intro")
    if role == "hero" or g == "hero":
        return role == "hero" and g == "hero"
    return g in ROLE_GROUPS.get(role, set()) or slot["form"] in FORM_LED or bool(variant.get("open"))


def fitting_variants(slot, lib):
    return [k for k, v in lib["variants"].items() if slot_accepts(slot, v)]


def check_blueprint(ctx, bp, bp_key, sections, lib, motion="calm", hero_override=None):
    """Match the page's content sections to the blueprint's slots, in order. Optional slots may be left out.
    hero_override (page "override_hero"): the client picked a hero from another real site, so any hero variant fills
    the blueprint's hero slot; the rest of the page still follows the blueprint."""
    slots = bp["sections"]
    body = [s for s in sections if s["variant"].get("group") not in CHROME_GROUPS]
    j = 0
    used = 0
    roles_seen, forms_seen = set(), set()
    for s in body:
        k = j
        hero_free = (bool(hero_override) or s["type"] in PHOTO_GROUND) and s["variant"].get("group") == "hero"
        while k < len(slots) and not (slot_accepts(slots[k], s["variant"]) or (hero_free and slots[k].get("role") == "hero")):
            k += 1
        if k == len(slots):
            nxt = slots[j] if j < len(slots) else None
            hint = ("the next slot is %s (%s): use one of %s" % (nxt["role"], nxt["form"], ", ".join(fitting_variants(nxt, lib)) or "a custom section")) if nxt else "the blueprint has no slots left"
            ctx.err(s["path"] + ".type", "%s does not fit blueprint %r here; %s. The page keeps the blueprint's order and forms (templates/blueprints/%s.json)." % (s["type"], bp_key, hint, bp_key))
            continue
        for m in range(j, k):
            # a second slot with a role the page already has (a second metrics band) may go when the brief runs out
            if not slot_optional(slots[m]) and slots[m]["role"] not in roles_seen and slots[m]["form"] not in forms_seen:
                ctx.err(s["path"], "blueprint %r needs a %s section (%s) before %s. Use one of: %s." % (bp_key, slots[m]["role"], slots[m]["form"], s["type"], ", ".join(fitting_variants(slots[m], lib)) or "a custom section"))
        s["bp_slot"] = slots[k]
        s["bp_blueprint"] = bp
        # the real site's hero composition ("compose" in the blueprint): a generic text-and-photo hero loses it
        compose = slots[k].get("compose")
        if hero_free:
            if hero_override:
                ctx.warn(s["path"] + ".type", "hero taken from %s instead of blueprint %r (%s): %s" % (hero_override["reference"], bp_key, slots[k]["form"], hero_override["reason"]))
            compose = None
        if compose and slots[k].get("role") == "hero" and s["type"] not in compose and s["type"] not in BUSINESS_HEROES and not s["type"].startswith("custom:") and not (motion in ("expressive", "signature") and s["variant"].get("tier") == "expressive"):
            ctx.err(s["path"] + ".type", "blueprint %r opens with this hero: %s. Build it with %s. A business hero (%s) may replace it when it fits the client and the form. A generic text-and-photo hero is what makes generated sites look alike." % (bp_key, slots[k].get("note", ""), " or ".join(compose), ", ".join(sorted(BUSINESS_HEROES))))
        roles_seen.add(slots[k]["role"])
        forms_seen.add(slots[k]["form"])
        want = slots[k].get("count")
        lists = [(n, f) for n, f in s["variant"].get("fields", {}).items() if isinstance(f, dict) and f.get("type") == "list" and isinstance(f.get("item"), dict) and f["item"].get("type") == "object"]
        if want and lists:
            name, spec = max(lists, key=lambda x: x[1].get("max", 0))
            have = len(s["data"].get(name) or [])
            target = max(spec.get("min", 0), min(want, spec.get("max", want)))
            if have and abs(have - target) > max(1, target // 4):
                ctx.warn(s["path"] + ".data." + name, "%d items where the real layout has %d (blueprint %r, %s). A grid of a different size changes the page's shape; pick a blueprint whose sections match the brief's content, or use %d items if the brief has them." % (have, want, bp_key, slots[k]["role"], target))
        # the real hero's alignment wins over the variant default
        if "align" in s["variant"].get("fields", {}) and slots[k]["form"] in ("hero-center", "hero-left-text"):
            s["data"]["align"] = "center" if slots[k]["form"] == "hero-center" else "left"
        used += 1
        j = k + 1
    for m in range(j, len(slots)):
        if not slot_optional(slots[m]) and slots[m]["role"] not in roles_seen and slots[m]["form"] not in forms_seen:
            ctx.err("sections", "blueprint %r ends with a %s section (%s) that the page does not have. Use one of: %s." % (bp_key, slots[m]["role"], slots[m]["form"], ", ".join(fitting_variants(slots[m], lib)) or "a custom section"))
    if len(body) < 5:
        ctx.err("sections", "the page has %d content sections; real BPO homepages have 5-14. Pick a blueprint whose sections the brief can fill, not the shortest one." % len(body))
    if not any((s.get("bp_slot") or {}).get("role") == "services" for s in body):
        ctx.err("sections", "no section of the page carries the services. Every BPO homepage says what the company does: pick a blueprint with a services section (python scripts/variety.py --blueprints <archetype>).")
    # proof sections (logos, quotes, cases...) are left out when the brief has none, so they do not count here
    core = [x for x in slots if x.get("role") not in PROOF_ROLES]
    core_used = sum(1 for s in body if s.get("bp_slot") and s["bp_slot"].get("role") not in PROOF_ROLES)
    if core and core_used < 0.6 * len(core):
        ctx.err("sections", "the page fills %d of the %d content sections of blueprint %r, too few to keep its layout. Pick a blueprint with fewer content sections (python scripts/variety.py --blueprints <archetype> shows the counts)." % (core_used, len(core), bp_key))


def rules_pin(ctx, top, out_dir):
    """The pinned rules version ("1", "2" or "3") when the page pins one and its output folder holds a build made under
    that version; otherwise False.

    The pin keeps a site that was built before rules 2 building: the content checks added since (brief, blueprint,
    evidence, copied example text, voice, design, motion) print as warnings. A new page cannot use it, because its
    output folder has no earlier build, or only builds made under the current rules."""
    pin = top.get("rules")
    if not pin or int(pin) >= RULES_VERSION:
        return False
    try:
        prev = int(json.loads((out_dir / "build-report.json").read_text(encoding="utf-8")).get("rules", 1))
    except (OSError, ValueError):
        prev = None
    if prev != int(pin):
        ctx.err("page.rules", "\"rules\": \"%s\" only keeps an existing site building, and %s holds no build made under rules %s. A new page follows the current rules: remove the field." % (pin, out_dir, pin))
        return False
    ctx.warn("page.rules", "this site was built under rules %s, so the content checks added since (up to rules %d) print as warnings marked [rules %s, not enforced]. Fix them and remove the field when the client's content is next revised." % (pin, RULES_VERSION, pin))
    return pin


def check_unique_blueprint(ctx, page, page_path, archetype_key, lib):
    """Warn when a sibling site already follows the same blueprint. A warning, not an error: the build must not
    depend on which other sites sit next to the page."""
    import variety
    key = page.get("blueprint")
    if not key:
        return
    taken = {}
    for path, other in variety.find_pages(page_path.parent.parent, skip=page_path):
        if other.get("blueprint"):
            taken.setdefault(other["blueprint"], []).append(path.parent.name)
    if key not in taken:
        return
    free = [k for k, b in lib["blueprints"].items() if archetype_key in b.get("fits", []) and k not in taken]
    free.sort(key=lambda k: not lib["blueprints"][k].get("preferred"))  # layouts clients named as the standard first
    msg = "blueprint %r is already used by %s" % (key, ", ".join(taken[key]))
    if free:
        ctx.warn("page.blueprint", msg + ". If one of these fits the brief as well, use it so the sites differ in layout: %s." % ", ".join(free))


def check_order(ctx, archetype, sections, lib):
    slots = archetype["slots"]
    pointer = 0
    used = set()
    for i, sec in enumerate(sections):
        t = sec.get("type", "")
        if t.startswith("custom:"):
            continue
        found = None
        for j in range(pointer, len(slots)):
            if t in slots[j]["variants"]:
                found = j
                break
        if found is None:
            expected = [s for s in slots[pointer:]]
            ctx.err("sections[%d]" % i, "type %r is not allowed at this position for archetype %r. Next allowed slots: %s" %
                    (t, archetype["_key"], "; ".join("%s (%s)" % (s["slot"], ", ".join(s["variants"])) for s in expected[:4])))
            continue
        for j in range(pointer, found):
            if slots[j].get("required") and j not in used:
                ctx.err("sections[%d]" % i, "required slot %r (%s) is missing before %r. Add it here." %
                        (slots[j]["slot"], ", ".join(slots[j]["variants"]), t))
        used.add(found)
        pointer = found + 1
    for j in range(pointer, len(slots)):
        if slots[j].get("required") and j not in used:
            ctx.err("sections", "required slot %r (%s) is missing at the end of the page." % (slots[j]["slot"], ", ".join(slots[j]["variants"])))
    for j, slot in enumerate(slots):
        if slot.get("recommended") and j not in used:
            ctx.warn("sections", "recommended slot %r (%s) is not on the page. Fine if the client has no real content for it; tell the user it is missing." % (slot["slot"], ", ".join(slot["variants"])))


PAGE_SPEC = {
    "fields": {
        "archetype": {"type": "text", "min": 3, "max": 40},
        "blueprint": {"type": "text", "min": 2, "max": 40, "required": False},
        "preset": {"type": "text", "min": 3, "max": 40},
        "lang": {"type": "enum", "values": ["en", "vi", "ja", "ko", "de", "fr", "es", "pt", "zh"], "default": "en"},
        "site": {"type": "object", "fields": {
            "brand": {"type": "text", "min": 2, "max": 32},
            "brand_mark": {"type": "text", "min": 1, "max": 3, "required": False},
            "logo": {"type": "image", "required": False},
            # the same logo in white or a light tint, shown instead of "logo" on dark and accent surfaces
            # (a dark header over a photo or video, the mobile drawer, a dark footer)
            "logo_light": {"type": "image", "required": False},
            "title": {"type": "text", "min": 20, "max": 70},
            "description": {"type": "text", "min": 70, "max": 170},
        }},
        "seo": seo.SPEC,
        "theme": {"type": "object", "required": False, "fields": {
            "primary": {"type": "color", "required": False},
            "accent": {"type": "color", "required": False},
            "accent_2": {"type": "color", "required": False},
            "eyebrow": {"type": "enum", "values": ["plain", "pill", "caps", "line"], "required": False},
            "edges": {"type": "enum", "values": ["none", "angle", "curve"], "required": False},
            "image_mask": {"type": "enum", "values": ["rounded", "angle", "arch"], "required": False},
            "highlight": {"type": "enum", "values": ["color", "gradient", "underline"], "required": False},
            "media_reveal": {"type": "enum", "values": ["fade", "clip"], "required": False},
            "motion_style": {"type": "enum", "values": list(MOTION_STYLES), "required": False},
        }},
        "features": {"type": "object", "required": False, "fields": {
            "magnetic_cta": {"type": "bool", "default": False},
        }},
        "motion": {"type": "enum", "values": ["calm", "expressive", "signature"], "default": "calm"},
        "rules": {"type": "enum", "values": [str(v) for v in range(1, RULES_VERSION)], "required": False},
        "override_order": {"type": "object", "required": False, "fields": {
            "reason": {"type": "text", "min": 20, "max": 300},
        }},
        "override_photos": {"type": "object", "required": False, "fields": {
            "reason": {"type": "text", "min": 20, "max": 300},
        }},
        "override_hero": {"type": "object", "required": False, "fields": {
            "reference": {"type": "href"},
            "reason": {"type": "text", "min": 20, "max": 300},
        }},
        "sections": {"type": "list", "min": 4, "max": 24, "item": {"type": "object", "fields": {}}},
    }
}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page", nargs="?", help="path to page.json")
    ap.add_argument("--out", default=None, help="output folder (default: dist next to page.json)")
    ap.add_argument("--list", action="store_true", help="print the library and exit")
    args = ap.parse_args()
    lib = load_library()
    if args.list:
        print_library(lib)
        return 0
    if not args.page:
        ap.error("page.json path is required")
    page_path = Path(args.page).resolve()
    if not page_path.is_file():
        print("ERROR %s: file not found" % page_path)
        return 1
    try:
        page = load_json(page_path)
    except json.JSONDecodeError as e:
        print("ERROR page.json is not valid JSON: line %d column %d: %s" % (e.lineno, e.colno, e.msg))
        return 1
    except UnicodeDecodeError:
        print("ERROR page.json is not UTF-8 text. Save it as UTF-8 and run again.")
        return 1
    if not isinstance(page, dict):
        print("ERROR page.json must be one object: {\"archetype\": ..., \"preset\": ..., \"sections\": [...]}")
        return 1
    # Later checks walk the sections as objects, so stop here when the shape is wrong.
    if "sections" in page and not isinstance(page["sections"], list):
        print("ERROR page.sections: must be a list of sections, each {\"type\": ..., \"data\": {...}}")
        return 1
    shape = ["sections[%d]" % i for i, s in enumerate(page.get("sections") or []) if not isinstance(s, dict) or not isinstance(s.get("type"), str)]
    if shape:
        for p in shape:
            print("ERROR %s: each section needs {\"type\": \"<variant>\", \"data\": {...}}" % p)
        return 1
    out_dir = Path(args.out).resolve() if args.out else page_path.parent / "dist"
    # The write step deletes out/assets and out/index.html, so never point it at the page's own folder or a stranger's site.
    if out_dir == page_path.parent or out_dir in page_path.parents:
        print("ERROR --out: %s holds page.json and its photos would be deleted; use a subfolder such as %s" % (out_dir, page_path.parent / "dist"))
        return 1
    if any((out_dir / n).exists() for n in ("assets", "index.html")) and not (out_dir / "build-report.json").exists():
        print("ERROR --out: %s already has assets/ or index.html that this build did not make; pick an empty folder or a previous build" % out_dir)
        return 1
    ctx = Ctx(page_path.parent, out_dir, lib)

    # Top level (sections are validated one by one below).
    raw_sections = page.get("sections", [])
    # "brief" holds the client's brief as given (any wording, not checked); it tells check_copied which figures are real.
    brief = page.get("brief") if isinstance(page.get("brief"), str) else ""
    top = validate_object(ctx, {k: v for k, v in page.items() if k not in ("sections", "brief")}, {"fields": {k: v for k, v in PAGE_SPEC["fields"].items() if k != "sections"}}, "page")
    if not isinstance(raw_sections, list) or not raw_sections:
        ctx.err("page.sections", "must be a non-empty list of sections")
        raw_sections = []

    arch_key = top.get("archetype")
    archetype = lib["archetypes"].get(arch_key)
    if archetype:
        archetype["_key"] = arch_key
    elif arch_key is not None:  # a missing key is already reported as required
        ctx.err("page.archetype", "unknown archetype %r. Choose one of: %s" % (arch_key, ", ".join(lib["archetypes"])))
    preset = lib["presets"].get(top.get("preset"))
    if not preset:
        if top.get("preset") is not None:  # a missing key is already reported as required
            ctx.err("page.preset", "unknown preset %r. Choose one of: %s" % (top.get("preset"), ", ".join(lib["presets"])))
    elif top.get("lang") == "vi":
        if preset.get("fonts_vi"):
            preset = dict(preset, fonts=preset["fonts_vi"])  # the preset's own faces lack Vietnamese diacritics
        missing = [preset["fonts"][k] for k in ("heading", "body") if preset["fonts"][k] not in VI_FONTS]
        if missing:
            ctx.err("page.preset", "preset %s uses %s, which has no Vietnamese glyphs, so accented letters fall back to another font. This is a library bug: give the preset a \"fonts_vi\" entry with families from VI_FONTS in build.py." % (top.get("preset"), ", ".join(missing)))

    # Sections.
    sections = []
    ids = {}
    for i, sec in enumerate(raw_sections):
        p = "sections[%d]" % i
        if not isinstance(sec, dict) or "type" not in sec:
            ctx.err(p, "each section needs {\"type\": ..., \"data\": {...}}")
            continue
        for k in sec:
            if k not in ("type", "id", "tone", "data", "_note"):
                ctx.err("%s.%s" % (p, k), "unknown key. A section has only type, id, tone and data.")
        t = sec["type"]
        if t.startswith("custom:"):
            variant = load_custom_variant(ctx, t[7:], p)
            if not variant:
                continue
        else:
            variant = lib["variants"].get(t)
            if not variant:
                ctx.err(p + ".type", "unknown section type %r. Available: %s" % (t, ", ".join(lib["variants"])))
                continue
        data = validate_object(ctx, sec.get("data", {}), {"fields": variant["fields"]}, p + ".data")
        enrich_stats(data)
        # enum values as flags for templates: "visual": "dots" gives {{#visual_is_dots}}
        for fk, fs in variant["fields"].items():
            if isinstance(fs, dict) and fs.get("type") == "enum" and isinstance(data.get(fk), str):
                data["%s_is_%s" % (fk, re.sub(r"[^a-z0-9]+", "_", data[fk].lower()))] = True
        if t == "hero-form":
            hf = data.get("form") or {}
            if hf.get("topic_label") and not hf.get("topic_options"):
                ctx.warn(p + ".data.form.topic_options", "topic_label without options: the select is left out of the form. List its 2-8 options (the services from the brief), or drop topic_label")
            if hf.get("topic_options") and not hf.get("topic_label"):
                ctx.warn(p + ".data.form.topic_label", "topic_options without topic_label: the select is left out of the form. Add a label such as \"Service you need\"")
            if len(data.get("points") or []) == 1:
                ctx.warn(p + ".data.points", "give 2-5 ticked points, or none; a single point reads as a leftover")
        if t == "banner-image" and not data.get("image") and not data.get("visual"):
            ctx.err(p + ".data.image", "banner-image needs an image, or a 3D visual (\"visual\": \"dots\" or \"terrain\") in its place")
        if t == "services-bento" and data.get("cards") and len(data["cards"][0].get("bullets") or []) < 3:
            ctx.err(p + ".data.cards[0].bullets", "the first card is the large feature card; give it 3-4 bullets so it does not look empty")
        if t == "comparison-table":
            cols = data.get("columns") or []
            icons = {"yes": "check", "no": "x", "partial": "minus"}
            for ri, row in enumerate(data.get("rows") or []):
                vals = row.get("values") or []
                if len(vals) != len(cols):
                    ctx.err("%s.data.rows[%d].values" % (p, ri), "has %d values but the table has %d columns. Give one value per column, in column order." % (len(vals), len(cols)))
                for ci, v in enumerate(vals):
                    v["col"] = cols[ci]["name"] if ci < len(cols) else ""
                    v["first"] = ci == 0
                    v["mark_icon"] = icons.get(v.get("mark"), "minus")
                    v["mark_label"] = data.get("%s_label" % v.get("mark"), "")
        if t == "tool-stack":
            for tool in data.get("tools") or []:
                m = re.search(r"\w", tool.get("name", ""))
                tool["initial"] = m.group().upper() if m else "?"
        if t == "image-cards" and not data.get("slider") and len(data.get("cards") or []) not in (3, 4, 6):
            ctx.err(p + ".data.cards", "a grid needs 3, 4 or 6 cards (got %d). Use that count, or set \"slider\": true for 3 to 8 cards." % len(data.get("cards") or []))
        if t == "hero-cycler-centered" and data.get("title_before") and data.get("words"):
            last = plain(data["title_before"]).split()[-1].lower()
            preps = ("in", "for", "to", "with", "at", "of", "on", "from", "by")
            bad = [w for w in data["words"] if last in preps and w.split()[0].lower() in preps]
            if bad:
                ctx.err(p + ".data.words", "the title reads \"%s %s\". Each word is shown right after title_before, so every one must finish that sentence; do not start a word with another preposition." % (plain(data["title_before"]), bad[0]))
        if t == "video-block":
            vid = data.get("video") or {}
            if bool(vid.get("src")) == bool(vid.get("embed")):
                ctx.err(p + ".data.video", "set exactly one of src (a video file) or embed (a YouTube or Vimeo URL)")
        if t == "voice-sample" and any(not x.get("audio") for x in data.get("samples") or []):
            ctx.warn(p + ".data.samples", "some samples have no audio file; their players animate without sound. Add real recordings before launch.")
        if (t in ("cta-multistep", "contact-split", "contact-photo", "hero-form") or t == "cta-letter" and data.get("form")) and not (data.get("form") or {}).get("action"):
            ctx.warn(p + ".data.form.action", "no form action set; the form shows a thank-you message but sends nothing. Add a form endpoint URL before launch.")
        if t == "cta-letter" and not data.get("form") and not data.get("primary_cta"):
            ctx.err(p + ".data", "cta-letter needs primary_cta or form, or the letter has no way to reply.")
        if t == "hero-slides":
            # every slide takes its own layout, so the hero changes shape from slide to slide (SoGlobal review)
            need = {"fullbleed": ("photo",), "split": ("photo", "ticks"), "cards": ("cards",), "panels": ("panels",), "overlap": ("photo",)}
            seen = {}
            for i, sl in enumerate(data.get("slides") or []):
                lay = sl.get("layout")
                if lay in seen:
                    ctx.err("%s.data.slides[%d].layout" % (p, i), "slide %d uses layout %r like slide %d. Every slide takes its own layout (fullbleed, split, cards, panels, overlap), so the hero changes shape from slide to slide." % (i + 1, lay, seen[lay] + 1))
                seen.setdefault(lay, i)
                for f in need.get(lay, ()):
                    if not sl.get(f):
                        ctx.err("%s.data.slides[%d].%s" % (p, i, f), "layout %r needs %s." % (lay, f))
                for f in ("photo", "ticks", "cards", "panels"):
                    if sl.get(f) and f not in need.get(lay, ()) and not (f == "ticks" and lay == "fullbleed"):
                        ctx.warn("%s.data.slides[%d].%s" % (p, i, f), "layout %r does not show %s; remove it or pick a layout that uses it." % (lay, f))
        if t == "hero-sundial":
            for i, hub in enumerate(data.get("hubs") or []):
                if isinstance(hub.get("city"), dict) and not hub["city"].get("tz"):
                    ctx.err("%s.data.hubs[%d].city" % (p, i), "this city has no time zone. Use a city key from templates/data/cities.json, or add \"tz\" (IANA name such as \"Asia/Manila\") to the city object; the dial never guesses a zone.")
        sid = sec.get("id") or variant.get("anchor") or t
        if not re.fullmatch(r"[a-z][a-z0-9-]*", sid):
            ctx.err(p + ".id", "id must be lowercase letters, digits and hyphens, starting with a letter")
        if sid in ids:
            ids[sid] += 1
            sid = "%s-%d" % (sid, ids[sid])
        else:
            ids[sid] = 1
        tone_override = sec.get("tone")
        if tone_override is not None and tone_override not in ("light", "muted", "dark"):
            ctx.err(p + ".tone", "must be light, muted or dark")
            tone_override = None
        sections.append({"type": t, "variant": variant, "id": sid, "data": data, "tone_override": tone_override, "path": p})

    legacy = rules_pin(ctx, top, out_dir)
    ctx.soft = legacy
    bp_key = top.get("blueprint")
    bp = lib["blueprints"].get(bp_key) if bp_key else None
    if bp_key and not bp:
        ctx.err("page.blueprint", "unknown blueprint %r. Choose one of: %s" % (bp_key, ", ".join(lib["blueprints"])))
    if bp:
        check_blueprint(ctx, bp, bp_key, sections, lib, top.get("motion", "calm"), top.get("override_hero"))
    elif archetype and not top.get("override_order"):
        check_order(ctx, archetype, raw_sections if isinstance(raw_sections, list) else [], lib)
    elif top.get("override_order"):
        ctx.warn("page.override_order", "archetype order check skipped: %s" % top["override_order"]["reason"])

    check_brand_colors(ctx, top, page_path.parent, brief, page.get("site"))
    check_voice(ctx, sections, top.get("lang", "en"), bp)
    check_design(ctx, sections, top.get("site") or {}, preset or {}, top.get("theme") or {}, top.get("override_photos"))
    check_figures(ctx, sections)
    check_images(ctx, sections)
    check_stock_photos(ctx, raw_sections, (top.get("site") or {}).get("brand"))
    check_legal(ctx, sections, (top.get("site") or {}).get("brand"))
    for s in sections:
        if s["type"] == "footer-columns" and s["data"].get("wordmark") and not WORDMARK_RE.search(brief or ""):
            ctx.err(s["path"] + ".data.wordmark", "the footer wordmark (the brand name in huge type) is on, but the brief does not ask for it. Clients read it as a template flourish; leave it off unless the brief asks for a large brand name in the footer.")
        if s["type"] == "footer-matrix" and not (MATRIX_RE.search(brief or "") or WORDMARK_RE.search(brief or "") or top.get("motion") in ("expressive", "signature")):
            ctx.err(s["path"], "footer-matrix draws the brand mark in a moving LED dot panel, and the brief does not ask for it. Like the footer wordmark, clients read it as a flourish; use footer-columns unless the brief asks for a dot-matrix or large brand mark, or the page is \"motion\": \"expressive\".")
    if SKILL / "examples" not in page_path.parents:
        check_copied(ctx, sections, brief)
        check_named_faces(ctx, raw_sections)
        if brief:
            check_numbers(ctx, sections, brief)
        if not top.get("blueprint") and lib["blueprints"]:
            ctx.err("page.blueprint", "add \"blueprint\": \"<key>\": every page follows the layout of one real site. List the ones that fit with: python scripts/variety.py --blueprints %s --sites sites" % (arch_key or "<archetype>"))
        if not brief:
            ctx.err("page.brief", "add the client's brief, word for word as they gave it, as \"brief\": \"...\" at the top of page.json. The build checks every client name, quote, certification, tool, guarantee and figure on the page against it.")
        else:
            check_evidence(ctx, sections, brief)
        check_variety(ctx, page, page_path)
        check_motion(ctx, sections, archetype, lib, top.get("motion", "calm"), brief or "")
        check_hero_ground(ctx, sections, top)
        check_unique_hero(ctx, page, page_path, sections, archetype, lib, top.get("motion", "calm"))
        check_unique_blueprint(ctx, page, page_path, arch_key, lib)
    ctx.soft = False
    seo.check(ctx, top, sections, SKILL / "examples" in page_path.parents)

    for path, anchor in ctx.anchors:
        if anchor not in ids and anchor != "top":
            ctx.err(path, "link points to #%s but no section has that id. Section ids on this page: %s" % (anchor, ", ".join(ids)))

    if ctx.errors:
        report(ctx, failed=True)
        return 1

    # Tones.
    hero_tone = preset["hero_tone"]
    prev = None
    for s in sections:
        mode = s["variant"].get("tone", "auto")
        bp_tone = (s.get("bp_slot") or {}).get("tone")
        if s["tone_override"]:
            tone = s["tone_override"]
        elif bp_tone and mode in ("auto", "hero", "light", "muted", "dark") and s["type"] not in PHOTO_GROUND:
            tone = bp_tone
        elif mode == "hero" or mode == "header":
            tone = hero_tone
        elif mode in ("light", "muted", "dark", "accent"):
            tone = mode
        elif mode == "none":
            s["tone"] = "light"
            continue
        else:
            tone = "muted" if prev == "light" else "light"
        s["tone"] = tone
        if mode != "header":
            if tone == "dark" and prev == "dark" and s["variant"].get("group") not in ("footer",) and not s.get("bp_slot"):
                ctx.warn(s["path"], "two dark sections in a row; consider reordering or setting tone")
            prev = tone
    # The header sits on top of the hero, so it takes the tone the hero really got.
    hero_sec = next((s for s in sections if s["variant"].get("group") == "hero"), None)
    if hero_sec:
        hero_tone = hero_sec["tone"]
        for s in sections:
            if s["variant"].get("tone") == "header" and not s["tone_override"]:
                s["tone"] = hero_tone

    # Render.
    renderer = Renderer(lib["icons"], lib["flags"])
    site = dict(top["site"])
    site["brand_mark"] = site.get("brand_mark") or "".join(w[0] for w in re.findall(r"[A-Za-z0-9]+", site["brand"])[:2]).upper()
    site["year"] = date.today().year
    site["seed"] = brand_seed(site["brand"])
    features = top.get("features") or {"magnetic_cta": False}
    body = []
    used_variants = []
    for s in sections:
        v = s["variant"]
        if v["_dir"] not in [u["_dir"] for u in used_variants]:
            used_variants.append(v)
        section_ctx = {"section": {"id": s["id"], "tone": s["tone"], "type": s["type"], "hero_tone": hero_tone},
                       "site": site, "features": features, "page": {"lang": top["lang"]}}
        markup = renderer.render_file(v["_dir"] / "section.html", [section_ctx, s["data"]]).strip()
        if not re.match(r'<(section|header|footer|div|aside|dialog)\b[^>]*\bid="%s"' % re.escape(s["id"]), markup):
            ctx.err(s["path"], "template bug: the root element of %s must carry id=\"{{section.id}}\"" % s["type"])
        body.append((v.get("group", "content"), markup))

    css = [theme_css(preset, top.get("theme") or {}, ctx), (TPL / "base.css").read_text(encoding="utf-8")]
    js = [vendor_text(ctx, TPL / "vendor" / "gsap.js"), (TPL / "base.js").read_text(encoding="utf-8")]
    shared_done = set()
    for v in used_variants:
        for name in v.get("shared", []) + shared_for_data(v, [s["data"] for s in sections if s["variant"] is v]):
            if name in shared_done:
                continue
            shared_done.add(name)
            for ext, bucket in ((".css", css), (".js", js)):
                f = SECTIONS_DIR / "_shared" / (name + ext)
                if f.is_file():
                    bucket.append(vendor_text(ctx, f) if f.name == "three.js" else f.read_text(encoding="utf-8"))
        if (v["_dir"] / "section.css").is_file():
            src = (v["_dir"] / "section.css").read_text(encoding="utf-8")
            if v.get("_custom"):
                check_custom_css(ctx, src, v["_dir"])
            css.append(src)
        if (v["_dir"] / "section.js").is_file():
            src = (v["_dir"] / "section.js").read_text(encoding="utf-8")
            if v.get("_custom"):
                check_custom_js(ctx, src, v["_dir"])
            js.append(src)

    theme = top.get("theme") or {}
    design = dict({"edges": "none", "image_mask": "rounded", "highlight": "color", "media_reveal": "fade"}, **preset.get("design", {}))
    for k in design:
        if theme.get(k):
            design[k] = theme[k]
    eyebrow = theme.get("eyebrow") or preset.get("eyebrow", "plain")
    if eyebrow == "line":
        eyebrow = "plain"  # the old rule before the label read as a dash; "line" is kept as a name only
    if eyebrow == "caps" and top.get("lang") == "vi":
        eyebrow = "plain"  # tracked capitals with Vietnamese diacritics are hard to read
    root_class = " ".join(["bl-eyebrow-%s" % eyebrow, "bl-edges-%s" % design["edges"], "bl-mask-%s" % design["image_mask"],
                           "bl-hl-%s" % design["highlight"], "bl-media-%s" % design["media_reveal"],
                           "bl-motion-%s" % motion_style(theme, preset, site["seed"])])
    try:
        prev_report = json.loads((out_dir / "build-report.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        prev_report = None
    seo_head, seo_files, seo_record = seo.build(ctx, top, site, sections, body, preset, ctx.placeholders, prev_report)
    shell = {"root_class": root_class, "lang": top["lang"], "site": site, "preset": preset, "fonts_query": preset["fonts"]["google"],
             "body": Safe(assemble_body(body)), "hero_tone": hero_tone, "seo_head": Safe(seo_head)}
    page_html = renderer.render_file(TPL / "page.html", [shell])
    page_html = re.sub(r"<!--.*?-->", "", page_html, flags=re.S)
    page_html = re.sub(r"\n\s*\n+", "\n", page_html)

    gl_sections = [s["id"] for s, (_, markup) in zip(sections, body) if 'data-gl="' in markup]
    if len(gl_sections) > MAX_GL_SCENES:
        ctx.err("sections", "%d sections draw a WebGL scene (%s); a page carries at most %d (the hero and one band, or two bands). "
                "Drop the \"visual\" of a band or pick a hero without a scene." % (len(gl_sections), ", ".join(gl_sections), MAX_GL_SCENES))
    own_js = sum(len(t) for t in js) - sum(len(t) for t in js if VENDOR_BANNER in t[:200])
    if own_js > OWN_JS_LIMIT:
        ctx.err("sections", "the page's own JavaScript is %d KB (limit %d KB, vendor files not counted). Use fewer script-heavy sections."
                % (own_js // 1024, OWN_JS_LIMIT // 1024))

    if ctx.errors:
        report(ctx, failed=True)
        return 1

    # Write.
    if out_dir.exists():
        for sub in ("assets", "index.html", "build-report.json", "robots.txt", "sitemap.xml"):
            target = out_dir / sub
            if target.is_dir():
                shutil.rmtree(target)
            elif target.exists():
                target.unlink()
    (out_dir / "assets" / "css").mkdir(parents=True, exist_ok=True)
    (out_dir / "assets" / "js").mkdir(parents=True, exist_ok=True)
    (out_dir / "assets" / "img").mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(page_html, encoding="utf-8")
    css_text = re.sub(r"/\*.*?\*/", "", "\n".join(css), flags=re.S)
    (out_dir / "assets" / "css" / "style.css").write_text(re.sub(r"\n\s*\n+", "\n", css_text), encoding="utf-8")
    (out_dir / "assets" / "js" / "main.js").write_text("\n".join(js), encoding="utf-8")
    for rel, src in ctx.images.items():
        (out_dir / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, out_dir / rel)
    for rel, text in seo_files.items():
        (out_dir / rel).write_bytes(text if isinstance(text, bytes) else text.encode("utf-8"))
    rep = {"rules": int(legacy) if legacy else RULES_VERSION, "archetype": arch_key, "preset": top["preset"], "motion_style": re.search(r"bl-motion-(\w+)", root_class).group(1), "sections": [{"type": s["type"], "id": s["id"], "tone": s["tone"], "group": s["variant"].get("group")} for s in sections],
           "seo": seo_record, "warnings": ctx.warnings, "placeholders": ctx.placeholders}
    (out_dir / "build-report.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    report(ctx, failed=False)
    print("OK built %d sections into %s" % (len(sections), out_dir / "index.html"))
    return 0


def shared_for_data(v, datas):
    """Extra _shared files a variant needs only for some field values, from its schema "shared_by_field":
    {"visual": {"*": [...], "dots": [...]}} adds "*" whenever the field is set and the value's own list."""
    out = []
    for field, table in (v.get("shared_by_field") or {}).items():
        for d in datas:
            value = d.get(field)
            if value in (None, "", False):
                continue
            for name in table.get("*", []) + table.get(str(value), []):
                if name not in out:
                    out.append(name)
    return out


def assemble_body(parts):
    head = [m for g, m in parts if g == "header"]
    tail = [m for g, m in parts if g in ("footer", "floating")]
    mid = [m for g, m in parts if g not in ("header", "footer", "floating")]
    return "\n".join(head) + '\n<main id="main">\n' + "\n".join(mid) + "\n</main>\n" + "\n".join(tail)


def load_custom_variant(ctx, name, path):
    d = ctx.page_dir / "sections" / name
    if not (d / "schema.json").is_file() or not (d / "section.html").is_file():
        ctx.err(path + ".type", "custom section %r needs %s with schema.json and section.html (see references/custom-section-spec.md)" % (name, d))
        return None
    v = dict(resolve_refs(load_json(d / "schema.json"), load_json(TPL / "data" / "schema-defs.json")), _dir=d, _custom=True)
    v.setdefault("tone", "auto")
    v.setdefault("anchor", name)
    return v


MAX_GL_SCENES = 2
OWN_JS_LIMIT = 300 * 1024
VENDOR_BANNER = "Built by tools/vendor/build.mjs"  # in the first line of every vendored file
_vendor_ok = {}
CRLF, LF = bytes([13, 10]), bytes([10])


def vendor_text(ctx, path):
    """A vendored library, checked against templates/vendor/VERSIONS.json so a hand edit or a partial rebuild fails the build."""
    text = path.read_text(encoding="utf-8")
    key = str(path)
    if key not in _vendor_ok:
        versions = load_json(TPL / "vendor" / "VERSIONS.json")
        rel = path.relative_to(TPL.parent).as_posix()
        entry = next((e for e in versions.values() if e["file"] == rel), None)
        digest = hashlib.sha256(path.read_bytes().replace(CRLF, LF)).hexdigest()  # a checkout with CRLF line ends still matches
        _vendor_ok[key] = bool(entry) and entry["sha256"] == digest
        if not _vendor_ok[key]:
            ctx.err(rel, "does not match templates/vendor/VERSIONS.json. Vendor files are generated: run npm ci and node build.mjs in tools/vendor, never edit them by hand.")
    return text


def check_custom_js(ctx, src, d):
    """Custom section scripts share the page's render loop, WebGL toolkit and pause switch (references/custom-section-spec.md)."""
    where = "%s/section.js" % d.name
    if "setAnimationLoop" in src or re.search(r"new\s+(THREE\.)?WebGLRenderer", src):
        ctx.err(where, "creates its own WebGL renderer or animation loop. Register a scene with BLGL.register(name, factory) "
                "(templates/sections/_shared/gl.js) so it shares the render loop, pause switch and fallback.")
    if re.search(r"repeat\s*:\s*-1", src) and "BL.motion.ambient" not in src:
        ctx.err(where, "has a GSAP tween with repeat: -1 that the Pause animations switch cannot stop. Wrap it in BL.motion.ambient(...).")
    if "requestAnimationFrame(" in src:
        ctx.warn(where, "runs its own requestAnimationFrame loop. Draw through BLRibbons.loop or a BLGL scene so it stops off screen and on Pause.")


def check_custom_css(ctx, src, d):
    for m in re.finditer(r"#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(", src):
        line = src.count("\n", 0, m.start()) + 1
        ctx.err("%s/section.css:%d" % (d.name, line), "raw color %r. Custom sections must use tokens like var(--text-strong), var(--c-accent)." % m.group())
    for m in re.finditer(r"font-family\s*:(?![^;]*var\()", src):
        ctx.err("%s/section.css" % d.name, "font-family must use var(--font-heading) or var(--font-body)")


def report(ctx, failed):
    for w in ctx.warnings:
        print("WARN  " + w)
    for e in ctx.errors:
        print("ERROR " + e)
    if failed:
        print("\nBUILD FAILED with %d error(s). Fix page.json and run build.py again. Do not edit dist/ by hand." % len(ctx.errors))
    if ctx.placeholders:
        print("\nPlaceholders to confirm with the client:")
        for p in ctx.placeholders:
            print("  " + p)


def run():
    try:
        return main()
    except Exception as e:  # a value of the wrong type that validation did not catch
        import traceback
        where = traceback.extract_tb(e.__traceback__)[-1]
        print("ERROR build.py stopped on page.json: %s: %s (%s line %d)." % (type(e).__name__, e, Path(where.filename).name, where.lineno))
        print("A value probably has the wrong type, such as text where a list, an object or a number is expected. "
              "Compare that part of page.json with an example in examples/. If it matches, this is a library bug: quote this message to the user.")
        return 1


if __name__ == "__main__":
    sys.exit(run())
