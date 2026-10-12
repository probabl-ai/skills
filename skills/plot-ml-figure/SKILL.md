---
name: plot-ml-figure
description: >
  Pick how to write a figure before custom plot code. Trigger when
  explore-ml-data, evaluate-ml-pipeline, or audit-ml-pipeline is
  about to save or display a chart, or when the user asks for a
  plot. Not a session owner. Not for skore/sklearn Display plots
  that already exist on a report.

  HOW TO USE: first match on the tree (owned plot, interactive
  iframe HTML, seaborn statistical, pandas chart, else
  matplotlib). In a notebook: save PNG (or HTML) then leave the
  figure as the cell output; never `plt.close`. Convert polars at
  the plot boundary. Missing lib → add-python-package. Confirm
  symbols with `api get`. The caller names the figure directory.
metadata:
  role: helper
  modelTier: small
---

# Plot ML Figure

Worker. Callers own the file and the turn. Do not `git end-turn`.

Details: `references/when.md`.

## Sequence

1. If a **skore report** or **sklearn Display** already plots this,
   use it. Stop.
2. If **interactivity** (hover, zoom, pan) is the requirement:
   Plotly Express. Write `<caller-figure-dir>/<slug>.html` with
   `include_plotlyjs=True` (inline, offline). `explore-ml-data`
   uses `data_analysis/`. Do not overwrite that caller’s owned
   HTML (e.g. `data_analysis_<slug>.html`). The caller embeds
   `<iframe src="<slug>.html" width="100%" height="640"></iframe>`
   in **its** markdown beside the implication. Do not add kaleido
   unless the user asked to export a static image. No Dash. Do
   not use a CDN.
3. If the plot is **statistical** on a tidy DataFrame (distribution,
   categorical compare, relationship, heatmap, pairplot, facet):
   seaborn figure-level when a notebook will display it
   (   `displot`, `relplot`, `catplot`, `pairplot`, `heatmap` via
   `FacetGrid` / axes only if already on a grid). Not a
   `plt.subplots` loop and not a `for` over columns with a
   trailing `g`. One figure-level call as the last expression;
   facet with `col=` / `col_wrap`. Save PNG, leave the
   figure/grid as the last expression. Never `plt.close`.
4. If it is a **simple** Series/DataFrame `bar` / `line` / `hist` /
   `area` from the index or a few columns, no statistical overlay:
   `df.plot(...)`. Save the figure (`ax.figure.savefig(...)`),
   leave `ax.figure` (or the axes) visible. Never `plt.close`.
5. Else **matplotlib**. Last resort. In a notebook still save and
   display; do not `plt.close`.

Notebook cells: save for the caller markdown **and** show the
figure in the notebook. `plt.close` is for non-notebook scripts
only (evaluate/audit scratch probes if they are not notebooks).

Polars → pandas at the plot boundary. Missing import →
`add-python-package` if installed; else name the package and
return. `api get` before new symbols.

Missing this skill from a caller → that caller one-line skips and
still follows this tree.

## Stop conditions

- Do not write a long matplotlib script for a hist, box, or bar
  of a Series.
- Do not load `choose-python-library` for matplotlib vs seaborn
  vs plotly.
- Do not `pixi add` / `uv add` / `env add`.
- Do not install plotly on the default EDA path.
- Do not `plt.close` a figure that should appear in a notebook.
