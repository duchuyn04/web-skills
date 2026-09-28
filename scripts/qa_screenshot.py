#!/usr/bin/env python3
"""Visual QA for a built page. Needs Python Playwright (pip install playwright).
Uses the installed Edge or Chrome, so no browser download is required on Windows.

Usage:
    python qa_screenshot.py dist                  screenshots at 1440, 768 and 390 px plus layout checks
    python qa_screenshot.py dist --sections       also one image per section and width (dist/qa/sections-<width>)
    python qa_screenshot.py dist --widths 1280,390
    python qa_screenshot.py dist --no-motion      skip the frame-rate check
    python qa_screenshot.py dist --cvd            also save colour-vision screenshots (qa/cvd-*.png) to review

Checks (exit code 1 if any fail):
    - elements sticking out of the viewport sideways (horizontal overflow)
    - text wider than its own box (buttons, headings, links)
    - broken images
    - JavaScript errors and failed local requests
    - exactly one <h1>
    - text contrast (WCAG 2.2 SC 1.4.3): every visible text run against the colour behind it, 4.5:1, or 3:1
      for large text (24px, or 18.66px bold); text over photos and gradients is left to the screenshots
    - focus (SC 2.4.7, 1.4.11): every Tab stop shows a solid outline of 2px or more at 3:1 on its background
    - links inside running text are underlined or differ from the text around them by 3:1 (SC 1.4.1)
    - frame rate: at 1440 px on a 2x (Retina-class) screen, the hero and every section with a canvas
      must keep at least 30 frames per second. Canvas and paint cost grow with the square of the pixel
      ratio, so a 1x run hides slow animation that desktop users with scaled screens see as lag.
Look at every screenshot yourself after the script passes.
"""
import argparse
import sys
from pathlib import Path

MIN_FPS = 30

CHECK_JS = r"""
() => {
  const vw = window.innerWidth;
  const clipsX = (el) => {
    for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) {
      const s = getComputedStyle(p);
      if (['hidden', 'clip', 'auto', 'scroll'].includes(s.overflowX)) return true;
    }
    return false;
  };
  const hiddenUp = (el) => {
    for (let p = el; p; p = p.parentElement) {
      const s = getComputedStyle(p);
      if (s.visibility === 'hidden' || s.display === 'none' || s.opacity === '0') return true;
    }
    return false;
  };
  const name = (el) => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (el.classList.length ? '.' + [...el.classList].slice(0, 2).join('.') : '');
  const section = (el) => { const s = el.closest('section, header, footer, aside, dialog'); return s ? (s.id || s.tagName.toLowerCase()) : 'page'; };
  const overflow = [];
  for (const el of document.querySelectorAll('body *')) {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    if ((r.right > vw + 1 || r.left < -1) && getComputedStyle(el).position !== 'fixed' && !clipsX(el) && !hiddenUp(el)) {
      overflow.push(`${section(el)}: ${name(el)} spans ${Math.round(r.left)}..${Math.round(r.right)}px (viewport ${vw}px)`);
    }
  }
  const clipped = [];
  for (const el of document.querySelectorAll('h1, h2, h3, .bl-btn, .bl-link, .bl-nav__link, .bl-chip, .bl-tabs__tab')) {
    if (hiddenUp(el)) continue;
    const box = el.getBoundingClientRect();
    if (!box.width) continue;
    const range = document.createRange();
    range.selectNodeContents(el);
    const txt = range.getBoundingClientRect();
    if (txt.right > box.right + 2 || txt.left < box.left - 2) {
      clipped.push(`${section(el)}: ${name(el)} content is ${Math.round(txt.width)}px wide but its box is ${Math.round(box.width)}px ("${el.textContent.trim().slice(0, 40)}")`);
    }
  }
  const broken = [...document.images].filter((i) => i.complete && i.naturalWidth === 0).map((i) => i.getAttribute('src'));
  return { overflow: overflow.slice(0, 12), overflowCount: overflow.length, clipped: clipped.slice(0, 12), broken, h1: document.querySelectorAll('h1').length, height: document.documentElement.scrollHeight };
}
"""

SCROLL_JS = r"""
async () => {
  const step = Math.round(window.innerHeight * 0.7);
  for (let y = 0; y < document.documentElement.scrollHeight; y += step) {
    window.scrollTo(0, y);
    await new Promise((r) => setTimeout(r, 90));
  }
  window.scrollTo(0, document.documentElement.scrollHeight);
  await new Promise((r) => setTimeout(r, 300));
  document.querySelectorAll('[data-reveal]').forEach((el) => el.classList.add('is-in'));
  window.scrollTo(0, 0);
  await new Promise((r) => setTimeout(r, 2300));
}
"""


