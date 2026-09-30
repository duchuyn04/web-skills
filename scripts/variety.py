#!/usr/bin/env python3
"""Keep generated pages from looking alike. Python standard library only.

Usage:
    python variety.py --archetype it-bpo-partner        least-used variant first, for every slot
    python variety.py --check sites/acme/page.json      compare one page with every other page
    python variety.py --report                          usage of every variant and preset
    python variety.py --blueprints it-bpo-partner       real-site layouts for an archetype, unused first
    python variety.py --blueprint concentrix            the variants that fit each section of one layout
    python variety.py --coverage                        blueprint sections the library cannot fill yet

Pages are found under --sites (default: ./sites). Examples in the skill folder are ignored.
A page's look is its preset plus the variant chosen for each slot. Two pages whose looks
share 70% or more of those choices read as the same template, and build.py warns about it.
"""
import argparse
import json
import sys
for _stream in (sys.stdout, sys.stderr):  # Vietnamese text must not crash printing on a cp1252 console or pipe
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
TPL = SKILL / "templates"
LIMIT = 0.7
# Slots that decide how a page looks at first glance count double.
HEAVY = {"hero": 2, "services": 2}


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def aliases():
    """custom section name mapped to the library variant it copies (schema "aliases"), so hand-built sites count too"""
    out = {}
    for d in (TPL / "sections").iterdir():
        f = d / "schema.json"
        if f.is_file():
            try:
                for a in load_json(f).get("aliases", []):
                    out[a] = d.name
            except ValueError:
                pass
    return out


def expressive_variants():
    """Variants in the expressive tier (3D objects, WebGL scenes, folding effects): only for "motion": "expressive" pages."""
    out = set()
    for d in (TPL / "sections").iterdir():
        f = d / "schema.json"
        if f.is_file() and '"tier": "expressive"' in f.read_text(encoding="utf-8"):
            out.add(d.name)
    return out


def archetypes():
    return {k: v for k, v in load_json(TPL / "archetypes.json").items() if not k.startswith("_")}


def look(page, arch):
    """Return {slot: variant} for a page, plus the preset under the key 'preset'."""
    slots = arch.get(page.get("archetype"), {}).get("slots", [])
    out = {"preset": page.get("preset", "")}
    alias = aliases()
    for sec in page.get("sections", []):
        t = sec.get("type", "")
        if t.startswith("custom:"):
            if t[7:] in alias:
                t = alias[t[7:]]
            else:
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


