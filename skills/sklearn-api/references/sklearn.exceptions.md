# `sklearn.exceptions`

_Exceptions and warnings._

### `ConvergenceWarning` <sub>class</sub>


Custom warning to capture convergence problems

### `DataConversionWarning` <sub>class</sub>


Warning used to notify implicit data conversions happening in the code.

### `DataDimensionalityWarning` <sub>class</sub>


Custom warning to notify potential issues with data dimensionality.

### `EfficiencyWarning` <sub>class</sub>


Warning used to notify the user of inefficient computation.

### `FitFailedWarning` <sub>class</sub>


Warning class used if there is an error while fitting the estimator.

### `InconsistentVersionWarning` <sub>class</sub>

```python
InconsistentVersionWarning(*, estimator_name, current_sklearn_version, original_sklearn_version)
```

Warning raised when an estimator is unpickled with an inconsistent version.

### `NotFittedError` <sub>class</sub>


Exception class to raise if estimator is used before fitting.

### `UndefinedMetricWarning` <sub>class</sub>


Warning used when the metric is invalid

### `EstimatorCheckFailedWarning` <sub>class</sub>

```python
EstimatorCheckFailedWarning(*, estimator, check_name: str, exception: Exception, status: str,
    expected_to_fail: bool, expected_to_fail_reason: str)
```

Warning raised when an estimator check from the common tests fails.
