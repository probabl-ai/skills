---
name: iterate-ml-experiment
description: >
  Owns the iteration loop on top of an ML workspace: the
  `plan/PLAN.md` history log and the per-experiment
  `plan/NN_short_name.md` design notes that must be written
  **and validated by the user** before the matching
  `experiments/NN_short_name.py` is created. Drives the
  conversational loop where the next experiment is proposed,
  refined, and committed to plan, then dispatches to one of the
  `iterate-from-*` strategy skills when the source of the next
  proposal needs to be picked. Stops at "the plan file is on disk
  and the user has approved it".

  TRIGGER when: a session starts in an ML workspace that already
  has a `plan/` folder (read `PLAN.md` first to see where things
  stand); the user says "what's next", "resume", "where were we",
  "let's iterate", "propose the next experiment", or similar;
  about to create a new `experiments/NN_*.py` (the matching
  `plan/NN_*.md` must exist and be validated first); the user
  wants to record an outcome from a finished experiment in
  `PLAN.md`; the user asks to compare past experiments or review
  what's been tried.

  SKIP when: there is no `plan/` folder yet and no workspace
  scaffolded (route to `organize-ml-workspace` first); the work
  is mechanical inside `pipeline.py` / `evaluate.py` / `data.py`
  with no plan implication (those are owned by
  `build-ml-pipeline` / `evaluate-ml-pipeline`); the user asks
  for a symbol lookup (use the `*-api` skills); the user is
  reviewing/diagnosing a single skore report without a "what
  next" framing (route to `evaluate-ml-pipeline`).

  HOW TO USE: **First action — always — read `plan/PLAN.md` and
  emit the Pre-flight checklist as visible text in your
  response.** Both are mandatory before writing or modifying any
  plan file. Then use the **Mode picker** (top of the body) to
  decide which section to read this turn — the body covers six
  operational modes (bootstrap, iterate, goal pivots,
  abandoned, compare, overview); you only need one per turn.
  Plan files are the only artifact this skill writes; reads,
  comparisons, and overviews don't write.
---

# Iterate ML Experiment

The loop on top of `experiments/`: what to try next, why, what
counts as a result, and how the trail of past experiments is
recorded. Pipeline mechanics, evaluation mechanics, and workspace
layout are out of scope and live in sibling skills.

## First action (every turn)

Before answering anything else:

1. **Read `plan/PLAN.md`.** If it doesn't exist or is the
   placeholder dropped by `organize-ml-workspace`, you're in
   bootstrap mode (§ 0).
2. **Emit the Pre-flight checklist** (below) as visible text
   in your response, with each box marked.
3. **Use the Mode picker** to find which one section to read
   this turn.

Skipping any of these is a Stop-condition violation.

## Mode picker — read this before navigating the body

You only need to read **one** mode section per turn. Decide
which by matching the user's signal (or workspace state) to
the table, then jump straight to that section.

| User signal / workspace state | Mode | Section to read |
|---|---|---|
| `plan/PLAN.md` missing, empty, or placeholder; OR exists but has no rows in History | **Bootstrap** | § 0 Bootstrap |
| `plan/` not even scaffolded (no `src/`, no `experiments/`) | **Bootstrap → handoff first** | § 0 step 1, then `organize-ml-workspace` |
| "what's next?", "let's iterate", "propose next", "resume" — and PLAN.md has ≥1 done row | **Iterate (propose)** | §§ 1-3 + Dispatch table |
| "the run finished", "log the result", "we got X = ...", "record outcome" | **Iterate (record)** | § 4 |
| "where are we?", "give me a one-pager", "status?", "what have we tried?" | **Project overview** | § Project overview / status requests |
| "compare X and Y", "X vs Y", "trend across runs", "stack up against baseline" | **Compare (read-only)** | § Compare past experiments |
| "let's pivot the goal", "actually we care about <new metric>", goal change signal | **Goal pivot** | § Goal pivots |
| "abandon X", "drop X", "X isn't going to happen" | **Abandoned** | § Abandoned experiments |
| User wants to redo a prior experiment under different conditions (paired seeds, fixed splitter, …) | **Re-run** | § Re-runs |

