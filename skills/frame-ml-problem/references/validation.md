# Folds

The fold count is an integer of at least 1.

`1` is one train/test split.

`2` or more is how often the model is retrained. On a time series
each fold is one refit on the history available at that moment.

Do not name a splitter class, a gap argument, or a test-size
constructor. Horizon and gap are already recorded when the
deployment is time.
