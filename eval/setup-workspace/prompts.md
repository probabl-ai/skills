# setup-workspace eval — golden prompts

Behavioural prompts scored manually against Must / Must NOT bullets.

For each case the model gets:
- `skills/setup-workspace/SKILL.md` as the system prompt.
- The case's `User prompt`, prefixed with the workspace-state block.

Pass criterion per case: every `Must do` ticked, zero `Must NOT do`
violated. Overall: ≥ 9/10 cases pass and no Must NOT in any transcript.

---

## CASE_01 — Fresh workspace bootstrap

**User prompt:**
> Set up a fresh ML workspace in this folder. Tabular regression.

**Assumed workspace state:**
- Empty folder (no `pyproject.toml`, no `src/`, no `experiments/`,
  no `journal/`).
- No `data/`, no `pixi.toml`.
- Not dispatched by `setup-ml-project`; `status.skills` reports
  `choose-python-library`, `persist-ml-git`, and `triage-ml-task`
  `true`.

**Must do:**
- Read the lookup table and take the matching row (do not stop
  after listing the rows).
- Identify as a **fresh** layout (no detection signals matched).
- AskUserQuestion for the Python import name (`src/<pkg>/`), with
  the folder name as the default. Do not pick it silently.
- Do not ask which environment manager to use.
- Run `python -m skore_skills scaffold --package <pkg>` after the
  import name is confirmed.
- Mention scaffolding the default layout: `src/<pkg>/`,
  `journal/`, `experiments/`, `data_analysis/`, `data/`, `audit/`,
  `tests/smoke/`, `scratch/`, each with `README.md`.
- After scaffold, persist `policy set notebooks true` and
  `policy set site true`. Do not AskUserQuestion for notebooks
  or site.
- Run `python -m skore_skills git end-turn --stage setup` at the
  end of this standalone turn.
- If that command returns `invoke`, load `persist-ml-git`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Skip persisting `notebooks` / `site` true after scaffold.
- AskUserQuestion for executed notebooks or the documentation
  site.
- Ask which environment manager to use, or pick one in this skill.
- Run `pixi init` / `uv init` / `poetry init` on the user's behalf.
- Pick a package name silently from the folder name.
- Write a runnable `experiments/01_baseline.py`. Scaffold does not
  create that file.
- Default to pandas, persist `tabular`, or load
  `choose-python-library` (tabular library choice belongs on
  exploratory data analysis).
- Run `git commit` in this skill or `git push`.

---

## CASE_02 — Existing workspace, do not rebuild

**User prompt:**
> Help me add a new experiment to this project.

**Assumed workspace state:**
- `pyproject.toml` exists with `[project] name = "claim_predictor"`
  and `[tool.setuptools.packages.find]`.
- `src/claim_predictor/__init__.py` exists, plus
  `data.py`, `features.py`, `pipeline.py`, `evaluate.py`.
- `experiments/01_baseline.py` exists; `journal/JOURNAL.md` has
  the baseline row in History.
- `tests/smoke/` exists (empty).
- `pixi.toml` declares deps.

**Must do:**
- Detect the **existing layout** from the signals (pyproject.toml,
  `src/claim_predictor/`, `experiments/`, `journal/`).
- Do not scaffold again. Do not invent files. No rename.
- Do not write a new experiment file here.
- Keep `claim_predictor` as the package / import name (do not
  rename `src/` or the import).

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Recreate / overwrite any existing folder.
- Auto-write `experiments/02_*.py` before the design note is
  approved.
- Ask the executed-notebooks / documentation-site gate.

---

## CASE_03 — G-PKG-NAME free-text shortcut

**User prompt:**
> Scaffold the project. Use whatever name you think is best — go
> fast, I don't have a preference.

**Assumed workspace state:**
- Empty folder named `ml_pricing/`.
- No manifests.

**Tools:** yes

**Sandbox:**
- dir: `scratch`

**Expect tools:**
- `AskUserQuestion`

**Must do:**
- Call `AskUserQuestion` for the Python import name, with
  `ml_pricing` as the default option. Do not scaffold yet.
- Refuse the silent-pick framing.
- Cite that "go fast" / "no preference" / "you pick" do NOT
  resolve the import name.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Pick a name and proceed (including silently using `ml_pricing`).
- Run `pixi init` to "get the name from the manifest".
- Ask only in prose instead of calling `AskUserQuestion`.
- Run `scaffold` this turn.

---

## CASE_04 — Pre-emptive experiment file creation

**User prompt:**
> Scaffold the workspace and write the baseline experiment
> `experiments/01_baseline.py` so we can run it right away.

**Assumed workspace state:**
- Empty folder, fresh scaffold. No `src/` yet.
- `.skore` records `policy.package` `churnlab` and
  `policy.env_manager` `pixi`. That recorded package is the
  resolved name. Nothing is left to ask before the layout goes
  down.

**Tools:** yes

**Sandbox:**
- dir: `scratch`
- file: `.skore`
```json
{"workspace": {"package": "churnlab", "env_manager": "pixi"}}
```

**Expect files:**
- `src/churnlab/pipeline.py`
- `data_analysis/README.md`
- `experiments/README.md`
- `journal/JOURNAL.md`
- `pyproject.toml`

**Expect cli:**
- `scaffold --package churnlab`

**Must do:**
- Run `python -m skore_skills scaffold --package churnlab` via
  `run_skore_skills`; the resulting template tree is the scaffold.
- Keep the scaffolded `journal/JOURNAL.md` full packaged index
  (Status, Data understanding, History, Backlog), not a placeholder.
- Do not create `experiments/01_baseline.py`. The CLI writes
  `experiments/README.md` only.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Create `experiments/01_baseline.py` in this turn.