# WCAG 2.2 SC 1.4.3 on the rendered page: every visible text run against the colour really behind it.
# Colours go through a 1x1 canvas, so oklch(), color-mix() and color() values parse like hex.
# Text over a gradient or photo is skipped (the pixel behind it is unknown); look at those in the screenshots.
CONTRAST_JS = r"""() => {
  const cv = document.createElement('canvas'); cv.width = cv.height = 1;
  const cx = cv.getContext('2d', { willReadFrequently: true });
  const parse = s => { cx.clearRect(0, 0, 1, 1); cx.fillStyle = '#000'; cx.fillStyle = s; cx.fillRect(0, 0, 1, 1); const d = cx.getImageData(0, 0, 1, 1).data; return [d[0], d[1], d[2], d[3] / 255]; };
  const lin = c => { c /= 255; return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
  const lum = c => 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]);
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  const over = (top, under) => [0, 1, 2].map(i => top[i] * top[3] + under[i] * (1 - top[3])).concat([1]);
  const hex = c => '#' + c.slice(0, 3).map(v => Math.round(v).toString(16).padStart(2, '0')).join('');
  function backdrop(el) {
    const layers = [];
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const cs = getComputedStyle(n);
      if (cs.backgroundImage !== 'none') return null;
      const c = parse(cs.backgroundColor);
      if (c[3] > 0) { layers.push(c); if (c[3] >= 0.999) break; }
      /* a fixed or sticky layer without its own opaque fill floats over whatever scrolls under it */
      if (cs.position === 'fixed' || cs.position === 'sticky') return null;
    }
    let bg = [255, 255, 255, 1];
    for (let i = layers.length - 1; i >= 0; i--) bg = over(layers[i], bg);
    return bg;
  }
  function hidden(el) {
    if (el.closest('[aria-hidden="true"], .bl-sr-only, [hidden], [inert]')) return true;
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) return true;
    let op = 1;
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const cs = getComputedStyle(n);
      if (cs.display === 'none' || cs.visibility === 'hidden') return true;
      op *= parseFloat(cs.opacity);
    }
    return op < 0.05;
  }
  /* text laid over a photo, video, canvas or positioned fill that is not its own ancestor: the pixel behind it is unknown */
  function overMedia(el) {
    const r = el.getBoundingClientRect(), x = r.left + r.width / 2, y = r.top + r.height / 2;
    let box = el.parentElement;
    for (let i = 0; box && i < 5; i++, box = box.parentElement) {
      for (const m of box.querySelectorAll('*')) {
        if (m.contains(el) || el.contains(m)) continue;
        const media = /^(IMG|VIDEO|CANVAS|PICTURE)$/.test(m.tagName);
        /* a positioned sibling layer with its own fill (switch knob, card shade) sits behind the text */
        const layer = !media && getComputedStyle(m).position === 'absolute' && (parse(getComputedStyle(m).backgroundColor)[3] > 0.5 || getComputedStyle(m).backgroundImage !== 'none');
        if (!media && !layer) continue;
        const b = m.getBoundingClientRect();
        if (b.width && x >= b.left && x <= b.right && y >= b.top && y <= b.bottom) return true;
      }
    }
    return false;
  }
  const seen = new Set(), fails = [];
  let checked = 0, skipped = 0;
  document.querySelectorAll('body *').forEach(el => {
    if (['SCRIPT', 'STYLE', 'SVG', 'svg', 'NOSCRIPT', 'OPTION'].includes(el.tagName)) return;
    const own = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 1);
    if (!own || hidden(el)) return;
    const cs = getComputedStyle(el);
    const bg = backdrop(el);
    if (!bg || overMedia(el)) { skipped++; return; }
    let fg = parse(cs.color);
    /* outlined numerals: the stroke is what you read */
    if (fg[3] < 0.1 && parseFloat(cs.webkitTextStrokeWidth) > 0) fg = parse(cs.webkitTextStrokeColor);
    if (fg[3] < 1) fg = over(fg, bg);
    const size = parseFloat(cs.fontSize), weight = parseInt(cs.fontWeight, 10) || 400;
    const large = size >= 24 || (size >= 18.66 && weight >= 700);
    const need = large ? 3 : 4.5, r = ratio(fg, bg);
    checked++;
    if (r + 0.005 >= need) return;
    const sec = el.closest('[id]');
    const key = hex(fg) + hex(bg) + (sec ? sec.id : '');
    if (seen.has(key)) return;
    seen.add(key);
    fails.push({ text: el.textContent.trim().replace(/\s+/g, ' ').slice(0, 40), ratio: Math.round(r * 100) / 100, need, fg: hex(fg), bg: hex(bg), where: sec ? sec.id : '' });
  });
  return { checked, skipped, fails: fails.slice(0, 15), failCount: fails.length };
}"""

