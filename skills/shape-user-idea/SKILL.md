---
name: shape-user-idea
description: >
  Shape an idea the user already has, or answer a project question,
  and write one idea file after they confirm. A topic with no
  artifact belongs to search-ml-literature. Do not write JOURNAL.md
  or a design note. Do not pick a backlog row.
---

# Shape User Idea

Comes after review, beside the backlog. The user already has an
idea, a question, or an artifact. This skill writes
`journal/ideas/<slug>.md` only after they confirm. The backlog
triages that file later.

## Human-facing prose

Details: `setup-workspace` `references/human_facing_prose.md`.
Questions and the confirmation paragraph describe this idea in
data-science terms — not skill ids or the wrapper CLI.

## Procedure

1. Run `python -m skore_skills status`. Read `journal/JOURNAL.md`
   Status and History, and `data_analysis/data_analysis.md` when it
   exists.
2. If the entry is not already a concrete idea, question, or
   artifact, **AskUserQuestion**: free-text or artifact. A URL,
   issue, path, or stated idea skips that menu.
3. A question about this project is answered from those files.
   Leave an unknown metric as `n/a`. Write no idea file and
   return to the caller.
4. A topic with no artifact ("what do people do for …") loads
   `search-ml-literature` only if
   `status.skills.search-ml-literature` is true. Otherwise
   one-line skip. Do not `WebSearch` for a paper from here.
5. An artifact is read, not reconstructed. Paper or doc URL:
   `WebFetch` the page. GitHub issue: `gh auth status` first;
   if unauthenticated, ask the user to run `gh auth login` or
   paste the body. Then `gh issue view`. Resolution: explicit
   URL, then `org/repo#N`, then bare `#N` only in the current
   `gh` repo — otherwise ask. Spec or notes file: read that
   file only.
6. Walk three questions. Do not fabricate a missing answer.
   - What are we trying to learn?
   - Why now? Quote the user or the artifact.
   - What changes versus the last experiment, in prose?
7. If the idea changes the project goal in `journal/JOURNAL.md`
   Status, ask before writing the file. A library the source names and
   the user has not agreed to add stays in Open gaps. A domain
   claim this dataset does not establish stays in Open gaps.
8. Restate the idea in one short paragraph and wait for an
   explicit yes. "Maybe" is not yes. No or stop writes nothing.
9. On yes, the only file this skill writes is
   `journal/ideas/<slug>.md`. Do not create or edit
   `journal/JOURNAL.md` or a design note. Write
   `journal/ideas/<slug>.md`:

```
# <slug>
- Experiment: <last History stem, or n/a>
- Source: user
- Question:
- Why now:
- What changes:
- Open gaps:
```

   Why now carries the quote, URL, or path. No acceptance
   criteria. Return the path to the caller (`manage-ml-backlog`
   or `triage-ml-task`).

## Stop conditions

- Do not write `JOURNAL.md` or a design note.
- Do not append a `B<N>` row. The backlog triages the file.
- Do not invent source content from a title.
- Do not `WebSearch` for a topic with no artifact.
- The entry question and the confirmation paragraph are
  required gates.
- If the user already asked to add a named library, put it in
  What changes and load `add-python-package` when that skill
  is installed. Do not `pixi add` from here.
