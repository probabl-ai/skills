# `skrub.selectors`

Composable column selectors for dataframes. Selectors can be combined with `&`, `|`, `-`, `~` and passed anywhere a column list is expected (e.g. `SelectCols`, `ApplyToCols`, `TableVectorizer.specific_transformers`).

```python
from skrub import selectors as s
```

## Base classes

### class `Selector`
**Signature:** `Selector()`

Base class for all selectors. Subclasses implement `_matches(col)` and may override `expand(df)`.

### class `Filter`
**Signature:** `Filter(predicate, args=None, kwargs=None, name=None, selector_repr=None)`

Selector that keeps columns for which `predicate(col, *args, **kwargs)` returns True. Built by `filter(...)`.

### class `NameFilter`
**Signature:** `NameFilter(predicate, args=None, kwargs=None, name=None, selector_repr=None)`

Like `Filter` but the predicate receives the column **name** instead of the column object. Built by `filter_names(...)`.

## Constructors

### function `all`
**Signature:** `all()`

Select all columns.

### function `cols`
**Signature:** `cols(*columns)`

Select columns by exact name. Raises if a name is missing from the dataframe (when used standalone).

### function `filter`
**Signature:** `filter(predicate, *args, **kwargs)`

Select columns for which `predicate(col, *args, **kwargs)` returns True.

### function `filter_names`
**Signature:** `filter_names(predicate, *args, **kwargs)`

Select columns based on their name (predicate receives the name string).

### function `inv`
**Signature:** `inv(obj)`

Invert a selector. Equivalent to the `~` operator.

### function `make_selector`
**Signature:** `make_selector(obj)`

Coerce a selector, column name, or list of names into a `Selector`.

### function `select`
**Signature:** `select(df, selector)`

Apply a selector to a dataframe and return the resulting dataframe.

## Name-based selectors

### function `glob`
**Signature:** `glob(pattern)`

Select columns by name with Unix shell style 'glob' pattern (e.g. `"price_*"`).

### function `regex`
**Signature:** `regex(pattern, flags=0)`

Select columns by name with a regular expression.

## Dtype selectors

### function `numeric`
**Signature:** `numeric()`

Select columns with a numeric data type (integer, float, …).

### function `integer`
**Signature:** `integer()`

Select columns with an integer data type.

### function `float`
**Signature:** `float()`

Select columns with a floating-point data type.

### function `any_date`
**Signature:** `any_date()`

Select columns with a Date or Datetime data type.

### function `categorical`
**Signature:** `categorical()`

Select columns with a Categorical (or polars Enum) data type.

### function `string`
**Signature:** `string()`

Select columns with a String data type.

### function `boolean`
**Signature:** `boolean()`

Select columns with a Boolean data type.

## Content-based selectors

### function `cardinality_below`
**Signature:** `cardinality_below(threshold)`

Select columns whose cardinality (number of unique values) is strictly below `threshold`.

### function `has_nulls`
**Signature:** `has_nulls(proportion=0.0)`

Select columns that contain at least one null value (or more than `proportion` nulls).

## Composition

```python
from skrub import selectors as s

# Numeric columns OR columns named "id_*"
sel = s.numeric() | s.glob("id_*")

# All except boolean
sel = s.all() - s.boolean()

# Equivalent inversion
sel = ~s.boolean()
```

`__all__ = ['Filter', 'NameFilter', 'Selector', 'all', 'cols', 'filter', 'filter_names',
'inv', 'make_selector', 'select', 'glob', 'regex', 'numeric', 'integer', 'float',
'any_date', 'categorical', 'string', 'boolean', 'cardinality_below', 'has_nulls']`
