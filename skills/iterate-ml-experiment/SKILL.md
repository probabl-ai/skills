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
  for a symbol lookup (use the `python-api` skill); the user is
  reviewing/diagnosing a single skore report without a "what
  next" framing (route to `evaluate-ml-pipeline`).

  HOW TO USE: **First action — always — read `plan/PLAN.md` and
  emit the Pre-flight checklist as visible text in your
  response.** Both are mandatory before writing or modifying any
  plan file. Then use the **Mode picker** (top of the body) to
  decide which section to read this turn — the body covers seven
  operational modes (bootstrap, iterate, overview, compare,
  goal pivots, abandoned, re-runs); you only need one per turn.
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
2. **Read `overview/summary.md` if it exists.** The workspace
   carries an agent-authored narrative digest at
   `overview/summary.md` — project framing + cross-experiment
   metrics table + curated per-experiment Headline + Implication
   blocks. `PLAN.md` is the *index* (Status, History one-liners,
   Backlog); `summary.md` is the *narrative* (what was learned,
   in one scannable read). Both are agent-facing; read both at
   session start. The source of truth remains the per-experiment
   plan files in `plan/NN_*.md` — `summary.md` is the curated
   view across them, rewritten by hand at every § 4 outcome
   recording (no auto-generation script).
3. **Emit the Pre-flight checklist** (below) as visible text
   in your response, with each box marked.
