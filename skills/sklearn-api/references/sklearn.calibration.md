# `sklearn.calibration`

_Probability calibration._

### `CalibratedClassifierCV` <sub>class</sub>

```python
CalibratedClassifierCV(estimator=None, *, method='sigmoid', cv=None, n_jobs=None, ensemble='auto')
```

Calibrate probabilities using isotonic, sigmoid, or temperature scaling.

### `calibration_curve` <sub>function</sub>

```python
calibration_curve(y_true, y_prob, *, pos_label=None, n_bins=5, strategy='uniform')
```

Compute true and predicted probabilities for a calibration curve.

## Visualization

### `CalibrationDisplay` <sub>class</sub>

```python
CalibrationDisplay(prob_true, prob_pred, y_prob, *, estimator_name=None, pos_label=None)
```

Calibration curve (also known as reliability diagram) visualization.
