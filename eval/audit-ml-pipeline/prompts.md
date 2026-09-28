# audit-ml-pipeline eval

---

## CASE_01 — Audit is read-only and returns a digest

**User prompt:**
> Audit experiment 02 after evaluation.

**Assumed workspace state:**
- The design is approved, smoke is green, and the persisted report exists.
- `review consent` returns `ask`. The user has not answered yet.

**Must do:**
- Run `python -m skore_skills review consent --stem <stem>` before
  the first `cells run`.
- On `ask`, give a 1–3 sentence preview: local read of the
  persisted report, every skore check, writes `audit/<stem>.py`
  and `scratch/audit/<stem>/audit.md`, can be slow. Do not invent
  minutes. Ask Review / Skip / Stop. Do not `cells run` until
  Review.
- After Review, confirm the report with `project.summarize()` and
  load it with `project.get(id)`.
- Render checks and metrics into the audit digest.
- Write `scratch/results/<stem>/{report,checks,metrics}.html`; leave
  the bare Display last on checks and metrics, with no text snapshot.
- Print a `help()` tree per namespace for the Additional report view
  menu.
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

---

## CASE_02 — Direct audit owns the close

**User prompt:**
> Re-audit experiment 03.

**Assumed workspace state:**
- This is a direct free-text invocation.
- The report exists and smoke is green.

**Must do:**
- Ask the review gate again before `cells run`, because a re-audit
  re-runs the checks.
- Run `python -m skore_skills loop artifacts --stem 03_*`
  (`record` expected) and `loop locator --stem 03_*`.
- Write 2–6 sentences from Checks + Metrics in the digest and
  link `journal/03_*.md`.
- Surface JSON `locator` verbatim (first among tokens, after the
  narrative) and G-AUDIT-FINDING verbatim.
- Run audit, then call `manage-ml-backlog` record-outcome with the
  digest and locator.
- Build the site only after record-outcome when enabled.
- Close with `git end-turn --stage evaluate`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Paste `scratch/audit/<stem>/audit.md` wholesale into chat.
- Open idea triage from record-outcome mode.
- Call record-outcome before audit.
- Run `git commit`.

---

## CASE_03 — Dispatched audit returns without a second close

**User prompt:**
> Continue the model loop and audit the evaluated baseline.

**Assumed workspace state:**
- `model-ml-pipeline` dispatched `review-ml-experiment`, which
  loaded this audit.
- `cells run` already produced the digest.
- The user picked Close audit at the post-audit gate.
- Normalized locator is
  `local workspace: [reports/](../reports/) · id: local-report-id`.

**Must do:**
- Return the digest, G-AUDIT-FINDING from `audit finding`, locator
  from `loop locator`, and optional headline to
  `model-ml-pipeline`.
- State that the dispatcher owns record-outcome, site, and git close.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Write the User-facing close (narrative + Open these) here;
  the dispatcher owns it.
- Run `git end-turn` or `persist-ml-git` from this skill (naming
  them as the **dispatcher's** close is allowed).
- Load `triage-ml-task` from this skill.
- Dispatch `manage-ml-backlog` from this skill.

---

## CASE_04 — Missing report stops without fabrication

**User prompt:**
> Audit experiment 04.

**Assumed workspace state:**
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
- The initial audit digest exists, including a `help()` tree per
  namespace.
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
  `## Core audit complete` on the same `audit/<stem>.py`, write
  `scratch/results/<stem>/<slug>.html`, leave the bare Display last,
  run style + cells run, and overwrite the digest.
- Recompute G-AUDIT-FINDING with `audit finding --stem <stem>` and
  present the same gate again.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Guess an accessor or show unavailable disabled choices.
- Convert notebooks, build the site, run git end-turn,
  record-outcome, or return to the dispatcher before Close audit.
- Call `evaluate` or `put`.
- Name ROC / confusion_matrix / permutation_importance from docs
  memory when they are absent from this turn's `help()` trees.
