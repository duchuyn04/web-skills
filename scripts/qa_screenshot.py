#!/usr/bin/env python3
"""Visual QA for a built page. Needs Python Playwright (pip install playwright).
Uses the installed Edge or Chrome, so no browser download is required on Windows.

Usage:
    python qa_screenshot.py dist                  screenshots at 1440, 768 and 390 px plus layout checks
    python qa_screenshot.py dist --sections       also one image per section and width (dist/qa/sections-<width>)
    python qa_screenshot.py dist --widths 1280,390

Checks (exit code 1 if any fail):
    - elements sticking out of the viewport sideways (horizontal overflow)
    - text wider than its own box (buttons, headings, links)
    - broken images
    - JavaScript errors and failed local requests
    - exactly one <h1>
Look at every screenshot yourself after the script passes.
"""
import argparse
import sys
from pathlib import Path

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
        for w in [int(x) for x in args.widths.split(",")]:
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
        browser.close()
    if failed:
        print("\nQA FAILED. Fix the cause in page.json (shorter copy, fewer items) or in the section template, rebuild, run QA again.")
        return 1
    print("\nQA PASSED. Now open the screenshots and look at them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
