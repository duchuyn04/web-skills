#!/usr/bin/env python3
"""Make a HyperFrames film from the client's own photos or logo, for the hero or the logo intro.

    py -3.11 scripts/make_film.py sites/<slug>/page.json loop                 hero background film
    py -3.11 scripts/make_film.py sites/<slug>/page.json loop --photos a.jpg,img/b.jpg,c.jpg
    py -3.11 scripts/make_film.py sites/<slug>/page.json intro --tagline "Outsourced accounting teams for UK firms" --places "London, Hanoi, Da Nang"

loop   3 to 5 photos (default: the hero photo, then the page's other client photos), each pushed in slowly and
       wiped to the next by a thin rule; the first photo comes back at the end, so the film loops with no seam.
       No text: the hero lays its own shade and headline over it. 3 s per photo, 1920x1080, then a 1600x900 web
       copy in media/hero-loop.mp4 and its first frame in media/hero-loop.jpg.
intro  the client's logo (site.logo) opens from the middle along a rule, then the tagline and the cities rise in.
       5 s, rendered 16:9 and 9:16, web copies in media/intro.mp4 and media/intro-portrait.mp4, for site-intro.

The HyperFrames projects stay in sites/<slug>/film/<name>/ (index.html, assets/, film.mp4, contact-sheet.jpg), so a
film can be adjusted by hand and rendered again with: npx --yes hyperframes@0.8.143 render -q high -f 30 -o film.mp4
Needs Node (npx) and ffmpeg. Look at every contact-sheet.jpg before using a film: the photos and logo are the
client's, and a crop can cut a face or a sign.
"""
import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build  # noqa: E402

FILM_TPL = build.TPL / "film"
HF = ["npx", "--yes", "hyperframes@0.8.143"]
for stream in (sys.stdout, sys.stderr):
    stream.reconfigure(encoding="utf-8", errors="replace")


def run(cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", shell=os.name == "nt",
                       env=dict(os.environ, HYPERFRAMES_SKIP_SKILLS="1"))
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def need_tools():
    missing = [t for t in ("npx", "ffmpeg") if not shutil.which(t)]
    if missing:
        sys.exit("ERROR %s not found. make_film.py needs Node (for npx hyperframes) and ffmpeg on the PATH." % " and ".join(missing))


def colors(page, lib):
    """Background, text, muted text and accent of the page's light tone, with the page's theme over the preset."""
    preset = lib["presets"].get(page.get("preset"), {})
    c = dict(preset.get("colors", {}))
    c.update({k: v for k, v in (page.get("theme") or {}).items() if isinstance(v, str) and v.startswith("#")})
    light = (preset.get("tones") or {}).get("light", {})

    def hexval(v, fallback):
        v = c.get(v[1:], v) if isinstance(v, str) and v.startswith("$") else v
        return v if isinstance(v, str) and re.match(r"^#[0-9a-fA-F]{6}$", v) else fallback
    return {"bg": hexval(light.get("bg"), "#ffffff"), "text": hexval(c.get("primary"), "#111827"),
            "muted": hexval(light.get("text_muted"), "#5b6474"), "accent": hexval(c.get("accent"), "#2563eb"),
            "dark": hexval(c.get("primary"), "#111827")}


def find_image(value, page_dir, lib):
    if not isinstance(value, str) or not value or value.startswith(("http://", "https://")):
        return None
    if value in lib["images"]:
        return lib["images"][value]
    p = (page_dir / value).resolve()
    return p if p.is_file() else None


def client_photos(page, page_dir):
    """Photo files the client supplied (paths, not library keys), hero first, in page order."""
    out = []

    def walk(o, key=""):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("src", "image", "photo", "poster") or key in ("photos", "images"):
                    walk(v, k)
                elif isinstance(v, (dict, list)):
                    walk(v, k)
        elif isinstance(o, list):
            for v in o:
                walk(v, key)
        elif isinstance(o, str) and re.search(r"\.(jpe?g|png|webp)$", o, re.I):
            p = (page_dir / o).resolve()
            if p.is_file() and p not in out and "logo" not in p.stem.lower():
                out.append(p)
    for s in page.get("sections") or []:
        walk(s.get("data") or {})
    return out


def project(name, film_dir, index_html, assets):
    if film_dir.exists():
        shutil.rmtree(film_dir)
    (film_dir / "assets").mkdir(parents=True)
    for target, src in assets.items():
        shutil.copyfile(src, film_dir / "assets" / target)
    (film_dir / "index.html").write_text(index_html, encoding="utf-8")
    (film_dir / "hyperframes.json").write_text(json.dumps({
        "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
        "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
        "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
        "media": {"autoProxy": True}}, indent=2), encoding="utf-8")
    (film_dir / "meta.json").write_text(json.dumps({"id": name, "name": name}), encoding="utf-8")


