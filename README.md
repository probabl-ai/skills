# Probabl Skills

A set of skills to team up with you in your machine learning experimentation journey.
It helps you at:

- organizing your workspace
- building your machine learning pipeline with the right libraries ensuring good methodologies
- evaluating and storing your results such that you can easily audit and get insights from them
- couple it with [Skore Hub](https://skore.probabl.ai/) to get a comprehensive view of your experiments and their results
- iterate on your next experiments taking insights thanks to Skore diagnostics and your own feedback

So we aim at allowing you to focus on the science, letting AI agents to take care about
the implementation but guided by two important ingredients: great libraries for the
maintainability and good methodologies to make experiments right.

## Install

One command, 55+ agents — including **Claude Code, Codex, Cursor, OpenCode, Gemini CLI, and Mistral Vibe**:

```bash
npx skills add probabl-ai/skills
```

That's the [`skills`](https://github.com/vercel-labs/skills) CLI from Vercel
Labs. It auto-detects which coding agents you have installed and drops the
skills into each one's skills directory — no per-agent configuration.

Install the **full bundle**. The skills cross-reference each other.

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

```bash
/plugin marketplace add probabl-ai/skills
```

```bash
/plugin install probabl-skills@probabl-skills
```

`/plugin update` pulls new releases.

### Coming soon

`skore` will provide a CLI
(cf. [skore CLI](https://github.com/probabl-ai/skore/pull/2976)) to help you with the
following:

```bash
uvx skore skills install
```

or

```bash
pixi exec skore skills install
```

or assuming that `skore` is already installed:

```bash
skore skills install
```

Skore comes with the following commands to deal with the skills:

```bash
skore skills find    # discover the list of skills
skore skills list    # list the installed skills
skore skills update  # update the skills to the latest version
skore skills remove  # remove the skills
```

## Skills in details

### ML pipeline lifecycle

| Skill | Description |
| --- | --- |
| [build-ml-pipeline](skills/build-ml-pipeline/SKILL.md) | Build a machine learning pipeline from the data source to the learner, including multi-tables engineering. |
| [evaluate-ml-pipeline](skills/evaluate-ml-pipeline/SKILL.md) | Evaluate a complex machine learning pipeline and get structured reports including metrics, plots, and diagnostics. |
| [test-ml-pipeline](skills/test-ml-pipeline/SKILL.md) | Make sure that your machine learning pipeline is production-ready statistically and functionally. |
| [smoke-test-ml-pipeline](skills/smoke-test-ml-pipeline/SKILL.md) | Stress test your machine learning pipeline on future data to make sure it works. |
| [audit-ml-pipeline](skills/audit-ml-pipeline/SKILL.md) | Once testing . |

### Iteration loop

| Skill | Description |
| --- | --- |
| [iterate-ml-experiment](skills/iterate-ml-experiment/SKILL.md) | Design, keep track of experiments and iterate on them. |
| [iterate-from-skore](skills/iterate-from-skore/SKILL.md) | Use skore to run diagnostics and checks that can be reported and addressed in the next experiment. |
| [iterate-from-user](skills/iterate-from-user/SKILL.md) | As a user be in the loop and propose new experiments — free-text, a scientific article URL, or a resource link (GitHub issue / spec / reference repo). |

### Workspace and tooling

| Skill | Description |
| --- | --- |
| [organize-ml-workspace](skills/organize-ml-workspace/SKILL.md) | An organized workspace to keep track of your experiments. |
| [python-code-style](skills/python-code-style/SKILL.md) | Enforce good practices out-of-the-box for the Python ecosystem for your code. |
| [python-env-manager](skills/python-env-manager/SKILL.md) | Bootstrapping the experiment setup based on your favorite Python environment manager. |
| [data-science-python-stack](skills/data-science-python-stack/SKILL.md) | Opinionated one-library-per-job Python stack, organized into mandatory / user-choice / optional / transitive tiers. |

### API references

| Skill | Description |
| --- | --- |
| [python-api](skills/python-api/SKILL.md) | Discover the public API of any installed Python package to make agent find their way without bothering your workspace. |
