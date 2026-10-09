# Audit ML Pipeline — Cell anatomy

Full anatomy of an audit-file cell: concrete right/wrong examples,
the core template sequence, and why a bare Display is the right
last expression. Cross-referenced from SKILL.md § "Audit file
contract — overview".

The template core is task-agnostic: persisted-report locator +
checks summary + metrics summary. `help()` trees are not a
notebook cell. `templates/materialize.py`, copied to
`scratch/audit/<stem>/materialize.py`, writes them to
`accessors.txt`. The rendered digest at
`scratch/audit/<stem>/audit.md` is what `review-ml-experiment`
reads — only `## Checks summary` and `## Metrics summary`. Do
not name extra Display headings like those two. Per-task
accessors are appended after the user picks Additional report
view from names in `accessors.txt`.

Markdown cells in `templates/audit.py` name the experiment and
interpret **this** report. Hub vs local id mapping, `put()` URL
plural→singular, `summarize(ignore=…)`, version floors, and
`help()`-as-menu recipes stay in this file and SKILL.md — never in
the audit notebook comments.

## Concrete cell examples — right vs wrong

A well-formed audit cell ends with a **bare expression**. A
malformed one wraps in `print()` or stores the value in a variable
that's never displayed.

### Right shapes

```python
# %% Right — bare expression auto-displays its repr
summary = project.summarize()
summary
```

```python
# %% Right — multiple statements, bare expression at the end
report = project.get(REPORT_ID)
report
```

```python
# %% Right — statement-only is fine (no output expected)
REPORT_ID = "skore:report:cross-validation:42"
```

### Wrong shapes

```python
# %% WRONG — print() loses rich repr; clutters the human-reading view
report = project.get(REPORT_ID)
print(repr(report))  # ← drop the print, leave `report` as bare expr
```

```python
# %% WRONG — value computed but not displayed; cell shows no output
report = project.get(REPORT_ID)
metrics = report.metrics  # ← add `metrics` on its own line at the end
```

```python
# %% WRONG — never call evaluate or put from an audit file
report = skore.evaluate(learner, ...)        # ← read-only contract violated
project.put("01_baseline", report)           # ← duplicates the row; pollutes summarize()
```

### Cell-execution semantics (notebook-style)

- The **last expression** of a code cell is auto-displayed if it's
  a bare expression (no assignment, no statement keyword, no
  `print`).
- Rich `_repr_html_` is preferred over `__repr__` when both exist
  in JupyterLab / VS Code. **The runner does NOT request
  `_repr_html_`** — it captures `repr(result.result)` only. skore
  Displays define both, so one bare Display line serves the editor
  and the digest at once.
- Assignment-only / statement-only cells produce **no output and
  no error** — they execute silently. This is the right shape for
  setup cells (imports, `REPORT_ID = …`, etc.).

## The core template sequence

The template ships with this cell sequence. Core cells are
task-agnostic. Leave them as-is; append Display cells only after
the user picks a name from `accessors.txt`. Snapshot writes stay
in `materialize.py`.

1. **Module-level docstring (markdown cell).** What this file is,
   the read-only rule, where the digest lands. Verbatim from the
   template.

2. **Imports (code cell).** `import skore` and
   `from <pkg> import PROJECT_ROOT`. No statement-only branching
   here.

3. **Open the Project (code cell, bare expression at the end).**
   ```python
   project = skore.Project(...)
   project
   ```
   The cell's output is the Project's repr — useful for confirming
   the right project, the right workspace, the right mode.

4. **List the available reports (code cell, bare expression).**
   ```python
   summary = project.summarize()
   summary
   ```
   The cell's output is the cross-experiment table.

5. **Load the report (code cell, bare expression).**

   Set `REPORT_ID` to the id of this experiment's report, then load
   it. The id comes from different sources per skore mode:

   - **Hub mode**: `project.put()` prints the exact frontend URL.
     Preserve it as the report locator. The id is
     `skore:report:<type-singular>:<N>` — the URL path segment is
     plural; the id uses the singular. Examples:
     `cross-validations/42` →
     `skore:report:cross-validation:42`; `estimators/7` →
     `skore:report:estimator:7`. Copy `<N>` and `<type-singular>` from
     the put() stdout; hardcode as `REPORT_ID`; no `summarize()` needed.
   - **Local mode**: `summarize()` last-expression is a Display.
     Bind `frame = summary.frame()`, then
     `frame.loc[frame["key"] == "<NN>_<short_name>", "id"].iloc[0]`.
     Do not treat the Display as a dict (`summary["id"]`). Keep
     `summary` as the cell's last expression.
   - **MLflow mode**: same as local — read `"id"` from
     `summary.frame()`, filtering to the newest row where
     `key == "<NN>_<short_name>"`. Preserve an emitted MLflow run URL
     when available; otherwise use the tracking URI + experiment id
     + run id locator contract.

   ```python
   REPORT_ID = "skore:report:<type-singular>:<N>"  # hub: from put() URL

   report = project.get(REPORT_ID)
   report
   ```
   Do not write `report.html` or `locator.txt` in this cell.
   `materialize.py` writes both (a direct audit has no evaluate
   snapshot yet). Confirm `_repr_html_` with `api get`. The HTML
   is for the site Results viewer; the digest's `repr(report)` is
   what the agent summarizes. The two report classes share the
   `checks` / `metrics` accessor API used by the next two cells,
   so the audit body is identical for both.

