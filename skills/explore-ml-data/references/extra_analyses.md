# Extra analyses — append to `data_analysis/data_analysis.py`

Recipes, not a second notebook. Run this board only after the user
picks **Choose additional pre-defined option** on the
continuation board. Do not ask extras after the default pass. Then
AskUserQuestion `allow_multiple`. The question's last line is
exactly: Select each one you want. Write nothing after that
line. Only list items that
apply and were **not** already in the user prompt. Picks:
`add-python-package` for the extra lib (agent), append the matching
cells, `style`, re-run `cells run`, refresh `facts.py`, then write
`data_analysis.md`. PNG unless the user asked for hover. Load
`plot-ml-figure` if installed before figure cells. One
figure-level call as the last expression of its own cell; table
cells stay table-only. If you save a PNG or HTML, embed it in
`data_analysis.md` with a sentence citing extras/JSON numbers.
Never `plt.close`.

Do not train/test split. Do not drop or rewrite raw rows.

## Multivariate / interactions

Lib: seaborn (already on the run path).

A few 2-way views among the bivariate column list, or
`sns.pairplot` on at most 6 numeric columns (target + top
associates). Save `interactions.png`. Last expression: the grid.

## 2D projection (PCA)

Lib: scikit-learn. UMAP only if the user insists (`umap-learn`).

Numeric columns, median-impute in the cell for the plot only — do
not write an imputed table. `PCA(n_components=2)`, then
`sns.relplot` of the two components colored by target if set.
Save `pca.png`. Last expression: the relplot grid. Do not use PCA
as a model preprocessor here.

## Hypothesis tests

Lib: scipy.

| Feature | Target | Test |
|---|---|---|
| numeric | classification | ANOVA or Kruskal–Wallis via `scipy.stats` |
| categorical | classification | chi-square on a crosstab |
| numeric | regression | Spearman via `scipy.stats.spearmanr` |

Last expression: a small p-value table. Interpret as a signal, not
a modelling decision. No figure unless you also add a separate
cell whose last expression is that figure.

## Subgroup / segment

Ask which grouping column if the user did not name one.

Table cell: `groupby(group)[TARGET]` summary (rate or mean); last
expression is that frame. If a facet plot is worth a sentence in
`data_analysis.md`, a **second** cell: seaborn figure-level facet,
save `subgroup_<group>.png`, last expression the grid. Otherwise
do not save a PNG.

## Full time-series

Only if a datetime column exists. Lib: statsmodels.

Table cell: ADF on the target (if numeric) or on one numeric
series; last expression is the statistic table. Figure cell:
ACF/PACF via seaborn/statsmodels plot, save `acf.png`, last
expression the figure. Additive seasonal decomposition only when
the series is regular, same split (table vs figure cells).

## Join keys / coverage

Only if two or more confirmed families exist. No extra lib.

Append `templates/join_coverage.py`. Substitute a real
`<OTHER_SLUG>` and `<JOIN_KEY>` (a shared column). Drop the
coverage cell if there is no candidate key. If both families
have datetime columns, a further table cell: min/max and overlap
of those columns — no empty datetime loop.

Last expressions are the summary frames. In-memory diagnostic
merge is allowed; do not write a joined frame to disk, do not
replace `FRAME` with the merge, do not add a TableReport on the
join. No figure unless it earns a sentence in `data_analysis.md`.

## Domain-specific

Only if those dtypes exist. No extra lib unless needed.

- **Text** (object/string, high unique count): length describe,
  empty-string rate as a table cell. If a length histogram earns a
  markdown sentence, a second cell: save `text_length.png`, last
  expression the grid. Otherwise do not save a PNG.
- **Geo** (lat/lon-like names or values in range): min/max,
  out-of-range counts as a table. Do not call a maps API.
