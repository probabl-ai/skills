# explore-ml-data eval

---

## CASE_01 — End of turn uses git hook

**User prompt:**
> EDA is done. Close the turn.

**Assumed workspace state:**
- `data_analysis/data_analysis.md` was just written.

**Must do:**
- Write 2–6 sentences of EDA findings (shape / target /
  leakage or duplicates that shape modelling).
- Link `data_analysis/data_analysis.md`.
- Run `python -m skore_skills git end-turn --stage data_analysis`.
- If that command returns `invoke`, load `persist-ml-git`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Paste the full `data_analysis.md` into chat.
- Run `git commit` in this skill.
- Run `git push`.

---

## CASE_02 — G-TABULAR before first EDA script

**User prompt:**
> Explore the dataset before we design a model.

**Assumed workspace state:**
- Scaffold exists (`has_src`, `journal/JOURNAL.md`).
- Raw data path is known.
- `policy.tabular` is unset.
- `choose-python-library` and `add-python-package` are installed.

**Must do:**
- Read `status.policy.tabular` and ask pandas vs polars
  (recommend pandas) via `choose-python-library` or ask here if
  that skill is missing.
- Persist `policy set tabular` after confirmation.
- Load `add-python-package` for the chosen frame library,
  `skrub`, `matplotlib`, and `seaborn`.
- Do not place `data_analysis/data_analysis.py` before the library
  choice is confirmed.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Silent-default pandas and write `data_analysis.py` first.
- Install sklearn, skore, or pytest in this turn.
- Call `env add` from this skill instead of `add-python-package`.

---

## CASE_03 — Skip G-DATA-ANALYSIS

**User prompt:**
> Skip the EDA. I already know the data.

**Assumed workspace state:**
- Scaffold exists (`has_src`, `journal/JOURNAL.md`).
- `status.data_analysis` is `missing`.
- No `data_analysis/data_analysis.md`.

**Must do:**
- Record JOURNAL § Data understanding `Status: skipped` with a
  date.
- Stop without placing `data_analysis/data_analysis.py`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `python -m skore_skills cells run`.
- Write `data_analysis/data_analysis.py` or `data_analysis/data_analysis.md`.
- Pick a package name or start modeling.
- Run `python -m skore_skills site build`.

---

## CASE_04 — EDA already present, no refresh

**User prompt:**
> Explore the dataset.

**Assumed workspace state:**
- `data_analysis/data_analysis.md` exists.
- JOURNAL § Data understanding records `Status: done`.
- The user did not ask to re-run or refresh EDA.

**Must do:**
- Detect exploratory data analysis already recorded (`status.data_analysis` present).
- Say the written analysis stays and offer to run it again or
  keep it.
- Do not overwrite `data_analysis/data_analysis.py` or
  `data_analysis/data_analysis.md` until the user accepts a
  re-run.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Write a JOURNAL Data understanding Status of `skipped`.
- Re-run `cells run` or rewrite the report before the user
  accepts a re-run.
- Design a model in this skill.
- Treat a methodology concern (“is this leakage”) as this stop
  (see CASE_18).

---

## CASE_05 — Human notebook vs agent scratch

**User prompt:**
> Explore the dataset. Write the TableReport HTML next to the EDA
> script.

**Assumed workspace state:**
- Scaffold exists. G-TABULAR is `pandas`. Skrub, IPython,
  matplotlib, and seaborn are installed.
- JOURNAL names target `MedHouseVal` (regression).
- Raw data path is known.
- User chose **run** for G-DATA-ANALYSIS.

**Must do:**
- Before writing or running the notebook, give a 1–3 sentence
  preview: local full-table profiling plus duplicate / target /
  bivariate / leakage work; name the `data_analysis/` and
  `scratch/data_analysis/` outputs.
- Say timing depends on table size, family count, and requested
  plots; do not invent a minute estimate.
- Write `data_analysis/data_analysis_<slug>.html` (not under `data/`).
- End overview cells on `TableReport` (or the frame), not on a
  json/dict digest.
- Include duplicate, target-distribution, bivariate-vs-target, and
  leakage cells (not TableReport dtypes/histograms/associations).
- Embed or link that HTML from `data_analysis/data_analysis.md`.
- Embed every saved PNG/HTML from extras in Modelling
  implications, each with a sentence citing extras/JSON numbers.
