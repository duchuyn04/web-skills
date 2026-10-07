# web-skills

Claude Code plugin with four skills for websites and app prototypes. The agent picks the skill from what you ask for; you do not call them by hand.

| Skill | Ask for | You write | You get |
|:---|:---|:---|:---|
| `bpo-landing-builder` | a landing page for a BPO, outsourcing, contact center, offshore staffing or AI data company | `page.json` | a single-page site built from pre-made, animated sections |
| `ecommerce-builder` | an online shop for electronics (phones, laptops, TVs, appliances, accessories) | `shop.json` | storefront, cart, checkout, order tracking, customer account and an admin dashboard, in one of five styles |
| `nail-salon-builder` | a website for a nail salon, nail bar or nail art studio with online booking | `salon.json` | price list, nail gallery, booking with technician and time slots, booking lookup, branches, offers and a salon admin (day calendar by technician, appointments, customers, services, reports), in one of four styles |
| `app-ui` | screens inside an app or admin area: dashboard, tables, lists, record detail, multi-step forms, settings, sign in | a short brief, then HTML with kit classes only | a clickable prototype of every screen in every state (empty, loading, error...), linted and checked in the browser, with a "View prototype" navigator on every page |

Examples of requests and the skill they trigger:
- "Làm landing page cho công ty outsourcing ở Đà Nẵng" uses `bpo-landing-builder`.
- "Làm web bán điện thoại có trang quản trị" uses `ecommerce-builder`.
- "Làm web tiệm nail có đặt lịch online và trang quản lý lịch hẹn" uses `nail-salon-builder`.
- "Dựng prototype các màn hình quản lý đơn và form tạo dự án" uses `app-ui`.

## Install

In Claude Code:

```
/plugin marketplace add duchuyn04/web-skills
/plugin install web-skills@web-skills
```

Other agents (Codex, Cursor and others) read plain skill folders. Copy or link the folders in `skills/` into the agent's skills directory (for example `.agents/skills/` or `.claude/skills/`), or use the `skills` CLI:

```
npx skills@latest add duchuyn04/web-skills
```

## Requirements

Python 3.9 or newer. `ecommerce-builder` and `nail-salon-builder` need `jinja2`; `app-ui` needs nothing beyond Python for its scripts. Browser checks need Python Playwright and Edge or Chrome. `pip install -r requirements.txt` installs both.

## Layout

```
.claude-plugin/   plugin.json and marketplace.json
skills/
  bpo-landing-builder/   SKILL.md, scripts, templates, examples, references
  ecommerce-builder/     SKILL.md, scripts, templates, examples, references
  nail-salon-builder/    SKILL.md, scripts, templates, examples, references, tests
  app-ui/                SKILL.md, kit (tokens, CSS, JS, icons, prototype navigator), recipes, gallery, scripts, references
```

Each skill keeps its own README or SKILL.md with the full workflow.

## Use with your own LLM

A skill is a folder with a `SKILL.md` (frontmatter `name` and `description`, then instructions) plus scripts and assets. To use them outside Claude Code:

1. Read `name` and `description` from every `skills/*/SKILL.md` and list them in the system prompt.
2. When the model picks a skill, load that `SKILL.md` into context.
3. Give the model a shell tool in a sandbox so it can run the skill's scripts.

With the Claude Agent SDK you can load the folder directly as a local plugin instead.

## License

Released under the [MIT License](LICENSE). You may use, modify and redistribute this plugin, including for commercial work, as long as the copyright and license notice stay with it. The software is provided without warranty.

Websites generated with these skills belong to you. Check the licenses of any third-party fonts, images or libraries a generated site loads.
