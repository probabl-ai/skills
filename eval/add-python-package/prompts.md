# add-python-package eval

---

## CASE_01 — Managed add

**User prompt:**
> Add skrub to the project.

**Assumed workspace state:**
- Pixi project (`pixi.toml` or `[tool.pixi]`).
- `status.policy.env.managed` is true.
- `env_manager` is pixi.
- `python -m skore_skills env route skrub` returns
  `scope: default`.

**Must do:**
- Emit the Pre-flight then run the commands (do not stop after
  listing boxes).
- Run `python -m skore_skills env detect` / status.
- Run `python -m skore_skills env add --execute skrub` (or
  `env route` then that add). Do not invent `pixi add` from memory.
- Route skrub to default (not `--feature agent`).
- Run `python -m skore_skills env graphviz` and, with `action`
  conda and managed, `env graphviz --execute`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `pip install skrub`.
- Run `pip install graphviz`.
- Re-bootstrap with `env init`.

---

## CASE_02 — Unmanaged default: I will handle it

**User prompt:**
> We need pandas for EDA.

**Assumed workspace state:**
- `policy.env.managed` is false.
- Manager is pixi (manifest present).

**Must do:**
- Ask with two options; default **I will handle it**.
- Name the package and show the manager command (`pixi add pandas`).
- Return without waiting after the default choice.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Pass `--execute` on `env add`.
- Mention `python -m skore_skills` or `env add` in the user-facing
  ask. The two-option ask must not tell the user to run `env add`.
  A sentence that the print-only `env add` could not run this turn
  is not that ask.
- Treat unmanaged as silent skip without naming the package.

---

## CASE_03 — Unmanaged: please install now

**User prompt:**
> Install pytest, and wait until I say it is done.

**Assumed workspace state:**
- `policy.env.managed` is false.
- User picks **Please install this now**.
- `python -m skore_skills env route pytest` returns
  `scope: default`.
- pytest is a stage library (not agent).

**Must do:**
- Show the manager command (pytest on default, not agent).
- Wait for the user to confirm.
- Still not execute `env add`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `python -m skore_skills env add pytest --execute`.
- Show `python -m skore_skills env add` in the user-facing ask.
- Put pytest in `--feature agent`.

---

## CASE_04 — Named booster is added

**User prompt:**
> Add xgboost.

**Assumed workspace state:**
- Managed pixi project.
- `python -m skore_skills env route xgboost` returns
  `scope: default`.

**Must do:**
- Run `python -m skore_skills env add --execute xgboost` (or
  `env route` then that add).

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Refuse xgboost or swap it for HistGradientBoosting.
- Run `pip install xgboost`.

---

## CASE_05 — Unresolved manager

**User prompt:**
> Add ruff.

**Assumed workspace state:**
- `env.managed` is null / unanswered.
- `env detect` reports none or unmanaged-unasked.
- `status.skills.setup-ml-project` is true.

**Must do:**
- Load `setup-ml-project` and stop. Do not ask a separate
  environment question. Do not load `setup-python-env`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `env init`.
- Run `env add` while managed is unanswered.
- Load `setup-python-env`.

---

## CASE_06 — Skore source follows the project manager

**User prompt:**
> Install Skore for Hub mode.

**Assumed workspace state:**
- Managed pixi project.
- `policy.skore_mode` is `hub`.

**Must do:**
- Run `python -m skore_skills env add-skore --mode hub --execute`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `pixi add "skore[hub]"`.
- Add Skore with `--pypi`.
- Infer the package source from PATH.

---

## CASE_07 — Editable workspace package

**User prompt:**
> Install the workspace package in editable mode.

**Assumed workspace state:**
- Managed pixi project.
- `has_src` is true.
- User asked for the workspace package (not a named dependency).

**Must do:**
- Run `python -m skore_skills env add --editable --execute`.
- If that command exits non-zero, do not describe the install as done.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `pip install -e .`.
- Run `env add --editable` for a named library such as skrub.

---

## CASE_08 — G-ENV-SCOPE ask

**User prompt:**
> Add optuna.

**Assumed workspace state:**
- Managed pixi project.
- `env route optuna` returns `scope: ask`.

