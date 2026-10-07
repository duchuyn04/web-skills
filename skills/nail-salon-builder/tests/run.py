"""Build every example and test fixture and check the outcome.

    python tests/run.py          build, lint and check expected failures
    python tests/run.py --qa     also run browser QA with --sweep on every site that should build

Expected failures are listed in EXPECT: each fixture must fail and print every listed fragment.
"""
import subprocess
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SKILL = Path(__file__).resolve().parent.parent
OUT = SKILL.parent.parent / "tmp" / "nail-tests"
BUILD = [SKILL / "examples" / "demo-nail.salon.json"] + sorted((SKILL / "examples" / "styles").glob("*.salon.json")) + [SKILL / "tests" / "real-salon.salon.json", SKILL / "tests" / "edge.salon.json", SKILL / "tests" / "bilingual.salon.json"]
EXPECT = {
    "bad-photos.salon.json": ["is a stock picture, not this salon's work", "technician pictures are the owner's photos only", "unknown library photo 'lib:nope-99'"],
    "bad-fonts.salon.json": ["Poppins has no Vietnamese letters", "DM Sans has no Vietnamese letters", "Pacifico: capitals and marks run together"],
    "bad-facts.salon.json": ["150.000 đ is not a price in the brief", "promises \"thuần chay\"", "figures that are not in the brief (4)", "reviews.rating", "$9 is not in the brief", "promises \"miễn phí\""],
}


def run(args):
    r = subprocess.run([sys.executable] + args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout + r.stderr


def main():
    qa = "--qa" in sys.argv
    bad = 0
    for f in BUILD:
        out = OUT / f.name.split(".")[0]
        code, log = run([str(SKILL / "scripts" / "build.py"), str(f), "--out", str(out)])
        ok = code == 0
        if ok:
            code, lint = run([str(SKILL / "scripts" / "lint_output.py"), str(out)])
            ok = code == 0
            log += lint
        if ok and qa:
            code, q = run([str(SKILL / "scripts" / "qa.py"), str(out), "--sweep"])
            ok = code == 0
            log += q
        print(("PASS " if ok else "FAIL ") + f.name, flush=True)
        if not ok:
            bad += 1
            print(log[-3000:])
    for name, frags in EXPECT.items():
        code, log = run([str(SKILL / "scripts" / "build.py"), str(SKILL / "tests" / name), "--out", str(OUT / "expect-fail")])
        missing = [x for x in frags if x not in log]
        ok = code != 0 and not missing
        print(("PASS " if ok else "FAIL ") + name + " (expected to fail)")
        if not ok:
            bad += 1
            print("missing:", missing, "\n", log[-2000:])
    print("ALL PASSED" if not bad else "%d FAILED" % bad)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
