#!/usr/bin/env python3
"""Visual QA for a built page. Needs Python Playwright (pip install playwright).
Uses the installed Edge or Chrome, so no browser download is required on Windows.

Usage:
    python qa_screenshot.py dist                  screenshots at 1440, 768 and 390 px plus layout checks
    python qa_screenshot.py dist --sections       also one image per section and width (dist/qa/sections-<width>)
    python qa_screenshot.py dist --widths 1280,390
    python qa_screenshot.py dist --no-motion      skip the frame-rate check
    python qa_screenshot.py dist --cvd            also save colour-vision screenshots (qa/cvd-*.png) to review
    python qa_screenshot.py dist --sweep          also narrow the page from 1440 to 360 px in 20 px steps

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
    - with --sweep: the width ranges between 1440 and 360 px where something sticks out sideways or header
      items overlap (fail), and where a short button or nav label wraps onto two lines (warning)
Look at every screenshot yourself after the script passes.
"""
import argparse
import json
import re
import sys
for _stream in (sys.stdout, sys.stderr):  # Vietnamese text must not crash printing on a cp1252 console or pipe
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")
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

# Run at every step of --sweep: header and nav items drawn over each other, and short button or link labels
# broken over two lines. The fixed widths miss a nav that collides at 1100 px or a button that wraps at 900.
SWEEP_JS = r"""
() => {
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
  const shown = (el) => {
    for (let p = el; p; p = p.parentElement) {
      const s = getComputedStyle(p);
      if (s.display === 'none' || s.visibility === 'hidden' || s.opacity === '0') return false;
    }
    return true;
  };
  const leaves = [];
  for (const el of document.querySelectorAll('header *, nav *')) {
    if (el.closest('[hidden],[aria-hidden="true"],.bl-sr-only,[inert]')) continue;
    const own = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()) || ['svg', 'IMG', 'INPUT'].includes(el.tagName);
    if (!own || !shown(el)) continue;
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2 || r.right < 0 || r.left > innerWidth || r.bottom < 0) continue;
    leaves.push([el, r]);
  }
  const label = e => ((e.textContent || '').trim().slice(0, 24) || e.getAttribute('aria-label') || e.getAttribute('alt') || e.tagName.toLowerCase());
  const overlap = [];
  for (let i = 0; i < leaves.length; i++) {
    for (let j = i + 1; j < leaves.length; j++) {
      const [a, ra] = leaves[i], [b, rb] = leaves[j];
      if (a.contains(b) || b.contains(a)) continue;
      const w = Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left);
      const h = Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top);
      if (w > 3 && h > 3) overlap.push(label(a) + ' / ' + label(b));
    }
  }
  const wrapped = [];
  for (const el of document.querySelectorAll('.bl-btn, .bl-nav__link, .bl-chip, .bl-tabs__tab, header a, header button')) {
    const text = (el.textContent || '').trim().replace(/\s+/g, ' ');
    if (!text || text.length > 32 || !shown(el) || !el.getClientRects().length) continue;
    if (wrapsText(el)) wrapped.push(text.slice(0, 30));
  }
  return { overlap: [...new Set(overlap)], wrapped: [...new Set(wrapped)] };
}
"""


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


FREEZE_JS = r"""
() => {
  const s = document.createElement('style');
  s.id = 'bl-qa-freeze';
  s.textContent = '.js [data-reveal]{opacity:1!important;transform:none!important;}'
    + '.js [data-reveal] :is(.bl-frame,.bl-mosaic__tile) img{clip-path:none!important;scale:1!important;transition:none!important;}'
    + '.js [data-draw]{transform:none!important;transition:none!important;}.js [data-wipe]{clip-path:none!important;transition:none!important;}'
    + '.js [data-seq]>*{opacity:1!important;transform:none!important;transition:none!important;}.bl-split__i{transform:none!important;}';
  document.head.appendChild(s);
}
"""

