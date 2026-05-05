# %% [markdown]
# # Experiment: <short title>
#
# **Date:** YYYY-MM-DD
# **Goal:** what hypothesis or change this experiment is testing.
# **Result:** filled in after the run.

# %%
import skore

from <pkg>.data import load_dataset
from <pkg>.evaluate import splitter
from <pkg>.pipeline import build_learner

# %% [markdown]
# ## Project
#
# One project per workspace; each experiment writes its report under a
# stable key (the file stem). Parameters:
#
# - `workspace="reports"` — the folder that holds the Project store.
# - `name=...` — a short, stable project name inferred from the
#   package / dataset / working directory; reused across all
#   experiments in this workspace.
# - `mode="local"` — current default. See `skore-api` for the full
#   constructor and other supported modes.

# %%
project = skore.Project(workspace="reports", name="<project-name>", mode="local")

# %% [markdown]
# ## Data and learner

# %%
X, y = load_dataset()
learner = build_learner()

# %% [markdown]
# ## Evaluate
#
# Cross-validator and any metric overrides are imported from
# `<pkg>.evaluate`. The experiment script does not redefine them.
# `SkrubLearner.fit` takes a single environment dict (it does *not*
# implement `fit(X, y)`), so we pass the bindings via `data=`.

# %%
report = skore.evaluate(learner, data={"X": X, "y": y}, splitter=splitter)
report

# %% [markdown]
# ## Persist
#
# Key = file stem. Reusing this key in a future run overwrites the
# stored report — fork into a new experiment file if you want both.

# %%
project.put("<experiment-key>", report)
