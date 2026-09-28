---
name: persist-ml-git
description: >
  Persist the current loop stage with the real git CLI when the
  end-turn hook says invoke. Trigger after
  `python -m skore_skills git end-turn --stage <stage>` returns
  action invoke, or when the user asks to commit this turn's work.
---

# Persist ML Git

The hook already ran this turn. Follow its JSON. Run `git` yourself.

1. If `action` is `skip`, stop. Do not nag. Load `triage-ml-task`
   if installed, else stop.
2. If `reason` is `resolve-dotfiles` and `ambiguous_dotfiles` is
   non-empty, ask once which hidden paths to keep. Then
   `python -m skore_skills git ignore-merge --decide` plus
   `--keep <path>` for each chosen path (no `--keep` if they keep
   none). Do not re-ask names gone from the next JSON. Never keep
   `.env` or `.skore`. If `ambiguous_dotfiles` is empty or `reason`
   is `persist`, do not ask about hidden paths.
   Exit code 2 from `git ignore-merge` is the structured
   `dotfile decision required` outcome, not a generic command
   failure: read its JSON, ask the decision, and rerun with
   `--decide`.
3. If `review_paths` is non-empty, ask once which of those paths
   to keep tracked. List each JSON `path` and `kind`, and say
   that the rest are ignored. Then
   `python -m skore_skills git review-decide` with
   `--keep <path>` for each chosen path and `--ignore <path>`
   for every other path in the list (no `--keep` if they keep
   none). Pass a folder path through with its trailing slash so
   the ignore line is that folder. Copy paths and kinds from the
   JSON; do not invent them. Do not re-ask paths gone from the
   next JSON. Never `--keep` `.env` or `.skore`. If
   `review_paths` is empty, do not ask about file size,
   artifacts, or datasets. Do this when `reason` is
   `resolve-review`, and also after step 2 when `reason` is
   `resolve-dotfiles` and that payload lists `review_paths`.
   Exit code 2 from `git review` or `git review-decide` is the
   structured `review decision required` outcome, not a generic
   command failure: read its JSON, ask the decision, and rerun
   `review-decide`.
4. Run `git status`. Stage only non-secret paths that are not
   still listed in `review_paths`: `git add -- <paths>`. Never
   `.env` or `.skore`.
5. Commit with a **one-line** subject from this turn's files and
   intent: `git commit -m "…"`. Do not use a canned stage slogan.
6. Load `triage-ml-task` if installed, else stop.

## Stop conditions

- Do not `git push`, amend, rebase, or `git config`.
- Do not invent a commit when the hook was `skip` (`off`,
  `unanswered`, `no_repo`, `clean`).
- Do not call `python -m skore_skills git end-turn --stage <stage>`
  to perform the commit; that command only prints facts.
