#!/usr/bin/env bash
#
# install_agent_feature_hatch.sh
#
# Installs the agent feature (ipython + pyright) on a hatch-managed
# project. Zero arguments — run from project root.
#
# IMPORTANT: hatch envs do not compose. Before running this script the
# user must have edited `pyproject.toml` to add BOTH:
#   [tool.hatch.envs.agent]
#       dependencies = [ <all runtime deps>, "ipython", "pyright" ]
#   [tool.hatch.envs.lsp]
#       dependencies = [ <all runtime deps>, "ruff", "pytest",
#                        "ipython", "pyright", <all optional deps> ]
# This script verifies those sections exist before creating the envs.
#
# Steps:
#   1. Verify [tool.hatch.envs.agent] and [tool.hatch.envs.lsp] exist.
#   2. Create both envs via `hatch env create`.
#   3. Substitute the bundled `pyrightconfig.json` template
#      (<PYTHON_PATH> → $(hatch env find lsp)/bin/python — ABSOLUTE,
#      machine-local) and write it to the project root.
#   4. Verify ipython and pyright are callable in the agent env.
#
# Exit codes:
#   0  — install + verification succeeded
#   1  — preconditions / install / verification failed

set -euo pipefail

if [ ! -f pyproject.toml ]; then
    echo "ERROR: pyproject.toml not at cwd. Run this from the project root." >&2
    exit 1
fi

if ! command -v hatch >/dev/null 2>&1; then
    echo "ERROR: hatch is not on PATH. Install hatch first." >&2
    exit 1
fi

echo "[1/4] Verifying hatch env declarations in pyproject.toml..."
if ! grep -q '^\[tool\.hatch\.envs\.agent\]' pyproject.toml; then
    echo "ERROR: [tool.hatch.envs.agent] not declared in pyproject.toml." >&2
    echo "       Add it manually with dependencies = [<runtime deps>, \"ipython\", \"pyright\"]." >&2
    echo "       Hatch envs do not compose; runtime deps must be duplicated." >&2
    exit 1
fi
if ! grep -q '^\[tool\.hatch\.envs\.lsp\]' pyproject.toml; then
    echo "ERROR: [tool.hatch.envs.lsp] not declared in pyproject.toml." >&2
    echo "       Add it manually with dependencies = [<runtime>, ruff, pytest, ipython, pyright, <optional>]." >&2
    exit 1
fi
echo "       both envs declared"

echo "[2/4] Creating hatch envs..."
hatch env create agent || true
hatch env create lsp || true

echo "[3/4] Substituting pyrightconfig.json template (ABSOLUTE path)..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$SCRIPT_DIR/../templates/pyrightconfig.json"
if [ ! -f "$TEMPLATE" ]; then
    echo "ERROR: template not found at $TEMPLATE" >&2
    exit 1
fi
LSP_PY="$(hatch env find lsp)/bin/python"
if [ ! -x "$LSP_PY" ]; then
    echo "ERROR: hatch env find lsp returned a non-existent Python interpreter: $LSP_PY" >&2
    exit 1
fi
sed -e "s|<PYTHON_PATH>|$LSP_PY|g" "$TEMPLATE" > ./pyrightconfig.json
echo "       wrote ./pyrightconfig.json with pythonPath=$LSP_PY"
echo "       WARNING: this path is machine-local; pyrightconfig.json is NOT portable across machines / CI."

echo "[4/4] Verifying ipython and pyright are callable in the agent env..."
if ! hatch run agent:python -c "import IPython; print('ipython OK')" >/dev/null 2>&1; then
    echo "ERROR: ipython verification failed in the agent env" >&2
    exit 1
fi
if ! hatch run agent:pyright --version >/dev/null 2>&1; then
    echo "ERROR: pyright verification failed in the agent env" >&2
    exit 1
fi
echo "       ipython + pyright callable"

echo ""
echo "Done. Agent feature installed; lsp env ready for the opencode LSP."
echo "NOTE: opencode reads pyrightconfig.json at session startup. Mid-session"
echo "      config changes won't take effect until the next opencode session."
