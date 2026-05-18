---
name: python-code-style
description: >
  Owns Python code style for this stack: ruff for lint + format, numpydoc
  for docstrings. Two responsibilities — (1) place the project's
  `ruff.toml` from the bundled template once the stack and workspace
  are in place, and (2) run ruff against any Python files Claude has
  just generated or edited. Stops at "the touched files pass `ruff
  check`."

  TRIGGER when (any of these):
  (1) a Python file was just created or edited via Write / Edit /
      MultiEdit — invoke this skill before declaring the task done so
      ruff is run on the touched files;
  (2) a fresh ML workspace was just scaffolded by
      `organize-ml-workspace` and the project has no `ruff.toml` at
      its root yet — drop the bundled template;
  (3) the user asks about lint, format, docstring style, or reaches
      for `black` / `isort` / `flake8` / `pydocstyle` (redirect to
      ruff — the stack's canonical linter, owned by
      `data-science-python-stack` Tier 1).

  SKIP when: the project is non-Python; the only edits in this turn
  are to Markdown / TOML / JSON / YAML; the file lives in a
  third-party vendored directory the user doesn't own.

  HOW TO USE: run ruff manually on the files you just touched — do
  not configure a PostToolUse hook for this. **Read the "Stop
  conditions" block and emit the Pre-flight checklist as visible
  text in your response — both are mandatory before running ruff.**
---

# Python Code Style

Single owner of "what does well-styled Python look like in this
stack": ruff (lint + format) and numpydoc docstrings. This skill is
explicitly **manual** — Claude runs ruff on the files it has just
touched, no hook involved.

## Stop conditions — read before anything else

- **Do not configure a PostToolUse / PreToolUse hook for ruff.** This
  skill is intentionally manual. A hook tightens the loop in ways
  that bite (every micro-edit triggers a fix cycle, partial files
  fail D-rule checks mid-write, retries can stall the turn). If the
  user explicitly asks for an automated hook later, redirect to
  `update-config` — but the default is "Claude runs ruff itself."
- **Do not substitute ruff with `black` / `isort` / `flake8` /
  `pydocstyle` / `pylint`.** Ruff is the canonical linter in this
  stack (`data-science-python-stack` Tier 1). If `import ruff` /
  `pixi run ruff --version` fails, route through `python-env-manager`
  to install — don't silently fall back.
- **One fix attempt per file, then surface.** If `ruff check`
  reports issues after Claude's first fix, address them once. If the
  *same* issue persists after the second pass, stop editing that
  file and surface the remaining diagnostics + diff to the user.
  This is the anti-infinite-loop guardrail — do not enter a third
  cycle on the same warning.
- **Don't lint files outside the user's code.** The hook scope is
  `src/<pkg>/`, `experiments/`, top-level `*.py` scripts, and any
  package directory the user owns. Skip vendored paths, generated
  files, and anything under `.pixi/`, `.venv/`, `node_modules/`, etc.
- **Never write `ruff.toml` from memory.** The bundled
  `templates/ruff.toml` is the single source of truth — it encodes
  the per-file ignores (`experiments/**`), the numpydoc convention,
  and the rule selection this stack expects. Initial setup requires
  **`Read .agents/skills/python-code-style/templates/ruff.toml`**
  *this turn*, then `Write <project-root>/ruff.toml` verbatim from
  that file's content. Authoring a custom `ruff.toml` from training-
  data memory drops half the contract silently. If you catch
  yourself typing `[lint]` / `[format]` / `select = [...]` without
  having read the template this turn, STOP and `Read` it first.

## Pre-flight — emit this checklist as visible text before running ruff

```
Pre-flight (python-code-style):
- [ ] ruff importable in the project's env (`pixi run ruff --version`
      succeeds, per `data-science-python-stack` Tier 1)
- [ ] `ruff.toml` present at project root.
      If absent AND stack + workspace are already set up: the
      bundled template MUST be read **this turn** before being
      written verbatim.
      Evidence: Read .agents/skills/python-code-style/templates/ruff.toml
                (this turn) + Write <project-root>/ruff.toml (this turn)
                | "n/a — ruff.toml already at project root"
      **Inline-authored ruff.toml from memory is NOT evidence.**
- [ ] File list ready: <abs paths of .py files touched this turn>
- [ ] Decision recorded: this is the first ruff pass on these files
      (proceed) | second pass (proceed but stop on persistent
      issues) | third pass on same warning (STOP, surface to user)
- [ ] One-fix-per-file rule acknowledged: max two passes per warning,
      then surface remaining diagnostics + diff to the user.
```

## Scope

- **In scope:** running `ruff format` + `ruff check --fix` + `ruff
  check` on Python files Claude has just generated or edited;
  authoring numpydoc docstrings on public functions and classes;
  dropping the `ruff.toml` template into a fresh project.
- **Out of scope:** type hints (mypy / pyright are not in the
  stack); naming conventions ruff doesn't enforce; setting up
  PostToolUse / PreToolUse hooks; linting non-Python files.

## What to run, in what order

For every Python file touched this turn (call them `<files>`), run
inside the project's environment manager — `pixi run` for pixi
projects, equivalent for uv / poetry / conda (per
`python-env-manager`):

```bash
pixi run ruff format <files>
pixi run ruff check --fix <files>
pixi run ruff check <files>
```

Three steps, in order:

1. **`ruff format`** — applies the formatter (line length, quoting,
   trailing commas, blank lines around defs). Idempotent.
2. **`ruff check --fix`** — auto-fixes everything ruff knows how to
   fix in place: import sorting (`I`), legacy syntax (`UP`),
   detectable bug patterns (`B`).
3. **`ruff check`** (no `--fix`) — final pass. Anything reported
   here needs Claude's attention: missing docstrings (`D`),
   undefined names (`F`), code structure issues. Address them, then
   re-run the trio. Apply the **one-fix-per-file rule** from Stop
   conditions.

If a file under `experiments/` has a `D100` ("missing module
docstring") or `D103` ("missing function docstring") warning,
that's expected for `# %%` cells; the bundled `ruff.toml` ignores
those for `experiments/**`. If you're seeing them, the `ruff.toml`
isn't loaded — check that it lives at the project root.

## Numpydoc — the docstring convention

Public functions and classes carry numpydoc-format docstrings; ruff's
`D` rules with `pydocstyle.convention = "numpy"` enforce the shape.

**A bare one-line summary is NOT sufficient for public functions.**
The `Parameters` / `Returns` (and `Raises` when applicable) sections
are mandatory — even when the function is small, even when the user
says "just the summary is fine". Approving a one-line docstring on
a public function silently fails the contract this skill enforces;
the function looks `D`-rule-clean (D100/D103 don't fire) but the
parameter shapes and return type that callers actually need are
missing. Private helpers (`_leading_underscore`) are the only
exception: the default `D` rules allow them to omit docstrings, but
public callable surfaces always carry the full numpydoc shape.

Skeleton:

```python
def predict_price(X, model, *, n_jobs=1):
    """Predict option prices from a feature matrix.

    Parameters
    ----------
    X : pandas.DataFrame
        Feature matrix with one row per option.
    model : sklearn.base.BaseEstimator
        Fitted estimator with a ``predict`` method.
    n_jobs : int, default=1
        Number of parallel jobs.

    Returns
    -------
    numpy.ndarray of shape (n_samples,)
        Predicted prices, one per row of ``X``.
    """
```

Conventions worth surfacing because they're non-obvious:

- **One-line summary on the first line**, in the imperative mood
  ("Predict ..." not "Predicts ..."). No trailing period in the
  summary line if D400 is enabled — but in `numpy` convention it
  is, so write the period.
- **Blank line between summary and the rest.**
- **Parameter shapes go in the type slot**, not the description, e.g.
  `X : ndarray of shape (n_samples, n_features)`.
- **`Returns` section** lists the return value; if there are
  multiple returns, list each on its own row. Don't omit the type.
- **Private helpers** (`_leading_underscore`) don't need a docstring
  under the default `D` rules — ruff allows that.
- **Modules** (top of file) should start with a one-line summary.
  Skipped under `experiments/**` per the bundled `ruff.toml`.

## Initial setup — dropping the `ruff.toml` template

When this skill is invoked on a fresh project that has no
`ruff.toml` at its root **and** the stack + workspace have been
scaffolded by their respective skills:

1. **Read the bundled template** with the file-reading tool *this
   turn*:
   `Read .agents/skills/python-code-style/templates/ruff.toml`.
   The pre-flight Evidence row for the `ruff.toml present` check
   requires this read; an inline-authored config from memory does
   not satisfy it.
2. **Write the content verbatim** to `<project-root>/ruff.toml`.
   No edits, no "improvements", no rule additions. The template
   encodes the per-file ignores (`experiments/**`), the
   `pydocstyle.convention = "numpy"` setting, and the rule
   selection this stack expects. Diverging from it drops half the
   contract.
3. **Verify ruff picks it up**: `pixi run ruff check --show-settings
   .` should report the `numpy` convention and the `select` list
   from the template.

Do not fold ruff config into `pyproject.toml` automatically — the
project may not have one, or the user may prefer a separate file.
The standalone `ruff.toml` is unambiguous.

**Forbidden shortcuts:**

| Shortcut | Why it's wrong |
|---|---|
| "I know what ruff.toml should contain" → author from memory | The bundled template carries `experiments/**` per-file ignores, the numpydoc convention, and a curated rule selection. Memory misses these and the contract silently breaks |
| Read this skill's SKILL.md text describing the template → write from that | The SKILL.md describes; the template file *is*. Read the file itself, write it verbatim |

## When ruff finds something Claude didn't write

A common case: Claude edits one function in a file that already had
unrelated `D`-rule violations. Ruff will report those too.

- **In scope of this turn**: the lines Claude touched. Fix those.
- **Out of scope**: pre-existing warnings in untouched code.
  Mention them in the response so the user can choose to address
  them, but don't drag every warning into the current task.

This keeps PR scope tight and avoids "while I was here" expansion
that the user didn't ask for.

## Companion skills

- **`data-science-python-stack`** — owns the decision that ruff is
  Tier 1 mandatory; this skill assumes ruff is already installed.
  If `pixi run ruff --version` fails, return there for the install.
- **`python-env-manager`** — turns "ruff is missing" into the right
  install command for the project's manager. Don't run `pip install
  ruff` in a pixi project.
- **`organize-ml-workspace`** — sets up the directory layout that
  the bundled `ruff.toml`'s per-file ignores (`experiments/**`)
  reference. Drop the template *after* this skill has run, so the
  paths it ignores actually exist.
- **`update-config`** — only relevant if the user explicitly asks
  for an automated lint hook later. Default is no hook.

## Conventions

- **Manual, not automatic.** Claude calls ruff itself, file by
  file. No hook.
- **One-fix-per-file rule.** Hard cap on retries — second pass max,
  then surface.
- **Project-root config only.** `ruff.toml` lives at the project
  root and is the single source of truth. Don't add per-directory
  overrides unless the user asks.
- **Don't widen scope on touched files.** Fix what Claude wrote;
  surface (don't auto-fix) pre-existing issues elsewhere.
