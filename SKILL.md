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
2. Never invent facts: no made-up client names, quotes, agent names, CSAT, headcount, prices, salary rates, certifications or promises (such as "same-day onboarding"). A missing single figure becomes `"[KPI]"` (number fields) or `"[figure]"` (text). A missing whole block of proof (logos, testimonials, case studies, call recordings, salary rates) means you leave that section out; its slot is "recommended", so the build only warns. If a section's minimum item count is higher than the facts you have, drop the section or pick another variant; never pad a list to reach the minimum. List everything missing in your report.
3. Copy follows `references/content-rules.md`. The build fails on emoji, arrows, em or en dashes, curly quotes and banned AI words, so fix the wording, do not work around the checker.
4. Keep the archetype's section order. Do not add keys that the schema does not list.

## Step 1: Collect the brief

Get these from the user or their files. Ask one short message for anything missing that matters (items marked *); do not stall on the rest.

- Company name*, what they sell*, who buys it* (industry, country)
- Delivery locations (cities), headcount, languages
- Proof: real KPIs, client names or logos, certifications, testimonials
- Contact: email, phone, WhatsApp or Zalo link, form endpoint if they have one
- Brand colors (hex) and page language (default English)
- Photos of their own office or team, if any (put them next to page.json)

## Step 2: Choose archetype and preset

Read `references/page-anatomy.md`. Pick the archetype from the client's headline pitch, the thing the brief says first or loudest:

| Headline pitch | Archetype | Default preset |
|:---|:---|:---|
| Many services, enterprise buyers, several hubs or countries | `enterprise-cx` | `enterprise-navy` |
| Cost savings, dedicated offshore staff, "hire a team in Vietnam or the Philippines" | `offshore-staffing` | `human-warm` |
| Data labeling, RLHF, trust and safety, content moderation | `ai-data-ops` | `dark-ai` |
| Call quality as the product: SDR, telesales, receptionists, and the client has call recordings | `cx-voice-sales` | `clean-minimal` |

Tie-breakers:

- A client with two service lines (for example voice support plus accounting) and a savings pitch is `offshore-staffing`; both lines go into the services section.
- Choose `cx-voice-sales` only when the client can supply call recordings or sells outbound sales meetings. Voice support alone, without recordings, fits `offshore-staffing` or `enterprise-cx`.
- Preset: use the archetype's default. Switch only when the client names brand colors or a style, or clearly matches another preset's "Pick it when" line in `references/style-presets.md`. Brand colors alone go in `theme` and do not change the preset.

## Step 3: Start from the example

Create a project folder, for example `sites/<company-slug>/`, and copy the matching example:

```
SKILL/examples/<archetype>.page.json  to  sites/<company-slug>/page.json
```

Then edit values only:

- Replace every string and number with the client's content. Delete `_note`.
- Keep the same section order. Delete "no" and "recommended" sections you have no real content for (see page-anatomy.md), and swap a section for another variant allowed in the same slot when it fits the content better.
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

Needs Python Playwright and Edge or Chrome. If `python` cannot import playwright, try `py -3.11` or `python3`. The script checks sideways overflow, clipped text, broken images and JS errors at 1440, 768 and 390 px and must print `QA PASSED`. Then open `dist/qa/page-1440.png` and a few files in `dist/qa/sections-390/` and look at them. Typical fixes: shorter titles, fewer items, a better photo.

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
- `references/style-presets.md`: presets, brand color overrides, tones
- `references/content-rules.md`: copy rules and how to handle missing facts
- `references/assets.md`: image library, icons, flags, cities
- `references/animation-map.md`: which section carries which of the 24 researched animations (generated)
- `references/custom-section-spec.md`: fallback for blocks outside the library

## Maintaining the library

After changing a template or schema, rebuild all four examples, run lint and QA on each, then run `python SKILL/scripts/make_catalog.py` to regenerate the catalog, anatomy and animation map (add `--previews <dist> ...` to refresh preview images).
