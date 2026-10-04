"""Probe how real BPO homepages animate: libraries, scroll reveals per element kind, parallax, pins, loops, hovers.
The results behind references/motion-research.md. Needs Playwright and Microsoft Edge.

py -3.11 scripts/research/motion_probe.py OUT_DIR [blueprint ids...]    then    py -3.11 scripts/research/motion_summary.py OUT_DIR
"""
import asyncio, json, sys, time
from pathlib import Path

BLUEPRINTS = Path(__file__).resolve().parents[2] / "templates" / "blueprints"
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
ONLY = set(sys.argv[2:])
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"

# Runs before any page script: log GSAP tween vars, WAAPI keyframes and IntersectionObserver use.
INIT = r"""
(() => {
  const log = window.__mp = { tweens: [], waapi: [], io: 0, split: 0 };
  const keep = v => {
    const o = {};
    for (const k in v) {
      const x = v[k];
      if (typeof x === 'number' || typeof x === 'string' || typeof x === 'boolean') o[k] = typeof x === 'string' ? x.slice(0, 60) : x;
      else if (k === 'scrollTrigger' && x && typeof x === 'object') {
        o.scrollTrigger = {};
        for (const s of ['scrub', 'pin', 'start', 'end', 'toggleActions']) if (x[s] !== undefined && typeof x[s] !== 'object' && typeof x[s] !== 'function') o.scrollTrigger[s] = x[s];
      } else if (k === 'stagger') o.stagger = typeof x === 'number' ? x : 'obj';
    }
    return o;
  };
  const wrap = g => {
    if (!g || g.__mpWrapped) return g;
    g.__mpWrapped = true;
    for (const m of ['to', 'from', 'fromTo', 'set']) {
      const orig = g[m];
      if (typeof orig !== 'function') continue;
      g[m] = function () {
        try {
          const a = arguments, t = a[0];
          const desc = t && t.nodeType ? (t.tagName + '.' + (t.className && t.className.baseVal === undefined ? String(t.className) : '')).slice(0, 80) : (typeof t === 'string' ? t.slice(0, 80) : (t && t.length ? 'list' + t.length : typeof t));
          if (log.tweens.length < 400) log.tweens.push({ m, t: desc, from: m === 'fromTo' ? keep(a[1] || {}) : null, v: keep((m === 'fromTo' ? a[2] : a[1]) || {}) });
        } catch (e) {}
        return orig.apply(this, arguments);
      };
    }
    return g;
  };
  let _g;
  try {
    Object.defineProperty(window, 'gsap', { configurable: true, get() { return _g; }, set(v) { _g = wrap(v); } });
  } catch (e) {}
  const an = Element.prototype.animate;
  Element.prototype.animate = function (kf, opts) {
    try {
      if (log.waapi.length < 200) log.waapi.push({ t: (this.tagName + '.' + String(this.className || '')).slice(0, 60), kf: JSON.stringify(kf).slice(0, 200), d: opts && (opts.duration || opts) });
    } catch (e) {}
    return an.apply(this, arguments);
  };
  const IO = window.IntersectionObserver;
  if (IO) window.IntersectionObserver = function (cb, o) { log.io++; return new IO(cb, o); };
  if (IO) window.IntersectionObserver.prototype = IO.prototype;
})();
"""

