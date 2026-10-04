# Product page and listing variants

Two new product pages (`pdp`) and two new listings (`plp`). They join the existing `retail`, `showcase`, `gallery` (pdp) and `sidebar`, `chips` (plp). Choose with `"layout": {"pdp": "...", "plp": "..."}` in shop.json. All four keep every hook in `data/hooks.json`, so cart, compare, wishlist, reviews, filters and the buying flow work unchanged, and use colour tokens only, so they work in every preset including `gaming-dark`.

## pdp `tabbed`

Gallery and buy box side by side, a row of other products from the same brand ("Cùng hãng"), then one sticky tab bar (Mô tả, Thông số, Đánh giá with the count, Hỏi đáp) over four sections. The tab of the section being read is marked; once the buy box scrolls out of view, the bar shows a small strip with the picture, the chosen version, the price and Mua ngay. On phones the strip is fixed at the bottom.
Pick it for products with long specs and many reviews (laptops, TVs). Data used: `p.highlights`, `p.description`, `p.in_box`, `p.faq`, `p.specs` (all groups shown), `p.reviews`, `p.qa`, `p.promos`, `p.warranty`, `p.addons`, the other products of the same brand.
Files: `templates/pdp/tabbed.html`, `css/v/pdp-tabbed.css`, `js/v/pdp-tabbed.js`.
The variant is named `tabbed` and not `tabs` because `layout.pdp` becomes a class on `<body>` (`pdp-<name>`) and `.pdp-tabs` already styles the retail tab bar.

## pdp `compact`

One narrow column for phones: the gallery is a swipe strip with dots (choosing a colour scrolls to its picture, swiping updates the dots and the prev and next buttons), then name, rating, buy box, highlights and collapsible sections for Khuyến mãi, Mô tả, Thông số, Câu hỏi thường gặp, Đánh giá, Hỏi đáp and store stock. The buy bar is fixed to the bottom at every width. Links to `#reviews`, `#specs`, `#qa` open the section they point to. No breadcrumbs, only a back link to the category.
Pick it for shops whose visitors mostly buy from a phone.
Files: `templates/pdp/compact.html`, `css/v/pdp-compact.css`, `js/v/pdp-compact.js`.

## plp `rows`

Each product as a wide row: the style's own card is laid out as picture on the left, name, spec chips and price in the middle, compare and wishlist on the right. A switch changes between Danh sách and Lưới (remembered in the browser). Filters are collapsible groups in a side column, with product counts per brand; on phones they are the bottom sheet from `store.css`.
Pick it for categories where buyers compare specs (laptops, TVs, appliances). It works with any card variant because it only arranges `.pc-link` children by grid.
Files: `templates/plp/rows.html`, `css/v/plp-rows.css`, `js/v/plp-rows.js`.

## plp `tiles`

A category banner with the first intro paragraph and quick brand chips, a column of links to the other categories (a row of pills on phones), large two-column tiles with 4:3 pictures, and the filters in a drawer that opens from a button at every screen width. The remaining intro paragraphs go under the grid.
Pick it for small catalogues where the picture sells the product.
Files: `templates/plp/tiles.html`, `css/v/plp-tiles.css`.

## Examples and checks

- `examples/variants/pdp-plp.shop.json`: `tabbed` and `rows`.
- `examples/variants/pdp-plp-2.shop.json`: `compact` and `tiles`.
- `python scripts/variants.py` passes; `python scripts/variants_qa.py --parts pdp,plp` and `--dark` build, lint and run the quick QA with the whole buying flow for every pdp and plp variant.

## Pitfalls found

- A variant name becomes a body class. Check `grep -n "\.pdp-<name>\|\.plp-<name>" templates/assets/css` before naming one.
- Grid columns written as `1fr` let wide content (a row of pills) push the page sideways on phones: write `minmax(0,1fr)`.
- Every `[data-clamp]` element needs its `[data-clamp-toggle]` inside it (`store.js` initClamp), which is why the tiles intro keeps both.
