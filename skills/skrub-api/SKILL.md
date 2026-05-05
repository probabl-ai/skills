---
name: skrub-api
description: Discover the public API of the skrub package — top-level estimators, joiners, the DataOps lazy-pipeline framework, column selectors, datasets, and configuration. Use when you need to know what skrub exposes, what a class/function does, its signature, and where it lives, without grepping the source.
---

# skrub-api

Reference index for skrub's public API. Each topic below has a dedicated file under `references/` listing every public symbol with its import path, signature, and one-line description.

Only public API is documented (anything reachable from `skrub`, `skrub.selectors`, `skrub.datasets`, or `skrub.core` via `__all__`). Do not infer the existence of private helpers from this skill — read the source for those.

## When to load a reference file

Read the file that matches the user's question. Don't preemptively load all of them.

| Topic | File | Load when the user mentions… |
|---|---|---|
| Top-level overview | `references/overview.md` | "what does skrub export", "which transformer should I use", first contact with the API |
| Single-column encoders | `references/encoders.md` | `DatetimeEncoder`, `GapEncoder`, `MinHashEncoder`, `SimilarityEncoder`, `StringEncoder`, `TextEncoder`, `ToCategorical`, `ToDatetime`, `ToFloat`, `SquashingScaler`, `DropUninformative` |
| Joiners | `references/joiners.md` | `Joiner`, `fuzzy_join`, `InterpolationJoiner`, `AggJoiner`, `MultiAggJoiner`, `AggTarget` |
| Vectorizers & pipelines | `references/vectorizers.md` | `TableVectorizer`, `Cleaner`, `tabular_pipeline` |
| Column selection / wrapping | `references/column_ops.md` | `SelectCols`, `DropCols`, `Drop`, `ApplyToCols` |
| `skrub.selectors` module | `references/selectors.md` | `s.numeric()`, `s.glob(...)`, building selector expressions |
| DataOps (lazy plans) | `references/data_ops.md` | `DataOp`, `var`, `X`, `y`, `.skb` namespace, `deferred`, `as_data_op`, `eval_mode` |
| Learners & tuning | `references/learners.md` | `SkrubLearner`, `ParamSearch`, `OptunaParamSearch`, `cross_validate`, `choose_*`, `optional` |
| Reporting | `references/reporting.md` | `TableReport`, `patch_display`, `unpatch_display`, `column_associations` |
| Configuration | `references/config.md` | `get_config`, `set_config`, `config_context` |
| Datasets | `references/datasets.md` | `fetch_*`, `toy_orders`, `toy_products`, `make_deduplication_data`, `get_data_dir` |
| Misc utilities | `references/misc.md` | `to_datetime` (function), `deduplicate` (function) |
| `skrub.core` | `references/core.md` | Building a custom `SingleColumnTransformer`, `RejectColumn` |

## How to use this skill

1. Identify the topic from the user's question and read the matching file (or `overview.md` if you're unsure).
2. Quote the signature and one-line description from the reference. If the user needs more (parameter semantics, return type, examples), fall back to the source under `skrub/` or call `help(...)` in the dev environment (`pixi run -e dev python -c "..."`).
3. The reference files are auto-generatable from `__all__` and `inspect.signature` — if a symbol is missing here but present in `skrub.__all__`, the reference is stale; update it rather than improvising.

## Conventions used in reference files

- Each entry: `### name` → import line → `Signature:` → one-line description.
- `class` vs `function` is noted in the heading.
- Keyword-only markers (`*`) and defaults are preserved verbatim from `inspect.signature`.
- Long sklearn-object defaults (e.g. `Pipeline(...)`, `OneHotEncoder(...)`) are abbreviated as `<...>` — check the source for the exact default if it matters.
