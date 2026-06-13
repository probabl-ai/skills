# Maintenance modes — overview / compare / goal pivot / abandoned / re-runs

Read-only or rare modes the iteration loop also covers. SKILL.md has
one-line summaries with pointers here. This file has the full
procedures.

## Project overview / status requests

When the user asks "where are we?", "give me a one-pager", "what's the
status?", "what have we tried?" — that is a **read** of
`journal/JOURNAL.md`, not a new artifact. **`JOURNAL.md` is the
canonical project digest** (Status, Data understanding (EDA), History,
Backlog — four sections by design). Do not generate a separate summary
document.

- For short asks ("status?") — surface the **Status block** verbatim
  plus the last one or two History rows.
- For "one-pager" / "where are we" framing — surface `JOURNAL.md`
  as-is (or summarize section-by-section if it has grown long), and
  add a one-sentence "what's ripe next" line drawn from Backlog +
  the most recent Implication. Nothing else.
- **Do not write to `journal/`** during these requests. Read-only.

If `JOURNAL.md` has drifted (Status references an experiment that no
longer matches History's last row, Backlog has stale items), flag the
drift to the user — but **don't auto-edit** during a read-only
request. Drift fixes belong to § 4 (next time an outcome is recorded)
or to an explicit "tidy up JOURNAL.md" ask.

---

## Compare past experiments (read-only mode)

When the user says "compare 01 and 02", "how does this run stack up
against the baseline?", "what's the trend across runs?" — that is
**not** a new-experiment request. Don't draft a design note. Don't
add a row to History. This is a **read** of past work.

### v1 scope: pairwise side-by-side, no programmatic multi-stem comparison

This skill family does not expose a `ComparisonReport` / multi-key
comparison entry point in v1 — deliberately. The handoff to
`evaluate-ml-pipeline` is single-learner by its declared scope, and we
do not stretch it.

### Procedure for "compare X and Y"

- **Headline side-by-side.** Pull the Headline result cells for each
  requested stem from `JOURNAL.md` History; surface them side by side,
  with one-sentence intent for each (also from History). This is
  usually enough to answer "is the new one worth it?".
- **Deeper read, one report at a time.** If the user wants more than
  the headline (residuals, calibration, slice metrics), route to
  `evaluate-ml-pipeline` **once per stem, separately** — that skill
  is single-learner by scope. The user does the cross-experiment
  synthesis from the two narratives; the skill does not.
- **Don't write to `journal/`** during a compare request. If the
  side-by-side reading surfaces a finding the user wants to act on,
  re-enter § 1 with the sourcing menu — typically `skore` (mine one
  or both reports into Backlog) or `user` (the user has a concrete
  idea drawn from the comparison).

### v2 gap, flagged

Statistical comparison (significance tests, shared-fold paired
comparisons, multi-key `ComparisonReport`) is out of scope for v1. If
the user explicitly asks for a significance test or "stat-sig
comparison", surface this gap:

> *"v1 doesn't expose programmatic multi-stem comparison; for
> significance, you'd need to run a paired re-run (see § Re-runs →
> Batch re-run) and compare the per-fold metrics manually."*

The design notes are the durable record of *experiments tried*;
comparisons are derived views, not new entries.

---

## Goal pivots

Sometimes the project goal itself changes mid-stream — the trader
cares about typical error not squared error, so MSE → MAE; the
downstream consumer changes from offline batch to online serving so
latency joins the goal; the metric class changes (regression →
ranking). This is **not** an experiment; it is a **strategic event**
that affects how every future experiment is judged.

When the user signals a goal pivot:

1. **Update `JOURNAL.md` Status** with the new goal and the date,
   keeping a one-line trace of what changed:

   ```
   Goal pivoted 2026-03-04: minimize MSE → minimize MAE.
   Reason: trader cares about typical error, not squared error.
   ```

2. **Insert a horizontal-rule row in History** below the last
   pre-pivot experiment, formatted as a clear divider:

   ```
   | --- | **Goal pivoted 2026-03-04: MSE → MAE** | --- | rows above evaluated against MSE; rows below against MAE | --- |
   ```

3. **Do NOT mass-edit prior `journal/NN_*.md` files.** Their Success
   criteria are frozen at approval — that's the contract. Their
   Headline result cells in History stay too (they were valid against
   the old goal).

