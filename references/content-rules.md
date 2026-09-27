# Content rules

build.py and lint_output.py enforce the copy rules below (they come from a strict house style guide: no emoji, no text arrows, no em or en dashes, no stock AI phrasing). Write copy that passes the first time.

## Hard rules (build fails)

- No emoji or emoji flags. Icons come from `icon` fields, flags from `flag` fields.
- No text arrows or arrow characters. Buttons and links add the SVG arrow themselves, so a label is just words: `"Get a staffing plan"`.
- No em dash or en dash. Use a comma, a colon or parentheses. Ranges use a plain hyphen: `14-21 days`, `10-25 agents`.
- Straight quotes only.
- None of these words: additionally, align with, bolster, crucial, deep dive, delve, emphasize, enduring, enhance, foster, garner, highlights (verb), interplay, intricate, landscape, meticulous, pivotal, quietly, robust, showcase, tapestry, testament, underscore, valuable, vibrant, boasts, breathtaking, nestled, stunning, renowned, diverse array, groundbreaking, serves as, stands as, functions as, operates as, at its core, fundamentally.
- No "not just X, but Y" or "it's not about X, it's Y". Say the positive claim.
- No chatbot phrases ("Certainly!", "Great question", "I hope this helps").
- Every text field has a length range (see `section-catalog.md`). Too long means rewrite shorter, never "make the font smaller".

## Writing each field

Read `industry-voice.md` first. It shows, with numbers from 120 real BPO homepages, what makes copy look AI-written to people in the industry. The short version:

- Hero title: 3-8 words about the company or its category, not about the reader. Good: `"Customer operations for *banks, telcos and retail*"`, `"Software outsourcing *in Vietnam*"`, `"Outbound SDR teams for *B2B sales*"`. Bad: `"Support teams that protect your CSAT while you scale"` (addresses the reader, "[people] that [verb] your [thing]" formula) and `"Transforming the future of customer experience"` (says nothing). Accent 1-3 words.
- Lead: the company name is the subject of the first sentence. Say what it does, for whom and since when, then scale or place: `"Northbridge CX has run voice, chat and back-office programs since 2009. Our 2,400 agents work from Manila, Bogota and Krakow in 12 languages."` Two sentences at most.
- Section headings: about a third are plain labels ("Our services", "Industries we serve", "How it works", "Case studies", "Frequently asked questions"). At most one in four addresses the reader. Accent markup on two or three headings, not all.
- Button labels: the labels real sites use: "Contact us", "Talk to an expert", "Get a quote", "Book a call", "Learn more", "See case studies". Do not invent labels such as "Ask about fit".
- Eyebrows: 1-4 plain words that add information ("Since 2009", "Delivery centers"). Do not repeat the heading.
- Card text: one sentence that says what the team does, in which tools or for which customers. At most one operational detail per card (a time, a tool, a count); do not scatter timetables ("every Friday", "by 07:00") across the page.
- Use the category words buyers search for (outsourcing, BPO, offshore, customer support, back office, delivery center, dedicated team). Repeating them is normal.
- Headings are sentence case. Do not capitalize every word.
- Paragraph fields that accept markup (for example `about-mosaic` paragraphs) take `**bold**` for two or three key terms, such as the service names. Do not bold whole sentences.

## Numbers and claims

- Use only facts the client gave you. Never invent CSAT, headcount, savings, prices, salary rates, client names, quotes, agent names or service promises.
- A single missing figure: write `"[KPI]"` in number fields and `"[figure]"` in text. build.py lists every placeholder so the user can fill them.
- A missing block of proof: leave the section out. Do not ship placeholder quotes or placeholder logos.
  - No client names or logos: drop `logo-marquee`.
  - No testimonials or case results: drop `testimonials` and `case-slider`.
  - No salary or rate data: drop `cost-calculator` (put the savings claim in the hero or metrics instead).
  - No call recordings: drop `voice-sample`.
  - No client video: drop `video-block`. The bundled `sample-ambient-loop` is for previews only; if you use it, list it in your report as something to replace.
- Prices: if the client has no public price, use `"Custom quote"`, or drop `pricing-toggle`.
- Certifications: list only ones the client actually holds, even if that is one badge.
- Split figures (headcount per office, share per service) only when the client gave the split. Otherwise use `"[KPI]"` or describe the office without a number.
- Generic process or FAQ copy is fine when it describes how outsourcing usually works, but keep it neutral ("We agree the scope with you") and flag it in your report so the client can confirm it.

## Language

- Set `"lang"` to the page language (`en`, `vi`, `ja`, ...). All copy, including form labels (`name_label`, `next_label`, ...) and screen reader labels (`menu_label`, `close_label`), must be in that language.
- Vietnamese copy keeps its diacritics. The dash and quote rules still apply.
