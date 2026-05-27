---
name: iterate-from-skore
description: >
  Source the next ML experiment proposal by **reading the audit
  digest** at `scratch/audit/<stem>/audit.md` (produced by
  `audit-ml-pipeline` at § 4 record-outcome). For every row in the
  digest's `## Checks summary` whose `severity` is `issue` or `tip`,
  follow the row's `documentation_url` to draft a Backlog row whose
  `Item` is the mitigation the docs recommend. The `## Metrics
  summary` provides context for the human summary paragraph but
  does not drive Backlog rows on its own. Returns the enriched
  Backlog rows + a one-paragraph summary back to
  `iterate-ml-experiment`, which writes the rows into `JOURNAL.md`
  and re-presents the sourcing menu so the user can promote a
  `B<N>` row. Stops at "Backlog enriched, summary returned"; never
  writes a per-experiment design note, never picks the "winning"
  finding — the user picks via `B<N>`.

  TRIGGER when: `iterate-ml-experiment` is picking a sourcing
  strategy and the user picks `skore` from the menu; the user says
  "mine the report", "what does skore see?", "fill the backlog from
  the diagnostic"; the previous experiment has finished and the
  user wants the report converted into actionable backlog items.

  SKIP when: the previous experiment hasn't run yet (no audit
  digest on disk); the user has a concrete modelling idea (use
  `iterate-from-user`); the task is the *mechanics* of running /
  opening a report — route to `evaluate-ml-pipeline`; the user
  wants a narrative read of one specific section of the report
  (route to `evaluate-ml-pipeline`).

  HOW TO USE: read the existing
  `scratch/audit/<stem>/audit.md` digest as text — do NOT re-open
  the skore Project, do NOT call `report.*` accessors. For each
  row in the `## Checks summary` section whose severity is `issue`
  or `tip`, follow the `documentation_url` (via WebFetch) and draft
  one Backlog row citing `audit:<stem>:checks.<code>`. Dedupe
  against rows already in `JOURNAL.md` Backlog by source citation.
  Return the candidate rows + a one-paragraph human summary. The
  parent skill writes the rows to `JOURNAL.md` and re-shows the
  sourcing menu.
---

# Iterate from skore

Source: the audit digest at `scratch/audit/<stem>/audit.md`,
produced by `audit-ml-pipeline` at § 4 record-outcome.
Output: a set of **Backlog-candidate rows** + a short human
summary, handed back to `iterate-ml-experiment`. The parent skill
writes the rows to `JOURNAL.md` Backlog and re-presents the
sourcing menu so the user can promote one via `B<N>`.

## What this skill consumes

The digest carries two sections that matter here:

- `## Checks summary` — a DataFrame whose rows each have `code`,
  `severity` (`passed` / `issue` / `tip`), and `documentation_url`.
  **Each `issue` / `tip` row → one Backlog candidate**, with the
  `documentation_url` driving the `Item` text.
