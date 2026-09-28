---
name: manage-ml-backlog
description: >
  Canonical backlog loop step. Record an experiment outcome in
  History and triage idea files into Backlog rows. Also
  supports the model-entry selection mode: show real B<N> rows
  supplied by the deterministic CLI and consume one into a
  proposal. Trigger after audit, when a run finishes, when the
  user asks what to try next or to triage idea files, or when model-ml-pipeline routes its
  Backlog choice here. This is cadence, not a methodology owner.
---

# Manage ML Backlog

Replace iterate-as-cadence. Do not own setup, exploratory data
analysis, build, smoke,
evaluate, or audit methodology.

## Human-facing prose

Details: `setup-workspace` `references/human_facing_prose.md`.
JOURNAL rows, design-note Status / Results, and `#` comments
describe **this** experiment's outcome — not the skills framework,
the CLI, or the command that produced an output. Questions and
replies use the same data-science language — not skill ids, `G-*`
names, or the wrapper CLI. `<!-- results-embed: … -->` is a site
marker. Authoring hints stay in this skill. `style` is ruff only.

The CLI writes JOURNAL with four sections in order: Status, Data
understanding, History, Backlog. History and Backlog start as
header-only tables. Column contracts stay here (Stem, Intent,
Status, Headline result, Report, Design note; `#`, Item, Source).
Do not put those contracts back into HTML comments in the file.

## Model-entry selection mode

When `model-ml-pipeline` calls with the `backlog` array from
`python -m skore_skills model choices`:

1. Present exactly those `B<N>` rows in their returned order and
   AskUserQuestion for one pick. Carry each row's Item and Source
   as the option context, and say in 2–4 lines what the pick
   authorizes (a Proposal, then a design note to approve) and what
   it does not (no model code yet). A file link is an addition,
   never the context. Do not rescan into a different
   menu and do not add an idea.
2. Turn the selected row's Item + Source into a Proposal. Ask only
   for missing shaping facts; do not invent a Method from a
   one-line item.
3. Return the confirmed Proposal to `model-ml-pipeline`. After the
   model stage creates and populates the design note, remove only
   the selected Backlog row and add the planned History row.
   Preserve every other stable B<N> index.

This mode does not require a report/audit digest and does not run
the outcome-recording procedure below. Empty Backlog is a routing
error: return to `model-ml-pipeline`; do not fabricate B1.

## Record-outcome mode

When `model-ml-pipeline`, `evaluate-ml-pipeline`, or
`audit-ml-pipeline` calls at end of turn with the normalized
G-REPORT-LOCATOR, optional headline, and G-AUDIT-FINDING. This is
the only path that records an outcome without a full backlog turn.
Audit may have been skipped; the locator remains required and the
finding becomes `n/a — audit not run`. If the caller omitted the
locator, run `python -m skore_skills loop locator --stem <stem>`
and paste JSON `locator`. If it omitted the finding, run
`python -m skore_skills audit finding --stem <stem>` (`stop` →
`n/a — audit not run` / `n/a — audit digest unavailable`). Do not
rephrase either string.

Run Procedure steps 1-3 and nothing else:

1. Step 1 — `python -m skore_skills status`; require an approved
   stem.
2. Step 2 — read `journal/JOURNAL.md`; scaffold the index if it is
   missing.
3. Step 3 — update the matching History row and design-note Status
   block from the digest or user-supplied headline when available.
   Paste G-REPORT-LOCATOR and G-AUDIT-FINDING verbatim into their
   separate Status lines. Also refresh the `journal/JOURNAL.md`
   Status rows `Last experiment` and `Last result`. Insert or replace `## Results`
   between Status and Notebooks from digest text, not HTML.

Then return to the caller. Do not read `journal/ideas/` and do
not open the idea-triage menu — the caller did not ask what to
try next.

Do not dispatch `audit-ml-pipeline` in this mode; the digest is
already in hand and dispatching would bounce back here. Do not run
this skill's End of turn either: the caller owns convert / site /
`git end-turn` and the User-facing close. This mode writes
History; it does not replace the caller's chat close.

The Procedure guards still bind. Never mark `done` while smoke is
red, and never invent a metric — no digest and no user-supplied
value means use `n/a`, not a guess. Never construct a missing
backend URL. Record `n/a — backend did not expose a locator` in
both markdown destinations when the digest has no authoritative
locator.

## Procedure

1. Run `python -m skore_skills status`. When recording a done
   outcome, run
   `python -m skore_skills design consent --stem <stem>`.
   `ask` / `stop` → do not mark `done`. Also require green smoke
   evidence and a normalized report locator. An audit digest is
   optional. G-AUDIT-FINDING is required as one of: the value
   returned by audit, `n/a — audit not run`, or
   `n/a — audit digest unavailable`.
