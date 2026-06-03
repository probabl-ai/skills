# tools/

Maintenance scripts for this repository. Every script is pure
standard-library Python; the recommended entry point is the
`pixi` task runner declared in `pixi.toml`.

## Pixi tasks

```bash
pixi run hash           # refresh per-skill + aggregate hashes in catalog.json
pixi run hash-check     # verify hashes match the on-disk skills (no writes)
pixi run validate       # validate catalog.json structure (skills, categories, workflows)
pixi run check-versions # verify the version matches across all declaring sources
pixi run bump-major     # bump the major version across all version sources
pixi run bump-minor     # bump the minor version across all version sources
pixi run bump-patch     # bump the patch version across all version sources
pixi run check          # composite: hash-check + validate + check-versions (the CI entry point)
```

`pixi run check` is what CI invokes via `prefix-dev/setup-pixi` — see
`.github/workflows/validate-catalog.yml`.

## hash_skills.py

Computes a SHA-256 digest of every skill listed in `catalog.json`
and writes it back into each skill's `hash` field. A top-level
`catalog_hash` is then computed over the sorted `(id, hash)` pairs to
give a stable fingerprint of the whole catalog.

The hash for a skill covers every file under its `path` directory
recursively, excluding `.DS_Store`, `__pycache__/`, `.pytest_cache/`,
`.mypy_cache/`, and `*.pyc` / `*.pyo` files. File paths are normalised
to POSIX so digests are stable across operating systems.

## validate_catalog.py

Checks four invariants:

1. Every directory under `skills/` has a matching entry in
   `catalog.json`'s `skills` array, and vice versa.
2. Every catalog entry's `path` resolves to a directory containing a
   `SKILL.md` file.
3. Every skill entry uses a known `category` and a permitted
   `subcategory` (or `null` when the category takes none).
4. Every workflow's `includes` list references known skill ids.

Run directly with `python tools/validate_catalog.py` or via
`pixi run validate`.

## check_versions.py

Checks that the package version agrees across every source that declares
it by hand, so a release bump can't leave one file lagging behind:

1. `catalog.json` — top-level `version`.
2. `pixi.toml` — `[workspace] version`.
3. `.claude-plugin/plugin.json` — `version`.
4. `.claude-plugin/marketplace.json` — each `plugins[].version`.
5. `.cursor-plugin/plugin.json` — `version`.

Run directly with `python tools/check_versions.py` or via
`pixi run check-versions`.

## bump_version.py

Increments the semver `major`, `minor`, or `patch` component and writes
the new version consistently to every source that declares it:

1. `catalog.json` — top-level `version`.
2. `pixi.toml` — `[workspace] version`.
3. `.claude-plugin/plugin.json` — `version`.
4. `.claude-plugin/marketplace.json` — each `plugins[].version`.
5. `.cursor-plugin/plugin.json` — `version`.

The script refuses to run when those sources disagree. Use `--dry-run`
to preview the bump without writing files. It does not create git commits
or tags — review and commit the changes yourself.

```bash
python tools/bump_version.py patch --dry-run
pixi run bump-patch
```
