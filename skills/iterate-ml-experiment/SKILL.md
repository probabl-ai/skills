---
name: iterate-ml-experiment
description: >
  Owns the iteration loop on top of an ML workspace: the
  `journal/JOURNAL.md` index and the per-experiment
  `journal/NN_short_name.md` design notes that must be drafted and
  approved by the user **before** `experiments/NN_short_name.py` is
  created. Drives the propose → iterate → approve → implement →
  record loop; dispatches to `iterate-from-skore` /
  `iterate-from-user` for sourcing.

  TRIGGER — any of:
  - A session opens in an ML workspace (whether or not `journal/`
    exists yet — missing/placeholder → bootstrap mode).
  - User says "what's next", "resume", "where were we", "let's
    iterate", "propose next", "first baseline".
  - About to create a new `experiments/NN_*.py` (the matching
    `journal/NN_*.md` must exist and be approved first).
  - User wants to record an outcome from a finished run.
  - User asks to compare past experiments or review what's been
    tried ("compare X and Y", "where are we?").

  SKIP when: no `journal/` yet AND no workspace scaffold (route to
  `organize-ml-workspace`); the work is mechanical inside
  `pipeline.py` / `evaluate.py` / `data.py` with no journal-level
  implication (owned by `build-ml-pipeline` /
  `evaluate-ml-pipeline`); the user asks for a symbol lookup
  (`python-api`); the user is diagnosing a single skore report
  without a "what next" framing (`evaluate-ml-pipeline`).

  HOW TO USE: read `journal/JOURNAL.md` first, classify the turn via
  the **Mode picker** (table near the top), then read only the
  matching section. Sibling skills open *just-in-time* when a step
  requires them — do not pre-read all nine at session start.
  Design notes are the only artifact this skill writes; read,
  compare, and overview modes don't write.
---

# Iterate ML Experiment

The loop on top of `experiments/`: what to try next, why, what
counts as a result, how the trail is recorded. Pipeline / evaluation
mechanics live in sibling skills.

## Next-step pointers — flow at a glance

```
session open
   │
   ├── JOURNAL.md missing / placeholder ──► § 0 Bootstrap
   │                                          │
   │                                          └─► design note → G-DESIGN → § 3 implement
   │
   ├── "what's next?" with ≥1 done row ───► § 1 → § 2 (sourcing) → § 3 implement
   │
   ├── "run finished" ─────────────────────► § 4 record outcome
   │                                          │
   │                                          └─► dispatch audit-ml-pipeline
   │
   └── "status?" / "compare X Y" ──────────► references/maintenance_modes.md
```

Always re-emit the Pre-flight checklist with evidence before
declaring the turn done.

## First action — read state + emit read-set tracker

Open each sibling SKILL.md **just-in-time** when a step calls for
it (e.g. open `evaluate-ml-pipeline` before § 3's CV-strategy
step). Do not pre-read all at session start.

```
Sibling skills (just-in-time):
  - organize-ml-workspace, data-science-python-stack,
    python-env-manager, python-api, python-code-style,
    build-ml-pipeline, evaluate-ml-pipeline, test-ml-pipeline,
    smoke-test-ml-pipeline, iterate-from-skore / iterate-from-user
```

Then before answering:

1. **Read `journal/JOURNAL.md`.** Missing/placeholder → bootstrap (§ 0).
   This is the canonical project digest (Status + History + Backlog).
2. **Check `Workspace decisions` block** for pre-recorded gates
   (tabular, env_manager, package, skore_mode, cv_splitter) — a
   recorded decision skips its `AskUserQuestion`.
3. **Emit the Pre-flight checklist** with each box filled.
4. **Use the Mode picker** to find which section to read.

## Mode picker — read this before navigating the body

You read **one** mode section per turn. Match the user's signal,
then jump.

| Signal / workspace state | Mode | Section |
|---|---|---|
| `JOURNAL.md` missing / placeholder / 0 History rows | **Bootstrap** | § 0 |
| `journal/` not scaffolded (no `src/`, no `experiments/`) | **Bootstrap → handoff first** | → `organize-ml-workspace`, then § 0 |
| "what's next?" / "let's iterate" / "propose next" — with ≥1 done row | **Iterate (propose)** | §§ 1–3 + Dispatch table |
| "the run finished" / "log the result" / "we got X = …" | **Iterate (record)** | § 4 |
| "where are we?" / "status?" / "what have we tried?" | **Project overview** | `references/maintenance_modes.md` § Overview |
| "compare X and Y" / "X vs Y" | **Compare (read-only)** | `references/maintenance_modes.md` § Compare |
| "let's pivot the goal" / "actually we care about <metric>" | **Goal pivot** | `references/maintenance_modes.md` § Goal pivots |
| "abandon X" / "drop X" | **Abandoned** | `references/maintenance_modes.md` § Abandoned |
| Re-do a prior experiment under different conditions | **Re-run** | `references/maintenance_modes.md` § Re-runs |

