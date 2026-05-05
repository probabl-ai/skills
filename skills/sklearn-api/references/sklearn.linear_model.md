# `sklearn.linear_model`

_Generalized linear models._

## Linear classifiers

### `LogisticRegression` <sub>class</sub>

```python
LogisticRegression(penalty='deprecated', *, C=1.0, l1_ratio=0.0, dual=False, tol=0.0001,
    fit_intercept=True, intercept_scaling=1, class_weight=None, random_state=None,
    solver='lbfgs', max_iter=100, verbose=0, warm_start=False, n_jobs=None)
```

Logistic Regression (aka logit, MaxEnt) classifier.

### `LogisticRegressionCV` <sub>class</sub>

```python
LogisticRegressionCV(*, Cs=10, l1_ratios='warn', fit_intercept=True, cv=None, dual=False,
    penalty='deprecated', scoring=None, solver='lbfgs', tol=0.0001, max_iter=100,
    class_weight=None, n_jobs=None, verbose=0, refit=True, intercept_scaling=1.0,
    random_state=None, use_legacy_attributes='warn')
```

Logistic Regression CV (aka logit, MaxEnt) classifier.

### `PassiveAggressiveClassifier` <sub>class</sub>

```python
PassiveAggressiveClassifier(*, C=1.0, fit_intercept=True, max_iter=1000, tol=0.001,
    early_stopping=False, validation_fraction=0.1, n_iter_no_change=5, shuffle=True, verbose=0,
    loss='hinge', n_jobs=None, random_state=None, warm_start=False, class_weight=None,
    average=False)
```

Passive Aggressive Classifier.

### `Perceptron` <sub>class</sub>

```python
Perceptron(*, penalty=None, alpha=0.0001, l1_ratio=0.15, fit_intercept=True, max_iter=1000,
    tol=0.001, shuffle=True, verbose=0, eta0=1.0, n_jobs=None, random_state=0,
    early_stopping=False, validation_fraction=0.1, n_iter_no_change=5, class_weight=None,
    warm_start=False)
```

Linear perceptron classifier.

### `RidgeClassifier` <sub>class</sub>

```python
RidgeClassifier(alpha=1.0, *, fit_intercept=True, copy_X=True, max_iter=None, tol=0.0001,
    class_weight=None, solver='auto', positive=False, random_state=None)
```

Classifier using Ridge regression.

### `RidgeClassifierCV` <sub>class</sub>

```python
RidgeClassifierCV(alphas=(0.1, 1.0, 10.0), *, fit_intercept=True, scoring=None, cv=None,
    class_weight=None, store_cv_results=False)
```

Ridge classifier with built-in cross-validation.

### `SGDClassifier` <sub>class</sub>

```python
SGDClassifier(loss='hinge', *, penalty='l2', alpha=0.0001, l1_ratio=0.15, fit_intercept=True,
    max_iter=1000, tol=0.001, shuffle=True, verbose=0, epsilon=0.1, n_jobs=None,
    random_state=None, learning_rate='optimal', eta0=0.01, power_t=0.5, early_stopping=False,
    validation_fraction=0.1, n_iter_no_change=5, class_weight=None, warm_start=False,
    average=False)
```

Linear classifiers (SVM, logistic regression, etc.) with SGD training.

### `SGDOneClassSVM` <sub>class</sub>

```python
SGDOneClassSVM(nu=0.5, fit_intercept=True, max_iter=1000, tol=0.001, shuffle=True, verbose=0,
    random_state=None, learning_rate='optimal', eta0=0.01, power_t=0.5, warm_start=False,
    average=False)
```

Solves linear One-Class SVM using Stochastic Gradient Descent.

## Classical linear regressors

### `LinearRegression` <sub>class</sub>

```python
LinearRegression(*, fit_intercept=True, copy_X=True, tol=1e-06, n_jobs=None, positive=False)
```

Ordinary least squares Linear Regression.

### `Ridge` <sub>class</sub>

```python
Ridge(alpha=1.0, *, fit_intercept=True, copy_X=True, max_iter=None, tol=0.0001, solver='auto',
    positive=False, random_state=None)
```

