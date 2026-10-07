"""Turn plan.json into a Scrum plan workbook (roadmap, sprints, backlog) and a CSV that Jira imports.

    python scripts/make_plan.py plan.json --out <folder>
    python scripts/make_plan.py plan.json --check            only check the plan, write nothing

Writes <folder>/<file>.xlsx and <folder>/<file>-jira.csv (<file> from plan.json, default the project name).
The workbook has three sheets in Jira terms: Lộ trình (epics over sprints, like Jira Timeline), Sprints (goal,
committed and completed points, state from today's date) and Backlog (one row per epic and issue with Jira's
fields). An "overview" block in plan.json adds a first sheet in plain words for a reader who is not technical.
Totals are Excel formulas over the Backlog sheet: change Status to Done and the sprint and roadmap totals follow.

The CSV is UTF-8 with a byte order mark so Excel shows Vietnamese correctly; Jira reads it too. Epics come first
and children point at them through Parent = the epic's Issue Id, which is what the Jira Cloud importer links on.

Checks (errors stop the run, warnings are printed): epic names follow "epic_naming"; every issue has a known epic,
a Jira type and priority, Fibonacci points, a sprint in range; labels have no spaces; every sprint has work and
stays under "capacity"; stories have acceptance criteria; with "deploy_every_sprint" each sprint before the last
has an issue labelled deploy; the release date is not a Friday and falls inside the plan; testing comes before
the release.
"""
import argparse
import csv
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

TYPES = ("Epic", "Story", "Task", "Bug")
PRIORITIES = ("Highest", "High", "Medium", "Low", "Lowest")
POINTS = (1, 2, 3, 5, 8, 13)
PALETTE = ["6554C0", "0065FF", "00A3BF", "36B37E", "FF8B00", "DE350B", "5243AA", "0747A6", "008DA6", "00875A",
           "FF991F", "BF2600", "006644", "403294", "97A0AF"]
WORDS = {
    "vi": {"roadmap": "Lộ trình", "sprints": "Sprints", "backlog": "Backlog", "overview": "Tổng quan",
           "roadmap_sub": "Giống Timeline của Jira: mỗi epic một thanh qua các sprint có issue của epic đó. SP tự tính từ Backlog.",
           "sprints_sub": "Sprint {w} tuần. Committed và Completed tự tính từ Backlog (Completed là Status = Done).",
           "backlog_sub": "Cột theo field của Jira. Epic nằm trên, story và task bên dưới. Sprint trống là còn trong backlog.",
           "name": "Tên", "goal": "Sprint Goal (mục tiêu cuối sprint)", "total": "Tổng", "milestones": "Mốc",
           "date": "Ngày", "milestone": "Mốc", "note": "Ghi chú", "sprint": "Sprint"},
    "en": {"roadmap": "Roadmap", "sprints": "Sprints", "backlog": "Backlog", "overview": "Overview",
           "roadmap_sub": "Like Jira Timeline: one bar per epic across the sprints that hold its issues. Points come from Backlog.",
           "sprints_sub": "{w}-week sprints. Committed and Completed come from Backlog (Completed means Status = Done).",
           "backlog_sub": "Columns follow Jira fields. Epics first, then stories and tasks. An empty Sprint means still in the backlog.",
           "name": "Name", "goal": "Sprint Goal", "total": "Total", "milestones": "Milestones",
           "date": "Date", "milestone": "Milestone", "note": "Note", "sprint": "Sprint"},
}


def load(path):
    p = json.loads(Path(path).read_text(encoding="utf-8"))
    p.setdefault("key", re.sub(r"[^A-Z]", "", p["project"].upper())[:4] or "PRJ")
    p.setdefault("sprint_weeks", 1)
    p.setdefault("lang", "vi")
    p.setdefault("file", re.sub(r"[^\w-]+", "-", p["project"]).strip("-"))
    p["start"] = date.fromisoformat(p["start"])
    if p.get("release"):
        p["release"] = date.fromisoformat(p["release"])
    for m in p.get("milestones", []):
        m["date"] = date.fromisoformat(m["date"])
    for i, e in enumerate(p["epics"]):
        e.setdefault("color", PALETTE[i % len(PALETTE)])
    return p


def sprint_dates(p, n):
    s = p["start"] + timedelta(weeks=p["sprint_weeks"] * (n - 1))
    return s, s + timedelta(weeks=p["sprint_weeks"], days=-3)