SCROLL_JS = r"""
async () => {
  const step = Math.round(window.innerHeight * 0.7);
  /* html has scroll-behavior: smooth; instant jumps make sure every section really scrolls into view */
  const go = (y) => window.scrollTo({ top: y, left: 0, behavior: 'instant' });
  for (let y = 0; y < document.documentElement.scrollHeight; y += step) {
    go(y);
    await new Promise((r) => setTimeout(r, 90));
  }
  go(document.documentElement.scrollHeight);
  await new Promise((r) => setTimeout(r, 300));
  document.querySelectorAll('[data-reveal]').forEach((el) => el.classList.add('is-in'));
  document.querySelectorAll('[data-draw],[data-wipe],[data-seq]').forEach((el) => el.classList.add('is-seen'));
  /* full-page shots showed empty frames where lazy photos had not loaded yet: load every photo before the shot */
  document.querySelectorAll('img[loading="lazy"]').forEach((img) => { img.loading = 'eager'; });
  const pending = [].filter.call(document.images, (img) => !img.complete)
    .map((img) => new Promise((r) => { img.addEventListener('load', r, { once: true }); img.addEventListener('error', r, { once: true }); }));
  await Promise.race([Promise.all(pending), new Promise((r) => setTimeout(r, 6000))]);
  go(0);
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
    const moving = i === 0 || s.matches('[data-fx="3d"]') || s.querySelector('canvas, video, [data-fx="3d"]') || [...s.querySelectorAll('*')].some(e => getComputedStyle(e).animationIterationCount === 'infinite');
    if (moving) out.push(s.id || ('section-' + (i + 1)));
  });
  return out;
}"""


