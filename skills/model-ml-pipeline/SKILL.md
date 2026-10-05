---
name: model-ml-pipeline
description: >
  Deterministic entry point for modeling. On a generic landing,
  offer only the choices justified by the workspace (the locked
  baseline, an EDA proposal, Backlog, discussion). A missing
  modeling lock loads `frame-ml-problem` and stops.
  After a design is approved, coordinate build (pytest smoke is a
  build sub-step), the user's Evaluate (Recommended) / Modify /
  Stop gate, evaluation, and audit. Not for a single action
  already owned by evaluate, audit, or smoke debugging.
---

# Model ML Pipeline

This meta skill owns selection and ordering, not child methodology.
Do not load `smoke-test-ml-pipeline` as a sibling of evaluate.

## Human-facing prose

Details: `setup-workspace` `references/human_facing_prose.md`.
Design notes, JOURNAL text, and `#` comments describe **this**
experiment — not the skills framework, the CLI, or the command that
produced an output. Questions, replies, and the close narrative
use the same data-science language — not skill ids, `G-*` names,
or the wrapper CLI. Trailing locator tokens stay index strings.
`<!-- results-embed: … -->` is a site marker. Authoring hints
stay in this skill. `style` is ruff only.

## Design note shell

`python -m skore_skills scaffold --journal --stem <NN_short>` writes
`journal/<stem>.md`. Do not recreate it from memory. Fill Question,
Motivation, Method, and Risks as science (what to learn, why now,
what changes, what could invalidate the result). Status lifecycle:
`planned` → `approved` → `running` → `done` | `abandoned`. Those
four content sections freeze after approval; only Status, generated
notebook viewers, and the Method `<!-- results-embed: pipeline -->`
embed change afterwards. Abandoned: one-line reason on State;
Headline result `n/a — abandoned: <reason>`. There is no "Success
criteria" section. Keep `## Notebooks` with Evaluation then Audit.

## Entry routing — deterministic

1. Run `python -m skore_skills status`. If `status.setup.pending`
   is non-empty and `status.skills.setup-ml-project` is true,
   load `setup-ml-project` and stop. Do not start this skill.
   When it returns, continue. Do not load it again on this turn.
   If that skill is not installed, name the pending pieces in
   one line and stop. Do not invent `git init`, scaffold, or
   `env init`. If `status.setup.env` or `status.setup.workspace`
   is `declined`, stop in one line. A declined `git` or
   `editable` is not asked again and does not block modeling.
2. **Framing is mandatory.** If `status.modeling_decisions` is not
   `locked`, load `frame-ml-problem` only if
   `status.skills.frame-ml-problem` is true and stop. Do not invent
   the table, offer model choices, write a design note, or declare
   a pipeline. Missing skill → stop in one line. This includes an
   approved-stem resume: do not build until the table is locked.
   When the table is `locked`, run
   `python -m skore_skills frame show`. Anything other than
   `proceed` loads `frame-ml-problem` and stops. A `proceed` whose
   `translation` is null has no splitter translation: say so and
   stop. Do not write model code. Do not present a choice list:
   no dummy predictor, standard baseline, EDA-driven proposal,
   Backlog row, or discussion.
3. **Resume beats menu.** If the user names an experiment stem, or
   `status.policy.loop.stem` / `last_history_stem` identifies a
   current design, run
   `python -m skore_skills design consent --stem <stem>`. Treat
   JSON `action` as authoritative. `proceed` → resume that stem
   directly; do not ask how to start again. `ask` → Design
   approval below (render JSON `context` inline per § Gate
   context); do not write code. `stop` → missing
   note: name `scaffold --journal --stem` (or abandoned: explain
   and do not implement). Do not infer approval from "build it".
   Missing shell: no `site build`, no fill from memory.
