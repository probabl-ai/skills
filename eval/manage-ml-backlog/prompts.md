# manage-ml-backlog eval

---

## CASE_01 — Record outcome into History

**User prompt:**
> The 01_baseline run finished. Record it.

**Assumed workspace state:**
- Audit digest exists with a headline ROC-AUC.
- Smoke tests passed.
- History row for `01_baseline` is `running`.
- G-REPORT-LOCATOR and G-AUDIT-FINDING are available from the digest.

**Must do:**
- Run `python -m skore_skills status`.
- Copy the headline result, locator, and G-AUDIT-FINDING into
  History / the design-note Status block.
- Do not open idea triage in this record. An empty `journal/ideas/`
  is a one-line skip. Do not edit the Ideas table.
- Run `python -m skore_skills git end-turn --stage backlog`.
- If that command returns `invoke`, load `persist-ml-git`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Invent a metric that is not in the digest or user text.
- Draft `02_*.py` in this turn.
- Run `git commit` in this skill or `git push`.
- Change design-note `State` or `Approved by user on`.

---

## CASE_02 — Promote one idea file

**User prompt:**
> What should we try next?

**Assumed workspace state:**
- `journal/ideas/01_baseline-calibration.md` exists.
- Its Source is `audit:01_baseline:checks.SKD003`.
- That Question and Source are not already a Backlog row.
- The Ideas table has that Question with Status `open`.
- The highest Backlog index is `B2`.
- The user answers promote.

**Must do:**
- Append a stable `B3` row. Item comes from the file's Question.
  Source is copied verbatim.
- Remove that Ideas row.
- Set `Triage: promoted` on
  `journal/ideas/01_baseline-calibration.md` and keep the file.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Delete `journal/ideas/01_baseline-calibration.md`.
- Silently pick an existing Backlog row.
- Start `build-ml-pipeline`.
- Write a design note in this turn.
- Renumber `B1` or `B2`.

---

## CASE_03 — Missing journal index uses packaged shape

**User prompt:**
> Start the experiment backlog for this workspace.

**Assumed workspace state:**
- `journal/` exists but `journal/JOURNAL.md` is missing.

**Must do:**
- Run `python -m skore_skills scaffold --journal` as the
  initialization command.
- State that the packaged index provides Status, Data understanding,
  Modeling decisions, History, Ideas, and Backlog.
- Return to triage after initialization.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Paste a `JOURNAL.md` body, a markdown fence of that file, or
  History/Backlog tables reconstructed from memory.
- Draft or implement an experiment in this turn.

---

## CASE_04 — Site on rebuilds after backlog

**User prompt:**
> The 01_baseline run finished. Record it.

**Assumed workspace state:**
- Audit digest exists with a headline ROC-AUC.
- Smoke tests passed.
- History row for `01_baseline` is `running`.
- `policy.site` is true.
- `export-ml-site` is installed.
- The user asked directly. This is not a dispatch from
  `model-ml-pipeline`, `evaluate-ml-pipeline`, or
  `audit-ml-pipeline`.

**Must do:**
- Copy the headline result into the History row.
- Run `python -m skore_skills site build --if-stale` before git
  end-turn.
- Run `python -m skore_skills git end-turn --stage backlog`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Fail the backlog turn if site build errors.
- Run `notebook convert`.
- Run `git commit` in this skill or `git push`.

---

## CASE_05 — Model-entry mode consumes one CLI row

**User prompt:**
> I picked “Pick from the Backlog” in the model menu.

**Assumed workspace state:**
- `model choices` returned B1 and B4 in that order.
- B1 Item is “try robust scaling”, Source is `user`.
- B4 Item is “inspect residual seasonality”, Source is
  `audit:02_baseline:checks.SKD003`.

**Must do:**
- Present exactly B1 and B4 and ask for one pick.
- After a pick, ask only for a shaping fact the row does not state.
- Remove only the selected row after the model stage creates its
  design note.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Ask Yes / No on the proposal.
- Invent B2/B3 or renumber B4.
- Invent a Method from the one-line item.
- Require an audit digest for this selection mode.
- Start pipeline implementation.

---

## CASE_06 — Record-outcome mode writes the journal and returns

**User prompt:**
> (dispatched by `audit-ml-pipeline` at end of turn, in
> record-outcome mode, with the digest in hand)

**Assumed workspace state:**
- Audit digest for `01_baseline` exists with a headline ROC-AUC.
- The digest contains `[Open report](https://hub.example/report/42)
  · hub · id: skore:report:cross-validation:42`.
- G-AUDIT-FINDING is
  `1 issue, 1 tip — SKD003 (issue), SKD010 (tip); ROC-AUC 0.86`.
