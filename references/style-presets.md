# Style presets

A preset sets fonts, colors, corner radius, button shape and which tone the hero uses. Pick one; do not mix. The eight presets group the UI style notes of 120 BPO and outsourcing websites reviewed while building this skill.

| Preset | Look | Pick it when | Reference sites |
|:---|:---|:---|:---|
| `enterprise-navy` | Deep navy, burnt coral accent, amber highlight, Montserrat headings, pill buttons, dark hero | Large CX or BPO groups selling to banks, telcos, healthcare; the buyer is procurement or a COO | Concentrix, Conduent, Teleperformance, Startek, TDCX |
| `human-warm` | Cream background, deep green text, orange accent, Plus Jakarta Sans, large rounded cards, light hero | Staffing and people-first CX brands that sell culture, retention and team fit | Foundever, TaskUs, SupportNinja, Boldr, PartnerHero |
| `dark-ai` | Near-black canvas, electric blue accent, mint highlight, Space Grotesk headings, every section dark | AI data annotation, RLHF, trust and safety, data-heavy operations | Scale AI, Invisible Technologies, EXL, Sutherland, Toloka |
| `clean-minimal` | White and pale gray, violet accent, Manrope headings, 10px buttons, light hero | Finance, accounting, legal, sales development, Nordic or Japanese buyers who prefer calm pages | Genpact, Transcom, Firstsource, Arvato, Capita |
| `orange-charcoal` | Burnt orange accent, bright orange highlight, charcoal dark panels, cool gray cards, Inter, pill buttons, pill labels above headings | IT outsourcing plus BPO partners selling to US, EU, Japan or Australia; confident and businesslike | Bestarion, Saigon Technology, SmartOSC, Orient Software, KMS Technology |
| `corporate-blue` | Navy text, bright corporate blue accent, sky blue highlight, Poppins headings, pill buttons, dark hero with angled bottom edges, photos wipe in | Enterprise CX, IT and BPO firms whose brand is blue (about a third of the sites reviewed); formal but modern | Cognizant Business Operations, Cloudstaff, Wing Assistant, FPT Software, Innovature BPO |
| `crimson-trust` | White and warm gray, crimson accent, amber highlight, Source Serif 4 headings over Source Sans 3, square-ish 6px buttons, photos with a cut corner, underlined heading highlights | Staffing, finance and accounting outsourcing that sells trust and long tenure; brands with a red logo | WNS Global Services, ModSquad, Kyanon Digital, Luvina Software, TPS Software |
| `teal-fresh` | Mint-white, deep teal accent, green highlight, Outfit headings, large rounded cards, pill labels, curved section edges, arched photo frames, gradient heading highlights | Friendly staffing, healthcare support and voice teams; brands with a teal or green logo | Emapta, Acquire BPO, Doxa Talent, CMC Global, Savvycom Software |

## Brand colors

If the client has brand colors, keep the preset and override only these keys in page.json:

```json
"theme": {"accent": "#0f62fe", "primary": "#0b1b33"}
```

- `accent` is the button and highlight color. `primary` is the dark section and footer background. `accent_2` is a decorative second color (glows, map rings, chart bars).
- Use 6-digit hex only. Put the logo's main color in `accent` exactly as the client gives it; do not pre-darken it. Give `primary` only when the client has a dark brand color, and `accent_2` only when the client has a real second brand color.
- build.py turns these into every color token by the rules in `references/color-system.md`, and prints a `theme.*` warning for each change. Read those warnings and pass them on to the client: they are design decisions, not errors. In short: a bright accent is darkened at the same hue until white button text reaches 4.5:1 and the original becomes `accent_2`; a warm accent without `primary` gets a dark tint of its own hue instead of the preset's navy; gray text and surfaces are tinted toward the accent hue; glows that would turn grey or brown over a colored dark section are dropped.
- Do not override fonts, radius or spacing. Those are what keep the layout consistent.

## Design options

Each preset also sets four page-wide design options. Keep the preset's choice unless the client asks for a different look; override any of them in `theme`:

```json
"theme": {"edges": "curve", "image_mask": "arch", "highlight": "gradient", "media_reveal": "clip"}
```

| Option | Values | What changes |
|:---|:---|:---|
| `edges` | `none` (default), `angle`, `curve` | The bottom of the hero and of dark sections is cut at a slant or curved, and the next section tucks under it. |
| `image_mask` | `rounded` (default), `angle`, `arch` | Photo frames in feature rows, split heroes, service tabs and boxed banners get a cut corner or an arched top. |
| `highlight` | `color` (default), `gradient`, `underline` | How `*accent*` words in headings look: accent colour, accent-to-highlight gradient, or an underline bar. |
| `media_reveal` | `fade` (default), `clip` | `clip` wipes photos up from the bottom as they scroll in. |

Presets that set them: `corporate-blue` (angle edges, clip reveal), `crimson-trust` (angle image mask, underline), `teal-fresh` (curve edges, arch mask, gradient, clip reveal). The other five keep the defaults. `examples/variations/` has one page per new preset showing each option.

## Heading labels

Every preset shows a small label (eyebrow) above section titles. `orange-charcoal` and `teal-fresh` draw it as a pill with a thin border; the others draw a short line before uppercase text. To switch on any preset, set `"theme": {"eyebrow": "pill"}` or `"theme": {"eyebrow": "line"}`.

## Tones

Each section gets one of three tones: `light`, `muted` or `dark`. A fourth tone, `accent`, paints a section in the brand colour; only `hero-gradient`, `ticker-band` and the office panel of `contact-split` use it, and text on it takes the button text colour so it stays readable. build.py assigns them: the hero follows the preset, metrics, CTA and footer are dark, and other sections alternate light and muted so neighbours never share a background. Only set `"tone"` on a section when the client asks for it.
