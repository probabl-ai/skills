# Horizon and gap

Record both in the same unit. Horizon may be a comma-separated
list. Gap is one quantity. A gap of `0 <unit>` is allowed.

**Horizon** is the lead from the moment a forecast is issued
(prediction time) to the target time. Each entry is one target
and one predictor. Write `<number> <unit>`, for example
`1 hour, 2 hour, 24 hour`. Every entry uses one unit.

**Gap** is the delay from the last training row to the first
moment a forecast can be issued. Write one `<number> <unit>`,
for example `0 hour`. For each horizon `h`, training ends at
least `gap + h` before that target.

Do not name a splitter class or a constructor argument.
