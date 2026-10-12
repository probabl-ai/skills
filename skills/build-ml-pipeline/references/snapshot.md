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
what installs or verifies Graphviz (`env graphviz --execute`).
Then run the report once more. Do not call `env graphviz` from
this skill. Do not run `dot -c` or `pip install graphviz`. If
that skill is missing, or the retry still fails, write
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
`model-ml-pipeline` and `evaluate-ml-pipeline` still fill
`experiments/<stem>.py` at close, without executing it.

For a pre-evaluation experiment (the source contains no
`skore.evaluate` / `project.put`), read the notebook policy
before executing these cells. When `policy.notebooks` is `true`,
`notebook convert experiments/<stem>.py` is the one snapshot
execution; add `--html` only when `policy.site` is also `true`.
Do not separately execute the script. When notebooks is `null`
or `false`, do not change policy and use the existing
non-notebook execution. If an existing source already contains
evaluation, keep the unfitted snapshot path above and do not
convert it here; the next evaluation runs `materialize.py` once
and fills the notebook without a kernel.

If `policy.site` is true and `export-ml-site` is installed, run
`python -m skore_skills site build --if-stale` after this snapshot and
before `smoke run` and the Evaluate question. Skipped or missing
EDA does not defer it. Skip in one line otherwise. If `site
build` errors with `mkdocs-material is required`, load
`add-python-package` for `mkdocs-material` (agent) and build
once more. Do not `pixi add` / `uv add`. If that skill is
missing, or the retry still fails, name the error in one line.
Name a build error; do not skip Evaluate.
