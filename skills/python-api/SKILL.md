---
name: python-api
description: >
  Discover the public API of any Python package by looking it up
  against the *installed version* and caching what's worth
  remembering. Owns the lookup procedure — four shapes, picked by
  question: (0) check the workspace's `scratch/api/<lib>/<version>/`
  cache; (1) `inspect.signature(...)` + `pydoc.render_doc(...)` (the
  rendered `help()` text) consolidated into a per-symbol card under
  the cache; (2) `dir(...)` / `pkgutil.iter_modules(...)` for a
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
  a cache write.** Every Shape 1 probe is structured to write
  `scratch/api/<lib>/<version>/<topic>.md` as a *side effect of
  running*. A probe that ran without producing a cache file is
  not a completed Shape 1 lookup — it is an investigation that
  needs to finish. The probe records the *investigation*; the
  cache file records the *conclusion*. The next agent reads the
  cache, not the probes. A multi-file scratch tree that
  rediscovers the same surfaces every session is the failure
  mode this rule blocks. Same contract applies to Shape 3
  (WebFetch): a conclusion that doesn't land in
  `scratch/api/<lib>/<version>/<topic>.md` is a discarded
  result.
- **`help()` text, not `__doc__`.** Symbol introspection captures
  the rendered help output via
  `pydoc.render_doc(sym, renderer=pydoc.plaintext)`. `__doc__` is
  the raw class attribute and is empty / misleading on
  properties, descriptors, decorated callables, and any
  accessor like `report.metrics.rmse` — exactly the cases the
  cache exists to disambiguate. `pydoc.render_doc` resolves
  inheritance, renders the `Examples` block, and produces a
  string a future agent can read on its own. The builtin
  `help(...)` cannot be captured via `output=` on Python 3.10+
  (`pydoc.help.output` is a read-only property); use
  `pydoc.render_doc` instead.
- **The "I already know this" trap.** The single biggest
  failure mode for this skill is the agent *recognizing* a
  symbol from training data and skipping the lookup because
  "I remember the signature". Training-data memory is keyed to
  an arbitrary version of the library that **may not match
  what's installed** — and the gap between memory and the
  installed version is exactly where renames, signature drops,
  and deprecations live. **Recognition is not a lookup.** The
  lookup is the tool call against the installed version this
  turn; nothing else counts. Recent named cases this trap has
  produced in real traces (named so the cases stay sticky):
  - `tabular_pipeline` (top-level) → renamed to
    `tabular_pipeline` in skrub 0.7+. Memory-based code
    typing `from skrub import tabular_pipeline` raises
    `ImportError` on 0.7+ envs.
  - `mark_as_y(target_column)` → signature changed to
    `mark_as_y()` (no positional column arg) in skrub 0.9+.
    The column selection is done by `.skb.select("...")` on
    the source op *before* the mark. Memory-based code
    typing `raw.skb.mark_as_y("Target")` raises `TypeError`.
  - `skrub.X(...)` / `skrub.y(...)` as graph roots →
    deprecated in favor of `skrub.var(name, value).skb.
    mark_as_X()` / `mark_as_y()`, because the sugar bakes the
    marker at the source and forbids late-marker patterns
    (see `build-ml-pipeline` Stop conditions).
  - `skore.Project(workspace="reports", name="...")` — the
    `workspace` keyword is mode-specific (`local` mode only);
    skipping the docs on `mode=` makes the agent assume
    `workspace=` is universal.
  - `skore.evaluate(...)` printing a Rich-rendered report
    when stdout is redirected can hit a recursion bug in CLI
    contexts; the workaround
    (`with configuration(show_progress=False):`) is a
    config-API call the agent will not find from memory.

  When you catch yourself about to write a symbol you "just
  know": **STOP**, look it up against the installed version
  via Shape 1 (signature) or Shape 0 (cache), and only then
  write the call. The 5–10 seconds of latency are the price
  of correctness across version drift.
- **Free-text doesn't resolve a symbol lookup.** The
  `AskUserQuestion` / "free-text resolves a gate" rule that
  applies to other skills' user-facing gates has no analogue
  here. Symbol correctness is an objective property of the
  installed library; the user telling you "I think the
  function is called X" is not evidence in the sense the
  cache file requires. Treat user-mentioned names as **leads**
  to look up, not as conclusions to write directly.

## Forbidden shortcuts (observed in real traces)

