"""Regenerate templates/partials/world-dots.html from Natural Earth land (world-atlas land-110m.json).
Run once when the map style changes:
    curl -o land-110m.json https://cdn.jsdelivr.net/npm/world-atlas@2/land-110m.json
    python make_world_map.py   (writes world-dots.svg; copy it to templates/partials/world-dots.html)
Keep STEP, LAT_TOP and LAT_BOT in sync with MAP_LAT_TOP / MAP_LAT_BOTTOM in build.py.
"""
import json
t = json.load(open('land-110m.json'))
sx, sy = t['transform']['scale']; tx, ty = t['transform']['translate']
arcs = []
for arc in t['arcs']:
    x = y = 0; pts = []
    for dx, dy in arc:
        x += dx; y += dy
        pts.append((x * sx + tx, y * sy + ty))
    arcs.append(pts)
def ring(idx):
    pts = []
    for i in idx:
        a = arcs[i] if i >= 0 else arcs[~i][::-1]
        pts.extend(a if not pts else a[1:])
    # unwrap longitudes so rings cut at the antimeridian stay continuous
    out = [pts[0]]
    for x, y in pts[1:]:
        px = out[-1][0]
        while x - px > 180: x -= 360
        while x - px < -180: x += 360
        out.append((x, y))
    return out
polys = []
for g in t['objects']['land']['geometries']:
    for poly in g['arcs']:
        rings = [ring(r) for r in poly]
        xs = [p[0] for r in rings for p in r]; ys = [p[1] for r in rings for p in r]
        polys.append((rings, (min(xs), max(xs), min(ys), max(ys))))
def inside(lon, lat):
    return any(inside1(lon + k, lat) for k in (0, 360, -360))
def inside1(lon, lat):
    for rings, (x0, x1, y0, y1) in polys:
        if not (x0 <= lon <= x1 and y0 <= lat <= y1): continue
        c = False
        for r in rings:
            n = len(r)
            for i in range(n):
                xa, ya = r[i]; xb, yb = r[i - 1]
                if (ya > lat) != (yb > lat) and lon < (xb - xa) * (lat - ya) / (yb - ya) + xa:
                    c = not c
        if c: return True
    return False
STEP = 2.5; LAT_TOP = 80; LAT_BOT = -56
W = int(360 / STEP); H = int((LAT_TOP - LAT_BOT) / STEP)
d = []
for j in range(H):
    lat = LAT_TOP - (j + 0.5) * STEP
    for i in range(W):
        lon = -180 + (i + 0.5) * STEP
        if inside(lon, lat):
            d.append(f"M{i*10+5} {j*10+5}h0")
svg = (f'<svg class="bl-map__dots" viewBox="0 0 {W*10} {H*10}" preserveAspectRatio="xMidYMid meet" aria-hidden="true" focusable="false">'
       f'<path d="{"".join(d)}" fill="none" stroke="currentColor" stroke-width="5.2" stroke-linecap="round"/></svg>')
open('world-dots.svg', 'w').write(svg)
json.dump({"step": STEP, "lat_top": LAT_TOP, "lat_bottom": LAT_BOT, "width": W*10, "height": H*10, "dots": len(d)}, open('world-dots.meta.json', 'w'))
print(W, H, len(d), len(svg))
