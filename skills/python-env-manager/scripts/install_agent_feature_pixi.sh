#!/usr/bin/env bash
#
# install_agent_feature_pixi.sh
#
# Installs the agent feature (ipython + pyright) and composes the `lsp`
# env on a pixi-managed project. Zero arguments — run from project root.
#
# Idempotent: safe to re-run; existing envs / features are detected and
# skipped rather than re-created.
#
# Steps:
#   1. Add `ipython` + `pyright` to the `agent` feature.
#   2. Ensure the `lsp` env composes default + dev + agent (+ any
#      already-declared optional features).
#   3. Sync the `lsp` env.
#   4. Substitute the bundled `pyrightconfig.json` template
#      (<PYTHON_PATH> → .pixi/envs/lsp/bin/python) and write it to the
#      project root.
#   5. Verify ipython and pyright are callable from the agent env.
#
# Exit codes:
#   0  — install + verification succeeded
#   1  — install or verification failed; nothing was rolled back

set -euo pipefail

if [ ! -f pixi.toml ]; then
    echo "ERROR: pixi.toml not at cwd. Run this from the project root." >&2
    exit 1
fi

if ! command -v pixi >/dev/null 2>&1; then
    echo "ERROR: pixi is not on PATH. Install pixi first." >&2
    echo "  curl -fsSL https://pixi.sh/install.sh | sh" >&2
    exit 1
fi

echo "[1/5] Adding ipython + pyright to the agent feature..."
pixi add --feature agent ipython pyright

echo "[2/5] Ensuring the lsp env composes default + dev + agent..."
if pixi info 2>/dev/null | grep -q "Environment: lsp"; then
    echo "       lsp env already declared; leaving features list as-is"
    echo "       (if you added an optional feature, append it to lsp by hand)"
else
    pixi project environment add lsp --feature default --feature dev --feature agent
fi

echo "[3/5] Installing lsp env (this is the largest env; may take a while)..."
pixi install -e lsp

echo "[4/5] Substituting pyrightconfig.json template..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$SCRIPT_DIR/../templates/pyrightconfig.json"
if [ ! -f "$TEMPLATE" ]; then
    echo "ERROR: template not found at $TEMPLATE" >&2
    exit 1
fi
sed -e 's|<PYTHON_PATH>|.pixi/envs/lsp/bin/python|g' "$TEMPLATE" > ./pyrightconfig.json
echo "       wrote ./pyrightconfig.json"

echo "[5/5] Verifying ipython and pyright are callable..."
if ! pixi run -e agent ipython -c "print('ipython OK')" >/dev/null 2>&1; then
    echo "ERROR: ipython verification failed in the agent env" >&2
    exit 1
fi
if ! pixi run -e agent pyright --version >/dev/null 2>&1; then
    echo "ERROR: pyright verification failed in the agent env" >&2
    exit 1
fi
echo "       ipython + pyright callable in agent env"

echo ""
echo "Done. Agent feature installed; lsp env ready for the opencode LSP."
echo "NOTE: opencode reads pyrightconfig.json at session startup. If you"
echo "      are mid-session, the LSP won't pick up this config until the"
echo "      next opencode session starts."
