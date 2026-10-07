# Maintaining ecommerce-builder

## Adding a rule

Rules added to cure one symptom tend to cause another on the next build. When a check, a SKILL.md rule or a reference rule is added:

- at most five new rules per change, each with the case it applies to ("on a demo shop", "in the hero"), never "always"
- say which rule it replaces or contradicts; when it reverses an old rule, leave a line "Old rule dropped: <rule>, because <reason>" so it is not brought back
- one rule lives in one file; SKILL.md points to it instead of copying it
- a rule that catches nothing in three rounds of building comes out
- after adding a rule, check the templates and examples against it: they are copied as they are, so a mistake in them spreads to every site
- write the rule and its reason, not its history: no dates or client names in the skill; those go in the commit message

## Maintaining the library

Templates live in `templates/` (Jinja2): `layout/base.html` (header, footer, drawers), `pages/`, `sections/` (home sections), `account/`, `admin/`, `partials/macros.html` (product card, rail, price, breadcrumbs, empty state). Behaviour is in `templates/assets/js/common.js` (storage, cart, totals, orders), `store.js` (storefront) and `admin.js` (dashboard and charts); styles in `store.css` and `admin.css`, held flat by `python tools/check_flat_css.py` in the plugin repository (`references/flat-style.md`; `scripts/flat_css.py` and that file are the same in every skill, so change all copies together). Product drawings are in `scripts/devices.py`. Demo history comes from `seed_data` in `build.py` and is written to `assets/js/seed.js` as compact arrays (format in the function's docstring and in `admin.js` seedOrder); `admin.js` decodes it once and caches it. Inside `admin.js` the sections are: data, formatting, charts (inline SVG line, column, bar list, sparkline, heatmap), shell (sidebar counts, collapse, notifications), quick search, period picker and metrics (`periodControl`, `measure`, `series`, `buckets`), then one function per page. Before a large edit of `admin.js`, keep a built `dist` as a copy to restore from. After any change, rebuild `examples/demo-electronics.shop.json`, run lint and QA, and look at the screenshots. Then run `python scripts/stress.py <example> --out <dir> --qa` on the example of each style you touched: it builds the same shop with edge-case data (a 52-character shop name, a 121-character product name, a price over a billion, a product out of stock in every version, a product with no specs or highlights) and runs QA with `--sweep`. Example data is tidy; client catalogues are not.
