"""Feature functions and transformers.

Owns: pure-Python feature functions (stateless, attached to the
pipeline via `.skb.apply_func`) and sklearn-compatible transformers
(stateful, attached via `.skb.apply`). Composition into the learner
happens in `pipeline.py`. See `build-ml-pipeline` for declarative
mechanics.
"""

from __future__ import annotations