4. Otherwise run `python -m skore_skills model choices`. Treat its
   JSON as authoritative.
   - `action` `stop` / `modeling_decisions_unlocked` — load
     `frame-ml-problem` and stop. Do not offer a model menu.
   - Otherwise present exactly `choices[]`, in returned order, in
     one single-choice **AskUserQuestion**:
     - `baseline` → **Build the locked baseline**
     - `eda_proposal` → **Propose a pipeline from the EDA**
     - `backlog` → **Pick from the Backlog**
     - `discuss` → **Discuss the next step**

   Carry each choice's JSON `reason` as its description so the user
   reads why it is on offer.

Do not add a disabled choice, infer availability yourself, or
reorder the list. In particular: no locked-baseline choice when
`model_stems` is non-empty; no EDA proposal unless
`data_analysis` is `present`; no Backlog option when `backlog` is
empty. Discussion is present only after the lock.

## Gate context

Every approval question carries its own context. Before asking,
state in 2–4 lines what the answer authorizes, the facts it rests
on — echoed inline — and what each option does, in data-science
terms (Approve / Modify / Stop; dummy vs baseline). Do not name
skill ids or `G-*` tokens in the question. A file link is an
addition, never the context: "read `journal/<stem>.md` and
approve" is not an approval request.

On `design consent` `ask`, the JSON `context` holds those facts:
`question`, `source`, `files_touched`, `change`, and up to two
`risks`. Quote them in the message (question and planned change
first, then the risks the user may push back on). After the note
is populated, rebuild the site per `export-ml-site` § Preview
before markdown-review gates **before** asking **Approve** /
**Modify** / **Stop**. Link `note` next to them, not instead of
them. An empty field means the note does not state that fact: say
the note is not ready for approval and offer to populate it;
never fill it from memory. Do not `site build` an empty shell.

## Choice contracts

Every choice first produces a user-confirmed proposal and an
approved design note. The proposal yes agrees the idea. The note
is approved only by Design approval below. No branch writes model
code before that gate is `proceed`. Use the next available numeric
stem; never overwrite an existing note.

- **Locked baseline (`baseline`).** The note names the one
  comparison model the journal already locked. A `dummy` token is a
  `DummyClassifier` or `DummyRegressor` inside the normal skrub
  DataOps declaration: it proves loading, fit/predict, and pytest
  smoke, and it is not expected to add predictive value. Any
  other token (`logistic`, `seasonal_naive`, `group_mean`,
  `production`) is that one comparison model. Do not upgrade it
  to another estimator. Restate the proposal, then one
  single-choice **AskUserQuestion**: **Yes** / **No**. Do not
  also ask for a typed yes. "Maybe" is not Yes. No or Stop
  writes nothing. A later Yes (the tool answer, or an explicit
  yes on a later turn) is what authorizes the write. On Yes,
  write the note, then Design approval, before build. Keep the
  normal post-smoke Evaluate (Recommended) / Modify / Stop gate.
- **EDA proposal (`eda_proposal`).** Read
  `data_analysis/data_analysis.md` and the project goal. Cite the
  EDA findings that motivate one pipeline proposal. Do not invent
  findings or present multiple silent alternatives. Restate the
  proposal, then one single-choice **AskUserQuestion**: **Yes** /
  **No**. Do not also ask for a typed yes. "Maybe" is not Yes.
  No or Stop writes nothing. A later Yes (the tool answer, or an
  explicit yes on a later turn) is what authorizes the write.
  On Yes, write the note, then Design approval, before build.
- **Backlog (`backlog`).** Load `manage-ml-backlog` only if
  `status.skills.manage-ml-backlog` is true. Else one-line skip;
  do not invent a Backlog. Pass the
  `backlog` rows returned by the CLI; ask the user to pick one
  `B<N>`, consume only that row into a proposal/design stem, then
  return here. Do not add a new Backlog idea in this branch.
- **Discussion (`discuss`).** Have an open conversation about what
  to learn, why now, and what changes. Restate the agreed idea,
  then one single-choice **AskUserQuestion**: **Yes** / **No**.
  Do not also ask for a typed yes. "Maybe" is not Yes. No or Stop
  writes nothing. A later Yes (the tool answer, or an explicit
  yes on a later turn) is what authorizes the write. Only after
  that confirmation create/populate the design note, then Design
  approval. If no idea is agreed, return to the entry choices.

