# Python Env Manager — per-manager footguns

Manager-specific traps when composing the `lsp` env and writing
`pyrightconfig.json`. SKILL.md links here from § "Composition model"
and § "Agent feature install". Read this when a per-manager install
script fails, or before recommending a manager to a user.

The bundled per-manager install scripts under
`.agents/skills/python-env-manager/scripts/install_agent_feature_<manager>.sh`
encode the workarounds for each of these footguns. If you find
yourself re-typing the equivalent commands by hand, you are almost
certainly going to hit one of these failure modes — run the script
instead.

## pixi

The `lsp` env grows on every optional-feature addition (per
`SKILL.md` § "Where does the package belong?" — § "Procedure when a
new named feature is picked"). When G-ENV-SCOPE creates a new
feature `foo`, the same step must append `"foo"` to `lsp`'s
`features` list, then re-run `pixi install -e lsp`. Forgetting
either step is the most common drift: the new dep is installable
into the `foo` env but pyright doesn't see it → legitimate code
shows "unresolved import" warnings.

`scripts/install_agent_feature_pixi.sh` covers the initial install
only — when adding optional features later, follow the procedure in
SKILL.md § G-ENV-SCOPE.

## uv

`uv sync` without `--all-groups` will install only the default
group. The `lsp` env is the same `.venv` as every other env (uv is
single-env per project); the composition is by sync flags, not by
env name. Use `uv sync --all-groups` after every dep add to keep
`.venv` current.

`scripts/install_agent_feature_uv.sh` runs `uv sync --all-groups`
on every invocation, so this is handled at install time. After
later optional-feature additions, the agent must re-run
`uv sync --all-groups` (or the install script) to keep `.venv`
indexed by pyright.

## poetry

If `virtualenvs.in-project` is false (poetry's default), the env
lives in poetry's user-level cache dir, and the `pythonPath` in
`pyrightconfig.json` becomes absolute and machine-local — not
portable across machines / CI.

`scripts/install_agent_feature_poetry.sh` runs `poetry config
virtualenvs.in-project true` as its first step, forcing the env
to `.venv` at the project root. This makes the `pythonPath` in
`pyrightconfig.json` portable. **If a user has already installed
poetry deps into the cache dir before this gate fires**, the
script will create a new `.venv` and the cached env is
orphaned — surface this to the user before running.

## hatch

`hatch env find <name>` returns an absolute path in hatch's data
dir (`~/.local/share/hatch/env/virtual/...`), not project-
relative. The `pyrightconfig.json` is therefore machine-local —
not portable.

Hatch envs do not compose. The `agent` env and the `lsp` env must
both list every runtime dep explicitly. The install script errors
out if those sections aren't authored in `pyproject.toml`; it
does NOT attempt to fill them in (the runtime dep list is the
user's contract).

For new projects, recommend pixi or uv over hatch when the LSP
integration is in scope. The duplication cost compounds with
every optional feature.

## conda

The envs dir is global (`conda env list` shows paths). The
`pyrightconfig.json` `pythonPath` will point at an absolute path
under that dir, which is machine-local. Not portable across
machines / CI.

The duplicated-deps cost from `SKILL.md` § "Where does the
package belong?" applies — every dep lands in three separate envs
(`<project>-agent`, `<project>-lsp`, the runtime env). The
install script requires `environment-agent.yml` and
`environment-lsp.yml` at cwd; it doesn't attempt to derive deps
from a single `environment.yml`.

## pip + venv

The manager-of-last-resort. No manifest, no reproducibility, no
shared cache between `.venv-agent` and `.venv-lsp`. Recommend
migration to a managed alternative (pixi by default) before
investing in the LSP integration.

The install script requires the runtime-deps file as an argument;
it cannot derive the deps from any project metadata.
