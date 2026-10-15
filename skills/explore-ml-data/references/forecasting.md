# Forecasting — target against time

Applies when the user prompt, the JOURNAL, or a recorded
Deployment of `time` says the goal is to predict future values of
a target that is indexed by time. A datetime column alone does
not make it a forecast.

The analysis then always contains at least one interactive
plot of each target against its timestamp, made with Plotly.
Seaborn and PNG-only versions do not replace it.

## Setup

- `add-python-package` for `plotly` (agent) together with the
  other analysis libraries, before the notebook is written.
- Append `templates/target_vs_time.py` to the first family.
  Substitute `<TIME_COL>` and `<TARGETS>` (a list, one entry per
  confirmed target). Drop the seaborn `relplot` cell of
  `templates/datetime.py`: this plot replaces it.
- The timestamp column is the one the prompt or the data names.
  When several datetime columns could be the time axis, use the
  one that orders the rows and say which in Modelling
  implications and Open questions.

The template writes `target_vs_time.html` (the full span) and
`target_vs_time_recent.html` (the last rows at full resolution).
`materialize.py` runs the same cells. It needs no change.

## Subset a large table

At most 50,000 points per target are drawn. The template keeps
every `keep_every`-th row after sorting by time and shows the
rest in the recent-rows plot. Raise `MAX_POINTS` only when the
file stays under about 10 MB. Do not write the subset to disk
and do not touch the raw rows. Missing stretches stay as gaps in
the line. Name the subset in the sentence beside the plot.

Several series (an id column): add `color="<ID_COL>"` to both
figures and keep at most 10 ids, the ones with the most rows.
Say how they were picked. With several series, plot one target
per figure and drop `facet_row`.

## Thumbnail and link

An HTML file holds about 5 MB of Plotly code plus about 0.04 MB
per 1,000 points. When a figure would draw more than 100,000
points in total (several targets or series), do not embed it. The
Plotly figure stays the full interactive page. Add a small PNG of
the same subset made with matplotlib, through pandas, and link the
HTML from it. Do not install `kaleido` and do not call
`write_image`.

```python
axes = series.iloc[::step].set_index(TIME)[VALUES].plot(
    subplots=True, legend=False, linewidth=0.5, xlabel="",
    figsize=(6, 1.5 * len(VALUES)),
)
axes[0].figure.savefig(OUT / "target_vs_time.png", dpi=70, bbox_inches="tight")
axes[0].figure
```

Put it in its own cell after the overview, as that cell's last
expression. The PNG is a preview, not a second analysis; the
sentence beside it describes the interactive plot.

In `data_analysis.md` the thumbnail sits in an anchor to the
HTML. That is the one case where an HTML file is linked and not
embedded; the PNG is the embed:

```html
<a href="target_vs_time.html" target="_blank"><img src="target_vs_time.png" alt="<caption>"></a>
```

Any other plot stays an iframe, as for every analysis.

## The sentence beside the plot

Cite the numbers from the summary table: the start and end of the
span, `n_rows`, `keep_every`, and any gap or level change the
figure shows. Do not describe a pattern the numbers and the
figure do not support.
