"""Data loading and X-marker wiring.

Owns: how raw data is materialized into `(X, y)`, and how structural
metadata (groups, time ordering, ...) is attached at the X marker via
`split_kwargs`. Pipeline mechanics live in `build-ml-pipeline`; data
paths are decided by the caller — this module does not invent a
`data/` directory.
"""

from __future__ import annotations


def load_dataset():
    """Return `(X, y)` ready for the pipeline.

    Replace the body with the actual loader: `pd.read_parquet`,
    `pd.read_csv`, a fixture fetch, a remote query, etc. The return
    contract is `(X, y)` where `X` is a DataFrame (or whatever the
    pipeline expects at its X marker) and `y` is the target.
    """
    raise NotImplementedError
