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

1. **Lookup against the installed version, never memory.**
   Recognition is not a lookup. The version may have renamed /
   re-signatured / deprecated the symbol you remember.
2. **Cache to `scratch/api/<lib>/<version>/<topic>.md`** so the
   next agent doesn't repeat the probe.
3. **Bundled `references/` ≠ workspace cache.** Bundled refs are
   durable workflow patterns; cache files are per-version extracts.

## Next-step pointers

| Came here for… | After lookup, next is… |
|---|---|
| Symbol signature for code about to be written | → continue caller's flow (e.g. `build-ml-pipeline` § next step) |
| "Which library / which entry?" | → continue with the picked symbol; cache lands |
| Bootstrap turn (first workspace) | → required minimum cache lands; see `references/bootstrap_cache.md` |
| Failure debugging (KeyError / AttributeError) | → see Stop condition "Lookup failure ≠ artifact missing" |

## What kind of question? → Shape

Pick the shape **by question type** before picking a tool. Wrong
shape produces a wrong-looking cache file and burns a turn.

| The user's question is shaped like… | Shape |
|---|---|
| "What's in `scratch/api/<lib>/<version>/`?" (always check first) | **0** cache hit |
| "Which entry point for &lt;task&gt;?" | **Stack orientation** below, then Shape 1 / 1b to confirm |
| "What's the signature of X?" / "What args does X take?" / "What's the return type?" | **1b** LSP hover (fast) → fall through to **1** if hover is sparse |
| "What does X do?" / "Full docstring of X?" (need Parameters / Examples / See Also) | **1** symbol card (pydoc) |
| "What's in module Y?" (open-ended discovery) | **2** module surface |
| "Search for symbols matching `foo*` across the env" | **2b** LSP workspace symbol |
| "How does X work?" / "Which of A or B should I use?" | **3** narrative |
| **"What does X return when `<arg>` is `<value>`?"** | **3** narrative |
| "What's the recommended pattern for …?" | **3** narrative |

**Shape 3 is the right answer when the question depends on a
*condition* over an argument.** `help()` carries a `Returns`
section but typically does not enumerate dispatch behaviour under
each argument value — that lives in narrative docs.

**Shape 1b vs Shape 1.** Pyright hover gives the type signature
(richer inferred return types than `inspect.signature`) + the first
paragraph of the docstring — fast, no Python execution. Pydoc gives
the **full** docstring with all sections — slower but authoritative.
Default escalation: 1b first for "what's the signature"; fall
through to 1 if hover is empty / one-liner.

**Prerequisites for Shape 1b / 2b (LSP shapes).** Pyright available
via opencode LSP AND `pyrightconfig.json` pointing at the `lsp` env.
If either is missing, LSP shapes are unavailable — use Shape 1 / 2
directly. The `agent feature: installed` row in `JOURNAL.md`
Status `Workspace decisions` is the precondition; see
`python-env-manager` § Agent feature.

## Stop conditions — read before any lookup

- **No symbols from memory.** Every function / class / method / arg
  must come from a lookup *this turn* — `inspect.signature`, a
  `scratch/api/<lib>/<version>/` file, or a fresh WebFetch.
  Recognition does not count. Sticky named cases — full list in
  `references/named_traps.md`:
  - skrub: `tabular_learner` → `tabular_pipeline` in 0.7+.
  - skrub: `mark_as_y(target_column)` → signature dropped the
    positional arg in 0.9+; use `.skb.select("...")` before mark.
  - skore: `Project.get(...)` is by **id**, not user-facing `key`;
    enumerate via `project.summarize()` first.
- **Never fabricate a probe result.** If the probe hasn't executed,
  the `Signature` / `help()` sections must remain blank or marked
  `<pending probe execution>`. Same rule for Shape 3: do not
  paraphrase docs from memory; cache file holds verbatim extracts.
- **Version-correct first.** Resolve `<pkg>.__version__` before any
  lookup. The version subfolder is the cache freshness key.
- **Cache hit before fresh fetch.** List
  `scratch/api/<lib>/<version>/` before Shape 1 / 2 / 3.
- **Lookup failure ≠ artifact missing.** A `KeyError` /
  `AttributeError` on a registry-style API (`project.get(key)`,
  `getattr(obj, name)`, `dict[key]`) is almost always the **lookup
  shape** (id vs key, wrong accessor) — not a missing artifact.
  Named instance: `skore.Project.get(...)` resolves by **id**, not
  by user-facing `key`; `project.summarize()` enumerates
  `(key, id)` pairs. **Never substitute by re-creating the
  artifact** — that lands a duplicate row.
