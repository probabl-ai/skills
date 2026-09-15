# model-ml-pipeline eval

---

## CASE_01 — Approved model implementation

**User prompt:**
> The baseline design is approved. Implement and test the model.

**Assumed workspace state:**
- Matching approved design note and experiment shell exist.

**Must do:**
- Dispatch build, then smoke-test. Do not insert evaluate between
  them.
- Preserve the matching experiment stem.
- After smoke, stop and ask triage.

**Must NOT do:**
- Replace skrub DataOps with a bare sklearn Pipeline.
- Mark the experiment done while smoke tests fail.
- Run `evaluate-ml-pipeline` as part of this stage.
