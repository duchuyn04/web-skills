"""Build a website: the home page.json plus the inner pages it lists in "pages". Called by build.py when page.json
has a "pages" field; references/site-builds.md explains the format.

Every page goes through build.build_page with the same checks as a single page (copy rules, the brief, photos,
contrast in QA), so a site is as safe as a landing page. On top of that this module checks what only a site has:

- every inner page follows an inner blueprint and opens with page-head or a photo hero (build.py)
- every link to another page (bookkeeping.html, contact.html#form) names a page of the site and a section on it
- every inner page can be reached: some other page links to it (the menu and the footer count)
- no two pages share a title or a description, since search results show both

Output: index.html and <id>.html side by side in one folder, one CSS and JS file per page (assets/css/<id>.css),
shared images, and one sitemap.xml and robots.txt for the whole site.
"""
import copy
import json
import re
import shutil
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlsplit

ID_RE = re.compile(r"^[a-z][a-z0-9-]{1,39}$")
RESERVED = {"index", "home", "assets", "sitemap", "robots"}
HOME_LABEL = {"en": "Home", "vi": "Trang chủ", "de": "Startseite", "fr": "Accueil", "es": "Inicio", "pt": "Início",
              "ja": "ホーム", "ko": "홈", "zh": "首页"}
CHROME = ("header", "footer", "floating")
INNER_KEYS = {"blueprint", "title", "description", "seo", "override_photos", "sections"}


def _rewrite_anchors(node, home_ids):
    """Links in the shared header and footer that point at a section of the home page (#services) lead there from
    every inner page (index.html#services). The brand link (#top) leads to the home page."""
    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            if k in ("href", "action") and isinstance(v, str) and v.startswith("#") and len(v) > 1:
                out[k] = "index.html" if v == "#top" else ("index.html" + v if v[1:] in home_ids else v)
            else:
                out[k] = _rewrite_anchors(v, home_ids)
        return out
    if isinstance(node, list):
        return [_rewrite_anchors(x, home_ids) for x in node]
    return node


def _clear(out_dir):
    """Remove what the previous build wrote (build.py's main already refused a folder it did not make)."""
    if not (out_dir / "build-report.json").exists():
        return
    for target in [out_dir / "assets", out_dir / "robots.txt", out_dir / "sitemap.xml", out_dir / "build-report.json"] + list(out_dir.glob("*.html")):
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()