- **All Python execution goes to
  `scratch/<YYYY-MM-DD>_<HHMMSS>_<short>.py`. No exceptions.**
  Every Python command — `pixi run python -c`, `python -c`,
  heredoc-style `python << 'EOF'`, or any inline Python — is
  forbidden, regardless of length. Write to scratch first, then
  execute via `pixi run python scratch/<ts>_<short>.py`. Applies
  to version checks, import smokes, signature lookups, module
  surface dumps, docstring extraction, anything. If you catch
  yourself typing `python -c` — STOP and write the file.
- **`inspect.signature` / `dir(...)` / `pydoc.render_doc` /
  `help(...)` executed inline is NOT a python-api consultation.**
  These are the exact APIs this skill wraps. Running them via
  `python -c` does NOT satisfy the "python-api consulted"
  pre-flight row in sibling skills. The deliverable is a
  `scratch/api/<lib>/<version>/<topic>.md` file written this turn.
- **`pydoc.render_doc`, not `__doc__`.** `__doc__` is empty /
  misleading on properties, descriptors, decorated callables, and
  accessors — exactly the cases the cache disambiguates.
- **Narrative findings get cached.** A WebFetch result read and
  discarded is forbidden. Land it in
  `scratch/api/<lib>/<version>/<topic>.md` with the source URL on
  the first line.
- **A probe without a cache write is not a completed lookup.**
  Probe records the *investigation*; cache file records the
  *conclusion*. Turn end without
  `scratch/api/<lib>/<version>/<topic>.md` on disk = incomplete.

## Forbidden shortcuts

| Shortcut | Why it's wrong |
|---|---|
| Recognise the symbol name from training data → write the call | Memory keyed to arbitrary version; install may have renamed / re-signatured |
| Probe ran, answer on screen → stop without writing the cache | Probe is investigation; cache is conclusion. Next session repeats the probe |
| Bundled `references/X.md` exists → treat as the cache | References are workflow patterns; cache is per-version extracts. Both must exist |
| Version subfolder missing → write into the latest existing one | Subfolder is the freshness key. Create the right one |
| Multi-symbol → string several `inspect.signature` into one inline `python -c` | All Python execution goes to scratch — no inline `-c` allowance. Multi-symbol → one scratch file → one consolidated cache file |
| Used `python -c "import <pkg>; print(<pkg>.__version__)"` for a quick version check | Rule is unconditional. Length is not the criterion — traceability is. Version checks go to `scratch/<ts>_version_<pkg>.py` |
| Cache exists for the topic; ran inline `inspect.signature(X)` to re-confirm one arg name | No inline single-signature carve-out exists. Every Shape 1 lookup uses the probe template |
| Used `python -c "...inspect.signature..."` instead of writing the Shape 1 probe | Probe records the investigation; cache records the conclusion. Next session needs the file, not your transcript |
| User pasted a docs URL → treat as the answer | Lookup still requires `inspect` or `WebFetch` + cache write. URLs are leads |
| Use `__doc__` instead of `pydoc.render_doc` | `__doc__` is empty on many accessors; cache file must be readable standalone |

## First action — every turn that triggers this skill

1. **Resolve the version.** Write
   `scratch/<YYYY-MM-DD>_<HHMMSS>_version_<pkg>.py` with
   `import <pkg>; print(<pkg>.__version__)`, run via
   `pixi run python scratch/<ts>_version_<pkg>.py`. **No inline
   `python -c`.**
2. **List the cache:** `ls scratch/api/<lib>/<version>/`.
3. **Cache hit?** Read the matching file. Done.
4. **Cache miss?** Classify the question (table above) → run Shape
   1 / 1b / 2 / 2b / 3.
5. **Emit the pre-flight checklist** with each box marked.

## Pre-flight — emit before any lookup