If two modes seem to match ("compare X and Y, then propose"), pick
the **read** mode first, stop. Re-entering § 1 is a separate turn.

## Stop conditions — read before anything else

- **No design note, no script.** Never create or edit
  `experiments/NN_*.py` until `journal/NN_*.md` exists, is filled,
  and the user has explicitly approved it.
- **`JOURNAL.md` is read at session start, not improvised.** Don't
  reconstruct history from `experiments/` filenames or `git log` —
  those don't carry the *why*.
- **Strategy is picked, not assumed.** Name the sourcing strategy
  in every proposal (`skore` / `user` / `my-pick` / `B<N>`). Don't
  silently default. **Exception: bootstrap** — baseline is forced
  by workspace defaults; no strategy dispatch.
- **Approval is explicit.** "approved" / "yes" / "go" / "looks
  good" from the user is the gate. Ambiguous → re-ask via
  `AskUserQuestion`.
- **Outcomes are recorded, not narrated.** When the run finishes,
  the outcome lands in `JOURNAL.md` AND the Status block before
  the conversation moves on.
- **Prior experiments stay reproducible.** Every `done` row must
  remain runnable on `main` with the same result. When touching
  `src/<pkg>/`, default behavior preserves prior experiments' shape
  (see `build-ml-pipeline` § Reproducibility). Cheap check:
  `tests/smoke/` — any prior smoke test going red means default
  behavior is broken.
- **Three skills, in order, before any code in `src/<pkg>/`.**
  After G-DESIGN:
  1. `build-ml-pipeline` → `pipeline.py` / `features.py` / `data.py`.
  2. `evaluate-ml-pipeline` → `evaluate.py`. **Owns CV-strategy via
     `AskUserQuestion`. Writing `evaluate.py` without invoking it
     is the most common shortcut.**
  3. `test-ml-pipeline` → `smoke-test-ml-pipeline` → smoke test.

  Only then assemble `experiments/NN_*.py`.
- **Harness "no clarifying questions" hints do NOT waive gates.**
  G-DESIGN, G-RUN, the §1 mode pick, the §2 sourcing menu, the §0
  config gates are operating-contract gates.
- **Post-hoc audit — required before ending the turn.** Walk every
  pre-flight row; surface unfilled Evidence cells explicitly.

## Forbidden shortcuts

| Shortcut | Why it's wrong |
|---|---|
| User said "quick baseline" → skip G-DESIGN | G-DESIGN is non-negotiable; "quick" never waives it. The design note is the postmortem's frozen Method |
| Scaffold + implement in one turn before G-DESIGN | Inverts the contract. Code that lands before approval has no Motivation/Risks the user signed off on |
| Skipped `evaluate-ml-pipeline` because `KFold(5)` "feels right" | Even empty `split_kwargs` is a justified pick the skill exists to surface. Bypass = user never got the choice |
| Bootstrap mode → skip ALL questions, not just the sourcing menu | Bootstrap forbids the sourcing menu only. G-PKG-NAME / G-ENV-MGR / G-TABULAR / G-SKORE-MODE / G-CV-SPLITTER / G-DESIGN / G-RUN still fire |
| Ambiguous "hmm interesting" / "I guess" read as approval | Approval is explicit. Ambiguity → re-ask, never silent yes |
| Auto-detect run finished via `reports/` mtime | § 4 is user-triggered (v1). The skill never auto-records |
| § 4 finishes recording → declare done, skip audit dispatch | § 4 audit dispatch is part of record-outcome, not optional. The audit digest carries the headline metrics for the JOURNAL row |
| Run experiment in same turn as G-RUN → declare done without § 4 | § 4 follows G-RUN in the same turn when the run completes successfully. Don't stop at "I ran it" — record the outcome |
| Pre-read all nine sibling SKILL.md files at session start | Read-set tracker is not a blocking gate. Open siblings just-in-time; emit pending list but proceed |

