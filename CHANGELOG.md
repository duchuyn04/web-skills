# Changelog

The version is the one at the top of SKILL.md. The major number is the rules version (`RULES_VERSION` in `scripts/build.py`): it goes up when a new check can fail a page that built before.

## 4.2.0 (2026-09-30)

Layouts from four sites a client named as the standard for a professional page: IRIS Software Group, Intelligent Outsourcing, Innovature BPO and Bestarion. Rules stay at 4: nothing here fails a page that built before.

- Blueprints: new `iris` and `intelligent-outsourcing`; `innovature-bpo` recaptured (its roles by industry carousel is now the services slot, so the build accepts it; hero composition `hero-tabs`; savings calculator slot; talent pool split) and `bestarion` updated (three review cards, fits offshore-staffing too). All four carry `"preferred": true`: `variety.py --blueprints` lists them first with a `*`, and build.py names them first when it suggests a free layout. Screenshots and section outlines of the four sites are in `data/layout-analysis/shots/client-refs/` (captured with `data/layout-analysis/tools/capture_refs.py`).
- Six calm variants: `hero-finder` (IRIS: portrait on a colour panel with small UI cards and a finder bar of dropdowns that jump to the right section), `solutions-vtabs` (IRIS: vertical tabs beside a raised panel of solution cards), `contact-photo` (IRIS: chevron photo with a call button beside a two-column enquiry form), `roles-carousel` (Innovature: role cards by industry on a track with a progress bar), `metrics-tiles` (Intelligent Outsourcing row of figure tiles, Innovature copy beside a two-by-two bento) and `faq-grid` (questions in two columns of tinted boxes).
- Stat suffixes of three or more letters get a space ("2 weeks", "5 năm"); short units stay attached ("10k", "3x").
- `metrics-tiles` counts as a metrics section for the missing-proof warning, and `contact-photo` gets the missing form action warning.
- Fix: `solution-panels` printed its entrance CSS as visible text under the section since 4.1.0 (the rules sat after `</section>` in the template). They are in `section.css` now, and lint fails visible text that looks like CSS or a code comment (`stray-code`).
- `service-links` also builds the `list-rows` form, so it fills Bestarion's (and SupportNinja's) link-row services slot. The missing metrics warning stays quiet on blueprints without a metrics or awards slot.
- `references/layout-blueprints.md` has a "Preferred layouts" section: which pattern comes from which site and which variant rebuilds it.
- Examples: `examples/blueprints/` has a page for each preferred blueprint; `examples/variations/` has one page per new variant.

## 4.1.0 (2026-09-30)

Motion measured on real sites. Rules stay at 4: nothing here fails a page that built before.

- `references/motion-research.md`: how 89 of the 92 blueprint homepages animate, measured with `scripts/research/motion_probe.py`. Half move nothing on scroll; the rest rise 30-60 px over 0.8-0.9 s, cards slide in from the side, and the differences sit in hovers, carousels, sticky and scroll-linked pieces.
- `theme.motion_style` (`rise`, `slide`, `fade`, `mask`) sets how elements arrive. Left out, build.py picks it from the brand name, so pages for different clients move differently. `build-report.json` records it.
- New base primitives in `base.js` and `base.css`: `data-draw` (a rule grows), `data-wipe` (a clip opens), `data-seq` (children arrive in turn), `data-parallax` (a photo drifts in its frame), `data-grow` (a block widens with the scroll) and `BL.motion.trackIn` (slider cards arrive from the right). QA's screenshot freeze and reduced-motion check cover them.
- 23 calm sections carry their own entrance tied to what they show: feature-rows, solution-panels, testimonials-rated, testimonials, audience-cards, pillars-numbered, quote-spotlight, cta-band, contact-split, video-block, banner-image, careers-band, image-cards, case-slider, country-cards, service-links, about-mosaic, faq-accordion, services-tabs, metrics-panel, metrics-counter, industries-tiles and compliance-badges. `references/animation-map.md` lists every one with its timing.
- Lint allows scroll entrances up to 1.2 s (real sites run 0.6-1 s); hovers stay within 0.5 s.

## 4.0.0 (2026-09-30)

