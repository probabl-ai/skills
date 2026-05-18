# Scaffold steps — full Decision flow with rationale

SKILL.md has the 13-step compact form. This file elaborates the
rationale and examples per step. Load when the inline version
doesn't answer a "why does this step do X?" question.

## Step 1 — Detection

Run `ls`/Glob on the project root. The Detection table in SKILL.md
lists the signals. **Any signal present → glue.** No signal → fresh
scaffold.

Most common confusion: a `pyproject.toml` exists but only carries
`[tool.pixi]` (no `[project]` section + no
`[tool.setuptools.packages.find]`). The package isn't declared as
installable — flag this and offer to add the missing
`[project]` + `[tool.setuptools.packages.find]` blocks before
proceeding.

## Step 2 — G-PKG-NAME ask

Two sub-cases:

- **A manifest already exists** with `[project].name = <name>`:
  fire `AskUserQuestion` — *"Keep package name `<name>` for
  `src/<pkg>/`?"* — with options `keep` / `rename to <other>`.
  Reading the manifest alone is **not** sufficient; the
  confirmation is the gate pass.

- **No manifest yet**: fire `AskUserQuestion` with the
  project-root folder name (snake_case) as the proposed default.
  **Do not** run `pixi init` / `uv init` / `poetry init` /
  similar before this gate passes.

Free-text resolution applies: a user message that names the
package directly ("call it `pricing_models`", "use `stock`")
resolves the gate; phrasing that doesn't name it ("you pick", "go
fast") does NOT — fall through to the structured ask.

Record the answer in `journal/JOURNAL.md` Status `Workspace decisions`.

## Step 3 — Drop `pyproject.toml`, route to env-manager

Copy `templates/pyproject.toml` to the project root, substituting
`<pkg>` with the name from step 2. Skip if a `pyproject.toml`
already declares the package via `[project]` + a build backend's
package-discovery section.

**Then hand off to `python-env-manager` § "Editable workspace
package"** for the actual install. Do NOT run the install
command yourself — that skill owns env-manager picks (G-ENV-MGR)
and the per-manager install command.

## Step 4 — Create `src/<pkg>/`

Use `templates/src___init__.py` for `__init__.py` (carries
`PROJECT_ROOT`). Use `templates/src_data.py`,
`templates/src_features.py`, `templates/src_pipeline.py`,
`templates/src_evaluate.py` for the four modules.

Each is a skeleton; the actual content lands later when
`build-ml-pipeline` / `evaluate-ml-pipeline` are invoked.

## Step 5 — Seed `experiments/01_baseline.py`

Copy `templates/experiment.py`, **substituting `<pkg>`** with the
package name from step 2. This substitution is load-bearing: the
`<pkg>` literals appear in `from <pkg> import ...` statements and
are Python syntax errors if left in place — `python-code-style`'s
ruff pass at step 12 will fail on them.

The other placeholders (`<short title>`, `YYYY-MM-DD`,
`<project-name>`, `<experiment-key>`) sit inside markdown comments
or string literals; they don't break syntax, leave them for
`iterate-ml-experiment` § 3 to fill in when the experiment script
is rewritten with real content after the implementation chain.

## Step 6 — Empty `tests/smoke/`

Create the folder. **Do NOT drop placeholder test files** —
`test-ml-pipeline`'s Stop condition forbids a test file before
the matching design note is approved, and no design note exists
at scaffold time.

Per-experiment placeholders land later via `test-ml-pipeline`
(called from `iterate-ml-experiment` § 3 once a design note is
approved).

Verify `pytest` is on the manifest (per `data-science-python-stack`
§ Tier 1); if not, hand off to `python-env-manager` to add it.

## Step 7 — Placeholder `journal/JOURNAL.md`

Drop a literal one-line placeholder:

```
# PLAN

<!-- placeholder; populated by iterate-ml-experiment on first invocation -->
```

This skill **does NOT** read `iterate-ml-experiment`'s
template — each skill owns its own template surface.
`iterate-ml-experiment` rewrites `JOURNAL.md` from its own
`templates/JOURNAL.md` and writes the matching
`journal/01_baseline.md`, validated **before** the experiment
script runs.

## Step 8 — `overview/summary.md` placeholder

Drop `templates/summary.md`. The placeholder documents the
expected structure (project narrative + cross-experiment metrics
table + per-experiment Status blocks) and carries a "_No
experiments recorded yet._" line so the file is meaningful at
scaffold time.

`iterate-ml-experiment` § 4 rewrites it by hand on every outcome
recording. **No Python script in `overview/`** — `summary.md` is
agent-authored prose, not script output.

## Step 9 — Empty `scratch/`

Just `mkdir scratch`. **Do NOT drop a README inside** — the
scratch convention is owned by `python-api` § "Scratch
traceability" and lives in that skill, not in a file on disk.
The folder is the agent's ad-hoc workspace; its contents are
gitignored entirely via step 11.

## Step 10 — Empty `reports/`

Just `mkdir reports`. Skore writes into it on the first run.

## Step 11 — `.gitignore`

If the project root has no `.gitignore`, drop `templates/.gitignore`
(includes `reports/` and `scratch/` lines by default).

If a `.gitignore` already exists, **do not overwrite**. Scan for
the entries this stack expects:

- `__pycache__/`
- `.pixi/`
- `*.egg-info/`
- `mlruns/`, `mlartifacts/`
- `*.db`, `*.db-journal`
- `*.ipynb`
- `scratch/`

Surface any missing ones to the user as a suggested patch; don't
auto-edit. The `reports/` line is **always asked** — some teams
commit their skore store selectively, others gitignore it
entirely; never default without checking. The `scratch/` line is
the default; ask before omitting. There is no
`!scratch/README.md` exception — `scratch/` is gitignored in its
entirety.

## Step 12 — `ruff.toml` + first ruff pass

**Hand off to `python-code-style` § "Initial setup".** That skill
owns its own `templates/ruff.toml`, writes it to the project
root, and runs `ruff format` + `ruff check` against the modules
dropped at step 4.

**Do not copy `templates/ruff.toml` by hand** and run ruff
yourself — invoking the skill is what teaches the agent the
NumPyDoc docstring convention (parameter shape in the type slot,
`Parameters` / `Returns` / `Raises` sections, blank line after
the one-line summary); the config alone only enforces ruff's
`D`-rules, which a one-line docstring silently satisfies.

The skill is **mandatory** at this step; skipping it is the most
common way agents drop the NumPyDoc contract on Day 1.

## Step 13 — Hand back

Hand off to the relevant sibling skill:

- `build-ml-pipeline` for what goes inside `pipeline.py`.
- `evaluate-ml-pipeline` for what `splitter` should be in
  `evaluate.py`.
- `iterate-ml-experiment` for the design-note content and the
  conversational loop with the user.
- `test-ml-pipeline` / `smoke-test-ml-pipeline` for the body of
  `tests/smoke/test_*.py`.
