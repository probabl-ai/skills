# Bootstrap API cache — required deliverable

The lookup procedure (Shapes 0–3 in `SKILL.md`) describes *how* to
discover an API. This reference describes *what must end up on disk*
before a **bootstrap turn** (the first session that scaffolds an ML
workspace) ends.

Ending bootstrap without these files is a Stop-condition violation,
on the same footing as scaffolding without a design note.

## Minimum bootstrap cache files

After the baseline experiment runs successfully — or once the agent
has touched skrub / skore / sklearn symbols enough to fit and
evaluate the baseline — the following cache files **must exist**:

```
scratch/api/skrub/<version>/tabular_pipeline.md
scratch/api/skrub/<version>/dataops_mark_as_X_y.md
scratch/api/skrub/<version>/var_and_source_binding.md
scratch/api/skore/<version>/evaluate.md
scratch/api/skore/<version>/project_local.md
scratch/api/sklearn/<version>/cv_splitters.md
```

`<version>` is the exact `<pkg>.__version__` resolved this turn —
**not** the latest available release, **not** a hand-typed version
number. The version subfolder is the cache's freshness key;
abbreviating (`0.18.0` → `0.18`) silently bifurcates the cache.

## Why these files, why now

Inline `pixi run python -c "inspect.signature(...)"` calls and
ad-hoc `scratch/<ts>_*.py` probes record the *investigation*; they
expire from the conversation log and do not carry forward. The
cache file records the *conclusion*; the next agent reads it and
skips the round-trip.

A bootstrap turn that fits skrub + skore + sklearn into a working
baseline without leaving the cache behind has done the discovery
work and thrown it away. The next session repeats every `dir(...)`
walk, every renamed-symbol surprise, every recursion-bug workaround.
The cache is the only mechanism that bounds that cost.

## Audit before declaring bootstrap complete

```bash
ls scratch/api/skrub/<version>/ \
   scratch/api/skore/<version>/ \
   scratch/api/sklearn/<version>/
```

Verify each minimum file is present. If any is missing, **surface
the gap to the user explicitly** and either write the file now or
record the non-compliance in the turn's audit.

## Beyond bootstrap

Iterate-mode turns extend the same contract: any new symbol
*discovered* (Shape 1, 2, or 3) and *used in committed code* this
turn must leave a cache file behind under
`scratch/api/<lib>/<version>/`. Cache hits (Shape 0) do not need a
re-write — the file already exists.
