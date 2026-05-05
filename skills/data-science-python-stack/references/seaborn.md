# seaborn

A statistical visualization library built on `matplotlib` (static
output). Provides a short, high-level API for the plots that show up
most often in data science: distributions, relationships, categorical
comparisons, regression diagnostics, faceting.

**Pick seaborn when:**
- You want a one-line call for a standard statistical plot
  (histogram, boxplot, scatter+regression, pairplot, heatmap).
- You want faceting (one subplot per subgroup) without writing a loop.
- The data is in a `pandas` DataFrame in long ("tidy") format.

**Pick something else when:**
- The plot isn't statistical or doesn't match a seaborn primitive →
  `matplotlib`.
- You need control over positioning, sizing, or annotation that seaborn
  hides → `matplotlib`.
- You need interactive plots → `plotly`.

**Watch out for:**
- Seaborn expects long-format pandas DataFrames. If the data is in
  polars or wide format, convert at the boundary.
- Seaborn returns matplotlib objects — drop down into matplotlib for
  fine-tuning rather than fighting the seaborn API.