- `## Metrics summary` — task-appropriate headline metrics
  (regression / classification / multiclass). Used to ground the
  human summary paragraph ("the run achieved X but the SKD003
  check flagged Y"). **Does not drive Backlog rows on its own.**

Nothing else. The audit template intentionally stops at these two
sections; deeper accessors (residuals, importance, calibration,
…) are out of scope here.

## Why read the digest (not re-walk the Project)

The audit already opened the Project, loaded the report, called
the two accessors, and rendered the output as markdown. Re-doing
that work here would duplicate the cost of materialising Display
objects, risk drift between two walks, and require the agent
environment this skill should not need. Reading the digest as
text is cheaper and deterministic.

## Output contract (read this before the body)

This skill **never writes `journal/` files** (including
`JOURNAL.md`) — the parent owns those. It returns two artifacts as
conversation text:

1. **Backlog-candidate rows** — one row per actionable check from
   the digest. Each row carries:
   - `Item`: one-line experiment idea derived from the check's
     `documentation_url` content. Phrase as an *experiment idea*,
     not as a metric reading.
   - `Source`: `audit:<stem>:checks.<code>` (e.g.
     `audit:01_baseline:checks.SKD003`). The citation is
     load-bearing for dedup.

2. **Summary** — one paragraph for the user: how many findings
   were surfaced, the top 2-3 by severity, the headline numbers
   from the metrics summary as context. Keep it dense.

If the parent's Backlog already contains a row with the same
`Source` citation, **drop the candidate** — do not duplicate. The
summary should note the number of dropped duplicates ("4 new
findings; 2 were already in Backlog from prior mining").

### Empty-checks outcome

If the digest's checks summary has no `issue` / `tip` rows (only
`passed`), return zero candidate rows and a summary that says so
explicitly: "the report looks clean on the checks surface; no
actionable findings on this turn." The parent will note this in
`JOURNAL.md` Status and the user picks `user` next.

### Inaccessible-digest fallback

If the digest at `scratch/audit/<stem>/audit.md` cannot be read
(file missing, audit never executed, audit errored), **do not
fabricate findings from memory and do not re-run probes**. Return
zero rows and a summary that explains the access failure. The
parent surfaces the gap to the user; recovery is owned by
`audit-ml-pipeline` (re-run the audit runner, fix the auth, …).

## Stop conditions

- **Don't write `journal/` files.** That includes `JOURNAL.md`.
  This skill returns rows as conversation text; the parent writes
  them.
- **Don't re-open the skore Project from this skill.** The audit
  already did. Reading the digest as text is the contract — see
  § "Why read the digest". If the digest is missing, re-execute
  the audit runner via `audit-ml-pipeline`; never call
  `project.get(...)` from `iterate-from-skore`.
- **Only `## Checks summary` rows drive Backlog candidates.** The
  metrics summary is context for the human paragraph; it does not
  produce Backlog rows on its own. Deeper diagnostic surfaces
  (residuals, feature importance, calibration, …) are not in the
  audit template and not in scope here.
- **Follow the `documentation_url`.** For each `issue` / `tip`
  check, fetch the linked skore docs page (via `WebFetch`) and
  derive the Backlog `Item` from what the page recommends. Do not
  invent mitigations from training-data memory of skore.
- **Don't pick a single "winning" finding for the user.** Emit one
  row per actionable check. The user picks via the parent's
  sourcing menu (`B<N>`).
- **Dedup against existing Backlog rows by `Source` citation.**
  Read `JOURNAL.md` Backlog before emitting; skip any candidate
  whose `Source` matches an existing row.
- **Don't author acceptance criteria.** Backlog rows are
  *experiment ideas*, not goals with target deltas. The user
  judges the result after the run.
- **No Python execution from this skill.** Reading the digest is a
  `Read` tool call; fetching the doc URL is a `WebFetch` call.
  No `pixi run python …`, no `python -c …`. The only side effect
  this skill triggers is re-executing the audit runner (via
  `audit-ml-pipeline`) when the digest is missing.

## The inspection loop

1. **Locate the digest.** The audit digest for the latest `done`
   experiment lives at `scratch/audit/<stem>/audit.md`. If
   multiple `done` experiments exist, default to the most recent
   — surface the choice to the user only if they ask.
2. **Read the digest as text.** Use the `Read` tool.
3. **Walk the `## Checks summary` section.** For every row whose
   `severity` is `issue` or `tip`:
   - **Follow `documentation_url`** with `WebFetch`. The page
     describes what the check tests and what to try next.
   - **Draft the Backlog `Item`** from the page's recommended
     mitigations, phrased as a one-line experiment idea.
   - **Citation**: `audit:<stem>:checks.<code>` (e.g.
     `audit:01_baseline:checks.SKD003`).
4. **Dedup against the existing Backlog.** Read `JOURNAL.md`
   Backlog. Drop candidates whose citation already exists.
5. **Read the `## Metrics summary`** for context only — the
   headline metrics anchor the human summary paragraph.
6. **Compose the return block** below.

## What is returned

```
Backlog candidates (from: audit digest of <prev_stem>):
  - Item:    <one-line experiment idea derived from the docs URL>
    Source:  audit:<prev_stem>:checks.<code>
  - Item:    ...
    Source:  ...
  - ...

Dropped as duplicates (already in Backlog): <N>

Summary:
  <one paragraph for the user — counts, top 2-3 highlights, the
  headline metrics for context, and the doc URLs of the surfaced
  checks. Dense, not chatty.>
```

`iterate-ml-experiment` consumes this:
1. Writes the candidate rows into `JOURNAL.md` Backlog with stable
   `B<N>` indices appended at the end.
2. Surfaces the summary verbatim to the user.
3. Re-presents the sourcing menu with the enriched Backlog visible
   so the user can pick a `B<N>` row directly or pick `user` if
   the findings prompt a different direction.

## Companion skills

- **`iterate-ml-experiment`** — the caller; owns the design notes
  (including `JOURNAL.md`).
- **`audit-ml-pipeline`** — **the producer of the digest this
  skill reads**. The two skills share the same diagnostic surface
  but have opposite directions: `audit-ml-pipeline` opens the
  Project and renders the digest (write side); `iterate-from-skore`
  consumes the digest as text and follows the check doc URLs (read
  side).
- **`evaluate-ml-pipeline`** — for "what does the report say"
  before "what should we try next". The narrative read side; not
  used by this skill.
- **`iterate-from-user`** — the sibling sourcing strategy; sources
  from the user (article, resource, or free text) when the
  digest's findings aren't the right starting point.
