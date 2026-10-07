# Fallback

Use this when `frame show` is missing, or when the problem is not
classification or regression. Do not open any other file under
`references/`. Do not invent the closed candidate menu.

Tell the user, in a few lines, that the closed menu does not cover
this case, so the comparison has to be written in words. Ask one
question: what would count as a better result, and what is an honest
baseline. Draw on the EDA report, free-form text that came with
the data if any is present, and facts they stated. Quote a fact
those sources already give. If that text is absent, do not invent it.

Then write:

- Prediction goal: `uncovered`
- Metric: the comparison, in words
- Baseline note: the baseline, in words
- Every other decision row: `n/a`, unless they already stated a value

Do not name a splitter class or write code. Set Status to `locked`.
Say these choices are reused for the rest of the experiment so
models stay comparable, and that any one of them can be changed by
naming it. Do not say "lock". There is no splitter translation.
Do not ask lock, modify, or stop.

If they say it is actually classification or regression, write that
goal instead of `uncovered` and stop. Do not set Status to `locked`.
The next `frame show` uses the closed menu.

If the command is missing, there is no JSON. The same write sets
Status to `locked` and uses the same lines. There is no splitter
translation.
