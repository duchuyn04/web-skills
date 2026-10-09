"""Regression tests for the build rules.

    py -3.11 tests/run.py                     fixture cases, then build and lint every example
    py -3.11 tests/run.py --sites ../sites    also rebuild every sites/*/page.json (into a temp folder) and lint it
    py -3.11 tests/run.py --qa                also run visual QA on the clean fixture
    py -3.11 tests/run.py -k quote            only the cases whose name contains "quote"

Each case in tests/cases.json starts from tests/fixtures/<base>.page.json, applies its edits and builds the page in
its own temporary sites folder, so no other site can change the result. A case passes when the build succeeds or
fails as "ok" says, every text under "errors" and "warnings" appears in an ERROR or WARN line, and every text under
"html" appears in the built index.html. Run this after any
change to build.py, lint_output.py, rules.py, a schema or an example.
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
PY = sys.executable
for stream in (sys.stdout, sys.stderr):
    stream.reconfigure(encoding="utf-8", errors="replace")


def run(args):
    r = subprocess.run([PY] + [str(a) for a in args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout + r.stderr


def lines(out, kind):
    return [l[len(kind):].strip() for l in out.splitlines() if l.startswith(kind)]


def walk(doc, path):
    """Return (parent, key) for a dotted path such as sections.2.data.logos (numbers index lists)."""
    parts = path.split(".")
    node = doc
    for p in parts[:-1]:
        node = node[int(p)] if isinstance(node, list) else node[p]
    last = parts[-1]
    return node, (int(last) if isinstance(node, list) else last)


def apply(doc, case):
    for path, value in case.get("set", {}).items():
        node, key = walk(doc, path)
        node[key] = value
    for path, (old, new) in case.get("replace", {}).items():
        node, key = walk(doc, path)
        assert old in node[key], "%s: %r not in %r" % (case["name"], old, node[key])
        node[key] = node[key].replace(old, new)
    for path, value in case.get("append", {}).items():
        node, key = walk(doc, path)
        node[key].append(value)
    for path in case.get("delete", []):
        node, key = walk(doc, path)
        del node[key]
    return doc


def check_case(case, tmp):
    base = json.loads((HERE / "fixtures" / (case.get("base", "quayside") + ".page.json")).read_text(encoding="utf-8"))
    sites = tmp / case["name"] / "sites"
    for i in range(case.get("siblings", 0)):
        # an identical sibling site, for the checks that compare a page with the other sites
        d = sites / ("sibling-%d" % i)
        d.mkdir(parents=True)
        (d / "page.json").write_text(json.dumps(base, indent=1), encoding="utf-8")
    page_dir = sites / "site"
    page_dir.mkdir(parents=True)
    for name, text in case.get("files", {}).items():
        (page_dir / name).write_text(text, encoding="utf-8")
    (page_dir / "page.json").write_text(json.dumps(apply(base, case), indent=1), encoding="utf-8")
    out = page_dir / "dist"
    if "prior_report" in case:
        out.mkdir()
        (out / "build-report.json").write_text(json.dumps(case["prior_report"]), encoding="utf-8")
    code, text = run([SKILL / "scripts" / "build.py", page_dir / "page.json", "--out", out])
    errs, warns = lines(text, "ERROR"), lines(text, "WARN")
    problems = []
    if (code == 0) != case["ok"]:
        problems.append("expected the build to %s, it %s" % ("pass" if case["ok"] else "fail", "passed" if code == 0 else "failed"))
    for want in case.get("errors", []):
        if not any(want in e for e in errs):
            problems.append("no ERROR contains %r" % want)
    for want in case.get("warnings", []):
        if not any(want in w for w in warns):
            problems.append("no WARN contains %r" % want)
    for bad in case.get("no_errors", []):
        if any(bad in e for e in errs):
            problems.append("unexpected ERROR containing %r" % bad)
    if code == 0:
        page = (out / "index.html").read_text(encoding="utf-8")
        for want in case.get("html", []):
            if want not in page:
                problems.append("index.html has no %r" % want)
    if case["ok"] and code == 0 and case.get("lint", True):
        lc, ltext = run([SKILL / "scripts" / "lint_output.py", out])
        if lc != 0:
            problems.append("lint failed: " + "; ".join(lines(ltext, "ERROR")[:3]))
    if problems:
        problems += ["  " + l for l in (errs or ["(no ERROR lines)"])[:6]]
    return problems, out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-k", default="", help="only cases whose name contains this text")
    ap.add_argument("--no-examples", action="store_true", help="skip building the examples")
    ap.add_argument("--sites", help="folder with one folder per site; rebuild and lint each page.json")
    ap.add_argument("--qa", action="store_true", help="run qa_screenshot.py on the clean fixture")
    args = ap.parse_args()
    failed = 0
    tmp = Path(tempfile.mkdtemp(prefix="bl-tests-"))
    try:
        cases = [c for c in json.loads((HERE / "cases.json").read_text(encoding="utf-8"))["cases"] if args.k in c["name"]]
        print("Cases (%d)" % len(cases))
        clean_out = None
        for case in cases:
            problems, out = check_case(case, tmp)
            if case["name"] == "clean":
                clean_out = out
            print("  %-4s %-28s %s" % ("ok" if not problems else "FAIL", case["name"], case.get("why", "")))
            for p in problems:
                print("         " + p)
            failed += bool(problems)

        if args.qa and clean_out:
            code, text = run([SKILL / "scripts" / "qa_screenshot.py", clean_out])
            print("QA on the clean fixture: %s" % ("passed" if code == 0 else "FAILED"))
            if code:
                print("\n".join("  " + l for l in text.splitlines() if l.startswith(("FAIL", "  ", "ERROR"))[:12]))
            failed += bool(code)

        if not args.no_examples and not args.k:
            pages = sorted((SKILL / "examples").rglob("*.page.json"))
            print("Examples (%d)" % len(pages))
            for p in pages:
                out = tmp / "examples" / p.relative_to(SKILL / "examples").with_suffix("").as_posix().replace("/", "_")
                code, text = run([SKILL / "scripts" / "build.py", p, "--out", out])
                msg = ""
                if code:
                    msg = "build: " + "; ".join(lines(text, "ERROR")[:2])
                else:
                    lc, ltext = run([SKILL / "scripts" / "lint_output.py", out])
                    if lc:
                        msg = "lint: " + "; ".join(lines(ltext, "ERROR")[:2])
                if msg:
                    print("  FAIL %s  %s" % (p.relative_to(SKILL).as_posix(), msg[:300]))
                failed += bool(msg)
            print("  %d built and linted" % len(pages))

        if args.sites:
            root = Path(args.sites).resolve()
            pages = sorted(root.glob("*/page.json"))
            print("Sites in %s (%d)" % (root, len(pages)))
            for p in pages:
                # build into a temp folder, carrying the last build report so a "rules" pin still applies
                out = tmp / "sites" / p.parent.name
                out.mkdir(parents=True)
                prior = p.parent / "dist" / "build-report.json"
                if prior.is_file():
                    shutil.copyfile(prior, out / "build-report.json")
                code, text = run([SKILL / "scripts" / "build.py", p, "--out", out])
                msg = ""
                if code:
                    msg = "build: " + "; ".join(lines(text, "ERROR")[:2])
                else:
                    lc, ltext = run([SKILL / "scripts" / "lint_output.py", out])
                    if lc:
                        msg = "lint: " + "; ".join(lines(ltext, "ERROR")[:2])
                print("  %-4s %s  %s" % ("FAIL" if msg else "ok", p.parent.name, msg[:300]))
                failed += bool(msg)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\n%s" % ("ALL TESTS PASSED" if not failed else "%d FAILED" % failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
