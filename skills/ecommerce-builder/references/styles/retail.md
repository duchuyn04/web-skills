# Style: retail

For mass-market phone and electronics chains with a wide catalogue: điện thoại, laptop, tablet, đồng hồ, tai nghe, phụ kiện. The look follows Thegioididong and CellphoneS: a solid red header with search in the middle, a category menu beside the banner carousel, dense product cards with discount badges, spec chips and a promotion line, a flash sale with a countdown and rows of products by category. It is the default style and the base the other styles restyle.

Set `"style": "retail"` (or leave `style` out). Defaults:

| Part | Variant | Notes |
|:---|:---|:---|
| preset | `red-retail` | red `#d70018` header, accent and prices, page `#f2f3f5`, sale band `#ffe9a8`, radius 10 and 14 px, Be Vietnam Pro |
| header | `bar` | solid accent bar: logo, category button, search, hotline, cart |
| hero | `sidebar` | category menu left, banner carousel, up to 3 side tiles from `side` |
| card | `dense` | picture, discount and badge, name, spec chips, price and old price, promotion line, flash-sale progress, compare and wishlist |
| pdp, plp, footer | `retail`, `sidebar`, `full` | no style sheet of its own: the other styles restyle these through `templates/assets/css/styles/<style>.css` |

## Sections

Retail uses the base home sections, whose keys are in `references/shop-schema.md` ("home sections"): `hero`, `categories`, `flash-sale`, `rail`, `banners`, `brands`, `grid`, `benefits` and `stores-cta`. A typical order, as in the example: hero, categories, flash-sale, rail, banners, two more rails, brands, grid, stores-cta.

- `flash-sale` needs 4 or more items, each with a `sale_price` that applies in cart and checkout; `sold` counts are allowed on a demo shop only.
- `rail` shows brand filter chips when its category has more than one brand; `"tabs": false` hides them.
- `stores-cta` counts the shops in `stores` and their cities; it renders nothing when `stores` is empty.
- Promotion lines and installment offers come from the products' `promos` and `installment`; every offer must be in the brief unless `sample_content` is true.

## Files

- `templates/assets/css/store.css`: the base look that retail uses unchanged
- `templates/sections/`: the base sections listed above
- `examples/demo-electronics.shop.json`: Hải Đăng Digital, 23 products in 7 categories, demo and sample content

## How it was checked

Built `examples/demo-electronics.shop.json` (62 pages), `lint_output.py` passed and `qa.py --quick` passed (index and admin at 1440 and 390 px).