# Tag candidate elements and record their resting style.
SNAP = r"""
(tag) => {
  const vh = innerHeight;
  const kindOf = el => {
    const t = el.tagName;
    if (/^H[1-3]$/.test(t)) return 'heading';
    if (t === 'IMG' || t === 'PICTURE' || t === 'VIDEO') return 'media';
    if (t === 'A' || t === 'BUTTON') return 'button';
    return 'card';
  };
  if (tag) {
    let n = 0;
    const pick = [];
    document.querySelectorAll('h1,h2,h3').forEach(e => pick.push(e));
    document.querySelectorAll('img,picture,video').forEach(e => { const r = e.getBoundingClientRect(); if (r.width > 180 && r.height > 120) pick.push(e); });
    document.querySelectorAll('a,button').forEach(e => { const cs = getComputedStyle(e); if (cs.backgroundColor !== 'rgba(0, 0, 0, 0)' && e.getBoundingClientRect().height > 30 && e.getBoundingClientRect().height < 80) pick.push(e); });
    document.querySelectorAll('[class*=card],[class*=Card],[class*=tile],[class*=item]').forEach(e => { const r = e.getBoundingClientRect(); if (r.width > 160 && r.width < 700 && r.height > 120) pick.push(e); });
    const seen = new Set();
    for (const e of pick) {
      if (seen.has(e) || n >= 260) continue;
      const r = e.getBoundingClientRect();
      if (r.top + scrollY < vh * 0.9) continue; // only elements below the first screen
      seen.add(e); e.setAttribute('data-mp', String(n++)); e.setAttribute('data-mp-kind', kindOf(e));
    }
  }
  const out = {};
  document.querySelectorAll('[data-mp]').forEach(e => {
    // effective opacity and transform over the element and up to 3 wrappers
    let op = 1, tr = [], clip = null, filt = null, x = e;
    for (let i = 0; i < 4 && x && x !== document.body; i++, x = x.parentElement) {
      const cs = getComputedStyle(x);
      op *= parseFloat(cs.opacity);
      if (cs.transform !== 'none') tr.push(i + ':' + cs.transform);
      if (cs.translate && cs.translate !== 'none') tr.push(i + ':tr ' + cs.translate);
      if (cs.scale && cs.scale !== 'none') tr.push(i + ':sc ' + cs.scale);
      if (!clip && cs.clipPath !== 'none') clip = i + ':' + cs.clipPath.slice(0, 80);
      if (!filt && cs.filter !== 'none') filt = cs.filter.slice(0, 60);
    }
    const cs = getComputedStyle(e);
    const img = e.tagName === 'IMG' ? e : e.querySelector('img');
    const imgT = img && img !== e ? getComputedStyle(img).transform : null;
    // split text: many inline children with their own transform or opacity
    let split = 0;
    if (/^H[1-3]$/.test(e.tagName)) e.querySelectorAll('span,div').forEach(s => { const c = getComputedStyle(s); if (c.transform !== 'none' || parseFloat(c.opacity) < 1 || c.display === 'inline-block') split++; });
    const r = e.getBoundingClientRect();
    out[e.getAttribute('data-mp')] = { k: e.getAttribute('data-mp-kind'), op: +op.toFixed(3), tr: tr.join('|').slice(0, 300), clip, filt, imgT, split,
      top: Math.round(r.top), trans: cs.transition.slice(0, 120), anim: cs.animationName !== 'none' ? cs.animationName + ' ' + cs.animationDuration : null,
      cls: String(e.className && e.className.baseVal === undefined ? e.className : '').slice(0, 80),
      aos: e.getAttribute('data-aos') || (e.closest('[data-aos]') && e.closest('[data-aos]').getAttribute('data-aos')) || null };
  });
  return out;
}
"""

LIBS = r"""
() => {
  const w = window, d = document;
  const st = w.ScrollTrigger && w.ScrollTrigger.getAll ? w.ScrollTrigger.getAll() : [];
  const scripts = [...d.scripts].map(s => s.src).filter(Boolean).join(' ').toLowerCase();
  const anims = d.getAnimations ? d.getAnimations().map(a => ({ n: a.animationName || a.constructor.name, it: a.effect && a.effect.getTiming ? a.effect.getTiming().iterations : null, d: a.effect && a.effect.getTiming ? a.effect.getTiming().duration : null, t: a.effect && a.effect.target ? (a.effect.target.tagName + '.' + String(a.effect.target.className || '')).slice(0, 60) : '' })) : [];
  let sticky = 0;
  d.querySelectorAll('section,div').forEach(e => { if (sticky < 50 && getComputedStyle(e).position === 'sticky') sticky++; });
  return {
    gsap: !!w.gsap || /gsap|greensock|tweenmax/.test(scripts), gsapVer: w.gsap && w.gsap.version,
    st: st.length, stPin: st.filter(s => s.pin).length, stScrub: st.filter(s => s.vars && s.vars.scrub).length,
    aos: !!w.AOS || !!d.querySelector('[data-aos]'), aosN: d.querySelectorAll('[data-aos]').length,
    aosKinds: [...new Set([...d.querySelectorAll('[data-aos]')].map(e => e.getAttribute('data-aos')))].slice(0, 20),
    webflow: !!w.Webflow || !!d.querySelector('[data-wf-page]'), wfIx: d.querySelectorAll('[data-w-id]').length,
    framer: !!d.querySelector('[data-framer-name],[data-framer-component-type]'),
    lenis: !!w.lenis || !!w.Lenis || d.documentElement.classList.contains('lenis'), locomotive: !!d.querySelector('[data-scroll-container]'),
    swiper: !!w.Swiper || !!d.querySelector('.swiper'), slick: !!d.querySelector('.slick-slider'), splide: !!d.querySelector('.splide'),
    lottie: !!w.lottie || !!w.bodymovin || !!d.querySelector('lottie-player,dotlottie-player,[data-animation-path]'),
    three: !!w.THREE || /three(\.min)?\.js/.test(scripts), wow: !!w.WOW || !!d.querySelector('.wow'),
    splitting: !!d.querySelector('[class*=split],[data-splitting],.char,.word,.line'),
    video: d.querySelectorAll('video').length, autoplay: d.querySelectorAll('video[autoplay]').length,
    sticky, anims: anims.slice(0, 80), mp: w.__mp || null, h: d.documentElement.scrollHeight
  };
}
"""

