# Motion on real BPO homepages

Measured on 2026-09-30 on the 92 homepages behind `templates/blueprints/` (89 loaded; two blocked the browser, one was empty). A script loaded each page at 1440 x 900, recorded every heading, photo, card and button below the first screen, scrolled down in 450 px steps and compared each element before and 1.3 s after it came into view. It also logged the animation libraries, GSAP tween settings, CSS animations, sticky and scroll-linked elements, and the `:hover` rules that move something.

## What the numbers say

| Measure | Share of sites |
|:---|:---|
| Any element animates in on scroll | 47% |
| Carousel library (Swiper, Slick, Splide) | 48% |
| Sticky element inside the page | 29% |
| Photo or block moves with the scroll (parallax) | 24% |
| Autoplaying background video | 21% |
| Webflow interactions | 15% |
| AOS (`fade`, `fade-up`) | 9% |
| GSAP | 4% |

How elements arrive, where they animate at all:

| Element | Most common entrance | Distance |
|:---|:---|:---|
| Section headings | fade (17% of sites), rise (15%) | median 40 px (30-59) |
| Photos | fade (11%), scale up from about 0.95 (10%), slide from the side (9%) | median 50 px |
| Cards in a row | slide in from the side (17%), fade (13%), rise (12%) | median 27 px |
| Buttons | fade (8%) | |

GSAP pages used `y: 40, opacity: 0, duration: 0.9, ease: power2.out` with a stagger. Headings split into masked words appeared on one site in 89.

Hover rules that move something (share of sites, from up to 15 rules sampled per site): buttons move or change fill (52%), cards lift (40%), photos zoom inside their frame (37%), icons or chevrons turn (36%), arrows and link text slide (24%). The median site has 12 such rules.

## What the skill takes from it

- Half the sites move nothing on scroll, so a calm page is normal. The other half move a little and slowly: 30-60 px over 0.8-0.9 s, never a bounce.
- Distinct pages differ in the details: how photos open, how a row of cards arrives, what a hover does, one scroll-linked piece (a sticky list, a drifting photo, a video that grows). The skill builds these into the sections instead of asking the model to invent motion.
- The page's motion style (`theme.motion_style`, else picked from the brand name) sets how elements arrive:

| Style | Entrance | Real-site pattern | Picked for |
|:---|:---|:---|:---|
| `rise` | fade and rise 40 px, 0.8 s, power3.out | the GSAP and AOS `fade-up` pages | 35% of brands |
| `slide` | cards in a row slide in 56 px from the right, other elements rise 24 px | cards sliding in, the most common card entrance | 25% |
| `fade` | fade only, 0.7 s | the half of sites that barely move | 25% |
| `mask` | section titles rise word by word from a mask, photos open from the bottom and settle from 112% | rare on BPO sites, common on agency sites | 15% |

- Every style keeps the section's own motion (frame wipes, check lists, counters, carousels) and the hover set, so two pages in the same style still differ by their sections.
- Scroll entrances run 0.6-1.2 s; hovers stay within 0.5 s (`lint_output.py`, `slow-motion`).