6. **Persisted report (markdown cell).**

   Substitute `<REPORT_LOCATOR>` with evaluate's normalized
   Markdown value. A direct audit derives it from the selected id
   and backend contract: local workspace link, exact Hub put URL,
   or MLflow run/tracking locator. Missing authoritative data is
   `n/a — backend did not expose a locator`; never guess.

7. **Checks summary (code cell, bare Display last).**
   ```python
   checks = report.checks.summarize()
   checks
   ```
   `materialize.py` writes `checks.html`. The notebook cell does not.
   The repr opens with the severity counts, then lists issues,
   tips, passed, and not-applicable checks with codes like
   `SKD003`. Actionable lines carry the documentation URL. The
   review reads that page and applies its recommendation.
   Verified on `CrossValidationReport` and `EstimatorReport`.

8. **Metrics summary (code cell, verbose frame last).**
   ```python
   metrics = report.metrics.summarize().frame(
       verbose_name=True, flat_index=False
   )
   metrics
   ```
   `materialize.py` writes `metrics.html` from that same frame. The
   notebook cell does not.
   The frame is the metric table, with verbose names and the
   estimator/aggregate columns left unflattened. That same HTML is
   the only metrics table the site shows under `### Metrics`.
   Do not also paste the values into the design note.

9. **Available report accessors (not a notebook cell).**
   `help()` prints its tree and returns `None`. `materialize.py`
   captures that stdout in `scratch/audit/<stem>/accessors.txt`.
   Do not put the loop in `audit/<stem>.py`. Each tree ends in a
   `Displays` group; Additional report view labels are exactly
   those names. The group is task-dependent — a regression report
   offers `prediction_error` and no `roc`. Do not remember Display
   class names from docs. `available()` is a different thing: it
   lists metric or check *names* and only exists on `metrics` and
   `checks`.

That's the core template. Deeper accessors are appended after
`## Core audit complete` only when the user picks Additional
report view (or a Custom query that is still a report accessor).
Confirm the method with `api get`. The notebook cell is the
bare Display. Append the HTML write only in `materialize.py`
(`EXTRA`), then re-run that script:

```python
# %% [markdown]
# ## <human title>
#
# Heading must not be Checks summary or Metrics summary.

# %%
disp = report.<namespace>.<slug>()  # <slug> from accessors.txt Displays
disp
```

Plot Displays carry `_repr_html_` too. Only when one does not,
`materialize.py` saves `<slug>.png` from `figure_`. Failed probes stay
under `scratch/` and do not become Results subsections. Re-run
`style`, then `materialize.py` once, after each append. Do not
`cells run` the audit file.

## Digest-to-finding contract

After every digest run, execute
`python -m skore_skills audit finding --stem <stem>` and paste
JSON `finding` verbatim. Do not re-derive the string by hand.
Extra Display cells do not change G-AUDIT-FINDING.

## Why the bare Display is the right last expression

Every skore Display — `ChecksSummaryDisplay`,
`MetricsSummaryDisplay`, and the plot ones like
`PredictionErrorDisplay` — defines **both** `_repr_html_` and a
`__repr__` that renders the underlying values as text. Pinned by
`tests/skore_skills/test_skore_display_repr.py`.

That makes one line serve both audiences. A human opening the
audit `.py` as a notebook gets the rich HTML; the runner captures
`repr(result.result)` and the digest gets the text. On checks,
`.frame()` is a downgrade: it drops the severity grouping and
buries the messages in a column. Metrics are the exception. The
Display `repr` is a flat index (`rmse`, `dummyregressor_mean`).
The last expression is
`summarize().frame(verbose_name=True, flat_index=False)`, and
`metrics.html` is that frame's `_repr_html_()`.

The only thing neither path produces is a *standalone* per-item
HTML file, because the converted notebook is one document. That is
why `materialize.py` writes `scratch/results/<stem>/<slug>.html` —
the site embeds those under `## Results`. Agents never read them;
they summarize from the digest. The notebook does not contain
those writes.

## Statement-only cells are fine

Don't pad them with `print(repr(...))` to "force" output. The
template's "Imports" cell and the `REPORT_ID = ...` setup line
are statement-only by design; they produce no output section in
the digest. That's the right shape.
