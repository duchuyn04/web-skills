# Layout blueprints

A blueprint is the layout of one real BPO homepage, section by section: order, layout form, content role, light or dark tone, columns, item count and where the picture sits. Every new page follows one blueprint. Two sites built from the library then differ the way two real sites do, in layout, while a page and its source differ only in colours, copy and photos (and, on a page whose brief asks for 3D, the visuals).

The blueprints live in `templates/blueprints/<key>.json`. They come from 113 homepages measured in the browser (`data/layout-analysis` in the job repository: DOM profiles, annotated screenshots, clusters), and each was checked by hand against its screenshot. They record structure only; nothing of the source site's copy, figures, names or images is used.

## Using one

```
python SKILL/scripts/variety.py --blueprints <archetype> --sites sites     layouts that fit, unused first
python SKILL/scripts/variety.py --blueprint <key>                          each section with the variants that fit it
```

1. Pick an unused blueprint whose sections the brief can fill. Read its `summary` and the role of every section. A layout full of case carousels does not suit a client with no cases; one with a long services area suits a client with many service lines.
2. Set `"blueprint": "<key>"` in page.json, next to `archetype` and `preset`.
3. Write one section per blueprint section, in the same order. Take the variant from the `--blueprint` list for that section.
4. Leave out a section only when the brief has no content for it: sections marked optional, sections that need client proof (logos, quotes, cases, awards, team, news, careers, locations; never invent them), and a second section of a form the page already has (a second metrics band when the brief has only four figures). build.py fails a page that skips any other section, reorders them, uses a variant whose form does not match, fills fewer than 60% of the non-proof sections, has fewer than 5 content sections, or has no services section.
5. Keep the item counts close to the blueprint's `count` (build.py warns when a grid is much larger or smaller than the real one).
6. Tones come from the blueprint, even for variants that are usually dark; do not set `tone` on sections.
7. Every figure on the page comes from the brief (stats, salaries, prices). Pages are calm by default; `"motion": "expressive"` is only for a brief that asks for a 3D or animation-led page.

## Preferred layouts

Four blueprints carry `"preferred": true`: `iris` (IRIS Software Group), `intelligent-outsourcing` (Intelligent Outsourcing), `innovature-bpo` (Innovature BPO) and `bestarion` (Bestarion). A client named these four sites as the standard for a professional page (2026-09-30). `variety.py --blueprints` lists them first with a `*`, unused ones before used ones, and build.py names them first when it suggests a free layout. Take the first unused `*` blueprint whose sections the brief can fill; go further down the list only when none fits (Iris needs client logos, reviews or articles to reach five sections; Innovature suits staffing with roles by industry; Intelligent Outsourcing suits a long staffing page with a founder and FAQ; Bestarion suits software plus back-office services).

What the four have in common, and what the library rebuilds from them:

| Pattern | Source | Variant |
|:---|:---|:---|
| Dark hero with a portrait on a colour panel, small UI cards and a solution finder bar over its lower edge | Iris | `hero-finder` |
| Solution browser: vertical tabs (by service, size, industry) beside a raised panel of cards | Iris | `solutions-vtabs` |
| Chevron-cut photo with a call button beside a two-column enquiry form | Iris | `contact-photo` |
| Row of four light figure tiles; copy beside a two-by-two bento of figure tiles | Intelligent Outsourcing, Innovature | `metrics-tiles` (`layout` row or split) |
| Questions in two columns of tinted boxes | Intelligent Outsourcing | `faq-grid` |
| Sideways track of role cards by industry with a progress bar | Innovature | `roles-carousel` |
| Hero stage with slide tabs along its lower edge | Innovature | `hero-tabs` |
| Split hero in the brand colour, link-row service lists, advantage panel beside the form | Bestarion | `hero-gradient`, `service-links`, `contact-split` |

Shared traits: people photography in almost every section, one accent colour on white or a pale tint, figures and certifications near the top, star-rated reviews, pill buttons, and quiet motion (reveals, counters, one carousel). None of them uses 3D or particles.

## The hero composition ("compose")

