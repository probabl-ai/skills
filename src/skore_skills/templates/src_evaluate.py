"""Inputs to `skore.evaluate`.

Holds only the objects passed to `skore.evaluate(...)`:

- `splitter` — the cross-validator,
- optional metric overrides (skore picks task-appropriate defaults
  otherwise).

The evaluation itself — running `skore.evaluate`, opening a project,
persisting the report — happens in the experiment scripts, not here.
"""

from __future__ import annotations

# Pick the cross-validator from the structural facts of the data
# (grouping, time ordering, class balance).
splitter = None  # e.g., KFold(n_splits=5, shuffle=True, random_state=0)
