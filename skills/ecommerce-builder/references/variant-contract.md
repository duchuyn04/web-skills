# Variant contract

Read this before adding a layout variant or a home section. `python scripts/variants.py` checks every rule below; the build checks the variants a shop chooses; `python scripts/variants_qa.py` builds and tests every variant.

## What a variant is

One template file in a part folder. Adding the file adds the variant, nothing else is registered.

| Part | Folder (`templates/`) | Chosen with |
|:---|:---|:---|
| header | `layout/headers/` | `layout.header` |
| hero | `sections/hero/` | `layout.hero`, or `variant` on one hero section |
| card | `partials/cards/` (macro `card(p, flash, lazy)`) | `layout.card` |
| pdp | `pdp/` | `layout.pdp` |
| plp | `plp/` | `layout.plp` |
| footer | `layout/footers/` | `layout.footer` |
| cart | `cart/` | `layout.cart` |
| checkout | `checkout/` | `layout.checkout` |
| thanks | `thanks/` (the order confirmation page) | `layout.thanks` |
| account | `account/shells/` (the frame around the account pages; the pages themselves are shared) | `layout.account` |

Home sections: `sections/<type>.html` is the default design of a section type; extra designs go in `sections/<type>/<variant>.html` and are chosen with `"variant"` on the section. A new type is a new `sections/<type>.html`.

## Rules

1. First line: a comment `{# what it is and when to pick it #}`, one or two sentences. It becomes the text of `--list` and of `references/variant-catalog.md`. Missing comment = error.
2. Hooks: keep every `data-...` attribute listed for the part in `data/hooks.json` (the file is the intersection of the first variants). `store.js`, `common.js` and `qa.py` find elements through them. An element a variant does not want visible stays in the markup with `hidden`.
3. Colours: tokens only (`var(--c-bg)`, `--c-surface`, `--c-surface-2`, `--c-text`, `--c-muted`, `--c-border`, `--c-accent`, `--c-accent-soft`, `--c-accent-ink`, `--c-btn`, `--c-btn-fg`, `--c-price`, `--c-link`, `--c-header`, `--c-header-fg`, `--c-dark`, `--c-ok`, `--c-warn`, `--c-bad`, `--radius`, `--radius-lg`, `--font`, `--font-head`). No hex colours in `assets/css/v/*.css`, so the variant works in every preset, including `gaming-dark`. A line may carry `/* hex-ok: reason */` for art-like colours.
4. CSS files: `assets/css/v/<part>-<variant>.css`, for sections `section-<type>.css` and `section-<type>-<variant>.css`. JS in `assets/js/v/` with the same names. They are included only when the variant is used.
5. No gradients except photo scrims; no glass or glow shadows; text 4.5:1 on its background; targets 24px or larger on phones; every interactive element reachable by keyboard.
6. Every variant must appear in at least one `examples/**/*.shop.json` (`variants_qa.py --coverage`).

## Hook details for the buying flow

- Checkout: all fields stay inside one `form#co-form` (inputs `name`, `phone`, `email`, `province`, `ward`, `street`, `shipping`, `payment`, `receive`, `store`, `note`...) even when shown in steps. Steps advance with a button carrying `data-step-next`; it validates the fields of the current step and shows the next. The final submit is `[data-place-order]` and must be visible on the last step. `qa.py` clicks `[data-step-next]` while it is visible, so hidden steps never block filling.
- Cart: `[data-cart-page]`, `[data-cart-list]` rows with class `cart-row`, `[data-voucher-form]`/`[data-voucher-input]`, `[data-totals]`, `[data-checkout-link]`.
- Thanks: `[data-order-page]`, `[data-o-code]`, `[data-o-items]`, `[data-o-totals]`, `[data-o-pay]`, `[data-o-ship]`, `[data-o-track]`.
- Account shell: `[data-account]` on the content wrapper, `[data-user-name]`, `[data-logout]`; pages fill `{% block account %}`.

## Checking

```
python scripts/variants.py                        rules 1-3 for every variant
python scripts/variants_qa.py --parts cart        build, lint and quick QA with each variant of a part
python scripts/variants_qa.py --dark              every variant under the dark preset
python scripts/variants_qa.py --coverage          every variant appears in an example
python scripts/make_catalog.py                    refresh references/variant-catalog.md
```