## Before execution

This dispatcher labels the next kind of work but does not
duplicate a child's detailed preview.

- For `discuss`, proposal shaping, or literature-backed design
  work, emit 1–3 natural sentences saying this is **LLM
  discussion/research** over recorded project facts, with no
  model fit, smoke test, or CV. Name any scratch research note or
  design note that may be written and stop at confirmation.
- For an approved implementation, say which child comes next and
  the broad sequence: local pipeline preparation → small
  real-data smoke fit/predict → optional full-dataset evaluation
  → gated review. Then let `build-ml-pipeline`,
  `smoke-test-ml-pipeline`, `evaluate-ml-pipeline`, and
  `review-ml-experiment` each own the single detailed Before
  execution preview at its actual compute boundary. The dispatcher
  preview is those four phase names only, one short line each. Do
  not mention the Method viewer, a site rebuild, a row-count
  assertion, `skore.evaluate`, or Review / Skip / Stop. Do not list
  their commands (`status`, `frame show`, `design consent`,
  `smoke run`) or a DataOps declaration in this preview. With
  no shell, that four-phase paragraph is the whole answer.

Do not invent minute estimates at dispatcher level. Name a known
duration only when explicit measured evidence is available;
otherwise leave cost details to the child that knows data scope,
folds, and selected views. Pending proposal/design approval may
preview the sequence but never starts local work.

If the design-note shell is missing, this turn only names
`python -m skore_skills scaffold --journal --stem <NN_short>`
and stops. Do not fill Question / Motivation / Method / Risks
from memory. Populate those sections only after that command
has created the shell, then Design approval.

## Design approval

One gate approves a populated note. Run
`python -m skore_skills design consent --stem <stem>`.
`proceed` → already approved; do not ask again. `ask` → render
the JSON `context` inline (§ Gate context), including the site
preview when `policy.site`, then **AskUserQuestion** (single
choice), in order: **Approve** / **Modify** / **Stop**. Do not
also ask in chat whether the note looks right.
- **Approve** → set `**State:**` to `approved` and
  `**Approved by user on:**` to today's date (`YYYY-MM-DD`).
  Re-run `design consent`; code starts only on `proceed`.
- **Modify** → leave `State` `planned`, edit the note, and ask
  this gate again.
- **Stop** → do not implement.

## Approved-design implement loop

1. Load `build-ml-pipeline` only if `status.skills.build-ml-pipeline`
   is true; else one-line skip and stop — do not declare the
   pipeline from this meta. That skill loads `smoke-test-ml-pipeline`
   after the experiment file exists and runs
   `python -m skore_skills smoke run --stem <stem>`. JSON `stop`
   stays in build (modify the pipeline, re-run `smoke run`).
   Do not tell the user to edit the smoke test's expected row
   count so it matches the sample.
   `proceed`: build reports the
   design, then
   `python -m skore_skills evaluate consent --stem <stem>`
   (Evaluate / Modify / Stop on `ask`, with that JSON `context`
   rendered inline per § Gate context). Build also writes the
   unfitted Method viewer
   (`scratch/results/<stem>/pipeline/` when `DataOp.skb.report`
   accepts `eval`, otherwise `pipeline.html`) and, when
   `policy.site` is true and `export-ml-site` is installed, runs
   `site build` after that snapshot and before Evaluate so Method
   shows that report. Missing or skipped EDA does not defer it.
   The post-loop rebuild refreshes the same unevaluated report;
   it does not replace this one. Do not convert
   `experiments/<stem>.py` at this unfitted snapshot if it
   already contains `skore.evaluate`. That ban ends here. The
   close still converts the experiment script.
