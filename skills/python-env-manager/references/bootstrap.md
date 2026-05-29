# Python Env Manager — Bootstrap detail

Full step-by-step pixi bootstrap when no manager is detected.
Cross-referenced from SKILL.md § Bootstrap. Load when scaffolding
a fresh workspace.

## Pre-conditions

- Detection (SKILL.md § Detection) found nothing at the project
  root.
- G-ENV-MGR fired and the user picked `pixi` (or another manager —
  mirror the same flow with the per-manager equivalents from
  SKILL.md § "Install commands — by manager").
- G-SKORE-MODE has resolved (SKILL.md § "Tier 1 install: skore
  variant per mode" reads the `skore mode:` row).
- G-TABULAR has resolved (the tabular library pick lives in
  `organize-ml-workspace` § G-TABULAR).
- G-PKG-NAME has resolved (`organize-ml-workspace` § G-PKG-NAME).

## The 9 steps (pixi)

### 1. Check pixi is on PATH

```bash
command -v pixi
```

If pixi is not installed, surface the install command and **ask the
user to run it** (do not run `curl | sh` yourself):

- Linux/macOS: `curl -fsSL https://pixi.sh/install.sh | sh`
- Windows: `iwr -useb https://pixi.sh/install.ps1 | iex`

### 2. Initialize the manifest

```bash
pixi init
```

Creates `pixi.toml` in the current directory. The default
generated content is minimal; the next step replaces it.

### 3. Apply the enforced 4-env layout

No user ask — the layout is the convention (SKILL.md § "Where does
the package belong?"). Edit `pixi.toml`:

```toml
[feature.default.dependencies]
# runtime deps land here (added in step 5)

[feature.dev.dependencies]
ruff = "*"
pytest = "*"

[feature.agent.dependencies]
ipython = "*"
pyright = "*"

[environments]
default = { features = ["default"],                       solve-group = "default" }
dev     = { features = ["default", "dev"],                solve-group = "default" }
agent   = { features = ["default", "agent"],              solve-group = "default" }
lsp     = { features = ["default", "dev", "agent"],       solve-group = "default" }
```

The `lsp` env composes every feature so the opencode LSP /
pyright sees every import path the user could write across `src/`
/ `tests/` / `experiments/` / `audit/`.

### 4. Add Tier 1 runtime deps to `default`

The skore install variant follows G-SKORE-MODE:

- `skore mode: local` → `pixi add scikit-learn skrub skore`
- `skore mode: hub`   → `pixi add scikit-learn skrub "skore[hub]"`

If G-SKORE-MODE hasn't fired yet at bootstrap time (rare —
`organize-ml-workspace` fires it alongside G-PKG-NAME and
G-TABULAR), route back to that skill before issuing the install
command. `ruff` / `pytest` are added by step 3 (the `[feature.dev]`
declaration); `ipython` / `pyright` are added by step 3 (the
`[feature.agent]` declaration). No per-install ask needed — the
layout dictates the routing.

**macOS post-install:** because skrub just landed, run
`pixi run dot -c` (or the manager-equivalent env-run) once on macOS
to rebuild graphviz's plugin cache — see SKILL.md § "skrub install
— macOS post-install". Linux + Windows: skip.

### 5. Add the tabular library

Per G-TABULAR (`organize-ml-workspace`):

- pandas branch: `pixi add pandas pyarrow`
- polars branch: `pixi add polars`

### 6. Wire the editable workspace package

Per `references/editable_workspace.md`:

```bash
pixi add --pypi "<pkg> @ ."
```

Then edit `pixi.toml` `[pypi-dependencies]` to flip the entry to:

```toml
<pkg> = { path = ".", editable = true }
```

Then `pixi install`. The name-prefixed `<pkg> @ .` syntax is
required by pixi 0.69; the bare `--editable .` form is rejected
with `× URL requirement must be preceded by a package name`.

### 7. Drop `pyrightconfig.json`

```bash
sed -e 's|<PYTHON_PATH>|.pixi/envs/lsp/bin/python|g' \
    .agents/skills/python-env-manager/templates/pyrightconfig.json \
    > ./pyrightconfig.json
```

### 8. Sync all four envs

```bash
pixi install                # syncs default
pixi install -e dev
pixi install -e agent
pixi install -e lsp         # largest of the four; what pyright reads from
```

### 9. Verify

```bash
pixi run python -c "import sklearn, skrub, skore"   # Tier 1
pixi run -e dev ruff --version                       # dev
pixi run -e agent ipython -c "print(0)"              # agent
pixi run -e agent pyright --version                  # agent
ls pyrightconfig.json                                # config dropped
```

All commands must succeed before declaring the bootstrap complete.

## Other managers

If the user picked a different manager (uv / poetry / hatch /
conda), mirror this flow with:

- The manager's `init` command (uv `init`, poetry `init`, hatch
  `new`, conda `create -n <project>`).
- The analogous 4-env mapping from SKILL.md § "Install commands —
  by manager" (uv groups, poetry groups, hatch envs, conda named
  envs).
- The per-manager editable install from
  `references/editable_workspace.md`.
- The per-manager `<PYTHON_PATH>` substitution from
  `references/agent_feature_anatomy.md`.

The 9-step shape is identical; only the commands change.
