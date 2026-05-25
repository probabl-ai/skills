---
name: python-api
description: >
  Look up the public API of a Python package against the *installed
  version* and cache what's worth keeping. Four shapes by question
  type: (0) cache hit under `scratch/api/<lib>/<version>/`;
  (1) `inspect.signature` + `pydoc.render_doc` for a symbol;
  (2) `dir` / `pkgutil.iter_modules` for a module surface;
  (3) WebSearch + WebFetch of versioned docs for narrative
  ("how", "which", "what does X return when Y"). Never write a
  symbol from training-data memory — recognition is not a lookup.

  TRIGGER — any of:
  - About to name a symbol (function / class / method / arg) in code.
  - User asks "what's the signature of X?", "what's in module Y?",
    "how do I call X?", "which of A/B should I use?".
  - User asks "what does X return when <condition>?" (Shape 3 — see
    decision table).
  - Another workflow skill (`build-ml-pipeline`,
    `evaluate-ml-pipeline`, `iterate-from-skore`,
    `smoke-test-ml-pipeline`) says "consult the API skill".
  - About to reach for a library's "obvious" pattern from memory.

  SKIP when: the signature is obvious from a call site you just
  read in this turn; the work is filesystem / shell only (no
  Python symbols); a `scratch/api/<lib>/<version>/<topic>.md`
  cache file already answers the question (still a Shape 0
  consultation — you just don't fetch).

  HOW TO USE: resolve the package version first via a scratch
  file (`scratch/<ts>_version_<pkg>.py` with `import <pkg>;
  print(<pkg>.__version__)` — run with `pixi run python
  scratch/<ts>_version_<pkg>.py`). Then list
  `scratch/api/<lib>/<version>/`. Then pick the shape from the
  "What kind of question?" table. Narrative findings get cached
  back. **All Python execution goes through `scratch/<ts>_*.py`
  files — inline `python -c` is forbidden regardless of length.**
  Stack-specific orientation lives in
  `references/stack_orientation.md` — load on demand.
---

# python-api

Discover the public API of any installed Python package, cache what
matters, never trust training-data memory.

Three durable rules:

1. **Lookup against the installed version, never memory.** Recognition
   is not a lookup. The version may have renamed / re-signatured /
   deprecated the symbol you remember.
2. **Cache to `scratch/api/<lib>/<version>/<topic>.md`** so the next
   agent doesn't repeat the probe.
3. **Bundled `references/` ≠ workspace cache.** Bundled refs are
   durable workflow patterns; cache files are per-version extracts.

## What kind of question? → Shape

Pick the shape **by question type** before picking a tool. This table
is load-bearing: the wrong shape produces a wrong-looking cache file
and burns a turn.

| The user's question is shaped like… | Shape |
|---|---|
| "What's in `scratch/api/<lib>/<version>/`?" (always check first) | **0** cache hit |
| "Which entry point should I use for &lt;task&gt;?" | **Stack orientation** below, then Shape 1 to confirm |
| "What's the signature of X?" / "What args does X take?" | **1** symbol card |
| "What's in module Y?" (open-ended discovery, no named entry point in mind) | **2** module surface |
| "How does X work?" / "Which of A or B should I use?" | **3** narrative |
| **"What does X return when `<arg>` is `<value>`?"** | **3** narrative |
| "What's the recommended pattern for …?" | **3** narrative |

**Shape 3 is the right answer when the question depends on a
*condition* over an argument, even though a signature is involved.**
The help() text from Shape 1 carries a `Returns` section but typically
does not enumerate the dispatch behaviour under each argument value —
that lives in the narrative docs.

## Stop conditions — read before any lookup

- **No symbols from memory.** Every function / class / method / arg
  you write must come from a lookup *this turn* — `inspect.signature`,
  a `scratch/api/<lib>/<version>/` file, or a fresh WebFetch.
  Recognition does not count. Sticky named cases in this stack
  (full list: `references/named_traps.md`):
  - skrub: `tabular_learner` → renamed to `tabular_pipeline` in
    skrub 0.7+. Memory-typed `from skrub import tabular_learner`
    raises `ImportError` on modern installs.
  - skrub: `mark_as_y(target_column)` → signature dropped the
    positional arg in 0.9+; column selection is now
    `.skb.select("...")` *before* the mark.
  - skore: `Project.get(...)` is by **id**, not user-facing `key`;
    enumerate via `project.summarize()` first. A failed
    `get(key)` does **not** mean the report is missing.
- **Never fabricate a probe result.** If the probe has not executed,
  the `Signature` / `help()` sections of the cache file must remain
  blank or marked `<pending probe execution>`. Writing plausible-looking
  output before running the tool is fabrication — the next agent
  reads the cache as authoritative and will trust it. **Same rule for
  Shape 3:** do not paraphrase docs from memory into the cache; the
  cache file holds verbatim extracts of fetched pages.
- **Version-correct first.** Resolve `<pkg>.__version__` before any
  lookup. The version subfolder is the cache freshness key; the wrong
  version pollutes the cache.
- **Cache hit before fresh fetch.** List `scratch/api/<lib>/<version>/`
  before Shape 1 / 2 / 3. Hit → Read, done.
- **Lookup failure ≠ artifact missing.** A `KeyError` /
  `AttributeError` / not-found on a registry-style API
  (`project.get(key)`, `getattr(obj, name)`, `dict[key]`) is almost
  always the **lookup shape** (id vs key, wrong accessor) or stale
  state — not a missing artifact. The named instance in this stack:
  `skore.Project.get(...)` resolves by **id**, not by user-facing
  `key`; `project.summarize()` enumerates `(key, id)` pairs.
  **Never substitute by re-creating the artifact** — that lands a
  duplicate row.
- **All Python execution goes to `scratch/<YYYY-MM-DD>_<HHMMSS>_<short>.py`.
  No exceptions.** Every Python command — `pixi run python -c`,
  `python -c`, heredoc-style `python << 'EOF'`, or any inline
  Python invocation — is forbidden, regardless of length. Write
  the code to a scratch file first, then execute it via
  `pixi run python scratch/<ts>_<short>.py`. Applies to:
  - version checks (`print(<pkg>.__version__)`),
  - existence / import smoke checks (`from <pkg> import X`),
  - signature lookups (`inspect.signature(...)`),
  - module surface dumps (`dir(...)`, `pkgutil.iter_modules(...)`),
  - docstring extraction (`pydoc.render_doc(...)`, `help(...)`),
  - any other Python investigation, including "just one line".

  If you catch yourself typing `python -c` — STOP and write the
  file instead. The scratch file is the deliverable; inline
  execution leaves no trace and no cache, which is exactly the
  bypass this rule blocks.
- **`inspect.signature` / `dir(...)` / `pydoc.render_doc` /
  `help(...)` executed inline is NOT a python-api consultation.**
  These are the exact APIs this skill wraps. Running them via
  `python -c "..."` (any length) and reading the output does NOT
  satisfy the "python-api consulted" pre-flight row in any
  sibling skill. The deliverable is a
  `scratch/api/<lib>/<version>/<topic>.md` file written this
  turn — Shape 1 probe template, no shortcut.
- **`pydoc.render_doc`, not `__doc__`.** `__doc__` is empty /
  misleading on properties, descriptors, decorated callables, and
  accessors like `report.metrics.rmse` — exactly the cases the cache
  exists to disambiguate.
- **Narrative findings get cached.** A WebFetch result that is read
  and discarded is forbidden. Land it in
  `scratch/api/<lib>/<version>/<topic>.md` with the source URL on
  the first line.
- **A probe without a cache write is not a completed lookup.** The
  probe records the *investigation*; the cache file records the
  *conclusion*. Ending a Shape 1 / 3 turn without
  `scratch/api/<lib>/<version>/<topic>.md` on disk = incomplete.

## Forbidden shortcuts

| Shortcut | Why it's wrong |
|---|---|
| Recognise the symbol name from training data → write the call | Memory is keyed to an arbitrary version; the install may have renamed / re-signatured |
| Probe ran, answer is on screen → stop without writing the cache | Probe is investigation; cache is conclusion. Next session will repeat the probe |
| Bundled `.agents/skills/python-api/references/X.md` exists → treat as the cache | References are workflow patterns; cache is per-version extracts. Both must exist |
| Version subfolder missing → write into the latest existing one | The subfolder is the freshness key. Create the right one |
| Multiple symbols needed → string several `inspect.signature` calls into one inline `python -c` | All Python execution goes to scratch — there is no inline `python -c` allowance. Multi-symbol → one scratch file, one consolidated cache file |
| Used `python -c "import <pkg>; print(<pkg>.__version__)"` for a quick version check | The rule is unconditional. Length is not the criterion — traceability is. Version checks go to `scratch/<ts>_version_<pkg>.py`. Inline calls leave no record in `scratch/`, breaking the convention |
| Cache for the topic already exists; ran inline `inspect.signature(X)` to re-confirm one arg name | Shape 1a (inline single-signature carve-out) is removed. Every Shape 1 lookup uses the probe template. Re-confirming one arg appends to the existing cache file via a fresh probe — no inline shortcut |
| Used `python -c "...inspect.signature..."` instead of writing the Shape 1 probe | "Inline gave me the signature this turn, that's enough" → the probe records the *investigation*; the cache file records the *conclusion*. Next session needs the file, not your transcript. Inline introspection ≠ python-api consultation |
| User pasted a docs URL → treat as the answer | The lookup still requires `inspect` or `WebFetch` + cache write. URLs are leads |
| Use `__doc__` instead of `pydoc.render_doc` | `__doc__` is empty on many accessors; the cache file must be readable standalone |

## First action — every turn that triggers this skill

1. **Resolve the version** of every library at stake. Write
   `scratch/<YYYY-MM-DD>_<HHMMSS>_version_<pkg>.py` containing
   `import <pkg>; print(<pkg>.__version__)`, run with
   `pixi run python scratch/<ts>_version_<pkg>.py`. **Do NOT use
   inline `python -c`** — the rule is unconditional (see Stop
   conditions).
2. **List the cache:** `ls scratch/api/<lib>/<version>/`.
3. **Cache hit?** Read the matching file. Done. Skip the rest.
4. **Cache miss?** Classify the question (see decision table) → run
   Shape 1, 2, or 3.
5. **Emit the pre-flight checklist below** as visible text in the
   response, with each box marked.

## Pre-flight — emit this checklist before any lookup

```
Pre-flight (python-api):
- [ ] Package version resolved this turn: <lib> <version>
      Evidence: Write scratch/<ts>_version_<lib>.py (this turn) +
                tool call `pixi run python scratch/<ts>_version_<lib>.py`
                output (paste version string).
                **Inline `python -c "..."` is NOT evidence.**
- [ ] Cache listed this turn (Shape 0): `ls scratch/api/<lib>/<version>/`
      Evidence: tool output (paste the listing, even if empty)
- [ ] Question shape classified (see table): signature | module surface | narrative
      Evidence: name the shape and one phrase from the question that put it there
- [ ] Lookup decision: cache hit (Read <file>) | Shape 1 | Shape 2 | Shape 3
      Evidence: name the file Read, the probe script written, or the URL fetched
- [ ] Cache file lands on disk before turn end
      Evidence: Write scratch/api/<lib>/<version>/<topic>.md (this turn)
                | "n/a — cache hit, file already on disk + Read this turn"
      **Inline `inspect.signature(...)` / `dir(...)` / `pydoc.render_doc(...)`
      WITHOUT a corresponding cache file is NOT evidence. Re-do as Shape 1.**
- [ ] If Shape 1: Usage section filled in (Call / Don't call / Trap / Returns)
      Evidence: Edit scratch/api/<lib>/<version>/<topic>.md (this turn)
                | "n/a — cache hit / Shape 2 / Shape 3"
```

The cache-listing row catches "I'll just inspect the symbol from
memory". Skipping it is a Stop-condition violation.

## The four shapes

### Shape 0 — cache hit

```bash
ls scratch/api/<lib>/<version>/ 2>/dev/null
```

Topic-matching file present → `Read` it. The first line carries the
source URL or `inspect:` ref; re-verify against live docs if a file
looks suspicious. Cache miss → Shape 1 / 2 / 3.

### Shape 1 — symbol card (signature + `help()` → cache file)

One probe script does both: introspects the symbol *and* writes the
cache file in a single execution. A small follow-up `Edit` fills the
`Usage` bullets.

**Probe template.** Copy, edit `LIB` / `DOTTED` / `TOPIC`, save as
`scratch/<YYYY-MM-DD>_<HHMMSS>_lookup_<lib>_<topic>.py`, run with
`pixi run python <path>`:

```python
"""Lookup: <lib>.<dotted> @ installed version."""
from __future__ import annotations

import datetime, importlib, inspect, io, pydoc
from pathlib import Path

LIB = "skore"          # top-level package name
DOTTED = "evaluate"    # dotted path under the package
TOPIC = "evaluate"     # cache filename stem (snake_case)

mod = importlib.import_module(LIB)
sym = mod
for part in DOTTED.split("."):
    sym = getattr(sym, part)

version = mod.__version__
try:
    sig = str(inspect.signature(sym))
except (TypeError, ValueError):
    sig = "<no signature; see help below>"
help_text = pydoc.render_doc(sym, renderer=pydoc.plaintext)

out = io.StringIO()
out.write(f"# {TOPIC}\n\n")
out.write(f"Source: inspect: {LIB}.{DOTTED} @ {version}\n")
out.write(f"Probed: {datetime.date.today():%Y-%m-%d}\n\n")
out.write(f"## Signature\n\n```\n{sig}\n```\n\n")
out.write(f"## help()\n\n```\n{help_text}\n```\n\n")
out.write(
    "## Usage (agent synthesis — fill in this section)\n\n"
    "- **Call:** TODO\n"
    "- **Don't call:** TODO\n"
    "- **Trap:** TODO\n"
    "- **Returns:** TODO\n"
)

cache_dir = Path("scratch/api") / LIB / version
cache_dir.mkdir(parents=True, exist_ok=True)
(cache_dir / f"{TOPIC}.md").write_text(out.getvalue())
print(out.getvalue())
```

**Step 2 — fill in `Usage`.** After the probe runs, `Edit` the cache
file and replace each `TODO` with one line. Read the actual `help()`
output the probe produced — do not write the synthesis from memory.

**No inline carve-out for single-signature checks.** Even when a
cache file already exists and you need to re-confirm one arg, you
run a fresh probe (or read the existing cache file). Inline
`pixi run python -c "...inspect.signature..."` is forbidden — the
2-line carve-out that previously allowed it is removed. The
reasons: (a) the probe records the investigation and the cache
file records the conclusion, both with traceability; (b) inline
calls leave no record in `scratch/`, so future agents can't audit
how the answer was reached; (c) the gradient from "one inline
call" to "I'll just inspect everything inline" is exactly the
bypass this rule blocks.

**Multi-symbol consolidation.** When several symbols share a topic
(e.g. `Project.put` / `Project.get` / `Project.summarize` under
`project_local`), iterate over a tuple of dotted paths inside the
probe and concatenate sections into one `<topic>.md`. One topic file
per *topic*, not per symbol.

**Python compatibility.** `pydoc.render_doc(sym, renderer=pydoc.plaintext)`
works on Python 3.10+ (pass `pydoc.plaintext`, do not call it).
`pydoc.help` cannot be captured via `output=` on 3.10+.

### Shape 2 — module surface

Write a scratch probe that dumps both the top-level surface and
the submodule list, then writes `surface.md` directly. **No inline
`python -c`** — same rule as Shape 1.

Probe template — save as
`scratch/<YYYY-MM-DD>_<HHMMSS>_surface_<lib>.py`, run with
`pixi run python <path>`:

```python
"""Surface dump: dir(<lib>) + pkgutil.iter_modules() @ installed version."""
from __future__ import annotations

import datetime
import importlib
import pkgutil
from pathlib import Path

LIB = "skrub"   # top-level package name

mod = importlib.import_module(LIB)
version = mod.__version__

top_level = sorted(n for n in dir(mod) if not n.startswith("_"))
try:
    submods = sorted(m.name for m in pkgutil.iter_modules(mod.__path__))
except AttributeError:
    submods = []

lines = [
    f"# {LIB} {version} — module surface",
    "",
    f"Source: dir({LIB}) + pkgutil.iter_modules({LIB}.__path__) "
    f"@ {datetime.date.today():%Y-%m-%d}",
    "",
    "## Top-level",
    "",
    *[f"- {n}" for n in top_level],
    "",
    "## Submodules",
    "",
    *[f"- {n}" for n in submods],
    "",
]

cache_dir = Path("scratch/api") / LIB / version
cache_dir.mkdir(parents=True, exist_ok=True)
(cache_dir / "surface.md").write_text("\n".join(lines))
print("\n".join(lines))
```

One topic per file. Replace only on a version bump.

### Shape 3 — narrative

Conceptual questions where the signature alone doesn't answer it —
"how does the DataOps graph evaluate?", "what does `skore.evaluate`
return when `splitter` is a `KFold`?", "which of `apply` /
`apply_func` should I use?". Procedure:

1. **WebSearch** for the versioned docs URL. Query shape:
   `<library> <MAJOR.MINOR> docs <topic>` — e.g.
   `skore 0.18 docs evaluate splitter`. Don't construct the URL
   from memory.
2. **WebFetch** the most relevant result whose URL contains the
   installed version (`/0.18/`, `/0.18.0/`). **Reject** any URL
   containing `/latest/` or `/stable/` — those drift on republish.
3. **Cache verbatim** to `scratch/api/<lib>/<version>/<topic>.md`:

   ```markdown
   # <topic>

   Source: <full URL>
   Fetched: <YYYY-MM-DD>

   <paste the salient sections verbatim — do NOT paraphrase from
   memory. Skip navigation chrome; keep prose that directly answers
   the question.>
   ```

Cache filename: snake_case mirror of the docs URL slug. One topic
per file. Replace only on a version bump.

## Cache file contract

Every `scratch/api/<lib>/<version>/<topic>.md` follows a
four-section shape:

```
# <topic>

Source: inspect: <lib>.<dotted> @ <version>  |  <docs URL>
Probed: <YYYY-MM-DD>

## Signature
<fenced block — exactly as inspect.signature returned it, Shape 1 only>

## help()  (or "## Docs extract" for Shape 3)
<verbatim pydoc.render_doc output for Shape 1, verbatim WebFetch
 extract for Shape 3. Never paraphrase.>

## Usage (agent synthesis)
- **Call:** import path + arg shape this workspace uses (2-3 line snippet)
- **Don't call:** named substitutes that look right from memory
- **Trap:** version-specific rename / deprecation / footgun (empty if none)
- **Returns:** return type + the one accessor the next caller needs
```

Bootstrap turns have a **required minimum cache** to leave behind —
see `references/bootstrap_cache.md` for the file list and audit
procedure.

## Cache layout & lifecycle

```
scratch/api/
├── skrub/0.9.0/
│   ├── data_ops.md          # Shape 3 narrative
│   ├── tabular_pipeline.md
│   └── surface.md           # Shape 2 dir() dump
├── skore/0.18.0/
│   ├── evaluate.md
│   └── project_local.md
└── sklearn/1.8.0/
    └── cv_splitters.md
```

- **Version subfolder == `<pkg>.__version__` exactly.** No abbreviation
  (`0.18.0` ≠ `0.18`). Different installed version → different folder.
- **First line is the source URL or `inspect:` ref.** Future agents
  can re-verify.
- **Gitignored** by the existing `scratch/*` rule. Regenerable from
  public docs.
- **Append-on-success.** Once written, frozen. Replace only on a
  version bump (the version-subfolder convention handles this — a
  bump creates a new empty subfolder; the old one stays until
  manual cleanup).
- **Cache miss in a stale subfolder is impossible by construction.**
  Shape 0 reads by version; old subfolder content is invisible.

## `scratch/` conventions — probes vs. cache

Two structured uses of `scratch/`, both gitignored:

| | Ad-hoc probes | API doc cache |
|---|---|---|
| **Path** | `scratch/<YYYY-MM-DD>_<HHMMSS>_<short>.py` | `scratch/api/<lib>/<version>/<topic>.md` |
| **What** | Multi-line `inspect` walks, sanity checks, metric extraction | Signature / help() / docs extract per topic |
| **Naming** | Timestamped (chronological) | Topic-organised (no timestamp) |
| **Lifecycle** | Append-only after success; overwrite on error in same loop | Append-on-success; replace on version bump |
| **Inline cap** | **No inline `python -c`. All Python execution goes to scratch, regardless of length** (see Stop conditions) | n/a (probes write the cache) |

**Never edit an experiment script to add agent-only `print(...)` calls
for inspection.** Inspection goes in `scratch/`. Experiment scripts
are the durable record of what was run.

**Never re-run an experiment / `project.put` from a scratch probe.**
Scratch is read-only against the skore Project (use
`project.summarize()` then `project.get(id)`). Re-running writes a
duplicate row. See Stop conditions above + `organize-ml-workspace`
§ "Scratch is read-only".

**The read-only rule extends to `audit/` files too.** The audit
flow owned by `audit-ml-pipeline` places one `# %%` file per
experiment under `audit/<NN>_<short_name>.py` and executes it via
jupytext + nbconvert. The same `summarize()` → `get(id)` →
`report.*` discipline applies — never call `skore.evaluate(...)`
or `project.put(...)` from an audit file. The executed
intermediates (`audit.ipynb`, `audit.executed.ipynb`, `audit.md`)
land under `scratch/audit/<stem>/`, which is gitignored just like
the rest of `scratch/`. The markdown digest is a legitimate
narrative read for the agent (per `audit-ml-pipeline` §
"Execution contract"); it is not a substitute for the
`scratch/api/<lib>/<version>/<topic>.md` cache shape this skill
owns. Two different artifacts, two different lifecycles:

| | API doc cache | Audit executed digest |
|---|---|---|
| **Owner** | `python-api` | `audit-ml-pipeline` |
| **Source** | `inspect.signature` / `pydoc.render_doc` / versioned-docs WebFetch | Executing `audit/<stem>.py` with jupytext + nbconvert |
| **Lifecycle** | Append-on-success; replace on version bump | Overwritten on every audit re-execution |
| **Read by** | Any skill needing a symbol's signature or contract | The agent during `iterate-ml-experiment` § 4 narrative work |

This skill is the canonical home for these conventions. The
workspace's `scratch/` folder does **not** carry a `README.md` —
rules of this importance live in the skill that's loaded into
context at use-time.

## Stack orientation — where things live

Tier-1 named entry points. Consult this *before* a Shape 2 surface
dump for "where does X live in this library" questions — the named
entry is often the right answer and a `dir()` walk just confirms it.

### scikit-learn

- `sklearn.metrics` — scoring functions (`accuracy_score`,
  `roc_auc_score`, `mean_absolute_error`, `make_scorer`).
- `sklearn.preprocessing` — stateful scalers / encoders / imputers
  (`StandardScaler`, `OneHotEncoder`, `KBinsDiscretizer`).
- `sklearn.pipeline` / `sklearn.compose` — `Pipeline`,
  `make_pipeline`, `ColumnTransformer`.
- `sklearn.model_selection` — splitters (`KFold`, `GroupKFold`,
  `TimeSeriesSplit`, `train_test_split`) + search (`GridSearchCV`).
- Estimators under `sklearn.linear_model` / `sklearn.ensemble` / etc.

### skrub

- **One-call mixed-type featuriser / learner**: `skrub.tabular_pipeline`
  (top-level function). This is the entry point for a default-everything
  featuriser+learner over a numeric+categorical+text DataFrame. **Not**
  `tabular_learner` (renamed in 0.7+); **not** `TabularLearner`.
- **Per-column encoders** (top-level): `TableVectorizer`,
  `DatetimeEncoder`, `TextEncoder`, `StringEncoder`.
- **DataOps DSL** (lazy pipeline graph): lives in the `.skb`
  namespace on every node — `X.skb.apply`, `X.skb.apply_func`,
  `X.skb.mark_as_X`, `X.skb.mark_as_y`, `X.skb.make_learner`,
  `.skb.preview`, `.skb.full_report`.
- **Sources / variables**: `skrub.var(name, value=...)`,
  `skrub.as_data_op({...})`.
- **Selectors** for column routing: `skrub.selectors.{numeric,
  categorical, string, ...}`.

### skore

- **Evaluation entry point**: `skore.evaluate(estimator, X=None,
  y=None, data=None, *, splitter=None, ...)` — dispatches by
  `splitter` to `EstimatorReport` (no splitter) /
  `CrossValidationReport` (CV splitter) / `ComparisonReport`
  (multi-key).
- **Project**: `skore.Project(workspace=..., name=..., mode=...)`
  with `put(key, report)` / `summarize()` (DataFrame indexed by id
  with `key` column) / `get(id)` — **`get` is by id, not by `key`**.

Full per-library surface map (rare submodules, accessor cheat
sheet): **`references/stack_orientation.md`** (load when the names
above don't cover the question).

## When the installed package is wrong

Two options, neither involves "writing from memory of a different
version":

1. Route to `python-env-manager` § "Upgrade / pin" to bump or pin.
   Re-do the lookup against the new install.
2. Adapt to what's installed — change the approach so the current
   surface works.

## See also

- **Companion skills**
  - `python-env-manager` — owns versions (the version it resolves
    is what keys `scratch/api/<lib>/<version>/`).
  - `data-science-python-stack` — owns *which library* to pick;
    this skill takes the library as given.
  - `build-ml-pipeline` / `evaluate-ml-pipeline` /
    `iterate-from-skore` / `smoke-test-ml-pipeline` — workflow skills
    that dispatch here when they need a symbol.

- **Bundled references (`references/`)** — durable workflow patterns
  - `pre_mark_alignment.md` — 3-layer skrub DataOps pattern for
    history-dependent pipelines. Read before authoring history-dep code.
  - `skrub_interop.md` — how `SkrubLearner` integrates with
    `skore.evaluate`. Read before writing `experiments/NN_*.py`.
  - `stack_orientation.md` — full per-library surface map (sklearn /
    skrub / skore). Load when the inline orientation above doesn't
    name what you need.
  - `bootstrap_cache.md` — required minimum cache files for a
    bootstrap turn + audit procedure.
  - `named_traps.md` — version-specific renames / deprecations the
    agent has hit in real traces (sticky named cases).
  - `authoring_protocol.md` — when and how to land a new reference
    doc (user-gated via `AskUserQuestion`; references are durable
    git content).

## What this skill does NOT do

- Maintain pre-baked signature listings *in the skill folder*.
  Per-version extracts live in the workspace cache; the skill
  folder carries only durable workflow patterns.
- Generate cache files on install. Caching is on-demand.
- Explain a library's API at depth — that's the library's own docs.
  This skill points at them and caches what's worth keeping.
- Auto-author references. New `references/<topic>.md` files are
  user-gated via `AskUserQuestion` (see
  `references/authoring_protocol.md`).
