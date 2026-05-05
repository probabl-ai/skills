# `sklearn.metrics`

_Metrics._

## Model selection interface

### `check_scoring` <sub>function</sub>

```python
check_scoring(estimator=None, scoring=None, *, allow_none=False, raise_exc=True)
```

Determine scorer from user options.

### `get_scorer` <sub>function</sub>

```python
get_scorer(scoring)
```

Get a scorer from string.

### `get_scorer_names` <sub>function</sub>

```python
get_scorer_names()
```

Get the names of all available scorers.

### `make_scorer` <sub>function</sub>

```python
make_scorer(score_func, *, response_method='predict', greater_is_better=True, **kwargs)
```

Make a scorer from a performance metric or loss function.

## Classification metrics

### `accuracy_score` <sub>function</sub>

```python
accuracy_score(y_true, y_pred, *, normalize=True, sample_weight=None)
```

Accuracy classification score.

### `auc` <sub>function</sub>

```python
auc(x, y)
```

Compute Area Under the Curve (AUC) using the trapezoidal rule.

### `average_precision_score` <sub>function</sub>

```python
average_precision_score(y_true, y_score, *, average='macro', pos_label=1, sample_weight=None)
```

Compute average precision (AP) from prediction scores.

### `balanced_accuracy_score` <sub>function</sub>

```python
balanced_accuracy_score(y_true, y_pred, *, sample_weight=None, adjusted=False)
```

Compute the balanced accuracy.

### `brier_score_loss` <sub>function</sub>

```python
brier_score_loss(y_true, y_proba, *, sample_weight=None, pos_label=None, labels=None,
    scale_by_half='auto')
```

Compute the Brier score loss.

### `class_likelihood_ratios` <sub>function</sub>

```python
class_likelihood_ratios(y_true, y_pred, *, labels=None, sample_weight=None,
    raise_warning='deprecated', replace_undefined_by=nan)
```

Compute binary classification positive and negative likelihood ratios.

### `classification_report` <sub>function</sub>

```python
classification_report(y_true, y_pred, *, labels=None, target_names=None, sample_weight=None,
    digits=2, output_dict=False, zero_division='warn')
```

Build a text report showing the main classification metrics.

### `cohen_kappa_score` <sub>function</sub>

```python
cohen_kappa_score(y1, y2, *, labels=None, weights=None, sample_weight=None)
```

Compute Cohen's kappa: a statistic that measures inter-annotator agreement.

### `confusion_matrix` <sub>function</sub>

```python
confusion_matrix(y_true, y_pred, *, labels=None, sample_weight=None, normalize=None)
```

Compute confusion matrix to evaluate the accuracy of a classification.

### `confusion_matrix_at_thresholds` <sub>function</sub>

```python
confusion_matrix_at_thresholds(y_true, y_score, pos_label=None, sample_weight=None)
```

Calculate :term:`binary` confusion matrix terms per classification threshold.

### `d2_brier_score` <sub>function</sub>

```python
d2_brier_score(y_true, y_proba, *, sample_weight=None, pos_label=None, labels=None)
```

:math:`D^2` score function, fraction of Brier score explained.

### `d2_log_loss_score` <sub>function</sub>

```python
d2_log_loss_score(y_true, y_pred, *, sample_weight=None, labels=None)
```

:math:`D^2` score function, fraction of log loss explained.

### `dcg_score` <sub>function</sub>

```python
dcg_score(y_true, y_score, *, k=None, log_base=2, sample_weight=None, ignore_ties=False)
```

Compute Discounted Cumulative Gain.

### `det_curve` <sub>function</sub>

```python
det_curve(y_true, y_score, pos_label=None, sample_weight=None, drop_intermediate=False)
```

Compute Detection Error Tradeoff (DET) for different probability thresholds.

### `f1_score` <sub>function</sub>

```python
f1_score(y_true, y_pred, *, labels=None, pos_label=1, average='binary', sample_weight=None,
    zero_division='warn')
```

Compute the F1 score, also known as balanced F-score or F-measure.

### `fbeta_score` <sub>function</sub>

```python
fbeta_score(y_true, y_pred, *, beta, labels=None, pos_label=1, average='binary',
    sample_weight=None, zero_division='warn')
```

