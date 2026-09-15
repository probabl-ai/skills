---
name: model-ml-pipeline
description: >
  Canonical implement stage: build the declaration, then smoke-test
  it. Trigger for modeling implementation after an approved design
  note. Evaluate is a later loop stage, not this meta.
---

# Model ML Pipeline

This meta skill owns **build then smoke** only:

1. `build-ml-pipeline` — declare the skrub DataOps learner.
2. `smoke-test-ml-pipeline` — verify prediction on held-out/future
   input and exact row-count preservation.

Do not run `evaluate-ml-pipeline` in this stage. CV and metric
overrides wait for the evaluate stage.

G-DESIGN: require an approved `journal/NN_<short>.md` before code.
Preserve identical stems across design, experiment, smoke, audit.

Journal pairing stays a rule here: the experiment script matches
the design-note stem. After smoke passes, stop and ask triage.

Before new library symbols are written, use
`python -m skore_skills api get <dotted>`.

## Stop conditions

- Require an approved `journal/NN_<short>.md` before code.
- Preserve identical stems across design, experiment, smoke, audit.
- Do not replace skrub DataOps with bare sklearn Pipeline.
- Do not persist a result as done while smoke tests fail.
- Do not evaluate, pick splitters, or override metrics here.
- Do not duplicate child-skill methodology in this dispatcher.

This first version is intentionally narrow pending joint review.
