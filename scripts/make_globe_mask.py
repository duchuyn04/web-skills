"""Writes the land mask used by templates/sections/_shared/gl-globe.js from templates/partials/world-dots.html.
The mask has one bit per 2.5 degree cell (144 columns from -180, 54 rows from 80 degrees north down to -55), row-major,
packed 8 cells per byte and base64-encoded. Run once after make_world_map.py changes the dot grid:
    python scripts/make_globe_mask.py
"""
import base64
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "templates" / "partials" / "world-dots.html"
DST = ROOT / "templates" / "sections" / "_shared" / "gl-globe.js"
W, H = 144, 54

bits = bytearray(W * H // 8)
for x, y in re.findall(r"M(\d+) (\d+)h0", SRC.read_text(encoding="utf-8")):
    i, j = (int(x) - 5) // 10, (int(y) - 5) // 10
    k = j * W + i
    bits[k >> 3] |= 1 << (k & 7)
mask = base64.b64encode(bytes(bits)).decode("ascii")
js = DST.read_text(encoding="utf-8")
js, n = re.subn(r"var MASK = '[^']*';", "var MASK = '%s';" % mask, js)
if n != 1:
    raise SystemExit("gl-globe.js has no \"var MASK = '...';\" line")
DST.write_text(js, encoding="utf-8")
print("wrote %d land cells into %s" % (sum(bin(b).count("1") for b in bits), DST.relative_to(ROOT)))
