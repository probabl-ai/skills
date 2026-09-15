# Python Env Manager — Pre-flight evidence format

Spec for the `Evidence:` line under each ticked Pre-flight box in
`SKILL.md` § Pre-flight. Every ticked box requires an `Evidence:`
line — a ticked box without evidence is a Stop-condition violation,
indistinguishable from a skipped check.

## Three row shapes

### Detection rows

Evidence is the tool output that triggered the detection-table
match:

```
Evidence: ls project_root | tool output (this turn) → matched signal "<signal>"
```

Example: `pixi.toml present → pixi`.

### Gate rows (G-ENV-MGR, G-ENV-SCOPE, G-AGENT-FEATURE)

Evidence is one of:

- `Evidence: AskUserQuestion id=<id>, answer=<option>` — the user
  picked via the structured tool this turn.
- `Evidence: user quote turn N: "..."` — free-text from the user
  named one of the listed options.
- `Evidence: JOURNAL.md Status (Workspace decisions, recorded YYYY-MM-DD)`
  — the decision was made in a prior session.

### Workflow rows

Evidence is the artifact produced or the command that ran:

```
Evidence: Shell pixi add <pkgs> → exit_code=0
```

## End-of-turn re-emission

The last box in every pre-flight is:

```
- [ ] Pre-flight re-emitted with evidence before final message.
```

This box is checked when the agent's final message contains the
same pre-flight block with every Evidence cell filled. The intent
is a forcing function — don't end the turn until the checklist is
green.