DESIGN_JS = r"""(hoverSelectors) => {
  const INTERACTIVE = 'a, button, summary, label, input, select, textarea, [role="button"], [role="tab"], [tabindex]';
  const visible = (el) => { const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none' && parseFloat(cs.opacity) > 0.05; };
  const where = (el) => { const s = el.closest('section, header, footer'); return s ? (s.id || s.tagName.toLowerCase()) : 'page'; };
  const name = (el) => el.tagName.toLowerCase() + (el.classList[0] ? '.' + el.classList[0] : '');
  const out = { hover: [], lines: [], thin: [], sizes: 0, cards: [], shadows: [] };

  // 1. hover motion on things that cannot be clicked
  const seenHover = new Set();
  for (const sel of hoverSelectors) {
    let els = [];
    try { els = document.querySelectorAll(sel); } catch (e) { continue; }
    for (const el of els) {
      if (!visible(el) || el.matches(INTERACTIVE) || el.querySelector(INTERACTIVE) || el.closest(INTERACTIVE)) continue;
      const key = where(el) + ' ' + name(el);
      if (!seenHover.has(key)) { seenHover.add(key); out.hover.push(key + ' (' + sel.slice(0, 60) + ')'); }
    }
  }

  // 2. line length, 3. thin small text, font sizes
  const sizes = new Set();
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const textEls = new Set();
  while (walker.nextNode()) {
    const n = walker.currentNode;
    if (!n.textContent.trim()) continue;
    const el = n.parentElement;
    if (!el || el.closest('script, style, canvas, svg, noscript, [aria-hidden="true"], .sr-only, .bl-sr')) continue;
    textEls.add(el);
  }
  for (const el of textEls) {
    if (!visible(el)) continue;
    const cs = getComputedStyle(el);
    const fs = parseFloat(cs.fontSize);
    sizes.add(Math.round(fs));
    if (parseInt(cs.fontWeight, 10) < 400 && fs < 24) out.thin.push(where(el) + ' ' + name(el) + ' weight ' + cs.fontWeight + ' at ' + Math.round(fs) + 'px');
  }
  out.sizes = sizes.size;
  const seenLine = new Set();
  for (const el of document.querySelectorAll('main p, main li, main .bl-lead')) {
    if (!visible(el) || el.closest('table, nav, [aria-hidden="true"]')) continue;
    const text = el.textContent.replace(/\s+/g, ' ').trim();
    if (text.length < 60) continue;
    const range = document.createRange(); range.selectNodeContents(el);
    const tops = new Set(Array.from(range.getClientRects()).filter(r => r.width > 2).map(r => Math.round(r.top / 4)));
    if (tops.size < 2) continue;
    const cpl = text.length / tops.size;
    const key = where(el) + ' ' + name(el);
    if (cpl > 75 && !seenLine.has(key)) { seenLine.add(key); out.lines.push({ where: key, cpl: Math.round(cpl), text: text.slice(0, 50) }); }
  }

  // 4. rows of three or more look-alike cards that lead nowhere
  const chrome = (el) => { const cs = getComputedStyle(el);
    const bg = cs.backgroundColor !== 'rgba(0, 0, 0, 0)' && cs.backgroundColor !== 'transparent';
    return (bg || parseFloat(cs.borderTopWidth) >= 1 || cs.boxShadow !== 'none') && parseFloat(cs.borderTopLeftRadius) > 0; };
  const seenRow = new Set();
  for (const parent of document.querySelectorAll('main *')) {
    const kids = Array.from(parent.children).filter(visible);
    if (kids.length < 3) continue;
    const r0 = kids[0].getBoundingClientRect();
    const row = kids.filter(k => { const r = k.getBoundingClientRect(); return Math.abs(r.width - r0.width) <= 2 && Math.abs(r.top - r0.top) <= 4 && r.width > 120 && r.height > 80; });
    if (row.length < 3 || !row.every(chrome)) continue;
    if (row.some(k => k.matches(INTERACTIVE) || k.querySelector(INTERACTIVE))) continue;
    const sec = where(parent);
    if (!seenRow.has(sec)) { seenRow.add(sec); out.cards.push(sec + ' ' + name(row[0]) + ' x' + row.length); }
  }

  // 5. resting shadows on things that are not controls
  for (const el of document.querySelectorAll('main *')) {
    if (el.matches(INTERACTIVE) || el.closest(INTERACTIVE) || el.closest('dialog, .fx3d-stage, canvas')) continue;
    const cs = getComputedStyle(el);
    if (cs.boxShadow === 'none') continue;
    const soft = cs.boxShadow.split(/,(?![^(]*\))/).some(l => { if (/inset/.test(l)) return false;
      const n = (l.match(/-?[\d.]+px/g) || []).map(parseFloat); return (n[2] || 0) > 0; });
    if (!soft) continue;
    if (!visible(el)) continue;
    out.shadows.push(where(el) + ' ' + name(el));
  }

  // 6. mock UI: empty grey bars standing in for lines of text, or empty bars drawn as a chart (rules 5).
  // Real sites show real words and photos; a stack of placeholder lines reads as a generated page.
  const filled = (el) => { const cs = getComputedStyle(el);
    return (cs.backgroundColor !== 'rgba(0, 0, 0, 0)' && cs.backgroundColor !== 'transparent') || cs.backgroundImage !== 'none'; };
  const blank = (el) => !el.textContent.trim() && !el.querySelector('img, video, picture, svg, canvas, input, select, textarea');
  const skip = (el) => el.closest('[role="progressbar"], [role="slider"], [role="tablist"], [role="meter"], progress, meter, nav, footer, header, [data-mock-ok]') || el.matches(INTERACTIVE) || el.closest(INTERACTIVE);
  out.mock = [];
  const seenMock = new Set();
  for (const parent of document.querySelectorAll('main *')) {
    const kids = Array.from(parent.children).filter(k => visible(k) && blank(k) && filled(k) && !skip(k));
    if (kids.length < 2) continue;
    const rects = kids.map(k => k.getBoundingClientRect());
    // text lines: flat bars of 3-16px stacked one under another
    const lines = rects.filter(r => r.height >= 3 && r.height <= 16 && r.width >= 30 && r.width > r.height * 4);
    const rows = new Set(lines.map(r => Math.round(r.top)));
    // chart: three or more narrow upright bars side by side, standing on one baseline
    const bars = rects.filter(r => r.width >= 3 && r.width <= 48 && r.height >= 8);
    const base = new Set(bars.map(r => Math.round(r.bottom / 3)));
    const kind = (lines.length >= 2 && rows.size >= 2) ? 'placeholder lines' : (bars.length >= 3 && base.size === 1 && new Set(bars.map(r => Math.round(r.height))).size >= 2) ? 'drawn bar chart' : '';
    if (!kind) continue;
    const key = where(parent) + ' ' + name(parent);
    if (!seenMock.has(key)) { seenMock.add(key); out.mock.push(key + ' (' + kind + ')'); }
  }
  return out;
}"""

