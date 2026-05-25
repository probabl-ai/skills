---
name: python-env-manager
description: >
  Single source of truth for "which Python environment manager does
  this project use, and how do I install a package with it?". Owns
  the detection table (pixi / uv / poetry / hatch / conda+mamba /
  pip+venv), the install / remove / upgrade commands per manager,
  and the bootstrap path when no manager is in place (default
  recommendation: pixi). Stops at "the install command was issued
  with the right manager and the package is importable".

  TRIGGER when (any of these):
  (1) **about to install / add / pin / upgrade / remove a Python
      package** — `pip install`, `pixi add`, `uv add`, `poetry add`,
      `conda install`, etc. — under any framing;
  (2) `data-science-python-stack` § "Missing dependency" surfaced a
      missing import and an install is the next step;
  (3) a workflow skill's Stop condition fired on a missing
      dependency (`build-ml-pipeline`, `evaluate-ml-pipeline`,
      `organize-ml-workspace`, `audit-ml-pipeline`);
  (4) starting a new Python project and no manager is in place yet
      (bootstrap with pixi unless the user picks otherwise);
  (5) `audit-ml-pipeline` (or another agent-only consumer) needs the
      **agent feature** (jupytext + ipykernel + nbconvert) and it
      isn't yet present in the project's manifest — see § "Agent
      feature".

  SKIP when: the project is non-Python; the install/add command is
  for a non-Python tool (npm, brew, apt, cargo, gem); the dependency
  is already installed and importable; the work is purely editing
  existing source code with no new dependency in play.

  HOW TO USE: **detect first, then install**. Run the § "Detection"
  table at the project root before issuing any install command. If
  no manager is detected, ask the user before bootstrapping. Never
  install with a different manager than the one the project uses
  (e.g., never `pip install` into a pixi-managed project) — that
  creates env state divergence the manifest won't track. **Read
  the "Stop conditions" block and emit the Pre-flight checklist as
  visible text in your response — both are mandatory before issuing
  any command.**
---

# Python Env Manager

Detect the env manager, install with the right command. Single
authority for `data-science-python-stack` and the workflow skills
when they need a dependency added.

## Stop conditions — read before anything else

- **Wrong-manager install is forbidden.** If the project uses pixi,
  do not `pip install`. If it uses poetry, do not `uv add`. If it
  uses uv, do not `poetry add`. Mixing managers creates environment
  state the project's manifest doesn't track, and the next
  `pixi install` / `poetry install` / `uv sync` will silently undo
  the install. Detection (below) is mandatory before any command.
- **No silent bootstrap.** If detection finds no manager, do not
  pick one and start installing. Ask the user; the default
  *recommendation* is pixi, but the user must approve before
  `pixi init` runs.
- **Environment / feature / group choice is asked, not assumed.**
  Before issuing **any** install command, ask the user where the
  package belongs — the default feature/env, an existing
  feature/env, or a new one — **unless the user has already told
  you in this conversation** (e.g. "add it to the `tracing`
  feature", "put this in dev"). Silently dumping new deps into the
  default environment is a frequent source of bloat and confusion
  (e.g., adding ML packages to a project where `default` was kept
  minimal because heavy deps live in a specialized feature). This
  rule applies to **every** manager — pixi features, uv groups,
  poetry groups, hatch envs, conda envs, pip venvs. See § "Where
  does the package belong?" for the per-manager question.
- **Don't pin without reason.** Install commands here add packages
  unpinned by default (matching `data-science-python-stack` §
  "Conventions"). Pin only when the user asks or there's a known
  incompatibility.
- **Don't run the bootstrap installer yourself.** When pixi (or any
  manager) is missing, surface the install command and let the
  user run it. `curl | sh` is a system-level action that needs the
  user's hands on it, not Claude's.
- **Harness-level "no clarifying questions" instructions do not
  apply to this skill's `AskUserQuestion` mandates.** The manager
  pick (when nothing is detected or when ambient state is mixed)
  and the scope pick (where does the package belong) are
  operating-contract gates, not clarifying questions. They fire
  regardless of any harness-level hint that tells the agent to
  avoid asking. When the situation is borderline — e.g. one
  manager on PATH but conda envs visible alongside it — err on
  the side of asking. The blanket policy: an `AskUserQuestion`
  mandate in any skill is never waived by a harness "don't ask"
  hint; cross-reference `iterate-ml-experiment` Stop conditions
  for the same policy across the ML workflow.
