# `sklearn.datasets`

_Datasets._

## Loaders

### `clear_data_home` <sub>function</sub>

```python
clear_data_home(data_home=None)
```

Delete all the content of the data home cache.

### `dump_svmlight_file` <sub>function</sub>

```python
dump_svmlight_file(X, y, f, *, zero_based=True, comment=None, query_id=None, multilabel=False)
```

Dump the dataset in svmlight / libsvm file format.

### `fetch_20newsgroups` <sub>function</sub>

```python
fetch_20newsgroups(*, data_home=None, subset='train', categories=None, shuffle=True,
    random_state=42, remove=(), download_if_missing=True, return_X_y=False, n_retries=3,
    delay=1.0)
```

Load the filenames and data from the 20 newsgroups dataset (classification).

### `fetch_20newsgroups_vectorized` <sub>function</sub>

```python
fetch_20newsgroups_vectorized(*, subset='train', remove=(), data_home=None,
    download_if_missing=True, return_X_y=False, normalize=True, as_frame=False, n_retries=3,
    delay=1.0)
```

Load and vectorize the 20 newsgroups dataset (classification).

### `fetch_california_housing` <sub>function</sub>

```python
fetch_california_housing(*, data_home=None, download_if_missing=True, return_X_y=False,
    as_frame=False, n_retries=3, delay=1.0)
```

Load the California housing dataset (regression).

### `fetch_covtype` <sub>function</sub>

```python
fetch_covtype(*, data_home=None, download_if_missing=True, random_state=None, shuffle=False,
    return_X_y=False, as_frame=False, n_retries=3, delay=1.0)
```

Load the covertype dataset (classification).

### `fetch_file` <sub>function</sub>

```python
fetch_file(url, folder=None, local_filename=None, sha256=None, n_retries=3, delay=1)
```

Fetch a file from the web if not already present in the local folder.

### `fetch_kddcup99` <sub>function</sub>

```python
fetch_kddcup99(*, subset=None, data_home=None, shuffle=False, random_state=None, percent10=True,
    download_if_missing=True, return_X_y=False, as_frame=False, n_retries=3, delay=1.0)
```

Load the kddcup99 dataset (classification).

### `fetch_lfw_pairs` <sub>function</sub>

```python
fetch_lfw_pairs(*, subset='train', data_home=None, funneled=True, resize=0.5, color=False,
    slice_=(slice(70, 195, None), slice(78, 172, None)), download_if_missing=True, n_retries=3,
    delay=1.0)
```

Load the Labeled Faces in the Wild (LFW) pairs dataset (classification).

### `fetch_lfw_people` <sub>function</sub>

```python
fetch_lfw_people(*, data_home=None, funneled=True, resize=0.5, min_faces_per_person=0,
    color=False, slice_=(slice(70, 195, None), slice(78, 172, None)), download_if_missing=True,
    return_X_y=False, n_retries=3, delay=1.0)
```

Load the Labeled Faces in the Wild (LFW) people dataset (classification).

### `fetch_olivetti_faces` <sub>function</sub>

```python
fetch_olivetti_faces(*, data_home=None, shuffle=False, random_state=0, download_if_missing=True,
    return_X_y=False, n_retries=3, delay=1.0)
```

Load the Olivetti faces data-set from AT&T (classification).

### `fetch_openml` <sub>function</sub>

```python
fetch_openml(name: Optional[str] = None, *, version: Union[str, int] = 'active', data_id:
    Optional[int] = None, data_home: Union[str, os.PathLike, NoneType] = None, target_column:
    Union[str, List, NoneType] = 'default-target', cache: bool = True, return_X_y: bool = False,
    as_frame: Union[str, bool] = 'auto', n_retries: int = 3, delay: float = 1.0, parser: str =
    'auto', read_csv_kwargs: Optional[Dict] = None)
```

Fetch dataset from openml by name or dataset id.

### `fetch_rcv1` <sub>function</sub>

```python
fetch_rcv1(*, data_home=None, subset='all', download_if_missing=True, random_state=None,
    shuffle=False, return_X_y=False, n_retries=3, delay=1.0)
```

Load the RCV1 multilabel dataset (classification).

### `fetch_species_distributions` <sub>function</sub>

```python
fetch_species_distributions(*, data_home=None, download_if_missing=True, n_retries=3, delay=1.0)
```

Loader for species distribution dataset from Phillips et. al. (2006).

### `get_data_home` <sub>function</sub>

```python
get_data_home(data_home=None) -> str
```

Return the path of the scikit-learn data directory.

### `load_breast_cancer` <sub>function</sub>

```python
load_breast_cancer(*, return_X_y=False, as_frame=False)
```

Load and return the breast cancer Wisconsin dataset (classification).

### `load_diabetes` <sub>function</sub>

```python
load_diabetes(*, return_X_y=False, as_frame=False, scaled=True)
```

Load and return the diabetes dataset (regression).

### `load_digits` <sub>function</sub>

```python
load_digits(*, n_class=10, return_X_y=False, as_frame=False)
```

Load and return the digits dataset (classification).

### `load_files` <sub>function</sub>

```python
load_files(container_path, *, description=None, categories=None, load_content=True,
    shuffle=True, encoding=None, decode_error='strict', random_state=0, allowed_extensions=None)
```

Load text files with categories as subfolder names.

### `load_iris` <sub>function</sub>

```python
load_iris(*, return_X_y=False, as_frame=False)
```

Load and return the iris dataset (classification).

### `load_linnerud` <sub>function</sub>

```python
load_linnerud(*, return_X_y=False, as_frame=False)
```

Load and return the physical exercise Linnerud dataset.

### `load_sample_image` <sub>function</sub>

```python
load_sample_image(image_name)
```

