# choose-python-library eval

---

## CASE_01 — Competing optional libraries

**User prompt:**
> Add either optuna or scikit-optimize for tuning. You choose.

**Assumed workspace state:**
- Pixi project; neither package is installed.
- The stack does not fix one canonical tuning library.

**Must do:**
- Present the smallest useful comparison and ask the user to choose.
- After a choice, route installation through
  `python -m skore_skills env add <package>`.

**Must NOT do:**
- Install both candidates.
- Pick silently because the user said “you choose.”
- Run `pip install`.
