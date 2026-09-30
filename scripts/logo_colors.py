"""Read the brand hues of a logo file (PNG, JPEG, WebP or SVG), so build.py can check that theme.accent comes from it.

Uses Pillow when it is installed. Without it, PNG (8-bit, not interlaced) and SVG still work; other formats return None.
"""
import re
import struct
import zlib
from pathlib import Path

MAX_PIXELS = 1_500_000  # the pure-Python PNG path unfilters every byte; larger files are sampled only with Pillow


def _pixels_pillow(path):
    try:
        from PIL import Image
    except ImportError:
        return None
    try:
        im = Image.open(path).convert("RGBA")
    except Exception:
        return None
    im.thumbnail((240, 240))
    return list(im.getdata())


def _pixels_png(path):
    data = Path(path).read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    pos, idat, palette, trns = 8, [], None, None
    width = height = depth = ctype = interlace = None
    while pos < len(data):
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        chunk = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if kind == b"IHDR":
            width, height, depth, ctype, _, _, interlace = struct.unpack(">IIBBBBB", chunk)
        elif kind == b"PLTE":
            palette = [tuple(chunk[i:i + 3]) for i in range(0, len(chunk), 3)]
        elif kind == b"tRNS":
            trns = chunk
        elif kind == b"IDAT":
            idat.append(chunk)
        elif kind == b"IEND":
            break
    if depth != 8 or interlace or ctype not in (0, 2, 3, 4, 6) or width * height > MAX_PIXELS:
        return None
    bpp = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ctype]
    raw = zlib.decompress(b"".join(idat))
    stride = width * bpp
    prev = bytearray(stride)
    out = []
    step = max(1, height // 200)
    i = 0
    for y in range(height):
        f = raw[i]
        line = bytearray(raw[i + 1:i + 1 + stride])
        i += 1 + stride
        if f == 1:
            for x in range(bpp, stride):
                line[x] = (line[x] + line[x - bpp]) & 255
        elif f == 2:
            for x in range(stride):
                line[x] = (line[x] + prev[x]) & 255
        elif f == 3:
            for x in range(stride):
                a = line[x - bpp] if x >= bpp else 0
                line[x] = (line[x] + ((a + prev[x]) >> 1)) & 255
        elif f == 4:
            for x in range(stride):
                a = line[x - bpp] if x >= bpp else 0
                b = prev[x]
                c = prev[x - bpp] if x >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        prev = line
        if y % step:
            continue
        for x in range(0, stride, bpp * max(1, width // 200)):
            px = line[x:x + bpp]
            if ctype == 2:
                out.append((px[0], px[1], px[2], 255))
            elif ctype == 6:
                out.append(tuple(px))
            elif ctype == 3 and palette:
                idx = px[0]
                alpha = trns[idx] if trns and idx < len(trns) else 255
                out.append(palette[idx] + (alpha,))
            elif ctype == 0:
                out.append((px[0], px[0], px[0], 255))
            elif ctype == 4:
                out.append((px[0], px[0], px[0], px[1]))
    return out


HEX_RE = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")


def _pixels_svg(path):
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    out = []
    for m in HEX_RE.finditer(text):
        h = m.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        out.extend([(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)] * 10)
    return out


def logo_hues(path, to_oklch):
    """Return [(hex, hue, share)] for the chromatic colours of a logo, largest first; [] for a black, white or grey
    logo; None when the file cannot be read."""
    path = Path(path)
    if not path.is_file():
        return None
    if path.suffix.lower() == ".svg":
        px = _pixels_svg(path)
    else:
        px = _pixels_pillow(path)
        if px is None and path.suffix.lower() == ".png":
            px = _pixels_png(path)
    if px is None:
        return None
    opaque = [p for p in px if p[3] >= 200]
    if not opaque:
        return []
    bins = {}
    for r, g, b, _ in opaque:
        L, C, H = to_oklch((r, g, b))
        if C < 0.06 or L < 0.2 or L > 0.97:
            continue
        bins.setdefault(int(H // 15) % 24, []).append((r, g, b, H))
    chromatic = sum(len(v) for v in bins.values())
    if chromatic < 0.02 * len(opaque):
        return []
    out = []
    for k, items in sorted(bins.items(), key=lambda kv: -len(kv[1])):
        share = len(items) / chromatic
        if share < 0.10:
            continue
        n = len(items)
        rgb = tuple(sorted(it[i] for it in items)[n // 2] for i in range(3))
        out.append(("#%02x%02x%02x" % rgb, to_oklch(rgb)[2], share))
    return out