**Must do:**
- Run `python -m skore_skills env route optuna`.
- Ask in plain language whether the package belongs in the
  project runtime vs a named optional extra / agent tools.
- After the choice, `env add --execute` with the mapped
  `--feature` / `--group`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Silently `pixi add optuna` from memory.
- Put `--feature` / `--group` in the question text.
- Put optuna on `--feature agent` without asking.

---

## CASE_09 — Skrub on uv never pip-installs Graphviz

**User prompt:**
> Add skrub to the project.

**Assumed workspace state:**
- Managed uv project.
- `env route skrub` returns `scope: default`.
- `env graphviz` already returned `action: system`, `dot: null`,
  and `instructions`: "Install Graphviz with your OS package
  manager so `dot` is on PATH."

**Must do:**
- Run `python -m skore_skills env add --execute skrub`.
- Treat that `env graphviz` JSON as already returned (naming
  `python -m skore_skills env graphviz` is optional).
- Ask the Graphviz question quoting JSON `instructions` only.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Propose `env add graphviz` or `uv add graphviz` as the
  Graphviz install (a fenced command or a step to run). Naming
  them in a STOP / "will not" sentence is allowed.
- Run `pip install graphviz`.
- Invent `brew install graphviz` without quoting CLI stdout.

---

## CASE_10 — Setup already chose user-managed

**User prompt:**
> Add pandas.

**Assumed workspace state:**
- `setup-ml-project` dispatched this turn.
- The opening question already set `policy.env.managed` to false.
- Manager is pixi (manifest present).
- This is not a standalone unmanaged request.

**Must do:**
- Name pandas and the pixi manager in words, then return.
- Do not run `env add`. Print-only refuses while managed is false.
- Do not ask **I will handle it** or **Please install this now**.
- Do not wait for confirmation, and do not say the turn continues
  once pandas is installed.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Ask the two-option unmanaged question.
- Run `env add` or pass `--execute`.
- Invent `pixi add pandas` as a command for the user to run.
- Wait for the user to install pandas.

---

## CASE_11 — Already-importable skrub still registers Graphviz

**User prompt:**
> Add skrub to the project.

**Assumed workspace state:**
- Pixi project (`pixi.toml` or `[tool.pixi]`).
- `status.policy.env.managed` is true.
- `env_manager` is pixi.
- `import skrub` already succeeds.
- `python -m skore_skills env route skrub` returns
  `scope: default`.
- `env graphviz` returns `action: conda` and `managed: true`.

**Must do:**
- Run `python -m skore_skills env graphviz` and
  `env graphviz --execute`.
- Do not return only because `import skrub` already succeeds.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Return before Graphviz setup because the import works.
- Run `pip install graphviz`.

---

## CASE_12 — Existing system Graphviz passes SVG verification

**User prompt:**
> Add skrub to the project.

**Assumed workspace state:**
- Managed uv project.
- `env route skrub` returns `scope: default`.
- `env graphviz` returns `action: system`,
  `dot: /opt/homebrew/bin/dot`, and `managed: true`.
- `env graphviz --execute` succeeds after verifying pydot can
  render SVG.

**Must do:**
- Run `python -m skore_skills env add --execute skrub`.
- Run `python -m skore_skills env graphviz --execute`.
- Finish without asking the user to install or repair Graphviz.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Ask the Graphviz installation question.
- Run or recommend `dot -c`.
- Run `pip install graphviz`.

---

## CASE_13 — Broken Graphviz reports the CLI repair diagnostic

**User prompt:**
> Add skrub to the project.

**Assumed workspace state:**
- Managed uv project.
- `env route skrub` returns `scope: default`.
- `env graphviz` returns `action: system` and
  `dot: C:\\Program Files\\Graphviz\\bin\\dot.exe`.
- `env graphviz --execute` fails with:
  "Graphviz SVG rendering failed; repair or reinstall pydot and
  Graphviz with their existing package managers".

**Must do:**
- Run `python -m skore_skills env add --execute skrub`.
- Run `python -m skore_skills env graphviz --execute`.
- Quote the repair diagnostic and end the turn. This turn's only
  job was adding the package.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Recommend admin rights or `dot -c`.
- Invent a brew, apt, dnf, pacman, zypper, or winget repair.
- Run `pip install graphviz`.
