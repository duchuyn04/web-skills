"""Summarise a motion_probe.py output folder: libraries, scroll entrances per element kind, hover patterns."""
import json, re, collections, statistics, sys
from pathlib import Path

D = Path(sys.argv[1])
NUM = r"-?[\d.e-]+"


def chain(tr):
    """Sum translate, product scale over the element and its wrappers."""
    tx = ty = 0.0
    sc = 1.0
    for part in (tr or "").split("|"):
        if not part:
            continue
        _, v = part.split(":", 1)
        m = re.match(r"matrix\((.*)\)", v)
        m3 = re.match(r"matrix3d\((.*)\)", v)
        if m:
            a = [float(x) for x in m.group(1).split(",")]
            sc *= (a[0] ** 2 + a[1] ** 2) ** 0.5
            tx += a[4]
            ty += a[5]
        elif m3:
            a = [float(x) for x in m3.group(1).split(",")]
            sc *= a[0]
            tx += a[12]
            ty += a[13]
        elif v.startswith("tr "):
            p = [float(x) for x in re.findall(NUM, v[3:])]
            if p:
                tx += p[0]
                ty += p[1] if len(p) > 1 else 0
        elif v.startswith("sc "):
            p = [float(x) for x in re.findall(NUM, v[3:])]
            if p:
                sc *= p[0]
    return tx, ty, sc


def img_scale(t):
    if not t or t == "none":
        return 1.0
    m = re.match(r"matrix\((.*)\)", t)
    if m:
        a = [float(x) for x in m.group(1).split(",")]
        return (a[0] ** 2 + a[1] ** 2) ** 0.5
    m = re.match(r"matrix3d\((.*)\)", t)
    if m:
        return float(m.group(1).split(",")[0])
    return 1.0


def classify(b, a):
    pats = set()
    if b["op"] < 0.5 and a["op"] > 0.9:
        pats.add("fade")
    btx, bty, bsc = chain(b["tr"])
    atx, aty, asc = chain(a["tr"])
    dy, dx = bty - aty, btx - atx
    if abs(dy) >= 4:
        pats.add("rise-%s" % ("s" if abs(dy) < 25 else "m" if abs(dy) < 70 else "l") if dy > 0 else "drop")
    if abs(dx) >= 4:
        pats.add("slide-x")
    if abs(bsc - asc) > 0.015:
        pats.add("scale-up" if bsc < asc else "scale-down")
    if b["clip"] and b["clip"] != a["clip"]:
        pats.add("clip")
    if abs(img_scale(b["imgT"]) - img_scale(a["imgT"])) > 0.015:
        pats.add("img-zoom-out" if img_scale(b["imgT"]) > img_scale(a["imgT"]) else "img-zoom-in")
    if b["filt"] and "blur" in (b["filt"] or "") and b["filt"] != a["filt"]:
        pats.add("blur")
    if b["k"] == "heading" and b["split"] >= 3 and pats:
        pats.add("split-text")
    return pats, dy


ok = []
for f in sorted(D.glob("*.json")):
    r = json.loads(f.read_text(encoding="utf-8"))
    if r.get("ok") and len(r["elements"]) >= 5:
        ok.append(r)
print("sites probed with content:", len(ok))

