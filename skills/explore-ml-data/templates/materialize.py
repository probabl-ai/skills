"""Agent-only materialize. Copy to scratch/data_analysis/materialize.py.

Do not commit. This is the only EDA run. Do not execute
``data_analysis/data_analysis.py`` and do not ``notebook convert``
or ``cells run`` it. Replace the ``<ANALYSIS>`` block with that
file's loads, ``TableReport.write_html`` calls, and figure or HTML
saves, same paths. One load per family. Bind ``FAMILIES`` as
``(slug, raw)`` and ``FRAME`` to the target family's pandas frame.
Leave the tail. It writes ``<slug>.json``
(``plot_distributions=False``) and ``extras.json``.
"""

import json

import matplotlib

matplotlib.use("Agg")

import pandas as pd
import seaborn as sns
import skrub

from <pkg> import PROJECT_ROOT

TARGET = <TARGET>  # column name str, or None
TASK = "<TASK>"  # classification | regression | none

analysis = PROJECT_ROOT / "data_analysis"
analysis.mkdir(parents=True, exist_ok=True)
out = PROJECT_ROOT / "scratch" / "data_analysis"
out.mkdir(parents=True, exist_ok=True)

# <ANALYSIS>
FAMILIES = [
    ("<slug>", <LOAD_RAW_DATA>),
]
FRAME = None
for slug, raw in FAMILIES:
    frame = raw.to_pandas() if hasattr(raw, "to_pandas") else raw
    skrub.TableReport(raw, title=slug, verbose=0).write_html(
        analysis / f"data_analysis_{slug}.html"
    )
    if FRAME is None and (TARGET is None or TARGET in frame.columns):
        FRAME = frame
# Figure and extra HTML saves from the human file, same paths.
# </ANALYSIS>

report_html_names = {f"data_analysis_{slug}.html" for slug, _raw in FAMILIES}
table_rows: list[dict] = []

for slug, raw in FAMILIES:
    frame = raw.to_pandas() if hasattr(raw, "to_pandas") else raw
    report = skrub.TableReport(
        raw, title=slug, verbose=0, plot_distributions=False
    )
    (out / f"{slug}.json").write_text(report.json(), encoding="utf-8")
    n_dup = int(frame.duplicated().sum())
    n_rows = int(len(frame))
    has_target = TARGET is not None and TARGET in frame.columns
    table_rows.append(
        {
            "slug": slug,
            "n_rows": n_rows,
            "n_duplicate_rows": n_dup,
            "duplicate_rate": n_dup / n_rows if n_rows else 0.0,
            "has_target": has_target,
        }
    )

if FRAME is None:
    _, raw0 = FAMILIES[0]
    FRAME = raw0.to_pandas() if hasattr(raw0, "to_pandas") else raw0

pngs = sorted(p.name for p in analysis.glob("*.png"))
htmls = sorted(
    p.name
    for p in analysis.glob("*.html")
    if p.name not in report_html_names and not p.name.endswith(".nb.html")
)

extras: dict = {
    "tables": table_rows,
    "n_rows": table_rows[0]["n_rows"] if table_rows else 0,
    "n_duplicate_rows": table_rows[0]["n_duplicate_rows"] if table_rows else 0,
    "duplicate_rate": table_rows[0]["duplicate_rate"] if table_rows else 0.0,
    "target": TARGET,
    "task": TASK,
    "class_counts": None,
    "target_skew": None,
    "feature_target_corr": [],
    "leakage_flags": [],
    "pngs": pngs,
    "htmls": htmls,
}

if TARGET is not None and TARGET in FRAME.columns:
    y = FRAME[TARGET]
    if TASK == "classification":
        extras["class_counts"] = {
            str(k): int(v) for k, v in y.value_counts(dropna=False).items()
        }
    elif pd.api.types.is_numeric_dtype(y):
        extras["target_skew"] = float(y.skew())
    if pd.api.types.is_numeric_dtype(y):
        corr = (
            FRAME.select_dtypes("number")
            .corrwith(y)
            .abs()
            .sort_values(ascending=False)
        )
        extras["feature_target_corr"] = [
            {"column": col, "abs_pearson": float(val)}
            for col, val in corr.items()
            if col != TARGET and pd.notna(val)
        ][:20]
        extras["leakage_flags"] = [
            f"{row['column']} abs(Pearson) vs {TARGET} = {row['abs_pearson']:.3f}"
            for row in extras["feature_target_corr"]
            if row["abs_pearson"] >= 0.99
        ]
    if TASK == "classification":
        for col in FRAME.columns:
            if col == TARGET:
                continue
            rates = FRAME.groupby(y, dropna=False)[col].apply(lambda s: s.isna().mean())
            if rates.max() - rates.min() >= 0.5:
                extras["leakage_flags"].append(
                    f"{col} null rate differs by class: {rates.to_dict()}"
                )

(out / "extras.json").write_text(
    json.dumps(extras, default=str), encoding="utf-8"
)