HOVER = r"""
() => {
  // CSS :hover rules that move or scale things (same-origin sheets only)
  const out = { transform: 0, bg: 0, sample: [] };
  for (const sh of document.styleSheets) {
    let rules; try { rules = sh.cssRules; } catch (e) { continue; }
    const walk = rs => { for (const r of rs) {
      if (r.cssRules && !r.selectorText) { walk(r.cssRules); continue; }
      if (!r.selectorText || !/:hover/.test(r.selectorText)) continue;
      const s = r.style;
      if (s.transform || s.translate || s.scale) { out.transform++; if (out.sample.length < 15) out.sample.push((r.selectorText.slice(0, 60) + ' { ' + (s.transform || s.translate || s.scale) + ' }')); }
      if (s.backgroundSize || s.backgroundPosition || /scaleX|inset/.test(s.cssText)) out.bg++;
    } };
    walk(rules);
  }
  return out;
}
"""


async def probe(browser, bid, url):
    ctx = await browser.new_context(viewport={"width": 1440, "height": 900}, user_agent=UA, locale="en-US")
    page = await ctx.new_page()
    await page.add_init_script(INIT)
    res = {"id": bid, "url": url}
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=45000)
        try:
            await page.wait_for_load_state("load", timeout=20000)
        except Exception:
            pass
        await page.wait_for_timeout(3000)
        # close cookie banners that cover the page
        for sel in ["#onetrust-accept-btn-handler", "button:has-text('Accept all')", "button:has-text('Accept All')", "button:has-text('Accept')", "button:has-text('I agree')", "button:has-text('Got it')"]:
            try:
                b = page.locator(sel).first
                if await b.is_visible(timeout=300):
                    await b.click(timeout=1000)
                    break
            except Exception:
                pass
        before = await page.evaluate(SNAP, True)
        h = await page.evaluate("document.documentElement.scrollHeight")
        entered, after, parallax = {}, {}, {}
        y = 0
        steps = 0
        while y < h and steps < 60:
            y += 450
            steps += 1
            await page.evaluate("y => window.scrollTo(0, y)", y)
            await page.wait_for_timeout(120)
            s0 = await page.evaluate(SNAP, False)
            for k, v in s0.items():
                if k not in entered and 0 < v["top"] < 900 * 0.8:
                    entered[k] = v
            await page.wait_for_timeout(1300)
            s1 = await page.evaluate(SNAP, False)
            for k, v in s1.items():
                if k in entered and k not in after:
                    after[k] = v
            # parallax: move 150px more and compare transforms of elements still on screen
            await page.evaluate("y => window.scrollTo(0, y)", y + 150)
            await page.wait_for_timeout(250)
            s2 = await page.evaluate(SNAP, False)
            for k, v in s2.items():
                a = s1.get(k)
                if a and 100 < a["top"] < 800 and a["tr"] != v["tr"] and k not in parallax:
                    parallax[k] = [a["tr"], v["tr"], a["imgT"], v["imgT"]]
            h = await page.evaluate("document.documentElement.scrollHeight")
        res["libs"] = await page.evaluate(LIBS)
        res["hover"] = await page.evaluate(HOVER)
        res["elements"] = {k: {"before": before.get(k), "enter": entered.get(k), "after": after.get(k)} for k in before}
        res["parallax"] = parallax
        res["ok"] = True
    except Exception as e:
        res["ok"] = False
        res["error"] = str(e)[:300]
    finally:
        await ctx.close()
    (OUT / (bid + ".json")).write_text(json.dumps(res), encoding="utf-8")
    print(("ok  " if res.get("ok") else "ERR ") + bid, flush=True)


async def main():
    from playwright.async_api import async_playwright
    rows = []
    for f in sorted(BLUEPRINTS.glob("*.json")):
        b = json.loads(f.read_text(encoding="utf-8"))
        rows.append((b["id"], b["source"]["url"]))
    rows = [r for r in rows if (not ONLY or r[0] in ONLY) and not (OUT / (r[0] + ".json")).exists()]
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="msedge", args=["--disable-blink-features=AutomationControlled"])
        sem = asyncio.Semaphore(4)

        async def run(r):
            async with sem:
                await probe(browser, r[0], r[1])
        await asyncio.gather(*(run(r) for r in rows))
        await browser.close()


asyncio.run(main())
