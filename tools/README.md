# tools/

Maintenance scripts for this repository. Every script is pure
standard-library Python; the recommended entry point is the
`pixi` task runner declared in `pixi.toml`.

## Pixi tasks

```bash
pixi run hash           # refresh per-skill + aggregate hashes in .catalog.json
pixi run hash-check     # verify hashes match the on-disk skills (no writes)
pixi run evals-check    # verify generated evals.json files match eval prompts
pixi run validate       # validate .catalog.json structure (skills, categories, workflows)
pixi run check-versions # verify the version matches across all declaring sources
pixi run integration-validate # verify integration scenario files and the seed snapshot
pixi run bump-major     # bump the major version across all version sources
pixi run bump-minor     # bump the minor version across all version sources
pixi run bump-patch     # bump the patch version across all version sources
pixi run check          # composite: hash-check + evals-check + validate + check-versions + integration-validate
```

`pixi run check` is what CI invokes via `prefix-dev/setup-pixi` — see
`.github/workflows/validate-catalog.yml`.

`evals-check` only verifies generated eval fixtures. Optional LLM skill
evals live in a separate pixi environment and are **not** run in catalog
CI. See [`eval/README.md`](../eval/README.md):

```bash
pixi install -e eval
pixi run -e eval eval -- -k build-ml-pipeline
```

## hash_skills.py

Computes a SHA-256 digest of every skill listed in `.catalog.json`
and writes it back into each skill's `hash` field. A top-level
`catalog_hash` is then computed over the sorted `(id, hash)` pairs to
give a stable fingerprint of the whole catalog.

The hash for a skill covers every file under its `path` directory
recursively, excluding `.DS_Store`, `__pycache__/`, `.pytest_cache/`,
`.mypy_cache/`, and `*.pyc` / `*.pyo` files. File paths are normalised
to POSIX so digests are stable across operating systems.

## validate_catalog.py

Checks these invariants:

1. Every directory under `skills/` has a matching entry in
   `.catalog.json`'s `skills` array, and vice versa.
2. Every catalog entry's `path` resolves to a directory containing a
   `SKILL.md` file.
3. Every skill entry uses a known `category` and a permitted
   `subcategory` (or `null` when the category takes none).
4. Every workflow's `includes` list references known skill ids.
5. Every `SKILL.md` description is shorter than 1024 characters.
   The count is the folded `description: >` text, including the
   final newline YAML clip chomping keeps.
6. Every `SKILL.md` ends its frontmatter with an unindented
   `metadata:` block whose `modelTier` is `small`, `medium`, or
   `big`. `role`, when present, is `entry` or `helper`.
7. At most one skill declares `metadata.role: entry`.
8. No skill loads a `metadata.role: helper` skill whose `modelTier`
   is higher than its own: a helper loaded while its caller keeps
   working runs on at most the caller's model, so its tier would never
   apply. Loads are `load` / `route to` / `re-enter` / `hand off to`
   instructions; `return to` and prohibitions are not. The entry skill
   is exempt.

Run directly with `python tools/validate_catalog.py` or via
`pixi run validate`.

## check_versions.py

Checks that the package version agrees across every source that declares
it by hand, so a release bump can't leave one file lagging behind:

1. `.catalog.json` — top-level `version`.
2. `pixi.toml` — `[workspace] version`.
3. `pyproject.toml` — `[project] version`.
4. `.claude-plugin/plugin.json` — `version`.
5. `.claude-plugin/marketplace.json` — each `plugins[].version`.
6. `.cursor-plugin/plugin.json` — `version`.

Run directly with `python tools/check_versions.py` or via
`pixi run check-versions`.

## integration_scenario.py

Validates, copies, prints, checks, and runs the scenarios under
`integration/scenarios/`. A scenario is a seed workspace, ordered
replies, filesystem snapshots, and a driver file. Manual checks stay
available. `run` launches Pi.
See [`integration/README.md`](../integration/README.md).

`validate` checks ids, the driver, fork links, expect keys, relative
paths, and that the seed matches the `setup-open` snapshot. `pixi run
check` includes this step.

```bash
python tools/integration_scenario.py materialize california-housing --dest ../housing
python tools/integration_scenario.py prompt california-housing --turn setup-open
python tools/integration_scenario.py check california-housing --workspace ../housing --turn setup-open
python tools/integration_scenario.py run california-housing --workspace ../housing
python tools/integration_scenario.py run california-housing --workspace ../housing --interactive
```

`run` launches Pi. It does not install Pi. `--interactive` shows the TUI.
Pi defaults to OpenRouter `~deepseek/deepseek-flash-latest`; `--model`
overrides that, and `--harness-arg` forwards any other token. Headless
output is streamed and stored under `.transcripts/integration/<run-id>/`
with `result.json`. `--approve` applies to that workspace only. The
journey can run `pixi`. Pi requires `pi install npm:@probabl/pi-skore`.
Before Pi starts, the runner stages the workflow sidecars, passes the
checkout skill paths with `--skill`, and prepends this checkout's `src`
to `PYTHONPATH`. The copied `SCENARIO.md` requires extension `skill(...)`
calls and adds this checkout's `skore-skills` as an editable pixi
dependency after pixi is initialized.

## bump_version.py

Increments the semver `major`, `minor`, or `patch` component and writes
the new version consistently to every source that declares it:

1. `.catalog.json` — top-level `version`.
2. `pixi.toml` — `[workspace] version`.
3. `pyproject.toml` — `[project] version`.
4. `.claude-plugin/plugin.json` — `version`.
5. `.claude-plugin/marketplace.json` — each `plugins[].version`.
6. `.cursor-plugin/plugin.json` — `version`.

The script refuses to run when those sources disagree. Use `--dry-run`
to preview the bump without writing files. It does not create git commits
or tags — review and commit the changes yourself.

```bash
python tools/bump_version.py patch --dry-run
pixi run bump-patch
```