def render(film_dir):
    code, out = run(HF + ["check"], cwd=film_dir)
    problems = [l for l in out.splitlines() if re.search(r"\berror\b", l, re.I) and not re.search(r"\b0 error", l, re.I)]
    if problems:
        print("WARN  hyperframes check in %s:\n      %s" % (film_dir, "\n      ".join(problems[:6])))
    code, out = run(HF + ["render", "-q", "high", "-f", "30", "-o", "film.mp4"], cwd=film_dir)
    if code or not (film_dir / "film.mp4").is_file():
        sys.exit("ERROR render failed in %s:\n%s" % (film_dir, "\n".join(out.splitlines()[-15:])))
    return film_dir / "film.mp4"


def frame_count(mp4):
    code, out = run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", str(mp4)])
    try:
        return int(out.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return 0


def contact_sheet(mp4, out, cols=4):
    n = frame_count(mp4) or 150
    picks = [round(i * (n - 1) / 7) for i in range(8)]
    sel = "+".join("eq(n\\,%d)" % f for f in picks)
    run(["ffmpeg", "-v", "error", "-y", "-i", str(mp4), "-vf", "select='%s',scale=480:-1,tile=%dx%d" % (sel, cols, 8 // cols), "-frames:v", "1", "-fps_mode", "vfr", str(out)])


def fix_right_edge(mp4, bg):
    """HyperFrames 0.8 can leave a dark band a few pixels wide on the right edge of a portrait render. On a light
    film, crop it off and pad the width back with the background colour."""
    try:
        from PIL import Image
    except ImportError:
        return
    png = mp4.with_suffix(".edge.png")
    run(["ffmpeg", "-v", "error", "-y", "-ss", "3", "-i", str(mp4), "-frames:v", "1", str(png)])
    if not png.is_file():
        return
    im = Image.open(png).convert("L")
    W, H = im.size
    png.unlink()
    lum = lambda x: sum(im.getpixel((x, y)) for y in range(0, H, 16)) / len(range(0, H, 16))
    dark = 0
    while dark < 24 and lum(W - 1 - dark) < 50:
        dark += 1
    if not dark or lum(W - 1 - dark) < 180:
        return
    keep = W - dark - (dark % 2)
    fixed = mp4.with_name("fixed.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(mp4), "-vf", "crop=%d:%d:0:0,pad=%d:%d:0:0:%s" % (keep, H, W, H, bg.replace("#", "0x")),
         "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p", str(fixed)])
    if fixed.is_file():
        fixed.replace(mp4)
        print("      cleared a %dpx dark band on the right edge of %s" % (dark, mp4))


def logo_size(logo, box_w, box_h):
    """The logo's size when it fills box_w x box_h without changing its shape (a small file is scaled up too)."""
    try:
        from PIL import Image
        w, h = Image.open(logo).size
    except Exception:
        return box_w, box_h
    k = min(box_w / w, box_h / h)
    return round(w * k), round(h * k)


def web_copy(src, dst, crf, scale=None):
    dst.parent.mkdir(parents=True, exist_ok=True)
    vf = ["-vf", "scale=%s:flags=lanczos" % scale] if scale else []
    run(["ffmpeg", "-v", "error", "-y", "-i", str(src)] + vf + ["-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-pix_fmt", "yuv420p",
                                                                 "-profile:v", "high", "-an", "-movflags", "+faststart", str(dst)])
    if not dst.is_file():
        sys.exit("ERROR ffmpeg could not write %s" % dst)
    return dst


def make_loop(page, page_dir, lib, args):
    if args.photos:
        photos = []
        for v in args.photos.split(","):
            p = find_image(v.strip(), page_dir, lib)
            if not p:
                sys.exit("ERROR photo %r not found (a library key or a path relative to page.json)" % v.strip())
            photos.append(p)
    else:
        photos = client_photos(page, page_dir)[:4]
    if not 3 <= len(photos) <= 5:
        sys.exit("ERROR the loop needs 3 to 5 of the client's photos (team, office, the work), found %d. Pass them with --photos a.jpg,b.jpg,c.jpg." % len(photos))
    n = len(photos)
    duration = 3 * n
    ids = ["p%d" % (i + 1) for i in range(n)] + ["p1b"]
    starts = [0] + [round(3 * i - 0.6, 2) for i in range(1, n)] + [round(duration - 0.8, 2)]
    assets, divs = {}, []
    for i, p in enumerate(photos + [photos[0]]):
        # the closing copy of photo 1 gets its own file name, so the renderer treats it as its own layer
        name = ("loop-end-" if i == n else "") + "%d-%s" % (i + 1 if i < n else 1, p.name)
        assets[name] = p
        divs.append('      <div class="photo" id="%s" data-layout-allow-overflow><img src="assets/%s" alt="" /></div>' % (ids[i], html.escape(name)))
    c = colors(page, lib)
    doc = (FILM_TPL / "hero-loop.html").read_text(encoding="utf-8")
    doc = (doc.replace("__PHOTOS__", "\n".join(divs)).replace("__DURATION__", str(duration)).replace("__BG__", c["dark"])
           .replace("__IDS__", json.dumps(ids)).replace("__STARTS__", json.dumps(starts)))
    film_dir = page_dir / "film" / "hero-loop"
    project("hero-loop", film_dir, doc, assets)
    print("Rendering the hero loop (%d photos, %d s) in %s ..." % (n, duration, film_dir))
    mp4 = render(film_dir) if not args.no_render else None
    if not mp4:
        return
    contact_sheet(mp4, film_dir / "contact-sheet.jpg")
    web = web_copy(mp4, page_dir / "media" / "hero-loop.mp4", 27, "1600:900")
    poster = page_dir / "media" / "hero-loop.jpg"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(web), "-frames:v", "1", "-q:v", "3", str(poster)])
    print("OK  %s (%d KB), poster %s" % (web.relative_to(page_dir).as_posix(), web.stat().st_size // 1024, poster.relative_to(page_dir).as_posix()))
    print("    look at %s, then set on the hero-fullbleed section:" % (film_dir / "contact-sheet.jpg"))
    print('    "image": "media/hero-loop.jpg", "video": "media/hero-loop.mp4"')


def make_intro(page, page_dir, lib, args):
    site = page.get("site") or {}
    logo = find_image(site.get("logo"), page_dir, lib)
    if not logo:
        sys.exit("ERROR the intro shows the client's logo: set site.logo in page.json to their logo file first.")
    if not args.tagline:
        sys.exit("ERROR pass --tagline with the line under the logo, from the brief (for example the hero title).")
    preset = lib["presets"].get(page.get("preset"), {})
    fonts = preset.get("fonts", {})
    c = colors(page, lib)
    places = [p.strip() for p in (args.places or "").split(",") if p.strip()]
    sep = '<b class="sep">/</b>'
    out = []
    for res, (W, H) in (("landscape", (1920, 1080)), ("portrait", (1080, 1920))):
        wide = res == "landscape"
        lines = ['        <div class="line" id="tagline"><span class="in">%s</span></div>' % html.escape(args.tagline)]
        if places:
            lines.append('        <div class="line" id="places"><span class="in">%s</span></div>' % sep.join(html.escape(p) for p in places))
        rep = {"__RES__": res, "__W__": str(W), "__H__": str(H), "__BG__": c["bg"], "__TEXT__": c["text"], "__MUTED__": c["muted"],
               "__ACCENT__": c["accent"], "__FONTS__": fonts.get("google", "family=Inter:wght@400;600;700"),
               "__HEADING_FONT__": fonts.get("heading", "Inter"), "__BODY_FONT__": fonts.get("body", "Inter"),
               "__HEADING_WEIGHT__": str((preset.get("type") or {}).get("heading_weight", 600)),
               "__LOGO__": "logo" + logo.suffix.lower(), "__BRAND__": html.escape(site.get("brand", "")),
               "__LOGO_W__": str(logo_size(logo, 900, 340)[0] if wide else logo_size(logo, 880, 440)[0]),
               "__RULE_W__": "900" if wide else "860", "__RULE_HALF__": "450" if wide else "430",
               "__LINE_W__": "1600" if wide else "920", "__GAP__": "84" if wide else "110",
               "__TAG_SIZE__": "58" if wide else "68", "__PLACE_SIZE__": "26" if wide else "30", "__LINES__": "\n".join(lines)}
        doc = (FILM_TPL / "intro.html").read_text(encoding="utf-8")
        for k, v in rep.items():
            doc = doc.replace(k, v)
        name = "intro" if wide else "intro-portrait"
        film_dir = page_dir / "film" / name
        project(name, film_dir, doc, {"logo" + logo.suffix.lower(): logo})
        if args.no_render:
            continue
        print("Rendering the %s logo intro in %s ..." % (res, film_dir))
        mp4 = render(film_dir)
        if not wide:
            fix_right_edge(mp4, c["bg"])
        contact_sheet(mp4, film_dir / "contact-sheet.jpg", cols=4 if wide else 8)
        out.append((film_dir, web_copy(mp4, page_dir / "media" / (name + ".mp4"), 23)))
    for film_dir, web in out:
        print("OK  %s (%d KB); look at %s" % (web.relative_to(page_dir).as_posix(), web.stat().st_size // 1024, film_dir / "contact-sheet.jpg"))
    if out:
        print("    add as the last section of page.json:")
        print('    {"type": "site-intro", "data": {"video": "media/intro.mp4", "video_portrait": "media/intro-portrait.mp4", "label": "%s logo intro"}}' % site.get("brand", ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page", help="sites/<slug>/page.json")
    ap.add_argument("kind", choices=["loop", "intro"])
    ap.add_argument("--photos", help="loop: 3 to 5 photos, comma-separated (library keys or paths relative to page.json)")
    ap.add_argument("--tagline", help="intro: the line under the logo, from the brief")
    ap.add_argument("--places", help="intro: cities or countries, comma-separated, from the brief")
    ap.add_argument("--no-render", action="store_true", help="write the HyperFrames project only")
    args = ap.parse_args()
    page_path = Path(args.page).resolve()
    page = json.loads(page_path.read_text(encoding="utf-8"))
    if not args.no_render:
        need_tools()
    lib = build.load_library()
    (make_loop if args.kind == "loop" else make_intro)(page, page_path.parent, lib, args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
