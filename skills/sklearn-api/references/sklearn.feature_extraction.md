# `sklearn.feature_extraction`

_Feature extraction._

### `DictVectorizer` <sub>class</sub>

```python
DictVectorizer(*, dtype=<class 'numpy.float64'>, separator='=', sparse=True, sort=True)
```

Transforms lists of feature-value mappings to vectors.

### `FeatureHasher` <sub>class</sub>

```python
FeatureHasher(n_features=1048576, *, input_type='dict', dtype=<class 'numpy.float64'>,
    alternate_sign=True)
```

Implements feature hashing, aka the hashing trick.

## From images

### `image.PatchExtractor` <sub>class</sub>

```python
image.PatchExtractor(*, patch_size=None, max_patches=None, random_state=None)
```

Extracts patches from a collection of images.

### `image.extract_patches_2d` <sub>function</sub>

```python
image.extract_patches_2d(image, patch_size, *, max_patches=None, random_state=None)
```

Reshape a 2D image into a collection of patches.

### `image.grid_to_graph` <sub>function</sub>

```python
image.grid_to_graph(n_x, n_y, n_z=1, *, mask=None, return_as=<class
    'scipy.sparse._coo.coo_matrix'>, dtype=<class 'int'>)
```

Graph of the pixel-to-pixel connections.

### `image.img_to_graph` <sub>function</sub>

```python
image.img_to_graph(img, *, mask=None, return_as=<class 'scipy.sparse._coo.coo_matrix'>, dtype=None)
```

Graph of the pixel-to-pixel gradient connections.

### `image.reconstruct_from_patches_2d` <sub>function</sub>

```python
image.reconstruct_from_patches_2d(patches, image_size)
```

Reconstruct the image from all of its patches.

## From text

### `text.CountVectorizer` <sub>class</sub>

```python
text.CountVectorizer(*, input='content', encoding='utf-8', decode_error='strict',
    strip_accents=None, lowercase=True, preprocessor=None, tokenizer=None, stop_words=None,
    token_pattern='(?u)\\b\\w\\w+\\b', ngram_range=(1, 1), analyzer='word', max_df=1.0,
    min_df=1, max_features=None, vocabulary=None, binary=False, dtype=<class 'numpy.int64'>)
```

Convert a collection of text documents to a matrix of token counts.

### `text.HashingVectorizer` <sub>class</sub>

```python
text.HashingVectorizer(*, input='content', encoding='utf-8', decode_error='strict',
    strip_accents=None, lowercase=True, preprocessor=None, tokenizer=None, stop_words=None,
    token_pattern='(?u)\\b\\w\\w+\\b', ngram_range=(1, 1), analyzer='word', n_features=1048576,
    binary=False, norm='l2', alternate_sign=True, dtype=<class 'numpy.float64'>)
```

Convert a collection of text documents to a matrix of token occurrences.

### `text.TfidfTransformer` <sub>class</sub>

```python
text.TfidfTransformer(*, norm='l2', use_idf=True, smooth_idf=True, sublinear_tf=False)
```

Transform a count matrix to a normalized tf or tf-idf representation.

### `text.TfidfVectorizer` <sub>class</sub>

```python
text.TfidfVectorizer(*, input='content', encoding='utf-8', decode_error='strict',
    strip_accents=None, lowercase=True, preprocessor=None, tokenizer=None, analyzer='word',
    stop_words=None, token_pattern='(?u)\\b\\w\\w+\\b', ngram_range=(1, 1), max_df=1.0,
    min_df=1, max_features=None, vocabulary=None, binary=False, dtype=<class 'numpy.float64'>,
    norm='l2', use_idf=True, smooth_idf=True, sublinear_tf=False)
```

Convert a collection of raw documents to a matrix of TF-IDF features.
