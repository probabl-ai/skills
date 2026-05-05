---
name: iterate-from-diagnostic
description: >
  Source the next ML experiment proposal by inspecting the
  skore report from the previous run — residuals, calibration,
  per-slice metrics, threshold behavior, statistical checks
  surfaced by skore. Hand the proposal back to
  `iterate-ml-experiment`, which writes it into
  `plan/NN_short_name.md` and seeks the user's approval. Stops
  at "a proposal (question, motivation, method outline) has been
  returned"; does not write any plan file itself, and does not
  author acceptance criteria — the user judges the result.

  TRIGGER when: `iterate-ml-experiment` is picking a sourcing
  strategy, the previous experiment has a skore report on disk,
  and the user says "the report shows X", "calibration looks
  bad", "why is slice Y so off?", "residuals look weird", or
  "what does the report tell us?"; the user is open-ended after
  a recent run — try this strategy first when a fresh report
  exists.

  SKIP when: the previous experiment hasn't run yet (no report
  to read); the user has a concrete modelling idea (use
  `iterate-from-user`); the issue is clearly methodological,
  not data-driven (use `iterate-from-methodology`); the user
  wants a literature scan (use `iterate-from-literature`); the
  task is the *mechanics* of running / opening a report —
  route to `evaluate-ml-pipeline`.

  HOW TO USE: this skill is shallow. Open the relevant report
  via `evaluate-ml-pipeline` / `skore-api` (don't guess
  signatures). Walk the diagnostic surface skore exposes
  (metrics, calibration, residuals, slices, statistical tests)
  and pick the **one** finding most likely to drive a useful
  next experiment. Return a proposal in the structured shape
  below; do not write any plan file.
---

# Iterate from diagnostic

Source: the skore report from the previous experiment. Output:
a proposal that targets the strongest diagnostic signal, handed
back to `iterate-ml-experiment`.

## Output contract (read this before the body)

This skill **never writes `plan/` files**. It returns one of
the following back to `iterate-ml-experiment`, which writes
the plan file from your output:

- **Default — a Proposal block** (full shape in § What is
  returned at the bottom): `Finding`, `Question`, `Motivation`,
  `Method outline`, `Success`, `Risks`. **Required:** every
  finding cites a specific section returned by
  `report.diagnosis()`.
- **Fallback — a stub** if the report isn't accessible on
  disk: same Proposal shape with `Finding: <pending — user
  describes>` and the rest blank. Use when the skore Project
  store is missing, the key isn't there, or skore isn't
  importable. Don't fabricate findings from memory.

## Stop conditions

- **Don't write `plan/` files.** That belongs to
  `iterate-ml-experiment`.
- **Don't read the report from memory.** Always go through
  `skore-api` for the report API and `evaluate-ml-pipeline` for
  the diagnostic narrative. Symbol names from training data are
  not acceptable.
- **`report.diagnosis()` is the v1 programmatic entry point.**
  When the report is accessible on disk, open the skore Project
  and call `report.diagnosis()` to walk the diagnostic surface
  programmatically — that is the only entry point this skill
  relies on. Confirm the exact signature via
  `Skill(skore-api)` in this turn; do not infer arguments from
  memory. Other report attributes are out of scope until v2.
- **If the report isn't accessible, ask — don't fabricate.** If
  the skore Project store doesn't exist at `reports/`, the key
  isn't there, or skore isn't importable: return a
  proposal-stub that asks the user to paste or describe the
  diagnostic finding, instead of inventing one. Stub fields:
  `Finding: <pending — user describes>`, the rest blank. The
  parent skill (`iterate-ml-experiment`) will park the
  proposal until the next session.
- **Don't propose without a concrete citation.** Every finding
  must point to a specific section / metric / plot returned by
  `report.diagnosis()` (e.g., "diagnosis section
  `residuals.by_target_bin` — bins target>0.95 show systematic
  positive bias").
- **Don't fan out.** One finding per proposal. The diagnostic
  surface returns many things; pick the one with the largest
  expected payoff and queue the rest as backlog items.

## The inspection loop

1. **Locate the report.** Open the skore Project for this
   workspace (the `name` and `workspace="reports"` are set in
   the experiment script). Pull the report keyed by the prior
   experiment's stem (e.g., `01_baseline`).
2. **Walk the diagnostic surface via `report.diagnosis()`.**
   Call `report.diagnosis()` and read what it returns — that's
   the v1 surface (metrics with CIs, calibration, residuals /
   probability distributions, per-slice / per-fold breakdowns,
   default plots, depending on task type). Use
   `Skill(skore-api)` this turn to confirm the exact return
   shape; do not assume keys or attributes from memory. Prefer
   the `evaluate-ml-pipeline` narrative for "what does the
   report say"; come back here for "what experiment does that
   imply?".
3. **Rank findings.** For each candidate signal, ask: how big
   is the gap, and is it actionable in `src/<pkg>/`? A
   calibration miscalibration on a small slice is interesting
   but not actionable; a systematic residual structure on a
   feature we control is actionable.
4. **Form the proposal.** The question is "if we fix this
   signal, does the headline metric (or the right metric) move
   the way we'd expect?" The method outline names the file in
   `src/<pkg>/` that changes.

## What is returned

A short structured block, not a plan file:

```
Proposal (from: diagnostic on report <prev_stem>):
  Finding:         <one sentence; cite the report section / metric / plot>
  Question:        <"does addressing <finding> move <metric>?">
  Motivation:      <why this finding is actionable in src/<pkg>/, not just interesting>
  Method outline:  <prose; which file in src/<pkg>/ is touched>
  Success:         <"finding-specific signal flips" + headline metric delta>
  Risks:           <ways the fix could move the metric for the wrong reason>
```

`iterate-ml-experiment` consumes this and drafts
`plan/NN_short_name.md`.

## Companion skills

- **`iterate-ml-experiment`** — the caller; owns the plan file.
- **`evaluate-ml-pipeline`** — for "what does the report say"
  before "what should we try next".
- **`skore-api`** — exact symbols for opening the Project and
  reading the report. Don't guess.
- **`iterate-from-user` / `iterate-from-literature` /
  `iterate-from-methodology`** — sibling strategies.
