"""Build a stressed copy of a shop: the same shop with edge-case data, to see how templates hold up.

    python scripts/stress.py examples/demo-electronics.shop.json --out <dir>          build the stressed shop
    python scripts/stress.py examples/styles/gaming.shop.json --out <dir> --qa        then run qa.py --quick --sweep on it

Real catalogues are not tidy: names run to 150 characters, a TV costs 1,28 billion dong, a product is out of
stock in every version, another has no specs, highlights or description at all. Templates checked only on the
example shops look fine until they meet that data. This script copies the shop, applies the cases below and
builds it next to --out (the stressed shop.json is written as <out>.stress.shop.json, never into examples/):

- shop name and tagline at the longest a real shop uses, and one category name in three words more
- one product with a 150-character name, a long highlight, promo line and spec value
- one product priced over a billion, with a long version name
- one product out of stock in every version
- one bare product: only the required keys, no card chips, highlights, description, specs, promos or badges

The stressed shop is a sample (demo, sample_content), so its copy is not checked against the brief.
"""
import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HERE = Path(__file__).resolve().parent

LONG_NAME_TAIL = " Phiên bản Đặc biệt Kỷ niệm 10 năm, Bảo hành Mở rộng 24 tháng Chính hãng, Kèm Bộ quà tặng Khởi động Đầy đủ"
LONG_SHOP = "Trung tâm Điện máy và Công nghệ Phương Nam Toàn quốc"
LONG_TAGLINE = "Điện thoại, laptop, máy tính bảng, tivi, gia dụng và phụ kiện chính hãng, trả góp 0%, giao nhanh toàn quốc"
LONG_CATEGORY_TAIL = " và phụ kiện chính hãng"
LONG_VERSION = "Intel Core Ultra 9 285H / 64 GB / 2 TB / RTX 5070 Ti 12 GB"
BIG_PRICE = 1284500000
BARE_KEYS = ("card_specs", "highlights", "description", "specs", "promos", "badges", "installment", "warranty",
             "in_box", "addons", "faq", "qa", "reviews", "rating", "sold", "facets", "keywords")


def referenced_ids(shop):
    """Product ids named anywhere in the homepage, so stock and bare cases avoid products a section needs."""
    ids = {p["id"] for p in shop["products"]}
    text = json.dumps(shop.get("home", []), ensure_ascii=False)
    return {i for i in ids if '"%s"' % i in text}


def priced_group(product):
    return next((o for o in product.get("options", []) if any("price" in v for v in o.get("values", []))), None)


def stress(shop):
    s = copy.deepcopy(shop)
    s["demo"] = True
    s["sample_content"] = True
    s["shop"]["name"] = LONG_SHOP
    s["shop"]["tagline"] = LONG_TAGLINE
    s["shop"].pop("slug", None)
    s["categories"][0]["name"] += LONG_CATEGORY_TAIL
    notes = ["shop name %d chars, tagline %d chars, category '%s'" % (len(LONG_SHOP), len(LONG_TAGLINE), s["categories"][0]["name"])]

    products = s["products"]
    used = referenced_ids(s)
    free = [p for p in products if p["id"] not in used]
    # QA's buying flow picks the first product in stock that has options: keep that one untouched.
    flow = next((p for p in products if p.get("options") and p.get("stock", 1) != 0), None)

    long_p = products[0]
    long_p["name"] = long_p["name"] + LONG_NAME_TAIL
    if long_p.get("highlights"):
        long_p["highlights"][0] += ", vỏ nhôm nguyên khối phay CNC, kháng nước và bụi chuẩn IP68 khi ngâm sâu 6 mét trong 30 phút"
    if long_p.get("promos"):
        long_p["promos"][0] += ", áp dụng đồng thời với chương trình thu cũ đổi mới và trả góp 0% qua thẻ tín dụng của 25 ngân hàng"
    if long_p.get("specs") and long_p["specs"][0].get("rows"):
        long_p["specs"][0]["rows"][0][1] += ", tấm nền LTPO thế hệ mới, độ sáng tối đa ngoài trời 3.000 nit, kính cường lực thế hệ thứ 3"
    notes.append("long name (%d chars): %s" % (len(long_p["name"]), long_p["id"]))

    big = next((p for p in products[1:] if priced_group(p) and p is not flow), None)
    if big:
        group = priced_group(big)
        for k, v in enumerate(v for v in group["values"] if "price" in v):
            v["price"] = BIG_PRICE + k * 100000000
            v["old_price"] = v["price"] + 214500000
        group["values"][0]["name"] = LONG_VERSION
        notes.append("price over a billion and long version name: %s" % big["id"])

    out = next((p for p in free if p is not flow and p is not big and p is not long_p), None)
    if out:
        out["stock"] = 0
        notes.append("out of stock in every version: %s" % out["id"])

    bare = next((p for p in free if p not in (flow, big, long_p, out)), None)
    if bare:
        for k in BARE_KEYS:
            bare.pop(k, None)
        notes.append("bare product, required keys only: %s" % bare["id"])
    return s, notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shop")
    ap.add_argument("--out", required=True)
    ap.add_argument("--qa", action="store_true", help="run qa.py --quick --sweep on the stressed build")
    a = ap.parse_args()
    shop = json.loads(Path(a.shop).read_text(encoding="utf-8"))
    stressed, notes = stress(shop)
    out = Path(a.out).resolve()
    src = out.parent / (out.name + ".stress.shop.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    src.write_text(json.dumps(stressed, ensure_ascii=False, indent=1), encoding="utf-8")
    for n in notes:
        print("CASE " + n, flush=True)
    r = subprocess.run([sys.executable, str(HERE / "build.py"), str(src), "--out", str(out)])
    if r.returncode:
        print("\nSTRESS BUILD FAILED: the stressed shop is in %s. An error here is a gap in build.py or the templates." % src)
        sys.exit(1)
    if a.qa:
        r = subprocess.run([sys.executable, str(HERE / "qa.py"), str(out), "--quick", "--sweep"])
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
