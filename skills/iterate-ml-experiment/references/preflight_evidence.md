# Pre-flight — evidence requirements

Spec for filling the Evidence column on every pre-flight row.
SKILL.md has the compact checklist; this file has the format
contract per row type.

## Row types

Every row in the pre-flight is one of three types:

- **Read-set row** — a sibling `SKILL.md` opened this turn.
- **Gate row** — an `AskUserQuestion` was fired (or a recorded
  decision was the trigger).
- **Workflow row** — a procedural action this skill drives (e.g.
  "design note drafted").

The Evidence cell must match the row type. A ticked box without
evidence is a Stop-condition violation, indistinguishable from a
skipped check.

## Read-set rows

Evidence is the file-reading tool call this turn for the named
SKILL.md.

```
Evidence: Read .agents/skills/<name>/SKILL.md (this turn)
```

Citing the cross-reference *to* a sibling skill (e.g. "see
`evaluate-ml-pipeline` § rule 3") is **not** evidence — the
sibling file itself must have been opened in this turn.

## Gate rows

One of:

- **Structured ask resolved by the user:**

  ```
  Evidence: AskUserQuestion id=<id>, answer=<option>
  ```

- **Free-text resolved the gate** (per the skill's "free-text
  handling" rule):

  ```
  Evidence: user quote turn N: "..."
  ```

  Quote the exact phrase and the turn number. Don't paraphrase.

- **Pre-recorded decision** (Workspace decisions block in
  `JOURNAL.md` Status):

  ```
  Evidence: JOURNAL.md Status (Workspace decisions, recorded YYYY-MM-DD)
  ```

  This skill read the Status block in this turn's Second action
  step.

## Workflow rows

Evidence is the artifact produced this turn:

```
Evidence: Write journal/<NN>_<name>.md (this turn)
Evidence: Backlog rows B5..B7 appended to JOURNAL.md
Evidence: Edit journal/03_target_transform.md Status block (this turn)
```

## n/a evidence

A box ticked with `Evidence: n/a` is allowed **only** when the
row's narrative explicitly carves out an n/a case. Cite which
carve-out applies:

```
Evidence: n/a — bootstrap mode (no sourcing menu)
Evidence: n/a — read-only compare mode (no design-note write)
Evidence: n/a — only re-using symbols already cached
```

A bare `Evidence: n/a` without a carve-out citation is a
violation. The audit (last pre-flight row) catches this — surface
it to the user, don't silently proceed.

## Post-hoc audit

Before declaring the turn complete, walk every pre-flight row and
confirm:

1. The box is ticked or explicitly marked `n/a`.
2. The Evidence cell is filled with a concrete citation.
3. The citation matches the row type (Read / Gate / Workflow).

If any row fails audit, **surface the non-compliance to the user
explicitly** in your final message — name the row(s) and why they
failed audit — rather than silently moving on. Visible
non-compliance is recoverable; hidden non-compliance is the
failure mode this audit closes.
