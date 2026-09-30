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

- A label (eyebrow) above a title only when it adds something the title does not say: a service line, a region, a date. At most a third of the section titles; build.py fails above that and when a label repeats a word of its title ("Security" above "Security and compliance"). Labels are plain small text: the short rule drawn before them read as an em dash and is gone, and lint fails any short line drawn before or after text (`dash-rule`). Vietnamese pages never set labels in tracked capitals.
- "01, 02" numbers only on real sequences: process steps, timelines. Templates number only those sections (`data-sequence`); lint fails a numbered marker anywhere else.
- `*accent*` words on the hero title. build.py warns when more than one title below the hero has them.

## Components

- Icons take the colour of their label and sit beside it, not in a tinted square. At most two sections with an icon on every item (build.py warns).
- Cards only where the card is a link or holds one. Rows of three or more look-alike boxes that lead nowhere read as a template; QA warns when three sections have them. Plain columns under a rule, a list or a table carry the same content.
- Hover movement and hover shadows only on links and buttons. QA fails any element that moves or grows a shadow on hover and cannot be clicked.
- Shadows are neutral. A shadow in the brand colour with a blur of 16px or more is a glow; lint fails it. QA warns when more than 12 elements that are not controls carry a resting shadow.
- Frosted glass (`backdrop-filter`) only on the header, menus, dialogs and floating controls. lint warns elsewhere.
- Surfaces are flat; see `color-system.md`, Gradients.

## Buttons and links (you)

- Labels say what happens: "Get a quote", "Book a call", "See case studies". Not "Learn more", "Read more", "Submit" or "Click here" (lint warns).
- Arrows on text links that go somewhere, not on buttons. lint warns when more than half of the buttons and links carry one.
- Every tap target is at least 24 by 24 px, or has room around it (WCAG 2.5.8). QA fails smaller ones.

## Brand and hero (you)

- The hero lead names the company, so the first screen could not belong to another brand. build.py fails a hero lead without the brand name.
- Hero variants that change on a timer (`hero-cycler-centered`, `hero-deck`) hide most of their text most of the time; say the essentials in the lead too (build.py warns).
- Stats may stay in the hero or right below it: 58% of real BPO homepages show big numbers (`industry-voice.md`), which outweighs the vendor advice against stat strips.

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

Fix the template, not the page, and rebuild every example (SKILL.md, "Maintaining the library").
