"""Agent-only materialize. Copy to scratch/audit/<stem>/materialize.py.

Do not commit. This is the only audit run. Do not execute
``audit/<stem>.py``, do not ``cells run`` it, and do not
``notebook convert`` it. Re-open the stored report. Do not call
``skore.evaluate`` or ``project.put``. Writes ``checks.html``,
``metrics.html``, ``report.html``, ``locator.txt``,
``accessors.txt``, and ``audit.md`` (``repr`` of the checks and
metrics). Append extra Displays to ``EXTRA``; put a custom query
or plot in the ``<CALL>`` block. The audit notebook stays a bare
display and is filled with empty outputs.
"""

import io
from contextlib import redirect_stdout

import skore

from <pkg> import PROJECT_ROOT

STEM = "<NN>_<short_name>"
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
audit_out = PROJECT_ROOT / "scratch" / "audit" / STEM
audit_out.mkdir(parents=True, exist_ok=True)

(results / "report.html").write_text(report._repr_html_(), encoding="utf-8")
(results / "locator.txt").write_text(LOCATOR + "\n", encoding="utf-8")

checks = report.checks.summarize()
(results / "checks.html").write_text(checks._repr_html_(), encoding="utf-8")

metrics = report.metrics.summarize().frame(verbose_name=True, flat_index=False)
(results / "metrics.html").write_text(metrics._repr_html_(), encoding="utf-8")

buffer = io.StringIO()
with redirect_stdout(buffer):
    for name in ("metrics", "checks", "inspection", "data"):
        namespace = getattr(report, name, None)
        if callable(getattr(namespace, "help", None)):
            namespace.help()
(audit_out / "accessors.txt").write_text(buffer.getvalue(), encoding="utf-8")

# <CALL>
# ("<namespace>", "<slug>") from this turn's Displays group in accessors.txt.
# Custom query or plot code copied from audit/<stem>.py goes here.
EXTRA: list[tuple[str, str]] = []
# </CALL>

for namespace_name, slug in EXTRA:
    disp = getattr(getattr(report, namespace_name), slug)()
    render = getattr(disp, "_repr_html_", None)
    if callable(render):
        (results / f"{slug}.html").write_text(render(), encoding="utf-8")
        continue
    figure = getattr(disp, "figure_", None)
    if figure is not None:
        figure.savefig(results / f"{slug}.png")

(audit_out / "audit.md").write_text(
    "## Checks summary\n\n"
    f"{checks!r}\n\n"
    "## Metrics summary\n\n"
    f"{metrics!r}\n",
    encoding="utf-8",
)
