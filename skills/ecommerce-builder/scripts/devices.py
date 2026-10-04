"""Product art: one SVG per product colour, drawn from a device kind and a body colour.

Real shops show photos of each colour. A demo or a shop without photos still needs a clean, consistent
picture per variant, so build.py draws one here instead of using stock photos of other brands' products.
Every drawing uses a 400 x 400 canvas, a soft floor shadow and the body colour of the variant; screens show
an abstract wallpaper in the shop accent hue. Shading gradients are allowed inside product art only.
"""
import colorsys
import hashlib

KINDS = ["phone", "tablet", "laptop", "monitor", "tv", "watch", "headphones", "earbuds", "speaker", "camera",
         "gamepad", "keyboard", "mouse", "chair", "fridge", "washer", "aircon", "charger", "powerbank"]


def _rgb(hex_):
    h = hex_.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _hex(rgb):
    return "#" + "".join("%02x" % max(0, min(255, round(c * 255))) for c in rgb)


def shade(hex_, amount):
    """amount > 0 lightens, < 0 darkens (HLS lightness)."""
    h, l, s = colorsys.rgb_to_hls(*_rgb(hex_))
    l = max(0.0, min(1.0, l + amount))
    return _hex(colorsys.hls_to_rgb(h, l, s))


def _lum(hex_):
    r, g, b = _rgb(hex_)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _wall(accent, uid, x, y, w, h, rx=0):
    """Abstract screen wallpaper: two soft colour fields in the accent hue."""
    a1 = shade(accent, 0.18)
    a2 = shade(accent, -0.22)
    return (
        '<defs><linearGradient id="w%(u)s" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="%(a1)s"/><stop offset="1" stop-color="%(a2)s"/></linearGradient>'
        '<clipPath id="c%(u)s"><rect x="%(x)s" y="%(y)s" width="%(w)s" height="%(h)s" rx="%(rx)s"/></clipPath></defs>'
        '<rect x="%(x)s" y="%(y)s" width="%(w)s" height="%(h)s" rx="%(rx)s" fill="url(#w%(u)s)"/>'
        '<g clip-path="url(#c%(u)s)" opacity=".55">'
        '<circle cx="%(c1x)s" cy="%(c1y)s" r="%(r1)s" fill="#ffffff" opacity=".28"/>'
        '<circle cx="%(c2x)s" cy="%(c2y)s" r="%(r2)s" fill="%(a2)s" opacity=".8"/></g>'
    ) % dict(u=uid, a1=a1, a2=a2, x=x, y=y, w=w, h=h, rx=rx,
             c1x=x + w * 0.25, c1y=y + h * 0.3, r1=max(w, h) * 0.45,
             c2x=x + w * 0.85, c2y=y + h * 0.9, r2=max(w, h) * 0.5)


def _body(uid, color):
    """Vertical shading for a body colour."""
    return ('<linearGradient id="b%s" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="%s"/>'
            '<stop offset=".55" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>'
            % (uid, shade(color, 0.08), color, shade(color, -0.1)))


def _shadow(uid, cx, cy, rx, ry=14):
    return ('<filter id="s%s" x="-50%%" y="-200%%" width="200%%" height="500%%"><feGaussianBlur stdDeviation="8"/></filter>'
            '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#0b1220" opacity=".16" filter="url(#s%s)"/>'
            % (uid, cx, cy, rx, ry, uid))


def device_svg(kind, color="#2b2f36", accent="#d70018", seed=""):
    uid = hashlib.md5(("%s|%s|%s" % (kind, color, seed)).encode()).hexdigest()[:6]
    dark = shade(color, -0.18)
    edge = shade(color, -0.3) if _lum(color) > 0.35 else shade(color, 0.12)
    fn = globals().get("_draw_" + kind.replace("-", "_"))
    if not fn:
        raise ValueError("unknown device kind %r; use one of %s" % (kind, ", ".join(KINDS)))
    inner = fn(uid, color, dark, edge, accent)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">'
            '<defs>%s</defs>%s</svg>' % (_body(uid, color), inner))