- Put `TableReport.json()` under `scratch/data_analysis/<slug>.json`
  and extras under `scratch/data_analysis/extras.json`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Describe this EDA execution as model training or smoke testing.
- Put unique-ratio / column-dict / `report.json()` cells in
  `data_analysis/data_analysis.py`.
- Write HTML under `data/`.
- Modify the user's raw data files.
- Train/test split or install sklearn unless extras were requested.
- Leave a saved figure unembedded in `data_analysis.md`.

---

## CASE_06 — Missing IPython delegates to add-python-package

**User prompt:**
> Run the EDA now.

**Assumed workspace state:**
- Scaffold exists. User chose **run**.
- `ipython` is not importable in the project env.
- `add-python-package` is installed.

**Must do:**
- Load `add-python-package` for `ipython` (`env route` agent
  scope). Do not place a fabricated digest.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `pixi add ipython` / `uv add ipython` from this skill.
- Hand-write expected exploratory data analysis output.

---

## CASE_07 — Notebook and site on after EDA

**User prompt:**
> EDA is done. Close the turn.

**Assumed workspace state:**
- `data_analysis/data_analysis.md` was just written.
- `policy.notebooks` is true. `policy.site` is true.
- `export-ml-notebook` and `export-ml-site` are installed.
- `jupytext`, `nbclient`, and `nbconvert` are installed.

**Must do:**
- Write 2–6 sentences of EDA findings.
- Name `report.html` and `html/data_analysis.html` in the
  user-facing close. Do not send the user to
  `data_analysis/data_analysis.md` instead.
- Run `python -m skore_skills notebook convert
  data_analysis/data_analysis.py --html` before site build.
- Run `python -m skore_skills site build` before git end-turn.
- Run `python -m skore_skills git end-turn --stage data_analysis`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Paste the full `data_analysis.md` into chat.
- Fail the data-analysis turn if site build errors; name the error.
- Run `cells run` as a substitute for convert.
- Run `git commit` in this skill.

---

## CASE_08 — Site off skips rebuild

**User prompt:**
> EDA is done. Close the turn.

**Assumed workspace state:**
- `data_analysis/data_analysis.md` was just written.
- `policy.site` is false.

**Must do:**
- Write 2–6 sentences of EDA findings and link
  `data_analysis/data_analysis.md`.
- Skip site build in one line.
- Run `python -m skore_skills git end-turn --stage data_analysis`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Name `report.html` or `html/data_analysis.html` as if the
  site was built.
- Run `python -m skore_skills site build`.

---

## CASE_09 — Notebooks on, site off converts without HTML

**User prompt:**
> EDA is done. Close the turn.

**Assumed workspace state:**
- `data_analysis/data_analysis.md` was just written.
- `policy.notebooks` is true. `policy.site` is false.
- `export-ml-notebook` is installed.
- `jupytext` and `nbclient` are installed.

**Must do:**
- Run `python -m skore_skills notebook convert
  data_analysis/data_analysis.py`.
- Run `python -m skore_skills git end-turn --stage data_analysis`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Pass `--html` when the site gate is off.
- Run `python -m skore_skills site build`.

---

## CASE_10 — Missing convert toolchain skips in one line

**User prompt:**
> EDA is done. Close the turn.

**Assumed workspace state:**
- `data_analysis/data_analysis.md` was just written.
- `policy.notebooks` is true. `policy.site` is false.
- `export-ml-notebook` is installed.
- `jupytext` and `nbclient` are not importable; `notebook convert`
  fails with that ImportError.

**Must do:**
- Skip the convert in one line, naming `add-python-package` for
  `jupytext` and `nbclient`.
- Run `python -m skore_skills git end-turn --stage data_analysis`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Fail the data-analysis turn because convert failed.
- Run `pixi add` / `uv add` from this skill.

---

## CASE_11 — Default run adds ML-gap cells

**User prompt:**
> Explore the California housing CSV. Target is MedHouseVal.

**Assumed workspace state:**
- Scaffold exists. G-TABULAR is `pandas`.
- `add-python-package` is installed.
- User chose **run** for G-DATA-ANALYSIS.
- IPython is available.

**Must do:**
- Load `plot-ml-figure` if installed before writing figure cells.
- Load `add-python-package` for `matplotlib` and `seaborn` (and
  skrub / pandas if missing).
