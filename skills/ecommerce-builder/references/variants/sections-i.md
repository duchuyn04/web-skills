# Second designs for the existing home sections (worker I)

Every type below keeps the data keys of its default design. A shop switches design with `"variant"` on the section, for example `{"type": "rail", "variant": "featured", "category": "dien-thoai"}`. The default design is used when `variant` is left out. Files: `templates/sections/<type>/<variant>.html`, `assets/css/v/section-<type>-<variant>.css`, `assets/js/v/section-brands-marquee.js`. Examples: `examples/variants/sections-i.shop.json` and `sections-i-2.shop.json` (together they use every variant listed here).

| Type | Variant | What it is, when to pick it |
|:---|:---|:---|
| `categories` | `icons` | Round icon wells in one row with name and count; scrolls sideways on phones. Many categories, light page. |
| `categories` | `cards` | Large cards with the first product's picture and a link line. 3-8 categories that deserve room. |
| `rail` | `featured` | First product large on the left, next four in a 2x2 grid. Shows 5 products; no brand chips. Push one hero product. |
| `rail` | `compact` | Row cards (thumbnail left, text right), two columns on phones, four on desktop; `limit` default 8. Accessories and cheaper products. |
| `banners` | `overlap` | Staggered tiles of different heights. Livelier offer band. |
| `banners` | `strip` | Each item one thin full-width strip. A single offer or short notices between rails. |
| `brands` | `marquee` | Slow auto-scrolling band; pauses on hover, keyboard focus and with the Tạm dừng button; static and scrollable under reduced motion. |
| `brands` | `grid-logo` | Wider grid with the product count per brand. Brands are a reason to buy. |
| `flash-sale` | `compact` | One coloured row: title, h:m:s countdown, four small deal items (first four). Deal should not take over the page. |
| `flash-sale` | `split` | Solid panel with title, countdown and link on the left, discounted products in a rail on the right. Deal is the main reason to visit. |
| `benefits` | `icons-row` | Centred icons with short text, no boxes, thin rules between. Calm promise bar. |
| `benefits` | `cards` | Boxed cards with an icon well. Promises that need weight. |
| `grid` | `featured-grid` | First card double size; `step` default 9. Lead with one product, keep a long list. |
| `grid` | `list` | Wide rows (picture left, details right), two per line on desktop; `step` default 6. Products whose spec chips and promo line should be read. |
| `stores-cta` | `map` | Band listing up to four stores (name, city, hours) and a link to the locator. No map is embedded. Optional `title`, `text`. |
| `stores-cta` | `split` | Sentence on the left, large button on a tinted panel on the right. Closing call to visit a store. |
| `needs` | `chips` | Pill links with an icon, no pictures. Many needs, image-heavy page. |
| `rooms` | `strip` | One strip of small picture chips; scrolls sideways on phones. Four or more rooms in little height. |
| `services` | `cards` | Boxed cards with an icon well. 3-6 services; promises still come from the brief. |
| `collections` | `rows` | Header (title, line, count) above a sideways rail of the collection's products. Collections of 4-6 products. |
| `spotlight-tiles` | `wide` | One full-width tile per row, text one side and product the other, alternating. `tone: "dark"` inverts the page colours, so it stays readable in every preset. |
| `lineup` | `cards` | Boxed cards with picture, name, price and the listed spec rows as labelled lines. Spec rows must name `specs[].rows[0]` labels or facet keys, otherwise the line reads "Không có". |
| `bundle` | `compact` | Whole combo in one row: thumbnails with plus signs, total or combo price, add-all button (same hooks as the default). |
| `editorial` | `centered` | Centred heading and text above one large picture. |
| `newsletter` | `inline` | Short row: heading left, email field and button right (same form hooks, same script). |

## Hooks and behaviour kept from the defaults

- `flash-sale` variants keep `[data-flash]` with `data-ends` and `[data-t=h|m|s]`, driven by `store.js`; `split` also keeps the rail from `m.rail`.
- `grid` variants keep `[data-more-grid]` with `data-step` and the `[data-more]` button inside the same section.
- `rail` `featured`, `compact` and `collections` `rows` render cards with `m.card(p)`, so the style's card is used.
- `bundle`, `newsletter` and `lineup` variants reuse the section scripts (`data-bundle`, `data-bundle-sku`, `data-bundle-add`, `data-newsletter`, `data-lineup-compare`).
- `needs`, `rooms` and `stores-cta` keep their link targets (filtered category listings, store locator).

## How it was verified

- `python scripts/variants.py` passes (first-line comments, tokens-only CSS).
- Both examples build; lint passes; `qa.py --quick` passes (sample pages and the buying flow).
- The same two examples with `"theme": {"preset": "gaming-dark"}` build and pass quick QA; screenshots at 1440 and 390 px were checked for every variant in the light and the dark preset. Fixes found that way: the lead card of `featured` and `featured-grid` grew a blank area, countdown digits and the dark spotlight tile were unreadable on dark surfaces (they now use `--c-text` on `--c-bg` inverted), the compact flash row put the countdown below the items on phones, compact cards showed a discount badge over a 64 px thumbnail, and `needs` chips wrapped their labels.
- Limits: `rail` `featured` shows five products and ignores brand chips; `banners` `strip` is meant for one to three items.
