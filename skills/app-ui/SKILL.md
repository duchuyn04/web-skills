---
name: app-ui
description: Build the screens inside a web app or admin area as a clickable prototype (dashboard, table, list, record detail, multi-step form, long-job progress, preview to approve, settings, sign in, error pages) from a fixed HTML/CSS kit and screen recipes that follow real SaaS apps on Mobbin, so the look does not depend on the model. Use when the user asks for app screens, an admin dashboard, a prototype with many screens, màn hình app, giao diện quản trị, trang admin, form nhiều bước, dựng prototype, or to redo app screens that look AI-made. Not for landing pages (bpo-landing-builder) or online shops, their storefront or their store admin (ecommerce-builder).
compatibility: Needs Python 3.9+ for the scripts. Browser QA needs Python Playwright plus Edge or Chrome, run with a Python that can import it.
metadata:
  version: "1.1.1"
---

# App UI

You do not design from a blank page. The kit (`kit/`) already fixes colour, type, spacing, shape and every
component; the recipes (`recipes/`) already fix the layout of each kind of screen with all its states. Your job
is to understand what each screen is for, pick the recipe, and rewrite it for the product: its words, its
columns, its sample data. Pages use kit classes only; `lint_ui.py` fails anything else.

`SKILL` below means the folder that holds this file. If you cannot run shell commands, stop and tell the user:
the scripts are required.

## Which path

Read the request and take the first row that matches.

| The user | Path |
|:---|:---|
| asks to look at screens built with this kit ("xem giúp", "review", "chỗ nào chưa ổn", a screenshot) | Review. Run lint and QA with `--sweep`, open the screenshots, answer the five questions in `references/rules.md`, then send one table: each problem with its kind (Broken: fails for any brand, such as overflow, low contrast, clipped text; Off-system: differs from the rest of the product; Taste: a preference) and the fix. Change nothing until the user picks the rows |
| asks to change screens already built with this kit | Edit. Change only what was asked, keep frames and recipes, rerun lint and QA, report what changed |
| has an app in another stack (React, Vue, Tailwind, a CSS framework) and wants it changed in place | This version writes plain HTML, CSS and JavaScript. Say so in one line; offer a static prototype of the screens to agree on first, which their developers then port |
| anything else that is app screens | Build: Step 1 onwards |

## Rules that are never negotiable

1. Kit classes only. No colour, shadow or gradient outside `kit/tokens.css`; no `<style>` blocks; no inline style except a custom property or a width in percent. A need the kit does not cover goes in one project CSS file that reads tokens (lint checks it), or in the kit itself when it is general (see Maintaining).
2. Never edit a project's copy of `kit/app.css` or `kit/app.js`. Brand changes go through `scripts/theme.py`.
3. One `h1` and at most one primary button per view and per dialog, in every state.
4. Every screen draws its states as static examples in the same file (`data-state`, opened with `?state=`): see "States every screen draws" in `references/screens.md`. No grey bars standing in for content.
5. Words follow `references/copy.md`: action labels, errors that say what to do, no emoji, arrows, em or en dashes or stock phrases. Sample data is invented on purpose, covers edge cases and is called invented in the report.
6. The kit draws; the project decides. No fetch calls, storage schemes or business rules: buttons fire `ui:` events or link to the next screen.

## Step 1: The brief (the only stop)

Read the project (README, spec, routes, data, existing screens), then send the brief from `references/screens.md`:
five lines (product, users, main jobs, device, what sets it apart) and one row per screen (what people come
to do, what they decide by, the final action, the recipe). Each line says where it came from. Ask at most five
questions, each with a guessed answer. Stop and wait for `ok` or corrections.

Skip the stop only when the request already settles it ("dựng luôn", a spec that answers it, or the user's reply
to an earlier brief); then put the brief in three lines at the top of the report.

## Step 2: Look at real screens

Each recipe already follows real apps (`references/sources.md`). Before rewriting a screen, look at what real
products of the same kind show on it. When the Mobbin tools are connected, search one screen at a time on the
web platform ("order list with status tabs and bulk actions", not a list of keywords) and open the results;
otherwise open the sources of the nearest recipe. Take from them what the screen shows and in what order
(columns, fields, actions, the empty state), never invent a layout the recipes and the references do not show,
and name the references you followed in the report. A screen no recipe fits is built only from such references.

## Step 3: Start the project

```
python SKILL/scripts/new.py --list
python SKILL/scripts/new.py <out> --name "<Product>" --accent "#<logo colour>" --primary brand --screens list:projects,wizard:new,review,dashboard,table:requests
```

It also writes `screens.html` and adds the prototype navigator to every page: a "Xem prototype" button on the
right edge that opens every screen and state, with previous and next screen and Alt+M, Alt+arrow keys
(`kit/proto-nav.js`, filled in by `scripts/protonav.py`). People reviewing a prototype do not find an index
page; they find a button that is always on screen.

