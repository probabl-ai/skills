"""Agent-only materialize. Copy to scratch/results/<stem>/materialize.py.

Do not commit. This is the only evaluation run. Do not execute
``experiments/<stem>.py`` and do not ``notebook convert`` it.
Replace the ``<CALL>`` block with that file's fit / ``skore.evaluate`` /
``report.checks.summarize()`` / ``project.put``, same arguments and
order. Leave the tail. It writes ``report.html``, ``report.txt``,
``checks.html``, ``metrics.html``, ``id.txt``, and the Method viewer.
The agent writes ``locator.txt`` from ``id.txt``. Do not call
``full_report``. Do not call ``report`` without ``eval=False``.
"""

import inspect

import skore
from sklearn.utils import estimator_html_repr

from <pkg> import PROJECT_ROOT

STEM = "<stem>"

# <SKORE_PROJECT_INIT>
project = skore.Project(
    name="<project-name>",
    mode="local",
    workspace=str(PROJECT_ROOT / "reports"),
)

# <CALL>
report = skore.evaluate(...)
report.checks.summarize()
project.put(STEM, report)
# </CALL>

results = PROJECT_ROOT / "scratch" / "results" / STEM
results.mkdir(parents=True, exist_ok=True)
checks = report.checks.summarize()
metrics = report.metrics.summarize().frame(verbose_name=True, flat_index=False)
(results / "report.html").write_text(report._repr_html_(), encoding="utf-8")
(results / "report.txt").write_text(repr(report) + "\n", encoding="utf-8")
(results / "checks.html").write_text(checks._repr_html_(), encoding="utf-8")
(results / "metrics.html").write_text(metrics._repr_html_(), encoding="utf-8")
summary = project.summarize().reset_index()
report_id = summary.loc[summary["key"] == STEM, "id"].iloc[-1]
(results / "id.txt").write_text(f"{report_id}\n", encoding="utf-8")

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