TARGET_JS = r"""() => {
  const els = Array.from(document.querySelectorAll('a[href], button, input:not([type=hidden]), select, textarea, summary, [role="button"]'));
  const rects = els.map(el => el.getBoundingClientRect());
  const out = [];
  els.forEach((el, i) => {
    const r = rects[i];
    const cs = getComputedStyle(el);
    if (!r.width || !r.height || cs.visibility === 'hidden' || el.closest('[aria-hidden="true"], [inert]')) return;
    if (r.width >= 24 && r.height >= 24) return;
    // inline links inside running text are exempt (WCAG 2.5.8)
    if (cs.display === 'inline' && el.closest('p, li, dd, td, figcaption, label')) return;
    // spacing exception: a 24px circle on its centre touches no other target
    const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    const clash = rects.some((o, j) => j !== i && o.width && o.height &&
      Math.max(o.left - cx, 0, cx - o.right) ** 2 + Math.max(o.top - cy, 0, cy - o.bottom) ** 2 < 144);
    if (!clash) return;
    const s = el.closest('section, header, footer');
    out.push((s ? (s.id || s.tagName.toLowerCase()) : 'page') + ' ' + el.tagName.toLowerCase() + (el.classList[0] ? '.' + el.classList[0] : '') + ' ' + Math.round(r.width) + 'x' + Math.round(r.height));
  });
  return Array.from(new Set(out)).slice(0, 12);
}"""


def hover_selectors(dist):
    """Selectors of elements that move or grow a shadow on :hover (the part of each selector before :hover)."""
    css = "\n".join(f.read_text(encoding="utf-8") for f in sorted((dist / "assets").rglob("*.css")))
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out = []
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        sel, body = m.group(1), m.group(2)
        if ":hover" not in sel or not re.search(r"(?<![-\w])(transform|translate|scale|box-shadow|filter)\s*:", body):
            continue
        for part in sel.split(","):
            if ":hover" in part:
                base = part.split(":hover")[0].strip()
                if base and base not in out:
                    out.append(base)
    return out


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


GL_HOSTS_JS = "() => [...document.querySelectorAll('[data-gl]')].map((h, i) => { if (!h.id) h.id = 'bl-gl-' + i; return h.id; })"
MIN_COVERAGE = 0.002  # share of canvas pixels a WebGL scene must draw


def webgl_check(browser, index):
    """Every data-gl scene mounts and draws. Returns (lines, problems, warnings)."""
    ctx = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
    page = ctx.new_page()
    page.goto(index.as_uri(), wait_until="load")
    page.wait_for_timeout(1200)
    lines, problems, warnings = [], [], []
    for hid in page.evaluate(GL_HOSTS_JS):
        page.evaluate("id => document.getElementById(id).scrollIntoView({block: 'center'})", hid)
        page.wait_for_timeout(1800)
        r = page.evaluate("id => { const h = document.getElementById(id); return {kind: h.dataset.gl, off: h.hasAttribute('data-gl-off'), "
                          "cov: window.BLGL ? BLGL.coverage(h) : -2}; }", hid)
        if r["off"]:
            warnings.append("WebGL is not available in this browser, so the %s scene in #%s is hidden; check it in a browser with a GPU" % (r["kind"], hid))
            continue
        if r["cov"] == -2:
            problems.append("#%s has data-gl=\"%s\" but _shared/gl.js is not on the page (add \"three\", \"gl\" and \"gl-%s\" to the section's shared list)" % (hid, r["kind"], r["kind"]))
            continue
        if r["cov"] < 0:
            problems.append("the %s scene in #%s never mounted: no gl-%s.js on the page, or the canvas has no data-gl-canvas" % (r["kind"], hid, r["kind"]))
            continue
        lines.append("%s %s %.1f%%" % (hid, r["kind"], r["cov"] * 100))
        if r["cov"] < MIN_COVERAGE:
            problems.append("the %s scene in #%s draws almost nothing (%.2f%% of the canvas); check its colours against the section tone and the data-gl-copy boxes" % (r["kind"], hid, r["cov"] * 100))
    ctx.close()
    return lines, problems, warnings