`--accent` is the logo colour; without one, keep the default and say where to change it. `--primary` is the
main button: `brand` paints it in the logo colour, `ink` near-black with the brand on the logo and links (real apps
split about evenly); ask in the brief when the user has not said, default `brand`. `recipe:file` names
the page. A product with an existing static site puts the prototype in its own folder (`<project>/app/`).

## Step 4: Rewrite each page for the product

For each page, keep the frame and the recipe's structure, then:

- set the navigation (same links and order on every page of an area; `aria-current` on the right one)
- rewrite the head: the title is the screen's job, the sub line says the one fact that matters now
- put first and largest what users decide by (the brief's column); move the rest down or to the detail page
- replace columns, fields and rows with the product's own; keep the edge cases (a long name, `0`, a big number, a missing value, a past-due item)
- keep and rewrite every state the recipe draws; add the states the product needs (limit, no-access) and list them in `data-states`
- copy any extra component from `references/components.md` exactly; a screen no recipe fits borrows the nearest recipe and says so in the report

Then wire the navigator again, since pages and states changed:

```
python SKILL/scripts/protonav.py <out>                    every page that uses the kit, one list
python SKILL/scripts/protonav.py <out> --config nav.json  groups by area, titles, state labels
```

Give it a config (`<out>/proto-nav.json` is read by default) as soon as the prototype has more than one area:
groups in the order a visitor meets them (visitor, signed-in user, admin), a title per page in the product's
words, a label for every state it reports as unlabelled. A page built by another skill (the landing page) goes in
the config with its path relative to `<out>`; the script adds the tag with the right relative path. When some
screens change with one choice (an industry, a plan), the config's `select` adds that parameter to their links.
The script prints pages the config forgot; list them or leave them in the last group on purpose.

## Step 5: Lint

```
python SKILL/scripts/lint_ui.py <out>
```

It must print `LINT PASSED`. Fix the page, not the rule: a colour error means use a token, a class error means
use a kit class, two primaries means decide which action matters.

## Step 6: Browser QA

```
python SKILL/scripts/qa.py <out> --sweep
```

If `python` cannot import Playwright, use a Python that has it (on Windows `py -0` lists the installed versions, then for example `py -3.11`).

It opens every page in every state at 1440 and 390 px, then narrows each page from 1440 to 360 px. It fails JS
errors, sideways scrolling, broken images, missing icons, low contrast and header items that overlap; it warns on
cut text, small tap targets, wrapped labels, uneven rows and hover that moves the layout. It must print
`QA PASSED`. Then open the screenshots in `<out>/qa/` (the 390 px shot and one desktop shot of each page at
least) and answer the five questions in `references/rules.md`. Fix and rerun; at most three rounds, then report
what is left.

## Step 7: Report

In the language the user wrote in:

- first, every choice you made for them, one line each with the reason and an offer to change it: frame per area, recipe per screen, accent and primary mode, which data is invented
- the real screens each page follows (Mobbin links or the recipe sources)
- where to open it (any page: the "Xem prototype" button on the right lists every screen and state; `<out>/screens.html` is the same list as a page; open the file or run `python -m http.server` in `<out>`)
- lint and QA results, and any warning left on purpose with its reason
- what is static: buttons fire `ui:` events, nothing is saved; where to change the brand (`kit/tokens.css` through `scripts/theme.py`)

## Reference files

- `references/screens.md`: the brief, which recipe for which screen, the states every screen draws, hand-off notes
- `references/components.md`: every kit component with its markup
- `references/charts.md`: which chart for which data, what an overview must have, one date range for the page with comparison, grains
- `references/rules.md`: what makes a screen look machine-made and the rule against each, twelve principles with tests, five questions for screenshots, how to add a rule
- `references/copy.md`: labels, messages, numbers and dates, sample data
- `references/sources.md`: the real screens (Mobbin) behind every kit choice and every recipe
- `references/credits.md`: sources of the kit, the MIT notice of the ui-ux skill whose ideas are adapted, Lucide icons
- `gallery/index.html`: every component in its states, built from the kit

## Maintaining the kit

`kit/tokens.css` is written by `scripts/theme.py` (edit the template there), `kit/icons.js` by
`scripts/make_icons.py` from `data/icons.json`. After any change to the kit, a recipe or the gallery:

```
python scripts/lint_ui.py recipes
python scripts/lint_ui.py gallery
python scripts/qa.py recipes --sweep
```

and look at the screenshots. A recipe starts with `<!doctype html>` and the one-line comment
`<!-- recipe: <name> | <what it is> | states: <list> | use for: <when> -->` that `new.py --list` reads.
A new component goes in `app.css`, `references/components.md` and the gallery together.
`kit/proto-nav.js` is a template: keep its `/*__DATA__*/ null` marker, its own CSS (it also runs on pages
without the kit) and its first-visit hint switched off under `navigator.webdriver`, so QA screenshots stay clean. New rules follow
"Adding a rule" in `references/rules.md`.
