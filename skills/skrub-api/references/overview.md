# skrub — top-level public API

Everything below is reachable as `skrub.<name>` (i.e. listed in `skrub.__all__`).

## Submodules

- `skrub.selectors` — column selectors. See `references/selectors.md`.
- `skrub.datasets` — example datasets and data-dir helpers. See `references/datasets.md`.
- `skrub.core` — base classes for extending skrub (e.g. `SingleColumnTransformer`). See `references/core.md`.

## Top-level symbols by topic

### Single-column encoders / cleaners → `references/encoders.md`
`DatetimeEncoder`, `ToDatetime`, `GapEncoder`, `MinHashEncoder`, `SimilarityEncoder`,
`StringEncoder`, `TextEncoder`, `ToCategorical`, `ToFloat`, `SquashingScaler`,
`DropUninformative`

### Joiners → `references/joiners.md`
`Joiner`, `fuzzy_join`, `InterpolationJoiner`, `AggJoiner`, `MultiAggJoiner`, `AggTarget`

### Whole-table vectorizers / pipelines → `references/vectorizers.md`
`TableVectorizer`, `Cleaner`, `tabular_pipeline`

### Column-level selection & wrapping → `references/column_ops.md`
`SelectCols`, `DropCols`, `Drop`, `ApplyToCols`

### DataOps lazy framework → `references/data_ops.md`
`DataOp`, `var`, `X`, `y`, `as_data_op`, `deferred`, `eval_mode`

### Learners & hyperparameter tuning → `references/learners.md`
`SkrubLearner`, `ParamSearch`, `OptunaParamSearch`, `cross_validate`,
`choose_from`, `choose_float`, `choose_int`, `choose_bool`, `optional`

### Reporting → `references/reporting.md`
`TableReport`, `patch_display`, `unpatch_display`, `column_associations`

### Configuration → `references/config.md`
`get_config`, `set_config`, `config_context`

### Misc utilities → `references/misc.md`
`to_datetime` (function), `deduplicate` (function)

## Naming conventions

- **Capitalized, no underscore** (`TableVectorizer`, `Joiner`, `GapEncoder`) — sklearn-style estimator classes implementing `fit` / `transform` / `fit_transform`.
- **`To<Type>`** (`ToDatetime`, `ToCategorical`, `ToFloat`) — single-column casters; reject columns they don't apply to.
- **`<Verb>Cols`** (`SelectCols`, `DropCols`) — whole-table column-level transformers.
- **lower_snake_case functions** (`fuzzy_join`, `to_datetime`, `deduplicate`, `column_associations`, `tabular_pipeline`) — eager helpers, not estimators.
- **`choose_*` / `optional`** — DataOps hyperparameter primitives.
