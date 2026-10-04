# Style: boutique

For accessory boutiques with a small curated range (earbuds, headphones, watches and bands, chargers, power banks, keyboards, mice, phone cases). Calm and warm: cream ground, ink text and prices, a terracotta accent for buttons, Lora for headings, Be Vietnam Pro for text, small radius, no promo clutter. Set `"style": "boutique"` in shop.json.

## Parts

| Part | Variant | What it does |
|:---|:---|:---|
| header | `centered` | One quiet announcement line, shop name centred in Lora, store and hotline links on the left, search icon (opens a search panel), account and cart on the right, category links in a row below. Phones: burger, store icon, name, search, cart; the category row scrolls sideways |
| hero | `editorial` | Split layout: product art on a tinted panel (`bg`) beside a text column with label, title, text, price and a text link; 1-3 slides with prev and next buttons |
| card | `gallery` | No border; tinted square picture that shows the next colour on hover; brand, name in Lora, ink price, colour dots; discount or "Mới" tag |
| pdp | `gallery` | Every colour picture in a two-column grid (the first one wide when the count is odd), sticky info on the right with option chips, stock line, Thêm vào giỏ, Mua ngay, then accordions Mô tả, Thông số, Giao hàng và đổi trả; reviews and questions side by side below; similar and recently viewed products. Choosing a colour marks its picture. Phones: pictures scroll sideways |
| plp | `chips` | From the premium style: filters as chips above the grid |
| footer | `minimal` | From the premium style |

Preset: `boutique-warm` (accent `#9a4a2e`, prices in ink `#2a2522`). A brand colour in `theme.accent` replaces the terracotta.

## Home sections made for this style

`collections`:
```json
{"type": "collections", "title": "Bộ sưu tập", "items": [
  {"title": "Tông kem cho ngày nhẹ nhàng", "text": "Tai nghe, sạc và pin cùng một màu kem.", "products": ["aura-pebble", "tessel-cube", "tessel-stone"], "bg": "#efe6d8"}
]}
```
2-4 collections; each takes 3-6 product ids (four show on wide screens, all scroll on phones). Every second collection puts its text on the right.

`editorial`:
```json
{"type": "editorial", "title": "Ốp da lên màu theo năm tháng", "text": ["Đoạn 1", "Đoạn 2"], "product": "bloom-case-x9", "bg": "#efe3d4", "cta": "Xem ốp da Bloom", "align": "right"}
```
The picture is the product's image, so `product` is required; `href` overrides the link.

`newsletter`:
```json
{"type": "newsletter", "title": "Nhận tin hàng mới", "text": "Mỗi tháng một email về hàng mới."}
```
The address is kept in this browser (localStorage key `newsletter`) and confirmed with a toast. On a demo shop the form says so.

Order used by the example: hero, collections, grid (Hàng mới về), editorial, categories, rail, brands, newsletter, benefits. No flash sale, no sold counts.

## Files

`templates/layout/headers/centered.html`, `templates/sections/hero/editorial.html`, `templates/partials/cards/gallery.html`, `templates/pdp/gallery.html`, `templates/sections/collections.html`, `editorial.html`, `newsletter.html`; css in `templates/assets/css/v/` (`header-centered`, `hero-editorial`, `card-gallery`, `pdp-gallery`, `section-collections`, `section-editorial`, `section-newsletter`) and `templates/assets/css/styles/boutique.css`; js in `templates/assets/js/v/` (`header-centered.js` search panel, `pdp-gallery.js` colour marking, `section-newsletter.js`). Example: `examples/styles/boutique.shop.json` (Sương Studio, fictional brands Aura, Tessel, Kiri, Bloom).

## Verified

Build OK, `lint_output.py` passed, `qa.py` passed (49 pages at 1440 and 390 px, full buying flow, admin confirm, price edit) with no storefront warnings; home, listing, product and cart checked by screenshot at 1440 and 390.
