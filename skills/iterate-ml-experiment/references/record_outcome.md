# Record outcome — full § 4 procedure

The recording loop after a run finishes. SKILL.md § 4 has the
compact version; this file has the full procedure including the
`overview/summary.md` refresh, backlog hygiene examples, and the
opt-in GitHub close-the-loop.

**Trigger is user-driven (v1).** This skill does **not** auto-detect
that a script has finished — no polling of the skore Project store,
no file-mtime watching, no background hook. The user says "the run
finished, record it" (or similar), and only then does § 4 start. If
you suspect a run finished but the user hasn't said so, ask.

## Step 1 — Decide if the report is accessible

Is the skore Project store at the expected path (`reports/`) and does
it contain the experiment's key?

### Accessible — read it programmatically

Open the report via the skore Project. Route through
`evaluate-ml-pipeline` for the call site, and **invoke
`python-api` this turn** to confirm signatures — don't reach into
report attributes from memory.

The programmatic entry point is **`report.diagnosis()`** — for v1
this is the only diagnostic entry point this skill relies on. For
a richer diagnostic narrative for the user, hand off to
`evaluate-ml-pipeline`.

**`Project.get` is by id, not by user-facing `key`.** Enumerate
with `project.summarize()` first; that returns a DataFrame indexed
by id with a `key` column. Pass the id to `get()`. A failed
`get(key)` does NOT mean the report is missing — it means the
lookup shape is wrong.

### Not accessible — ask the user

Run on a different machine, batch system, script crashed before
`project.put`, …: **do not fabricate report content from memory.**
Ask the user for the headline metric (and a one-line note on
anything that looked off). Mark the design note's "Implication"
field as `deferred — report not accessible this session` and pick
the diagnostic up next time.

### Inspection lives in `scratch/`, not in the experiment script

The experiment script's job ends at `project.put(...)`. To pull
metrics, walk diagnosis, sanity-check any post-run state:

```
scratch/<YYYY-MM-DD>_<HHMMSS>_<short>.py
```

See `python-api` § "Scratch traceability" for the full
convention. **Inline `pixi run python -c "..."` is forbidden
regardless of length** (see `python-api` § Stop conditions). All
Python execution goes to `scratch/<ts>_<short>.py`.

**Do NOT edit the experiment script to add agent-only `print`
calls.** The script is the durable record of what was run; the
inspection trace lives in `scratch/`.

## Step 2 — Fill the four Status-block fields

Both branches (accessible / not accessible) require all four
fields filled in `journal/NN_*.md`:

- **State:** `done` (or `abandoned` with a one-line reason)
- **Approved by user on:** unchanged from approval (don't edit)
- **Headline result:** the metric + uncertainty
  (e.g. `RMSE 0.083 ± 0.004 (5-fold CV)`)
- **Implication for next iteration:** one or two sentences — this
  is the seed for the next strategy dispatch

## Step 3 — Smoke-test gate before `done`

**Full `tests/smoke/` must pass, not just the new one.** The new
experiment's smoke test catches structural bugs in *its* pipeline
shape; the prior experiments' tests catch the reproducibility
regression rule — if your change to `pipeline.py` / `features.py`
/ `data.py` silently changed what `build_learner()` returns for a
caller that didn't opt in, *their* test will go red.

Both failure modes route to `build-ml-pipeline`:

- Pipeline-shape bugs → its X-marker rule.
- Reproducibility regressions → its § "Reproducibility mechanics"
  (parametrize / new function / branch the module, per the
  judgment ladder).

Resolve, re-run, only then re-record the outcome. The CV report
can land in the skore Project regardless (CV is independent of
predict-time binding), but the JOURNAL row stays `approved` until
the full smoke suite is green.

**Abandonment** does not require passing smoke tests — an
experiment can move from `approved` straight to `abandoned` with
a one-line reason.

## Step 4 — Append headline to JOURNAL.md History

Update the existing History row for the experiment with the
headline result. Don't add a new row; the existing row was added
at approval time.

## Step 5 — Backlog hygiene

Scan the existing Backlog for items the just-finished experiment
has answered, killed, or made irrelevant — items about a feature
/ splitter / transform no longer in the pipeline. Two treatments
per item:

- **Delete** the bullet outright if the rationale no longer
  applies.
- **Strikethrough with a brief reason** if the breadcrumb is
  worth preserving but should not be promoted:

  ```
  | B3 | ~~Explore target log-transform for high-end bias~~ — resolved in 03_target_transform | skore:02 |
  ```

**Diagnostic mining of the *new* report is NOT done here** — that
is `iterate-from-skore`'s job, triggered when the user picks
`skore` from the sourcing menu in a later turn. § 4 only prunes
existing items; it never appends new findings.

## Step 6 — Refresh `overview/summary.md`

`summary.md` is **not** generated by a script. It is rewritten by
hand at every outcome recording so the cross-experiment narrative
stays curated rather than dump-pasted.

### 6a — Probe the data via a scratch script

Write `scratch/<YYYY-MM-DD>_<HHMMSS>_refresh_summary.py`. The
script's job is **extraction, not formatting**:

- Open the skore Project (consult `python-api` for `Project` /
  `summarize` signatures this turn — don't guess) and call
  `project.summarize()` for the cross-experiment metrics table.
- List `journal/[0-9][0-9]_*.md` files and extract each one's
  `## Status` block (State, Headline result, Implication).
- Print or pickle whatever the agent needs to read next.

Run with `pixi run python scratch/<ts>_refresh_summary.py`. Output
lands in the conversation; the file stays on disk per the scratch
append-on-success convention.

### 6b — Rewrite `overview/summary.md` by hand

From the probe output. Structure is fixed by the placeholder;
fill it:

- **Project narrative** — 1-2 paragraphs covering dataset, goal,
  and the path so far (what was tried, where the metric stands).
- **Cross-experiment metrics** — curated table from
  `project.summarize()`. Drop columns that aren't comparable
  across the listed experiments (e.g. classification metrics in a
  regression-only project, fit-time / predict-time unless the
  user cares).
- **Per-experiment status** — one subsection per `done`
  experiment with the curated Headline + Implication. Quote the
  design note's Status text where it's already concise; rewrite
  where it isn't. The point is a *narrative*, not a paste.

**Do NOT regenerate from a script.** If `overview/summary.py`
exists in a legacy workspace, delete it (after this rewrite lands)
— the per-version contract is "`summary.md` only".

### 6c — First-time bootstrap

If the workspace has no `overview/summary.md` at all (bootstrapped
before this contract, or fresh scaffold where § 4 has never
fired), drop the placeholder from `organize-ml-workspace`'s
`templates/summary.md` first, then rewrite per 6a-6b.

## Step 7 — (Opt-in) GitHub issue close-the-loop

If the just-recorded experiment's `Source` is a GitHub issue —
the `Sourcing strategy` was `user` and the `Source` field links
to `github.com/<owner>/<repo>/issues/<N>` — **offer** to post the
headline back via `AskUserQuestion` with exactly two options:

- **comment back** — run
  `gh issue comment <N> --body "<headline + design-note link>"`
  this turn.
- **skip** — move on, no outbound action.

**Never auto-post.** The `gh issue comment` call only fires on
explicit `AskUserQuestion` approval — a free-text "yes" is not
enough, because this is the only outbound side effect this skill
is allowed and consent for it should be structured.

## Step 8 — STOP. Do NOT auto-launch the next dispatch

The user controls cadence; this skill records, it doesn't
propose-and-record in one breath.

Surface the implication to the user as a one-liner ("the residual
bias near boundaries points at a target-transform experiment") and
ask via `AskUserQuestion` with exactly two options:

- **draft it now** — re-enter § 1 with the implication as the
  proposal seed; route via the sourcing menu.
- **not yet** — record the implication in `JOURNAL.md` Backlog as
  a one-liner and stop.
