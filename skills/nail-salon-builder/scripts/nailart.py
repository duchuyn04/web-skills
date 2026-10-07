"""Drawn nail art: a fan of five nail tips (shape, length, finish, colours) and polish bottles, as SVG.

Used wherever salon.json has no photo: gallery looks, service categories, the hero, packages. The drawings show
objects only (tips on a display, bottles), never hands or faces.

    art = {"shape": "almond", "length": "medium", "style": "french", "colors": ["#f3d9cf", "#ffffff"], "bg": "#f6efe9"}
    svg = tips(art, seed="look-1")
"""
import hashlib
import math
import random

SHAPES = ["square", "squoval", "oval", "almond", "coffin", "stiletto"]
LENGTHS = {"short": 1.2, "medium": 1.55, "long": 1.95}
STYLES = ["solid", "french", "ombre", "chrome", "cat-eye", "glitter", "dots", "floral", "marble", "stripes", "heart", "gem", "aura"]


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    ra, rb = _rgb(a), _rgb(b)
    return "#" + "".join("%02x" % round(x + (y - x) * t) for x, y in zip(ra, rb))


def _lum(h):
    r, g, b = (c / 255 for c in _rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def nail_path(shape, w, h):
    """Nail standing up: cuticle at the bottom (y = h), free edge at the top (y = 0), centred on x = 0."""
    hw = w / 2
    b = h * 0.86
    base = "M%.1f,%.1f Q0,%.1f %.1f,%.1f " % (-hw, b, h * 1.06, hw, b)
    if shape == "square":
        r = w * 0.08
        top = "L%.1f,%.1f Q%.1f,0 %.1f,0 L%.1f,0 Q%.1f,0 %.1f,%.1f Z" % (hw, r, hw, hw - r, -hw + r, -hw, -hw, r)
    elif shape == "squoval":
        r = w * 0.3
        top = "L%.1f,%.1f Q%.1f,0 %.1f,0 L%.1f,0 Q%.1f,0 %.1f,%.1f Z" % (hw, r, hw, hw - r, -hw + r, -hw, -hw, r)
    elif shape == "oval":
        top = "L%.1f,%.1f A%.1f,%.1f 0 0 0 %.1f,%.1f Z" % (hw, hw * 1.05, hw, hw * 1.05, -hw, hw * 1.05)
    elif shape == "coffin":
        top = "L%.1f,%.1f L%.1f,%.1f Q%.1f,0 %.1f,0 L%.1f,0 Q%.1f,0 %.1f,%.1f Z" % (
            hw, h * 0.42, w * 0.25, h * 0.03, w * 0.24, w * 0.2, -w * 0.2, -w * 0.24, -w * 0.25, h * 0.03)
    elif shape == "stiletto":
        top = "L%.1f,%.1f C%.1f,%.1f %.1f,%.1f 0,0 C%.1f,%.1f %.1f,%.1f %.1f,%.1f Z" % (
            hw, h * 0.5, hw, h * 0.28, w * 0.1, h * 0.12, -w * 0.1, h * 0.12, -hw, h * 0.28, -hw, h * 0.5)
    else:  # almond
        top = "L%.1f,%.1f C%.1f,%.1f %.1f,0 0,0 C%.1f,0 %.1f,%.1f %.1f,%.1f Z" % (
            hw, h * 0.45, hw, h * 0.14, w * 0.16, -w * 0.16, -hw, h * 0.14, -hw, h * 0.45)
    return base + top


def _flower(cx, cy, r, petal, centre):
    out = []
    for k in range(5):
        a = k * 2 * math.pi / 5 - math.pi / 2
        out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (cx + math.cos(a) * r, cy + math.sin(a) * r, r * 0.85, petal))
    out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (cx, cy, r * 0.7, centre))
    return "".join(out)


def _heart(cx, cy, s, color):
    return ('<path d="M%.1f,%.1f c%.1f,%.1f %.1f,%.1f %.1f,%.1f c%.1f,%.1f %.1f,%.1f %.1f,%.1f Z" fill="%s"/>'
            % (cx, cy + s * 0.9, -s * 1.4, -s * 0.9, -s * 0.9, -s * 2.1, 0, -s * 1.3, s * 0.9, s * -0.8, s * 1.4, s * 0.4, 0, s * 1.3, color))