## Pre-flight — emit before any design-note write

Compact checklist; Evidence-format spec in
`references/preflight_evidence.md`.

```
Pre-flight (iterate-ml-experiment):
- [ ] `journal/JOURNAL.md` read this turn (or confirmed missing → bootstrap)
      Evidence: Read journal/JOURNAL.md (this turn) | "missing — bootstrap"
- [ ] `Workspace decisions` block checked for pre-recorded gates
      Evidence: lists each <gate>: <value | not recorded>
- [ ] Mode: bootstrap | iterate-propose | iterate-record |
      overview | compare | goal-pivot | abandoned | re-run
      Evidence: rule that matched (Mode picker row)
- [ ] Last experiment + status: <NN_name> | n/a — bootstrap
      Evidence: last row of JOURNAL.md History
- [ ] (Iterate-propose only) Sourcing menu presented; user picked
      Evidence: AskUserQuestion id=<id>, answer=<skore|user|my-pick|B<N>>
                | user free-text quote turn N
                | "n/a — bootstrap / read-only mode"
- [ ] (Bootstrap only) Config gates fired (G-PKG-NAME, G-ENV-MGR,
      G-TABULAR, G-SKORE-MODE, G-CV-SPLITTER)
      Evidence: per-gate ask id OR JOURNAL.md Status reference
                | "n/a — iterate mode"
- [ ] Design note drafted (or Backlog enriched, for `skore`)
      Evidence: Write journal/<NN>_<name>.md (this turn) | "Backlog
                rows B<x>..B<y> appended" | "n/a — read-only mode"
- [ ] G-DESIGN: user approved before any `experiments/NN_*.py` touched
      Evidence: AskUserQuestion id=<id>, answer=approved | user quote |
                "n/a"
- [ ] (§ 3 only) Three-skill chain ran in order:
      build → evaluate → test
      Evidence: each owning skill produced its file this turn
                | "n/a outside § 3"
- [ ] (§ 3 only) G-RUN resolved: run now | leave for later
      Evidence: AskUserQuestion id=<id> | "n/a outside § 3"
- [ ] (§ 4 only) All artifacts written: Status block + JOURNAL row +
      Backlog hygiene + audit dispatch
      Evidence: list each artifact written | "n/a outside § 4"
- [ ] python-api consulted for any new external symbol
      Evidence: Read/Write scratch/api/<lib>/<v>/<topic>.md (this turn)
                | "n/a — only re-using cached symbols"
- [ ] Pre-flight re-emitted with evidence before final message.
      Evidence: this checklist appears in the end-of-turn summary.
```

## § 0 Bootstrap (first session only)

Workspace is in bootstrap mode when `journal/JOURNAL.md` is missing,
placeholder, or has 0 History rows.

**Procedure (compact — full version in `references/bootstrap.md`):**

1. **Scaffold first if needed.** No `src/` / `experiments/` /
   `journal/` → hand off to `organize-ml-workspace`, return when
   the placeholder `JOURNAL.md` exists.
2. **Rewrite `JOURNAL.md` from `templates/JOURNAL.md`**.
3. **Derive the goal default from `data/README.md`** *before*
   asking. Propose one sentence; user confirms or amends.
4. **Auto-draft `journal/01_baseline.md`** via the consultation
   chain: learner default (`build-ml-pipeline`), splitter default
   (`evaluate-ml-pipeline`), metric default (`python-api` on
   skore.evaluate). Conflicts → flag in **Risks**, don't override.
5. **User's role in bootstrap is approve or amend** — not invent.
6. **Exit bootstrap** once the baseline is approved and recorded.
   Audit file lands at first § 4 record-outcome.

### Bootstrap skips the sourcing menu — NOT the config gates

**Skipped**: sourcing menu, § 1 resume/record/propose pick.

**Still fires**:

| Gate ID | Picks | Owner | Fires |
|---|---|---|---|
| `G-PKG-NAME` | `src/<pkg>/` import name | `organize-ml-workspace` | before manifest creation |
| `G-ENV-MGR` | Env manager | `python-env-manager` | before any install command |
| `G-TABULAR` | Tabular library (pandas / polars) | `data-science-python-stack` | before `data.py` write |
| `G-SKORE-MODE` | Skore Project mode (local / hub) + hub workspace name | `organize-ml-workspace` | before `pyproject.toml` write |
| `G-CV-SPLITTER` | CV family for `skore.evaluate` | `evaluate-ml-pipeline` | before `evaluate.py` write — mandatory even with empty `split_kwargs` |
| `G-DESIGN` | User approval of `journal/01_baseline.md` | this skill | before `experiments/01_baseline.py` write |
| `G-RUN` | "run now" vs "leave for later" | this skill | before executing the experiment script |

