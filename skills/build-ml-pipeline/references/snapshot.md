# Unfitted snapshot

After `build_learner` exists and before `smoke run`. No fit, no
`.skb.eval`. Do not call `full_report`. Do not call
`learner.report` without `eval=False`.

Confirm `DataOp.skb.report` with `python -m skore_skills api get`.
`learner.report` forwards that call. When `eval` is a parameter,
the experiment cell builds the
unfitted `build_learner()` and writes the DataOp report. No
`environment`. `results` is `scratch/results/<stem>`.

```python
learner.report(
    eval=False,
    open=False,
    overwrite=True,
    output_dir=results / "pipeline",
)
```

`pipeline/index.html` is the graph. Node pages carry each step's
source and docstring. Do not also write `pipeline.svg`. Leave
`learner` as the last expression.

Graphviz is required for that call. If `dot` is null, or output
contains `install Pydot and Graphviz` or `Format: "svg" not
recognized`, a finished `pipeline.html` does not authorize a
skip. Load `add-python-package` for `skrub` once. That load is
what runs `dot -c` (`env graphviz --execute`). Then run the
report once more. Do not run `dot -c` or call `env graphviz`
from this skill. Do not `pip install graphviz`. If that skill
is missing, or the retry still fails, write
`scratch/results/<stem>/pipeline.html` from `_repr_html_` or
`sklearn.utils.estimator_html_repr`. Confirm with `api get`.
Do not rewrite the pipeline.

When `eval` is absent, skip `learner.report` and write that
same `pipeline.html`. Do not call `full_report`.

Ensure `journal/<stem>.md` Method contains
`<!-- results-embed: pipeline -->` (add the line if the note
predates the marker). Add or update `experiments/<stem>.py`:
markdown plus a code cell that builds the unfitted
`build_learner()`, writes the report directory or the
`pipeline.html` fallback, and leaves `learner` as the last
expression. Do not add `skore.evaluate` or `project.put` here.
Do not `notebook convert` this unfitted snapshot if the
experiment file already contains `skore.evaluate`. That ban is
only for this snapshot, before the first evaluation.
`model-ml-pipeline` and `evaluate-ml-pipeline` still convert
`experiments/<stem>.py` at close.

If `policy.site` is true and `export-ml-site` is installed, run
`python -m skore_skills site build` after this snapshot and
before `smoke run` and the Evaluate question. Skipped or missing
EDA does not defer it. Skip in one line otherwise. If `site
build` errors with `mkdocs-material is required`, load
`add-python-package` for `mkdocs-material` (agent) and build
once more. Do not `pixi add` / `uv add`. If that skill is
missing, or the retry still fails, name the error in one line.
Name a build error; do not skip Evaluate.
