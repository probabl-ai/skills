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

## First action — read state + emit read-set tracker

Track which siblings you've opened **this turn**. Open each
sibling SKILL.md **just-in-time** when a step in this skill calls
for it (e.g. open `evaluate-ml-pipeline` before § 3's CV-strategy
step). Do not pre-read all nine at session start — that produces
paralysis and the user is left waiting.

Emit this tracker as visible text once per turn (mark each
`opened` / `pending`):

```
Sibling skills (open just-in-time when a step requires):
  - organize-ml-workspace, data-science-python-stack,
    python-env-manager, python-api, python-code-style,
    build-ml-pipeline, evaluate-ml-pipeline, test-ml-pipeline,
    smoke-test-ml-pipeline, iterate-from-skore / iterate-from-user
```

Then do the context reads below before answering:

1. **Read `journal/JOURNAL.md`.** Missing or placeholder → bootstrap
   mode (see § 0).
2. **Read `overview/summary.md` if it exists.** `JOURNAL.md` is the
   *index*; `summary.md` is the *narrative digest*.
3. **Check `Workspace decisions` block in JOURNAL.md Status** for
   pre-recorded gates (tabular, env_manager, package, cv_splitter)
   — a recorded decision skips its `AskUserQuestion` and cites
   `JOURNAL.md Status (recorded YYYY-MM-DD)` as evidence.
4. **Emit the Pre-flight checklist below** with each box filled.
5. **Use the Mode picker** to find which section to read this turn.

## Mode picker — read this before navigating the body

You only read **one** mode section per turn. Match the user's signal
to a row, then jump.

| Signal / workspace state | Mode | Section |
|---|---|---|
| `journal/JOURNAL.md` missing, empty, or placeholder; OR exists but History has 0 rows | **Bootstrap** | § 0 |
| `journal/` not even scaffolded (no `src/`, no `experiments/`) | **Bootstrap → handoff first** | hand off to `organize-ml-workspace`, then § 0 |
| "what's next?", "let's iterate", "propose next", "resume" — with ≥1 done row | **Iterate (propose)** | §§ 1-3 + Dispatch table |
| "the run finished", "log the result", "we got X = ...", "record outcome" | **Iterate (record)** | § 4 |
| "where are we?", "give me a one-pager", "status?", "what have we tried?" | **Project overview** | `references/maintenance_modes.md` § Overview |
| "compare X and Y", "X vs Y", "trend across runs" | **Compare (read-only)** | `references/maintenance_modes.md` § Compare |
| "let's pivot the goal", "actually we care about <new metric>" | **Goal pivot** | `references/maintenance_modes.md` § Goal pivots |
| "abandon X", "drop X" | **Abandoned** | `references/maintenance_modes.md` § Abandoned |
| User wants to redo a prior experiment under different conditions | **Re-run** | `references/maintenance_modes.md` § Re-runs |

If two modes seem to match ("compare X and Y, then propose something"),
pick the **read** mode first, surface its result, and stop. Re-entering
§ 1 is a separate user-driven turn.

## Stop conditions — read before anything else

- **No design note, no script.** Never create or edit
  `experiments/NN_*.py` until `journal/NN_*.md` exists, is filled
  in, and the user has explicitly approved it. The design note is
  written first and validated first; the script is its consequence.
- **`JOURNAL.md` is read at session start, not improvised.** Don't
  reconstruct history from `experiments/` filenames or `git log` —
  those don't carry the *why*.
- **Strategy is picked, not assumed.** Name the sourcing strategy
  in every proposal: `skore` / `user` / `my-pick` / `B<N>`. Don't
  silently default. **Exception: bootstrap** — the baseline is
  forced by workspace defaults, no strategy dispatch.
- **Approval is explicit.** "approved" / "yes" / "go" / "looks
  good" from the user is the gate. Ambiguous ("hmm interesting") →
  re-ask via `AskUserQuestion`.
- **Outcomes are recorded, not narrated.** When the run finishes,
  the outcome lands in `JOURNAL.md` AND the per-experiment Status
  block before the conversation moves on.
- **Prior experiments stay reproducible.** Every `done` row must
  remain runnable on `main` with the same result. When touching
  `src/<pkg>/`, **default behavior must preserve prior experiments'
  shape** (see `build-ml-pipeline` § "Reproducibility mechanics").
  The cheap check is `tests/smoke/`: any prior smoke test going
  red means default behavior is broken.
