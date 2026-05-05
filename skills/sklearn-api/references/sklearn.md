# `sklearn`

_Settings and information tools._

### `config_context` <sub>function</sub>

```python
config_context(*, assume_finite=None, working_memory=None, print_changed_only=None,
    display=None, pairwise_dist_chunk_size=None, enable_cython_pairwise_dist=None,
    array_api_dispatch=None, transform_output=None, enable_metadata_routing=None,
    skip_parameter_validation=None)
```

Context manager to temporarily change the global scikit-learn configuration.

### `get_config` <sub>function</sub>

```python
get_config()
```

Retrieve the current scikit-learn configuration.

### `set_config` <sub>function</sub>

```python
set_config(assume_finite=None, working_memory=None, print_changed_only=None, display=None,
    pairwise_dist_chunk_size=None, enable_cython_pairwise_dist=None, array_api_dispatch=None,
    transform_output=None, enable_metadata_routing=None, skip_parameter_validation=None)
```

Set global scikit-learn configuration.

### `show_versions` <sub>function</sub>

```python
show_versions()
```

Print useful debugging information.
