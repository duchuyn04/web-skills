---
name: sprint-plan
description: Plan the build of a prototype or spec as Scrum sprints and export it as an Excel workbook (roadmap, sprints with goals, Jira-style backlog) plus a CSV that Jira imports with epics linked to their issues. Use when the user asks for a project plan, sprint plan, product backlog, roadmap, kế hoạch dự án, kế hoạch sprint, chia sprint, backlog chuẩn Jira, file Excel kế hoạch, import Jira, or how long building a prototype will take. Works best after app-ui, bpo-landing-builder or ecommerce-builder made the prototype, but any spec will do.
compatibility: Needs Python 3.9+ with openpyxl. Checking the workbook in Excel (optional) needs Windows with Excel.
metadata:
  version: "1.0.0"
---

# Sprint plan

You turn what the prototype shows into a plan someone can run: epics, issues sized in points, one-week sprints
with a goal each, testing before release, and files that open in Excel and import into Jira. You write
`plan.json`; `scripts/make_plan.py` checks it and writes the files, so the layout, the formulas and the Jira
format never depend on you.

`SKILL` below means the folder that holds this file.

## Step 1: Read what will be built

Read the prototype and the spec before planning: every screen and state (an app-ui prototype lists them in
`kit/proto-nav.js` and `screens.html`), the modules and their order of dependence, the stack, the rules that
cost time (security, realtime, AI calls), and what is already decided or still open. Each epic and issue must
come from something you read; name the screen or spec section in the description.

## Step 2: Settle the frame (ask once, with guesses)

Ask in one message, each with your guess, only what the request and the project do not answer:

| Question | Default when the user does not say |
|:---|:---|
| Who reads it | The user themself: Jira terms, technical words allowed, three sheets. A manager who is not technical gets an `overview` block in plain words (see `references/plan-rules.md`) |
| Start date and length | Next Monday; the length the scope needs at the stated capacity, inside the user's range |
| Team and capacity | Ask; with AI-assisted coding a developer pair often lands 25 to 30 points a week, but say it is a guess to recalibrate after sprint 1 |
| Epic naming | Whatever the team uses; record it in `epic_naming` so the script enforces it (for example "Quản lý", "Danh sách") |
| Release policy | Production exists from sprint 1 and every finished module deploys to it (`deploy_every_sprint`); the public launch is a later date |

A user who says the plan is for themself wants no hand-over work, no training tasks, no glossary.

## Step 3: Write plan.json

Follow `references/plan-rules.md`: the schema, how to cut epics and issues, sizing, sprint goals, testing and
release. `examples/webnhanh.plan.json` is a full plan (62 issues, 7 sprints) to copy the shape from.

## Step 4: Check and build

```
python SKILL/scripts/make_plan.py plan.json --check
python SKILL/scripts/make_plan.py plan.json --out <folder>
```

Fix every ERROR in the plan, not in the script. Read every WARN and either fix it or keep it with a reason in
the report (a sprint over capacity is a decision, not a typo). The run prints each sprint's points; balance them
before you build.

If the script says a file is open, the user has it in Excel: ask them to close it without saving and run again.
Never write a second copy under a new name to get around it, and never kill their Excel.

## Step 5: Look at the workbook

On Windows with Excel, open the workbook through COM read-only, set four Status cells to Done, recalculate, and
check that the sprint and epic totals move; export to PDF and look at the roadmap and backlog pages. Without
Excel, reopen it with openpyxl and check the formulas are there. Do not open the CSV in Excel and save it: Excel
rewrites the encoding and breaks Vietnamese.

## Step 6: Report

In the user's language:

- where the two files are
- every choice you made for them, one line each: start date, sprint length, capacity, epic naming, release policy
- points per sprint in one table, and what stays in the backlog after the plan
- how to import the CSV (from `references/plan-rules.md`, "Jira import"), including what you have not tested
- that the estimates are yours and the team should re-estimate at the first planning

## Reference files

- `references/plan-rules.md`: plan.json schema, epics and issues, sizing, sprint goals, testing and release, the overview block, Jira import, the Excel pitfalls the script already handles
- `examples/webnhanh.plan.json`: a complete plan for an app-ui prototype with 16 screens