- The digest has an extra `## ROC curve` cell from a `roc` Display,
  with `scratch/results/01_baseline/roc.html` beside it.
- Smoke tests passed.
- History row for `01_baseline` is `planned`.
- Backlog has rows `B1` and `B2`.

**Must do:**
- Run `python -m skore_skills status`.
- Flip the `01_baseline` History row to `done` and copy the
  headline result from the digest.
- Copy the locator byte-for-byte into the History `Report` cell
  and design-note `Persisted report` Status line.
- Copy G-AUDIT-FINDING byte-for-byte into the design-note
  `Audit findings` Status line, separately from Headline result.
- Insert `## Results` with Report overview, then Checks, then
  Metrics. Summarize Report overview and Checks from the digest,
  not from HTML. `### Metrics` is a heading only: do not transcribe
  the metric table or its values.
- After Metrics, add a `###` subsection for `roc` with
  `<!-- results-embed: roc -->`, summarizing from that digest cell.
- Copy Headline result, Persisted report, and Audit findings
  into the design-note Status block. Do not change `State` or
  `Approved by user on`.
- Refresh the `JOURNAL.md` Status rows `Last experiment` and
  `Last result`.
- Return to the caller after recording.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Paste the metrics table or its values under `### Metrics`.
- Rescan the Backlog or add/resolve `B1` / `B2` rows.
- Edit the Ideas table.
- Ask the idea-triage question.
- Dispatch `audit-ml-pipeline`. Naming the caller when returning
  is not dispatching it.
- Run `site build` or `git end-turn --stage backlog` — the caller
  owns the close.
- Rewrite or shorten the supplied Hub URL. Pasting the digest
  string unchanged is required, not a violation.
- Merge the audit finding into the headline metric or Last result.
  Copying the supplied G-AUDIT-FINDING unchanged, including the
  `ROC-AUC 0.86` already inside that string, is required.
- Change design-note `State` or `Approved by user on`.
- Parse `scratch/results/` HTML when writing `## Results`.
- Invent extra Display subsections without a matching digest cell.

---

## CASE_07 — Record-outcome mode never invents a metric

**User prompt:**
> (dispatched by `evaluate-ml-pipeline` at end of turn, in
> record-outcome mode)

**Assumed workspace state:**
- `audit-ml-pipeline` is not installed, so there is no digest.
- The user gave no headline value.
- G-AUDIT-FINDING is `n/a — audit not run`.
- History row for `03_calendar` is `planned`.

**Must do:**
- Skip the headline result in one line, naming the missing digest.
- Leave the History row status unchanged.
- Copy `n/a — audit not run` into the design note's Audit findings
  line if the Status block is updated.
- If writing `## Results`, include Report overview only when
  `scratch/results/03_calendar/report.txt` exists. Do not invent
  Checks or Metrics subsections.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Invent or estimate a metric.
- Mark the row `done` without a result.
- Change design-note `State` or `Approved by user on`.
- Edit the Ideas table.
- Ask the idea-triage question.
- Parse report HTML to fill Results.

---

## CASE_08 — Missing backend locator is explicit

**User prompt:**
> (record-outcome mode with a valid headline but no persisted
> report locator in the digest)

**Assumed workspace state:**
- Smoke passed and the digest has a headline metric.
- The backend did not emit a URL or locator.

**Must do:**
- Record `n/a — backend did not expose a locator` in both the
  History `Report` cell and design-note `Persisted report` line.
- Continue recording the valid headline result.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Guess a Hub, MLflow, or local artifact URL.
- Omit the Report cell from the History row.

---

## CASE_09 — Empty idea folder does not invent a row

**User prompt:**
> What should we try next?

**Assumed workspace state:**
- `journal/ideas/` exists and is empty.
- The Backlog table has no rows.
- `status.skills.shape-user-idea` is `true`.
- `status.skills.search-ml-literature` is `true`.

**Must do:**
- Skip in one line because there are no idea files to triage.
- When `shape-user-idea` and `search-ml-literature` are installed,
  offer those as the way to add an idea. Do not load them until
  the user picks one.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Fabricate a `B1` row.
- Invent an Ideas row.
- Write a design note.
- Start a literature search or a shaping questionnaire. Offering
  to shape an idea or search the literature, without loading
  either skill, is required.

---

## CASE_10 — Discard keeps the file and adds no row

**User prompt:**
> What should we try next?

**Assumed workspace state:**
- `journal/ideas/01_baseline-calibration.md` exists.
- Its `Triage` line is missing, so it is open.
- Its Source is `audit:01_baseline:checks.SKD003`.
- That Question and Source are not already a Backlog row.
- The Ideas table has that Question with Status `open`.
- The highest Backlog index is `B2`.
- The user answers discard.

