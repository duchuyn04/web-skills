# Style: gaming

For shops that sell gaming laptops, PC parts and gear (monitors, keyboards, mice, headsets, chairs, gamepads). Dark storefront, red accent, headings in Chakra Petch, specs shown before anything else on the card, compact corners. Reference: GearVN (docs/research/ecommerce/gear-*), with a dark theme.

Set `"style": "gaming"` in shop.json. Defaults (from data/styles.json): preset `gaming-dark`, header `tiered`, hero `bento`, card `spec`, pdp `retail`, plp `sidebar`, footer `full`. Override single parts with `"layout"`.

## Variants built for this style

| Part | Variant | What it is |
|:---|:---|:---|
| header | `tiered` | Row 1: logo, wide light search box, hotline, account, cart. Row 2: a bar with every category and its icon plus Khuyến mãi; scrolls sideways on phones. Announcements become one thin line (the first one only on phones). Colours come from the header tokens, so the appliance style reuses it in blue. |
| hero | `bento` | Up to five tiles from `slides` then `side`: the first is large (left, two rows), the rest fill the right. Each tile: `label`, `title`, `text`, price "Từ" when it has a `product`, `cta`, art. `bg` sets the tile colour; the build picks white or dark text. |
| card | `spec` | Brand line, name, up to four spec lines from `card_specs` (first line with a chip icon), old price with discount, large price in the heading font, first badge, flash progress, rating, compare and wishlist. |

## Sections

`needs` (shop by need):

```json
{"type": "needs", "title": "Mua theo nhu cầu", "items": [
  {"title": "Chơi game eSports", "text": "Laptop RTX 5060 trở lên", "icon": "gamepad", "category": "laptop-gaming", "query": {"gpu": "RTX 5060"}, "product": "raxon-strike-15"}
]}
```

3-6 items. Each tile links to `c/<category>.html?<query>`; the listing opens with that filter ticked. Query keys: `brand` (brand id), `price` (`"lo-hi"` exactly as a price range of that category, for example `"10000000-15000000"`), or a facet key of the category with a value exactly as written in the products' facets. `product` adds that product's picture; `href` replaces the link. The build does not check `category` yet, so use an existing category id.

`bundle` (combo, PC build):

```json
{"type": "bundle", "title": "Combo góc máy chơi game", "text": "...", "products": ["vyrex-27q", "kestrel-k75", "kestrel-viper"], "price": 16990000}
```

2-5 product ids. Shows each item (first variant in stock) joined by plus icons, the sum, and when `price` is given the combo price and the saving with the line "Giá combo áp dụng khi nhân viên xác nhận đơn; giỏ hàng hiện giá lẻ từng sản phẩm", because the cart charges normal prices. The button adds every item to the cart (assets/js/v/section-bundle.js). On a real shop `price` must come from the brief.

## Files

templates/layout/headers/tiered.html, templates/sections/hero/bento.html, templates/partials/cards/spec.html, templates/sections/needs.html, templates/sections/bundle.html, templates/assets/css/v/{header-tiered,hero-bento,card-spec,section-needs,section-bundle}.css, templates/assets/css/styles/gaming.css (dark overrides of colours that store.css writes as fixed values: badges, promo box, installment line, compare highlight, inputs, modals, toasts, footer, product image stages), templates/assets/js/v/section-bundle.js, examples/styles/gaming.shop.json (Nova Gear, 15 products, sample data).

## How it was verified

`build.py examples/styles/gaming.shop.json` OK (54 pages), `lint_output.py` passed, `qa.py` passed (54 pages at 1440 and 390, buying flow, admin confirm, price edit). Screenshots of home, laptop listing, product page, search, compare, login, tracking, stores, 404, filled cart, checkout and order confirmation at 1440 and 390 were reviewed: all pages dark, text readable, borders visible.
