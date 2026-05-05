# plotly

Python library for **interactive** plots rendered as HTML/JS. Charts
support hover, zoom, pan, and selection out of the box, and integrate
naturally with `marimo`, Jupyter, and Dash apps.

**Pick plotly when:**
- The user wants interactive visualization (hover tooltips, zoom, pan).
- Output is consumed in a notebook, browser, or dashboard rather than
  a static report or paper.
- You need to share an HTML report that the recipient can explore.
- You're building a dashboard (Dash is plotly's web framework).

**Pick something else when:**
- Output is static (publication, PDF report) → `matplotlib` or
  `seaborn`. Plotly can export PNG/PDF but it isn't its strength.
- You want a one-line statistical plot from a tidy dataframe —
  `seaborn` is shorter to write.
- File size matters — plotly figures embed plotly.js, which inflates
  HTML / notebook size.

**Pair with:**
- `pandas` / `polars` — both supported as data inputs (plotly's
  high-level API mirrors seaborn ergonomics).
- `dash` — plotly's web framework, if the project grows into a full
  dashboard (out of scope of this skill until requested).
