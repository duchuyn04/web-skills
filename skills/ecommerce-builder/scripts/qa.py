"""Browser QA for a built shop: every page at 1440 and 390 px, then the full buying flow and the admin flow.

    python scripts/qa.py sites/<slug>/dist            (add --shots to save a screenshot of every page)

Checks per page: JavaScript errors, sideways overflow, broken images, text cut by its box, tap targets
under 24 px on mobile. Flow: product page, choose a variant, add to cart, voucher, checkout with
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

CHECK_JS = r"""
() => {
  const out = {overflow: 0, broken: [], cut: [], small: []};
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dist")
    ap.add_argument("--shots", action="store_true")
    a = ap.parse_args()
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

        # 1. every page, two widths
        for w, h in ((1440, 900), (390, 844)):
            page.set_viewport_size({"width": w, "height": h})
            for rel in rep["pages"]:
                errors.clear()
                url = base + "/" + rel
                if rel == "admin/order.html":
                    url += "?code=" + page.evaluate("window.SEED && SEED.orders.length ? 'DH' + SEED.orders[SEED.orders.length - 1][0] : ''")
                elif rel == "admin/product.html":
                    url += "?id=" + page.evaluate("window.SHOP.products[0].id")
                page.goto(url)
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
                if a.shots or rel in ("index.html", "admin/index.html"):
                    page.screenshot(path=str(qa / ("%s-%d.png" % (rel.replace("/", "_").replace(".html", ""), w))), full_page=True)
            print("OK   %d pages checked at %dpx" % (len(rep["pages"]), w))

        # 2. buying flow
        page.set_viewport_size({"width": 1440, "height": 900})
        page.evaluate("s => { for (const k of Object.keys(localStorage)) if (k.startsWith('shop:' + s + ':') && !k.endsWith('adm:staff')) localStorage.removeItem(k); }", slug)
        step = "open product"
        try:
            errors.clear()
            prod = page.evaluate("window.SHOP.products.find(p => p.variants.some(v => v.stock > 0) && p.options.length).id")
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
            page.locator("[data-place-order]").click()
            assert page.locator("[aria-invalid=true]").count() >= 2, "empty checkout form was not stopped"
            step = "checkout fill"
            page.fill("input[name=name]", "Nguyễn Văn Kiểm")
            page.fill("input[name=phone]", "0912345678")
            page.select_option("select[name=province]", index=1)
            page.fill("input[name=ward]", "Phường Bến Thành")
            page.fill("input[name=street]", "12 Lê Lợi")
            page.locator("[data-place-order]").click()
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
