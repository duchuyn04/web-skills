"""Browser QA for pages built with the app-ui kit: every page, every state, at 1440 and 390 px.

    python scripts/qa.py <project folder>                  every page that loads kit/app.css
    python scripts/qa.py <folder> --pages list.html,wizard.html
    python scripts/qa.py <folder> --sweep                   also narrow each page from 1440 to 360 px in 20 px steps

Fails (exit 1): JavaScript errors, sideways scrolling, empty page under the content, broken images, icons that are not in the sprite, text
below 4.5:1 contrast (3:1 when large), and with --sweep: sideways scrolling or header items that overlap at
any width in between. Warns: text cut by its box, tap targets under 24 px on phones, short labels that wrap,
items of one kind in one row that differ in height by 1 to 4 px or that start at different heights in a grid,
hover that moves the layout.
Screenshots of every page, state and width go to <folder>/qa/ (or --out). Look at them: the script measures
what can be measured, the eye judges the rest. Needs Python Playwright with Edge or Chrome.
"""
import argparse
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    raise SystemExit("qa.py needs Playwright: python -m pip install playwright (on Windows try py -3.11)")

WRAPS_FN = r"""
  const wrapsText = (el) => {
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    const range = document.createRange();
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      if (!node.textContent.trim()) continue;
      range.selectNodeContents(node);
      const tops = [...range.getClientRects()].filter(r => r.width > 1).map(r => r.top);
      if (tops.length > 1 && Math.max(...tops) - Math.min(...tops) > 4) return true;
    }
    return false;
  };
  const shown = (el) => el.offsetParent !== null || getComputedStyle(el).position === 'fixed';
"""

CHECK_JS = r"""
() => {
/*WRAPS*/
  const out = {overflow: document.documentElement.scrollWidth - innerWidth, broken: [], cut: [], small: [], wrapped: [], uneven: [], icons: []};
  /* empty space under the page: something hidden (a table in .sr-only, an absolute block) makes the page longer
     than what it shows */
  const kids = [...document.body.children].filter(e => !['SCRIPT', 'DIALOG', 'TEMPLATE'].includes(e.tagName) && getComputedStyle(e).position !== 'fixed' && shown(e));
  const bottom = Math.max(innerHeight, ...kids.map(e => e.getBoundingClientRect().bottom + scrollY));
  out.gap = Math.round(document.documentElement.scrollHeight - bottom);
  for (const img of document.images) {
    if (!shown(img)) continue;
    if (img.complete && img.naturalWidth === 0) out.broken.push(img.getAttribute('src'));
  }
  for (const u of document.querySelectorAll('svg use')) {
    const id = (u.getAttribute('href') || '').replace('#', '');
    if (id && !document.getElementById(id)) out.icons.push(id);
  }
  for (const el of document.querySelectorAll('h1,h2,h3,.btn,.item-title,.filter,.badge,.status,label,[role=tab]')) {
    if (!shown(el) || el.closest('.sr-only')) continue;
    const cs = getComputedStyle(el);
    if (cs.textOverflow === 'ellipsis' || cs.webkitLineClamp !== 'none') continue;
    if (el.scrollWidth > el.clientWidth + 2 && cs.whiteSpace === 'nowrap' && cs.overflow !== 'visible') out.cut.push((el.textContent || '').trim().slice(0, 40));
  }
  for (const el of document.querySelectorAll('button,.btn,.filter,.badge,[role=tab],.status')) {
    if (!shown(el)) continue;
    const text = (el.textContent || '').trim().replace(/\s+/g, ' ');
    if (text && text.length <= 32 && wrapsText(el)) out.wrapped.push(text.slice(0, 30));
  }
  for (const parent of document.querySelectorAll('body *')) {
    if (parent.children.length < 2 || !shown(parent)) continue;
    const rows = new Map();
    for (const el of parent.children) {
      if (!shown(el) || typeof el.className !== 'string' || !el.className.trim()) continue;
      const r = el.getBoundingClientRect();
      if (r.width < 40 || r.height < 20) continue;
      const key = el.tagName.toLowerCase() + '.' + el.className.trim().split(/\s+/)[0] + '@' + Math.round(r.top);
      if (!rows.has(key)) rows.set(key, []);
      rows.get(key).push(r.height);
    }
    for (const [key, hs] of rows) {
      const diff = Math.max(...hs) - Math.min(...hs);
      if (hs.length > 1 && diff >= 1 && diff <= 4) out.uneven.push(key.split('@')[0] + ' ' + diff.toFixed(1) + 'px');
    }
  }
  /* items in one row of a grid start at the same height: a margin meant for stacked fields must not push one down */
  for (const g of document.querySelectorAll('.grid-2, .grid-3, .figures')) {
    if (!shown(g)) continue;
    const cols = getComputedStyle(g).gridTemplateColumns.split(' ').filter(Boolean).length || 1;
    const kids = [...g.children].filter(shown);
    for (let i = 0; i + 1 < kids.length; i++) {
      if (Math.floor(i / cols) !== Math.floor((i + 1) / cols)) continue;
      const d = Math.abs(kids[i].getBoundingClientRect().top - kids[i + 1].getBoundingClientRect().top);
      if (d >= 1) { out.uneven.push(g.className.split(' ')[0] + ' row starts ' + Math.round(d) + 'px apart'); break; }
    }
  }
  out.uneven = [...new Set(out.uneven)];
  if (innerWidth < 500) {
    for (const el of document.querySelectorAll('a[href],button,input:not([type=hidden]),select,textarea')) {
      if (!shown(el) || el.closest('p, td .sub, .sr-only, .tag-item, label')) continue;
      /* a link inside a sentence is exempt (WCAG 2.5.8): its parent carries text of its own */
      if (el.tagName === 'A' && [...el.parentElement.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) continue;
      const r = el.getBoundingClientRect();
      if (el.type === 'checkbox' || el.type === 'radio') continue;
      if (r.width && r.height && (r.width < 24 || r.height < 24)) out.small.push((el.textContent || el.getAttribute('aria-label') || el.tagName).trim().slice(0, 30));
    }
  }
  return out;
}
"""