Free-text "quick baseline" / "you pick" do NOT resolve any of
these — fall through to structured `AskUserQuestion`.

→ next: G-DESIGN, then § 3 implementation chain.

## § 1 Session start (iterate mode)

- Read `JOURNAL.md`.
- Summarize to the user in 2–3 lines: dataset, goal, last
  experiment + status, what's ripe in Backlog.
- **Ask via `AskUserQuestion`** — three options, no silent default:
  - **resume** — last experiment still planned/approved/unfinished.
  - **record outcome** — last one ran; enter § 4.
  - **propose next** — last one is `done` or `abandoned`; → § 2.

  Free-text "let's keep going" / "yeah" is ambiguous — wait.

## § 2 Propose the next experiment

### The sourcing menu — surface VERBATIM

Every time § 2 runs in iterate mode, surface this menu with the
JOURNAL.md Backlog table. **Never silently default.**

```
How would you like me to source the next experiment?

  skore    — read the audit digest at scratch/audit/<stem>/audit.md
             from the latest run; follow each surfaced check's
             documentation_url to draft a Backlog row, summarize,
             re-present this menu.
  user     — you tell me what to try: article URL, GitHub issue,
             spec / reference repo, or free text.
  my-pick  — I synthesize 2–4 candidate ideas; you pick one.
  B<N>     — promote a Backlog row directly.

Backlog (pick by index):
<paste JOURNAL.md Backlog table here>
```

Use `AskUserQuestion` for the pick. Plain-text enumeration only if
unavailable.

### Free-text handling — first match wins

| User said… | Resolves to |
|---|---|
| Exact label (`skore` / `user` / `my-pick` / `B<N>`) | that pick |
| `B2` / "let's do B2" | `B<N>` pick |
| Scientific article URL pasted | `user` → article-link branch |
| GitHub issue URL / `org/repo#N` / spec path | `user` → resource-link branch |
| "give me ideas" / "you decide" | `my-pick` |
| "let me try X" / "use Y instead" | `user` → free-text branch |
| Ambiguous / off-menu | fire `AskUserQuestion`, don't guess |

### Branches

- **`skore`** → dispatch to `iterate-from-skore`. Returns
  Backlog-candidate rows + summary. Write rows with stable `B<N>`,
  surface summary, **re-present sourcing menu**. *No design note
  this turn.*
- **`user`** → dispatch to `iterate-from-user`. Returns a Proposal.
  Draft into `journal/NN_short_name.md`.
- **`my-pick`** → handled inline. Read JOURNAL.md Status, last
  Implication / Risks, current Backlog. Synthesize 2–4 candidates,
  present via `AskUserQuestion`. Draft the design note on pick.
- **`B<N>`** → promote the row. The row's `Item` becomes the seed;
  the row's `Source` becomes `Sourcing strategy`. Remove from
  Backlog on approval.

For `user` / `my-pick` / `B<N>`: write draft to
`journal/NN_short_name.md` using `templates/experiment_design.md`.
`NN` is the next free integer; `short_name` is the user's call.

→ next: § 3.

## § 3 Iterate on the design note + implement

- Surface the draft: file path + 3–5 line summary
  (Question / Method / Risks).
- **Mid-iteration feedback is free-text.** Edit `journal/NN_*.md`
  in place; loop here.
- **Final approval gate is `AskUserQuestion`** with two options:
  - **approved** — flip status, add JOURNAL History row, hand off
    to the three-skill chain.
  - **more changes** — back to amendment loop.

  Clear free-text "approved" / "go" / "looks good" resolves;
  ambiguous → structured ask.
- **Do not create `experiments/NN_*.py`** during design iteration.
- **Track provenance honestly.** Risks-only edits keep the original
  `Sourcing strategy`. Method changes → `<original> + user override`.

### Three-skill implementation chain — non-skippable

After G-DESIGN passes, dispatch in order:

1. `build-ml-pipeline` → `src/<pkg>/{pipeline,features,data}.py`.
2. `evaluate-ml-pipeline` → `src/<pkg>/evaluate.py`. **Owns the
   CV-strategy via `AskUserQuestion`. Bypassing is the named
   forbidden shortcut.**
3. `test-ml-pipeline` → `smoke-test-ml-pipeline` → matching smoke
   test at `tests/smoke/test_NN_<short_name>.py`.

Only then assemble `experiments/NN_*.py`. Confirm signatures via
`python-api`, not memory.

### G-RUN — post-smoke run gate

Once `tests/smoke/` passes (the new test AND every prior one):
ask via `AskUserQuestion`:

- **run now** — execute
  `pixi run python experiments/NN_<short_name>.py`.
- **leave for later** — do NOT print the command, do NOT
  auto-propose. Surface JOURNAL Status + Backlog verbatim, stop.

No silent default.

→ next: if the run completed in this turn, continue immediately to
§ 4. Don't stop at "I ran it" — record the outcome.

## § 4 Record outcome

**Trigger**: user says "the run finished" / "log it", OR the
agent ran the experiment in the same turn (G-RUN = run now) and it
completed successfully. **Do NOT auto-detect via `reports/` mtime
or polling for runs the user kicked off themselves.**

### Procedure

1. **Audit-first**: dispatch to `audit-ml-pipeline` to place +
   execute `audit/NN_<short_name>.py`. The audit reads the report
   read-only via the bundled runner and streams a markdown digest
   that carries the headline metrics. **The audit replaces scratch
   probes** — don't write `scratch/<ts>_inspect_*.py` to extract
   metrics from the report when the audit is the canonical path.
   - Agent feature must be installed; if not, audit-ml-pipeline
     routes to `python-env-manager` § Agent feature
     (`G-AGENT-FEATURE`).
2. **Read the audit digest**. The metrics + checks summary are
   the source for the next 3 steps.
3. **Fill all four Status-block fields** in `journal/NN_*.md`:
   - **State**: `done` (or `abandoned` with one-line reason).
   - **Approved by user on**: unchanged from approval.
   - **Headline result**: metric + uncertainty (e.g.
     `RMSE 0.083 ± 0.004 (5-fold CV)`).
   - **Implication for next iteration**: 1–2 sentences.
4. **Smoke-test gate before `done`** — **all** `tests/smoke/`
   must pass. Prior failures = reproducibility regression → route
   to `build-ml-pipeline` § Reproducibility. The CV report can
   still land in skore Project, but the JOURNAL row stays
   `approved` until full smoke suite is green. Abandonment doesn't
   require passing smoke.
5. **Append the headline** to `JOURNAL.md` History.
6. **Backlog hygiene**: scan for items the new run answered or
   killed. Delete or strikethrough (`~~old~~ — resolved in NN_X`).
   Diagnostic mining of the *new* report is `iterate-from-skore`'s
   job, not § 4's.
7. **(Opt-in) GitHub issue close-the-loop** — if the experiment's
   `Source` is a GitHub issue, ask via `AskUserQuestion` whether to
   `gh issue comment <N>` with the headline. Never auto-post.

**Stop here. Do NOT auto-propose the next experiment in the same
turn.** Surface the implication, ask via `AskUserQuestion`:

- **draft it now** — re-enter § 1 with the implication as seed.
- **not yet** — record the implication in Backlog, stop.

The user controls cadence; this skill records, it doesn't
propose-and-record in one breath.

## Dispatch table — which iterate-from-* skill

| Situation | Action |
|---|---|
| **No prior experiment** (bootstrap) | § 0 forces auto-drafted baseline. No strategy skill |
| User names a Backlog row (`B2`, "let's do B5") | Promote directly; no strategy skill |
| "mine the report" / "what does skore see?" | `iterate-from-skore` — enriches Backlog, re-shows menu. *No design note this turn.* |
| "I want to try X" / article URL / GitHub issue | `iterate-from-user` — three-branch ask. If free-text already resolved, pass pre-resolved branch |
| "give me ideas" / "you decide" | `my-pick` — handled inline. Synthesize 2–4 candidates, AskUserQuestion |
| Open-ended "what's next?" with ≥1 recorded experiment | Present sourcing menu verbatim + Backlog. No silent default |

The strategy skills are intentionally shallow: they *source*, this
skill *drafts*. The `skore` strategy requires a prior experiment
with an on-disk report — bootstrap can't use it.