Compute the F-beta score.

### `hamming_loss` <sub>function</sub>

```python
hamming_loss(y_true, y_pred, *, sample_weight=None)
```

Compute the average Hamming loss.

### `hinge_loss` <sub>function</sub>

```python
hinge_loss(y_true, pred_decision, *, labels=None, sample_weight=None)
```

Average hinge loss (non-regularized).

### `jaccard_score` <sub>function</sub>

```python
jaccard_score(y_true, y_pred, *, labels=None, pos_label=1, average='binary', sample_weight=None,
    zero_division='warn')
```

Jaccard similarity coefficient score.

### `log_loss` <sub>function</sub>

```python
log_loss(y_true, y_pred, *, normalize=True, sample_weight=None, labels=None)
```

Log loss, aka logistic loss or cross-entropy loss.

### `matthews_corrcoef` <sub>function</sub>

```python
matthews_corrcoef(y_true, y_pred, *, sample_weight=None)
```

Compute the Matthews correlation coefficient (MCC).

### `multilabel_confusion_matrix` <sub>function</sub>

```python
multilabel_confusion_matrix(y_true, y_pred, *, sample_weight=None, labels=None, samplewise=False)
```

Compute a confusion matrix for each class or sample.

### `ndcg_score` <sub>function</sub>

```python
ndcg_score(y_true, y_score, *, k=None, sample_weight=None, ignore_ties=False)
```

Compute Normalized Discounted Cumulative Gain.

### `precision_recall_curve` <sub>function</sub>

```python
precision_recall_curve(y_true, y_score, *, pos_label=None, sample_weight=None,
    drop_intermediate=False)
```

Compute precision-recall pairs for different probability thresholds.

### `precision_recall_fscore_support` <sub>function</sub>

```python
precision_recall_fscore_support(y_true, y_pred, *, beta=1.0, labels=None, pos_label=1,
    average=None, warn_for=('precision', 'recall', 'f-score'), sample_weight=None,
    zero_division='warn')
```

Compute precision, recall, F-measure and support for each class.

### `precision_score` <sub>function</sub>

```python
precision_score(y_true, y_pred, *, labels=None, pos_label=1, average='binary',
    sample_weight=None, zero_division='warn')
```

Compute the precision.

### `recall_score` <sub>function</sub>

```python
recall_score(y_true, y_pred, *, labels=None, pos_label=1, average='binary', sample_weight=None,
    zero_division='warn')
```

Compute the recall.

### `roc_auc_score` <sub>function</sub>

```python
roc_auc_score(y_true, y_score, *, average='macro', sample_weight=None, max_fpr=None,
    multi_class='raise', labels=None)
```

Compute Area Under the Receiver Operating Characteristic Curve (ROC AUC)     from prediction scores.

### `roc_curve` <sub>function</sub>

```python
roc_curve(y_true, y_score, *, pos_label=None, sample_weight=None, drop_intermediate=True)
```

Compute Receiver operating characteristic (ROC).

### `top_k_accuracy_score` <sub>function</sub>

```python
top_k_accuracy_score(y_true, y_score, *, k=2, normalize=True, sample_weight=None, labels=None)
```

Top-k Accuracy classification score.

### `zero_one_loss` <sub>function</sub>

```python
zero_one_loss(y_true, y_pred, *, normalize=True, sample_weight=None)
```

Zero-one classification loss.

## Regression metrics

### `d2_absolute_error_score` <sub>function</sub>

```python
d2_absolute_error_score(y_true, y_pred, *, sample_weight=None, multioutput='uniform_average')
```

:math:`D^2` regression score function, fraction of absolute error explained.

### `d2_pinball_score` <sub>function</sub>

```python
d2_pinball_score(y_true, y_pred, *, sample_weight=None, alpha=0.5, multioutput='uniform_average')
```

:math:`D^2` regression score function, fraction of pinball loss explained.

### `d2_tweedie_score` <sub>function</sub>

```python
d2_tweedie_score(y_true, y_pred, *, sample_weight=None, power=0)
```

:math:`D^2` regression score function, fraction of Tweedie deviance explained.

### `explained_variance_score` <sub>function</sub>

