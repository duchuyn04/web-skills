# Style: premium

For authorised resellers of premium brands and shops that sell a few flagship models. The page leads with large product art on light grey bands, uses few words and large type, shows prices in ink, and keeps promotions out of the cards. Reference: Apple and Samsung online stores (`docs/research/ecommerce-electronics-dashboards.md` section 2, screenshots `docs/research/ecommerce/apple-*` (in the job repository, not shipped with this skill), `samsung-*`).

Set `"style": "premium"`. Default preset `clean-premium`; the logo colour goes in `theme.accent` as usual.

## Variants

| Part | Variant | What it is |
|:---|:---|:---|
| header | `minimal` | White bar: logo, the first six categories as text links, a search icon that opens a search panel (with category shortcuts), account and cart icons. The first `announcement` line shows as one quiet line above it. |
| hero | `spotlight` | One product per screen: centered title, one line of text, "Giá từ" of the product, a button (`cta`) and a "Tìm hiểu thêm" link, large art underneath, dots below. Slides take light or dark `bg`; the build picks the text colour. |
| card | `clean` | Product art on a soft tile, colour dots, "Mới" (badge `new`) only, name, the first two `card_specs` as one line, "Từ" price when versions differ. Discount badges, spec chips, promo lines and sold counts are hidden, also on cards that store.js draws. |
| pdp | `showcase` | Sticky gallery on a soft panel, calm buy column (large option tiles, Mua ngay, Thêm vào giỏ, promises, promotions folded in a details box, store stock), then `highlights` and `description` as alternating feature blocks, the full spec sheet in two columns, FAQ, reviews as cards, similar products. |
| plp | `chips` | No sidebar. A sticky row of filter chips (Thương hiệu, Mức giá, each facet, Khác) opening small panels on wide screens, the same filters as a bottom sheet on phones, sort select, active filter chips, a three column grid. |
| footer | `minimal` | Small grey link columns (Mua sắm, Hỗ trợ, Chính sách, Liên hệ), payment names in one line, legal line and demo note. |

Other styles can borrow these with `"layout"`, for example `"layout": {"plp": "chips"}`.

## Sections

`spotlight-tiles`: two to four large tiles in two columns (a third tile in a set of three spans the row).

```json
{"type": "spotlight-tiles", "title": "optional", "items": [
  {"title": "Aurel Slate Pro 12", "text": "Mỏng 5,1 mm, màn hình OLED hai lớp.", "product": "aurel-slate-pro-12", "bg": "#f5f5f7", "cta": "Xem máy"},
  {"title": "Aurel Pods Pro 3", "text": "Chống ồn chủ động.", "product": "aurel-pods-pro-3", "bg": "#1d1d1f", "tone": "dark"}]}
```

Each item needs `product` (its picture and "Giá từ" are shown). `bg` is the tile colour; set `"tone": "dark"` when `bg` is dark so the text turns white. `href` overrides the link to the product page.

`lineup`: two to four models side by side, with the spec rows that tell them apart.

```json
{"type": "lineup", "title": "Chọn điện thoại phù hợp", "products": ["a", "b", "c"], "rows": ["Kích thước", "Chip xử lý", "Camera sau", "Thời lượng pin"]}
```

`rows` are spec row names exactly as written in `products[].specs`, or facet keys. A missing value shows "Không có". "So sánh chi tiết" puts the first three models on the compare page.

## Files

Templates: `layout/headers/minimal.html`, `sections/hero/spotlight.html`, `partials/cards/clean.html`, `pdp/showcase.html`, `plp/chips.html`, `layout/footers/minimal.html`, `sections/spotlight-tiles.html`, `sections/lineup.html`. Styles: `assets/css/v/header-minimal.css`, `hero-spotlight.css`, `card-clean.css`, `pdp-showcase.css`, `plp-chips.css`, `footer-minimal.css`, `section-spotlight-tiles.css`, `section-lineup.css`, `assets/css/styles/premium.css`. Scripts: `assets/js/v/header-minimal.js` (search panel), `hero-spotlight.js` (keyboard focus follows the shown slide), `plp-chips.js` (chip panels), `section-lineup.js` (lineup to compare page). Example: `examples/styles/premium.shop.json` (Vân Đài Store, fictional brands Aurel and Mira, 13 products).

## Verified

Example built with `build.py` (51 pages), `lint_output.py` passed, `qa.py` passed at 1440 and 390 px including the buying flow and admin. Home, listing (chip panel open, phone filter sheet), product page and cart were checked on screenshots at both widths.
