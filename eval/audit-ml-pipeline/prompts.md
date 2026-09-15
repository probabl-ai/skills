# audit-ml-pipeline eval

---

## CASE_01 — Audit stop is triage

**User prompt:**
> Audit experiment 01 and tell me what the report says.

**Assumed workspace state:**
- Approved design, experiment, smoke, and a skore report exist
  for stem `01_baseline`.

**Must do:**
- Name `python -m skore_skills cells run` for `audit/01_baseline.py`.
- After the digest, ask triage rather than iterate.

**Must NOT do:**
- Call `skore.evaluate` or `project.put`.
- Load `iterate-ml-experiment` as the next owner.
