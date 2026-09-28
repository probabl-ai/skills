# Deployment

How a new row arrives, so later evaluation can copy that.

- `iid` — a new row is exchangeable with the rows already seen.
- `time` — a new row is later than the rows used to fit. The
  series has one or more horizons and one gap, recorded
  separately.
- `groups` — a new row belongs to an id that was not in the fit,
  and that id is the one the model must generalize to.

On a time deployment, also record the time column's role.
`sort_key` means the column only orders rows. `covariate` means
the model may use it as a feature. That choice is not a splitter
setting.

When the deployment does not use horizon, gap, time role, or a
generalize-to column, those cells are `n/a`.
