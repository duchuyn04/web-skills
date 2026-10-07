# Anti-slop design rules

Generated pages converge on the same look: a label above every heading, "01 / 02" on everything, one coloured word in each title, an icon in a tinted square on every card, an arrow on every button, every section fading up, cards that lift on hover but lead nowhere. Anthropic's and OpenAI's own frontend guidance name these patterns as the tells of model-made sites. The research behind each rule, with sources (Anthropic frontend-design skill, OpenAI frontend guide, Material, Carbon, GOV.UK, Polaris, Atlassian, Apple HIG, Nielsen Norman Group, WCAG 2.2), is in `docs/research/ui-anti-slop.md` in the job repository.

The library templates already follow these rules. What you control in `page.json` is marked "you".

## Type

- Headings do not use Inter, Roboto, Arial, Helvetica, Open Sans, Lato, a system stack or Space Grotesk, unless it is the client's brand font. Every preset has its own heading face. build.py warns.
- Caps only for short labels, tracked 0.05-0.12em. lint fails other tracking on uppercase text.
- No text lighter than weight 400 below 24px. QA fails it.
- Lines under 75 characters. QA warns above 75 and fails above 90.
- No justified text. lint fails it.

## Labels, numbers, accents (you)

- No pill badge above the hero title: an outlined, rounded label over the headline is one of the most named tells of generated pages. Presets draw labels as plain text; `"theme": {"eyebrow": "pill"}` stays for a client whose own site uses pills.
- A label (eyebrow) above a title only when it adds something the title does not say: a service line, a region, a date. At most a third of the section titles; build.py fails above that and when a label repeats a word of its title ("Security" above "Security and compliance"). Labels are plain small text: the short rule drawn before them read as an em dash and is gone, and lint fails any short line drawn before or after text (`dash-rule`). Vietnamese pages never set labels in tracked capitals.
- "01, 02" numbers only on real sequences: process steps, timelines. Templates number only those sections (`data-sequence`); lint fails a numbered marker anywhere else.
- `*accent*` words on the hero title. build.py warns when more than one title below the hero has them.

## Components

- Icons take the colour of their label and sit beside it, not in a tinted square. At most two sections with an icon on every item (build.py warns).
- Cards only where the card is a link or holds one. Rows of three or more look-alike boxes that lead nowhere read as a template; QA warns when three sections have them. Plain columns under a rule, a list or a table carry the same content.
- Nothing rises or grows a shadow on hover, cards that are links included: a hover changes the border, the background or the underline. QA fails any element that moves or grows a shadow on hover and cannot be clicked; lint warns on a rise (`hover-lift`) or a hover shadow (`hover-shadow`) anywhere.
- Shadows only on what floats: the header once scrolled, menus, the mega menu, popovers, dialogs, the floating chat and assistant, map tooltips, and drawn 3D objects on expressive pages (marked `/* flat-ok: ... */` in the CSS). Photo frames, panels, forms, pricing plans, testimonial cards and buttons are flat: a 1px border or a surface tone separates them. lint warns on any other shadow larger than a hairline (`resting-shadow`); `tools/check_flat_css.py` keeps the library at zero. QA warns when more than 12 elements that are not controls carry a resting shadow.
- Shadows are neutral. A shadow in the brand colour with a blur of 16px or more is a glow; lint fails it.
- Frosted glass (`backdrop-filter`) only on the header, menus, dialogs and floating controls. lint warns elsewhere. The glass badges over photos are opaque surfaces.
- Surfaces are flat; see `flat-style.md` (shared by every skill: the tells of generated sites, flat colour, shadows, gradients) and `color-system.md`, Gradients.

## Buttons and links (you)

- Labels say what happens: "Get a quote", "Book a call", "See case studies". Not "Learn more", "Read more", "Submit" or "Click here" (lint warns).
- Arrows on text links that go somewhere, not on buttons. lint warns when more than half of the buttons and links carry one.
- Every tap target is at least 24 by 24 px, or has room around it (WCAG 2.5.8). QA fails smaller ones.

## Brand and hero (you)

- The hero lead names the company, so the first screen could not belong to another brand. build.py fails a hero lead without the brand name.
- Hero variants that change on a timer (`hero-cycler-centered`, `hero-deck`) hide most of their text most of the time; say the essentials in the lead too (build.py warns).
- Stats may stay in the hero or right below it: 58% of real BPO homepages show big numbers (`industry-voice.md`), which outweighs the vendor advice against stat strips.

## Mock UI

Rules 5, from a user review of six generated sites (SoGlobal, 2026-09-30): decoration that imitates software reads as generated. Real BPO homepages show real words, real figures and photos.

- No grey bars standing in for lines of text (skeleton lines), no drawn bar charts without data, no fake notifications, like counts, hearts, chat bubbles, floating chips or badges, code windows or dashboards filled with placeholder rows. A card over a photo carries a real service name, a figure from the brief or a tick, nothing else.
- `qa_screenshot.py` fails empty filled shapes stacked like text lines and rows of empty bars on one baseline ("mock UI"). Progress bars, sliders, meters and controls are exempt; a custom section that truly needs such a shape marks it `data-mock-ok` and says why in the spec. Browser window dots and other drawn device frames are decoration, not such a case: drop them instead of marking them.
- Sample screens (screenshots of sites or app screens shown as examples of the work, as on a web design company's page): real pages in the page's language, spread across the industries the brief names rather than the two closest to hand, each tagged on the picture as a sample ("Bản mẫu", "Sample"). A sample shows no figures, certifications or client names as if they were the company's own, and screenshots stay off sections whose sentence a photo can show.
- 3D is for a picture of the actual work (a ledger, a desk, a device), used once on a page and only when the brief asks for it.
- The footer wordmark (the brand name edge to edge in huge type) stays off unless the brief asks for it; build.py fails it otherwise.
- The hero users rated most professional: a full-bleed photo under a dark scrim with centered copy (`hero-fullbleed` with `"align": "center"`, or a `"fullbleed"` slide in `hero-slides`). `variety.py` lists these heroes first.

## Colour

- A violet accent on a light page, and a cream page with a terracotta accent, are the default looks of generated sites. build.py warns when a preset produces them without client colours. The client's own colours always win.

## Pictures

- A page with 6 or more content sections carries a photo in at least 40% of them (real BPO homepages: median 33%, top quarter 44%); build.py fails below that and lists the sections that take a photo.
- At most two sections put an icon on every item; build.py fails a third. Rows of icon cards are what makes a page read as text and template.
- The hero follows the source site's composition when the blueprint names one (`"compose"`), so sites do not all open with text beside one photo.

## Motion

- Reveals are short (0.3-0.4s, 12px, stagger capped at four items). lint fails reveal or hover transitions longer than 0.5s.
- Pages are calm by default (SKILL.md, Step 2c): photos, reveals, counters, a logo strip, a review carousel, tabs and a map, with at most one contextual piece in the hero. Expressive variants (3D objects, WebGL scenes, particles, folding paper) and band `"visual"` backdrops fail the build unless page.json sets `"motion": "expressive"` and the brief asks for a 3D or animation-led page.
- At most one pinned scroll section per page (build.py warns).

## When a rule fails in a library section

Fix the template, not the page, and rebuild every example (`references/maintaining.md`, "Maintaining the library").
