# Credits and sources

## Where the kit comes from

- **Real SaaS screens on Mobbin**: the look of the kit and the layout of every recipe follow the majority of the
  screens listed in `sources.md`. They are references only; nothing was copied from them.
- **Webnhanh prototype**: the first draft of the components and of the wizard and preview flows. Its look was not
  approved; every visual choice taken from it was checked against the real screens and changed where they differ.
- **ecommerce-builder admin** in this repository: the sidebar with groups and counts, status tabs, bulk actions,
  undo toasts, the order detail with steps and timeline, settings with a save bar. Its colours were written as
  literal hex values; in this kit every colour is a token.

## Ideas adapted from the ui-ux skill

The brief gate (five lines and a table of what each screen is for), the twelve principles with a test each, the
five questions to ask of a screenshot, drawing every state as a static example, the edge-case sample data, and
the rules for adding rules are adapted from the `ui-ux` skill of evondevKit (https://github.com/evondev/evondevKit),
used under the MIT License:

> Copyright (c) 2026 Tuấn Trần
>
> Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
> documentation files (the "Software"), to deal in the Software without restriction, including without limitation
> the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
> to permit persons to whom the Software is furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in all copies or substantial portions
> of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
> THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
> CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
> DEALINGS IN THE SOFTWARE.

No code or files were copied from it; the wording here is this skill's own. Choices of that skill that this kit
does not follow: it removes focus rings by default (this kit keeps a visible focus outline, WCAG 2.4.7) and
writes for React and Tailwind (this kit writes plain HTML, CSS and JavaScript).

## Icons

Lucide (https://lucide.dev), ISC License, Copyright (c) for portions of Lucide are held by Cole Bemis 2013-2022
as part of Feather (MIT); all other copyright for Lucide is held by Lucide Contributors 2022. The paths are in
`data/icons.json` and `kit/icons.js`.

## Font

Be Vietnam Pro, SIL Open Font License 1.1, loaded from Google Fonts.
