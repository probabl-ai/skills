---
name: iterate-from-methodology
description: >
  Source the next ML experiment proposal by auditing the
  *methodology* of the previous experiment(s) — split strategy,
  leakage risk, target encoding, sample size, metric choice,
  baseline comparability, randomness control. Hand the proposal
  back to `iterate-ml-experiment`, which writes it into
  `plan/NN_short_name.md` and seeks the user's approval. Stops
  at "a proposal (question, motivation, method outline) has been
  returned"; does not write any plan file itself, and does not
  author acceptance criteria — the user judges the result.

  TRIGGER when: `iterate-ml-experiment` is picking a sourcing
  strategy and the user says "did we get the split right?",
  "is this leaking?", "small sample size?", "is the baseline
  fair?", "is this metric the right one?"; the previous
  experiment's result looks suspicious (too good, too noisy, too
  flat) and the user wants to check the setup before iterating
  further; a literature / diagnostic strategy has surfaced
  something that turns out to be a methodology issue, not a
  modelling issue.

  SKIP when: the user has a concrete modelling idea (use
  `iterate-from-user`); the user wants to scan literature (use
  `iterate-from-literature`); the user wants to read the skore
  report itself (use `iterate-from-diagnostic` for "what does
  the report say?", `evaluate-ml-pipeline` for the report
  mechanics).

  HOW TO USE: this skill is shallow. Read the previous
  experiment's `plan/NN_*.md` and skim the matching
  `experiments/NN_*.py`, `src/<pkg>/data.py`,
  `src/<pkg>/evaluate.py`. Run the audit checklist below
  systematically. **Cite concrete file:line references** for
  every issue found. Return one or two proposals (the most
  important findings) in the structured shape below; do not
  write any plan file.
---

# Iterate from methodology

Source: an audit of the prior experiment's setup. Output: a
proposal that fixes the most important methodological gap,
handed back to `iterate-ml-experiment`.

## Output contract (read this before the body)

This skill **never writes `plan/` files**. It returns one of
two payloads back to `iterate-ml-experiment`:

- **Proposal — the audit found something** (full shape in §
  What is returned at the bottom): `Audit summary`,
  `Question`, `Motivation` with `file:line` citations,
  `Method outline`, `Success`, `Risks`. If a methodology
  finding spans **multiple prior experiments** (e.g., paired
  seeds across `{01, 02, 03}`), the proposal is shaped as a
  **batch re-run** — see `iterate-ml-experiment` § Re-runs →
  Batch re-run.
- **Clean audit — no proposal:** if no FAILs and no meaningful
  WARNs, return the literal payload
  `{ "outcome": "methodology_clean", "audited": [<stems>] }`
  (see § Stop conditions). This is a *real outcome*, not a
  failure. Don't invent a weak finding to fill the slot.

## Stop conditions

- **Don't write `plan/` files.** That belongs to
  `iterate-ml-experiment`.
- **Don't audit from memory.** Read the actual files.
  `plan/NN_*.md` for intent, `experiments/NN_*.py` for what
  was run, `src/<pkg>/data.py` and `src/<pkg>/evaluate.py` for
  the splitter and the data shape. Quote `file:line` for every
  finding.
- **Don't reframe modelling preferences as methodology issues.**
  "Try a different model" is not a methodology fix; it's a
  modelling choice (route to `iterate-from-user` or
  `iterate-from-literature`). This skill catches setup errors,
  not model substitutions.
- **Don't pile on findings.** Pick the one or two with the
  largest effect on result validity. The rest can go to the
  backlog in `PLAN.md`.
- **A clean audit is a real outcome.** If no FAILs and no
  meaningful WARNs, return the literal payload
  `{ "outcome": "methodology_clean", "audited": [<stems>] }`
  instead of a proposal. This is not a failure — it tells the
  parent skill "the prior comparison was sound; rotate to the
  next strategy." `iterate-ml-experiment` will note the clean
  audit in `PLAN.md` (no new History row), reset its
  anti-monoculture counter, and dispatch the next strategy in
  the rotation. Do not invent a weak finding just to "have
  something to return."

## Audit checklist

Read the previous experiment's `plan/NN_*.md` and supporting
files, then run through:

- **Split strategy.** Is the splitter in `evaluate.py`
  appropriate for the data? Group structure (patient, user,
  store) honored? Time ordering honored? Stratification
  appropriate for the target imbalance?
- **Leakage.** Does any feature in `features.py` use information
  not available at prediction time? Is the target encoded in
  any feature path (e.g., target encoding done before the
  split)?
- **Sample size.** Is the smallest fold / slice large enough to
  trust the metric? Are confidence intervals reported (skore
  does this — is it being read)?
- **Target encoding / definition.** Is the target the *operational*
  target, or a proxy? Class imbalance handled honestly (no
  resampling that bleeds across folds)?
- **Metric choice.** Does the metric reflect the project goal
  from `PLAN.md` § Status? AUC vs. PR-AUC vs. calibration —
  which one matches the use case?
- **Baseline comparability.** Was the latest experiment fit on
  the same splits, the same metric, the same preprocessing as
  its baseline? An improvement over an unfair baseline is not
  an improvement. **If `PLAN.md` History contains more than one
  prior `done` experiment**, run this check across **all** of
  them — not just latest-vs-its-direct-predecessor. Cross-
  experiment comparability is the most common silent failure
  on a multi-experiment workspace: experiments drift to
  different seeds, splitters, or preprocessing as the
  workspace ages, and the headline-metric ranking becomes
  noise-bound. If FAIL, the proposal is typically a **batch
  re-run** (see `iterate-ml-experiment` § Re-runs → Batch
  re-run) listing the affected stems, not a new modelling
  experiment.
- **Randomness control.** Are seeds set in the splitter and the
  estimator? Is the variance across folds reported (not just
  the mean)?

For each item: PASS, FAIL, or N/A. For every FAIL, capture
`file:line` and a one-line description.

## What is returned

A short structured block, not a plan file:

```
Proposal (from: methodology audit of <prev_stem>):
  Audit summary:   <PASS/FAIL counts; the one or two FAILs that matter>
  Question:        <"does fixing <FAIL> change the result?">
  Motivation:      <which FAIL, with file:line, why it likely affects validity>
  Method outline:  <what to change in src/<pkg>/ — prose, not code>
  Success:         <"the previous result moves by ≥X" or "the result holds with the fix">
  Risks:           <ways the fix itself could mislead>
```

`iterate-ml-experiment` consumes this and drafts
`plan/NN_short_name.md`.

## Companion skills

- **`iterate-ml-experiment`** — the caller; owns the plan file.
- **`evaluate-ml-pipeline`** — the source of truth for splitter
  selection. Consult it when proposing a splitter change.
- **`build-ml-pipeline`** — for leakage / target-encoding fixes
  that require changes inside `pipeline.py` / `features.py`.
- **`iterate-from-user` / `iterate-from-literature` /
  `iterate-from-diagnostic`** — sibling strategies.