- **Post-hoc audit — required before ending the turn.** Before
  declaring the turn complete, walk the pre-flight checklist
  and confirm every ticked box has its `Evidence:` line filled
  with a concrete citation (per § "Pre-flight evidence
  requirements" below). If any row is missing evidence,
  **surface the non-compliance to the user explicitly in your
  final message** rather than silently moving on. A successful
  install command is not proof the gates passed — the audit is.

## Gates — structured `AskUserQuestion` calls this skill owns

These are the two operating-contract gates this skill drives.
Both must pass via `AskUserQuestion` (or be answered out of
`JOURNAL.md` Status; see "Persistence lookup" below) before any
install / bootstrap command runs. They are gates, not Stop
conditions, because they have an explicit user-driven resolution
mechanism — but they share the Stop conditions' non-skippable
quality: no harness "don't ask" hint waives them.

### `G-ENV-MGR` — which manager and which scope

Fires when **either** of the following holds:

- Detection (§ "Detection") returns `(nothing detected)` and the
  project is fresh — the agent is about to bootstrap a manager.
- Detection returns a single manager but no recorded
  `Workspace decisions` row for `env manager` exists yet — the
  agent is about to issue its first install against this
  workspace.

The `AskUserQuestion` carries two coupled sub-picks:

1. **Manager.** Options come from the detection table (the
   single match, or the full list of supported managers when
   nothing was detected). The default *recommendation* when
   nothing is detected is `pixi`; surface it as the proposed
   default but require explicit confirmation.
2. **Scope.** Once the manager is picked, enumerate the
   existing environments / features / groups from the manifest
   and present them as options, plus "create a new
   feature/env/group `<name>`". The default-on-no-preference
   for the scope sub-pick is the manager's default env
   (`default` for pixi, the implicit env for uv/poetry, the
   `base`/active env for conda) — but it still requires the
   structured confirmation; never silent.

Free-text resolution applies. A user message resolves the
manager sub-pick only if it names one of the listed managers
("use pixi", "let's go with uv"); urgency phrasing ("just go",
"go fast", "you pick") does NOT resolve and falls through to
the structured ask. The same rule applies to the scope sub-pick:
"the dev feature" / "default env" resolves; "wherever" does not.

The answer is persisted in `journal/JOURNAL.md` Status
`Workspace decisions` (`env manager:` and `env scope:` rows)
so future sessions skip the re-ask.

### `G-ENV-SCOPE` — where each new install belongs

After `G-ENV-MGR` has resolved the project's default scope,
**every install command** still confirms the scope for *that
install*. The default `Workspace decisions` scope is the
fall-back when the user does not specify; it is not a license
to dump every new dep into the same place. Fire a lightweight
`AskUserQuestion` for non-trivial installs ("DL framework",
"serving stack", "notebook tier" — any tier-shift), with the
recorded default offered as the proposed answer.

Skip the structured ask only when the user has already told you
in the current conversation ("add it to the `tracing` feature",
"put this in dev"); record the source as
`user quote turn N: "..."` in the pre-flight evidence row.

### `G-AGENT-FEATURE` — install the agent feature

Fires when an agent-only consumer (currently `audit-ml-pipeline`,
future skills may join) needs `jupytext` + `ipykernel` +
`nbconvert` and the project's manifest doesn't yet expose them.
The full per-manager composition pattern (and the kernel-
registration step that's mandatory regardless of manager) lives
in § "Agent feature" below; this gate is the structured ask that
opens that section.

The `AskUserQuestion` carries three coupled sub-picks:

1. **Install scope.** Default proposal: a new
   feature/group/env/extra named `agent` (manager-appropriate
   keyword — see § "Agent feature" table), carrying the agent
   deps. User may pick "merge into the default scope" instead,
   or "into an existing feature/group/env" if the project's
   convention already has a suitable bucket (e.g. an existing
   `dev` group).
2. **Composed env name.** Default proposal: `dev`. Only relevant
   for managers that compose features into environments
   (pixi). For uv / poetry / hatch / conda / pip the agent deps
   land additively into the chosen scope and there is no
   separate "compose into env" step — surface `n/a` in the
   AskUserQuestion option description for those managers.
3. **Kernel name.** Default proposal: the project's package
   name from `pyproject.toml` `[project] name` (or
   `pixi.toml`'s `[project]` table). Used in `python -m
   ipykernel install --user --name <kernel>`. Must be unique
   across kernelspecs on the machine; if a kernel of that name
   already exists for another project, ask the user to pick a
   different name (e.g. `<project>-py3`).

Free-text resolution: "use a new agent feature named X, compose
into env Y, kernel name Z" resolves all three; partial
free-text falls through to the structured ask for the
unresolved sub-picks.

The answers persist in `journal/JOURNAL.md` Status under
`Workspace decisions` as three new rows: `agent scope:`,
`agent env:`, `agent kernel:`. Cross-session continuity follows
the same lookup contract as the other gates.

### Persistence lookup — read `JOURNAL.md` Status before any gate fires

Before issuing `G-ENV-MGR`, `G-ENV-SCOPE`, or `G-AGENT-FEATURE`,
read the `Workspace decisions` block in `journal/JOURNAL.md`
Status. If the matching row is already recorded (`env manager:
<pick> — recorded: <date>`, `env scope: <name> — recorded:
<date>`, `agent scope: <name> — recorded: <date>`, etc.),
**do not re-ask** — the gate is already resolved; cite
`JOURNAL.md Status (Workspace decisions, recorded YYYY-MM-DD)`
as the evidence for that row in the pre-flight.

If the workspace has no `journal/JOURNAL.md` yet (truly fresh
project before `organize-ml-workspace` has scaffolded), the
gates fire fresh and their answers will land in the
`Workspace decisions` block the moment `iterate-ml-experiment`
writes the JOURNAL from its template.

## Forbidden shortcuts (observed in real traces)

| Shortcut | Why it feels right | Why it's wrong |
|----------|--------------------|----------------|
| `pixi` is on PATH → assume pixi and run `pixi init` / `pixi add` | "Manager is obvious" | Detection on PATH is context, not a pick. G-ENV-MGR still fires when no `Workspace decisions` row exists for `env manager` |
| Detection returned exactly one manager (e.g. `pixi.toml` present) → skip G-ENV-MGR | The pick is already made | Detection skips re-asking *manager choice* because the manifest commits the project. But the *scope* sub-pick (G-ENV-SCOPE) and the per-install scope confirmation still apply on each new install |
| Default env is the only env → skip the scope question | "Where else would it go?" | The default-only state is itself a defaultable answer that requires structured confirmation. Silently dumping into default is the bloat path this gate exists to block |
| User said "quick baseline" / "just install the stack" → bundle all installs into one `pixi add` without asking scope | Task urgency, fewer round-trips | Urgency never waives G-ENV-MGR or G-ENV-SCOPE. Bundle the install commands once both gates have passed, not before |
| `python-env-manager` was opened earlier this conversation → assume gates passed | Continuity from prior turn | Reading the SKILL.md is not the same as the gate firing. The `AskUserQuestion` (or the `JOURNAL.md` Status lookup) is the gate pass |

## Pre-flight — emit this checklist as visible text before any command

Before running an install / add / remove / upgrade command, output
this block verbatim. **Each ticked box requires an `Evidence:`
line** — a ticked box without evidence is a Stop-condition
violation, indistinguishable from a skipped check.

### Pre-flight evidence requirements

- **Detection rows.** Evidence is the tool output that triggered
  the detection-table match: `Evidence: ls project_root | tool
  output (this turn) → matched signal "<signal>"` (e.g.
  `pixi.toml present → pixi`).
- **Gate rows (G-ENV-MGR, G-ENV-SCOPE, G-AGENT-FEATURE).** Evidence is one of:
  - `Evidence: AskUserQuestion id=<id>, answer=<option>` — the
    user picked via the structured tool this turn.
  - `Evidence: user quote turn N: "..."` — free-text from the
    user named one of the listed options.
  - `Evidence: JOURNAL.md Status (Workspace decisions, recorded
    YYYY-MM-DD)` — the decision was made in a prior session.
- **Workflow rows.** Evidence is the artifact produced or the
  command that ran: `Evidence: Shell pixi add <pkgs> →
  exit_code=0`.

### The checklist

```
Pre-flight (python-env-manager):
- [ ] Sibling SKILL.md files opened **this turn**:
      data-science-python-stack (for the install context),
      iterate-ml-experiment (for the JOURNAL.md persistence
      contract), organize-ml-workspace (for the editable install
      handoff).
      Evidence: Read .agents/skills/<each>/SKILL.md (this turn)
- [ ] `journal/JOURNAL.md` Status `Workspace decisions` block read
      this turn for pre-recorded `env manager` and `env scope` rows.
      Evidence: lists each row's value or "not recorded yet" |
                "n/a — JOURNAL.md does not exist yet"
- [ ] Detection done; manager identified: <pixi | uv | poetry | hatch
      | conda | pip+venv | none>
      Evidence: tool output of `ls` / Glob on project root +
                matched signal from § "Detection"
- [ ] G-ENV-MGR resolved: <pixi | uv | poetry | hatch | conda | pip+venv>
      Evidence: AskUserQuestion id=<id>, answer=<manager> |
                JOURNAL.md Status (Workspace decisions, recorded YYYY-MM-DD) |
                "detection returned a single manager; manifest commits the project — no AskUserQuestion needed"
- [ ] Existing environments / features / groups enumerated from the
      manifest (so the user has a real list to pick from)
      Evidence: tool output of the manager's list command (e.g.
                Read pixi.toml + grep for [feature.*])
- [ ] G-ENV-SCOPE resolved: default | <existing feature/env/group> | <new feature/env/group>
      Evidence: AskUserQuestion id=<id>, answer=<scope> |
                user quote turn N: "..." |
                JOURNAL.md Status (Workspace decisions, recorded YYYY-MM-DD)
- [ ] (Agent-feature installs only) G-AGENT-FEATURE resolved:
      agent scope=<name> | agent env=<name | n/a> | agent kernel=<name>
      Evidence: AskUserQuestion id=<id>, three-part answer |
                JOURNAL.md Status (Workspace decisions, recorded YYYY-MM-DD) |
                "n/a — not an agent-feature install"
- [ ] Install command syntax confirmed for that manager (see § "Install
      commands" or § "Agent feature" for jupytext/ipykernel/nbconvert)
      Evidence: cite the matching subsection
- [ ] Package list ready: <pkg-1, pkg-2, ...>
      Evidence: explicit list in this turn's response
- [ ] (Agent-feature installs only) Kernel registration step queued:
      `<activation> python -m ipykernel install --user --name <kernel>`
      Evidence: command quoted in this turn's response |
                "n/a — not an agent-feature install"
- [ ] (Agent-feature installs only) Verification commands queued
      (`jupytext --version`, `jupyter nbconvert --version`,
      `jupyter kernelspec list | grep <kernel>`)
      Evidence: commands quoted in this turn's response |
                "n/a — not an agent-feature install"
```

## Detection — figure out the manager first

Run these checks at the project root in order. **The first signal
that matches wins.** If multiple signals are present (a real
possibility — e.g. `pyproject.toml` + `pixi.toml`), surface the
ambiguity to the user before installing.

| Signal at project root | Manager | Notes |
|---|---|---|
| `pixi.toml` or `pixi.lock` | **pixi** | Default for this stack. Likely multi-feature. |
| `uv.lock`, or `pyproject.toml` with `[tool.uv]` | **uv** | Fast Rust-based manager. |
| `poetry.lock`, or `pyproject.toml` with `[tool.poetry]` | **poetry** | Common in older Python projects. |
| `hatch.toml`, or `pyproject.toml` with `[tool.hatch]` | **hatch** | Declarative; install flow varies — ask the user. |
| `environment.yml` (and `conda` / `mamba` on PATH) | **conda / mamba** | Heavy but common in scientific stacks. |
| `requirements.txt` + `.venv/` or `venv/` | **pip + venv** | Plain Python; least integrated. |
| None of the above | **(nothing detected)** | Ask the user. Default *suggestion*: pixi. |

Notes:
- A `pyproject.toml` with **only** `[build-system]` / `[project]` and
  no `[tool.X]` table for any manager is ambiguous. Don't infer a
  manager from `pyproject.toml` alone — ask.
- `hatch` is declarative: dependencies live in `[project]
  dependencies` or `[tool.hatch.envs.<env>.dependencies]` in
  `pyproject.toml`, and `hatch` re-syncs on next `hatch run`. If
  detected, ask the user how they prefer to add deps (edit
  `pyproject.toml` vs. another flow) — there's no universal `hatch
  add` command.
- If both `pixi.toml` and a `pyproject.toml` with another manager's
  `[tool.X]` are present, the project may be transitioning. Ask
  before picking.

### Ambient managers — check before recommending a fresh bootstrap

When § "Detection" finds **no project-root signals**, do not silently
default to "pixi is the recommendation". A bare project root often sits
on top of a developer machine that already has one or more managers
installed and existing envs the user might want to reuse. Before
firing any `pixi init` (or equivalent), probe the *ambient* state:

```bash
command -v pixi uv poetry hatch conda mamba
conda env list 2>/dev/null  # if conda/mamba is on PATH
```

If **two or more** managers are on PATH, **or** there are existing
conda envs that already carry parts of the stack (sklearn / skrub /
skore), surface the situation to the user via `AskUserQuestion`. Offer
at least these branches:

- **Bootstrap a fresh pixi project** (the default *recommendation*
  when nothing has to be reused).
- **Reuse an existing env**: if `conda env list` shows an env with
  the stack already installed (or close to it), reusing avoids a
  duplicate install. Name the envs in the option description so the
  user can see what's on offer.
- **Bootstrap a different manager** (uv / poetry / hatch / conda):
  pick this when the user's team standard differs from pixi.

The contract: "no project-root signals" does not mean "no relevant
state." Defaulting to pixi when an existing conda env could have
served is a frequent ergonomic miss; the `AskUserQuestion` exists
to surface that choice rather than presume it.

## Where does the package belong? — ask before installing

Every manager in this skill supports **scoped** dependencies — pixi
features, uv groups, poetry groups, hatch envs, conda envs, pip
venvs. Picking the wrong scope is a real cost: ML deps dropped into
a `default` feature that the project deliberately kept slim, dev
tools polluting the runtime env, a heavy library installed into the
wrong conda env. **The user owns this decision.**

**Default rule:** before any install command, enumerate the
existing scopes from the manifest and ask the user where the
package(s) belong. Offer three branches: an existing scope, a new
scope (and ask for a name), or the default. **Skip the question
only when the user has already specified a scope in this
conversation** (e.g. "add it to the `tracing` feature", "put this
under dev"). When skipping, record the source in the Pre-flight
checklist ("user said in turn N: ...").

The exact question to ask, per manager:

| Manager | Existing scopes to enumerate | Question template |
|---|---|---|
| **pixi** | features in `pixi.toml` `[feature.X]` and environments in `[environments]` | "I see features `<list>`. Should `<pkg>` go into the default feature, an existing one (`<list>`), or a new feature (and what should it be named)?" |
| **uv** | groups in `[dependency-groups]` / `[tool.uv]` | "Should `<pkg>` be a runtime dep, a dev dep (`--dev`), or live in an optional group (existing: `<list>`, or a new one)?" |
| **poetry** | groups in `[tool.poetry.group.X]` | "Should `<pkg>` be a runtime dep, in `--group dev`, or in another group (existing: `<list>`, or a new one)?" |
| **hatch** | envs in `[tool.hatch.envs.X]` | "Should `<pkg>` go into the project's `[project] dependencies`, or into a hatch env (existing: `<list>`, or a new one)?" |
| **conda / mamba** | envs from `conda env list` (or those declared in `environment.yml`) | "Which conda env should `<pkg>` go into — the active one (`<name>`), another existing env (`<list>`), or a new env (and what should it be named)?" |
| **pip + venv** | venvs visible at the project root (`.venv/`, `venv/`, etc.) | "Should `<pkg>` go into the existing venv (`<path>`), or into a new venv (and where)?" |

If the manifest lists no scopes (a fresh `pixi.toml` with only
`[dependencies]`, a `pyproject.toml` with no groups), you can offer
"default" + "create a new <feature/group/env>" and skip
enumeration.

**Why this matters.** The manifest is the project's contract. Every
new dep nudges the contract; doing it without the user makes the
contract drift in ways the user has to discover later. Asking is
cheap; reverting is not (especially with `pixi remove --feature`,
`poetry remove --group`, or undoing a conda env mutation).

## Install commands — by manager

Once detected, use *only* the matching commands. Do not mix.

### pixi

Default for this stack. Pixi organizes deps per **feature**
(e.g. `default`, `dev`, `tracing`). **Before running any
`pixi add`, ask the user which feature the package belongs in** —
see § "Where does the package belong?" for the question template.
Enumerate the existing features from `pixi.toml` first so the user
has a concrete list.

| Action | Command |
|---|---|
| Add to default feature | `pixi add <pkg>` |
| Add to a specific feature | `pixi add --feature <feature> <pkg>` |
| Add to a specific environment | `pixi add -e <env> <pkg>` |
| Remove | `pixi remove <pkg>` (or `--feature <feature>`) |
| Upgrade | `pixi upgrade <pkg>` |
| Run inside an env | `pixi run -e <env> <command>` |
| Sync env from manifest | `pixi install` |

A real-world example: in some projects `mlflow` lives in a
`tracing` feature, not `default` — silently dropping it into
`default` would have been wrong. Always ask.

### uv

**Before running any `uv add`, ask the user whether the package is
a runtime dep, a dev dep (`--dev`), or belongs to an optional
group** — see § "Where does the package belong?". Enumerate
existing groups from `pyproject.toml` (`[dependency-groups]` or
`[project.optional-dependencies]`) so the user has a real list.

| Action | Command |
|---|---|
| Add a runtime dep | `uv add <pkg>` |
| Add a dev dep | `uv add --dev <pkg>` |
| Add to an optional group | `uv add --optional <group> <pkg>` |
| Remove | `uv remove <pkg>` |
| Upgrade a single pkg | `uv lock --upgrade-package <pkg>` |
| Run inside the env | `uv run <command>` |
| Sync env from manifest | `uv sync` |

### poetry

**Before running any `poetry add`, ask the user whether the package
is a runtime dep, in `--group dev`, or in another group** — see §
"Where does the package belong?". Enumerate existing groups from
`pyproject.toml` (`[tool.poetry.group.X]`) so the user has a real
list.

| Action | Command |
|---|---|
| Add a runtime dep | `poetry add <pkg>` |
| Add a dev dep | `poetry add --group dev <pkg>` |
| Add to a named group | `poetry add --group <name> <pkg>` |
| Remove | `poetry remove <pkg>` |
| Upgrade | `poetry update <pkg>` |
| Run inside the env | `poetry run <command>` |
| Sync env from manifest | `poetry install` |

### hatch

Hatch is declarative. There is no universal `hatch add`. **Before
editing `pyproject.toml`, ask the user whether the package should
go into project-level deps or an env-specific section** — see §
"Where does the package belong?". Enumerate existing envs from
`[tool.hatch.envs.X]` so the user has a real list.

Standard flow:

1. Edit `pyproject.toml`:
   - Project-level dep → add to `[project] dependencies`.
   - Env-specific dep → add to
     `[tool.hatch.envs.<env>.dependencies]`.
2. Re-sync the env: `hatch env prune` (optional, removes stale
   envs), then any `hatch run -e <env> <command>` re-creates it.

### conda / mamba

`mamba` is a faster drop-in replacement for `conda`. Prefer it if
both are on PATH.

**Before running any `conda install` / `mamba install`, ask the
user which env the package belongs in** — see § "Where does the
package belong?". Enumerate envs with `conda env list` (or read
the `name:` field from `environment.yml`) so the user has a real
list. Defaulting to the active env without asking can pollute a
shared base environment.

| Action | Command |
|---|---|
| Add a dep (conda-forge channel) | `conda install -n <env> -c conda-forge <pkg>` |
| Same with mamba | `mamba install -n <env> -c conda-forge <pkg>` |
| Remove | `conda remove -n <env> <pkg>` |
| Sync from `environment.yml` | `conda env update -f environment.yml --prune` |

If `environment.yml` is the source of truth for the project, edit
it and run the `env update` rather than installing one-off; this
keeps the manifest in sync.

### pip + venv

The least-integrated path. There is no manifest update — `pip
install` mutates the live env without tracking.

**Before running any `pip install`, ask the user whether the
package goes into the existing venv or a new one** — see § "Where
does the package belong?". List visible venvs at the project root
(`.venv/`, `venv/`, etc.) so the user can pick. Don't activate and
install silently — even with pip, the choice of which venv to
mutate is the user's.

Steps:

1. Activate the venv: `source .venv/bin/activate` (Linux/macOS) or
   `.venv\Scripts\activate` (Windows).
2. Install: `pip install <pkg>`.
3. If `requirements.txt` is the project's manifest, regenerate or
   edit it — `pip freeze > requirements.txt` is one option, but
   it captures all transitive pins; for a tighter diff, edit the
   file by hand to add the new top-level dep.

Surface to the user that `pip install` alone leaves no audit trail.
If the project is fresh, offer migration to a managed alternative
(pixi by default).

## Editable workspace package — wire `src/<pkg>/` per manager

When the project ships a local Python package under `src/<pkg>/`
(declared by a `pyproject.toml` at the project root), it must be
installed in **editable** mode so that `from <pkg>.X import Y` works
from any CWD without `PYTHONPATH=src` hacks **and** so that edits to
the source tree are picked up immediately. `organize-ml-workspace`
hands off to this section after dropping `pyproject.toml`.

The wiring differs per manager. Use the matching command — never
fall back to `pip install -e .` inside a managed env (that produces
the same out-of-manifest drift as any other wrong-manager install).

| Manager | Wiring | Notes |
|---|---|---|
| **pixi** | `pixi add --pypi --editable .` | Adds to `[pypi-dependencies]`. Pass `--feature <name>` to scope (e.g. the same feature where Tier 1 lives). On next `pixi install`, the package is editable in every env that includes that feature. |
| **uv** | nothing extra — `uv sync` installs the `[project]` package editable by default | If the workspace has multiple packages, add `[tool.uv.sources]` entries; for the single-package case the default `uv sync` behavior is enough. |
| **poetry** | nothing extra — `poetry install` is editable by default | Make sure `pyproject.toml` carries `[tool.poetry] packages = [{include = "<pkg>", from = "src"}]` (or that the build backend's package discovery picks up `src/<pkg>/`). |
| **hatch** | nothing extra — `hatch run` envs install editable by default | Make sure `[tool.hatch.build.targets.wheel] packages = ["src/<pkg>"]` is declared in `pyproject.toml`. |
| **conda / mamba** | after the env is in place: `pip install -e .` (run inside the conda env) | conda has no native concept of editable installs from a local `pyproject.toml`; pip is the right tool. The `pip install -e .` here is **inside a conda-managed env** — that's the supported hybrid, not a wrong-manager install. |
| **pip + venv** | activate the venv, then `pip install -e .` | The standalone case. There is no manifest entry — surface this and offer migration to a managed alternative. |

Detection cleanup: if you find a stale `<pkg>.egg-info/` at the
project root or under `src/` (typically a relic of an out-of-band
`pip install -e .`) **and** the manager's manifest does not carry
the editable entry, that is drift. Clean up the egg-info **after**
wiring the install correctly through the manager — never before
(the cleanup can break a working but unmanaged setup).

## Agent feature — install jupytext + ipykernel + nbconvert

The **agent feature** is a project-scoped install of the
notebook-execution toolchain (`jupytext`, `ipykernel`,
`nbconvert`) plus a one-time kernel registration. It is what
makes `audit-ml-pipeline`'s two-step execution path work
(jupytext converts `audit/<stem>.py` → `.ipynb`; nbconvert
executes the notebook with a named kernel; nbconvert renders
the executed notebook to markdown).

The deps themselves live in `data-science-python-stack` (under
the "agent feature" category — separate from Tier 1 mandatory,
because not every workspace uses the audit flow). This section
owns *where they get installed* and *how the kernel is
registered*, per the project's env manager.

### Composition model — pixi composes; others layer

The agent feature is conceptually "deps that the agent runs but
the production-shape runtime doesn't need". Two manager
classes:

- **Composable** (pixi only). The agent deps land in a
  dedicated `[feature.agent]` block; a composed environment
  `[environments.dev] = ["default", "agent"]` lets the agent
  invoke `pixi run -e dev ...` to get both the data-science
  deps *and* the agent deps in scope, while `pixi run ...`
  (defaulting to the `default` env) stays lean.
- **Additive** (uv / poetry / hatch / conda / pip+venv). The
  agent deps land in a separate group / env / extra, and the
  agent invokes them via a group-targeted command (e.g.
  `uv run --group agent ...`, `poetry run ...` with the group
  installed). No environment composition step.

### Per-manager invocations

Overview table — the kernel-registration step is **constant across
managers** (`python -m ipykernel install --user --name <kernel>`,
run inside the agent-scoped env). Only the install command and the
agent's invocation prefix change.

| Manager | Install command | Agent invocation prefix |
|---|---|---|
| **pixi** | `pixi add --feature agent jupytext ipykernel nbconvert` + compose `[environments.dev] = ["default", "agent"]` | `pixi run -e dev <cmd>` |
| **uv** | `uv add --group agent jupytext ipykernel nbconvert` | `uv run --group agent <cmd>` |
| **poetry** | `poetry add --group agent jupytext ipykernel nbconvert` | `poetry run <cmd>` (group is added to the single env on install) |
| **hatch** | Edit `pyproject.toml` `[tool.hatch.envs.agent]` then run via the env | `hatch run agent:<cmd>` |
| **conda / mamba** | `conda install -n <env> -c conda-forge jupytext ipykernel nbconvert` (or `mamba`) | `conda run -n <env> <cmd>` |
| **pip + venv** | Activate venv, then `pip install jupytext ipykernel nbconvert` | (with venv active) `<cmd>` directly |

**Manager-specific footguns** (caught here so the per-manager
subsections don't have to repeat them):

- **pixi:** running `pixi run <cmd>` without `-e dev` uses the
  `default` env and misses the agent feature → the audit-execute
  command fails with "command not found: jupytext". The `-e dev`
  flag is load-bearing.
- **uv:** running `uv run <cmd>` without `--group agent` works at
  first (the group is installed) but only resolves the agent deps
  if `uv.lock` includes them. Confirm `uv sync --group agent` ran
  before the first audit execution.
- **hatch:** the `agent` env is fully isolated from `default` →
  the data-science Tier 1 deps must also be added to the agent env
  manifest, or the audit cells will fail at `import skore`. This
  duplication is the price of hatch's isolation model; flag it to
  the user before recommending hatch for new agent-feature
  workspaces.
- **conda / mamba:** registering the kernel with `--name <kernel>`
  from a conda env writes the kernelspec into the *user's* Jupyter
  registry (not the env). If the user has multiple conda envs that
  all want the agent feature, give each kernel a project-scoped
  name (e.g. `<project>-py3`) to avoid collisions.
- **pip + venv:** `jupyter kernelspec` and `jupytext` resolve
  against the **active** venv; if the user opens a new shell
  without activating, the commands "look like" they work (system
  jupyter, if any, takes over) but execute with the wrong
  interpreter. Always activate explicitly in the agent's command.

#### pixi

```bash
# Install the agent feature
pixi add --feature agent jupytext ipykernel nbconvert

# Compose the dev env (one-time, via `pixi.toml` edit or this CLI form)
# [environments]
# default = ["default"]
# dev = ["default", "agent"]
pixi project environment add dev --feature default --feature agent

# Register the project's kernel (run inside the dev env)
pixi run -e dev python -m ipykernel install --user --name <kernel>

# Agent invokes jupytext / nbconvert via:
pixi run -e dev jupytext --to ipynb <src> -o <out>
pixi run -e dev jupyter nbconvert --execute --to notebook \
  --ExecutePreprocessor.kernel_name=<kernel> ...
```

#### uv

```bash
# Install the agent feature into a dependency group
uv add --group agent jupytext ipykernel nbconvert

# Register the project's kernel (run inside uv's env)
uv run --group agent python -m ipykernel install --user --name <kernel>

# Agent invokes jupytext / nbconvert via:
uv run --group agent jupytext --to ipynb <src> -o <out>
uv run --group agent jupyter nbconvert --execute --to notebook \
  --ExecutePreprocessor.kernel_name=<kernel> ...
```

#### poetry

```bash
# Install the agent feature into a named group
poetry add --group agent jupytext ipykernel nbconvert

# Register the project's kernel
poetry run python -m ipykernel install --user --name <kernel>

# Agent invokes jupytext / nbconvert via:
poetry run jupytext --to ipynb <src> -o <out>
poetry run jupyter nbconvert --execute --to notebook \
  --ExecutePreprocessor.kernel_name=<kernel> ...
```

Poetry's group-install puts deps in the single project env;
there is no per-invocation group selection.

#### hatch

Edit `pyproject.toml`:

```toml
[tool.hatch.envs.agent]
dependencies = ["jupytext", "ipykernel", "nbconvert"]
```

```bash
# Hatch creates the env on first `hatch run agent:<cmd>`. Register
# the kernel from inside the agent env:
hatch run agent:python -m ipykernel install --user --name <kernel>

# Agent invokes jupytext / nbconvert via:
hatch run agent:jupytext --to ipynb <src> -o <out>
hatch run agent:jupyter nbconvert --execute --to notebook \
  --ExecutePreprocessor.kernel_name=<kernel> ...
```

Hatch envs are isolated (no composition with `default`), so the
hatch path duplicates the data-science deps in the `agent` env
when they're needed alongside. If that duplication is a problem,
recommend the user switch to pixi or uv for new projects.

#### conda / mamba

```bash
# Add to the active env (most common) or a named env
conda install -n <env> -c conda-forge jupytext ipykernel nbconvert
# or with mamba (faster):
mamba install -n <env> -c conda-forge jupytext ipykernel nbconvert

# Register the project's kernel from inside the env
conda run -n <env> python -m ipykernel install --user --name <kernel>

# Agent invokes jupytext / nbconvert via:
conda run -n <env> jupytext --to ipynb <src> -o <out>
conda run -n <env> jupyter nbconvert --execute --to notebook \
  --ExecutePreprocessor.kernel_name=<kernel> ...
```

If the project pins deps in `environment.yml`, also add the
three agent deps to the file so the env is reproducible.

#### pip + venv

```bash
# Activate the venv first
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install the agent feature
pip install jupytext ipykernel nbconvert

# Register the project's kernel
python -m ipykernel install --user --name <kernel>

# Agent invokes jupytext / nbconvert via (with the venv active):
jupytext --to ipynb <src> -o <out>
jupyter nbconvert --execute --to notebook \
  --ExecutePreprocessor.kernel_name=<kernel> ...
```

There is no manifest entry; if `requirements.txt` is the
project's source of truth, regenerate or hand-edit it to
include the three agent deps.

### Kernel registration — mandatory regardless of manager

After the agent deps are installed, the project must register an
IPython kernel for nbconvert's `--ExecutePreprocessor.kernel_name`
to resolve against. The command is the same across managers
(only the activation wrapper differs):

```bash
python -m ipykernel install --user --name <kernel>
```

Two requirements on `<kernel>`:

- **Unique across the user's kernelspecs.** Run `jupyter
  kernelspec list` first; if a kernel with that name already
  exists for another project, pick a different name
  (e.g. `<project>-py3`).
- **Stable across sessions.** The audit skill's execution
  command embeds the kernel name; renaming forces every audit
  file to be re-edited. Pick a name and stick with it. Record
  it in `JOURNAL.md` Status `Workspace decisions` as
  `agent kernel:`.

### Cleanup — when an agent feature is removed

If the user wants to remove the agent feature (e.g. dropping the
audit flow):

```bash
# Remove the deps (manager-specific; example for pixi)
pixi remove --feature agent jupytext ipykernel nbconvert

# Remove the kernel registration
jupyter kernelspec remove <kernel> -y
```

Update `JOURNAL.md` Status to remove the `agent scope:`,
`agent env:`, `agent kernel:` rows. Note in the History or
Status block that the audit flow was disabled.

### Verification — what should be true after install

Before handing back to the calling skill (e.g.
`audit-ml-pipeline`), confirm:

```bash
# jupytext is callable in the agent-scoped env
<activation> jupytext --version

# nbconvert is callable
<activation> jupyter nbconvert --version

# The project's kernel is registered
jupyter kernelspec list | grep <kernel>
```

All three must succeed before declaring `G-AGENT-FEATURE`
resolved. If any fails, surface the failure to the user
verbatim — do not paper over with a partial install.

## Tier 1 install: skore variant per mode

When installing `skore` for a workspace, the install variant
depends on the `skore mode:` decision recorded in
`journal/JOURNAL.md` Status `Workspace decisions` (set by
`organize-ml-workspace` § "G-SKORE-MODE"). Two variants:

| `skore mode:` | Install command (per manager) |
|---|---|
| `local` | Plain `skore` package — `pixi add skore`, `uv add skore`, `poetry add skore`, etc. |
| `hub` | The `skore[hub]` extra — `pixi add "skore[hub]"`, `uv add "skore[hub]"`, `poetry add "skore[hub]"`, etc. Pulls hub-client deps (HTTPX, auth helpers). The `[hub]` extra is **additive over `skore`** — installing it gives you both local and hub functionality, but the extra deps are unused on a local-mode workspace, hence the split. |

**Why the variant matters.** Hub mode calls `skore.login(mode="hub")`
before instantiating `skore.Project(...)`. That `login` flow is
implemented in the `[hub]` extra; on a plain `skore` install,
`from skore import login` raises `ImportError`. Installing the
wrong variant silently produces working CI for local-mode
operations but breaks hub-mode operations at first `login()`.

**Reading the recorded decision.** Before issuing the skore install
command, read `journal/JOURNAL.md` Status `Workspace decisions` for
the `skore mode:` row. If the row is absent (workspace not yet
bootstrapped through `organize-ml-workspace`), route back to
`organize-ml-workspace` § "G-SKORE-MODE" — do not guess. The
default proposal at G-SKORE-MODE is `local`, but **the decision is
the user's**, not the install layer's.

**Forbidden:** silently picking `skore[hub]` "to be safe" or
"because the user might want hub later". The `[hub]` extra costs
~20 MB of network deps + authentication infrastructure the
local-mode user did not ask for; the gate-based split exists to
avoid that.

**Switching modes.** If the user pivots `skore mode:` mid-project
(per `organize-ml-workspace` § "Switching skore mode mid-project
is forbidden by default" — requires explicit user confirmation):

- `local` → `hub`: run the manager's `add` command for
  `"skore[hub]"` over the existing install. The extra deps land
  additively; existing local-mode reports under `reports/` stay
  on disk but are no longer the active store.
- `hub` → `local`: optionally remove the hub extra to slim the
  env (`pixi remove skore` then `pixi add skore`, or the
  equivalent). Existing hub-mode reports stay on Skore Hub but
  are no longer the active store from this workspace.

In both directions, surface to the user that the prior store's
reports are orphaned from this workspace's perspective until a
manual migration.

## Bootstrap — when no manager is detected

If detection found nothing **and the user agrees to use pixi**:

1. Check whether pixi is on PATH: `command -v pixi`.
2. If pixi is not installed, surface the install command and **ask
   the user to run it** (do not run `curl | sh` yourself):
   - Linux/macOS: `curl -fsSL https://pixi.sh/install.sh | sh`
   - Windows: `iwr -useb https://pixi.sh/install.ps1 | iex`
3. Once pixi is available, initialize: `pixi init` (creates
   `pixi.toml` in the current directory).
4. **Ask the user how to organize features** before adding any
   deps: a single `default` feature for everything, or split (e.g.
   `default` for runtime + `dev` for dev tools, or `core` +
   `tracing` if mlflow / observability is in scope). The skill's §
   "Where does the package belong?" rule applies even at bootstrap
   — defaulting to a single feature without asking sets a layout
   the user has to migrate later.
5. Add the relevant Tier 1 deps for an ML project (per
   `data-science-python-stack` § "Tier 1") into the chosen
   feature. The skore install variant follows G-SKORE-MODE (see §
   "Tier 1 install: skore variant per mode" above):
   - `skore mode: local` →
     `pixi add [--feature <name>] scikit-learn skrub skore ruff pytest`
   - `skore mode: hub` →
     `pixi add [--feature <name>] scikit-learn skrub "skore[hub]" ruff pytest`

   If G-SKORE-MODE hasn't fired yet at bootstrap time (rare —
   `organize-ml-workspace` fires it alongside G-PKG-NAME and
   G-TABULAR), route back to that skill before issuing the install
   command. Ruff and pytest are mandatory; both go into the same
   feature as the rest of the Tier 1 stack so a single `pixi run`
   activation has everything Claude needs.
6. Ask the user about the tabular-library choice (per
   `organize-ml-workspace` § "Stop conditions" — pandas vs polars)
   and which feature it belongs in. Add accordingly:
   `pixi add [--feature <name>] pandas pyarrow` or
   `pixi add [--feature <name>] polars`.

If the user wants a different manager (uv / poetry / hatch / conda),
mirror the same flow with that manager's init command (`uv init`,
`poetry init`, `conda env create -f environment.yml`, etc.) — and
apply § "Where does the package belong?" at every install step.

## Cross-references

This skill is the install layer for the rest of the stack. Invoke it
whenever those skills surface a missing dependency or a new install:

- **`data-science-python-stack`** — owns *what* to install (Tier 1
  mandatory, Tier 2 user choice, Tier 3 optional). When that skill
  decides a package is needed, this skill turns the decision into
  the right shell command.
- **`organize-ml-workspace`** — its Stop condition "Tabular library
  is asked, not assumed" produces a pandas-vs-polars decision; this
  skill executes the install. It also hands off to § "Editable
  workspace package" once `pyproject.toml` is on disk so the local
  `src/<pkg>/` package gets installed editable through the project's
  manager (no `PYTHONPATH=src` workaround, no out-of-band
  `pip install -e .`).
- **`build-ml-pipeline`** / **`evaluate-ml-pipeline`** — their Stop
  conditions on missing `skrub` / `skore` redirect here for the
  install command. Their Pre-flight checklists include "Tier 1
  importable"; if a box fails, this skill is the next step. When
  installing skore, the variant (`skore` vs `skore[hub]`) follows
  the workspace's recorded `skore mode:` decision (see § "Tier 1
  install: skore variant per mode" below).
- **`audit-ml-pipeline`** — when the audit skill fires and the
  agent feature isn't installed, it routes here for the install
  + kernel registration. The `G-AGENT-FEATURE` gate (above) is
  the structured ask that opens § "Agent feature".

## Conventions

- **One install operation per response.** Don't batch unrelated
  packages into one command. Group related packages (Tier 1
  bootstrap, or a single feature's deps) and confirm before
  continuing.
- **No `--no-deps` or version pins by default.** Match
  `data-science-python-stack` § "Conventions". Pin only on user
  request or known incompatibility.
- **Surface, don't bypass.** If an install fails (network, version
  conflict, missing channel), surface the error and the command —
  don't try alternative managers as a workaround. Wrong-manager
  workarounds are a Stop-condition violation.
