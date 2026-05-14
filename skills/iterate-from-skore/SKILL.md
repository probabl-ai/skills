---
name: iterate-from-skore
description: >
  Source the next ML experiment proposal by walking the skore
  report's diagnostic surface (`report.diagnosis()`) and converting
  every actionable finding into a row in `PLAN.md`'s Backlog. Returns
  the enriched Backlog rows + a one-paragraph summary back to
  `iterate-ml-experiment`, which writes the rows into `PLAN.md` and
  re-presents the sourcing menu so the user can now promote a `B<N>`
  row. Stops at "Backlog enriched, summary returned"; never writes a
  per-experiment plan file, never picks the "winning" finding — the
  user picks via `B<N>`.

  TRIGGER when: `iterate-ml-experiment` is picking a sourcing strategy
  and the user picks `skore` from the menu; the user says "mine the
  report", "what does skore see?", "fill the backlog from the
  diagnostic"; the previous experiment has finished and the user wants
  the report converted into actionable backlog items.

  SKIP when: the previous experiment hasn't run yet (no report on
  disk); the user has a concrete modelling idea (use
  `iterate-from-user`); the task is the *mechanics* of running /
  opening a report — route to `evaluate-ml-pipeline`; the user wants a
  narrative read of one specific section of the report (route to
  `evaluate-ml-pipeline`).

  HOW TO USE: open the skore Project (consult `Skill(python-api)` in
  this turn for the exact signature — never name skore symbols from
  memory), call `report.diagnosis()` on the latest experiment's
  report, walk every actionable finding it returns, and emit one
  Backlog-candidate row per finding. Dedupe against rows already in
  `PLAN.md` Backlog by source citation. Return the candidate rows + a
  one-paragraph human summary. The parent skill writes the rows to
  `PLAN.md` and re-shows the sourcing menu.
---

# Iterate from skore

Source: `report.diagnosis()` on the prior experiment's skore report.
Output: a set of **Backlog-candidate rows** + a short human summary,
handed back to `iterate-ml-experiment`. The parent skill writes the
rows to `PLAN.md` Backlog and re-presents the sourcing menu so the
user can promote one via `B<N>`.

## Output contract (read this before the body)

This skill **never writes `plan/` files** (including `PLAN.md`) — the
parent owns those. It returns two artifacts as conversation text:

1. **Backlog-candidate rows** — one row per actionable diagnostic
   finding. Each row carries:
   - `Item`: one-line description of the finding, phrased as an
     *experiment idea*, not as a metric reading (e.g.
     "investigate target-bin>0.95 residual bias via target transform",
     not "residuals are biased on bin>0.95").
   - `Source`: a stable citation pointing into `report.diagnosis()`'s
     output (e.g. `diagnosis:residuals.by_target_bin` or
     `diagnosis:calibration.bin_4_underconfident`). The citation is
     load-bearing for dedup.
2. **Summary** — one paragraph for the user: how many findings were
   surfaced, the top 2-3 by expected payoff, what the report looked
   *clean* on. Keep this dense; the rows are the durable artifact, the
   summary is just orientation.

