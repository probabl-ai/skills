# Unfitted snapshot

After `build_learner` exists and before `smoke run`. No fit, no
`SkrubLearner.report`, no `full_report`, no `.skb.eval`.

Confirm `sklearn.utils.estimator_html_repr` (or the learner's
`_repr_html_`) with `python -m skore_skills api get`. Write
`scratch/results/<stem>/pipeline.html` from that HTML.

Ensure `journal/<stem>.md` Method contains
`<!-- results-embed: pipeline -->` (add the line if the note
predates the marker). Add or update `experiments/<stem>.py`:
markdown plus a code cell that builds the unfitted
`build_learner()`, writes the same HTML path, and leaves
`learner` as the last expression. Do not add `skore.evaluate` or
`project.put` here. Do not `notebook convert` if the experiment
file already contains `skore.evaluate`.

Optional: `DataOp.skb.draw_graph()` to `pipeline.svg` only if
`python -m skore_skills env graphviz` is healthy. Otherwise skip
Graphviz in one line. Do not `pip install graphviz` and do not
`env graphviz` from this skill. A "install Pydot and Graphviz"
stub is `add-python-package` for `skrub`, not a pipeline rewrite.

If `policy.site` is true and `export-ml-site` is installed, run
`python -m skore_skills site build` after this snapshot and
before `smoke run` and the Evaluate question. Skipped or missing
EDA does not defer it. Skip in one line otherwise.
