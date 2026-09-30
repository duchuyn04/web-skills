---
name: bpo-landing-builder
description: Build a production-quality landing page for a BPO, outsourcing, contact center, offshore staffing, AI data annotation or outbound sales company. The page is assembled by a script from pre-built, pre-animated sections, so layout and quality do not depend on the model. Use when the user asks for a BPO or outsourcing website, landing page, homepage or giao dien outsourcing, or wants to turn a company brief into such a page.
compatibility: Needs Python 3.9+ for build and lint. Visual QA needs Python Playwright plus Edge or Chrome. Works with any agent that can read files and run shell commands.
metadata:
  version: "1.0.0"
---

# BPO landing builder

You do not write HTML, CSS or JavaScript. You write one JSON file (`page.json`) with the page content. `scripts/build.py` turns it into a finished page using fixed section templates that already contain the layout, spacing, colors, responsive rules and the animations researched from 120 BPO websites. Your job is to choose well and write good copy.

`SKILL` below means the folder that contains this file. In this project the real folder is `.agents/skills/bpo-landing-builder`; agent-specific folders such as `.claude/skills/bpo-landing-builder` or `.qwen/skills/bpo-landing-builder` are links to it. Use whichever path you loaded this file from. If you cannot run shell commands, stop and tell the user: the build scripts are required.

## Rules that are never negotiable

1. Never edit files in `dist/`. Change `page.json` (or a template, if the user asked you to change the library) and rebuild.
2. Never invent facts: no made-up client names, quotes, agent names, CSAT, headcount, prices, salary rates, certifications or promises (such as "same-day onboarding"). A missing single figure becomes `"[KPI]"` (number fields) or `"[figure]"` (text). A missing whole block of proof (logos, testimonials, case studies, call recordings, salary rates) means you leave that section out; its slot is "recommended", so the build only warns. If a section's minimum item count is higher than the facts you have, drop the section or pick another variant; never pad a list to reach the minimum. List everything missing in your report. build.py enforces this against the brief: client names, quotes (word for word), certifications, tools, guarantees, languages, recordings and figures with a unit that the brief does not give are build errors (see "What build.py checks against the brief" in `references/content-rules.md`). Never extend a quote, never add a placeholder testimonial or logo, and never add facts to the brief to make the build pass. The reverse also holds: when the brief gives figures (headcount, years in business, savings, retention, certifications), put them on the page in `metrics-counter` or `metrics-panel` and `compliance-badges`. Real BPO homepages lead with this proof, and a page without it reads as generic.
3. Copy follows `references/content-rules.md` and `references/industry-voice.md`. Write the way real BPO vendors write: hero titles name the company's category ("Software outsourcing in Vietnam"), about a third of section headings are plain labels ("Our services", "Case studies"), the lead starts with the company name, and buttons use standard labels ("Contact us", "Get a quote"). The build fails on emoji, arrows, em or en dashes, curly quotes, banned AI words and phrases that mark copy as AI-written ("while you scale", "peace of mind", "hãy để chúng tôi"), so fix the wording, do not work around the checker. Treat its voice warnings as things to fix.
4. Keep the archetype's section order. Do not add keys that the schema does not list.

## Step 1: Collect the brief

Get these from the user or their files. Ask one short message for anything missing that matters (items marked *); do not stall on the rest.

- Company name*, what they sell*, who buys it* (industry, country)
- Delivery locations (cities), headcount, languages
- Proof: real KPIs, client names or logos, certifications, testimonials
- Contact: email, phone, WhatsApp or Zalo link, form endpoint if they have one
- Brand colors (hex, exactly as in the logo; build.py derives every shade) and page language (default English). The logo color always goes in `theme.accent`, even when it is bright: build.py darkens the button shade for contrast and keeps the original for highlights. Do not skip it and do not put it in `theme.primary`, which is the dark section and footer color.
- Photos of their own office or team, if any (put them next to page.json)

## Step 2: Choose archetype and preset

Read `references/page-anatomy.md`. Pick the archetype from the client's headline pitch, the thing the brief says first or loudest:

| Headline pitch | Archetype | Default preset |
|:---|:---|:---|
| Many services, enterprise buyers, several hubs or countries | `enterprise-cx` | `enterprise-navy` |
| Cost savings, dedicated offshore staff, "hire a team in Vietnam or the Philippines" | `offshore-staffing` | `human-warm` |
| Data labeling, RLHF, trust and safety, content moderation | `ai-data-ops` | `dark-ai` |
| Call quality as the product: SDR, telesales, receptionists, and the client has call recordings | `cx-voice-sales` | `clean-minimal` |
| Software teams (ITO) plus back-office services (BPO), many services each with its own page, often a Vietnam or Asia delivery base | `it-bpo-partner` | `orange-charcoal` |

Tie-breakers:

- A client with two service lines (for example voice support plus accounting) and a savings pitch is `offshore-staffing`; both lines go into the services section.
- Choose `cx-voice-sales` only when the client can supply call recordings or sells outbound sales meetings. Voice support alone, without recordings, fits `offshore-staffing` or `enterprise-cx`.
- Preset: use the archetype's default. Switch only when the client names brand colors or a style, or clearly matches another preset's "Pick it when" line in `references/style-presets.md`. Brand colors alone go in `theme` and do not change the preset.
- Brand hue presets: when the client's logo is clearly blue, red or teal, `corporate-blue`, `crimson-trust` or `teal-fresh` may replace the default. Each also sets page-wide design options (angled or curved section edges, photo masks, heading highlight style, photo wipe-in); see "Design options" in `references/style-presets.md`.

## Step 2a: Follow a real layout (blueprint)

Every page follows the layout of one real BPO homepage, section by section. The layouts are in `templates/blueprints/` (about 90 real sites, measured in the browser and checked by hand against their screenshots). What changes from the source is the client's copy, the brand colours and the 3D visuals; the order, layout forms, tones and grid sizes stay. Read `references/layout-blueprints.md`, then:

```
python SKILL/scripts/variety.py --blueprints <archetype> --sites sites
python SKILL/scripts/variety.py --blueprint <key>
```

The first command lists the layouts that fit the archetype, unused ones first, with their section roles (`?` marks optional ones). Pick an unused one whose sections the brief can fill. The second prints each section with the variants that fit it; the ones marked `*` carry the 3D visual. Set `"blueprint": "<key>"` in page.json and write one section per blueprint section, in order, leaving out only optional ones the brief cannot fill. build.py fails a page without a blueprint, a page that reorders or skips required sections, and a second site on the same blueprint while free ones remain.

## Step 2b: Do not repeat a look

Every page is built from the same library, so two clients can end up with the same page in different words. Before you pick variants, run:

```
python SKILL/scripts/variety.py --archetype <archetype> --sites sites
```

It lists every slot with its variants ordered from least to most used across `sites/*/page.json`, and the presets the same way. For each slot, take the first variant in the line that fits the client's content (a variant still has to suit the facts: do not pick `models-board` without engagement models or `industries-rows` without industries). Prefer a preset nobody has used when the client has no brand colours. `build.py` warns when the finished page shares 70% or more of its look (preset plus variant per slot, hero and services count double) with another site, and names the slots to swap; treat that warning like a copy warning and fix it.

Motion-signature variants, added to widen the library: `hero-ribbons` (canvas line ribbons, word-rise headline, globe and photo carousel, optional `echo` of the ribbons behind later dark sections), `services-stack` (sticky stacking cards), `models-board` (compare slot: engagement models with a who-does-what board) and `industries-rows` (industries or audience slot: large rows, cursor-follow card). `examples/variations/motion-signature.page.json` shows all four.

Effects from `bpo-landing-animations/05-new-effects-research.md`: `hero-chat` (a sample support chat plays in the hero; label it as a sample), `logo-wall` (logo grid whose cells flip, instead of the marquee), `metrics-rings` (SLA percentages as drawing rings), `testimonials-drift` (drifting quote columns with a Pause button, 9 or more real quotes), `case-filter` (case studies filtered by industry with a View Transition) and `"wordmark": true` on `footer-columns` (brand name edge to edge). `examples/variations/proof-motion.page.json` shows them. Every footer carries a Pause animations button that stops all motion on the page (WCAG 2.2.2); keep `motion_toggle` on whenever the page has a loop, a carousel, a video or `testimonials-drift`.

## Step 2c: Give the page signature motion

Clients compare these pages with agency-built sites, so a page made only of fade-in sections reads as a template. Every page needs at least three sections from the signature set, and build.py fails the page until it has them:

| Slot | Signature variants (pick by metaphor, not list order) |
|:---|:---|
| hero, tech and AI | `hero-particles` (particles form the monogram), `hero-magnetic` (dot plane bends under the pointer), `hero-dark-network` (AI data operations), `hero-monolith` (extruded monogram block) |
| hero, back office and data | `hero-flow` (scattered particle streams sorted into calm lanes; finance, accounting, data processing, IT operations) |
| hero, operations and scale | `hero-terrain` (landscape with stats on the peaks), `hero-isometric` (operations floor), `hero-dashboard` (exploded dashboard of real services and stats), `hero-wavefield` (field of dots under slow swells; CX and voice) |
| hero, several service lines | `hero-orbits` (service chips on orbit rings), `hero-prism` (headline line turns through the services), `hero-ribbons` (line ribbons and globe carousel) |
| hero, people and staffing | `hero-deck` (fanned deck of real roles), `hero-shatter` (the client's team photo assembles), `hero-liquid` ("your team and ours" merge) |
| hero, contact centers and 24/7 | `hero-sundial` (24-hour dial with live hub times; needs 2+ real hubs), `hero-chat` (sample support chat) |
| hero, offshore and multi-site | `hero-globe` (dotted globe with the real delivery cities pinned and arcs to client markets; needs 1+ real hub city) |
| services | `services-stack` (sticky stacking cards), `services-cylinder` (drum of 5-8 services), `services-cube` (blocks that turn to scope, SLA, tools) |
| process | `process-sticky`, `process-layers` (isometric plates open with scroll), `process-pipeline` (packets through stations) |
| compare | `models-board` (who does what in each engagement model) |
| industries, audience | `industries-rows` (4+ industries), `industries-slats` (angled slats turn to face you) |
| metrics, trust | `metrics-rings` (percentages), `metrics-bars3d` (real before and after results) |
| logos | `logo-wall` (8+ real client names) |
| proof | `testimonials-drift` (6+ real quotes), `case-filter` (4+ real cases), `proof-book` (3+ real cases as an open book) |
| about, team | `about-helix` (4+ real milestones), `team-coverflow` (3+ real leaders) |
| locations | `locations-map`, `locations-relief` (tilted map with a column per hub) |
| faq, cta | `faq-fold` (answers unfold like paper), `cta-letter` (closing letter unfolds) |
| calculator, voice | `cost-calculator`, `voice-sample` |

The hero is the page's identity, so every site in `sites/` gets its own signature hero: build.py fails a page whose hero another site already uses while an unused signature hero fits the archetype, and names the free ones. Pick the one whose metaphor suits the company (see the table), not the first in the list. All 3D heroes seed their motion from the brand name, so even a repeated hero moves differently. `python SKILL/scripts/variety.py --archetype <archetype>` marks them with `*` and lists them first. The archetype examples in `examples/` use the calmer variants, so after copying one, swap at least three slots to signature variants, taking the data shape from `examples/variations/motion-signature.page.json` and `examples/variations/proof-motion.page.json`. Signature variants still need real content: never invent industries, quotes or logos to use one. `hero-ribbons` repeats its ribbons behind the dark sections below it by itself; that shared motif is what makes the page feel designed. Set `"motion": "calm"` at the top of page.json only when the client asks for a still, conservative page.

## Step 3: Start from the example

Create a project folder, for example `sites/<company-slug>/`, and copy the matching example. `examples/blueprints/concentrix.page.json` shows a page built on a blueprint; the archetype examples show the data shape of each section:

```
SKILL/examples/<archetype>.page.json  to  sites/<company-slug>/page.json
```

For a Vietnamese page (`"lang": "vi"`), copy `SKILL/examples/vi/enterprise-cx.page.json` instead, or use it as the model for wording with another archetype. Write Vietnamese directly in that voice; do not translate the English examples sentence by sentence.

Then edit values only:

- Paste the client's brief, as given, into a top-level `"brief": "..."` field. It is required: the build fails without it, and it checks every name, quote, claim and figure on the page against it.
- Replace every string and number with the client's content. Delete `_note`. The examples describe fictional companies: their figures, time frames, guarantees and contract terms ("30 days notice", "replies within 48 hours", "90-day replacement") are sample data. Keep such a detail only when the brief states it; otherwise write the sentence without it or drop the FAQ question. The build fails on sentences copied from an example and on example figures that are not in the brief.
- Put the sections in the blueprint's order (Step 2a), taking each variant from `variety.py --blueprint <key>` and its data shape from the examples.
- Optional slots `ticker`, `intro` and `banner` (ticker-band, statement-band, banner-image) and the heroes `hero-qualifier` and `hero-collage` are not in the archetype examples. Copy their data from `examples/variations/*.page.json`, which also shows `image-cards` with `"slider": true` and `quote-spotlight`.
- `examples/variations/staffing-extended.page.json` shows the optional slots `tools` (tool-stack), `compare` (comparison-table), `awards` (awards-strip), `team` (team-grid) and `careers` (careers-band), plus `steps-row` for the process slot and `country-cards` for locations. Use awards, team and review scores only when the brief supplies them.
- For each section, check field names, item counts and length limits in `references/section-catalog.md`. Look at `previews/<variant>.jpg` to see what the section looks like.
- Images and video: pick keys from `references/assets.md`, or use the client's files by relative path. Icons, flags and cities must come from `python SKILL/scripts/build.py --list`.
- Every `href` that starts with `#` must match a section id (the default ids are listed in the catalog as "Default anchor").

## Step 4: Build until clean

```
python SKILL/scripts/build.py sites/<slug>/page.json --out sites/<slug>/dist
```

Each error line gives the JSON path and the fix. Fix all errors in page.json and run again. Repeat until it prints `OK built`. Read the WARN lines too: placeholders, missing audio, a form without an endpoint.

## Step 5: Lint

```
python SKILL/scripts/lint_output.py sites/<slug>/dist
```

It must print `LINT PASSED`. Copy errors are fixed in page.json; structural errors mean a template problem, so tell the user instead of hacking around it.

## Step 6: Visual QA

```
python SKILL/scripts/qa_screenshot.py sites/<slug>/dist --sections
```

Needs Python Playwright and Edge or Chrome. If `python` cannot import playwright, try `py -3.11` or `python3`. The script checks sideways overflow, clipped text, broken images and JS errors at 1440, 768 and 390 px, then measures the frame rate of the hero and every moving section at 1440 px on a 2x screen (minimum 30 fps; 1x screens hide canvas lag that laptops with scaled displays show). It also checks that every WebGL scene draws, that the page reads fully with reduced motion (nothing left hidden, no pins), that Pause animations stops every loop and scene, and that a browser without WebGL gets no JS errors. At the first width it also checks the contrast of every visible text run against the color behind it, the focus outline of every Tab stop and the underline or contrast of links in running text (see `references/color-system.md`). Add `--cvd` to save color-blindness screenshots for review. It must print `QA PASSED`. A page whose QA fails is not finished: never call it ready or deliverable. Fix what page.json can fix and run QA again. If a failure sits in a library section or in build.py's colors (for example low contrast in the footer with correct theme values), stop, quote the failing lines and tell the user it is a library bug. Then open `dist/qa/page-1440.png` and a few files in `dist/qa/sections-390/` and look at them. Typical fixes: shorter titles, fewer items, a better photo.

## Step 7: Report

Tell the user, briefly:

- where the page is (`sites/<slug>/dist/index.html`) and how to view it (open the file, or `python -m http.server` in `dist`)
- archetype, preset and the sections used
- every placeholder and warning still open (fake KPIs, missing audio, form endpoint, stock photos or the sample video to replace)

## When the library does not fit

If the user needs a block no variant can carry, follow `references/custom-section-spec.md`. Write the spec, confirm it with the user, then build it with tokens only. Everything else in this workflow stays the same.

## Reference files

- `references/page-anatomy.md`: archetypes and exact slot order (generated)
- `references/section-catalog.md`: every variant, its fields, limits and preview (generated)
- `references/style-presets.md`: presets, design options, brand color overrides, tones
- `references/layout-blueprints.md`: the real-site layouts every page follows, how sections map to variants, and where the 3D visuals go
- `references/anti-slop.md`: design tells of generated pages (labels on every heading, 01/02 on everything, icon squares, arrows on every button, hover lift on cards, glows) and which build, lint and QA checks catch them. Read it before writing page.json.
- `references/color-system.md`: how brand colors become tokens (OKLCH, contrast, harmony rules), the gradient policy (flat surfaces; gradients only for photo scrims, edge fades, shading and hard-stop patterns, enforced by lint) and the contrast, focus and link checks in QA
- `references/content-rules.md`: copy rules and how to handle missing facts
- `references/mobbin-references.md`: where the tool, compare, awards, team, careers, steps and country sections come from, and how to research new sections on Mobbin
- `references/industry-voice.md`: how real BPO sites write (hero patterns, heading labels, proof, button labels, Vietnamese), measured on 120 homepages
- `references/assets.md`: image library, icons, flags, cities
- `references/animation-map.md`: which section carries which animation, with timings (generated)
- `references/custom-section-spec.md`: fallback for blocks outside the library
- `scripts/variety.py`: variant and preset usage across `sites/`, least used first; `--check page.json` compares one page with the rest

## Maintaining the library

After changing a template or schema, rebuild every page in `examples/` and `examples/variations/`, run lint and QA on each, then run `python SKILL/scripts/make_catalog.py` to regenerate the catalog, anatomy and animation map (add `--previews <dist> ...` to refresh preview images).

New variants widen the library only if agents can reach them: add each one to the matching slots in `templates/archetypes.json`, give every new animation id a timing line in `TIMING` in `make_catalog.py`, and put the variant in at least one page under `examples/variations/` so it is built and checked with the rest. Motion runs on vendored GSAP (`templates/vendor/gsap.js`, loaded on every page before `base.js`) and 3D on vendored Three.js (`templates/sections/_shared/three.js`, loaded only by sections that draw a WebGL scene); `references/motion-libraries.md` covers both, the `BL.motion` and `BLGL` helpers and how to update the vendored files. Canvas and WebGL motion share one render loop and one pause state in `templates/sections/_shared/ribbons.js` (`window.BLRibbons`); new 3D goes in a `BLGL.register` scene, never a second loop. Any new moving section follows "Motion and performance" in `references/custom-section-spec.md` and must pass the QA frame-rate check at 2x. `qa_screenshot.py` adds the class `bl-shot` to the page before element screenshots, so scroll-linked layouts can lay out flat for previews.
