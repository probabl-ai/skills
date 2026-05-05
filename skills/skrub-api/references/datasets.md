# `skrub.datasets`

Example datasets used in the user guide and gallery, plus helpers to manage where they're cached.

```python
from skrub import datasets
```

All `fetch_*` functions return a `Bunch` (sklearn-like) with at least `.X`, `.y`, and metadata; some also return raw tables (`.{name}`). They cache under `~/.skrub_data/` by default; pass `data_home=...` to override, or set the global `data_dir` via `skrub.set_config`.

## Real-world datasets — regression

### function `fetch_bike_sharing`
**Signature:** `fetch_bike_sharing(data_home=None)`

### function `fetch_california_housing`
**Signature:** `fetch_california_housing(data_home=None)`

### function `fetch_country_happiness`
**Signature:** `fetch_country_happiness(data_home=None)`

### function `fetch_employee_salaries`
**Signature:** `fetch_employee_salaries(data_home=None, split='all')`

`split` is `'all'`, `'train'`, or `'test'`.

### function `fetch_flight_delays`
**Signature:** `fetch_flight_delays(data_home=None)`

### function `fetch_medical_charge`
**Signature:** `fetch_medical_charge(data_home=None)`

### function `fetch_movielens`
**Signature:** `fetch_movielens(data_home=None)`

### function `fetch_videogame_sales`
**Signature:** `fetch_videogame_sales(data_home=None)`

## Real-world datasets — classification

### function `fetch_credit_fraud`
**Signature:** `fetch_credit_fraud(data_home=None, split='train')`

### function `fetch_drug_directory`
**Signature:** `fetch_drug_directory(data_home=None)`

### function `fetch_midwest_survey`
**Signature:** `fetch_midwest_survey(data_home=None)`

### function `fetch_open_payments`
**Signature:** `fetch_open_payments(data_home=None)`

### function `fetch_toxicity`
**Signature:** `fetch_toxicity(data_home=None)`

### function `fetch_traffic_violations`
**Signature:** `fetch_traffic_violations(data_home=None)`

## Toy / synthetic datasets

### function `toy_orders`
**Signature:** `toy_orders(split='train')`

Tiny toy orders dataframe + targets, used in DataOps documentation and tests.

### function `toy_products`
**Signature:** `toy_products()`

Tiny toy products dataframe (companion table for `toy_orders`).

### function `make_deduplication_data`
**Signature:** `make_deduplication_data(examples, entries_per_example, prob_mistake_per_letter=0.2, random_state=None)`

Duplicate `examples` with random spelling mistakes — used to demonstrate `skrub.deduplicate`.

## Cache directory

### function `get_data_dir`
**Signature:** `get_data_dir(name=None, data_home=None)`

Return the directory where skrub caches datasets. Pass `name` to get a sub-directory.