SWEEP_JS = r"""
() => {
/*WRAPS*/
  const out = {overflow: document.documentElement.scrollWidth - innerWidth, overlap: [], wrapped: []};
  const leaves = [];
  for (const el of document.querySelectorAll('header *, nav *, .page-head *, .record-head *, .ws-bar *')) {
    if (!shown(el) || el.closest('[hidden],[aria-hidden=true],.sr-only,.menu,dialog')) continue;
    const own = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()) || ['svg', 'IMG', 'INPUT'].includes(el.tagName);
    if (!own) continue;
    let floating = false;
    for (let a = el; a && !floating; a = a.parentElement) floating = getComputedStyle(a).position === 'fixed';
    if (floating) continue;
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2 || r.right < 0 || r.left > innerWidth) continue;
    leaves.push([el, r]);
  }
  const name = e => ((e.textContent || '').trim().slice(0, 20) || e.getAttribute('aria-label') || e.tagName.toLowerCase());
  for (let i = 0; i < leaves.length; i++) {
    for (let j = i + 1; j < leaves.length; j++) {
      const [a, ra] = leaves[i], [b, rb] = leaves[j];
      if (a.contains(b) || b.contains(a)) continue;
      const w = Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left);
      const h = Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top);
      if (w > 3 && h > 3) out.overlap.push(name(a) + ' / ' + name(b));
    }
  }
  out.overlap = [...new Set(out.overlap)];
  for (const el of document.querySelectorAll('.btn, .filter, [role=tab], .topnav a, .side-link')) {
    if (!shown(el)) continue;
    const text = (el.textContent || '').trim().replace(/\s+/g, ' ');
    if (text && text.length <= 32 && wrapsText(el)) out.wrapped.push(text.slice(0, 30));
  }
  return out;
}
"""
CHECK_JS = CHECK_JS.replace("/*WRAPS*/", WRAPS_FN)
SWEEP_JS = SWEEP_JS.replace("/*WRAPS*/", WRAPS_FN)

