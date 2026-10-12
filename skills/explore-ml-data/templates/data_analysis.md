# Exploratory data analysis — <project / dataset name>

## Dataset at a glance

<iframe src="data_analysis_<slug>.html" width="100%" height="640"></iframe>

## Modelling implications

Translate TableReport **and** extras (duplicates, each target's
balance/skew, feature-vs-target, target-vs-target, leakage flags)
into *candidate*
modelling choices (splitter, metric, leakage risk). The owning
gates make the picks.
Every saved PNG and extra HTML is embedded here —
`![<caption>](<name>.png)` or
`<iframe src="<slug>.html" width="100%" height="640"></iframe>`.
A sibling of this file, never a bare link. Each embed sits beside a
sentence that cites numbers from the analysis. If a figure earns no
such sentence, do not save it. Glance stays TableReport-only.

## Open questions

Domain ambiguities to confirm before modelling (why duplicates
exist, whether a near-perfect correlate is leakage, a capped
target).