# WCAG 2.2 SC 2.4.7 / 1.4.11: the element reached with Tab shows a solid outline of 2px or more at 3:1 on the colour around it.
FOCUS_JS = r"""() => {
  const el = document.activeElement;
  if (!el || el === document.body) return null;
  const cv = document.createElement('canvas'); cv.width = cv.height = 1;
  const cx = cv.getContext('2d', { willReadFrequently: true });
  const parse = s => { cx.clearRect(0, 0, 1, 1); cx.fillStyle = '#000'; cx.fillStyle = s; cx.fillRect(0, 0, 1, 1); const d = cx.getImageData(0, 0, 1, 1).data; return [d[0], d[1], d[2], d[3] / 255]; };
  const lin = c => { c /= 255; return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
  const lum = c => 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]);
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  const over = (top, under) => [0, 1, 2].map(i => top[i] * top[3] + under[i] * (1 - top[3])).concat([1]);
  const cs = getComputedStyle(el);
  const name = (el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/)[0] : '')).slice(0, 60);
  const where = (el.closest('[id]') || {}).id || '';
  const width = parseFloat(cs.outlineWidth) || 0;
  if (cs.outlineStyle === 'none' || width < 2) {
    const ring = cs.boxShadow && cs.boxShadow !== 'none';
    return { name, where, ok: false, why: ring ? 'focus shown only as a box-shadow; use a 2px outline' : 'no visible focus outline' };
  }
  /* the outline sits outside the element, on its parent's ground */
  const layers = [];
  for (let n = el.parentElement; n && n.nodeType === 1; n = n.parentElement) {
    const s = getComputedStyle(n);
    if (s.backgroundImage !== 'none') return { name, where, ok: true, why: 'over a gradient or photo, check by eye' };
    const c = parse(s.backgroundColor);
    if (c[3] > 0) { layers.push(c); if (c[3] >= 0.999) break; }
    if (s.position === 'fixed' || s.position === 'sticky') { if (!layers.length) return { name, where, ok: true, why: 'floating layer' }; break; }
  }
  let bg = [255, 255, 255, 1];
  for (let i = layers.length - 1; i >= 0; i--) bg = over(layers[i], bg);
  let oc = parse(cs.outlineColor);
  if (oc[3] < 1) oc = over(oc, bg);
  const r = ratio(oc, bg);
  return { name, where, ok: r >= 3, why: 'outline ' + (Math.round(r * 100) / 100) + ':1 on its background, needs 3:1' };
}"""

# WCAG 2.2 SC 1.4.1: a link inside running text is underlined, or differs from the text around it by 3:1.
LINKS_JS = r"""() => {
  const cv = document.createElement('canvas'); cv.width = cv.height = 1;
  const cx = cv.getContext('2d', { willReadFrequently: true });
  const parse = s => { cx.clearRect(0, 0, 1, 1); cx.fillStyle = '#000'; cx.fillStyle = s; cx.fillRect(0, 0, 1, 1); const d = cx.getImageData(0, 0, 1, 1).data; return [d[0], d[1], d[2]]; };
  const lin = c => { c /= 255; return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
  const lum = c => 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]);
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  const out = [];
  document.querySelectorAll('p a, li a').forEach(a => {
    const p = a.parentElement;
    const prose = [...p.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 2);
    if (!prose || a.closest('[aria-hidden="true"], nav, footer')) return;
    const s = getComputedStyle(a);
    if (s.textDecorationLine.includes('underline')) return;
    const r = ratio(parse(s.color), parse(getComputedStyle(p).color));
    if (r < 3) out.push({ text: a.textContent.trim().slice(0, 40), ratio: Math.round(r * 100) / 100, where: (a.closest('[id]') || {}).id || '' });
  });
  return out.slice(0, 10);
}"""