def sprint_name(p, n):
    return "%s Sprint %d" % (p["key"], n)


def check(p):
    errs, warns = [], []
    n_sprints = len(p["sprints"])
    codes = {e["code"] for e in p["epics"]}
    prefixes = p.get("epic_naming") or []
    for e in p["epics"]:
        if prefixes and not any(e["name"].startswith(x + " ") for x in prefixes):
            errs.append('epic %s "%s" does not start with %s' % (e["code"], e["name"], " or ".join('"%s"' % x for x in prefixes)))
        if not any(i["epic"] == e["code"] for i in p["issues"]):
            warns.append("epic %s has no issues" % e["code"])
    for n, i in enumerate(p["issues"], 1):
        where = 'issue %d "%s"' % (n, i.get("summary", "")[:50])
        if i.get("epic") not in codes:
            errs.append("%s: unknown epic %r" % (where, i.get("epic")))
        if i.get("type") not in TYPES[1:]:
            errs.append("%s: type must be one of %s" % (where, ", ".join(TYPES[1:])))
        if i.get("priority") not in PRIORITIES:
            errs.append("%s: priority must be one of %s" % (where, ", ".join(PRIORITIES)))
        if i.get("points") not in POINTS:
            errs.append("%s: points must be one of %s" % (where, POINTS))
        s = i.get("sprint")
        if s is not None and not (isinstance(s, int) and 1 <= s <= n_sprints):
            errs.append("%s: sprint %r is outside 1..%d (null keeps it in the backlog)" % (where, s, n_sprints))
        if len(i.get("summary", "")) > 255 or not i.get("summary"):
            errs.append("%s: summary must be 1 to 255 characters (Jira limit)" % where)
        for lab in i.get("labels", []):
            if " " in lab:
                errs.append("%s: label %r has a space; Jira splits labels on spaces" % (where, lab))
        if i.get("type") == "Story" and s is not None and not i.get("ac"):
            warns.append("%s: a story in a sprint without acceptance criteria" % where)
    cap = p.get("capacity")
    for n in range(1, n_sprints + 1):
        items = [i for i in p["issues"] if i.get("sprint") == n]
        pts = sum(i.get("points", 0) for i in items)
        if not items:
            errs.append("sprint %d has no issues" % n)
        if cap and pts > cap:
            warns.append("sprint %d holds %d points, over the capacity of %d" % (n, pts, cap))
        if p.get("deploy_every_sprint") and n < n_sprints and not any("deploy" in i.get("labels", []) for i in items):
            errs.append('sprint %d has no issue labelled "deploy" (deploy_every_sprint is on)' % n)
    rel = p.get("release")
    if rel:
        first, last = sprint_dates(p, 1)[0], sprint_dates(p, n_sprints)[1]
        if not first <= rel <= last:
            errs.append("release %s is outside the plan (%s to %s)" % (rel, first, last))
        if rel.weekday() == 4:
            warns.append("release falls on a Friday; a Tuesday leaves the rest of the week to fix what breaks")
        rel_sprint = next(n for n in range(1, n_sprints + 1) if rel <= sprint_dates(p, n)[1]) if first <= rel <= last else n_sprints
        if not any("qa" in i.get("labels", []) and i.get("sprint") and i["sprint"] < rel_sprint for i in p["issues"]):
            warns.append('no issue labelled "qa" before the release sprint; plan the testing before going live')
    if p["start"].weekday() != 0:
        warns.append("start date %s is not a Monday" % p["start"])
    return errs, warns