# --------------------------------------------------------------------------- drawings
def _draw_phone(u, c, dark, edge, acc):
    back = (
        '<rect x="70" y="40" width="160" height="318" rx="32" fill="url(#b%(u)s)" stroke="%(e)s" stroke-width="2"/>'
        '<rect x="86" y="58" width="78" height="82" rx="22" fill="%(d)s" opacity=".9"/>'
        '<circle cx="108" cy="82" r="15" fill="#11151c" stroke="%(e)s" stroke-width="3"/><circle cx="108" cy="82" r="6" fill="#2c3644"/>'
        '<circle cx="108" cy="118" r="15" fill="#11151c" stroke="%(e)s" stroke-width="3"/><circle cx="108" cy="118" r="6" fill="#2c3644"/>'
        '<circle cx="143" cy="100" r="15" fill="#11151c" stroke="%(e)s" stroke-width="3"/><circle cx="143" cy="100" r="6" fill="#2c3644"/>'
        '<circle cx="146" cy="70" r="4" fill="#f4e7b5"/>'
    ) % dict(u=u, d=dark, e=edge)
    front = (
        '<rect x="168" y="56" width="160" height="314" rx="30" fill="#0e1116" stroke="%(e)s" stroke-width="3"/>'
        + _wall(acc, u, 177, 65, 142, 296, 23) +
        '<rect x="226" y="76" width="44" height="12" rx="6" fill="#05070a"/>'
    ) % dict(e=edge)
    return _shadow(u, 200, 372, 140) + back + front


def _draw_tablet(u, c, dark, edge, acc):
    return (_shadow(u, 200, 340, 165) +
            '<rect x="34" y="80" width="332" height="240" rx="24" fill="url(#b%s)" stroke="%s" stroke-width="2"/>' % (u, edge) +
            '<rect x="44" y="90" width="312" height="220" rx="16" fill="#0e1116"/>' +
            _wall(acc, u, 50, 96, 300, 208, 12) +
            '<rect x="300" y="60" width="72" height="9" rx="4.5" fill="%s" transform="rotate(-8 336 64)"/>' % shade(c, 0.1))


def _draw_laptop(u, c, dark, edge, acc):
    return (_shadow(u, 200, 312, 175, 12) +
            '<rect x="62" y="70" width="276" height="186" rx="12" fill="url(#b%s)" stroke="%s" stroke-width="2"/>' % (u, edge) +
            '<rect x="70" y="78" width="260" height="170" rx="6" fill="#0e1116"/>' +
            _wall(acc, u, 76, 84, 248, 158, 3) +
            '<path d="M40 258 H360 L372 286 Q373 296 362 296 H38 Q27 296 28 286 Z" fill="url(#b%s)" stroke="%s" stroke-width="2"/>' % (u, edge) +
            '<rect x="170" y="258" width="60" height="7" rx="3.5" fill="%s"/>' % dark)


def _draw_monitor(u, c, dark, edge, acc):
    return (_shadow(u, 200, 338, 110, 10) +
            '<rect x="30" y="56" width="340" height="206" rx="10" fill="#0e1116" stroke="%s" stroke-width="2"/>' % edge +
            _wall(acc, u, 38, 64, 324, 182, 4) +
            '<rect x="30" y="246" width="340" height="16" rx="0" fill="url(#b%s)"/>' % u +
            '<path d="M180 262 h40 l8 54 h-56 z" fill="url(#b%s)" stroke="%s" stroke-width="2"/>' % (u, edge) +
            '<rect x="120" y="314" width="160" height="14" rx="7" fill="url(#b%s)" stroke="%s" stroke-width="2"/>' % (u, edge))


def _draw_tv(u, c, dark, edge, acc):
    return (_shadow(u, 200, 322, 170, 10) +
            '<rect x="16" y="70" width="368" height="214" rx="6" fill="#0b0d12" stroke="%s" stroke-width="2"/>' % edge +
            _wall(acc, u, 22, 76, 356, 202, 2) +
            '<path d="M70 284 l-18 30 h14 l18 -30 z M330 284 l18 30 h-14 l-18 -30 z" fill="url(#b%s)"/>' % u)


def _draw_watch(u, c, dark, edge, acc):
    a = shade(acc, 0.1)
    return (_shadow(u, 200, 372, 70, 10) +
            '<path d="M150 30 h100 l-8 90 h-84 z" fill="url(#b%s)"/>' % u +
            '<path d="M158 280 h84 l8 86 h-100 z" fill="url(#b%s)"/>' % u +
            '<rect x="120" y="110" width="160" height="180" rx="44" fill="%s" stroke="%s" stroke-width="4"/>' % (dark, edge) +
            '<rect x="132" y="122" width="136" height="156" rx="34" fill="#05070a"/>' +
            '<circle cx="200" cy="200" r="48" fill="none" stroke="%s" stroke-width="10" stroke-dasharray="210 400" stroke-linecap="round" transform="rotate(-90 200 200)"/>' % a +
            '<circle cx="200" cy="200" r="32" fill="none" stroke="#7dd3fc" stroke-width="8" stroke-dasharray="120 300" stroke-linecap="round" transform="rotate(-90 200 200)"/>' +
            '<rect x="282" y="168" width="10" height="30" rx="4" fill="%s"/>' % edge)


