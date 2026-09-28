---
name: setup-git
description: >
  Set up git for an ML workspace after scaffolding. Trigger when the
  user asks to initialize version control, add ignore rules, or make
  the first commit. This action owns first-time git setup only.
---

# Set Up Git

## Pre-flight

Tick, then immediately run the matching sequence step. Do not stop
after listing the boxes.

```
- [ ] status (skip autocommit ask if already on/off, unless the user asked to change it)
- [ ] git init if no .git
- [ ] git ignore-merge (+ --decide / --keep if resolve-dotfiles)
- [ ] git.autocommit ask if null
- [ ] git review (+ review-decide if review_paths) before first commit
- [ ] first commit only if autocommit is on and no HEAD yet
```

## Sequence

1. Run `python -m skore_skills status`. If the user asked to
   change the commit choice and `policy.git.autocommit` is
   already `on` or `off`, re-ask that question and persist `on`
   or `off`. Do not `git init`. Do not `git ignore-merge`. If
   the new value is `on` and the repo has no HEAD yet, continue
   at the first-commit review (step 6). If the new value is
   `off`, or `on` and HEAD exists, stop this sequence: use the
   return rule in step 10 and do not continue at step 2. Do not
   invent another commit. Later stages follow the new value.
   Otherwise, if autocommit is already `on` or `off`, do not ask
   that question again.
2. If there is no `.git` directory, run `git init`. Do not run
   `git config`.
3. Run `python -m skore_skills git ignore-merge`.
4. If JSON `ambiguous_dotfiles` is non-empty, ask once which hidden
   paths to keep tracked, listing those exact paths in the question
   and saying that the rest get ignored. Then re-run
   `python -m skore_skills git ignore-merge --decide` plus
   `--keep <path>` for each chosen path (no `--keep` if they keep
   none). Do not re-ask names gone from the next JSON. Never
   `--keep` `.env` or `.skore`.
5. If `policy.git.autocommit` is `null`, ask **once**: should later
   stages persist with `git commit` (`on`) or never (`off`)? State
   in 2–4 lines what the answer authorizes — commits at the end of
   later stages, starting with the first commit this turn — and
   which paths stay ignored; a file link is an addition, never the
   context. Persist
   with `python -m skore_skills policy set git.autocommit on` or
   `off`. That answer is also consent for the first commit. It
   does not authorize tracking paths in `review_paths`.
6. If autocommit is `on` and this repo has no HEAD yet, run
   `python -m skore_skills git review`. If `review_paths` is
   non-empty, ask once which of those paths to keep tracked.
   List each JSON `path` and `kind`, and say that the rest are
   ignored. Copy paths from the JSON; do not reclassify them.
   Then `python -m skore_skills git review-decide` with
   `--keep <path>` for each chosen path and `--ignore <path>`
   for every other path in that list (no `--keep` if they keep
   none). Pass a folder path through with its trailing slash so
   the ignore line is that folder. Do not re-ask paths gone from
   the next JSON. Never `--keep` `.env` or `.skore`. Exit code 2
   from `git review` or `git review-decide` is the structured
   review outcome, not a generic command failure: read its JSON,
   ask the decision, and rerun `review-decide`. If `review_paths`
   is empty, do not ask about file size, artifacts, or datasets.
7. Then `git status`. `git add -- <paths>` only paths that are
   not still listed in `review_paths`, and
   `git commit -m "<one-line subject>"` from this setup turn. Do
   not ask a second time about autocommit. Never stage `.env` or
   `.skore`.
8. If autocommit is `off`, stop after ignore-merge. Do not
   `git commit`.
9. If autocommit is already `on` and HEAD exists, stop after
   ignore-merge. Do not invent another commit. Later stages use
   `python -m skore_skills git end-turn --stage <stage>` then
   `persist-ml-git`, where `<stage>` is `setup`, `data_analysis`,
   `implement`, `evaluate`, or `backlog`. When that skill is not installed, those stages report the
   pending paths instead of committing.
10. When `setup-ml-project` dispatched this turn and is in this
   session, return control to it. Otherwise load `triage-ml-task`
   if `status.skills` reports it installed, else stop.

## Stop conditions

- Never overwrite `.gitignore`; `git ignore-merge` unions packaged
  rules.
- Never stage `.env`, `.skore`, or a review path that was not
  kept.
- Never push, create a remote, amend, rebase, or set git identity.
- Do not call `python -m skore_skills git end-turn --stage …` to
  create the first commit.