A blueprint's hero slot may list `"compose"`: the variants that rebuild the source site's hero composition, not only its form. `hero-overlap` (Foundever: heading over a wide photo, white card over its lower edge), `hero-mosaic` (Kyanon: tilted, tinted photo mosaic behind a centered heading), `hero-portrait` (MicroSourcing, Horatio: dark card with service chips beside a round portrait), `hero-promo` (Firstsource: centered headline with an accent block, photo cards below), `hero-tabs` (Genpact, TDCX: photo stage with thumbnail tabs instead of a slider), `hero-news` (Concentrix: copy over a dark photo, a column of news cards), `hero-panels` (ELEKS: photo panel beside tall sector panels), `hero-finder` (IRIS: portrait on a colour panel with small UI cards and a finder bar over the hero's lower edge), plus the existing `hero-collage`, `hero-dashboard`, `hero-qualifier` and `hero-gradient` where they match. build.py fails a hero outside the list, except a business hero (`hero-voice`, `hero-ledger`, `hero-chat`, `hero-dashboard`) and, on a page whose brief asked for 3D, an expressive hero. `variety.py --blueprint <key>` marks the listed variants with `=`. When adding a blueprint, add `"compose"` whenever the source hero is more than text beside or over one photo, and build a new variant when none matches.

## Where the 3D goes (expressive pages only)

Everything in this section applies only to a page with `"motion": "expressive"`, which build.py accepts only when the brief asks for a 3D or animation-led page. On every other page the variants marked `^` in `variety.py` and the `"visual"` field are build errors. A 3D visual never changes the layout. It takes the place of a picture or sits behind the copy:

- Hero forms: every hero variant with the same form has the same layout; the 3D heroes swap only the visual. `hero-split` (copy left, visual right): `hero-orbits`, `hero-monolith`, `hero-isometric`, `hero-dashboard`, `hero-deck`, `hero-shatter`, `hero-liquid`, `hero-sundial`, `hero-chat`, `hero-particles`, `hero-ribbons`, `hero-globe`, `hero-voice`, `hero-ledger`. `hero-fullbleed` and `hero-video`: `hero-terrain`, `hero-magnetic`, `hero-dark-network`, `hero-wavefield`, `hero-flow` (fullbleed only). `hero-center`: `hero-terrain`, `hero-magnetic` and `hero-wavefield` set `align` to center by themselves. `hero-left-text`: `hero-prism`, `hero-magnetic`, `hero-flow`.
- Band sections take a WebGL backdrop through `"visual"`: `dots` (the dot plane that bends under the pointer), `terrain` (the rolling wireframe), `wave` (a field of dots under slow swells), `globe` (a dotted globe at the right of the band) or `flow` (particle streams sorted into lanes). It works on `cta-band` and `banner-image` (the scene replaces the photo), `statement-band` and `metrics-counter`. A page carries at most two WebGL scenes (the hero and one band, or two bands); build.py fails a third.
- Other expressive variants that keep the form: `metrics-bars3d`, `cta-letter`, `faq-fold`, `locations-relief`. (`metrics-rings`, `models-board` and `case-filter` are calm variants and fit any page.)
- Variants marked `"reshape": true` (`industries-slats`, `services-cylinder`, `services-cube`, `team-coverflow`, `proof-book`, `about-helix`, `services-stack`, `process-pipeline`, `process-layers`, `logo-wall`, `testimonials-drift`) change the section's geometry, so a blueprint page cannot use them.

Seed nothing by hand: every scene takes its shape from the brand name. build.py warns (it does not fail) when another site already opens with the same hero.

## Format

```json
{
  "id": "concentrix",
  "source": {"name": "...", "url": "...", "category": "...", "collected": "2026-09-26"},
  "fits": ["enterprise-cx"],
  "summary": "one sentence on the page's shape",
  "header": "mega",
  "sections": [
    {"form": "hero-fullbleed", "role": "hero", "tone": "dark", "media": "full", "note": "copy left over a full-width visual"},
    {"form": "metrics", "role": "metrics", "tone": "dark", "cols": 6, "count": 6, "note": "..."},
    {"form": "cards-image", "role": "industries", "tone": "light", "cols": 4, "count": 8, "optional": true, "note": "..."}
  ]
}
```

Forms: hero-split, hero-fullbleed, hero-video, hero-center, hero-left-text, metrics, cards-image, carousel-cards, feature-split, cards-text, cards-icon, list-rows, text-block, statement, logo-strip, cta-band, video-block, image-band, form, faq-accordion, testimonial-block, tabs, icon-strip, media-list, link-list, locations-map. Each variant lists the forms it builds in its schema (`"forms"`).

Roles: hero, services, industries, about, intro, metrics, cases, testimonial, clients, awards, process, team, locations, news, careers, faq, cta, pricing, compare, tools. A variant fits a role when its group suits it, when the form fixes the content (metrics, logo strip, FAQ, form, video, badges, CTA band), or when the variant is `"open"` (generic title, text, picture and link fields, such as `image-cards`, `feature-rows`, `services-bento`).

## Adding blueprints

`data/layout-analysis/tools/blueprints.py` drafts blueprints from the measured profiles; `data/layout-analysis/out/blueprints-draft/_brief.md` is the review brief. Sites whose capture showed only the hero, a pop-up or the wrong site are left out (parked drafts in `out/blueprints-low-confidence/`). `data/layout-analysis/tools/tallshot.py` recaptures sites that scroll inside a fixed container; pages that slide one screen at a time (FPT Software, Co-well Asia, Mat Bao BPO) still cannot be captured. After adding blueprints run `python scripts/variety.py --coverage`: every section of every blueprint must have at least one variant.