| Shortcut | Why it feels right | Why it's wrong |
|----------|--------------------|----------------|
| Recognize the symbol name from training data → write the call without looking it up | "I know this library" | Memory is keyed to an arbitrary version; the installed version may have renamed / re-signatured the symbol. See the "I already know this" trap above |
| Inline `pixi run python -c "inspect.signature(...)"` produced the right answer → stop after the probe | "The probe answered the question" | The probe records the investigation; the cache file records the conclusion. Ending without the cache write means the next session repeats the probe |
| Skill bundles a reference under `.agents/skills/python-api/references/<topic>.md` → use that as the cache | "Documentation is already there" | Bundled references are *workflow patterns* (cross-version guidance); the cache is *per-version extracts*. Both must exist. Citing a bundled reference for a Shape-1 signature question is not a cache hit |
| Version subfolder doesn't exist yet (`scratch/api/skrub/<version>/` missing) → write into the latest existing subfolder | Avoid creating "yet another folder" | The subfolder is the freshness key; writing under the wrong version pollutes the next agent's cache hit. Create the right subfolder |
| Multiple symbols needed → use one inline `python -c` with several `inspect.signature` calls strung together | "Fewer round-trips" | The 2-line inline cap is contract. Multi-symbol walks go to `scratch/<ts>_<short>.py` per § "Multi-line probes" |
| User pasted the docs URL → treat as the lookup | "User did the discovery for me" | The lookup still requires either `inspect` against the installed version or `WebFetch` of the URL + cache write. Free-text URLs are leads, not conclusions |
| Capture `__doc__` instead of `pydoc.render_doc(sym)` in the probe | "It's the same string" | `__doc__` is the raw class attribute and is empty / misleading on properties, descriptors, decorated callables, and accessors like `report.metrics.rmse`. The cache file is meant to be readable on its own — without the rendered `Examples` block it isn't |

## First action — every turn that invokes this skill

Before any new probe runs, before any WebSearch, before any
symbol is named in code:

1. **Resolve the installed version** of every library at stake
   in this turn: `pixi run python -c "import <pkg>;
   print(<pkg>.__version__)"`. The version is what keys the
   cache; without it the next step can read the wrong subfolder.
2. **List the cache** for each library: `ls
   scratch/api/<lib>/<version>/`. Capture the listing — it
   becomes the Evidence row for the pre-flight below.
3. **Read the topic-matching file**, if any. Cache hit → done;
   skip to writing code with the conclusion from the cache.
4. **Only on cache miss** pick Shape 1 (signature + `help()`
   probe), Shape 2 (module surface), or Shape 3 (narrative
   WebFetch). The chosen shape decides whether a fresh cache
   file is written this turn.

Then emit the pre-flight checklist below as visible text and
proceed.

## Pre-flight — emit this checklist as visible text before any lookup

```
Pre-flight (python-api):
- [ ] Package version resolved this turn: <lib> <version>
      Evidence: tool call `pixi run python -c "import <lib>; print(<lib>.__version__)"`
                output (paste version string)
- [ ] Cache listed this turn (Shape 0): `ls scratch/api/<lib>/<version>/`
      Evidence: tool output (paste the listing, even if empty)
- [ ] Lookup decision: cache hit (Read <file>) | cache miss → Shape 1 probe
      | cache miss → Shape 2 module surface | cache miss → Shape 3 narrative
      Evidence: name the file Read, the probe script written, or the URL fetched
- [ ] Cache file lands on disk before turn end (Shape 1 / Shape 2 / Shape 3 path)
      Evidence: Write scratch/api/<lib>/<version>/<topic>.md (this turn)
                | "n/a — cache hit, file already on disk"
                | "n/a — Shape 1a single-signature inline confirmation
                   against an existing cache file <path>"
- [ ] If Shape 1: the Usage section has Call / Don't call / Trap /
      Returns filled in (not left as TODO).
      Evidence: Edit scratch/api/<lib>/<version>/<topic>.md (this turn)
                | "n/a — cache hit / Shape 2 surface dump / Shape 3 docs extract"
```

The cache-listing row (`ls ...`) is the gate that catches the
"I'll just inspect the symbol from memory" reflex. Skipping it
is a Stop-condition violation, same severity as naming a symbol
from training-data memory.

## Bootstrap API cache — required deliverable