Load the numpy array of a single sample image.

### `load_sample_images` <sub>function</sub>

```python
load_sample_images()
```

Load sample images for image manipulation.

### `load_svmlight_file` <sub>function</sub>

```python
load_svmlight_file(f, *, n_features=None, dtype=<class 'numpy.float64'>, multilabel=False,
    zero_based='auto', query_id=False, offset=0, length=-1)
```

Load datasets in the svmlight / libsvm format into sparse CSR matrix.

### `load_svmlight_files` <sub>function</sub>

```python
load_svmlight_files(files, *, n_features=None, dtype=<class 'numpy.float64'>, multilabel=False,
    zero_based='auto', query_id=False, offset=0, length=-1)
```

Load dataset from multiple files in SVMlight format.

### `load_wine` <sub>function</sub>

```python
load_wine(*, return_X_y=False, as_frame=False)
```

Load and return the wine dataset (classification).

## Sample generators

### `make_biclusters` <sub>function</sub>

```python
make_biclusters(shape, n_clusters, *, noise=0.0, minval=10, maxval=100, shuffle=True,
    random_state=None)
```

Generate a constant block diagonal structure array for biclustering.

### `make_blobs` <sub>function</sub>

```python
make_blobs(n_samples=100, n_features=2, *, centers=None, cluster_std=1.0, center_box=(-10.0,
    10.0), shuffle=True, random_state=None, return_centers=False)
```

Generate isotropic Gaussian blobs for clustering.

### `make_checkerboard` <sub>function</sub>

```python
make_checkerboard(shape, n_clusters, *, noise=0.0, minval=10, maxval=100, shuffle=True,
    random_state=None)
```

Generate an array with block checkerboard structure for biclustering.

### `make_circles` <sub>function</sub>

```python
make_circles(n_samples=100, *, shuffle=True, noise=None, random_state=None, factor=0.8)
```

Make a large circle containing a smaller circle in 2d.

### `make_classification` <sub>function</sub>

```python
make_classification(n_samples=100, n_features=20, *, n_informative=2, n_redundant=2,
    n_repeated=0, n_classes=2, n_clusters_per_class=2, weights=None, flip_y=0.01, class_sep=1.0,
    hypercube=True, shift=0.0, scale=1.0, shuffle=True, random_state=None, return_X_y=True)
```

Generate a random n-class classification problem.

### `make_friedman1` <sub>function</sub>

```python
make_friedman1(n_samples=100, n_features=10, *, noise=0.0, random_state=None)
```

Generate the "Friedman #1" regression problem.

### `make_friedman2` <sub>function</sub>

```python
make_friedman2(n_samples=100, *, noise=0.0, random_state=None)
```

Generate the "Friedman #2" regression problem.

### `make_friedman3` <sub>function</sub>

```python
make_friedman3(n_samples=100, *, noise=0.0, random_state=None)
```

Generate the "Friedman #3" regression problem.

### `make_gaussian_quantiles` <sub>function</sub>

```python
make_gaussian_quantiles(*, mean=None, cov=1.0, n_samples=100, n_features=2, n_classes=3,
    shuffle=True, random_state=None)
```

Generate isotropic Gaussian and label samples by quantile.

### `make_hastie_10_2` <sub>function</sub>

```python
make_hastie_10_2(n_samples=12000, *, random_state=None)
```

Generate data for binary classification used in Hastie et al. 2009, Example 10.2.

### `make_low_rank_matrix` <sub>function</sub>

```python
make_low_rank_matrix(n_samples=100, n_features=100, *, effective_rank=10, tail_strength=0.5,
    random_state=None)
```

Generate a mostly low rank matrix with bell-shaped singular values.

### `make_moons` <sub>function</sub>

```python
make_moons(n_samples=100, *, shuffle=True, noise=None, random_state=None)
```

Make two interleaving half circles.

### `make_multilabel_classification` <sub>function</sub>

```python
make_multilabel_classification(n_samples=100, n_features=20, *, n_classes=5, n_labels=2,
    length=50, allow_unlabeled=True, sparse=False, return_indicator='dense',
    return_distributions=False, random_state=None)
```

Generate a random multilabel classification problem.

### `make_regression` <sub>function</sub>

```python
make_regression(n_samples=100, n_features=100, *, n_informative=10, n_targets=1, bias=0.0,
    effective_rank=None, tail_strength=0.5, noise=0.0, shuffle=True, coef=False,
    random_state=None)
```

Generate a random regression problem.

### `make_s_curve` <sub>function</sub>

```python
make_s_curve(n_samples=100, *, noise=0.0, random_state=None)
```

Generate an S curve dataset.

### `make_sparse_coded_signal` <sub>function</sub>

```python
make_sparse_coded_signal(n_samples, *, n_components, n_features, n_nonzero_coefs, random_state=None)
```

Generate a signal as a sparse combination of dictionary elements.

### `make_sparse_spd_matrix` <sub>function</sub>

```python
make_sparse_spd_matrix(n_dim=1, *, alpha=0.95, norm_diag=False, smallest_coef=0.1,
    largest_coef=0.9, sparse_format=None, random_state=None)
```

Generate a sparse symmetric definite positive matrix.

### `make_sparse_uncorrelated` <sub>function</sub>

```python
make_sparse_uncorrelated(n_samples=100, n_features=10, *, random_state=None)
```

Generate a random regression problem with sparse uncorrelated design.

### `make_spd_matrix` <sub>function</sub>

```python
make_spd_matrix(n_dim, *, random_state=None)
```

Generate a random symmetric, positive-definite matrix.

### `make_swiss_roll` <sub>function</sub>

```python
make_swiss_roll(n_samples=100, *, noise=0.0, random_state=None, hole=False)
```

Generate a swiss roll dataset.
