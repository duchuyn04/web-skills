#!/usr/bin/env python3
"""Build a BPO landing page from a page.json config. Python standard library only.

Usage:
    python build.py page.json --out dist
    python build.py --list            print archetypes, presets, variants, icons, images, cities

The model writes page.json. This script owns layout, spacing, colors, animation and markup.
Every error names the JSON path and says how to fix it.
"""
import argparse
import html
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rules  # noqa: E402

SKILL = HERE.parent
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
    with open(path, encoding="utf-8") as f:
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
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
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

    def err(self, path, msg):
        self.errors.append("%s: %s" % (path, msg))

    def warn(self, path, msg):
        self.warnings.append("%s: %s" % (path, msg))


PLACEHOLDER_RE = re.compile(r"^\[[^\]]{1,40}\]$")
MARKUP_RE = re.compile(r"\*([^*]+)\*")
HREF_RE = re.compile(r"^(#[A-Za-z][\w-]*|#|https?://\S+|mailto:\S+|tel:[+\d][\d\s-]*|[\w./-]+\.(html|pdf))$")
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def check_copy(ctx, path, text):
    for f in rules.check_text(text):
        (ctx.err if f.level == "error" else ctx.warn)(path, "%s (near: \"%s\")" % (f.message, f.excerpt))
    for m in re.finditer(r"\[[^\]]{1,40}\]", text):
        ctx.placeholders.append("%s: %s" % (path, m.group()))


