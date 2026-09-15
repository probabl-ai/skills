# setup-ml-project eval

---

## CASE_01 — Full project setup

**User prompt:**
> Set up this empty folder for a tabular ML project.

**Assumed workspace state:**
- Empty folder; no manager or package name selected.

**Must do:**
- Dispatch workspace, environment, then git setup in that order.
- Ask for unresolved package, tabular, manager, and skore-mode
  decisions before scaffold/install actions.

**Must NOT do:**
- Run `pip install`.
- Commit without asking.
- Write a runnable baseline experiment.
