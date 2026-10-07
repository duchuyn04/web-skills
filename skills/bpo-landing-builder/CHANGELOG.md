# Changelog

The version is the one at the top of SKILL.md. The major number is the rules version (`RULES_VERSION` in `scripts/build.py`): it goes up when a new check can fail a page that built before.

## 5.5.3 (2026-10-07)

From a font study for Vietnamese pages (`research/fonts/` in the project). Rules stay at 5: nothing here fails a page that built before.

- Headings on `"lang": "vi"` pages use a line-height measured for their font (`VI_HEAD_LH` in build.py; `html:lang(vi)` rule in base.css). Vietnamese stacked marks (ẫ, ệ, ữ) at the English display line-heights of 1,06 to 1,12 touched the descenders of the line above in Plus Jakarta Sans (human-warm) and Bricolage Grotesque (dark-ai), and sat close in the others. Values: 1,15 (Montserrat, Source Sans 3, Source Serif 4, Public Sans and others) to 1,3 (Plus Jakarta Sans), 1,35 (Onest) and 1,4 (Bricolage Grotesque). English pages are unchanged.
- build.py stops at import when a family in `VI_FONTS` has no measured value, so a new Vietnamese font cannot ship with the tight line-height.

## 5.5.2 (2026-10-07)

From a review of the whole plugin. Rules stay at 5: the new hero-form findings are warnings.

- `hero-form` is a business hero (`BUSINESS_HEROES`): it may replace a blueprint's hero composition, like `hero-voice` and `hero-ledger`. `variety.py --blueprint` now lists on a hero slot with `"compose"` only the variants build.py accepts there (before, it offered `hero-form` on 33 blueprints and the build took it on 13).
- `hero-form`: a `topic_label` without `topic_options` (or the reverse) leaves the select out instead of drawing an empty one, with a warning; a single ticked point warns.
- `hero-dark-network`: the drawn bar chart in the panel is gone (QA failed it as mock UI); the panel shows only the label and value rows. Example `fx-hero-dark-network` and a new preview.
- Examples for `about-statement` and `steps-timeline` (`fx-statement-timeline`), with previews; every variant is now built by the tests.
- The share image falls back to a video hero's poster (`hero-stage`, `hero-fullbleed` with a video), so those pages get `og:image`.
- build.py refuses an `--out` that holds page.json or a folder with `assets/` or `index.html` it did not build, reads page.json saved with a byte order mark (Notepad, PowerShell 5.1), and reports a missing file, a page that is not an object or a section that is not `{"type", "data"}` as one ERROR line instead of a traceback. A missing `preset` or `archetype` is reported once.
- "Adding a rule" and "Maintaining the library" moved from SKILL.md to `references/maintaining.md`.

## 5.5.1 (2026-10-07)

From a review of the second slide of a web design company's hero (a giant word behind three website screenshots). Rules stay at 5: the new copy finding is a warning and the slide checks run only with `--sweep`.

- `qa_screenshot.py --sweep` opens every slide of a hero carousel (the buttons in the hero whose `aria-controls` names a slide or tab panel) and checks each one for sideways overflow, clipped text and, at the first width, contrast. It also measures how much of each hero heading a photo or card covers: over 10% fails, over 3% warns (a giant word half hidden behind screenshots read as a covered heading to the user). Before, only the first slide was ever checked, so a heading hidden behind screenshots on phones passed. Shots of the slides go to `qa/slides-<width>/`.
- Copy: Vietnamese spoken or slang words ("ưng", "ưng ý", "xịn", "xịn sò", "chất lừ", "đỉnh của chóp", "hết sảy") print a `colloquial-vi` warning in build and lint with neutral words to use instead. Test case `colloquial-vi`.
- `references/anti-slop.md`, Mock UI: browser window dots and drawn device frames are dropped, not marked `data-mock-ok`; sample screens are real pages in the page's language, spread across the brief's industries, tagged as samples on the picture, and show no figures, certifications or client names as the company's own.

## 5.5.0 (2026-10-07)

Three calm heroes from trending Mobbin hero sections. Rules stay at 5: nothing here fails a page that built before.