Linear least squares with l2 regularization.

### `RidgeCV` <sub>class</sub>

```python
RidgeCV(alphas=(0.1, 1.0, 10.0), *, fit_intercept=True, scoring=None, cv=None, gcv_mode=None,
    store_cv_results=False, alpha_per_target=False)
```

Ridge regression with built-in cross-validation.

### `SGDRegressor` <sub>class</sub>

```python
SGDRegressor(loss='squared_error', *, penalty='l2', alpha=0.0001, l1_ratio=0.15,
    fit_intercept=True, max_iter=1000, tol=0.001, shuffle=True, verbose=0, epsilon=0.1,
    random_state=None, learning_rate='invscaling', eta0=0.01, power_t=0.25,
    early_stopping=False, validation_fraction=0.1, n_iter_no_change=5, warm_start=False,
    average=False)
```

Linear model fitted by minimizing a regularized empirical loss with SGD.

## Regressors with variable selection

### `ElasticNet` <sub>class</sub>

```python
ElasticNet(alpha=1.0, *, l1_ratio=0.5, fit_intercept=True, precompute=False, max_iter=1000,
    copy_X=True, tol=0.0001, warm_start=False, positive=False, random_state=None,
    selection='cyclic')
```

Linear regression with combined L1 and L2 priors as regularizer.

### `ElasticNetCV` <sub>class</sub>

```python
ElasticNetCV(*, l1_ratio=0.5, eps=0.001, n_alphas='deprecated', alphas='warn',
    fit_intercept=True, precompute='auto', max_iter=1000, tol=0.0001, cv=None, copy_X=True,
    verbose=0, n_jobs=None, positive=False, random_state=None, selection='cyclic')
```

Elastic Net model with iterative fitting along a regularization path.

### `Lars` <sub>class</sub>

```python
Lars(*, fit_intercept=True, verbose=False, precompute='auto', n_nonzero_coefs=500,
    eps=np.float64(2.220446049250313e-16), copy_X=True, fit_path=True, jitter=None,
    random_state=None)
```

Least Angle Regression model a.k.a. LAR.

### `LarsCV` <sub>class</sub>

```python
LarsCV(*, fit_intercept=True, verbose=False, max_iter=500, precompute='auto', cv=None,
    max_n_alphas=1000, n_jobs=None, eps=np.float64(2.220446049250313e-16), copy_X=True)
```

Cross-validated Least Angle Regression model.

### `Lasso` <sub>class</sub>

```python
Lasso(alpha=1.0, *, fit_intercept=True, precompute=False, copy_X=True, max_iter=1000,
    tol=0.0001, warm_start=False, positive=False, random_state=None, selection='cyclic')
```

Linear Model trained with L1 prior as regularizer (aka the Lasso).

### `LassoCV` <sub>class</sub>

```python
LassoCV(*, eps=0.001, n_alphas='deprecated', alphas='warn', fit_intercept=True,
    precompute='auto', max_iter=1000, tol=0.0001, copy_X=True, cv=None, verbose=False,
    n_jobs=None, positive=False, random_state=None, selection='cyclic')
```

Lasso linear model with iterative fitting along a regularization path.

### `LassoLars` <sub>class</sub>

```python
LassoLars(alpha=1.0, *, fit_intercept=True, verbose=False, precompute='auto', max_iter=500,
    eps=np.float64(2.220446049250313e-16), copy_X=True, fit_path=True, positive=False,
    jitter=None, random_state=None)
```

Lasso model fit with Least Angle Regression a.k.a. Lars.

### `LassoLarsCV` <sub>class</sub>

```python
LassoLarsCV(*, fit_intercept=True, verbose=False, max_iter=500, precompute='auto', cv=None,
    max_n_alphas=1000, n_jobs=None, eps=np.float64(2.220446049250313e-16), copy_X=True,
    positive=False)
```

Cross-validated Lasso, using the LARS algorithm.

### `LassoLarsIC` <sub>class</sub>

```python
LassoLarsIC(criterion='aic', *, fit_intercept=True, verbose=False, precompute='auto',
    max_iter=500, eps=np.float64(2.220446049250313e-16), copy_X=True, positive=False,
    noise_variance=None)
```

