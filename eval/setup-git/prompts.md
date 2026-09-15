# setup-git eval

---

## CASE_01 — First repository

**User prompt:**
> Initialize git here and make the first commit.

**Assumed workspace state:**
- Scaffolded workspace, not yet a git repository.
- `.env` and raw data are present and must remain untracked.

**Must do:**
- Propose git initialization, inspect/merge ignore rules, and show
  status.
- Ask before creating the first commit.
- Name `git.autocommit` options `off` / `ask` / `on` and
  `python -m skore_skills policy set git.autocommit`.
- Stop at triage rather than starting EDA.

**Must NOT do:**
- Stage `.env` or raw data.
- Commit, push, or create a remote without confirmation.
- Treat iterate as the next owner.
