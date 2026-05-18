# Authoring protocol — when to write a new reference

Two folders carry library knowledge in this workspace. Keep them
straight:

| | Skill `references/` | Workspace `scratch/api/` |
|---|---|---|
| **What** | Workflow patterns (how to compose libraries for a recurring task) | API extracts (signatures, narrative pages, surface dumps) |
| **Lifetime** | Durable; survive library upgrades | Version-tagged; regenerated on bump |
| **Authoring** | Hand-authored prose + worked code; user-gated via `AskUserQuestion` | Agent-generated from `inspect` / WebFetch |
| **Tracked in git?** | Yes | No (gitignored under `scratch/*`) |
| **Read at** | Project bootstrap, during new-experiment planning | Every API question (Shape 0) |

Workflow patterns are *codebase knowledge*; API extracts are
*library knowledge*. Both worth caching, in different places.

## Current references (durable)

- **`pre_mark_alignment.md`** — the 3-layer skrub DataOps pattern
  for cross-row pipelines (lags, joins with history). Why early
  `mark_as_X` matters; how Layer-3 feature steps reference the
  upstream history DataOp; the executable proof in `tests/smoke/`.
  Read before authoring or modifying any history-dependent pipeline.
- **`skrub_interop.md`** — how the `SkrubLearner` produced by the
  pattern above integrates with `skore.evaluate` (env-dict-style
  fit, source-bound vars, Project key conventions). Read before
  writing a new `experiments/NN_*.py`.
- **`stack_orientation.md`** — full sklearn / skrub / skore surface
  map. Load when the inline orientation in `SKILL.md` doesn't name
  what you need.
- **`bootstrap_cache.md`** — required minimum cache files for a
  bootstrap turn + audit procedure.
- **`named_traps.md`** — version-specific renames / deprecations.
- **`authoring_protocol.md`** — this file.

## When to write a new reference

A new reference doc lands here when **all three** hold:

1. The agent has nontrivially figured out a *workflow pattern* (via
   `scratch/` work, WebFetch, multiple `inspect` calls, or
   trial-and-error). One inspect call is not enough; the threshold
   is "this took meaningful figuring-out time".
2. The pattern is **workflow-relevant** for this project — would
   help future iterations or future agents reading the codebase
   cold. Generic library docs don't qualify; this-codebase patterns
   do.
3. The pattern is **not just an API extract** — references are
   prose + worked examples about *combining* libraries, not "here's
   what `skore.evaluate` returns" (that's
   `scratch/api/skore/<version>/evaluate.md`).

## Gate

When all three hold, **fire an `AskUserQuestion`** before writing.
The user gates the new file because references are durable git
content. The doc lives at
`.agents/skills/python-api/references/<topic>.md`.