def reduced_motion_check(browser, index):
    """With prefers-reduced-motion: every revealed element is visible, nothing is pinned, no errors. Returns problems."""
    ctx = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1, reduced_motion="reduce")
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append("JS error with reduced motion: %s" % e))
    page.goto(index.as_uri(), wait_until="load")
    page.evaluate(SCROLL_JS)
    page.wait_for_timeout(400)
    r = page.evaluate("""() => {
      const seqKids = [...document.querySelectorAll('[data-seq] > *')];
      const hidden = [...document.querySelectorAll('[data-reveal]'), ...seqKids].filter(el => el.getClientRects().length && parseFloat(getComputedStyle(el).opacity) < 0.99)
        .slice(0, 5).map(el => (el.closest('[id]') || {}).id + ' ' + el.tagName.toLowerCase() + '.' + [...el.classList].join('.'));
      const pins = window.ScrollTrigger ? ScrollTrigger.getAll().filter(t => t.pin).length : 0;
      const covered = [...document.querySelectorAll('[data-wipe],[data-draw]')].filter(el => { const cs = getComputedStyle(el); return (/inset\(/.test(cs.clipPath) && /100%/.test(cs.clipPath)) || /matrix\(0,|matrix\([^,]+, [^,]+, [^,]+, 0,/.test(cs.transform); })
        .slice(0, 5).map(el => (el.closest('[id]') || {}).id + ' ' + el.tagName.toLowerCase() + '.' + [...el.classList].join('.'));
      return {hidden: hidden.concat(covered), pins};
    }""")
    ctx.close()
    problems = errors
    problems += ["still hidden with reduced motion: %s" % h for h in r["hidden"]]
    if r["pins"]:
        problems.append("%d ScrollTrigger pins stay active with reduced motion; build pins inside BL.motion.media and skip them when reduce is true" % r["pins"])
    return problems


def pause_check(browser, index):
    """After the page-wide Pause switch: no registered GSAP loop runs and WebGL canvases stand still. Returns problems."""
    ctx = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
    page = ctx.new_page()
    page.goto(index.as_uri(), wait_until="load")
    page.wait_for_timeout(1500)
    page.evaluate("window.BL && BL.setPaused(true)")
    problems = []
    running = page.evaluate("() => window.BL && BL.motion && BL.motion.ambientList ? BL.motion.ambientList().filter(a => a.isActive && a.isActive()).length : 0")
    if running:
        problems.append("%d GSAP loops keep running after Pause animations" % running)
    for hid in page.evaluate(GL_HOSTS_JS):
        frames = "id => { const m = document.getElementById(id).__blgl; return m && m.drawn ? m.drawn.frames : -1; }"
        page.evaluate("id => document.getElementById(id).scrollIntoView({block: 'center'})", hid)
        page.wait_for_timeout(600)
        a = page.evaluate(frames, hid)
        if a < 0:
            continue
        page.wait_for_timeout(900)
        if page.evaluate(frames, hid) - a > 2:
            problems.append("the WebGL scene in #%s keeps moving after Pause animations" % hid)
    ctx.close()
    return problems


def no_webgl_check(p, index):
    """In a browser without WebGL the page still runs: no JS errors, scenes marked data-gl-off. Returns problems."""
    try:
        browser = p.chromium.launch(channel="msedge", args=["--disable-webgl", "--disable-3d-apis"])
    except Exception:
        try:
            browser = p.chromium.launch(args=["--disable-webgl", "--disable-3d-apis"])
        except Exception:
            return []
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    errors = []
    page.on("pageerror", lambda e: errors.append("JS error without WebGL: %s" % e))
    page.goto(index.as_uri(), wait_until="load")
    page.evaluate(SCROLL_JS)
    left = page.evaluate("() => [...document.querySelectorAll('[data-gl]')].filter(h => !h.hasAttribute('data-gl-off') && h.__blgl).length")
    browser.close()
    if left:
        errors.append("%d WebGL scenes claim to run in a browser without WebGL" % left)
    return errors


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


