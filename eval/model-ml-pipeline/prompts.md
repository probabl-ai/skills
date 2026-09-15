# model-ml-pipeline eval

---

## CASE_01 — Approved model implementation

**User prompt:**
> The baseline design is approved. Implement and test the model.

**Assumed workspace state:**
- Matching approved design note and experiment shell exist.

**Must do:**
- Dispatch build, evaluate, then smoke-test in that order.
- Preserve the matching experiment stem.

**Must NOT do:**
- Replace skrub DataOps with a bare sklearn Pipeline.
- Mark the experiment done while smoke tests fail.

---

## CASE_02 — Missing design note stops before code

**User prompt:**
> Implement experiment 02 for the selected target transform.

**Assumed workspace state:**
- The Backlog choice is confirmed with stem `02_target_transform`.
- `journal/02_target_transform.md` does not exist.

**Must do:**
- Name `python -m skore_skills scaffold --journal --stem
  02_target_transform` to create the packaged design-note shell.
- State that Question, Motivation, Method, and Risks are filled only
  after that command creates the shell, then stop for user approval.

**Must NOT do:**
- Write model or experiment code before the design note is approved.
- Recreate or fill the design-note shape from memory when the CLI
  command did not run this turn.
