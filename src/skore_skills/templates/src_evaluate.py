"""Unused splitter stub.

``skore.evaluate`` and ``project.put`` live in
``experiments/NN_*.py``, not here. The locked cross-validator sits
on the DataOp. Do not pass ``splitter=`` from the experiment
script. ``None`` here is not a holdout by itself: a holdout is a
marker with no ``cv``. See
``evaluate-ml-pipeline/references/metadata-routing.md``.
"""

from __future__ import annotations

splitter = None
