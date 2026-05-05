---
name: sklearn-api
description: Look up the public API surface of any scikit-learn module — names, signatures, and one-line summaries. Use whenever you need to know what's exported from `sklearn.X`, recall a class/function signature, find the right estimator/metric/utility for a task, or check whether something is part of the public API. The reference is generated from `doc/api_reference.py`, so it matches what appears on the official docs site.
allowed-tools:
  - Read
  - Bash(ls *)
  - Bash(grep *)
---

# sklearn-api — scikit-learn public API reference

This skill is a flat, file-per-module index of scikit-learn's public API. Each
file under `references/` lists the names that the documentation site exposes
for one module, with their signature and a one-line summary pulled from the
docstring.

**The references are the source of truth for "is X public?"** If a name is
not in the relevant `references/sklearn.<module>.md`, treat it as private —
even if it's importable. The list is generated from `doc/api_reference.py`,
which is what gets rendered on scikit-learn.org.

## How to use

1. Identify the module the user is asking about (or that you need to recall).
2. Read `references/sklearn.<module>.md`. For the top-level `sklearn`
   namespace itself (e.g. `set_config`), read `references/sklearn.md`.
3. If you don't know which module owns a name, `grep` across the references:

   ```bash
   grep -l "^### \`<Name>\`" .claude/skills/sklearn-api/references/
   ```

4. The reference gives you the signature and a one-liner. For full parameter
   docs, examples, or attributes, read the actual source under `sklearn/` —
   the reference is for *discovery*, not for replacing the docstring.

## Available module references

Top-level:

- `sklearn.md` — `config_context`, `get_config`, `set_config`, `show_versions`

Core building blocks:

- `sklearn.base.md` — base classes and mixins (`BaseEstimator`, `*Mixin`, `clone`)
- `sklearn.exceptions.md` — warning / error classes
- `sklearn.pipeline.md` — `Pipeline`, `FeatureUnion`, `make_pipeline`
- `sklearn.compose.md` — `ColumnTransformer`, `TransformedTargetRegressor`
- `sklearn.frozen.md` — `FrozenEstimator`
- `sklearn.experimental.md` — opt-in flags for experimental features

Estimators by family:

- `sklearn.linear_model.md` — linear / logistic / GLM / robust regressors
- `sklearn.svm.md` — SVC, SVR, NuSVC, LinearSVC, OneClassSVM
- `sklearn.tree.md` — decision tree estimators + `export_*`
- `sklearn.ensemble.md` — random forests, gradient boosting, stacking, voting
- `sklearn.neighbors.md` — KNN, radius neighbors, KD/Ball tree, LOF
- `sklearn.naive_bayes.md` — Gaussian / Multinomial / Bernoulli / Categorical NB
- `sklearn.discriminant_analysis.md` — LDA, QDA
- `sklearn.gaussian_process.md` — GP regressor/classifier + kernels
- `sklearn.neural_network.md` — MLP, BernoulliRBM
- `sklearn.semi_supervised.md` — `LabelPropagation`, `LabelSpreading`, `SelfTrainingClassifier`
- `sklearn.dummy.md` — `DummyClassifier`, `DummyRegressor`
- `sklearn.kernel_ridge.md` — `KernelRidge`
- `sklearn.isotonic.md` — `IsotonicRegression` + helpers
- `sklearn.calibration.md` — `CalibratedClassifierCV`, `CalibrationDisplay`
- `sklearn.multiclass.md` / `sklearn.multioutput.md` — meta-estimators

Unsupervised:

- `sklearn.cluster.md` — KMeans, DBSCAN, HDBSCAN, hierarchical, spectral, etc.
- `sklearn.mixture.md` — `GaussianMixture`, `BayesianGaussianMixture`
- `sklearn.decomposition.md` — PCA, NMF, ICA, dictionary learning, LDA
- `sklearn.cross_decomposition.md` — PLS family, CCA
- `sklearn.manifold.md` — TSNE, UMAP-style (Isomap, LLE, MDS, SpectralEmbedding)
- `sklearn.covariance.md` — robust / shrinkage covariance estimators
- `sklearn.random_projection.md` — Gaussian / sparse random projections

Data prep & feature work:

- `sklearn.preprocessing.md` — scalers, encoders, polynomial, splines, target encoding
- `sklearn.impute.md` — `SimpleImputer`, `IterativeImputer`, `KNNImputer`, `MissingIndicator`
- `sklearn.feature_extraction.md` — dict/hash vectorizers + `image.*` + `text.*` submodules
- `sklearn.feature_selection.md` — filter / wrapper / model-based selection
- `sklearn.kernel_approximation.md` — Nystroem, RBFSampler, etc.

Evaluation & selection:

- `sklearn.metrics.md` — every scorer, classification/regression/clustering metric, `*Display`, `pairwise.*`
- `sklearn.model_selection.md` — splitters, search CV, `cross_val_*`, learning/validation curves
- `sklearn.inspection.md` — `permutation_importance`, partial dependence, `*Display`

Data:

- `sklearn.datasets.md` — `load_*`, `fetch_*`, `make_*`, `dump_svmlight_file`

Utilities:

- `sklearn.utils.md` — validation, parallel, sparse helpers, multiclass utils, `Bunch`, fixes, etc.

## Tips for common questions

- **"What estimators does sklearn ship for X?"** — open the family file
  (`sklearn.linear_model.md`, `sklearn.ensemble.md`, ...) and scan the section
  headings; they group estimators by sub-family.
- **"What scorer / metric should I use for X?"** — `sklearn.metrics.md` is
  segmented into Classification / Regression / Clustering / Pairwise / Plotting
  sections.
- **"Is this thing public?"** — search the references. If it's not there, it's
  not part of the documented API.
- **Submodule entries** (e.g. `image.PatchExtractor` inside
  `sklearn.feature_extraction.md`, or `pairwise.cosine_similarity` inside
  `sklearn.metrics.md`) live under their parent module's reference file; the
  prefix tells you the actual import path.

## Regenerating

The reference files are generated, not hand-written. After a public-API
change in scikit-learn (anything that touches `doc/api_reference.py`,
constructor signatures, or first-line docstrings), re-run:

```bash
pixi run -e dev python .claude/skills/sklearn-api/generate_references.py
```

The generator walks `API_REFERENCE` from `doc/api_reference.py`, resolves each
name via `importlib`, formats `inspect.signature(...)`, and writes one markdown
file per module key into `references/`.
