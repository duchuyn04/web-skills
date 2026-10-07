# Fonts

Every font the build accepts is in `data/fonts.json`: it has Vietnamese letters on Google Fonts and its stacked marks (ầ ẫ ậ ể ỗ ữ) were rendered and measured. `python scripts/build.py --list` prints them by role. The study behind it (render sheets and measurements) is `research/fonts/` in the job repository, not shipped with this skill.

## Choosing

- Each style has a tested pair in `data/presets.json`. Change it only when the brief names a font or the brand clearly needs another voice.
- `theme.font_head`: headings. `theme.font_body`: everything else. `theme.font_accent`: optional script font, used only for the short line above the hero title.
- The build refuses fonts without Vietnamese (Poppins, DM Sans, Jost, Outfit, Lato, Libre Baskerville, Italiana, Cinzel, Marcellus, Bodoni Moda, Caveat, Sacramento and others in `no_vietnamese`) and fonts whose marks break or collide (`avoid`: Ephesis, Pacifico, Bad Script, Lemonada, Playpen Sans, Shantell Sans, Coiny, Paytone One). Close substitutes: Poppins to Montserrat or Be Vietnam Pro; DM Sans, Jost, Outfit to Manrope, Plus Jakarta Sans or Lexend; Libre Baskerville to Lora; Italiana, Cinzel, Marcellus to Cormorant Garamond; Bodoni Moda to Playfair Display or Libre Bodoni; Caveat, Sacramento to Dancing Script, Birthstone or Allura.
- Script fonts marked `lowercase_only` (Great Vibes, Alex Brush, Pinyon Script and others) read badly in capitals with stacked marks: keep the accent line in sentence case.

## What the build does

- Heading line-height comes from the font (`lh_mixed`): Cormorant 1,15, Playfair Display 1,25, Prata 1,3, Bricolage Grotesque 1,35. At 1,2 Prata's marks touch the line above.
- The Google Fonts link asks only for weights the family has. A weight it lacks makes css2 drop the family without an error.
- Korean, Japanese, Chinese and Thai words in the content (bilingual menus for tourists) are wrapped in `<span lang>` and get their national font (Noto Sans KR, JP, SC or TC, Thai, then system fonts). A single shared fallback list would draw Japanese and Chinese with Korean glyphs. Only the letters the site uses are downloaded (`&text=`). Chinese characters without kana are read as `theme.han` (default `zh`).
