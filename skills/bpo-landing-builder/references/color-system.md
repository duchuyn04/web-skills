# Color system

How build.py turns a preset and the client's brand colors into CSS tokens, and what QA checks on the finished page. The research behind every rule, with sources (WCAG 2.2, CSS Color 4, Material Design 3, Radix Colors, Tailwind, Carbon, Atlassian, Apple HIG), is in `docs/research/ui-color-system.md` in the job repository.

You do not pick shades yourself. Give the client's colors in `theme` (see `style-presets.md`), build, read the `theme.*` warnings, and fix what QA reports.

## Tokens

| Token | Use | Rule |
|:---|:---|:---|
| `--c-accent` | Button fills, active states, key marks | White label at 4.5:1. A brighter brand is darkened at the same OKLCH hue until it passes. |
| `--c-on-accent` | Text on `--c-accent` | White, or a dark tint of the accent hue for very light accents (OKLCH L 0.80 or more). |
| `--c-accent-2` | Decorative second color | Within 60 degrees of the accent hue unless the client supplied it. |
| `--c-accent-blend` | Second flat tone for small decorative marks (daylight bands, beacons, map rings) | `accent_2` when it is within 90 degrees of the accent, otherwise a light tint of the accent. |
| `--c-accent-blend-deep` | A deeper blend tone that still carries on-accent text | `--c-accent-blend` darkened until the on-accent text still reaches 4.5:1 over it. |
| `--c-accent-on-dark` | Accent text or marks on a `--c-primary` block inside a light section | 4.5:1 on the primary color. |
| `--c-primary` | Dark sections, footer, heading text on light tones | The preset's, the client's, or a dark tint of a warm accent's hue. |
| `--text`, `--text-muted`, `--text-strong` | Body, secondary and heading text per tone | 4.5:1 on the tone's `bg`, `surface` and `surface-2`. |
| `--accent-ink` | Links, eyebrows, chips, numbers in accent color | 4.5:1 on `bg`, `surface`, `surface-2` and on the accent-tinted chip ground over each of them. |
| `--border-input` | Borders of inputs, selects, option cards | 3:1 on `bg` and `surface` (WCAG 1.4.11). Decorative borders use `--border` and `--border-strong` and may stay faint. |
| `--focus-ring` | Focus outlines | 3:1 on `bg` and `surface`. |

All shade changes move OKLCH lightness at a fixed hue (chroma only drops when the color would leave sRGB), so a brand never slides toward brown or grey the way an sRGB mix toward black does.

## Build-time rules (build.py)

1. Contrast uses the WCAG 2 relative luminance (sRGB threshold 0.04045) and the ratio is never rounded before comparing (4.499:1 fails 4.5).
2. Button labels reach 4.5:1. The accent is darkened at constant hue for white labels; a dark label is used only for accents with OKLCH L 0.80 or more.
3. A darkened accent keeps its hue within 5 degrees; build.py warns when it loses more than 0.20 of lightness.
4. When the accent was darkened and the client gave no `accent_2`, the original brand color becomes `accent_2`, so the bright color still appears in small decorative marks.
5. Accent text (`--accent-ink`) passes 4.5:1 on every ground of its tone, including tinted chips.
6. Text tokens pass 4.5:1 on `bg`, `surface` and `surface-2`.
7. Input borders pass 3:1; focus rings pass 3:1.
8. A preset `accent_2` more than 60 degrees from the accent hue is replaced by an analogous one (accent hue plus 25 degrees, a little lighter). A client's own second color is kept.
9. When accent and `accent_2` are more than 90 degrees apart, `--c-accent-blend` never mixes them: complementary hues average to grey or olive in every interpolation space.
10. Color mixes between two brand colors interpolate `in oklab`.
11. Gradients follow the section "Gradients" below; lint_output.py enforces it.
12. Neutrals (backgrounds, surfaces, gray text) with visible chroma are moved to the accent hue and capped at chroma 0.012-0.015 for surfaces and 0.02 for text. A warm brand gets warm grays, a blue brand cool grays.
13. A warm accent (hue 20-100) set in `theme` without `primary` gets a brand-tinted dark `primary` (OKLCH L 0.24) instead of the preset's navy. A light, colored `primary` given without an `accent` is the logo color in the wrong key and becomes the accent; any other `primary` lighter than OKLCH L 0.40 is darkened to L 0.24 at the same hue.
15. The accent comes from the client. With `site.logo` set, build.py (`check_brand_colors`, `scripts/logo_colors.py`) reads the logo's chromatic colours and fails a `theme.accent` more than 25 degrees of OKLCH hue from all of them, and a coloured logo with no `theme.accent`. Framework default colours (Bootstrap and Tailwind palette values) fail in any `theme` key unless the brief or logo contains them: they are what a model picks when it has no brand colour, and a Bootstrap danger red on navy is a typical generated look.
14. Pass or fail uses the WCAG 2 ratio only. APCA is not normative yet, and CSS `contrast-color()` is not used for button text.

## Gradients

Surfaces are flat. A gradient is allowed only when it does a job a flat color cannot:

- a scrim over a photo or video so the text on it stays readable (hero-fullbleed, banner-image, video-block, country-cards, industries-slats)
- an edge fade: a mask that fades a marquee, carousel or canvas into the section background
- a shadow or the shading of a 3D object in one hue (a book gutter, a fold crease, a sphere, a floor shadow)
- a hard-stop pattern: grid lines, dot grids, split fills, range tracks

Never use gradient text, glow blobs (blurred color circles), color-to-color backgrounds on sections, cards, panels or buttons, light sweeps on buttons, or hover spotlights and glare. The `highlight: gradient` preset value is kept for old pages and renders like `color`.

lint_output.py fails the page when a soft gradient mixes two color families (accent, second accent, primary or a raw colored value), when a soft gradient fades the accent or second accent out (a glow), when gradient text is used (`background-clip: text`), and when an element is blurred by 24px or more (a glow blob). Neutral fades (transparent, black, white, background and surface tokens), shading in the primary color and hard-stop patterns pass.

## Render-time checks (qa_screenshot.py)

- Every visible text run against the color really behind it: 4.5:1, or 3:1 for large text (24px, or 18.66px at weight 700). Text over photos, canvases, gradients and positioned fills is skipped and left to the screenshots.
- Every Tab stop shows a solid outline of 2px or more at 3:1 against its background.
- Links inside running text are underlined, or differ from the text around them by 3:1.
- `--cvd` saves deuteranopia, protanopia and achromatopsia screenshots (`qa/cvd-*.png`). Look at them: nothing may be told apart by color alone.

When QA reports low contrast in a library section, fix the token or the template (never the page copy) and rebuild every example.

## Guidance for page authors

- One accent hue family per page. Red, amber and green stay for status (errors, warnings, success), never decoration.
- The accent is for emphasis: buttons, active states, a few marks. Neutrals carry the page. At most one section is painted in the brand color (`hero-gradient`, `hero-ribbons`, `ticker-band`).
- "60-30-10" has no primary source in any major design system; do not cite it. What the systems agree on is the rule above: neutral surfaces, one accent for action and emphasis.
- Do not use the accent for plain text that is not a link, when the same color marks links and buttons.
- Decorative card and divider borders may stay faint; input borders may not.
- Thin or light font weights need more than 4.5:1; the presets use 400 or heavier for body text for that reason.
- Status and comparison marks carry text, an icon or a shape as well as color.
