#!/usr/bin/env bash
#
# verify_layout.sh
#
# Asserts the env layout is correct for the detected manager. Run
# after any env mutation (G-ENV-SCOPE add, agent feature install,
# optional-feature install, manual manifest edit) to catch drift
# before it bites at LSP time.
#
# Per-manager checks:
#   * Manifest declares the required features / groups.
#   * The `lsp` view (pixi env / uv all-groups / poetry --with all)
#     composes every dep the project knows about.
#   * `pyrightconfig.json` is at the project root with the right
#     `pythonPath`.
#
# Returns 0 on success, 1 on drift, 2 on "manager not yet supported".
# Stdout is human-readable; stderr carries remediation guidance.
#
# Currently supports: pixi (default), uv, poetry. Other managers
# (hatch / conda / pip+venv) print a "not yet supported — see
# references/per_manager_footguns.md for the manual checklist" message
# and return exit code 2.

set -uo pipefail

PROJECT_ROOT="$(pwd)"
FAILED=0

note() { printf '  [ok]  %s\n' "$1"; }
fail() { printf '  [FAIL] %s\n' "$1" >&2; FAILED=1; }
warn() { printf '  [warn] %s\n' "$1"; }

# ---------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------

# check_pyrightconfig <expected-python-path>
# Verifies pyrightconfig.json is at project root, has a "pythonPath"
# key, and the key matches the expected path. Warns (not fails) on
# mismatch — a custom pythonPath may be intentional.
check_pyrightconfig() {
    local expected="$1"
    printf '\nChecking pyrightconfig.json...\n'
    if [ ! -f "${PROJECT_ROOT}/pyrightconfig.json" ]; then
        fail "pyrightconfig.json missing at project root — run install_agent_feature_<manager>.sh"
        return
    fi
    note "pyrightconfig.json present"
    local py_path
    py_path=$(grep -oE '"pythonPath"[[:space:]]*:[[:space:]]*"[^"]+"' pyrightconfig.json \
        | sed -E 's/.*"([^"]+)"$/\1/')
    if [ -z "$py_path" ]; then
        fail "pyrightconfig.json has no 'pythonPath' key — re-substitute the template"
    elif [ "$py_path" != "$expected" ]; then
        warn "pythonPath is '$py_path' (expected '$expected') — non-standard but may be intentional"
    else
        note "pythonPath = '$py_path'"
    fi
}

