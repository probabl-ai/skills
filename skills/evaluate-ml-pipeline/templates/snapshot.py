"""Agent-only snapshot. Copy to scratch/results/<stem>/snapshot.py.

Do not commit. Re-open the stored report after ``put``. Do not call
``skore.evaluate`` or ``project.put``. Writes ``report.html``,
``report.txt``, ``locator.txt``, and the Method viewer. When
``DataOp.skb.report`` accepts ``eval``, write
``scratch/results/<stem>/pipeline/`` with ``eval=False`` (no fit).
Otherwise write ``pipeline.html`` from ``_repr_html_`` or
``estimator_html_repr``. Do not call ``full_report``. Do not call
``report`` without ``eval=False``.
"""

import inspect

import skore
from sklearn.utils import estimator_html_repr

from <pkg> import PROJECT_ROOT

STEM = "<stem>"
REPORT_ID = "<id>"
LOCATOR = "<REPORT_LOCATOR>"

# <SKORE_PROJECT_INIT>
project = skore.Project(
    name="<project-name>",
    mode="local",
    workspace=str(PROJECT_ROOT / "reports"),
)

report = project.get(REPORT_ID)
results = PROJECT_ROOT / "scratch" / "results" / STEM
results.mkdir(parents=True, exist_ok=True)
(results / "report.html").write_text(report._repr_html_(), encoding="utf-8")
(results / "report.txt").write_text(repr(report) + "\n", encoding="utf-8")
(results / "locator.txt").write_text(LOCATOR + "\n", encoding="utf-8")

learner = (
    report.estimator_
    if hasattr(report, "estimator_")
    else report.reports_[0].estimator_
)
data_op = getattr(getattr(learner, "data_op", None), "skb", None)
method = getattr(data_op, "report", None)
if callable(method) and "eval" in inspect.signature(method).parameters:
    learner.report(
        eval=False,
        open=False,
        overwrite=True,
        output_dir=results / "pipeline",
    )
else:
    render = getattr(learner, "_repr_html_", None)
    (results / "pipeline.html").write_text(
        render() if callable(render) else estimator_html_repr(learner),
        encoding="utf-8",
    )
