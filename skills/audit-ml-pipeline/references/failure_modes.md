# Audit ML Pipeline — failure modes and recovery

Load this reference when an audit-ml-pipeline action fails and you
need to know how to recover. The SKILL.md body links here from its
"Failure modes" section.

## `project.get(key)` raises `KeyError` / `TypeError`

Lookup shape is wrong: `get` is by id, not by key.

- **Hub mode**: the id comes from the URL printed by `project.put()`:
  `https://…/<workspace>/<project>/<type-plural>/<N>` → id is
  `skore:report:<type-singular>:<N>` (URL segment is plural; id is
  singular — drop the trailing `s`, e.g. `cross-validations` →
  `cross-validation`, `estimators` → `estimator`). If the audit
  file's `REPORT_ID` is wrong, update it from the correct URL.
- **Local mode**: `summarize()` returns a DataFrame with a flat
  `RangeIndex` and an `"id"` column — read
  `summary.loc[summary["key"] == "<NN>_<short_name>", "id"].iloc[0]`
  and set it as `REPORT_ID`.

Never substitute by re-running `evaluate` + `put`. See `python-api`
§ "Lookup failure ≠ artifact missing".

## `run_audit.py` exits with `ModuleNotFoundError: No module named 'IPython'`

Agent feature not installed in the env the runner is invoked from.
**Delegate to `python-env-manager` § "Agent feature" via
`G-AGENT-FEATURE`.** Do not type install commands from this skill.
The per-manager install scripts under
`.agents/skills/python-env-manager/scripts/install_agent_feature_<manager>.sh`
do the full install + verification in one call.

## Cell renders as `<Display object at 0x…>` in the digest

The cell called a `*.summarize()` accessor without `.frame()`. The
`__repr__` of skore's `Display` classes is the bare object-at-address;
the runner can't extract a useful text representation. Edit the cell
to chain `.frame()`:

```python
report.metrics.summarize().frame()
report.checks.summarize().frame()
```

## Digest contains `**error:** AttributeError: 'X' object has no attribute 'Y'` for a `report.*` accessor

Symbol drift between skore versions OR symbol-from-memory in the
audit file. Consult `python-api` against the installed skore version,
update the cell, re-run the runner.

## Digest contains `**error:**` for the `project.get(REPORT_ID)` cell

`project.get(REPORT_ID)` raised — the id doesn't match any report in
this Project. Most likely cause: the audit's `<SKORE_PROJECT_INIT>`
block points to a different Project than the experiment wrote to (wrong
hub workspace name, wrong mode, wrong project name). Verify it matches
`experiments/<stem>.py` exactly. For hub mode, also confirm `REPORT_ID`
was copied from the correct `put()` URL output.

## Report differs between runs even when source code didn't change

Most often: the experiment was re-run with a different data slice,
or a non-deterministic step (RNG seed) shifted. Not a bug in this
skill; surface to the user before assuming the audit changed.

## Hub mode: `skore.login(mode="hub")` fails with an authentication error

Token expired or the user hasn't logged in on this machine yet.
Surface the failure verbatim; do not retry from a `scratch/`
probe — `login` is interactive (browser or API key prompt) and
belongs in the audit file's own execution. Re-run the runner after
the user has refreshed credentials.

## Hub mode: `TypeError: Project.__init__() got an unexpected keyword argument 'workspace'`

The `<SKORE_PROJECT_INIT>` substitution dropped the hub form but
left a `workspace=` kwarg in the call. `workspace=` is local-mode-
only — hub mode rejects it. Re-check the audit file's Project init
block against the experiment script's (they must match), or
re-substitute the marker from a clean template.

## Hub mode: report appears missing in `summarize()` but the experiment script reported a successful `put()`

Two possibilities:

1. **Different hub workspace.** The audit is opening a different hub
   workspace than the experiment wrote to. Verify the
   `<hub-workspace>` part of the name matches `Workspace decisions`.
2. **No read access.** The user's credentials don't have read access
   to the workspace they wrote to (rare). Surface the access issue
   to the user; do not silently fall back to local mode.
