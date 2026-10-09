"""Build a nail salon website (public pages, online booking, admin) from one salon.json.

    python scripts/build.py sites/<slug>/salon.json --out sites/<slug>/dist
    python scripts/build.py --list            styles, presets, home sections, icons, nail art options

The model writes only salon.json. This script validates it, checks facts against the brief, draws nail art for
anything without a photo, seeds demo history for the admin and renders every page from templates/. Errors name
the JSON path and the fix; the build fails until there are none.
"""
import argparse
import datetime as dt
import hashlib
import json
import random
import re
import shutil
import sys
import unicodedata
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
EXAMPLE = SKILL / "examples" / "demo-nail.salon.json"
sys.path.insert(0, str(HERE))
import rules  # noqa: E402
import nailart  # noqa: E402

PRESETS = json.loads((DATA / "presets.json").read_text(encoding="utf-8"))
STYLES = json.loads((DATA / "styles.json").read_text(encoding="utf-8"))
ICONS = json.loads((DATA / "icons.json").read_text(encoding="utf-8"))
FONTS = json.loads((DATA / "fonts.json").read_text(encoding="utf-8"))
LIB = SKILL / "library"
PHOTOS = {p["id"]: p for p in json.loads((LIB / "photos.json").read_text(encoding="utf-8"))["photos"]} if (LIB / "photos.json").exists() else {}

TOP_KEYS = {"_note", "demo", "sample_content", "lang", "brief", "style", "layout", "salon", "theme", "announcement", "price_notes", "booking",
            "locations", "categories", "services", "addons", "art_levels", "technicians", "gallery", "packages", "membership",
            "gift_cards", "promotions", "reviews", "trust", "policies", "faq", "home", "staff"}
SECTION_TYPES = {
    "hero": "Opening block: title, text, booking and price buttons, nail art or a photo. Variants: split, stack, full, collage",
    "story": "A short paragraph about the salon (salon.intro or text) with up to three facts from the brief. Variants: plain, ink (words ink in with the scroll)",
    "categories": "Service categories as cards with art, short intro and the lowest price. Variants: grid, scroll (a row that moves sideways while the section is pinned), fan (three looks per card)",
    "popular": "Services marked popular (or ids in `services`) as cards with price, time and a book button. Variants: grid, marquee (drifting rows of names, the look pops on hover)",
    "price-list": "The full price list in tabs by category, with add-ons; `categories` limits which tabs. Variants: tabs, spy (one long list, the row being read shows its look in a sticky panel)",
    "gallery": "Recent looks with tag filters and 'Đặt mẫu này'; `limit`, `tags`. Variants: grid, canvas (a board of looks to drag), checker (looks and tinted tiles that turn over)",
    "art-levels": "Nail art priced by level (art_levels)",
    "trust": "Hygiene, products, warranty and timing promises (trust). Variants: grid, drop (cards drop onto a pile while the section is pinned)",
    "team": "Technicians with title, specialties and branch",
    "reviews": "Rating summary and quotes (demo, or text given word for word in the brief)",
    "offers": "Packages, membership and gift cards side by side",
    "locations": "Branches with address, hours, parking, phone, map and book buttons",
    "faq": "Questions and answers",
    "cta": "Closing band with the booking button, hotline and Zalo",
}
HERO_VARIANTS = ["split", "stack", "full", "collage"]
# Motion variants of the other home sections (references/patterns.md, Motion); the first value is the plain layout.
SECTION_VARIANTS = {"categories": ["grid", "scroll", "fan"], "popular": ["grid", "marquee"], "price-list": ["tabs", "spy"],
                    "gallery": ["grid", "canvas", "checker"], "trust": ["grid", "drop"], "story": ["plain", "ink"]}
FOOTER_VARIANTS = ["plain", "matrix"]
# The LED dot panel in the footer is a brand flourish: only when the brief asks for it.
MATRIX_RE = re.compile(r"dot[- ]?matrix|led|pixel|ma trận (chấm|điểm)|bảng (đèn )?led|chấm (led|sáng)|đèn led|"
                       r"(logo|chữ|tên tiệm|tên thương hiệu) (thật |rất )?(lớn|to|cỡ lớn)|wordmark|large (logo|brand name)", re.I)
NAME_STOP = {"nail", "nails", "art", "salon", "studio", "spa", "bar", "tiệm", "tiem", "house", "room", "the", "&", "và"}
HEADER_VARIANTS = ["classic", "centered"]
CARD_VARIANTS = ["line", "soft"]
DAY_NAMES = {1: "Thứ 2", 2: "Thứ 3", 3: "Thứ 4", 4: "Thứ 5", 5: "Thứ 6", 6: "Thứ 7", 7: "Chủ nhật"}
STATUSES = [["pending", "Chờ xác nhận"], ["confirmed", "Đã xác nhận"], ["arrived", "Đang làm"], ["done", "Hoàn thành"],
            ["cancelled", "Đã hủy"], ["no_show", "Không đến"]]
SOURCES = [["web", "Website"], ["zalo", "Zalo"], ["phone", "Điện thoại"], ["walkin", "Khách vãng lai"], ["facebook", "Facebook"]]
PAYMENTS = [["cash", "Tiền mặt"], ["transfer", "Chuyển khoản"], ["card", "Thẻ"]]
PAGES = {
    "index.html": "Trang chủ", "bang-gia.html": "Bảng giá", "mau-nail.html": "Mẫu nail", "dat-lich.html": "Đặt lịch",
    "lich-hen.html": "Tra cứu lịch hẹn", "chi-nhanh.html": "Chi nhánh", "doi-ngu.html": "Thợ của tiệm",
    "uu-dai.html": "Ưu đãi và thẻ quà", "hoi-dap.html": "Hỏi đáp", "404.html": "Không tìm thấy trang",
}
ADMIN_PAGES = ["login", "index", "calendar", "appointments", "appointment", "customers", "customer", "services", "staff", "reports", "settings"]


# --------------------------------------------------------------------------- errors
class Ctx:
    def __init__(self):
        self.errors, self.warnings = [], []

    def err(self, path, msg):
        self.errors.append("%s: %s" % (path, msg))

    def warn(self, path, msg):
        self.warnings.append("%s: %s" % (path, msg))


def slugify(s):
    s = str(s).lower()
    table = str.maketrans("àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ",
                          "aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd")
    return re.sub(r"[^a-z0-9]+", "-", s.translate(table)).strip("-")


def vnd(n):
    if n is None:
        return ""
    return "{:,}".format(int(round(n))).replace(",", ".") + " đ"


def price_text(price, ptype="fixed", pmax=None):
    if price is None:
        return "Báo giá khi tư vấn"
    if pmax:
        return "%s - %s" % (vnd(price)[:-2], vnd(pmax))
    if ptype == "from":
        return "từ " + vnd(price)
    return vnd(price)


def usd_text(v):
    if v is None:
        return ""
    return "$%s" % ("%g" % v)


def minutes_text(m):
    m = int(m or 0)
    if m < 60:
        return "%d phút" % m
    h, r = divmod(m, 60)
    return "%d giờ" % h + (" %d phút" % r if r else "")


def days_label(days):
    """[1,2,3,4,5] -> 'Thứ 2 đến Thứ 6'; [6,7] -> 'Thứ 7, Chủ nhật'; [1,3] -> 'Thứ 2, Thứ 4'."""
    days = sorted(days)
    if len(days) >= 3 and days == list(range(days[0], days[-1] + 1)):
        return "%s đến %s" % (DAY_NAMES[days[0]], DAY_NAMES[days[-1]])
    return ", ".join(DAY_NAMES[d] for d in days)


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


def readable(color, bg, target=4.5):
    """Move a colour toward black (light background) or white (dark background) until it reaches the target."""
    c, to = color, ("#000000" if _lum(bg) > 0.18 else "#ffffff")
    for _ in range(40):
        if contrast(c, bg) >= target:
            return c
        c = mix(c, to, 0.06)
    return c


FALLBACK = {"Serif": "Georgia, serif", "Handwriting": "cursive", "Display": "system-ui, sans-serif"}


