# audit-ml-pipeline eval

---

## CASE_01 — Audit is read-only and returns a digest

**User prompt:**
> Audit experiment 02 after evaluation.

**Assumed workspace state:**
- `status.setup.pending` is empty.
- The design is approved, smoke is green, and the persisted report exists.
- `review consent` returns `audit`.

**Must do:**
- Run `python -m skore_skills review consent --stem <stem>` before
  the first `cells run`.
- On `audit`, write `audit/<stem>.py` and `cells run`.
- Confirm the report with `project.summarize()` and load it with
  `project.get(id)`.
- Render checks and metrics into the audit digest.
- Copy `templates/viewers.py` to `scratch/audit/<stem>/viewers.py`
  and run it. It writes
  `scratch/results/<stem>/{report,checks,metrics}.html`. Leave
  the bare Display last on checks in `audit/<stem>.py`. Metrics
  last is `summarize().frame(verbose_name=True, flat_index=False)`,
  and `metrics.html` is that frame's `_repr_html_()`. No second
  text snapshot of the table.
- Write a `help()` tree per namespace to
  `scratch/audit/<stem>/accessors.txt` for the Additional report
  view menu. Do not put that loop in the audit notebook.
- Derive G-AUDIT-FINDING by running
  `python -m skore_skills audit finding --stem <stem>` and pasting
  JSON `finding` verbatim.
- Ask Additional report view / Custom query / Custom plot / Close
  audit in that order; return the digest, JSON `finding`, and
  `loop locator` JSON only after Close audit.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Describe audit as model training or full CV.
- Call `skore.evaluate` or `project.put`.
- Require the experiment to be `done` before audit.
- Dispatch record-outcome before producing the digest.
- Write the journal directly.
- Write skill ids, `skore_skills`, `cells run`, or API-tutorial
  prose (version floors, `summarize(ignore=…)`, hub locator
  recipes) into `audit/<stem>.py` markdown cells or `#` comments.
- Put snapshot `write_text` calls or the `help()` loop in
  `audit/<stem>.py`. Those belong in
  `scratch/audit/<stem>/viewers.py`.

---

## CASE_02 — Direct audit owns the close

**User prompt:**
> Re-audit experiment 03.

**Assumed workspace state:**
- `status.setup.pending` is empty.
- This is a direct free-text invocation.
- The report exists and smoke is green.

**Must do:**
- Run `cells run` for the re-audit.
- Do not run the direct close before Close audit.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Paste `scratch/audit/<stem>/audit.md` wholesale into chat.
- Run `loop notebooks` before Close audit.
- Call record-outcome before Close audit.
- Run `git commit`.

---

## CASE_03 — Dispatched audit returns without a second close

**User prompt:**
> Continue the model loop and audit the evaluated baseline.

**Assumed workspace state:**
- `status.setup.pending` is empty.
- `model-ml-pipeline` dispatched `review-ml-experiment`, which
  loaded this audit.
- `cells run` already produced the digest.
- The user picked Close audit at the post-audit gate.
- Normalized locator is
  `local workspace: [reports/](../reports/) · id: local-report-id`.

**Must do:**
- Return to `model-ml-pipeline`. Naming `audit finding` and
  `loop locator`, plus the digest path, counts when the digest
  body is not in the prompt. Do not invent Checks or Metrics.
- State that the dispatcher owns record-outcome, the notebook
  gate, site, and git close.
- Tell the caller to run `python -m skore_skills loop notebooks
  --stem <stem>` and obey `convert` before record-outcome, then
  the caller's `git end-turn` (`--stage implement` from model,
  `--stage evaluate` from evaluate). Naming `notebook convert`
  is not that close.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Write the User-facing close (narrative + Open these) here;
  the dispatcher owns it.
- Run `git end-turn` or `persist-ml-git` from this skill (naming
  them as the **dispatcher's** close is allowed).
- Load `triage-ml-task` from this skill.
- Dispatch `manage-ml-backlog` from this skill.
- Run `loop notebooks` or `notebook convert` here.
- Treat naming `notebook convert` as finishing the close.
- Treat the close as finished after converting only
  `audit/<stem>.py`.
- Add `<!-- results-embed: audit -->`.

---

## CASE_04 — Missing report stops without fabrication

**User prompt:**
> Audit experiment 04.

**Assumed workspace state:**
- `status.setup.pending` is empty.
- The design is approved and smoke is green.
- `project.summarize()` has no row for experiment 04.

**Must do:**
- Stop and report that the persisted report is missing.
- Route recovery to evaluation.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Re-run `skore.evaluate` from audit.
- Invent a report id, URL, metrics, or digest.
- Mark the experiment done.

---

## CASE_05 — Additional audit work loops before close

**User prompt:**
> Add another audit view before we close.

**Assumed workspace state:**
- `status.setup.pending` is empty.
- The initial audit digest exists. `help()` trees are in
  `scratch/audit/<stem>/accessors.txt`, not in the notebook.
- A tree's `Displays` group lists one extra view; `api get` confirms
  that method.

**Must do:**
- Refresh the execution preview for the selected view because it
  materially changes report rendering; do not repeat it before
  every style / cells command.
- Present Additional report view / Custom query / Custom plot /
  Close audit in that exact order.
- Offer only accessor names from this turn's `Displays` groups — not
  a remembered Display catalog.
- Confirm the selected accessor with `api get`, append it below
  `## Core audit complete` on the same `audit/<stem>.py` as a bare
  Display, write `scratch/results/<stem>/<slug>.html` from
  `viewers.py` only, run style + cells run, re-run `viewers.py`,
  and overwrite the digest.
- Recompute G-AUDIT-FINDING with `audit finding --stem <stem>` and
  present the same gate again.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Guess an accessor or show unavailable disabled choices.
- Convert notebooks, build the site, run git end-turn,
  record-outcome, or return to the dispatcher before Close audit.
- Call `evaluate` or `put`.
- Name ROC / confusion_matrix / permutation_importance from docs
  memory when they are absent from this turn's `accessors.txt`
  trees.
- Put the extra-view `write_text` in `audit/<stem>.py`.

---

## CASE_06 — Fired-check advice follows its docs

**User prompt:**
> What should we do about this check?

**Assumed workspace state:**
- The audit digest exists.
- One `Issues:` line is `SKD004`, with a documentation URL.
- That page recommends tuning the decision threshold. It does not
  recommend class weighting or resampling.

**Must do:**
- Read that documentation URL and apply its recommendation:
  tune the decision threshold.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Recommend class weighting or resampling.
- Call `skore.evaluate` or `project.put`.