Rules 4, from a test page built by Haiku. Pages built under rules 3 keep building with `"rules": "3"`.

- Library photos: each appears once on a page, and the alt text may not name the client or say "our". Library avatars on reviews and library portraits in `team-grid` and `team-coverflow` fail: a stock face never stands for a named person.
- A form `action` must be a URL the brief gives. Without one the form shows its thank-you message.
- The footer `legal` text may not start with a copyright line (the template prints one).
- The brief checks catch "hidden charges", "never share", "time zones", "background checks" and "encrypted" when the brief does not say them, and let the page repeat a "no" the brief gives ("No setup fee").
- Examples: stock alts describe the picture, repeated photos replaced, library avatars removed from reviews.

## 3.0.0 (2026-09-30)

Rules 3. Pages built under rules 1 or 2 keep building with `"rules": "1"` or `"rules": "2"`.

- Eyebrows: no rule before the label (it read as an em dash), at most a third of section titles carry one (was a warning above half), no tracked capitals on Vietnamese pages. Lint fails any short line drawn before or after text (`dash-rule`).
- Colours: with `site.logo`, `theme.accent` must be one of the logo's hues and a coloured logo must set it (`scripts/logo_colors.py`). Bootstrap and Tailwind palette defaults fail unless the brief or logo has them.
- Fonts: `corporate-blue`, `clean-minimal`, `orange-charcoal` and `teal-fresh` carry `fonts_vi` for Vietnamese pages; a preset font without Vietnamese glyphs fails the build.
- Seven hero compositions from real sites: `hero-overlap` (Foundever), `hero-mosaic` (Kyanon), `hero-portrait` (MicroSourcing, Horatio), `hero-promo` (Firstsource), `hero-tabs` (Genpact, TDCX), `hero-news` (Concentrix), `hero-panels` (ELEKS). 63 of 92 blueprints name their source hero in `"compose"`, and build.py requires it (or a business hero).
- Photos: pages with 6+ content sections need a photo in 40% of them, and at most two icon-per-item sections. New optional photos on `metrics-counter`, `services-bento`, `process-sticky`, `steps-row`, `industries-rows`, `faq-accordion` and `contact-split`; process-sticky and industries-rows move the photo with the step or row being read.
- Examples updated to pass: photo-led starters, `concentrix` on `hero-news`, fewer eyebrows.

## 2.0.0 (2026-09-30)

Rules 2. Pages built under rules 1 keep building with `"rules": "1"` (SKILL.md, "Maintaining the library").

- Motion is calm by default. The rule that every page needs three signature sections is gone.
- 28 variants form the expressive tier (`"tier": "expressive"` in their schema: 3D objects, WebGL scenes, particles, folding effects), and so does the `"visual"` backdrop on bands. build.py fails them unless page.json sets `"motion": "expressive"`, and fails that value unless the brief asks for a 3D or animation-led page. The old value `"signature"` still works.
- The checks that compare a page with the other sites in `sites/` (same hero, same blueprint, same look) are warnings, so a page builds the same way whatever sits next to it.
- `examples/ai-data-ops.page.json` and `examples/blueprints/concentrix.page.json` use photo heroes (`hero-fullbleed`) instead of 3D heroes.
- New `tests/run.py` with a clean fixture and must-fail cases, plus a build and lint of every example and site.
- `build-report.json` records the rules version it was built under.
- `variety.py` lists calm variants first and marks expressive ones with `^`.

## 1.x (2026-09-26 to 2026-09-30)

Rules 1, built up over these commits without a version change:

- Library: 5 archetypes, 8 presets, 89 section variants, CC0 photo library, sections researched from 113 BPO homepages and from Mobbin.
- Copy: industry voice measured on 125 homepages, AI-tell phrases, copied example text, and the brief as the source of every client name, quote, claim and figure.
- Layout: 92 real-site blueprints that every page outside `examples/` must follow.
- Design: OKLCH colour tokens with contrast checks, anti-slop checks in build, lint and QA, frame-rate, reduced-motion, pause and no-WebGL checks in QA.
- Motion: vendored GSAP and Three.js, WebGL scenes, and a rule that every page carried three signature sections (removed in 2.0.0).
