"""Learner declaration.

Owns: the function that builds and returns the (unfit) learner —
typically a `SkrubLearner` produced from a skrub DataOps graph that
composes the steps in `data.py` and `features.py` with the chosen
estimator. Fitting, evaluation, and persistence happen elsewhere.
See `build-ml-pipeline` for the declarative mechanics.
"""

from __future__ import annotations


def build_learner():
    """Return the unfit learner for the experiment scripts to consume."""
    raise NotImplementedError
