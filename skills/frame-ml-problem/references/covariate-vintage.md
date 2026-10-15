# Covariate vintage

Asked only when the deployment is time. It records what the model
will be given about the future when it forecasts, and what the
history can honestly reproduce.

- `none` — the features come from the target's own history only.
- `known_future` — the features are known ahead of time with
  certainty, such as the calendar and holidays.
- `forecast_vintage` — the features include outside forecasts
  (for example weather) and the history keeps the forecast that
  was issued at each prediction time.
- `actuals_only` — the features include outside values that are
  forecasts in deployment, but the history only holds what was
  observed afterwards. The score is optimistic: the model sees
  better inputs than it will get in deployment.

Ask about forecast-like columns the EDA report, the text shipped
with the data, or the user already names. Quote that source. If
none is named, offer `none` and `known_future` first.

`actuals_only` does not stop the work. When it is chosen, say in
one line that scores will be optimistic for that reason, and that
the report and every forecast plot will carry the same caveat.
Do not ask to confirm.
