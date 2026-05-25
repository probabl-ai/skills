# Skills

A collection of skills for ML experimentation in Python, organized around
[skrub](https://skrub-data.org/), [scikit-learn](https://scikit-learn.org/),
and [skore](https://skore.probabl.ai/) and more broadly to the PyData
ecosystem.

## Install

One command, 55+ agents — including **Claude Code, Codex, Cursor, OpenCode, Gemini CLI, and Mistral Vibe**:

```bash
npx skills add probabl-ai/skills
```

That's the [`skills`](https://github.com/vercel-labs/skills) CLI from Vercel
Labs. It auto-detects which coding agents you have installed and drops the
skills into each one's skills directory — no per-agent configuration.

Install the **full bundle**. The skills cross-reference each other (the
iteration-loop skill dispatches to its sourcing strategies, the test router
dispatches to the smoke-test skill, several skills point to `python-api` for
symbol lookups), and the Agent Skills spec doesn't yet carry a `requires`
field, so the CLI can't auto-resolve those references — a partial install
will leave dangling pointers.

Useful flags once you have it:

```bash
npx skills add probabl-ai/skills --list                  # preview the catalog
npx skills add probabl-ai/skills -g                      # global install (~/<agent>/skills/)
npx skills add probabl-ai/skills -a claude-code -a codex # target specific agents
npx skills update                                        # pull the latest
```

See the full agent list and command reference in the
[`skills` CLI docs](https://github.com/vercel-labs/skills#supported-agents).

### Alternative — Claude Code plugin marketplace

If you only use Claude Code and prefer the native plugin flow, this repo is
also a [Claude Code plugin marketplace](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces):

```
/plugin marketplace add probabl-ai/skills
/plugin install probabl-skills@probabl-skills
```

`/plugin update` pulls new releases.

## ML pipeline lifecycle

| Skill | Description |
| --- | --- |
| [build-ml-pipeline](skills/build-ml-pipeline/SKILL.md) | Declare the pipeline from data source to predictor as a skrub DataOps graph. Stops at the declared object — no fit, split, tuning, or persistence. |
| [evaluate-ml-pipeline](skills/evaluate-ml-pipeline/SKILL.md) | Evaluate a single sklearn-compatible learner: pick the right entry point (`skore.evaluate` first), the right cross-validator, and consume report metadata. |
| [test-ml-pipeline](skills/test-ml-pipeline/SKILL.md) | Router that owns the `tests/` folder of an ML workspace and the experiment ↔ test pairing rule. Dispatches to a per-category subskill. |
| [smoke-test-ml-pipeline](skills/smoke-test-ml-pipeline/SKILL.md) | Diagnostic-by-construction pytest that catches the "load → featurize → split" anti-pattern by predicting on a disjoint, no-buffer slice of the real data source. |
| [audit-ml-pipeline](skills/audit-ml-pipeline/SKILL.md) | Owns the `audit/` folder: one `# %%` file per experiment that loads its skore report read-only and uses bare-last-expression cells. The agent executes via jupytext + nbconvert and reads the markdown digest. Read-only — never calls `evaluate` or `put`. |

## Iteration loop

| Skill | Description |
| --- | --- |
| [iterate-ml-experiment](skills/iterate-ml-experiment/SKILL.md) | Drives the iteration loop on top of an ML workspace — owns `journal/JOURNAL.md` and per-experiment design notes, and dispatches to a sourcing strategy below. |
| [iterate-from-skore](skills/iterate-from-skore/SKILL.md) | Source the next experiment by walking `report.diagnosis()` on the previous skore report and turning every actionable finding into a Backlog row. |
| [iterate-from-user](skills/iterate-from-user/SKILL.md) | Source the next experiment from the user directly — free-text, a scientific article URL, or a resource link (GitHub issue / spec / reference repo). |

## Workspace and tooling

| Skill | Description |
| --- | --- |
| [organize-ml-workspace](skills/organize-ml-workspace/SKILL.md) | Decide where files live: reusable code, per-experiment scripts (jupytext-style `# %%`), reports. One file per experiment. |
| [python-code-style](skills/python-code-style/SKILL.md) | Place the project's `ruff.toml` template and run ruff (lint + format) on touched files. numpydoc for docstrings. |
| [python-env-manager](skills/python-env-manager/SKILL.md) | Detect the project's env manager (pixi / uv / poetry / hatch / conda / pip+venv) and issue the right install command. Defaults to pixi when bootstrapping. |
| [data-science-python-stack](skills/data-science-python-stack/SKILL.md) | Opinionated one-library-per-job Python stack, organized into mandatory / user-choice / optional / transitive tiers. |

## API references

| Skill | Description |
| --- | --- |
| [python-api](skills/python-api/SKILL.md) | Discover the public API of any installed Python package — `inspect.signature` + `pydoc.render_doc` for a symbol, `dir` / `pkgutil.iter_modules` for a module, versioned-docs WebSearch + cache for narrative. Carries conceptual orientation for sklearn / skrub / skore. |
