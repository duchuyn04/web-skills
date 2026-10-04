# shop.json reference

Every key the build accepts. `*` marks required keys. Unknown keys are build errors. Prices are whole VND numbers (`8990000`, not `"8.990.000 đ"`). Text is plain: no HTML, no emoji, no arrows, no em or en dashes.

## Top level

| Key | Type | Notes |
|:---|:---|:---|
| `style` | string | `retail` (default), `premium`, `gaming`, `appliance` or `boutique`; sets every layout part, the type and the default preset (see "Styles and layout") |
| `layout` | object | optional overrides of the style's parts: `header`, `hero`, `card`, `pdp`, `plp`, `footer` |
| `sample_content` | bool | `true` only when the user asked for an invented sample shop with no catalogue of its own: turns off the check that figures, model codes and promises come from the brief |
| `demo` | bool | `true` for a sample shop: sample notice, `noindex`, generated admin orders and customers, reviews and sold counts allowed |
| `lang` | string | `"vi"` (default) |
| `brief`* | string | The owner's brief as given. Reviews on a real shop must appear in it word for word |
| `shop`* | object | See "shop" |
| `theme` | object | `preset`, `accent`, `header_bg`, `price` (6-digit hex) |
| `announcement` | list of strings | 1-4 short lines in the dark top bar (delivery, installment, returns) |
| `categories`* | list | See "categories" |
| `brands`* | list | `{"id": "lumen", "name": "Lumen"}`; product `brand` must be one of these ids |
| `products`* | list | At least 4. See "products" |
| `home`* | list | Homepage sections in order. See "home sections" |
| `promotions` | list | Voucher codes. See "promotions" |
| `shipping`* | list | `{"id", "name", "fee", "free_over"?, "eta", "cities"?}`; `cities` limits a method (express) to listed provinces |
| `payments`* | list | `{"id", "name", "icon"?, "note"?, "bank"?}`; ids used by the admin: `cod`, `bank`, `card`, `wallet`, `installment`. `bank` = `{"name", "account", "holder"}` |
| `benefits`* | list | 3-4 `{"icon", "title", "text"}` promises shown in the footer and on product pages |
| `stores` | list | `{"id", "name", "city", "address", "hours" ("8:00 - 21:30"), "phone"?, "map"?}`; `city` must be one of the 34 provinces in `data/provinces.json` for the store filter to match checkout |
| `policies`* | list | `{"id", "title", "body"}`; `body` items are strings (paragraphs) or `{"heading", "items"?: [..], "text"?}` |
| `staff` | list | Admin accounts shown at login: `{"name", "role"}`; roles `Chủ cửa hàng`, `Bán hàng`, `Kho` |

## shop

`name`*, `tagline`* (one line, the category and the offer: "Điện thoại, laptop chính hãng, trả góp 0%"), `hotline`*, `email`*, `address`, `hours`, `legal` (company name and tax code line for the footer), `socials` (`[{"type": "facebook"|"youtube", "url"}]`), `slug` (defaults to the name).

## Styles and layout

| Style | header | hero | card | pdp | plp | footer | preset |
|:---|:---|:---|:---|:---|:---|:---|:---|
| `retail` | `bar` | `sidebar` | `dense` | `retail` | `sidebar` | `full` | `red-retail` |
| `premium` | `minimal` | `spotlight` | `clean` | `showcase` | `chips` | `minimal` | `clean-premium` |
| `gaming` | `tiered` | `bento` | `spec` | `retail` | `sidebar` | `full` | `gaming-dark` |
| `appliance` | `tiered` | `wide` | `dense` | `retail` | `sidebar` | `full` | `appliance-fresh` |
| `boutique` | `centered` | `editorial` | `gallery` | `gallery` | `chips` | `minimal` | `boutique-warm` |