- New `hero-form` (after beehiiv, Circle, Parker and HBO Max advertising): headline, lead and 2-5 ticked points on the left, an enquiry form card in the first screen on the right (name, work email, company, optional phone, optional service select and message) over a rounded photo or flat brand-colour panel. The panel opens sideways, the card rises, the fields arrive in order. The build warns when the form has no `action`, as it does for the contact sections.
- New `hero-stage` (after Customer.io, Figma, Vizcom, FLORA, Sana and Clay): copy at the top in three alignments (`left`, `center`, `split` with the headline left and the lead and buttons right), then a wide rounded photo or looping video stage that opens from the text column to the screen edges as the page scrolls. Video gets a pause button and follows Pause animations; phones keep the stage at the column width.
- New `hero-scatter` (after Maze, MasterClass at Work and T1 Energy): copy on a rounded panel with 4-6 photos of mixed sizes set loosely on the right, some past its edges; they grow in one after another, drift by depth on scroll and lean toward a fine pointer. Phones get one row of mixed sizes under the copy.
- All three are in the hero slot of every archetype, have examples in `examples/variations/` (`fx-hero-form`, `fx-hero-stage`, `fx-hero-stage-b`, `fx-hero-scatter`), previews, catalog entries and timing lines, and rows in `references/mobbin-references.md`.

## 5.4.0 (2026-10-07)

- New `about-statement` (statement left, paragraphs right, points in a row under a rule) and `steps-timeline` (one card: copy and buttons left, numbered steps on a line right), both without photos, after Airtasker, United Carriers, Railway and Givingli on Mobbin. They fill the same feature-split slots as `about-mosaic` and `feature-rows`.
- page.json `"override_photos": {"reason"}`: the client chose sections without photos; the photo-share check prints a warning instead of failing.
- `roles-carousel`: when every card fits the track they are centred and the scroll bar and arrows are hidden (a left-aligned row looked off-centre).
- New `floating-assistant` (group floating, after GoDaddy Conversations, Resend Help, Podia and Klook support on Mobbin): a chat panel in the corner with a greeting, suggested questions, answers written in page.json and a call-back form. Answers are never generated, so the build checks them against the brief like any section; a typed question is matched to the topics by its words without accents and with common words left out, and one it cannot answer offers the call-back instead of guessing. A teaser shows once per visit after 8 s. Keyboard and screen reader friendly, no motion with reduced motion, a bottom sheet on phones that does not open the keyboard. Rules stay at 5.

## 5.3.0 (2026-10-07)

A hero the client picks from another site, and a framed hero after IntegratedBio. Rules stay at 5: both are opt-in fields.

- `hero-fullbleed` gets `"layout": "frame"`: the photo or video fills a rounded frame inset 12px from the page edge and the first screen, with a very large headline top left, the lead bottom left and the buttons bottom right (the main one with a square arrow chip). Its intro (`hero-frame-intro`): the frame opens from a small pill in the middle (clip 2s expo.inOut), the headline and lead rise line by line out of masks from 1.6s, then the header fades in and the buttons pop up; the media grows a little as the hero scrolls away. Reduced motion shows the end state, and CSS shows the copy after 4s if the script never runs. The frame turns off the page's angled or curved hero edge.
- page.json `"override_hero": {"reference", "reason"}`: when the client chose a hero from another real site, any hero variant fills the blueprint's hero slot (and its `compose` list no longer applies); the rest of the page still follows the blueprint, and the build prints the swap as a warning.

## 5.2.1 (2026-10-07)

- SKILL.md rule 2: figures put in metrics are proof the business stands behind; product limits, quotas and maximum times never go in a figure tile, badge or hero chip, and a brief with only such limits leaves metrics out and picks a blueprint without a required metrics slot. Rules stay at 5.

## 5.2.0 (2026-10-07)

Width sweep in QA, and a clearer workflow around a build. Rules stay at 5: the sweep runs only with `--sweep`, and on a site pinned to an older rules version its findings print as warnings.

