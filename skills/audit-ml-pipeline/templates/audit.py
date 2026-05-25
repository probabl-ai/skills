# %% [markdown]
# # Audit: experiments/<NN>_<short_name>.py
#
# Read-only narrative of this experiment's skore report. The agent
# executes this file via the two-step jupytext + nbconvert path (see
# `audit-ml-pipeline` § "Execution contract") and reads the resulting
# markdown digest from `scratch/audit/<NN>_<short_name>/audit.md`.
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
# Same `workspace` + `name` as `experiments/<NN>_<short_name>.py`.
# Reading them from there (not retyping from memory) is the
# audit-ml-pipeline pre-flight contract.

# %%
project = skore.Project(
    workspace=str(PROJECT_ROOT / "reports"),
    name="<project-name>",
    mode="local",
)
project

# %% [markdown]
# ## List the available reports
#
# `project.summarize()` returns a DataFrame indexed by report id,
# with a `key` column. Used in two ways: (1) confirm this
# experiment's report is on disk, (2) resolve the user-facing key
# to the internal id (which is what `project.get(...)` consumes —
# `get` is by id, not by key; see `python-api` § "Lookup failure ≠
# artifact missing").

# %%
summary = project.summarize()
summary

# %% [markdown]
# ## Resolve this experiment's report id
#
# Filter `summary` by the experiment stem; pull the (single) row's
# id. If `.itertuples` raises `ValueError: too many values to
# unpack` the project has multiple rows under the same key — flag
# it; the experiment was re-run without overwriting.

# %%
KEY = "<NN>_<short_name>"
((_, id_),) = summary.loc[summary["key"] == KEY, ["key", "id"]].itertuples(
    index=False,
)
id_

# %% [markdown]
# ## Load the report
#
# Rich repr (HTML when available) renders in-notebook; the
# executed markdown digest preserves it.

# %%
report = project.get(id_)
report

# %% [markdown]
# ## Diagnosis surface
#
# `report.diagnosis()` is the v1 programmatic diagnostic walk —
# the same surface `iterate-from-skore` consumes. Reading it here
# (in audit context) is for *understanding this experiment*; the
# sourcing-strategy use of the same call lives in
# `iterate-from-skore`.

# %%
report.diagnosis()

# %% [markdown]
# ## Metric accessors
#
# Task-dependent. Replace this block with the accessors that
# matter for this experiment per the design note's Method.
# Reference shapes by task (confirm names via `python-api`
# against the installed skore version):
#
# - regression: `report.metrics.rmse`, `report.metrics.mae`,
#   `report.metrics.r2`
# - binary classification: `report.metrics.roc_auc`,
#   `report.metrics.brier_score`,
#   `report.metrics.precision_recall`
# - multiclass: `report.metrics.classification_report`
# - calibration: `report.metrics.calibration`
#
# One bare expression per cell so the markdown digest shows one
# output per metric — easier for the agent to scan.

# %%
report.metrics

# %% [markdown]
# ## End of audit
#
# Re-running this audit file overwrites
# `scratch/audit/<NN>_<short_name>/`. The source `audit/<NN>_<short_name>.py`
# is the durable record; the executed `.ipynb` + rendered `.md` are
# ephemeral.
