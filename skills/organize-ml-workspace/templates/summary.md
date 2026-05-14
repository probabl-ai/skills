# SUMMARY

<!--
Project-level narrative digest. Read at the top of every session by
`iterate-ml-experiment`'s first-action ritual; complements `plan/PLAN.md`'s
index role (PLAN.md is the *table*, summary.md is the *story*).

Rewriting protocol (owned by `iterate-ml-experiment` § 4 — "Refresh
overview/summary.md"):

1. Run a scratch probe to extract the data:
   - `project.summarize()` from the skore Project → cross-experiment metrics
   - `## Status` blocks from each `plan/NN_*.md` → headline + implication
   Save the probe to `scratch/<YYYY-MM-DD>_<HHMMSS>_refresh_summary.py`.

2. Write THIS file by hand from the probe output. Curate, don't dump:
   - Drop metrics that aren't comparable across the listed experiments.
   - Quote the plan's Status text where it is already concise.
   - Rewrite where it isn't. The point is a *narrative*, not a paste.

3. Keep the three sections below in this order. Add a section only on user
   request — the contract is "easy to read in two minutes, scannable from
   the top."

The per-experiment plan files in `plan/NN_*.md` remain the source of truth
(frozen Method / Risks). This file is the curated view across them.
-->

## Project narrative

_No experiments recorded yet. Fill in once `01_baseline` has run: 1–2
paragraphs covering the dataset, the goal, and the path so far._

## Cross-experiment metrics

_Filled in from `project.summarize()` after the first outcome recording._

## Per-experiment status

_One subsection per `done` experiment, with the curated Headline +
Implication. See the per-experiment `plan/NN_*.md` Status blocks for
the unedited record._
