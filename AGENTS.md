# AGENTS

Applies repo-wide.

## Workflow

- Read the closest `AGENTS.md` for the area you touch.
- Run relevant hooks/tests locally before opening a PR.
- PR title: `type(scope): Imperative summary`. All CI checks must pass before merge.
- Avoid redundant comments that restate what obvious code already expresses.

## Coding Discipline

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

- State assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features, abstractions, or configurability beyond what was asked.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

- Don't improve adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.
- Remove imports/variables/functions that YOUR changes made unused.

Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## CLI package (`src/skore_skills`)

Any change under `src/skore_skills/` **ships pytest in the same PR**.
Do not land a subcommand or helper uncovered, and do not defer tests
to a follow-up.

Before opening a PR that touches the CLI or its tests:

1. `pixi run -e lint lint`
2. `pixi run -e test-py311 tests` (pytest with `--cov=skore_skills`)

New subcommands need tests for the happy path, bad argv / missing
inputs, and at least one failure mode. Do not merge if the change
adds branches Codecov would mark uncovered (project/patch drop
beyond the 1% auto threshold in `codecov.yml`).

Catalog-only edits (`skills/`, `.catalog.json`, plugin manifests):
run `pixi run check`. Do not run the LLM eval suite unless the PR
touches `eval/` or `skills/*/SKILL.md`.
