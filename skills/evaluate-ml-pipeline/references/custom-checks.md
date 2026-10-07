# Custom check routing

Register a custom check only on an explicit user request (including
"encode this finding as a check"). Do not invent checks. Built-in
SKD checks stay in place; `report.checks.add` extends them.

Confirm `skore.Check`, `CheckNotApplicable`, and `checks.add` with
`python -m skore_skills api get`. Example:
https://docs.skore.probabl.ai/stable/auto_examples/technical_details/plot_custom_checks.html

Custom checks inspect the **report**. They are not DataOp scoring
and do not go through `build-ml-pipeline`.

## Subclass `Check` before `Project.put`

Define a named module-level subclass in `experiments/NN_*.py`.
Project storage pickles the check registry; nested classes and
lambdas are not the portable contract.

```python
from skore import Check, CheckNotApplicable


class HighFeatureCount(Check):
    code = "CSTM001"
    title = "High feature count"
    report_types = ["estimator"]
    severity = "tip"
    docs_url = (
        "https://scikit-learn.org/stable/modules/"
        "feature_selection.html#feature-selection"
    )

    def check_function(self, report):
        if report.X_test is None:
            raise CheckNotApplicable()

        n_features = report.X_test.shape[1]
        if n_features > 50:
            return (
                f"The dataset has {n_features} features which may "
                "hurt model performance. Consider feature selection "
                "or dimensionality reduction."
            )
        return None
```

`check_function` returns a **string** to flag, `None` to pass, or
raises `CheckNotApplicable` when required data is missing.

| Attribute | Rule |
|---|---|
| `code` | Project prefix such as `CSTM001`; unique in that experiment |
| `title` | Short label shown in the checks summary |
| `report_types` | `"estimator"`, `"cross-validation"`, or both |
| `severity` | `"tip"` (caution) or `"issue"` (fix) |
| `docs_url` | Optional. Prefer a full `http…` URL so the review can cite it. Omit or set `None` when none exists |

`"estimator"` checks do **not** run on `CrossValidationReport`.
To share logic, set `report_types = ["estimator", "cross-validation"]`
and branch on the report. `ComparisonReport` aggregates component
reports.

Do not reimplement SKD\* (the gallery's high-variance CV check
overlaps SKD003 — pedagogical only).

The ordering is mandatory:

```python
report = skore.evaluate(...)
report.checks.add([HighFeatureCount()])
report.checks.summarize()
project.put(STEM, report)
```

`report.checks.summarize()` with no arguments is required before
every `project.put`, including when no custom check is added.
Do not pass `fast_mode` or `ignore`. Call it after `add` so the
custom check is in the stored results. `Project.put` stores that
cache. A later audit reads it and does not recompute those
checks. Adding a check after `put` changes only the in-memory
report until another `put`. `add` does not replace built-in SKD
checks.

Audit reads the bare `report.checks.summarize()` Display; do not call
`checks.add` from `audit/` (no `put` there).
