# Human-facing prose

The user sees **data science**, not the skills framework.

**Agent-internal** (SKILL.md, tool calls, reasoning): skill ids,
`G-*` keys, HITL, `python -m skore_skills …`, `AskUserQuestion`.
**User-visible** (project files, chat, questions, closes): this
data or experiment — what we will do, what a choice authorizes,
what a figure/table/result shows.

## Project files

Text in the **user project** must earn its place as data science:
what the pipeline or analysis is doing, what a figure/table/report
section shows for **this** data or experiment, or an insight,
caveat, or modelling implication.

It must **not**:

- describe the skills framework, skill ids, or HITL/gates
- mention `skore_skills`, `python -m …`, `cells run`, `site build`,
  `notebook convert`
- explain how an output was produced
- document API surface, version floors, or locator recipes

**Allowed exceptions** (machine contracts, not prose):

- `<!-- results-embed: <slug> -->`
- `# %%` / `# %% [markdown]` cell markers
- substitution tokens (`<stem>`, `<pkg>`, `REPORT_ID = "..."`)
  without a tutorial comment

Authoring hints belong in SKILL.md and `references/`, not in the
artifact. `python -m skore_skills style` is ruff only; it does not
rewrite comments.

## Chat and questions

Surfaces: assistant replies, `AskUserQuestion` (title, option
labels, descriptions), the 2–4 lines of gate context before a
pick, and the User-facing close **narrative**.

Same bans as project files. Also do not:

- say “loading skill X” or list catalog ids as menu labels
- name HITL, “gate”, or `G-*` tokens in the question
- quote `python -m skore_skills`, `env add`, `cells run`,
  `site build`, or `notebook convert` as something the user
  should run or choose

Run those commands yourself. Tell the user the **work**: explore
this table, approve this design, evaluate on the full dataset.

**Allowed exceptions** (not the story):

- Unmanaged install: show the manager line from print-only
  stdout (`pixi add …`, `uv add …`, `pip install …`) or a
  plain-language intent. Never paste the wrapper CLI.
- Trailing close tokens: `G-REPORT-LOCATOR` / `G-AUDIT-FINDING`
  (or `n/a — …`) after the narrative. Index strings, not prose.
- File paths and `report.html` / `html/<stem>.html` links.

Gate context stays 2–4 lines of **scientific** authorization
(what the pick allows on this data/experiment, facts echoed
inline, what each option does). A file link is an addition,
never the context.

Examples:

- Ask: **What should the Python import name be?** — not
  “Resolve G-PKG-NAME”.
- Option: **Explore the data** — not ``explore-ml-data``.
- Close: findings + `report.html` — not “I ran `site build`”.
