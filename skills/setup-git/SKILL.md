---
name: setup-git
description: >
  Set up git for an ML workspace after scaffolding. Trigger when the
  user asks to initialize version control, add ignore rules, or make
  the first commit. This action owns git setup only.
---

# Set Up Git

1. Detect whether the workspace is already a repository.
2. If not, propose `git init`.
3. Preserve existing ignore rules. For a fresh scaffold, verify that
   `.gitignore` excludes ephemeral `scratch/`, environments, caches,
   and credentials without ignoring durable journal, experiment,
   audit, or report sources.
4. Show `git status`.
5. Ask whether to create the first commit and what scope it should
   contain. Commit only after confirmation.

## Stop conditions

- Never overwrite `.gitignore`; merge only necessary entries.
- Never stage secrets, raw data, `.env`, or generated environments.
- Never commit, push, create a remote, or rewrite history without
  explicit authorization.
- Do not configure global git identity.

No dedicated `skore_skills git` command exists; keep this action
simple until reviewed.
