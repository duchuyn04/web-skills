"""Browser QA for a built salon: every page at 1440 and 390 px, then the booking flow end to end.

    python scripts/qa.py sites/<slug>/dist            (add --shots to save a screenshot of every page)
    python scripts/qa.py sites/<slug>/dist --sweep    also narrow the main pages from 1440 to 360 px in 20 px steps

Checks per page: JavaScript errors, sideways overflow, broken images, text cut by its box, tap targets under 24 px
on phones, short button and chip labels that wrap, items in one row that differ in height by 1 to 4 px, and (at
1440 px on the main pages) links and cards whose hover moves the layout. Flow (native booking only): book a service
with an add-on, the empty contact step must be stopped, the confirmation shows a code, the lookup page finds it as
"Chờ xác nhận", the admin finds it, confirms it, the lookup shows "Đã xác nhận", a walk-in added in the admin shows
on the day calendar, a price changed in the admin shows in the booking summary, and the customer can cancel online.
Needs Python Playwright and Edge or Chrome (on Windows run it with py -3.11 if python cannot import Playwright).
"""
import argparse
import json
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
    raise SystemExit("qa.py needs Playwright: python -m pip install playwright, or run with py -3.11 / python3")

# One run of text broken over two lines. Icon above label or a count badge beside it are separate nodes and
# do not count: only a single text node whose line boxes start at different heights.
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
"""

CHECK_JS = r"""
() => {
/*WRAPS*/  const out = {overflow: 0, broken: [], cut: [], small: []};
  out.overflow = document.documentElement.scrollWidth - innerWidth;
  for (const img of document.images) {
    if (img.closest('[hidden]') || img.offsetParent === null) continue;
    if (img.complete && img.naturalWidth === 0) out.broken.push(img.getAttribute('src'));
  }
  for (const el of document.querySelectorAll('h1,h2,h3,.btn,.chip,label,.badge')) {
    if (el.offsetParent === null) continue;
    const cs = getComputedStyle(el);
    if (cs.overflow === 'hidden' || cs.webkitLineClamp !== 'none') continue;
    if (el.scrollWidth > el.clientWidth + 2 && cs.whiteSpace === 'nowrap') out.cut.push((el.textContent || '').trim().slice(0, 40));
  }
  out.wrapped = [];
  // A short button or chip label that breaks onto a second line reads as two controls.
  for (const el of document.querySelectorAll('button,.btn,.chip,.badge,[role=tab]')) {
    if (el.offsetParent === null) continue;
    const text = (el.textContent || '').trim().replace(/\s+/g, ' ');
    if (!text || text.length > 32) continue;
    if (wrapsText(el)) out.wrapped.push(text.slice(0, 30));
  }
  out.uneven = [];
  // Items of one kind sitting in one row should be one height: 1 to 4 px off is a slip, not a choice.
  for (const parent of document.querySelectorAll('body *')) {
    if (parent.children.length < 2 || parent.offsetParent === null) continue;
    const rows = new Map();
    for (const el of parent.children) {
      if (el.offsetParent === null || !el.className || typeof el.className !== 'string') continue;
      const r = el.getBoundingClientRect();
      if (r.width < 40 || r.height < 20) continue;
      const key = el.tagName + '.' + el.className.trim().split(/\s+/)[0] + '@' + Math.round(r.top);
      if (!rows.has(key)) rows.set(key, []);
      rows.get(key).push(r.height);
    }
    for (const [key, hs] of rows) {
      if (hs.length < 2) continue;
      const diff = Math.max(...hs) - Math.min(...hs);
      if (diff >= 1 && diff <= 4) out.uneven.push(key.split('@')[0].toLowerCase() + ' ' + diff.toFixed(1) + 'px');
    }
  }
  out.uneven = [...new Set(out.uneven)];
  if (innerWidth < 500) {
    for (const el of document.querySelectorAll('a[href],button,input,select')) {
      if (el.offsetParent === null || el.closest('[hidden],.sr,.skip,.crumbs,.ftr,.tbl,p,td,dd,small')) continue;
      const r = el.getBoundingClientRect();
      if (r.width && r.height && (r.width < 24 || r.height < 24) && el.type !== 'checkbox' && el.type !== 'radio') out.small.push((el.textContent || el.getAttribute('aria-label') || el.tagName).trim().slice(0, 30));
    }
  }
  return out;
}
"""

# Run at every step of --sweep: what breaks between the fixed widths (a header that overlaps at 900px).
SWEEP_JS = r"""
() => {
/*WRAPS*/  const out = {overflow: document.documentElement.scrollWidth - innerWidth, overlap: [], wrapped: []};
  // Header and nav items drawn over each other: each leaf with its own text or icon is one box.
  const leaves = [];
  for (const el of document.querySelectorAll('header *, nav *')) {
    if (el.offsetParent === null || el.closest('[hidden],[aria-hidden=true],.sr')) continue;
    const own = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()) || el.tagName === 'svg' || el.tagName === 'IMG' || el.tagName === 'INPUT';
    if (!own) continue;
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || +cs.opacity === 0) continue;
    // A fixed bar (bottom tabs on phones, a cookie strip) floats over the page on purpose.
    let floating = false;
    for (let a = el; a && !floating; a = a.parentElement) floating = getComputedStyle(a).position === 'fixed';
    if (floating) continue;
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2 || r.right < 0 || r.left > innerWidth) continue;
    leaves.push([el, r]);
  }
  for (let i = 0; i < leaves.length; i++) {
    for (let j = i + 1; j < leaves.length; j++) {
      const [a, ra] = leaves[i], [b, rb] = leaves[j];
      if (a.contains(b) || b.contains(a)) continue;
      const w = Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left);
      const h = Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top);
      if (w > 3 && h > 3) {
        const name = e => ((e.textContent || '').trim().slice(0, 20) || e.getAttribute('aria-label') || e.tagName.toLowerCase());
        out.overlap.push(name(a) + ' / ' + name(b));
      }
    }
  }
  out.overlap = [...new Set(out.overlap)];
  for (const el of document.querySelectorAll('header button, header .btn, nav a, nav button, .btn')) {
    if (el.offsetParent === null) continue;
    const text = (el.textContent || '').trim().replace(/\s+/g, ' ');
    if (!text || text.length > 32) continue;
    if (wrapsText(el)) out.wrapped.push(text.slice(0, 30));
  }
  return out;
}
"""

# Hover must not move the layout: a border that appears, a bold label, a line that opens below the item push
# everything after it. Offsets ignore transforms, so a lift drawn with translate is not counted here.
HOVER_MARK_JS = r"""
(limit) => {
  const kinds = new Map();
  let n = 0;
  for (const el of document.querySelectorAll('main a[href], main button, main [class*=card], main .pc, header a[href], header button')) {
    if (n >= limit || el.offsetParent === null || el.closest('[hidden],[disabled]')) continue;
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
  const parent = el.parentElement;
  return {
    self: box(el),
    sibs: parent ? [...parent.children].map(box).join(';') : '',
    height: document.documentElement.scrollHeight,
    label: ((el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 30) || el.getAttribute('aria-label') || el.tagName.toLowerCase()),
  };
}
"""

CHECK_JS = CHECK_JS.replace("/*WRAPS*/", WRAPS_FN)
SWEEP_JS = SWEEP_JS.replace("/*WRAPS*/", WRAPS_FN)


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


def check_hover(page, limit=30):
    """Hover a sample of links, buttons and cards; return the labels of those that moved the layout."""
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




def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dist")
    ap.add_argument("--shots", action="store_true")
    ap.add_argument("--sweep", nargs="?", const="1440,360,20", metavar="FROM,TO,STEP")
    a = ap.parse_args()
    sweep = None
    if a.sweep:
        hi, lo, step_ = (list(map(int, a.sweep.split(","))) + [20])[:3]
        sweep = list(range(max(hi, lo), min(hi, lo) - 1, -abs(step_)))
    dist = Path(a.dist).resolve()
    rep = json.loads((dist / "build-report.json").read_text(encoding="utf-8"))
    base = dist.as_uri()
    qa = dist / "qa"
    qa.mkdir(exist_ok=True)
    fails, warns = [], []
    main_pages = [p for p in ("index.html", "bang-gia.html", "dat-lich.html", "mau-nail.html", "admin/index.html",
                              "admin/calendar.html", "admin/appointments.html") if p in rep["pages"]]

    with sync_playwright() as p:
        browser = None
        for ch in ("msedge", "chrome", None):
            try:
                browser = p.chromium.launch(channel=ch) if ch else p.chromium.launch()
                break
            except Exception:
                continue
        if not browser:
            raise SystemExit("No Chromium-based browser found for Playwright.")
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN")
        page = ctx.new_page()
        page.on("dialog", lambda d: d.accept())
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" and "Failed to load resource" not in m.text else None)
        page.on("requestfailed", lambda r: errors.append("missing file " + r.url) if r.url.startswith("file:") else None)
        page.goto(base + "/admin/login.html")
        slug = page.evaluate("window.SALON.salon.slug")
        pre = "nail:%s:" % slug
        clear = "([p]) => Object.keys(localStorage).filter(k => k.startsWith(p)).forEach(k => localStorage.removeItem(k))"
        page.evaluate(clear, [pre])
        page.evaluate("([p]) => localStorage.setItem(p + 'adm:staff', JSON.stringify({name: 'QA', role: 'Chủ tiệm'}))", [pre])

        def url(rel):
            u = base + "/" + rel
            if rel == "admin/appointment.html":
                u += "?code=" + page.evaluate("NS.all().length ? NS.all()[NS.all().length - 1].code : ''")
            elif rel == "admin/customer.html":
                u += "?key=" + page.evaluate("NS.customers().length ? encodeURIComponent(NS.customers()[0].key) : ''")
            return u

        # 1. every page at two widths
        for w, h in ((1440, 900), (390, 844)):
            page.set_viewport_size({"width": w, "height": h})
            for rel in rep["pages"]:
                errors.clear()
                page.goto(url(rel))
                page.wait_for_timeout(200)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(120)
                page.evaluate("window.scrollTo(0, 0)")
                r = page.evaluate(CHECK_JS)
                where = "%s @%d" % (rel, w)
                for e in errors:
                    fails.append("%s: JS error: %s" % (where, e[:200]))
                if r["overflow"] > 1:
                    fails.append("%s: page scrolls sideways by %dpx" % (where, r["overflow"]))
                for b in r["broken"]:
                    fails.append("%s: broken image %s" % (where, b))
                for c in r["cut"][:3]:
                    warns.append("%s: text cut off: %s" % (where, c))
                if r["small"]:
                    warns.append("%s: %d tap targets under 24px (%s)" % (where, len(r["small"]), ", ".join(r["small"][:3])))
                if r["wrapped"]:
                    warns.append("%s: %d short labels wrap onto two lines (%s)" % (where, len(r["wrapped"]), ", ".join(r["wrapped"][:3])))
                if r["uneven"]:
                    warns.append("%s: items in one row differ in height by 1-4px (%s)" % (where, ", ".join(r["uneven"][:3])))
                if a.shots or rel in ("index.html", "dat-lich.html", "admin/index.html", "admin/calendar.html"):
                    page.screenshot(path=str(qa / ("%s-%d.png" % (rel.replace("/", "_").replace(".html", ""), w))), full_page=True)
                if w == 1440 and rel in main_pages:
                    moved = check_hover(page)
                    if moved:
                        warns.append("%s: hover moves the layout (%s)" % (where, ", ".join(moved[:3])))

        # 2. sweep widths on the main pages
        if sweep:
            for rel in main_pages:
                bad = {"overflow": [], "overlap": [], "wrapped": []}
                page.goto(url(rel))
                for w in sweep:
                    page.set_viewport_size({"width": w, "height": 900})
                    page.wait_for_timeout(40)
                    r = page.evaluate(SWEEP_JS)
                    for k in bad:
                        if (r[k] > 1) if k == "overflow" else r[k]:
                            bad[k].append(w)
                if bad["overflow"]:
                    fails.append("%s: scrolls sideways at %s px" % (rel, width_ranges(bad["overflow"])))
                if bad["overlap"]:
                    fails.append("%s: header items overlap at %s px" % (rel, width_ranges(bad["overlap"])))
                if bad["wrapped"]:
                    warns.append("%s: button labels wrap at %s px" % (rel, width_ranges(bad["wrapped"])))

        # 3. booking flow
        page.set_viewport_size({"width": 1440, "height": 900})
        page.goto(base + "/index.html")
        mode = page.evaluate("window.SALON.booking.mode")

        def step(msg, ok):
            if not ok:
                fails.append("flow: " + msg)
            return ok

        if mode != "native":
            warns.append("booking mode is %s: the booking flow check is skipped" % mode)
        else:
            errors.clear()
            svc = page.evaluate("(SALON.services.filter(s => !s.hidden && s.addons.length)[0] || SALON.services.filter(s => !s.hidden)[0]).id")
            page.goto(base + "/dat-lich.html?service=" + svc)
            page.wait_for_timeout(200)
            step("the service from ?service= is not ticked", page.locator("input[name=svc][value='%s']" % svc).is_checked())
            addon = page.locator("[data-addons-for='%s'] input[name=addon]" % svc)
            if addon.count():
                addon.first.check()
            page.click("[data-step='1'] [data-next]")
            if page.locator("[data-step='2'] [data-next]").is_visible():
                page.click("[data-step='2'] [data-next]")
            page.wait_for_timeout(150)
            slot = page.locator("[data-bk-slots] input[name=time]")
            days = page.locator("[data-bk-days] input:not([disabled])")
            k = 0
            while not slot.count() and k < min(6, days.count() - 1):
                k += 1
                days.nth(k).check(force=True)
                page.wait_for_timeout(100)
            if step("no free slot in the next days", slot.count() > 0):
                slot.first.check(force=True)
                page.click("[data-step='3'] [data-next]")
                page.click("[data-submit]")
                step("an empty contact step was not stopped", page.locator("[data-err='4']").is_visible())
                page.fill("input[name=name]", "Khách QA")
                page.fill("input[name=phone]", "0912 345 678")
                page.fill("textarea[name=note]", "Kiểm tra tự động")
                page.click("[data-submit]")
                page.wait_for_timeout(250)
                code = page.inner_text("[data-done-code]").strip() if page.locator("[data-bk-done]").is_visible() else ""
                if step("the booking was not confirmed on screen", bool(code)):
                    lookup = base + "/lich-hen.html?code=%s&phone=0912345678" % code
                    page.goto(lookup)
                    page.wait_for_timeout(200)
                    step("lookup does not show the booking as Chờ xác nhận", "Chờ xác nhận" in page.inner_text("[data-lookup-result]"))
                    page.goto(base + "/admin/appointments.html?q=" + code)
                    page.wait_for_timeout(300)
                    row = page.locator("tr[data-go='%s']" % code)
                    if step("the admin list does not show " + code, row.count() == 1):
                        row.locator("[data-act=confirmed]").click()
                        page.wait_for_timeout(200)
                        page.goto(lookup)
                        page.wait_for_timeout(200)
                        step("lookup does not show Đã xác nhận after the admin confirmed", "Đã xác nhận" in page.inner_text("[data-lookup-result]"))
                        cancel = page.locator("[data-cancel]")
                        if cancel.count():
                            cancel.click()
                            page.wait_for_timeout(150)
                            step("cancelling online did not show Đã hủy", "Đã hủy" in page.inner_text("[data-lookup-result]"))
                    page.goto(base + "/admin/appointment.html?code=" + code)
                    page.wait_for_timeout(200)
                    step("the appointment page does not open", code in page.inner_text("main"))
            # a walk-in added in the admin shows on the day calendar
            page.goto(base + "/admin/calendar.html")
            page.wait_for_timeout(200)
            open_today = page.evaluate("(() => { const l = document.querySelector('[data-cal-loc]'); const id = l ? l.value : SALON.locations[0].id; return NS.hoursOn(id, NS.today()); })()")
            page.click("[data-new-appt]")
            page.fill("[data-new-form] input[name=name]", "Khách vãng lai QA")
            page.fill("[data-new-form] input[name=phone]", "0987654321")
            page.select_option("[data-new-form] select[name=svc]", svc)
            page.fill("[data-new-form] input[name=time]", page.evaluate("h => NS.hm(h ? h[0] : 600)", open_today))
            page.click("[data-new-form] button[type=submit]")
            page.wait_for_timeout(250)
            step("a walk-in added in the admin was not saved", page.evaluate("NS.all().filter(a => a.customer.name === 'Khách vãng lai QA').length") == 1)
            if open_today:
                step("the walk-in does not show on today's calendar", page.locator(".blk:has-text('Khách vãng lai QA')").count() == 1)
            # a price changed in the admin shows in the booking summary
            page.goto(base + "/admin/services.html")
            page.wait_for_timeout(200)
            inp = page.locator("input[data-edit=price][data-id='%s']" % svc)
            inp.fill("123000")
            inp.dispatch_event("change")
            page.goto(base + "/dat-lich.html?service=" + svc)
            page.wait_for_timeout(200)
            step("a price changed in the admin does not show in the booking summary", "123.000" in page.inner_text("[data-sum-list]"))
            for e in errors:
                fails.append("flow: JS error: " + e[:200])
        page.evaluate(clear, [pre])
        browser.close()

    for w in warns:
        print("WARN", w)
    for f in fails:
        print("FAIL", f)
    print("Screenshots in", qa)
    if fails:
        print("QA FAILED: %d problems" % len(fails))
        sys.exit(1)
    print("QA PASSED (%d pages, %d warnings)" % (len(rep["pages"]), len(warns)))


if __name__ == "__main__":
    main()
