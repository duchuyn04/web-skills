# Flat style

Shared by every skill in this plugin (the same file in each `references/`). `scripts/flat_css.py`, also the same in every skill, checks stylesheets against it, and `tools/check_flat_css.py` in the plugin repository holds every library stylesheet to it with no finding allowed.

## Why pages built by a model look alike

A model picks the most common choice in its training data each time, so generated pages converge on one look; Anthropic calls this distributional convergence. Reviewers now spot that look at a glance and read it as "made by AI, nobody checked". The tells below are the ones named by design reviewers and by the AI tool makers themselves, with the CSS that produces each.

| Tell | In CSS or markup | Do instead |
|:---|:---|:---|
| Gradient headings | `background-clip: text` over a gradient | One flat colour; emphasis from size and weight |
| Purple, indigo or violet to pink or blue gradients | `linear-gradient(#6366f1, #8b5cf6)` on heroes, buttons, cards | The client's colour as a solid fill |
| Glow | a shadow in the brand colour (`0 20px 60px rgba(brand, .4)`), blurred colour blobs, aurora or spotlight behind the hero | A plain surface, a real photo, or contrast and space |
| Soft shadow on every card | `box-shadow: 0 10px 30px rgba(0,0,0,.1)` on things that sit in the page | A 1px border or one step of surface tone; never both a border and a wide shadow |
| Cards that rise on hover | `:hover { transform: translateY(-4px); box-shadow: ... }` | Change the border, the background or the underline |
| Frosted glass on content | `backdrop-filter: blur()` on cards and badges | Opaque surfaces; glass only on a header or menu over content |
| Pill badge above the headline | a rounded, outlined "New" or label chip over the H1 | Drop it, or put the point in the headline |
| Icon in a tinted square on every card | a 40-48px tile in the accent tint above each heading, three columns | The icon in the text colour beside its label, or no icon |
| Everything in a rounded card, cards inside cards | `rounded-2xl` boxes for every block | Group with space, type and dividers; a card only for a thing you can open |
| The same large radius everywhere | 24-44px on buttons, cards and inputs alike | Radius scaled to the element, small on small things |
| Neon accents on dark | glowing borders, five bright colours on near-black | One accent, used on purpose |
| Default fonts | Inter, Roboto or a system stack for headings | A heading face chosen for the trade |
| Emoji as icons, numbered 01 02 03 on things that are not steps, made-up stats | | One icon set; numbers only on real sequences; figures from the brief |

## Flat colour

A flat page separates and ranks things with colour and space, not with light effects.

- **Palette.** One brand hue, a neutral scale tinted toward it (a warm brand gets warm greys), and at most one second accent close to it on the colour wheel. Red, amber and green stay for status.
- **Proportion.** Neutrals carry the page: backgrounds, surfaces, text. The brand colour marks what to act on and a few key marks. At most one section is painted in the brand colour.
- **Separation.** Use, in this order: space; a 1px hairline border; one step of surface tone (the page `bg`, a `surface`, a `surface-2` a few percent darker or tinted toward the brand); a solid colour block for a whole section. Pick one per element.
- **Tints for soft fills.** A soft fill is the brand colour mixed with the surface (`color-mix(in oklab, var(--accent) 10%, var(--surface))`), used flat. Chips, selected rows and notices use it; whole cards rarely do.
- **Contrast.** Text 4.5:1 (3:1 at 24px, or 18.66px bold); input borders, focus rings and state marks 3:1 (WCAG 1.4.11). Decorative hairlines may be fainter. No grey text on a coloured fill: use white or a dark tint of that hue.
- **Keep the signifiers.** Flat does not mean ambiguous: buttons have a solid fill or a clear outline, links are underlined or clearly coloured, and the selected state differs by more than colour.

## Shadows

A shadow says "this floats above the page". Only things that really float carry one:

- menus, dropdowns, popovers, tooltips and autocomplete lists
- dialogs, drawers, bottom sheets and the off-canvas sidebar on phones
- toasts and the bulk-action or compare bar
- a sticky header or bar once the page scrolls under it
- a floating button (chat, back to top)
- a drawn 3D object or a device frame, marked in the CSS with `/* flat-ok: <reason> */` inside the rule or just before it

Everything else (cards, photos, panels, forms, pricing plans, the featured item, testimonial cards, buttons) is flat: no shadow at rest and none on hover. A hairline shadow of 4px blur or less and 2px offset or less passes, as do inset rings (`inset 0 0 0 1px`, `inset 0 -2px 0` for a selected tab) and focus rings (`0 0 0 3px` with no blur).

When a shadow is used, it is neutral (a grey or a very dark tint of the page hue, never the brand colour), one or two layers, alpha between about 0.06 and 0.25, and comes from the skill's shadow tokens rather than being typed per rule. On dark pages a raised surface is lighter instead of shadowed.

## Gradients

Surfaces are flat. A gradient is allowed only when it does a job a flat colour cannot:

- a scrim over a photo or video so text on it stays readable (one neutral or dark colour fading to transparent)
- an edge fade, as a `mask-image`
- shading inside a drawn object in one hue (a device body, a sphere, a floor shadow)
- a hard-stop pattern: stripes, a split fill, a progress or range track

Never: gradient text, colour-to-colour backgrounds on sections, cards, panels, buttons or borders, a brand colour fading to transparent or white (it reads as a glow), blurred colour blobs, light sweeps, hover spotlights.

## What the scripts check

`scripts/flat_css.py`, run by each skill's lint on every built stylesheet and `<style>` block:

| Code | Finding |
|:---|:---|
| `gradient-text` | `background-clip: text` |
| `gradient` | a soft gradient that blends two colour families, or fades a brand colour out |
| `blur-blob` | `filter: blur()` of 24px or more |
| `glow` | a shadow in a brand or other chromatic colour with 16px blur or more |
| `resting-shadow` | a shadow larger than a hairline on something that does not float |
| `hover-shadow` | a shadow that appears or grows on hover |
| `hover-lift` | an element that moves up on hover (warning) |
| `glass` | `backdrop-filter` on something that does not float (warning) |

A rule counts as floating when its selector names a floating part (header, nav, menu, mega, dropdown, popover, tooltip, dialog, modal, drawer, sheet, toast, fab, suggest, flyout, palette, tray, buybar, savebar, bulk, slider thumb and a few more), when it sets `position: fixed` or `sticky`, or when it carries the `flat-ok` marker. Each skill says in its own docs whether a finding fails the page or prints a warning.

## Sources

- Anthropic, Improving frontend design through skills: https://claude.com/blog/improving-frontend-design-through-skills
- Impeccable, AI slop patterns: https://impeccable.style/slop
- The Fountain Institute, 7 tells that a UI is AI generated: https://pages.thefountaininstitute.com/posts/7-tells-that-a-ui-is-ai-generated
- Why your AI keeps building the same purple gradient website: https://prg.sh/ramblings/Why-Your-AI-Keeps-Building-the-Same-Purple-Gradient-Website
- Atlassian Design, Elevation: https://atlassian.design/foundations/elevation
- GOV.UK brand, Colour (single colour gradients only over imagery): https://brand.design-system.service.gov.uk/colour/govuk-blue
- Refactoring UI, Building your color palette: https://refactoringui.com/previews/building-your-color-palette
- Nielsen Norman Group, Flat design long exposure: https://www.nngroup.com/articles/flat-design-long-exposure/
- WCAG 2.2, 1.4.3 and 1.4.11 contrast
