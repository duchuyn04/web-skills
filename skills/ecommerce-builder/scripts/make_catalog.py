"""Write references/variant-catalog.md from the first-line comments of every variant template.

    python scripts/make_catalog.py
"""
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
sys.path.insert(0, str(Path(__file__).resolve().parent))
import variants as V  # noqa: E402

out = V.SKILL / "references" / "variant-catalog.md"
out.write_text(V.catalog(), encoding="utf-8")
print("wrote", out)
