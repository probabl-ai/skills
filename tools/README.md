# tools/

Maintenance scripts for this repository. Every script is pure
standard-library Python; the recommended entry point is the
`pixi` task runner declared in `pixi.toml`.

## Pixi tasks

```bash
pixi run hash         # refresh per-skill + aggregate hashes in catalog.json
pixi run hash-check   # verify hashes match the on-disk skills (no writes)
pixi run validate     # validate catalog.json structure (skills, categories, workflows)
pixi run check        # composite: hash-check + validate (the CI entry point)
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