2. Read `journal/JOURNAL.md` History and Backlog. If the index is
   missing, run `python -m skore_skills scaffold --journal`. Do
   not write or paste the file. The CLI writes four sections:
   Status, Data understanding, History, and Backlog. If that
   command cannot run this turn, name it and stop. After the file
   exists, edit the existing History and Backlog tables (columns:
   Stem, Intent, Status, Headline result, Report, Design note; and
   #, Item, Source). A planned History row uses `n/a` in Report.
   Stable `B<N>` indices. Do not renumber on removal.
3. If recording a run: copy the headline metric from the audit
   digest or the user's value. Do not invent numbers. With no
   digest and no user headline, skip the headline in one line and
   leave the History status unchanged. Do not write `done` with
   headline `n/a`. Update the
   matching History row (`planned` → `done` only if smoke passed
   and a headline result exists).
   Headline metric remains the source for History and Last result;
   never substitute G-AUDIT-FINDING for performance. Copy the
   digest's persisted-report locator into the History `Report`
   cell and the design note's `Persisted report` Status line.
   Paste that string verbatim; do not paraphrase it as
   "normalized" or rewrite the Hub URL. If
   the digest has none, write
   `n/a — backend did not expose a locator` in both places; do not
   derive or guess a URL. Copy G-AUDIT-FINDING verbatim into the
   design note's `Audit findings` line. Audit skipped →
   `n/a — audit not run`; missing/errored digest →
   `n/a — audit digest unavailable`. Update the rest of the
   design-note Status block the same way. Then insert or replace
   `## Results` in the design note, between `## Status` and
   `## Notebooks`. Summarize from the audit digest — its cell
   outputs carry `repr(report)`, `## Checks summary`, and
   `## Metrics summary` as text. With no audit this turn, fall back
   to `scratch/results/<stem>/report.txt`, which evaluate writes.
   Write `### Report overview` from the report text, then
   `### Checks` then `### Metrics` when those sections exist.
   Evaluation-only (audit skipped): Report overview only — do not
   invent Checks or Metrics subsections. After Metrics, add one
   `###` subsection per extra Display cell the audit appended, using
   a human title and a `<!-- results-embed: <slug> -->` comment with
   the accessor name as `<slug>` so site build can inject the
   viewer. Each subsection is 2–4 sentences of context from that
   cell's output; do not copy G-AUDIT-FINDING, do not parse
   `*.html`, and do not paste iframes (site build injects those). If
   no subsection has a source, skip the Results section.
4. Idea triage, separate from record-outcome. Read
   `journal/ideas/*.md`. Drop a file whose Source is already a
   Backlog row. For each remaining file, ask promote / dismiss /
   leave. Promote appends a stable `B<N>` row (Item from Question,
   Source copied verbatim) and deletes the file. Dismiss deletes
   the file. Leave keeps it. Do not create a design note here.
   An empty folder is a one-line skip: there are no idea files to
   triage, and it does not fabricate `B1`. The only follow-up is
   offering to shape an idea or search the literature when those
   skills are installed. Do not load either skill, and do not start
   a search or a shaping menu, until the user picks one. Missing
   skill → one-line skip; do not invent that skill's search or
   shaping steps. After the user picks, that skill writes the idea
   file and returns here; triage the new file in this same mode.
   When the user picks an existing `B<N>` to draft, return that
   row to `model-ml-pipeline`, which can create its design-note
   shell with
   `python -m skore_skills scaffold --journal --stem <NN_short_name>`.
   Do not draft that template in this backlog turn.

## Stop conditions

- Do not design or implement the next experiment in this turn.
- Do not dispatch setup or audit by skill id. Returning a
  selected row or confirmed proposal to `model-ml-pipeline` is
  required.
- In model-entry selection mode, do not invent a Backlog row or
  remove it before the paired design note exists.
- Do not invent metrics.
- Do not derive, shorten, or merge G-AUDIT-FINDING with the
  headline metric. Copy each into its owned field.
- Do not parse `scratch/results/<stem>/*.html` when writing
  `## Results`. Summarize from the digest, or from `report.txt` on
  the evaluation-only path.
- Do not paste a `JOURNAL.md` body or recreate the index from
  memory.
- Do not mark `done` while smoke is red.
- Design approval is owned by `model-ml-pipeline`; this skill only
  returns a confirmed proposal or selected Backlog row.

## End of turn

If `policy.site` is true, `export-ml-site` is installed, run
`python -m skore_skills site build`. Do not run
`notebook convert`. Skip
in one line otherwise. Name a build error; do not fail the
backlog turn.

Run `python -m skore_skills git end-turn --stage backlog`. If JSON
`action` is `invoke`, load `persist-ml-git` only if
`status.skills.persist-ml-git` is true and stop; that skill
returns to triage. If persist is missing, name the pending
`staged` paths and stop. Otherwise load `triage-ml-task` only if
`status.skills.triage-ml-task` is true; else stop. Do not run
`git commit` in this skill.
