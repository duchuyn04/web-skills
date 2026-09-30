# Motion libraries: GSAP and Three.js

The library runs its motion on GSAP and its 3D scenes on Three.js. Both are vendored into the skill, so a built page works offline, from `file://` and without a CDN (lint fails any external script). Page authors never touch them: page.json picks variants and `"visual"` values, and the section scripts do the rest. This file is for maintainers and for authors of custom sections.

| Library | Version | File | Loaded | Size (min / gzip) |
|:---|:---|:---|:---|:---|
| GSAP core, CSSPlugin, ScrollTrigger | 3.15.0 | `templates/vendor/gsap.js` | on every page, before `base.js` | 112 KB / 44 KB |
| Three.js (the classes in `tools/vendor/three-entry.js`) | 0.186.1 | `templates/sections/_shared/three.js` | only by sections that draw a WebGL scene | 524 KB / 131 KB |

GSAP is free under the GSAP standard license (https://gsap.com/standard-license); Three.js is MIT. `templates/vendor/VERSIONS.json` records version, license, size and sha256 of each file, and build.py fails when a vendored file does not match it.

## Updating the vendored files

```
cd tools/vendor
npm ci                # or npm install after changing a version in package.json
node build.mjs        # writes both files and VERSIONS.json
```

`build.mjs` bundles each entry file with esbuild into a classic script (IIFE) that sets `window.gsap`, `window.ScrollTrigger` and `window.THREE`. Classic scripts are needed because Three.js ships only ES modules since r160, and module scripts do not load from `file://`. `charset: 'ascii'` escapes every non-ASCII character, so the vendored code passes the character lint (no dashes, arrows or curly quotes). When a new scene needs another Three.js class, add its name to `three-entry.js` and rerun. Most of the Three.js size is `WebGLRenderer` and its shader chunks; unused classes cost nothing. Then rebuild every example page, run lint and QA on each, and run `make_catalog.py`.

## GSAP on the page (`templates/base.js`)

- Reveal: `[data-reveal]` elements fade and move in with GSAP (0.4 s, `expo.out`, which matches `--ease-out`), up to four 60 ms stagger steps inside `[data-reveal-group]`. Variants: default rises 12 px, `pop` scales from 0.96, `fade` only fades, `left` and `right` slide 16 px. GSAP moves the element with `transform` and clears its inline styles afterwards, so a resting offset a section sets with the CSS `translate` property stays. `.is-in` is still added, so section CSS keyed to it keeps working. An IntersectionObserver decides when a reveal starts; it copes with sticky and horizontally scrolled parents better than cached scroll positions.
- Counters (`[data-count]`) count up over 2 s; the magnetic CTA uses `gsap.quickTo`; the header shrink is a ScrollTrigger.
- `BL.tween(ms, onFrame, onDone)` still exists for older section scripts and runs on GSAP.
- `BL.RM` is live: it reads `prefers-reduced-motion` each time.

`BL.motion` for section scripts:

| Helper | Use |
|:---|:---|
| `BL.motion.media(function (reduce) { ... })` | Runs the setup inside one shared `gsap.matchMedia`. Tweens and ScrollTriggers made inside are reverted and the setup runs again when reduced motion changes. Build `pin` and `scrub` work only when `reduce` is false. |
| `BL.motion.ambient(tweenOrTimeline)` | Registers a repeating or longer than 5 s tween. The Pause animations switch pauses and resumes it. |
| `BL.motion.reveal(elements)` | Reveals elements added after load (a filter, a tab) with the page reveal. |
| `BL.motion.ease` | The page's ease name for one-off tweens. |
| `BL.motion.split(el, 'words' or 'chars')` | Splits a heading into masked words or characters and returns `{targets, words, chars}` to animate (for example `gsap.from(targets, {yPercent: 110, stagger: .04})`). Text is normalised to NFC so Vietnamese letters with marks stay whole, inline markup such as the `.bl-hl` accent is kept, the heading gets an `aria-label` and the pieces are `aria-hidden`. |

Pause animations (`BL.setPaused`) pauses ambient tweens, freezes CSS animations through `html[data-motion="paused"]`, pauses autoplay videos and fires `bl:motion`. One-shot reveals and scroll-linked tweens keep working, because they are short or follow the reader's own scrolling.

## Three.js scenes (`templates/sections/_shared/gl.js`)

`BLGL.register(name, factory)` mounts the factory on every element with `data-gl="<name>"` that holds a canvas with `data-gl-canvas`. The toolkit:

- creates the `WebGLRenderer` (WebGL2 only, alpha, no antialias, low-power GPU) with the pixel ratio capped at 1.5, or at 1 for line scenes (`ctx.dprCap = 1`);
- draws through `BLRibbons.loop`, so a scene stops off screen, in hidden tabs, on Pause and under reduced motion (one still frame);
- sizes the canvas with a ResizeObserver;
- passes colours from the section's tokens (`ctx.colors.text`, `muted`, `accent`, `blend`, `accent2`, `bg`) as sRGB numbers that shaders write straight to the canvas;
- dims the scene under every `data-gl-copy` block (up to 8) through the `GUARD` shader chunk, so text keeps its contrast;
- seeds every random choice from `data-seed` (the brand name);
- without WebGL2 marks the host `data-gl-off` and hides the canvas and anything with `data-gl-hide`; every scene is decoration, so the section reads the same without it.

The factory returns `{ frame(time, dt), resize(w, h) }`. `time` stops while the page is paused. `ctx.intro()` eases from 0 to 1 over the first 1.4 s. Write shaders with `ShaderMaterial`, `transparent: true`, `depthTest: false`, and output `vec4(colour, alpha)`.

Scenes in the library:

| `data-gl` | File | Used by |
|:---|:---|:---|
| `dots` | `gl-dots.js` | `hero-magnetic`, band `"visual": "dots"` |
| `terrain` | `gl-terrain.js` | `hero-terrain`, band `"visual": "terrain"` |
| `wave` | `gl-wave.js` | `hero-wavefield`, band `"visual": "wave"` |
| `flow` | `gl-flow.js` | `hero-flow`, band `"visual": "flow"` |
| `globe` | `gl-globe.js` | `hero-globe` (pins from the hub and market cities), band `"visual": "globe"` |

Driving a scene from a section script (custom sections): `host.__blgl.vis` is the object the scene returned once it has mounted (`host.__blgl` is just `true` when there is no WebGL, so test `host.__blgl && host.__blgl.vis`).

- `globe`: `vis.focus(lat, lon)` turns the globe to face a point and marks the pin there with `.is-focus`; `vis.focus(null)` returns to the sway. `data-globe-layout` is `fit`, `side`, `rise` (a huge globe rising from the bottom edge, for a full-screen hero) or `tour` (a whole globe right of centre); `rise` and `tour` are solid, with a lit body, an atmosphere rim and 90 000 dots. Overrides: `data-globe-scale`, `data-globe-x`, `data-globe-y`, `data-globe-tilt` (degrees the pins sit above the disc centre, 30 for `rise`).
- `flow`: `vis.setSort(p)` with `p` from 0 to 1 takes over the sorting from the stream position: 0 is a cloud, 1 is calm lanes everywhere, so a scroll position can drive it. `data-flow-density` scales the particle count (0.3 to 2.2), `data-flow-lanes` fixes the lane count.
- Inside a scene factory `ctx.frozen()` says whether only still frames are drawn (reduced motion or Pause animations) and `ctx.redraw()` draws one now; call it after changing state while frozen.

Band sections list the scene files under `"shared_by_field"` in their schema, so Three.js is added to a page only when a band sets `visual`. The globe's land mask comes from `templates/partials/world-dots.html`; regenerate it with `python scripts/make_globe_mask.py` after the dot map changes.

## Checks

- build.py: vendored files must match `VERSIONS.json`; at most two WebGL scenes per page; the page's own JavaScript stays under 300 KB (vendored files not counted); a custom section fails with its own `WebGLRenderer`, `setAnimationLoop` or an unregistered `repeat: -1` tween, and gets a warning for its own `requestAnimationFrame` loop.
- qa_screenshot.py: frame rate at 2x (minimum 30 fps) as before; every scene draws (`BLGL.coverage`); with reduced motion nothing stays hidden and nothing is pinned; after Pause no ambient tween runs and no scene renders new frames; with WebGL turned off the page has no JS errors.
