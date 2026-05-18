# Reproducibility mechanics — full procedures

Three options for extending a shared `src/<pkg>/` module without
breaking prior experiments. SKILL.md has the criterion + tripwires
in prose; this file has the worked code per option.

The hard rule (from `iterate-ml-experiment`'s Stop conditions):
every `done` row in `JOURNAL.md` History must remain runnable on
`main` and produce the same result.

**Don't pick mechanically** — read the criterion and choose.

## Option 1 — Parametrize the existing function

Pick this when the change is **small and well-scoped**:

- a step appended at the end of a chain,
- a single conditional branch in the graph,
- a new stateless transform that adds columns without reshaping
  existing ones,
- the flag has an obvious default that matches prior behavior.

**The flag's default must mirror what prior callers saw before
the change.** Prior experiment scripts call the function
unchanged; the new experiment passes the flag.

```python
# Before:
def build_learner(data_dir_preview=None): ...

# After (parametrize for experiment 02):
def build_learner(
    data_dir_preview=None,
    *,
    include_calendar_features: bool = False,
):
    ...
    if include_calendar_features:
        X = X.skb.apply_func(add_calendar_features)
    ...
```

`experiments/01_baseline.py` is unchanged (uses default `False`);
`experiments/02_calendar_features.py` passes `True`. The prior
smoke test still calls `build_learner()` and sees the baseline
shape.

## Option 2 — Add a new function called only from the new experiment

Pick this when the change **doesn't fit cleanly behind a flag**:

- a new estimator at the tail of the chain,
- a fundamentally different feature-engineering step that reshapes
  the graph (not just appends),
- Option 1's function would grow ugly internal branching.

Pattern: keep the original (`build_learner`) for prior
experiments, add a new function for the new one. The two may
share helpers freely; only the entrypoint diverges.

```python
def build_learner(...): ...                  # used by 01_baseline, 02, ...

def build_learner_with_quantile_head(...): ...  # used only by 04_quantile
```

## Option 3 — Branch the module

**Last resort.** Pick this only when the change touches enough
internal structure that Options 1 and 2 would obscure the diff
(the whole pipeline shape changes; the data loader has to produce
a different schema). Usually a signal of a deeper layering issue
worth surfacing to the user before cloning.

Pattern: copy `pipeline.py` to `pipeline_v2.py` (or a descriptive
name), edit freely. Prior experiments keep importing the original.
Document the split in the new experiment's design-note Risks.

## Tripwires (also in SKILL.md)

- **3+ flags in one function.** When the same function ends up
  with `include_calendar_features=False, include_X=False,
  include_Y=False, ...`, the parametrization model is leaking.
  Reach for Option 2 for the *next* feature.
- **Visible branching in the function body.** When the if-tree
  for the flags makes the function hard to read, reach for
  Option 2.
- **A flag changes default behavior of an existing caller.**
  STOP. The rule is broken. Fix it: either keep the default
  preserving, or use Option 2.

## Cheap executable check

`iterate-ml-experiment`'s § 3 smoke-test gate runs **all of
`tests/smoke/`**, not just the new experiment's test. If a prior
smoke test goes red after your change, default behavior isn't
preserving the prior experiment's shape — fix it before
declaring the new experiment ready to run.
