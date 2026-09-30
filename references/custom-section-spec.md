# Custom section (fallback only)

Use this only when the user needs a block that no variant in `section-catalog.md` can carry, for example a job openings table. Try hard to fit the content into an existing variant first: a custom section is where layout quality can slip.

## 1. Write the spec first

Fill this in and show it to the user before writing code.

```
Name: <kebab-case, for example open-roles>
Purpose: <one sentence: what the visitor learns or does here>
Slot: <after which section it goes>
Content: <fields and item counts, for example 4-8 roles with title, location, type>
Layout desktop: <grid or split, columns, what sits where>
Layout 768px and 390px: <how it stacks>
Interaction: <none, or which existing behavior: reveal, accordion, tabs>
Closest existing variant: <name, and why it does not fit>
```

## 2. Files

Create the folder next to page.json:

```
sections/<name>/schema.json      same format as templates/sections/*/schema.json
sections/<name>/section.html     template
sections/<name>/section.css      optional
```

Reference it in page.json as `{"type": "custom:<name>", "data": {...}}`. Custom sections skip the archetype order check, so place them sensibly.

## 3. Template rules (build.py enforces the starred ones)

- Root element: `<section id="{{section.id}}" class="bl-section bl-tone-{{section.tone}}">` (*).
- Inside: `<div class="bl-container">`, then a heading block copied from `templates/partials/head.html` via `{{> head}}` (needs a `head` field with `{"$ref": "head"}` in the schema).
- Layout only with existing classes where possible: `bl-grid bl-grid-2|3|4`, `bl-split`, `bl-card`, `bl-card--lift`, `bl-checks`, `bl-icon-box`, `bl-btn bl-btn--primary|ghost`, `bl-link`, `bl-chip`.
- CSS must use tokens only: `var(--text-strong)`, `var(--surface)`, `var(--border)`, `var(--accent-ink)`, `var(--c-accent)`, `var(--radius-lg)`, `var(--font-heading)` (*). No hex, rgb or hsl colors (*), no new fonts (*).
- Flat surfaces. No gradient text, glow blobs, color-to-color backgrounds or hover spotlights; a gradient is allowed only for a photo scrim, an edge fade mask, neutral or primary shading, or a hard-stop pattern (lint_output.py fails the rest; see `color-system.md`, Gradients).
- Class names start with `bl-<name>__`.
- Icons with `{{icon:name}}` or `{{icon:$field}}`, arrows with `{{arrow}}`, flags with `{{flag:$field}}`.
- Add `data-reveal` to blocks that should fade in; put `data-reveal-group` on a parent to stagger children.
- Animate only transform and opacity. Add nothing that ignores `prefers-reduced-motion`.

## 4. Motion and performance

Continuous motion costs raster time, not script time. A full-width canvas that looked smooth on a 1x office monitor ran at 6 frames per second on a 2x laptop screen: its script took under 1 ms per frame, but repainting about 50 long anti-aliased paths over 2880 x 1800 pixels did not fit in the frame. Canvas and paint cost grows with the square of the device pixel ratio, so test at 2x. `qa_screenshot.py` does this and fails any moving section below 30 frames per second.

- Tweens: use GSAP (`window.gsap`, `window.ScrollTrigger`; always on the page, see `motion-libraries.md`). Build scroll-linked work (`scrub`, `pin`) inside `BL.motion.media(function (reduce) { ... })` and skip it when `reduce` is true. Wrap every repeating or longer than 5 s tween in `BL.motion.ambient(...)` so Pause animations stops it; build.py fails a custom section with `repeat: -1` outside it.
- 3D: register a scene with `BLGL.register(name, factory)` (`templates/sections/_shared/gl.js`) and add `"ribbons", "three", "gl"` plus your scene file to the schema's `shared` list. The toolkit gives the renderer (pixel ratio capped at 1.5), colours from the tokens, the pointer, dimming under `data-gl-copy` and the fallback without WebGL. build.py fails a custom section that creates its own `WebGLRenderer` or calls `setAnimationLoop`.
- Canvas: reuse `window.BLRibbons` from `templates/sections/_shared/ribbons.js` (`waves` for line ribbons, `loop` and `fit` for anything else). Its loop stops when the canvas is off screen, when the tab is hidden, under reduced motion and when the page-wide Pause animations switch is on. Never start a second `requestAnimationFrame` loop of your own (build.py warns).
- Decorative lines and dots: back the canvas at 1x, not at `devicePixelRatio`. Thin, soft, semi-transparent strokes look the same, and the pixel count drops by a factor of 4 on a 2x screen. Keep the device ratio (capped at 2) only for sharp shapes the eye follows, such as the globe.
- Build fewer, longer paths. Put every line that shares a colour and opacity into one `Path2D` and stroke it once (group opacities into 3-5 steps). Use `quadraticCurveTo` through about one point per 24 CSS px instead of `lineTo` every few pixels.
- Cap slow ambient motion at 30 fps (skip a frame when less than 32 ms passed). Keep full rate only while something follows the pointer or a one-off draw-in runs.
- No `shadowBlur`, no `filter` on a canvas, and no `backdrop-filter` layer on top of one; each forces a full repaint of the layer every frame.
- CSS: animate `transform` and `opacity` only. `stroke-dashoffset`, `clip-path`, `width`, `height` and colours repaint every frame; use them only for one-off transitions on small elements.
- Anything that moves for more than 5 seconds on its own must stop with the page-wide switch (listen for the `bl:motion` event or rely on `html[data-motion="paused"]`, which pauses CSS animations).

## 5. Verify

Run build, lint and QA like any page, and look at the section at 1440, 768 and 390 px. If it looks weaker than its neighbours, simplify it. If QA reports `slow animation`, apply the rules above before anything else; do not raise the threshold.
