---
name: add-python-package
description: >
  Add a Python dependency through the project env manager, or ask
  the user to install it when env.managed is false. Trigger when a
  workflow needs a missing import, after choose-python-library
  picks a library, or for editable install of src/<pkg>/.

  SKIP choosing between competing libraries (choose-python-library
  owns that). SKIP bootstrapping a missing manager directly
  (setup-python-env). When env.managed is null, load
  setup-ml-project if it is installed.

  HOW TO USE: read status.policy.env.managed, env detect, and
  env route. Classify this turn first (editable | add-skore |
  named package). If managed is null, load setup-ml-project and
  stop. If managed, env add --execute (or --editable).
  If unmanaged, ask; default is the user handles it — do not wait.
  When setup-ml-project already chose user-managed this turn,
  name the package and the manager, then return. Do not ask and
  do not wait.
  Never --execute while managed is false.
metadata:
  role: helper
  modelTier: small
---

# Add Python Package

The only skill that knows `python -m skore_skills env add`. Callers
must not splice manager commands themselves.

## Human-facing prose

Details: `setup-workspace` `references/human_facing_prose.md`.
Run `python -m skore_skills …` yourself. In questions and replies,
show the manager command from print-only stdout (`pixi add …`,
`uv add …`, `pip install …`) or a plain-language intent. Never
paste `python -m skore_skills`, `env add`, `env add-skore`, or
`--feature` / `--group` as something the user should run or choose.
Never paste `env graphviz` either; quote that command's
`instructions` or printed manager line.

## Pre-flight

Tick, then immediately run the matching sequence step. Do not stop
after listing the boxes.

```
- [ ] status + env detect
- [ ] env.managed: null and setup-ml-project installed → load it and stop | null → say unresolved and stop | false and setup already chose unmanaged → name package and manager, return | false → ask, no --execute | true → continue
- [ ] classify: editable | add-skore | env route then env add
- [ ] skrub → env graphviz (install conda Graphviz and verify SVG when allowed)
```

## Sequence

1. `python -m skore_skills status` and `env detect`.
2. If `policy.env.managed` is null: env is unresolved. If
   `status.skills.setup-ml-project` is true, load
   `setup-ml-project` and stop. Do not ask whether to set up an
   environment. Do not load `setup-python-env`. If that skill is
   not installed, say the environment is unresolved and stop.
   Do not bootstrap here.
3. Classify this turn **before** adding anything:

   - **Editable** only if the user asked to install the workspace
     package, or `setup-ml-project` selected that box. `has_src`
     true is not enough.
   - **Skore** if the package is Skore.
   - **Named package** otherwise (`skrub`, pandas, …). Never
     `--editable` for a named dependency.

4. If `managed` is false and `setup-ml-project` dispatched this
   turn: the opening question already chose user-managed. Name
   the package and the manager in words, then return. Do not run
   `env add` — print-only refuses while managed is false. Do not
   invent `pixi add` / `uv add` / `pip install`. Do not ask. Do
   not wait. Do not say the turn continues after the user
   confirms. Stop this sequence. Do not continue at step 5 or
   step 6.
5. If `managed` is false on a standalone turn: **do not**
   `--execute`. Run print-only `env add` (or `env add --editable`,
   or `env add-skore --mode <mode>`) to obtain the manager line.
   Every ask in this skill carries its context inline: name the
   package(s), the manager and env the command would touch, and
   what each option does.
   Do not name the calling skill. A file link is an addition,
   never the context. Ask with two options:

   1. **I will handle it** (default) — name the package(s) and
      **show that stdout** (e.g. `pixi add pandas`). Do not wait;
      return.
   2. **Please install this now** — show the same manager line,
      wait until the user confirms it is done, then return.

   Show **exactly one** manager command. Do not list agent extras,
   optional extras, `ask`, or refuse unless `env route` JSON
   **this turn** returned that `scope`. If print-only did not run,
   name the package and the manager in words. Do not invent a
   wrapper command.

6. If this turn is editable and `has_src` is true:

   ```bash
   python -m skore_skills env add --editable --execute
   ```

   Never `pip install -e .` in a pixi project. If `has_src` is
   false, stop. Name `setup-workspace` only if it is installed.
   A non-zero exit is not a successful install. Do not describe
   it as done.
7. If the package is Skore, read the persisted `policy.skore_mode`
   and run:

   ```bash
   python -m skore_skills env add-skore --mode <mode> --execute
   ```

   If the mode is unset, return to `evaluate-ml-pipeline`. Do not
   spell `skore[...]` or pick conda vs PyPI yourself. See
   `add-python-package/references/skore_variant.md`.
8. Else `python -m skore_skills env route <pkg>`. Use **only** the
   `scope` returned **this turn**. Do not list other branches. Do
   not guess `default`.

   - No JSON this turn → name `env route <pkg>` and stop. Do not
     `env add --execute`.
   - `refuse` → stop. Quote `message`. Do not install.
   - `default` → `env add --execute <pkg>`
   - `agent` → `env add --feature agent --execute <pkg>`
   - `ask` → One question, then stop. Two options only: the
     project runtime, or a named optional extra / agent tools.
     Do not add a context line, a manager command, or a flag to
     either option. Do not preview `pixi add`. Record only
     `python -m skore_skills env route <pkg>`. The install
     command waits until the next turn, after they answer.

   When `managed` is true and `scope` is not `refuse`, pass
   `--execute` on that one command. Never paste `pixi add` /
   `uv add` / `pip install` from memory.

9. If this turn is `skrub`, Graphviz is required for DataOp HTML
   graphs. An already-importable skrub still runs this step. Do
   not return before it because `import skrub` succeeds. After
   the add, run `python -m skore_skills env graphviz`. Then:

   - `dot` is set, or `action` is `conda` and managed →
     `python -m skore_skills env graphviz --execute` (installs
     conda Graphviz when needed, then verifies pydot can render
     SVG in the composed env).
   - `action` is `system` and `dot` is null → AskUserQuestion
     with two options, quoting JSON `instructions` only:
     1. **I will install Graphviz** (default) — do not wait;
        return.
     2. **Please wait until I confirm** — wait, then re-run
        `env graphviz --execute` to verify SVG rendering.
   - Unmanaged → do not `--execute`. Show `command` (conda) or
     `instructions` (system) from print-only JSON.

   If `--execute` fails, quote its repair diagnostic and end this
   install sequence. Return that diagnostic to the caller. Do not
   discard analysis the caller already finished. When this turn's
   only job was adding the package, that return ends the turn.
   Never prescribe `dot -c`, admin rights, or a package-manager
   repair from memory. Never invent `brew` / `apt` / `dnf` /
   `pacman` / `zypper` / `winget` from memory. Do not pip-install
   Graphviz or add it as a Python package on uv / poetry / hatch /
   pip-venv. Refuse that in prose; do not paste
   `env add graphviz` or `uv add graphviz` as a command fence.

Return when the import is available, when the user confirmed they
installed it, when they chose to handle it themselves, or when
this setup turn already chose user-managed and the package was
named. That last return does not wait.

## References

- `references/skore_variant.md`