def build_site(build, page, page_path, out_dir, lib):
    site_dir = page_path.parent
    lang = page.get("lang", "en")
    errors = []

    def err(where, msg):
        errors.append("%s: %s" % (where, msg))

    # 1. The page list.
    entries = page.get("pages")
    if not isinstance(entries, list) or not entries:
        print("ERROR page.pages: list the inner pages, each {\"id\": \"payroll\", \"src\": \"pages/payroll.json\", \"label\": \"Payroll\", \"parent\": \"solutions\"}")
        return 1
    pages, order = {}, []
    for i, e in enumerate(entries):
        where = "page.pages[%d]" % i
        if not isinstance(e, dict):
            err(where, "must be an object {\"id\", \"src\", \"label\", \"parent\"}")
            continue
        for k in e:
            if k not in ("id", "src", "label", "parent"):
                err("%s.%s" % (where, k), "unknown field. A page entry has id, src, label and parent.")
        pid = e.get("id")
        if not isinstance(pid, str) or not ID_RE.match(pid) or pid in RESERVED:
            err(where + ".id", "%r: use 2-40 lowercase letters, digits and hyphens, starting with a letter (the page is written as <id>.html); not %s" % (pid, ", ".join(sorted(RESERVED))))
            continue
        if pid in pages:
            err(where + ".id", "%r is listed twice" % pid)
            continue
        if not isinstance(e.get("label"), str) or not 2 <= len(e["label"].strip()) <= 40:
            err(where + ".label", "the page's short name for breadcrumbs and links, 2-40 characters")
        src = site_dir / str(e.get("src", ""))
        if not e.get("src") or not src.is_file():
            err(where + ".src", "file %r not found next to page.json" % e.get("src"))
            continue
        pages[pid] = dict(e, file=pid + ".html", path=src)
        order.append(pid)
    for pid in order:
        parent = pages[pid].get("parent")
        if parent and parent not in pages:
            err("pages %s.parent" % pid, "%r is not the id of another page" % parent)
            pages[pid]["parent"] = None
    for pid in order:  # a parent chain that loops back would never end
        seen, cur = {pid}, pages[pid].get("parent")
        while cur:
            if cur in seen:
                err("pages %s.parent" % pid, "the parent chain loops back to %s" % cur)
                pages[pid]["parent"] = None
                break
            seen.add(cur)
            cur = pages[cur].get("parent")
    if errors:
        for e in errors:
            print("ERROR " + e)
        print("\nSITE FAILED with %d error(s) in the page list." % len(errors))
        return 1

    try:
        prev = json.loads((out_dir / "build-report.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        prev = {}
    prev_pages = prev.get("pages") or {}
    _clear(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 2. The home page, built like a single page with every homepage rule.
    print("== page.json (index.html)")
    ok, home = build.build_page(page, page_path, out_dir, lib, spage={
        "kind": "home", "id": "index", "file": "index.html", "home": "#top", "prefix": "page.json: ",
        "page_dir": site_dir, "prev_seo": (prev_pages.get("index") or {}).get("seo"), "crumbs": None})
    results = {"index": (ok, home)}
    failed = not ok

    # 3. The shared header, footer and floating parts, as written in page.json.
    chrome_top, chrome_bottom = [], []
    seen_body = False
    for s in page.get("sections") or []:
        t = s.get("type", "") if isinstance(s, dict) else ""
        group = (lib["variants"].get(t) or {}).get("group")
        if group in CHROME:
            (chrome_bottom if seen_body or group == "footer" else chrome_top).append(_rewrite_anchors(copy.deepcopy(s), set(home["ids"])))
        elif t:
            seen_body = True
    base_seo = page.get("seo") if isinstance(page.get("seo"), dict) else {}
    base_url = base_seo.get("url")
    folder_url = urljoin(base_url, "./") if base_url else None
    home_label = HOME_LABEL.get(lang, "Home")
    # the picture shared for an inner page without photos: the site's share image, else the home hero photo
    hero = next((s.get("data") or {} for s in page.get("sections") or [] if isinstance(s, dict) and str(s.get("type", "")).startswith("hero")), {})
    share_image = (base_seo.get("image"), base_seo.get("image_alt") or "") if base_seo.get("image") else ((hero.get("image"), "") if hero.get("image") else None)

    # 4. Inner pages.
    for pid in order:
        meta = pages[pid]
        rel = meta["path"].relative_to(site_dir).as_posix()
        print("\n== %s (%s)" % (rel, meta["file"]))
        try:
            raw = json.loads(meta["path"].read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeDecodeError) as e:
            print("ERROR %s: not valid UTF-8 JSON: %s" % (rel, e))
            results[pid], failed = (False, None), True
            continue
        if not isinstance(raw, dict):
            print("ERROR %s: must be one object {\"blueprint\", \"title\", \"description\", \"sections\"}" % rel)
            results[pid], failed = (False, None), True
            continue
        unknown = [k for k in raw if k not in INNER_KEYS and not k.startswith("_")]
        if unknown:
            print("ERROR %s: unknown field(s) %s. An inner page has %s; the brand, theme, brief, header and footer come from page.json." % (rel, ", ".join(unknown), ", ".join(sorted(INNER_KEYS))))
            results[pid], failed = (False, None), True
            continue
        trail, cur = [], meta.get("parent")
        while cur:
            trail.insert(0, {"label": pages[cur]["label"], "href": pages[cur]["file"]})
            cur = pages[cur].get("parent")
        crumbs = [{"label": home_label, "href": "index.html"}] + trail + [{"label": meta["label"]}]
        sections = copy.deepcopy(raw.get("sections") or [])
        body = [s for s in sections if isinstance(s, dict)]
        if body and body[0].get("type") == "page-head" and isinstance(body[0].get("data"), dict):
            body[0]["data"].setdefault("crumbs", crumbs)
        synth = {k: copy.deepcopy(page[k]) for k in ("archetype", "preset", "lang", "theme", "features", "motion", "brief", "rules") if k in page}
        synth["site"] = dict(page.get("site") or {}, title=raw.get("title", ""), description=raw.get("description", ""))
        seo = {k: base_seo[k] for k in ("icon", "locale", "index") if k in base_seo}
        if folder_url:
            seo["url"] = urljoin(folder_url, meta["file"])
        seo.update({k: v for k, v in (raw.get("seo") or {}).items() if v is not None})
        if seo:
            synth["seo"] = seo
        for k in ("blueprint", "override_photos"):
            if k in raw:
                synth[k] = raw[k]
        synth["sections"] = copy.deepcopy(chrome_top) + sections + copy.deepcopy(chrome_bottom)
        ok, info = build.build_page(synth, meta["path"], out_dir, lib, spage={
            "kind": "inner", "id": pid, "file": meta["file"], "home": "index.html", "prefix": rel + ": ",
            "page_dir": site_dir, "prev_seo": (prev_pages.get(pid) or {}).get("seo"), "crumbs": crumbs,
            "chrome": (len(chrome_top), len(chrome_top) + len(chrome_bottom)), "share_image": share_image})
        results[pid] = (ok, info)
        failed = failed or not ok

    # 5. What only a site has: links between pages, reachability, unique titles.
    files = {"index.html": "index"}
    files.update({pages[p]["file"]: p for p in order})
    linked = set()
    print("\n== site")
    for pid, (ok, info) in results.items():
        if not info:
            continue
        own = "index.html" if pid == "index" else pages[pid]["file"]
        where = "page.json" if pid == "index" else pages[pid]["path"].relative_to(site_dir).as_posix()
        for path, href in info["page_links"]:
            m = build.PAGE_LINK_RE.match(href)
            target, anchor = m.group(1), m.group(2)
            if target not in files:
                err("%s: %s" % (where, path), "%s is not a page of this site. Pages: %s" % (target, ", ".join(files)))
                continue
            if target != own:
                linked.add(files[target])
            tinfo = results.get(files[target], (False, None))[1]
            if anchor and tinfo and anchor not in tinfo["ids"]:
                err("%s: %s" % (where, path), "%s has no section #%s. Its sections: %s" % (target, anchor, ", ".join(tinfo["ids"])))
    for pid in order:
        if pid not in linked:
            err("pages %s" % pid, "%s is linked from no other page. Add it to the menu, the footer or a section of its parent page, or drop it from \"pages\"." % pages[pid]["file"])
    seen_title, seen_desc = {}, {}
    for pid in ["index"] + order:
        src = page if pid == "index" else None
        if src is None:
            try:
                src = json.loads(pages[pid]["path"].read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            title, desc = src.get("title"), src.get("description")
        else:
            title, desc = (src.get("site") or {}).get("title"), (src.get("site") or {}).get("description")
        name = "index.html" if pid == "index" else pages[pid]["file"]
        for value, seen, what in ((title, seen_title, "title"), (desc, seen_desc, "description")):
            if not isinstance(value, str):
                continue
            key = value.strip().lower()
            if key in seen:
                err(name, "has the same %s as %s. Search results show it for both pages; say what this page is about." % (what, seen[key]))
            seen.setdefault(key, name)
    for e in errors:
        print("ERROR " + e)
    failed = failed or bool(errors)

    # 6. Sitemap, robots and the report.
    home_info = results["index"][1] or {}
    entries_out = []
    for pid in ["index"] + order:
        info = results.get(pid, (False, None))[1]
        rec = (info or {}).get("seo") or {}
        if rec.get("url") and rec.get("index"):
            entries_out.append((rec["url"], rec.get("lastmod") or date.today().isoformat()))
    if entries_out and not failed:
        folder = urlsplit(base_url).path.rsplit("/", 1)[0] + "/"
        sitemap_url = urljoin(base_url, folder + "sitemap.xml")
        (out_dir / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                             + "".join("  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n  </url>\n" % (u, d) for u, d in entries_out)
                                             + "</urlset>\n", encoding="utf-8")
        if folder == "/":
            (out_dir / "robots.txt").write_text("User-agent: *\nAllow: /\n\nSitemap: %s\n" % sitemap_url, encoding="utf-8")
    report = {"rules": int(home_info.get("legacy")) if home_info.get("legacy") else build.RULES_VERSION, "site": True,
              "archetype": home_info.get("archetype"), "preset": home_info.get("preset"), "motion_style": home_info.get("motion_style"),
              "sections": home_info.get("sections"), "seo": home_info.get("seo"),
              "warnings": sum(((r[1] or {}).get("warnings", []) for r in results.values()), []),
              "placeholders": sum(((r[1] or {}).get("placeholders", []) for r in results.values()), []),
              "pages": {pid: {"file": "index.html" if pid == "index" else pages[pid]["file"],
                              "seo": (r[1] or {}).get("seo"), "sections": (r[1] or {}).get("sections")} for pid, r in results.items()}}
    # written even when the site failed: the pages that built are already in the folder, and the next build clears
    # only a folder that carries this report
    report["failed"] = failed
    (out_dir / "build-report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    bad = [("index.html" if p == "index" else pages[p]["file"]) for p, r in results.items() if not r[0]]
    if failed:
        print("\nSITE FAILED: %s. Fix the errors above in page.json and the page files, then run build.py again."
              % ("pages with errors: " + ", ".join(bad) if bad else "%d site error(s)" % len(errors)))
        return 1
    print("\nOK built %d pages into %s" % (len(results), out_dir))
    return 0
