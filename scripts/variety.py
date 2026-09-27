#!/usr/bin/env python3
"""Keep generated pages from looking alike. Python standard library only.

Usage:
    python variety.py --archetype it-bpo-partner        least-used variant first, for every slot
    python variety.py --check sites/acme/page.json      compare one page with every other page
    python variety.py --report                          usage of every variant and preset

Pages are found under --sites (default: ./sites). Examples in the skill folder are ignored.
A page's look is its preset plus the variant chosen for each slot. Two pages whose looks
share 70% or more of those choices read as the same template, and build.py warns about it.
"""
import argparse
import json
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
TPL = SKILL / "templates"
LIMIT = 0.7
# Slots that decide how a page looks at first glance count double.
HEAVY = {"hero": 2, "services": 2}


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def archetypes():
    return {k: v for k, v in load_json(TPL / "archetypes.json").items() if not k.startswith("_")}


def look(page, arch):
    """Return {slot: variant} for a page, plus the preset under the key 'preset'."""
    slots = arch.get(page.get("archetype"), {}).get("slots", [])
    out = {"preset": page.get("preset", "")}
    for sec in page.get("sections", []):
        t = sec.get("type", "")
        if t.startswith("custom:"):
            out["custom:" + t[7:]] = t
            continue
        for s in slots:
            if t in s["variants"] and s["slot"] not in out:
                out[s["slot"]] = t
                break
    return out


def similarity(a, b):
    keys = [k for k in a if k in b and k not in ("floating", "exit", "header", "footer")]
    if not keys:
        return 0.0, []
    total = same = 0
    shared = []
    for k in keys:
        w = HEAVY.get(k, 1)
        total += w
        if a[k] == b[k]:
            same += w
            shared.append(k)
    return same / total, shared


def find_pages(sites, skip=None):
    root = Path(sites)
    if not root.is_dir():
        return []
    pages = []
    for p in sorted(root.glob("*/page.json")):
        if skip and p.resolve() == Path(skip).resolve():
            continue
        try:
            pages.append((p, load_json(p)))
        except (OSError, json.JSONDecodeError):
            continue
    return pages


def usage(pages, arch):
    count = {}
    for _, page in pages:
        for k, v in look(page, arch).items():
            if k == "preset":
                count[("preset", v)] = count.get(("preset", v), 0) + 1
            else:
                count[v] = count.get(v, 0) + 1
    return count


def compare(page, pages, arch, limit=LIMIT):
    """Pages that look too close to `page`, with the slots they share. Used by build.py."""
    mine = look(page, arch)
    hits = []
    for path, other in pages:
        if other.get("archetype") != page.get("archetype"):
            continue
        score, shared = similarity(mine, look(other, arch))
        if score >= limit:
            hits.append((path, score, shared))
    return sorted(hits, key=lambda h: -h[1])


def swaps(page, shared, pages, arch):
    """For each shared slot, the allowed variants this page does not use, least used first."""
    count = usage(pages, arch)
    slots = {s["slot"]: s["variants"] for s in arch.get(page.get("archetype"), {}).get("slots", [])}
    mine = look(page, arch)
    out = {}
    for slot in shared:
        if slot == "preset":
            continue
        options = [v for v in slots.get(slot, []) if v != mine.get(slot)]
        out[slot] = sorted(options, key=lambda v: (count.get(v, 0), v))[:3]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sites", default="sites", help="folder that holds one folder per site (default: ./sites)")
    ap.add_argument("--archetype", help="print every slot of this archetype with variants ordered from least to most used")
    ap.add_argument("--check", help="page.json to compare with the other pages")
    ap.add_argument("--report", action="store_true", help="print usage of every variant and preset")
    args = ap.parse_args()
    arch = archetypes()
    pages = find_pages(args.sites, skip=args.check)
    count = usage(pages, arch)
    print("Pages found under %s: %d" % (args.sites, len(pages)))

    if args.archetype:
        a = arch.get(args.archetype)
        if not a:
            print("unknown archetype %r. Choose one of: %s" % (args.archetype, ", ".join(arch)))
            return 1
        presets = sorted((p.stem for p in (TPL / "presets").glob("*.json")), key=lambda p: (count.get(("preset", p), 0), p))
        print("\npreset: " + ", ".join("%s (%d)" % (p, count.get(("preset", p), 0)) for p in presets))
        for s in a["slots"]:
            if s["slot"] in ("floating", "exit"):
                continue
            ordered = sorted(s["variants"], key=lambda v: (count.get(v, 0), s["variants"].index(v)))
            flag = "required" if s.get("required") else ("recommended" if s.get("recommended") else "optional")
            print("%-12s %-11s %s" % (s["slot"], flag, ", ".join("%s (%d)" % (v, count.get(v, 0)) for v in ordered)))
        print("\nPick the first variant in each line that fits the content. A count of 0 means no page uses it yet.")

    if args.check:
        page = load_json(args.check)
        hits = compare(page, pages, arch)
        if not hits:
            print("OK %s does not share %d%% of its look with any other page." % (args.check, LIMIT * 100))
        for path, score, shared in hits:
            print("CLOSE %s shares %d%% of its look with %s (%s)." % (args.check, score * 100, path, ", ".join(shared)))
            for slot, options in swaps(page, shared, pages, arch).items():
                if options:
                    print("  swap %s for one of: %s" % (slot, ", ".join(options)))
            if "preset" in shared:
                print("  or pick another preset (python variety.py --archetype %s lists them by use)" % page.get("archetype"))

    if args.report:
        for k in sorted(count, key=lambda k: (-count[k], str(k))):
            print("%4d  %s" % (count[k], "preset " + k[1] if isinstance(k, tuple) else k))
    return 0


if __name__ == "__main__":
    sys.exit(main())