lib = collections.Counter()
kind_sites = collections.defaultdict(collections.Counter)  # sites per pattern, per element kind
kind_total = collections.Counter()
animated_sites = collections.Counter()
dys = collections.defaultdict(list)
per_site = {}
tween_keys = collections.Counter()
tween_vals = collections.defaultdict(collections.Counter)
anim_names = collections.Counter()
hover = []
for r in ok:
    L = r["libs"]
    for k in ("gsap", "aos", "webflow", "framer", "lenis", "locomotive", "swiper", "slick", "splide", "lottie", "three", "wow"):
        if L.get(k):
            lib[k] += 1
    if L.get("st"):
        lib["scrolltrigger"] += 1
    if L.get("stPin"):
        lib["pin"] += 1
    if L.get("stScrub"):
        lib["scrub"] += 1
    if L.get("sticky"):
        lib["sticky"] += 1
    if L.get("autoplay"):
        lib["autoplay-video"] += 1
    if r["parallax"]:
        lib["parallax(any)"] += 1
    loops = {a["n"] for a in L["anims"] if a["it"] in (None, "Infinity") or a["it"] == float("inf") or str(a["it"]) == "Infinity"}
    for n in {a["n"] for a in L["anims"]}:
        anim_names[n] += 1
    mp = L.get("mp") or {}
    for t in mp.get("tweens", []):
        for k, v in list((t.get("from") or {}).items()) + list(t["v"].items()):
            tween_keys[k] += 1
            if k in ("y", "yPercent", "x", "xPercent", "scale", "duration", "ease", "stagger", "clipPath", "opacity", "rotation", "delay"):
                tween_vals[k][str(v)[:30]] += 1
    hover.append(r["hover"]["transform"])
    site = collections.defaultdict(set)
    any_anim = False
    for k, v in r["elements"].items():
        b, a = v["before"], v["after"]
        if not b or not a:
            continue
        kind_total[b["k"]] += 1
        pats, dy = classify(b, a)
        if pats:
            any_anim = True
            site[b["k"]].update(pats)
            if "rise-s" in pats or "rise-m" in pats or "rise-l" in pats:
                dys[b["k"]].append(dy)
        else:
            site[b["k"]].add("static")
    if any_anim:
        animated_sites["any"] += 1
    per_site[r["id"]] = {k: sorted(v) for k, v in site.items()}
    for kind, pats in site.items():
        for p in pats:
            kind_sites[kind][p] += 1

N = len(ok)
print("\nLibraries (share of sites):")
for k, v in lib.most_common():
    print("  %-15s %3d  %3.0f%%" % (k, v, 100 * v / N))
print("\nSites with any scroll reveal: %d (%.0f%%)" % (animated_sites["any"], 100 * animated_sites["any"] / N))
for kind in ("heading", "media", "card", "button"):
    print("\n%s (sites that have this kind below the fold):" % kind)
    for p, v in kind_sites[kind].most_common():
        print("  %-14s %3d  %3.0f%%" % (p, v, 100 * v / N))
    if dys[kind]:
        print("  rise distance px: median %.0f, p25 %.0f, p75 %.0f" % (statistics.median(dys[kind]), statistics.quantiles(dys[kind], n=4)[0], statistics.quantiles(dys[kind], n=4)[2]))
print("\nHover transform rules per site: median %s, sites with >5: %d" % (statistics.median(hover), sum(1 for h in hover if h > 5)))
print("\nGSAP tween keys:", tween_keys.most_common(25))
for k in ("y", "yPercent", "duration", "ease", "stagger", "clipPath", "scale", "x", "xPercent"):
    print("  %s:" % k, tween_vals[k].most_common(8))
print("\nCSS animation names on 3+ sites:", [(n, c) for n, c in anim_names.most_common(40) if c >= 3])

# Hover patterns from the sampled :hover rules
HC = collections.Counter()
for r in ok:
    kinds = set()
    for s in r["hover"]["sample"]:
        sel, _, val = s.partition("{")
        sel = sel.lower()
        sc = re.search(r"scale\(([\d.]+)", val)
        ty = re.search(r"translatey\((-?[\d.]+)", val.lower()) or re.search(r"translate\([^,]+,\s*(-?[\d.]+)", val.lower())
        tx = re.search(r"translatex\((-?[\d.]+)", val.lower()) or re.search(r"translate\((-?[\d.]+)px", val.lower())
        if sc and float(sc.group(1)) > 1 and re.search(r"img|image|photo|thumb|media|figure|picture|bg", sel):
            kinds.add("image-zoom")
        elif re.search(r"arrow|icon|svg|chevron|link", sel) and tx:
            kinds.add("arrow-or-link-slide")
        elif re.search(r"card|item|tile|box|post|col|block", sel) and ty and float(ty.group(1)) < 0:
            kinds.add("card-lift")
        elif re.search(r"btn|button|cta", sel):
            kinds.add("button-move")
        elif "rotate" in val.lower():
            kinds.add("rotate")
        elif sc:
            kinds.add("scale-other")
    for k in kinds:
        HC[k] += 1
print("\nHover patterns (sites, from up to 15 sampled rules each):")
for k, v in HC.most_common():
    print("  %-22s %3d  %3.0f%%" % (k, v, 100 * v / N))
