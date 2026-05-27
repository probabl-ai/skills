# %% [markdown]
# # Audit: experiments/<NN>_<short_name>.py
#
# Read-only narrative of this experiment's skore report. The agent
# executes this file via the bundled in-process runner (see
# `audit-ml-pipeline` § "Execution contract") and reads the resulting
# markdown digest from stdout.
#
# **Hard rule (audit-ml-pipeline § "Read-only against the skore
# Project"):** this file MUST NOT call `skore.evaluate(...)` or
# `project.put(...)`. Only `project.summarize()`, `project.get(id)`,
# and `report.*` accessors are allowed. Re-running evaluate / put
# from an audit file lands a duplicate row under the same key and
# pollutes `project.summarize()`.
#
# **Bare-expression contract:** each cell ends with a bare
# expression so the executed notebook captures its auto-displayed
# repr. Do not wrap in `print(repr(...))` — that loses rich repr
# (`_repr_html_`, plot mime types) and clutters the human-reading
# view.

# %%
import skore

from <pkg> import PROJECT_ROOT

# %% [markdown]
# ## Open the project
#
# Same Project init form as `experiments/<NN>_<short_name>.py` — the
# `<SKORE_PROJECT_INIT>` marker below is filled at scaffold time per
# the workspace's `skore mode:` decision (see `organize-ml-workspace`
# § "G-SKORE-MODE" and `audit-ml-pipeline` § "Audit file contract").
# Two forms (only one is used per workspace):
#
# - **local mode**: `skore.Project(name=..., mode="local",
#   workspace=str(PROJECT_ROOT / "reports"))`.
# - **hub mode**: `skore.login(mode="hub")` first, then
#   `skore.Project("<hub-workspace>/<project-name>", mode="hub")`.
#
# Read the form from `experiments/<NN>_<short_name>.py` — never retype
# from memory; the audit must open the exact same Project the
# experiment wrote to.

# %%
# <SKORE_PROJECT_INIT>
project = skore.Project(
    name="<project-name>",
    mode="local",
    workspace=str(PROJECT_ROOT / "reports"),
)
project

# %% [markdown]
# ## List the available reports
#
# `project.summarize()` provides an overview of all reports in this
# Project — useful to confirm the experiment's report landed and to
# spot duplicate keys from accidental re-runs.

# %%
summary = project.summarize()
summary

# %% [markdown]
# ## Load the report
#
# **Hub mode** — `project.put()` prints a URL of the form:
#
#   `https://skore.probabl.ai/<hub-workspace>/<project>/<type-plural>/<N>`
#
# The report id is `skore:report:<type-singular>:<N>`.  The URL path
# segment is the plural; the id uses the singular (drop the trailing
# `s`).  Examples:
#
#   `.../cross-validations/42`  →  `skore:report:cross-validation:42`
#   `.../estimators/7`          →  `skore:report:estimator:7`
#
# Copy `<N>` and `<type-singular>` from the experiment's stdout and
# set `REPORT_ID` below — no `summarize()` traversal needed.
#
# **Local mode** — `project.put()` does not print a URL.  Read the
# `"id"` column value from the `summary` DataFrame above for the row
# whose `"key"` matches this experiment's stem, and set `REPORT_ID` to
# that value.

# %%
REPORT_ID = "skore:report:<type-singular>:<N>"  # hub: from put() URL (plural→singular, e.g. cross-validations→cross-validation, estimators→estimator); local: from summary["id"]

report = project.get(REPORT_ID)
report

# %% [markdown]
# ## Checks summary
#
# `report.checks.summarize().frame()` returns a DataFrame whose rows
# each carry a `code` (e.g. `SKD003`), a `severity` (`passed` /
# `issue` / `tip`), and a `documentation_url`. The
# `documentation_url` is the actionable mitigation — every check
# that surfaces here is documented on the skore docs site, and the
# linked page describes what the check tests **and what to try
# next**. `iterate-from-skore` reads this section and follows the
# URLs to draft Backlog rows.
#
# Available on `EstimatorReport` and `CrossValidationReport` in
# skore ≥ 0.18. Mute a noisy check via
# `report.checks.summarize(ignore=['<code>']).frame()`.
#
# Docs: https://docs.skore.probabl.ai/0.18/user_guide/automated_checks.html

# %%
report.checks.summarize().frame()

# %% [markdown]
# ## Metrics summary
#
# `report.metrics.summarize().frame()` covers task-appropriate
# defaults in one call:
#
# - regression: RMSE / MAE / R² + fit/predict timings,
# - binary classification: accuracy / precision / recall / F1 /
#   ROC-AUC / log-loss + timings,
# - multiclass: macro / micro averages of the above.
#
# Same accessor on both `EstimatorReport` and
# `CrossValidationReport`; the latter additionally reports mean ±
# std across folds. This section is the headline reading; it does
# not drive Backlog rows on its own — actionable findings come
# from the checks section above.

# %%
report.metrics.summarize().frame()

# %% [markdown]
# ## End of audit
#
# Re-running this audit file overwrites
# `scratch/audit/<NN>_<short_name>/`. The source
# `audit/<NN>_<short_name>.py` is the durable record; the digest
# at `scratch/audit/<NN>_<short_name>/audit.md` is the canonical
# input to `iterate-from-skore`.
