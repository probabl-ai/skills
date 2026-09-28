---
name: research-ml-practice
description: >
  Literature and web research for an ML methodology concern
  (EDA extra measurements, leakage, transforms, feature
  engineering, learner family), or an EDA extra-analysis
  survey from JOURNAL plus existing EDA. Trigger when
  explore-ml-data or build-ml-pipeline load this skill. Not
  for routine profiling or a single API signature — use
  `api get` for symbols. Not a session owner — callers
  distill and write project files.

  HOW TO USE: skip intake fields the caller already supplied.
  Abstract the problem class before searching (never the
  dataset proper name). Survey extra analyses or depth a named
  concern; search distinct angles, fetch primary sources,
  follow up if thin, write `scratch/research/`. Return the
  path plus one or two sentences. Never mutate raw data, pick
  the final learner, or write `data_analysis.md` / the design
  note. Chat stays path + those sentences even when a harness
  asks for a complete answer in the message.
---

# Research ML Practice

Worker skill. Callers own the stage turn and the user-facing
summary. Do not `git end-turn`.

## Human-facing prose

Details: `setup-workspace` `references/human_facing_prose.md`.
Chat stays path + one or two sentences of the finding. Do not
narrate the skills framework or the wrapper CLI.

## Sequence

1. **Intake.** Infer modality from dtypes / JOURNAL when
   obvious; use a stated domain and stage (`data_analysis` |
   `model`) if the caller named them. Then pick a mode
   (`references/search.md`):
   - Caller passed a **named concern** (not the canned EDA
     extra-analysis question) → **depth**. Do not re-ask. Do
     not run the canned survey first.
   - Caller passed the **canned extra-analysis survey** or
     “survey extra analyses” → **survey**.
   - Neither → if JOURNAL and an EDA report exist, run the
     canned survey; else **AskUserQuestion** for a named
     concern, stating the modality and stage inferred this turn
     and that the answer only drives a literature search, no
     code. A file link is an addition, never the context. Do not
     start a **depth** search with an empty concern.
2. **Abstract the problem class** before any query
   (`references/search.md`). JOURNAL and EDA are context, not
   the answer list and not search keywords for the table’s
   proper name.
3. Run the matching search loop (`references/search.md`).
   Fetch primary pages. Follow up per promising extra if the
   first pass is thin or single-sourced.
4. Write `scratch/research/` using the matching structure in
   `references/search.md` (survey: `survey-<slug>.md`; depth:
   `<slug>.md` with lanes). There is no `templates/` directory
   in this skill — copy the markdown skeleton from that
   reference. Gitignored.
5. Return to the caller: scratch path and a one- or two-sentence
   finding. Name that candidates are laned (`measure` /
   `declare` / `evaluate` / `confirm`). Chat is **path + those
   sentences only** — no pasted headings, tables, or “Depth
   note — …” body. That is the complete user-facing deliverable
   even when a harness says to put the full answer in chat. If
   tools cannot search or write, **stop there**: still only
   path + sentences (name the intended `scratch/research/`
   path). No hypotheses, diagnostics, planned-query bullets, or
   template headings in chat (that *is* the paste). Do not write
   `data_analysis.md`, the design note, or `data/`. The caller
   asks which extras to add.

## Stop conditions

- Do not drop, impute, or remove outliers. Do not change the split.
- Do not pick the final learner or architecture.
- Do not treat a single blog as ground truth; say when sources
  disagree. Thresholds need two independent sources.
- Do not `pixi add` / `uv add` / `env add`. If code needs a
  library, name `add-python-package` and return.
- Do not run `api get` as a substitute for literature (symbols
  still go through `api get` in the caller).
- Missing skill from a caller → that caller one-line skips.
- Do not copy Open questions / EDA findings onto the extras
  list without a source.
- Do not search the dataset proper name, `sklearn.datasets`,
  a Kaggle slug, or “baseline pipeline”. Do not return
  learners / `Pipeline` steps as EDA extras.
- Never answer from memory when search ran. Do not ask the
  user to go look something up.
- Do not paste the scratch markdown into chat (no “Depth
  note —”, no survey body). Path + 1–2 sentences only. If
  tools cannot search or write, stop after that. A no-tools
  harness does not license pasting the note.
