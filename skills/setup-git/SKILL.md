---
name: setup-git
description: >
  Set up git for an ML workspace after scaffolding. Trigger when the
  user asks to initialize version control, add ignore rules, or make
  the first commit. This action owns first-time git setup only.
  Before the first commit, ask once which unknown hidden files and
  review paths to keep tracked.
---

# Set Up Git

## Pre-flight

Tick, then immediately run the matching sequence step. Do not stop
after listing the boxes.

```
- [ ] status (skip autocommit ask if already on/off, unless the user asked to change it)
- [ ] git init -b main if no .git
- [ ] git ignore-merge (record ambiguous_dotfiles; do not ask yet)
- [ ] git.autocommit ask if null
- [ ] off, or on and HEAD exists → stop; no file question; no commit
- [ ] on and no HEAD → git review; one keep-or-ignore question if either list is non-empty; first commit
```

## Sequence

1. Run `python -m skore_skills status`. If the user asked to
   change the commit choice and `policy.git.autocommit` is
   already `on` or `off`, re-ask that question and persist `on`
   or `off`. Do not `git init`. Do not `git ignore-merge`. If
   the new value is `on` and the repo has no HEAD yet, continue
   at the first-commit review (step 7). If the new value is
   `off`, or `on` and HEAD exists, stop this sequence: use the
   return rule in step 9 and do not continue at step 2. Do not
   invent another commit. Later stages follow the new value.
   Otherwise, if autocommit is already `on` or `off`, do not ask
   that question again.
2. If there is no `.git` directory, run `git init -b main`. The
   initial branch is `main`. Do not run `git config`. Do not name
   that branch `master`. Do not rename a branch that already
   exists.
3. Run `python -m skore_skills git ignore-merge`. Keep the JSON
   `ambiguous_dotfiles` list. Exit code 2 is that structured
   list, not a command failure. Do not ask yet.
4. If `policy.git.autocommit` is `null`, ask **once**: should later
   stages persist with `git commit` (`on`) or never (`off`)? State
   in 2–4 lines what the answer authorizes — commits at the end of
   later stages, starting with the first commit this turn — and
   which paths stay ignored; a file link is an addition, never the
   context. Persist
   with `python -m skore_skills policy set git.autocommit on` or
   `off`. That answer is also consent for the first commit. It
   does not authorize tracking `ambiguous_dotfiles` or
   `review_paths`. When `setup-ml-project` already persisted `on`
   or `off` this turn, do not ask again.
5. If autocommit is `off`, stop. Do not ask which files to keep.
   Do not `git commit`. Use the return rule in step 9.
6. If autocommit is `on` and HEAD exists, stop after ignore-merge.
   Do not ask which files to keep. Do not invent another commit.
   Later stages use
   `python -m skore_skills git end-turn --stage <stage>` then
   `persist-ml-git`, where `<stage>` is `setup`, `data_analysis`,
   `implement`, `evaluate`, or `backlog`. When that skill is not
   installed, those stages report the pending paths instead of
   committing.
7. If autocommit is `on` and this repo has no HEAD yet, run
   `python -m skore_skills git review`. When this step is reached
   from step 1, ignore-merge did not run: use only
   `review_paths`. If `ambiguous_dotfiles` and `review_paths` are
   both empty, do not ask. If either list is non-empty, ask
   **once** which of those paths to keep tracked. List every
   hidden path and each review `path` with its `kind`. Say that
   paths they do not keep are ignored. Do not ask a second
   question for the other list. Copy paths from the JSON; do not
   reclassify them. Do not ask about file size, artifacts, or
   datasets when `review_paths` is empty, and do not ask about
   hidden files when `ambiguous_dotfiles` is empty.
   Then:

   - `ambiguous_dotfiles` was non-empty → re-run
     `python -m skore_skills git ignore-merge --decide` plus
     `--keep <path>` for each chosen hidden path (no `--keep` if
     they keep none).
   - `review_paths` was non-empty →
     `python -m skore_skills git review-decide` with
     `--keep <path>` for each chosen path and `--ignore <path>`
     for every other path in that list (no `--keep` if they keep
     none). Pass a folder path through with its trailing slash so
     the ignore line is that folder. Exit code 2 from `git review`
     or `git review-decide` is the structured review outcome, not
     a generic command failure: read its JSON. The question in
     this step is that decision; do not ask again. If
     `review-decide` still lists paths, rerun it with the same
     choices.

   Run only the command for a list that was non-empty. Do not
   re-ask paths gone from the next JSON. Never `--keep` `.env` or
   `.skore`.
8. Then `git status`. `git add -- <paths>` only paths that are
   not still listed in `review_paths`, and
   `git commit -m "<one-line subject>"` from this setup turn. Do
   not ask a second time about autocommit. Never stage `.env` or
   `.skore`.
9. When `setup-ml-project` dispatched this turn and is in this
   session, return control to it. Otherwise load `triage-ml-task`
   if `status.skills` reports it installed, else stop.

## Stop conditions

- Never overwrite `.gitignore`; `git ignore-merge` unions packaged
  rules.
- Never stage `.env`, `.skore`, or a review path that was not
  kept.
- Never split hidden files and review paths into two questions
  before the first commit.
- Never push, create a remote, amend, rebase, or set git identity.
- The initial branch is `main`. Do not name it `master`. Do not
  rename a branch that already exists.
- Do not call `python -m skore_skills git end-turn --stage …` to
  create the first commit.
