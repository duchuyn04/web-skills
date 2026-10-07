"""Browser QA for a built shop: every page at 1440 and 390 px, then the full buying flow and the admin flow.

    python scripts/qa.py sites/<slug>/dist            (add --shots to save a screenshot of every page)
    python scripts/qa.py sites/<slug>/dist --sweep    also narrow the sample pages from 1440 to 360 px in 20 px steps

Checks per page: JavaScript errors, sideways overflow, broken images, text cut by its box, tap targets
under 24 px on mobile, short button and chip labels that wrap onto two lines, items of one kind in one row
that differ in height by 1 to 4 px, and (at 1440 px on the sample pages) links, buttons and cards whose hover
moves the layout. --sweep reports the width ranges where a page scrolls sideways, header items overlap or a
button label wraps: the fixed widths miss a header that breaks at 900 px or a table that overflows at 360. Flow: product page, choose a variant, add to cart, voucher, checkout with
validation, order page, tracking, admin login, the order in the admin list, confirm it, see the new status
in tracking, change a price in admin and see it on the product page. Needs Python Playwright and Edge or
Chrome (on this machine run it with py -3.11).
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
  for (const el of document.querySelectorAll('h1,h2,h3,.btn,.pc-name,.chip,label,.badge')) {
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
      if (el.offsetParent === null || el.closest('[hidden],.sr,.rail-track,.crumbs,.ftr,.pc-specs,p,td,dd,small')) continue;
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


def reveal(page, selector):
    """Multi-step checkouts keep every field in one form but show them step by step. Advance with [data-step-next]
    (validating the visible fields) until the element can be used."""
    for _ in range(6):
        if page.locator(selector).first.is_visible():
            return
        nxt = page.locator("[data-step-next]:visible")
        if not nxt.count():
            return
        nxt.first.click()
        page.wait_for_timeout(120)


def press_place_or_next(page):
    po = page.locator("[data-place-order]")
    if po.first.is_visible():
        po.first.click()
    else:
        page.locator("[data-step-next]:visible").first.click()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dist")
    ap.add_argument("--shots", action="store_true")
    ap.add_argument("--quick", action="store_true", help="check a sample of pages (home, a category, a product, search, compare, cart, checkout, tracking, account) instead of all")
    ap.add_argument("--sweep", nargs="?", const="1440,360,20", metavar="FROM,TO,STEP",
                    help="after the fixed widths, narrow the sample pages from 1440 to 360 px in 20 px steps and report the "
                         "width ranges where the page scrolls sideways, header items overlap or a button label wraps")
    a = ap.parse_args()
    sweep = None
    if a.sweep:
        try:
            hi, lo, step = (list(map(int, a.sweep.split(","))) + [20])[:3]
            sweep = list(range(max(hi, lo), min(hi, lo) - 1, -abs(step)))
        except ValueError:
            ap.error("--sweep takes FROM,TO,STEP, for example 1440,360,20")
    dist = Path(a.dist).resolve()
    rep = json.loads((dist / "build-report.json").read_text(encoding="utf-8"))
    base = dist.as_uri()
    qa = dist / "qa"
    qa.mkdir(exist_ok=True)
    fails, warns = [], []
    slug = None

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
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" and "Failed to load resource" not in m.text else None)
        page.on("requestfailed", lambda r: errors.append("missing file " + r.url) if r.url.startswith("file:") else None)
        page.goto(base + "/index.html")
        slug = page.evaluate("window.SHOP.shop.slug")
        # log a staff member in so admin pages render
        page.evaluate("s => localStorage.setItem('shop:' + s + ':adm:staff', JSON.stringify({name: 'QA', role: 'Chủ cửa hàng'}))", slug)

        keep = ["index.html", "search.html", "compare.html", "cart.html", "checkout.html", "order.html", "track.html", "account/index.html", "account/login.html", "admin/index.html"]
        firsts = [next((p for p in rep["pages"] if p.startswith(pre)), None) for pre in ("c/", "p/", "policy/")]
        sample = [p for p in rep["pages"] if p in keep or p in firsts]

        def page_url(rel):
            url = base + "/" + rel
            if rel == "admin/order.html":
                url += "?code=" + page.evaluate("window.SEED && SEED.orders.length ? 'DH' + SEED.orders[SEED.orders.length - 1][0] : ''")
            elif rel == "admin/product.html":
                url += "?id=" + page.evaluate("window.SHOP.products[0].id")
            return url

        # 1. every page, two widths
        for w, h in ((1440, 900), (390, 844)):
            page.set_viewport_size({"width": w, "height": h})
            pages_to_check = sample if a.quick else rep["pages"]
            for rel in pages_to_check:
                errors.clear()
                page.goto(page_url(rel))
                page.wait_for_timeout(150)
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
                if a.shots or rel in ("index.html", "admin/index.html"):
                    page.screenshot(path=str(qa / ("%s-%d.png" % (rel.replace("/", "_").replace(".html", ""), w))), full_page=True)
                if w == 1440 and rel in sample:
                    moved = check_hover(page)
                    if moved:
                        warns.append("%s: hover moves the layout (%s)" % (where, ", ".join(moved[:3])))
            print("OK   %d pages checked at %dpx" % (len(pages_to_check), w))

        # 1b. width sweep on the sample pages: what breaks between the fixed widths
        if sweep:
            for rel in sample:
                errors.clear()
                page.set_viewport_size({"width": sweep[0], "height": 900})
                page.goto(page_url(rel))
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
                for e in errors:
                    fails.append("%s sweep: JS error: %s" % (rel, e[:200]))
            print("OK   %d pages swept from %d to %dpx in %dpx steps" % (len(sample), sweep[0], sweep[-1], sweep[0] - sweep[1] if len(sweep) > 1 else 0))

        # 2. buying flow
        page.set_viewport_size({"width": 1440, "height": 900})
        page.evaluate("s => { for (const k of Object.keys(localStorage)) if (k.startsWith('shop:' + s + ':') && !k.endsWith('adm:staff')) localStorage.removeItem(k); }", slug)
        step = "open product"
        try:
            errors.clear()
            prod = page.evaluate("window.SHOP.products.find(p => p.variants[0].stock > 0 && p.options.length).id")
            page.goto(base + "/p/%s.html" % prod)
            step = "choose variant"
            btns = page.locator("[data-opt] [data-opt-btn]:not(.is-out)")
            if btns.count() > 1:
                btns.nth(1).click()
            price_txt = page.locator("[data-v-price]").inner_text()
            step = "add to cart"
            page.locator(".buybox [data-add-cart]").click()
            page.wait_for_timeout(100)
            assert page.evaluate("s => JSON.parse(localStorage.getItem('shop:' + s + ':cart') || '[]').length", slug) == 1, "cart is empty after Add to cart"
            step = "cart page"
            page.goto(base + "/cart.html")
            assert page.locator("[data-cart-list] .cart-row").count() == 1, "cart page shows no row"
            promo = page.evaluate("(window.SHOP.promotions || []).find(p => p.type !== 'shipping')")
            if promo:
                step = "voucher"
                page.fill("[data-voucher-input]", promo["code"])
                page.locator("[data-voucher-form] button").click()
                page.wait_for_timeout(100)
            step = "checkout validation"
            page.goto(base + "/checkout.html")
            press_place_or_next(page)
            assert page.locator("[aria-invalid=true]").count() >= 2, "empty checkout form was not stopped"
            step = "checkout fill"
            reveal(page, "input[name=name]")
            page.fill("input[name=name]", "Nguyễn Văn Kiểm")
            page.fill("input[name=phone]", "0912345678")
            reveal(page, "select[name=province]")
            page.select_option("select[name=province]", index=1)
            reveal(page, "input[name=ward]")
            page.fill("input[name=ward]", "Phường Bến Thành")
            reveal(page, "input[name=street]")
            page.fill("input[name=street]", "12 Lê Lợi")
            reveal(page, "[data-place-order]")
            page.locator("[data-place-order]").first.click()
            page.wait_for_url("**/order.html?code=*", timeout=5000)
            code = page.locator("[data-o-code]").inner_text().strip()
            assert code, "order page shows no code"
            step = "tracking"
            page.goto(base + "/track.html?code=%s&phone=0912345678" % code)
            assert "Chờ xác nhận" in page.locator("[data-t-status]").inner_text(), "tracking does not show the pending order"
            step = "admin order list"
            page.goto(base + "/admin/orders.html?q=" + code)
            assert page.locator("[data-orders] tbody tr").count() >= 1, "new order missing from admin list"
            step = "admin confirm"
            page.goto(base + "/admin/order.html?code=" + code)
            page.locator("[data-act=confirmed]").click()
            page.wait_for_timeout(300)
            page.goto(base + "/track.html?code=%s&phone=0912345678" % code)
            assert "Đã xác nhận" in page.locator("[data-t-status]").inner_text(), "admin status change not visible in tracking"
            step = "admin price change"
            page.goto(base + "/admin/product.html?id=" + prod)
            first = page.locator("[data-v-price]").first
            new_price = int(first.input_value()) - 100000
            first.fill(str(new_price))
            page.locator("[data-product-form] button[type=submit]").click()
            page.wait_for_timeout(100)
            page.goto(base + "/p/%s.html" % prod)
            shown = page.locator("[data-v-price]").inner_text()
            assert "{:,}".format(new_price).replace(",", ".") in shown or shown != price_txt, "admin price change not shown on the product page"
            step = "admin dashboard"
            page.goto(base + "/admin/index.html")
            assert page.locator("[data-kpis] .kpi").count() >= 4, "dashboard KPIs missing"
            assert page.locator("[data-chart=main] svg").count() == 1, "main chart missing"
            page.locator("[data-period-btn]").click()
            page.locator("[data-preset=lastmonth]").click()
            page.locator("[data-period-apply]").click()
            assert "/" in page.locator("[data-period-range]").inner_text(), "date range picker did not apply"
            for e in errors:
                fails.append("flow: JS error: %s" % e[:200])
            print("OK   buying flow: order %s placed, tracked, confirmed in admin; price edit reached the product page" % code)
        except Exception as e:
            fails.append("flow failed at '%s': %s" % (step, str(e).splitlines()[0][:300]))
            page.screenshot(path=str(qa / "flow-failure.png"), full_page=True)
        browser.close()

    for w in warns:
        print("WARN " + w)
    for f in fails:
        print("FAIL " + f)
    if fails:
        print("\nQA FAILED: %d problem(s). Screenshots in %s" % (len(fails), qa))
        sys.exit(1)
    print("\nQA PASSED. Screenshots in %s; open index and admin index and look at them." % qa)


if __name__ == "__main__":
    main()
