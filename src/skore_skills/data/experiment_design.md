# <NN>_<short_name>

<!--
Design note for experiments/<NN>_<short_name>.py (same stem, one to
one with the script). Write and agree on it before creating the
script.

Lifecycle:
  planned   → draft, not yet approved
  approved  → agreed; safe to create the matching .py
  done      → result recorded; Status block + JOURNAL.md row updated
  abandoned → discarded; record a one-line reason on State

The four content sections (Question, Motivation, Method, Risks) are
fixed once approved; only the Status block changes afterwards. There
is no "Success criteria" section — judge the result once it is in.
-->

## Question / hypothesis

<!-- One sentence. What are we trying to learn — not just "try X". -->

## Motivation

<!--
Why now. Cite the source concretely — the request or article claim to
build on, the finding from a prior experiment's report that prompted
this, or the backlog item being promoted.
-->

- **Sourcing strategy:** <user | my-pick | skore:<stem> | backlog:B<N>>
- **Source(s):**
  <!--
  One line is enough for most cases. For an article, paste the exact
  claim verbatim — it is what makes the result interpretable later.
  -->
  - <e.g. issue #42 / "Paper Title" (year) URL — "exact claim" /
    a check from the 01_baseline report + its documentation_url /
    B2 (originally from the 01_baseline report)>
- **Why this matters:** <one or two sentences>

## Method

<!--
What changes versus the previous experiment, in prose. Which file in
src/<pkg>/ is touched? State intent, not code.
-->

- **Files touched:** <e.g., `src/<pkg>/features.py`, `src/<pkg>/evaluate.py`>
- **Change versus baseline (or previous experiment):** <prose>
- **Cross-validation:** decided at the evaluation step, data-driven
  from the data's structure (groups / time ordering) — not fixed here.
- **Out of scope for this experiment:** <what we are deliberately not changing>

## Risks / things that could invalidate the result

<!--
What would make the metric move for the wrong reason — leakage,
sample size, distribution shift, an artifact of the splitter, a
benchmark that's not directly comparable. The user reads this
both before approving (to push back on guard-rails) and after the
run (to interpret the headline result honestly).
-->

- <e.g., "ROC-AUC may improve via leakage if the new feature is post-outcome">
- <e.g., "sample size in slice X is too small for the calibration claim">

## Status

- **State:** planned
  <!--
  Lifecycle: planned → approved → running → done | abandoned.
  - `done`: fill Headline result + Implication.
  - `abandoned`: add a one-line reason on this line itself
    (e.g., `abandoned — paper's required dep was non-trivial; deferred to v2`).
    Headline result becomes `n/a — abandoned: <reason>`.
    The row stays in JOURNAL.md History; only the State field flips.
  -->
- **Approved by user on:** <date or n/a>
- **Headline result:** <fill in after run, or `n/a — abandoned: <reason>`>
- **Implication for next iteration:** <fill in after run — what it suggests to try next. For abandonment: one line on what the abandonment teaches (e.g., "rules out monotonic-NN direction without paid GPU env")>
