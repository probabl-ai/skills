# setup-git eval

---

## CASE_01 — First repository, autocommit on

**User prompt:**
> Initialize git here and make the first commit.

**Assumed workspace state:**
- Scaffolded workspace, not yet a git repository.
- `.env` is present and must remain untracked. Raw inputs are
  already ignored and are not in `git status`.
- `policy.git.autocommit` is `null` (never asked).
- The user answers the autocommit question with `on`.
- `python -m skore_skills git review` returns `review_paths` empty.

**Must do:**
- Emit the Pre-flight then run the commands (do not stop after
  listing boxes).
- Run `git init -b main` so the initial branch is `main`.
- Run `python -m skore_skills git ignore-merge`.
- Ask once whether later stages may autocommit (`on` vs `off`) and
  persist with `python -m skore_skills policy set git.autocommit on`.
- Run `python -m skore_skills git review` before the first commit.
- After `on`, and with `review_paths` empty, use `git add` and
  `git commit -m` without a second confirm.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Leave the initial branch as `master`.
- Stage `.env` or raw data.
- Ask a second time before the first commit after `on`.
- Ask which review paths to keep when `review_paths` is empty.
- Push or create a remote.
- Use `python -m skore_skills git end-turn` to create the first
  commit.

---

## CASE_02 — Autocommit already persisted

**User prompt:**
> Git is already initialized. Check ignore rules.

**Assumed workspace state:**
- A git repository exists and already has a HEAD commit.
- `policy.git.autocommit` is already `on`.

**Must do:**
- Run or run `python -m skore_skills git ignore-merge`.
- Skip the autocommit policy question because it is already `on`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Re-ask whether later stages may autocommit.
- Invent another `git commit` on this turn.
- Run `git push`.

---

## CASE_03 — Autocommit off, no first commit

**User prompt:**
> Initialize git here.

**Assumed workspace state:**
- Scaffolded workspace, not yet a git repository.
- `policy.git.autocommit` is `null`.
- The user answers the autocommit question with `off`.

**Must do:**
- Run `git init -b main` so the initial branch is `main`.
- Run `python -m skore_skills git ignore-merge`.
- Persist `python -m skore_skills policy set git.autocommit off`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Leave the initial branch as `master`.
- Run `git commit`.
- Run `git push`.
- Use `python -m skore_skills git end-turn` to create a commit.

---

## CASE_04 — Resolve hidden paths

**User prompt:**
> Set up git and keep the `.cursor` folder tracked.

**Assumed workspace state:**
- Scaffolded workspace, not yet a git repository.
- `python -m skore_skills git ignore-merge` returns
  `action: resolve-dotfiles` with `.cursor/` listed.
- `python -m skore_skills git review` returns `review_paths` empty.
- `policy.git.autocommit` is already `on`.
- No HEAD yet.

**Must do:**
- Run `git init -b main` so the initial branch is `main`.
- Run `python -m skore_skills git ignore-merge`.
- Ask which hidden paths to keep, then re-run
  `python -m skore_skills git ignore-merge --decide --keep .cursor`.
- After autocommit `on` and no HEAD, `git add` and `git commit`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Leave the initial branch as `master`.
- `--keep` `.env` or `.skore`.
- Ask a second question for review paths when `review_paths` is
  empty.
- Use `python -m skore_skills git end-turn` to create the first
  commit.

---

## CASE_05 — Ignore a review folder

**User prompt:**
> Set up git and make the first commit. Do not track `checkpoints/`.

**Assumed workspace state:**
- A git repository exists and has no HEAD yet.
- `policy.git.autocommit` is already `on`.
- `python -m skore_skills git ignore-merge` returns no
  `ambiguous_dotfiles`.
- `python -m skore_skills git review` returns
  `action: resolve-review` with `checkpoints/` kind `artifact`.
- `src/pkg/data.py` is also dirty.

**Must do:**
- Run `python -m skore_skills git review`.
- Ask which review paths to keep, listing `checkpoints/` and kind
  `artifact`, and saying the rest are ignored.
- Run `python -m skore_skills git review-decide --ignore checkpoints/`.
- `git add` and `git commit` the source file.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- `--keep` `checkpoints/`.
- Stage `checkpoints/`.
- Ask a separate hidden-file question when `ambiguous_dotfiles`
  is empty.
- Choose the ignore path by size or extension instead of the JSON.
- Use `python -m skore_skills git end-turn` to create the first
  commit.

---

## CASE_06 — Change an existing autocommit choice

**User prompt:**
> Stop committing at the end of each stage.

**Assumed workspace state:**
- A git repository exists and already has a HEAD commit.
- `policy.git.autocommit` is `on`.
- The user asked to change that choice. They answer `off`.

**Must do:**
- Re-ask whether later stages may commit, and persist
  `python -m skore_skills policy set git.autocommit off`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `git init`.
- Run `python -m skore_skills git ignore-merge`.
- Invent another `git commit` on this turn.

---

## CASE_07 — One question for hidden files and review paths

**User prompt:**
> Set up git and make the first commit. Keep `.python-version` tracked and do not track `checkpoints/`.

**Assumed workspace state:**
- Scaffolded workspace, not yet a git repository.
- `policy.git.autocommit` is already `on`.
- No HEAD yet.
- `python -m skore_skills git ignore-merge` returns
  `action: resolve-dotfiles` with `.python-version` listed.
- `python -m skore_skills git review` returns
  `action: resolve-review` with `checkpoints/` kind `artifact`.
- `src/pkg/data.py` is also dirty.

**Must do:**
- Run `git init -b main` so the initial branch is `main`.
- Run `python -m skore_skills git ignore-merge` and
  `python -m skore_skills git review` before asking.
- Ask **once**, listing `.python-version` and `checkpoints/`
  with kind `artifact`, and saying paths that are not kept are
  ignored.
- Run `python -m skore_skills git ignore-merge --decide --keep .python-version`.
- Run `python -m skore_skills git review-decide --ignore checkpoints/`.
- `git add` and `git commit` the source file.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Leave the initial branch as `master`.
- Ask two questions, one for hidden files and another for review
  paths.
- `--keep` `checkpoints/`, `.env`, or `.skore`.
- Stage `checkpoints/`.
- Use `python -m skore_skills git end-turn` to create the first
  commit.
