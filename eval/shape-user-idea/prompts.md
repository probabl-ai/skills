# shape-user-idea eval

---

## CASE_01 — Confirmed idea writes one file

**User prompt:**
> I want to try a monotonic constraint on the target.

**Assumed workspace state:**
- The last History stem is `01_baseline`.
- The user already stated the idea, so the free-text / artifact
  menu is skipped.
- The user answers the three shaping questions, then says yes.

**Must do:**
- Walk what to learn, why now, and what changes.
- Restate the idea and wait for an explicit yes before writing.
- On yes, write `journal/ideas/<slug>.md` with Source `user`,
  Experiment `01_baseline`, Question, Why now, What changes, and
  Open gaps.
- Return that path.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Write the file before yes.
- Write `JOURNAL.md` or a design note.
- Append a `B<N>` row.
- Add acceptance criteria.

---

## CASE_02 — A project question writes no idea file

**User prompt:**
> What was the headline of the last run?

**Assumed workspace state:**
- History has one done row. The headline cell is `0.81`.

**Must do:**
- Answer from `JOURNAL.md`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Write `journal/ideas/`.
- Invent a metric that is not in History.

---

## CASE_03 — A topic with no artifact loads literature search

**User prompt:**
> What do people do for censored regression?

**Assumed workspace state:**
- No URL, issue, or file was named.
- `status.skills.search-ml-literature` is `true`.

**Must do:**
- Load `search-ml-literature`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- `WebSearch` for a paper from this skill.
- Write an idea file in this skill.
- Invent papers or URLs.