def _draw_headphones(u, c, dark, edge, acc):
    return (_shadow(u, 200, 360, 130) +
            '<path d="M96 230 V170 a104 104 0 0 1 208 0 V230" fill="none" stroke="%s" stroke-width="22" stroke-linecap="round"/>' % dark +
            '<path d="M96 228 V170 a104 104 0 0 1 208 0 V228" fill="none" stroke="url(#b%s)" stroke-width="14" stroke-linecap="round"/>' % u +
            '<rect x="56" y="204" width="84" height="132" rx="40" fill="url(#b%s)" stroke="%s" stroke-width="2"/>' % (u, edge) +
            '<rect x="260" y="204" width="84" height="132" rx="40" fill="url(#b%s)" stroke="%s" stroke-width="2"/>' % (u, edge) +
            '<rect x="76" y="222" width="44" height="96" rx="22" fill="%s" opacity=".55"/>' % dark +
            '<rect x="280" y="222" width="44" height="96" rx="22" fill="%s" opacity=".55"/>' % dark)


def _draw_earbuds(u, c, dark, edge, acc):
    return (_shadow(u, 200, 352, 120) +
            '<rect x="100" y="150" width="200" height="180" rx="70" fill="url(#b%s)" stroke="%s" stroke-width="2"/>' % (u, edge) +
            '<path d="M104 216 H296" stroke="%s" stroke-width="2"/>' % edge +
            '<circle cx="200" cy="270" r="5" fill="#34d399"/>' +
            '<g transform="translate(118 64) rotate(-18)"><ellipse cx="30" cy="40" rx="30" ry="34" fill="url(#b%s)" stroke="%s" stroke-width="2"/><rect x="38" y="52" width="18" height="70" rx="9" fill="url(#b%s)" stroke="%s" stroke-width="2"/></g>' % (u, edge, u, edge) +
            '<g transform="translate(222 52) rotate(16)"><ellipse cx="30" cy="40" rx="30" ry="34" fill="url(#b%s)" stroke="%s" stroke-width="2"/><rect x="4" y="52" width="18" height="70" rx="9" fill="url(#b%s)" stroke="%s" stroke-width="2"/></g>' % (u, edge, u, edge))


