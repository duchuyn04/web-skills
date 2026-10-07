# Plan rules

## plan.json

```json
{
 "project": "Webnhanh",            "key": "WEB",               "file": "Ke-hoach-Webnhanh",
 "lang": "vi",                      "start": "2026-10-12",      "sprint_weeks": 1,
 "release": "2026-11-24",           "capacity": 30,             "version": "v1.0", "later_version": "v1.1",
 "epic_naming": ["Quản lý", "Danh sách"],
 "deploy_every_sprint": true,
 "epics":   [{"code": "SETUP", "name": "Quản lý hạ tầng và CI/CD", "color": "6554C0"}],
 "sprints": [{"name": "Trang chủ, nhận yêu cầu, đăng nhập", "goal": "Khách gửi được yêu cầu ... Production tự deploy khi test xanh."}],
 "milestones": [{"date": "2026-11-13", "name": "Code freeze", "note": "Chỉ nhận bug fix.", "color": "FF8B00"}],
 "issues": [{"epic": "SETUP", "type": "Task", "summary": "CI/CD: test xanh thì tự deploy production",
             "description": "...", "priority": "Highest", "points": 2, "sprint": 1,
             "ac": ["Pipeline đỏ thì không deploy", "Deploy xong trong 10 phút"],
             "labels": ["devops", "deploy"], "component": "infra"}],
 "overview": {"subtitle": "...", "lines": [["Sản phẩm", "..."]]}
}
```

`key` becomes the issue keys (`WEB-1`) and sprint names (`WEB Sprint 1`). `sprint: null` keeps an issue in the
backlog after the plan (it gets `later_version`). `overview` is optional (see below). `color` is optional.

## Epics and issues

- One epic per module or area a person would name: the order screens, the admin, sign-in, the build pipeline,
  testing, release. Follow the spec's modules when there is a spec; never one epic per screen.
- Epic names follow the team's convention in `epic_naming`. Without one, name the area a user sees, not the code.
- Story: something a user can do, written "Là [ai], tôi muốn [gì], để [vì sao]" (or the English form). Task:
  work no user sees (setup, CI, a test campaign, a deploy). Bug: only a planned fix buffer.
- Every story has acceptance criteria a tester can check without asking: numbers, states, what must not happen.
  Pull them from the prototype's states (empty, error, quota-out, expired) and the spec's rules.
- Labels are single words (`frontend`, `backend`, `qa`, `devops`, `deploy`); components are the spec's modules.
- Summary under 255 characters, says the outcome, not the activity ("Trang Tài khoản", not "Làm trang tài khoản").

## Sizing and sprints

- Points on the Fibonacci scale 1, 2, 3, 5, 8 (13 means split it). They compare work, they are not hours.
- One-week sprints when the team codes with AI help: modules land in days, and a weekly demo catches drift.
- Fill each sprint to the capacity, not over; the last sprint before release stays light.
- Order: what earns money or unblocks others first (lead capture before the tool, shared foundations before
  features), riskiest unknowns early (the AI loop, realtime), polish late.
- Each sprint goal is one or two sentences that say what works at the end, checkable at the demo
  ("Sales handle one lead from New to Won in the admin"), never a list of tasks.

## Testing and release

- Testing runs in every sprint (each story is tested against its criteria before Done) and a whole sprint
  before release is testing: end-to-end, devices, security (one user cannot read another's data, admin APIs
  refuse normal users, no secret in the browser), load, AI quality on sample inputs, a few real users, a bug buffer.
- With `deploy_every_sprint`, production with HTTPS, backup and CI/CD is built in sprint 1, and each sprint has
  one task labelled `deploy`: "Deploy production sprint N: <the modules that finished>", with a smoke test and a
  day of log watching. Before the public launch, production is closed with a password; launch day opens it.
- Milestones: code freeze at the end of the last feature sprint, a go/no-go meeting at the end of the testing
  sprint with its conditions in the note, the public launch on a Tuesday (not a Friday).

## Overview for a manager

Only when someone who is not technical reads the plan. `overview.lines` holds a few rows in plain words: what
the product is, what exists already (the prototype), why the length is enough, the order of work. Each sprint
may carry an `outcome`: what the manager sees at the demo, in plain words, used instead of the goal on that
sheet. Keep technical words out of it (no API, deploy, staging); keep Jira terms in the other sheets.

## Jira import

The CSV is UTF-8 with a byte order mark. Steps for Jira Cloud: Settings, System, External system import, CSV.

- Map `Issue Id` to Issue Id and `Parent` to Parent; Parent holds the epic's Issue Id, not its key, and epics
  come first in the file. This is how the Jira Cloud importer links children to epics.
- Map both `Labels` columns to Labels. `Story Points` is "Story point estimate" in team-managed projects.
- Sprint: create the sprints with the exact names (`WEB Sprint 1` ...) before importing, or leave the column
  unmapped and drag issues into sprints after. Whether the importer creates missing sprints is not verified.
- Components may need to exist in the project first.
- Try the first import on a scratch project. Say in the report that the import itself was not tested by you.

## Pitfalls the script already handles

Kept here so a change to the script does not bring them back:

- Conditional-format fills need `start_color` and `end_color`; a plain `fgColor` fill shows nothing.
- A `COUNTIFS(..., "Sprint*")` also counts the header cell named Sprint; match full sprint names instead.
- An epic total that sums its own column over the whole column is a circular reference; start the range below
  the epic rows.
- A CSV without a byte order mark opens in Excel with broken Vietnamese.
- Writing over a workbook the user has open in Excel fails; the script says so instead of writing elsewhere.
- If a chart is ever added: openpyxl bar charts hide both axes unless `delete = False`, and a chart title
  overlaps a legend placed on top.
