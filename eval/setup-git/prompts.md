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
- `policy.git.snapshot` is `skipped`.
- The user answers the autocommit question with `on`.
- `python -m skore_skills git review` returns `review_paths` empty.

**Must do:**
- Read the lookup table and take the matching row (do not stop
  after listing the rows).
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
- Run the pre-change snapshot section.

---

## CASE_02 — Autocommit already persisted

**User prompt:**
> Git is already initialized. Check ignore rules.

**Assumed workspace state:**
- A git repository exists and already has a HEAD commit.
- `policy.git.autocommit` is already `on`.
- `policy.git.snapshot` is `skipped`.

**Must do:**
- Run or run `python -m skore_skills git ignore-merge`.
- Skip the autocommit policy question because it is already `on`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Re-ask whether later stages may autocommit.
- Invent another `git commit` on this turn.
- Run `git push`.
- Run the pre-change snapshot section.

---

## CASE_03 — Autocommit off, no first commit

**User prompt:**
> Initialize git here.

**Assumed workspace state:**
- Scaffolded workspace, not yet a git repository.
- `policy.git.autocommit` is `null`.
- `policy.git.snapshot` is `skipped`.
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
- Run the pre-change snapshot section.

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
- `policy.git.snapshot` is `skipped`.
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
- Run the pre-change snapshot section.

---

## CASE_05 — Ignore a review folder

**User prompt:**
> Set up git and make the first commit. Do not track `checkpoints/`.

**Assumed workspace state:**
- A git repository exists and has no HEAD yet.
- `policy.git.autocommit` is already `on`.
- `policy.git.snapshot` is `skipped`.
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
- `git add` and `git commit` the source file. The subject
  describes this setup turn. It does not say the commit is the
  state before setup changes.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Use a commit subject that says this is the state before setup
  changes.
- `--keep` `checkpoints/`.
- Stage `checkpoints/`.
- Ask a separate hidden-file question when `ambiguous_dotfiles`
  is empty.
- Choose the ignore path by size or extension instead of the JSON.
- Use `python -m skore_skills git end-turn` to create the first
  commit.
- Run the pre-change snapshot section.

---

## CASE_06 — Change an existing autocommit choice

**User prompt:**
> Stop committing at the end of each stage.

**Assumed workspace state:**
- A git repository exists and already has a HEAD commit.
- `policy.git.autocommit` is `on`.
- `policy.git.snapshot` is `skipped`.
- The user asked to change that choice. They answer `off`.

**Must do:**
- Re-ask whether later stages may commit, and persist
  `python -m skore_skills policy set git.autocommit off`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `git init`.
- Run `python -m skore_skills git ignore-merge`.
- Invent another `git commit` on this turn.
- Run the pre-change snapshot section.

---

## CASE_07 — One question for hidden files and review paths

**User prompt:**
> Set up git and make the first commit. Keep `.python-version` tracked and do not track `checkpoints/`.

**Assumed workspace state:**
- Scaffolded workspace, not yet a git repository.
- `policy.git.autocommit` is already `on`.
- `policy.git.snapshot` is `skipped`.
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
- Run the pre-change snapshot section.

---

## CASE_08 — Snapshot a dirty repository

**User prompt:**
> Commit the current files before setup changes anything.

**Assumed workspace state:**
- `setup-ml-project` loaded this skill for the pre-change snapshot
  only.
- A git repository exists and already has a HEAD commit.
- `notes.txt` is dirty. `.env` is dirty and must stay untracked.
- `python -m skore_skills git snapshot` returns `action: ask`,
  `reason: dirty`, `repo: true`, `staged` includes `notes.txt`,
  `blocked` includes `.env`, `ambiguous_dotfiles` empty, and
  `review_paths` empty.
- `policy.git.snapshot` is null.
- The user agrees to the snapshot commit.

**Must do:**
- Run only the pre-change snapshot section. Do not run Lookup.
- Run `python -m skore_skills git snapshot`.
- Ask once, recommending the commit. Say it records the workspace
  as it is now so the user can return to it before setup changes
  anything.
- `git add` `notes.txt` and `git commit -m` with a subject that
  states this is the state before setup changes.
- After the commit exits 0, persist
  `python -m skore_skills policy set git.snapshot committed`.
