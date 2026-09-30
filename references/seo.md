# Search and share tags

build.py writes every search and share tag from page.json (`scripts/seo.py`), and lint checks the result. You supply facts and never write tags yourself. This file covers what the build writes, the fields that feed it, what real BPO homepages do, and the work the client does outside the page after launch.

Sources: Google Search Central, Bing Webmaster Guidelines, IndexNow, schema.org, ogp.me, Meta and web.dev, collected with links in `docs/research/seo-standard.md` in the job project (2026-09-30). Measurements come from `scripts/research/seo_probe.py`.

## What real BPO homepages do

Measured on 2026-09-30 from the server HTML of the 94 blueprint homepages. 85 answered; 9 timed out or blocked the probe.

| Tag | Share of 85 sites | Notes |
|:---|:---|:---|
| `<title>` | 100% | length p25 46, median 54, p75 61 characters; 71 end with "\| Brand" or "- Brand" |
| meta description | 100% | length p25 139, median 151, p75 161 |
| canonical link | 92% | |
| robots meta | 60% | most common: `index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1` (34 sites) |
| og:title / og:description | 98% / 96% | |
| og:image | 85% | with width and height 45%, with alt 22% |
| og:url / og:type | 80% / 87% | |
| og:site_name / og:locale | 66% / 55% | |
| twitter:card | 89% | `summary_large_image` on 68 of 76 |
| favicon | 98% | apple-touch-icon 71%, web manifest 13%, theme-color 12% |
| hreflang alternates | 31% | only sites with several language versions |
| JSON-LD | 86% | Organization 61, WebSite 55, WebPage 43, PostalAddress 39, ContactPoint 33, BreadcrumbList 26, FAQPage 11, LocalBusiness 9, AggregateRating 4 |
| exactly one h1 | 84% | 6 sites have none, 8 have several |
| images with alt | median 100% | lazy loading on 76 of 84 sites with images |

## What build.py writes

| Output | From | When |
|:---|:---|:---|
| `<title>`, meta description | `site.title`, `site.description` | always |
| `<meta name="robots">` | `seo.index`, placeholders | `index, follow, max-image-preview:large`; `noindex, nofollow` when `seo.index` is false or the page still has placeholders |
| verification meta tags | `seo.google_verification`, `seo.bing_verification` | when set |
| `<link rel="canonical">`, `og:url` | `seo.url` | when set |
| `<link rel="alternate" hreflang>` | `seo.alternates` | when set |
| `og:type`, `og:site_name`, `og:locale`, `og:title`, `og:description` | site fields, `lang`, `seo.locale` | always; og:title drops the "\| Brand" part, as Meta asks, because og:site_name carries it |
| `og:image` with width, height and alt | `seo.image`, else the hero photo, else the first content photo | when the page has a photo; absolute when `seo.url` is set |
| `twitter:card` | | `summary_large_image` with a share image, `summary` without |
| favicon | `seo.icon`, else a monogram of `site.brand_mark` on the dark theme colour | `favicon.svg` for browsers plus a 192 px `favicon.png` (also the apple-touch-icon), because Google Search shows only BMP, GIF, ICO, PNG, JPEG, PPM and TIFF favicons |
| JSON-LD `@graph` | see below | always |
| `sitemap.xml` | `seo.url` | when the page is indexable; `lastmod` changes only when the page content changes (build-report.json keeps a content hash) |
| `robots.txt` with a Sitemap line | `seo.url` | when the page is indexable and sits at the root of its host; crawlers read robots.txt only there |

JSON-LD carries only facts the page shows:

- `Organization`: brand, description, logo (`site.logo`, at least 112 x 112 px or build warns), `sameAs` (footer social links), telephone and email (footer contacts), `address` (offices in `locations-gmap`).
- `WebSite` and `WebPage`, linked to the Organization by `@id`, with the language and the share image. Google reads the site name from WebSite, so `site.brand` must match the name on the client's signage and profiles.
- `FAQPage` from the questions of every FAQ section. Google stopped showing FAQ rich results on 2026-05-07; the markup matches visible content, schema.org keeps the type, and other engines may still read it, so it stays.