2. Only if the user chose **Evaluate** and `smoke run` is `proceed`: load
   `evaluate-ml-pipeline` only if `status.skills.evaluate-ml-pipeline`
   is true. It reuses the DataOp `cv` and writes
   `skore.evaluate` in the experiment script. Re-run `status`
   first, then `python -m skore_skills evaluate consent --stem
   <stem>`. Consent JSON is authoritative, not the user's wording
   alone. Missing `evaluate-ml-pipeline` → one-line skip. Do not
   invent that skill's steps.
3. After a successful dispatched evaluate (locator returned): run
   `python -m skore_skills review consent --stem <stem>`. Treat
   JSON `action` as authoritative.
   - `stop` — no `scratch/results/<stem>/report.html`. Do not
     review. Name that file. This is the evaluation snapshot, not
     the site launcher `report.html`. Do not record-outcome.
   - `ask` — the review skill owns the cost preview and
     Review (Recommended) / Skip / Stop question. Load
     `review-ml-experiment` only if
     `status.skills.review-ml-experiment` is true so it can ask.
     Missing skill → one-line skip and record-outcome with
     `n/a — audit not run`.
   - **Review** or `proceed` — load `review-ml-experiment` (same
     gate). It returns the digest, G-AUDIT-FINDING, locator, and
     idea paths. Do not load `audit-ml-pipeline` from this
     dispatcher.
   - **Skip** — no idea files. Record-outcome with
     `n/a — audit not run`.
   - **Stop** — do not record-outcome and do not audit. Return
     to triage when `status.skills.triage-ml-task` is true.
4. After **Review** or `proceed`, or after **Skip** / a missing
   review skill: load `manage-ml-backlog` only if
   `status.skills.manage-ml-backlog` is true, in **record-outcome
   mode**, handing it the locator, optional headline, and
   G-AUDIT-FINDING (`n/a — audit not run` when skipped). Else
   one-line skip; do not write History from this meta. It writes
   the `journal/JOURNAL.md` History row and design-note Status block plus
   `## Results`, then returns. It does not triage idea files in
   this mode. Never mark `done` while `smoke run` is `stop`.
   Missing headline becomes `n/a`, never an invented metric. Do
   not claim History remains `planned` because a child was not
   executed in-process.

Do not duplicate child-skill methodology. Before new library
symbols are written, children use
`python -m skore_skills api get <dotted>`.

## Stop conditions

- Pending setup (`status.setup.pending` non-empty): load
  `setup-ml-project` and do not start build. A declined `git`
  is not asked again. A declined env or workspace stops.
- Generic model landing: do not hand-author the menu; run
  `python -m skore_skills model choices`.
- If `journal/NN_<short>.md` is missing, this turn only names
  `python -m skore_skills scaffold --journal --stem
  <NN_short>` and stops. Do not recreate or fill the template
  from memory. Populate Question / Motivation / Method / Risks
  only after that command has created the shell, then Design
  approval. Do not `site build` before the shell exists.
- Require `design consent` `proceed` before code. Do not treat
  "the user asked to build", or a chat yes on the drafted note,
  as approval.
- Do not open an approval gate whose only context is a file path;
  render the `context` facts inline (§ Gate context).
- Preserve identical stems across design, experiment, smoke, audit.
- Do not replace skrub DataOps with bare sklearn Pipeline.
- Do not persist a result as done while `smoke run` is `stop`.
- Do not load evaluate (or write `skore.evaluate`) before the
  post-smoke HITL answer is Evaluate (`evaluate consent` `ask`),
  except `proceed` for a stem that already has a persisted report,
  or while `smoke run` is `stop`.
- Do not load `smoke-test-ml-pipeline` from this dispatcher.
- Do not duplicate child-skill methodology in this dispatcher.
- If `status.data_analysis` is `missing`, continue with facts the user
  stated; do not invent an exploratory data analysis report.
- Literature-backed feature-engineering or learner-family
  questions: load `build-ml-pipeline` only if
  `status.skills.build-ml-pipeline` is true (it loads
  `research-ml-practice` only if `status.skills.research-ml-practice`
  is true). Else one-line skip. Do not distill research
  here; do not invent papers from memory.

