# explore-ml-data eval

---

## CASE_01 — End of EDA returns to triage

**User prompt:**
> Explore the dataset and tell me what you found.

**Assumed workspace state:**
- Scaffolded workspace with raw data and tabular library recorded.
- No `data/eda.md` yet.

**Must do:**
- Name `python -m skore_skills cells run` for `data/eda.py`.
- After findings, give a short summary and ask triage (deeper EDA
  vs next stage).

**Must NOT do:**
- Design a learner or write `src/<pkg>/pipeline.py`.
- Load `iterate-ml-experiment` or skip to `build-ml-pipeline`.

---

## CASE_02 — Missing data is a status fact

**User prompt:**
> Run EDA.

**Assumed workspace state:**
- Scaffolded workspace with no data files and no data path.

**Must do:**
- Name `python -m skore_skills status`.
- Explain that data is missing and ask triage.

**Must NOT do:**
- Invent a dataset.
- Start `build-ml-pipeline`.
