"""Check that the copy rules shared by every skill stay the same in each skills/*/scripts/rules.py.

    python tools/check_rules_sync.py

Each skill ships its own rules.py so it can be installed on its own; that copy drifts when a rule is added in one
skill and not the others. The lists below are the house style for every page (banned words, AI tells, emoji,
dashes, slang). Lists tied to one trade, such as LLM_TELLS_VI (BPO phrasing in one skill, retail filler in another),
may differ and are not compared.
"""
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHARED = ["EMOJI", "FLAG_PAIR", "ARROW_CHARS", "ARROW_TEXT", "DASH_CHARS", "DASH_TEXT", "CURLY", "BANNED",
          "WARN_WORDS_RE", "LLM_TELLS", "COLLOQUIAL_VI", "CHATBOT_RE", "NOT_X_BUT_Y"]


def load(path):
    spec = importlib.util.spec_from_file_location("rules_" + path.parent.parent.name.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def plain(value):
    """Compiled patterns compare by their source and flags."""
    if isinstance(value, re.Pattern):
        return (value.pattern, value.flags)
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    return value


def main():
    files = sorted(ROOT.glob("skills/*/scripts/rules.py"))
    if len(files) < 2:
        print("RULES SYNC OK: %d rules.py, nothing to compare" % len(files))
        return 0
    mods = {f.parent.parent.name: load(f) for f in files}
    base_name = "bpo-landing-builder" if "bpo-landing-builder" in mods else next(iter(mods))
    base = mods[base_name]
    problems = []
    for name, mod in mods.items():
        if name == base_name:
            continue
        for key in SHARED:
            if not hasattr(base, key) and not hasattr(mod, key):
                continue
            if not hasattr(mod, key) or not hasattr(base, key):
                has, lacks = (base_name, name) if hasattr(base, key) else (name, base_name)
                problems.append("%s is in %s but missing in %s" % (key, has, lacks))
                continue
            a, b = plain(getattr(base, key)), plain(getattr(mod, key))
            if a == b:
                continue
            if isinstance(a, list) and isinstance(b, list):
                only_a = [x for x in a if x not in b]
                only_b = [x for x in b if x not in a]
                problems.append("%s differs between %s and %s: only in %s %s; only in %s %s"
                                % (key, base_name, name, base_name, only_a[:5], name, only_b[:5]))
            else:
                problems.append("%s differs between %s and %s" % (key, base_name, name))
    for p in problems:
        print("FAIL " + p)
    if problems:
        print("\nRULES SYNC FAILED: copy the change to every skill's scripts/rules.py (or move a trade-specific list out of SHARED).")
        return 1
    print("RULES SYNC OK: %s share the same copy rules" % ", ".join(mods))
    return 0


if __name__ == "__main__":
    sys.exit(main())
