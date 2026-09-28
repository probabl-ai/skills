# plot-ml-figure eval

---

## CASE_01 — Statistical plot uses seaborn

**User prompt:**
> Plot income vs target as a boxplot in the EDA notebook.

**Assumed workspace state:**
- Caller is writing a cell in `data_analysis/data_analysis.py`.
- Target is classification. `income` is numeric.
- Output is a PNG for `data_analysis.md`.

**Must do:**
- Use seaborn (`sns.catplot(..., kind="box")` or equivalent) on
  the tidy frame.
- Save a PNG and leave the figure/grid as the cell output.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Write a long matplotlib `bar`/`bxp` loop for the same plot.
- Use plotly for this PNG.
- Load `choose-python-library` for matplotlib vs seaborn vs plotly.
- Call `plt.close`.
- Loop over columns with a trailing `g`.

---

## CASE_02 — Simple counts use pandas plot

**User prompt:**
> Bar chart of class counts from a pandas Series named `counts`.

**Assumed workspace state:**
- `counts` is a Series of class frequencies.
- PNG for the EDA report.

**Must do:**
- Use `counts.plot` (or `DataFrame.plot`) for the bar chart.
- Save the figure and leave it visible (no `plt.close`).

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Hand-build 20+ lines of `plt.bar` from the Series.
- Use plotly for this PNG.
- Call `plt.close`.

---

## CASE_03 — Interactive asks for plotly

**User prompt:**
> I want an interactive scatter I can hover, embedded in the EDA
> markdown.

**Assumed workspace state:**
- User asked for hover. Caller is `explore-ml-data`.
- `data_analysis/data_analysis.md` exists.

**Must do:**
- Use Plotly Express.
- `write_html` to the caller’s figure directory
  (`data_analysis/<slug>.html` for explore) with
  `include_plotlyjs=True`.
- Embed `<iframe src="<slug>.html" …>` in the caller’s markdown
  (`data_analysis.md` implications, not glance).
- Load `add-python-package` for `plotly` if it is not importable.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Use seaborn-only for this interactive request.
- Overwrite `data_analysis_<slug>.html`.
- Add kaleido unless the user asked to export a static image.
- Start a Dash app.
- Use `include_plotlyjs="cdn"`.

---

## CASE_04 — Static md figure is not plotly

**User prompt:**
> Save a histogram of MedHouseVal next to data_analysis.md.

**Assumed workspace state:**
- Figure is a PNG embed in `data_analysis.md`.

**Must do:**
- Use seaborn `displot` / `histplot` (or pandas `plot` hist).
- Save a PNG and leave the figure visible as the cell output.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Use plotly for this PNG.
- Load `choose-python-library` for the plotting competing set.
- Call `plt.close`.