FPS_JS = """async (ms) => {
  const f = []; let last = 0; const t0 = performance.now();
  await new Promise(res => { const tick = ts => { if (last) f.push(ts - last); last = ts; if (performance.now() - t0 < ms) requestAnimationFrame(tick); else res(); }; requestAnimationFrame(tick); });
  if (!f.length) return { fps: 0, p95: 0 };
  f.sort((a, b) => a - b);
  return { fps: Math.round(1000 * f.length / f.reduce((a, b) => a + b, 0)), p95: Math.round(f[Math.floor(f.length * .95)]) };
}"""

# The hero, plus every section that owns a canvas (ribbons, globe, echo), a video or an endless CSS loop.
MOTION_TARGETS_JS = """() => {
  const out = [];
  document.querySelectorAll('main > *').forEach((s, i) => {
    const moving = i === 0 || s.querySelector('canvas, video') || [...s.querySelectorAll('*')].some(e => getComputedStyle(e).animationIterationCount === 'infinite');
    if (moving) out.push(s.id || ('section-' + (i + 1)));
  });
  return out;
}"""


def motion_check(browser, index):
    """Frame rate at 1440 px and pixel ratio 2 for the hero and every moving section. Returns (lines, problems)."""
    ctx = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
    page = ctx.new_page()
    page.goto(index.as_uri(), wait_until="load")
    page.wait_for_timeout(2500)
    lines, problems = [], []
    for sid in page.evaluate(MOTION_TARGETS_JS):
        page.evaluate("id => { const el = document.getElementById(id); if (el) window.scrollTo(0, el.getBoundingClientRect().top + scrollY); }", sid)
        page.wait_for_timeout(1200)
        r = page.evaluate(FPS_JS, 1500)
        lines.append("%s %d fps" % (sid, r["fps"]))
        if r["fps"] < MIN_FPS:
            problems.append("slow animation: #%s runs at %d fps (slowest frames %d ms) on a 2x screen, minimum %d. "
                            "Canvas: draw at 1x for decorative lines, fewer points, one stroke per colour, 30 fps cap "
                            "(see Motion and performance in references/custom-section-spec.md)." % (sid, r["fps"], r["p95"], MIN_FPS))
    ctx.close()
    return lines, problems


def focus_problems(page, limit=80):
    """Press Tab through the page; every stop needs a visible 2px outline at 3:1. One line per distinct control."""
    page.evaluate("window.scrollTo(0, 0); document.activeElement && document.activeElement.blur()")
    seen, out, first = set(), [], None
    for _ in range(limit):
        page.keyboard.press("Tab")
        r = page.evaluate(FOCUS_JS)
        if not r:
            continue
        key = (r["name"], r["where"])
        if first is None:
            first = key
        elif key == first:
            break
        if key in seen or r["ok"]:
            seen.add(key)
            continue
        seen.add(key)
        out.append("focus: %s in #%s: %s" % (r["name"], r["where"], r["why"]))
    page.evaluate("document.activeElement && document.activeElement.blur(); window.scrollTo(0, 0)")
    return out[:10]


def cvd_shots(browser, index, out):
    """Full-page screenshots as seen with three colour vision deficiencies (Chrome DevTools emulation). For review only."""
    ctx = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
    page = ctx.new_page()
    page.goto(index.as_uri(), wait_until="load")
    page.evaluate(SCROLL_JS)
    cdp = ctx.new_cdp_session(page)
    files = []
    for kind in ("deuteranopia", "protanopia", "achromatopsia"):
        cdp.send("Emulation.setEmulatedVisionDeficiency", {"type": kind})
        f = out / ("cvd-%s.png" % kind)
        page.screenshot(path=str(f), full_page=True)
        files.append(f.name)
    ctx.close()
    return files


