"""Real-shop homepage blueprints: list, inspect and check a shop's home order against one.

    python scripts/blueprints.py --style retail            blueprints that fit a style, with their role order
    python scripts/blueprints.py --show thegioididong      one blueprint, section by section, with the section types that fit
    python scripts/blueprints.py --check shop.json         check a shop's home against its "blueprint"

A blueprint (data/blueprints/<id>.json) records the sections of a real shop's homepage in order, each with a role.
A shop picks one with "blueprint": "<id>". The build enforces only the ORDER: the shop's sections, taken in sequence, must
follow the blueprint's role order (a section may repeat a role, and may skip any role; a brief with 8 products cannot fill a
chain's 20 rails), and at least min_matched_roles distinct roles must appear. Sections that no blueprint role fits are allowed.
"""
import json
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SKILL = Path(__file__).resolve().parent.parent
DATA = SKILL / "data"
ROLES = json.loads((DATA / "blueprint-roles.json").read_text(encoding="utf-8"))


def load_all():
    out = {}
    for f in sorted((DATA / "blueprints").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        d["roles"] = [s["role"] for s in d["sections"] if ROLES["roles"].get(s["role"])]
        d["usable"] = len(d["roles"]) >= ROLES["min_sections"]
        out[d["id"]] = d
    return out


def types_for(role):
    return ROLES["roles"].get(role) or []


def fits_style(bp, style):
    return bp["kind"] in ROLES["style_kinds"].get(style, [])


def check(bp, section_types):
    """Return a list of error strings; [] when the shop's section order follows the blueprint."""
    errs = []
    seq = bp["roles"]
    p, matched = 0, set()
    for i, t in enumerate(section_types):
        roles_of_t = {r for r in set(seq) if t in types_for(r)}
        if not roles_of_t:
            continue                      # a section no role of this blueprint wants: allowed
        j = next((k for k in range(p, len(seq)) if seq[k] in roles_of_t), None)
        if j is None:
            later = [seq[k] for k in range(p, len(seq))][:4]
            errs.append("home[%d] '%s' comes too late: in %s the roles of this section (%s) are all before the section you placed it after. "
                        "Move it up, or pick another blueprint. Remaining order: %s" % (i, t, bp["id"], ", ".join(sorted(roles_of_t)), ", ".join(later) or "(end)"))
            break
        p = j
        matched.add(seq[j])
    need = min(ROLES["min_matched_roles"], len(set(seq)))
    if not errs and len(matched) < need:
        missing = [r for r in dict.fromkeys(seq) if r not in matched]
        errs.append("the home page follows only %d of the %d roles needed from blueprint %s. Add sections for: %s" % (
            len(matched), need, bp["id"], "; ".join("%s (%s)" % (r, "/".join(types_for(r))) for r in missing[:6])))
    return errs


def main():
    a = sys.argv[1:]
    bps = load_all()
    if a[:1] == ["--style"]:
        style = a[1]
        for bid, bp in bps.items():
            if fits_style(bp, style) and bp["usable"]:
                print("%-16s %-13s %s" % (bid, bp["kind"], " > ".join(dict.fromkeys(bp["roles"]))))
    elif a[:1] == ["--show"]:
        bp = bps[a[1]]
        print(bp["site"], "|", bp["kind"], "|", bp.get("header", ""))
        for s in bp["sections"]:
            print("  %-16s %-34s fits: %s" % (s["role"], s["form"][:34], ", ".join(types_for(s["role"])) or "(not built)"))
    elif a[:1] == ["--check"]:
        shop = json.loads(Path(a[1]).read_text(encoding="utf-8"))
        bp = bps.get(shop.get("blueprint"))
        if not bp:
            print("no valid blueprint set")
            sys.exit(1)
        errs = check(bp, [s["type"] for s in shop.get("home", [])])
        for e in errs:
            print("ERROR " + e)
        print("BLUEPRINT %s" % ("FAILED" if errs else "OK"))
        sys.exit(1 if errs else 0)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
