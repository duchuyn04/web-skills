# Home sections, group G

Five section types for the homepage, each with two designs. The first design of each type is the default (`sections/<type>.html`); every design can also be asked for by name with `"variant"`. All of them draw from data the shop already has (products, categories, brands, sold counts, release dates), so they add no claims that need checking against the brief. Cards come from `m.card(p)` and `m.rail(...)`, so they take the look of the shop's card style.

Example with every design: `examples/variants/sections-g.shop.json`. The same page with no `variant` set (default designs only): `examples/variants/sections-g-default.shop.json`.

## new-arrivals

| Variant | Design |
|:---|:---|
| `tabs` (default) | One rail of the newest products per category, switched by category tabs (arrow keys, Home and End work) |
| `carousel` | One wide rail with three large cards in view |

```json
{"type": "new-arrivals", "variant": "tabs", "title": "Sản phẩm mới về", "categories": ["dien-thoai", "laptop"], "limit": 8}
{"type": "new-arrivals", "variant": "carousel", "title": "Laptop mới về", "category": "laptop", "limit": 9}
```

Newest means the product's `released` date, newest first; products without a date follow. `products` (a list of ids) replaces the automatic choice. `tabs` with no `categories` uses every category.

## best-sellers

| Variant | Design |
|:---|:---|
| `ranked` (default) | Top five cards under large rank numbers |
| `grid` | Up to ten cards in two rows, each with a small rank badge |

```json
{"type": "best-sellers", "variant": "ranked", "title": "Bán chạy nhất tuần này"}
{"type": "best-sellers", "variant": "grid", "category": "phu-kien", "limit": 10}
```

Order: by `sold` when products carry it (demo shops only), otherwise the order of `products` (ids) or of the catalogue. Never write a ranking the data does not show: on a real shop without sold counts, pass `products` in the order the owner states.

## price-ladder

| Variant | Design |
|:---|:---|
| `chips` (default) | Wide chips, each with the band and the number of products in it |
| `tiles` | Large tiles with the cheapest and the dearest product picture of the band, the real price span and the count |

```json
{"type": "price-ladder", "variant": "chips", "title": "Điện thoại theo tầm giá", "items": [
  {"min": 2000000, "max": 5000000, "category": "dien-thoai"},
  {"min": 20000000, "category": "dien-thoai"}]}
```

`title` of an item is optional; it is written from `min` and `max` ("2 - 5 triệu", "Trên 20 triệu"). A band with no product is left out. Each link opens `c/<category>.html?price=<min>-<max>`. The listing page ticks a price filter only when the band equals one of the category's own price ranges (for the standard steps: 0, 2, 5, 10, 15, 20, 30 and 50 million), so use those edges; other bands open the category unfiltered. `category` defaults to the first category.

## category-tiles

| Variant | Design |
|:---|:---|
| `mosaic` (default) | One large lead tile and up to four smaller ones, with a product picture, the name and the count |
| `rows` | Up to four rows, each a category line with its first three products as cards |

```json
{"type": "category-tiles", "variant": "mosaic", "categories": ["dien-thoai", "laptop", "tivi", "am-thanh", "phu-kien"]}
{"type": "category-tiles", "variant": "rows", "title": "Từng nhóm sản phẩm", "categories": ["tivi", "dong-ho"]}
```

`mosaic` lays itself out for 1 to 5 categories (the first is the lead). All categories are used when `categories` is left out. The type is named `category-tiles` because `category-showcase` trips the banned-word check.

## brand-focus

| Variant | Design |
|:---|:---|
| `featured` (default) | The brand's initial, name and product count, a link to all its products and a rail of its products |
| `logos` | A wall of brand name tiles with product counts, each linking to a search by brand |

```json
{"type": "brand-focus", "variant": "featured", "brand": "lumen", "limit": 10}
{"type": "brand-focus", "variant": "logos", "brands": ["lumen", "orbit"]}
```

`featured` needs `brand` (an id from `brands`); an unknown id draws nothing. `logos` lists every brand when `brands` is left out.

## Files

Templates `templates/sections/<type>.html` and `<type>/<variant>.html` (the named default only includes the default file); css `templates/assets/css/v/section-<type>.css` (default design) and `section-<type>-<variant>.css` (the other design); js `templates/assets/js/v/section-new-arrivals.js` (tabs).

## How it was verified

- `scripts/variants.py` passes (first-line descriptions, no hex colours).
- Both examples build, pass `lint_output.py` and `qa.py --quick` (the buying flow included).
- Screenshots of every design at 1440 and 390 wide, in the default retail preset and in `gaming-dark`.
- In the browser: tab click and arrow keys switch panels and the rail arrows refresh; a price-ladder chip opens the category with the matching price filter ticked.

## Limits worth knowing

- The `dense` card's spec chips and promo line use fixed grey text in `store.css`, so they read faintly under `gaming-dark`. That is outside these sections; the fix belongs in `store.css` or the card variant.
- A free price band (min and max not matching a category price range) cannot preselect on the listing page, because `store.js` initPlp reads only the `price` checkboxes. Reading `min` and `max` into `[data-price-min]` and `[data-price-max]` would make any band work.