def _draw_speaker(u, c, dark, edge, acc):
    dots = "".join('<circle cx="%d" cy="%d" r="3.2" fill="%s" opacity=".55"/>' % (x, y, dark)
                   for y in range(118, 330, 14) for x in range(142 + (7 if (y // 14) % 2 else 0), 262, 14))
    return (_shadow(u, 200, 360, 90) +
            '<rect x="124" y="70" width="152" height="282" rx="60" fill="url(#b%s)" stroke="%s" stroke-width="2"/>' % (u, edge) +
            dots +
            '<ellipse cx="200" cy="96" rx="44" ry="12" fill="%s" opacity=".7"/>' % shade(c, 0.12) +
            '<circle cx="200" cy="96" r="5" fill="%s"/>' % shade(acc, 0.05))


def _draw_camera(u, c, dark, edge, acc):
    return (_shadow(u, 200, 330, 160) +
            '<path d="M48 130 h70 l18 -28 h66 l18 28 h132 a16 16 0 0 1 16 16 v148 a16 16 0 0 1 -16 16 H48 a16 16 0 0 1 -16 -16 V146 a16 16 0 0 1 16 -16z" fill="url(#b%s)" stroke="%s" stroke-width="2"/>' % (u, edge) +
            '<rect x="32" y="150" width="60" height="150" rx="14" fill="%s" opacity=".85"/>' % dark +
            '<circle cx="214" cy="218" r="82" fill="%s" stroke="%s" stroke-width="4"/>' % (dark, edge) +
            '<circle cx="214" cy="218" r="62" fill="#0b0f16"/><circle cx="214" cy="218" r="40" fill="#1b2433"/>' +
            '<circle cx="196" cy="200" r="12" fill="#ffffff" opacity=".25"/>' +
            '<rect x="300" y="110" width="40" height="14" rx="5" fill="%s"/>' % dark)


def _draw_gamepad(u, c, dark, edge, acc):
    return (_shadow(u, 200, 320, 160) +
            '<path d="M120 120 h160 c46 0 70 30 82 86 l14 70 c6 34 -30 52 -54 26 l-38 -40 H116 l-38 40 c-24 26 -60 8 -54 -26 l14 -70 c12 -56 36 -86 82 -86z" fill="url(#b%s)" stroke="%s" stroke-width="2"/>' % (u, edge) +
            '<path d="M104 180 h16 v-16 h14 v16 h16 v14 h-16 v16 h-14 v-16 h-16z" fill="%s"/>' % dark +
            '<circle cx="282" cy="168" r="9" fill="%s"/><circle cx="302" cy="188" r="9" fill="%s"/><circle cx="262" cy="188" r="9" fill="%s"/><circle cx="282" cy="208" r="9" fill="%s"/>' % (shade(acc, 0.1), dark, dark, dark) +
            '<circle cx="162" cy="236" r="20" fill="%s"/><circle cx="238" cy="236" r="20" fill="%s"/>' % (dark, dark))


def _draw_keyboard(u, c, dark, edge, acc):
    keys = []
    for r in range(5):
        for k in range(12):
            x = 52 + k * 25 + (r % 2) * 6
            if x > 334:
                continue
            keys.append('<rect x="%d" y="%d" width="20" height="18" rx="4" fill="%s"/>' % (x, 158 + r * 23, dark))
    return (_shadow(u, 200, 300, 170, 10) +
            '<rect x="34" y="140" width="332" height="140" rx="14" fill="url(#b%s)" stroke="%s" stroke-width="2"/>' % (u, edge) +
            "".join(keys) +
            '<rect x="120" y="250" width="150" height="16" rx="5" fill="%s"/>' % dark)


def _draw_mouse(u, c, dark, edge, acc):
    return (_shadow(u, 200, 350, 80) +
            '<path d="M200 60 c62 0 90 50 90 140 c0 90 -30 140 -90 140 c-60 0 -90 -50 -90 -140 c0 -90 28 -140 90 -140z" fill="url(#b%s)" stroke="%s" stroke-width="2"/>' % (u, edge) +
            '<path d="M200 62 V170" stroke="%s" stroke-width="2"/>' % edge +
            '<rect x="192" y="96" width="16" height="36" rx="8" fill="%s"/>' % dark +
            '<path d="M120 200 q80 26 160 0" fill="none" stroke="%s" stroke-width="3" opacity=".5"/>' % shade(acc, 0.05))


def _draw_fridge(u, c, dark, edge, acc):
    return (_shadow(u, 200, 384, 110, 10) +
            '<rect x="110" y="18" width="180" height="360" rx="16" fill="url(#b%s)" stroke="%s" stroke-width="2"/>' % (u, edge) +
            '<path d="M110 150 H290" stroke="%s" stroke-width="3"/>' % edge +
            '<rect x="126" y="60" width="8" height="64" rx="4" fill="%s"/>' % dark +
            '<rect x="126" y="176" width="8" height="100" rx="4" fill="%s"/>' % dark +
            '<rect x="214" y="40" width="56" height="30" rx="5" fill="#0e1116"/>' +
            '<rect x="220" y="47" width="22" height="6" rx="3" fill="%s"/>' % shade(acc, 0.2))


def _draw_washer(u, c, dark, edge, acc):
    return (_shadow(u, 200, 372, 140, 10) +
            '<rect x="70" y="40" width="260" height="320" rx="20" fill="url(#b%s)" stroke="%s" stroke-width="2"/>' % (u, edge) +
            '<path d="M70 104 H330" stroke="%s" stroke-width="2"/>' % edge +
            '<rect x="92" y="60" width="70" height="26" rx="6" fill="%s"/>' % dark +
            '<circle cx="292" cy="72" r="15" fill="%s" stroke="%s" stroke-width="3"/>' % (shade(c, 0.05), edge) +
            '<rect x="200" y="64" width="54" height="16" rx="4" fill="#0e1116"/><rect x="206" y="69" width="20" height="6" rx="3" fill="%s"/>' % shade(acc, 0.2) +
            '<circle cx="200" cy="232" r="96" fill="%s" stroke="%s" stroke-width="4"/>' % (dark, edge) +
            '<circle cx="200" cy="232" r="72" fill="#1e2a3a"/>' +
            '<path d="M140 250 q60 -40 120 0 v20 q-60 40 -120 0z" fill="#5b8bb8" opacity=".55"/>' +
            '<circle cx="176" cy="206" r="16" fill="#ffffff" opacity=".2"/>')


def _draw_aircon(u, c, dark, edge, acc):
    return (_shadow(u, 200, 254, 170, 8) +
            '<rect x="22" y="110" width="356" height="120" rx="26" fill="url(#b%s)" stroke="%s" stroke-width="2"/>' % (u, edge) +
            '<path d="M40 196 H360" stroke="%s" stroke-width="2"/>' % edge +
            '<path d="M56 212 H344" stroke="%s" stroke-width="5" stroke-linecap="round" opacity=".6"/>' % dark +
            '<rect x="300" y="132" width="44" height="14" rx="4" fill="#0e1116"/><rect x="306" y="136" width="14" height="6" rx="3" fill="%s"/>' % shade(acc, 0.2) +
            '<g transform="translate(270 268) rotate(-12)"><rect width="40" height="96" rx="12" fill="url(#b%s)" stroke="%s" stroke-width="2"/><rect x="8" y="12" width="24" height="14" rx="3" fill="#0e1116"/><circle cx="20" cy="48" r="6" fill="%s"/></g>' % (u, edge, dark))


def _draw_charger(u, c, dark, edge, acc):
    return (_shadow(u, 200, 352, 140) +
            '<path d="M230 200 C 330 220 330 330 220 330 C 140 330 110 300 90 340" fill="none" stroke="%s" stroke-width="12" stroke-linecap="round"/>' % dark +
            '<path d="M230 200 C 330 220 330 330 220 330 C 140 330 110 300 90 340" fill="none" stroke="url(#b%s)" stroke-width="8" stroke-linecap="round"/>' % u +
            '<rect x="120" y="110" width="120" height="120" rx="26" fill="url(#b%s)" stroke="%s" stroke-width="2"/>' % (u, edge) +
            '<rect x="152" y="74" width="12" height="40" rx="3" fill="#a3aab5"/><rect x="196" y="74" width="12" height="40" rx="3" fill="#a3aab5"/>' +
            '<rect x="166" y="200" width="28" height="10" rx="4" fill="%s"/>' % dark)


def _draw_powerbank(u, c, dark, edge, acc):
    return (_shadow(u, 200, 360, 120) +
            '<rect x="110" y="56" width="180" height="290" rx="30" fill="url(#b%s)" stroke="%s" stroke-width="2"/>' % (u, edge) +
            '<rect x="170" y="70" width="60" height="12" rx="6" fill="%s"/>' % dark +
            "".join('<circle cx="%d" cy="310" r="5" fill="%s"/>' % (172 + i * 18, shade(acc, 0.15) if i < 3 else dark) for i in range(4)) +
            '<path d="M206 170 l-26 40 h20 l-6 34 l28 -44 h-20z" fill="%s" opacity=".7"/>' % dark)


def _draw_chair(u, c, dark, edge, acc):
    wheels = "".join('<circle cx="%d" cy="%d" r="9" fill="#1b1e24"/>' % (x, y) for x, y in ((120, 372), (160, 382), (240, 382), (280, 372), (200, 366)))
    return (_shadow(u, 200, 384, 110, 8) +
            '<path d="M200 300 V340 M200 340 L124 362 M200 340 L162 372 M200 340 L238 372 M200 340 L276 362" stroke="#2a2e35" stroke-width="10" stroke-linecap="round"/>' + wheels +
            '<rect x="186" y="260" width="28" height="48" rx="6" fill="#3a3f47"/>' +
            '<path d="M128 40 Q200 14 272 40 L262 230 Q200 246 138 230 Z" fill="url(#b%s)" stroke="%s" stroke-width="2"/>' % (u, edge) +
            '<path d="M150 58 Q200 40 250 58 L244 210 Q200 222 156 210 Z" fill="%s" opacity=".55"/>' % dark +
            '<rect x="172" y="84" width="56" height="26" rx="10" fill="%s" opacity=".9"/>' % shade(acc, 0.05) +
            '<path d="M118 236 H282 Q292 236 290 248 L284 270 Q282 280 272 280 H128 Q118 280 116 270 L110 248 Q108 236 118 236Z" fill="url(#b%s)" stroke="%s" stroke-width="2"/>' % (u, edge) +
            '<rect x="96" y="196" width="16" height="64" rx="6" fill="#2a2e35"/><rect x="288" y="196" width="16" height="64" rx="6" fill="#2a2e35"/>' +
            '<rect x="86" y="188" width="38" height="12" rx="6" fill="#3a3f47"/><rect x="276" y="188" width="38" height="12" rx="6" fill="#3a3f47"/>')