- Write duplicate, target-distribution, bivariate-vs-target, and
  leakage cells in `data_analysis/data_analysis.py` for
  **regression only**.
- Use seaborn figure-level plots (`displot` / `relplot`); save
  PNGs and leave figures as cell output. Feature-vs-target is
  one faceted `relplot` (`bivariate_grid.png`), last expression
  `g`.
- After `data_analysis.md`, AskUserQuestion keep exploring vs
  close (neither option recommended or preselected).

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Re-plot TableReport univariate histograms or the association
  matrix in extra cells.
- Add a **second** target histogram / extra `displot` besides
  the one regression snippet. Copying
  `templates/target_regression.py` into
  `data_analysis/data_analysis.py` (that file's `displot`) is
  required, not a violation.
- Install sklearn, skore, pytest, or plotly on the default path.
- Train/test split the raw table.
- Run `git end-turn` before the user picks Close.
- Leave classification / no-target branches (`if TASK`,
  `if TARGET is None`) in the notebook.
- Write skill ids, `skore_skills`, `cells run`, or "generated from
  …" process notes into `data_analysis/data_analysis.py` /
  `data_analysis.md` markdown or `#` comments.
- Call `plt.close` or `import matplotlib.pyplot` for these
  figures.
- Loop over columns with a trailing `g` (that is not displayed).
- AskUserQuestion grouping when only one data file is in play.

---

## CASE_12 — Unspecified target asks, does not guess

**User prompt:**
> Explore the dataset.

**Assumed workspace state:**
- Scaffold exists. User chose **run**.
- JOURNAL Goal does not name a column.
- Column names are `A`, `B`, `C`.

**Must do:**
- AskUserQuestion for the target (column list plus "no target
  yet") before writing target-aware cells.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Guess a target column silently.
- Skip the duplicate-row cell when the user picks "no target yet".
- Write target-distribution / bivariate / leakage cells when the
  user picks "no target yet".

---

## CASE_13 — Prompt already asked for PCA

**User prompt:**
> Explore the data and add a PCA plot of the numeric columns.

**Assumed workspace state:**
- Scaffold exists. User chose **run**. Target is known.
- `add-python-package` is installed.

**Must do:**
- Load `add-python-package` for `scikit-learn`.
- Append a PCA cell from `references/extra_analyses.md`.
- Do not re-ask PCA on the pre-defined-option board.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Treat PCA as a pipeline preprocessor in this skill.
- Run `pixi add scikit-learn` from this skill.

---

## CASE_14 — Close after default pass keeps sklearn off

**User prompt:**
> Explore the dataset. Target is MedHouseVal.

**Assumed workspace state:**
- Default notebook, extras.json, and `data_analysis.md` are on
  disk.
- User picks **Close** on keep-exploring vs close.

**Must do:**
- AskUserQuestion keep exploring vs close (neither option
  recommended or preselected).
- After Close, write 2–6 sentences of findings and link
  `data_analysis/data_analysis.md`.
- Run `python -m skore_skills git end-turn --stage data_analysis`
  after Close.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Paste the full `data_analysis.md` into chat.
- Load `add-python-package` for sklearn / scipy / statsmodels.

---

## CASE_15 — Keep exploring does not end the turn

**User prompt:**
> Explore the dataset. Target is MedHouseVal.

**Assumed workspace state:**
- `data_analysis/data_analysis.md` was just written.
- `policy.site` is true.
- `export-ml-site` is installed.
- User picks **Keep exploring the data**.

**Must do:**
- Run `python -m skore_skills site build` after the md and
  before keep exploring vs close.
- Name `report.html` and `html/data_analysis.html`.
- After **Keep exploring**, AskUserQuestion four picks, none
  recommended: Choose additional pre-defined option; Provide a
  query to extend the exploration; Automatic exploration related
  to the data and problem; Describe a plot.
- Stay in `explore-ml-data`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `python -m skore_skills git end-turn`.
- Invent a domain-specific checklist skill or `references/domains/`.
- Run `python -m skore_skills site build` again on the four-pick
  extras board.
- Run `notebook convert` before Close.
- Say “extra-analyses” or “standard extra analysis” on that
  board.

---

## CASE_16 — Keep exploring then research

**User prompt:**
> Is 0.97 correlation with the target leakage?

**Assumed workspace state:**
- EDA markdown exists. User picked Keep exploring, then
  Automatic exploration related to the data and problem. The
  prompt already names a leakage concern.
- `status.skills.research-ml-practice` is true.

**Must do:**
- Preview Automatic exploration as LLM research over the recorded
  EDA that may write a scratch note, with no model fitting or
  testing before the measurement-choice board.
- Load `research-ml-practice` with the named leakage concern
  (skip the canned extra-analysis survey).
- Summarize the scratch note in chat (what is happening + why
  it matters here).
- AskUserQuestion `allow_multiple` on `measure` rows only.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Drop the correlated column from the raw data.
- Run `git end-turn` in this keep-exploring pass.
- Copy literature into modelling implications as if it were
  measured.
- Append a `declare` or `evaluate` row as an EDA cell.

---

## CASE_17 — Research skill missing is a one-line skip

**User prompt:**
> Is 0.97 correlation with the target leakage?

**Assumed workspace state:**
- EDA markdown exists. User picked Keep exploring, then Research
  this concern.
- `status.skills.research-ml-practice` is false or absent.

**Must do:**
- One-line skip that `research-ml-practice` is not installed.
- Stay in the keep-exploring menu (re-ask the four human
  picks, or keep vs close). Do not say “extra-analyses” on
  that board.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Invent papers or leakage thresholds from memory.
- Run `git end-turn` in this keep-exploring pass.

---

## CASE_18 — Leakage question while EDA is already done

**User prompt:**
> Is 0.97 correlation with the target leakage?

**Assumed workspace state:**
- `data_analysis/data_analysis.md` exists.
- JOURNAL § Data understanding records `Status: done`.
- `status.data_analysis` is present.
- The user did not pick Keep exploring first.
- `status.skills.research-ml-practice` is true.

**Must do:**
- Do not overwrite `data_analysis/data_analysis.py`.
- Load `research-ml-practice` (Keep exploring § Automatic
  exploration; named concern — skip the canned extra-analysis
  survey).
- Summarize the scratch note in chat.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Stop as CASE_04 (EDA already recorded, no refresh).
- Run `git end-turn` in this pass.
- Re-run `cells run` or rewrite the default notebook.

---

## CASE_19 — No target omits target-aware cells

**User prompt:**
> Explore the dataset.

**Assumed workspace state:**
- Scaffold exists. User chose **run**.
- User picked **no target yet** on the target AskUserQuestion.
- `plot-ml-figure` is installed.

**Must do:**
- Write TableReport and duplicate-row cells.
- Omit `templates/target_regression.py` and
  `templates/target_classification.py`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Write `if TARGET is None` / `if TASK` branches for unused
  tasks.
- Call `plt.close`.

---

## CASE_20 — Automatic exploration uses the problem class

**User prompt:**
> Keep exploring. Research extra analyses for this table.

**Assumed workspace state:**
- `data_analysis/data_analysis.md` exists with Open questions.
- JOURNAL names California housing / MedHouseVal.
- User picked **Keep exploring**, then **Automatic exploration
  related to the data and problem**.
- `status.skills.research-ml-practice` is true.

**Must do:**
- Load `research-ml-practice` with the canned JOURNAL+EDA
  extra-measurement question (problem class, not the dataset
  proper name).
- Read `scratch/research/survey-<slug>.md`.
- AskUserQuestion `allow_multiple` (unchecked) on **only**
  sourced **`measure`** extras from that note.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Search `california_housing`, `sklearn.datasets`, or a
  sklearn fetcher name.
- Offer pipeline / learner / `GridSearch` extras on the EDA
  board.
- Copy Open questions onto the board without a source.
- Write a ranked pipeline action table in the survey note.
- Run `git end-turn` in this pass.
- Name `Close` as recommended on keep vs close.

---

## CASE_21 — Multiple files ask grouping before the notebook

**User prompt:**
> Explore the data. Target is y.

**Assumed workspace state:**
- Scaffold exists. G-TABULAR is `pandas`.
- User chose **run** for G-DATA-ANALYSIS.
- IPython is available. `add-python-package` is installed.
- Raw files: `data/a_1.csv`, `data/a_2.csv`, `data/b.parquet`.
- Families are not yet confirmed.

**Must do:**
- AskUserQuestion grouping (none recommended): Use a proposed
  grouping / Profile every file separately / I will describe
  the grouping — before placing `data_analysis/data_analysis.py`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Place `data_analysis/data_analysis.py` or concat shards on
  disk before the user answers the grouping ask. Do not treat
  `family_a` / `family_b` as confirmed until that pick. Proposing
  those slugs and an in-memory concat **inside** "Use the
  proposed grouping" is required, not a violation.
- Write a joined frame to disk.
- Append join-coverage cells on the default pass.

---

## CASE_22 — Two confirmed families, default pass

**User prompt:**
> Explore the data. Target is y.

**Assumed workspace state:**
- Scaffold exists. G-TABULAR is `pandas`.
- User chose **run** for G-DATA-ANALYSIS.
- IPython is available. `plot-ml-figure` is installed.
- Raw files: `data/a_1.csv`, `data/a_2.csv`, `data/b.parquet`.
- User confirmed families: `family_a` is `data/a_1.csv` and
  `data/a_2.csv` (columns `id`, `y`); `family_b` is
  `data/b.parquet` (columns `id`, `z`).

**Must do:**
- Write a TableReport cell and HTML per family
  (`data_analysis_family_a.html`, `data_analysis_family_b.html`).
- Embed one glance iframe per family in
  `data_analysis/data_analysis.md`.
- Put target-distribution, bivariate, and leakage cells only on
  `family_a`.
- Append `templates/drift.py` (shared column names).
- Write `scratch/data_analysis/family_a.json`,
  `scratch/data_analysis/family_b.json`, and `extras.json` with
  `tables[]`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Append join-coverage cells on the default pass.
- Install sklearn, skore, or pytest.
- Write a joined frame to disk.
- Put target/bivariate/leakage cells on `family_b`.

---

## CASE_23 — Keep exploring join keys / coverage

**User prompt:**
> Keep exploring. Add join keys / coverage.

**Assumed workspace state:**
- Two families are already in `data_analysis/data_analysis.py`
  (`family_a` with `id`, `y`; `family_b` with `id`, `z`).
- `data_analysis/data_analysis.md` exists.
- User picked **Keep exploring**, then **Choose additional
  pre-defined option**, then **Join keys / coverage**.

**Must do:**
- Append `templates/join_coverage.py` (shared columns and
  unmatched counts on `id`).
- Refresh facts and rewrite `data_analysis.md` from results.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Write a joined frame to disk.
- Replace `FRAME` with the merge or add a TableReport on the
  join.
- Run `git end-turn` in this keep-exploring pass.

---

## CASE_24 — Single file skips grouping

**User prompt:**
> Explore the data. Target is y.

**Assumed workspace state:**
- Scaffold exists. G-TABULAR is `pandas`.
- User chose **run** for G-DATA-ANALYSIS.
- IPython is available.
- One raw file: `data/a.csv` (columns `id`, `y`).

**Must do:**
- Write `data_analysis/data_analysis.py` without an AskUserQuestion
  grouping board.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- AskUserQuestion grouping (Use a proposed grouping / Profile
  every file separately / I will describe the grouping).
- Append join-coverage cells.

---

## CASE_25 — Site on rebuilds before keep vs close

**User prompt:**
> Explore the California housing CSV. Target is MedHouseVal.

**Assumed workspace state:**
- Scaffold exists. G-TABULAR is `pandas`.
- User chose **run** for G-DATA-ANALYSIS.
- IPython is available.
- `policy.site` is true.
- `export-ml-site` is installed.

**Must do:**
- After `data_analysis.md` and JOURNAL, name
  `python -m skore_skills site build`.
- Name `report.html` and `html/data_analysis.html`.
- Then AskUserQuestion keep exploring vs close (neither option
  recommended or preselected).

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `notebook convert` or `git end-turn` before the user picks
  Close.
- Fail the keep-vs-close gate if site build errors; name the
  error.

---

## CASE_26 — Present analysis cannot be marked skipped

**User prompt:**
> Skip the data analysis. We already wrote it.

**Assumed workspace state:**
- `data_analysis/data_analysis.md` exists.
- `status.data_analysis` is `present`.

**Must do:**
- Say the written analysis stays.
- Offer to run exploration again (overwrite
  `data_analysis/data_analysis.*`) or keep it.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Write a JOURNAL Data understanding Status of `skipped`.
- Overwrite `data_analysis/data_analysis.md` before the user
  accepts a re-run.
