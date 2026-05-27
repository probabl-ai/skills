#!/usr/bin/env bash
#
# install_agent_feature_poetry.sh
#
# Installs the agent feature (ipython + pyright) on a poetry-managed
# project. Zero arguments — run from project root.
#
# Poetry has no env composition; the project has a single env. By
# default poetry puts it in `~/.cache/pypoetry/virtualenvs/...` —
# machine-local and unportable. This script first forces in-project
# venv mode (`.venv`) so the pyrightconfig.json stays portable.
#
# Steps:
#   1. `poetry config virtualenvs.in-project true` (so .venv is project-local).
#   2. Add `ipython` + `pyright` to the `agent` group.
#   3. Detect all declared groups and install them.
#   4. Substitute the bundled `pyrightconfig.json` template
#      (<PYTHON_PATH> → .venv/bin/python) and write it to the project root.
#   5. Verify ipython and pyright are callable.
#
# Exit codes:
#   0  — install + verification succeeded
#   1  — install or verification failed

set -euo pipefail

if [ ! -f pyproject.toml ]; then
    echo "ERROR: pyproject.toml not at cwd. Run this from the project root." >&2
    exit 1
fi

if ! command -v poetry >/dev/null 2>&1; then
    echo "ERROR: poetry is not on PATH. Install poetry first." >&2
    echo "  https://python-poetry.org/docs/#installation" >&2
    exit 1
fi

echo "[1/5] Forcing poetry to use in-project venv (.venv)..."
poetry config virtualenvs.in-project true

echo "[2/5] Adding ipython + pyright to the agent group..."
poetry add --group agent ipython pyright

echo "[3/5] Installing all declared groups..."
# Poetry 2.x supports two group formats:
#   - legacy: [tool.poetry.group.<name>.dependencies] / [tool.poetry.group.<name>]
#   - PEP 735: [dependency-groups] with group names as keys
# Detect both.
LEGACY_GROUPS=$(grep -E '^\[tool\.poetry\.group\.[^]]+\]' pyproject.toml 2>/dev/null \
    | sed -E 's/.*group\.([^].]+).*/\1/' \
    | sort -u)
PEP735_GROUPS=""
if grep -qE '^\[dependency-groups\]' pyproject.toml 2>/dev/null; then
    PEP735_GROUPS=$(awk '
        /^\[dependency-groups\]/ { in_block=1; next }
        /^\[/ && in_block { in_block=0 }
        in_block && /^[a-zA-Z_-]+[[:space:]]*=/ {
            name=$1; sub(/[[:space:]]*=.*/, "", name); print name
        }
    ' pyproject.toml | sort -u)
fi
ALL_GROUPS=$(printf '%s\n%s\n' "$LEGACY_GROUPS" "$PEP735_GROUPS" \
    | grep -v '^$' \
    | sort -u \
    | tr '\n' ',' \
    | sed 's/,$//')
if [ -n "$ALL_GROUPS" ]; then
    echo "       found groups (legacy + PEP 735): $ALL_GROUPS"
    poetry install --with "$ALL_GROUPS"
else
    echo "       no groups detected; running plain poetry install"
    poetry install
fi

echo "[4/5] Substituting pyrightconfig.json template..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$SCRIPT_DIR/../templates/pyrightconfig.json"
if [ ! -f "$TEMPLATE" ]; then
    echo "ERROR: template not found at $TEMPLATE" >&2
    exit 1
fi
sed -e 's|<PYTHON_PATH>|.venv/bin/python|g' "$TEMPLATE" > ./pyrightconfig.json
echo "       wrote ./pyrightconfig.json"

echo "[5/5] Verifying ipython and pyright are callable..."
if ! poetry run python -c "import IPython; print('ipython OK')" >/dev/null 2>&1; then
    echo "ERROR: ipython verification failed" >&2
    exit 1
fi
if ! poetry run pyright --version >/dev/null 2>&1; then
    echo "ERROR: pyright verification failed" >&2
    exit 1
fi
echo "       ipython + pyright callable"

echo ""
echo "Done. Agent feature installed; .venv ready for the opencode LSP."
echo "NOTE: opencode reads pyrightconfig.json at session startup. Mid-session"
echo "      config changes won't take effect until the next opencode session."
