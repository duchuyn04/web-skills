---
name: bpo-landing-builder
description: Build a production-quality landing page for a BPO, outsourcing, contact center, offshore staffing, AI data annotation or outbound sales company. The page is assembled by a script from pre-built, pre-animated sections, so layout and quality do not depend on the model. Use when the user asks for a BPO or outsourcing website, landing page, homepage or giao dien outsourcing, or wants to turn a company brief into such a page.
compatibility: Needs Python 3.9+ for build and lint. Visual QA needs Python Playwright plus Edge or Chrome. Works with any agent that can read files and run shell commands.
metadata:
  version: "5.6.0"
---

# BPO landing builder

You do not write HTML, CSS or JavaScript. You write one JSON file (`page.json`) with the page content. `scripts/build.py` turns it into a finished page using fixed section templates that already contain the layout, spacing, colors, responsive rules and the animations researched from 120 BPO websites. Your job is to choose well and write good copy.

`SKILL` below means the folder that contains this file. Use whichever path you loaded this file from. If you cannot run shell commands, stop and tell the user: the build scripts are required.

## Which path

Read the request and take the first row that matches.

| The user | Path |
|:---|:---|
| asks to look at a page this skill already built ("xem giúp", "review", "chỗ nào chưa ổn", sends its link or a screenshot) | Review. Run lint and QA with `--sweep` on its `dist`, open the screenshots, then send one table: each problem with its kind (Broken: fails for any brand, such as overflow, low contrast, clipped text; Off-system: differs from the rest of the page; Taste: a preference) and the fix in page.json. Change nothing until the user picks the rows |
| asks to change a page already built (`sites/<slug>/page.json` exists): a colour, a section, some copy, a photo | Edit. Change only what was asked in that page.json, keep the archetype, blueprint and variants as they are, rebuild, lint, QA, and report what changed. Pick another archetype, blueprint or variant only when the user asks |
| gives a site this skill did not build (their own code, WordPress, another builder) | Say in one line that this skill builds from page.json and does not edit other code; offer to build a new page from their content (Step 1) |
| anything else | Build a new page: Step 1 onwards |

## Rules that are never negotiable

1. Never edit files in `dist/`. Change `page.json` (or a template, if the user asked you to change the library) and rebuild.
2. Never invent facts: no made-up client names, quotes, agent names, CSAT, headcount, prices, salary rates, certifications or promises (such as "same-day onboarding"). A missing single figure becomes `"[KPI]"` (number fields) or `"[figure]"` (text). A missing whole block of proof (logos, testimonials, case studies, call recordings, salary rates) means you leave that section out; its slot is "recommended", so the build only warns. If a section's minimum item count is higher than the facts you have, drop the section or pick another variant; never pad a list to reach the minimum. List everything missing in your report. build.py enforces this against the brief: client names, quotes (word for word), certifications, tools, guarantees, languages, recordings and figures with a unit that the brief does not give are build errors (see "What build.py checks against the brief" in `references/content-rules.md`). Never extend a quote, never add a placeholder testimonial or logo, and never add facts to the brief to make the build pass. The reverse also holds: when the brief gives figures that are proof the business stands behind (headcount, years in business, delivered work, savings, retention, certifications), put them on the page in `metrics-counter` or `metrics-panel` and `compliance-badges`. Real BPO homepages lead with this proof, and a page without it reads as generic. Product limits, quotas and maximum times ("5 lần mỗi ngày", "tối đa 20 phút", "10 mẫu") are never proof: they go in no figure tile, badge or hero chip. When the brief has only such limits, leave metrics out and pick a blueprint without a required metrics slot.
3. Copy follows `references/content-rules.md` and `references/industry-voice.md`. Write the way real BPO vendors write: hero titles name the company's category ("Software outsourcing in Vietnam"), about a third of section headings are plain labels ("Our services", "Case studies"), the lead starts with the company name, and buttons use standard labels ("Contact us", "Get a quote"). The build fails on emoji, arrows, em or en dashes, curly quotes, banned AI words and phrases that mark copy as AI-written ("while you scale", "peace of mind", "hãy để chúng tôi"), so fix the wording, do not work around the checker. Treat its voice warnings as things to fix.
4. Keep the archetype's section order. Do not add keys that the schema does not list.

## Step 1: Collect the brief

Get these from the user or their files. Ask one short message for anything missing that matters (items marked *); do not stall on the rest.

