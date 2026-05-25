# %% [markdown]
# # Experiment: <short title>
#
# **Date:** YYYY-MM-DD
# **Goal:** what hypothesis or change this experiment is testing.
# **Result:** filled in after the run.

# %%
import skore

from <pkg> import PROJECT_ROOT
from <pkg>.data import load_dataset
from <pkg>.evaluate import splitter
from <pkg>.pipeline import build_learner

# %% [markdown]
# ## Paths
#
# `PROJECT_ROOT` comes from the package's `__init__.py` and resolves
# from `__file__` — independent of the current working directory.
# Replace `"data"` with the project's actual data folder if different;
# data layout is user-owned. The same absolute path is passed both as
# the pipeline preview and via `data=` to `skore.evaluate`, so
# `learner.skb.preview()` and `skore.evaluate(...)` see the same
# binding.

# %%
DATA_DIR = PROJECT_ROOT / "data"

# %% [markdown]
# ## Project
#
# One project per workspace; each experiment writes its report under a
# stable key (the file stem). The Project init block below is filled
# at scaffold time per the workspace's `skore mode:` decision
# (recorded in `journal/JOURNAL.md` Status `Workspace decisions`; see
# `organize-ml-workspace` § "G-SKORE-MODE"). Two forms:
#
# - **local mode**: `skore.Project(name=..., mode="local",
#   workspace=str(PROJECT_ROOT / "reports"))`. Reports persist to disk
#   under `reports/`. No account or login required.
# - **hub mode**: `skore.login(mode="hub")` first (interactive on
#   first run; cached after), then `skore.Project("<hub-workspace>/
#   <project-name>", mode="hub")`. Reports persist on Skore Hub.
#   Requires `pip install "skore[hub]"` (see `python-env-manager` §
#   "Tier 1 install: skore variant per mode") and a Skore Hub
#   account with access to the named hub workspace.
#
# `<SKORE_PROJECT_INIT>` is replaced by the right form at scaffold
# time. Do NOT keep both forms in the same file — only one is valid.

# %%
# <SKORE_PROJECT_INIT>
project = skore.Project(
    name="<project-name>",
    mode="local",
    workspace=str(PROJECT_ROOT / "reports"),
)

# %% [markdown]
# ## Data and learner
#
# `data_dir_preview=DATA_DIR` makes `learner.skb.preview()` work; it
# does not affect what `skore.evaluate` actually fits on (that comes
# from `data=` below).

# %%
X, y = load_dataset()
learner = build_learner(data_dir_preview=DATA_DIR)

# %% [markdown]
# ## Evaluate
#
# Cross-validator and any metric overrides are imported from
# `<pkg>.evaluate`. The experiment script does not redefine them.
# `SkrubLearner.fit` takes a single environment dict (it does *not*
# implement `fit(X, y)`), so we pass the bindings via `data=`. Use
# the source-bound form (`data={"data_dir": str(DATA_DIR)}`) when the
# pipeline binds a source identifier; use `data={"X": X, "y": y}` for
# materialized bindings.

# %%
report = skore.evaluate(learner, data={"data_dir": str(DATA_DIR)}, splitter=splitter)
report

# %% [markdown]
# ## Persist
#
# Key = file stem. Reusing this key in a future run overwrites the
# stored report — fork into a new experiment file if you want both.

# %%
project.put("<experiment-key>", report)
