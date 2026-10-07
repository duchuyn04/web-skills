# Rules for app screens

The kit decides colour, shape and spacing. These rules decide the rest: what goes on a screen, what stands
out, and the habits that make a screen read as machine-made. `lint_ui.py` and `qa.py` enforce what they can
(marked **checked**); the rest you check by looking at the screenshots.

## Above every rule: follow real apps, do not invent

A screen looks machine-made when its layout and details were made up. Every part of this kit follows what
most real SaaS apps do (`references/sources.md`). For anything the kit does not cover, look at real screens of
that kind first (Mobbin when the connection is there, else the sources listed for the nearest recipe) and follow
the majority. Do not design a new pattern because it seems nicer.

Old rule dropped: "a status is a word with an icon, never a pill", because most real apps show status as a soft
pill with the word.

## Then: do what users already know

Where most apps do a thing one way (the logo top left goes home, the close button sits top right, Cancel sits
left of the main button, a red `*` marks a required field), do it that way, even when another way looks
cleaner. The taste of this kit only decides what no convention covers.

*Test:* a first-time user, on any part of the screen, has to ask "what does this mean" or "where do I click to…".
If so, the screen breaks a convention there.

## What a machine-made screen looks like, and the rule against each

| Tell | Rule |
|:---|:---|
| Every block is a card in a grid of cards | Rows and tables for records; a card only when it is a container of one thing or is clickable as a whole |
| An icon in a coloured square on every item | Icons stand beside the word they belong to, in the text colour. No icon squares (**checked**: the kit has no class for them and project CSS cannot set colours) |
| Arrows on buttons ("Tiếp tục →") | The label names the action; no arrows (**checked**) |
| Gradients, glows, coloured shadows | Flat surfaces; a shadow only on what floats: menus, dialogs, toasts, the bulk bar, device frames (**checked**: project CSS cannot set one, and `scripts/flat_css.py` checks the project's copy of the kit, see `references/flat-style.md`) |
| A thick coloured stripe down one side of a rounded box (notices, cards, quotes) | A notice is a soft flat fill with its icon in the status colour; no side stripe on any box (**checked** in project CSS) |
| Three solid buttons competing in one view | One primary per view and one per dialog; the rest outline or quiet (**checked** per state) |
| Status shown as a coloured dot alone | A status is a soft pill with its word (`.status`); an icon in it is optional |
| Grey bars standing in for text, fake charts, fake notifications | Real words and real (or realistic sample) figures. A loading state says what is loading |
| Labels and badges repeated on every block ("Mới", "Bản nháp" everywhere) | A label appears where it changes a decision; repeated on every row it is noise |
| Big hero headline with half the words in the accent colour, inside an app | Screen titles are plain: `h1` at 24 px, the accent is for actions and the selected item |
| Stock phrases ("trải nghiệm liền mạch", "giải pháp toàn diện") | Say what happens: "Đơn được giao trong 2 giờ" (**checked**: warning) |
| Emoji in copy, em or en dashes | None (**checked**) |
| Sample data that is all tidy | Edge cases on purpose: a name over two lines, `0`, `1.284.500.000 đ`, a missing phone, an empty list |

## Twelve principles, each with a test

Adapted from the `ui-ux` skill by Tuấn Trần (MIT, see `credits.md`). Where no component spec covers a case,
these decide.

1. **A state change does not move the layout.** Selecting, hovering, loading and errors keep every box where it was. *Test:* hover and click through the screen: does anything jump or resize? (`qa.py` checks hover.)
2. **Every state is drawn, and each is recognisable at a glance.** Empty, loading, error, one item, many items, no permission. *Test:* open each `?state=`: can you tell which one it is in a second?
3. **One signal per idea; the strongest signal is spent once.** The accent fill, bold red, a big number: one place each per view. *Test:* squint: is there exactly one thing that shouts?
4. **Colour carries status by one table for the whole app, always with a word.** Done is green everywhere, waiting is amber everywhere. *Test:* the same status in two places has the same colour and word.
5. **Same role, same shape and same class.** Two badges for one meaning are two apps glued together. *Test:* find two things that do the same job: do they look the same?
6. **Copy says what happened, why, and what to do next.** "Chưa gửi được vì mất mạng. Thử lại khi có mạng." *Test:* every error and empty state answers those three.
7. **Do not act or guess for the user.** No auto-advance after a click, no silent defaults that cost money. *Test:* did anything happen that the user did not ask for?
8. **Never hide or cut what the user needs to decide.** Prices, names and the main figure stay whole at 375 px. *Test:* the longest name and the biggest number, on a phone.
9. **Everything works by mouse, keyboard and finger.** Tab reaches every control, targets are 24 px or more on phones. *Test:* Tab through the screen; tap it on a phone width.
10. **The kit draws, the project decides.** Handlers stay empty (`ui:` events) for the project to wire: where data comes from, what save does.
11. **No negative space tricks.** No negative margins or absolute nudges to make something line up; fix the layout instead.
12. **Text in a block has an order and a rhythm, and names are not cut.** Title, then meta, then the action; truncate descriptions, never names.

## Look at the screenshots: five questions a script cannot answer

After `qa.py` passes, open the 375 px shot and one desktop shot of each page and look at the edge cases:

1. **Does each edge case look intended?** A count of `0` reads "Chưa có" or disappears; a missing photo is a clear "no photo" state; a missing description closes up instead of leaving a gap.
2. **Is any space there only to hold a place?** Keep it only when it lines up what matters (prices across cards) and say so in the report.
3. **Do the copies of a repeated block read the same way?** Same unit and number format down a list, same order of lines, same labels.
4. **Is one area carrying too much?** More than three things stacked on a header, a photo or a corner: move some out.
5. **Is what decides still whole in the longest case?** Longest name, biggest price, at 375 px.

## Adding a rule

Rules added to cure one symptom tend to cause another on the next build. When a rule, a check or a recipe
change is added:

- at most five new rules per change, each with the case it applies to, never "always"
- say which rule it replaces or contradicts; when it reverses an old rule, leave a line "Old rule dropped: <rule>, because <reason>" so it is not brought back
- one rule lives in one file; SKILL.md points to it instead of copying it
- a rule that catches nothing in three rounds of building comes out
- after adding a rule, check the recipes and the gallery against it: they are copied as they are, so a mistake in them spreads to every project
- write the rule and its reason, not its history: no dates or client names here; those go in the commit message
