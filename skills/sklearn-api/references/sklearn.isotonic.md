# `sklearn.isotonic`

_Isotonic regression._

### `IsotonicRegression` <sub>class</sub>

```python
IsotonicRegression(*, y_min=None, y_max=None, increasing=True, out_of_bounds='nan')
```

Isotonic regression model.

### `check_increasing` <sub>function</sub>

```python
check_increasing(x, y)
```

Determine whether y is monotonically correlated with x.

### `isotonic_regression` <sub>function</sub>

```python
isotonic_regression(y, *, sample_weight=None, y_min=None, y_max=None, increasing=True)
```

Solve the isotonic regression model.
