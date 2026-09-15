# Python Env Manager — skore variant per mode

Why `skore` vs `skore[hub]` vs `skore[mlflow]` matters, and the
procedure for switching modes mid-project. Cross-referenced from
SKILL.md § "Tier 1 install: skore variant per mode".

## Why the variant matters

Hub mode calls `skore.login(mode="hub")` before instantiating
`skore.Project(...)`. That `login` flow is implemented in the
`[hub]` extra; on a plain `skore` install,
`from skore import login` raises `ImportError`.

MLflow mode instantiates `skore.Project(mode="mlflow",
tracking_uri=...)`, which drives an MLflow client under the hood;
that client lives in the `[mlflow]` extra. On a plain `skore`
install, constructing an mlflow-mode Project raises `ImportError` /
`ModuleNotFoundError` for `mlflow`.

Installing the wrong variant silently produces working CI for
local-mode operations but breaks hub-mode operations at first
`login()`, or mlflow-mode operations at first `Project(...)`.

## The `[jupyter]` extra — PyPI only

A second axis, orthogonal to mode: the package **source**.

- **conda-forge** (`pixi`, `conda` / `mamba`) — the conda-forge
  `skore` package already bundles the jupyter integration
  (ipywidgets-based `TableReport` rendering, `report.*` widgets).
  No extras needed beyond `[hub]` for hub mode.
- **PyPI** (`uv`, `poetry`, `hatch`, `pip`+`venv`) — the PyPI
  `skore` wheel ships the jupyter integration behind the
  `[jupyter]` extra. Without it, `TableReport(...)` and the audit
  flow's `report.*` widgets fail to render in `jupyterlab` (the
  widget falls back to a `<…Display at 0x…>` repr).

Combined matrix:

| `skore mode:` | conda-forge install | PyPI install |
|---|---|---|
| `local` | `skore` | `skore[jupyter]` |
| `hub` | `skore[hub]` | `skore[hub,jupyter]` |
| `mlflow` | `skore[mlflow]` + `mlflow>=3` | `skore[mlflow,jupyter]` + `mlflow>=3` |

Why a single combined extra string for PyPI hub / mlflow mode: PEP
508 allows comma-separated extras (`skore[hub,jupyter]`,
`skore[mlflow,jupyter]`) and that's the form all four PyPI-based
managers accept. Splitting into two install calls works too but
produces two manifest rows, which is noisier than necessary.

### Why the `mlflow>=3` pin

The `skore[mlflow]` extra declares mlflow as a dependency with a loose
lower bound, so the environment solver can resolve an **old mlflow
(2.x)** — which the skore MLflow backend (`skore.Project(mode="mlflow",
...)`) does not support. Co-install an explicit `mlflow>=3` constraint
so the solver is forced onto mlflow 3+:

- conda-forge: `pixi add "skore[mlflow]" "mlflow>=3"`
- PyPI: `uv add "skore[mlflow,jupyter]" "mlflow>=3"` (and the poetry /
  hatch / pip equivalents).

This is a hard requirement of the mlflow variant — the install is
considered wrong without it.

## Forbidden

- Silently picking `skore[hub]` / `skore[mlflow]` "to be safe" or
  "because the user might want it later". The `[hub]` / `[mlflow]`
  extras cost network deps + infrastructure (auth for hub, the
  mlflow client for mlflow) the local-mode user did not ask for;
  the gate-based split exists to avoid that.
- Dropping `[jupyter]` on PyPI installs. The audit flow's report
  widgets and the TableReport viz silently degrade.
- Adding `[jupyter]` on conda-forge installs. Redundant — the
  conda-forge package already brings the integration in.
- Installing `skore[mlflow]` **without** the `mlflow>=3` pin. The
  solver will happily resolve mlflow 2.x, which the skore MLflow
  backend does not support — see § "Why the `mlflow>=3` pin".

## Reading the recorded decision

Before issuing the skore install command, read
`journal/JOURNAL.md` Status `Workspace decisions` for the
`skore mode:` row.

If the row is absent (workspace not yet bootstrapped through
`organize-ml-workspace`), route back to `organize-ml-workspace` §
G-SKORE-MODE — do not guess. The default proposal at G-SKORE-MODE
is `local`, but **the decision is the user's**, not the install
layer's.

## Switching modes mid-project

If the user pivots `skore mode:` mid-project (per
`organize-ml-workspace` § "Switching skore mode mid-project is
forbidden by default" — requires explicit user confirmation):

- **`local` → `hub`**: run the manager's `add` command for the
  hub variant over the existing install — `"skore[hub]"`
  (conda-forge) or `"skore[hub,jupyter]"` (PyPI). The extra deps
  land additively; existing local-mode reports under `reports/`
  stay on disk but are no longer the active store.
- **`local` → `mlflow`** (or **`hub` → `mlflow`**): add the mlflow
  variant **with the pin** — `"skore[mlflow]" "mlflow>=3"`
  (conda-forge) or `"skore[mlflow,jupyter]" "mlflow>=3"` (PyPI). The
  prior store's reports stay where they were (disk / Skore Hub) but
  are no longer the active store.
- **`hub` / `mlflow` → `local`**: optionally remove the extra to
  slim the env. Per-manager: `pixi remove skore && pixi add skore`
  (conda-forge) or `uv remove skore && uv add "skore[jupyter]"`
  (PyPI), and the equivalents for poetry / hatch / pip+venv.
  Existing hub-/mlflow-mode reports stay on their backend but are
  no longer the active store from this workspace.

In all directions, surface to the user that the prior store's
reports are orphaned from this workspace's perspective until a
manual migration.
