# Going live: what the static build does not do

The build produces HTML, CSS and JavaScript with no server. Everything that changes after the build lives in the visitor's browser (localStorage): cart, wishlist, account, orders placed, and every admin change. That makes a complete demo. It is not a store that can take real orders.

Facts below come from `docs/research/ecommerce-electronics-dashboards.md` (in the job repository, not shipped with this skill) section 5.3, which cites the vendor documentation.

## What a real launch needs

| Need | Why the static build is not enough |
|:---|:---|
| Payment | No payment gateway is called. Card and wallet options are placeholders until a gateway (or a hosted cart) is connected |
| Shared orders | Orders are stored in the buyer's browser only. The shop owner's admin sees them only on the same browser |
| Live prices and stock | Prices and stock are fixed at build time (admin edits change only that browser). Google Merchant Center expects the price on the page, in structured data and at checkout to match the feed, so every price change means a rebuild or a price API at run time |
| Staff login | The admin password is a demo value checked in the browser. A real admin needs server-side accounts |
| Order emails, SMS, Zalo | Not sent |
| Shipping labels, COD reconciliation | Not connected to carriers |

## Options read from vendor docs

- Shopify Storefront API: products, collections, search and cart (read and write) are available to the browser with a public token. The storefront templates can keep their layout and read data from it.
- Snipcart: a script plus buttons with `data-item-id`, `data-item-name`, `data-item-price`; before confirming an order Snipcart fetches the product page and checks the price in the static HTML, so it suits a static build that is rebuilt on price changes.
- Medusa: an open-source Node.js server with its own admin; the storefront calls its Store API with a publishable key. It needs a server to run.
- Vietnamese platforms (Sapo, Haravan) track COD collection, returned shipments and redelivery as separate order states, which a custom backend should copy.

## What carries over

The page layouts, product data model (options, variants, SKUs, facets, specs), order states, admin screens and KPI definitions in this skill match what those platforms use, so they are a spec for the real build.
