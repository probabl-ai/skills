---
name: python-api
description: >
  Discover the public API of any Python package by looking it up
  against the *installed version* and caching what's worth
  remembering. Owns the lookup procedure — four shapes, picked by
  question: (0) check the workspace's `scratch/api/<lib>/<version>/`
  cache; (1) `inspect.signature(...)` + `__doc__` for a specific
  symbol; (2) `dir(...)` / `pkgutil.iter_modules(...)` for a
  module's surface; (3) WebSearch the versioned docs site for
  narrative ("how to use", "which one of these", "what's the
  recommended pattern"), then WebFetch + cache. Carries brief
  conceptual orientation for the stack's tier-1 libraries (sklearn
  / skrub / skore) so the agent knows *where* to look. Never
  pre-bakes per-version signatures in the skill folder — those
  live in the workspace cache and get regenerated on a version
  bump.

  TRIGGER when about to write code using a library that isn't
  actively in working memory — *any* of: (a) signature unclear;
  (b) don't know which submodule owns the thing; (c) don't recall
  the conceptual entry point ("how do I do X with Y?"); (d)
  picking between two approaches in the same library; (e) about
  to reach for a library's "obvious" pattern from training-data
  memory. Also when the user asks "what's the signature of X?",
  "what does X return?", "what's in module Y?", "how do I call
  ...?"; or when another workflow skill (`build-ml-pipeline`,
  `evaluate-ml-pipeline`, `iterate-from-skore`,
  `smoke-test-ml-pipeline`) says "consult the API skill before
  naming a symbol".

  SKIP when: the symbol's signature is obvious from the call site
  immediately preceding (you can read it), and you've already
  resolved the package's version in this turn; the work is purely
  filesystem / shell (no Python symbols at stake); the cache at
  `scratch/api/<lib>/<version>/` already answers the question (in
  which case you've still consulted this skill — you just didn't
  need a fresh fetch).

  HOW TO USE: **first, identify the package version** (`pixi run
  python -c "import <pkg>; print(<pkg>.__version__)"`). **Then
  list `scratch/api/<lib>/<version>/`** — if the topic is already
  cached, read it. Otherwise pick the lookup shape that matches
  your need (signature, module surface, or narrative). Narrative
  findings get cached back to `scratch/api/<lib>/<version>/`.
  Anything multi-line goes through `scratch/`, not inline `python
  -c`. Stack-specific orientation (where things live for
  sklearn / skrub / skore) is in the body — use it to know
  *which* module to introspect.
---

# python-api

The agent's API discovery skill. Three durable rules: **lookup
against the installed version, never against memory**; **cache
narrative findings to the workspace** (`scratch/api/`) so future
turns and future sessions don't repeat the same WebFetch; **keep
workflow patterns in `references/`** separate from per-version
extracts in the cache.

## Stop conditions — read before naming any symbol

- **No symbols from memory.** Any function / class / method name
  you write in code must come from a lookup *this turn* against
  the installed version — `inspect.signature(...)`, `dir(...)`, a
  cache file under `scratch/api/<lib>/<version>/`, or a fresh
  WebFetch. "I remember sklearn has X" is not acceptable; the
  model's training data may be older than the installed version
  (or newer).
- **Version-correct first.** Before any lookup, confirm the
  installed version: `pixi run python -c "import <pkg>;
  print(<pkg>.__version__)"`. The version is what keys the
  workspace cache (`scratch/api/<lib>/<version>/`); without it
  you can read the wrong subfolder or write to the wrong one.
- **Cache hit before fresh fetch.** After confirming the
  version, list `scratch/api/<lib>/<version>/` for the topic
  you're after. If a file already exists, read it instead of
  re-fetching. Stale cache is impossible by construction — the
  version subfolder protects against version drift, and a
  pinned-version install keeps the same subfolder relevant
  across turns.
