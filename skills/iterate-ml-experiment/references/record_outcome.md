# Record outcome — full § 4 procedure

The recording loop after a run finishes. SKILL.md § 4 has the
compact version; this file has the full procedure including the
backlog hygiene examples and the opt-in GitHub close-the-loop.

**Trigger is user-driven (v1).** This skill does **not** auto-detect
that a script has finished — no polling of the skore Project store,
no file-mtime watching, no background hook. The user says "the run
finished, record it" (or similar), and only then does § 4 start. If
you suspect a run finished but the user hasn't said so, ask.

## Step 1 — Run the audit and read its digest

§ 4 is **audit-first**: dispatch to `audit-ml-pipeline` to place +
execute `audit/NN_<short_name>.py` before doing anything else. The
audit runner is the one path that opens the skore Project from
this skill's flow; § 4 itself never calls `project.get(...)` or
`report.*` accessors directly.

The audit produces the **digest** at
`scratch/audit/<stem>/audit.md` — the canonical programmatic entry
point for the recording step. Read it as text and pull:

- **Headline metric + uncertainty** from `## Metrics summary`.
- **Actionable checks** from `## Checks summary` (each row with
  `severity == issue` / `tip` carries a `documentation_url`; that
  link is the recommended mitigation).

### Audit succeeded — proceed

The digest carries everything needed for steps 2–7 below. Don't
re-open the Project, don't write `scratch/<ts>_inspect_*.py` to
extract metrics — the audit already did the walk.

### Audit cannot run / digest unreadable — ask the user

Agent feature missing, report not landed in the Project, hub
auth expired, script crashed before `project.put`: **do not
fabricate report content from memory.** Recovery is owned by
`audit-ml-pipeline` (re-run the runner once the issue is fixed)
or `python-env-manager` (G-AGENT-FEATURE). If the user wants to
record the outcome anyway, ask them for the headline metric (and
a one-line note on anything that looked off), set the design
note's Implication to `deferred — audit not accessible this
session`, and revisit on the next session.

### Scratch is only for needs beyond the digest

If a step downstream of the digest needs more (e.g. a
cross-experiment metrics view from `project.summarize()` that the
digest doesn't carry), the probe goes to
`scratch/<YYYY-MM-DD>_<HHMMSS>_<short>.py` and runs via
`pixi run python scratch/<ts>_<short>.py`.

See `python-api` § "Scratch traceability" for the full
convention. **Inline `pixi run python -c "..."` is forbidden
regardless of length** (see `python-api` § Stop conditions).

**Do NOT edit the experiment script to add agent-only `print`
calls.** The script is the durable record of what was run; the
audit is the durable diagnostic walk; scratch is only for the
gaps between them.

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

## Step 6 — (Opt-in) GitHub issue close-the-loop

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

## Step 7 — STOP. Do NOT auto-launch the next dispatch

The user controls cadence; this skill records, it doesn't
propose-and-record in one breath.

Surface the implication to the user as a one-liner ("the residual
bias near boundaries points at a target-transform experiment") and
ask via `AskUserQuestion` with exactly two options:

- **draft it now** — re-enter § 1 with the implication as the
  proposal seed; route via the sourcing menu.
- **not yet** — record the implication in `JOURNAL.md` Backlog as
  a one-liner and stop.