```
Pre-flight (python-api):
- [ ] Package version resolved this turn: <lib> <version>
      Evidence: Write scratch/<ts>_version_<lib>.py (this turn) +
                `pixi run python scratch/<ts>_version_<lib>.py` output.
                **Inline `python -c "..."` is NOT evidence.**
- [ ] Cache listed this turn (Shape 0): `ls scratch/api/<lib>/<version>/`
      Evidence: tool output (paste the listing, even if empty)
- [ ] Question shape classified: signature | module surface | narrative
      Evidence: name the shape + one phrase from the question
- [ ] Lookup decision: cache hit (Read <file>) | Shape 1 | 1b | 2 | 2b | 3
      Evidence: name the file Read, probe script written, LSP
                operation requested, or URL fetched
- [ ] (Shape 1b / 2b only) LSP preconditions confirmed:
      `agent feature: installed` in JOURNAL.md AND
      `pyrightconfig.json` at project root pointing at the `lsp` env
      Evidence: Read journal/JOURNAL.md + Read pyrightconfig.json
                (this turn) | "n/a — not an LSP shape"
- [ ] Cache file lands on disk before turn end
      Evidence: Write scratch/api/<lib>/<version>/<topic>.md (this turn)
                | "n/a — cache hit, already on disk + Read this turn"
                | "n/a — Shape 2b ad-hoc discovery"
      **Inline `inspect.signature(...)` / `dir(...)` / `pydoc.render_doc(...)`
      WITHOUT a corresponding cache file is NOT evidence. Re-do as Shape 1.**
- [ ] If Shape 1 / 1b: Usage section filled in (Call / Don't call / Trap / Returns)
      Evidence: Edit scratch/api/<lib>/<version>/<topic>.md (this turn)
                | "n/a — cache hit / Shape 2 / 2b / 3"
- [ ] Pre-flight re-emitted with evidence before final message.
      Evidence: this checklist appears in the end-of-turn summary.
```

## The four shapes

### Shape 0 — cache hit

```bash
ls scratch/api/<lib>/<version>/ 2>/dev/null
```

Topic-matching file present → `Read` it. First line carries the
source URL or `inspect:` ref; re-verify against live docs if a file
looks suspicious. Cache miss → Shape 1 / 2 / 3.

### Shape 1 — symbol card (pydoc → cache file)

