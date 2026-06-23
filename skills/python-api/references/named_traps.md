# Named version-specific traps

Renames, signature changes, and footguns the agent has hit in real
traces. Named so the cases stay sticky in future sessions.

These are **leads**, not authority. Always confirm against the
installed version via a Shape 1 probe before writing the call.

## skrub

- **`tabular_learner` → `tabular_pipeline`** (skrub 0.7+). The
  one-call default-everything featuriser was renamed. Memory-based
  code typing `from skrub import tabular_learner` raises
  `ImportError` on skrub ≥ 0.7.
- **`mark_as_y(target_column)` → `mark_as_y()`** (skrub 0.9+). The
  positional column argument was dropped. Column selection now
  happens via `.skb.select("...")` on the source op *before* the
  mark. Memory-based code typing `raw.skb.mark_as_y("Target")`
  raises `TypeError` on skrub ≥ 0.9.
- **`skrub.X(...)` / `skrub.y(...)` graph roots** — deprecated in
  favour of `skrub.var(name, value).skb.mark_as_X()` /
  `mark_as_y()`. The sugar bakes the marker at the source and
  forbids the late-marker pattern (see `build-ml-pipeline` Stop
  conditions).

## skore

- **`skore.Project(workspace=..., name="...")`** — the
  `workspace` keyword is **mode-specific in meaning**: a directory
  path in `local` mode, the Hub org/team identifier in `hub` mode,
  and rejected in `mlflow` mode (which takes `tracking_uri=`
  instead). Assuming a single universal meaning for `workspace=`
  silently writes to the wrong store. Always look up the `Project`
  signature against the installed skore and key off `mode=`.
- **`skore.evaluate(...)` recursion bug with Rich rendering** —
  when stdout is redirected (CLI contexts), the Rich-rendered
  report can hit a recursion in some versions. Workaround:
  `with configuration(show_progress=False):`. This is a config-API
  call the agent will not find from memory; confirm via Shape 1 /
  Shape 3 in the installed version before using it.
- **`Project.get(...)` is by id, not key** — `project.get("01_baseline")`
  raises `KeyError`. Get the id from `project.summarize()` first
  (returns a DataFrame indexed by id with a `key` column), then
  `project.get(<id>)`. **A failed `get(key)` does not mean the
  report is missing.** Never substitute by re-running
  `experiments/NN_*.py` and `put`-ing — that lands a duplicate row.

## How to use this list

When you catch yourself about to write a symbol from "what I
remember": grep this file for the symbol name. A hit doesn't end
the lookup — it tells you which way the trap leans, then you
confirm against the installed version.

A miss does **not** mean the symbol is safe — only that no agent
has hit a trap with it yet. Recognition is not a lookup.
