# Assets: images, icons, flags, cities

Run `python scripts/build.py --list` for the live lists. This file explains what the images show so you can pick the right one.

## Image library (`templates/assets/images`)

Use the key (file name without extension) in any `image` field. Always write a real `alt` describing the photo in the page's context.

| Key | What it shows | Good for |
|:---|:---|:---|
| `team-coworking-laptops` | Four people at a wooden table on laptops, one with headphones | Hero, services, case studies (the safest general image) |
| `team-engineers-screen` | Three engineers looking at code on a laptop | Tech support, QA, AI data, trust and safety |
| `office-interior` | Empty modern office corridor with kitchen | Delivery center, back office, security |
| `meeting-handshake` | Two men in shirts shaking hands across a desk | Case studies, partnerships. Not a call center image |
| `portrait-woman-office` | Smiling woman in a blazer by a window, tall crop | Hero split, team lead, services tab |
| `portrait-woman-studio` | Woman in dark top, studio light, tall crop | Case study person, hero split |
| `city-hcmc-skyline` | Ho Chi Minh City skyline at dusk | Vietnam hub |
| `city-danang-golden-bridge` | Golden Bridge (stone hands), Da Nang | Da Nang hub |
| `coast-philippines-island` | Island coast and lagoon, Philippines | Philippines hub only, not Manila offices |
| `avatar-man-1`, `avatar-man-2`, `avatar-man-3`, `avatar-woman-1`, `avatar-woman-2` | Head-and-shoulder portraits | Testimonial avatars only |

There is no photo of agents on headsets. For a contact center hero, prefer the client's own photos: put them next to page.json and use the relative path (`"src": "photos/floor.jpg"`). Real photos of the client's floor beat stock images.

## Icons

Lucide-style SVG icons, by name, for example `headset`, `shield-check`, `users`, `landmark`, `heart-pulse`. Use `--list` for all names. Unknown names fail the build and print the full list.

## Flags

Lowercase ISO country codes: `vn`, `ph`, `us`, `gb`, `jp`, `kr`, `in`, `mx`, `co`, and 35 more. They render as SVG, never emoji.

## Cities (for `locations-map`)

Keys such as `manila`, `cebu`, `ho-chi-minh-city`, `hanoi`, `da-nang`, `bangalore`, `bogota`, `krakow`, `mexico-city`. If a city is missing, pass an object: `{"name": "Iloilo", "country": "ph", "lat": 10.72, "lon": 122.56}`.
