---
name: manage-ml-backlog
description: >
  Canonical backlog loop step. Record an experiment outcome in
  History, refresh Backlog, and name next-lever options. Trigger
  after audit, when a run finishes, or when the user asks what to
  try next. This is cadence, not a dispatcher.
---

# Manage ML Backlog

Replace iterate-as-cadence. Do not own setup, EDA, build, smoke,
evaluate, or audit methodology.

## Procedure

1. Run `python -m skore_skills status`. Require an approved stem
   and a report/audit digest when recording a done outcome.
2. Read `journal/JOURNAL.md` History and Backlog. If the index is
   missing, initialize the packaged shape with
   `python -m skore_skills scaffold --journal`; do not invent it.
3. If recording a run: copy the headline metric from the audit
   digest or the user's value. Do not invent numbers. Update the
   matching History row (`planned` → `done` only if smoke passed).
   Update the design-note Status block the same way.
4. Scan Backlog. Resolve rows the run answered or killed. Add at
   most a few next-lever options (`skore:<stem>`, `user`,
   `my-pick:<stem>`).
5. Ask triage: draft the next experiment now, pick a Backlog row,
   or stop. When a row is selected, the model stage can create its
   design-note shell with
   `python -m skore_skills scaffold --journal --stem <NN_short_name>`.
   Do not draft it in this backlog turn.

Use the existing table shapes in `journal/JOURNAL.md`:

```text
## History
| Stem | Intent (one line) | Status | Headline result | Design note |

## Backlog
| # | Item | Source |
```

Stable `B<N>` indices. Do not renumber on removal.

## Stop conditions

- Do not design or implement the next experiment in this turn.
- Do not dispatch setup, model, or audit by skill id.
- Do not invent metrics.
- Do not mark `done` while smoke is red.
- G-DESIGN stays in the implement/evaluate skills, not here.

End of turn is triage.