def write_xlsx(p, path):
    from openpyxl import Workbook
    from openpyxl.formatting.rule import CellIsRule
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation

    W = WORDS[p["lang"]]
    FONT, NAVY, LINE, GREY = "Calibri", "253858", "DFE1E6", "F4F5F7"
    side = Side(style="thin", color=LINE)
    BORDER = Border(left=side, right=side, top=side, bottom=side)
    TOP = Alignment(wrap_text=True, vertical="top")
    MID = Alignment(horizontal="center", vertical="center", wrap_text=True)

    def fill(c):  # conditional formats need start and end colour, a plain fgColor shows no fill there
        return PatternFill(fill_type="solid", start_color=c, end_color=c)

    def title(ws, text, sub):
        ws.sheet_view.showGridLines = False
        ws["A1"], ws["A2"] = text, sub
        ws["A1"].font = Font(name=FONT, size=16, bold=True, color=NAVY)
        ws["A2"].font = Font(name=FONT, size=10, italic=True, color="5E6C84")

    def head(ws, row, cols):
        for c, v in enumerate(cols, 1):
            cell = ws.cell(row=row, column=c, value=v)
            cell.font, cell.fill, cell.alignment, cell.border = Font(name=FONT, bold=True, color="FFFFFF"), fill(NAVY), MID, BORDER
        ws.row_dimensions[row].height = 30

    def grid(ws, r1, r2, c1, c2):
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                cell = ws.cell(row=r, column=c)
                cell.border = BORDER
                if not cell.alignment.horizontal and not cell.alignment.vertical:
                    cell.alignment = TOP

    def widths(ws, ws_w):
        for c, w in enumerate(ws_w, 1):
            ws.column_dimensions[get_column_letter(c)].width = w

    def landscape(ws):
        ws.page_setup.orientation, ws.page_setup.paperSize = "landscape", ws.PAPERSIZE_A4
        ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True

    n_sprints = len(p["sprints"])
    epic_by = {e["code"]: e for e in p["epics"]}
    wb = Workbook()

    # Backlog
    bl = wb.active
    bl.title = W["backlog"]
    BL = "'%s'" % W["backlog"]
    title(bl, "%s: %s" % (W["backlog"], p["key"]), W["backlog_sub"])
    cols = ["Issue Key", "Issue Type", "Summary", "Parent", "Epic", "Priority", "Story Points", "Sprint", "Status",
            "Assignee", "Labels", "Component", "Fix Version", "Description", "Acceptance Criteria"]
    head(bl, 4, cols)
    widths(bl, [10, 10, 44, 10, 26, 10, 9, 15, 12, 13, 16, 15, 10, 52, 52])
    keys, r = {}, 4
    for n, e in enumerate(p["epics"], 1):
        keys[e["code"]] = "%s-%d" % (p["key"], n)
    first_child = 5 + len(p["epics"])
    for e in p["epics"]:
        r += 1
        k = keys[e["code"]]
        vals = [k, "Epic", e["name"], "", e["name"], "", "=SUMIFS($G$%d:$G$9999,$D$%d:$D$9999,A%d)" % (first_child, first_child, r),
                "", "To Do", "", e["code"].lower(), "", e.get("version", p.get("version", "v1.0")), e.get("description", ""), ""]
        for c, v in enumerate(vals, 1):
            bl.cell(row=r, column=c, value=v)
        for c in range(1, len(cols) + 1):
            bl.cell(row=r, column=c).fill = fill(GREY)
        bl.cell(row=r, column=3).font = Font(name=FONT, bold=True, color=e["color"])
        bl.cell(row=r, column=7).font = Font(name=FONT, bold=True, italic=True, color="5E6C84")
    n = len(p["epics"])
    for i in p["issues"]:
        n += 1
        r += 1
        e = epic_by[i["epic"]]
        vals = ["%s-%d" % (p["key"], n), i["type"], i["summary"], keys[i["epic"]], e["name"], i["priority"], i["points"],
                sprint_name(p, i["sprint"]) if i.get("sprint") else "", i.get("status", "To Do"), i.get("assignee", ""),
                ", ".join(i.get("labels", [])), i.get("component", ""),
                p.get("version", "v1.0") if i.get("sprint") else p.get("later_version", "v1.1"),
                i.get("description", ""), "\n".join("• " + a for a in i.get("ac", []))]
        for c, v in enumerate(vals, 1):
            bl.cell(row=r, column=c, value=v)
        bl.cell(row=r, column=5).font = Font(name=FONT, bold=True, color=e["color"])
        bl.row_dimensions[r].height = max(45, 15 * (1 + len(i.get("ac", []))))
    last = r
    grid(bl, 5, last, 1, len(cols))
    for rr in range(5, last + 1):
        for c in (1, 2, 4, 6, 7, 8, 9, 13):
            bl.cell(row=rr, column=c).alignment = Alignment(horizontal="center", vertical="top", wrap_text=True)
        bl.cell(row=rr, column=1).font = Font(name=FONT, color="0052CC")
        t = bl.cell(row=rr, column=2).value
        bl.cell(row=rr, column=2).font = Font(name=FONT, bold=True, color={"Epic": "6554C0", "Story": "36B37E", "Task": "0065FF", "Bug": "DE350B"}[t])
    lists = [("B", '"%s"' % ",".join(TYPES)), ("F", '"%s"' % ",".join(PRIORITIES)), ("I", '"To Do,In Progress,In Review,Done"'),
             ("H", '"%s"' % ",".join(sprint_name(p, k) for k in range(1, n_sprints + 1)))]
    for col, f in lists:
        dv = DataValidation(type="list", formula1=f, allow_blank=True)
        bl.add_data_validation(dv)
        dv.add("%s5:%s%d" % (col, col, last + 200))
    dv = DataValidation(type="list", formula1='"%s"' % ",".join(map(str, POINTS)), allow_blank=True)
    bl.add_data_validation(dv)
    dv.add("G%d:G%d" % (first_child, last + 200))
    pr = {"Highest": ("FFEBE6", "BF2600"), "High": ("FFF0E6", "C25100"), "Medium": ("FFFAE6", "7A5D00"), "Low": ("E6F0FF", "0747A6"), "Lowest": ("F4F5F7", "5E6C84")}
    stc = {"To Do": ("DFE1E6", "42526E"), "In Progress": ("DEEBFF", "0747A6"), "In Review": ("EAE6FF", "403294"), "Done": ("E3FCEF", "006644")}
    for txt, (bg, fg) in pr.items():
        bl.conditional_formatting.add("F5:F%d" % (last + 200), CellIsRule(operator="equal", formula=['"%s"' % txt], fill=fill(bg), font=Font(color=fg, bold=True)))
    for txt, (bg, fg) in stc.items():
        bl.conditional_formatting.add("I5:I%d" % (last + 200), CellIsRule(operator="equal", formula=['"%s"' % txt], fill=fill(bg), font=Font(color=fg, bold=True)))
    bl.auto_filter.ref = "A4:O%d" % last
    bl.freeze_panes = "D5"
    landscape(bl)

    # Sprints
    sp = wb.create_sheet(W["sprints"], 0)
    title(sp, W["sprints"], W["sprints_sub"].format(w=p["sprint_weeks"]))
    head(sp, 4, [W["sprint"], "Start", "End", W["name"], W["goal"], "Issues", "Committed SP", "Completed SP", "% Done", "State"])
    widths(sp, [15, 11, 11, 28, 70, 8, 12, 12, 9, 11])
    for k, s in enumerate(p["sprints"], 1):
        r = 4 + k
        a, b = sprint_dates(p, k)
        vals = [sprint_name(p, k), a, b, s["name"], s["goal"], "=COUNTIFS(%s!H:H,A%d)" % (BL, r),
                "=SUMIFS(%s!G:G,%s!H:H,A%d)" % (BL, BL, r), '=SUMIFS(%s!G:G,%s!H:H,A%d,%s!I:I,"Done")' % (BL, BL, r, BL),
                "=IFERROR(H%d/G%d,0)" % (r, r), '=IF(TODAY()<B%d,"Future",IF(TODAY()>C%d,"Closed","Active"))' % (r, r)]
        for c, v in enumerate(vals, 1):
            sp.cell(row=r, column=c, value=v)
        sp.cell(row=r, column=2).number_format = sp.cell(row=r, column=3).number_format = "dd/mm/yyyy"
        sp.cell(row=r, column=9).number_format = "0%"
        sp.row_dimensions[r].height = 36
    tr = 5 + n_sprints
    sp.cell(row=tr, column=1, value=W["total"])
    for c, f in ((6, "=SUM(F5:F%d)"), (7, "=SUM(G5:G%d)"), (8, "=SUM(H5:H%d)")):
        sp.cell(row=tr, column=c, value=f % (tr - 1))
    sp.cell(row=tr, column=9, value="=IFERROR(H%d/G%d,0)" % (tr, tr)).number_format = "0%"
    grid(sp, 5, tr, 1, 10)
    for rr in range(5, tr + 1):
        for c in range(1, 11):
            sp.cell(row=rr, column=c).alignment = Alignment(horizontal=None if c in (4, 5) else "center", vertical="center", wrap_text=True)
        sp.cell(row=rr, column=1).font = Font(name=FONT, bold=True, color="0052CC")
    for c in range(1, 11):
        sp.cell(row=tr, column=c).fill = fill(GREY)
        sp.cell(row=tr, column=c).font = Font(name=FONT, bold=True)
    for txt, key in (("Active", "In Progress"), ("Closed", "Done"), ("Future", "To Do")):
        bg, fg = stc[key]
        sp.conditional_formatting.add("J5:J%d" % (tr - 1), CellIsRule(operator="equal", formula=['"%s"' % txt], fill=fill(bg), font=Font(color=fg, bold=True)))
    ms = sorted(p.get("milestones", []), key=lambda m: m["date"])
    if ms:
        r = tr + 2
        sp.cell(row=r, column=1, value=W["milestones"]).font = Font(name=FONT, size=12, bold=True, color=NAVY)
        head(sp, r + 1, [W["date"], W["milestone"], "", "", W["note"]])
        sp.merge_cells(start_row=r + 1, start_column=2, end_row=r + 1, end_column=4)
        for k, m in enumerate(ms):
            rr = r + 2 + k
            sp.cell(row=rr, column=1, value=m["date"]).number_format = "dd/mm/yyyy"
            sp.cell(row=rr, column=2, value=m["name"]).font = Font(name=FONT, bold=True)
            sp.merge_cells(start_row=rr, start_column=2, end_row=rr, end_column=4)
            sp.cell(row=rr, column=5, value=m.get("note", ""))
            sp.row_dimensions[rr].height = 30
        grid(sp, r + 2, r + 1 + len(ms), 1, 5)
        for rr in range(r + 2, r + 2 + len(ms)):
            sp.cell(row=rr, column=1).alignment = MID
    sp.freeze_panes = "B5"
    landscape(sp)

    # Roadmap
    rm = wb.create_sheet(W["roadmap"], 0)
    title(rm, W["roadmap"], W["roadmap_sub"])
    widths(rm, [10, 34, 8] + [15] * n_sprints)
    head(rm, 4, ["Key", "Epic", "SP"] + ["Sprint %d" % k for k in range(1, n_sprints + 1)])
    for k in range(1, n_sprints + 1):
        a, b = sprint_dates(p, k)
        c = rm.cell(row=5, column=3 + k, value="%s – %s" % (a.strftime("%d/%m"), b.strftime("%d/%m")))
        c.font, c.alignment = Font(name=FONT, size=9, color="5E6C84"), MID
    r = 5
    for e in p["epics"]:
        spr = [i["sprint"] for i in p["issues"] if i["epic"] == e["code"] and i.get("sprint")]
        if not spr:
            continue
        r += 1
        rm.cell(row=r, column=1, value=keys[e["code"]]).font = Font(name=FONT, color="0052CC")
        rm.cell(row=r, column=2, value=e["name"]).font = Font(name=FONT, bold=True)
        rm.cell(row=r, column=3, value="=SUMIFS(%s!G:G,%s!D:D,A%d,%s!H:H,\"?*\")" % (BL, BL, r, BL))
        for k in range(min(spr), max(spr) + 1):
            cell = rm.cell(row=r, column=3 + k)
            cell.fill = fill(e["color"])
            pts = sum(i["points"] for i in p["issues"] if i["epic"] == e["code"] and i.get("sprint") == k)
            if pts:
                cell.value = "%d SP" % pts
                cell.font = Font(name=FONT, size=9, bold=True, color="FFFFFF")
        rm.row_dimensions[r].height = 22
    last_epic = r
    for m in ms:
        k = next((k for k in range(1, n_sprints + 1) if m["date"] <= sprint_dates(p, k)[1]), None)
        if not k:
            continue
        r += 1
        color = m.get("color", "FF8B00")
        rm.cell(row=r, column=2, value="◆ " + m["name"]).font = Font(name=FONT, bold=True, color=color)
        rm.cell(row=r, column=3 + k, value="◆").font = Font(name=FONT, size=12, bold=True, color=color)
    grid(rm, 5, r, 1, 3 + n_sprints)
    for rr in range(5, r + 1):
        for c in [1] + list(range(3, 4 + n_sprints)):
            rm.cell(row=rr, column=c).alignment = MID
        rm.cell(row=rr, column=2).alignment = Alignment(vertical="center")
    r += 1
    rm.cell(row=r, column=2, value=W["total"]).font = Font(name=FONT, bold=True)
    rm.cell(row=r, column=3, value="=SUM(C6:C%d)" % last_epic).font = Font(name=FONT, bold=True)
    rm.cell(row=r, column=3).alignment = MID
    rm.freeze_panes = "D6"
    landscape(rm)

    # Overview in plain words, for a reader who is not technical
    if p.get("overview"):
        ov = wb.create_sheet(W["overview"], 0)
        title(ov, p["project"], p["overview"].get("subtitle", ""))
        widths(ov, [26, 90])
        r = 3
        for k, v in p["overview"].get("lines", []):
            r += 1
            ov.cell(row=r, column=1, value=k).font = Font(name=FONT, bold=True, color=NAVY)
            ov.cell(row=r, column=2, value=v)
            ov.row_dimensions[r].height = 34
        grid(ov, 4, r, 1, 2)
        r += 2
        head(ov, r, [W["sprint"], W["goal"]])
        for k, s in enumerate(p["sprints"], 1):
            a, b = sprint_dates(p, k)
            ov.cell(row=r + k, column=1, value="Sprint %d · %s – %s" % (k, a.strftime("%d/%m"), b.strftime("%d/%m")))
            ov.cell(row=r + k, column=2, value=s.get("outcome", s["goal"]))
            ov.row_dimensions[r + k].height = 34
        grid(ov, r + 1, r + n_sprints, 1, 2)

    wb.calculation.fullCalcOnLoad = True
    wb.active = 0
    wb.save(path)