def launch(p):
    for kind, opts in (("chromium", {"channel": "msedge"}), ("chromium", {"channel": "chrome"}), ("chromium", {}), ("webkit", {})):
        try:
            return getattr(p, kind).launch(**opts), "%s %s" % (kind, opts.get("channel", "bundled"))
        except Exception:
            continue
    raise SystemExit("No browser available. Install Edge or Chrome, or run: python -m playwright install chromium")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dist", help="folder that contains index.html")
    ap.add_argument("--widths", default="1440,768,390")
    ap.add_argument("--sections", action="store_true", help="save one JPEG per section for every width")
    ap.add_argument("--out", default=None, help="screenshot folder (default: <dist>/qa)")
    ap.add_argument("--no-motion", action="store_true", help="skip the frame-rate check")
    ap.add_argument("--cvd", action="store_true", help="also save deuteranopia, protanopia and achromatopsia screenshots (qa/cvd-*.png) to review")
    args = ap.parse_args()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Python Playwright is missing. Run: pip install playwright")
        return 2
    dist = Path(args.dist).resolve()
    index = dist / "index.html"
    if not index.is_file():
        print("No index.html in %s. Run build.py first." % dist)
        return 2
    out = Path(args.out).resolve() if args.out else dist / "qa"
    out.mkdir(parents=True, exist_ok=True)
    failed = False
    with sync_playwright() as p:
        browser, label = launch(p)
        print("Browser: " + label)
        widths = [int(x) for x in args.widths.split(",")]
        for w in widths:
            ctx = browser.new_context(viewport={"width": w, "height": 900}, device_scale_factor=1)
            page = ctx.new_page()
            errors = []
            page.on("pageerror", lambda e: errors.append("JS error: %s" % e))
            page.on("console", lambda m: errors.append("console.%s: %s" % (m.type, m.text)) if m.type == "error" else None)
            page.on("requestfailed", lambda r: errors.append("request failed: %s" % r.url) if r.url.startswith("file:") else None)
            page.goto(index.as_uri(), wait_until="load")
            page.evaluate("document.fonts.ready.then(() => true)")
            page.evaluate(SCROLL_JS)
            res = page.evaluate(CHECK_JS)
            shot = out / ("page-%d.png" % w)
            page.screenshot(path=str(shot), full_page=True)
            problems = []
            problems += ["overflow: " + s for s in res["overflow"]]
            if res["overflowCount"] > len(res["overflow"]):
                problems.append("overflow: ... %d more elements" % (res["overflowCount"] - len(res["overflow"])))
            problems += ["clipped text: " + s for s in res["clipped"]]
            problems += ["broken image: %s" % s for s in res["broken"]]
            problems += errors
            if w == widths[0]:
                con = page.evaluate(CONTRAST_JS)
                for f in con["fails"]:
                    problems.append("low contrast %.2f:1 (needs %g:1) in #%s: %s on %s, \"%s\"" % (f["ratio"], f["need"], f["where"], f["fg"], f["bg"], f["text"]))
                if con["failCount"] > len(con["fails"]):
                    problems.append("low contrast: ... %d more colour pairs" % (con["failCount"] - len(con["fails"])))
                for f in page.evaluate(LINKS_JS):
                    problems.append("link in running text in #%s is not underlined and only %.2f:1 from the text around it (needs 3:1): \"%s\"" % (f["where"], f["ratio"], f["text"]))
                problems += focus_problems(page)
            if res["h1"] != 1:
                problems.append("expected exactly one <h1>, found %d" % res["h1"])
            status = "OK  " if not problems else "FAIL"
            print("%s %4dpx  page height %dpx  screenshot %s" % (status, w, res["height"], shot))
            for pr in problems:
                print("       " + pr)
            failed = failed or bool(problems)
            if args.sections:
                sdir = out / ("sections-%d" % w)
                sdir.mkdir(exist_ok=True)
                # Scroll-linked layouts (sticky stacks) lay out flat for element shots.
                page.evaluate("document.documentElement.classList.add('bl-shot'); window.dispatchEvent(new Event('resize'))")
                els = page.query_selector_all("body > header, main > *, body > footer")
                for i, el in enumerate(els):
                    sid = el.get_attribute("id") or "section"
                    el.screenshot(path=str(sdir / ("%02d-%s.jpg" % (i + 1, sid))), type="jpeg", quality=72)
                print("     section shots in %s" % sdir)
            ctx.close()
        if not args.no_motion:
            lines, problems = motion_check(browser, index)
            print("%s motion 1440px at 2x: %s" % ("OK  " if not problems else "FAIL", ", ".join(lines) or "nothing moves"))
            for pr in problems:
                print("       " + pr)
            failed = failed or bool(problems)
        if args.cvd:
            try:
                print("     colour vision shots: %s" % ", ".join(cvd_shots(browser, index, out)))
            except Exception as e:
                print("     colour vision shots need Chrome or Edge: %s" % e)
        browser.close()
    if failed:
        print("\nQA FAILED. Fix the cause in page.json (shorter copy, fewer items) or in the section template, rebuild, run QA again.")
        return 1
    print("\nQA PASSED. Now open the screenshots and look at them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