```python
explained_variance_score(y_true, y_pred, *, sample_weight=None, multioutput='uniform_average',
    force_finite=True)
```

Explained variance regression score function.

### `max_error` <sub>function</sub>

```python
max_error(y_true, y_pred)
```

The max_error metric calculates the maximum residual error.

### `mean_absolute_error` <sub>function</sub>

```python
mean_absolute_error(y_true, y_pred, *, sample_weight=None, multioutput='uniform_average')
```

Mean absolute error regression loss.

### `mean_absolute_percentage_error` <sub>function</sub>

```python
mean_absolute_percentage_error(y_true, y_pred, *, sample_weight=None, multioutput='uniform_average')
```

Mean absolute percentage error (MAPE) regression loss.

### `mean_gamma_deviance` <sub>function</sub>

```python
mean_gamma_deviance(y_true, y_pred, *, sample_weight=None)
```

Mean Gamma deviance regression loss.

### `mean_pinball_loss` <sub>function</sub>

```python
mean_pinball_loss(y_true, y_pred, *, sample_weight=None, alpha=0.5, multioutput='uniform_average')
```

Pinball loss for quantile regression.

### `mean_poisson_deviance` <sub>function</sub>

```python
mean_poisson_deviance(y_true, y_pred, *, sample_weight=None)
```

Mean Poisson deviance regression loss.

### `mean_squared_error` <sub>function</sub>

```python
mean_squared_error(y_true, y_pred, *, sample_weight=None, multioutput='uniform_average')
```

Mean squared error regression loss.

### `mean_squared_log_error` <sub>function</sub>

```python
mean_squared_log_error(y_true, y_pred, *, sample_weight=None, multioutput='uniform_average')
```

Mean squared logarithmic error regression loss.

### `mean_tweedie_deviance` <sub>function</sub>

```python
mean_tweedie_deviance(y_true, y_pred, *, sample_weight=None, power=0)
```

Mean Tweedie deviance regression loss.

### `median_absolute_error` <sub>function</sub>

```python
median_absolute_error(y_true, y_pred, *, multioutput='uniform_average', sample_weight=None)
```

Median absolute error regression loss.

### `r2_score` <sub>function</sub>

```python
r2_score(y_true, y_pred, *, sample_weight=None, multioutput='uniform_average', force_finite=True)
```

:math:`R^2` (coefficient of determination) regression score function.

### `root_mean_squared_error` <sub>function</sub>

```python
root_mean_squared_error(y_true, y_pred, *, sample_weight=None, multioutput='uniform_average')
```

Root mean squared error regression loss.

### `root_mean_squared_log_error` <sub>function</sub>

```python
root_mean_squared_log_error(y_true, y_pred, *, sample_weight=None, multioutput='uniform_average')
```

Root mean squared logarithmic error regression loss.

## Multilabel ranking metrics

### `coverage_error` <sub>function</sub>

```python
coverage_error(y_true, y_score, *, sample_weight=None)
```

Coverage error measure.

### `label_ranking_average_precision_score` <sub>function</sub>

```python
label_ranking_average_precision_score(y_true, y_score, *, sample_weight=None)
```

Compute ranking-based average precision.

### `label_ranking_loss` <sub>function</sub>

```python
label_ranking_loss(y_true, y_score, *, sample_weight=None)
```

Compute Ranking loss measure.

## Clustering metrics

### `adjusted_mutual_info_score` <sub>function</sub>

```python
adjusted_mutual_info_score(labels_true, labels_pred, *, average_method='arithmetic')
```

Adjusted Mutual Information between two clusterings.

### `adjusted_rand_score` <sub>function</sub>

```python
adjusted_rand_score(labels_true, labels_pred)
```

Rand index adjusted for chance.

### `calinski_harabasz_score` <sub>function</sub>

```python
calinski_harabasz_score(X, labels)
```

Compute the Calinski and Harabasz score.

### `cluster.contingency_matrix` <sub>function</sub>

```python
cluster.contingency_matrix(labels_true, labels_pred, *, eps=None, sparse=False, dtype=<class
    'numpy.int64'>)
```

Build a contingency matrix describing the relationship between labels.

### `cluster.pair_confusion_matrix` <sub>function</sub>

```python
cluster.pair_confusion_matrix(labels_true, labels_pred)
```

