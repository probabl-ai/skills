# %% [markdown]
# ## Target over time
#
# Each target against its timestamp: the full span, then the most
# recent rows at full resolution. Interactive: hover, zoom, pan.

# %%
import plotly.express as px

TIME = "<TIME_COL>"
VALUES = <TARGETS>
MAX_POINTS = 50_000
ZOOM_POINTS = 2_000

series = FRAME[[TIME, *VALUES]].sort_values(TIME)
step = max(1, -(-len(series) // MAX_POINTS))


def target_figure(rows):
    long = rows.melt(id_vars=TIME, var_name="target", value_name="value")
    fig = px.line(long, x=TIME, y="value", facet_row="target")
    fig.update_yaxes(matches=None, title_text=None)
    fig.for_each_annotation(lambda note: note.update(text=note.text.split("=")[-1]))
    return fig


overview = target_figure(series.iloc[::step])
overview.write_html(OUT / "target_vs_time.html", include_plotlyjs=True)
overview

# %%
pd.DataFrame(
    {
        "start": [series[TIME].min()],
        "end": [series[TIME].max()],
        "n_rows": [len(series)],
        "keep_every": [step],
        "n_plotted": [len(series.iloc[::step])],
    }
)

# %%
recent = target_figure(series.tail(ZOOM_POINTS))
recent.write_html(OUT / "target_vs_time_recent.html", include_plotlyjs=True)
recent
