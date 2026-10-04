# Cart and checkout variants

Two cart designs and three checkout designs beside the originals (`cart/split`, `checkout/onepage`). Choose them with `"layout": {"cart": "...", "checkout": "..."}` in shop.json. Rules for writing variants are in `variant-contract.md`; the one-line description of each is in `variant-catalog.md`.

## Cart

| Variant | Pick it when | What differs |
|:---|:---|:---|
| `split` (original) | default | item rows on the left, sticky summary on the right |
| `stacked` | few, high-value items; most visitors on phones | one centred column of large item cards, the summary card under the items; on phones a fixed bottom bar shows the total and an Đặt hàng button |
| `table` | buyers add many lines (accessories, office equipment) | header row (product, quantity, line total) over a table-like list; below it a band with the voucher and code list on the left, totals and the order button on the right |

Hooks kept in both: everything in `data/hooks.json` for `cart` (`data-cart-page`, `data-cart-full`, `data-cart-list`, `data-cart-empty`, `data-cart-n`, `data-free-ship`, `data-free-ship-text`, `data-totals`, `data-voucher-form`, `data-voucher-input`, `data-voucher-msg`, `data-voucher-use`, `data-checkout-link`).

Rules the markup follows because `store.js` and `qa.py` rely on them:
- Exactly one `[data-voucher-input]` and one `[data-totals]` per page (QA fills the voucher with a strict selector; `store.js` writes the totals into the first match). Extra totals elsewhere on the page are mirrored by script, not marked with the hook.
- Item rows are drawn by `store.js` as `li.cart-row` (checkbox, image, `.cart-info`, `.cart-side` with price and `.qty`). A cart variant restyles them with CSS only. `table` makes `.cart-side` `display: contents` so price and quantity become grid columns.
- `stacked` ships `js/v/cart-stacked.js`: the bottom bar copies `dd.grand` from `[data-totals]` through a MutationObserver and its button clicks the real `[data-checkout-link]`, so the disabled-cart check still applies.

## Checkout

| Variant | Pick it when | What differs |
|:---|:---|:---|
| `onepage` (original) | default | three numbered blocks on one page, summary on the right |
| `steps` | first-time buyers, long forms, phones | three steps shown one at a time (buyer, delivery, payment) with a progress bar and Back and Continue buttons; the summary stays on the right |
| `split-pay` | payment methods are the main decision (COD, transfer, installment) | left: buyer and delivery as open accordions; right: a sticky card with order lines, payment choice, voucher, totals and the Đặt hàng button |
| `express` | impulse buys, phone visitors | one centred card: name, phone and address first, payment as large cards, the order summary folded at the top with the total in its header, email, note and company invoice behind one link |

Hooks kept in all: everything in `data/hooks.json` for `checkout`. All fields stay inside `form#co-form` (`name`, `phone`, `email`, `province`, `ward`, `street`, `receive`, `store`, `shipping`, `payment`, `note`, `invoice`, company fields), whether shown in steps or not.

### Details per variant

`steps` (`js/v/checkout-steps.js`)
- Sections carry `data-step="1..3"`; steps not yet reached carry `hidden`. Continue is a button with `data-step-next`; it checks only the fields of the visible step (same messages as `store.js`), then shows the next step, scrolls to the top of the form and focuses the first field. Back is `data-step-prev`; completed dots in the progress bar are buttons (`data-step-go`) that return to that step.
- `[data-place-order]` exists only in step 3. The script registers a `submit` listener on the form before `store.js` binds its own, and calls `stopImmediatePropagation` while a step before the last is showing, so pressing Enter in a field moves forward and never places the order early.
- Fields in earlier steps are skipped by the final submit check because they sit in hidden sections; each was already validated when Continue was pressed.
- `qa.py` clicks `[data-step-next]` while it is visible (`reveal()`), so hidden steps never block filling.

`split-pay` (`js/v/checkout-split-pay.js`)
- The payment radios sit outside the form element but belong to it through `form="co-form"`, so `form.payment.value` works. The "Trả góp 0%" quick buy from a product page stores `pay_pref`; `store.js` looks for the radio inside the form only, so the script pre-selects it.
- Accordions start open (so every field is visible to QA and to keyboard users). When a field becomes invalid inside a folded accordion, a MutationObserver opens it and moves focus there. A closed accordion shows a one-line summary of what was typed.

`express`
- `js/v/checkout-express.js` folds the summary on screens up to 700 px, mirrors the grand total into `[data-cex-total]` and opens the "more" block when a field inside it is invalid.
- The summary is a `details.co-summary`, which is the scope `store.js` uses for the voucher form.

## Examples that cover them

- `examples/variants/cart-checkout.shop.json`: `stacked` plus `steps`
- `examples/variants/cart-checkout-2.shop.json`: `table` plus `split-pay`
- `examples/variants/cart-checkout-3.shop.json`: `split` plus `express`

They are copies of the retail demo with another shop name. The first product with options has a fixed stock of 12 so that the QA price-edit step does not depend on the random demo stock (see "Known issue" below).

## How it was checked

- `python scripts/variants.py`: passes (comment, hooks, tokens-only css).
- `python scripts/variants_qa.py --parts cart,checkout`: all 7 variants build, lint and pass the quick QA with the whole buying flow (variant choice, cart, voucher, empty checkout stopped, fill, order, tracking, admin confirm, admin price edit).
- `python scripts/variants_qa.py --parts cart,checkout --dark`: four round-robin builds under `gaming-dark` pass.
- `python scripts/variants_qa.py --coverage`: passes.
- Screenshots of the cart with two items and every checkout step at 1440 and 390 px were read and corrected.

## Known issue (outside these variants)

`qa.py` picks the first product with options and in-stock variants, then edits the price of its first variant. When that first variant has stock 0 (random demo stock), the product page opens on the first in-stock variant and the edit does not show, so the step fails with "admin price change not shown on the product page". It happens with every cart and checkout variant, including the originals. The fix belongs in `qa.py`: pick a product whose first variant has stock above 0.