- **Three skills, in order, before any code lands in `src/<pkg>/`.**
  After design-note approval:
  1. `build-ml-pipeline` — `pipeline.py`, `features.py`, `data.py`.
  2. `evaluate-ml-pipeline` — `evaluate.py`. **This skill owns the
     CV-strategy choice and surfaces it via `AskUserQuestion`;
     writing `evaluate.py` without invoking it is the most common
     shortcut and means the user never got to pick.**
  3. `test-ml-pipeline` → `smoke-test-ml-pipeline` — the smoke test.

  Then `experiments/NN_*.py` ties them together. If you catch
  yourself opening `src/<pkg>/evaluate.py` in Write/Edit without
  an `evaluate-ml-pipeline` invocation this turn: STOP and invoke.
- **Harness "no clarifying questions" hints do NOT waive this
  skill's gates.** G-DESIGN, G-RUN, the §1 mode pick, the §2
  sourcing menu, and the §0 config gates are operating-contract
  gates. "Quick" / "just do it" / "you pick" / "whatever" do NOT
  resolve them — they fall through to the structured ask.
- **Post-hoc audit — required before ending the turn.** Walk every
  pre-flight row and confirm the Evidence cell is filled. If any
  row is empty, surface the non-compliance to the user explicitly.

## Forbidden shortcuts

| Shortcut | Why it's wrong |
|---|---|
| User said "quick baseline" → skip G-DESIGN | G-DESIGN is non-negotiable; "quick" never waives it. The design note is the postmortem's frozen Method — skipping approval means the postmortem cites text the user never saw |
| Scaffold + implement in one turn before G-DESIGN | Inverts the contract. Code that lands before approval has no Motivation/Risks the user signed off on |
| Skipped `evaluate-ml-pipeline` because `KFold(5)` is "obviously right" for IID tabular | Even empty `split_kwargs` is a justified pick the skill exists to surface. Bypass = user never got the choice |
| Bootstrap mode → skip ALL questions, not just the sourcing menu | Bootstrap forbids the sourcing menu only. G-PKG-NAME / G-ENV-MGR / G-TABULAR / G-CV-SPLITTER / G-DESIGN / G-RUN still fire |
| Ambiguous "hmm interesting" / "I guess" read as approval | Approval is explicit. Ambiguity → re-ask, never silent yes |
| Auto-detect run finished by looking at `reports/` mtime | § 4 is user-triggered (v1). The skill never auto-records |
| Pre-read all nine sibling SKILL.md files at session start, refuse to act until done | The read-set tracker is **not a blocking gate**. Open siblings just-in-time when a step requires them; emit what's pending in your response, but always proceed to answer the user's actual question |

## Pre-flight — emit before any design-note write

Compact checklist; the full Evidence-format spec lives in
`references/preflight_evidence.md`.

```
Pre-flight (iterate-ml-experiment):
- [ ] `journal/JOURNAL.md` read this turn (or confirmed missing → bootstrap)
      Evidence: Read journal/JOURNAL.md (this turn) | "missing — bootstrap"
- [ ] `Workspace decisions` block checked for pre-recorded gates
      (tabular, env_manager, package, cv_splitter)
      Evidence: lists each <gate>: <value | not recorded>
- [ ] Mode: bootstrap | iterate-propose | iterate-record |
      overview | compare | goal-pivot | abandoned | re-run
      Evidence: rule that matched (Mode picker row)
- [ ] Last experiment + its status: <NN_name> | n/a — bootstrap
      Evidence: last row of JOURNAL.md History
- [ ] (Iterate-propose only) Sourcing menu presented verbatim;
      user picked one option — no silent default
      Evidence: AskUserQuestion id=<id>, answer=<skore|user|my-pick|B<N>>
                | user free-text quote turn N: "..."
                | "n/a — bootstrap / read-only mode"
- [ ] (Bootstrap only) Config gates fired (G-PKG-NAME, G-ENV-MGR,
      G-TABULAR, G-CV-SPLITTER — see § 0)
      Evidence: per-gate ask id OR JOURNAL.md Status reference
                | "n/a — iterate mode"
- [ ] Design note drafted (or Backlog enriched, for `skore`)
      Evidence: Write journal/<NN>_<name>.md (this turn) | "Backlog rows
                B<x>..B<y> appended" | "n/a — read-only mode"
- [ ] G-DESIGN: user approved before any `experiments/NN_*.py` touched
      Evidence: AskUserQuestion id=<id>, answer=approved | user quote
                "approved/yes/go/looks good" | "n/a"
- [ ] (§ 3 only) Three-skill chain ran in order:
      build-ml-pipeline → evaluate-ml-pipeline → test-ml-pipeline
      Evidence: each owning skill produced its file this turn
                | "n/a outside § 3"
- [ ] (§ 4 only) Smoke gate green; Status block filled
      (State, Headline, Implication); JOURNAL.md History updated;
      Backlog hygiene done; `overview/summary.md` refreshed
      Evidence: list each artifact written | "n/a outside § 4"
- [ ] python-api consulted for any new external symbol used
      Evidence: Read/Write scratch/api/<lib>/<v>/<topic>.md (this turn)
                | "n/a — only re-using cached symbols"
```

