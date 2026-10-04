# Style: appliance

For home appliance and TV chains that sell to families: tivi, tủ lạnh, máy giặt, máy lạnh, loa. The look follows Điện Máy Xanh (screenshots in `docs/research/ecommerce/dmx-*`): fresh blue header, a white category bar with large icons, a wide banner carousel, round category wells, shopping by room and service promises (delivery, installation, warranty at home) near the top.

Set `"style": "appliance"`. Defaults:

| Part | Variant | Notes |
|:---|:---|:---|
| preset | `appliance-fresh` | blue `#0b74de`, page `#eef3f8`, Nunito, radius 12 and 18 px |
| header | `tiered` | built by the gaming style; `styles/appliance.css` turns its category bar white with 26 px icons above the labels |
| hero | `wide` | full-width carousel, labelled dots, up to 3 promo tiles from `side` (4 once the build allows it) |
| card | `dense` | restyled: rounder, soft image well, spec chips as blue pills |
| pdp, plp, footer | `retail`, `sidebar`, `full` | restyled through tokens and `appliance.css` |

## Sections

**hero, variant `wide`** (default for this style; any style can set `"variant": "wide"` on its hero)

```json
{"type": "hero",
 "slides": [{"title": "...", "text": "...", "label": "...", "tab": "...", "cta": "...", "product": "<id>", "bg": "#0b5cad"}],
 "side":   [{"title": "...", "text": "...", "product": "<id>", "bg": "#fff4cc"}]}
```

Slides take dark or light backgrounds; the build picks white or ink text (`ink`). The button is drawn in the text colour on the background colour. When a slide has a product, "Giá chỉ từ" shows its lowest price and the old price. Side tiles are small cards under the carousel; on phones they scroll sideways.

**rooms**: shop by room

```json
{"type": "rooms", "title": "Mua sắm theo phòng",
 "items": [{"title": "Phòng ngủ", "text": "Máy lạnh 1 HP", "category": "may-lanh", "query": {"power": "1 HP"}, "product": "<id>", "bg": "#f1eafa"}]}
```

3 to 6 tiles. Each links to `c/<category>.html`, pre-filtered by `query` (keys are facet keys, `brand` or `price` such as `"5000000-10000000"`), or to `href`. The picture is the product's image, or the first product of the category when there is no `product`. Use light `bg` colours: the text is ink.

**services**: service promises

```json
{"type": "services", "title": "Dịch vụ tại <shop>",
 "items": [{"icon": "truck", "title": "Giao và lắp đặt miễn phí", "text": "Nội thành, trong ngày với đơn đặt trước 16:00"}]}
```

2 to 6 items. Every promise and figure must come from the brief; the build rejects claims such as "miễn phí", "lắp đặt", "tại nhà" or times that the brief does not state (unless `sample_content` is true). Icons that fit: `truck`, `home`, `settings`, `refresh`, `shield-check`, `credit-card`, `headset`, `clock`.

## Files

- `templates/sections/hero/wide.html`, `templates/assets/css/v/hero-wide.css`
- `templates/sections/rooms.html`, `templates/assets/css/v/section-rooms.css`
- `templates/sections/services.html`, `templates/assets/css/v/section-services.css`
- `templates/assets/css/styles/appliance.css`
- `examples/styles/appliance.shop.json`: Điện máy Gia An, 13 products in 5 categories (TVs by size, fridges by capacity and colour, washers by load, air conditioners by power, speakers), demo and sample content

## How it was checked

Built `examples/styles/appliance.shop.json` (50 pages), `lint_output.py` passed, `qa.py` passed (every page at 1440 and 390 px, buying flow, admin confirm, price edit). Home, a category, a product page and the cart were looked at in screenshots at both widths.
