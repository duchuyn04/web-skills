"""Wire the prototype navigator: a "View prototype" button on the right edge of every page that lists every
screen and state, with previous and next screen (kit/proto-nav.js).

    python scripts/protonav.py <out>                         every page in <out> that uses the kit, one group
    python scripts/protonav.py <out> --config nav.json       groups, titles, state labels, an optional select

Writes <out>/kit/proto-nav.js (the kit template with the screen list filled in) and adds
<script src="kit/proto-nav.js"></script> before </body> of each listed page that lacks it. Run it again after
adding a page or changing a page's data-states. new.py runs it once when it starts a project.

Config (JSON, all keys optional; <out>/proto-nav.json is read when --config is not given):

    {"key": "webnhanh",                                   storage prefix, so two prototypes do not share state
     "groups": [{"group": "Visitors", "pages": [["index.html", "Home"], ["app/list.html", "Projects"]]}],
     "states": {"quota-out": "No runs left"},              labels for states, over the built-in ones
     "select": {"param": "industry", "label": "Industry", "pages": ["wizard.html"],
                "options": [["", "As the page shows"], ["spa", "Spa"]]}}

Page paths are relative to <out>; a page in another folder (a landing page next to the app) loads
the script with its own relative path. Pages that use the kit but are missing from the groups go in a last group
and are reported, so nothing is left out by accident.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SKILL = Path(__file__).resolve().parent.parent
MARK = "/*__DATA__*/ null"

STATES = {
    "vi": {
        "default": "Mặc định", "empty": "Trống", "loading": "Đang tải", "error": "Lỗi", "saved": "Đã lưu", "dirty": "Có thay đổi",
        "no-results": "Không có kết quả", "first-day": "Ngày đầu", "alert": "Cảnh báo", "confirmed": "Đã xác nhận", "cancelled": "Đã huỷ",
        "not-found": "Không tìm thấy", "forbidden": "Không có quyền", "server-error": "Lỗi máy chủ", "maintenance": "Bảo trì",
        "offline": "Mất mạng", "quota-out": "Hết lượt", "running": "Đang chạy", "failed": "Thất bại", "done": "Xong", "stopped": "Đã dừng",
        "timed-out": "Quá giờ", "desktop": "Máy tính", "mobile": "Điện thoại", "expired": "Hết hạn", "published": "Đã xuất bản",
        "choose": "Chọn", "details": "Thông tin", "products": "Sản phẩm", "review": "Xem lại", "login": "Đăng nhập",
        "login-error": "Sai mật khẩu", "register": "Đăng ký", "forgot": "Quên mật khẩu", "sent": "Đã gửi", "verify-email": "Xác nhận email",
        "detail": "Chi tiết", "lock": "Khoá", "sent-ok": "Đã gửi",
    },
    "en": {
        "default": "Default", "empty": "Empty", "loading": "Loading", "error": "Error", "saved": "Saved", "dirty": "Unsaved changes",
        "no-results": "No results", "first-day": "First day", "alert": "Alert", "confirmed": "Confirmed", "cancelled": "Cancelled",
        "not-found": "Not found", "forbidden": "No access", "server-error": "Server error", "maintenance": "Maintenance",
        "offline": "Offline", "quota-out": "Limit reached", "running": "Running", "failed": "Failed", "done": "Done", "stopped": "Stopped",
        "timed-out": "Timed out", "desktop": "Desktop", "mobile": "Mobile", "expired": "Expired", "published": "Published",
        "choose": "Choose", "details": "Details", "products": "Products", "review": "Review", "login": "Sign in",
        "login-error": "Wrong password", "register": "Sign up", "forgot": "Forgot password", "sent": "Sent", "verify-email": "Verify email",
        "detail": "Detail", "lock": "Locked",
    },
}
SKIP_DIRS = {"kit", "qa", "node_modules", ".git"}


def page_title(html, fallback):
    m = re.search(r"<title>([^<]*)</title>", html)
    t = (m.group(1) if m else "").strip()
    t = re.split(r"\s+[·|–-]\s+", t)[0].strip() if t else ""
    return t or fallback


def uses_kit(html):
    return "kit/app.css" in html or "data-states=" in html


def find_pages(out):
    found = []
    for f in sorted(out.rglob("*.html")):
        rel = f.relative_to(out)
        if SKIP_DIRS & set(rel.parts[:-1]) or rel.name == "screens.html":
            continue
        if uses_kit(f.read_text(encoding="utf-8", errors="replace")):
            found.append(rel.as_posix())
    return found


def build(out, config=None, lang=None, quiet=False):
    out = Path(out).resolve()
    cfg_path = Path(config) if config else out / "proto-nav.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.is_file() else {}
    html_lang = lang
    if not html_lang:
        first = next(iter(sorted(out.glob("*.html"))), None)
        m = re.search(r'<html[^>]*lang="(\w+)', first.read_text(encoding="utf-8")) if first else None
        html_lang = "en" if m and m.group(1).startswith("en") else "vi"
    labels = dict(STATES[html_lang])
    labels.update(cfg.get("states", {}))

    groups = cfg.get("groups") or [{"group": "", "pages": [[p, None] for p in find_pages(out)]}]
    listed = {p for g in groups for p, _ in g["pages"]}
    extra = [p for p in find_pages(out) if p not in listed]
    if extra:
        groups = groups + [{"group": "Khác" if html_lang == "vi" else "Other", "pages": [[p, None] for p in extra]}]

    data = {"key": cfg.get("key") or re.sub(r"[^\w-]", "", out.name.lower()) or "app", "groups": []}
    if cfg.get("select"):
        data["select"] = cfg["select"]
    unlabelled, missing, n_states = set(), [], 0
    for g in groups:
        dg = {"group": g.get("group", ""), "pages": []}
        for f, title in g["pages"]:
            path = out / f
            if not path.is_file():
                missing.append(f)
                continue
            html = path.read_text(encoding="utf-8")
            m = re.search(r'<body[^>]*\sdata-states="([^"]*)"', html)
            states = m.group(1).split() if m else []
            for s in states:
                if s not in labels:
                    unlabelled.add(s)
            n_states += max(1, len(states))
            dg["pages"].append({"f": f, "t": title or page_title(html, path.stem), "s": [[s, labels.get(s, s)] for s in states]})
        if dg["pages"]:
            data["groups"].append(dg)
    if missing:
        sys.exit("protonav: pages in the config do not exist: " + ", ".join(missing))

    tpl = (SKILL / "kit" / "proto-nav.js").read_text(encoding="utf-8")
    assert MARK in tpl, "kit/proto-nav.js lost its data marker"
    (out / "kit").mkdir(exist_ok=True)
    (out / "kit" / "proto-nav.js").write_text(tpl.replace(MARK, json.dumps(data, ensure_ascii=False)), encoding="utf-8")

    hooked = []
    for g in data["groups"]:
        for p in g["pages"]:
            path = out / p["f"]
            html = path.read_text(encoding="utf-8")
            if "proto-nav.js" in html:
                continue
            if html.count("</body>") != 1:
                print("skip  %s: needs exactly one </body> to add the script" % p["f"])
                continue
            src = os.path.relpath(out / "kit" / "proto-nav.js", path.parent).replace(os.sep, "/")
            path.write_text(html.replace("</body>", '<script src="%s"></script>\n</body>' % src), encoding="utf-8")
            hooked.append(p["f"])

    n_pages = sum(len(g["pages"]) for g in data["groups"])
    if not quiet:
        print("write kit/proto-nav.js (%d pages, %d stops)" % (n_pages, n_states))
        if hooked:
            print("hook  " + ", ".join(hooked))
        if extra and cfg.get("groups"):
            print("note  pages not in the config, listed under the last group: " + ", ".join(extra))
        if unlabelled:
            print("note  states without a label (shown as written; add them to \"states\" in the config): " + ", ".join(sorted(unlabelled)))
    return data


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out")
    ap.add_argument("--config", help="JSON with groups, titles, state labels and an optional select")
    ap.add_argument("--lang", choices=("vi", "en"), help="state label language (default: the pages' <html lang>)")
    a = ap.parse_args()
    build(a.out, a.config, a.lang)


if __name__ == "__main__":
    main()
