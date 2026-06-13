# %% [markdown]
# # EDA: <project / dataset name>
#
# Exploratory data analysis, run **before** any model is designed.
# The agent executes this file via the shared in-process runner (see
# `explore-ml-data` § "Execution contract") and reads the resulting
# markdown digest from stdout, then authors `data/eda.md` and the
# `journal/JOURNAL.md` § "Data understanding (EDA)" section from it.
#
# **Two locations, kept separate:**
#
# - **Raw data source** — user-owned, READ-ONLY. May live in `data/`,
#   another in-repo folder (`raw/`, `inputs/`), an absolute path, or
#   outside the repo. Set it at `RAW` below; it can be anything.
# - **EDA deliverables** — always written under `EDA_DIR`
#   (`<project>/data/`): the `eda_<table>.html` reports here, and
#   `eda.md` authored by the agent. These are committed.
#
# **Hard rule (explore-ml-data § "Read-only-against-raw-data
# contract"):** this file READS the raw data and writes ONLY the
# `data/eda.*` deliverables. It MUST NOT clean, impute, drop, or
# re-save the raw files — cleaning belongs in the pipeline
# (`build-ml-pipeline`), applied at fit time.
#
# **Library-agnostic:** the structured facts come from `skrub`
# (`TableReport`, `column_associations`), which work the same on
# pandas and polars. The ONLY place a dataframe library appears is the
# `RAW = <LOAD_RAW_DATA>` line you adapt. Do not reach for
# pandas/polars-specific summary methods — read them off the skrub
# report instead.
#
# **Bare-expression contract:** every code cell ends on a *text-
# friendly* bare expression (a `dict`, a `list`, a `DataFrame`) so the
# runner captures real values in the digest. NEVER end a cell on a
# bare `skrub.TableReport(...)` — outside a notebook its repr is
# `<TableReport: use .open() to display>`. Use `report.write_html(...)`
# (a statement) for the rich HTML, and read facts from
# `report.json()`.

# %%
import json

import skrub

from <pkg> import PROJECT_ROOT

# Deliverables always land here (created if missing). This is NOT
# necessarily where the raw data lives.
EDA_DIR = PROJECT_ROOT / "data"
EDA_DIR.mkdir(parents=True, exist_ok=True)

# %% [markdown]
# ## Load the raw data
#
# Replace `<LOAD_RAW_DATA>` with the real load of the raw file(s),
# wherever they live. Examples:
#
#   RAW = pd.read_parquet(PROJECT_ROOT / "data" / "train.parquet")
#   RAW = pd.read_csv(Path("/abs/path/or/other_folder/train.csv"))
#   RAW = pl.read_parquet("s3://bucket/train.parquet")
#
# Use the workspace's tabular library (G-TABULAR: pandas or polars);
# skrub accepts both. End the cell on `RAW.shape`. For multiple tables,
# load each into its own variable and repeat the overview cell per
# table.

# %%
RAW = <LOAD_RAW_DATA>
RAW.shape

# %% [markdown]
# ## Table overview (skrub TableReport)
#
# `TableReport` is the user-facing artifact: write it to
# `data/eda_<table>.html` (rich, interactive — types, distributions,
# associations). For the agent digest, read structured per-column
# stats off `report.json()` instead of ending on the report object.
# `verbose=0` keeps progress prints out of the digest.

# %%
report = skrub.TableReport(RAW, title="<table>", verbose=0)
report.write_html(EDA_DIR / "eda_<table>.html")

summary = json.loads(report.json())
n_rows = summary.get("n_rows")
overview = [
    {
        "column": col.get("name"),
        "dtype": col.get("dtype"),
        "null_pct": col.get("null_proportion"),
        "n_unique": col.get("nunique"),
    }
    for col in summary.get("columns", [])
]
{"n_rows": n_rows, "n_columns": len(overview), "columns": overview}

# %% [markdown]
# ## Target
#
# Drives the metric default and whether the splitter should stratify
# (classification) or whether the target is skewed (regression). Read
# the target column's entry from the same `report.json()` — it carries
# the value counts (low-cardinality) or the distribution summary
# (numeric), so this works for both task types without library-
# specific code. Delete this cell if the task is unsupervised / the
# target is unknown.

# %%
TARGET = "<TARGET_COLUMN>"
next((col for col in summary.get("columns", []) if col.get("name") == TARGET), None)

# %% [markdown]
# ## Structure signals
#
# Candidate datetime columns (→ consider `TimeSeriesSplit`) and
# high-cardinality id / group-like columns (→ consider `GroupKFold`).
# Both come from the skrub summary: skrub infers datetime types even
# from string columns, and the unique ratio flags id/group columns.
# This cell only surfaces the evidence; the splitter pick is
# `G-CV-SPLITTER`.

# %%
datetime_cols = [
    col.get("name")
    for col in summary.get("columns", [])
    if "date" in str(col.get("dtype", "")).lower()
]
unique_ratio = sorted(
    (
        {
            "column": col.get("name"),
            "unique_ratio": (col.get("nunique") or 0) / n_rows if n_rows else None,
        }
        for col in summary.get("columns", [])
    ),
    key=lambda r: (r["unique_ratio"] is not None, r["unique_ratio"]),
    reverse=True,
)
{"datetime_cols": datetime_cols, "top_unique_ratio": unique_ratio[:10]}

# %% [markdown]
# ## Associations
#
# `skrub.column_associations` ranks pairwise column associations
# (library-agnostic; returns a small table). Strong feature↔target
# links are candidate predictors; an implausibly perfect link is a
# leakage flag to call out explicitly.

# %%
skrub.column_associations(RAW).head(20)

# %% [markdown]
# ## End of EDA
#
# Re-running this file overwrites `data/eda_<table>.html` and the
# `scratch/eda/` digest. Now author `data/eda.md` (findings +
# **modelling implications**) and the `journal/JOURNAL.md` § "Data
# understanding (EDA)" summary from the digest above.