Lasso model fit with Lars using BIC or AIC for model selection.

### `OrthogonalMatchingPursuit` <sub>class</sub>

```python
OrthogonalMatchingPursuit(*, n_nonzero_coefs=None, tol=None, fit_intercept=True, precompute='auto')
```

Orthogonal Matching Pursuit model (OMP).

### `OrthogonalMatchingPursuitCV` <sub>class</sub>

```python
OrthogonalMatchingPursuitCV(*, copy=True, fit_intercept=True, max_iter=None, cv=None,
    n_jobs=None, verbose=False)
```

Cross-validated Orthogonal Matching Pursuit model (OMP).

## Bayesian regressors

### `ARDRegression` <sub>class</sub>

```python
ARDRegression(*, max_iter=300, tol=0.001, alpha_1=1e-06, alpha_2=1e-06, lambda_1=1e-06,
    lambda_2=1e-06, compute_score=False, threshold_lambda=10000.0, fit_intercept=True,
    copy_X=True, verbose=False)
```

Bayesian ARD regression.

### `BayesianRidge` <sub>class</sub>

```python
BayesianRidge(*, max_iter=300, tol=0.001, alpha_1=1e-06, alpha_2=1e-06, lambda_1=1e-06,
    lambda_2=1e-06, alpha_init=None, lambda_init=None, compute_score=False, fit_intercept=True,
    copy_X=True, verbose=False)
```

Bayesian ridge regression.

## Multi-task linear regressors with variable selection

### `MultiTaskElasticNet` <sub>class</sub>

```python
MultiTaskElasticNet(alpha=1.0, *, l1_ratio=0.5, fit_intercept=True, copy_X=True, max_iter=1000,
    tol=0.0001, warm_start=False, random_state=None, selection='cyclic')
```

Multi-task ElasticNet model trained with L1/L2 mixed-norm as regularizer.

### `MultiTaskElasticNetCV` <sub>class</sub>

```python
MultiTaskElasticNetCV(*, l1_ratio=0.5, eps=0.001, n_alphas='deprecated', alphas='warn',
    fit_intercept=True, max_iter=1000, tol=0.0001, cv=None, copy_X=True, verbose=0, n_jobs=None,
    random_state=None, selection='cyclic')
```

Multi-task L1/L2 ElasticNet with built-in cross-validation.

### `MultiTaskLasso` <sub>class</sub>

```python
MultiTaskLasso(alpha=1.0, *, fit_intercept=True, copy_X=True, max_iter=1000, tol=0.0001,
    warm_start=False, random_state=None, selection='cyclic')
```

Multi-task Lasso model trained with L1/L2 mixed-norm as regularizer.

### `MultiTaskLassoCV` <sub>class</sub>

```python
MultiTaskLassoCV(*, eps=0.001, n_alphas='deprecated', alphas='warn', fit_intercept=True,
    max_iter=1000, tol=0.0001, copy_X=True, cv=None, verbose=False, n_jobs=None,
    random_state=None, selection='cyclic')
```

Multi-task Lasso model trained with L1/L2 mixed-norm as regularizer.

## Outlier-robust regressors

### `HuberRegressor` <sub>class</sub>

```python
HuberRegressor(*, epsilon=1.35, max_iter=100, alpha=0.0001, warm_start=False,
    fit_intercept=True, tol=1e-05)
```

L2-regularized linear regression model that is robust to outliers.

### `QuantileRegressor` <sub>class</sub>

```python
QuantileRegressor(*, quantile=0.5, alpha=1.0, fit_intercept=True, solver='highs',
    solver_options=None)
```

Linear regression model that predicts conditional quantiles.

### `RANSACRegressor` <sub>class</sub>

```python
RANSACRegressor(estimator=None, *, min_samples=None, residual_threshold=None,
    is_data_valid=None, is_model_valid=None, max_trials=100, max_skips=inf, stop_n_inliers=inf,
    stop_score=inf, stop_probability=0.99, loss='absolute_error', random_state=None)
```

RANSAC (RANdom SAmple Consensus) algorithm.