def write_csv(p, path):
    labels_max = max([len(i.get("labels", [])) for i in p["issues"]] + [1])
    rows = [["Issue Id", "Issue Type", "Summary", "Parent", "Priority", "Story Points", "Sprint", "Status"]
            + ["Labels"] * labels_max + ["Component", "Fix Version", "Description"]]
    ids = {}
    for n, e in enumerate(p["epics"], 1):
        ids[e["code"]] = n
        rows.append([n, "Epic", e["name"], "", "", "", "", "To Do", e["code"].lower()] + [""] * (labels_max - 1)
                    + ["", e.get("version", p.get("version", "v1.0")), e.get("description", "")])
    for n, i in enumerate(p["issues"], len(p["epics"]) + 1):
        labs = list(i.get("labels", []))
        body = i.get("description", "")
        if i.get("ac"):
            body += "\n\n*Acceptance Criteria*\n" + "\n".join("* " + a for a in i["ac"])
        rows.append([n, i["type"], i["summary"], ids[i["epic"]], i["priority"], i["points"],
                     sprint_name(p, i["sprint"]) if i.get("sprint") else "", i.get("status", "To Do")]
                    + labs + [""] * (labels_max - len(labs))
                    + [i.get("component", ""), p.get("version", "v1.0") if i.get("sprint") else p.get("later_version", "v1.1"), body])
    with open(path, "w", encoding="utf-8-sig", newline="") as fh:
        csv.writer(fh).writerows(rows)
    # read it back the way the importer will
    back = list(csv.reader(open(path, encoding="utf-8-sig")))
    known = {r[0] for r in back[1:]}
    assert all(len(r) == len(back[0]) for r in back), "rows of different length"
    assert all(not r[3] or r[3] in known for r in back[1:]), "a Parent points at no Issue Id"
    order = {r[0]: k for k, r in enumerate(back)}
    assert all(not r[3] or order[r[3]] < order[r[0]] for r in back[1:]), "a child comes before its epic"
    return len(rows) - 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan")
    ap.add_argument("--out", default=".")
    ap.add_argument("--check", action="store_true", help="check the plan only")
    a = ap.parse_args()
    p = load(a.plan)
    errs, warns = check(p)
    for w in warns:
        print("WARN  " + w)
    for e in errs:
        print("ERROR " + e)
    for k in range(1, len(p["sprints"]) + 1):
        items = [i for i in p["issues"] if i.get("sprint") == k]
        s, e = sprint_dates(p, k)
        print("%s  %s – %s  %2d issues  %3d SP  %s" % (sprint_name(p, k), s.strftime("%d/%m"), e.strftime("%d/%m"),
                                                    len(items), sum(i["points"] for i in items), p["sprints"][k - 1]["name"]))
    later = [i for i in p["issues"] if not i.get("sprint")]
    print("backlog after the plan: %d issues, %d SP" % (len(later), sum(i["points"] for i in later)))
    if errs:
        sys.exit("PLAN FAILED: %d error(s)" % len(errs))
    if a.check:
        print("PLAN OK")
        return
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    xlsx, csvp = out / (p["file"] + ".xlsx"), out / (p["file"] + "-jira.csv")
    try:
        write_xlsx(p, xlsx)
        n = write_csv(p, csvp)
    except PermissionError as e:
        sys.exit("cannot write %s: it is open, most likely in Excel. Close it without saving, then run again." % e.filename)
    print("write %s\nwrite %s (%d rows, UTF-8 with BOM)\nPLAN OK" % (xlsx, csvp, n))


if __name__ == "__main__":
    main()