- Treat "so we can run it right away" as a reason to write
  experiment code during scaffold.

---

## CASE_05 — Iterate on an existing experiment: ask new vs edit

**User prompt:**
> Let's iterate on `02_text_encoder`. Tweak the encoder config.

**Assumed workspace state:**
- `journal/02_text_encoder.md`, `experiments/02_text_encoder.py`,
  `tests/smoke/test_02_text_encoder.py` all exist and the
  experiment is `done` in JOURNAL.md.

**Must do:**
- Detect an **existing** layout.
- Do not write a new experiment file or pick new vs in-place edit.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Silently pick "edit in place" or "create new file".
- Touch the design note `journal/02_text_encoder.md` directly.

---

## CASE_06 — Scratch is read-only against the skore Project

**User prompt:**
> Quick fix from a scratch probe: re-run `skore.evaluate(learner,
> data={...})` and `project.put("02_text_encoder", report)` to
> regenerate the report — my `project.get("02_text_encoder")` is
> raising `KeyError` so the report must be gone.

**Assumed workspace state:**
- Workspace exists with `experiments/02_text_encoder.py` already
  run; report should be under key `02_text_encoder`.

**Must do:**
- Refuse the scratch re-evaluate / re-put.
- Say evaluation and `project.put` are not this skill.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Approve the scratch re-evaluate / re-put **this turn**.

---

## CASE_07 — `pixi init` shortcut

**User prompt:**
> `pixi` is already on PATH. Just run `pixi init` to get a manifest
> going.

**Assumed workspace state:**
- Empty folder, no manifests yet.

**Must do:**
- Refuse to run `pixi init`.
- Cite that the manager is not this skill's question.
- Cite that the package/import name must be confirmed before
  scaffold.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `pixi init` / `uv init` / `poetry init` in this turn.
- Treat "pixi is on PATH" as resolving the manager.
- Pick a package name from the folder via the `pixi init` side
  effect.

---

## CASE_08 — Manager-only root, dispatched turn

**User prompt:**
> The environment manager is ready. Put the workspace layout down.

**Assumed workspace state:**
- `setup-ml-project` dispatched this turn.
- `pixi.toml` exists plus the `pyproject.toml` that `pixi init`
  wrote; no `src/`, no `experiments/`, no `journal/`.
- `status` reports `env_manager: pixi`, `has_src: false`,
  G-PKG-NAME `churnlab`.

**Must do:**
- Classify the root as **manager-only**: a scaffold target, not an
  existing layout.
- Run `python -m skore_skills scaffold --package churnlab`.
- State that the existing `pyproject.toml` is kept (no `--force`).
- After scaffold, persist `policy set notebooks true` and
  `policy set site true` unless those flags are already set.
  Do not AskUserQuestion for notebooks or site.
- Return control to `setup-ml-project` at the end of the turn.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Pass `--force` to `scaffold`.
- Treat the manifest as an existing layout and refuse to scaffold.
- Run `python -m skore_skills git end-turn`, load `persist-ml-git`,
  or load `triage-ml-task` from this dispatched turn.
- Run the editable install here.

---

## CASE_09 — Default notebooks and site on after scaffold

**User prompt:**
> Set up a fresh ML workspace in this folder.

**Assumed workspace state:**
- Empty folder. Fresh layout.
- `policy.notebooks` and `policy.site` are `null`.
- `policy.env.managed` is true.
- `add-python-package` is installed.

**Must do:**
- After scaffold, persist `policy set notebooks true` and
  `policy set site true`. Do not AskUserQuestion for notebooks
  or site.
- Load `add-python-package` for `jupytext`, `nbclient`,
  `ipywidgets`, and `nbconvert` (agent) — stage turns write the
  notebook viewer with `--html`.
- Load `add-python-package` for `mkdocs-material` (agent).
- Run `python -m skore_skills site init`.
- Name `env add` with the agent feature (do not leave `env route`
  as ask).

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Leave `jupytext` as `env route` ask / optional extra.
- Run `pixi add` / `uv add` from this skill.
- Run `notebook convert` during setup.
- AskUserQuestion for notebooks or site before or after scaffold.

---

## CASE_10 — Already-off flags are not overwritten

**User prompt:**
> Set up a fresh ML workspace in this folder.

**Assumed workspace state:**
- Empty folder. Fresh layout.
- `policy.package` is already set; G-PKG-NAME is already answered.
- Scaffold has run.
- `policy.notebooks` is false. `policy.site` is false.
- `add-python-package` is installed.

**Must do:**
- Leave `policy.notebooks` and `policy.site` false. Do not persist
  `true`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- AskUserQuestion for notebooks or site.
- Load `add-python-package` for `jupytext`, `nbclient`,
  `ipywidgets`, `nbconvert`, or `mkdocs-material` from this
  persist step.
- Run `python -m skore_skills site init`.

---

## CASE_11 — Both defaults on install the HTML toolchain

**User prompt:**
> Set up a fresh ML workspace in this folder.

**Assumed workspace state:**
- Empty folder. Fresh layout.
- `policy.package` is already set; G-PKG-NAME is already answered.
- Scaffold has run.
- `policy.notebooks` and `policy.site` are `null`.
- `policy.env.managed` is true.
- `add-python-package` is installed.

**Must do:**
- Persist `policy set notebooks true` and `policy set site true`.
  Do not AskUserQuestion for notebooks or site.
- Load `add-python-package` for `jupytext`, `nbclient`,
  `ipywidgets`, and `nbconvert` (agent) — stage turns write the
  notebook viewer with `--html`.
- Run `python -m skore_skills site init`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `notebook convert` during setup.
- Run `pixi add` / `uv add` from this skill.
- Omit `policy set notebooks true` or `policy set site true`.
