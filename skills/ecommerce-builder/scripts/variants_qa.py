"""Test every variant, not only the ones the style examples happen to use.

    python scripts/variants_qa.py                     one build per layout variant on the retail example, light preset
    python scripts/variants_qa.py --parts cart,checkout
    python scripts/variants_qa.py --dark              round-robin builds under the dark preset, every variant used at least once
    python scripts/variants_qa.py --coverage          every variant and section variant appears in at least one example
    python scripts/variants_qa.py --no-browser        build and lint only (fast)

Each build runs lint_output.py and qa.py --quick (a sample of pages plus the whole buying flow). Run it with py -3.11 where
Playwright is installed. Exit code 1 when anything fails.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(HERE))
import variants as V  # noqa: E402

BASE = SKILL / "examples" / "demo-electronics.shop.json"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout + r.stderr)


def build_one(tmp, name, layout, preset=None, browser=True):
    shop = json.loads(BASE.read_text(encoding="utf-8"))
    shop["layout"] = layout
    if preset:
        shop["theme"] = {"preset": preset}
    d = Path(tmp) / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "shop.json").write_text(json.dumps(shop, ensure_ascii=False), encoding="utf-8")
    out = d / "dist"
    code, text = run([sys.executable, str(HERE / "build.py"), str(d / "shop.json"), "--out", str(out)])
    if code:
        return ["build failed: " + "; ".join(l for l in text.splitlines() if l.startswith("ERROR"))[:600]]
    code, text = run([sys.executable, str(HERE / "lint_output.py"), str(out)])
    if code:
        return ["lint failed: " + "; ".join(l for l in text.splitlines() if l.startswith("ERROR"))[:400]]
    if browser:
        code, text = run([sys.executable, str(HERE / "qa.py"), str(out), "--quick"])
        if code:
            return ["qa failed: " + "; ".join(l for l in text.splitlines() if l.startswith("FAIL"))[:600]]
    return []


def coverage():
    used = {part: set() for part in V.PART_DIRS}
    sect = {}
    styles = json.loads((V.DATA / "styles.json").read_text(encoding="utf-8"))
    styles.pop("_variants", None)
    files = [BASE] + sorted((SKILL / "examples").rglob("*.shop.json"))
    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        st = styles.get(d.get("style", "retail"), {})
        for part in V.PART_DIRS:
            used[part].add((d.get("layout") or {}).get(part) or st.get(part) or V.PART_DEFAULT.get(part))
        for sec in d.get("home", []):
            sect.setdefault(sec["type"], set()).add(sec.get("variant") or "")
            if sec["type"] == "hero":
                used["hero"].add(sec.get("variant") or "")
    missing = []
    for part in V.PART_DIRS:
        for v in V.variants(part):
            if v not in used[part]:
                missing.append("%s variant '%s' is not used by any example" % (part, v))
    for t in V.section_types():
        if t == "hero":
            continue
        if t not in sect:
            missing.append("section '%s' is not used by any example" % t)
        for v in V.section_variants(t):
            if v not in sect.get(t, set()):
                missing.append("section '%s' variant '%s' is not used by any example" % (t, v))
    return missing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts", help="comma list of parts to test (default: all)")
    ap.add_argument("--dark", action="store_true")
    ap.add_argument("--coverage", action="store_true")
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args()
    fails = []
    if a.coverage:
        miss = coverage()
        for m in miss:
            print("FAIL " + m)
        print("COVERAGE %s: %d variant(s) without an example" % ("FAILED" if miss else "PASSED", len(miss)))
        sys.exit(1 if miss else 0)
    parts = a.parts.split(",") if a.parts else list(V.PART_DIRS)
    # the stock layout of the base example, to override one part at a time
    base_layout = {"header": "bar", "hero": "sidebar", "card": "dense", "pdp": "retail", "plp": "sidebar", "footer": "full", **V.PART_DEFAULT}
    with tempfile.TemporaryDirectory() as tmp:
        if a.dark:
            n = max(len(V.variants(p)) for p in parts)
            for i in range(n):
                layout = {p: V.variants(p)[i % len(V.variants(p))] for p in parts}
                label = "dark-%d" % i
                errs = build_one(tmp, label, layout, "gaming-dark", not a.no_browser)
                print(("FAIL " if errs else "OK   ") + label + " " + json.dumps(layout))
                fails += ["%s: %s" % (label, e) for e in errs]
        else:
            for p in parts:
                for v in V.variants(p):
                    layout = dict(base_layout)
                    layout[p] = v
                    label = "%s-%s" % (p, v)
                    errs = build_one(tmp, label, layout, None, not a.no_browser)
                    print(("FAIL " if errs else "OK   ") + label)
                    fails += ["%s: %s" % (label, e) for e in errs]
    for f in fails:
        print("  " + f)
    print("VARIANT QA %s: %d failure(s)" % ("FAILED" if fails else "PASSED", len(fails)))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