def text_len(s):
    return len(MARKUP_RE.sub(r"\1", s))


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
            return Safe(MARKUP_RE.sub(r'<span class="bl-hl">\1</span>', html.escape(value, quote=False)))
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
            ctx.err(path, "needs %s items, got %d. Other counts leave gaps in the grid." %
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
                out[k + "_plain"] = MARKUP_RE.sub(r"", value[k].strip())
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
    """Turn stat fields into display strings plus counter attributes; add initials for people."""
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
    return {"icons": icons, "flags": flags, "cities": cities, "presets": presets,
            "archetypes": {k: v for k, v in archetypes.items() if not k.startswith("_")},
            "variants": variants, "images": images, "videos": videos}


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


def theme_css(preset, overrides, ctx):
    colors = dict(preset["colors"])
    for k in ("primary", "accent", "accent_2"):
        if overrides.get(k):
            colors[k] = overrides[k]
    accent = parse_hex(colors["accent"])
    white, ink = (255, 255, 255), (11, 15, 25)
    cw, cd = contrast(accent, white), contrast(accent, ink)
    on_accent = white if cw >= 4.5 or cw >= cd else ink
    if max(cw, cd) < 4.5:
        ctx.warn("theme.accent", "button text contrast is %.2f:1 (target 4.5). Pick a darker or lighter accent." % max(cw, cd))
    lines = [":root {",
             "  --font-heading: '%s', system-ui, sans-serif;" % preset["fonts"]["heading"],
             "  --font-body: '%s', system-ui, sans-serif;" % preset["fonts"]["body"],
             "  --font-mono: '%s', ui-monospace, monospace;" % preset["fonts"]["mono"],
             "  --heading-weight: %s;" % preset["type"]["heading_weight"],
             "  --heading-tracking: %s;" % preset["type"]["heading_tracking"],
             "  --c-primary: %s;" % colors["primary"],
             "  --c-accent: %s;" % colors["accent"],
             "  --c-accent-2: %s;" % colors["accent_2"],
             "  --c-on-accent: %s;" % to_hex(on_accent)]
    for k, v in preset["shape"].items():
        lines.append("  --%s: %s;" % (k.replace("_", "-"), v))
    lines.append("}")
    for tone, spec in preset["tones"].items():
        vals = {k: resolve_color(v, colors) if isinstance(v, str) else v for k, v in spec.items()}
        bg = parse_hex(vals["bg"])
        strong = parse_hex(vals["text_strong"])
        dark = vals["is_dark"]
        accent_ink = ink_for(accent, bg)
        for key in ("text", "text_muted"):
            c = parse_hex(vals[key])
            if c and contrast(c, bg) < 4.5:
                vals[key] = to_hex(ink_for(c, bg))
        border_strong = to_hex(mix(bg, strong, 0.22 if not dark else 0.28))
        surf = parse_hex(vals["surface"]) or bg
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
                  "  --accent-ink: %s;" % to_hex(accent_ink),
                  "  --glass: %s;" % ("rgba(%d, %d, %d, 0.62)" % surf if dark else "rgba(255, 255, 255, 0.74)"),
                  "  --glass-border: %s;" % ("rgba(255, 255, 255, 0.12)" if dark else "rgba(255, 255, 255, 0.9)"),
                  "  --shadow-lg: %s;" % ("0 24px 48px -20px rgba(0, 0, 0, 0.65)" if dark else "0 24px 48px -24px rgba(15, 23, 42, 0.24)"),
                  "}"]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- page structure
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
        "preset": {"type": "text", "min": 3, "max": 40},
        "lang": {"type": "enum", "values": ["en", "vi", "ja", "ko", "de", "fr", "es", "pt", "zh"], "default": "en"},
        "site": {"type": "object", "fields": {
            "brand": {"type": "text", "min": 2, "max": 32},
            "brand_mark": {"type": "text", "min": 1, "max": 3, "required": False},
            "logo": {"type": "image", "required": False},
            "title": {"type": "text", "min": 20, "max": 70},
            "description": {"type": "text", "min": 70, "max": 170},
        }},
        "theme": {"type": "object", "required": False, "fields": {
            "primary": {"type": "color", "required": False},
            "accent": {"type": "color", "required": False},
            "accent_2": {"type": "color", "required": False},
        }},
        "features": {"type": "object", "required": False, "fields": {
            "magnetic_cta": {"type": "bool", "default": False},
        }},
        "override_order": {"type": "object", "required": False, "fields": {
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
    try:
        page = load_json(page_path)
    except json.JSONDecodeError as e:
        print("ERROR page.json is not valid JSON: line %d column %d: %s" % (e.lineno, e.colno, e.msg))
        return 1
    out_dir = Path(args.out).resolve() if args.out else page_path.parent / "dist"
    ctx = Ctx(page_path.parent, out_dir, lib)

    # Top level (sections are validated one by one below).
    raw_sections = page.get("sections", [])
    top = validate_object(ctx, {k: v for k, v in page.items() if k != "sections"}, {"fields": {k: v for k, v in PAGE_SPEC["fields"].items() if k != "sections"}}, "page")
    if not isinstance(raw_sections, list) or not raw_sections:
        ctx.err("page.sections", "must be a non-empty list of sections")
        raw_sections = []

    arch_key = top.get("archetype")
    archetype = lib["archetypes"].get(arch_key)
    if not archetype:
        ctx.err("page.archetype", "unknown archetype %r. Choose one of: %s" % (arch_key, ", ".join(lib["archetypes"])))
    else:
        archetype["_key"] = arch_key
    preset = lib["presets"].get(top.get("preset"))
    if not preset:
        ctx.err("page.preset", "unknown preset %r. Choose one of: %s" % (top.get("preset"), ", ".join(lib["presets"])))

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
        if t == "services-bento" and data.get("cards") and len(data["cards"][0].get("bullets") or []) < 3:
            ctx.err(p + ".data.cards[0].bullets", "the first card is the large feature card; give it 3-4 bullets so it does not look empty")
        if t == "video-block":
            vid = data.get("video") or {}
            if bool(vid.get("src")) == bool(vid.get("embed")):
                ctx.err(p + ".data.video", "set exactly one of src (a video file) or embed (a YouTube or Vimeo URL)")
        if t == "voice-sample" and any(not x.get("audio") for x in data.get("samples") or []):
            ctx.warn(p + ".data.samples", "some samples have no audio file; their players animate without sound. Add real recordings before launch.")
        if t == "cta-multistep" and not (data.get("form") or {}).get("action"):
            ctx.warn(p + ".data.form.action", "no form action set; the form shows a thank-you message but sends nothing. Add a form endpoint URL before launch.")
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

    if archetype and not top.get("override_order"):
        check_order(ctx, archetype, raw_sections if isinstance(raw_sections, list) else [], lib)
    elif top.get("override_order"):
        ctx.warn("page.override_order", "archetype order check skipped: %s" % top["override_order"]["reason"])

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
        if s["tone_override"]:
            tone = s["tone_override"]
        elif mode == "hero" or mode == "header":
            tone = hero_tone
        elif mode in ("light", "muted", "dark"):
            tone = mode
        elif mode == "none":
            s["tone"] = "light"
            continue
        else:
            tone = "muted" if prev == "light" else "light"
        s["tone"] = tone
        if mode != "header":
            if tone == "dark" and prev == "dark" and s["variant"].get("group") not in ("footer",):
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
    js = [(TPL / "base.js").read_text(encoding="utf-8")]
    shared_done = set()
    for v in used_variants:
        for name in v.get("shared", []):
            if name in shared_done:
                continue
            shared_done.add(name)
            for ext, bucket in ((".css", css), (".js", js)):
                f = SECTIONS_DIR / "_shared" / (name + ext)
                if f.is_file():
                    bucket.append(f.read_text(encoding="utf-8"))
        if (v["_dir"] / "section.css").is_file():
            src = (v["_dir"] / "section.css").read_text(encoding="utf-8")
            if v.get("_custom"):
                check_custom_css(ctx, src, v["_dir"])
            css.append(src)
        if (v["_dir"] / "section.js").is_file():
            js.append((v["_dir"] / "section.js").read_text(encoding="utf-8"))

    shell = {"lang": top["lang"], "site": site, "preset": preset, "fonts_query": preset["fonts"]["google"],
             "body": Safe(assemble_body(body)), "hero_tone": hero_tone}
    page_html = renderer.render_file(TPL / "page.html", [shell])
    page_html = re.sub(r"<!--.*?-->", "", page_html, flags=re.S)
    page_html = re.sub(r"\n\s*\n+", "\n", page_html)

    if ctx.errors:
        report(ctx, failed=True)
        return 1

    # Write.
    if out_dir.exists():
        for sub in ("assets", "index.html", "build-report.json"):
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
    rep = {"archetype": arch_key, "preset": top["preset"], "sections": [{"type": s["type"], "id": s["id"], "tone": s["tone"], "group": s["variant"].get("group")} for s in sections],
           "warnings": ctx.warnings, "placeholders": ctx.placeholders}
    (out_dir / "build-report.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    report(ctx, failed=False)
    print("OK built %d sections into %s" % (len(sections), out_dir / "index.html"))
    return 0


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


if __name__ == "__main__":
    sys.exit(main())