What each variant is:
- header: `bar` (solid colour bar, category button and mega menu, wide search, hotline), `minimal` (white bar, category text links, search behind an icon), `tiered` (search row plus a horizontal category bar with icons), `centered` (centered logo, category row under it).
- hero: `sidebar` (category list, carousel with tab labels, side banners), `spotlight` (one product per screen, centered title, large picture), `bento` (grid of one large and several small tiles), `wide` (full-width carousel with a row of small promo tiles), `editorial` (picture and text side by side).
- card: `dense` (discount, badge, spec chips, promo line, rating, compare), `clean` (large picture, name, price from, colour dots), `spec` (dark card with spec lines), `gallery` (borderless, second colour on hover).
- pdp: `retail` (promo box, installment, store stock, add-ons), `showcase` (large gallery, feature blocks, full spec table), `gallery` (image grid, sticky info, accordions).
- plp: `sidebar` (filter column) or `chips` (filter chips above the grid).
- footer: `full` (promise row, five link columns) or `minimal` (one row of links and the legal line).

A hero section can also set its own `"variant"`. Parts not built yet are rejected by the build, which names the ones available.

## theme presets

| Preset | Pick it when |
|:---|:---|
| `red-retail` | Default. Phone and electronics chains with a red logo; red header |
| `sun-yellow` | Yellow logo, mass-market phone and appliance stores; yellow header, dark button text |
| `blue-tech` | Blue logo, laptops, PC parts, office electronics; white header |
| `dark-gear` | Gaming gear and PC builds; near-black header, red accent |
| `clean-premium` | Authorised resellers of premium brands with few products; white, larger radius |
| `gaming-dark` | Dark surfaces for the gaming style; red accent, Chakra Petch headings |
| `appliance-fresh` | Fresh blue for the appliance style; Nunito, rounder corners |
| `boutique-warm` | Cream background, ink text and prices, terracotta accent, Lora headings |

Put the logo colour in `theme.accent`. The build darkens it for white button text when needed and keeps prices readable.

## categories

| Key | Notes |
|:---|:---|
| `id`* | lowercase ascii and hyphens (`dien-thoai`); becomes `c/<id>.html` |
| `name`* | as shown in menus |
| `icon` | icon name (`build.py --list`) for menus: smartphone, laptop, tablet, watch, headphones, tv, plug, monitor, camera, gamepad, chair, refrigerator, washing-machine, air-vent |
| `device` | product drawing for products without photos (see list below) |
| `facets` | filters on the category page: `[{"key": "ram", "label": "RAM"}]`. Each product gives `facets.ram`. Price and brand filters are added automatically |
| `price_ranges` | optional `[[0, 5000000], [5000000, 10000000], [10000000, null]]`; generated from prices if missing |
| `intro` | optional list of paragraphs shown under the product grid (buying advice, written from facts) |
| `intro_title` | optional heading for `intro` |

Device kinds: `phone, tablet, laptop, monitor, tv, watch, headphones, earbuds, speaker, camera, gamepad, keyboard, mouse, chair, fridge, washer, aircon, charger, powerbank`.

## products

| Key | Notes |
|:---|:---|
| `id`* | lowercase ascii and hyphens; becomes `p/<id>.html` |
| `name`*, `brand`*, `category`* | brand and category are ids |
| `price` | selling price, when no option carries prices |
| `old_price` | list price before discount; must be higher than `price` |
| `options` | up to 2 groups. Priced group: `{"name": "Phiên bản", "values": [{"name": "8GB/128GB", "price": 7490000, "old_price": 7990000}]}`. Colour group: `{"name": "Màu sắc", "values": [{"name": "Đen", "hex": "#25272c", "image"?: "photos/den.jpg"}]}`. Prices go on one group only. Versions of one model (16GB/512GB, 32GB/1TB) are one product with a priced option, never separate products. Leave out options with a single value, except a single colour |
| `stock` | number for every variant, or a map from variant label (`"8GB/128GB / Đen"`) to number. On a demo shop it is generated when missing |
| `device` | overrides the category drawing (a case in the phone category: `phone`) |
| `facets` | values for the category facets; a string or a list (`"storage": ["128 GB", "256 GB"]`) |
| `card_specs` | 2-3 short chips on the card (`["6,7 inch", "12 GB", "256 GB"]`) |
| `highlights` | 2-4 short facts in the "Thông tin sản phẩm" box |
| `description` | paragraphs for "Đặc điểm nổi bật" |
| `specs` | `[{"group": "Màn hình", "rows": [["Kích thước", "6,7 inch"], ...]}]`; the first two groups show, the rest open with "Xem cấu hình chi tiết"; the compare page lines groups up by name, so use the same group and row names across a category |
| `promos` | numbered promotion lines on the product page; the first also shows on the card |
| `badges` | any of `new`, `hot`, `installment`, `exclusive`, `preorder` (first one shows on the card) |
| `installment` | `true` adds the "Trả góp 0%" button and the monthly estimate |
| `warranty` | text, for example `"12 tháng tại trung tâm bảo hành của hãng"` |
| `in_box` | list of what is in the box |
| `addons` | product ids offered as "Thường được mua kèm" |
| `faq` | `[{"q", "a"}]` shown as "Câu hỏi thường gặp" |
| `qa` | customer questions with the shop's answers `[{"name", "q", "a"}]` |
| `reviews` | `[{"name", "stars" (1-5), "text", "date"?, "variant"?, "verified"?, "reply"?}]`; real shops: text must appear in the brief |
| `rating` | `{"avg", "count"}`; demo shops only unless computed from `reviews` |
| `sold` | demo shops only |
| `released` | `"2026-09"`, used by the "Mới về" sort |
| `keywords` | extra search words (model codes, other spellings) |
| `sku` | prefix for variant SKUs (defaults to the id) |

