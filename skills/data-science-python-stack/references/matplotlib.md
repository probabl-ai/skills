# matplotlib

The foundation for static plotting in Python. Nearly every other viz
library in the PyData ecosystem (seaborn, pandas/polars plotting,
scikit-learn display objects) renders through matplotlib.

**Pick matplotlib when:**
- You need fine control over a plot's exact appearance.
- You're writing reusable plotting code or a custom viz.
- You need a multi-panel figure with disciplined layout.
- You need to drop down from another library (e.g. seaborn) to fine-tune.

**Pick something else when:**
- You're doing statistical visualization (distributions, regression,
  faceting) → `seaborn` is faster to write and reads better.
- You need interactive / browser-based plots → `plotly`.