Pair confusion matrix arising from two clusterings.

### `completeness_score` <sub>function</sub>

```python
completeness_score(labels_true, labels_pred)
```

Compute completeness metric of a cluster labeling given a ground truth.

### `davies_bouldin_score` <sub>function</sub>

```python
davies_bouldin_score(X, labels)
```

Compute the Davies-Bouldin score.

### `fowlkes_mallows_score` <sub>function</sub>

```python
fowlkes_mallows_score(labels_true, labels_pred, *, sparse='deprecated')
```

Measure the similarity of two clusterings of a set of points.

### `homogeneity_completeness_v_measure` <sub>function</sub>

```python
homogeneity_completeness_v_measure(labels_true, labels_pred, *, beta=1.0)
```

Compute the homogeneity and completeness and V-Measure scores at once.

### `homogeneity_score` <sub>function</sub>

```python
homogeneity_score(labels_true, labels_pred)
```

Homogeneity metric of a cluster labeling given a ground truth.

### `mutual_info_score` <sub>function</sub>

```python
mutual_info_score(labels_true, labels_pred, *, contingency=None)
```

Mutual Information between two clusterings.

### `normalized_mutual_info_score` <sub>function</sub>

```python
normalized_mutual_info_score(labels_true, labels_pred, *, average_method='arithmetic')
```

Normalized Mutual Information between two clusterings.

### `rand_score` <sub>function</sub>

```python
rand_score(labels_true, labels_pred)
```

Rand index.

### `silhouette_samples` <sub>function</sub>

```python
silhouette_samples(X, labels, *, metric='euclidean', **kwds)
```

Compute the Silhouette Coefficient for each sample.

### `silhouette_score` <sub>function</sub>

```python
silhouette_score(X, labels, *, metric='euclidean', sample_size=None, random_state=None, **kwds)
```

Compute the mean Silhouette Coefficient of all samples.

### `v_measure_score` <sub>function</sub>

```python
v_measure_score(labels_true, labels_pred, *, beta=1.0)
```

V-measure cluster labeling given a ground truth.

## Biclustering metrics

### `consensus_score` <sub>function</sub>

```python
consensus_score(a, b, *, similarity='jaccard')
```

The similarity of two sets of biclusters.

## Distance metrics

### `DistanceMetric` <sub>class</sub>


Uniform interface for fast distance metric functions.

## Pairwise metrics

### `pairwise.additive_chi2_kernel` <sub>function</sub>

```python
pairwise.additive_chi2_kernel(X, Y=None)
```

Compute the additive chi-squared kernel between observations in X and Y.

### `pairwise.chi2_kernel` <sub>function</sub>

```python
pairwise.chi2_kernel(X, Y=None, gamma=1.0)
```

Compute the exponential chi-squared kernel between X and Y.

### `pairwise.cosine_distances` <sub>function</sub>

```python
pairwise.cosine_distances(X, Y=None)
```

Compute cosine distance between samples in X and Y.

### `pairwise.cosine_similarity` <sub>function</sub>

```python
pairwise.cosine_similarity(X, Y=None, dense_output=True)
```

Compute cosine similarity between samples in X and Y.

### `pairwise.distance_metrics` <sub>function</sub>

```python
pairwise.distance_metrics()
```

Valid metrics for pairwise_distances.

### `pairwise.euclidean_distances` <sub>function</sub>

```python
pairwise.euclidean_distances(X, Y=None, *, Y_norm_squared=None, squared=False, X_norm_squared=None)
```

Compute the distance matrix between each pair from a feature array X and Y.

### `pairwise.haversine_distances` <sub>function</sub>

```python
pairwise.haversine_distances(X, Y=None)
```

Compute the Haversine distance between samples in X and Y.

### `pairwise.kernel_metrics` <sub>function</sub>

```python
pairwise.kernel_metrics()
```

Valid metrics for pairwise_kernels.

### `pairwise.laplacian_kernel` <sub>function</sub>

```python
pairwise.laplacian_kernel(X, Y=None, gamma=None)
```

Compute the laplacian kernel between X and Y.

### `pairwise.linear_kernel` <sub>function</sub>

```python
pairwise.linear_kernel(X, Y=None, dense_output=True)
```

