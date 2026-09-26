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

- Hero title: one concrete promise, 5-10 words, with 2-4 accent words in `*asterisks*`. Good: `"Support teams that *protect your CSAT* while you scale"`. Bad: `"Transforming the future of customer experience"`.
- Lead: who you serve, what you do for them, one proof. Two sentences at most.
- Button labels: verb first, 2-4 words: "Get a staffing plan", "See client results", "Book a call".
- Eyebrows: 1-4 plain words: "Services", "Delivery centers".
- Card text: one sentence that says what the team does, in which tools or for which customers.
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
