# `sklearn.tree`

_Decision trees._

### `DecisionTreeClassifier` <sub>class</sub>

```python
DecisionTreeClassifier(*, criterion='gini', splitter='best', max_depth=None,
    min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features=None,
    random_state=None, max_leaf_nodes=None, min_impurity_decrease=0.0, class_weight=None,
    ccp_alpha=0.0, monotonic_cst=None)
```

A decision tree classifier.

### `DecisionTreeRegressor` <sub>class</sub>

```python
DecisionTreeRegressor(*, criterion='squared_error', splitter='best', max_depth=None,
    min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features=None,
    random_state=None, max_leaf_nodes=None, min_impurity_decrease=0.0, ccp_alpha=0.0,
    monotonic_cst=None)
```

A decision tree regressor.

### `ExtraTreeClassifier` <sub>class</sub>

```python
ExtraTreeClassifier(*, criterion='gini', splitter='random', max_depth=None, min_samples_split=2,
    min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features='sqrt', random_state=None,
    max_leaf_nodes=None, min_impurity_decrease=0.0, class_weight=None, ccp_alpha=0.0,
    monotonic_cst=None)
```

An extremely randomized tree classifier.

### `ExtraTreeRegressor` <sub>class</sub>

```python
ExtraTreeRegressor(*, criterion='squared_error', splitter='random', max_depth=None,
    min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features=1.0,
    random_state=None, min_impurity_decrease=0.0, max_leaf_nodes=None, ccp_alpha=0.0,
    monotonic_cst=None)
```

An extremely randomized tree regressor.

## Exporting

### `export_graphviz` <sub>function</sub>

```python
export_graphviz(decision_tree, out_file=None, *, max_depth=None, feature_names=None,
    class_names=None, label='all', filled=False, leaves_parallel=False, impurity=True,
    node_ids=False, proportion=False, rotate=False, rounded=False, special_characters=False,
    precision=3, fontname='helvetica')
```

Export a decision tree in DOT format.

### `export_text` <sub>function</sub>

```python
export_text(decision_tree, *, feature_names=None, class_names=None, max_depth=10, spacing=3,
    decimals=2, show_weights=False)
```

Build a text report showing the rules of a decision tree.

## Plotting

### `plot_tree` <sub>function</sub>

```python
plot_tree(decision_tree, *, max_depth=None, feature_names=None, class_names=None, label='all',
    filled=False, impurity=True, node_ids=False, proportion=False, rounded=False, precision=3,
    ax=None, fontsize=None)
```

Plot a decision tree.
