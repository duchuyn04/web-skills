# Custom section (fallback only)

Use this only when the user needs a block that no variant in `section-catalog.md` can carry, for example a job openings table. Try hard to fit the content into an existing variant first: a custom section is where layout quality can slip.

## 1. Write the spec first

Fill this in and show it to the user before writing code.

```
Name: <kebab-case, for example open-roles>
Purpose: <one sentence: what the visitor learns or does here>
Slot: <after which section it goes>
Content: <fields and item counts, for example 4-8 roles with title, location, type>
Layout desktop: <grid or split, columns, what sits where>
Layout 768px and 390px: <how it stacks>
Interaction: <none, or which existing behavior: reveal, accordion, tabs>
Closest existing variant: <name, and why it does not fit>
```

## 2. Files

Create the folder next to page.json:

```
sections/<name>/schema.json      same format as templates/sections/*/schema.json
sections/<name>/section.html     template
sections/<name>/section.css      optional
```

Reference it in page.json as `{"type": "custom:<name>", "data": {...}}`. Custom sections skip the archetype order check, so place them sensibly.

## 3. Template rules (build.py enforces the starred ones)

- Root element: `<section id="{{section.id}}" class="bl-section bl-tone-{{section.tone}}">` (*).
- Inside: `<div class="bl-container">`, then a heading block copied from `templates/partials/head.html` via `{{> head}}` (needs a `head` field with `{"$ref": "head"}` in the schema).
- Layout only with existing classes where possible: `bl-grid bl-grid-2|3|4`, `bl-split`, `bl-card`, `bl-card--lift`, `bl-checks`, `bl-icon-box`, `bl-btn bl-btn--primary|ghost`, `bl-link`, `bl-chip`.
- CSS must use tokens only: `var(--text-strong)`, `var(--surface)`, `var(--border)`, `var(--accent-ink)`, `var(--c-accent)`, `var(--radius-lg)`, `var(--font-heading)` (*). No hex, rgb or hsl colors (*), no new fonts (*).
- Class names start with `bl-<name>__`.
- Icons with `{{icon:name}}` or `{{icon:$field}}`, arrows with `{{arrow}}`, flags with `{{flag:$field}}`.
- Add `data-reveal` to blocks that should fade in; put `data-reveal-group` on a parent to stagger children.
- Animate only transform and opacity. Add nothing that ignores `prefers-reduced-motion`.

## 4. Verify

Run build, lint and QA like any page, and look at the section at 1440, 768 and 390 px. If it looks weaker than its neighbours, simplify it.
