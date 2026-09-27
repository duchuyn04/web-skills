# Mobbin references

Mobbin (mobbin.com) is a curated library of screens and website sections from well-designed products. This file records what was taken from it for the section library, and how to use it again when the library grows.

## What Mobbin has, and what it lacks

Mobbin does not index BPO companies. Searches for Concentrix, Teleperformance or TaskUs return other products. It does index companies next to the BPO market, with stronger design than most BPO sites:

| Neighbour | Close to archetype | Useful for |
|:---|:---|:---|
| Deel, Upwork | `offshore-staffing` | country coverage cards, per-person pricing, comparison with other providers, cost calculators |
| Intercom, Zendesk, Front, Giga | `enterprise-cx`, `cx-voice-sales` | human support sections, review badges, leadership grids |
| Airtable, Lattice, monday.com | all | integration and tool grids |
| Miro, Tines, Maze, Faire | all | team grids, careers sections |

Mobbin is a source of layout and interaction patterns only. The copy on these sites is written for software products and often uses phrasing the house style bans; follow `industry-voice.md` for wording. Do not copy screenshots, logos or text from Mobbin into a page or into this skill.

## Sections built from the study

Links point to the reference sections on Mobbin (a Mobbin account is needed to open them).

| Section | Pattern taken | References |
|:---|:---|:---|
| `comparison-table` | Company column tinted, tick and cross rows, notes under marks; stacked cards on phones | [Deel](https://mobbin.com/sites/sections/3fa1b67f-d6bb-4898-b7c6-d1e13307781f), [Front](https://mobbin.com/sites/sections/887ca35c-b1cf-4975-82af-c178a50ff4a4), [MindMarket](https://mobbin.com/sites/sections/753bc368-0401-48d4-b4e5-2efece65adca), [Firecrawl](https://mobbin.com/sites/sections/75ae8fde-bf77-478b-8b46-c4e2f7566af0) |
| `awards-strip` | Row of shield badges (issuer band, award, year) plus a star rating line; optional dark card | [Mural](https://mobbin.com/sites/sections/24e120b0-9369-49db-a009-ab3e1d1a754e), [ClickUp](https://mobbin.com/sites/sections/1dcec600-bc14-4b26-8e7a-47220d9d7a7d), [Sana](https://mobbin.com/sites/sections/7a8c2178-cea1-4a2d-b91d-780654319e23), [7shifts](https://mobbin.com/sites/sections/582ec4b5-6580-4c06-973b-8d531704e4cb) |
| `team-grid` | Square portraits on tinted tiles, name and role, LinkedIn button | [Miro](https://mobbin.com/sites/sections/28f34e76-1c4c-40e5-9148-b7936ec729fd), [Tines](https://mobbin.com/sites/sections/b1fea55a-b18b-4f6b-ba96-05960cabbb77), [Intercom](https://mobbin.com/sites/sections/fc292fd5-ab37-469b-b09b-dc378471521c) |
| `careers-band` | Centered invitation with office photos around it, open-positions count | [Tines](https://mobbin.com/sites/sections/cb78af06-910b-40c4-91a6-f8a7f49bbc9d), [Faire](https://mobbin.com/sites/sections/56add723-35e9-4ed9-b91f-17f17cc03995), [Maze](https://mobbin.com/sites/sections/8f55958e-a1dc-4732-9fdc-bed5c0b73f83) |
| `tool-stack` | Heading beside a grid of tool chips (mark, name, category) in offset rows | [Airtable](https://mobbin.com/sites/sections/978d622a-0a04-44c2-be6f-6a91eacebcff), [Lattice](https://mobbin.com/sites/sections/2006d3b7-193b-4953-82c6-561f459bf832), [Customer.io](https://mobbin.com/sites/sections/363f8cb4-072f-4e38-94e3-24e24e5f2573) |
| `steps-row` | Three or four step cards with large numerals | [PayPal](https://mobbin.com/sites/sections/fc3046a5-a7dc-4377-87cc-d90bc9fd1848), [ClassPass](https://mobbin.com/sites/sections/193363c3-3373-49a5-a1d0-00ff01f07b4d) |
| `country-cards` | Tall photo cards per country at staggered heights, service tags, round flag | [Deel](https://mobbin.com/sites/sections/59bb9d63-e615-4175-8851-3019fb58f0c5) |

Adaptations for BPO pages:

- Award badges are drawn in the brand colours with the issuer's name as text. Third-party award artwork and logos are trademarks and are not bundled; a client may add its own badge files later as a custom section.
- Tool chips show a letter mark by default. A tool's real logo appears only when the client supplies the file (`logo` field).
- Flags are the skill's SVG flags, never emoji.

## Using Mobbin for the next library update

Mobbin is a maintainer tool. Page builds do not call it, so a page looks the same whether or not the agent has Mobbin connected.

1. Pick a gap: a block real BPO sites use (see the proof table in `industry-voice.md`) that the library lacks.
2. Search sections on Mobbin (MCP tool `search_sections`) with a plain description of the block, for example "comparison table against in-house hiring". Name a neighbour company to narrow results ("Deel pricing per employee").
3. Keep 3-5 references that agree on a structure. Note the structure, spacing and interaction, not the copy.
4. Build the section from tokens in `base.css` like any other variant (schema, html, css), add it to an example page, then build, lint, QA and run `make_catalog.py`.
5. Add a row to the table above with the reference links (`mobbin_url` from the search result). Mobbin image links expire after 30 days, so do not link to images.
