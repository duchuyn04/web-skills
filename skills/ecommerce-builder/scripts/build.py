"""Build an electronics shop (storefront + admin dashboard) from one shop.json.

    python scripts/build.py sites/<slug>/shop.json --out sites/<slug>/dist

The model writes only shop.json. This script validates it, draws product art, seeds demo data for the
dashboard and renders every page from the fixed templates in templates/. Errors name the JSON path and the
fix; the build fails until there are none.
"""
import argparse
import datetime as dt
import hashlib
import html
import json
import math
import random
import re
import shutil
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import jinja2
    from markupsafe import Markup
except ImportError:
    raise SystemExit("build.py needs Jinja2: run  python -m pip install jinja2")

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
TPL = SKILL / "templates"
DATA = SKILL / "data"
EXAMPLE = SKILL / "examples" / "demo-electronics.shop.json"
sys.path.insert(0, str(HERE))
import rules  # noqa: E402
import devices  # noqa: E402
import variants as V  # noqa: E402
import blueprints as BP  # noqa: E402

ARROW_SVG = ('<svg class="i i-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" '
             'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"></line>'
             '<polyline points="12 5 19 12 12 19"></polyline></svg>')

PRESETS = json.loads((DATA / "presets.json").read_text(encoding="utf-8"))
STYLES = json.loads((DATA / "styles.json").read_text(encoding="utf-8"))
STYLES.pop("_variants", None)
VARIANTS = V.all_variants()       # part -> variant names, found from the template folders
ICONS = json.loads((DATA / "icons.json").read_text(encoding="utf-8"))
PROVINCES = json.loads((DATA / "provinces.json").read_text(encoding="utf-8"))["provinces"]

TOP_KEYS = {"_note", "demo", "sample_content", "style", "layout", "blueprint", "lang", "brief", "shop", "theme", "announcement", "categories", "brands", "products", "home",
            "promotions", "shipping", "payments", "benefits", "stores", "policies", "staff"}
PRODUCT_KEYS = {"id", "name", "brand", "category", "device", "price", "old_price", "options", "stock", "sku", "color", "facets",
                "card_specs", "highlights", "description", "specs", "promos", "badges", "installment", "warranty", "in_box",
                "rating", "reviews", "qa", "faq", "sold", "released", "addons", "keywords", "images"}
HOME_TYPES = V.section_types()
BADGES = {"new": "Mới", "hot": "Bán chạy", "installment": "Trả góp 0%", "exclusive": "Độc quyền", "preorder": "Đặt trước"}
ORDER_STATUSES = [
    ["pending", "Chờ xác nhận"], ["confirmed", "Đã xác nhận"], ["packing", "Đang chuẩn bị"],
    ["shipping", "Đang giao"], ["delivered", "Đã giao"], ["cancelled", "Đã hủy"], ["returned", "Trả hàng"],
]


# --------------------------------------------------------------------------- errors
class Ctx:
    def __init__(self):
        self.errors, self.warnings = [], []

    def err(self, path, msg):
        self.errors.append("%s: %s" % (path, msg))

    def warn(self, path, msg):
        self.warnings.append("%s: %s" % (path, msg))


def slugify(s):
    s = s.lower()
    table = str.maketrans("àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ",
                          "aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd")
    s = s.translate(table)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def vnd(n):
    if n is None:
        return ""
    return "{:,}".format(int(round(n))).replace(",", ".") + " đ"


