# review-ml-experiment eval

---

## CASE_01 — First audit runs without a question

**User prompt:**
> Review experiment 01_baseline.

**Assumed workspace state:**
- `scratch/results/01_baseline/report.html` exists.
- `scratch/audit/01_baseline/audit.md` does not.
- `python -m skore_skills review consent --stem 01_baseline`
  returns `audit`.
- `status.skills.audit-ml-pipeline` is `true`.

**Must do:**
- Run `python -m skore_skills review consent --stem 01_baseline`.
- On `audit`, load `audit-ml-pipeline` and `cells run`. Do not
  ask Review / Skip / Stop.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Ask Review / Skip / Stop.
- Open the Project or call `report.*` from this skill.
- Skip `cells run`.
- Write `journal/ideas/` before the digest exists.

---

## CASE_02 — Review loads audit and writes idea files

**User prompt:**
> Review.

**Assumed workspace state:**
- `review consent` returned `audit` and `cells run` produced the
  digest.
- `status.skills.audit-ml-pipeline` is `true`.
- The digest has one `Issues:` line, code `SKD003`.
- The design note named a gap this run did not test.

**Must do:**
- Write one file per candidate under `journal/ideas/`, including
  the check line and the design-note gap.
- Source the check file as `audit:01_baseline:checks.SKD003` and
  the gap as `design:01_baseline`.
- Write `Triage: open` on each new idea file.
- Upsert one `## Ideas` row per file: Question as plain text,
  Status `open`, Experiment `01_baseline`, Source copied from
  the file.
- Return the digest, `audit finding` JSON, `loop locator` JSON,
  and the idea paths.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Ask Review / Skip / Stop.
- Open the Project or call `report.*` from this skill.
- Write History, Backlog, Status, or a design note.
- Invent a metric or a winning idea.
- Put acceptance criteria in the idea files.

---

## CASE_03 — Missing audit skill writes no idea files

**User prompt:**
> Review experiment 01_baseline.

**Assumed workspace state:**
- `review consent` returned `audit`.
- `status.skills.audit-ml-pipeline` is not true.

**Must do:**
- Return `n/a — audit not run` so the caller can record-outcome.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `cells run`.
- Write any `journal/ideas/` file.
- Write an Ideas row or any other `JOURNAL.md` edit.
- Ask Review / Skip / Stop.

---

## CASE_04 — Existing digest refreshes files without cells run

**User prompt:**
> Review experiment 01_baseline.

**Assumed workspace state:**
- `python -m skore_skills review consent --stem 01_baseline`
  returns `proceed`.
- `scratch/audit/01_baseline/audit.md` already exists.
- `journal/ideas/01_baseline-calibration.md` exists with
  `Triage: discarded`.
- The Ideas table has that question with Status `discarded`.
- The user did not ask to re-audit.

**Must do:**
- Refresh `journal/ideas/` from the existing digest.
- Keep that file's `Triage: discarded`.
- Keep that Ideas row and its Status `discarded`.
- Skip `cells run`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Reset that file's `Triage` to `open`.
- Reset that Ideas Status to `open`.
- Delete that idea file.
- Remove that Ideas row.
- Re-run the skore checks.
- Write History, Backlog, Status, or a design note.

---

## CASE_05 — Missing report does not audit

**User prompt:**
> Review experiment 01_baseline.

**Assumed workspace state:**
- `review consent` returned `stop` / `report_html_missing`.
- `scratch/results/01_baseline/report.html` does not exist.

**Must do:**
- Name the missing `scratch/results/01_baseline/report.html`.
- Stop. Do not audit.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `cells run`.
- Load `manage-ml-backlog` record-outcome.
- Ask Review / Skip / Stop.
