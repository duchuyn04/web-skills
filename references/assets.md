# Assets: images, icons, flags, cities

Run `python scripts/build.py --list` for the live lists. This file explains what the images show so you can pick the right one.

## Image library (`templates/assets/images`)

Use the key (file name without extension) in any `image` field. Always write a real `alt` describing the photo in the page's context. Read the "What it shows" column before choosing: pick the photo whose content matches the section, not the one whose name sounds closest. These are sample photos of strangers, not the client's staff; tell the user every stock photo on the page should be replaced with the client's own before launch.

Photos marked (card) are 1024 px wide: use them in cards, tiles and case slides, never as a full-width hero or banner background.

### People at work

| Key | What it shows | Good for | Not for |
|:---|:---|:---|:---|
| `team-coworking-laptops` | Four people at a wooden table on laptops, one with headphones | Hero, services, case studies (safe general image) | |
| `desk-phone-monitors` | Woman at a desk with a desk phone and two monitors showing a web app, seen from behind | Customer support, back office, "our team" rows | A face-forward hero (her face is hidden) |
| `office-worker-laptop` | Smiling man in a blazer typing on a laptop in a bright office | Account manager, client success, feature rows | |
| `developer-headphones-monitors` | Woman in orange headphones coding at a standing desk with three screens, city view | Software, QA, IT outsourcing, AI data, tech support | Contact center (headphones, not a call headset) |
| `code-review-pair` | Two women looking at code on a laptop, from over the shoulder | QA, code review, pair work, training | |
| `team-engineers-screen` | Three engineers looking at code on a laptop | Tech support, QA, AI data, trust and safety | |
| `laptop-conference-room` | Man with glasses on a laptop at a long conference table | Consulting, solutions team, remote project work | |
| `team-meeting-table` | Diverse team of eight around a conference table with laptops and coffee | About us, culture, enterprise team, case studies | |
| `team-meeting-bright-office` | Five colleagues in a lively meeting in a glass-walled office, one man standing | Team, onboarding, account reviews | |
| `training-workshop-board` | Man presenting to a group in front of a flip chart covered with sticky notes | Training, onboarding, workshops, process design | |
| `presenter-planning-board` | Woman in a wheelchair presenting a sticky-note plan to colleagues | Workshops, process mapping, discovery, inclusive culture | |
| `meeting-handshake` | Two men in shirts shaking hands across a desk | Case studies, partnerships | A call center image |

### Back office and finance

| Key | What it shows | Good for | Not for |
|:---|:---|:---|:---|
| `accounting-documents-calculator` | Close-up of hands writing in a ledger next to a desk calculator, binders and charts | Bookkeeping, accounting, finance and accounting BPO | |
| `paperwork-review-desk` | A person at a wooden desk reading printed documents, warm window light, hands and papers in focus | Accounting, payroll, document processing, back office | |
| `paperwork-desk-hands` | Hands holding a pen over printed pages on a desk, phone to one side | Bookkeeping, document review, contract work | |
| `calculator-pens-flatlay` | Calculator, pens and an orange folder on a wooden desk, seen from above | Accounting, tax, finance and accounting BPO | |
| `bookkeeping-calculator-laptop` | Hands on a calculator in front of a laptop showing an accounting app | Bookkeeping, invoicing, payroll, accounts payable | |
| `paperwork-signing-laptop` | Man in a brown jacket leaning over a desk signing papers beside a laptop | Document processing, contracts, KYC, claims | |
| `finance-chart-screen` | Dark screen with market charts and figures | Banking, fintech, data analytics industry cards | People-focused sections (no people) |

### Industries

| Key | What it shows | Good for | Not for |
|:---|:---|:---|:---|
| `healthcare-consultation` | Senior doctor at a desk with a patient and a nurse | Healthcare BPO, patient support, medical billing | |
| `doctor-tablet` | Doctor in a white coat with a stethoscope holding a tablet | Healthcare, telehealth support, medical records | |
| `ecommerce-packing` | Person packing a cardboard parcel on a work table | Ecommerce support, order and returns processing | |
| `warehouse-aisle-boxes` | Warehouse aisle lined with stacked cardboard boxes (card) | Logistics, fulfillment, order processing cards | Hero |
| `warehouse-racks` | Rows of tall orange pallet racks in an empty warehouse (card) | Logistics, supply chain cards | Hero |
| `port-containers` | Container port from above with a crane and trucks (card) | Logistics, shipping, import and export cards | Hero |

### Places