SIZE_LIMIT = 18    # distinct font sizes: base tokens are seven, the library pages measure 14-18; more means sections add their own
SHADOW_LIMIT = 12  # resting shadows on non-controls


def sweep_check(browser, index, widths):
    """Narrow the page step by step. Returns (problems, warnings) with the width ranges where each one shows."""
    ctx = browser.new_context(viewport={"width": widths[0], "height": 900}, device_scale_factor=1)
    page = ctx.new_page()
    page.goto(index.as_uri(), wait_until="load")
    page.evaluate("document.fonts.ready.then(() => true)")
    page.evaluate(SCROLL_JS)
    page.evaluate(FREEZE_JS)
    page.add_style_tag(content="*,*::before,*::after{transition:none!important;animation:none!important}")
    over, overlap, wrapped = {}, {}, {}
    for w in widths:
        page.set_viewport_size({"width": w, "height": 900})
        page.wait_for_timeout(60)
        res = page.evaluate(CHECK_JS)
        for line in res["overflow"][:3]:
            over.setdefault(line.split(" spans ")[0], []).append(w)
        r = page.evaluate(SWEEP_JS)
        for o in r["overlap"]:
            overlap.setdefault(o, []).append(w)
        for t in r["wrapped"]:
            wrapped.setdefault(t, []).append(w)
    ctx.close()
    problems = ["sticks out sideways at %s px: %s" % (width_ranges(ws), el) for el, ws in list(over.items())[:6]]
    problems += ["header items overlap at %s px: %s" % (width_ranges(ws), o) for o, ws in list(overlap.items())[:6]]
    warnings = ["label wraps onto two lines at %s px: \"%s\"" % (width_ranges(ws), t) for t, ws in list(wrapped.items())[:6]]
    return problems, warnings


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
    ap.add_argument("--sweep", nargs="?", const="1440,360,20", metavar="FROM,TO,STEP",
                    help="also narrow the page from 1440 to 360 px in 20 px steps and report the width ranges where "
                         "something sticks out sideways, header items overlap or a button label wraps")
    args = ap.parse_args()
    sweep = None
    if args.sweep:
        try:
            hi, lo, step = (list(map(int, args.sweep.split(","))) + [20])[:3]
            sweep = list(range(max(hi, lo), min(hi, lo) - 1, -abs(step)))
        except ValueError:
            ap.error("--sweep takes FROM,TO,STEP, for example 1440,360,20")
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
    try:
        # a site that pins an older rules version ("rules" in page.json) gets the newer checks as warnings
        pinned = int(json.loads((dist / "build-report.json").read_text(encoding="utf-8")).get("rules", 99))
    except (OSError, ValueError, TypeError):
        pinned = 99
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
            # the full-page capture grows the viewport, which restarts photo reveals (clip wipes) mid-shot and left
            # empty frames in page-*.png; hold every reveal at its end state for this one shot
            page.evaluate(FREEZE_JS)
            page.screenshot(path=str(shot), full_page=True)
            page.evaluate("() => { const s = document.getElementById('bl-qa-freeze'); if (s) s.remove(); }")
            problems, warnings = [], []
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
                des = page.evaluate(DESIGN_JS, hover_selectors(dist))
                for h in des["hover"]:
                    problems.append("hover motion on something that cannot be clicked: %s. Move or shadow only links and buttons on hover (references/anti-slop.md)" % h)
                for x in des["thin"][:6]:
                    problems.append("light font weight on small text: %s. Use 400 or heavier below 24px" % x)
                for ln in des["lines"]:
                    msg = "about %d characters per line in %s (\"%s...\"); keep lines under 75" % (ln["cpl"], ln["where"], ln["text"])
                    if ln["cpl"] > 90:
                        problems.append(msg)
                    else:
                        warnings.append(msg)
                for m in des["mock"]:
                    (problems if pinned >= 5 else warnings).append(("" if pinned >= 5 else "[rules %d, not enforced] " % pinned) + "mock UI in %s: empty shapes stand in for real content. Show real words, figures from the brief or a photo; no grey text lines, drawn charts, fake notifications or floating chips (references/anti-slop.md, Mock UI)" % m)
                if des["sizes"] > SIZE_LIMIT:
                    warnings.append("%d different font sizes on the page; a clear type scale uses fewer (target %d or less)" % (des["sizes"], SIZE_LIMIT))
                if len(des["cards"]) >= 3:
                    warnings.append("rows of look-alike cards that lead nowhere in %d sections (%s); use a list, columns under a rule or fewer boxes" % (len(des["cards"]), "; ".join(des["cards"])))
                if len(des["shadows"]) > SHADOW_LIMIT:
                    warnings.append("%d resting shadows on things that are not controls (%s ...); a shadow reads as clickable" % (len(des["shadows"]), ", ".join(des["shadows"][:4])))
            for x in page.evaluate(TARGET_JS):
                problems.append("tap target smaller than 24x24px with a neighbour too close (WCAG 2.5.8): %s" % x)
            if res["h1"] != 1:
                problems.append("expected exactly one <h1>, found %d" % res["h1"])
            status = "OK  " if not problems else "FAIL"
            print("%s %4dpx  page height %dpx  screenshot %s" % (status, w, res["height"], shot))
            for pr in problems:
                print("       " + pr)
            for wr in warnings:
                print("  WARN " + wr)
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
        if sweep:
            problems, warnings = sweep_check(browser, index, sweep)
            if pinned < 5:  # a site pinned to an older rules version gets the sweep as warnings
                warnings = ["[rules %d, not enforced] %s" % (pinned, x) for x in problems] + warnings
                problems = []
            print("%s sweep %d to %dpx in %dpx steps" % ("OK  " if not problems else "FAIL", sweep[0], sweep[-1], sweep[0] - sweep[1] if len(sweep) > 1 else 0))
            for pr in problems:
                print("       " + pr)
            for wr in warnings:
                print("  WARN " + wr)
            failed = failed or bool(problems)
        if not args.no_motion:
            lines, problems = motion_check(browser, index)
            print("%s motion 1440px at 2x: %s" % ("OK  " if not problems else "FAIL", ", ".join(lines) or "nothing moves"))
            for pr in problems:
                print("       " + pr)
            failed = failed or bool(problems)
        has_gl = 'data-gl="' in index.read_text(encoding="utf-8")
        if has_gl:
            lines, problems, warnings = webgl_check(browser, index)
            print("%s webgl: %s" % ("OK  " if not problems else "FAIL", ", ".join(lines) or "no scene drew"))
            for pr in problems:
                print("       " + pr)
            for wr in warnings:
                print("  WARN " + wr)
            failed = failed or bool(problems)
        for name, problems in (("reduced motion", reduced_motion_check(browser, index)), ("pause", pause_check(browser, index))):
            print("%s %s" % ("OK  " if not problems else "FAIL", name))
            for pr in problems:
                print("       " + pr)
            failed = failed or bool(problems)
        if args.cvd:
            try:
                print("     colour vision shots: %s" % ", ".join(cvd_shots(browser, index, out)))
            except Exception as e:
                print("     colour vision shots need Chrome or Edge: %s" % e)
        browser.close()
        if has_gl:
            problems = no_webgl_check(p, index)
            print("%s without WebGL" % ("OK  " if not problems else "FAIL"))
            for pr in problems:
                print("       " + pr)
            failed = failed or bool(problems)
    if failed:
        print("\nQA FAILED. Fix the cause in page.json (shorter copy, fewer items) or in the section template, rebuild, run QA again.")
        return 1
    print("\nQA PASSED. Now open the screenshots and look at them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