If the parent's Backlog already contains a row with the same `Source`
citation, **drop the candidate** — do not duplicate. The summary
should note the number of dropped duplicates ("4 new findings; 2 were
already in Backlog from prior mining").

### Empty-diagnosis outcome

If `report.diagnosis()` surfaces nothing actionable (rare — a clean
report is real), return zero candidate rows and a summary that says so
explicitly: "the report looks clean on <metric>, <calibration>,
<residuals>; no actionable findings on this turn." The parent will
note this in `PLAN.md` Status and the user picks `user` next.

### Inaccessible-report fallback

If the skore Project store isn't on disk, the key isn't present, or
`skore` isn't importable, **do not fabricate findings from memory**.
Return zero rows and a summary that explains the access failure
(e.g. "skore Project store at `reports/` not found — was the
experiment run? was the project key spelled right?"). The parent will
surface the gap to the user.

## Stop conditions

- **Don't write `plan/` files.** That includes `PLAN.md`. This skill
  returns rows as conversation text; the parent writes them.
- **Don't read the report from memory.** Always go through
  `Skill(python-api)` for the report API and `evaluate-ml-pipeline` for
  any narrative read. Symbol names from training data are not
  acceptable.
- **`report.diagnosis()` is the v1 programmatic entry point.** When
  the report is accessible, open the skore Project and call
  `report.diagnosis()` to walk the diagnostic surface programmatically
  — that is the only entry point this skill relies on. Confirm the
  exact signature via `Skill(python-api)` in this turn; do not infer
  arguments from memory. Other report attributes are out of scope
  until v2.
- **Don't pick a single "winning" finding for the user.** This skill
  enriches the Backlog. The user picks which one to act on via the
  parent's sourcing menu (`B<N>`). Emitting only one row when the
  diagnosis surfaced five hides choices the user is supposed to make.
- **Dedup against existing Backlog rows by `Source` citation.** Read
  `PLAN.md` Backlog before emitting; skip any candidate whose `Source`
  matches an existing row. Re-mining a stale report shouldn't double
  the Backlog.
- **Don't fabricate when the report is inaccessible.** Return zero
  rows with a summary that explains why. The user will route the
  problem (run missing, key wrong, skore not installed) themselves.
- **Don't author acceptance criteria.** Backlog rows are
  *experiment ideas*, not goals with target deltas. The user judges
  the result after the run, per `iterate-ml-experiment`'s broader
  rule.
- **Multi-line probes go to `scratch/`, not inline.** Walking
  `report.diagnosis()` and pulling its actionable rows grows
  multi-line fast. Any payload longer than 2 lines lands in
  `scratch/<YYYY-MM-DD>_<HHMMSS>_<short>.py` (per the
  workspace's `scratch/README.md`), not in `pixi run python -c
  "..."`. The 2-line cap is contract; ignoring it defeats the
  traceability the scratch folder exists for. See `python-api`
  § "Scratch traceability" for the file layout.

## The inspection loop

1. **Locate the report.** Open the skore Project for this workspace
   (the `name` and `workspace="reports"` are set in the experiment
   script). Pull the report keyed by the *latest done* experiment's
   stem (e.g. `02_target_transform`). If multiple `done` experiments
   exist, default to the most recent — surface the choice to the user
   only if they ask.
2. **Walk the diagnostic surface via `report.diagnosis()`.** Call it
   once; read what it returns. The shape depends on task type
   (regression / classification / time series); consult
   `Skill(python-api)` for the v1 surface (metrics with CIs,
   calibration, residuals, per-slice / per-fold breakdowns, default
   plots).
3. **Convert every actionable finding into a Backlog candidate.**
   *Actionable* means there's a clear thing to try in `src/<pkg>/`
   that addresses the finding. A miscalibration on a 5-row slice is
   *not* actionable (sample too small); a systematic residual on a
   feature we control *is* actionable. Skip the un-actionable ones —
   they're noise.
4. **Dedup against the existing Backlog.** Read `PLAN.md` Backlog
   (the parent's most recent state). For each candidate, check
   whether a row with the same `Source` citation already exists.
   Drop the duplicates.
5. **Rank by expected payoff for the summary.** The Backlog rows
   themselves are unordered (the parent assigns `B<N>` indices on
   write), but the summary calls out the top 2-3 the user should
   look at first. Bigger metric gaps and clearer mechanisms beat
   marginal noise.

## What is returned

A short structured block, not a plan file:

```
Backlog candidates (from: skore diagnosis on <prev_stem>):
  - Item:    <one-line experiment idea, not a metric reading>
    Source:  diagnosis:<path.into.diagnosis.output>
  - Item:    ...
    Source:  ...
  - ...

Dropped as duplicates (already in Backlog): <N>

Summary:
  <one paragraph for the user — counts, top 2-3 highlights, where the
  report looked clean. Dense, not chatty.>
```

`iterate-ml-experiment` consumes this:
1. Writes the candidate rows into `PLAN.md` Backlog with stable
   `B<N>` indices appended at the end.
2. Surfaces the summary verbatim to the user.
3. Re-presents the sourcing menu with the enriched Backlog visible
   so the user can pick a `B<N>` row directly or pick `user` if the
   findings prompt a different direction.

## Companion skills

- **`iterate-ml-experiment`** — the caller; owns the plan files
  (including `PLAN.md`).
- **`evaluate-ml-pipeline`** — for "what does the report say" before
  "what should we try next". This skill is the *next-step* side;
  `evaluate-ml-pipeline` is the *read* side.
- **`python-api`** — exact symbols for opening the Project, naming
  the report key, and calling `report.diagnosis()`. Do not guess.
  **Cache hits first**: check `scratch/api/skore/<version>/`
  before WebSearching; cache new findings back there (per
  `python-api` Shape 0/3).
- **`iterate-from-user`** — the only sibling strategy; sources from
  the user (article, resource, or free text) when the skore findings
  aren't the right starting point.
