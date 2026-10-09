# Maintaining bpo-landing-builder

## Adding a rule

Rules added to cure one symptom tend to cause another on the next build. When a check, a SKILL.md rule or a reference rule is added:

- at most five new rules per change, each with the case it applies to ("on a demo shop", "in the hero"), never "always"
- say which rule it replaces or contradicts; when it reverses an old rule, leave a line "Old rule dropped: <rule>, because <reason>" so it is not brought back
- one rule lives in one file; SKILL.md points to it instead of copying it
- a rule that catches nothing in three rounds of building comes out
- after adding a rule, check the templates and examples against it: they are copied as they are, so a mistake in them spreads to every site
- write the rule and its reason, not its history: no dates or client names in the skill; those go in the commit message and `CHANGELOG.md`

## Maintaining the library

Run the regression tests after any change to `build.py`, `lint_output.py`, `rules.py`, a schema or an example:

```
python SKILL/tests/run.py --qa --sites sites
```

It builds the clean fixture `tests/fixtures/quayside.page.json` and each must-fail case in `tests/cases.json` (invented logos, extended quotes, figures and claims missing from the brief, copied example text, emoji, dashes, arrows, banned words, expressive motion without a request, the rules pin), then builds and lints every example and every site in `sites/` without touching their `dist/`. It must print `ALL TESTS PASSED`. A rule that the build learns from a new failure gets a case in `tests/cases.json`.

When a new check can fail a page that built before, raise `RULES_VERSION` in `build.py` and the version at the top of this file, and add an entry to `CHANGELOG.md`. A site built under an older version keeps building with `"rules": "<that version>"` ("1" to "5") in its page.json. For example, a site built under rules 1 keeps building with `"rules": "1"`: build.py then prints the content checks added in rules 2 as warnings and lint does the same for the design checks, while the schema, copy (AGENTS.md) and accessibility checks stay errors. build.py accepts the pin only when the site's output folder holds a build made under rules 1, so a new page cannot use it. Never add `"rules"` to a new page.

After changing a template's CSS, run `python tools/check_flat_css.py` from the plugin repository: it holds every library stylesheet to `references/flat-style.md` with no finding allowed, and fails when `scripts/flat_css.py` or `references/flat-style.md` differs between skills (change all four copies together). After changing a template or schema, rebuild every page in `examples/` and `examples/variations/`, run lint and QA on each, then run `python SKILL/scripts/make_catalog.py` to regenerate the catalog, anatomy and animation map (add `--previews <dist> ...` to refresh preview images).

New variants widen the library only if agents can reach them: add each one to the matching slots in `templates/archetypes.json`, give every new animation id a timing line in `TIMING` in `make_catalog.py`, and put the variant in at least one page under `examples/variations/` so it is built and checked with the rest. Motion runs on vendored GSAP (`templates/vendor/gsap.js`, loaded on every page before `base.js`) and 3D on vendored Three.js (`templates/sections/_shared/three.js`, loaded only by sections that draw a WebGL scene); `references/motion-libraries.md` covers both, the `BL.motion` and `BLGL` helpers and how to update the vendored files. Canvas and WebGL motion share one render loop and one pause state in `templates/sections/_shared/ribbons.js` (`window.BLRibbons`); new 3D goes in a `BLGL.register` scene, never a second loop. Any new moving section follows "Motion and performance" in `references/custom-section-spec.md` and must pass the QA frame-rate check at 2x. `qa_screenshot.py` adds the class `bl-shot` to the page before element screenshots, so scroll-linked layouts can lay out flat for previews.