The lookup procedure (Shapes 0–3 below) describes *how* to
discover an API. This section describes *what must end up on
disk* before a bootstrap turn (the first session that scaffolds
an ML workspace) ends. Ending bootstrap without these files is
a Stop-condition violation, on the same footing as scaffolding
without a design note.

### Minimum bootstrap cache files

After the baseline experiment runs successfully (or, equivalently,
once the agent has touched skrub / skore / sklearn symbols enough
to fit and evaluate the baseline), the following cache files
**must exist on disk**:

```
scratch/api/skrub/<version>/tabular_pipeline.md
scratch/api/skrub/<version>/dataops_mark_as_X_y.md
scratch/api/skrub/<version>/var_and_source_binding.md
scratch/api/skore/<version>/evaluate.md
scratch/api/skore/<version>/project_local.md
scratch/api/sklearn/<version>/cv_splitters.md
```

`<version>` is the exact `<pkg>.__version__` resolved this turn
— **not** the latest available release, **not** a hand-typed
version number. The version subfolder is the cache's
freshness key; getting it wrong (e.g. by abbreviating `0.18.0`
to `0.18`) silently bifurcates the cache for the next agent.

### File contract

Every cache file under `scratch/api/<lib>/<version>/` follows
the same four-section shape. Two sections are mechanically
produced by the Shape 1 probe (`Signature`, `help()`); one
records provenance (`Source` header); one is the agent's
synthesis (`Usage`).

```
# <topic>

Source: inspect: <lib>.<dotted> @ <version>  |  <docs URL>
Probed: <YYYY-MM-DD>

## Signature

<one fenced code block with the signature exactly as inspect.signature returned it>

## help() / docs extract

<verbatim pydoc.render_doc output for Shape 1, or a verbatim
 trimmed WebFetch extract for Shape 3. Never paraphrase. If both
 a probe and a docs page are needed, both sections exist —
 `## help()` and `## Docs extract` side by side.>

## Usage (agent synthesis)

- **Call:** import path + arg shape this workspace uses (2-3 line
  snippet drawn from / inspired by the Examples block above).
- **Don't call:** named substitutes that look right from
  training-data memory (e.g. `tabular_learner` for the renamed
  `tabular_pipeline`).
- **Trap:** version-specific rename / deprecation / footgun.
  Empty bullet if no known trap.
- **Returns:** the return type plus the one accessor the next
  caller usually needs (e.g. `CrossValidationReport` →
  `.metrics.rmse()`).
```

The `Source:` header line carries either an `inspect:` reference
for Shape 1 (`inspect: skrub.tabular_pipeline @ 0.9.0`) or a docs
URL for Shape 3, separated by ` | ` if both apply.

### Why this is a deliverable, not a side effect

Inline `pixi run python -c "inspect.signature(...)"` calls and
ad-hoc `scratch/<ts>_*.py` probes record the *investigation*;
they expire from the conversation log and do not carry forward.
The cache file records the *conclusion*; the next agent reads
it and skips the round-trip. A bootstrap turn that fits skrub
+ skore + sklearn into a working baseline without leaving the
cache behind has done the discovery work and thrown it away —
the next session will repeat the same `dir(...)` walks, the
same renamed-symbol surprises, and the same recursion-bug
workarounds. The cache is the only mechanism that bounds that
cost.

**Audit before ending bootstrap.** Before declaring a
bootstrap turn complete, `ls scratch/api/skrub/<version>/
scratch/api/skore/<version>/ scratch/api/sklearn/<version>/`
and verify each minimum file is present. If any is missing,
**surface the gap to the user explicitly in your final
message** and either write the file now or record the
non-compliance in the turn's audit.

### Beyond bootstrap

Iterate-mode turns extend the same contract: any new symbol
*discovered* (Shape 1, 2, or 3) and *used in committed code*
this turn must leave a cache file behind under
`scratch/api/<lib>/<version>/`. Cache hits (Shape 0) do not
need a re-write — the file already exists.

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

### Shape 1 — symbol card (signature + `help()` text → cache file)

One canonical probe-script template that introspects the symbol
and writes the cache file in a single execution. A small
follow-up Edit then fills in the `Usage` bullets. The two-step
loop (mechanical write → human synthesis) is what makes Shape 1
robust: even if the agent forgets the second step, the cache file
exists with signature + `help()` text and the next session has
something to read.

Probe template — copy, edit `LIB` / `DOTTED` / `TOPIC`, save as
`scratch/<YYYY-MM-DD>_<HHMMSS>_lookup_<lib>_<topic>.py`, and run:

```python
"""Lookup: <lib>.<dotted> @ installed version."""
from __future__ import annotations