**If `iterate-from-skore` returns zero candidates**: append a
one-liner to JOURNAL Status (`Audit checks clean on <stem> as of
<date>` or `Audit digest inaccessible on <stem> as of <date>`).
No History row. Re-present sourcing menu.

## Maintenance modes — pointers

Each is read-only or rare. Full procedures in
`references/maintenance_modes.md`:

- **Project overview** — read-only summary from JOURNAL + Backlog.
  Don't generate a separate document.
- **Compare past experiments** — read-only. v1 is pairwise
  side-by-side. Don't draft a design note. Don't add JOURNAL rows.
- **Goal pivots** — update Status with date + reason, insert a
  horizontal divider in History, flag incomparability in the next
  experiment's Risks.
- **Abandoned experiments** — `AskUserQuestion`(`abandon` / `defer`
  / `run now`). Status becomes `abandoned` with one-line reason.
- **Re-runs** — single (`NN_<stem>_rerun`) or batch
  (`NN_paired_comparison`). New design note; original notes
  unchanged.

## Files this skill owns

```
journal/
├── JOURNAL.md                # status + history + backlog (index)
├── 01_baseline.md            # design note for experiments/01_baseline.py
├── 02_<short_name>.md
└── …
```

Pairing rule (hard, four-way): `journal/NN_<short_name>.md` ↔
`experiments/NN_<short_name>.py` ↔
`tests/smoke/test_NN_<short_name>.py` ↔
`audit/NN_<short_name>.py`, identical stems, 1:1.

### `JOURNAL.md` shape

1. **Status** — 2-3 lines: dataset, goal, last experiment + status.
2. **History** (chronological) — one row per experiment: stem,
   intent, status, headline, design-note link.
3. **Backlog** (forward-looking) — indexed table; columns `#`,
   `Item`, `Source` (`skore:<stem>` / `my-pick:<stem>` / `user`).

Template: `templates/JOURNAL.md`. Don't invent sections.

### Per-experiment design-note shape

Template: `templates/experiment_design.md`. Sections:

- **Question / hypothesis** — one sentence.
- **Motivation** — pulled from sourcing strategy; cite
  concretely.
- **Method** — what changes vs. previous, in prose. Mechanics live
  in `build-ml-pipeline` / `evaluate-ml-pipeline`.
- **Risks** — what would make the metric move for the wrong reason.
- **Status block** — `planned` → `approved` → `done | abandoned`.

**No "Success criteria" section.** The user judges post-run.

## What this skill does NOT do

- Run experiments (user / runner does that).
- Open or query the skore Project (`evaluate-ml-pipeline` +
  `python-api`).
- Edit `pipeline.py` / `features.py` / `data.py`
  (`build-ml-pipeline`).
- Decide whether a workspace exists or where things go
  (`organize-ml-workspace`).
- Write commits / PRs.
- Define what counts as a successful experiment.
- Pick a sourcing strategy on the user's behalf.

## Companion skills

| Skill | Relationship |
|---|---|
| `organize-ml-workspace` | Scaffold + stem-pairing rule |
| `iterate-from-user` | User-sourced proposals (article / resource / free text) |
| `iterate-from-skore` | Report-sourced Backlog enrichment |
| `build-ml-pipeline` | `pipeline.py` / `features.py` / `data.py` body; reproducibility mechanics |
| `evaluate-ml-pipeline` | `evaluate.py` body; CV-strategy decision; report inspection |
| `test-ml-pipeline` → `smoke-test-ml-pipeline` | Smoke-test body; § 4 won't flip `done` until smoke is green |
| `audit-ml-pipeline` | § 4 dispatch; audit digest carries the headline metrics for the JOURNAL row |
| `python-api` | Signature lookups |
| `python-env-manager` | G-AGENT-FEATURE for audit prerequisites |

## References (load on demand)

- `references/bootstrap.md` — full bootstrap procedure, config-gate
  details, baseline-template substitution.
- `references/record_outcome.md` — full § 4 procedure with Backlog
  hygiene examples, GitHub comment template.
- `references/maintenance_modes.md` — overview / compare /
  goal-pivot / abandoned / re-runs with full procedures.
- `references/preflight_evidence.md` — Evidence-format spec.

## Templates

- `templates/JOURNAL.md` — three-section index skeleton.
- `templates/experiment_design.md` — design note with Status block.

Copy, don't rewrite.
