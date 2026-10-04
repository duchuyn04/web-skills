# Thanks, account and footer variants

Added in the page-variant phase. Every variant keeps the hooks in `data/hooks.json` and uses colour tokens only. Choose them with `"layout"` in shop.json.

## Thanks (order confirmation page, `layout.thanks`)

| Variant | Look | Pick it when |
|:---|:---|:---|
| `receipt` | green tick and code on top, items and totals left, payment and delivery right (the original) | default |
| `timeline` | confirmation strip, then a vertical "Các bước tiếp theo" timeline with the order summary, payment and delivery boxes beside it | buyers ask what comes after paying |
| `compact` | one small centered card: code, payment instructions, two buttons; items, totals and delivery fold into details | simple orders, clean look |

`timeline` writes its steps only from shop data: `shop.hours` for the confirmation call, `shipping[].name` and `shipping[].eta` for delivery, `stores` for pickup. Nothing about packing or delivery times is invented. The text of the steps is fixed template copy, so a shop whose process differs should not use it unchanged.

## Account shell (`layout.account`)

The account pages (index, orders, order, wishlist, addresses) are shared; the shell is the frame around them.

| Variant | Look |
|:---|:---|
| `sidebar` | user card and side menu left, content right (the original; the menu is hidden on phones) |
| `tabs` | user strip on top with logout, horizontal tabs under it, content full width; tabs scroll sideways on phones |
| `hub` | tinted greeting card, compact side menu; on phones the menu opens as a bottom sheet from the "Menu tài khoản" button (js `assets/js/v/account-hub.js`: Esc and scrim close it) |

## Footer (`layout.footer`)

| Variant | Look |
|:---|:---|
| `full` | promise row, five columns, payment, legal (original) |
| `minimal` | one row of links, contacts, payments, legal |
| `newsletter` | email signup band on a tinted strip, four link columns, legal. The address is kept with `Shop.set('newsletter', [...])` and a toast confirms it (js `assets/js/v/footer-newsletter.js`). On a real shop the list stays in the visitor's browser: connect a mailing service before launch |
| `centered` | centered logo and tagline, one wrapped row of links, payment names, contact line, social icons, legal |

## Examples

- `examples/variants/pages-footer.shop.json`: `thanks: timeline`, `account: tabs`, `footer: newsletter`.
- `examples/variants/pages-footer-2.shop.json`: `thanks: compact`, `account: hub`, `footer: centered`.

## Verification

Both examples build, pass `lint_output.py` and the full `qa.py` (every page at 1440 and 390 px, the buying flow and the admin flow). `scripts/variants.py` passes for these files. `scripts/variants_qa.py --parts thanks,account,footer` was run with the light and the dark (`gaming-dark`) preset. Screenshots of the order page, account index and orders, the hub bottom sheet and the footers were checked at both widths.