## § 0 Bootstrap (first session only)

A workspace is in bootstrap mode when `journal/JOURNAL.md` is
missing, the placeholder, or has 0 rows in History.

**Procedure (compact — full version in `references/bootstrap.md`):**

1. **Scaffold first if needed.** No `src/` / `experiments/` /
   `journal/` → hand off to `organize-ml-workspace`, return when
   the placeholder `JOURNAL.md` exists.
2. **Rewrite `JOURNAL.md` from `templates/JOURNAL.md`**, replacing
   the placeholder.
3. **Derive the goal default from `data/README.md`** *before*
   asking the user. Propose one sentence: "minimize <metric> on
   <split> for <task>". User confirms or amends. Only ask blank
   if no README exists.
4. **Auto-draft `journal/01_baseline.md` via the consultation
   chain** — the baseline is forced, but its defaults come from
   sibling skills (open just-in-time):
   - Learner default: consult `build-ml-pipeline` (tabular
     regression / classification → `skrub.tabular_pipeline`).
   - Splitter default: consult `evaluate-ml-pipeline` (typically
     `KFold` for IID tabular, the skill picks by data structure).
   - Metric default: consult `python-api` for what
     `skore.evaluate` reports by default.
   - **Mismatch handling**: if any default conflicts with the
     project goal, flag it in the design note's **Risks** section.
     Don't silently override.
5. **The user's role in bootstrap is approve or amend** — not
   invent.
6. **Exit bootstrap** once the baseline is approved and recorded.
   Every session afterwards uses § 1.

### Bootstrap skips the sourcing menu — NOT the config gates

**Skipped in bootstrap** (no history to source from):
- Sourcing menu (`skore` / `user` / `my-pick` / `B<N>`).
- "Resume / record outcome / propose next" pick from § 1.

**Still fires in bootstrap**:

| Gate ID | Picks | Owner | Fires |
|---|---|---|---|
| `G-PKG-NAME` | `src/<pkg>/` import name | `organize-ml-workspace` | before manifest creation |
| `G-ENV-MGR` | Env manager + install scope | `python-env-manager` | before any install command |
| `G-TABULAR` | Tabular library (pandas/polars) + other Tier 2 picks | `data-science-python-stack` | before `data.py` write |
| `G-CV-SPLITTER` | Cross-validator family for `skore.evaluate` | `evaluate-ml-pipeline` | before `evaluate.py` write — mandatory even when `split_kwargs` is empty |
| `G-DESIGN` | Explicit user approval of `journal/01_baseline.md` | this skill | before `experiments/01_baseline.py` write |
| `G-RUN` | "run now" vs "leave for later" | this skill | before executing the experiment script |

Free-text "quick baseline" / "you pick" do NOT resolve any of
these — fall through to structured `AskUserQuestion`.

## § 1 Session start (iterate mode)

- Read `journal/JOURNAL.md`.
- Summarize to the user in 2-3 lines: dataset, goal, last
  experiment + status, what's ripe in the Backlog.
- **Ask via `AskUserQuestion`** — three options, no silent default:
  - **resume** — last experiment still planned/approved/unfinished.
  - **record outcome** — last one ran; enter § 4.
  - **propose next** — last one is `done` or `abandoned`; enter § 2.

  Free-text "let's keep going" / "yeah" is ambiguous — wait for an
  explicit pick.

## § 2 Propose the next experiment

### The sourcing menu — surface VERBATIM

Every time § 2 runs in iterate mode, surface this menu and pair it
with the `JOURNAL.md` Backlog table. **Never silently default.**

```
How would you like me to source the next experiment?

  skore    — call `report.diagnosis()` on the latest run; convert
             each actionable finding into a row in the Backlog
             below, summarize, re-present this menu.
  user     — you tell me what to try, one of three ways:
               (a) paste a scientific article URL — I read it,
               (b) point me at a GitHub issue / spec / reference repo,
               (c) describe the idea in free text.
  my-pick  — I synthesize 2-4 candidate ideas from JOURNAL.md +
             last experiment's Implication; you pick one.
  B<N>     — promote a row from the Backlog table directly.

Backlog (pick by index):
<paste the JOURNAL.md Backlog table here>
```