4. **The first post-pivot experiment auto-flags incomparability** in
   its **Risks** section:

   > "evaluating against new goal (MAE); not directly comparable to
   > {01_baseline, 02_text_encoder} which used MSE."

   This blocks silent cross-comparison across the pivot.

**A goal pivot is user-only.** The skill never auto-pivots.

---

## Abandoned experiments

The lifecycle states are `planned → approved → running → done |
abandoned`. Abandonment is a real outcome and needs the same handling
rigor as `done`.

- **User-decided only.** The skill never auto-abandons. If an
  experiment has been planned/approved for many sessions without
  progress, **flag** it to the user via `AskUserQuestion` with three
  options:
  - **abandon** — flip status to `abandoned`; the skill then prompts
    in a follow-up turn for the one-line reason that lands in the
    Status block.
  - **defer** — leave as `approved`; the skill will re-flag in a
    future session.
  - **run now** — the script already exists; route to § 3's
    post-smoke run prompt.

  Don't change state without an explicit pick — free-text ("eh, drop
  it") is ambiguous between abandon and defer.

- **Status block requires a one-line reason.**

  > "Dependency was non-trivial to install; deferred to v2."
  >
  > "Method was superseded by 06_softer_transform's success."
  >
  > "Direction ruled out by skore finding in 04_monotonic_gbm."

  The reason is the whole point — it's what makes the abandonment a
  useful provenance signal rather than a gap.

- **Headline result becomes** `n/a — abandoned: <reason>`. The
  History row stays (provenance is the whole point); only the Status
  field flips.

- A subsequent re-run of an abandoned experiment is a normal re-run
  (per § Re-runs); the abandoned row is not edited beyond the
  optional `Implication` back-link.

---

## Re-runs

Sometimes the right next step is to **redo** a prior experiment under
different conditions — paired seeds for a fair comparison, a
corrected splitter, a fresh data snapshot.

**A re-run is a new file**, never an in-place edit. Two shapes,
dispatched by how many prior experiments are being redone.

### Single re-run (one prior target)

Use when the user (often after a `skore`-surfaced finding) asks to
redo exactly one prior experiment under a controlled change.

- New stem: `NN_<original_stem>_rerun.py` and the matching
  `journal/NN_<original_stem>_rerun.md`. The numeric prefix is the
  next free integer; `<original_stem>` preserves provenance.
- `Sourcing strategy` line: typically `user re-run` (the user asks
  for the redo, often after a `skore`-surfaced finding pointed at the
  prior experiment's setup).
- **Motivation** must quote the original experiment stem and state
  precisely what changed (the fix being tested).
- **Method** notes that the experiment is a re-run and what is held
  constant from the original.

### Batch re-run (N prior targets)

Use when the user (often after a `skore`-surfaced finding flags a
cross-experiment fairness gap, or after their own audit) calls for
N≥2 prior experiments to be redone under a controlled condition —
e.g. "redo 01, 02, 03 with paired seeds and a fixed splitter".

**This is one intervention, not N; it gets one design note.**

- New stem: `NN_paired_comparison.py` and
  `journal/NN_paired_comparison.md` (or another descriptive name:
  `NN_seeded_redo`, `NN_aligned_splits`, …). One numeric prefix; one
  approval; one History row.
- `Sourcing strategy`: `user batch re-run` (or `skore batch re-run`
  when the impetus came from a diagnostic finding the user promoted
  from the Backlog).
- **Motivation** quotes the comparability gap (skore-surfaced or
  user-identified) and cites the affected stems.
- **Method** lists the rerun targets explicitly (`{01, 02, 03}`) and
  the controlled condition applied uniformly (paired seed, identical
  splitter, …). The script produces **multiple report keys** in the
  skore Project — one per rerun target — under a shared prefix
  (e.g. `paired:01`, `paired:02`, `paired:03`).
- **Outcome shape is a comparison, not a single metric.** The
  experiment produces multiple report keys (one per re-run target)
  and the user reads them side-by-side to judge whether the prior
  ranking holds or flips. The skill does not predefine what counts as
  "successful" — the user owns the call.

### Both shapes

A new row goes into `JOURNAL.md` History at approval; the original
rows are **not** edited. The `Implication` block of each original
may be updated post-re-run with a one-line link:

> "see `NN_X_rerun` for the seeded comparison"
>
> "see `NN_paired_comparison` for the paired-seed redo"

That is the only edit allowed to a frozen file.

In-place edits to an approved design note are reserved for the
Status block. Re-runs are not amendments — they're new experiments
that happen to share most of the design.