| Key | What it shows | Good for | Not for |
|:---|:---|:---|:---|
| `office-interior` | Empty modern office corridor with kitchen | Delivery center, back office, security | |
| `meeting-room-empty` | Long empty meeting room with a glass wall and city view | Delivery center, facilities, security, banner-image | |
| `office-building-entrance` | Glass office building entrance at dusk with people walking in | Locations, about us, banner-image, contact | |
| `city-hcmc-skyline` | Ho Chi Minh City skyline at dusk | Vietnam hub | |
| `city-danang-golden-bridge` | Golden Bridge (stone hands), Da Nang | Da Nang hub | |
| `coast-philippines-island` | Island coast and lagoon, Philippines | Philippines hub | Manila offices |

### Portraits

Wide portraits with the face near the centre, so they crop cleanly to squares in `team-grid` and to circles in `hero-collage`.

- `portrait-man-desk` and `portrait-man-desk-wood` show the same man. Never use both on one page.
- `team-meeting-bright-office`, `training-workshop-board`, `presenter-planning-board` and the three office-background portraits (`portrait-exec-*`, `portrait-woman-team-lead`) come from one photo shoot, so the same people appear in several of them. That reads as one company, which is fine on one page, but do not present them as different offices or clients.
- None of the portraits shows an East or Southeast Asian person. Match names to faces: do not put a Vietnamese or Filipino name under one of these photos. When the client's leaders are Vietnamese or Filipino, use their real photos or leave `team-grid` out.

| Key | What it shows | Good for |
|:---|:---|:---|
| `portrait-exec-man-senior` | Grey-haired man with arms crossed in an office, team behind him | CEO, founder, managing director |
| `portrait-exec-woman-senior` | Grey-haired woman in glasses holding a tablet, team behind her | CEO, COO, head of quality |
| `portrait-woman-team-lead` | Smiling woman in a red sweater with a coffee, team behind her | Team lead, head of people, client success |
| `portrait-woman-glasses-desk` | Woman in glasses at a white desk, calm expression | Finance lead, compliance, operations |
| `portrait-man-desk` | Smiling man in a polo at a white desk with a laptop | Delivery lead, sales, recruiting |
| `portrait-man-desk-wood` | Smiling man in a polo at a desk, wood wall behind | Delivery lead, account manager |
| `portrait-woman-office` | Smiling woman in a blazer by a window, tall crop | Hero split, team lead, services tab |
| `portrait-woman-studio` | Woman in a dark top under studio light, tall crop | Case study person, hero split |
| `avatar-man-1`, `avatar-man-2`, `avatar-man-3`, `avatar-woman-1`, `avatar-woman-2` | Head-and-shoulder portraits | Testimonial avatars only |

### Gaps

The library has no photo of agents wearing call headsets, no contact center floor and no office photos in Manila, Hanoi or Bogota. Photos of that kind with an open licence were not found in public-domain sources. For a contact center page, prefer the client's own photos: put them next to page.json and use the relative path (`"src": "photos/floor.jpg"`). Real photos of the client's floor beat stock images.

### Sources and licence

`templates/assets/images/credits.json` lists the source page, photographer and licence of each photo added on 2026-09-27. All of them are CC0 1.0 (StockSnap and the rawpixel public-domain collection): free for commercial use without attribution. The older files (`team-coworking-laptops`, `team-engineers-screen`, `office-interior`, `meeting-handshake`, the `portrait-woman-*`, `city-*`, `coast-*` and `avatar-*` photos) have no recorded source; confirm their licence before using them on a client site.

## Video library (`templates/assets/video`)

| Key | What it shows | Good for |
|:---|:---|:---|
| `sample-ambient-loop` | 8 second abstract loop: soft moving light on a dark grid, drawn by `scripts/make_sample_video.py` | Previewing `hero-fullbleed` (`video` field) or `video-block` (`src`) before the client sends footage |

The sample clip is a placeholder, not content. In `video-block` it has no story to tell, so replace it with the client's real video or drop the section. In `hero-fullbleed` it works as a neutral ambient background until real office footage arrives. Client videos go next to page.json as `.mp4` or `.webm`; YouTube and Vimeo links go in `video-block`'s `embed` field.

## Icons

Lucide-style SVG icons, by name, for example `headset`, `shield-check`, `users`, `landmark`, `heart-pulse`. Use `--list` for all names. Unknown names fail the build and print the full list.

## Flags

Lowercase ISO country codes: `vn`, `ph`, `us`, `gb`, `jp`, `kr`, `in`, `mx`, `co`, and 35 more. They render as SVG, never emoji.

## Cities (for `locations-map`)

Keys such as `manila`, `cebu`, `ho-chi-minh-city`, `hanoi`, `da-nang`, `bangalore`, `bogota`, `krakow`, `mexico-city`. If a city is missing, pass an object: `{"name": "Iloilo", "country": "ph", "lat": 10.72, "lon": 122.56}`.
