#!/usr/bin/env bash
#
# install_agent_feature_uv.sh
#
# Installs the agent feature (ipython + pyright) on a uv-managed project.
# Zero arguments — run from project root.
#
# uv has no env composition; the project has a single `.venv` and groups
# are installed into it via `--all-groups` on sync. After this script
# runs, `.venv` contains runtime + dev + agent + all optional groups.
#
# Steps:
#   1. Add `ipython` + `pyright` to the `agent` dependency group.
#   2. `uv sync --all-groups` to install every group into `.venv`.
#   3. Substitute the bundled `pyrightconfig.json` template
#      (<PYTHON_PATH> → .venv/bin/python) and write it to the project
#      root.
#   4. Verify ipython and pyright are callable from the agent group.
#
# Exit codes:
#   0  — install + verification succeeded
#   1  — install or verification failed

set -euo pipefail

if [ ! -f pyproject.toml ]; then
    echo "ERROR: pyproject.toml not at cwd. Run this from the project root." >&2
    exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
    echo "ERROR: uv is not on PATH. Install uv first." >&2
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
    exit 1
fi

echo "[1/4] Adding ipython + pyright to the agent dependency group..."
uv add --group agent ipython pyright

echo "[2/4] Syncing all groups into .venv (runtime + dev + agent + optional)..."
uv sync --all-groups

echo "[3/4] Substituting pyrightconfig.json template..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$SCRIPT_DIR/../templates/pyrightconfig.json"
if [ ! -f "$TEMPLATE" ]; then
    echo "ERROR: template not found at $TEMPLATE" >&2
    exit 1
fi
sed -e 's|<PYTHON_PATH>|.venv/bin/python|g' "$TEMPLATE" > ./pyrightconfig.json
echo "       wrote ./pyrightconfig.json"

echo "[4/4] Verifying ipython and pyright are callable..."
if ! uv run --group agent python -c "import IPython; print('ipython OK')" >/dev/null 2>&1; then
    echo "ERROR: ipython verification failed" >&2
    exit 1
fi
if ! uv run --group agent pyright --version >/dev/null 2>&1; then
    echo "ERROR: pyright verification failed" >&2
    exit 1
fi
echo "       ipython + pyright callable"

echo ""
echo "Done. Agent feature installed; .venv has all groups for the opencode LSP."
echo "NOTE: opencode reads pyrightconfig.json at session startup. Mid-session"
echo "      config changes won't take effect until the next opencode session."
