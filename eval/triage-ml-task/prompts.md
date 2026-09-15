# triage-ml-task eval

---

## CASE_01 — Ambiguous capability request

**User prompt:**
> What can you help me with on this machine learning project?

**Assumed workspace state:**
- Existing scaffold with no specific task requested.
- No `.skore` file.

**Must do:**
- Name `python -m skore_skills status`.
- Name the current `loop_stage` (or equivalent stage) from the
  snapshot, even when `.skore` is missing.
- Ask exactly one focused question: stay, go deeper, next stage,
  confirm/persist detected facts, or change a persisted choice.

**Must NOT do:**
- Start designing the next experiment.
- Claim to have loaded or executed every skill.
- Treat `iterate-ml-experiment` as the session owner.
- Treat the missing `.skore` as an empty project despite the
  existing scaffold.