# WCAG 1.4.3 on the rendered page: each visible text run against the colour really behind it. Text over an
# image, a gradient or a positioned layer is skipped (the pixel behind it is unknown); see the screenshots.
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
    }
    let bg = [255, 255, 255, 1];
    for (let i = layers.length - 1; i >= 0; i--) bg = over(layers[i], bg);
    return bg;
  }
  function hidden(el) {
    if (el.closest('[aria-hidden="true"], .sr-only, [hidden], [inert]')) return true;
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) return true;
    let op = 1;
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const cs = getComputedStyle(n);
      if (cs.display === 'none' || cs.visibility === 'hidden') return true;
      op *= parseFloat(cs.opacity);
    }
    /* a disabled control is exempt (WCAG 1.4.3) */
    return op < 0.05 || !!el.closest(':disabled, [aria-disabled="true"]');
  }
  const seen = new Set(), fails = [];
  document.querySelectorAll('body *').forEach(el => {
    if (['SCRIPT', 'STYLE', 'svg', 'NOSCRIPT', 'OPTION', 'IFRAME'].includes(el.tagName)) return;
    const own = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 1);
    if (!own || hidden(el)) return;
    const cs = getComputedStyle(el);
    const bg = backdrop(el);
    if (!bg) return;
    let fg = parse(cs.color);
    if (fg[3] < 1) fg = over(fg, bg);
    const size = parseFloat(cs.fontSize), weight = parseInt(cs.fontWeight, 10) || 400;
    const need = size >= 24 || (size >= 18.66 && weight >= 700) ? 3 : 4.5, r = ratio(fg, bg);
    if (r + 0.005 >= need) return;
    const key = hex(fg) + hex(bg);
    if (seen.has(key)) return;
    seen.add(key);
    fails.push({ text: el.textContent.trim().replace(/\s+/g, ' ').slice(0, 40), ratio: Math.round(r * 100) / 100, need, fg: hex(fg), bg: hex(bg) });
  });
  return fails.slice(0, 10);
}"""

HOVER_MARK_JS = r"""
(limit) => {
  const kinds = new Map();
  let n = 0;
  for (const el of document.querySelectorAll('main a[href], main button, .list-item, table.data tbody tr, .side-link, .topnav a')) {
    if (n >= limit || el.offsetParent === null || el.closest('[hidden],[disabled],.menu,dialog')) continue;
    const r = el.getBoundingClientRect();
    if (r.width < 8 || r.height < 8) continue;
    const kind = el.tagName + '.' + ((typeof el.className === 'string' && el.className.trim().split(/\s+/)[0]) || '');
    if ((kinds.get(kind) || 0) >= 2) continue;
    kinds.set(kind, (kinds.get(kind) || 0) + 1);
    el.setAttribute('data-qa-h', n++);
  }
  return n;
}
"""

HOVER_SNAP_JS = r"""
(i) => {
  const el = document.querySelector('[data-qa-h="' + i + '"]');
  if (!el) return null;
  const box = e => [e.offsetLeft, e.offsetTop, e.offsetWidth, e.offsetHeight].join(',');
  const p = el.parentElement;
  return { self: box(el), sibs: p ? [...p.children].map(box).join(';') : '', height: document.documentElement.scrollHeight,
           label: ((el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 30) || el.getAttribute('aria-label') || el.tagName.toLowerCase()) };
}
"""

NO_MOTION_CSS = "*,*::before,*::after{transition:none!important;animation:none!important}"


def width_ranges(widths):
    """[1000, 980, 960, 700] with step 20 -> '960-1000, 700'."""
    if not widths:
        return ""
    ws = sorted(set(widths), reverse=True)
    step = min((a - b for a, b in zip(ws, ws[1:])), default=0) or 1
    out, start, prev = [], ws[0], ws[0]
    for w in ws[1:]:
        if prev - w > step:
            out.append(str(prev) if prev == start else "%d-%d" % (prev, start))
            start = w
        prev = w
    out.append(str(prev) if prev == start else "%d-%d" % (prev, start))
    return ", ".join(out)


def check_hover(page, limit=24):
    page.add_style_tag(content=NO_MOTION_CSS)
    moved = []
    for i in range(page.evaluate(HOVER_MARK_JS, limit)):
        el = page.locator('[data-qa-h="%d"]' % i)
        try:
            el.scroll_into_view_if_needed(timeout=500)
            box = el.bounding_box()
        except Exception:
            continue
        if not box or box["width"] < 1:
            continue
        before = page.evaluate(HOVER_SNAP_JS, i)
        page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        page.wait_for_timeout(30)
        after = page.evaluate(HOVER_SNAP_JS, i)
        page.mouse.move(0, 0)
        if before and after and (before["self"] != after["self"] or before["sibs"] != after["sibs"] or before["height"] != after["height"]):
            moved.append(before["label"])
    return moved


def launch(p):
    for ch in ("msedge", "chrome", None):
        try:
            return p.chromium.launch(channel=ch) if ch else p.chromium.launch()
        except Exception:
            continue
    raise SystemExit("No Chromium-based browser for Playwright. Install Edge or Chrome, or: python -m playwright install chromium")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("--pages", help="comma list of pages to check (default: every .html outside kit/)")
    ap.add_argument("--out", help="screenshot folder (default <folder>/qa)")
    ap.add_argument("--sweep", nargs="?", const="1440,360,20", metavar="FROM,TO,STEP")
    a = ap.parse_args()
    root = Path(a.folder).resolve()
    pages = [root / x for x in a.pages.split(",")] if a.pages else \
        [p for p in sorted(root.rglob("*.html")) if "kit" not in p.relative_to(root).parts and "qa" not in p.relative_to(root).parts
         and "app.css" in p.read_text(encoding="utf-8", errors="replace")]
    out = Path(a.out).resolve() if a.out else root / "qa"
    out.mkdir(parents=True, exist_ok=True)
    sweep = None
    if a.sweep:
        hi, lo, step = (list(map(int, a.sweep.split(","))) + [20])[:3]
        sweep = list(range(max(hi, lo), min(hi, lo) - 1, -abs(step)))
    fails, warns = [], []
    with sync_playwright() as p:
        browser = launch(p)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" and "Failed to load resource" not in m.text else None)
        for f in pages:
            rel = f.relative_to(root).as_posix()
            page.set_viewport_size({"width": 1440, "height": 900})
            page.goto(f.as_uri())
            states = page.evaluate("(document.body.getAttribute('data-states') || 'default').split(/\\s+/).filter(Boolean)")
            for st in states:
                for w, h in ((1440, 900), (390, 844)):
                    errors.clear()
                    page.set_viewport_size({"width": w, "height": h})
                    page.goto(f.as_uri() + "?state=" + st)
                    page.wait_for_timeout(250)
                    where = "%s [%s] @%d" % (rel, st, w)
                    r = page.evaluate(CHECK_JS)
                    for e in errors:
                        fails.append("%s: JS error: %s" % (where, e[:200]))
                    if r["overflow"] > 1:
                        fails.append("%s: page scrolls sideways by %dpx" % (where, r["overflow"]))
                    if r.get("gap", 0) > 8:
                        fails.append("%s: %dpx of empty page under the content (a hidden table or an absolute block makes the page longer; wrap a hidden table in div.sr-only)" % (where, r["gap"]))
                    for b in r["broken"]:
                        fails.append("%s: broken image %s" % (where, b))
                    for i in sorted(set(r["icons"])):
                        fails.append("%s: icon #%s is not in kit/icons.js" % (where, i))
                    if r["cut"]:
                        warns.append("%s: text cut off: %s" % (where, ", ".join(r["cut"][:3])))
                    if r["small"]:
                        warns.append("%s: %d tap targets under 24px (%s)" % (where, len(r["small"]), ", ".join(r["small"][:3])))
                    if r["wrapped"]:
                        warns.append("%s: short labels wrap onto two lines (%s)" % (where, ", ".join(r["wrapped"][:3])))
                    if r["uneven"]:
                        warns.append("%s: items in one row differ in height by 1-4px (%s)" % (where, ", ".join(r["uneven"][:3])))
                    if w == 1440:
                        for c in page.evaluate(CONTRAST_JS):
                            fails.append("%s: low contrast %.2f:1 (needs %g:1): %s on %s, \"%s\"" % (where, c["ratio"], c["need"], c["fg"], c["bg"], c["text"]))
                    page.screenshot(path=str(out / ("%s-%s-%d.png" % (rel.replace("/", "_").replace(".html", ""), st, w))), full_page=True)
                    if w == 1440 and st == states[0]:
                        moved = check_hover(page)
                        if moved:
                            warns.append("%s: hover moves the layout (%s)" % (where, ", ".join(moved[:3])))
            print("OK   %s: %d state(s) at 1440 and 390px" % (rel, len(states)))
            if sweep:
                page.set_viewport_size({"width": sweep[0], "height": 900})
                page.goto(f.as_uri())
                page.add_style_tag(content=NO_MOTION_CSS)
                page.wait_for_timeout(150)
                over, overlap, wrapped = {}, {}, {}
                for w in sweep:
                    page.set_viewport_size({"width": w, "height": 900})
                    page.wait_for_timeout(40)
                    r = page.evaluate(SWEEP_JS)
                    if r["overflow"] > 1:
                        over[w] = r["overflow"]
                    for o in r["overlap"]:
                        overlap.setdefault(o, []).append(w)
                    for t in r["wrapped"]:
                        wrapped.setdefault(t, []).append(w)
                if over:
                    fails.append("%s: page scrolls sideways (up to %dpx) at %s px" % (rel, max(over.values()), width_ranges(list(over))))
                for o, ws in list(overlap.items())[:4]:
                    fails.append("%s: header items overlap (%s) at %s px" % (rel, o, width_ranges(ws)))
                for t, ws in list(wrapped.items())[:4]:
                    warns.append("%s: label '%s' wraps at %s px" % (rel, t, width_ranges(ws)))
        browser.close()
    for w in warns:
        print("WARN " + w)
    for f in fails:
        print("FAIL " + f)
    if fails:
        print("\nQA FAILED: %d problem(s). Screenshots in %s" % (len(fails), out))
        sys.exit(1)
    print("\nQA PASSED. Screenshots in %s: open them and look." % out)


if __name__ == "__main__":
    main()