### `TheilSenRegressor` <sub>class</sub>

```python
TheilSenRegressor(*, fit_intercept=True, max_subpopulation=10000.0, n_subsamples=None,
    max_iter=300, tol=0.001, random_state=None, n_jobs=None, verbose=False)
```

Theil-Sen Estimator: robust multivariate regression model.

## Generalized linear models (GLM) for regression

### `GammaRegressor` <sub>class</sub>

```python
GammaRegressor(*, alpha=1.0, fit_intercept=True, solver='lbfgs', max_iter=100, tol=0.0001,
    warm_start=False, verbose=0)
```

Generalized Linear Model with a Gamma distribution.

### `PoissonRegressor` <sub>class</sub>

```python
PoissonRegressor(*, alpha=1.0, fit_intercept=True, solver='lbfgs', max_iter=100, tol=0.0001,
    warm_start=False, verbose=0)
```

Generalized Linear Model with a Poisson distribution.

### `TweedieRegressor` <sub>class</sub>

```python
TweedieRegressor(*, power=0.0, alpha=1.0, fit_intercept=True, link='auto', solver='lbfgs',
    max_iter=100, tol=0.0001, warm_start=False, verbose=0)
```

Generalized Linear Model with a Tweedie distribution.

## Miscellaneous

### `PassiveAggressiveRegressor` <sub>class</sub>

```python
PassiveAggressiveRegressor(*, C=1.0, fit_intercept=True, max_iter=1000, tol=0.001,
    early_stopping=False, validation_fraction=0.1, n_iter_no_change=5, shuffle=True, verbose=0,
    loss='epsilon_insensitive', epsilon=0.1, random_state=None, warm_start=False, average=False)
```

Passive Aggressive Regressor.

### `enet_path` <sub>function</sub>

```python
enet_path(X, y, *, l1_ratio=0.5, eps=0.001, n_alphas=100, alphas=None, precompute='auto',
    Xy=None, copy_X=True, coef_init=None, verbose=False, return_n_iter=False, positive=False,
    check_input=True, **params)
```

Compute elastic net path with coordinate descent.

### `lars_path` <sub>function</sub>

```python
lars_path(X, y, Xy=None, *, Gram=None, max_iter=500, alpha_min=0, method='lar', copy_X=True,
    eps=np.float64(2.220446049250313e-16), copy_Gram=True, verbose=0, return_path=True,
    return_n_iter=False, positive=False)
```

Compute Least Angle Regression or Lasso path using the LARS algorithm.

### `lars_path_gram` <sub>function</sub>

```python
lars_path_gram(Xy, Gram, *, n_samples, max_iter=500, alpha_min=0, method='lar', copy_X=True,
    eps=np.float64(2.220446049250313e-16), copy_Gram=True, verbose=0, return_path=True,
    return_n_iter=False, positive=False)
```

The lars_path in the sufficient stats mode.

### `lasso_path` <sub>function</sub>

```python
lasso_path(X, y, *, eps=0.001, n_alphas=100, alphas=None, precompute='auto', Xy=None,
    copy_X=True, coef_init=None, verbose=False, return_n_iter=False, positive=False, **params)
```

Compute Lasso path with coordinate descent.

### `orthogonal_mp` <sub>function</sub>

```python
orthogonal_mp(X, y, *, n_nonzero_coefs=None, tol=None, precompute=False, copy_X=True,
    return_path=False, return_n_iter=False)
```

Orthogonal Matching Pursuit (OMP).

### `orthogonal_mp_gram` <sub>function</sub>

```python
orthogonal_mp_gram(Gram, Xy, *, n_nonzero_coefs=None, tol=None, norms_squared=None,
    copy_Gram=True, copy_Xy=True, return_path=False, return_n_iter=False)
```

Gram Orthogonal Matching Pursuit (OMP).

### `ridge_regression` <sub>function</sub>

```python
ridge_regression(X, y, alpha, *, sample_weight=None, solver='auto', max_iter=None, tol=0.0001,
    verbose=0, positive=False, random_state=None, return_n_iter=False, return_intercept=False,
    check_input=True)
```

Solve the ridge equation by the method of normal equations.
