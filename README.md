# Probabl Skills

A set of skills to steer your AI-assisted machine learning experiments.
The skills help you:

- build your machine learning pipeline with core data science libraries
  (e.g. scikit-learn, skrub, skore, pandas, polars) while ensuring
  your agent follows correct methodologies
- evaluate and store your results so you can easily audit and get insights from them
- connect your agent to [Skore Hub](https://skore.probabl.ai/) to get a comprehensive view of
  your experiments and results
- iterate on your next experiments from a Skore audit digest (a
  separate backlog turn) and from your own feedback
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
as Qwen 3.7 Flash or DeepSeek v4.1 Flash.

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
skore skills install setup  # workspace, environment, git, export
skore skills install data_analysis  # data exploration
skore skills install model  # frame, build, smoke-test, evaluate, audit
skore skills install loop   # triage, explore, model, review, backlog, export
skore skills install export  # notebooks and documentation site
```

`skore skills install ml-experimentation` remains the complete pack,
containing every active skill. The default `install` / `install all`
behavior is unchanged.

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
| [triage-ml-task](skills/triage-ml-task/SKILL.md) | Session owner: list installed entry skills and ask which to run. |
| [review-ml-choices](skills/review-ml-choices/SKILL.md) | Show stored project choices and re-enter the skill that can change one. |
| [review-ml-experiment](skills/review-ml-experiment/SKILL.md) | Read the stored report, then write one idea file and one Ideas row per candidate. |
| [setup-ml-project](skills/setup-ml-project/SKILL.md) | Ask only the setup pieces that are not already recorded, then coordinate workspace, environment, and git. |
| [setup-workspace](skills/setup-workspace/SKILL.md) | Detect or scaffold the standard ML workspace layout. |
| [setup-python-env](skills/setup-python-env/SKILL.md) | Detect the env manager and bootstrap the runtime, agent-tools, and composed development environments. |
| [setup-git](skills/setup-git/SKILL.md) | Initialize safe version control for an ML workspace. |
| [persist-ml-git](skills/persist-ml-git/SKILL.md) | Commit the current loop stage when git end-turn says invoke. |
| [model-ml-pipeline](skills/model-ml-pipeline/SKILL.md) | Require locked problem framing, write the first baseline design note for approval, then coordinate later choices, build, smoke testing, evaluation, and audit. |
| [export-ml-project](skills/export-ml-project/SKILL.md) | Coordinate executed notebooks and an offline MkDocs site. |
| [sync-ml-reports](skills/sync-ml-reports/SKILL.md) | Copy skore reports between local, Hub, and MLflow, and optionally switch the upload destination. |

### ML pipeline lifecycle

| Skill | Description |
| --- | --- |
| [explore-ml-data](skills/explore-ml-data/SKILL.md) | Explore the dataset before designing any model. |
| [frame-ml-problem](skills/frame-ml-problem/SKILL.md) | Record the problem, deployment setting, metric, baseline, and fold count before any model code. |
| [research-ml-practice](skills/research-ml-practice/SKILL.md) | Literature research for an ML methodology concern. |
| [build-ml-pipeline](skills/build-ml-pipeline/SKILL.md) | Declare a skrub DataOps graph from the data source to the predictor after framing is locked. |
| [evaluate-ml-pipeline](skills/evaluate-ml-pipeline/SKILL.md) | Evaluate one sklearn-compatible learner with the locked validation scheme and persist structured skore reports. |
| [smoke-test-ml-pipeline](skills/smoke-test-ml-pipeline/SKILL.md) | Structural pytest: prediction count must match the predict-grid row count. |
| [audit-ml-pipeline](skills/audit-ml-pipeline/SKILL.md) | Audit a persisted skore report read-only and produce a reusable digest. |

### Ideas and backlog

| Skill | Description |
| --- | --- |
| [manage-ml-backlog](skills/manage-ml-backlog/SKILL.md) | Record experiment outcomes and triage idea files. A promoted idea moves from the Ideas table into a Backlog row. |
| [shape-user-idea](skills/shape-user-idea/SKILL.md) | Shape a user idea or a named artifact into one idea file and one Ideas row after they confirm. |
| [search-ml-literature](skills/search-ml-literature/SKILL.md) | Search scientific and technical sources and write one idea file and one Ideas row for the direction the user confirms. |

### Workspace and tooling

| Skill | Description |
| --- | --- |
| [add-python-package](skills/add-python-package/SKILL.md) | Add a dependency through the project env manager, or ask the user when the environment is user-managed. |
| [choose-python-library](skills/choose-python-library/SKILL.md) | Resolve a library choice and add the selected dependency. |
| [plot-ml-figure](skills/plot-ml-figure/SKILL.md) | Pick pandas, seaborn, plotly, or matplotlib before writing figure code. |
| [export-ml-notebook](skills/export-ml-notebook/SKILL.md) | Convert a jupytext percent file into an executed notebook. |
| [export-ml-site](skills/export-ml-site/SKILL.md) | Package workspace markdown and existing notebook HTML into an offline MkDocs site. |

Canonical package policy lives in the CLI; print it with `python -m skore_skills env stack`. `choose-python-library` resolves competing libraries.

### Compatibility and removed skills

The catalog temporarily retains two deprecated compatibility skills. They are not
included in workflow packs:

| Deprecated skill | Replacement |
| --- | --- |
| [organize-ml-workspace](skills/organize-ml-workspace/SKILL.md) | Use [setup-workspace](skills/setup-workspace/SKILL.md). |
| [data-science-python-stack](skills/data-science-python-stack/SKILL.md) | Use [choose-python-library](skills/choose-python-library/SKILL.md) and the canonical package policy. |

Catalog ids `python-env-manager` and `python-code-style` have been removed. Run
`skore skills remove` on any leftover sidecars and reinstall the setup pack.

## Website

The catalog page lives in `site/` and is published at
<https://probabl-ai.github.io/skills/>.

Build it with the `site` Pixi environment, which provides Node.js:

```bash
pixi run -e site site-build
```

Pull requests that change `site/`, `.catalog.json`, or the Pixi manifest build
the site in CI. GitHub Pages builds it from `main` when those same paths change.
A repo admin turns this on once: Settings → Pages → Source **GitHub Actions**.
If Pages is enabled after that workflow is already on `main`, run the **Pages**
workflow with **Run workflow**. Catalog edits still go through `pixi run check`.
