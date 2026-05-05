# Skills

A collection of skills for ML experimentation in Python, organized around
[skrub](https://skrub-data.org/), [scikit-learn](https://scikit-learn.org/),
and [skore](https://skore.probabl.ai/).

## ML pipeline lifecycle

| Skill | Description |
| --- | --- |
| [build-ml-pipeline](skills/build-ml-pipeline/SKILL.md) | Declare the pipeline from data source to predictor as a skrub DataOps graph. Stops at the declared object — no fit, split, tuning, or persistence. |
| [evaluate-ml-pipeline](skills/evaluate-ml-pipeline/SKILL.md) | Evaluate a single sklearn-compatible learner: pick the right entry point (`skore.evaluate` first), the right cross-validator, and consume report metadata. |

## Iteration loop

| Skill | Description |
| --- | --- |
| [iterate-ml-experiment](skills/iterate-ml-experiment/SKILL.md) | Drives the iteration loop on top of an ML workspace — owns `plan/PLAN.md` and per-experiment design notes, and dispatches to a sourcing strategy below. |
| [iterate-from-diagnostic](skills/iterate-from-diagnostic/SKILL.md) | Source the next experiment by inspecting the previous skore report — residuals, calibration, per-slice metrics. |
| [iterate-from-literature](skills/iterate-from-literature/SKILL.md) | Source the next experiment by searching papers, blog posts, and library docs for applicable techniques. |
| [iterate-from-methodology](skills/iterate-from-methodology/SKILL.md) | Source the next experiment by auditing the methodology of previous runs — split, leakage, target encoding, sample size, metric, baseline. |
| [iterate-from-user](skills/iterate-from-user/SKILL.md) | Source the next experiment from the user directly, or from a GitHub issue / spec / notes they point at. |

## Workspace and tooling

| Skill | Description |
| --- | --- |
| [organize-ml-workspace](skills/organize-ml-workspace/SKILL.md) | Decide where files live: reusable code, per-experiment scripts (jupytext-style `# %%`), reports. One file per experiment. |
| [python-code-style](skills/python-code-style/SKILL.md) | Place the project's `ruff.toml` template and run ruff (lint + format) on touched files. numpydoc for docstrings. |
| [python-env-manager](skills/python-env-manager/SKILL.md) | Detect the project's env manager (pixi / uv / poetry / hatch / conda / pip+venv) and issue the right install command. Defaults to pixi when bootstrapping. |
| [data-science-python-stack](skills/data-science-python-stack/SKILL.md) | Opinionated one-library-per-job Python stack, organized into mandatory / user-choice / optional / transitive tiers. |

## API references

| Skill | Description |
| --- | --- |
| [sklearn-api](skills/sklearn-api/SKILL.md) | File-per-module index of scikit-learn's public API — names, signatures, and one-line summaries generated from `doc/api_reference.py`. |
| [skore-api](skills/skore-api/SKILL.md) | API reference for skore as an evaluation library: `evaluate`, the report types and their accessors, and `Project` for persisting and comparing runs. |
| [skrub-api](skills/skrub-api/SKILL.md) | Reference index for skrub's public API — top-level estimators, joiners, the DataOps framework, column selectors, datasets, configuration. |