4. **Use the Mode picker** to find which one section to read
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
  experiment, name the sourcing strategy you used: `skore`
  (diagnostic findings mined from the prior report), `user`
  (user idea / article / issue / spec), `my-pick`
  (agent-synthesized candidates the user chose from), or
  backlog-promotion (`B<N>`). If the user hasn't signalled one,
  ask — but accept clear free-text intents (see § "The
  sourcing menu" § Free-text handling). Don't silently default
  to one — that's how plans turn into wishlists.
  **Exception: bootstrap (§ 0).** When `PLAN.md` has
  no recorded experiment, the baseline is forced by the
  workspace defaults — no strategy dispatch, no "what do you
  want to try?". The user's role is to approve or amend the
  baseline, not invent it.
- **Approval is explicit.** "Looks good", "yes", "go" from the
  user is the gate. Anything ambiguous ("hmm interesting") is
  not approval. If unsure, ask.
- **Outcomes are recorded, not narrated.** When an experiment
  finishes, the outcome lands in `PLAN.md` *and* in the per-
  experiment file's status block, before the conversation moves
  on. The skore report is the source of truth for metrics; the
  plan files capture what was learned and what it implies for
  the next iteration.
- **Prior experiments stay reproducible.** Every `done` row in
  `PLAN.md` History must remain runnable on `main` and produce
  the same result. When the next iteration touches a shared
  module under `src/<pkg>/` (`features.py`, `pipeline.py`,
  `data.py`, `evaluate.py`), the **default behavior must
  preserve prior experiments' shape** — never silently change
  what `build_learner()` returns for a caller that didn't ask
  for the new feature. The choice of *how* — parametrize an
  existing function with a default that mirrors prior behavior,
  add a new function called only from the new experiment, or
  branch the module — is a judgment call; the criterion lives
  in `build-ml-pipeline` § "Reproducibility mechanics". The
  cheap executable check is `tests/smoke/` (see § 4's smoke-
  test gate): if any prior smoke test goes red, default
  behavior is broken.
- **Three skills, in order, before any code lands in
  `src/<pkg>/`.** After plan approval, the implementation step
  is *not* "let me write the modules"; it is a non-skippable
  three-skill sequence:
  1. `build-ml-pipeline` — `pipeline.py`, `features.py`,
     `data.py` (the pipeline declaration).
  2. `evaluate-ml-pipeline` — `evaluate.py` (cross-validator,
     metric overrides). This skill owns the CV-strategy choice
     and surfaces it to the user via `AskUserQuestion`; writing
     `evaluate.py` without invoking it is the most common
     shortcut and means the user never got to pick.
  3. `test-ml-pipeline` → `smoke-test-ml-pipeline` — the
     matching smoke test.

  Then `experiments/NN_*.py` ties them together. None of the
  three skills may be substituted by "I'll just write the file
  myself" — they exist to surface decisions to the user. If
  you catch yourself opening `src/<pkg>/evaluate.py` directly
  in Write/Edit without an `evaluate-ml-pipeline` invocation
  earlier in the same turn, STOP and invoke the skill.

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
- [ ] Sourcing strategy chosen by user: skore | user | my-pick |
      B<N> | n/a — bootstrap, baseline forced by workspace
      defaults
- [ ] Strategy skill dispatched (iterate mode only):
      iterate-from-skore | iterate-from-user | n/a — my-pick or
      backlog item handled inline
- [ ] Proposal turned into a `plan/NN_short_name.md` draft
      (or, for `skore`, Backlog enriched and the sourcing menu
      re-presented — no plan file on this turn)
- [ ] User has explicitly approved the plan file before any
      `experiments/NN_*.py` is touched
- [ ] Post-approval implementation chain (§ 3) is the three-skill
      sequence: `build-ml-pipeline` → `evaluate-ml-pipeline` →
      `test-ml-pipeline` (→ `smoke-test-ml-pipeline`) — *none*
      substituted by writing the file directly. `evaluate.py` in
      particular has `evaluate-ml-pipeline` invoked first.
      (n/a outside § 3.)
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
   next experiment ("go with B2"). Columns: `#`, `Item`, `Source`.
   The `Source` field follows one of three conventions:
   - `skore:<stem>` — written by `iterate-from-skore` from the
     report of `<stem>`.
   - `my-pick:<stem>` — written by § 4 when an experiment's
     Implication seeds future-iteration leads, or by § 2's
     `my-pick` branch when unpicked candidates are saved. The
     `<stem>` is the experiment whose context (Implication,
     Risks, …) fed the synthesis.
   - `user` — the user added the row directly (in conversation,
     not via a strategy skill).

   When an item graduates into a plan file, the row is removed
   and the new experiment lands in History above. The skill
   **must surface this table to the user** every time it presents
   the sourcing menu (see § "The sourcing menu") — the backlog
   is one of the menu's branches, not a side-document.

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
  a user idea (free-text), an article the user pointed at, a
  GitHub issue / spec resource, or a skore diagnostic finding
  promoted from the Backlog. Cite concretely (issue link, paper
  title, prior experiment stem, `report.diagnosis()` section).
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
   - **Metric default**: consult `python-api` for what
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
- **Ask via `AskUserQuestion`** — three mutually exclusive
  options, no silent default:
  - **resume** — the last experiment is still
    planned / approved / unfinished; pick up where we left off.
  - **record outcome** — the last one ran since we last spoke;
    enter § 4 to log the result.
  - **propose next** — the last experiment is `done` or
    `abandoned`; enter § 2 to pick a sourcing strategy.

  Free-text continuations ("let's keep going", "yeah") are
  ambiguous between the three branches — wait for an explicit
  pick.

### The sourcing menu

Every time § 2 runs in iterate mode, surface this menu
**verbatim** before any strategy dispatch — and pair it with the
`PLAN.md` Backlog table so the user can pick a `B<N>` row. The
menu is the contract: the skill never *silently* picks for the
user, but it does propose candidates when asked (via `my-pick`).

```
How would you like me to source the next experiment?

  skore    — call `report.diagnosis()` on the latest run; convert
             each actionable finding into a row in the Backlog
             below, summarize, and re-present this menu so you
             can pick a B<N> row.
  user     — you tell me what to try, one of three ways:
               (a) paste a scientific article URL — I read it
                   and synthesize before drafting,
               (b) point me at a GitHub issue / spec file /
                   reference repo,
               (c) just describe the idea in free text.
  my-pick  — I synthesize from current context (PLAN.md Status,
             the last experiment's Implication and Risks, the
             current Backlog) and propose 2-4 candidate ideas;
             you pick one via a follow-up AskUserQuestion. Use
             this when you want suggestions rather than mining
             a specific report.
  B<N>     — promote a row from the Backlog table below directly
             into a new experiment (no strategy skill invoked).

Backlog (pick by index):
<paste the PLAN.md Backlog table here>
```

Use `AskUserQuestion` for the pick — four options plus the
backlog rows displayed as context. Only fall back to plain-text
enumeration if `AskUserQuestion` is genuinely unavailable in the
current session. **Do not silently default to one option** —
even if a fresh report sits on disk, the user must say `skore`
(or `my-pick`, etc.). The Dispatch table below covers
signal-driven shortcuts (e.g. the user says "mine the report"
— that *is* a `skore` pick); they short-circuit the menu but
never silence it.

### Free-text handling

Users can type free text instead of picking a structured option.
Process it as follows, in priority order — first rule that
matches wins:

- **Exact-match (case-insensitive, whitespace-trimmed) to an
  option label** (`skore` / `user` / `my-pick` / `B<N>`):
  treat as that pick and proceed.
- **A backlog reference** (`B2`, `let's do B2`, `B2 please`):
  treat as the `B<N>` pick for that row.
- **A scientific article URL pasted directly** (the message is
  primarily a URL): treat as `user` → article-link branch,
  passing the URL to `iterate-from-user` and skipping its inner
  entry-point AskUserQuestion.
- **A GitHub issue URL, `org/repo#N` shorthand, or a spec file
  path**: treat as `user` → resource-link branch, skipping the
  inner AskUserQuestion.
- **A meta-request** ("give me ideas", "what do you suggest",
  "you decide", "come up with something", "propose for me"):
  treat as `my-pick`.
- **A concrete experiment idea typed inline** ("let me try
  adding future weather covariates", "use a quantile regression
  instead"): treat as `user` → free-text branch, passing the
  text in as the idea and skipping the inner AskUserQuestion.
- **Ambiguous or off-menu** ("hmm", "I'm not sure", "what?"):
  fire a clarifying AskUserQuestion — do not guess.

The goal: never block the user on the structured pick when
their intent is clear from free text. The structured pick is
the *default*, not the *only* path.

### 2. Propose the next experiment

- **Always present the sourcing menu first** — see § "The
  sourcing menu" for the canonical wording. Surface the
  `PLAN.md` Backlog table next to it so the user can pick a
  `B<N>` row directly. **Do not silently default.** Use
  `AskUserQuestion` for the pick (the runtime exposes it); only
  fall back to plain-text enumeration if `AskUserQuestion` is
  genuinely unavailable in the current session.
- Once the user picks (or their free text resolves to a pick
  per § "Free-text handling"), the four branches diverge:

  - **`skore`** — dispatch to `iterate-from-skore`. The skill
    walks `report.diagnosis()` and returns Backlog-candidate
    rows + a one-paragraph summary. **Write the rows into
    `PLAN.md` Backlog** with stable `B<N>` indices appended at
    the end, surface the summary to the user verbatim, and
    **re-present the sourcing menu** with the enriched Backlog
    visible. *No plan file is drafted on this turn* — the
    proposal comes from the user's next pick (typically `B<N>`).
  - **`user`** — dispatch to `iterate-from-user`. The skill
    opens its own `AskUserQuestion` (article-link /
    resource-link / free-text), gathers the source, synthesizes,
    confirms with the user, and returns a Proposal block. If
    the free-text handler already resolved the entry point
    (URL / issue link / inline idea), pass the resolved
    branch + content to `iterate-from-user` so it skips its
    inner AskUserQuestion. Draft into `plan/NN_short_name.md`
    per the bullet below.
  - **`my-pick`** — *handled inline by this skill, no sibling
    skill invoked.* Read PLAN.md Status, the last experiment's
    `plan/NN_*.md` (Implication, Risks), and the current Backlog
    state. Synthesize 2-4 candidate next-experiment ideas drawn
    from that context; present them via a follow-up
    `AskUserQuestion` (one option per candidate, short labels,
    one-line descriptions). The user picks one. The picked idea
    becomes the seed for a Proposal block with
    `Sourcing strategy: my-pick` and a `Source` field citing
    which context fields fed the synthesis (e.g.
    `my-pick: 01_baseline.md Implication`). Unpicked candidates
    are discarded — the user can re-invoke `my-pick` later if
    they want a fresh shortlist. Then draft the plan file per
    the bullet below.
  - **`B<N>`** — promote the named Backlog row directly: no
    strategy skill invoked. The row's `Item` text becomes the
    seed for the new plan file's `Question` / `Method outline`;
    the row's `Source` becomes the `Sourcing strategy` (e.g.
    `skore:02_target_transform` for a row that came from mining
    `02`'s report). Remove the row from Backlog when the plan
    file is approved.

- For the `user`, `my-pick`, and `B<N>` branches: write the
  draft to `plan/NN_short_name.md` using the template. The `NN`
  is the next free integer; the `short_name` is the user's call
  (offer one, don't force it).

### 3. Iterate on the plan with the user

- Show the draft to the user — surface the file path plus a 3-5
  line headline summary (Question / Method bullets / Risks
  bullets) so the user can read in chat or open the file.
- **Mid-iteration feedback is free-text.** The user pushes back
  on Method / Risks / scope / short_name in plain language; edit
  `plan/NN_short_name.md` in place and re-surface the changes.
  Loop here for as long as the user keeps amending.
- **The final approval gate is an `AskUserQuestion`** with two
  options:
  - **approved** — flip status to `approved`, add the row to
    `PLAN.md` History, hand off to `organize-ml-workspace`.
  - **more changes** — back to the free-text amendment loop.

  Fire it once you've made all requested changes or the user
  has stopped pushing back. Clear free-text "approved" / "go"
  / "looks good" resolves to the approve option per § "Free-
  text handling"; ambiguous responses ("hmm interesting", "I
  guess") get the structured pick — don't infer approval.
- **Do not** create `experiments/NN_*.py` during this step —
  the plan file is the only artifact in play.
- **Track provenance honestly.** If the user's amendment touches
  only the **Risks** section (a guard-rail tweak), keep the
  original `Sourcing strategy` line. If it changes the
  **Method** (different transform, different estimator,
  different feature) — that's a *material* override. Update
  `Sourcing strategy` to `<original> + user override` (e.g.,
  `skore:02 + user override` or `user:article + user override`)
  and quote both the original source and the user's amendment in
  **Motivation**. The per-experiment file should never lie about
  its own origin.
- When the user approves, flip the status block from `planned` to
  `approved`, add the row to `PLAN.md` history (status:
  `approved`), and hand off to `organize-ml-workspace` to create
  the experiment script with the matching stem.
- **Three-skill implementation chain, in order, before the
  experiment script is wired:**
  1. **`build-ml-pipeline`** for `src/<pkg>/{pipeline,features,
     data}.py` — the pipeline declaration, X-marker placement,
     `split_kwargs` wiring.
  2. **`evaluate-ml-pipeline`** for `src/<pkg>/evaluate.py` —
     cross-validator + metric overrides. *This skill is
     non-skippable.* It owns the CV-strategy decision and
     surfaces it to the user via `AskUserQuestion`; writing
     `evaluate.py` from memory (e.g. dropping in
     `KFold(5)` / `TimeSeriesSplit(5)` because they "feel
     right") bypasses the user choice this skill exists to
     enable. Even if `split_kwargs` at the X marker is empty,
     `evaluate-ml-pipeline` must be invoked — its rule 3
     mapping table is what justifies that emptiness.
  3. **`test-ml-pipeline`** → `smoke-test-ml-pipeline` for the
     matching smoke test at
     `tests/smoke/test_NN_<short_name>.py`.

  Only after all three have written their files does the
  experiment script in `experiments/NN_*.py` get assembled. The
  script is the integrator, not the place where evaluation
  decisions land.

  **This skill owns the assembly.** After the three-skill chain
  completes, *this skill* rewrites `experiments/NN_<short_name>.py`,
  overwriting the scaffold-time template that `organize-ml-workspace`
  step 5 dropped (which had `<pkg>` substituted but otherwise
  carried placeholder cells). The rewrite plugs in the real
  imports, sets `skore.Project(..., name=...)` from the project
  name, calls `skore.evaluate(learner, data={...}, splitter=splitter)`,
  and persists via `project.put("<stem>", report)`. Confirm
  signatures via `Skill(python-api)` rather than guessing from
  memory.

  Stop-condition restatement: if you catch yourself opening
  `src/<pkg>/evaluate.py` in Write/Edit and you have not invoked
  `evaluate-ml-pipeline` earlier in this turn, STOP and invoke
  the skill before continuing.
- **The smoke test is non-optional** for every approved experiment
  (per `test-ml-pipeline`'s required-test-per-experiment rule) and
  must exist before the experiment runs, so a structural
  pipeline bug shows up at iteration time rather than after the
  CV report is in hand. Do not
  start the experiment run before **all of `tests/smoke/` has
  passed locally** (the new test *and* every prior experiment's
  test). The new test catches structural bugs in this
  experiment's pipeline shape; the prior tests catch
  reproducibility regressions — if your change to a shared
  `src/<pkg>/` module silently broke a previous experiment's
  default path, *their* test goes red here, cheaply, before any
  CV time is spent. Route both failure modes to
  `build-ml-pipeline` (pipeline-shape bug → X-marker rule;
  reproducibility regression → § "Reproducibility mechanics").
- **Once the smoke test passes, ask whether to run the
  experiment.** Use `AskUserQuestion` with exactly two options:
  - **run now** — execute
    `pixi run python experiments/NN_<short_name>.py`
    directly in this turn. The user signed off on the run; the
    skill does not hand back a shell command for the user to
    copy-paste.
  - **leave for later** — do **not** print the command, do
    **not** auto-propose the next experiment. Instead, surface
    a short read of `PLAN.md` so the user can see where things
    stand: the **Status block** verbatim plus the **Backlog
    table** verbatim. Then stop. § 4 fires whenever the user
    later comes back with "the run finished, record it".

  No silent default — even if the smoke test passed cleanly,
  the user picks. The two options above are the only branches;
  this is the gate between "ready to run" and "actually ran".

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
`Skill(python-api)` in this turn** to confirm the exact
signatures). For programmatic access to the diagnostic surface,
use **`report.diagnosis()`** — for v1 this is the only
programmatic entry point this skill relies on; do not reach
into other report attributes from memory. If you need a richer
diagnostic narrative for the user, hand off to
`evaluate-ml-pipeline`.

**Do the inspection in `scratch/`, not in the experiment
script.** The experiment script's job ends at
`project.put(...)`. To pull metrics, walk the diagnosis, or
sanity-check any post-run state, write a
`scratch/<YYYY-MM-DD>_<HHMMSS>_<short>.py` and run it (see
`scratch/README.md` for the full convention). Inline
`pixi run python -c "..."` is reserved for ≤ 2 lines; anything
longer goes to `scratch/`. Do **not** edit the experiment
script to add agent-only `print` calls — the script is the
durable record of what was run; the inspection trace lives
in `scratch/`.

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

**Smoke-test gate before `done` — full `tests/smoke/`, not just
the new one.** An experiment cannot flip to `done` until
**every test in `tests/smoke/` passes**, including the prior
experiments' tests. The new experiment's smoke test catches
structural bugs in *its* pipeline shape; the prior experiments'
smoke tests catch the reproducibility regression rule (Stop
conditions, above) — if your change to `pipeline.py` /
`features.py` / `data.py` silently changed what `build_learner()`
returns for a caller that didn't opt in, *their* test will go
red. Both failure modes route to `build-ml-pipeline`: pipeline-
shape bugs to its X-marker rule, reproducibility regressions to
its § "Reproducibility mechanics" (pick parametrize / new
function / branch the module per the judgment ladder). Resolve;
re-run; only then re-record the outcome. The CV report can land
in the skore Project regardless (CV is independent of
predict-time binding), but the experiment row in `PLAN.md`
stays `approved` until the full smoke suite is green.
**Abandonment** does not require passing smoke tests — an
experiment can move from `approved` straight to `abandoned`
with a one-line reason on State, exactly as before.

And append the headline result to `PLAN.md`'s History row for
that experiment.

**Backlog hygiene at outcome time.** Scan the existing Backlog
for items the just-finished experiment has answered, killed, or
made irrelevant — items about a feature / splitter / transform
no longer in the pipeline. Two treatments per item:

- **Delete** the bullet outright if the rationale no longer
  applies.
- **Strikethrough with a brief reason** (`~~old item~~ —
  resolved in 03_softer_transform`) if the breadcrumb is worth
  preserving but should not be promoted to a future proposal.

Diagnostic mining of the *new* report is **not** done here —
that is `iterate-from-skore`'s job, triggered when the user
picks `skore` from the sourcing menu in a later turn. § 4 only
prunes existing items; it never appends new findings.

**Refresh `overview/summary.md` — agent-authored, scratch-driven.**
`summary.md` is *not* generated by a script. It is rewritten by
hand at every outcome recording so the cross-experiment
narrative stays curated rather than dump-pasted. Procedure,
once the per-experiment Status block and `PLAN.md` are up to
date:

1. **Probe the data via a scratch script.** Write
   `scratch/<YYYY-MM-DD>_<HHMMSS>_refresh_summary.py`. The
   script's job is *extraction*, not formatting:
   - Open the skore Project (consult `Skill(python-api)` for
     `Project` / `summarize` signatures in this turn — don't
     guess) and call `project.summarize()` for the
     cross-experiment metrics table.
   - List `plan/[0-9][0-9]_*.md` files and extract each one's
     `## Status` block (State, Headline result, Implication).
   - Print or pickle whatever the agent needs to read next.

   `pixi run python scratch/<ts>_refresh_summary.py` — output
   lands in the conversation; the file stays on disk per the
   scratch convention (append-only after success).

2. **Rewrite `overview/summary.md` by hand** from the probe
   output. The structure is fixed by the placeholder; fill it:
   - **Project narrative** — 1-2 paragraphs covering dataset,
     goal, and the path so far (what was tried, where the
     metric stands).
   - **Cross-experiment metrics** — a curated table from
     `project.summarize()`. Drop columns that aren't comparable
     across the listed experiments (e.g. classification metrics
     in a regression-only project, fit-time / predict-time
     unless the user cares).
   - **Per-experiment status** — one subsection per `done`
     experiment with the curated Headline + Implication. Quote
     the plan's Status text where it's already concise; rewrite
     where it isn't. The point is a *narrative*, not a paste.

   **Do not regenerate from a script.** If `overview/summary.py`
   exists in a legacy workspace, delete it (after this rewrite
   lands) — the per-version contract is "summary.md only".

3. If the workspace has no `overview/summary.md` at all
   (bootstrapped before this contract, or a fresh scaffold
   where § 4 has never fired), drop the placeholder from
   `organize-ml-workspace`'s `templates/summary.md` first, then
   rewrite per steps 1-2.

**Closing the loop with a GitHub issue (opt-in).** If the
just-recorded experiment's `Source` is a GitHub issue (the
`Sourcing strategy` was `user` and the `Source` field links
to `github.com/<owner>/<repo>/issues/<N>`), **offer** to post
the headline result back as an issue comment via
`AskUserQuestion` with exactly two options:

- **comment back** — run
  `gh issue comment <N> --body "<headline + plan-file link>"`
  in this turn.
- **skip** — move on, no outbound action.

Never auto-post; the `gh issue comment` call only fires on
explicit `AskUserQuestion` approval — a free-text "yes" is
not enough, because this is the only outbound side effect
this skill is allowed and consent for it should be
structured rather than inferred.

**Stop here.** Do not auto-launch the next strategy dispatch in
the same turn. Surface the implication to the user as a one-
liner ("the residual bias near boundaries points at a target-
transform experiment") and ask via `AskUserQuestion` with
exactly two options:

- **draft it now** — re-enter § 1 with the implication as the
  proposal seed; route via the sourcing menu (`skore` for the
  full diagnostic walk into the Backlog, `user` if the user
  already has a specific idea drawn from the implication).
- **not yet** — record the implication in `PLAN.md` Backlog
  as a one-liner and stop.

The user controls cadence; this skill records, it doesn't
propose-and-record in one breath.

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

A goal pivot is user-only — the skill never auto-pivots.

## Abandoned experiments

The lifecycle states are `planned → approved → running → done |
abandoned`. Abandonment is a real outcome and needs the same
handling rigor as `done`:

- **User-decided only.** The skill never auto-abandons. If an
  experiment has been planned/approved for many sessions
  without progress, *flag* it to the user via
  `AskUserQuestion` with three options:
  - **abandon** — flip status to `abandoned`; the skill then
    prompts in a follow-up turn for the one-line reason that
    lands in the Status block.
  - **defer** — leave as `approved`; the skill will re-flag it
    in a future session.
  - **run now** — the script already exists; route to § 3's
    post-smoke run prompt.

  Do not change state without an explicit pick — free-text
  ("eh, drop it") is ambiguous between abandon and defer.
- **Status block requires a one-line reason.** "Dependency was
  non-trivial to install; deferred to v2." "Method was
  superseded by 06_softer_transform's success." "Direction
  ruled out by skore finding in 04_monotonic_gbm." The reason
  is the whole point — it's what makes the abandonment a useful
  provenance signal rather than a gap.
- **`Headline result` becomes** `n/a — abandoned: <reason>`.
  The History row stays (provenance is the whole point); only
  the Status field flips.
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
  on, re-enter § 1 with the sourcing menu — typically `skore`
  (mine one or both reports into Backlog rows) or `user` (the
  user already has a concrete idea drawn from the comparison).

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

Use when the user (often after a `skore`-surfaced finding) asks
to redo exactly one prior experiment under a controlled change.

- New stem: `NN_<original_stem>_rerun.py` and the matching
  `plan/NN_<original_stem>_rerun.md`. The numeric prefix is the
  next free integer; `<original_stem>` preserves provenance.
- `Sourcing strategy` line: typically `user re-run` (the user
  asks for the redo, often after a `skore`-surfaced finding
  pointed at the prior experiment's setup).
- **Motivation** must quote the original experiment stem and
  state precisely what changed (the fix being tested).
- **Method** notes that the experiment is a re-run and what is
  held constant from the original.

### Batch re-run (N prior targets)

Use when the user (often after a `skore`-surfaced finding flags
a cross-experiment fairness gap, or after their own audit of
past runs) calls for N≥2 prior experiments to be redone under a
controlled condition — for example, "redo 01, 02, 03 with
paired seeds and a fixed splitter so the comparisons are
sound." This is **one** intervention, not N; it gets **one**
plan file.

- New stem: `NN_paired_comparison.py` and
  `plan/NN_paired_comparison.md` (or another descriptive name
  reflecting the controlled condition: `NN_seeded_redo`,
  `NN_aligned_splits`, …). One numeric prefix; one approval; one
  History row.
- `Sourcing strategy`: `user batch re-run` (or
  `skore batch re-run` when the impetus came from a diagnostic
  finding the user promoted from the Backlog).
- **Motivation** quotes the comparability gap (skore-surfaced
  or user-identified) and cites the affected stems.
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

Use the user's framing first; fall back to the sourcing menu
otherwise.

| Situation | Action |
|---|---|
| **No prior experiment in `PLAN.md`** (bootstrap) | None — § 0 forces an auto-drafted baseline. The strategy skills only apply once at least one experiment is recorded. |
| **The user names a Backlog row** ("go with B2", "let's do B5") | Promote directly: no strategy skill invoked. Frame the proposal from the row's `Item` + `Source`; remove the row from Backlog when the plan file is approved. |
| "mine the report", "what does skore see?", "fill the backlog from the diagnostic" | `iterate-from-skore` — enriches Backlog, summarizes, re-shows the menu. *No plan file drafted on this turn.* |
| "I want to try X", "let's add Y", a scientific article link, a GitHub issue link, a spec file path | `iterate-from-user` — opens its own three-branch AskUserQuestion (article / resource / free-text), confirms synthesis with the user, returns a Proposal. (If the user already typed a URL / issue / inline idea, pass it in pre-resolved.) |
| "give me ideas", "what do you suggest", "you decide", "come up with something", "propose for me" | `my-pick` — handled inline. Synthesize 2-4 candidates from PLAN.md context, present via AskUserQuestion, user picks, plan file drafted. |
| Open-ended ("what's next?") with at least one recorded experiment | **Present the sourcing menu** (see § "The sourcing menu") — paired with the Backlog table — and let the user pick. No silent default. Free text resolves per § "Free-text handling". |

The strategy skills are intentionally shallow: each one knows
how to *source* a proposal (or, for `skore`, a set of Backlog
rows) and hand it back here. This skill is where the proposal
becomes a plan file. The `skore` strategy requires a prior
experiment with an on-disk report — that's why bootstrap (§ 0)
skips dispatch entirely.

**If `iterate-from-skore` returns zero candidate rows** — the
report was clean (every diagnostic surface looks fine) or the
report wasn't accessible (no skore Project store, key missing,
skore not importable; see `iterate-from-skore`'s
"empty-diagnosis outcome" and "inaccessible-report fallback")
— append a one-liner under `PLAN.md` Status citing the date:

- `Skore diagnosis clean on <stem> as of <YYYY-MM-DD>`, or
- `Skore report inaccessible on <stem> as of <YYYY-MM-DD>;
  surfaced to user.`

Do **not** add a History row — nothing was experimented on.
Re-present the sourcing menu so the user can pick `user`
instead.

## What this skill does NOT do

- Run experiments. The experiment script is created by
  `organize-ml-workspace` and executed by the user / their
  runner.
- Open or query the skore Project. That's
  `evaluate-ml-pipeline` and the `python-api` lookups.
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
  `PLAN.md`) and `tests/smoke/` (placeholder
  `test_01_baseline.py`); enforces the three-way stem-pairing
  rule between `plan/NN_*.md`, `experiments/NN_*.py`, and
  `tests/smoke/test_NN_*.py`.
- **`iterate-from-user`** — sources the next experiment from
  the user via three entry points (article URL, resource link,
  free text); confirms its synthesis with the user before
  returning a Proposal block.
- **`iterate-from-skore`** — walks the prior experiment's skore
  report via `report.diagnosis()`, enriches `PLAN.md` Backlog
  with one row per actionable finding, summarizes for the user,
  and hands back to the sourcing menu (where the user typically
  picks a `B<N>` row next).
- **`evaluate-ml-pipeline`** — read the skore report after a run
  before recording the outcome.
- **`build-ml-pipeline`** — implementation of the *method*
  section once the plan is approved. Also where § 3 routes when
  a smoke-test failure points at a graph-topology bug (typically
  a late `mark_as_X`).
- **`test-ml-pipeline`** — router for `tests/`. § 3 dispatches
  here right after plan approval to draft the matching smoke
  test; § 4 refuses to flip an experiment to `done` until that
  smoke test passes.
- **`smoke-test-ml-pipeline`** — owns the smoke test contract
  (fixture from real `data/`, hard row-count assertion, soft
  metric-vs-CV gap). The `test-ml-pipeline` router dispatches
  here for the body of each `tests/smoke/test_NN_*.py`.

## Templates

- `templates/PLAN.md` — the three-section index skeleton.
- `templates/experiment_plan.md` — the per-experiment design
  note skeleton with status block.

Copy, don't rewrite. The templates encode the contract — keep
the section names stable so `PLAN.md` stays diffable across
experiments and sessions.
