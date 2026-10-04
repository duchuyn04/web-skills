# Patterns behind the templates

Counts come from the project research: 7 Vietnamese electronics stores and 2 international ones read in full (`docs/research/ecommerce-electronics-dashboards.md`, section 5) and 434 Mobbin screens (`docs/research/ecommerce-mobbin-screens.md`). "Template" names the file that carries the pattern.

## Storefront

| Pattern | Seen on | Template |
|:---|:---|:---|
| Dark top bar with delivery, installment, returns | 4/7 VN | `layout/base.html` (`announcement`) |
| Header: logo, wide search with suggestions, hotline, account, cart count | 7/7 VN | `layout/base.html`, `store.js` initSuggest |
| Category menu beside the carousel, flyout with brands, price ranges, a top facet, top products | 3/7 VN | `sections/hero.html`, `macros.catmenu` |
| Carousel with tab labels under it, side banners | 7/7 VN have a carousel | `sections/hero.html` |
| Flash sale with h:m:s countdown in the section head, discount badge, "đã bán x/y" bar | 4/7 VN, 6/6 Mobbin iOS countdowns | `sections/flash-sale.html` |
| Rows per category with brand chips and "Xem tất cả" | 7/7 VN | `sections/rail.html` |
| Product card: price, struck old price, discount (8/8), installment label (6/8), spec chips, rating (4/8), compare (4/8), gift line (3/8) | 8 cards read | `macros.card` |
| Listing: count by the title, quick brand chips (4/7), filters for brand, price ranges plus min-max, specs; sort by price (7/7); "Xem thêm" with the number left (6/7), no page numbers | 7/7 VN | `pages/category.html`, `store.js` initPlp |
| Mobile filters in a bottom sheet with a sticky "Xem N kết quả" button | 5/7 Mobbin drawers | `pages/category.html` |
| Product page: two columns, gallery with colour thumbnails, variant price on each option (4/9), numbered promotion box (7/7 VN), installment (7/9), promises row (7/7 VN), store availability (6/9), add-ons (4/9), grouped specs, FAQ (6/9), rating histogram (4/9), Q&A (3/9), similar products | 9 sites | `pages/product.html` |
| Out-of-stock variants marked on the option, "Báo khi có hàng" | 4/6 Mobbin | `store.js` initPdp |
| Sticky buy bar on mobile product pages | 7/9 | `.buybar` in `pages/product.html` |
| Product JSON-LD with offers in the HTML | 9/9 have Product, 5/9 Offer; Google requires offers for merchant listings | `pages/product.html` head |
| Cart: two columns, sticky summary, quantity stepper, voucher, free-shipping progress, save for later | 8/8 Mobbin carts | `pages/cart.html` |
| Checkout on one page in numbered blocks, contact first, delivery or store pickup as cards with fee and time, payment list with COD and bank transfer | 3/3 and 7/7 Mobbin | `pages/checkout.html` |
| Order confirmation with code, items, totals, payment instructions | 5/5 Mobbin | `pages/order.html` |
| Tracking with a step bar, estimated date, item list | 7/7 Mobbin iOS | `pages/track.html` |
| Account: side menu, recent orders, default address, order tabs, wishlist | 7/7 Mobbin | `account/` |

Addresses use the 34 provinces in force since 1 July 2025 and a ward field, with no district level (`data/provinces.json`).

## Admin

| Pattern | Seen on | Template |
|:---|:---|:---|
| Fixed left menu with settings at the bottom | 8/8 Mobbin | `admin/_layout.html` |
| 6 KPI tiles (net revenue, orders, AOV, sessions, conversion, returning customers) with change against the comparison period, daily averages and a sparkline; clicking a tile draws that metric on the main chart | 8/8, Shopify, WooCommerce | `admin/index.html`, `admin.js` kpiTiles |
| Date range picker: 14 presets (today to last year, including period to date), custom from-to in dd/mm/yyyy, comparison with the previous period, the same period last year or none; period-to-date presets compare the same days of the previous week, month or quarter; kept in the URL and per browser | WooCommerce, Shopify, Sapo, GA4 (`docs/research/ecommerce-overview-analytics.md`) | `admin.js` periodControl |
| Main chart grouped by hour, day, week or month depending on the range length, comparison as a dashed line, table view | WooCommerce interval rules | `admin.js` pageIndex |
| Funnel: website sessions, add to cart, checkout, orders; new versus returning customers; orders heatmap by weekday and hour; cancel, return and unreconciled COD rates; top customers, vouchers, low stock | Shopify, GA4, KiotViet, Sapo, Haravan | `admin/index.html` |
| To-do list on the home page (orders to confirm, to ship, out of stock) | 5/8 | `admin/index.html` |
| Order list: status tabs with counts, search, filters, payment and delivery status as separate badges, bulk actions, export | 6/8, 4/8 | `admin/orders.html` |
| Order detail: items and totals left, customer and address right, status actions, timeline with internal notes | 4/6 | `admin/order.html` |
| IMEI or serial per phone, laptop and tablet before shipping | Sapo | `admin/order.html` |
| Product list with thumbnail, status badge, stock with variant count, bulk show or hide | 5/5 | `admin/products.html` |
| Product form: content left, status and classification right, price and compare-at price per variant, SEO preview, sticky save bar | 6/12, 8/12 | `admin/product.html` |
| Inventory table separate from products, inline adjustment with reason, low-stock tab, adjustment log | 5/6 | `admin/inventory.html` |
| Customers with total spent, order count, segments; detail with summary figures and notes | 6/6, 4/5 | `admin/customers.html`, `admin/customer.html` |
| Voucher creation: percent, fixed or free shipping, minimum order, cap, usage limit, end date, generate code | 7/7 | `admin/promotions.html` |
| Reports with the metric formulas written on the page (AOV differs between Shopify and WooCommerce) | research 5.2 | `admin/reports.html` |
| Notifications from the bell: new orders, out of stock, reviews and questions waiting | 4/4 | `admin.js` shell |
| Order quick view: a side panel opened from the list with status steps, the next action, items, totals and customer, so the list stays in place | DoorDash, Etsy (2/6 use a drawer) | `admin.js` pageOrders |
| Status changes in place with a toast that offers undo; destructive and bulk changes ask in a confirm dialog that names the orders and amount | Mobbin admin flows; native confirm boxes removed | `admin.js` ui.confirm, ui.toast, runAction |
| Sortable columns, keyboard use (j, k, Enter, x, /, Esc in the order list; [ and ] between orders; ? lists keys) | Shopify, Linear-style admin lists | `admin.js` pageOrders, pageOrder, shell |
| Phones: tables become labelled cards, filters fold behind one button | Mobbin mobile admin screens | `admin.js` cardify, `admin.css` |
| Delivery slip header when printing an order: shop, order code, recipient, cash to collect | Sapo, Haravan print forms | `admin/order.html`, `admin.css` print |
| Adding a product writes the shop.json entry, since the site has no server; names and specs are read-only in the admin | honest limits of a static build | `admin.js` newProductDialog |