def nail_fill(style, colors, w, h, uid, rng):
    """Defs and shapes that paint one nail; clipped to the nail by the caller."""
    c = list(colors) + ["#ffffff", "#d9a5b3", "#c9a227"]
    c0, c1, c2 = c[0], c[1], c[2]
    defs, body = [], []
    full = '<rect x="%.1f" y="-5" width="%.1f" height="%.1f" fill="%s"/>' % (-w, w * 2, h * 1.3, "%s")
    if style == "french":
        body.append(full % c0)
        body.append('<path d="M%.1f,%.1f Q0,%.1f %.1f,%.1f L%.1f,-5 L%.1f,-5 Z" fill="%s"/>' % (-w, h * 0.34, h * 0.12, w, h * 0.34, w, -w, c1))
    elif style == "ombre":
        defs.append('<linearGradient id="g%s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (uid, c1, c0))
        body.append(full % ("url(#g%s)" % uid))
    elif style == "chrome":
        defs.append('<linearGradient id="g%s" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="%s"/><stop offset=".35" stop-color="%s"/>'
                    '<stop offset=".55" stop-color="%s"/><stop offset=".8" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>'
                    % (uid, mix(c0, "#ffffff", .55), c0, mix(c0, "#000000", .35), mix(c0, "#ffffff", .7), c0))
        body.append(full % ("url(#g%s)" % uid))
    elif style == "cat-eye":
        defs.append('<linearGradient id="g%s" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="%s"/><stop offset=".42" stop-color="%s"/>'
                    '<stop offset=".5" stop-color="%s"/><stop offset=".58" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>'
                    % (uid, c0, c0, c1, c0, c0))
        body.append(full % ("url(#g%s)" % uid))
    elif style == "aura":
        defs.append('<radialGradient id="g%s" cx=".5" cy=".55" r=".6"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></radialGradient>' % (uid, c1, c0))
        body.append(full % ("url(#g%s)" % uid))
    else:
        body.append(full % c0)
    if style == "glitter":
        for _ in range(int(w * h / 90)):
            body.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" opacity="%.2f"/>' % (
                rng.uniform(-w / 2, w / 2), rng.uniform(0, h), rng.uniform(0.6, 1.8), rng.choice([c1, c2, "#ffffff"]), rng.uniform(.6, 1)))
    elif style == "dots":
        r = w * 0.075
        y, row = h * 0.12, 0
        while y < h * 0.9:
            x = -w / 2 + (r * 2.6 if row % 2 else r * 1.3)
            while x < w / 2:
                body.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (x, y, r, c1))
                x += r * 3.6
            y += r * 3
            row += 1
    elif style == "floral":
        body.append(_flower(w * 0.08, h * 0.38, w * 0.13, c1, c2))
        body.append(_flower(-w * 0.18, h * 0.66, w * 0.08, c1, c2))
    elif style == "marble":
        for k in range(3):
            x0 = rng.uniform(-w / 2, w / 2)
            d = "M%.1f,-2 C%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (x0, x0 + rng.uniform(-w, w) * .6, h * .3, x0 + rng.uniform(-w, w) * .6, h * .6, rng.uniform(-w / 2, w / 2), h)
            body.append('<path d="%s" stroke="%s" stroke-width="%.1f" fill="none" opacity=".8"/>' % (d, c1 if k % 2 == 0 else c2, 1.2 + k * 0.6))
    elif style == "stripes":
        for k in range(-3, 6):
            x = k * w * 0.32
            body.append('<path d="M%.1f,%.1f L%.1f,-5" stroke="%s" stroke-width="%.1f"/>' % (x - w * .5, h * 1.1, x + w * .5, c1, w * 0.09))
    elif style == "heart":
        body.append(_heart(0, h * 0.42, w * 0.16, c1))
    elif style == "gem":
        cy = h * 0.62
        body.append('<circle cx="0" cy="%.1f" r="%.1f" fill="%s"/>' % (cy, w * 0.14, c1))
        body.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#ffffff" opacity=".8"/>' % (-w * 0.04, cy - w * 0.04, w * 0.04))
        for dx in (-w * 0.26, w * 0.26):
            body.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (dx, cy + w * 0.05, w * 0.06, c2))
    return "".join(defs), "".join(body)


def _seed(s):
    return int(hashlib.md5(str(s).encode("utf-8")).hexdigest()[:8], 16)


def tips(art, seed="x", size=(400, 400), count=5, area=None, wmax=0.165, cx=0.5):
    """Five nail tips fanned out over a soft disc, like a display wheel at the salon desk.
    area = (top, bottom) in px keeps the fan inside that band (the hero leaves room for bottles)."""
    rng = random.Random(_seed(seed))
    W, H = size
    shape = art.get("shape", "almond")
    length = LENGTHS.get(art.get("length", "medium"), 1.55)
    style = art.get("style", "solid")
    colors = art.get("colors") or ["#e8b4b8", "#ffffff"]
    bg = art.get("bg") or mix(colors[0], "#ffffff", 0.82)
    disc = mix(bg, "#000000", 0.045) if _lum(bg) > 0.5 else mix(bg, "#ffffff", 0.07)
    y0, y1 = area or (0, H)
    w = min(W * wmax, (y1 - y0) * 0.78 / (length * 1.1 + 0.5))
    h = w * length
    radius = w * 3.6
    angles = [-30, -15, 0, 15, 30] if count == 5 else [-18, 0, 18]
    # fan around a pivot below the nails, then centre the whole fan in the band
    top_y = [-math.cos(math.radians(a)) * radius - h for a in angles]
    bot_y = [-math.cos(math.radians(a)) * radius + h * 0.06 for a in angles]
    pivot_y = (y0 + y1) / 2 - (min(top_y) + max(bot_y)) / 2
    pivot = (W * cx, pivot_y)
    defs, shapes = [], []
    for i, a in enumerate(angles):
        uid = "%x%d" % (_seed(seed) % 99999, i)
        r = math.radians(a)
        cx = pivot[0] + math.sin(r) * radius
        cy = pivot[1] - math.cos(r) * radius - h
        p = nail_path(shape, w, h)
        d, body = nail_fill(style, colors, w, h, uid, rng)
        defs.append('<clipPath id="c%s"><path d="%s"/></clipPath>%s' % (uid, p, d))
        shade = mix(colors[0], "#000000", 0.25)
        shapes.append(
            '<g transform="translate(%.1f %.1f) rotate(%d %.1f %.1f)">'
            '<path d="%s" fill="%s" opacity=".18" transform="translate(3 5)"/>'
            '<g clip-path="url(#c%s)">%s</g>'
            '<path d="%s" fill="none" stroke="%s" stroke-opacity=".25" stroke-width="1"/>'
            '<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f" stroke="#ffffff" stroke-opacity=".55" stroke-width="%.1f" stroke-linecap="round" fill="none"/>'
            '</g>' % (cx, cy, a, 0, h, p, shade, uid, body, p, shade,
                      -w * 0.26, h * 0.7, -w * 0.3, h * 0.35, -w * 0.12, h * 0.16, w * 0.07))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" role="img"><defs>%s</defs>'
            '<rect width="%d" height="%d" fill="%s"/><circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>%s</svg>'
            % (W, H, "".join(defs), W, H, bg, W * cx, (y0 + y1) / 2, min(W, y1 - y0) * 0.4, disc, "".join(shapes)))