One probe script does both: introspects the symbol AND writes the
cache file in a single execution. Small follow-up `Edit` fills the
`Usage` bullets (Call / Don't call / Trap / Returns).

Probe template: → `references/probe_templates.md` § Shape 1.

**Multi-symbol consolidation.** Several symbols sharing a topic
(e.g. `Project.put` / `Project.get` / `Project.summarize` under
`project_local`) → iterate over a tuple of dotted paths inside the
probe and concatenate sections into one `<topic>.md`. **One topic
file per *topic*, not per symbol.**

**No inline carve-out for single-signature checks.** Even when a
cache exists and you want to re-confirm one arg, run a fresh probe
(or Read the existing cache).

### Shape 1b — LSP hover (no Python execution)

Pyright via the opencode LSP returns hover info (type signature +
first paragraph of docstring) for a symbol at a `file:line:character`
position. **First stop for "what's the signature" questions** when
Shape 1b is known available this session (see Step 0 below); fall
through to Shape 1 otherwise, or when the hover output is sparse.

#### Step 0 — probe LSP availability (mandatory, once per session)

The opencode LSP server reads `pyrightconfig.json` once at session
startup. Mid-session edits do NOT reload. If the LSP returns
`(import) <name>: Unknown` for every external library, the config
was written after the LSP initialized — Shape 1b is unavailable
this session. **Sticky decision**: use Shape 1 for ALL signature
questions until next opencode session.

Probe procedure + interpretation table + every footgun
(session-startup ordering, conda-style envs, character offset,
scratch-excluded paths, C-extension types):
→ `references/shape1b_lsp_setup.md`.

#### After availability is confirmed

1. Write a probe file (under `tests/` or `src/<pkg>/` — `scratch/`
   is excluded from pyright's analysis). Template:
   → `references/probe_templates.md` § Shape 1b.
2. Call `lsp(operation="hover", filePath=..., line=..., character=...)`.
3. Cache the result at
   `scratch/api/<lib>/<version>/<topic>.md` with `Source:
   lsp-hover: <lib>.<dotted> @ <version>` and a `## LSP hover`
   section.
4. Escalate to Shape 1 if hover is empty / one-liner.

### Shape 2 — module surface

Scratch probe that dumps both top-level surface and submodule list,
then writes `surface.md` directly. No inline `python -c`.

Probe template: → `references/probe_templates.md` § Shape 2.

One topic per file. Replace only on a version bump.

### Shape 2b — LSP workspace symbol (cross-package search)

Given a query string, return all matching symbols across the `lsp`
env's site-packages. Use for discovery before committing to a
dotted path; faster than `dir()` on every candidate module.

```
lsp(
    operation="workspaceSymbol",
    filePath="<any-existing-Python-file>",
    line=1, character=1,
    query="<symbol substring>",
)
```

(`filePath`/`line`/`character` are ignored by pyright for
`workspaceSymbol`; only used to select the LSP server.)

Return: list of `(name, kind, location)` tuples. NOT a Shape-2
replacement (doesn't enumerate a full module surface). Use as a
**discovery aid** before running Shape 1 / Shape 2 on the right
dotted path. Cache only if the search becomes recurring.

### Shape 3 — narrative

Conceptual questions where the signature alone doesn't answer it —
"how does X work?", "which of A/B should I use?", "what does X
return when `<arg>` is `<value>`?". Procedure:

1. **WebSearch** for the versioned docs URL. Query:
   `<library> <MAJOR.MINOR> docs <topic>`. Don't construct URLs
   from memory.
2. **WebFetch** the most relevant result whose URL contains the
   installed version (`/0.18/`, `/0.18.0/`). **Reject** any URL
   with `/latest/` or `/stable/` — those drift on republish.
3. **Cache verbatim** to `scratch/api/<lib>/<version>/<topic>.md`:

   ```markdown
   # <topic>

   Source: <full URL>
   Fetched: <YYYY-MM-DD>

   <paste salient sections verbatim — do NOT paraphrase from
   memory. Skip nav chrome; keep prose that answers the question.>
   ```

Cache filename: snake_case mirror of the docs URL slug. One topic
per file. Replace only on version bump.

## Cache file contract

Every `scratch/api/<lib>/<version>/<topic>.md` follows a four-section
shape:

```
# <topic>

Source: inspect: <lib>.<dotted> @ <version>  |  <docs URL>
Probed: <YYYY-MM-DD>

## Signature
<fenced block — exactly as inspect.signature returned it, Shape 1 only>

## help()  (or "## Docs extract" for Shape 3, "## LSP hover" for 1b)
<verbatim pydoc.render_doc / WebFetch extract / hover output.
 Never paraphrase.>

## Usage (agent synthesis)
- **Call:** import path + arg shape (2-3 line snippet)
- **Don't call:** named substitutes that look right from memory
- **Trap:** version-specific rename / deprecation / footgun (empty if none)
- **Returns:** return type + the one accessor the next caller needs
```

Bootstrap turns have a **required minimum cache** to leave behind —
file list + audit procedure: → `references/bootstrap_cache.md`.

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

- **Version subfolder == `<pkg>.__version__` exactly.** No
  abbreviation (`0.18.0` ≠ `0.18`).
- **First line is the source URL or `inspect:` ref.**
- **Gitignored** by the existing `scratch/*` rule. Regenerable.
- **Append-on-success.** Once written, frozen. Replace only on
  version bump (the version-subfolder convention handles this).
- **Cache miss in a stale subfolder is impossible by construction.**
  Shape 0 reads by version; old subfolder content is invisible.

## `scratch/` conventions — probes vs. cache

Two structured uses of `scratch/`, both gitignored:

| | Ad-hoc probes | API doc cache |
|---|---|---|
| **Path** | `scratch/<YYYY-MM-DD>_<HHMMSS>_<short>.py` | `scratch/api/<lib>/<version>/<topic>.md` |
| **What** | Multi-line `inspect` walks, sanity checks, metric extraction | Signature / help() / docs extract per topic |
| **Naming** | Timestamped (chronological) | Topic-organised |
| **Lifecycle** | Append-only after success; overwrite on error in same loop | Append-on-success; replace on version bump |
| **Inline cap** | **No inline `python -c`. All execution goes to scratch** | n/a (probes write the cache) |

**Never edit an experiment script to add agent-only `print(...)`
calls for inspection.** Inspection goes in `scratch/`.

**Never re-run an experiment / `project.put` from a scratch probe.**
Scratch is read-only against the skore Project (use
`project.summarize()` then `project.get(id)`).

**Read-only rule extends to `audit/`.** The audit flow places one
`# %%` file per experiment under `audit/<NN>_<short_name>.py` and
executes it via the bundled runner. Same `summarize()` → `get(id)`
→ `report.*` discipline. Executed digests land in
`scratch/audit/<stem>/` (gitignored). Two artifacts, two
lifecycles:

| | API doc cache | Audit executed digest |
|---|---|---|
| **Owner** | `python-api` | `audit-ml-pipeline` |
| **Source** | `inspect.signature` / `pydoc.render_doc` / WebFetch | Executing `audit/<stem>.py` |
| **Lifecycle** | Append-on-success; replace on version bump | Overwritten on every audit re-execution |
| **Read by** | Any skill needing a symbol's signature/contract | The agent during `iterate-ml-experiment` § 4 narrative work |

The workspace's `scratch/` folder does **not** carry a `README.md`
— rules of this importance live in the skill that's loaded at
use-time.

## Stack orientation — where things live

Tier-1 named entry points. Consult **before** a Shape 2 surface
dump for "where does X live" — the named entry is often the right
answer.

### scikit-learn

- `sklearn.metrics` — scoring (`accuracy_score`, `roc_auc_score`,
  `mean_absolute_error`, `make_scorer`).
- `sklearn.preprocessing` — stateful scalers / encoders / imputers
  (`StandardScaler`, `OneHotEncoder`, `KBinsDiscretizer`).
- `sklearn.pipeline` / `sklearn.compose` — `Pipeline`,
  `make_pipeline`, `ColumnTransformer`.
- `sklearn.model_selection` — splitters (`KFold`, `GroupKFold`,
  `TimeSeriesSplit`, `train_test_split`) + search (`GridSearchCV`).
- Estimators: `sklearn.linear_model` / `sklearn.ensemble` / etc.

### skrub

- **One-call featuriser / learner**: `skrub.tabular_pipeline`
  (top-level function — **not** `tabular_learner`, **not**
  `TabularLearner`; renamed in 0.7+).
- **Per-column encoders** (top-level): `TableVectorizer`,
  `DatetimeEncoder`, `TextEncoder`, `StringEncoder`.
- **DataOps DSL** (lazy pipeline graph): the `.skb` namespace on
  every node — `X.skb.apply`, `X.skb.apply_func`,
  `X.skb.mark_as_X`, `X.skb.mark_as_y`, `X.skb.make_learner`,
  `.skb.preview`, `.skb.full_report`.
- **Sources / variables**: `skrub.var(name, value=...)`,
  `skrub.as_data_op({...})`.
- **Selectors**: `skrub.selectors.{numeric, categorical, string,
  ...}`.

### skore

- **Evaluation**: `skore.evaluate(estimator, X=None, y=None,
  data=None, *, splitter=None, ...)` — dispatches by `splitter` to
  `EstimatorReport` (no splitter) / `CrossValidationReport` (CV
  splitter) / `ComparisonReport` (multi-key).
- **Project**: `skore.Project(name, *, mode="local", **kwargs)`
  (per-mode kwargs: `workspace=` for local dir / hub workspace name,
  `tracking_uri=` for mlflow) with `put(key, report)` /
  `summarize()` (DataFrame indexed by id with `key` column, rows
  ascending by `date`) / `get(id)` — **`get` is by id, not by
  `key`** — and static `Project.delete(name, *, mode, **kwargs)`.

Full per-library surface map (rare submodules, accessor cheat sheet):
→ `references/stack_orientation.md`.

## When the installed package is wrong

Two options, neither involves "writing from memory of a different
version":

1. Route to `python-env-manager` § "Upgrade / pin" to bump or pin.
   Re-do the lookup against the new install.
2. Adapt to what's installed — change the approach.

## Companion skills

| Skill | Relationship |
|---|---|
| `python-env-manager` | Owns versions (the version it resolves keys `scratch/api/<lib>/<version>/`) |
| `data-science-python-stack` | Owns *which* library; this skill takes the library as given |
| `build-ml-pipeline` / `evaluate-ml-pipeline` / `iterate-from-skore` / `smoke-test-ml-pipeline` | Workflow skills that dispatch here when they need a symbol |

## What this skill does NOT do

- Maintain pre-baked signature listings *in the skill folder*.
  Per-version extracts live in the workspace cache; the skill
  folder carries durable workflow patterns.
- Generate cache files on install. Caching is on-demand.
- Explain a library's API at depth — that's the library's own
  docs. This skill points at them and caches what's worth keeping.
- Auto-author references. New `references/<topic>.md` files are
  user-gated via `AskUserQuestion` (see
  `references/authoring_protocol.md`).

## References (load on demand)

Durable workflow patterns (bundled with the skill):

- `references/probe_templates.md` — full code for Shape 1 (pydoc
  symbol card), Shape 1b (LSP hover probe file), Shape 2 (module
  surface dump). Copy + edit `LIB` / `DOTTED` / `TOPIC`.
- `references/shape1b_lsp_setup.md` — Step 0 availability probe,
  interpretation table, footguns (session-startup ordering,
  conda-style envs, character offset, scratch-excluded paths,
  C-extension types).
- `references/stack_orientation.md` — full per-library surface
  map (sklearn / skrub / skore).
- `references/pre_mark_alignment.md` — 3-layer skrub DataOps
  pattern for history-dependent pipelines. Read before authoring
  history-dep code.
- `references/skrub_interop.md` — how `SkrubLearner` integrates
  with `skore.evaluate`. Read before writing
  `experiments/NN_*.py`.
- `references/bootstrap_cache.md` — required minimum cache files
  for a bootstrap turn + audit procedure.
- `references/named_traps.md` — version-specific renames /
  deprecations the agent has hit in real traces.
- `references/authoring_protocol.md` — when and how to land a new
  reference doc (user-gated via `AskUserQuestion`).