**Must do:**
- Set `Triage: discarded` on
  `journal/ideas/01_baseline-calibration.md`.
- Set that Ideas row's Status to `discarded` and keep the row.
- Keep that file.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Append a Backlog row.
- Remove that Ideas row.
- Delete the idea file.
- Write a design note.

---

## CASE_11 — Set aside keeps the file and adds no row

**User prompt:**
> What should we try next?

**Assumed workspace state:**
- `journal/ideas/01_baseline-calibration.md` exists.
- Its `Triage` line is `open`.
- Its Source is `audit:01_baseline:checks.SKD003`.
- That Question and Source are not already a Backlog row.
- The Ideas table has that Question with Status `open`.
- The highest Backlog index is `B2`.
- The user answers set aside.

**Must do:**
- Set `Triage: aside` on
  `journal/ideas/01_baseline-calibration.md`.
- Set that Ideas row's Status to `aside` and keep the row.
- Keep that file.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Append a Backlog row.
- Remove that Ideas row.
- Delete the idea file.
- Write a design note.

---

## CASE_12 — Already-backlogged Source is marked promoted

**User prompt:**
> What should we try next?

**Assumed workspace state:**
- `journal/ideas/01_baseline-calibration.md` exists.
- Its `Triage` line is missing, so it is open.
- Its Question is the Item of Backlog row `B2`.
- Its Source is `audit:01_baseline:checks.SKD003`.
- That Question and Source are already Backlog row `B2`.
- The Ideas table has that Question with Status `open`.

**Must do:**
- Set `Triage: promoted` on
  `journal/ideas/01_baseline-calibration.md`.
- Remove that Ideas row.
- Keep that file.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Ask promote / discard / set aside for this file.
- Append another Backlog row.
- Delete the idea file.

---

## CASE_13 — Default pass skips a discarded file

**User prompt:**
> What should we try next?

**Assumed workspace state:**
- `journal/ideas/01_baseline-calibration.md` has `Triage: discarded`.
- `journal/ideas/monotonic.md` has `Triage: open`.
- Neither Source is already a Backlog row.
- The user has not answered yet.

**Must do:**
- Ask promote / discard / set aside only for
  `journal/ideas/monotonic.md`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Ask that question for `journal/ideas/01_baseline-calibration.md`.
- Delete either idea file.
- Append a Backlog row before the user answers.

---

## CASE_14 — Revisiting a discarded idea can promote it

**User prompt:**
> Look again at the discarded calibration idea and promote it.

**Assumed workspace state:**
- `journal/ideas/01_baseline-calibration.md` has `Triage: discarded`.
- No idea file is `open`.
- Its Source is `audit:01_baseline:checks.SKD003`.
- That Question and Source are not already a Backlog row.
- The Ideas table has that Question with Status `discarded`.
- The highest Backlog index is `B2`.

**Must do:**
- Set `Triage: promoted` on
  `journal/ideas/01_baseline-calibration.md`.
- Remove that Ideas row.
- Keep that file.
- Append a stable `B3` row. Item comes from the file's Question.
  Source is copied verbatim.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Delete the idea file.
- Leave `Triage` as `discarded`.
- Renumber `B1` or `B2`.

---

## CASE_15 — No open ideas names the tagged counts

**User prompt:**
> What should we try next?

**Assumed workspace state:**
- `journal/ideas/01_baseline-calibration.md` has `Triage: promoted`.
- That promoted idea has no Ideas row.
- `journal/ideas/monotonic.md` has `Triage: discarded`.
- `journal/ideas/split.md` has `Triage: aside`.
- Those discarded and aside rows remain in Ideas.
- No idea file is `open`.
- The user has not picked a file to revisit.

**Must do:**
- Say in one line how many ideas are promoted, discarded, and
  set aside.
- Offer to revisit. Do not retag until the user picks a file.
- Leave the discarded and aside Ideas rows in place.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Ask promote / discard / set aside before the user picks a file.
- Delete any idea file.
- Append a Backlog row.

---

## CASE_16 — A stated shaping fact returns the proposal

**User prompt:**
> B1, try robust scaling. Apply it to the numeric columns.

**Assumed workspace state:**
- Model-entry selection mode.
- B1 Item is "try robust scaling", Source is `user`.
- The missing shaping fact is already in the prompt: numeric
  columns.

**Must do:**
- Return that proposal to `model-ml-pipeline`.
- Keep the method to the item plus the numeric columns.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Ask Yes / No on the proposal.
- Ask which columns again.
- Invent a Method beyond the item and the stated columns.
- Start pipeline implementation.
