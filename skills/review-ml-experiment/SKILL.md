---
name: review-ml-experiment
description: >
  Post-evaluate review. Gate the expensive skore-check audit, then
  write one markdown idea file per candidate. Trigger after a
  successful evaluate, on "review this stem", or when review consent
  is Review or proceed. Do not write JOURNAL.md or a design note.
  Do not run cells run until the user accepts the audit cost.
---

# Review ML Experiment

Optional loop step after evaluate. Record-outcome stays with the
caller. This skill writes idea files only.

## Human-facing prose

Details: `setup-workspace` `references/human_facing_prose.md`.
The Review / Skip / Stop question and cost preview describe
reading this report and writing follow-up ideas — not skill ids,
`cells run`, or the wrapper CLI.

## Procedure

1. Run `python -m skore_skills status` and
   `python -m skore_skills review consent --stem <stem>`. Treat
   JSON `action` as authoritative.
   - `stop` — no `scratch/results/<stem>/report.html`. Name that
     file and stop. Do not audit.
   - `ask` — report exists, digest does not. Emit the cost preview
     below, then **AskUserQuestion**: Review (Recommended) / Skip /
     Stop. "Audit it" on a first run is not consent. If this turn
     already answered **Review**, do not ask again.
   - `proceed` — digest already on disk. Do not re-run checks.
     Refresh idea files from the existing digest.
2. **Skip** — write no idea files. Return
   `n/a — audit not run` so the caller can record-outcome.
3. **Stop** — do not audit and do not record-outcome. The persisted
   report stays. Load `triage-ml-task` when
   `status.skills.triage-ml-task` is true.
4. **Review**, or `proceed` for idea refresh: load
   `audit-ml-pipeline` only if `status.skills.audit-ml-pipeline`
   is true. On **Review**, that skill runs `cells run` (consent
   stays `ask` until the digest exists; the Review answer is what
   starts it). On `proceed`, do not `cells run`. Missing audit
   skill → one-line skip; return `n/a — audit not run` and write
   no idea files. Do not open the Project or call `report.*` here.
5. Read the design note, the EDA summary, the last History row,
   and the digest. One candidate per `Issues:` / `Tips:` line.
   A methodological gap the design note named and this run did
   not test is another candidate. A user idea or a literature
   query is not a candidate here: after this skill returns,
   `shape-user-idea` or `search-ml-literature` writes that file
   when the user asks. Load `research-ml-practice` only if
   `status.skills.research-ml-practice` is true and an audit or
   design candidate needs sources; otherwise one-line skip. Do
   not invent papers, metrics, or a winner.
6. Write one file per candidate at
   `journal/ideas/<stem>-<slug>.md` with Experiment, Source
   (`audit:<stem>:checks.<code>` or `design:<stem>`), Question,
   Why now, What changes, Open gaps. No acceptance criteria.
7. Return the digest, JSON `finding` from
   `python -m skore_skills audit finding --stem <stem>`, the
   locator from `python -m skore_skills loop locator --stem <stem>`,
   and the idea paths.

An explicit re-audit asks the gate again before `cells run`, even
when a digest exists, because it re-runs the checks.

## Cost preview

On `ask`, before the question, emit 1–3 sentences. This is a
**local read of the persisted report**, not another fit. The audit
template runs every skore check, writes `audit/<stem>.py` and
`scratch/audit/<stem>/audit.md`, and can be slow on a large
report. Name the stem and those paths. Do not invent minutes.

## Stop conditions

- Do not run `cells run` before **Review** or an explicit re-audit
  confirmation.
- Do not write `JOURNAL.md` or a design note.
- Do not call `skore.evaluate` or `project.put`.
- Do not pick a winning idea.
- Do not invent a missing child's procedure.