- Company name*, what they sell*, who buys it* (industry, country)
- Delivery locations (cities), headcount, languages
- Proof: real KPIs, client names or logos, certifications, testimonials
- Contact: email, phone, WhatsApp or Zalo link, form endpoint if they have one
- Brand colors (hex, exactly as in the logo; build.py derives every shade) and page language (default English). The logo color always goes in `theme.accent`, even when it is bright: build.py darkens the button shade for contrast and keeps the original for highlights. Do not skip it and do not put it in `theme.primary`, which is the dark section and footer color. When page.json names a logo file (`site.logo`), build.py reads the logo's colours and fails a `theme.accent` that is not one of them, and a coloured logo without `theme.accent`. It also fails framework default colours (Bootstrap's `#D9534F` red, Tailwind's `#3B82F6` blue and the like) unless the brief or the logo has that exact colour. Never invent a brand colour: without a logo and without a colour in the brief, leave `theme` out and let the preset choose.
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

Every page follows the layout of one real BPO homepage, section by section. The layouts are in `templates/blueprints/` (about 90 real sites, measured in the browser and checked by hand against their screenshots). What changes from the source is the client's copy, brand colours and photos; the order, layout forms, tones and grid sizes stay. Read `references/layout-blueprints.md`, then:

```
python SKILL/scripts/variety.py --blueprints <archetype> --sites sites
python SKILL/scripts/variety.py --blueprint <key>
```

The first command lists the layouts that fit the archetype, unused ones first, with their section roles (`?` marks optional ones). Layouts marked `*` are preferred: clients named those sites (IRIS, Intelligent Outsourcing, Innovature, Bestarion) as the standard for a professional page, so they come first. Take the first unused `*` layout whose sections the brief can fill, and go further down only when none fits; otherwise pick an unused one whose sections the brief can fill. The second prints each section with the variants that fit it, calm ones first; `=` marks the real site's hero composition and `^` marks expressive variants (Step 2c). Set `"blueprint": "<key>"` in page.json and write one section per blueprint section, in order, leaving out only optional ones the brief cannot fill. build.py fails a page without a blueprint and a page that reorders or skips required sections. It warns when another site in `sites/` already follows the same blueprint and names free ones; switch when one fits the brief as well.

The hero follows the real site too. About two thirds of the blueprints name the hero composition of their source site in `"compose"` (a white card over a wide photo, a tilted photo mosaic, a round portrait beside a card of service chips, a row of photo cards under a centered headline, a photo stage with thumbnail tabs, a column of news cards, tall sector panels). build.py fails a page on such a blueprint whose hero is not one of those variants, or a business hero (`hero-voice`, `hero-ledger`, `hero-chat`, `hero-dashboard`, `hero-form`) when it fits the client. This is what keeps ten sites from opening with the same text-left, photo-right hero.

When the client picks a hero from another real site (a Mobbin section, a site they name), keep the blueprint for the rest of the page and add `"override_hero": {"reference": "<url of that hero>", "reason": "<what the client asked for>"}` to page.json. Any hero variant then fills the blueprint's hero slot, and the build prints the swap as a warning. Never set it on your own choice. The same goes for `"override_photos": {"reason": "..."}`: when the client asks for sections without photos (they have no real pictures and stock or screenshots do not fit), use `about-statement` and `steps-timeline` and record the reason; the photo-share check then prints a warning instead of failing. For a full-screen photo or video in a rounded inset frame with a very large headline (IntegratedBio), use `hero-fullbleed` with `"layout": "frame"`.

## Step 2b: Do not repeat a look

Every page is built from the same library, so two clients can end up with the same page in different words. Before you pick variants, run:

```
python SKILL/scripts/variety.py --archetype <archetype> --sites sites
```

It lists every slot with its variants ordered from least to most used across `sites/*/page.json`, and the presets the same way. For each slot, take the first variant in the line that fits the client's content (a variant still has to suit the facts: do not pick `models-board` without engagement models or `industries-rows` without industries). Prefer a preset nobody has used when the client has no brand colours. `build.py` warns when the finished page shares 70% or more of its look (preset plus variant per slot, hero and services count double) with another site, and names the slots to swap; treat that warning like a copy warning and fix it.

## Step 2c: Keep motion calm

BPO buyers judge a vendor on trust first: people photography, certifications, client logos, figures, case studies, star-rated reviews, office addresses with a map and a contact form. Sites such as TDCX, TaskUs and Concentrix keep motion quiet (reveals, counters, a logo strip, a review carousel, tabs). Pages built here do the same: `"motion"` defaults to `"calm"`, and you normally leave the field out.