- **Multi-line probes go to `scratch/`, not inline.** Any Python
  investigation longer than 2 lines lands in `scratch/<ts>_<short>.py`
  (per the workspace's `scratch/README.md`), not in `pixi run
  python -c "..."`. Applies to multi-symbol `inspect.signature`
  walks, long `dir(...)` listings, docstring extracts that span
  several names. The 2-line cap is contract.
- **Never edit the experiment script to add agent-only `print`
  calls** as a way to "look at" what the pipeline produces.
  Inspection goes in `scratch/` per `organize-ml-workspace` §
  "What an experiment script does".
- **Narrative findings get cached.** When you do reach the
  WebSearch + WebFetch path (Shape 3 below), the result lands
  in `scratch/api/<lib>/<version>/<topic>.md` with the source
  URL on the first line. Read-and-discard is forbidden — the
  *next* agent that needs the same page should hit the cache,
  not the network.
- **Ad-hoc `scratch/<ts>_*.py` probes are not a substitute for
  a cache write.** When `inspect.signature` / `dir` / WebFetch
  has yielded a *conclusion* about a library — "skore.evaluate
  rejects `X=, y=` for a SkrubLearner; use `data={"X": ..., "y":
  ...}`"; "skore.Project.summarize() returns a MultiIndex with
  `id` as the second level"; "skrub.X / skrub.y are sugar for
  `var().skb.mark_as_X`" — that conclusion **must** land in
  `scratch/api/<lib>/<version>/<topic>.md` *in addition to* any
  probe `.py` file. The probe records the *investigation*; the
  cache file records the *conclusion*. The next agent reads the
  cache, not the probes. A multi-file scratch tree that
  rediscovers the same surfaces every session is the failure
  mode this rule blocks.

## The lookup procedure — four shapes

Pick the shape that matches your question. Always start with
Shape 0.

### Shape 0 — cache hit?

After resolving the version, list the cache:

```bash
ls scratch/api/<lib>/<version>/ 2>/dev/null
```

If a file with a name matching your topic is there, `Read` it.
The first line of every cache file is the source URL, so you
can re-verify against public docs if the file looks suspicious
(typically only relevant if the version subfolder convention
was violated — which would be a bug, not staleness).

Cache miss → continue to Shape 1, 2, or 3.

### Shape 1 — signature + docstring of a specific symbol

```bash
pixi run python -c "
import inspect
from <pkg>.<module> import <Symbol>
print(inspect.signature(<Symbol>))
print(<Symbol>.__doc__)
"
```

Inline ≤2 lines for one or two symbols. For a method on an
instance, instantiate first or call
`inspect.signature(Class.method)`. For overloaded / decorated
callables, `inspect.signature` may not show the user-facing
form — fall back to `<Symbol>.__doc__` and / or Shape 3.

Single-symbol signature lookups are not cached — they're cheap
and the inline form is the canonical "lookup record" already
visible in the tool trace.

### Shape 2 — module surface

```bash
pixi run python -c "
import <pkg>
print(sorted(n for n in dir(<pkg>) if not n.startswith('_')))
"
```

For subpackage discovery:

```bash
pixi run python -c "
import pkgutil, <pkg>
print([m.name for m in pkgutil.iter_modules(<pkg>.__path__)])
"
```

If you're going to grep the listing more than once, cache it as
markdown to `scratch/api/<lib>/<version>/surface.md`:

```markdown
# <lib> <version> — module surface

Source: `dir(<lib>)` + `pkgutil.iter_modules(<lib>.__path__)` at <YYYY-MM-DD>.

## Top-level

- foo
- bar
- ...

## Submodules

- <lib>.metrics
- <lib>.preprocessing
- ...
```

One file per library/version. Append-on-success — only replace
on a version bump.

### Shape 3 — narrative ("how to use", "which of these", "recommended pattern")

Conceptual questions where signatures don't answer it: "how
does the DataOps graph evaluate?", "what does
`skore.evaluate` return when `splitter` is a `KFold`?", "what's
the difference between `apply_func` and `deferred`?". The
procedure:

1. **WebSearch first** to find the versioned docs URL. Query
   shape: `<library> <MAJOR.MINOR> docs <topic>` — e.g.
   `skrub 0.9 docs DataOps`, `skore 0.18 docs evaluate splitter`,
   `scikit-learn 1.8 docs TimeSeriesSplit`. Don't construct the
   URL from memory; the project's docs URL convention may
   differ (`/stable/`, `/<MAJOR.MINOR>/`, `/latest/`, a custom
   subdomain).

2. **WebFetch** the most relevant versioned URL from the search
   results. Reject any result whose URL contains `/latest/` or
   doesn't carry the installed version — those drift on
   republish.

3. **Cache** the salient sections to
   `scratch/api/<lib>/<version>/<topic>.md`:

   ```markdown
   # <topic>

   Source: <full URL>
   Fetched: <YYYY-MM-DD>

   <paste the salient sections verbatim — do NOT paraphrase
   from memory. If the page is long, extract the headings and
   prose blocks that directly answer the question; skip
   navigation chrome and unrelated tutorials.>
   ```

   Naming: snake_case mirror of the docs URL slug
   (`cross_validation.md`, `data_ops.md`, `tabular_learner.md`).
   One topic per file. Replace only on a version bump.

The cache file is what every subsequent turn reads. WebFetch
is the *generator* of cache files; Shape 0 is the *reader*.

## The `scratch/api/` cache — layout and lifecycle

```
scratch/api/
├── skrub/
│   └── 0.9.0/
│       ├── data_ops.md          # narrative cached via Shape 3
│       ├── tabular_learner.md
│       └── surface.md           # dir() dump via Shape 2
├── skore/
│   └── 0.18.0/
│       ├── evaluate.md
│       └── project.md
└── sklearn/
    └── 1.8.0/
        └── linear_model.md
```

- **Version subfolder == `<pkg>.__version__` exactly.** Different
  installed version → different folder. The `<MAJOR>.<MINOR>.<PATCH>`
  string from `__version__` is the source of truth (not a docs
  URL slug — those can differ, e.g. scikit-learn 1.8.0 → docs
  path `/1.8/`).
- **Topic file mirrors the docs URL slug** in snake_case
  (`cross_validation.md`, `data_ops.md`). One topic per file.
- **First line is the source URL** the content came from.
  Future agents can re-verify against the live docs.
- **Gitignored** by the existing `scratch/*` rule. Caches are
  regenerable from public docs; fresh-clone agents repopulate
  on demand.
- **Append-on-success.** Once a cache file lands, it's frozen.
  Replace only on a version bump (the version-subfolder
  convention handles this for free — bumping skrub 0.9.0 → 0.10.0
  creates a new subfolder; the old one stays until cleanup).
- **Cache miss in a stale subfolder.** If `scratch/api/skrub/0.9.0/`
  exists but the installed skrub is now 0.10.0, you'll see a
  cache miss in `0.10.0/` (which is empty) — Shape 0 reads the
  correct subfolder by version, so the old `0.9.0/` content is
  invisible to a 0.10.0 lookup. Periodic manual cleanup of old
  subfolders is optional, not required.

## Stack orientation — where things live

Conceptual orientation (which submodule owns what). Stable
across versions; the per-version detail goes in the cache.

### scikit-learn

- `sklearn.metrics` — scoring functions, both functional
  (`accuracy_score`, `roc_auc_score`, `mean_absolute_error`) and
  callable-via-`make_scorer`.
- `sklearn.preprocessing` — stateful scalers, encoders, imputers
  (`StandardScaler`, `OneHotEncoder`, `KBinsDiscretizer`).
- `sklearn.pipeline` / `sklearn.compose` — `Pipeline`,
  `make_pipeline`, `ColumnTransformer`, `FeatureUnion`.
- `sklearn.model_selection` — splitters (`KFold`, `GroupKFold`,
  `TimeSeriesSplit`, `train_test_split`) and search
  (`GridSearchCV`, `RandomizedSearchCV`).
- `sklearn.linear_model` / `sklearn.ensemble` /
  `sklearn.neighbors` / etc. — the estimators themselves.

When in doubt, Shape 2 on `sklearn` (top level is mostly
submodule re-exports) followed by
`pkgutil.iter_modules(sklearn.__path__)` finds the right
submodule.

### skrub

- **Top-level helpers**: `tabular_learner`, `tabular_pipeline`,
  `TableVectorizer`, `DatetimeEncoder`, `TextEncoder`,
  `StringEncoder`. Use these for tabular learners that pick
  reasonable defaults per column type.
- **DataOps**: the lazy-pipeline DSL lives in the `.skb`
  namespace on every node (`X.skb.apply`, `X.skb.apply_func`,
  `X.skb.mark_as_X`, `X.skb.mark_as_y`, `X.skb.make_learner`,
  `.skb.preview`, `.skb.full_report`). Sources / variables are
  `skrub.var(name, value=...)` and `skrub.as_data_op({...})`.
- **Selectors** for column-routing within `apply`:
  `skrub.selectors.{numeric, categorical, string, ...}`.

`dir(skrub)` for top-level; `dir(X.skb)` for the DataOp node
API.

### skore

- **Evaluation entry point**: `skore.evaluate(estimator, X=None,
  y=None, data=None, *, splitter=..., ...)` — dispatcher,
  returns the right report type based on `splitter`. `X`/`y` for
  sklearn-style fits; `data={"<var>": value}` for env-dict-style
  (`SkrubLearner`).
- **Report types**: `EstimatorReport` (single train/test split),
  `CrossValidationReport` (CV), `ComparisonReport` (multi-key).
  All expose `.metrics`, `.feature_importance` (where applicable),
  `.diagnosis()` (the diagnostic surface used by
  `iterate-from-skore`).
- **Project**: `skore.Project(workspace="reports", name="...",
  mode="local"|"hub"|"mlflow")`. Methods: `put(key, report)`,
  `get(id)` (note: by id, not by key — get the id from
  `summarize()`), `summarize()` (returns a pandas DataFrame
  indexed by id with columns including `key`, `learner`,
  `ml_task`, `report_type`, mean metrics, …), `delete(id)`.

`dir(skore)` for top-level; `dir(report)` and
`dir(report.metrics)` for the report accessor surface.

## Scratch traceability — ad-hoc probes vs. the API cache

Two structured uses of `scratch/`:

- **`scratch/<ts>_<short>.py`** — ad-hoc, one-file-per-probe,
  timestamped. Multi-line `inspect` walks, multi-symbol
  dump-and-grep, sanity-checks of report state. Append-on-success
  (per `scratch/README.md`).
- **`scratch/api/<lib>/<version>/<topic>.md`** — structured cache
  of API extracts. Topic-organized, version-keyed, NOT
  timestamped. The first line is the source URL.

Both subtrees are gitignored. The README at `scratch/README.md`
covers the convention.

Example ad-hoc probe (Shape 1, multi-symbol → scratch file):

```python
"""Lookup: skore.Project's get / summarize / put signatures."""
import inspect
import skore

p = skore.Project(workspace="reports", name="load-forecast", mode="local")
for m in ("get", "put", "summarize", "delete"):
    print(f"--- {m} ---")
    print(inspect.signature(getattr(p, m)))
    print(getattr(p, m).__doc__)
    print()
```

`pixi run python scratch/...py`.

## When the installed package is wrong

If a lookup reveals the installed version is older / newer than
expected for the task, two options:

1. **Bump / pin via the env manager** — route to
   `python-env-manager` § "Upgrade / pin" to change the
   version. Re-do the lookup against the new install. The
   version-subfolder convention means caches from the prior
   version are simply invisible to the new lookup; they don't
   need manual deletion (though periodic cleanup is fine).
2. **Adapt to what's installed** — change the approach so the
   currently-installed surface works. This is the right move
   when the version is pinned for compatibility reasons.

Never paper over a version mismatch by using "what you
remember" from a different version.

## References vs. cache — two registries, one boundary

Two folders carry library knowledge. Don't confuse them.

| | Skill `references/` | Workspace `scratch/api/` |
|---|---|---|
| **What** | Workflow patterns (how to compose libraries for a recurring task) | API extracts (signatures, narrative pages, surface dumps) |
| **Lifetime** | Durable; survive library upgrades | Version-tagged; regenerated on bump |
| **Authoring** | Hand-authored prose + worked code; user-gated via `AskUserQuestion` | Agent-generated from `inspect` / WebFetch |
| **Tracked in git?** | Yes | No (gitignored under `scratch/*`) |
| **Read at** | Project bootstrap, during new-experiment planning | Every API question (Shape 0) |

Workflow patterns are *codebase knowledge*; API extracts are
*library knowledge*. Both worth caching, but in different
places.

### Current references (durable)

- **`references/pre_mark_alignment.md`** — the 3-layer skrub
  DataOps pattern for cross-row pipelines (lags, joins with
  history). Why early `mark_as_X` matters; how Layer-3 feature
  steps reference the upstream history DataOp; the executable
  proof in `tests/smoke/`. Read before authoring or modifying
  any history-dependent pipeline.
- **`references/skrub_interop.md`** — how the `SkrubLearner`
  produced by the pattern above integrates with
  `skore.evaluate` (env-dict-style fit, source-bound vars,
  Project key conventions). Read before writing a new
  `experiments/NN_*.py`.

### Authoring protocol — when to write a new reference

A new reference doc lands here when **all three** hold:

1. The agent has nontrivially figured out a *workflow
   pattern* (via `scratch/` work, WebFetch, multiple
   `inspect` calls, or trial-and-error). One inspect call is
   not enough; the threshold is "this took meaningful
   figuring-out time."
2. The pattern is **workflow-relevant** for this project —
   would help future iterations or future agents reading the
   codebase cold. Generic library docs don't qualify; this-codebase
   patterns do.
3. The pattern is **not just an API extract** — references
   are prose + worked examples about *combining* libraries,
   not "here's what `skore.evaluate` returns" (that's
   `scratch/api/skore/<version>/evaluate.md`).

When all three hold, **fire an `AskUserQuestion`** before
writing — the user gates the new file because references are
durable git content. The doc lives at
`.claude/skills/python-api/references/<topic>.md`.

## What this skill does NOT do

- Maintain pre-cached signature listings *in the skill folder*
  (those would go stale). The workspace cache at
  `scratch/api/` is version-keyed and per-workspace, not
  globally shipped with the skill.
- Generate a per-version reference file on install. Caching
  is on-demand: the first time an agent needs `data_ops.md`,
  it WebSearches + WebFetches + caches. Subsequent reads are
  cache hits.
- Explain *how to use* a library at depth — that's the
  library's own documentation. This skill points at it
  (WebSearch + WebFetch) and caches what's worth keeping.
- Auto-author references without the user's go-ahead. New
  reference docs (the durable workflow patterns) are
  user-gated via `AskUserQuestion`. Cache files
  (`scratch/api/`) are agent-managed and don't need
  approval — they're regenerable.

## Companion skills

- **`python-env-manager`** — owns the version of every
  installed package. Consult before assuming a version; route
  here for upgrades / pins / installs. The version it resolves
  is the version that keys `scratch/api/<lib>/<version>/`.
- **`data-science-python-stack`** — owns *which library to
  pick* for a given task. This skill takes the library as a
  given and looks up its API.
- **`build-ml-pipeline`** / **`evaluate-ml-pipeline`** /
  **`iterate-from-skore`** / **`smoke-test-ml-pipeline`** —
  workflow skills that dispatch here when they need a symbol
  signature; they tell you *which* symbol, this skill tells
  you *what it takes* and where to cache the answer.
