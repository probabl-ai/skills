# <NN>_<short_name>

## Question / hypothesis

<one sentence: what we are trying to learn>

## Motivation

- **Sourcing strategy:** <user | skore | my-pick | audit:<stem>:checks.<code> | backlog:B<N>>
- **Source(s):**
  - <e.g. issue #42 / "Paper Title" (year) URL — "exact claim" /
    a check from the 01_baseline report + its documentation_url /
    B2 (originally from the 01_baseline report)>
- **Why this matters:** <one or two sentences>

## Method

- **Files touched:** <e.g., `src/<pkg>/features.py`, `src/<pkg>/pipeline.py`>
- **Change versus baseline (or previous experiment):** <prose>
- **Cross-validation:** the scheme locked under Modeling decisions
  in the journal.
- **Out of scope for this experiment:** <what we are deliberately not changing>
- **Pipeline:** <!-- results-embed: pipeline -->

## Risks / things that could invalidate the result

- <e.g., "ROC-AUC may improve via leakage if the new feature is post-outcome">
- <e.g., "sample size in slice X is too small for the calibration claim">

## Status

- **State:** planned
- **Approved by user on:** <date or n/a>
- **Headline result:** <fill in after run, or `n/a — abandoned: <reason>`>
- **Persisted report:** <backend locator after `project.put`, or `n/a — backend did not expose a locator`>
- **Audit findings:** n/a — audit not run
- **Implication for next iteration:** <fill in after run — what it suggests to try next. For abandonment: one line on what the abandonment teaches (e.g., "rules out monotonic-NN direction without paid GPU env")>

## Notebooks

### Evaluation notebook

### Audit notebook
