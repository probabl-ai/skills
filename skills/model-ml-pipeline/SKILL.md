---
name: model-ml-pipeline
description: >
  Coordinate the model workflow after an experiment design is
  approved: build the declaration, evaluate it, then smoke-test it.
  Trigger for an end-to-end modeling implementation, not a single
  action already owned by a child skill.
---

# Model ML Pipeline

This meta skill owns ordering, not implementation details:

1. `build-ml-pipeline` — declare the skrub DataOps learner.
2. `evaluate-ml-pipeline` — choose the leakage-safe splitter and
   write evaluation in the experiment script.
3. `smoke-test-ml-pipeline` — verify prediction on held-out/future
   input and exact row-count preservation.

Before new library symbols are written, use
`python -m skore_skills api get <dotted>`.

## Stop conditions

- If `journal/NN_<short>.md` is missing, create its packaged shell
  with `python -m skore_skills scaffold --journal --stem
  <NN_short>`. Only after that command succeeds, fill the shell's
  question, motivation, method, and risks; then stop for user
  approval. If the CLI cannot run this turn, name the command and
  stop without recreating the template from memory.
- Require that design note to be approved before code.
- Preserve identical stems across design, experiment, smoke, audit.
- Do not replace skrub DataOps with bare sklearn Pipeline.
- Do not persist a result as done while smoke tests fail.
- Do not duplicate child-skill methodology in this dispatcher.

This first version is intentionally narrow pending joint review.
