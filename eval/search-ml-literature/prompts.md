# search-ml-literature eval

---

## CASE_01 — Show directions and do not pick a winner

**User prompt:**
> What do people do for censored regression?

**Assumed workspace state:**
- JOURNAL Status names a regression task.
- The dataset is loaded with `sklearn.datasets.fetch_openml`.

**Must do:**
- Rewrite the query as a problem class before searching. Do not
  search the loader or the dataset name.
- Fetch primary pages.
- Show two to four directions, each with a URL and the claim.
- Ask the user to pick one, narrow, or stop.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Load `research-ml-practice`.
- Rank a winner or say which direction to run next.
- Invent a paper, URL, or claim.
- Write `journal/ideas/` before the user picks and confirms.

---

## CASE_02 — Confirmed direction writes one idea file

**User prompt:**
> Yes, that one.

**Assumed workspace state:**
- The user picked one of the directions shown this turn.
- Its URL is `https://example.invalid/censored-models`.
- The last History stem is `01_baseline`.

**Must do:**
- Restate the direction and wait for yes. The user already said
  yes in this prompt, so write the file.
- Write `journal/ideas/<slug>.md` with Source
  `literature: https://example.invalid/censored-models` and
  Experiment `01_baseline`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Write `JOURNAL.md` or a design note.
- Append a `B<N>` row.
- Add a package.

---

## CASE_03 — Stop writes nothing

**User prompt:**
> Stop.

**Assumed workspace state:**
- Directions were shown. The user chose stop.

**Must do:**
- Return to the caller with no idea file.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Write `journal/ideas/`.
- Pick a direction anyway.