Values with a placeholder (`[So dien thoai]`) or an example domain (`example.com`, `.example`) are left out. Reviews are never marked up as `AggregateRating` or `Review` of the company: Google treats reviews a business publishes about itself as self-serving and does not show them.

## Fields

| Field | Write |
|:---|:---|
| `site.title` | The service first, then the brand: "Offshore accounting teams in Da Nang \| So Sang". Google sets no length limit and cuts titles to the screen width; three quarters of BPO titles stay within 60 characters, so build warns above that. Brand missing warns. |
| `site.description` | One or two plain sentences, 120-160 characters: what the company does, where, for whom. Google may show page text instead when it matches the search better. Do not start it with the title. |
| `seo.url` | Live https address ending in `/` or `.html`. Errors: http, a query, a #fragment, a path without `/` or `.html`. Leave it out until the client gives the domain. |
| `seo.image`, `seo.image_alt` | 1200 x 630 JPG or PNG (Meta's size, ratio 1.91:1, under 8 MB). A photo, never the logo or an image of text. SVG fails; below 600 px wide warns. |
| `seo.icon` | Square PNG, 192 px or more. SVG only works in browsers (warns). |
| `seo.locale` | `language_COUNTRY` such as `en_AU`, only when it differs from the default for `lang` (`en_US`, `vi_VN`). |
| `seo.index` | `false` for a page that must stay out of search. |
| `seo.alternates` | The same page in other languages, this page included: `[{"lang": "en", "url": "https://x.com/"}, {"lang": "vi", "url": "https://x.com/vi/"}, {"lang": "x-default", "url": "https://x.com/"}]`. Every version must list the same set; Google ignores links that are not returned from the other side. Codes are languages (`en`, `vi`, optionally `en-GB`), never a country alone. Each version keeps its own `seo.url` as canonical. |
| `seo.google_verification`, `seo.bing_verification` | The content value of the verification meta tag from Search Console or Bing Webmaster Tools. Keep it after verification; removing it loses access. |

What does not matter: meta keywords (Google ignores them), the `lang` attribute for language detection (Google reads the visible text), and sitemap `priority` and `changefreq` (ignored).

## Lint

`lint_output.py` fails a built page without `<html lang>`, with no or several `<title>`, without a meta description, without `og:title`, `og:description` or `og:type`, without a favicon link, with several canonical links or a relative one, with an hreflang link that is not a full https address, with JSON-LD that is not valid JSON, with a sitemap next to a `noindex` page, or with a sitemap URL that differs from the canonical. It warns on a missing `og:image`, an SVG-only favicon and headings that skip a level (h2 then h4).

Page speed is part of the library, not page.json: hero images load eagerly with `fetchpriority="high"`, section photos below the hero load lazily, and templates give each `<img>` its width and height. The Core Web Vitals targets (75th percentile of real visits) are LCP within 2.5 s, INP within 200 ms and CLS within 0.1.

## After launch

Put these in the report to the client (Step 7). None of them can be done from page.json.

1. Google Search Console: add the site (a Domain property needs a DNS record; a URL-prefix property can use `seo.google_verification`), submit `sitemap.xml`, and request indexing of the home page.
2. Bing Webmaster Tools: import the site from Search Console, or verify with `seo.bing_verification`. Bing also accepts IndexNow pings for fast recrawls; Google does not use IndexNow.
3. robots.txt: when the page does not sit at the root of the host, add `Sitemap: <url>sitemap.xml` to the root robots.txt. Google also takes the favicon and the site name from the root page.
4. Google Business Profile, only for an office clients or staff can visit, with fixed signage. One profile per business location.
5. Same name, address and phone (NAP) everywhere: the page, the footer, Google Business Profile, LinkedIn, Clutch and other directories.
6. Links come from real mentions: partner and client sites, directories, press, events, business cards. Never buy links.
7. Check the share preview with the Facebook Sharing Debugger and LinkedIn Post Inspector, and the structured data with Google's Rich Results Test and the Schema Markup Validator.
