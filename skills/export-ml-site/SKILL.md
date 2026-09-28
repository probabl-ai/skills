---
name: export-ml-site
description: >
  Package JOURNAL, exploratory data analysis markdown, and design notes into an offline
  MkDocs site opened via report.html at the workspace root. Embeds existing notebook HTML
  companions in their associated reports. Never executes Python. Trigger
  when the user asks for a website, mkdocs, or documentation site.
---

# Export ML Site

## Human-facing prose

Details: `setup-workspace` `references/human_facing_prose.md`.
Tell the user to open `report.html`. Do not quote `site init` /
`site build` as something they should run.

The site is a derived index of files other skills already write.
Markdown is the report: its figures, TableReport HTML, and existing
converted notebooks (`<stem>.nb.html`, written only by
`export-ml-notebook` with `notebook convert --html`) are embedded
inline. HTML viewers have open-separately and fullscreen controls.
Each experiment design note has one `## Notebooks` section:
evaluation first, then audit; a missing viewer is omitted.
Derived HTML and PNG viewers under `scratch/results/<stem>/`
(report, checks, metrics, plus extra Display slugs) may be copied
into the staged docs. Core Results headings are Report overview /
Checks / Metrics. Extra slugs use `<!-- results-embed: <slug> -->`
under `## Results` **or** `## Method` (`pipeline` is the Method
diagram: unfitted after construct, fitted after evaluate).
Only Markdown and already-generated notebook/HTML viewers are
exported. The gitignored serialized Skore `reports/` directory is
private runtime state and is never copied into the site.
On desktop, site pages are in the top bar (experiments in a
scrollable dropdown) and the page contents are in a collapsible
left rail beside a 1200px report column. Mobile uses a drawer.

## Sequence

1. `python -m skore_skills status`. Read `policy.site`.
2. If `policy.site` is `null`: persist
   `python -m skore_skills policy set site true`. Do not
   AskUserQuestion. Then load `add-python-package` for
   `mkdocs-material` (agent) then
   `python -m skore_skills site init`. Continue to build.
3. If `policy.site` is false: say the documentation site is
   off; offer to turn it on. Do not init or build until it is
   true.
4. If this is the first site turn, run `site init` (gitignore
   only). Later turns only `site build`.
5. `python -m skore_skills site build`. Do not run
   `notebook convert`. Name a build error; the markdown sources
   remain the record. Tell the user to open `report.html` at
   the workspace root (double-click; no server). Do not send
   them to the markdown instead. Stage owners that just ran
   `site build` must name that launcher (and the stage page:
   `html/data_analysis.html` or `html/<stem>.html`) in the same
   User-facing close.

## Preview before markdown-review gates

Stage owners that just wrote durable markdown and will ask the
user to approve or continue must rebuild the site **before**
that AskUserQuestion / consent stop — not only at End of turn.

1. If `policy.site` is true and this skill is installed, run
   `python -m skore_skills site build`. Skip in one line
   otherwise. Name a build error; do not fail the gate.
2. In the same message as the gate, **Open these**: the `.md`
   path, plus `report.html` and the stage page
   (`html/<stem>.html`, `html/data_analysis.html`, or the home
   page for `JOURNAL.md`) when the build ran. A file link is an
   addition, never the context.
3. Do **not** `notebook convert`, `git end-turn`, or `git commit`
   on this preview rebuild. Do not re-run `site init`.
4. Convert + a later `site build` remain End of turn after the
   user **closes** the stage.

## Stop conditions

- Do not `git commit` or `git end-turn`.
- Do not `pixi add` / `uv add`; load `add-python-package`.
- Do not convert or execute `# %%` scripts.
- Do not copy or link serialized files from gitignored `reports/`.
- Skip in one line if this skill is not installed.
