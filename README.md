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
| [build-ml-pipeline](skills/build-ml-pipeline/SKILL.md) | Build a machine learning pipeline from the data source to the learner, including multi-tables engineering. |
| [evaluate-ml-pipeline](skills/evaluate-ml-pipeline/SKILL.md) | Evaluate a complex machine learning pipeline and get structured reports including metrics, plots, and diagnostics. |
| [test-ml-pipeline](skills/test-ml-pipeline/SKILL.md) | Make sure that your machine learning pipeline is production-ready statistically and functionally. |
| [smoke-test-ml-pipeline](skills/smoke-test-ml-pipeline/SKILL.md) | Stress test your machine learning pipeline on future data to make sure it works. |
| [audit-ml-pipeline](skills/audit-ml-pipeline/SKILL.md) | Once testing . |

## Iteration loop

| Skill | Description |
| --- | --- |
| [iterate-ml-experiment](skills/iterate-ml-experiment/SKILL.md) | Design, keep track of experiments and iterate on them. |
| [iterate-from-skore](skills/iterate-from-skore/SKILL.md) | Use skore to run diagnostics and checks that can be reported and addressed in the next experiment. |
| [iterate-from-user](skills/iterate-from-user/SKILL.md) | As a user be in the loop and propose new experiments — free-text, a scientific article URL, or a resource link (GitHub issue / spec / reference repo). |

## Workspace and tooling

| Skill | Description |
| --- | --- |
| [organize-ml-workspace](skills/organize-ml-workspace/SKILL.md) | An organized workspace to keep track of your experiments. |
| [python-code-style](skills/python-code-style/SKILL.md) | Enforce good practices out-of-the-box for the Python ecosystem for your code. |
| [python-env-manager](skills/python-env-manager/SKILL.md) | Bootstrapping the experiment setup based on your favorite Python environment manager. |
| [data-science-python-stack](skills/data-science-python-stack/SKILL.md) | Opinionated one-library-per-job Python stack, organized into mandatory / user-choice / optional / transitive tiers. |

## API references

| Skill | Description |
| --- | --- |
| [python-api](skills/python-api/SKILL.md) | Discover the public API of any installed Python package to make agent find their way without bothering your workspace. |
