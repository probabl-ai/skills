# Audit ML Pipeline — Cell anatomy

Full anatomy of an audit-file cell: concrete right/wrong examples,
the 7-cell template sequence, and why `.frame()` matters.
Cross-referenced from SKILL.md § "Audit file contract — overview".

The template is deliberately narrow: checks summary + metrics
summary. The rendered digest at `scratch/audit/<stem>/audit.md`
is what `iterate-from-skore` reads to populate the JOURNAL
Backlog — each row in the checks summary carries a
`documentation_url` that drives an actionable mitigation. Do not
extend the template with per-task accessors (residuals, confusion
matrices, feature importances, calibration, …) unless the user
asks for one — the goal is a small, predictable digest.

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
  `_repr_html_`** — it captures `repr(result.result)` only. Use
  `.frame()` on Display objects to get a text-readable repr.
- Assignment-only / statement-only cells produce **no output and
  no error** — they execute silently. This is the right shape for
  setup cells (imports, `REPORT_ID = …`, etc.).

## The 7-cell template sequence

The template ships with this cell sequence. All seven cells are
task-agnostic. Leave them as-is unless a specific experiment's
user asks for a deeper accessor.

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

   - **Hub mode**: `project.put()` prints a URL of the form
     `https://skore.probabl.ai/<workspace>/<project>/<type-plural>/<N>`.
     The id is `skore:report:<type-singular>:<N>` — the URL path
     segment is the plural; the id uses the singular (drop the trailing
     `s`). Examples: `cross-validations/42` →
     `skore:report:cross-validation:42`; `estimators/7` →
     `skore:report:estimator:7`. Copy `<N>` and `<type-singular>` from
     the put() stdout; hardcode as `REPORT_ID`; no `summarize()` needed.
   - **Local mode**: read `summary["id"]` from the `summarize()` cell
     above, filtering to the row where `key == "<NN>_<short_name>"`.

   ```python
   REPORT_ID = "skore:report:<type-singular>:<N>"  # hub: from put() URL

   report = project.get(REPORT_ID)
   report
   ```
   The runner captures `repr(report)` — the report's plain text
   repr identifies the estimator (and, for `CrossValidationReport`,
   the splitter as well). The two report classes share the
   `checks` / `metrics` accessor API used by the next two cells,
   so the audit body is identical for both.

6. **Checks summary (code cell, bare expression).**
   ```python
   report.checks.summarize().frame()
   ```
   Pandas DataFrame of the passed/issue/tip walk with codes like
   `SKD003`. Each row carries a `documentation_url` — the
   actionable mitigation lives at that link, and
   `iterate-from-skore` follows it to draft Backlog rows.
   Verified on `CrossValidationReport` and `EstimatorReport` in
   skore ≥ 0.18.

7. **Metrics summary (code cell, bare expression).**
   ```python
   report.metrics.summarize().frame()
   ```
   Pandas DataFrame with task-appropriate defaults:
   - **regression**: RMSE / MAE / R² + fit/predict timings.
   - **binary classification**: accuracy / precision / recall / F1
     / ROC-AUC / log-loss + timings.
   - **multiclass**: macro/micro averages.

That's the whole template. Deeper accessors
(`prediction_error()`, `confusion_matrix()`, `roc()`,
`permutation_importance()`, …) are intentionally out of scope —
add them per-experiment only when the user asks.

## Why `.frame()` is load-bearing on cells 6–7

`MetricsSummaryDisplay` and `ChecksSummaryDisplay` define
`_repr_html_` for rich HTML in JupyterLab / VS Code, but their
`__repr__` is the default `<…Display object at 0x…>` — no useful
text.

The runner captures `repr(result.result)`, so `.frame()` is what
turns the Display into a pandas DataFrame whose `repr` carries the
actual values. The runner's pandas display options widen that repr;
the agent reads the values from there.

When a human opens the audit `.py` as a notebook in their editor,
the rich HTML view still works — `.frame()` doesn't suppress it; it
just adds a text-readable path for the agent.

## Statement-only cells are fine

Don't pad them with `print(repr(...))` to "force" output. The
template's "Imports" cell and the `REPORT_ID = ...` setup line
are statement-only by design; they produce no output section in
the digest. That's the right shape.