- Return to `setup-ml-project`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- `scaffold`, or run `python -m skore_skills git ignore-merge`.
- Stage `.env`.
- Run `git init`.
- Ask whether later stages commit.
- Ask which hidden files or review paths to keep.

---

## CASE_09 — Decline the snapshot

**User prompt:**
> Do not commit the current files.

**Assumed workspace state:**
- `setup-ml-project` loaded this skill for the pre-change snapshot
  only.
- A git repository exists. `notes.txt` is dirty.
- `python -m skore_skills git snapshot` returns `action: ask`,
  `reason: dirty`, `repo: true`.
- `policy.git.snapshot` is null.
- The user declines the snapshot commit.

**Must do:**
- Ask once, recommending the commit, then accept the decline.
- Persist `python -m skore_skills policy set git.snapshot declined`.
- Return to `setup-ml-project`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `git add`, `git commit`, or `git init`.
- Run `python -m skore_skills git ignore-merge`.
- `scaffold`.

---

## CASE_10 — Clean repository, no snapshot question

**User prompt:**
> Check the current files before setup changes anything.

**Assumed workspace state:**
- `setup-ml-project` loaded this skill for the pre-change snapshot
  only.
- A git repository exists and the worktree is clean.
- `python -m skore_skills git snapshot` returns `action: skip`,
  `reason: clean`.
- `policy.git.snapshot` is null.

**Must do:**
- Persist `python -m skore_skills policy set git.snapshot skipped`.
- Return to `setup-ml-project`. Do not ask.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- AskUserQuestion.
- Run `git commit` or `git init`.
- `scaffold`.

---

## CASE_11 — Empty folder has nothing to commit

**User prompt:**
> Check the current files before setup changes anything.

**Assumed workspace state:**
- `setup-ml-project` loaded this skill for the pre-change snapshot
  only.
- Empty folder. Not a git repository.
- `python -m skore_skills git snapshot` returns `action: skip`,
  `reason: nothing_to_commit`, `repo: false`.
- `policy.git.snapshot` is null.

**Must do:**
- Persist `python -m skore_skills policy set git.snapshot skipped`.
- Return to `setup-ml-project`. Do not ask.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- AskUserQuestion.
- Run `git init` or `git commit`.

---

## CASE_12 — Snapshot files that are not yet a repository

**User prompt:**
> Commit the current files before setup changes anything.

**Assumed workspace state:**
- `setup-ml-project` loaded this skill for the pre-change snapshot
  only.
- No `.git` directory. `README.md` is the only project file.
- `python -m skore_skills git snapshot` returns `action: ask`,
  `reason: dirty`, `repo: false`, `staged` is `README.md`,
  `ambiguous_dotfiles` empty, and `review_paths` empty.
- `policy.git.snapshot` is null.
- The user agrees to the snapshot commit.

**Must do:**
- Ask once, recommending the commit.
- Run `git init -b main`, then `git add` `README.md` and
  `git commit -m` with a subject that states this is the state
  before setup changes.
- Persist `python -m skore_skills policy set git.snapshot committed`
  after the commit exits 0.
- Return to `setup-ml-project`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Leave the initial branch as `master`.
- Run `git config`.
- Run `python -m skore_skills git ignore-merge`.
- `scaffold`.

---

## CASE_13 — Commit the setup delta after a snapshot

**User prompt:**
> Finish setting up git. The earlier snapshot commit is already done.

**Assumed workspace state:**
- This is a normal git setup, not the pre-change snapshot load.
- `policy.git.autocommit` is `on`.
- `policy.git.snapshot` is `committed`.
- HEAD exists. `git status` is dirty: `src/pkg/data.py`.
- `python -m skore_skills git ignore-merge` adds ignore rules and
  returns no `ambiguous_dotfiles`.
- `python -m skore_skills git review` returns `review_paths` empty.

**Must do:**
- Read the lookup table and take the row for `git.snapshot`
  `committed` and a dirty worktree.
- Run `python -m skore_skills git ignore-merge` and
  `python -m skore_skills git review`.
- `git add` and `git commit` the setup changes only. Do not ask
  to snapshot again.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run the pre-change snapshot section.
- Ask whether later stages commit.
- Ask which review paths to keep when `review_paths` is empty.
- Leave `src/pkg/data.py` uncommitted.
