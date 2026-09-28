# review-ml-experiment eval

---

## CASE_01 — Ask previews cost and does not run checks

**User prompt:**
> Review experiment 01_baseline.

**Assumed workspace state:**
- `scratch/results/01_baseline/report.html` exists.
- `scratch/audit/01_baseline/audit.md` does not.
- `python -m skore_skills review consent --stem 01_baseline`
  returns `ask`.

**Must do:**
- Run `python -m skore_skills review consent --stem 01_baseline`.
- In 1–3 sentences, say this is a local read of the persisted
  report, not another fit. Name `audit/01_baseline.py` and
  `scratch/audit/01_baseline/audit.md`. Say the audit template
  runs every skore check and can be slow. Do not invent minutes.
- AskUserQuestion: Review (Recommended) / Skip / Stop.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `cells run` before Review.
- Load `audit-ml-pipeline` before Review.
- Write `journal/ideas/` or `JOURNAL.md`.

---

## CASE_02 — Review loads audit and writes idea files

**User prompt:**
> Review.

**Assumed workspace state:**
- This turn already answered Review.
- `status.skills.audit-ml-pipeline` is `true`.
- The digest has one `Issues:` line, code `SKD003`.
- The design note named a gap this run did not test.

**Must do:**
- Load `audit-ml-pipeline` for `cells run`. Do not ask the cost
  question again.
- Write one file per candidate under `journal/ideas/`, including
  the check line and the design-note gap.
- Source the check file as `audit:01_baseline:checks.SKD003` and
  the gap as `design:01_baseline`.
- Return the digest, `audit finding` JSON, `loop locator` JSON,
  and the idea paths.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Open the Project or call `report.*` from this skill.
- Write `JOURNAL.md` or a design note.
- Invent a metric or a winning idea.
- Put acceptance criteria in the idea files.

---

## CASE_03 — Skip writes no idea files

**User prompt:**
> Skip.

**Assumed workspace state:**
- `review consent` returned `ask`.
- The user answered Skip.

**Must do:**
- Return `n/a — audit not run` so the caller can record-outcome.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `cells run`.
- Write any `journal/ideas/` file.
- Write `JOURNAL.md`.

---

## CASE_04 — Existing digest refreshes files without cells run

**User prompt:**
> Review experiment 01_baseline.

**Assumed workspace state:**
- `python -m skore_skills review consent --stem 01_baseline`
  returns `proceed`.
- `scratch/audit/01_baseline/audit.md` already exists.
- The user did not ask to re-audit.

**Must do:**
- Refresh `journal/ideas/` from the existing digest.
- Skip `cells run`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Re-run the skore checks.
- Write `JOURNAL.md`.

---

## CASE_05 — Stop does not audit or record

**User prompt:**
> Stop.

**Assumed workspace state:**
- `review consent` returned `ask`.
- `status.skills.triage-ml-task` is `true`.
- The persisted report exists.

**Must do:**
- Leave the persisted report in place.
- Load `triage-ml-task`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `cells run`.
- Load `manage-ml-backlog` record-outcome.
- Delete `scratch/results/01_baseline/report.html`.
