"""Keep every skill's stylesheets flat (references/flat-style.md in each skill).

    python tools/check_flat_css.py

1. Every skill ships the same scripts/flat_css.py and references/flat-style.md; a copy that drifts fails.
2. The flat_css self-test runs.
3. Each skill's own CSS (templates, kit) is checked with it, using the colour families its lint script declares. Library CSS is held to every finding, warnings included:
   a page built from the library should never print one.
4. Each skill's lint_output.py reports gradient text, a glow and shadows on a built page.
"""
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"

# The stylesheets of each skill's library, and the lint script whose FLAT_FAMILIES (the colour families of that skill's
# tokens) the check uses, so the families are written once, next to the lint that reports them.
CONFIG = {
    "bpo-landing-builder": {
        "css": ["templates/base.css", "templates/sections/**/*.css"], "lint": "scripts/lint_output.py",
        # build.py writes this token into the page; the value is its light-theme one
        "tokens": {"--shadow-lg": "0 24px 48px -24px rgba(15, 23, 42, 0.24)"},
    },
    "ecommerce-builder": {"css": ["templates/assets/css/**/*.css"], "lint": "scripts/lint_output.py"},
    "nail-salon-builder": {"css": ["templates/assets/css/**/*.css"], "lint": "scripts/lint_output.py"},
    "app-ui": {"css": ["kit/tokens.css", "kit/app.css"], "lint": "scripts/lint_ui.py"},
}
SHARED_FILES = ["scripts/flat_css.py", "references/flat-style.md"]


def load(path, name):
    """Import a skill script on its own: its folder first on sys.path and its sibling modules (rules, flat_css) fresh."""
    for mod in ("rules", "flat_css"):
        sys.modules.pop(mod, None)
    sys.path.insert(0, str(path.parent))
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        sys.path.pop(0)
    return mod


SLOP_CSS = """.title{background:linear-gradient(90deg,#7c3aed,#ec4899);-webkit-background-clip:text;color:transparent}
.card{box-shadow:0 20px 40px rgba(0,0,0,.2)}
.card:hover{transform:translateY(-4px);box-shadow:0 30px 60px rgba(0,0,0,.25)}
.glow{box-shadow:0 10px 40px #7c3aed}
"""
# what each skill's lint_output.py must print for SLOP_CSS (bpo reports gradient text under its older "gradient" code)
SLOP_EXPECT = {
    "bpo-landing-builder": ["[gradient] gradient text", "[glow]", "[resting-shadow]", "[hover-shadow]", "[hover-lift]"],
    "ecommerce-builder": ["gradient-text", "glow", "resting-shadow", "hover-shadow", "hover-lift"],
    "nail-salon-builder": ["gradient-text", "glow", "resting-shadow", "hover-shadow", "hover-lift"],
}


def run_lint(script, folder):
    r = subprocess.run([sys.executable, str(script), str(folder)], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    return r.returncode, r.stdout + r.stderr


def lint_catches_slop():
    """Each skill's lint runs the flat checks: on a built page's stylesheets, and in app-ui on the project's kit copy."""
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        dist = Path(tmp)
        (dist / "assets" / "css").mkdir(parents=True)
        (dist / "index.html").write_text('<!doctype html><html lang="en"><head><title>t</title></head><body><h1>t</h1></body></html>', encoding="utf-8")
        (dist / "assets" / "css" / "custom.css").write_text(SLOP_CSS, encoding="utf-8")
        for skill, wants in SLOP_EXPECT.items():
            code, out = run_lint(SKILLS / skill / "scripts" / "lint_output.py", dist)
            if code == 0:
                problems.append("%s lint_output.py passed a page with gradient text and a glow" % skill)
            for w in wants:
                if w not in out:
                    problems.append("%s lint_output.py did not report %s" % (skill, w))
    with tempfile.TemporaryDirectory() as tmp:
        proj = Path(tmp)
        app = SKILLS / "app-ui"
        shutil.copytree(app / "kit", proj / "kit")
        shutil.copytree(app / "recipes", proj / "screens")
        with open(proj / "kit" / "app.css", "a", encoding="utf-8") as f:
            f.write("\n" + SLOP_CSS)
        code, out = run_lint(app / "scripts" / "lint_ui.py", proj)
        if code == 0:
            problems.append("app-ui lint_ui.py passed a kit copy with gradient text and a glow")
        for w in SLOP_EXPECT["nail-salon-builder"]:
            if w not in out:
                problems.append("app-ui lint_ui.py did not report %s in kit/app.css" % w)
    return problems


def main():
    problems = []
    base = SKILLS / "bpo-landing-builder"
    for rel in SHARED_FILES:
        text = (base / rel).read_text(encoding="utf-8")
        for skill in CONFIG:
            other = SKILLS / skill / rel
            if not other.is_file():
                problems.append("%s has no %s" % (skill, rel))
            elif other.read_text(encoding="utf-8") != text:
                problems.append("skills/%s/%s differs from the bpo-landing-builder copy; copy the change to every skill" % (skill, rel))
    flat = load(base / "scripts" / "flat_css.py", "flat_css_shared")
    problems += ["self-test: " + b for b in flat._self_test()]

    checked = 0
    for skill, cfg in CONFIG.items():
        folder = SKILLS / skill
        files = sorted({f for pat in cfg["css"] for f in folder.glob(pat)})
        fams = load(folder / cfg["lint"], "lint_" + skill.replace("-", "_")).FLAT_FAMILIES
        tokens = dict(cfg.get("tokens", {}))
        for f in files:
            tokens.update(flat.tokens_in(f.read_text(encoding="utf-8")))
        for f in files:
            checked += 1
            for fd in flat.check(f.read_text(encoding="utf-8"), fams, tokens):
                problems.append("%s %s: %s %s" % (f.relative_to(ROOT).as_posix(), fd.selector, fd.code, fd.message))
    problems += lint_catches_slop()
    for p in problems:
        print("FAIL " + p)
    if problems:
        print("\nFLAT CSS FAILED: %d problem(s)." % len(problems))
        return 1
    print("FLAT CSS OK: %d stylesheet(s) in %s; flat_css.py and flat-style.md identical in each" % (checked, ", ".join(CONFIG)))
    return 0


if __name__ == "__main__":
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
