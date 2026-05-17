"""Learner declaration.

Owns: the function that builds and returns the (unfit) learner —
typically a `SkrubLearner` produced from a skrub DataOps graph that
composes the steps in `data.py` and `features.py` with the chosen
estimator. Fitting, evaluation, and persistence happen elsewhere.
See `build-ml-pipeline` for the declarative mechanics.

Note on the source-binding preview. When the graph roots a
`skrub.var(name, value=...)` on a source identifier (path, URL,
table name), the `value` is the **preview** — the binding used by
`learner.skb.preview()` while iterating interactively. The preview
is intentionally exposed as an **optional** keyword on
`build_learner` so the caller (typically the experiment script) can
pass an absolute path resolved from the package root, instead of a
CWD-relative literal baked into this file. Without a preview, the
graph still fits and evaluates — only `.skb.preview()` is
unavailable. See `build-ml-pipeline` rule 2.
"""

from __future__ import annotations

from pathlib import Path


def build_learner(data_dir_preview: str | Path | None = None):
    """Return the unfit learner for the experiment scripts to consume.

    Parameters
    ----------
    data_dir_preview : str or Path or None, optional
        Preview value for the source-bound `skrub.var("data_dir", ...)`
        root. Pass an absolute path (e.g. `<pkg>.PROJECT_ROOT / "data"`)
        when iterating interactively so `learner.skb.preview()` works.
        Leave as `None` for fit / cross-validate runs — the env-dict
        passed to `skore.evaluate(..., data={"data_dir": ...})`
        supplies the binding regardless.
    """
    raise NotImplementedError
