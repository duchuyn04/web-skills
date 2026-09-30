# Layout blueprints

A blueprint is the layout of one real BPO homepage, section by section: order, layout form, content role, light or dark tone, columns, item count and where the picture sits. Every new page follows one blueprint. Two sites built from the library then differ the way two real sites do, in layout, while a page and its source differ only in colours, copy and the 3D visuals.

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
7. Every figure on the page comes from the brief (stats, salaries, prices); `"motion": "calm"` is only for a brief that asks for a still page.

## Where the 3D goes

A 3D visual never changes the layout. It takes the place of a picture or sits behind the copy:

- Hero forms: every hero variant with the same form has the same layout; the 3D heroes swap only the visual. `hero-split` (copy left, visual right): `hero-orbits`, `hero-monolith`, `hero-isometric`, `hero-dashboard`, `hero-deck`, `hero-shatter`, `hero-liquid`, `hero-sundial`, `hero-chat`, `hero-particles`, `hero-ribbons`, `hero-globe`. `hero-fullbleed` and `hero-video`: `hero-terrain`, `hero-magnetic`, `hero-dark-network`, `hero-wavefield`, `hero-flow` (fullbleed only). `hero-center`: `hero-terrain`, `hero-magnetic` and `hero-wavefield` set `align` to center by themselves. `hero-left-text`: `hero-prism`, `hero-magnetic`, `hero-flow`.
- Band sections take a WebGL backdrop through `"visual"`: `dots` (the dot plane that bends under the pointer), `terrain` (the rolling wireframe), `wave` (a field of dots under slow swells), `globe` (a dotted globe at the right of the band) or `flow` (particle streams sorted into lanes). It works on `cta-band` and `banner-image` (the scene replaces the photo), `statement-band` and `metrics-counter`. A band with a visual counts as a signature section. A page carries at most two WebGL scenes (the hero and one band, or two bands); build.py fails a third.
- Other signature variants that keep the form: `metrics-rings`, `metrics-bars3d`, `cta-letter`, `faq-fold`, `locations-relief`, `models-board`, `case-filter`.
- Variants marked `"reshape": true` (`industries-slats`, `services-cylinder`, `services-cube`, `team-coverflow`, `proof-book`, `about-helix`, `services-stack`, `process-pipeline`, `process-layers`, `logo-wall`, `testimonials-drift`) change the section's geometry, so a blueprint page cannot use them.

Pick a different 3D visual from the other sites (the unique hero rule still applies) and seed nothing by hand: every scene takes its shape from the brand name.

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
