"""Start a prototype from the kit: copy it, theme it, copy the chosen screen recipes, write a screen index.

    python scripts/new.py --list
    python scripts/new.py <out> --name "Webnhanh" --mark W --accent "#1f4aa8" --screens list,wizard,review,dashboard
    python scripts/new.py <out> --screens table:orders,table:customers      (name:file copies one recipe twice)

<out>/kit/ gets tokens.css (from --accent, see theme.py), app.css, app.js and icons.js. Each recipe becomes
<out>/<file>.html with links to kit/ and the product name and logo letter swapped in. Everything else in the
recipe (copy, sample rows, states) is a starting point to rewrite for the product. <out>/screens.html lists
every page and state so the user can click through, and protonav.py adds the "View prototype" button to every
page (kit/proto-nav.js). Existing files are left alone unless --force.
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(HERE))
import theme  # noqa: E402
import protonav  # noqa: E402

HEADER = re.compile(r"<!-- recipe: ([\w-]+) \| (.*?) \| states: (.*?) \| use for: (.*?) -->")


def recipes():
    out = {}
    for f in sorted((SKILL / "recipes").glob("*.html")):
        m = HEADER.search(f.read_text(encoding="utf-8"))
        if m:
            out[m.group(1)] = {"file": f, "what": m.group(2), "states": m.group(3).split(), "use": m.group(4)}
    return out


def screens_page(name, mark, pages):
    rows = []
    for file, rec, states in pages:
        links = " ".join('<a class="btn sm" href="%s?state=%s">%s</a>' % (file, s, s) for s in states)
        rows.append('<li class="list-item no-thumb"><div><a class="item-title" href="%s">%s</a><div class="item-meta">%s</div></div>'
                    '<div class="row wrap tight">%s</div><div></div></li>' % (file, file, rec["what"], links))
    return """<!doctype html>
<!-- screens index written by new.py: every page and state of this prototype -->
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Các màn hình · %(name)s</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="kit/tokens.css">
<link rel="stylesheet" href="kit/app.css">
</head>
<body data-states="default">
<header class="topbar"><a class="logo" href="screens.html"><span class="logo-mark" aria-hidden="true">%(mark)s</span><span class="logo-name">%(name)s</span></a></header>
<main class="page">
  <div class="page-head"><div><h1>Các màn hình của bản mẫu</h1><p class="sub">Bấm tên màn để mở, bấm một trạng thái để xem màn đó ở trạng thái ấy.</p></div></div>
  <ul class="list">
%(rows)s
  </ul>
</main>
<script src="kit/icons.js"></script>
<script src="kit/app.js"></script>
</body>
</html>
""" % {"name": name, "mark": mark, "rows": "\n".join("    " + r for r in rows)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out", nargs="?")
    ap.add_argument("--list", action="store_true", help="print the recipes with their states")
    ap.add_argument("--name", default="Lumen", help="product name shown in the logo and titles")
    ap.add_argument("--mark", help="logo letter (default: first letter of --name)")
    ap.add_argument("--accent", default=theme.DEFAULT_ACCENT, help="brand colour, 6-digit hex")
    ap.add_argument("--primary", choices=("brand", "ink"), default="brand", help="main button colour (theme.py)")
    ap.add_argument("--screens", help="comma list of recipes, or recipe:file to choose the file name")
    ap.add_argument("--force", action="store_true", help="overwrite files that exist")
    a = ap.parse_args()
    all_recipes = recipes()
    if a.list or not a.out:
        for k, r in all_recipes.items():
            print("%-10s %s\n           states: %s\n           use for: %s" % (k, r["what"], " ".join(r["states"]), r["use"]))
        return
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", a.accent):
        sys.exit("--accent takes a 6-digit hex colour such as #1f4aa8")
    mark = (a.mark or a.name[:1]).upper()
    out = Path(a.out).resolve()
    (out / "kit").mkdir(parents=True, exist_ok=True)

    t = theme.tokens(a.accent.lower(), a.primary)
    tokens = out / "kit" / "tokens.css"
    if tokens.exists() and not a.force:
        print("keep  kit/tokens.css (exists; --force to rewrite it)")
    else:
        tokens.write_text(theme.TEMPLATE.format(source=a.accent.lower(), **t), encoding="utf-8")
        print("write kit/tokens.css (accent %s)" % t["accent"])
    for k in ("app.css", "app.js", "icons.js"):
        shutil.copyfile(SKILL / "kit" / k, out / "kit" / k)
    shutil.copytree(SKILL / "kit" / "img", out / "kit" / "img", dirs_exist_ok=True)
    print("copy  kit/app.css, kit/app.js, kit/icons.js, kit/img/")

    wanted = [s.strip() for s in (a.screens or ",".join(all_recipes)).split(",") if s.strip()]
    pages = []
    for item in wanted:
        rec_name, _, file = item.partition(":")
        if rec_name not in all_recipes:
            sys.exit("unknown recipe '%s'. Known: %s" % (rec_name, ", ".join(all_recipes)))
        rec = all_recipes[rec_name]
        file = (file or rec_name) + ("" if (file or rec_name).endswith(".html") else ".html")
        dest = out / file
        # a page already rewritten for the product lists its own states; the index follows the page
        own = re.search(r'data-states="([^"]+)"', dest.read_text(encoding="utf-8")) if dest.exists() else None
        pages.append((file, rec, own.group(1).split() if own and not a.force else rec["states"]))
        if dest.exists() and not a.force:
            print("keep  %s (exists)" % file)
            continue
        html = rec["file"].read_text(encoding="utf-8")
        html = html.replace('href="../kit/', 'href="kit/').replace('src="../kit/', 'src="kit/')
        html = html.replace("<!-- recipe: ", "<!-- from recipe: ", 1)
        html = html.replace('<span class="logo-name">Lumen</span>', '<span class="logo-name">%s</span>' % a.name)
        html = html.replace('<span class="logo-mark" aria-hidden="true">L</span>', '<span class="logo-mark" aria-hidden="true">%s</span>' % mark)
        html = re.sub(r"(<title>[^<]*?)Lumen(</title>)", r"\g<1>%s\2" % a.name.replace("\\", ""), html)
        dest.write_text(html, encoding="utf-8")
        print("write %s (from %s, states: %s)" % (file, rec_name, " ".join(rec["states"])))
        # sample pictures the recipe shows; replace them with the product's own
        for img in sorted(set(re.findall(r'src="(img/[^"]+)"', html))):
            src, to = SKILL / "recipes" / img, out / img
            if src.is_file() and (not to.exists() or a.force):
                to.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, to)
                print("copy  %s (sample picture)" % img)
    (out / "screens.html").write_text(screens_page(a.name, mark, pages), encoding="utf-8")
    print("write screens.html")
    protonav.build(out)
    print("\nNext: rewrite each page for the product (copy, columns, sample rows, states), keep to kit classes, then\n"
          "  python %s %s\n  python %s %s --sweep" % (HERE / "lint_ui.py", out, HERE / "qa.py", out))


if __name__ == "__main__":
    main()