If two modes seem to match (e.g., "compare X and Y, then propose
something based on it"), pick the **read** mode first
(Compare/Overview), surface its result, and stop. Re-entering
§ 1 for a propose-step is a separate user-driven turn.

## Stop conditions — read before anything else

- **No plan, no script.** Never create or edit
  `experiments/NN_*.py` until `plan/NN_*.md` exists, is filled
  in, and the user has explicitly approved it. The plan is
  written *first* and validated *first*; the script is a
  consequence of the plan, not the other way around. If you
  catch yourself about to write Python before the plan exists:
  STOP and write the plan.
- **`PLAN.md` is read at session start, not improvised.** When a
  session opens in a workspace with `plan/PLAN.md`, read the
  file before answering any "what next" question. Don't
  reconstruct history from `experiments/` filenames or
  `git log` — those don't carry the *why*.
- **Strategy is picked, not assumed.** When you propose a next
  experiment, name the sourcing strategy you used: user input,
  literature, methodology audit, diagnostic. If the user hasn't
  signalled one, ask. Don't silently mix strategies in a single
  proposal — that's how plans turn into wishlists. **Exception:
  bootstrap (§ 0).** When `PLAN.md` has no recorded experiment,
  the baseline is forced by the workspace defaults — no
  strategy dispatch, no "what do you want to try?". The user's
  role is to approve or amend the baseline, not invent it.
- **Approval is explicit.** "Looks good", "yes", "go" from the
  user is the gate. Anything ambiguous ("hmm interesting") is
  not approval. If unsure, ask.
- **Outcomes are recorded, not narrated.** When an experiment
  finishes, the outcome lands in `PLAN.md` *and* in the per-
  experiment file's status block, before the conversation moves
  on. The skore report is the source of truth for metrics; the
  plan files capture what was learned and what it implies for
  the next iteration.

## Pre-flight — emit this checklist as visible text before any plan write

Before writing or editing any file under `plan/`, output the
following block verbatim. Each box must be backed by an actual
tool call or an explicit decision documented in the response.

```
Pre-flight (iterate-ml-experiment):
- [ ] `plan/PLAN.md` read this turn (or confirmed missing → about to scaffold)
- [ ] Mode: bootstrap (no recorded experiment) | iterate
- [ ] Last experiment + its status known: <NN_name> | n/a (bootstrap)
- [ ] In iterate mode, the **sourcing menu was presented to the user
      verbatim** (see § "The sourcing menu") and the user picked one
      option — no silent default. Skip in bootstrap mode.
- [ ] Sourcing strategy chosen by user: my-pick | diagnostic |
      methodology | literature | user | backlog:B<N> |
      n/a — bootstrap, baseline forced by workspace defaults
- [ ] Strategy skill dispatched (iterate mode only): iterate-from-<...>
      | n/a — backlog item promoted directly
- [ ] Proposal turned into a `plan/NN_short_name.md` draft
- [ ] User has explicitly approved the plan file before any
      `experiments/NN_*.py` is touched
```

## Layout this skill owns

```
plan/
├── PLAN.md                     # session-start log + index + future ideas
├── 01_baseline.md              # design note for experiments/01_baseline.py
├── 02_text_encoder.md          # design note for experiments/02_text_encoder.py
└── ...
```

The pairing rule is hard: `plan/NN_short_name.md` ↔
`experiments/NN_short_name.py`, identical stems, one-to-one. The
plan file is created first and edited until the user approves;
the script is created only after that. This is the contract
that lets `PLAN.md` stay a faithful index of what was tried.

## `PLAN.md` shape

`PLAN.md` is a thin, durable index — *not* a long-form journal.
It has three sections:

1. **Status (top).** A two-or-three-line snapshot: the dataset,
   the project goal, the most recent experiment and whether it
   ran/passed/regressed. This is what you read first at session
   start.
2. **History (chronological).** One row per experiment: stem,
   one-line intent, status (planned / running / done / abandoned),
   headline result, link to the per-experiment plan file. New
   rows go at the bottom.
3. **Backlog (forward-looking).** Indexed **table** of ideas not
   yet committed to a `NN_*.md` file. Each row carries a stable
   `B<N>` index so the user can pick by number when choosing the
   next experiment ("go with B2"). Columns: `#`, `Item`, `Source`
   (where the idea came from — diagnostic from `<stem>`, user
   input, literature, etc.). When an item graduates into a plan
   file, the row is removed and the new experiment lands in
   History above. The skill **must surface this table to the
   user** every time it presents the sourcing menu (see § "The
   sourcing menu") — the backlog is one of the menu's branches,
   not a side-document.

Use `templates/PLAN.md` as the starting skeleton. Don't invent
new sections per project — the three sections above are the
contract.

## Per-experiment plan file

Each `plan/NN_short_name.md` file is the design note for one
experiment. It is **the proposal** while it is being drafted,
**the contract** once approved, and **the postmortem** once the
experiment has run. Use `templates/experiment_plan.md` as the
starting skeleton; sections are:

- **Question / hypothesis** — one sentence. What are we trying
  to learn? Not "try X" — *why* X, and what would it tell us.
- **Motivation** — why now. Pulled from the sourcing strategy:
  user request, paper, methodology audit, diagnostic finding.
  Cite concretely (issue link, paper title, prior experiment
  stem, report section).
- **Method** — what changes versus the previous experiment, in
  prose. Which file in `src/<pkg>/` is touched (`features.py`,
  `pipeline.py`, `evaluate.py`, `data.py`)? Mechanics live in
  `build-ml-pipeline` / `evaluate-ml-pipeline`; this section
  states the *intent*, not the code.
- **Risks / things that could invalidate the result** — what
  would make the metric move for the wrong reason (leakage,
  sample size, distribution shift, …).

**No "Success criteria" / "Acceptance criteria" section.** The
skill proposes and runs experiments; **the user judges whether
the result is good enough.** Inventing a target metric delta or
"this counts as success" line ahead of time is out of scope —
it nudges the run toward a foregone conclusion the user didn't
ask for. The post-run **Headline result** + **Implication**
fields (in the Status block) are the durable record; the user
reads them and decides what to do next.
- **Status block** (filled in over time): planned → approved →
  done | abandoned, with the headline result on completion.
  There is no observable "running" state — this skill is
  user-triggered, so the experiment sits in `approved` from
  script-creation until the user reports the outcome via § 4.

The status block is the only part that is updated *after* the
experiment runs. The other sections are frozen at approval —
that's what makes them useful as a postmortem.

## The conversational loop

This is the choreography that this skill owns end-to-end. There
are two modes — **bootstrap** (the very first session in a
workspace) and **iterate** (every session after that). Bootstrap
is one-shot; iterate is the recurring loop.

### 0. Bootstrap (first session only)

A workspace is in bootstrap mode when **either** `plan/PLAN.md`
is missing or is the one-line placeholder dropped by
`organize-ml-workspace`, **or** it exists but has no rows in
History (no experiment has been planned yet). In bootstrap mode
the session-start ritual below does **not** apply — there is no
last experiment to summarize and no backlog to look at. Instead:

1. **Scaffold first if needed.** If the workspace itself isn't
   in place (no `src/`, no `experiments/`, no `plan/`), hand
   off to `organize-ml-workspace`; come back here when its
   placeholder `PLAN.md` exists.
2. **Rewrite `PLAN.md` from this skill's template.** Read
   `templates/PLAN.md` and write it to `plan/PLAN.md`,
   replacing the placeholder. This skill — not
   `organize-ml-workspace` — owns plan content.
3. **Derive a goal default from what the project tells you.**
   Read `data/README.md` (or whatever dataset card / problem
   statement is at the project root) **before** asking the
   user. Synthesize one sentence of the form "minimize <metric>
   on <split> for <task description>" and propose it; the user
   confirms or amends. **Do not prompt the user with a blank.**
   If no README / dataset card exists, then ask — but make that
   the exception, not the default.
4. **Auto-draft `plan/01_baseline.md` via the consultation
   chain.** The baseline is forced, not invented — but its
   defaults come from sibling skills, not from memory:
   - **Learner default**: consult `build-ml-pipeline` for what
     a "baseline" means for the data shape (tabular
     regression / classification → skrub `tabular_learner`;
     other shapes have their own defaults).
   - **Splitter default**: consult `evaluate-ml-pipeline` for
     the cross-validator default (typically `KFold` for IID
     tabular, but the skill picks based on the data structure).
   - **Metric default**: consult `skore-api` for what
     `skore.evaluate` reports by default for the task type.
   - **Mismatch handling**: if any default conflicts with the
     project goal (e.g., the README requires Squared Error but
     skore's default is RMSE; the dataset has 1M rows and
     5-fold KFold may be slow / OOM), **flag it in the Risks
     section** of `01_baseline.md`. Don't silently override the
     default — surface the tension to the user.
5. **The user's role in bootstrap is to approve or amend the
   baseline plan**, not to invent it. Skip the strategy
   dispatch entirely for this one.
6. **Exit bootstrap.** Once the baseline is approved and
   recorded in `PLAN.md`'s History, the workspace is out of
   bootstrap. Every session afterwards uses § 1.

### 1. Session start (iterate mode)

- Read `plan/PLAN.md`.
- Summarize to the user, in two or three lines: dataset, goal,
  last experiment + its status, anything in the backlog that
  looks ripe.
- Ask explicitly: do you want to **resume the last experiment**
  (still planned / running / unfinished), **record an outcome**
  (the last one ran since we last spoke), or **propose the
  next** one?

### The sourcing menu

Every time § 2 runs in iterate mode, surface this menu **verbatim**
before any strategy dispatch — and pair it with the `PLAN.md`
Backlog table so the user can pick a `B<N>` row. The menu is the
contract: the skill never picks for the user.

```
How would you like me to source the next experiment?

  diagnostic   — read the latest skore report (residuals,
                 calibration, slice metrics) and propose from
                 what it surfaces.
  methodology  — audit the previous experiment(s) against good
                 ML practice (leakage, splitter, sample size,
                 baseline comparability, metric choice).
  literature   — search papers, blog posts, or library docs for
                 techniques applicable to this problem.
  user         — you describe an idea, point me at a GitHub
                 issue, or hand me a spec / notes repo to read
                 from.
  my-pick      — I synthesize across the above and pick what I
                 find most logical given the current state.
  B<N>         — promote a row from the Backlog table below
                 directly into a new experiment.

Backlog (pick by index):
<paste the PLAN.md Backlog table here>
```

Use `AskUserQuestion` (or whatever structured-pick UI the runtime
exposes) when available — six options + the backlog rows fits it
well. Otherwise enumerate the menu in plain text and wait for the
user's pick. **Do not silently default to one option** — even if
the latest experiment has a fresh diagnostic report, the user must
say "diagnostic". The Dispatch table below covers signal-driven
shortcuts (e.g. the user says "what does the report show?" — that
*is* a `diagnostic` pick); they short-circuit the menu but never
silence it.

### 2. Propose the next experiment

- **Always present the sourcing menu first** — see § "The
  sourcing menu" for the canonical wording. Surface the
  `PLAN.md` Backlog table next to it so the user can pick a
  `B<N>` row directly. **Do not silently default.** Use
  `AskUserQuestion` (or equivalent structured-pick UI) when the
  runtime offers it; otherwise enumerate the menu in plain text
  and wait for the user's pick.
- Once the user picks: dispatch as the picked option dictates —
  `diagnostic` / `methodology` / `literature` / `user` go to
  the matching `iterate-from-*` skill (see Dispatch table for
  edge cases); `my-pick` lets you synthesize across strategies;
  `B<N>` promotes the backlog row directly without invoking a
  strategy skill. Bring back a proposal: question, motivation,
  method outline.
- Write the draft to `plan/NN_short_name.md` using the
  template. The `NN` is the next free integer; the
  `short_name` is the user's call (offer one, don't force it).

### 3. Iterate on the plan with the user

- Show the draft to the user. Ask for changes.
- Edit `plan/NN_short_name.md` in place until the user explicitly
  approves. **Do not** create `experiments/NN_*.py` during this
  step — the plan file is the only artifact in play.
- **Track provenance honestly.** If the user's amendment touches
  only the **Risks** section (a guard-rail tweak), keep the
  original `Sourcing strategy` line. If it changes the
  **Method** (different transform, different estimator,
  different feature) — that's a *material* override. Update `Sourcing strategy` to
  `<original> + user override` (e.g., `diagnostic + user
  override`) and quote both the original source and the user's
  amendment in **Motivation**. The per-experiment file should
  never lie about its own origin.
- When the user approves, flip the status block from `planned` to
  `approved`, add the row to `PLAN.md` history (status:
  `approved`), and hand off to `organize-ml-workspace` to create
  the experiment script with the matching stem.

### 4. After the run

**Trigger is user-driven (v1).** This skill does **not**
auto-detect that a script has finished — no polling of the
skore Project store, no file-mtime watching, no background
hook. The user tells you "the run finished, record it" (or a
phrase like "log the result", "we got X"), and only then do
you start this step. If you suspect a run finished but the
user hasn't said so, ask — don't assume.

When triggered, decide first whether the report is **accessible
in this session** — i.e., the skore Project store exists at the
expected path (`reports/`) and contains the experiment's key.

**If accessible — read it programmatically.** Open the report
via the skore Project (route through
`evaluate-ml-pipeline` for the call site, and **invoke
`Skill(skore-api)` in this turn** to confirm the exact
signatures). For programmatic access to the diagnostic surface,
use **`report.diagnosis()`** — for v1 this is the only
programmatic entry point this skill relies on; do not reach
into other report attributes from memory. If you need a richer
diagnostic narrative for the user, hand off to
`evaluate-ml-pipeline`.

**If not accessible** (run was on a different machine, batch
system, the script crashed before `project.put`, …): **do not
fabricate report content from memory.** Ask the user for the
headline metric (and a one-line note on anything that looked
off). Mark the per-experiment file's "Implication" field as
"deferred — report not accessible this session" and pick the
diagnostic up next time.

In both branches, fill **all four** Status-block fields in
`plan/NN_*.md`:

- **State:** `done` (or `abandoned` with a one-line reason)
- **Approved by user on:** unchanged from approval (don't edit)
- **Headline result:** the metric + uncertainty (e.g.
  `RMSE 0.083 ± 0.004 (5-fold CV)`)
- **Implication for next iteration:** one or two sentences;
  this is the seed for the next strategy dispatch

And append the headline result to `PLAN.md`'s History row for
that experiment.

**Secondary findings → Backlog.** The diagnostic walk almost
always surfaces *more than one* signal. Pick the strongest as
the next-iteration seed (above), and append the rest to
`PLAN.md`'s **Backlog** as one-liners (e.g., "high-tail
variance after logit transform — investigate if we keep the
transform"). One bullet per finding; don't elaborate. The
backlog is a queue for future strategy dispatches, not a
journal.

**Backlog hygiene — prune what the latest run rendered moot.**
Before appending new items, scan the existing Backlog for
entries the just-finished experiment has answered, killed, or
made irrelevant. Examples: an item about logit-tail variance is
moot once we've abandoned the logit transform; an item about
slow KFold(5) is moot once we've moved to HoldOut. Two
treatments — pick whichever is cleaner per item:

- **Delete** the bullet outright if the rationale no longer
  applies (the transform / splitter / feature it referred to is
  no longer in the pipeline).
- **Strikethrough with a brief reason** (`~~old item~~ —
  resolved in 03_softer_transform`) if the item is worth
  preserving as breadcrumb but should not be picked up as a
  future proposal.

The backlog is a working queue, not an archive. If it grows
past ~10 items, prune more aggressively: a backlog that long
will not be read.

**Closing the loop with a GitHub issue (opt-in).** If the
just-recorded experiment's `Source` is a GitHub issue (the
`Sourcing strategy` was `user` and the `Source` field links
to `github.com/<owner>/<repo>/issues/<N>`), **offer** to post
the headline result back as an issue comment:

> "Source was issue #<N>. Want me to comment back with the
> headline (RMSE 0.087 ± 0.003) + a link to plan/<stem>.md? Y/N"

Never auto-post. The `gh issue comment` call only fires on
explicit user approval. If the user accepts, run
`gh issue comment <N> --body "<headline + plan-file link>"`;
if they decline, move on. This is the only outbound side
effect this skill is allowed; it exists to close the
feedback loop with the issue tracker without being
surprising.

**Stop here.** Do not auto-launch the next strategy dispatch in
the same turn. Surface the implication to the user as a one-
liner ("the residual bias near boundaries points at a target-
transform experiment — want me to draft it?") and **wait for
the user's go-ahead** before re-entering § 1. The user controls
cadence; this skill records, it doesn't propose-and-record in
one breath.

## Project overview / status requests

When the user asks "where are we?", "give me a one-pager",
"what's the status?", "what have we tried?" — that is a *read*
of `plan/PLAN.md`, not a new artifact. **PLAN.md is the canonical
project digest** (Status + History + Backlog, three sections by
design). Do not generate a separate summary document.

- For short asks ("status?"), surface the **Status block** verbatim
  plus the last one or two History rows.
- For "one-pager" / "where are we" framing, surface PLAN.md as-is
  (or summarize it section-by-section if it has grown long), and
  add a one-sentence "what's ripe next" line drawn from Backlog
  + most recent Implication. Nothing else.
- Do not write to `plan/` during these requests. Read-only.

If `PLAN.md` has drifted (Status references an experiment that
no longer matches History's last row, Backlog has stale items),
flag the drift to the user — but **don't auto-edit** during a
read-only request. Drift fixes belong to § 4 (next time an
outcome is recorded) or to an explicit "tidy up PLAN.md" ask.

## Goal pivots

Sometimes the project goal itself changes mid-stream — the
trader cares about typical error not squared error, so MSE → MAE;
the downstream consumer changes from offline batch to online
serving so latency joins the goal; the metric class changes
(regression → ranking). This is **not** an experiment;
it is a *strategic event* that affects how every future
experiment is judged.

When the user signals a goal pivot:

1. **Update `PLAN.md` Status** with the new goal and the date,
   keeping a one-line trace of what changed: `Goal pivoted
   <date>: <old> → <new>. Reason: <one sentence>.`
2. **Insert a horizontal-rule row in History** below the last
   pre-pivot experiment, formatted as a clear divider:

   ```
   | --- | **Goal pivoted <date>: <old> → <new>** | --- | rows above evaluated against <old>; rows below against <new> | --- |
   ```

3. **Do not mass-edit prior `plan/NN_*.md` files.** Their
   Success criteria are frozen at approval — that's the
   contract. Their Headline result cells in History stay too
   (they were valid against the old goal).
4. **The first post-pivot experiment auto-flags incomparability**
   in its **Risks** section: `"evaluating against new goal
   (<new>); not directly comparable to {<pre-pivot stems>} which
   used <old>."` This blocks silent cross-comparison across the
   pivot.
5. **Reset the anti-monoculture counter to 0.** The goal pivot
   is a strategic event; the prior diagnostic streak isn't
   relevant to the new goal.

A goal pivot is user-only — the skill never auto-pivots.

## Abandoned experiments

The lifecycle states are `planned → approved → running → done |
abandoned`. Abandonment is a real outcome and needs the same
handling rigor as `done`:

- **User-decided only.** The skill never auto-abandons. If an
  experiment has been planned/approved for many sessions
  without progress, *flag* it to the user ("`05_quantile_intervals`
  is still in `approved` status — abandon, defer, or run?")
  but do not change its state without an explicit answer.
- **Status block requires a one-line reason.** "Dependency was
  non-trivial to install; deferred to v2." "Method was
  superseded by 06_softer_transform's success." "Direction
  ruled out by literature finding in 04_monotonic_gbm." The
  reason is the whole point — it's what makes the
  abandonment a useful provenance signal rather than a gap.
- **`Headline result` becomes** `n/a — abandoned: <reason>`.
  The History row stays (provenance is the whole point); only
  the Status field flips.
- **Anti-monoculture counter is unaffected.** Abandoned
  diagnostic-sourced experiments do not count toward the
  two-consecutive streak — abandonment means the strategy
  didn't produce a real datapoint.
- **"Fresh report" eligibility is unaffected** (already
  excluded by fix #11's "status=done" requirement). An
  abandoned experiment never has a report to mine.
- A subsequent re-run of an abandoned experiment is a normal
  re-run (per § Re-runs); the abandoned row is not edited
  beyond the optional `Implication` back-link.

## Compare past experiments (read-only mode)

When the user says "compare 01 and 02", "how does this run stack
up against the baseline?", "what's the trend across runs?" — that
is **not** a new-experiment request. Don't draft a plan file.
Don't add a row to History. This is a *read* of past work.

**v1 scope: pairwise side-by-side, no programmatic
multi-stem comparison.** This skill family does not expose a
`ComparisonReport` / multi-key comparison entry point in v1 —
deliberately. The handoff to `evaluate-ml-pipeline` is
single-learner by its declared scope, and we do not stretch it.
Procedure for "compare X and Y":

- **Headline side-by-side.** Pull the Headline result cells for
  each requested stem from `PLAN.md` History and surface them
  side by side, with one-sentence intent for each (also from
  History). This is usually enough to answer "is the new one
  worth it?".
- **Deeper read, one report at a time.** If the user wants more
  than the headline (residuals, calibration, slice metrics),
  route to `evaluate-ml-pipeline` **once per stem, separately**
  — that skill is single-learner by scope. The user does the
  cross-experiment synthesis from the two narratives; the skill
  does not.
- **Don't write to `plan/`** during a compare request. If the
  side-by-side reading surfaces a finding the user wants to act
  on, re-enter § 1 with the appropriate strategy (typically
  `diagnostic` if the finding came from a per-stem report walk;
  `methodology` if it came from a fairness concern between
  splits or seeds across the two).

**v2 gap, flagged.** Statistical comparison (significance tests,
shared-fold paired comparisons, multi-key `ComparisonReport`)
is out of scope for v1. If the user explicitly asks for a
significance test or "stat-sig comparison", surface this gap:
*"v1 doesn't expose programmatic multi-stem comparison; for
significance, you'd need to run a paired re-run (see § Re-runs
→ Batch re-run) and compare the per-fold metrics manually."*

The plan files are the durable record of *experiments tried*;
comparisons are derived views, not new entries.

## Re-runs

Sometimes the right next step is to *redo* a prior experiment
under different conditions — paired seeds for a fair comparison,
a corrected splitter, a fresh data snapshot. A re-run is a new
file, **never** an in-place edit. Two shapes, dispatched by
how many prior experiments are being redone:

### Single re-run (one prior target)

Use when the methodology audit (or user request) targets exactly
one prior experiment.

- New stem: `NN_<original_stem>_rerun.py` and the matching
  `plan/NN_<original_stem>_rerun.md`. The numeric prefix is the
  next free integer; `<original_stem>` preserves provenance.
- `Sourcing strategy` line: typically `methodology re-run`
  (occasionally `user re-run` if the request is direct).
- **Motivation** must quote the original experiment stem and
  state precisely what changed (the fix being tested).
- **Method** notes that the experiment is a re-run and what is
  held constant from the original.

### Batch re-run (N prior targets)

Use when the methodology audit returns N≥2 re-run targets — for
example, "redo 01, 02, 03 with paired seeds and a fixed
splitter so the comparisons are sound." This is **one**
methodological intervention, not N; it gets **one** plan file.

- New stem: `NN_paired_comparison.py` and
  `plan/NN_paired_comparison.md` (or another descriptive name
  reflecting the controlled condition: `NN_seeded_redo`,
  `NN_aligned_splits`, …). One numeric prefix; one approval; one
  History row.
- `Sourcing strategy`: `methodology batch re-run`.
- **Motivation** quotes the methodology finding and the
  comparability gap it surfaced.
- **Method** lists the rerun targets explicitly (`{01, 02, 03}`)
  and the controlled condition that's being applied uniformly
  (paired seed, identical splitter, …). The script will produce
  **multiple report keys** in the skore Project — one per
  rerun target — under a shared prefix
  (e.g., `paired:01`, `paired:02`, `paired:03`).
- **Outcome shape** is a comparison, not a single metric: the
  experiment produces multiple report keys (one per re-run
  target) and the user reads them side-by-side to judge whether
  the prior ranking holds or flips. The skill does not predefine
  what counts as a "successful" comparison — the user owns the
  call.

### Both shapes

A new row goes into `PLAN.md` History at approval; the
original rows are **not** edited. The `Implication` block of
each original may be updated post-re-run with a one-line link
("see `NN_X_rerun` for the seeded comparison" or
"see `NN_paired_comparison` for the paired-seed redo") — that
is the only edit allowed to a frozen file.

In-place edits to an approved plan file are reserved for the
Status block. Re-runs are not amendments — they're new
experiments that happen to share most of the design.

## Dispatch table — which iterate-from-* skill

Use the user's framing first; fall back to defaults below.

| Situation | Skill |
|---|---|
| **No prior experiment in `PLAN.md`** (bootstrap) | None — § 0 forces an auto-drafted baseline. The strategy skills only apply once at least one experiment is recorded. |
| **`PLAN.md` Backlog has an actionable item** relevant to the latest report (e.g., a secondary diagnostic finding that wasn't acted on) | None — *promote the backlog item* to the user **first**, before any strategy dispatch. The backlog is pre-mined work; re-mining is wasted compute and can produce a different answer the second time. If the user accepts, frame the proposal directly from the backlog text and skip the strategy skill. If the user passes, fall through to the rows below. |
| "I want to try X", "let's add Y", a GitHub issue link | `iterate-from-user` |
| "any papers on this?", "what does the literature say?", "how do people usually handle X?" | `iterate-from-literature` |
| "did we get the split right?", "is this leaking?", "small sample size?" | `iterate-from-methodology` |
| "the report shows X", "calibration looks bad", "why is slice Y so off?" | `iterate-from-diagnostic` |
| Open-ended ("what's next?") with at least one recorded experiment | **Present the sourcing menu** (see § "The sourcing menu") — paired with the Backlog table — and let the user pick. No silent default. The "Fresh report" / anti-monoculture rules below only apply when the user picks `my-pick`; in every other case the user has already chosen the strategy. |

**"Fresh report" definition.** A report is *fresh* when **all
three** hold: (1) the latest experiment in `PLAN.md` has
`status=done` (i.e., § 4 has run for it); (2) no later
experiment row exists in History; (3) no per-experiment plan
file already cites it as its `Source` (i.e., we haven't already
drawn a proposal from this report's diagnostic). Once a
diagnostic-sourced proposal is approved, the underlying report
is no longer "fresh" — fall through to methodology / literature
/ user for the next round.

**Anti-monoculture rule.** After **two consecutive
diagnostic-sourced approved experiments** in the History, the
default order for the *next* open-ended dispatch becomes
`methodology → literature → user`, and `diagnostic` drops to
last. Diagnostic strategy is sharp but narrow: looping on it
runs a project into local minima of "what the last report said
to do". The rule is a default, not a gate — if the user
explicitly asks for diagnostic, honor it. Reset the counter
when any non-diagnostic strategy is approved, **or** when
`iterate-from-methodology` returns the `methodology_clean`
payload (no proposal — see below).

**Handling "no proposal" outcomes from strategy skills.** Two
strategies can return a structured "nothing actionable" payload
instead of a proposal — that is a real outcome, not a failure:

- `iterate-from-methodology` →
  `{ "outcome": "methodology_clean", "audited": [<stems>] }`
- `iterate-from-literature` →
  `{ "outcome": "literature_empty", "queries": [...],
  "considered": [<short list of titles ruled out and why>] }`

When either fires:

- Append a one-liner under `PLAN.md` Status, citing the strategy
  and the date — e.g. `Methodology audit clean on {01,02,03}
  as of <date>` or `Literature empty on <topic> as of <date>;
  considered: <short list>`. **Do not** add a History row —
  nothing was experimented on.
- For `methodology_clean`, reset the anti-monoculture counter
  to 0. For `literature_empty`, the counter is unchanged
  (literature wasn't a diagnostic-counter-resetting outcome
  to begin with).
- Continue the dispatch rotation to the next strategy in the
  default order (after methodology → literature → user; after
  literature → user). Don't ask the user to re-pick — the
  empty / clean result *is* the signal to move on.
- **`user` in the rotation isn't a skill invocation — it's a
  question to the user.** `iterate-from-user` only fires when
  the user has volunteered an idea; it isn't designed to be
  "asked" by the dispatcher. When the rotation reaches `user`
  after methodology and literature both came up empty, **ask
  the user directly** with the three options laid out:

  > Methodology was clean and literature came up empty. Three
  > paths from here: (a) you propose something concrete and we
  > go from there; (b) wait for new data or a fresh run before
  > iterating; (c) reframe the project goal — maybe the
  > current target isn't the right one. Which?

  Do not invoke `iterate-from-user` without an idea in hand,
  and do not pick (a)/(b)/(c) for the user — the rotation
  ends in a human conversation, not another silent dispatch.

The strategy skills are intentionally shallow: each one knows
how to *source* a proposal and hand it back here. This skill is
where the proposal becomes a plan file. The `methodology` and
`diagnostic` strategies require a prior experiment — that's why
bootstrap (§ 0) skips dispatch entirely.

## What this skill does NOT do

- Run experiments. The experiment script is created by
  `organize-ml-workspace` and executed by the user / their
  runner.
- Open or query the skore Project. That's
  `evaluate-ml-pipeline` and the `skore-api` lookups.
- Edit `pipeline.py` / `features.py` / `data.py`. Those are
  owned by `build-ml-pipeline`.
- Decide *whether* a workspace exists or where things go. That's
  `organize-ml-workspace`.
- Write commits or PRs describing what was done. The plan files
  are the durable record; commit messages are out of scope here.
- **Define what counts as a successful experiment.** No
  "Success criteria" / "Acceptance criteria" / "target metric
  delta" written ahead of the run. The skill proposes, the
  experiment runs, the headline result is recorded; the user
  judges whether it's good enough and what to try next.
- **Pick a sourcing strategy on the user's behalf.** The
  sourcing menu is the contract — § 2 always presents it and
  waits for the user's pick.

## Companion skills

- **`organize-ml-workspace`** — scaffolds `plan/` (empty
  `PLAN.md`); enforces the stem-pairing rule between
  `plan/NN_*.md` and `experiments/NN_*.py`.
- **`iterate-from-user`** — sources the next experiment from
  user input or a GitHub issue tracker.
- **`iterate-from-literature`** — sources from web search over
  papers/docs.
- **`iterate-from-methodology`** — sources by auditing the
  methodology of the last experiment.
- **`iterate-from-diagnostic`** — sources by inspecting the
  skore report (residuals, calibration, slice metrics).
- **`evaluate-ml-pipeline`** — read the skore report after a run
  before recording the outcome.
- **`build-ml-pipeline`** — implementation of the *method*
  section once the plan is approved.

## Templates

- `templates/PLAN.md` — the three-section index skeleton.
- `templates/experiment_plan.md` — the per-experiment design
  note skeleton with status block.

Copy, don't rewrite. The templates encode the contract — keep
the section names stable so `PLAN.md` stays diffable across
experiments and sessions.