## home sections

| `type` | Keys | Notes |
|:---|:---|:---|
| `hero` | `slides` (2-5), `side` (0-3), `interval` | Each banner: `title`*, `text`, `label`, `tab` (short label under the carousel), `cta`, `product` (id; shows its drawing and "Giá chỉ từ") or `device` + `device_color`, `bg` (a brand word: `accent`, `accent-dark`, `accent-soft`, `dark`, `light`, `surface`; or a hex colour. Text turns white or dark to reach 4.5:1; prefer the brand words so banners follow the logo colour), `href` |
| `categories` | `title` | Tiles for every category, with the first product's picture |
| `flash-sale` | `title`, `ends` (`"23:59"`), `items` (4+) | `{"product", "sale_price", "limit"?, "sold"? (demo only)}`; the sale price applies in cart and checkout |
| `rail` | `category` or `products` (ids), `title`, `limit`, `tabs` (false hides brand chips) | Horizontal row with brand filter chips |
| `banners` | `items` (2-4), `title` | Same banner keys as hero |
| `brands` | `title` | Brand names as tiles |
| `grid` | `category` or `products`, `title`, `limit`, `step` | Product grid with "Xem thêm" |
| `benefits` | none | The `benefits` list as a row |
| `stores-cta` | `title`, `text` | "N cửa hàng tại ..." band with a link to the store locator |
| `spotlight-tiles` | `items` (2-4), `title` | Large two-column tiles, one product each (premium) |
| `lineup` | `products` (2-4), `rows`, `title` | Models side by side with the listed spec rows (premium) |
| `needs` | `items` (3-6: `title`, `icon`, `category`, `query`), `title` | Shop by need, each tile opens a filtered listing (gaming) |
| `bundle` | `products` (2-5), `title`, `text`, `price` | Setup or PC combo with one add-all button (gaming) |
| `rooms` | `items` (3-6: `title`, `category`, `query`, `product` or `device`), `title` | Shop by room (appliance) |
| `services` | `items` (2-6: `icon`, `title`, `text`), `title` | Service promises band; texts must come from the brief (appliance) |
| `collections` | `items` (2-4: `title`, `text`, `products`), `title` | Curated groups beside their products (boutique) |
| `editorial` | `title`, `text` (paragraphs), `product` or `device`, `bg`, `align` | Picture and text block (boutique) |
| `newsletter` | `title`, `text` | Email signup kept in the browser on a demo shop (boutique) |

Exact data shapes for the style sections are in `references/styles/<style>.md`. Every section can be used in every style.

## promotions

`{"code", "type": "fixed"|"percent"|"shipping", "value", "max"? (percent cap), "min"? (order minimum), "label" (shown to customers), "ends"? ("31/12/2026"), "limit"?, "used"? (demo)}`. Codes are entered in the cart or checkout; the admin can create more and pause them.