Calm does not mean every page moves the same way. Each section carries its own entrance tied to what it shows (a photo frame that opens from the side of the copy, a check list that ticks in, panel bars that wipe open, stars that fill, a video that grows with the scroll), and `theme.motion_style` sets how the page's elements arrive: `rise`, `slide`, `fade` or `mask`. Leave `motion_style` out: build.py picks it from the brand name, so pages for different clients differ. Set it only when the client asks for calmer (`fade`) or livelier (`mask`) motion. `references/motion-research.md` has the measurements from 89 real BPO homepages behind these choices. Never add animation code to a page.

The library has two tiers.

Calm variants fit any page: everything that `variety.py` does not mark with `^`. A few of them carry one small moving piece tied to the business. Use at most one of those in the hero, and only when it fits (the archetype's hero line in `variety.py --archetype` shows which heroes it accepts):

Hero compositions from real sites (the blueprint names the one to use; each needs real content and photos):

| Variant | Source | Needs |
|:---|:---|:---|
| `hero-overlap` | Foundever | a wide people photo; lead and buttons sit on a white card over its lower edge |
| `hero-mosaic` | Kyanon | 6-10 photos of the team, offices and work, tinted in the brand colour |
| `hero-portrait` | MicroSourcing, Horatio | one smiling team member photo; 3-6 service chips linking to sections; 2-3 real figures |
| `hero-promo` | Firstsource | 3-4 photo cards linking to real sections (a service, a case study, careers) |
| `hero-tabs` | Genpact, TDCX, CMC | 3-4 real service lines, each with its photo; replaces the photo sliders of real sites |
| `hero-news` | Concentrix | 2-3 real items (case studies, a report, a new center) and an optional featured item |
| `hero-panels` | ELEKS | 3-4 real sectors or service lines, each with a photo |
| `hero-finder` | IRIS | one person photo; 2-3 real service lines for the small cards; 2-3 ways to browse (industry, size, need) whose options link to page sections |

Business heroes, when the client's work fits:

| Business | Hero |
|:---|:---|
| Contact center, multilingual support | `hero-voice` (team photo with a call card that answers in each language the brief names), `hero-chat` (sample support chat; label it as a sample) |
| Accounting, payroll, back office | `hero-ledger` (paperwork photo with report sheets that fan in and get ticked) |
| Several service lines with reporting | `hero-dashboard` (panels built from the real services and stats) |
| Sells on a quick quote or call back, and has (or will add) a form endpoint | `hero-form` (enquiry form card in the first screen over a photo or brand-colour panel) |
| Anything else | `hero-fullbleed` with `"align": "center"` first (the hero clients rated most professional), `hero-slides` when the client wants several slides, then `hero-stage` (one wide office or work photo, or a video, under the copy), `hero-scatter` (4-6 real photos of the office, city and work), `hero-split-image`, `hero-collage`, `hero-qualifier`, `hero-cycler-centered`, `hero-gradient` |

Photos: a page with 6 or more content sections needs a photo in at least 40% of them (real BPO homepages: median 33%, top quarter 44%), and at most two sections may put an icon on every item; build.py fails otherwise and names the sections that take a photo. Text-only sections now take photos: `metrics-counter` "image" (the figures over a photo), `services-bento` first card "photo", `process-sticky` and `steps-row` a photo on every step (process-sticky swaps the pinned photo as the reader moves through the steps), `industries-rows` a photo on every row (shown in the card that follows the hovered row), `faq-accordion` "photo", `contact-split` "aside.photo". Use the client's photos first, then library photos from `references/assets.md` that match the section. Library photos are strangers: each one appears once on a page, and its alt says what the picture shows ("Two people checking invoices at a desk"), never the company name, "our team" or "our office". A stock face never stands for a named person: no library `avatar` on reviews and no library portraits in `team-grid` or `team-coverflow`. build.py fails all of these.

No mock UI: no grey bars standing in for text, drawn charts without data, fake notifications, like counts, hearts, floating chips, code windows or placeholder dashboards, in library or custom sections. Clients read them as a generated page. QA fails empty shapes stacked like text lines or drawn as a chart, and build.py fails the footer wordmark unless the brief asks for it (`references/anti-slop.md`, Mock UI). When the client wants a hero with several slides, use `hero-slides` (2-4 slides switched by dots, each slide in its own layout) instead of writing a custom hero.

Trust sections to reach for when the brief has the content: `testimonials-rated` (3-8 real reviews with star ratings, optional overall score), `locations-gmap` (office cards beside a live Google Map; a blueprint with no locations slot can show the office through `contact-split` with `"map": {"query": "<address>"}`), `logo-wall` (8+ real client names), `metrics-rings` (real percentages), `case-filter` (4+ real cases), `voice-sample` (real call recordings) and `cost-calculator` (real salary rates). `process-sticky`, `services-stack`, `models-board` and `industries-rows` need no client figures.

Expressive variants (`^` in `variety.py`) are 3D objects, WebGL scenes, particles and folding effects: `hero-globe`, `hero-particles`, `hero-terrain`, `hero-flow`, `hero-wavefield`, `hero-magnetic`, `hero-dark-network`, `hero-ribbons`, `hero-orbits`, `hero-monolith`, `hero-prism`, `hero-isometric`, `hero-deck`, `hero-shatter`, `hero-liquid`, `hero-sundial`, `services-cube`, `services-cylinder`, `process-layers`, `process-pipeline`, `industries-slats`, `metrics-bars3d`, `locations-relief`, `proof-book`, `about-helix`, `team-coverflow`, `faq-fold` and `cta-letter`, plus the `"visual"` backdrop on bands. build.py fails any of them unless page.json sets `"motion": "expressive"`, and it fails `"expressive"` unless the brief asks for a 3D or animation-led page (words such as "3D", "WebGL", "immersive", "nhiều hiệu ứng"). Never add such words to the brief yourself. `examples/variations/*.page.json` shows the expressive variants; copy their data shape only for such a client, and read "Where the 3D goes" in `references/layout-blueprints.md`.

build.py warns when another site in `sites/` already opens with the same hero and names unused ones. Switch only to one that fits the business as well; a fitting repeated hero is better than an unfitting new one.

Every footer carries a Pause animations button that stops all motion on the page (WCAG 2.2.2); keep `motion_toggle` on whenever the page has a loop, a carousel, a video or `testimonials-drift`.

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

## Step 3a: Search and share tags

build.py writes the SEO head for you: title, description, robots, canonical, Open Graph and Twitter tags, a favicon (SVG plus the PNG that Google Search shows), JSON-LD (Organization, WebSite, WebPage, and FAQPage when the page has an FAQ section), `sitemap.xml` and `robots.txt`. You only supply facts:

- `site.title`: the service first, then the brand, within 60 characters ("Offshore accounting teams in Da Nang | So Sang"). 71 of 85 real BPO homepages end the title with the brand. Google cuts long titles to the screen width, and build.py warns above 60.
- `site.description`: one or two plain sentences, 120-160 characters, that say what the company does, where and for whom. Write it for the searcher, not as a keyword list.
- `seo.url`: the page's live https address, ending in `/` or `.html`. With it the build adds the canonical link, `og:url`, absolute share image URLs, `sitemap.xml`, and `robots.txt` when the page sits at the root of the host. Leave it out until the client gives the domain; never invent one.
- `seo.image` and `seo.image_alt`: the share picture, a 1200 x 630 JPG or PNG photo (not the logo). Left out, the hero photo is used.
- `seo.icon`: the client's square PNG icon. Left out, build.py draws a monogram from `site.brand_mark`.
- `seo.alternates`: when the client has the same page in English and Vietnamese, list both versions and `x-default` with full addresses, the same list on each page (hreflang).
- `seo.google_verification`, `seo.bing_verification`: the content value of the verification meta tag, when the client gives it.
- `seo.locale`: only when the country differs from the language default (`en_US`, `vi_VN`), for example `"en_AU"`.
- `seo.index`: `false` keeps a published page out of search. A page that still has placeholders is built with `noindex` automatically, so a demo never gets indexed.

Structured data only carries facts shown on the page: footer phone and email, social profile links, office addresses from `locations-gmap`, FAQ answers. Placeholders and example.com addresses are left out. Reviews are never marked up as ratings, because Google does not show reviews a company publishes about itself. `references/seo.md` has the rules, their sources and the measurements behind them.

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
python SKILL/scripts/qa_screenshot.py sites/<slug>/dist --sections --sweep
```

Needs Python Playwright and Edge or Chrome. If `python` cannot import Playwright, use a Python that has it (on Windows `py -0` lists the installed versions, then for example `py -3.11`). The script checks sideways overflow, clipped text, broken images and JS errors at 1440, 768 and 390 px, then measures the frame rate of the hero and every moving section at 1440 px on a 2x screen (minimum 30 fps; 1x screens hide canvas lag that laptops with scaled displays show). It also checks that every WebGL scene draws, that the page reads fully with reduced motion (nothing left hidden, no pins), that Pause animations stops every loop and scene, and that a browser without WebGL gets no JS errors. At the first width it also checks the contrast of every visible text run against the color behind it, the focus outline of every Tab stop and the underline or contrast of links in running text (see `references/color-system.md`). `--sweep` then narrows the page from 1440 to 360 px in 20 px steps and fails anything that sticks out sideways or header items that overlap at any width in between (a nav that collides at 1100 px passes the three fixed widths). It also opens every slide of a hero carousel (`hero-slides` or a custom hero with several slides) and checks it like the first one, and fails a slide heading that a photo or card covers by more than 10% (a giant word set behind pictures included); shots of the slides go to `dist/qa/slides-<width>/`. Add `--cvd` to save color-blindness screenshots for review. It must print `QA PASSED`. A page whose QA fails is not finished: never call it ready or deliverable. Fix what page.json can fix and run QA again. If a failure sits in a library section or in build.py's colors (for example low contrast in the footer with correct theme values), stop, quote the failing lines and tell the user it is a library bug. Then open `dist/qa/page-1440.png` and a few files in `dist/qa/sections-390/` and look at them. Typical fixes: shorter titles, fewer items, a better photo.

## Step 7: Report

Tell the user, briefly, in the language they wrote in:

- first, every choice you made for them, one line each with the reason and an offer to change it: archetype, blueprint, preset, hero variant, motion. This is the only place where you may have guessed wrong, so it goes on top
- where the page is (`sites/<slug>/dist/index.html`) and how to view it (open the file, or `python -m http.server` in `dist`)
- archetype, preset and the sections used
- every placeholder and warning still open (fake KPIs, missing audio, form endpoint, stock photos or the sample video to replace)
- SEO: whether the page is indexable (`noindex` while placeholders remain), whether `seo.url` is set, and the launch steps from "After launch" in `references/seo.md` (Search Console, Bing Webmaster Tools, Google Business Profile)

## When the library does not fit

If the user needs a block no variant can carry, follow `references/custom-section-spec.md`. Write the spec, confirm it with the user, then build it with tokens only. Everything else in this workflow stays the same.

## Reference files

- `references/page-anatomy.md`: archetypes and exact slot order (generated)
- `references/section-catalog.md`: every variant, its fields, limits and preview (generated)
- `references/style-presets.md`: presets, design options, brand color overrides, tones
- `references/layout-blueprints.md`: the real-site layouts every page follows, how sections map to variants, and where the 3D visuals go on expressive pages
- `references/anti-slop.md`: design tells of generated pages (labels on every heading, 01/02 on everything, icon squares, arrows on every button, hover lift on cards, glows) and which build, lint and QA checks catch them. Read it before writing page.json.
- `references/flat-style.md`: the tells of generated sites and the flat colour, shadow and gradient rules (shared by all skills; `scripts/flat_css.py` checks them in lint)
- `references/color-system.md`: how brand colors become tokens (OKLCH, contrast, harmony rules), the gradient policy (flat surfaces; gradients only for photo scrims, edge fades, shading and hard-stop patterns, enforced by lint) and the contrast, focus and link checks in QA
- `references/content-rules.md`: copy rules and how to handle missing facts
- `references/mobbin-references.md`: where the tool, compare, awards, team, careers, steps, country and the form, stage and scatter hero sections come from, and how to research new sections on Mobbin
- `references/industry-voice.md`: how real BPO sites write (hero patterns, heading labels, proof, button labels, Vietnamese), measured on 120 homepages
- `references/assets.md`: image library, icons, flags, cities
- `references/animation-map.md`: which section carries which animation, with timings (generated)
- `references/motion-research.md`: how 89 real BPO homepages animate (scroll entrances, hovers, carousels, sticky and scroll-linked pieces) and the four motion styles built from it
- `references/custom-section-spec.md`: fallback for blocks outside the library
- `references/seo.md`: the search and share tags build.py writes, the fields that feed them, what 85 real BPO homepages do, and the launch steps outside the page
- `references/maintaining.md`: adding a rule, a variant or a check, versioning, and the regression tests to run after a change to the library
- `scripts/variety.py`: variant and preset usage across `sites/`, least used first; `--check page.json` compares one page with the rest

## Changing the library

Adding a rule, a variant, a section or a check, and the regression tests to run afterwards, are in `references/maintaining.md`. Read it before editing build.py, a template, a schema or this file; building a page for a client does not need it.