def check_font(ctx, name, role, path):
    """A family from data/fonts.json (checked for Vietnamese marks); explains why others are refused."""
    if name in FONTS["no_vietnamese"]:
        ctx.err(path, "%s has no Vietnamese letters on Google Fonts: words with marks would mix two typefaces. Pick one from build.py --list (fonts)" % name)
        return False
    if name in FONTS["avoid"]:
        ctx.err(path, "%s: %s with Vietnamese. Pick another from build.py --list (fonts)" % (name, FONTS["avoid"][name]))
        return False
    f = FONTS["fonts"].get(name)
    if not f:
        ctx.err(path, "%s has not been checked for Vietnamese marks. Pick one from build.py --list (fonts) or add it to data/fonts.json after testing" % name)
        return False
    if role not in f["roles"]:
        ctx.err(path, "%s is not listed for %s text; it fits: %s" % (name, role, ", ".join(f["roles"])))
        return False
    return True


def font_stack(name):
    cat = FONTS["fonts"].get(name, {}).get("category", "Sans Serif")
    return "'%s', %s" % (name, FALLBACK.get(cat, "system-ui, sans-serif"))


def fonts_query(spec):
    """{family: wanted weights} -> css2 query using only weights the family has (a missing weight silently drops the family)."""
    parts = []
    for fam, want in spec.items():
        have = FONTS["fonts"][fam]["weights"]
        ws = sorted({w for w in want if w in have}) or [min(have, key=lambda x: abs(x - 400))]
        parts.append("family=%s:wght@%s" % (fam.replace(" ", "+"), ";".join(map(str, ws))))
    return "&".join(parts)


def theme_vars(theme, style, ctx):
    name = theme.get("preset") or STYLES[style]["preset"]
    if name not in PRESETS:
        ctx.err("theme.preset", "unknown preset '%s'. Use one of: %s" % (name, ", ".join(PRESETS)))
        name = STYLES[style]["preset"]
    p = dict(PRESETS[name])
    head = theme.get("font_head") or p["head_font"]
    body = theme.get("font_body") or p["body_font"]
    accent_font = theme.get("font_accent")
    ok = check_font(ctx, head, "head", "theme.font_head") & check_font(ctx, body, "body", "theme.font_body")
    if accent_font:
        ok &= check_font(ctx, accent_font, "accent", "theme.font_accent")
    if not ok:
        head, body, accent_font = p["head_font"], p["body_font"], None
    hw = int(theme.get("head_weight") or p["head_weight"])
    if hw not in FONTS["fonts"][head]["weights"]:
        hw = min(FONTS["fonts"][head]["weights"], key=lambda x: abs(x - hw))
    want = {body: {400, 500, 600, 700}}
    want.setdefault(head, set()).update({hw, 700})
    if accent_font:
        want.setdefault(accent_font, set()).add(400)
    p["fonts"] = fonts_query(want)
    head_lh = max(1.15, FONTS["fonts"][head]["lh_mixed"])
    p["accent_font"] = accent_font
    if theme.get("accent"):
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", theme["accent"]):
            ctx.err("theme.accent", "use a 6-digit hex colour such as #a8606f")
        else:
            p["accent"] = theme["accent"].lower()
    bg, surface, text = p["bg"], p["surface"], p["text"]
    dark = _lum(surface) < 0.18
    accent = p["accent"]
    if dark:
        btn = accent if contrast(accent, "#ffffff") >= 4.5 else readable(accent, "#ffffff", 4.5)
    else:
        btn = readable(accent, "#ffffff", 4.5)
    soft = mix(accent, surface, 0.84) if dark else mix(accent, "#ffffff", 0.88)
    v = {
        "--c-bg": bg, "--c-surface": surface, "--c-surface-2": p["surface_2"], "--c-text": text,
        "--c-muted": readable(p["muted"], p["surface_2"], 4.5), "--c-border": p["border"],
        "--c-accent": accent, "--c-accent-text": readable(accent, bg, 4.5), "--c-btn": btn, "--c-btn-fg": "#ffffff",
        "--c-btn-hover": mix(btn, "#000000", 0.14), "--c-soft": soft, "--c-soft-ink": readable(accent, soft, 4.5),
        "--c-accent-2": p.get("accent_2", soft), "--c-dark": p["dark"], "--c-dark-fg": "#ffffff",
        "--c-ok": "#3ccf7e" if dark else "#0f7a3d", "--c-bad": "#ff7a6b" if dark else "#b42318",
        "--radius": p["radius"], "--radius-lg": p["radius_lg"], "--font": font_stack(body), "--font-head": font_stack(head),
        "--font-accent": font_stack(accent_font) if accent_font else font_stack(head),
        "--head-weight": str(hw), "--head-lh": "%.2f" % head_lh, "--head-scale": p["head_scale"],
    }
    admin = {"--c-accent": accent, "--c-btn": readable(accent, "#ffffff", 4.5), "--c-btn-hover": mix(readable(accent, "#ffffff", 4.5), "#000000", 0.14),
             "--c-soft": mix(accent, "#ffffff", 0.88), "--c-soft-ink": readable(accent, mix(accent, "#ffffff", 0.88), 4.5),
             "--c-link": readable(accent, "#ffffff", 4.5)}
    return v, p, name, admin, dark


# --------------------------------------------------------------------------- copy checks
SKIP_KEYS = {"brief", "_note", "id", "href", "url", "map", "image", "icon", "layout", "style", "variant", "type", "art",
             "category", "service", "services", "locations", "addons", "code", "period", "price_type", "mode", "external_url",
             "zalo", "messenger", "socials", "preset", "accent", "level", "email", "source", "tags"}


