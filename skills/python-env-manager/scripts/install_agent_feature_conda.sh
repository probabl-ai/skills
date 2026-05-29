#!/usr/bin/env bash
#
# install_agent_feature_conda.sh <project-name>
#
# Installs the agent feature (ipython + pyright) on a conda-managed
# project. Takes the project name as its sole argument; uses it to
# build env names `<project>-agent` and `<project>-lsp`.
#
# IMPORTANT: conda has no env composition. Both envs must duplicate
# the runtime deps. This script REQUIRES the user to maintain
# manifest files declaring the deps:
#   environment-agent.yml — runtime + ipython + pyright
#   environment-lsp.yml   — runtime + ruff + pytest + jupyterlab
#                           + ipykernel + ipython + pyright
#                           + every optional-feature dep
# If only `environment.yml` exists, the script appends ipython + pyright
# for the agent env, but cannot derive the lsp env's full dep list
# automatically — it errors and asks the user to author environment-lsp.yml.
#
# Steps:
#   1. Verify environment-agent.yml exists (or attempt to derive from
#      environment.yml + ipython + pyright).
#   2. Verify environment-lsp.yml exists; error if not.
#   3. Create both envs via `conda env create`.
#   4. Substitute the bundled `pyrightconfig.json` template
#      (<PYTHON_PATH> → absolute path to the lsp env's interpreter,
#      machine-local) and write it to the project root.
#   5. Verify ipython and pyright are callable in the agent env.
#
# Exit codes:
#   0  — install + verification succeeded
#   1  — preconditions / install / verification failed

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 <project-name>" >&2
    echo "  Creates conda envs <project-name>-agent and <project-name>-lsp" >&2
    exit 1
fi
PROJECT="$1"
AGENT_ENV="${PROJECT}-agent"
LSP_ENV="${PROJECT}-lsp"

if ! command -v conda >/dev/null 2>&1; then
    echo "ERROR: conda is not on PATH. Install Miniconda / Anaconda first." >&2
    exit 1
fi

echo "[1/5] Verifying environment-agent.yml..."
if [ ! -f environment-agent.yml ]; then
    echo "ERROR: environment-agent.yml not at cwd." >&2
    echo "       Author it with: name: ${AGENT_ENV}" >&2
    echo "                       channels: [conda-forge]" >&2
    echo "                       dependencies: [<runtime deps>, ipython, pyright]" >&2
    exit 1
fi

echo "[2/5] Verifying environment-lsp.yml..."
if [ ! -f environment-lsp.yml ]; then
    echo "ERROR: environment-lsp.yml not at cwd." >&2
    echo "       Author it with: name: ${LSP_ENV}" >&2
    echo "                       channels: [conda-forge]" >&2
    echo "                       dependencies: [<runtime>, ruff, pytest, jupyterlab, ipykernel, ipython, pyright, <optional>]" >&2
    exit 1
fi

echo "[3/5] Creating conda envs..."
conda env create -f environment-agent.yml || conda env update -f environment-agent.yml --prune
conda env create -f environment-lsp.yml   || conda env update -f environment-lsp.yml   --prune

echo "[4/5] Substituting pyrightconfig.json template (ABSOLUTE path)..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$SCRIPT_DIR/../templates/pyrightconfig.json"
if [ ! -f "$TEMPLATE" ]; then
    echo "ERROR: template not found at $TEMPLATE" >&2
    exit 1
fi
LSP_PY="$(conda info --base)/envs/${LSP_ENV}/bin/python"
if [ ! -x "$LSP_PY" ]; then
    echo "ERROR: lsp env's python not found at $LSP_PY" >&2
    exit 1
fi
sed -e "s|<PYTHON_PATH>|$LSP_PY|g" "$TEMPLATE" > ./pyrightconfig.json
echo "       wrote ./pyrightconfig.json with pythonPath=$LSP_PY"
echo "       WARNING: this path is machine-local; pyrightconfig.json is NOT portable across machines / CI."

echo "[5/5] Verifying ipython and pyright are callable..."
if ! conda run -n "${AGENT_ENV}" python -c "import IPython; print('ipython OK')" >/dev/null 2>&1; then
    echo "ERROR: ipython verification failed in ${AGENT_ENV}" >&2
    exit 1
fi
if ! conda run -n "${AGENT_ENV}" pyright --version >/dev/null 2>&1; then
    echo "ERROR: pyright verification failed in ${AGENT_ENV}" >&2
    exit 1
fi
echo "       ipython + pyright callable"

echo ""
echo "Done. Agent feature installed; ${LSP_ENV} ready for the opencode LSP."
echo "NOTE: opencode reads pyrightconfig.json at session startup. Mid-session"
echo "      config changes won't take effect until the next opencode session."
