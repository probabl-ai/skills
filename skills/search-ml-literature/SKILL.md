---
name: search-ml-literature
description: >
  Search scientific and technical sources for a query and, after
  the user picks and confirms one direction, write one idea file.
  Comes after review, beside the backlog. Do not call
  research-ml-practice. Do not write JOURNAL.md or a design note.
  Do not pick a winner.
---

# Search ML Literature

Comes after review, beside the backlog. Source is a query, not an
artifact the user already named. Show a few directions, then write
one `journal/ideas/<slug>.md` for the direction they confirm.
`manage-ml-backlog` triages that file later.

## Human-facing prose

Details: `setup-workspace` `references/human_facing_prose.md`.
Directions and the pick question are scientific options for this
project — not skill ids or the wrapper CLI.

## Procedure

1. Run `python -m skore_skills status`. Read `journal/JOURNAL.md`
   Status, the last History headline, and the EDA summary when
   `data_analysis/data_analysis.md` exists. If the query is too
   vague to search, ask once.
2. Rewrite the query as a problem class before any search. Drop
   dataset names, loader names (`sklearn.datasets`, `fetch_*`),
   and Kaggle slugs. JOURNAL and EDA are context for that
   rewrite, not search strings.
3. Search scientific and technical sources. Fetch the primary
   pages. When sources disagree, say so. Do not fill a gap from
   memory after a search has run. If search cannot run, say so
   and stop. Do not invent papers, URLs, or claims.
4. Write `scratch/research/direction-<slug>.md` when that write
   can run. Do not paste it into chat.
5. Show two to four directions. Each one: a one-line idea, why
   it might transfer here, what it would change, and the URL
   plus the claim. Do not rank a winner.
6. **AskUserQuestion**: pick one, narrow the query, or stop.
   Narrow restarts at step 2. Stop writes no idea file.
7. Restate the picked direction and wait for an explicit yes.
   Until yes, that paragraph is the whole message. No or stop
   writes nothing.
8. On yes, the only file this skill writes is
   `journal/ideas/<slug>.md`. Do not create or edit
   `journal/JOURNAL.md` or a design note. Write
   `journal/ideas/<slug>.md`:

```
# <slug>
- Experiment: <last History stem, or n/a>
- Source: literature: <url>
- Question:
- Why now:
- What changes:
- Open gaps:
```

   Open gaps hold transfer risks, disagreements, and domain
   claims this dataset does not establish. A library named only
   by a source stays in Open gaps until the user asks to add it.
   Return the path to the caller.

## Stop conditions

- Do not load `research-ml-practice`.
- Do not write `JOURNAL.md` or a design note.
- Do not append a `B<N>` row.
- Do not search a dataset proper name, a loader, or a Kaggle slug.
- Do not add a package or run `env add` / `pixi add`.
- Do not treat one blog as ground truth.