def walk_strings(node, path=""):
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, dict):
        for k, v in node.items():
            if k in SKIP_KEYS:
                continue
            yield from walk_strings(v, "%s.%s" % (path, k) if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_strings(v, "%s[%d]" % (path, i))


def check_copy(ctx, salon):
    for path, text in walk_strings(salon):
        if path.startswith("reviews.quotes"):
            continue  # customer words are kept as given
        for f in rules.check_text(text):
            (ctx.err if f.level == "error" else ctx.warn)(path, "%s (%s)" % (f.message, f.excerpt))
        m = re.search(r"\b\d+\.\d+\s?(?:cm|mm|giờ|tuần|tháng|triệu|tr)\b", text)
        if m:
            ctx.err(path, "write the decimal with a comma in Vietnamese: '%s' should be '%s'" % (m.group(), m.group().replace(".", ",", 1)))


# --------------------------------------------------------------------------- facts against the brief
# Text fields that state facts or promises about the salon; each figure and promise in them must be in the brief.
FACT_PATH = re.compile(r"^(announcement|price_notes|salon\.(intro|tagline)|booking\.note|services\[\d+\]\.(includes|note)|addons|art_levels\[\d+\]\.text"
                       r"|packages|membership|gift_cards|promotions|trust|policies|faq\[\d+\]\.a|technicians\[\d+\]\.(title|specialties)"
                       r"|home\[\d+\]\.(text|items))")
CLAIMS = ["miễn phí", "bảo hành", "thuần chay", "vegan", "không hema", "hema", "hữu cơ", "organic", "tiệt trùng", "hấp", "chính hãng",
          "bà bầu", "cam kết", "tặng", "rẻ nhất", "tốt nhất", "số 1", "hàng đầu", "đầu tiên", "uy tín nhất", "nhập khẩu", "dùng một lần",
          "hoàn tiền", "làm lại", "đặt cọc", "cọc"]


def _digits(text):
    out = []
    for t in re.findall(r"[A-Za-z]*\d[\w.,]*", text):
        t = t.strip(".,").lower()
        if t:
            out.append(t)
    return out


def _norm_num(t):
    t = t.lower().replace(",", ".")
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", t):
        t = t.replace(".", "")
    return t


def brief_amounts(brief):
    """Money amounts written in a brief in the forms Vietnamese owners use: 150k, 150.000, 150.000đ, 150 nghìn, 1tr2, 1,5 triệu."""
    out = set()
    low = brief.lower()
    for m in re.finditer(r"(\d+(?:[.,]\d+)*)\s*(k|nghìn|ngàn|n\b|tr|triệu|củ|đ|vnd|vnđ|d\b)?\s*(\d{1,3})?", low):
        num, unit, tail = m.group(1), m.group(2) or "", m.group(3)
        if re.fullmatch(r"\d{1,3}([.,]\d{3})+", num):
            base = float(re.sub(r"[.,]", "", num))
        else:
            base = float(num.replace(",", "."))
        if unit in ("k", "nghìn", "ngàn", "n"):
            out.add(int(round(base * 1000)))
        elif unit in ("tr", "triệu", "củ"):
            v = base * 1_000_000
            if tail:  # 1tr2 = 1.200.000, 1 triệu 500 = 1.500.000
                v += int(tail) * (100_000 if len(tail) == 1 else 1000 if len(tail) == 3 else 10_000)
            out.add(int(round(v)))
        else:
            out.add(int(round(base)))
            if base < 10000:
                out.add(int(round(base * 1000)))  # "giá 150" in a price list usually means 150.000
    return out


def brief_usd(brief):
    """Dollar amounts in a brief: $5, 5$, 5 USD, US$ 5, 12.5 usd."""
    out = set()
    for m in re.finditer(r"(?:us\$|\$)\s?(\d+(?:[.,]\d+)?)|(\d+(?:[.,]\d+)?)\s?(?:\$|usd)", brief.lower()):
        out.add(float((m.group(1) or m.group(2)).replace(",", ".")))
    return out


def check_facts(ctx, salon, example_strings):
    brief = salon.get("brief", "")
    bnorm = brief.lower()
    bnums = {_norm_num(t) for t in _digits(brief)}
    for t in list(bnums):
        bnums.update(re.findall(r"\d+(?:\.\d+)?", t))
    amounts = brief_amounts(brief)
    for path, text in walk_strings(salon):
        if not FACT_PATH.search(path):
            continue
        low = text.lower()
        if len(text.split()) >= 6 and text.strip() in example_strings and low.strip() not in bnorm:
            ctx.err(path, "'%s' is copied from the example salon, whose facts are made up. Use the client's facts from the brief, or leave it out." % text[:80])
            continue
        missing = []
        for t in _digits(text):
            n = _norm_num(t)
            parts = re.findall(r"\d+(?:\.\d+)?", n)
            if n in bnums or all(p in bnums for p in parts):
                continue
            missing.append(t)
        if missing:
            ctx.err(path, "'%s' has figures that are not in the brief (%s). Prices, times, warranty days and offers must come from the brief; drop the detail or ask the client. A salon the user asked you to invent sets \"sample_content\": true." % (text[:90], ", ".join(missing[:5])))
        for c in CLAIMS:
            rx = r"(?<!\w)" + re.escape(c) + r"(?!\w)"
            if re.search(rx, low) and not re.search(rx, bnorm):
                ctx.err(path, "'%s' promises \"%s\", which the brief does not. Remove the promise or ask the client." % (text[:90], c))
    # prices are numbers in salon.json; each must be written somewhere in the brief
    def money(path, v):
        if isinstance(v, (int, float)) and v and int(v) not in amounts:
            ctx.err(path, "%s is not a price in the brief. Copy prices from the client's price list; write 'price': null for 'báo giá khi tư vấn'." % vnd(v))
    for i, s in enumerate(salon.get("services") or []):
        money("services[%d].price" % i, s.get("price"))
        money("services[%d].price_max" % i, s.get("price_max"))
    for key in ("addons", "art_levels", "packages", "membership"):
        for i, a in enumerate(salon.get(key) or []):
            money("%s[%d].price" % (key, i), a.get("price"))
            money("%s[%d].old_price" % (key, i), a.get("old_price"))
    for i, a in enumerate((salon.get("gift_cards") or {}).get("amounts") or []):
        money("gift_cards.amounts[%d]" % i, a)
    usd = brief_usd(brief)
    for key in ("services", "addons", "art_levels"):
        for i, a in enumerate(salon.get(key) or []):
            v = a.get("price_usd")
            if isinstance(v, (int, float)) and float(v) not in usd:
                ctx.err("%s[%d].price_usd" % (key, i), "$%s is not in the brief. Show a dollar price only when the owner's menu gives it" % ("%g" % v))


# --------------------------------------------------------------------------- normalise
def need(ctx, obj, key, path, kind=str, msg=""):
    v = obj.get(key) if isinstance(obj, dict) else None
    full = "%s.%s" % (path, key) if path else key
    if v is None or v == "" or v == []:
        ctx.err(full, "required. " + msg)
        return None
    if kind and not isinstance(v, kind):
        ctx.err(full, "must be %s" % getattr(kind, "__name__", kind))
        return None
    return v


def known(ctx, obj, keys, path):
    for k in obj:
        if k not in keys:
            ctx.err("%s.%s" % (path, k) if path else k, "unknown key. Allowed here: %s" % ", ".join(sorted(keys)))


def check_id(ctx, v, path, seen):
    if not isinstance(v, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,40}", v or ""):
        ctx.err(path, "ids are lowercase letters, digits and dashes, such as 'son-gel'")
    elif v in seen:
        ctx.err(path, "duplicate id '%s'" % v)
    seen.add(v)


def check_price(ctx, v, path, allow_none=False):
    if v is None and allow_none:
        return
    if not isinstance(v, int) or v < 0:
        ctx.err(path, "a price is a whole number of đồng, such as 150000")
    elif 0 < v < 1000:
        ctx.err(path, "%d looks like thousands; write the full amount (%d000)" % (v, v))


def check_image(ctx, ref, path, base_dir, own_work=False, demo=False):
    """A photo next to salon.json, or "lib:<id>" from the skill's photo library (stock photos with a licence).
    own_work: the picture claims to show the salon's own work (gallery), so stock photos are allowed on a demo only."""
    if not ref:
        return
    if str(ref).startswith("lib:"):
        if ref[4:] not in PHOTOS:
            ctx.err(path, "unknown library photo '%s'. List them with build.py --photos" % ref)
        elif own_work and not demo:
            ctx.err(path, "a library photo is a stock picture, not this salon's work. Gallery items on a real salon use the owner's photos or drawn art")
    elif not (base_dir / ref).exists():
        ctx.err(path, "file not found next to salon.json: %s" % ref)


def check_art(ctx, art, path):
    if art is None:
        return
    if not isinstance(art, dict):
        ctx.err(path, "art is an object such as {\"shape\": \"almond\", \"style\": \"french\", \"colors\": [\"#f3d9cf\", \"#ffffff\"]}")
        return
    known(ctx, art, {"shape", "length", "style", "colors", "bg"}, path)
    if art.get("shape", "almond") not in nailart.SHAPES:
        ctx.err(path + ".shape", "use one of: " + ", ".join(nailart.SHAPES))
    if art.get("length", "medium") not in nailart.LENGTHS:
        ctx.err(path + ".length", "use one of: " + ", ".join(nailart.LENGTHS))
    if art.get("style", "solid") not in nailart.STYLES:
        ctx.err(path + ".style", "use one of: " + ", ".join(nailart.STYLES))
    for i, c in enumerate(art.get("colors") or []):
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", str(c)):
            ctx.err("%s.colors[%d]" % (path, i), "use 6-digit hex colours")


def normalise(salon, ctx, base_dir):
    known(ctx, salon, TOP_KEYS, "")
    demo = bool(salon.get("demo"))
    out = {"demo": demo, "sample": bool(salon.get("sample_content"))}
    if not isinstance(salon.get("brief"), str) or not salon.get("brief").strip():
        ctx.err("brief", "put the client's brief here as given (their messages, price list, addresses); the build checks facts against it")
    style = salon.get("style", "warm-luxury")
    if style not in STYLES:
        ctx.err("style", "use one of: " + ", ".join(STYLES))
        style = "warm-luxury"
    out["style"] = style
    lay = dict(STYLES[style])
    lay["footer"] = "plain"
    for k, v in (salon.get("layout") or {}).items():
        allowed = {"header": HEADER_VARIANTS, "hero": HERO_VARIANTS, "card": CARD_VARIANTS, "footer": FOOTER_VARIANTS}.get(k)
        if not allowed:
            ctx.err("layout." + k, "layout parts are header, hero, card and footer")
        elif v not in allowed:
            ctx.err("layout." + k, "use one of: " + ", ".join(allowed))
        else:
            lay[k] = v
    if lay["footer"] == "matrix" and not MATRIX_RE.search(salon.get("brief") or ""):
        ctx.err("layout.footer", "the dot-matrix footer (the salon's initials on a moving LED dot panel) is on, but the brief does not ask for it. "
                "Owners read it as a decoration they did not order; use \"plain\" unless the brief asks for an LED or dot-matrix panel or a large logo.")
    out["layout"] = lay

    # salon
    s = salon.get("salon") or {}
    known(ctx, s, {"name", "tagline", "intro", "hotline", "zalo", "messenger", "whatsapp", "kakao", "line", "email", "socials", "legal", "logo", "founded"}, "salon")
    for k in ("whatsapp",):
        if s.get(k) and not re.fullmatch(r"\+?\d[\d ]{7,16}", str(s[k])):
            ctx.err("salon." + k, "the WhatsApp number with country code, such as +84 900 000 000")
    for k in ("kakao", "line"):
        if s.get(k) and not str(s[k]).startswith("https://"):
            ctx.err("salon." + k, "the salon's %s link (https://...), from the owner" % {"kakao": "KakaoTalk open chat", "line": "LINE"}[k])
    name = need(ctx, s, "name", "salon") or "Salon"
    need(ctx, s, "hotline", "salon", msg="Use \"[Hotline]\" until the client gives it.")
    info = dict(s)
    info["slug"] = slugify(name) or "salon"
    # initials for the dot-matrix footer: the words of the name that are not the trade ("Mây Nail Studio" -> "M")
    words = [w for w in re.split(r"[\s&,.]+", unicodedata.normalize("NFC", str(name))) if w and w.lower() not in NAME_STOP]
    info["mark"] = "".join(w[0] for w in words[:2]).upper() or str(name)[:1].upper()
    for k in ("hotline", "zalo", "email"):
        if str(info.get(k, "")).startswith("["):
            ctx.warn("salon." + k, "placeholder left in the site: %s" % info[k])
    for k, v in (info.get("socials") or {}).items():
        if k not in ("facebook", "instagram", "tiktok", "youtube"):
            ctx.err("salon.socials." + k, "use facebook, instagram, tiktok or youtube")
    if info.get("logo") and not (base_dir / info["logo"]).exists():
        ctx.err("salon.logo", "file not found next to salon.json: %s" % info["logo"])
    out["salon"] = info

    # booking
    b = dict(salon.get("booking") or {})
    known(ctx, b, {"mode", "external_url", "send_to", "slot_minutes", "lead_minutes", "days_ahead", "choose_technician", "photo_upload",
                   "cancel_hours", "deposit", "note"}, "booking")
    b.setdefault("mode", "native")
    if b["mode"] not in ("native", "external", "chat"):
        ctx.err("booking.mode", "use native (booking form on the site), external (a booking platform link) or chat (Zalo, Messenger, hotline)")
    if b["mode"] == "external" and not b.get("external_url"):
        ctx.err("booking.external_url", "required with mode external: the salon's Fresha, Vagaro, Square or other booking link")
    if b["mode"] == "chat" and not (info.get("zalo") or info.get("messenger")):
        ctx.err("booking.mode", "chat booking needs salon.zalo or salon.messenger")
    if b.get("send_to") is None:
        b["send_to"] = "zalo" if info.get("zalo") else "whatsapp" if info.get("whatsapp") else "messenger" if info.get("messenger") else None
    elif b["send_to"] not in ("zalo", "whatsapp", "messenger", "none"):
        ctx.err("booking.send_to", "use zalo, whatsapp, messenger or none: the chat the confirmation screen offers for sending the booking")
    elif b["send_to"] != "none" and not info.get(b["send_to"]):
        ctx.err("booking.send_to", "needs salon.%s" % b["send_to"])
    if b.get("send_to") == "none":
        b["send_to"] = None
    b.setdefault("slot_minutes", 15)
    if b["slot_minutes"] not in (10, 15, 20, 30):
        ctx.err("booking.slot_minutes", "use 10, 15, 20 or 30")
    b.setdefault("lead_minutes", 60)
    b.setdefault("days_ahead", 21)
    if not isinstance(b["days_ahead"], int) or not 1 <= b["days_ahead"] <= 90:
        ctx.err("booking.days_ahead", "a whole number of days from 1 to 90")
    b.setdefault("choose_technician", True)
    b.setdefault("photo_upload", True)
    b.setdefault("cancel_hours", 4)
    dep = b.get("deposit")
    if dep is not None:
        if not isinstance(dep, dict) or not (dep.get("percent") or dep.get("amount")):
            ctx.err("booking.deposit", "{\"percent\": 30} or {\"amount\": 100000}, optionally with \"over\": 500000 for bookings above that total")
    out["booking"] = b

    # locations
    locs = []
    seen = set()
    for i, l in enumerate(salon.get("locations") or []):
        p = "locations[%d]" % i
        known(ctx, l, {"id", "name", "address", "phone", "hours", "parking", "map", "booking_url", "note", "last_order"}, p)
        check_id(ctx, l.get("id"), p + ".id", seen)
        need(ctx, l, "name", p)
        need(ctx, l, "address", p, msg="Use \"[Địa chỉ]\" until the client gives it.")
        if str(l.get("address", "")).startswith("["):
            ctx.warn(p + ".address", "placeholder left in the site")
        rows, covered = [], set()
        for j, h in enumerate(l.get("hours") or []):
            hp = "%s.hours[%d]" % (p, j)
            days = h.get("days")
            if not isinstance(days, list) or not days or not all(isinstance(d, int) and 1 <= d <= 7 for d in days):
                ctx.err(hp + ".days", "a list of weekdays 1 to 7 (1 = Thứ 2, 7 = Chủ nhật), such as [1, 2, 3, 4, 5]")
                continue
            if covered & set(days):
                ctx.err(hp + ".days", "a day appears in two rows")
            covered |= set(days)
            for k in ("open", "close"):
                if not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", str(h.get(k, ""))):
                    ctx.err("%s.%s" % (hp, k), "time as HH:MM, such as 09:00")
            if h.get("open", "") >= h.get("close", ""):
                ctx.err(hp, "close must be after open")
            rows.append({"days": sorted(days), "label": days_label(days), "open": h.get("open"), "close": h.get("close")})
        if not rows:
            ctx.err(p + ".hours", "required: [{\"days\": [1, 2, 3, 4, 5, 6, 7], \"open\": \"09:00\", \"close\": \"21:00\"}]")
        closed = [DAY_NAMES[d] for d in range(1, 8) if d not in covered]
        lo = l.get("last_order")
        if lo is not None:
            if not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", str(lo)):
                ctx.err(p + ".last_order", "time as HH:MM: the last time a new customer is taken, such as 20:30")
            elif rows and lo >= max(r["close"] for r in rows):
                ctx.err(p + ".last_order", "must be before closing time")
        locs.append(dict(l, hours=rows, closed=", ".join(closed)))
    if not locs:
        ctx.err("locations", "at least one branch with id, name, address and hours")
    out["locations"] = locs
    loc_ids = {l.get("id") for l in locs}

    # categories, services, add-ons
    cats, seen = [], set()
    for i, c in enumerate(salon.get("categories") or []):
        p = "categories[%d]" % i
        known(ctx, c, {"id", "name", "name_en", "intro", "art", "image"}, p)
        check_id(ctx, c.get("id"), p + ".id", seen)
        need(ctx, c, "name", p)
        check_art(ctx, c.get("art"), p + ".art")
        check_image(ctx, c.get("image"), p + ".image", base_dir)
        cats.append(dict(c))
    if not cats:
        ctx.err("categories", "at least one service category")
    cat_ids = {c.get("id") for c in cats}
    addons, seen_a = [], set()
    for i, a in enumerate(salon.get("addons") or []):
        p = "addons[%d]" % i
        known(ctx, a, {"id", "name", "name_en", "price", "price_usd", "per_nail", "minutes"}, p)
        check_id(ctx, a.get("id"), p + ".id", seen_a)
        need(ctx, a, "name", p)
        check_price(ctx, a.get("price"), p + ".price")
        addons.append(dict(a, minutes=int(a.get("minutes") or 0), per_nail=bool(a.get("per_nail"))))
    techs, seen_t = [], set()
    for i, t in enumerate(salon.get("technicians") or []):
        p = "technicians[%d]" % i
        known(ctx, t, {"id", "name", "title", "specialties", "locations", "level", "image", "off_days"}, p)
        check_id(ctx, t.get("id"), p + ".id", seen_t)
        need(ctx, t, "name", p)
        tl = t.get("locations") or sorted(loc_ids)
        for j, lid in enumerate(tl):
            if lid not in loc_ids:
                ctx.err("%s.locations[%d]" % (p, j), "unknown branch id '%s'" % lid)
        if t.get("level") and t["level"] not in ("junior", "senior", "master"):
            ctx.err(p + ".level", "use junior, senior or master")
        if str(t.get("image", "")).startswith("lib:"):
            ctx.err(p + ".image", "technician pictures are the owner's photos only; leave image out to show the initial")
        else:
            check_image(ctx, t.get("image"), p + ".image", base_dir)
        techs.append(dict(t, locations=tl, specialties=t.get("specialties") or [], off_days=t.get("off_days") or []))
    tech_ids = {t["id"] for t in techs}
    services, seen_s = [], set()
    for i, sv in enumerate(salon.get("services") or []):
        p = "services[%d]" % i
        known(ctx, sv, {"id", "category", "name", "name_en", "minutes", "price", "price_usd", "price_type", "price_max", "includes", "note", "popular",
                        "addons", "technicians", "hidden", "image"}, p)
        check_id(ctx, sv.get("id"), p + ".id", seen_s)
        need(ctx, sv, "name", p)
        if sv.get("category") not in cat_ids:
            ctx.err(p + ".category", "unknown category '%s'. Use one of: %s" % (sv.get("category"), ", ".join(sorted(cat_ids))))
        if not isinstance(sv.get("minutes"), int) or not 5 <= sv["minutes"] <= 480:
            ctx.err(p + ".minutes", "the time the service takes, in minutes (5 to 480); booking slots are planned from it")
        check_price(ctx, sv.get("price"), p + ".price", allow_none=True)
        if sv.get("price_type", "fixed") not in ("fixed", "from"):
            ctx.err(p + ".price_type", "use fixed or from")
        if sv.get("price_max") is not None:
            check_price(ctx, sv["price_max"], p + ".price_max")
            if isinstance(sv.get("price"), int) and isinstance(sv["price_max"], int) and sv["price_max"] <= sv["price"]:
                ctx.err(p + ".price_max", "must be above price")
        for j, aid in enumerate(sv.get("addons") or []):
            if aid not in seen_a:
                ctx.err("%s.addons[%d]" % (p, j), "unknown add-on '%s'" % aid)
        for j, tid in enumerate(sv.get("technicians") or []):
            if tid not in tech_ids:
                ctx.err("%s.technicians[%d]" % (p, j), "unknown technician '%s'" % tid)
        services.append(dict(sv, price_type=sv.get("price_type", "fixed"), includes=sv.get("includes") or [],
                             addons=sv.get("addons") if sv.get("addons") is not None else [a["id"] for a in addons],
                             technicians=sv.get("technicians") or []))
    if not services:
        ctx.err("services", "at least one service with id, category, name, minutes and price")
    for c in cats:
        cs = [s for s in services if s.get("category") == c.get("id") and not s.get("hidden")]
        if not cs:
            ctx.warn("categories", "category '%s' has no services and is left out of the menu" % c.get("id"))
        prices = [s["price"] for s in cs if isinstance(s.get("price"), int)]
        c["min_price"] = min(prices) if prices else None
        c["count"] = len(cs)
    out["categories"] = [c for c in cats if c["count"]]
    out["services"] = services
    out["addons"] = addons
    out["technicians"] = techs

    levels = []
    for i, a in enumerate(salon.get("art_levels") or []):
        p = "art_levels[%d]" % i
        known(ctx, a, {"name", "text", "price", "price_usd", "price_type", "price_max"}, p)
        need(ctx, a, "name", p)
        check_price(ctx, a.get("price"), p + ".price")
        levels.append(dict(a, price_type=a.get("price_type", "fixed")))
    out["art_levels"] = levels

    gallery, seen_g = [], set()
    svc_ids = {s.get("id") for s in services}
    for i, g in enumerate(salon.get("gallery") or []):
        p = "gallery[%d]" % i
        known(ctx, g, {"id", "title", "tags", "service", "art", "image"}, p)
        gid = g.get("id") or "look-%d" % (i + 1)
        check_id(ctx, gid, p + ".id", seen_g)
        need(ctx, g, "title", p)
        if g.get("service") and g["service"] not in svc_ids:
            ctx.err(p + ".service", "unknown service '%s'" % g["service"])
        if not g.get("art") and not g.get("image"):
            ctx.err(p, "give a photo in image (next to salon.json) or a drawn look in art")
        check_image(ctx, g.get("image"), p + ".image", base_dir, own_work=True, demo=demo)
        check_art(ctx, g.get("art"), p + ".art")
        gallery.append(dict(g, id=gid, tags=g.get("tags") or []))
    out["gallery"] = gallery
    out["tags"] = sorted({t for g in gallery for t in g["tags"]}, key=lambda t: -sum(t in g["tags"] for g in gallery))

    for key, keys in (("packages", {"name", "items", "price", "old_price", "note"}), ("membership", {"name", "price", "period", "perks", "note"})):
        rows = []
        for i, x in enumerate(salon.get(key) or []):
            p = "%s[%d]" % (key, i)
            known(ctx, x, keys, p)
            need(ctx, x, "name", p)
            check_price(ctx, x.get("price"), p + ".price")
            if x.get("old_price") is not None and isinstance(x.get("price"), int) and x["old_price"] <= x["price"]:
                ctx.err(p + ".old_price", "must be above price")
            rows.append(dict(x))
        out[key] = rows
    gc = salon.get("gift_cards") or {}
    known(ctx, gc, {"amounts", "note"}, "gift_cards")
    out["gift_cards"] = gc if gc.get("amounts") or gc.get("note") else None
    promos = []
    for i, x in enumerate(salon.get("promotions") or []):
        p = "promotions[%d]" % i
        known(ctx, x, {"title", "text", "code", "percent", "amount"}, p)
        need(ctx, x, "title", p)
        if x.get("code") and not re.fullmatch(r"[A-Z0-9]{3,16}", x["code"]):
            ctx.err(p + ".code", "codes are 3 to 16 capital letters or digits")
        promos.append(dict(x))
    out["promotions"] = promos

    r = salon.get("reviews")
    if r:
        known(ctx, r, {"rating", "count", "source", "quotes"}, "reviews")
        brief = (salon.get("brief") or "").lower()
        if not demo:
            for k in ("rating", "count"):
                if r.get(k) is not None and str(r[k]).replace(".", ",") not in brief and str(r[k]) not in brief:
                    ctx.err("reviews." + k, "%s is not in the brief. A real salon shows only the rating and count the owner gives (from Google or Facebook)." % r[k])
            for i, q in enumerate(r.get("quotes") or []):
                if q.get("text", "").lower().strip() not in brief:
                    ctx.err("reviews.quotes[%d].text" % i, "on a real salon, quotes are copied word for word from the brief")
    out["reviews"] = r or None
    out["trust"] = salon.get("trust") or []
    for i, t in enumerate(out["trust"]):
        known(ctx, t, {"icon", "title", "text"}, "trust[%d]" % i)
        if t.get("icon") and t["icon"] not in ICONS:
            ctx.err("trust[%d].icon" % i, "unknown icon. See build.py --list")
    pols, seen_p = [], set()
    for i, x in enumerate(salon.get("policies") or []):
        p = "policies[%d]" % i
        known(ctx, x, {"id", "title", "body"}, p)
        check_id(ctx, x.get("id"), p + ".id", seen_p)
        need(ctx, x, "title", p)
        if not isinstance(x.get("body"), list):
            ctx.err(p + ".body", "a list of paragraphs")
        pols.append(dict(x))
    out["policies"] = pols
    out["faq"] = salon.get("faq") or []
    out["announcement"] = salon.get("announcement")
    pn = salon.get("price_notes") or []
    if not isinstance(pn, list) or not all(isinstance(x, str) for x in pn):
        ctx.err("price_notes", "a list of short lines shown under the price list (warranty, free removal, surcharges), from the brief")
        pn = []
    out["price_notes"] = pn
    for key in ("services", "addons", "art_levels"):
        for i, a in enumerate(salon.get(key) or []):
            v = a.get("price_usd")
            if v is not None and (not isinstance(v, (int, float)) or v <= 0):
                ctx.err("%s[%d].price_usd" % (key, i), "a dollar amount such as 5 or 12.5")

    home = []
    for i, sec in enumerate(salon.get("home") or []):
        p = "home[%d]" % i
        t = sec.get("type")
        if t not in SECTION_TYPES:
            ctx.err(p + ".type", "unknown section. Use one of: " + ", ".join(SECTION_TYPES))
            continue
        known(ctx, sec, {"type", "title", "text", "variant", "art", "image", "limit", "tags", "services", "categories", "items"}, p)
        if t == "hero":
            check_art(ctx, sec.get("art"), p + ".art")
            if sec.get("variant") and sec["variant"] not in HERO_VARIANTS:
                ctx.err(p + ".variant", "use one of: " + ", ".join(HERO_VARIANTS))
            check_image(ctx, sec.get("image"), p + ".image", base_dir)
        elif sec.get("variant") is not None:
            allowed = SECTION_VARIANTS.get(t)
            if not allowed:
                ctx.err(p + ".variant", "section '%s' has one layout; remove variant. Sections with variants: %s" % (t, ", ".join(["hero"] + list(SECTION_VARIANTS))))
            elif sec["variant"] not in allowed:
                ctx.err(p + ".variant", "use one of: " + ", ".join(allowed))
            elif t == "popular" and sec["variant"] == "marquee":
                # with fewer names one row shows the same service twice on a wide screen
                n_names = len(sec.get("services") or [s for s in salon.get("services") or [] if s.get("popular") and not s.get("hidden")])
                if n_names < 6:
                    ctx.err(p + ".variant", "the marquee needs 6 or more services and has %d: list 6 to 12 ids in `services` or use the grid" % n_names)
        empty = {"art-levels": not levels, "team": not techs, "reviews": not r, "offers": not (out["packages"] or out["membership"] or out["gift_cards"]),
                 "faq": not out["faq"], "trust": not out["trust"], "gallery": not gallery}
        if empty.get(t):
            ctx.err(p, "section '%s' has no data: fill its list in salon.json or leave the section out" % t)
        home.append(dict(sec))
    if not home or home[0].get("type") != "hero":
        ctx.err("home", "the home page starts with a hero section")
    out["home"] = home
    out["staff"] = salon.get("staff") or [{"name": "Chủ tiệm", "role": "Chủ tiệm"}]
    return out


# --------------------------------------------------------------------------- demo history
FAMILY = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
MIDDLE = ["Thị", "Ngọc", "Thanh", "Thu", "Minh", "Bảo", "Khánh", "Hoài", "Phương", "Mai", "Gia", "Kim"]
GIVEN = ["An", "Anh", "Châu", "Diệp", "Dung", "Giang", "Hà", "Hạnh", "Hân", "Hằng", "Hương", "Lan", "Linh", "Loan", "Mai", "My", "Nga",
         "Ngân", "Nhi", "Nhung", "Oanh", "Phương", "Quyên", "Tâm", "Thảo", "Thư", "Trang", "Trâm", "Uyên", "Vân", "Vy", "Xuân", "Yến",
         "Quân", "Huy", "Khoa", "Long", "Nam"]
NOTES = ["Da tay nhạy cảm", "Thích form móng ngắn", "Hay đặt thợ cũ", "Dị ứng gel có HEMA", "Thích màu nude", "Đi cùng bạn", ""]


def seed_data(n, rng, anchor, past=400, future=14):
    """Demo appointments, days relative to the build date (admin.js shifts them by whole weeks to today).

    customers: [name, phone, first_day, note]
    appts:     [day, start_min, loc, tech, [service idx], [addon idx], total_k, status, source, customer, pay]
               status 0 done, 1 cancelled, 2 no show, 3 confirmed, 4 pending (today and later are resolved in admin.js)
    """
    services = [s for s in n["services"] if not s.get("hidden")]
    svc_idx = {s["id"]: i for i, s in enumerate(n["services"])}
    weights = [3 if s.get("popular") else 1 for s in services]
    techs = n["technicians"] or [{"id": "_", "locations": [l["id"] for l in n["locations"]], "off_days": []}]
    loc_idx = {l["id"]: i for i, l in enumerate(n["locations"])}
    customers, appts = [], []
    visits = []
    hours = {}
    for l in n["locations"]:
        for h in l["hours"]:
            for d in h["days"]:
                o = [int(x) for x in h["open"].split(":")]
                c = [int(x) for x in h["close"].split(":")]
                hours[(l["id"], d)] = (o[0] * 60 + o[1], c[0] * 60 + c[1])
    dow_w = {1: .72, 2: .76, 3: .8, 4: .86, 5: 1.0, 6: 1.32, 7: 1.24}

    def season(day):
        m, d = day.month, day.day
        f = 1.0
        if m == 12 or (m == 1) or (m == 2 and d < 10):
            f *= 1.3
        if (m, d) in ((2, 13), (2, 14), (3, 7), (3, 8), (10, 19), (10, 20), (11, 19), (11, 20)):
            f *= 1.5
        if m in (6, 7):
            f *= 0.92
        return f

    def new_customer(day_off):
        nm = "%s %s %s" % (rng.choice(FAMILY), rng.choice(MIDDLE), rng.choice(GIVEN))
        customers.append([nm, "0900%06d" % rng.randrange(10 ** 6), day_off, rng.choice(NOTES) if rng.random() < .25 else ""])
        visits.append(0)
        return len(customers) - 1

    addons = n["addons"]
    for off in range(-past, future + 1):
        day = anchor + dt.timedelta(days=off)
        dow = day.isoweekday()
        trend = 0.8 + 0.2 * (off + past) / (past + future)
        for t_i, t in enumerate(techs):
            if dow in t.get("off_days", []):
                continue
            for lid in t["locations"][:1]:
                if (lid, dow) not in hours:
                    continue
                o, c = hours[(lid, dow)]
                load = (0.35 + 0.35 * rng.random()) * dow_w[dow] * season(day) * trend
                if off > 0:
                    load *= max(0.15, 0.85 - off * 0.05)  # fewer bookings the further ahead
                cur = o + rng.choice([0, 15, 30])
                while cur < c - 30:
                    if rng.random() > load:
                        cur += rng.choice([15, 30, 45])
                        continue
                    picks = [rng.choices(services, weights)[0]]
                    if rng.random() < .18:
                        extra = rng.choices(services, weights)[0]
                        if extra is not picks[0]:
                            picks.append(extra)
                    mins = sum(s["minutes"] for s in picks)
                    ad = []
                    if addons and rng.random() < .3:
                        a = rng.randrange(len(addons))
                        if addons[a]["id"] in picks[0]["addons"]:
                            ad.append(a)
                            mins += addons[a]["minutes"]
                    if cur + mins > c:
                        break
                    total = sum((s.get("price") or 0) for s in picks)
                    total += sum(addons[a]["price"] * (rng.choice([2, 4, 10]) if addons[a]["per_nail"] else 1) for a in ad)
                    known_pool = [i for i, v in enumerate(visits) if v and customers[i][2] < off]
                    if known_pool and rng.random() < .62:
                        cust = rng.choice(known_pool[-400:])
                    else:
                        cust = new_customer(off)
                    visits[cust] += 1
                    if off < 0:
                        r = rng.random()
                        status = 1 if r < .06 else 2 if r < .085 else 0
                    else:
                        status = 4 if rng.random() < (.3 if off <= 1 else .1) else 3
                    src = rng.choices(range(len(SOURCES)), [30, 26, 14, 20, 10])[0]
                    pay = rng.choices(range(3), [44, 41, 15])[0]
                    appts.append([off, cur, loc_idx[lid], t_i, [svc_idx[s["id"]] for s in picks], ad, int(round(total / 1000)), status, src, cust, pay])
                    cur += mins + rng.choice([0, 0, 15, 15, 30])
                    cur = -(-cur // 15) * 15  # salons book on the quarter hour
    return {"anchor": anchor.isoformat(), "customers": customers, "appts": appts}


# --------------------------------------------------------------------------- other scripts in Vietnamese pages
# Korean, Japanese, Chinese and Thai words (bilingual menus for tourists) are wrapped in <span lang> so site.css can give
# each its own national font; one shared fallback list draws Japanese and Chinese with Korean glyphs.
FOREIGN = "\u0E00-\u0E7F\u1100-\u11FF\u3040-\u30FF\u3130-\u318F\u3400-\u4DBF\u4E00-\u9FFF\uAC00-\uD7AF\uFF01-\uFF5E\u3001-\u303F"
FOREIGN_RX = re.compile("[%s]+(?:[ \u00B7][%s]+)*" % (FOREIGN, FOREIGN))
LANG_FONT = {"ko": "Noto Sans KR", "ja": "Noto Sans JP", "zh": "Noto Sans SC", "zh-Hant": "Noto Sans TC", "th": "Noto Sans Thai"}


def lang_of(run, han):
    if re.search("[\u0E00-\u0E7F]", run):
        return "th"
    if re.search("[\u1100-\u11FF\u3130-\u318F\uAC00-\uD7AF]", run):
        return "ko"
    if re.search("[\u3040-\u30FF]", run):
        return "ja"
    return han


def wrap_foreign(html, han, used):
    """Wrap runs of foreign letters in page text (not in tags, scripts, styles, titles, options or textareas)."""
    head, mark, body = html.partition("<body")
    if not mark:
        return html
    parts = re.split(r"(<script.*?</script>|<style.*?</style>|<[^>]+>)", body, flags=re.S)
    skip = False
    for i, t in enumerate(parts):
        if t.startswith("<"):
            m = re.match(r"<(/?)(\w+)", t)
            if m and m.group(2).lower() in ("title", "option", "textarea"):
                skip = not m.group(1)
            continue
        if skip or not FOREIGN_RX.search(t):
            continue

        def rep(m):
            lg = lang_of(m.group(0), han)
            used.setdefault(lg, set()).update(m.group(0))
            return '<span lang="%s">%s</span>' % (lg, m.group(0))
        parts[i] = FOREIGN_RX.sub(rep, t)
    return head + mark + "".join(parts)


def lang_font_links(used):
    """One small css2 request per language with only the letters the site uses (&text=)."""
    from urllib.parse import quote
    out = []
    for lg, chars in sorted(used.items()):
        text = "".join(sorted(c for c in chars if not c.isspace()))
        out.append('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=%s:wght@400;700&amp;text=%s&amp;display=swap">'
                   % (LANG_FONT[lg].replace(" ", "+"), quote(text)))
    return chr(10).join(out)


# --------------------------------------------------------------------------- render helpers
def icon(name, cls=""):
    body = ICONS.get(name)
    if body is None:
        return Markup("")
    return Markup('<svg class="i %s" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
                  'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>' % (cls, body))


def write_art(out, n, preset, salon):
    """Draw every picture the site needs and return {key: relative path}."""
    art_dir = out / "assets" / "art"
    art_dir.mkdir(parents=True, exist_ok=True)
    pics = {}
    bg = preset["art_bg"]
    accent = preset["accent"]

    def put(key, svg):
        (art_dir / (key + ".svg")).write_text(svg, encoding="utf-8")
        pics[key] = "assets/art/%s.svg" % key

    def palette(art):
        a = dict(art)
        a.setdefault("colors", [accent, "#ffffff"])
        a.setdefault("bg", bg)
        return a

    for c in n["categories"]:
        if c.get("image"):
            pics["cat-" + c["id"]] = copy_media(out, salon["_dir"], c["image"])
        else:
            art = c.get("art") or dict(nailart.DEFAULT_CATEGORY_ART["gel"])
            put("cat-" + c["id"], nailart.tips(palette(art), seed=c["id"]))
    for g in n["gallery"]:
        if g.get("image"):
            pics["look-" + g["id"]] = copy_media(out, salon["_dir"], g["image"])
        else:
            put("look-" + g["id"], nailart.tips(palette(g["art"]), seed=g["id"]))
    # categories "fan": three looks per category card; categories with fewer looks get drawn ones in the category art
    if any(sec["type"] == "categories" and sec.get("variant") == "fan" for sec in n["home"]):
        svc_cat = {s["id"]: s["category"] for s in n["services"]}
        for c in n["categories"]:
            looks = ["look-" + g["id"] for g in n["gallery"] if svc_cat.get(g.get("service")) == c["id"]][:3]
            art = c.get("art") or dict(nailart.DEFAULT_CATEGORY_ART["gel"])
            if len(looks) < 3:
                looks.append("cat-" + c["id"])
            k = 0
            while len(looks) < 3:
                key = "fan-%s-%d" % (c["id"], k)
                put(key, nailart.tips(palette(art), seed=key, count=3 + k))
                looks.append(key)
                k += 1
            pics["fan-" + c["id"]] = [pics[x] for x in looks]
    for i, sec in enumerate(n["home"]):
        if sec["type"] == "hero":
            if sec.get("image"):
                pics["hero"] = copy_media(out, salon["_dir"], sec["image"])
            else:
                art = palette(sec.get("art") or {"shape": "almond", "length": "long", "style": "solid"})
                cols = art["colors"] + [mix(accent, "#ffffff", .6), mix(accent, "#000000", .3)]
                full = (sec.get("variant") or n["layout"]["hero"]) == "full"
                put("hero", nailart.still_life(cols[:3], art["bg"], seed="hero", art=art,
                                               size=(1440, 720) if full else (640, 520), cx=0.7 if full else 0.5))
                for k, g in enumerate(n["gallery"][:3]):
                    pics.setdefault("hero-%d" % k, pics.get("look-" + g["id"]))
    for t in n["technicians"]:
        if t.get("image"):
            pics["tech-" + t["id"]] = copy_media(out, salon["_dir"], t["image"])
    put("favicon", '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="%s"/>'
                   '<path d="M22,46 Q32,52 42,46 L42,26 C42,16 36,10 32,10 C28,10 22,16 22,26 Z" fill="#ffffff"/></svg>' % readable(accent, "#ffffff", 3))
    return pics


CREDITS = []


def copy_media(out, base_dir, rel):
    """Copy a photo into assets/media; library photos also go on the credits page."""
    dst_dir = out / "assets" / "media"
    dst_dir.mkdir(parents=True, exist_ok=True)
    if str(rel).startswith("lib:"):
        ph = PHOTOS[rel[4:]]
        name = "lib-" + Path(ph["file"]).name
        shutil.copyfile(LIB / "photos" / ph["file"], dst_dir / name)
        if ph["id"] not in {c["id"] for c in CREDITS}:
            CREDITS.append(dict(ph, src="assets/media/" + name))
        return "assets/media/" + name
    src = base_dir / rel
    shutil.copyfile(src, dst_dir / Path(rel).name)
    return "assets/media/" + Path(rel).name


def js_data(n):
    """What the browser needs: salon, branches, menu, technicians, booking rules, offers."""
    return {
        "salon": {k: n["salon"].get(k) for k in ("name", "slug", "hotline", "zalo", "messenger", "whatsapp", "email")},
        "demo": n["demo"],
        "booking": n["booking"],
        "locations": [{"id": l["id"], "name": l["name"], "address": l["address"], "phone": l.get("phone"),
                       "hours": [{"days": h["days"], "open": h["open"], "close": h["close"]} for h in l["hours"]], "last_order": l.get("last_order")} for l in n["locations"]],
        "categories": [{"id": c["id"], "name": c["name"]} for c in n["categories"]],
        "services": [{"id": s["id"], "category": s["category"], "name": s["name"], "name_en": s.get("name_en"), "minutes": s["minutes"], "price": s.get("price"), "price_usd": s.get("price_usd"),
                      "price_type": s["price_type"], "price_max": s.get("price_max"), "addons": s["addons"],
                      "technicians": s["technicians"], "hidden": bool(s.get("hidden")), "popular": bool(s.get("popular"))} for s in n["services"]],
        "addons": n["addons"],
        "technicians": [{"id": t["id"], "name": t["name"], "title": t.get("title", ""), "locations": t["locations"], "off_days": t["off_days"],
                         "level": t.get("level", "")} for t in n["technicians"]],
        "promotions": [p for p in n["promotions"] if p.get("code")],
        "gallery": [{"id": g["id"], "title": g["title"], "service": g.get("service")} for g in n["gallery"]],
        "statuses": STATUSES, "sources": SOURCES, "payments": PAYMENTS,
        "staff": n["staff"],
    }


def build(salon_path, out, ctx, today=None):
    salon_path = Path(salon_path).resolve()
    raw = json.loads(salon_path.read_text(encoding="utf-8"))
    raw["_dir"] = salon_path.parent
    data = {k: v for k, v in raw.items() if k != "_dir"}
    n = normalise(data, ctx, salon_path.parent)
    check_copy(ctx, data)
    if not n["sample"]:
        ex = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        example_strings = {t.strip() for _, t in walk_strings(ex)}
        check_facts(ctx, data, example_strings)
    if n["sample"] and not n["demo"]:
        ctx.err("sample_content", "invented content is only allowed on a demo site (\"demo\": true)")
    theme = data.get("theme") or {}
    known(ctx, theme, {"preset", "accent", "font_head", "font_body", "font_accent", "head_weight", "han"}, "theme")
    cssv, preset, preset_name, admin_vars, dark = theme_vars(theme, n["style"], ctx)
    if ctx.errors:
        return None

    out = Path(out).resolve()
    if out.exists():
        shutil.rmtree(out)
    (out / "assets" / "js").mkdir(parents=True)
    (out / "assets" / "css").mkdir(parents=True)
    for f in (TPL / "assets" / "css").glob("*.css"):
        shutil.copyfile(f, out / "assets" / "css" / f.name)
    for f in (TPL / "assets" / "js").glob("*.js"):
        shutil.copyfile(f, out / "assets" / "js" / f.name)
    CREDITS.clear()
    pics = write_art(out, n, preset, raw)
    n["credits"] = list(CREDITS)
    payload = js_data(n)
    (out / "assets" / "js" / "salon.js").write_text("window.SALON=" + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";", encoding="utf-8")
    today = today or dt.date.today()
    seed_rng = random.Random(int(hashlib.md5(n["salon"]["slug"].encode()).hexdigest()[:8], 16))
    seed = seed_data(n, seed_rng, today) if n["demo"] else {"anchor": today.isoformat(), "customers": [], "appts": []}
    (out / "assets" / "js" / "seed.js").write_text("window.SEED=" + json.dumps(seed, ensure_ascii=False, separators=(",", ":")) + ";", encoding="utf-8")
    # the booking pages only need the coming days to mark taken slots
    busy = {"anchor": seed["anchor"], "customers": [], "appts": [a + [i] for i, a in enumerate(seed["appts"]) if a[0] >= -7]}
    (out / "assets" / "js" / "seed-busy.js").write_text("window.SEED=" + json.dumps(busy, separators=(",", ":")) + ";", encoding="utf-8")

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(TPL)), autoescape=True, trim_blocks=True, lstrip_blocks=True)
    env.globals.update(icon=icon, vnd=vnd, price_text=price_text, minutes_text=minutes_text, usd_text=usd_text)
    env.tests["contains"] = lambda seq, x: x in (seq or [])
    svc_by_id = {s["id"]: s for s in n["services"]}
    cat_by_id = {c["id"]: c for c in n["categories"]}
    loc_by_id = {l["id"]: l for l in n["locations"]}
    popular = [s for s in n["services"] if s.get("popular") and not s.get("hidden")]
    common = dict(n=n, salon=n["salon"], demo=n["demo"], css_vars=cssv, admin_vars=admin_vars, preset=preset, dark=dark,
                  style=n["style"], layout=n["layout"], pics=pics, svc_by_id=svc_by_id, cat_by_id=cat_by_id, loc_by_id=loc_by_id,
                  popular=popular, fonts=preset["fonts"], pages=PAGES, year=today.year, booking=n["booking"],
                  menu=[s for s in n["services"] if not s.get("hidden")])
    skip = {"uu-dai.html": not (n["packages"] or n["membership"] or n["gift_cards"] or n["promotions"]),
            "doi-ngu.html": not n["technicians"], "mau-nail.html": not n["gallery"], "hoi-dap.html": not n["faq"]}
    n["pages_built"] = [rel for rel in PAGES if not skip.get(rel)] + (["nguon-anh.html"] if n["credits"] else [])
    pages = []

    used_scripts = {}
    han = theme.get("han", "zh")
    if han not in ("zh", "zh-Hant", "ja"):
        ctx.err("theme.han", "Chinese characters without kana are read as zh (simplified), zh-Hant or ja")
        han = "zh"

    def render(tpl, rel, **kw):
        depth = rel.count("/")
        html = env.get_template(tpl).render(root="../" * depth, page=rel, **common, **kw)
        if not rel.startswith("admin/"):
            html = wrap_foreign(html, han, used_scripts)
        (out / rel).parent.mkdir(parents=True, exist_ok=True)
        (out / rel).write_text(html, encoding="utf-8")
        pages.append(rel)

    for rel in n["pages_built"]:
        render("pages/" + rel, rel, title=PAGES.get(rel, "Nguồn ảnh"))
    for pol in n["policies"]:
        render("pages/policy.html", "chinh-sach/%s.html" % pol["id"], title=pol["title"], policy=pol)
    for a in ADMIN_PAGES:
        if not (TPL / "admin" / ("%s.html" % a)).exists():
            continue
        render("admin/%s.html" % a, "admin/%s.html" % a, title=a, adm=a)

    links = lang_font_links(used_scripts)
    for rel in pages:
        f = out / rel
        t = f.read_text(encoding="utf-8")
        if "<!--LANGFONTS-->" in t:
            f.write_text(t.replace("<!--LANGFONTS-->", links), encoding="utf-8")
    report = {"salon": n["salon"]["name"], "scripts": sorted(used_scripts), "style": n["style"], "preset": preset_name, "layout": n["layout"], "demo": n["demo"],
              "sample_content": n["sample"], "pages": pages, "services": len(n["services"]), "categories": len(n["categories"]),
              "technicians": len(n["technicians"]), "looks": len(n["gallery"]), "seed_appointments": len(seed["appts"]),
              "warnings": ctx.warnings}
    (out / "build-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return report


def print_list():
    print("Styles:")
    for k, v in STYLES.items():
        print("  %-12s %s (header %s, hero %s, card %s)" % (k, v["for"], v["header"], v["hero"], v["card"]))
    print("Presets:", ", ".join(PRESETS))
    print("Layout parts: header %s; hero %s; card %s" % (HEADER_VARIANTS, HERO_VARIANTS, CARD_VARIANTS))
    print("Home sections:")
    for k, v in SECTION_TYPES.items():
        print("  %-11s %s" % (k, v))
    print("Nail art: shape %s; length %s; style %s" % (nailart.SHAPES, list(nailart.LENGTHS), nailart.STYLES))
    print("Fonts checked for Vietnamese (theme.font_head, font_body, font_accent):")
    for role in ("head", "body", "accent"):
        print("  %-6s %s" % (role, ", ".join("%s (lh %.2f)" % (k, v["lh_mixed"]) if role == "head" else k for k, v in FONTS["fonts"].items() if role in v["roles"])))
    print("  no Vietnamese, refused:", ", ".join(FONTS["no_vietnamese"]))
    print("Icons:", ", ".join(sorted(ICONS)))


def unsafe_out(salon_path, out):
    sp, op = Path(salon_path).resolve(), Path(out).resolve()
    if op == sp.parent or op in sp.parents or op == SKILL or op in SKILL.parents:
        return True
    return any(op == SKILL / d or SKILL / d in op.parents for d in ("scripts", "templates", "data", "examples", "references"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("salon", nargs="?")
    ap.add_argument("--out")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--photos", nargs="?", const="", metavar="GROUP", help="list library photos, optionally one group (interior, polish, tools, nails, pedicure, spa)")
    ap.add_argument("--today", help="build date YYYY-MM-DD (demo history ends here); default today")
    a = ap.parse_args()
    if a.list:
        print_list()
        return
    if a.photos is not None:
        for ph in PHOTOS.values():
            if not a.photos or ph["group"] == a.photos:
                print("lib:%-28s %-9s %-9s %s" % (ph["id"], ph["group"], ph["orientation"], ", ".join(ph.get("tags", [])[:6])))
        return
    if not a.salon or not a.out:
        ap.error("usage: build.py sites/<slug>/salon.json --out sites/<slug>/dist")
    if unsafe_out(a.salon, a.out):
        raise SystemExit("--out must be a new folder such as sites/<slug>/dist, not the folder that holds salon.json or the skill itself: the build deletes it first.")
    ctx = Ctx()
    today = dt.date.fromisoformat(a.today) if a.today else None
    rep = build(a.salon, a.out, ctx, today)
    for w in ctx.warnings:
        print("WARN", w)
    if ctx.errors:
        for e in ctx.errors:
            print("ERROR", e)
        print("FAILED: %d errors" % len(ctx.errors))
        sys.exit(1)
    print("OK built %d pages for %s (%s, %s) into %s" % (len(rep["pages"]), rep["salon"], rep["style"], "demo" if rep["demo"] else "real", a.out))


if __name__ == "__main__":
    main()
