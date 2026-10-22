# Websites with several pages

A single page.json builds one landing page. When the client wants a website (a home page plus service, company, trust, resource, contact and legal pages), page.json becomes the home page and lists the other pages in `"pages"`. One command builds the whole site:

```
python SKILL/scripts/build.py sites/<slug>/page.json
```

Every page goes through the same checks as a landing page: copy rules, the brief, photos, voice. On top of those the build checks what only a site has (links between pages, reachability, duplicate titles), and lint and QA run on every page.

## Folder

```
sites/<slug>/
  page.json            the home page (index.html), with "pages", the brief, the theme, the header and the footer
  pages/<id>.json      one file per inner page, written to <id>.html
  img/  media/         the client's photos and films; paths in every page are relative to page.json
  dist/                the built site: index.html, <id>.html, assets/css/<id>.css, assets/js/<id>.js, shared images
```

`examples/site/` is a small working site (a home page and three inner pages) to copy from.

## The page list

```json
"pages": [
  {"id": "solutions", "src": "pages/solutions.json", "label": "Solutions"},
  {"id": "bookkeeping", "src": "pages/bookkeeping.json", "label": "Bookkeeping", "parent": "solutions"},
  {"id": "privacy", "src": "pages/privacy.json", "label": "Privacy notice"}
]
```

- `id`: 2-40 lowercase letters, digits and hyphens. The page is written as `<id>.html`, side by side with `index.html`, so the site opens straight from the folder and needs no server.
- `label`: the short name in the breadcrumb.
- `parent`: the page above it in the breadcrumb (Home / Solutions / Bookkeeping). Leave it out for a page directly under Home.

Menu groups are not pages. A dropdown called "Resources" holds links to pages; it is not one itself.

## What an inner page file holds

```json
{
  "blueprint": "qx-service-detail-bookkeeping",
  "title": "Outsourced bookkeeping for UK firms | Brand",
  "description": "120-160 characters on what the page covers and for whom.",
  "seo": {"image": "img/x.jpg", "image_alt": "...", "index": false},
  "sections": [{"type": "page-head", "data": {...}}, ...]
}
```

Only these fields. The brand, theme, preset, brief, motion, header and footer come from page.json, so a change to the menu is made once. `seo` is optional; an inner page without a photo shares the home page's picture.

## Layout: inner blueprints

Every inner page follows the measured layout of a real inner page of the same kind, the way the home page follows a real homepage. The layouts are in `templates/inner-blueprints/`: 121 pages from 12 BPO and accounting outsourcing sites, plus the trust pages of three accounting software companies (Xero, Karbon, Dext), measured at 1440 px in the browser in October 2026. `scripts/research/inner_blueprints.py` turns new measurements into blueprint files.

```
python SKILL/scripts/variety.py --inner-blueprints                 every type with its layouts
python SKILL/scripts/variety.py --inner-blueprints service-detail  one type
python SKILL/scripts/variety.py --blueprint <key>                  each section and the variants that fit it
```

Types: solutions-overview, service-detail, dedicated-team, audience, software, about, why-us, people, locations, careers, how-we-work, engagement-models, ai-automation, trust-hub, trust-detail, case-studies, case-study, insights, article, resources, guide-landing, contact, legal.

The rules are the homepage rules with three changes:

- The first slot is the page head: `page-head`, or a photo hero (`hero-fullbleed`, `hero-mosaic`). The build fails an inner page that opens with anything else, or that has a second page opening further down.
- An inner page has no minimum section count and needs no services section. Real legal notices are a head and one block of text.
- Proof slots are left out when the brief has no proof. On inner pages these include tool names and certificates as well as logos, quotes, cases, team members and awards.

Pick a layout whose required sections (no `?`) the client's content can fill, and use different layouts for pages of the same type where the content allows, so a site with five service pages does not repeat one shape.

## Sections made for inner pages

| Variant | Use |
|:---|:---|
| `page-head` | Breadcrumb, title, lead, an optional line such as an effective date, up to two buttons. `"layout": "ground"` puts the photo behind the copy under the brand shade; `"side"` puts it in a frame on the right (needs `image_alt`); no image gives a tinted band. The breadcrumb comes from the page list. |
| `prose` | Long text: legal notices, policies, articles, trust detail. Blocks with a heading, paragraphs and lists; paragraphs take `**bold**` and links written `[label](page.html)`. With three or more blocks a sticky contents column marks the block being read. Each block's `id` is a link target (`privacy.html#cookies`). |
| `matrix-table` | A table of short text cells: who prepares, reviews and approves; a cost worksheet line by line; a working-hours example. Rows become cards on phones. A cell that is not known is left out with its row, never guessed. |
| `list-columns` | Two to four titled lists under a rule, with tick, cross or dot markers: scope, what the client sends, what they receive, what is not included. |

Fields and limits are in `section-catalog.md`. Every other variant works on inner pages too.

## Links

- To another page: `bookkeeping.html`. To a section on it: `bookkeeping.html#faq`. The build fails a link to a page the site does not have, or to a section that page does not have.
- The header and footer are written once in page.json. A link there to a home page section (`#services`) leads to `index.html#services` from every inner page, and the logo leads home.
- The menu marks the page being read (`aria-current="page"`), and a dropdown that holds it is underlined.
- Every inner page must be linked from some other page: the menu, the footer, or a section of its parent. The build fails an orphan page.

## Search

Each page has its own title and description; the build fails two pages that share either. With `seo.url` on the home page, every page gets its canonical address (`https://example.com/bookkeeping.html`), and one `sitemap.xml` and `robots.txt` cover the site. An inner page with a breadcrumb carries `BreadcrumbList` structured data. `"index": false` on the home page keeps the whole site out of search, which is right for a site under client review.

## Check

```
python SKILL/scripts/lint_output.py sites/<slug>/dist
python SKILL/scripts/qa_screenshot.py sites/<slug>/dist --all-pages --sweep
python SKILL/scripts/qa_screenshot.py sites/<slug>/dist --page bookkeeping.html --sections --sweep
```

Lint reads every page and checks links between them. QA checks one page with `--page`, or every page with `--all-pages`; screenshots of an inner page go to `dist/qa/<id>/`. Each page takes about as long as a landing page, so on a large site check the pages you changed with `--page` and run `--all-pages` before delivery.

## Writing many pages

A site of 20 or 30 pages is a lot of copy. It helps to write the home page and one inner page first, check them in the browser, then write the rest from those two. Pages may be written in parallel; build each writer's work into its own `--out` folder, since every build writes the whole site. Keep a list of statements the client must confirm (roles, controls, processes described from the brief) and hand it over with the site.