- `qa_screenshot.py --sweep` narrows the page from 1440 to 360 px in 20 px steps (`--sweep FROM,TO,STEP` to change) and reports the width ranges where an element sticks out sideways or header and nav items overlap (fail), and where a short button or nav label wraps onto two lines (warning). The three fixed widths miss a nav that collides at 1100 px or a block that overflows at 880 px. Step 6 now runs it.
- SKILL.md: a "Which path" table (review a built page, change a built page, a site this skill did not build, a new page); the report starts with the choices made for the user; an "Adding a rule" section on keeping the rule set small.

## 5.1.0 (2026-10-01)

Search and share tags. Rules stay at 5: every new finding on existing fields is a warning, and only the new `seo` fields fail when malformed.

- New `scripts/seo.py`, called by build.py. It writes the robots meta, canonical link, hreflang alternates, Open Graph (type, site name, locale, title without the brand, description, url, image with width, height and alt), `twitter:card`, verification meta tags for Search Console and Bing, a favicon (monogram SVG plus a 192 px PNG, because Google Search does not show SVG favicons) and one JSON-LD graph: Organization, WebSite, WebPage and FAQPage, from facts shown on the page only. It also writes `sitemap.xml` and, at the root of a host, `robots.txt`.
- New optional page field `seo`: `url`, `image`, `image_alt`, `icon`, `locale`, `index`, `alternates`, `google_verification`, `bing_verification`.
- A page with placeholders is built with `noindex, nofollow` and without a sitemap, so demos stay out of search.
- The sitemap `lastmod` changes only when the page content changes: build-report.json keeps a content hash.
- Warnings: title over 60 characters or without the brand, description over 160 characters or starting with the title, no `seo.url` outside examples, a share image under 600 px wide, no photo to share, an SVG or non-square `seo.icon`, a logo under 112 px, a page in a subfolder (no robots.txt there).
- Lint: `<html lang>`, one title, a meta description, og:title, og:description and og:type, a favicon link, at most one absolute canonical, full https hreflang links and valid JSON-LD are errors; a sitemap next to a noindex page or with another URL than the canonical fails. Missing og:image, an SVG-only favicon and skipped heading levels warn.
- `references/seo.md`: what 85 real BPO homepages put in their head (measured with the new `scripts/research/seo_probe.py`), what the build writes, the fields, and the steps after launch (Search Console, Bing Webmaster Tools, Google Business Profile, consistent name, address and phone). Sources: Google Search Central, Bing, IndexNow, schema.org, ogp.me, Meta and web.dev.
- Tests: 11 new cases in `tests/cases.json`.

## 5.0.0 (2026-09-30)

Rules 5, from a user review of six sites built with 4.2.0 (SoGlobal: accounting, IT and marketing outsourcing). Pages built under rules 4 keep building with `"rules": "4"`; the new checks then print as warnings.

- No mock UI. QA fails empty filled shapes stacked like lines of text and rows of empty bars drawn as a chart (`mock UI`): the user read grey placeholder lines, fake notifications, hearts, floating chips and code windows as a generated page. Progress bars, sliders, meters and controls are exempt; a custom section marks a genuine exception with `data-mock-ok`. `references/anti-slop.md` has a new Mock UI section.
- `hero-finder` cards carry real words only: a title, an icon or a tick, and an optional one-line note. The drawn bar chart and grey list lines are gone (`mark` is replaced by `note` and `tick`).
- The footer wordmark (the brand name in huge type) fails the build unless the brief asks for it.
- New calm variant `hero-slides`: 2-4 slides switched by round dots with a 6 s timer that holds on hover, focus and Pause animations and stops once a dot is picked. Every slide takes its own layout (`fullbleed`, `split`, `cards`, `panels`, `overlap`; build.py fails a repeated layout or a layout without its photo, ticks, cards or panels). The first slide carries the h1. On phones and tablets each slide keeps its own height and the dots sit under the header, so nothing is cropped and the dots stay in the first screen. It replaces the custom multi-slide heroes six sites had to write.
- The heroes users rated most professional, `hero-fullbleed` (with `"align": "center"`) and `hero-slides`, are listed first by `variety.py`.
- The hero copy checks read the first slide of `hero-slides`.

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