# --------------------------------------------------------------------------- colour
def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _lum(h):
    def ch(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = _rgb(h)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def mix(a, b, t):
    ra, rb = _rgb(a), _rgb(b)
    return "#" + "".join("%02x" % round(x + (y - x) * t) for x, y in zip(ra, rb))


def darken_until(color, bg, target=4.5):
    c = color
    for _ in range(40):
        if contrast(c, bg) >= target:
            return c
        c = mix(c, "#000000", 0.06)
    return c


def readable(color, bg, target=4.5):
    """Move a colour toward black (light background) or white (dark background) until it reaches the contrast target."""
    c, to = color, ("#000000" if _lum(bg) > 0.18 else "#ffffff")
    for _ in range(40):
        if contrast(c, bg) >= target:
            return c
        c = mix(c, to, 0.06)
    return c


def theme_vars(theme, ctx, default_preset="red-retail"):
    name = theme.get("preset", default_preset)
    if name not in PRESETS:
        ctx.err("theme.preset", "unknown preset '%s'. Use one of: %s" % (name, ", ".join(PRESETS)))
        name = default_preset
    p = dict(PRESETS[name])
    for k in ("accent", "header_bg", "price"):
        if theme.get(k):
            if not re.fullmatch(r"#[0-9a-fA-F]{6}", theme[k]):
                ctx.err("theme." + k, "use a 6-digit hex colour such as #d70018")
            else:
                p[k] = theme[k]
    if theme.get("accent") and not theme.get("header_bg") and p.get("header_follows_accent"):
        p["header_bg"] = theme["accent"]
    bg, surface = p["bg"], p.get("surface", "#ffffff")
    text, muted = p.get("text", "#1b1f24"), p.get("muted", "#5b6470")
    dark = _lum(surface) < 0.18
    accent = p["accent"]
    # button fill must carry white text
    btn = accent if contrast(accent, "#ffffff") >= 4.5 else darken_until(accent, "#ffffff", 4.5)
    if p.get("button_dark_text") and contrast(accent, "#111111") >= 7:
        btn_fg, btn = "#111111", accent
    else:
        btn_fg = "#ffffff"
    price = readable(p.get("price", "#d70018"), surface, 4.5)
    hb = p["header_bg"]
    hfg = "#ffffff" if contrast(hb, "#ffffff") >= contrast(hb, "#111111") else "#111111"
    link = readable(p.get("link", accent if dark else btn), surface, 4.5)
    soft = mix(accent, surface, 0.82) if dark else mix(accent, "#ffffff", 0.9)
    v = {
        "--c-bg": bg, "--c-surface": surface, "--c-surface-2": p.get("surface_2", "#f6f7f9"),
        "--c-text": text, "--c-muted": readable(muted, surface, 4.5), "--c-border": p.get("border", "#e3e6ea"),
        "--c-accent": accent, "--c-btn": btn, "--c-btn-fg": btn_fg, "--c-btn-hover": mix(btn, "#000000", 0.12),
        "--c-accent-soft": soft, "--c-accent-ink": readable(accent, soft, 4.5),
        "--c-price": price, "--c-link": link,
        "--c-header": hb, "--c-header-fg": hfg, "--c-header-soft": mix(hb, hfg, 0.14),
        "--c-sale": (mix(accent, surface, 0.8) if dark else mix(accent, "#ffffff", 0.86)) if theme.get("accent") or dark else p.get("sale_bg", "#ffe8a3"),
        "--c-ok": "#3ccf7e" if dark else "#0f7a3d", "--c-warn": "#f0b33a" if dark else "#9a5b00", "--c-bad": "#ff7a6b" if dark else "#b42318",
        "--c-dark": p.get("dark", "#14171c"), "--radius": p.get("radius", "10px"), "--radius-lg": p.get("radius_lg", "14px"),
        "--font": p.get("font", "'Be Vietnam Pro', system-ui, sans-serif"), "--font-head": p.get("font_head", p.get("font", "'Be Vietnam Pro', system-ui, sans-serif")),
    }
    # the admin always stays on light surfaces
    admin = dict(v)
    admin.update({"--c-bg": "#f4f5f7", "--c-surface": "#ffffff", "--c-surface-2": "#f6f7f9", "--c-text": "#1b1f24", "--c-muted": "#5b6470",
                  "--c-border": "#e3e6ea", "--c-ok": "#0f7a3d", "--c-warn": "#9a5b00", "--c-bad": "#b42318",
                  "--c-price": readable(p.get("price", "#d70018"), "#ffffff"), "--c-link": readable(btn, "#ffffff")})
    return v, p, name, admin


# --------------------------------------------------------------------------- copy checks
def walk_strings(node, path=""):
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, dict):
        for k, v in node.items():
            if k in ("brief", "_note", "id", "href", "url", "hex", "map", "image", "images", "sku", "icon", "device", "layout", "style", "variant", "blueprint", "bg", "device_color", "type"):
                continue
            yield from walk_strings(v, "%s.%s" % (path, k) if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_strings(v, "%s[%d]" % (path, i))


def check_copy(ctx, shop):
    for path, text in walk_strings(shop):
        for f in rules.check_text(text):
            (ctx.err if f.level == "error" else ctx.warn)(path, "%s (%s)" % (f.message, f.excerpt))
        # Vietnamese decimals use a comma: 6,7 inch, 1,2 kg
        m = re.search(r"\b\d+\.\d+\s?(?:inch|kg|g|mm|cm|GHz|giờ|triệu|tỷ)\b", text)
        if m and shop.get("lang", "vi") == "vi":
            ctx.err(path, "write the decimal with a comma in Vietnamese: '%s' should be '%s'" % (m.group(), m.group().replace(".", ",", 1)))


# --------------------------------------------------------------------------- facts against the brief
# Fields whose text states product facts or promises to buyers.
FACT_FIELDS = re.compile(r"(\.specs\[\d+\]\.rows\[\d+\]\[1\]|\.highlights|\.description|\.card_specs|\.promos|\.faq\[\d+\]\.a|\.qa\[\d+\]\.a|\.in_box|\.warranty"
                         r"|^benefits|^announcement|^shipping\[\d+\]\.(eta|name)|^policies|^home\[\d+\]\.(slides|side|items)\[\d+\]\.(text|title|label|tab))")
# Claims a shop has to be able to back up; each must appear in the brief.
CLAIMS = ["chính hãng", "hoàn tiền", "1 đổi 1", "một đổi một", "miễn phí", "trong ngày", "2 giờ", "tuyệt đối", "vat", "hóa đơn",
          "lắp đặt", "tại nhà", "trọn đời", "thu cũ", "trả góp", "tặng", "quà", "rẻ nhất", "giá tốt nhất", "cam kết", "bảo hành"]


HOME_SKIP = {"youtube", "type", "variant", "bg", "ink", "query", "category", "href", "icon", "cta", "device", "device_color", "product", "products", "ends", "id", "tone", "align", "sold", "limit", "sale_price"}


def is_fact_path(path):
    """Product texts and every text inside a home section (item texts, quotes, numbers), but not a section's own title or its wiring keys."""
    if FACT_FIELDS.search(path):
        return True
    m = re.match(r"^home\[\d+\]\.(.+)$", path)
    if not m:
        return False
    rest = m.group(1)
    last = re.sub(r"\[\d+\]", "", rest.split(".")[-1])
    return rest != "title" and last not in HOME_SKIP


def _tokens_with_digits(text):
    """Numbers and model codes in a text: 14650HX, 2560x1600, 90, 2,4, RTX5070."""
    out = []
    for t in re.findall(r"[A-Za-z]*\d[\w.,]*", text):
        t = t.strip(".,").lower()
        if t:
            out.append(t)
    return out


def _norm_num(t):
    t = t.lower().replace(",", ".")
    # 1.000.000 style thousands
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", t):
        t = t.replace(".", "")
    return t


def check_facts(ctx, shop, example_strings):
    """On a shop built from a client brief, product facts, offers and promises must come from the brief."""
    brief = shop.get("brief", "")
    bnorm = brief.lower()
    bnums = {_norm_num(t) for t in _tokens_with_digits(brief)}
    # numbers inside the brief's own compound tokens (RTX 5070 / 5070) count too
    for t in list(bnums):
        bnums.update(re.findall(r"\d+(?:\.\d+)?", t))
    names = {_norm_num(t) for p in shop.get("products") or [] for t in _tokens_with_digits(p.get("name", ""))}
    reported = set()
    for path, text in walk_strings(shop):
        if not is_fact_path(path):
            continue
        low = text.lower()
        copyable = re.search(r"(\.description|\.highlights|\.promos|\.faq|\.qa|\.specs|^home)", path) and len(text.split()) >= 6
        if copyable and text.strip() in example_strings and text.strip().lower() not in bnorm:
            ctx.err(path, "'%s' is copied from the example shop, whose facts are made up. Use the client's facts from the brief, or leave it out." % text[:80])
            continue
        missing = []
        for t in _tokens_with_digits(text):
            n = _norm_num(t)
            parts = re.findall(r"\d+(?:\.\d+)?", n)
            if n in bnums or n in names or all(p in bnums for p in parts):
                continue
            missing.append(t)
        if missing:
            key = (path, tuple(missing))
            if key not in reported:
                reported.add(key)
                ctx.err(path, "'%s' has figures or model codes that are not in the brief (%s). Product facts, offers and times must come from the brief; drop the detail or ask the client. A shop the user asked you to invent from scratch sets \"sample_content\": true." % (text[:90], ", ".join(missing[:5])))
        for c in CLAIMS:
            rx = r"(?<!\w)" + re.escape(c) + r"(?!\w)"
            if re.search(rx, low) and not re.search(rx, bnorm):
                ctx.err(path, "'%s' promises \"%s\", which the brief does not. Remove the promise or ask the client." % (text[:90], c))


# --------------------------------------------------------------------------- normalise
def need(ctx, obj, key, path, kind=str, msg=""):
    v = obj.get(key) if isinstance(obj, dict) else None
    if v is None or v == "" or v == []:
        ctx.err("%s.%s" % (path, key) if path else key, "required. " + msg)
        return None
    if kind and not isinstance(v, kind):
        ctx.err("%s.%s" % (path, key) if path else key, "must be %s" % getattr(kind, "__name__", kind))
        return None
    return v


def norm_value(v):
    if isinstance(v, str):
        return {"name": v}
    return dict(v)


def normalise(shop, ctx, rng):
    out = {}
    demo = bool(shop.get("demo"))
    s = shop.get("shop") or {}
    need(ctx, shop, "shop", "", dict)
    for k in ("name", "tagline", "hotline", "email"):
        need(ctx, s, k, "shop")
    s.setdefault("slug", slugify(s.get("name", "shop")))
    out["shop"] = s
    out["demo"] = demo
    out["lang"] = shop.get("lang", "vi")

    cats = []
    for i, c in enumerate(shop.get("categories") or []):
        p = "categories[%d]" % i
        need(ctx, c, "id", p)
        need(ctx, c, "name", p)
        c = dict(c)
        c.setdefault("icon", "package")
        if c["icon"] not in ICONS:
            ctx.err(p + ".icon", "unknown icon '%s'. Run build.py --list for the icon names." % c["icon"])
        c.setdefault("device", "phone")
        if c["device"] not in devices.KINDS:
            ctx.err(p + ".device", "unknown device '%s'. Use one of: %s" % (c["device"], ", ".join(devices.KINDS)))
        c.setdefault("facets", [])
        cats.append(c)
    if not cats:
        ctx.err("categories", "add at least one category, for example {\"id\": \"dien-thoai\", \"name\": \"Điện thoại\", \"icon\": \"smartphone\", \"device\": \"phone\"}")
    cat_by = {c["id"]: c for c in cats if c.get("id")}

    brands = []
    for i, b in enumerate(shop.get("brands") or []):
        need(ctx, b, "id", "brands[%d]" % i)
        need(ctx, b, "name", "brands[%d]" % i)
        brands.append(dict(b))
    brand_by = {b["id"]: b for b in brands if b.get("id")}

    products = []
    seen = set()
    for i, p0 in enumerate(shop.get("products") or []):
        path = "products[%d]" % i
        if not isinstance(p0, dict):
            ctx.err(path, "each product is an object {\"id\": ..., \"name\": ..., \"price\": ...}")
            continue
        p = json.loads(json.dumps(p0))
        for k in ("id", "name", "brand", "category"):
            need(ctx, p, k, path)
        if not p.get("id"):
            continue
        if p["id"] in seen:
            ctx.err(path + ".id", "duplicate product id '%s'" % p["id"])
        seen.add(p["id"])
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", p["id"]):
            ctx.err(path + ".id", "use lowercase letters, digits and hyphens (it becomes the page file name)")
        if p.get("category") not in cat_by:
            ctx.err(path + ".category", "'%s' is not a category id. Use one of: %s" % (p.get("category"), ", ".join(cat_by)))
            continue
        if p.get("brand") not in brand_by:
            ctx.err(path + ".brand", "'%s' is not a brand id. Add it to brands or use one of: %s" % (p.get("brand"), ", ".join(brand_by)))
            continue
        cat = cat_by[p["category"]]
        p["device"] = p.get("device") or cat["device"]
        if p["device"] not in devices.KINDS:
            ctx.err(path + ".device", "unknown device '%s'" % p["device"])
            p["device"] = cat["device"]
        options = []
        if not isinstance(p.get("options") or [], list):
            ctx.err(path + ".options", "a list of options such as [{\"name\": \"Dung lượng\", \"values\": [...]}]")
            continue
        for j, o in enumerate(p.get("options") or []):
            op = "%s.options[%d]" % (path, j)
            if not isinstance(o, dict) or not isinstance(o.get("values") or [], list):
                ctx.err(op, "an option is {\"name\": ..., \"values\": [...]}")
                continue
            need(ctx, o, "name", op)
            vals = [norm_value(v) for v in (o.get("values") or [])]
            if not vals:
                ctx.err(op + ".values", "list at least one value")
            options.append({"name": o.get("name", ""), "values": vals, "color": any("hex" in v for v in vals)})
        if len([o for o in options if o["color"]]) > 1:
            ctx.err(path + ".options", "only one option may carry colours (hex)")
        p["options"] = options
        base_price = p.get("price")
        priced = [o for o in options if any("price" in v for v in o["values"])]
        if base_price is None and not priced:
            ctx.err(path + ".price", "give the selling price in VND (number), or a price on each value of one option such as storage")
            continue
        if len(priced) > 1:
            ctx.err(path + ".options", "put prices on one option only (usually storage); the other options share them")
        # variants: cross product of option values
        combos = [[]]
        for o in options:
            combos = [c + [v] for c in combos for v in o["values"]]
        stock_map = p.get("stock") if isinstance(p.get("stock"), dict) else {}
        variants = []
        for n, combo in enumerate(combos):
            price, old = base_price, p.get("old_price")
            for v in combo:
                if "price" in v:
                    price, old = v["price"], v.get("old_price")
            label = " / ".join(v["name"] for v in combo)
            if isinstance(p.get("stock"), int):
                stock = p["stock"]
            elif label in stock_map:
                stock = stock_map[label]
            elif demo:
                stock = rng.choice([0, 3, 5, 8, 12, 18, 25, 40]) if rng.random() > 0.08 else 0
            else:
                stock = None
            color = next((v for v in combo if "hex" in v), None)
            variants.append({
                "sku": "%s-%02d" % (p.get("sku", p["id"]).upper()[:14], n + 1),
                "values": [v["name"] for v in combo], "label": label, "price": price, "old_price": old,
                "stock": stock, "color": color["name"] if color else None,
            })
        if not variants:
            continue
        if demo and not isinstance(p.get("stock"), (int, dict)) and all(not v["stock"] for v in variants):
            variants[0]["stock"] = rng.choice([4, 8, 12])   # a demo product always has something to sell
        bad_price = False
        for v in variants:
            if not isinstance(v["price"], (int, float)) or v["price"] < 1000:
                bad_price = True
                ctx.err(path, "price must be a VND number such as 8990000 (no dots or quotes), got %r" % v["price"])
            elif v["old_price"] is not None and not isinstance(v["old_price"], (int, float)):
                bad_price = True
                ctx.err(path, "old_price must be a VND number such as 9990000 (no dots or quotes), got %r" % v["old_price"])
            elif v["old_price"] is not None and v["old_price"] <= v["price"]:
                ctx.err(path, "old_price (%s) must be higher than price (%s), or leave it out" % (v["old_price"], v["price"]))
        if bad_price:
            continue
        if not demo and any(v["stock"] is None for v in variants):
            ctx.warn(path + ".stock", "no stock given; the page shows every variant as in stock. Give stock as a number or a map of variant label to number.")
            for v in variants:
                if v["stock"] is None:
                    v["stock"] = 10
        p["variants"] = variants
        cheapest = min(variants, key=lambda v: v["price"])
        p["price"] = cheapest["price"]
        p["old_price"] = cheapest["old_price"]
        p["discount"] = round((cheapest["old_price"] - cheapest["price"]) * 100 / cheapest["old_price"]) if cheapest["old_price"] else 0
        p["stock_total"] = sum(v["stock"] or 0 for v in variants)
        p["brand_name"] = brand_by[p["brand"]]["name"]
        p["category_name"] = cat["name"]
        p.setdefault("facets", {})
        for f in cat["facets"]:
            if f["key"] not in p["facets"]:
                ctx.warn(path + ".facets", "no value for filter '%s' (%s); the product will not match that filter" % (f["key"], f["label"]))
        p.setdefault("card_specs", [x if isinstance(x, str) else ", ".join(x) for x in list(p["facets"].values())[:3]])
        p.setdefault("highlights", [])
        p.setdefault("specs", [])
        p.setdefault("promos", [])
        p.setdefault("badges", [])
        for b in p["badges"]:
            if b not in BADGES:
                ctx.err(path + ".badges", "unknown badge '%s'. Use: %s" % (b, ", ".join(BADGES)))
        if p.get("installment") and "installment" not in p["badges"]:
            p["badges"].append("installment")
        if not p["specs"]:
            ctx.warn(path + ".specs", "no specification table; electronics buyers compare specs, add groups such as Màn hình, Hiệu năng, Pin")
        # images: client photos per colour, else product art per colour
        colors = next((o["values"] for o in options if o["color"]), None) or [{"name": "", "hex": p.get("color", "#2b2f36")}]
        p["gallery"] = []
        for v in colors:
            src = v.get("image")
            p["gallery"].append({"color": v["name"], "hex": v.get("hex"), "src": src, "art": not src})
        if not demo and all(g["art"] for g in p["gallery"]):
            ctx.warn(path + ".images", "no product photos; the page shows drawn product art. Add \"image\" on each colour value with the shop's own photos before launch.")
        p["reviews"] = p.get("reviews") or []
        if p.get("rating") and not demo and not p["reviews"]:
            ctx.err(path + ".rating", "a star rating needs the reviews it comes from (reviews list) or \"demo\": true")
        if p["reviews"] and not p.get("rating"):
            n = len(p["reviews"])
            p["rating"] = {"avg": round(sum(r.get("stars", 5) for r in p["reviews"]) / n, 1), "count": n}
        if not demo:
            brief = shop.get("brief", "")
            for j, r in enumerate(p["reviews"]):
                if r.get("text") and r["text"] not in brief:
                    ctx.err("%s.reviews[%d].text" % (path, j), "reviews must be real and appear word for word in the brief. Remove invented reviews or set \"demo\": true for a sample shop.")
            if p.get("sold"):
                ctx.err(path + ".sold", "sold counts are only allowed on a demo shop (\"demo\": true)")
        p["qa"] = p.get("qa") or []
        for k in ("description", "in_box", "addons", "faq"):
            p.setdefault(k, [])
        products.append(p)
    # versions of one model must be one product with a priced option, not several products
    import collections
    stems = collections.defaultdict(list)
    for p in products:
        stem = re.sub(r"\b\d+\s?(gb|tb)\b|/|\(.*?\)", " ", p["name"].lower())
        stems[(p["brand"], p["category"], re.sub(r"\s+", " ", stem).strip())].append(p["id"])
    for k, group in stems.items():
        if len(group) > 1:
            ctx.err("products", "%s look like versions of the same model. Make one product and put the versions in a priced option: {\"name\": \"Phiên bản\", \"values\": [{\"name\": \"16GB/512GB\", \"price\": ...}, ...]}." % ", ".join(group))
    for p in products:
        for o in p["options"]:
            if len(o["values"]) == 1 and not o["color"] and "price" not in o["values"][0]:
                ctx.err("products[%s].options" % p["id"], "the option '%s' has a single value '%s', so the buyer has nothing to choose. Remove it." % (o["name"], o["values"][0]["name"]))
    ids = {p["id"] for p in products}
    for i, p in enumerate(products):
        bad = [a for a in p["addons"] if a not in ids or a == p["id"]]
        if bad:
            ctx.err("products[%s].addons" % p["id"], "unknown or self product ids: %s" % ", ".join(bad))
            p["addons"] = [a for a in p["addons"] if a in ids and a != p["id"]]
    if len(products) < 4:
        ctx.err("products", "a shop needs at least 4 products so listings, rails and comparison work")

    for c in cats:
        items = [p for p in products if p["category"] == c["id"]]
        c["count"] = len(items)
        c["brands"] = [b for b in brands if any(p["brand"] == b["id"] for p in items)]
        for f in c["facets"]:
            vals = []
            for p in items:
                v = p["facets"].get(f["key"])
                for x in (v if isinstance(v, list) else [v]):
                    if x and x not in vals:
                        vals.append(x)
            f["values"] = sorted(vals, key=natural_key)
        if not c.get("price_ranges"):
            top = max([p["price"] for p in items] or [10000000])
            steps = [2000000, 5000000, 10000000, 15000000, 20000000, 30000000, 50000000]
            edges = [0] + [s for s in steps if s < top] + [None]
            c["price_ranges"] = [[edges[k], edges[k + 1]] for k in range(len(edges) - 1)][-6:]
        if c["count"] == 0:
            ctx.warn("categories", "category '%s' has no products; it is left out of the menu" % c["id"])
    out["categories"] = [c for c in cats if c["count"]]
    out["brands"] = brands
    out["products"] = products
    return out


UNIT_SCALE = {"mb": 1 / 1024, "gb": 1, "tb": 1024, "w": 1, "kw": 1000, "mah": 1, "hz": 1, "inch": 1, "kg": 1, "g": 1 / 1000, "l": 1, "lít": 1, "btu": 1, "mm": 1}


def natural_key(s):
    """Sort facet values by their size when they read like '256 GB' or '1 TB', otherwise naturally."""
    m = re.match(r"^\s*(\d+(?:[.,]\d+)?)\s*([a-zA-Zíí]+)", str(s))
    if m and m.group(2).lower() in UNIT_SCALE:
        unit = m.group(2).lower()
        group = "storage" if unit in ("mb", "gb", "tb") else unit
        return [0, group, float(m.group(1).replace(",", ".")) * UNIT_SCALE[unit]]
    return [1] + [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", str(s))]


# --------------------------------------------------------------------------- seed (demo dashboard data)
FAMILY = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
MIDDLE = ["Văn", "Thị", "Minh", "Quốc", "Thanh", "Ngọc", "Gia", "Hoài", "Đức", "Thu", "Hải", "Bảo", "Khánh", "Anh"]
GIVEN = ["An", "Bình", "Châu", "Dũng", "Giang", "Hà", "Hạnh", "Hiếu", "Hùng", "Huy", "Khoa", "Lan", "Linh", "Long",
         "Mai", "Nam", "Ngân", "Nhung", "Phong", "Phúc", "Quân", "Quỳnh", "Sơn", "Tâm", "Thảo", "Trang", "Trung", "Tú", "Vy", "Yến"]


def seed_data(shop, norm, rng, days=400):
    """Demo history for the admin: customers, orders and daily traffic over `days` days ending today.

    Compact arrays keep seed.js small; admin.js decodes them. Orders follow a weekly rhythm, Vietnamese
    shopping peaks (Tet, double days 9/9 to 12/12, year end) and a growth of about 20% a year, so the
    previous-year comparison has something to show.
    """
    today = dt.date.today()
    cities = list(PROVINCES[:6]) + rng.sample(PROVINCES[6:], 8)
    city_w = [28, 33, 6, 7, 5, 3] + [2] * 8
    prods = norm["products"]
    skus = [v["sku"] for p in prods for v in p["variants"]]
    sku_i = {s: i for i, s in enumerate(skus)}
    weights = [max(1.0, 40.0 / math.sqrt(p["price"] / 1e6 + 1)) for p in prods]
    pays = [p["id"] for p in shop.get("payments") or [{"id": "cod"}]]
    pay_w = {"cod": 46, "bank": 22, "card": 14, "wallet": 12, "installment": 9}
    ships = shop.get("shipping") or [{"id": "standard", "fee": 30000}]
    channels = ["Website", "Hotline", "Cửa hàng"]
    statuses = [s[0] for s in ORDER_STATUSES]
    hours = list(range(7, 24))
    hour_w = [2, 3, 4, 6, 9, 10, 8, 5, 5, 6, 6, 7, 8, 10, 11, 9, 5]
    month_w = {1: 1.35, 2: 1.05, 3: 0.9, 4: 0.9, 5: 0.95, 6: 1.0, 7: 0.95, 8: 1.0, 9: 1.05, 10: 1.0, 11: 1.2, 12: 1.3}

    customers = []
    n_cust = int(days * 3.2)
    for i in range(n_cust):
        name = "%s %s %s" % (rng.choice(FAMILY), rng.choice(MIDDLE), rng.choice(GIVEN))
        customers.append(["KH%05d" % (1001 + i), name, "09%d*****%02d" % (rng.randint(0, 9), rng.randint(0, 99)),
                          "%s%d@example.com" % (slugify(name.split()[-1]), rng.randint(1, 99)),
                          cities.index(rng.choices(cities, city_w)[0]), -rng.randint(0, days + 60)])
    by_join = {}
    for ci, c in enumerate(customers):
        by_join.setdefault(c[5], []).append(ci)

    orders, traffic = [], []
    num = 20001
    eligible = [ci for ci, c in enumerate(customers) if c[5] < -days + 1]
    for d in range(-days + 1, 1):
        day = today + dt.timedelta(days=d)
        eligible += by_join.get(d, [])
        factor = (1.25 if day.weekday() >= 5 else 1.0) * month_w[day.month] * (1 + 0.2 * (d + days) / 365)
        if day.day == day.month and day.month >= 9:
            factor *= 2.2          # 9/9, 10/10, 11/11, 12/12 sales
        n = max(2, int(rng.gauss(11, 3) * factor))
        if d == 0:
            n = max(3, int(n * min(1.0, (dt.datetime.now().hour + 1) / 24)))
        conv = rng.uniform(0.017, 0.026)
        sessions = int(n / conv)
        checkouts = int(n * rng.uniform(1.55, 1.9))
        carts = int(checkouts * rng.uniform(2.2, 2.8))
        traffic.append([d, sessions, carts, checkouts])
        fresh = by_join.get(d, [])
        for k in range(n):
            # people who joined today place their first order today; the rest are repeat buyers
            ci = fresh[k] if k < len(fresh) else rng.choice(eligible or [0])
            items = []
            for p in rng.choices(prods, weights, k=rng.choices([1, 2, 3], [74, 21, 5])[0]):
                v = rng.choice(p["variants"])
                if any(it[0] == sku_i[v["sku"]] for it in items):
                    continue
                items.append([sku_i[v["sku"]], 1 if rng.random() > 0.08 else 2, v["price"]])
            sub = sum(it[1] * it[2] for it in items)
            si = rng.randrange(len(ships))
            ship = ships[si]
            fee = 0 if sub >= ship.get("free_over", 10 ** 12) else ship.get("fee", 0)
            disc, pi = 0, -1
            if rng.random() < 0.18 and shop.get("promotions"):
                pi = rng.randrange(len(shop["promotions"]))
                pr = shop["promotions"][pi]
                if sub < pr.get("min", 0):
                    pi = -1
                else:
                    if pr.get("type") == "fixed":
                        disc = pr["value"]
                    elif pr.get("type") == "percent":
                        disc = min(sub * pr["value"] // 100, pr.get("max", 10 ** 12))
                    else:
                        disc = fee
            age = -d
            if age == 0:
                st = rng.choices(["pending", "confirmed", "packing"], [55, 30, 15])[0]
            elif age <= 2:
                st = rng.choices(["confirmed", "packing", "shipping", "delivered", "cancelled"], [10, 25, 40, 20, 5])[0]
            else:
                st = rng.choices(["delivered", "cancelled", "returned"], [88, 8, 4])[0]
            pay = rng.choices(pays, [pay_w.get(x, 5) for x in pays])[0]
            paid = st != "cancelled" and (pay != "cod" or st in ("delivered", "returned"))
            minute = rng.choices(hours, hour_w)[0] * 60 + rng.randint(0, 59)
            if d == 0:
                now_m = dt.datetime.now().hour * 60 + dt.datetime.now().minute
                if minute > now_m:
                    minute = rng.randint(min(7 * 60, now_m), now_m)
            orders.append([num, d, minute, ci, items, int(disc), fee, statuses.index(st), pays.index(pay), 1 if paid else 0, si,
                           rng.choices([0, 1, 2], [70, 18, 12])[0], pi])
            num += 1
    store_stock = {}
    for st in shop.get("stores") or []:
        store_stock[st["id"]] = [v["sku"] for p in prods for v in p["variants"] if (v["stock"] or 0) > 0 and rng.random() < 0.7]
    return {"v": 2, "days": days, "skus": skus, "cities": cities, "channels": channels, "pays": pays,
            "ships": [s["id"] for s in ships], "statuses": statuses, "promos": [p["code"] for p in shop.get("promotions") or []], "customers": customers, "orders": orders,
            "traffic": traffic, "store_stock": store_stock, "demo": True}


def style_layout(style):
    return {k: STYLES[style].get(k, V.PART_DEFAULT.get(k)) for k in VARIANTS}


def look_of(shop):
    """What a visitor notices first: style, the layout parts and the colour preset."""
    style = shop.get("style", "retail") if shop.get("style") in STYLES else "retail"
    layout = style_layout(style)
    layout.update({k: v for k, v in (shop.get("layout") or {}).items() if k in VARIANTS and v in VARIANTS[k]})
    preset = (shop.get("theme") or {}).get("preset", STYLES[style]["preset"])
    return style, layout, preset


def check_variety(ctx, shop, shop_path):
    """Sibling shops (sites/<slug>/shop.json) must not share the same look: a page made from the same parts reads as a copy."""
    me = Path(shop_path).resolve()
    if me.parent.parent.name != "sites":
        return
    style, layout, preset = look_of(shop)
    for other in sorted(me.parent.parent.glob("*/shop.json")):
        if other.resolve() == me:
            continue
        try:
            o = json.loads(other.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        ostyle, olayout, opreset = look_of(o)
        same = [k for k in VARIANTS if layout[k] == olayout[k]]
        total = sum(V.PART_WEIGHT.get(k, 1) for k in VARIANTS) + 4          # +4: style 2, preset 2
        score = sum(V.PART_WEIGHT.get(k, 1) for k in same) + (2 if style == ostyle else 0) + (2 if preset == opreset else 0)
        if score / total >= 0.8:
            free = {k: [v for v in VARIANTS[k] if v != layout[k]] for k in ("header", "hero", "card")}
            ctx.err("layout", "this shop looks like %s (%d%% the same: style %s, preset %s, same %s). Change the header, hero or card in \"layout\" "
                    "(header: %s; hero: %s; card: %s), pick another preset, or choose another style." % (
                        other.parent.name, round(score * 100 / total), style, preset, ", ".join(same), ", ".join(free["header"]), ", ".join(free["hero"]), ", ".join(free["card"])))


# --------------------------------------------------------------------------- render helpers
def icon(name, cls=""):
    body = ICONS.get(name)
    if body is None:
        return Markup("")
    return Markup('<svg class="i %s" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
                  'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>' % (cls, body))


def build(shop_path, out_dir, ctx):
    shop = json.loads(Path(shop_path).read_text(encoding="utf-8-sig"))  # -sig: Notepad and PowerShell 5.1 write a byte order mark
    if not isinstance(shop, dict):
        ctx.err("shop.json", "must be one object: {\"brief\": ..., \"shop\": {...}, \"products\": [...]}")
        return None
    src_dir = Path(shop_path).parent
    seed = int(hashlib.md5(json.dumps(shop.get("shop", {}).get("name", "")).encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)
    if "brief" not in shop:
        ctx.err("brief", "paste the shop owner's brief (or the sample brief) as given. It is required: the build checks reviews and claims against it.")
    for k in shop:
        if k not in TOP_KEYS:
            ctx.err(k, "unknown top-level key. Allowed: %s" % ", ".join(sorted(TOP_KEYS)))
    for i, p in enumerate(shop.get("products") or []):
        for k in (p if isinstance(p, dict) else []):
            if k not in PRODUCT_KEYS:
                ctx.err("products[%d].%s" % (i, k), "unknown product key. Allowed: %s (see references/shop-schema.md)" % ", ".join(sorted(PRODUCT_KEYS)))
    check_copy(ctx, shop)
    check_variety(ctx, shop, shop_path)
    if not shop.get("sample_content"):
        ex = json.loads(EXAMPLE.read_text(encoding="utf-8")) if EXAMPLE.exists() and Path(shop_path).resolve() != EXAMPLE.resolve() else {}
        ex_strings = {t.strip() for p, t in walk_strings(ex) if FACT_FIELDS.search(p) and len(t.strip()) > 5}
        check_facts(ctx, shop, ex_strings)
    norm = normalise(shop, ctx, rng)
    style = shop.get("style", "retail")
    if style not in STYLES:
        ctx.err("style", "unknown style '%s'. Use one of: %s" % (style, ", ".join("%s (%s)" % (k, v["pick"]) for k, v in STYLES.items())))
        style = "retail"
    layout = style_layout(style)
    for k, val in (shop.get("layout") or {}).items():
        if k not in VARIANTS:
            ctx.err("layout." + k, "unknown layout part. Use: %s" % ", ".join(VARIANTS))
        elif val not in VARIANTS[k]:
            ctx.err("layout." + k, "unknown %s '%s'. Use one of: %s" % (k, val, ", ".join(VARIANTS[k])))
        else:
            layout[k] = val
    for k, val in layout.items():
        if val not in VARIANTS[k]:
            ctx.err("layout." + k, "the %s variant '%s' is not built; choose one of: %s" % (k, val, ", ".join(VARIANTS[k])))
        else:
            for e in V.check_variant(k, val):
                ctx.err("layout." + k, e)
    tvars, preset, preset_name, admin_vars = theme_vars(shop.get("theme") or {}, ctx, STYLES[style]["preset"])

    home = shop.get("home") or []
    if not home:
        ctx.err("home", "list the homepage sections, for example [{\"type\": \"hero\", ...}, {\"type\": \"categories\"}, {\"type\": \"rail\", \"category\": \"dien-thoai\"}]")
    pid = {p["id"]: p for p in norm["products"]}
    # banner and tile backgrounds may name brand colours instead of hex values
    accent = tvars["--c-accent"]
    BG_WORDS = {"accent": tvars["--c-btn"], "accent-dark": mix(accent, "#000000", 0.55), "accent-soft": mix(accent, "#ffffff", 0.86),
                "dark": tvars["--c-dark"], "light": mix(tvars["--c-bg"], "#ffffff", 0.5), "surface": tvars["--c-surface-2"]}

    def resolve_bg(node):
        if isinstance(node, dict):
            if isinstance(node.get("bg"), str) and node["bg"] in BG_WORDS:
                node["bg"] = BG_WORDS[node["bg"]]
            for v in node.values():
                resolve_bg(v)
        elif isinstance(node, list):
            for v in node:
                resolve_bg(v)
    resolve_bg(home)
    for i, sec in enumerate(home):
        sec["_i"] = i + 1
        path = "home[%d]" % i
        t = sec.get("type")
        if t not in HOME_TYPES:
            ctx.err(path + ".type", "unknown section '%s'. Use one of: %s" % (t, ", ".join(HOME_TYPES)))
            continue
        have = V.section_variants(t)
        if sec.get("variant") and sec["variant"] not in have:
            ctx.err(path + ".variant", "section '%s' has no variant '%s'%s" % (t, sec["variant"], ("; use one of: " + ", ".join(have)) if have else " (it has a single design)"))
        for e in V.check_section(t, sec.get("variant") if sec.get("variant") in have else None):
            ctx.err(path, e)
        if t == "hero":
            if not 1 <= len(sec.get("slides") or []) <= 5:
                ctx.err(path + ".slides", "give 1-5 slides, each with title, text, cta and product (or device)")
            side_max = 4 if (sec.get("variant") or layout["hero"]) in ("wide", "bento", "split") else 3
            if len(sec.get("side") or []) > side_max:
                ctx.err(path + ".side", "at most %d side banners for this hero" % side_max)
            for j, sl in enumerate((sec.get("slides") or []) + (sec.get("side") or [])):
                if sl.get("product") and sl["product"] not in pid:
                    ctx.err("%s.slides[%d].product" % (path, j), "unknown product id '%s'" % sl["product"])
        if t == "deal-of-day":
            for it in (sec.get("items") or ([{"product": sec.get("product"), "sale_price": sec.get("sale_price")}] if sec.get("product") else [])):
                if it.get("product") in pid and it.get("sale_price") and it["sale_price"] >= pid[it["product"]]["price"]:
                    ctx.err(path + ".sale_price", "the deal price must be lower than the normal price %s" % pid[it["product"]]["price"])
        if t == "flash-sale":
            for j, it in enumerate(sec.get("items") or []):
                if it.get("product") not in pid:
                    ctx.err("%s.items[%d].product" % (path, j), "unknown product id '%s'" % it.get("product"))
                elif it.get("sale_price") and it["sale_price"] >= pid[it["product"]]["price"]:
                    ctx.err("%s.items[%d].sale_price" % (path, j), "the flash sale price must be lower than the normal price %s" % pid[it["product"]]["price"])
                if it.get("sold") is not None and not norm["demo"]:
                    ctx.err("%s.items[%d].sold" % (path, j), "sold counts are only allowed on a demo shop")
            if len(sec.get("items") or []) < 4:
                ctx.err(path + ".items", "a flash sale rail needs 4 or more products")
        if t == "banners" and not 2 <= len(sec.get("items") or []) <= 4:
            ctx.err(path + ".items", "give 2-4 banners")
        for b in [x for x in (sec.get("items") or []) + ([sec] if sec.get("bg") else []) if isinstance(x, dict)] if t not in ("hero", "banners") else []:
            if b.get("bg") and re.fullmatch(r"#[0-9a-fA-F]{6}", b["bg"]):
                b["ink"] = "#ffffff" if contrast(b["bg"], "#ffffff") >= 4.5 else "#14171c"
                if contrast(b["bg"], b["ink"]) < 4.5:
                    ctx.err(path + ".bg", "the background %s is a middle tone: neither white nor dark text reaches contrast 4.5" % b["bg"])
        if t in ("hero", "banners"):
            for j, b in enumerate((sec.get("slides") or []) + (sec.get("side") or []) + (sec.get("items") or [] if t == "banners" else [])):
                if not b.get("title"):
                    ctx.err("%s banner %d" % (path, j), "every banner needs a title")
                if b.get("bg") and not re.fullmatch(r"#[0-9a-fA-F]{6}", b["bg"]):
                    ctx.err("%s banner %d .bg" % (path, j), "use a 6-digit hex colour")
                elif b.get("bg"):
                    # text colour follows the background: white on dark, ink on light
                    if contrast(b["bg"], "#ffffff") >= 4.5:
                        b["ink"] = "#ffffff"
                    elif contrast(b["bg"], "#14171c") >= 4.5:
                        b["ink"] = "#14171c"
                    else:
                        ctx.err("%s banner %d .bg" % (path, j), "the background %s is a middle tone: neither white nor dark text reaches contrast 4.5. Use a darker or a lighter colour." % b["bg"])
                if not b.get("product") and not b.get("device"):
                    ctx.warn("%s banner %d" % (path, j), "no product or device, so the banner has no picture")
        def refs(node, p):
            if isinstance(node, dict):
                for k2, v2 in node.items():
                    if k2 == "product" and isinstance(v2, str) and v2 not in pid:
                        ctx.err(p + "." + k2, "unknown product id '%s'" % v2)
                    elif k2 == "category" and isinstance(v2, str) and v2 not in {c["id"] for c in norm["categories"]}:
                        ctx.err(p + "." + k2, "unknown category id '%s'. Use one of: %s" % (v2, ", ".join(c["id"] for c in norm["categories"])))
                    elif k2 == "products" and isinstance(v2, list):
                        for j2, x in enumerate(v2):
                            if isinstance(x, str) and x not in pid:
                                ctx.err("%s.products[%d]" % (p, j2), "unknown product id '%s'" % x)
                    else:
                        refs(v2, p + "." + k2)
            elif isinstance(node, list):
                for j2, x in enumerate(node):
                    refs(x, "%s[%d]" % (p, j2))
        if t not in ("rail", "grid", "hero", "flash-sale", "banners"):
            refs(sec, path)
        if t in ("rail", "grid"):
            if sec.get("category") and sec["category"] not in {c["id"] for c in norm["categories"]}:
                ctx.err(path + ".category", "unknown category '%s'" % sec["category"])
            for j, x in enumerate(sec.get("products") or []):
                if x not in pid:
                    ctx.err("%s.products[%d]" % (path, j), "unknown product id '%s'" % x)
    # home order follows the layout of a real shop (data/blueprints); only the order is enforced, slots may be left out
    bps = BP.load_all()
    bp_id = shop.get("blueprint")
    usable = [k for k, b in bps.items() if BP.fits_style(b, style) and b["usable"]]
    if not bp_id:
        if not shop.get("sample_content"):
            ctx.err("blueprint", "choose the real shop whose homepage order this shop follows: python scripts/blueprints.py --style %s lists them (%s). Set \"blueprint\": \"<id>\" and order the home sections as it does." % (style, ", ".join(usable[:8])))
    elif bp_id not in bps:
        ctx.err("blueprint", "unknown blueprint '%s'. Use one of: %s" % (bp_id, ", ".join(usable)))
    elif not BP.fits_style(bps[bp_id], style) or not bps[bp_id]["usable"]:
        ctx.err("blueprint", "'%s' (%s) does not fit style %s. Use one of: %s" % (bp_id, bps[bp_id]["kind"], style, ", ".join(usable)))
    else:
        for e in BP.check(bps[bp_id], [x.get("type") for x in home]):
            ctx.err("home", e)
    for k in ("shipping", "payments", "policies", "benefits"):
        if not shop.get(k):
            ctx.err(k, "required for checkout and footer pages; copy the shape from examples/demo-electronics.shop.json")
    if not shop.get("stores"):
        ctx.warn("stores", "no stores: the store locator and pickup option are left out")
    for i, pr in enumerate(shop.get("promotions") or []):
        for k in ("code", "type", "value", "label"):
            need(ctx, pr, k, "promotions[%d]" % i, None)
        if pr.get("type") not in ("fixed", "percent", "shipping"):
            ctx.err("promotions[%d].type" % i, "use fixed (VND off), percent (with optional max) or shipping (free delivery)")
    for i, pm in enumerate(shop.get("payments") or []):
        if pm.get("id") == "bank" and not (pm.get("bank") or {}).get("account"):
            ctx.warn("payments[%d].bank" % i, "bank transfer without account details; the order page shows a placeholder")
    if not norm["demo"]:
        ctx.warn("admin", "admin/ is a browser-only preview with the password demo and no security; do not publish admin/ until references/going-live.md is done")
        for k in ("hotline", "email"):
            if re.search(r"\[|example\.com", str(norm["shop"].get(k, ""))):
                ctx.warn("shop." + k, "placeholder contact; replace before launch")
    if ctx.errors:
        return None

    # ---------------------------------------------------------------- output
    out = Path(out_dir)
    if out.exists():
        shutil.rmtree(out)
    (out / "assets" / "p").mkdir(parents=True)
    accent = preset.get("art_accent", tvars["--c-accent"])
    (out / "assets" / "p" / "favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="%s"/>'
        '<text x="32" y="44" font-family="Arial, sans-serif" font-size="34" font-weight="700" text-anchor="middle" fill="%s">%s</text></svg>'
        % (tvars["--c-btn"], tvars["--c-btn-fg"], html.escape(norm["shop"]["name"][:1])), encoding="utf-8")
    for p in norm["products"]:
        for n, g in enumerate(p["gallery"]):
            if g["art"]:
                name = "%s-%d.svg" % (p["id"], n)
                (out / "assets" / "p" / name).write_text(devices.device_svg(p["device"], g["hex"] or "#2b2f36", accent, p["id"]), encoding="utf-8")
                g["src"] = "assets/p/" + name
            else:
                srcf = src_dir / g["src"]
                if not srcf.exists():
                    ctx.err(p["id"], "image file not found: %s" % g["src"])
                    continue
                dst = out / "assets" / "p" / ("%s-%d%s" % (p["id"], n, srcf.suffix.lower()))
                shutil.copy(srcf, dst)
                g["src"] = "assets/p/" + dst.name
        p["image"] = p["gallery"][0]["src"]
        for v in p["variants"]:
            gi = next((k for k, g in enumerate(p["gallery"]) if g["color"] == v["color"]), 0)
            v["image"] = p["gallery"][gi]["src"]
    for sec in home:
        # every item that names a device gets drawn art; items that name a product use its picture
        for sl in (sec.get("slides") or []) + (sec.get("side") or []) + [x for x in (sec.get("items") or []) if isinstance(x, dict)] + ([sec] if sec.get("device") or sec.get("product") else []):
            if sl.get("device") and not sl.get("product"):
                name = "banner-%s.svg" % hashlib.md5(json.dumps(sl, ensure_ascii=False).encode()).hexdigest()[:8]
                (out / "assets" / "p" / name).write_text(devices.device_svg(sl["device"], sl.get("device_color", "#2b2f36"), accent, name), encoding="utf-8")
                sl["art"] = "assets/p/" + name
            elif sl.get("product"):
                sl["art"] = pid[sl["product"]]["image"]
    if ctx.errors:
        return None

    for d in ("css", "js"):
        shutil.copytree(TPL / "assets" / d, out / "assets" / d)
    # storefront css: base, then the css of each chosen variant, then the style's own tokens and type
    parts = [(TPL / "assets/css/store.css").read_text(encoding="utf-8")]
    for k, val in layout.items():
        vf = TPL / "assets/css/v" / ("%s-%s.css" % (k, val))
        if vf.exists():
            parts.append("/* %s %s */\n" % (k, val) + vf.read_text(encoding="utf-8"))
    for sec in home:
        if sec.get("type") == "hero" and sec.get("variant") and sec["variant"] != layout["hero"]:
            hv = TPL / "assets/css/v" / ("hero-%s.css" % sec["variant"])
            if hv.exists() and ("/* hero %s */" % sec["variant"]) not in "".join(parts):
                parts.append("/* hero %s */\n" % sec["variant"] + hv.read_text(encoding="utf-8"))
    used = sorted({(sec.get("type"), sec.get("variant") or "") for sec in home})
    for typ, var in used:
        for name in ([typ, "%s-%s" % (typ, var)] if var else [typ]):
            sf = TPL / "assets/css/v" / ("section-%s.css" % name)
            if sf.exists() and ("/* section %s */" % name) not in "".join(parts):
                parts.append("/* section %s */\n" % name + sf.read_text(encoding="utf-8"))
    stf = TPL / "assets/css/styles" / (style + ".css")
    if stf.exists():
        parts.append("/* style %s */\n" % style + stf.read_text(encoding="utf-8"))
    for d in ("v", "styles"):
        shutil.rmtree(out / "assets" / "css" / d, ignore_errors=True)
    (out / "assets/css/store.css").write_text(":root{%s}\n" % ";".join("%s:%s" % kv for kv in tvars.items()) + "\n".join(parts), encoding="utf-8")
    fp = out / "assets/css/admin.css"
    fp.write_text(":root{%s}\n" % ";".join("%s:%s" % kv for kv in admin_vars.items()) + fp.read_text(encoding="utf-8"), encoding="utf-8")
    # extra behaviour: one js per chosen variant or section (assets/js/v/<part>-<name>.js) plus the style's own js
    js_parts = []
    for k, val in layout.items():
        jf = TPL / "assets/js/v" / ("%s-%s.js" % (k, val))
        if jf.exists():
            js_parts.append(jf.read_text(encoding="utf-8"))
    seen_js = set()
    for sec in home:
        if sec.get("type") == "hero" and sec.get("variant") and sec["variant"] != layout["hero"]:
            hj = TPL / "assets/js/v" / ("hero-%s.js" % sec["variant"])
            if hj.exists() and ("hero-" + sec["variant"]) not in seen_js:
                seen_js.add("hero-" + sec["variant"])
                js_parts.append(hj.read_text(encoding="utf-8"))
    for typ, var in used:
        for name in ([typ, "%s-%s" % (typ, var)] if var else [typ]):
            jf = TPL / "assets/js/v" / ("section-%s.js" % name)
            if jf.exists() and name not in seen_js:
                seen_js.add(name)
                js_parts.append(jf.read_text(encoding="utf-8"))
    sj = TPL / "assets/js/styles" / (style + ".js")
    if sj.exists():
        js_parts.append(sj.read_text(encoding="utf-8"))
    for d in ("styles", "v"):
        shutil.rmtree(out / "assets" / "js" / d, ignore_errors=True)
    if js_parts:
        (out / "assets/js/style.js").write_text("\n".join(js_parts), encoding="utf-8")

    seeded = seed_data(shop, norm, rng) if norm["demo"] else {"v": 2, "days": 0, "customers": [], "orders": [], "traffic": [], "store_stock": {}, "demo": False}
    # client-side catalogue (works from file://, no fetch)
    catalog = {
        "shop": {k: norm["shop"].get(k) for k in ("name", "slug", "tagline", "hotline", "email", "address", "hours")},
        "demo": norm["demo"],
        "categories": [{k: c.get(k) for k in ("id", "name", "icon", "facets", "price_ranges", "count")} for c in norm["categories"]],
        "brands": norm["brands"],
        "products": [{
            "id": p["id"], "name": p["name"], "brand": p["brand"], "brand_name": p["brand_name"], "category": p["category"],
            "category_name": p["category_name"], "price": p["price"], "old_price": p["old_price"], "discount": p["discount"],
            "image": p["image"], "variants": p["variants"], "options": [{"name": o["name"], "values": o["values"], "color": o["color"]} for o in p["options"]],
            "facets": p["facets"], "card_specs": p["card_specs"], "rating": p.get("rating"), "badges": p["badges"],
            "specs": p["specs"], "installment": bool(p.get("installment")), "warranty": p.get("warranty", ""),
            "keywords": p.get("keywords", ""), "sold": p.get("sold"), "released": p.get("released", ""),
        } for p in norm["products"]],
        "promotions": shop.get("promotions") or [], "shipping": shop.get("shipping") or [], "payments": shop.get("payments") or [],
        "stores": shop.get("stores") or [], "provinces": PROVINCES, "statuses": ORDER_STATUSES,
        "store_stock": seeded["store_stock"],
        "staff": shop.get("staff") or [],
        "flash": {it["product"]: {"sale_price": it.get("sale_price"), "limit": it.get("limit")}
                  for sec in home if sec.get("type") in ("flash-sale", "deal-of-day")
                  for it in (sec.get("items") or ([{"product": sec.get("product"), "sale_price": sec.get("sale_price")}] if sec.get("product") else []))
                  if it.get("product") in pid},
    }
    js = out / "assets" / "js"
    (js / "catalog.js").write_text("window.SHOP=" + json.dumps(catalog, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    (js / "seed.js").write_text("window.SEED=" + json.dumps(seeded, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(TPL)), autoescape=jinja2.select_autoescape(["html"]),
                             trim_blocks=True, lstrip_blocks=True, undefined=jinja2.Undefined)
    env.globals.update(icon=icon, arrow=Markup(ARROW_SVG), badges=BADGES, statuses=ORDER_STATUSES)
    env.filters["vnd"] = vnd
    env.filters["extract"] = lambda key, container: container[key]
    env.filters["stars"] = lambda r: Markup(stars_svg(r))

    cats = norm["categories"]
    by_cat = {c["id"]: [p for p in norm["products"] if p["category"] == c["id"]] for c in cats}
    fonts = STYLES[style].get("fonts_query") or preset.get("fonts_query", "family=Be+Vietnam+Pro:wght@400;500;600;700")
    base_ctx = dict(shop=norm["shop"], demo=norm["demo"], cats=cats, brands=norm["brands"], products=norm["products"],
                    pid=pid, by_cat=by_cat, payments=shop["payments"], shipping=shop["shipping"], policies=shop["policies"],
                    benefits=shop["benefits"], stores=shop.get("stores") or [], promotions=shop.get("promotions") or [],
                    announcement=shop.get("announcement") or [], fonts=fonts, lang=norm["lang"], preset=preset_name,
                    header_style=preset.get("header_style", "solid"), year=dt.date.today().year, style=style, layout=layout, search_ph=norm["shop"].get("search_placeholder") or "Bạn cần tìm gì?",
                    style_js=bool(js_parts), extra=shop.get("extra") or {}, socials=norm["shop"].get("socials") or [])
    pages = []

    def page(tpl, dest, **kw):
        depth = dest.count("/")
        c = dict(base_ctx, root="../" * depth, page_file=dest, **kw)
        try:
            text = env.get_template(tpl).render(**c)
        except jinja2.TemplateError as e:
            raise SystemExit("Template error in %s: %s" % (tpl, e))
        f = out / dest
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text, encoding="utf-8")
        pages.append(dest)

    card_tpl = env.from_string('{% import "partials/macros.html" as m with context %}{{ m.card(p) }}')
    cards = {p["id"]: card_tpl.render(**dict(base_ctx, root="__ROOT__", p=p)).strip() for p in norm["products"]}
    (js / "cards.js").write_text("window.CARDS=" + json.dumps(cards, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    flash = next((s for s in home if s.get("type") == "flash-sale"), None)
    page("pages/home.html", "index.html", sections=home, title=norm["shop"]["name"] + " | " + norm["shop"]["tagline"], body_class="pg-home")
    for c in cats:
        page("pages/category.html", "c/%s.html" % c["id"], cat=c, items=by_cat[c["id"]], title=c["name"] + " | " + norm["shop"]["name"], body_class="pg-cat")
    for p in norm["products"]:
        similar = [x for x in by_cat[p["category"]] if x["id"] != p["id"]][:10]
        page("pages/product.html", "p/%s.html" % p["id"], p=p, cat=next(c for c in cats if c["id"] == p["category"]), similar=similar,
             title="%s | %s" % (p["name"], norm["shop"]["name"]), body_class="pg-pdp")
    simple = [("search", "Tìm kiếm"), ("compare", "So sánh sản phẩm"), ("cart", "Giỏ hàng"), ("checkout", "Đặt hàng"),
              ("order", "Đặt hàng thành công"), ("track", "Tra cứu đơn hàng"), ("deals", "Khuyến mãi"), ("404", "Không tìm thấy trang")]
    if shop.get("stores"):
        simple.append(("stores", "Hệ thống cửa hàng"))
    for name, t in simple:
        page("pages/%s.html" % name, "%s.html" % name, title="%s | %s" % (t, norm["shop"]["name"]), body_class="pg-" + name, flash=flash)
    for pol in shop["policies"]:
        page("pages/policy.html", "policy/%s.html" % pol["id"], pol=pol, title="%s | %s" % (pol["title"], norm["shop"]["name"]), body_class="pg-policy")
    for name, t in [("index", "Tài khoản"), ("login", "Đăng nhập"), ("orders", "Đơn hàng của tôi"), ("order", "Chi tiết đơn hàng"),
                    ("wishlist", "Sản phẩm yêu thích"), ("addresses", "Sổ địa chỉ")]:
        page("account/%s.html" % name, "account/%s.html" % name, title="%s | %s" % (t, norm["shop"]["name"]), body_class="pg-account", acc=name)
    admin_pages = [("index", "Tổng quan"), ("orders", "Đơn hàng"), ("order", "Chi tiết đơn hàng"), ("products", "Sản phẩm"),
                   ("product", "Sửa sản phẩm"), ("inventory", "Tồn kho"), ("customers", "Khách hàng"), ("customer", "Chi tiết khách hàng"),
                   ("promotions", "Khuyến mãi"), ("reports", "Báo cáo"), ("settings", "Cài đặt"), ("login", "Đăng nhập quản trị")]
    for name, t in admin_pages:
        if not (TPL / "admin" / ("%s.html" % name)).exists():
            continue
        page("admin/%s.html" % name, "admin/%s.html" % name, title="%s | Quản trị %s" % (t, norm["shop"]["name"]), body_class="adm adm-" + name, adm=name)

    report = {"pages": pages, "products": len(norm["products"]), "categories": len(cats), "preset": preset_name, "demo": norm["demo"], "style": style, "layout": layout,
              "seed_orders": len(seeded["orders"]), "warnings": ctx.warnings}
    (out / "build-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return report


def stars_svg(r):
    avg = (r or {}).get("avg", 0)
    out = ['<span class="stars" aria-label="%s trên 5 sao">' % str(avg).replace(".", ",")]
    for k in range(5):
        fill = max(0.0, min(1.0, avg - k))
        out.append('<svg viewBox="0 0 24 24" aria-hidden="true"><defs><linearGradient id="g%d%d"><stop offset="%d%%" stop-color="currentColor"/>'
                   '<stop offset="%d%%" stop-color="transparent"/></linearGradient></defs><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" '
                   'fill="currentColor" fill-opacity="%.2f" stroke="currentColor" stroke-width="1.5"/></svg>' % (k, int(avg * 10), fill * 100, fill * 100, fill if fill >= 0.99 else (0.5 if fill > 0.25 else 0)))
    out.append("</span>")
    return "".join(out)


def unsafe_out(shop_path, out):
    """The build wipes --out, so refuse folders that hold the input or files the build did not make."""
    shop_dir, out = shop_path.resolve().parent, out.resolve()
    if out == shop_dir or out in shop_dir.parents:
        return "%s holds shop.json and would be wiped; use a subfolder such as %s" % (out, shop_dir / "dist")
    if out.is_file():
        return "%s is a file, not a folder" % out
    if out.is_dir() and any(out.iterdir()) and not (out / "build-report.json").exists():
        return "%s has files this build did not make; pick an empty folder or a previous build" % out
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shop", nargs="?")
    ap.add_argument("--out")
    ap.add_argument("--list", action="store_true", help="print icon names, device kinds, presets and home section types")
    a = ap.parse_args()
    if a.list:
        print("icons:", ", ".join(sorted(ICONS)))
        print("devices:", ", ".join(devices.KINDS))
        print("presets:", ", ".join("%s (%s)" % (k, v.get("pick", "")) for k, v in PRESETS.items()))
        print("home sections:", ", ".join(HOME_TYPES))
        print("styles:", "; ".join("%s (%s)" % (k, v["pick"]) for k, v in STYLES.items()))
        for k, vs in VARIANTS.items():
            print("layout %s:" % k)
            for v in vs:
                print("   %s: %s" % (v, V.describe(V.part_file(k, v)) or ""))
        print("section variants:", "; ".join("%s: %s" % (t, ", ".join(V.section_variants(t))) for t in HOME_TYPES if V.section_variants(t)))
        print("badges:", ", ".join(BADGES))
        return
    if not a.shop or not a.out:
        ap.error("give shop.json and --out")
    problem = unsafe_out(Path(a.shop), Path(a.out))
    if problem:
        print("ERROR --out: " + problem)
        sys.exit(1)
    if not Path(a.shop).is_file():
        print("ERROR %s: file not found" % a.shop)
        sys.exit(1)
    ctx = Ctx()
    try:
        rep = build(a.shop, a.out, ctx)
    except json.JSONDecodeError as e:
        print("ERROR shop.json is not valid JSON: %s" % e)
        sys.exit(1)
    except UnicodeDecodeError:
        print("ERROR shop.json is not UTF-8 text. Save it as UTF-8 and run again.")
        sys.exit(1)
    except Exception as e:  # a value of the wrong type that validation did not catch
        import traceback
        where = traceback.extract_tb(e.__traceback__)[-1]
        print("ERROR build.py stopped on shop.json: %s: %s (%s line %d)." % (type(e).__name__, e, Path(where.filename).name, where.lineno))
        print("A value probably has the wrong type, such as text where a list, an object or a number is expected. "
              "Compare that part of shop.json with examples/demo-electronics.shop.json. If it matches, this is a library bug: quote this message to the user.")
        sys.exit(1)
    for w in ctx.warnings:
        print("WARN  " + w)
    for e in ctx.errors:
        print("ERROR " + e)
    if ctx.errors or rep is None:
        print("\nBUILD FAILED: %d error(s). Fix them in shop.json and run again." % len(ctx.errors))
        sys.exit(1)
    print("OK built %d pages, %d products, preset %s%s into %s" % (len(rep["pages"]), rep["products"], rep["preset"],
          ", demo data %d orders" % rep["seed_orders"] if rep["demo"] else "", a.out))


if __name__ == "__main__":
    main()
