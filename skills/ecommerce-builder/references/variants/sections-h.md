# Home sections, group H

Six home section types, each with a default design and one extra variant. The default is `sections/<type>.html` and is used when a section has no `variant`; the extra design is `sections/<type>/<variant>.html` and is chosen with `"variant"`. The example `examples/variants/sections-h.shop.json` uses every design. Rules for all of them are in `references/variant-contract.md`.

Common to all six: the text a section shows comes only from the section's own fields or from shop data, so the build checks it against the brief like any other home text (numbers, model codes and promise words must be in the brief unless `sample_content` is on). Templates add no claims of their own. In JSON write `sec["items"]`-style keys as plain `items`.

## accessories-for

Accessories for one product.

| Design | Pick it for |
|:---|:---|
| default `strip` | a main product panel on the left and a rail of accessories on the right; 3 to 6 accessories |
| `grid` | a slim header with the main product, then every accessory as a product card; 6 or more accessories |

```json
{"type": "accessories-for", "title": "Phụ kiện cho Lumen X9 Pro", "product": "lumen-x9-pro",
 "products": ["sac-nhanh-67w", "op-lung-x9", "tai-nghe-vexa-buds-2"]}
{"type": "accessories-for", "variant": "grid", "product": "kaze-air-14", "products": ["chuot-vexa-g5", "ban-phim-vexa-k7"]}
```

`product` is optional; without it the section shows only the accessories. `title` defaults to "Phụ kiện cho <product name>". Cards use the shop's card design.

## bundle-offers

Several combos, each adding every item to the cart with one button (`assets/js/v/section-bundle-offers.js`).

| Design | Pick it for |
|:---|:---|
| default `cards` | one card per combo: thumbnails joined by plus icons, retail sum, combo price, difference |
| `compare` | combos as columns with a tick list of what is included; a basic, standard and full combo |

```json
{"type": "bundle-offers", "title": "Combo mua cùng", "items": [
  {"title": "Điện thoại và sạc nhanh", "products": ["lumen-x9", "sac-nhanh-67w"], "price": 17400000},
  {"title": "Laptop và chuột", "products": ["kaze-forge-16", "chuot-vexa-g5"]}]}
```

`price` is optional. The cart always charges each item's normal price, so a card with a combo price says "Giỏ hàng tính giá lẻ từng sản phẩm"; staff confirm the combo price on the order. Each item uses its first in-stock variant. Use 2 to 4 combos and 2 to 4 products in each.

## warranty-care

Warranty and service promises.

| Design | Pick it for |
|:---|:---|
| default `columns` | 2 to 4 icon columns separated by thin rules |
| `banner` | a statement block in the button colour with the promises as a row; warranty is the main selling point |

```json
{"type": "warranty-care", "title": "Bảo hành và dịch vụ", "items": [
  {"icon": "shield-check", "title": "Bảo hành chính hãng", "text": "Theo thời hạn ghi trên từng sản phẩm"}]}
{"type": "warranty-care", "variant": "banner", "title": "Máy lỗi do hãng, đổi máy mới", "text": "Một câu dưới tiêu đề.", "items": [{"icon": "refresh", "title": "Đổi trả 30 ngày"}]}
```

Icon names come from `build.py --list`. Every title and text is a promise the brief must contain.

## stats

Store figures. Write the number first, then the unit: `"12 cửa hàng"`.

| Design | Pick it for |
|:---|:---|
| default `counters` | big numbers in cards; a plain integer or an integer with dot thousands ("1.200 đơn") counts up once when scrolled into view (`assets/js/v/section-stats.js`). With reduced motion or no JavaScript the final text is shown at once |
| `inline` | one quiet line of figures, no animation |

```json
{"type": "stats", "title": "Cửa hàng trong con số", "items": [{"value": "12 cửa hàng", "label": "tại 4 tỉnh, thành"}, {"value": "8 năm"}]}
{"type": "stats", "variant": "inline", "items": [{"value": "12 cửa hàng"}, {"value": "8 năm", "label": "kinh doanh"}]}
```

Use only figures the brief gives; the build rejects numbers that are not in it.

## gallery

A lookbook of pictures.

| Design | Pick it for |
|:---|:---|
| default `masonry` | tiles in columns with alternating shapes, no holes for any count; 5 to 9 items |
| `strip` | one horizontal snapping strip with captions; 4 to 8 items |

```json
{"type": "gallery", "title": "Bộ sưu tập hình ảnh", "items": [
  {"product": "lumen-x9-pro", "caption": "Lumen X9 Pro"}, {"device": "headphones", "device_color": "#2b2f36", "caption": "Tai nghe"}]}
```

An item names a `product` (its picture, linking to its page) or a `device` kind (drawn art, no link). `caption` is optional; the strip falls back to the product name.

## contact-band

Contact details taken from the shop: hotline, email, hours, address and, when the shop has stores, a link to the store locator. No data needed except an optional `title`.

| Design | Pick it for |
|:---|:---|
| default `bar` | a thin band of contact details |
| `card` | a large card with the hotline as the call button, near the end of the page; optional `text` |

```json
{"type": "contact-band"}
{"type": "contact-band", "variant": "card", "title": "Cần tư vấn trước khi mua", "text": "Gọi hoặc nhắn cho cửa hàng trong giờ làm việc."}
```

A placeholder address such as `[Địa chỉ trụ sở]` is shown as written, like in the footer, so it gets replaced before launch.

## Files

- Templates: `templates/sections/{accessories-for,bundle-offers,warranty-care,stats,gallery,contact-band}.html` and `templates/sections/<type>/{grid,compare,banner,inline,strip,card}.html`
- CSS: `templates/assets/css/v/section-<type>.css` and `section-<type>-<variant>.css` (colour tokens only)
- JS: `templates/assets/js/v/section-bundle-offers.js`, `section-stats.js`
- Example: `examples/variants/sections-h.shop.json`

## Verified

- `python scripts/variants.py` passes; `python scripts/variants_qa.py --coverage` passes.
- The example builds, `lint_output.py` passes and `qa.py --quick` passes (pages at 1440 and 390 px, buying flow).
- Each section checked by screenshot at 1440 and 390 px in the light preset and in `gaming-dark`.
- Stats counters: with animation the figures end on the original text; with `prefers-reduced-motion` the text never changes.
- Fixes made after screenshots: gallery images were cut off (now absolutely positioned inside the tile) and the mosaic left holes (now columns).