def blueprint_report(args, pages, count):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import build
    lib = build.load_library()
    bps = lib["blueprints"]
    sig = expressive_variants()
    taken = {}
    for path, page in pages:
        if page.get("blueprint"):
            taken.setdefault(page["blueprint"], []).append(path.parent.name)
    if args.blueprints:
        # a page must say what the company does, so layouts without a services section are not offered
        fit = [k for k, b in bps.items() if args.blueprints in b.get("fits", []) and any(s["role"] == "services" for s in b["sections"])]
        if not fit:
            print("no blueprint fits %r. Archetypes: %s" % (args.blueprints, ", ".join(sorted({a for b in bps.values() for a in b.get("fits", [])}))))
        # layouts a client named as the standard ("preferred": true) come first, unused ones before used ones
        for k in sorted(fit, key=lambda k: (not bps[k].get("preferred"), len(taken.get(k, [])), k)):
            b = bps[k]
            forms = " | ".join("%s:%s%s" % (s["role"], s["form"], "?" if build.slot_optional(s) else "") for s in b["sections"])
            used = (", used by " + ", ".join(taken[k])) if k in taken else ", unused"
            core = [s for s in b["sections"] if not build.slot_optional(s)]
            proof = [s for s in b["sections"] if s.get("role") in build.PROOF_ROLES]
            print("")
            print("%s%s  (%s%s)" % (k, " *" if b.get("preferred") else "", b["source"]["name"], used))
            print("  %d sections: %d always needed, %d need client proof (logos, quotes, cases, team), %d other optional" % (len(b["sections"]), len(core), len(proof), len(b["sections"]) - len(core) - len(proof)))
            print("  " + b.get("summary", ""))
            print("  " + forms)
        print("")
        print("* = preferred: a layout clients named as the standard for a professional page. Take the first unused * blueprint the brief can fill; go down the list only when none fits.")
        print("Pick an unused blueprint whose sections the brief can fill (? = optional; proof sections are left out when the brief has no proof). The page needs a services section and at least 5 content sections. Then run --blueprint KEY.")
    if args.blueprint:
        b = bps.get(args.blueprint)
        if not b:
            print("unknown blueprint %r" % args.blueprint)
            return
        print("%s: %s" % (args.blueprint, b["source"]["name"]))
        print(b.get("summary", ""))
        print("")
        for i, s in enumerate(b["sections"]):
            compose = s.get("compose") or []
            opts = sorted(build.fitting_variants(s, lib), key=lambda v: (v not in compose, v in sig, count.get(v, 0), v))
            grid = ("cols %s, items %s" % (s.get("cols"), s.get("count"))) if s.get("count") else ""
            print("%2d %-11s %-15s %-6s %s%s" % (i + 1, s["role"], s["form"], s.get("tone", ""), "optional " if build.slot_optional(s) else "", grid))
            print("     " + s.get("note", ""))
            print("     variants: " + (", ".join(v + ("=" if v in compose else "") + ("^" if v in sig else "") for v in opts) or "NONE (use a custom section)"))
        print("")
        print("Keep the order; leave out only optional sections. Calm variants come first.")
        print("= = the real site's hero composition. When a hero lists one, build.py requires it (or a business hero: %s)." % ", ".join(sorted(build.BUSINESS_HEROES)))
        print("^ = expressive tier (3D object, WebGL scene or folding effect): only on pages with \"motion\": \"expressive\", for a brief that asks for a 3D or animation-led page. Bands with a \"visual\" field take a WebGL backdrop only on those pages too.")
    if args.coverage:
        gaps = {}
        for k, b in bps.items():
            for s in b["sections"]:
                if not build.fitting_variants(s, lib):
                    gaps.setdefault((s["form"], s["role"]), []).append(k)
        for (form, role), keys in sorted(gaps.items(), key=lambda x: -len(x[1])):
            print("%-16s %-12s %2d  %s" % (form, role, len(keys), ", ".join(keys[:6])))
        print("%d form and role pairs have no variant." % len(gaps))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sites", default="sites", help="folder that holds one folder per site (default: ./sites)")
    ap.add_argument("--archetype", help="print every slot of this archetype with variants ordered from least to most used")
    ap.add_argument("--check", help="page.json to compare with the other pages")
    ap.add_argument("--report", action="store_true", help="print usage of every variant and preset")
    ap.add_argument("--blueprints", metavar="ARCHETYPE", help="list the real-site layouts that fit this archetype, unused first")
    ap.add_argument("--blueprint", metavar="KEY", help="print each section of one layout with the variants that fit it")
    ap.add_argument("--coverage", action="store_true", help="list blueprint sections that no variant fits")
    args = ap.parse_args()
    arch = archetypes()
    pages = find_pages(args.sites, skip=args.check)
    count = usage(pages, arch)
    print("Pages found under %s: %d" % (args.sites, len(pages)))

    if args.archetype:
        a = arch.get(args.archetype)
        sig = expressive_variants()
        if not a:
            print("unknown archetype %r. Choose one of: %s" % (args.archetype, ", ".join(arch)))
            return 1
        presets = sorted((p.stem for p in (TPL / "presets").glob("*.json")), key=lambda p: (count.get(("preset", p), 0), p))
        print("\npreset: " + ", ".join("%s (%d)" % (p, count.get(("preset", p), 0)) for p in presets))
        for s in a["slots"]:
            if s["slot"] in ("floating", "exit"):
                continue
            ordered = sorted(s["variants"], key=lambda v: (v in sig, count.get(v, 0), s["variants"].index(v)))
            flag = "required" if s.get("required") else ("recommended" if s.get("recommended") else "optional")
            print("%-12s %-11s %s" % (s["slot"], flag, ", ".join("%s%s (%d)" % (v, "^" if v in sig else "", count.get(v, 0)) for v in ordered)))
        print("\nPick the first variant in each line that fits the content. A count of 0 means no page uses it yet.")
        print("^ = expressive tier (3D object, WebGL scene or folding effect): build.py accepts it only when page.json sets \"motion\": \"expressive\" and the brief asks for a 3D or animation-led page.")

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

    if args.blueprints or args.blueprint or args.coverage:
        blueprint_report(args, pages, count)

    if args.report:
        for k in sorted(count, key=lambda k: (-count[k], str(k))):
            print("%4d  %s" % (count[k], "preset " + k[1] if isinstance(k, tuple) else k))
    return 0


if __name__ == "__main__":
    sys.exit(main())