# extract_pep735_groups <pyproject-path>
# Echoes the group names declared in [dependency-groups], one per line.
extract_pep735_groups() {
    local pp="$1"
    awk '
        /^\[dependency-groups\]/ { in_block=1; next }
        /^\[/ && in_block { in_block=0 }
        in_block && /^[a-zA-Z_-]+[[:space:]]*=/ {
            name=$1; sub(/[[:space:]]*=.*/, "", name); print name
        }
    ' "$pp"
}

# ---------------------------------------------------------------------
# Detect the manager
# ---------------------------------------------------------------------

if [ -f "${PROJECT_ROOT}/pixi.toml" ]; then
    MANAGER="pixi"
elif [ -f "${PROJECT_ROOT}/uv.lock" ] || grep -q '^\[tool\.uv\]' "${PROJECT_ROOT}/pyproject.toml" 2>/dev/null; then
    MANAGER="uv"
elif [ -f "${PROJECT_ROOT}/poetry.lock" ] || grep -q '^\[tool\.poetry\]' "${PROJECT_ROOT}/pyproject.toml" 2>/dev/null; then
    MANAGER="poetry"
elif grep -q '^\[tool\.hatch\]' "${PROJECT_ROOT}/pyproject.toml" 2>/dev/null; then
    MANAGER="hatch"
elif [ -f "${PROJECT_ROOT}/environment.yml" ]; then
    MANAGER="conda"
elif [ -d "${PROJECT_ROOT}/.venv" ] && [ -f "${PROJECT_ROOT}/requirements.txt" ]; then
    MANAGER="pip+venv"
else
    echo "verify_layout.sh: no env manager detected at ${PROJECT_ROOT}" >&2
    exit 2
fi

printf 'verify_layout.sh — detected manager: %s\n' "$MANAGER"
printf '\n'

# ---------------------------------------------------------------------
# pixi checks
# ---------------------------------------------------------------------

if [ "$MANAGER" = "pixi" ]; then
    printf 'Checking pixi.toml structure...\n'
    for feat in default dev agent; do
        if grep -qE "^\[feature\.${feat}(\.|])" pixi.toml; then
            note "feature '${feat}' declared"
        elif [ "$feat" = "default" ]; then
            if grep -qE '^\[dependencies\]' pixi.toml; then
                note "feature 'default' declared (implicit via [dependencies])"
            else
                fail "feature 'default' not declared (no [feature.default.*] or top-level [dependencies])"
            fi
        else
            fail "feature '${feat}' not declared in pixi.toml — run install_agent_feature_pixi.sh"
        fi
    done

    printf '\nChecking pixi.toml environments...\n'
    for env in default dev agent lsp; do
        if grep -qE "^${env}[[:space:]]*=" pixi.toml; then
            note "env '${env}' declared"
        else
            fail "env '${env}' not declared in pixi.toml [environments] — run install_agent_feature_pixi.sh"
        fi
    done

    printf '\nChecking lsp env composition...\n'
    LSP_LINE=$(grep -E '^lsp[[:space:]]*=' pixi.toml || true)
    if [ -z "$LSP_LINE" ]; then
        fail "lsp env not declared — cannot verify composition"
    else
        LSP_FEATS=$(echo "$LSP_LINE" | sed -nE 's/.*features[[:space:]]*=[[:space:]]*\[([^]]+)\].*/\1/p')
        for feat in default dev agent; do
            if echo "$LSP_FEATS" | grep -qE "\"${feat}\""; then
                note "lsp includes '${feat}'"
            else
                fail "lsp env does NOT include '${feat}' — pyright will miss ${feat} deps"
            fi
        done
        OPT_FEATS=$(grep -oE '^\[feature\.([^.\]]+)' pixi.toml | sed -E 's/.*feature\.//' | sort -u)
        for opt in $OPT_FEATS; do
            if [ "$opt" = "default" ] || [ "$opt" = "dev" ] || [ "$opt" = "agent" ]; then
                continue
            fi
            if echo "$LSP_FEATS" | grep -qE "\"${opt}\""; then
                note "lsp includes optional feature '${opt}'"
            else
                fail "optional feature '${opt}' is declared but NOT in lsp — append to lsp's features list and re-run 'pixi install -e lsp'"
            fi
        done
    fi

    printf '\nChecking .pixi/envs/lsp...\n'
    if [ -d "${PROJECT_ROOT}/.pixi/envs/lsp" ]; then
        note ".pixi/envs/lsp exists"
        if [ -x "${PROJECT_ROOT}/.pixi/envs/lsp/bin/python" ]; then
            note ".pixi/envs/lsp/bin/python is executable"
        else
            fail ".pixi/envs/lsp/bin/python missing or not executable — run 'pixi install -e lsp'"
        fi
    else
        fail ".pixi/envs/lsp not materialized — run 'pixi install -e lsp'"
    fi

    check_pyrightconfig ".pixi/envs/lsp/bin/python"
fi

# ---------------------------------------------------------------------
# uv checks
# ---------------------------------------------------------------------

if [ "$MANAGER" = "uv" ]; then
    if [ ! -f "${PROJECT_ROOT}/pyproject.toml" ]; then
        fail "pyproject.toml not at project root"
    else
        printf 'Checking pyproject.toml [dependency-groups]...\n'
        if ! grep -qE '^\[dependency-groups\]' pyproject.toml; then
            fail "[dependency-groups] table missing — run install_agent_feature_uv.sh"
        else
            note "[dependency-groups] declared"
            UV_GROUPS=$(extract_pep735_groups pyproject.toml)
            for grp in dev agent; do
                if echo "$UV_GROUPS" | grep -qE "^${grp}$"; then
                    note "group '${grp}' declared"
                else
                    fail "group '${grp}' not declared in [dependency-groups] — run install_agent_feature_uv.sh"
                fi
            done
            # Any additional groups beyond dev/agent are optional features; surface them
            OPT_GROUPS=$(echo "$UV_GROUPS" | grep -vE '^(dev|agent)$' || true)
            if [ -n "$OPT_GROUPS" ]; then
                for opt in $OPT_GROUPS; do
                    note "optional group '${opt}' declared (will be picked up by 'uv sync --all-groups')"
                done
            fi
        fi
    fi

    printf '\nChecking .venv...\n'
    if [ -d "${PROJECT_ROOT}/.venv" ]; then
        note ".venv exists"
        if [ -x "${PROJECT_ROOT}/.venv/bin/python" ]; then
            note ".venv/bin/python is executable"
        else
            fail ".venv/bin/python missing or not executable — run 'uv sync --all-groups'"
        fi
    else
        fail ".venv not materialized — run 'uv sync --all-groups'"
    fi

    # Confirm pyright + ipython are visible in the .venv (the agent group
    # was synced). The cheapest check is to look for site-packages dirs.
    printf '\nChecking agent group is synced into .venv...\n'
    PY_SP=$(find "${PROJECT_ROOT}/.venv/lib" -maxdepth 2 -type d -name 'site-packages' 2>/dev/null | head -1)
    if [ -n "$PY_SP" ]; then
        for pkg in IPython pyright; do
            # IPython is a dir; pyright is also a dir (npm/python wrapper)
            if [ -d "$PY_SP/$pkg" ] || compgen -G "$PY_SP/${pkg}-"* > /dev/null 2>&1 || compgen -G "$PY_SP/${pkg}_"* > /dev/null 2>&1; then
                note "${pkg} present in .venv site-packages"
            else
                fail "${pkg} not in .venv site-packages — run 'uv sync --all-groups'"
            fi
        done
    else
        warn ".venv has no site-packages dir yet — run 'uv sync --all-groups'"
    fi

    check_pyrightconfig ".venv/bin/python"
fi

# ---------------------------------------------------------------------
# poetry checks
# ---------------------------------------------------------------------

if [ "$MANAGER" = "poetry" ]; then
    if [ ! -f "${PROJECT_ROOT}/pyproject.toml" ]; then
        fail "pyproject.toml not at project root"
    else
        printf 'Checking poetry group declarations...\n'
        LEGACY_GROUPS=$(grep -oE '^\[tool\.poetry\.group\.[^]]+\]' pyproject.toml 2>/dev/null \
            | sed -E 's/.*group\.([^].]+).*/\1/' \
            | sort -u)
        PEP735_GROUPS=""
        if grep -qE '^\[dependency-groups\]' pyproject.toml; then
            PEP735_GROUPS=$(extract_pep735_groups pyproject.toml)
        fi
        ALL_GROUPS=$(printf '%s\n%s\n' "$LEGACY_GROUPS" "$PEP735_GROUPS" \
            | grep -v '^$' | sort -u)
        for grp in dev agent; do
            if echo "$ALL_GROUPS" | grep -qE "^${grp}$"; then
                note "group '${grp}' declared (legacy or PEP 735)"
            else
                fail "group '${grp}' not declared — run install_agent_feature_poetry.sh"
            fi
        done
        OPT_GROUPS=$(echo "$ALL_GROUPS" | grep -vE '^(dev|agent)$' || true)
        if [ -n "$OPT_GROUPS" ]; then
            for opt in $OPT_GROUPS; do
                note "optional group '${opt}' declared (must be passed to 'poetry install --with')"
            done
        fi
    fi

    printf '\nChecking poetry virtualenvs.in-project setting...\n'
    if command -v poetry >/dev/null 2>&1; then
        IN_PROJECT=$(poetry config virtualenvs.in-project 2>/dev/null || echo "unknown")
        if [ "$IN_PROJECT" = "true" ]; then
            note "virtualenvs.in-project = true (env at .venv, portable pyrightconfig)"
        else
            fail "virtualenvs.in-project = ${IN_PROJECT} — set to 'true' or pyrightconfig becomes machine-local: 'poetry config virtualenvs.in-project true'"
        fi
    else
        warn "poetry not on PATH — cannot verify virtualenvs.in-project setting"
    fi

    printf '\nChecking .venv...\n'
    if [ -d "${PROJECT_ROOT}/.venv" ]; then
        note ".venv exists"
        if [ -x "${PROJECT_ROOT}/.venv/bin/python" ]; then
            note ".venv/bin/python is executable"
        else
            fail ".venv/bin/python missing or not executable — run install_agent_feature_poetry.sh"
        fi
    else
        fail ".venv not at project root — set 'poetry config virtualenvs.in-project true' then 'poetry install'"
    fi

    printf '\nChecking agent group is installed into .venv...\n'
    PY_SP=$(find "${PROJECT_ROOT}/.venv/lib" -maxdepth 2 -type d -name 'site-packages' 2>/dev/null | head -1)
    if [ -n "$PY_SP" ]; then
        for pkg in IPython pyright; do
            if [ -d "$PY_SP/$pkg" ] || compgen -G "$PY_SP/${pkg}-"* > /dev/null 2>&1 || compgen -G "$PY_SP/${pkg}_"* > /dev/null 2>&1; then
                note "${pkg} present in .venv site-packages"
            else
                fail "${pkg} not in .venv site-packages — run 'poetry install --with dev,agent'"
            fi
        done
    else
        warn ".venv has no site-packages dir yet — run 'poetry install --with dev,agent'"
    fi

    check_pyrightconfig ".venv/bin/python"
fi

# ---------------------------------------------------------------------
# Other managers — not yet supported
# ---------------------------------------------------------------------

if [ "$MANAGER" != "pixi" ] && [ "$MANAGER" != "uv" ] && [ "$MANAGER" != "poetry" ]; then
    printf 'verify_layout.sh: %s not yet supported — see\n' "$MANAGER" >&2
    printf '  references/per_manager_footguns.md\n' >&2
    printf 'for the manual checklist.\n' >&2
    exit 2
fi

# ---------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------

printf '\n'
if [ "$FAILED" -ne 0 ]; then
    printf 'verify_layout.sh: drift detected — see [FAIL] lines above for remediation.\n' >&2
    exit 1
fi
printf 'verify_layout.sh: layout OK for %s.\n' "$MANAGER"
exit 0
