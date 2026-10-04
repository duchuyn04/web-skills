# Header, hero and card variants (worker D)

Two new variants for each of three parts. They sit on top of the five styles; none of them is the default of a style yet, so use them through `"layout"` in shop.json:

```
"layout": {"header": "split", "hero": "split", "card": "poster"}
"layout": {"header": "rail",  "hero": "ticker", "card": "row"}
```

Examples that use them: `examples/variants/header-hero-card.shop.json` and `examples/variants/header-hero-card-2.shop.json`.

## Header

| Variant | What it is | Pick it for |
|:---|:---|:---|
| `split` | Dark thin top row (announcements, stores, track order, hotline). White main row with logo, wide search, account and cart. Second row with a Danh mục mega-menu button, up to six categories as links, a Khuyến mãi link and the hotline. Phones: the second row folds into the usual category drawer. | a general electronics shop that wants a calm white header with every shortcut visible |
| `rail` | One slim bar: Danh mục button, logo, wide search, account, cart. The button opens a wide slide-in panel with every category as an accordion (brands, price ranges, three top products), then Khuyến mãi, stores, tracking and the hotline. | a shop with many categories that wants a quiet page |

Hooks kept (data/hooks.json, header): `data-header`, `data-open` (the burger on `split`, the Danh mục button on `rail`, which opens `#railpanel`), `data-search`, `data-search-input`, `data-suggest`, `data-account-link`, `data-account-label`, `data-cart-count`. `split` also keeps `data-mega-toggle` and `#mega` so `store.js` opens the mega menu. The rail panel is a `.drawer[data-drawer]` placed after the header (not inside it, so its stacking is not capped by the sticky header).

## Hero

| Variant | Data | Pick it for |
|:---|:---|:---|
| `split` | `slides[0]` is the message column (label, title, text, price when it has a `product`, button). The tiles on the right are `side` first, then the remaining `slides`, four at most. Tile colours follow `bg` (default the surface tone) and the build sets the text colour. | a home page that leads with four products next to one offer |
| `ticker` | The slides as a calm full-width banner (arrows appear when there are two or more slides). Under it a slim strip scrolls product names with prices. Optional `products` (ids) fills the strip, default the first 12 products. The strip pauses on hover and focus, has a pause button (`[data-ht-pause]`) and stands still with an overflow scroll under reduced motion. | shops with many products and one main message |

Both use `[data-carousel]` hooks where they carry slides (ticker); `split` has no carousel.

## Card

| Variant | What it is | Pick it for |
|:---|:---|:---|
| `poster` | Square soft tile with the picture, the name and price laid over its bottom on a fade into the tile colour (no hex, the fade ends in `--c-surface-2` so text keeps contrast in every preset), discount and badge top left, compare and wishlist as round buttons top right. | lookbook-like grids with few words |
| `row` | Horizontal compact card: 96px picture, name, one spec line (`card_specs` joined with a dot), price, old price and discount. Grids become two or three columns of rows; rails stack two rows per column. | dense lists and phone-first rails |

Cards are macro modules (`card(p, flash, lazy)`). The build pre-renders each product in the shop's card style into `cards.js`, so search results, the wishlist and "recently viewed" use the same card.

## Verification

- `scripts/variants.py` passes for these files.
- `scripts/variants_qa.py --parts header,hero,card` builds the retail example once per variant, then lint and quick QA; also with `--dark` (round robin under `gaming-dark`).
- Screenshots checked at 1440 and 390: home, category, search results, open mega menu, open rail panel.

## Notes for the maintainer

- A hero chosen with `"variant"` on one section does not load that variant's css or js; css and js are included for the layout part only (`layout.hero`). Use `layout.hero` for these two heroes.
- Hero `split` takes at most 3 side banners because of the build limit; with 3 side banners plus the second slide it shows four tiles.
- `hero.products` is not validated by the build; the template ignores unknown ids.
