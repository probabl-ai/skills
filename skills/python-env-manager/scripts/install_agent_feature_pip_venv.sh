#!/usr/bin/env bash
#
# install_agent_feature_pip_venv.sh <requirements-file>
#
# Installs the agent feature (ipython + pyright) on a pip+venv-managed
# project. Takes the project's main requirements file as its sole
# argument; uses it to populate the agent and lsp venvs with runtime deps.
#
# IMPORTANT: pip+venv has no manifest integrity. The user must
# maintain dep lists by hand. This script creates two venvs:
#   .venv-agent  — runtime + ipython + pyright
#   .venv-lsp    — runtime + ruff + pytest + jupyterlab + ipykernel
#                  + ipython + pyright + optional
# Both source their runtime deps from <requirements-file>. Optional
# deps for the lsp venv must be added by the user after the script
# runs.
#
# Steps:
#   1. Verify the requirements file exists.
#   2. Create .venv-agent with runtime + ipython + pyright.
#   3. Create .venv-lsp with runtime + dev (ruff, pytest, jupyterlab,
#      ipykernel) + agent (ipython, pyright).
#   4. Substitute the bundled `pyrightconfig.json` template
#      (<PYTHON_PATH> → .venv-lsp/bin/python) and write to project root.
#   5. Verify ipython and pyright are callable.
#
# Exit codes:
#   0  — install + verification succeeded
#   1  — preconditions / install / verification failed

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 <requirements-file>" >&2
    echo "  Reads runtime deps from the requirements file (one per line)." >&2
    exit 1
fi
REQ="$1"

if [ ! -f "$REQ" ]; then
    echo "ERROR: requirements file not found: $REQ" >&2
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 is not on PATH." >&2
    exit 1
fi

echo "[1/5] Reading runtime deps from $REQ..."
RUNTIME=$(grep -vE '^\s*(#|$)' "$REQ" | tr '\n' ' ')
echo "       deps: $RUNTIME"

echo "[2/5] Creating .venv-agent..."
python3 -m venv .venv-agent
# shellcheck disable=SC1091
source .venv-agent/bin/activate
pip install --upgrade pip
# shellcheck disable=SC2086
pip install $RUNTIME ipython pyright
deactivate

echo "[3/5] Creating .venv-lsp..."
python3 -m venv .venv-lsp
# shellcheck disable=SC1091
source .venv-lsp/bin/activate
pip install --upgrade pip
# shellcheck disable=SC2086
pip install $RUNTIME ruff pytest jupyterlab ipykernel ipython pyright
deactivate

echo "[4/5] Substituting pyrightconfig.json template..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$SCRIPT_DIR/../templates/pyrightconfig.json"
if [ ! -f "$TEMPLATE" ]; then
    echo "ERROR: template not found at $TEMPLATE" >&2
    exit 1
fi
sed -e 's|<PYTHON_PATH>|.venv-lsp/bin/python|g' "$TEMPLATE" > ./pyrightconfig.json
echo "       wrote ./pyrightconfig.json"

echo "[5/5] Verifying ipython and pyright are callable in .venv-agent..."
if ! .venv-agent/bin/python -c "import IPython; print('ipython OK')" >/dev/null 2>&1; then
    echo "ERROR: ipython verification failed" >&2
    exit 1
fi
if ! .venv-agent/bin/pyright --version >/dev/null 2>&1; then
    echo "ERROR: pyright verification failed" >&2
    exit 1
fi
echo "       ipython + pyright callable"

echo ""
echo "Done. Agent feature installed; .venv-lsp ready for the opencode LSP."
echo "NOTE: pip+venv has no manifest. Re-running this script with new deps"
echo "      requires re-creating the venvs from scratch — there is no"
echo "      reproducibility track here. Migration to pixi / uv recommended."
echo "NOTE: opencode reads pyrightconfig.json at session startup. Mid-session"
echo "      config changes won't take effect until the next opencode session."