import datetime
import importlib
import inspect
import io
import pydoc
from pathlib import Path

LIB = "skore"          # top-level package name
DOTTED = "evaluate"    # dotted path under the package; e.g. "Project.put"
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

Run with `pixi run python scratch/<ts>_lookup_<lib>_<topic>.py`.
The cache file lands at
`scratch/api/<lib>/<version>/<topic>.md`. The four-section
contract for that file is defined in § "Bootstrap API cache" →
"File contract".

**Step 2 — fill in `Usage`.** Open the just-written cache file
and replace each `TODO` with a one-line synthesis: the import
path + arg shape this workspace will call (lean on the Examples
block in the `help()` output for a starting snippet); the named
substitutes the agent should not reach for from training-data
memory; any version-specific rename / deprecation / footgun; the
return type plus the next-step accessor. This is the only part
`inspect` and `pydoc.render_doc` cannot produce mechanically.

**Python-version compatibility.**
`pydoc.render_doc(sym, renderer=pydoc.plaintext)` works on
Python 3.10+. (`pydoc.plaintext` is a module-level instance of
`pydoc._PlainTextDoc` — pass it as the renderer, do not call
it.) The builtin `help(...)` cannot be captured into a
StringIO via `output=` — `pydoc.help.output` is a read-only
property on 3.10+, confirmed on Python 3.14 in this workspace.

**Shape 1a — inline single-signature check (not cached).** When
you already have a cache hit and just need to re-confirm one arg
name at the call site, an inline ≤2-line `pixi run python -c
"import inspect; from <pkg> import <Sym>; print(inspect.signature(<Sym>))"`
is permitted. This is the only Shape 1 form that does not produce
a cache file, because the cache file already exists. Any other
Shape 1 usage runs the probe template above.

**Multi-symbol consolidation.** When two or more closely related
symbols share the same topic (e.g. `Project.put` /
`Project.get` / `Project.summarize` all under `project_local`),
extend the probe template to iterate over a tuple of dotted
paths and concatenate their Signature + help() sections under
the same `<topic>.md`. One topic file per *topic*, not per
symbol.

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
   (`cross_validation.md`, `data_ops.md`, `tabular_pipeline.md`).
   One topic per file. Replace only on a version bump.

The cache file is what every subsequent turn reads. WebFetch
is the *generator* of cache files; Shape 0 is the *reader*.

## The `scratch/api/` cache — layout and lifecycle

```
scratch/api/
├── skrub/
│   └── 0.9.0/
│       ├── data_ops.md          # narrative cached via Shape 3
│       ├── tabular_pipeline.md
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

- **Top-level helpers**: `tabular_pipeline`, `TableVectorizer`,
  `DatetimeEncoder`, `TextEncoder`, `StringEncoder`. Use these
  for tabular learners that pick reasonable defaults per column
  type.
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

Example Shape 1 probe — single symbol, signature +
`pydoc.render_doc`, writes the cache file in one execution
(stored as `scratch/<ts>_lookup_skrub_var.py`):

```python
"""Lookup: skrub.var @ installed version."""
from __future__ import annotations

import datetime
import importlib
import inspect
import io
import pydoc
from pathlib import Path

LIB = "skrub"
DOTTED = "var"
TOPIC = "var_and_source_binding"

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

Run with `pixi run python scratch/<ts>_lookup_skrub_var.py`,
then Edit
`scratch/api/skrub/<version>/var_and_source_binding.md` to
replace the four `TODO` lines with the synthesis bullets.

**Multi-symbol consolidation variant.** When several symbols
share a topic (e.g. `Project.put` / `Project.get` /
`Project.summarize` all belong under
`project_local`), iterate over a tuple of dotted paths inside
the probe and concatenate their Signature + help() sections
into one `<topic>.md`. One topic file per *topic*, not per
symbol. The `Usage` section at the bottom still has a single
`Call` / `Don't call` / `Trap` / `Returns` block — the synthesis
captures how the symbols compose, not each one in isolation.

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
`.agents/skills/python-api/references/<topic>.md`.

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