After **Stop**, or while smoke is red: skip evaluate, audit, and
record-outcome. This is an explicit no-result close: do not mark
the experiment done, but still run § Close — notebooks and site
when applicable, then return to triage.

After **Review** or **Skip** (or a missing review skill),
implement-loop step 4 (record-outcome) runs first, so the journal
files are on disk before anything is staged. **Stop** skips
record-outcome. This dispatcher owns the User-facing close.
Children return locator / digest / finding and do not preview
this close. The User-facing close below names the two
`notebook convert` commands; run them after that narrative.

### User-facing close

The user-facing message is a short story plus links. It is not
Pre-flight, not a dump of the digest or design note, and not
locator/finding alone.

1. **Narrative first** — 2–6 sentences of the result, grounded in
   the audit digest when present (Checks + Metrics), else the
   user's headline / `report.txt`. Do not invent a metric.
2. **Open these** — resolved absolute paths. When `site build`
   ran or is about to, link the site and not the design note:
   `[report.html](<workspace>/report.html)` and
   `html/<stem>.html`. Otherwise
   `[journal/<stem>.md](journal/<stem>.md)`.
3. **Normalized tokens second** — G-REPORT-LOCATOR evaluate
   passed up (or `n/a — backend did not expose a locator`) first
   among tokens, then G-AUDIT-FINDING (`n/a — audit not run`
   when skipped). Index strings, not the narrative.

Then run § Close — notebooks and site. That is both
`python -m skore_skills notebook convert experiments/<stem>.py`
when that file exists and the same command on
`audit/<stem>.py` when that file exists, with `--html` when
`policy.site` is also true. The audit skill did not convert
either file. Converting only the audit file does not finish the
close. The site appends the audit viewer to the experiment
design note's `## Notebooks` section after the evaluation
notebook.

### Close — notebooks and site

This close applies to **Stop**, red smoke, **Review**, **Skip**,
and a missing review skill. The unfitted-snapshot ban in
`build-ml-pipeline/references/snapshot.md` does not apply,
including when `experiments/<stem>.py` already contains
`skore.evaluate`. Converting only `audit/<stem>.py` does not
finish the close.

If `policy.notebooks` is true and `export-ml-notebook` is
installed, run
`python -m skore_skills notebook convert experiments/<stem>.py`
when the experiment script already exists, and the same command
on `audit/<stem>.py` when that file exists, with `--html` when
`policy.site` is also true. `audit-ml-pipeline` does not convert
on this path. Site build embeds `audit/<stem>.nb.html` under
`## Notebooks`; do not add `<!-- results-embed: audit -->`.
Convert re-executes the script; say so when it is slow. If
convert fails because `ipywidgets` is missing, load
`add-python-package` for it (agent) and convert again. Missing
jupytext / nbclient / nbconvert → one-line skip naming
`add-python-package`; do not fail the turn.

Then, if `policy.site` is true, `export-ml-site` is installed, run
`python -m skore_skills site build` so the Method DataOp report
(and Results) replace the construct-time snapshot. Skip in
one line otherwise. If `site build` errors with `mkdocs-material
is required`, load `add-python-package` for `mkdocs-material`
(agent) and build once more. Do not `pixi add` / `uv add`. If
that skill is missing, or the retry still fails, name the error
in one line. Name a build error; do not fail the model turn. Name
`report.html` (and `html/<stem>.html`) in the User-facing
close when the build ran. Do not also send the user to the
markdown.

Then run
`python -m skore_skills git end-turn --stage implement`. If JSON
`action` is `invoke`, load `persist-ml-git` only if
`status.skills.persist-ml-git` is true and stop; that skill
returns to triage. If persist is missing, name the pending
`staged` paths and stop. Otherwise load `triage-ml-task` only if
`status.skills.triage-ml-task` is true; else stop. Do not run
`git commit` in this skill.
Never mark `done` while smoke is red.