Compute the linear kernel between X and Y.

### `pairwise.manhattan_distances` <sub>function</sub>

```python
pairwise.manhattan_distances(X, Y=None)
```

Compute the L1 distances between the vectors in X and Y.

### `pairwise.nan_euclidean_distances` <sub>function</sub>

```python
pairwise.nan_euclidean_distances(X, Y=None, *, squared=False, missing_values=nan, copy=True)
```

Calculate the euclidean distances in the presence of missing values.

### `pairwise.paired_cosine_distances` <sub>function</sub>

```python
pairwise.paired_cosine_distances(X, Y)
```

Compute the paired cosine distances between X and Y.

### `pairwise.paired_distances` <sub>function</sub>

```python
pairwise.paired_distances(X, Y, *, metric='euclidean', **kwds)
```

Compute the paired distances between X and Y.

### `pairwise.paired_euclidean_distances` <sub>function</sub>

```python
pairwise.paired_euclidean_distances(X, Y)
```

Compute the paired euclidean distances between X and Y.

### `pairwise.paired_manhattan_distances` <sub>function</sub>

```python
pairwise.paired_manhattan_distances(X, Y)
```

Compute the paired L1 distances between X and Y.

### `pairwise.pairwise_kernels` <sub>function</sub>

```python
pairwise.pairwise_kernels(X, Y=None, metric='linear', *, filter_params=False, n_jobs=None, **kwds)
```

Compute the kernel between arrays X and optional array Y.

### `pairwise.polynomial_kernel` <sub>function</sub>

```python
pairwise.polynomial_kernel(X, Y=None, degree=3, gamma=None, coef0=1)
```

Compute the polynomial kernel between X and Y.

### `pairwise.rbf_kernel` <sub>function</sub>

```python
pairwise.rbf_kernel(X, Y=None, gamma=None)
```

Compute the rbf (gaussian) kernel between X and Y.

### `pairwise.sigmoid_kernel` <sub>function</sub>

```python
pairwise.sigmoid_kernel(X, Y=None, gamma=None, coef0=1)
```

Compute the sigmoid kernel between X and Y.

### `pairwise_distances` <sub>function</sub>

```python
pairwise_distances(X, Y=None, metric='euclidean', *, n_jobs=None, ensure_all_finite=True, **kwds)
```

Compute the distance matrix from a feature array X and optional Y.

### `pairwise_distances_argmin` <sub>function</sub>

```python
pairwise_distances_argmin(X, Y, *, axis=1, metric='euclidean', metric_kwargs=None)
```

Compute minimum distances between one point and a set of points.

### `pairwise_distances_argmin_min` <sub>function</sub>

```python
pairwise_distances_argmin_min(X, Y, *, axis=1, metric='euclidean', metric_kwargs=None)
```

Compute minimum distances between one point and a set of points.

### `pairwise_distances_chunked` <sub>function</sub>

```python
pairwise_distances_chunked(X, Y=None, *, reduce_func=None, metric='euclidean', n_jobs=None,
    working_memory=None, **kwds)
```

Generate a distance matrix chunk by chunk with optional reduction.

## Plotting

### `ConfusionMatrixDisplay` <sub>class</sub>

```python
ConfusionMatrixDisplay(confusion_matrix, *, display_labels=None)
```

Confusion Matrix visualization.

### `DetCurveDisplay` <sub>class</sub>

```python
DetCurveDisplay(*, fpr, fnr, estimator_name=None, pos_label=None)
```

Detection Error Tradeoff (DET) curve visualization.

### `PrecisionRecallDisplay` <sub>class</sub>

```python
PrecisionRecallDisplay(precision, recall, *, average_precision=None, name=None, pos_label=None,
    prevalence_pos_label=None, estimator_name='deprecated')
```

Precision Recall visualization.

### `PredictionErrorDisplay` <sub>class</sub>

```python
PredictionErrorDisplay(*, y_true, y_pred)
```

Visualization of the prediction error of a regression model.

### `RocCurveDisplay` <sub>class</sub>

```python
RocCurveDisplay(*, fpr, tpr, roc_auc=None, name=None, pos_label=None, estimator_name='deprecated')
```

ROC Curve visualization.
