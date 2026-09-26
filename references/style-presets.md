# Style presets

A preset sets fonts, colors, corner radius, button shape and which tone the hero uses. Pick one; do not mix. The four presets group the UI style notes of 120 BPO and outsourcing websites reviewed while building this skill.

| Preset | Look | Pick it when | Reference sites |
|:---|:---|:---|:---|
| `enterprise-navy` | Deep navy, burnt coral accent, teal highlight, Montserrat headings, pill buttons, dark hero | Large CX or BPO groups selling to banks, telcos, healthcare; the buyer is procurement or a COO | Concentrix, Conduent, Teleperformance, Startek, TDCX |
| `human-warm` | Cream background, deep green text, orange accent, Plus Jakarta Sans, large rounded cards, light hero | Staffing and people-first CX brands that sell culture, retention and team fit | Foundever, TaskUs, SupportNinja, Boldr, PartnerHero |
| `dark-ai` | Near-black canvas, electric blue accent, mint highlight, Space Grotesk headings, every section dark | AI data annotation, RLHF, trust and safety, data-heavy operations | Scale AI, Invisible Technologies, EXL, Sutherland, Toloka |
| `clean-minimal` | White and pale gray, violet accent, Manrope headings, 10px buttons, light hero | Finance, accounting, legal, sales development, Nordic or Japanese buyers who prefer calm pages | Genpact, Transcom, Firstsource, Arvato, Capita |

## Brand colors

If the client has brand colors, keep the preset and override only these keys in page.json:

```json
"theme": {"accent": "#0f62fe", "primary": "#0b1b33"}
```

- `accent` is the button and highlight color. `primary` is the dark section and footer background. `accent_2` is a decorative second color (glows, map rings, chart bars).
- Use 6-digit hex only.
- build.py checks button text contrast and picks white or dark text for you. It also darkens or lightens the accent for text on each background so links stay readable. If it warns about contrast, choose a deeper accent.
- Do not override fonts, radius or spacing. Those are what keep the layout consistent.

## Tones

Each section gets one of three tones: `light`, `muted` or `dark`. build.py assigns them: the hero follows the preset, metrics, CTA and footer are dark, and other sections alternate light and muted so neighbours never share a background. Only set `"tone"` on a section when the client asks for it.
