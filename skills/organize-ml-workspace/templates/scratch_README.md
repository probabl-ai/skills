# scratch/

Agent scratch space. Used by the iteration agent for ad-hoc Python the user
doesn't need to maintain — inspecting a persisted skore report, walking
`report.diagnosis()` to fill a Status block, extracting a metric for a
design note. The folder exists for **traceability**: every probe lands as
a file
on disk, not as an inline `pixi run python -c "..."` lost to the
conversation log.

## Convention

Two structured uses of this folder; both are gitignored except this README.

### Ad-hoc probes — `scratch/<YYYY-MM-DD>_<HHMMSS>_<short-name>.py`

- **One file per probe.** Example:
  `scratch/2026-05-14_143012_extract_02_metrics.py`.
- **Timestamped** so files sort chronologically and the user can see what
  was probed when.
- **Append-only after success**: once a scratch script has executed
  cleanly, the file is frozen. Re-probes start a new file (new
  timestamp).
- **Overwrite-on-error within the same loop is OK**: if a script errors
  out (typo, wrong API), the agent edits the same file and re-runs
  until it succeeds — only the working version is kept.

### API doc cache — `scratch/api/<lib>/<version>/<topic>.md`

Owned by the `python-api` skill. Per-library, per-version cache of
extracts from official docs and `dir()` dumps so the next agent
doesn't re-WebFetch the same page.

- **Version subfolder == `<pkg>.__version__` exactly** (e.g.
  `scratch/api/skrub/0.9.0/`, `scratch/api/skore/0.18.0/`).
- **Topic file** mirrors the docs URL slug, snake_cased
  (`data_ops.md`, `cross_validation.md`, `tabular_pipeline.md`).
  One topic per file.
- **First line is the source URL** the content came from.
  Future agents can re-verify against the live docs.
- **Append-on-success**, same as ad-hoc probes. Replace only on a
  version bump (the version-subfolder convention handles this for
  free — a new version's lookups land in a new subfolder; the old
  one is invisible to them).
- **Not timestamped** — topic-organized, not chronological. This
  is the one structured exception inside `scratch/`.

See `python-api` § "The lookup procedure — four shapes" for when
to read vs. cache.

## When the agent uses it

- **Yes** — multi-line Python that isn't a reusable artifact: inspect a
  skore report, sanity-check a dataframe shape, walk a diagnosis, pull
  metrics for a Status block.
- **No** — reusable code (experiment / smoke test) goes to its proper
  folder.
- **No** — re-fitting / re-evaluating / `project.put`-ing from scratch.
  `experiments/NN_*.py` is the **sole producer** of reports in the
  workspace's skore Project; scratch only inspects existing ones via
  `project.summarize()` (enumerate `(key, id)` pairs) and
  `project.get(id)` (retrieve by id). The trap: `project.get(key)`
  raising `KeyError` looks like "the report is missing" but actually
  means "the lookup shape is wrong — `get` is by id, not by `key`".
  Never substitute by calling `skore.evaluate(...)` + `project.put(...)`
  from a scratch probe — that writes a duplicate row under the same
  `key` into `project.summarize()` and breaks the cross-experiment
  metrics view. See `organize-ml-workspace` § Stop conditions
  ("Scratch is read-only against the skore Project") and
  `evaluate-ml-pipeline` § Stop conditions
  ("`skore.evaluate(...)` and `project.put(...)` live only in
  `experiments/NN_*.py`") for the full rule.
- **Special case**: the data-extraction probe behind `overview/summary.md`
  lives here as `scratch/<ts>_refresh_summary.py` (per
  `iterate-ml-experiment` § 4). The probe is one-shot scratch; the
  curated `summary.md` is what's durable.
- **Inline `pixi run python -c "..."` is reserved for ≤ 2 lines.** Any
  longer → a scratch file.

## Git policy

Contents of this folder are **gitignored** (see project-root `.gitignore`);
only this README is tracked. Scratch lives locally; a fresh clone gets the
folder but not the history of probes. If you want to keep a specific
script, copy it out (e.g. to `experiments/` or `overview/` if it's worth
making reusable, or to a notes file you maintain).

## Why not just `print(...)` in the experiment script?

Experiment scripts (`experiments/NN_*.py`) are the durable record of *what
was run*. Adding agent-only debug prints (`print(report)`,
`print('checking ...')`) pollutes them with content that means nothing
once the run is recorded. Keep experiment scripts clean of agent-only
prints; use `scratch/` instead.
