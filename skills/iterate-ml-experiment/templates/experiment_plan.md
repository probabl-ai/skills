# <NN>_<short_name>

<!--
Design note for `experiments/<NN>_<short_name>.py`. Same stem,
one-to-one with the script. Owner: `iterate-ml-experiment`.

Lifecycle:
  planned   → draft, not yet shown to the user / not approved
  approved  → user said "go"; safe to create the matching .py
  done      → result recorded; status block + PLAN.md row updated
  abandoned → discarded; record one-line reason on State

This skill is user-triggered (no polling, no auto-detection),
so there is no observable "running" state — the experiment
sits in `approved` from the moment the script is created until
the user reports the outcome via § 4 ("the run finished, record
it"), at which point it flips to `done` (or `abandoned`).

Freeze rule: the four content sections (Question, Motivation,
Method, Risks) are frozen at `approved`. Only the Status block
is updated after that. **No "Success criteria" section** — the
skill's job is to propose and run; the user judges whether the
result is good enough.
-->

## Question / hypothesis

<!-- One sentence. What are we trying to learn — not just "try X". -->

## Motivation

<!--
Why now. Cite the source concretely:
  - user (free-text)    → quote the request the user typed
  - user (article-link) → article title + year + URL + the exact
                          claim to build on
  - user (resource)     → GitHub issue link, or spec file:line,
                          or reference-repo path
  - my-pick             → which PLAN.md / prior-plan fields fed
                          the synthesis (Status, last Implication,
                          last Risks, current Backlog state)
  - skore               → `report.diagnosis()` section / metric /
                          slice / plot from the prior experiment's
                          report
  - backlog (B<N>)      → the index promoted + the row's original
                          Source carried forward
-->

- **Sourcing strategy:** <user | my-pick | skore:<stem> | backlog:B<N>>
- **Source(s):**
  <!--
  Single line is the right shape for most strategies. For an
  article-link, paste the exact claim verbatim — the design
  note becomes the postmortem and the original claim is what
  makes the result interpretable later.
  -->
  - <e.g. issue #42 / "Paper Title" (year) URL — "exact claim" /
    `report.diagnosis().residuals.by_target_bin` on `01_baseline` /
    B2 (originally skore:01_baseline)>
- **Why this matters:** <one or two sentences>

## Method

<!--
What changes versus the previous experiment, in prose. Which file
in `src/<pkg>/` is touched? State intent, not code. Mechanics live
in `build-ml-pipeline` / `evaluate-ml-pipeline`.
-->

- **Files touched:** <e.g., `src/<pkg>/features.py`, `src/<pkg>/evaluate.py`>
- **Change versus baseline (or previous experiment):** <prose>
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
  - `done`: Headline result + Implication required (filled by § 4).
  - `abandoned`: requires a one-line reason on this line itself
    (e.g., `abandoned — paper's required dep was non-trivial; deferred to v2`).
    Headline result becomes `n/a — abandoned: <reason>`.
    The row stays in PLAN.md History; only the State field flips.
  - User-decided only: the skill never auto-abandons.
  -->
- **Approved by user on:** <date or n/a>
- **Headline result:** <fill in after run, or `n/a — abandoned: <reason>`>
- **Implication for next iteration:** <fill in after run — feeds the next strategy dispatch. For abandonment: one line on what the abandonment teaches (e.g., "rules out monotonic-NN direction without paid GPU env")>
