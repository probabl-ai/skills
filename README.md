# Probabl Skills

A set of skills to steer your AI-assisted machine learning experiments.
The skills help you:

- build your machine learning pipeline with core data science libraries
  (e.g. scikit-learn, skrub, skore, pandas, polar) while ensuring
  your agent follows correct methodologies
- evaluate and store your results so you can easily audit and get insights from them
- connect your agent to [Skore Hub](https://skore.probabl.ai/) to get a comprehensive view of
  your experiments and results
- iterate on your next experiments using insights from Skore diagnostics and your own
  feedback
- organize your workspace according to best practices for data science projects
  (e.g. cookiecutter template)

Probabl skills let you focus on the science while AI agents handle the implementation,
guided by two important ingredients: core data science libraries for maintainability  and
methodological best practices for running your machine learning experiments properly.

In practice, from a prompt such as:

```text
╭────────────────────────────────────────────────────────────────────────╮
│ > Given the context in the file `data/README.md` and the data located  │
│   in `data/`, let's build a first machine learning pipeline that will  │
│   serve as baseline for the next experiments that we are going to run  │
│   together.                                                            │
╰────────────────────────────────────────────────────────────────────────╯
```

you can expect your agent to start experimenting with you. The skills work well with
models such as Claude Opus and Sonnet and produce great results with smaller models such
as Qwen 3.6 30B or DeepSeek v4 Flash.

As for agent harnesses, we tested them with Claude Code, OpenCode, Cursor, and GitHub
Copilot and found no significant difference in terms of skill invocation.

## Install

You can install the skills using the `skore` CLI that you can install from PyPI or from
conda-forge and run the following command.

First install [skore-cli](https://github.com/probabl-ai/skore-cli):
```
# with pip
pip install skore-cli
# with uv
uv tool install skore-cli
# with pixi
pixi global install skore-cli
```

Then run the following command:

```bash
skore skills install
```

Install a smaller workflow pack by id when you do not need the full
companion:

```bash
skore skills install setup  # workspace, environment, stack, style
skore skills install eda    # data exploration
skore skills install model  # build, evaluate, test, smoke
skore skills install loop   # triage, backlog, audit, sourcing
```

`skore skills install ml-experimentation` remains the complete pack,
and the default `install` / `install all` behavior is unchanged.

You can use `uvx` or `pixi exec` to install the `skore` CLI and directly run the
command in an isolated environment:

```bash
uvx --from skore-cli skore skills install
```

or

```bash
pixi exec --spec skore-cli skore skills install
```

If you prefer `npx`, then you can use:

```bash
npx skills add probabl-ai/skills
```

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

## Skills in detail

### Meta and setup actions

| Skill | Description |
| --- | --- |
| [triage-ml-task](skills/triage-ml-task/SKILL.md) | Own the canonical loop and ask one next-stage question. |
| [setup-ml-project](skills/setup-ml-project/SKILL.md) | Coordinate workspace, environment, and git setup. |
| [setup-workspace](skills/setup-workspace/SKILL.md) | Detect or scaffold the standard ML workspace layout. |
| [setup-python-env](skills/setup-python-env/SKILL.md) | Configure dependencies, editable install, and Python code style. |
| [setup-git](skills/setup-git/SKILL.md) | Initialize safe version control for an ML workspace. |
| [model-ml-pipeline](skills/model-ml-pipeline/SKILL.md) | Coordinate build, evaluation, and smoke testing. |
| [choose-python-library](skills/choose-python-library/SKILL.md) | Resolve a library choice and add the selected dependency. |

### ML pipeline lifecycle

| Skill | Description |
| --- | --- |
| [explore-ml-data](skills/explore-ml-data/SKILL.md) | Explore the dataset before designing any model. |
| [build-ml-pipeline](skills/build-ml-pipeline/SKILL.md) | Build a machine learning pipeline from the data source to the learner, including multi-tables engineering. |
| [evaluate-ml-pipeline](skills/evaluate-ml-pipeline/SKILL.md) | Evaluate a complex machine learning pipeline and get structured reports including metrics, plots, and diagnostics. |
| [smoke-test-ml-pipeline](skills/smoke-test-ml-pipeline/SKILL.md) | Stress test your machine learning pipeline on future data to make sure it works. |
| [audit-ml-pipeline](skills/audit-ml-pipeline/SKILL.md) | Once testing and the experiment are done, audit the model by loading a skore report and investigate. |

### Iteration loop

| Skill | Description |
| --- | --- |
| [iterate-ml-experiment](skills/iterate-ml-experiment/SKILL.md) | Deprecated one-release pointer to triage and backlog. |
| [manage-ml-backlog](skills/manage-ml-backlog/SKILL.md) | Record experiment outcomes and next-lever backlog rows. |
| [iterate-from-skore](skills/iterate-from-skore/SKILL.md) | Use skore to run diagnostics and checks that can be reported and addressed in the next experiment. |
| [iterate-from-user](skills/iterate-from-user/SKILL.md) | As a user, be in the loop and propose new experiments — free-text, a scientific article URL, or a resource link (GitHub issue / spec / reference repo). |

### Workspace and tooling

| Skill | Description |
| --- | --- |
| [setup-workspace](skills/setup-workspace/SKILL.md) | An organized workspace to keep track of experiments. |
| [setup-python-env](skills/setup-python-env/SKILL.md) | Environment, editable install, Ruff configuration, and style execution. |
| [choose-python-library](skills/choose-python-library/SKILL.md) | Select optional libraries without reopening fixed stack choices. |

### API references

| Skill | Description |
| --- | --- |
