# Home sections: reviews, compare-picks, video, faq, deal-of-day

Five section types for the home page, each with a default design and one or two variants. Put them in `home` like any section; choose a variant with `"variant"`. Examples that use all of them: `examples/variants/sections-e.shop.json`, `sections-e-2.shop.json`, `sections-e-3.shop.json`.

Every text a shop writes in these sections (questions, answers, video titles, notes) is checked against the brief: figures, model codes and promises must appear in the brief unless `"sample_content": true`. Reviews are the exception in the other direction: the `reviews` section has no text of its own, it only shows reviews that already exist on products.

## reviews

Shows product reviews already in shop.json. Nothing renders when no product has reviews. Duplicate review texts are shown once.

| Key | Meaning |
|:---|:---|
| `title` | heading, default "Khách hàng đánh giá" |
| `products` | optional list of product ids to take reviews from (default: all products) |
| `limit` | `cards` only: how many reviews, default 6 |

Variants:
- default `cards`: grid of review cards (stars, text, reviewer, product link), best-rated first.
- `quotes`: three large pull quotes (only reviews of 4 stars or more) separated by thin rules.
- `score`: the average and a five-row histogram computed from the reviews, plus the first three reviews.

```json
{"type": "reviews", "title": "Khách hàng đánh giá", "products": ["lumen-x9-pro", "kaze-air-14"], "limit": 6}
{"type": "reviews", "variant": "score"}
```

## compare-picks

| Key | Meaning |
|:---|:---|
| `title`, `text` | heading and an optional line under it |
| `products` | 2-3 product ids (`duel` uses the first two) |
| `rows` | spec row names to compare, for example `["Chip xử lý", "RAM"]`; the value is taken from the product's `specs` rows with that name, then from `facets`; a missing value reads "Không ghi" |

Variants: default `table` (picture, name, price, one row per spec, a link under each product); `duel` (two products face to face, spec names in a centred column).

```json
{"type": "compare-picks", "title": "Chọn máy nào", "products": ["lumen-x9-pro", "lumen-x9"], "rows": ["RAM", "Camera sau"]}
{"type": "compare-picks", "variant": "duel", "products": ["lumen-x9-pro", "orbit-nova-12"], "rows": ["RAM"]}
```

## video

| Key | Meaning |
|:---|:---|
| `title` | section heading |
| `items` | list of `{ "title", "text"?, "product"?, "youtube"? }`; `product` supplies the poster picture, `youtube` is the video id only (not the address) |

The YouTube player (`youtube-nocookie.com`) is created by a script only after a click on the play button, so the page makes no third-party request before. An item without `youtube` shows the poster and text and no play button.

Variants: default `player` (the first item as one large card with a link to the product); `grid` (up to three thumbnails in a row).

```json
{"type": "video", "title": "Video sản phẩm", "items": [{"title": "Mở hộp Lumen X9 Pro", "text": "Xem camera và pin.", "product": "lumen-x9-pro", "youtube": "VIDEO_ID"}]}
```

## faq

| Key | Meaning |
|:---|:---|
| `title` | heading, default "Câu hỏi thường gặp" |
| `items` | list of `{ "q", "a" }` |
| `open_first` | default design only: open the first answer |

Variants: default `accordion` (details and summary, works without script); `two-col` (questions on the left, one answer at a time on the right; needs the script, and without it every answer stays visible; arrow keys move between questions).

```json
{"type": "faq", "variant": "two-col", "items": [{"q": "Giao hàng mất bao lâu?", "a": "Giao tiêu chuẩn 2-4 ngày."}]}
```

## deal-of-day

Uses the countdown markup that the flash sale uses (`[data-flash]`, `[data-t=h]`, `[data-t=m]`, `[data-t=s]`), driven by `store.js`. Use it only for a real time-limited offer.

| Key | Meaning |
|:---|:---|
| `title` | label on the tag (default design) or the heading (`list`) |
| `product` | product id (default design) |
| `text` | optional line; default: the product's first card specs |
| `ends` | end time `"HH:MM"`, default `23:59` |
| `items` | `list` only: up to three `{ "product", "ends"? }` |

The price shown is the product's own price and old price. `sale_price` (on the section or on a list item) is shown when it is lower than the product price, but it changes the display only: the cart and checkout still charge the product's price, so leave it out until the build maps deal prices into the cart (see the report of this worker).

Variants: default `single` (one large product with a tag, timer and price); `list` (rows, each with its own timer).

```json
{"type": "deal-of-day", "title": "Ưu đãi trong ngày", "product": "kaze-forge-16", "ends": "23:59"}
{"type": "deal-of-day", "variant": "list", "items": [{"product": "kaze-forge-16", "ends": "21:00"}, {"product": "vexa-watch-5"}]}
```

## Verified

Built from the three examples and an extra dark build (preset `gaming-dark`); lint and `qa.py --quick` pass on light builds; each variant was screenshotted at 1440 and 390 px; the video poster creates an iframe only after the click; the two-column FAQ shows one answer at a time. The CSS uses colour tokens only.