Use `AskUserQuestion` for the pick (four options + backlog rows
as context). Plain-text enumeration only if `AskUserQuestion` is
unavailable.

### Free-text handling — priority list, first match wins

- **Exact-match** to option label (`skore` / `user` / `my-pick` /
  `B<N>`) → that pick.
- **Backlog reference** (`B2`, "let's do B2") → `B<N>` pick.
- **Scientific article URL pasted directly** → `user` → article-
  link branch, pre-resolved (skip `iterate-from-user`'s inner ask).
- **GitHub issue URL, `org/repo#N`, spec file path** → `user` →
  resource-link branch, pre-resolved.
- **Meta-request** ("give me ideas", "you decide") → `my-pick`.
- **Concrete experiment idea inline** ("let me try X", "use Y
  instead") → `user` → free-text branch, pre-resolved.
- **Ambiguous / off-menu** → fire `AskUserQuestion`, don't guess.

### Branches

- **`skore`** → dispatch to `iterate-from-skore`. The skill returns
  Backlog-candidate rows + a one-paragraph summary. Write rows
  with stable `B<N>` indices, surface the summary, **re-present
  the sourcing menu** with the enriched Backlog. *No design note
  on this turn.*
- **`user`** → dispatch to `iterate-from-user`. The skill returns a
  Proposal. If the free-text handler already resolved the entry
  point (URL / issue / inline idea), pass the resolved branch +
  content so the inner ask is skipped. Draft into
  `journal/NN_short_name.md`.
- **`my-pick`** → handled inline. Read JOURNAL.md Status, the last
  experiment's Implication and Risks, current Backlog. Synthesize
  2-4 candidate ideas; present via `AskUserQuestion`. User picks
  one; that becomes the Proposal seed with
  `Sourcing strategy: my-pick` and a `Source:` citing the context
  field that fed it. Then draft the design note.
- **`B<N>`** → promote the named Backlog row directly. The row's
  `Item` becomes the design-note seed; the row's `Source` becomes
  `Sourcing strategy`. Remove the row from Backlog on approval.

For `user` / `my-pick` / `B<N>`: write the draft to
`journal/NN_short_name.md` using `templates/experiment_design.md`.
`NN` is the next free integer; `short_name` is the user's call
(offer one, don't force).

## § 3 Iterate on the design note + implement

- Surface the draft: file path + 3-5 line summary (Question / Method
  / Risks). User reads in chat or opens the file.
- **Mid-iteration feedback is free-text.** Edit
  `journal/NN_*.md` in place and re-surface. Loop here.
- **Final approval gate is `AskUserQuestion`** with two options:
  - **approved** — flip status, add row to `JOURNAL.md` History,
    hand off to `organize-ml-workspace`.
  - **more changes** — back to amendment loop.

  Clear free-text "approved" / "go" / "looks good" resolves;
  ambiguous ("hmm") → structured ask.
- **Do not create `experiments/NN_*.py`** during design iteration.
- **Track provenance honestly.** Risks-only edits keep the original
  `Sourcing strategy`. Method changes → `<original> + user override`,
  with both quoted in Motivation.

### Three-skill implementation chain — non-skippable

After G-DESIGN passes, open and dispatch in order:

1. `build-ml-pipeline` → `src/<pkg>/{pipeline,features,data}.py`.
2. `evaluate-ml-pipeline` → `src/<pkg>/evaluate.py`. **Owns the
   CV-strategy decision; surfaces via `AskUserQuestion`. Mandatory
   even when `KFold(5)` "feels right" — bypassing this skill is
   the named forbidden shortcut.**
3. `test-ml-pipeline` → `smoke-test-ml-pipeline` → matching smoke
   test at `tests/smoke/test_NN_<short_name>.py`.

Only then this skill assembles `experiments/NN_*.py`, overwriting
the scaffold template. Confirm signatures via `python-api`, not
memory.

### G-RUN — post-smoke run gate

Once `tests/smoke/` passes (the new test AND every prior one — the
reproducibility check), ask via `AskUserQuestion`:

- **run now** — execute
  `pixi run python experiments/NN_<short_name>.py` directly.
- **leave for later** — do **not** print the command, do **not**
  auto-propose. Surface `JOURNAL.md` Status + Backlog verbatim, stop.

No silent default.

## § 4 Record outcome (user-triggered)

**Trigger is user-driven.** The user says "the run finished, log
it" — only then does this step start. Do **not** auto-detect via
`reports/` mtime or polling.

When triggered:

1. **Decide if report is accessible** in this session (skore
   Project at `reports/` exists, key matches).
2. **If accessible** — open via skore (consult `python-api` for
   `Project.get` signature this turn; **`get` is by id, not key** —
   enumerate with `project.summarize()` first). Programmatic
   diagnostic surface is `report.diagnosis()`. Inspection lives in
   `scratch/`, NOT in the experiment script.
3. **If not accessible** — ask the user for the headline metric.
   Don't fabricate report content from memory.
4. **Fill all four Status-block fields** in `journal/NN_*.md`:
   - **State:** `done` (or `abandoned` with a one-line reason)
   - **Approved by user on:** unchanged from approval
   - **Headline result:** metric + uncertainty (e.g.
     `RMSE 0.083 ± 0.004 (5-fold CV)`)
   - **Implication for next iteration:** one or two sentences
5. **Smoke-test gate before `done`** — **all** `tests/smoke/`
   must pass, not just the new one. Prior smoke failures =
   reproducibility regression → route to `build-ml-pipeline` §
   "Reproducibility mechanics". The CV report can still land in
   the skore Project, but the JOURNAL row stays `approved` until
   the full smoke suite is green. Abandonment doesn't require
   passing smoke tests.
6. **Append the headline result** to `JOURNAL.md` History.
7. **Backlog hygiene** — scan existing Backlog for items the new
   run answered or killed. Delete or strikethrough (`~~old~~ —
   resolved in NN_X`). Diagnostic mining of the *new* report is
   `iterate-from-skore`'s job, not § 4's.
8. **Refresh `overview/summary.md`** — agent-authored, hand-written
   from a `scratch/<ts>_refresh_summary.py` extraction probe. NOT
   script-generated. Structure: Project narrative (1-2 paragraphs)
   + curated cross-experiment metrics table from
   `project.summarize()` + per-experiment Headline + Implication.
   See `references/record_outcome.md` for the full procedure.
9. **(Opt-in) GitHub issue close-the-loop** — if the experiment's
   `Source` is a GitHub issue, ask via `AskUserQuestion` whether
   to `gh issue comment <N>` back with the headline. Never
   auto-post — only on structured approval.

**Stop here. Do NOT auto-propose the next experiment** in the same
turn. Surface the implication and ask via `AskUserQuestion`:

- **draft it now** — re-enter § 1 with the implication as seed.
- **not yet** — record the implication in Backlog, stop.

The user controls cadence; this skill records, it doesn't
propose-and-record in one breath.

## Dispatch table — which iterate-from-* skill

Use the user's framing first; fall back to the sourcing menu.

| Situation | Action |
|---|---|
| **No prior experiment** (bootstrap) | § 0 forces auto-drafted baseline. No strategy skill |
| User names a Backlog row ("B2", "let's do B5") | Promote directly; no strategy skill |
| "mine the report", "what does skore see?", "fill the backlog" | `iterate-from-skore` — enriches Backlog, re-shows the menu. *No design note this turn.* |
| "I want to try X", "let's add Y", an article URL, a GitHub issue link, a spec path | `iterate-from-user` — opens its three-branch ask (article / resource / free-text). If free-text already resolved, pass pre-resolved branch |
| "give me ideas", "what do you suggest", "you decide" | `my-pick` — handled inline. Synthesize 2-4 candidates, AskUserQuestion, draft on pick |
| Open-ended "what's next?" with ≥1 recorded experiment | **Present the sourcing menu** verbatim + Backlog table. No silent default. Free text resolves per § "Free-text handling" |

The strategy skills are intentionally shallow: they *source*, this
skill *drafts*. The `skore` strategy requires a prior experiment
with an on-disk report — bootstrap can't use it.

**If `iterate-from-skore` returns zero candidates** — report was
clean or inaccessible — append a one-liner to `JOURNAL.md` Status
(`Skore diagnosis clean on <stem> as of <date>` or `Skore report
inaccessible on <stem> as of <date>`). No History row. Re-present
the sourcing menu.

## Maintenance modes — pointers

Each is read-only or rare. Full procedures in
`references/maintenance_modes.md`:

- **Project overview** ("status?", "where are we?", "what's been
  tried?") — read-only summary from `JOURNAL.md` + Backlog. Don't
  generate a separate document.
- **Compare past experiments** ("compare X and Y", "how does Z
  stack up?") — read-only. v1 is pairwise side-by-side; no
  programmatic multi-stem `ComparisonReport`. Don't draft a design
  note. Don't add JOURNAL rows.
- **Goal pivots** ("we actually care about MAE now") — update
  Status with date + reason, insert a horizontal divider in
  History, flag incomparability in the next experiment's Risks.
  Don't mass-edit prior notes.
- **Abandoned experiments** — `AskUserQuestion`(`abandon` /
  `defer` / `run now`). Status becomes `abandoned` with one-line
  reason; Headline becomes `n/a — abandoned: <reason>`. History
  row stays.
- **Re-runs** — single (`NN_<original_stem>_rerun`) or batch
  (`NN_paired_comparison`). New design note; original notes
  unchanged. In-place edits reserved for the Status block.

## Files this skill owns

```
journal/
├── JOURNAL.md                # status + history + backlog (index)
├── 01_baseline.md            # design note for experiments/01_baseline.py
├── 02_<short_name>.md
└── ...
```

Pairing rule (hard): `journal/NN_<short_name>.md` ↔
`experiments/NN_<short_name>.py`, identical stems, 1:1.

### `JOURNAL.md` shape

1. **Status** — 2-3 lines: dataset, goal, last experiment + status.
2. **History** (chronological) — one row per experiment: stem,
   one-line intent, status (planned / running / done / abandoned),
   headline result, link.
3. **Backlog** (forward-looking) — indexed table; columns `#`,
   `Item`, `Source`. `Source` is `skore:<stem>` / `my-pick:<stem>`
   / `user`. Surface this table every time the sourcing menu fires.

Use `templates/JOURNAL.md` as the skeleton. Don't invent sections.

### Per-experiment design note shape

Use `templates/experiment_design.md`. Sections:

- **Question / hypothesis** — one sentence. Why X, what would it tell us.
- **Motivation** — pulled from the sourcing strategy. Cite
  concretely (issue link, paper, prior stem, diagnosis section).
- **Method** — what changes vs. previous experiment, in prose.
  Mechanics live in `build-ml-pipeline` / `evaluate-ml-pipeline`.
- **Risks** — what would make the metric move for the wrong reason.
- **Status block** — `planned` → `approved` → `done | abandoned`.

**No "Success criteria" section.** The user judges whether the
result is good enough, post-run, from Headline + Implication.

## What this skill does NOT do

- Run experiments (user / runner does that).
- Open or query the skore Project (`evaluate-ml-pipeline` +
  `python-api`).
- Edit `pipeline.py` / `features.py` / `data.py`
  (`build-ml-pipeline`).
- Decide whether a workspace exists or where things go
  (`organize-ml-workspace`).
- Write commits / PRs.
- Define what counts as a successful experiment (no acceptance
  criteria pre-run).
- Pick a sourcing strategy on the user's behalf.

## Companion skills

- `organize-ml-workspace` — scaffolds the layout + `tests/smoke/`
  placeholder; owns the stem-pairing rule.
- `iterate-from-user` — sources from the user (article URL /
  resource link / free text); confirms synthesis; returns a
  Proposal.
- `iterate-from-skore` — walks `report.diagnosis()` on the prior
  experiment; enriches Backlog; re-shows the sourcing menu.
- `evaluate-ml-pipeline` — read the skore report after a run
  before recording; owns the CV-strategy decision.
- `build-ml-pipeline` — implements the *method* once approved.
  Also where smoke-test failures route (X-marker bugs,
  reproducibility regressions).
- `test-ml-pipeline` → `smoke-test-ml-pipeline` — drafts the
  matching smoke test after design-note approval; § 4 won't flip
  to `done` until the smoke test passes.

## References (load on demand)

- `references/bootstrap.md` — full bootstrap procedure, config-gate
  details, baseline-template substitution.
- `references/record_outcome.md` — full § 4 procedure with backlog
  hygiene examples, `summary.md` refresh extraction probe, GitHub
  comment template.
- `references/maintenance_modes.md` — overview / compare /
  goal-pivot / abandoned / re-runs with full procedures.
- `references/preflight_evidence.md` — Evidence-format spec
  (read-set rows, gate rows, workflow rows).

## Templates

- `templates/JOURNAL.md` — the three-section index skeleton.
- `templates/experiment_design.md` — per-experiment design note
  with Status block.

Copy, don't rewrite. Section names are the contract.