def bottle(x, y, s, color, cap="#1d1b1f", uid="b"):
    """One polish bottle with its base at (x, y); s is the body width."""
    bw, bh = s, s * 1.05
    cw, ch = s * 0.42, s * 0.95
    body = mix(color, "#000000", 0.12)
    return (
        '<g>'
        '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#000" opacity=".12"/>'
        '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="%s"/>'
        '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="%s"/>'
        '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="#ffffff" opacity=".35"/>'
        '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="%s"/>'
        '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="#ffffff" opacity=".18"/>'
        '</g>' % (
            x, y, bw * 0.62, s * 0.08,
            x - bw / 2, y - bh, bw, bh, s * 0.18, body,
            x - bw / 2 + s * 0.06, y - bh + s * 0.06, bw - s * 0.12, bh - s * 0.12, s * 0.14, color,
            x - bw / 2 + s * 0.14, y - bh + s * 0.14, s * 0.1, bh * 0.6, s * 0.05,
            x - cw / 2, y - bh - ch + 2, cw, ch, s * 0.06, cap,
            x - cw / 2 + s * 0.05, y - bh - ch + 8, s * 0.06, ch * 0.7))


def still_life(colors, bg, seed="hero", size=(640, 520), art=None, cx=0.5):
    """Hero picture: a fan of tips with three bottles in front, all from the salon palette.
    cx moves the group sideways (0.68 for a wide hero whose text sits on the left)."""
    W, H = size
    rng = random.Random(_seed(seed))
    art = dict(art or {"shape": "almond", "length": "long", "style": "solid"})
    art.setdefault("colors", colors[:2])
    art["bg"] = bg
    unit = min(W, H * 1.23)
    fan = tips(art, seed, size=(W, H), area=(H * 0.02, H * 0.72), wmax=0.13 * unit / W, cx=cx)
    inner = fan.split("</defs>", 1)
    head, rest = inner[0] + "</defs>", inner[1].rsplit("</svg>", 1)[0]
    caps = ["#1d1b1f", mix(colors[0], "#000000", 0.55), "#c9a227"]
    x0 = W * cx
    bs = [bottle(x0 - unit * 0.3, H * 0.97, unit * 0.13, colors[0], caps[0]),
          bottle(x0 + unit * 0.32, H * 0.97, unit * 0.11, colors[1 % len(colors)], caps[rng.randrange(3)]),
          bottle(x0 + unit * 0.18, H * 0.99, unit * 0.09, colors[2 % len(colors)], caps[2])]
    return head + rest + "".join(bs) + "</svg>"


def swatch_row(colors, size=(400, 120)):
    """Colour chips for a palette or a colour card."""
    W, H = size
    n = len(colors)
    gap = 10
    cw = (W - gap * (n + 1)) / max(n, 1)
    chips = "".join('<rect x="%.1f" y="%d" width="%.1f" height="%d" rx="12" fill="%s"/>' % (gap + i * (cw + gap), gap, cw, H - 2 * gap, c) for i, c in enumerate(colors))
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d">%s</svg>' % (W, H, chips)


DEFAULT_CATEGORY_ART = {
    "manicure": {"shape": "squoval", "length": "short", "style": "solid"},
    "pedicure": {"shape": "square", "length": "short", "style": "solid"},
    "gel": {"shape": "almond", "length": "medium", "style": "solid"},
    "extension": {"shape": "coffin", "length": "long", "style": "ombre"},
    "art": {"shape": "almond", "length": "medium", "style": "floral"},
    "care": {"shape": "oval", "length": "short", "style": "french"},
    "removal": {"shape": "oval", "length": "short", "style": "solid"},
    "combo": {"shape": "almond", "length": "medium", "style": "chrome"},
}
