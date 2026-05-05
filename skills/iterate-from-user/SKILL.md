---
name: iterate-from-user
description: >
  Source the next ML experiment proposal from the user directly,
  from a GitHub issue tracker the user has pointed us at, or from
  a spec / notes / reference repo the user has pointed us at.
  Hand the proposal back to `iterate-ml-experiment`, which writes
  it into `plan/NN_short_name.md` and seeks the user's approval.
  Stops at "a proposal (question, motivation, method outline) has
  been returned"; does not write any plan file itself, and does
  not author acceptance criteria — the user judges the result.

  TRIGGER when: `iterate-ml-experiment` is picking a sourcing
  strategy and the user has offered a concrete idea ("I want to
  try X", "let's add Y", "tweak the encoder"); the user pastes or
  links a GitHub issue / discussion that describes the next
  experiment; the user says "use the issue tracker" or "check
  issue #N"; the user points us at another repo / folder / set of
  notes ("look at the spec at <path>", "see the notes in
  <repo-url>", "read what's in <dir>").

  SKIP when: the user is open-ended ("what's next?") with no idea
  in hand — try a different strategy (diagnostic / methodology /
  literature) first; the user is asking for a symbol lookup or
  pipeline mechanics (use the `*-api` skills); there is no `gh`
  CLI / GitHub access and the user wants the issue tracker —
  surface the gap and fall back to direct user input.

  HOW TO USE: this skill is shallow — it elicits the proposal
  and returns it. If the user has a verbal idea, ask the three
  shaping questions in the body and synthesize a proposal. If a
  GitHub issue is the source, fetch it with `gh issue view <N>`
  (or `gh api`), summarize it through the same three-question
  lens, and flag anything the issue doesn't answer. If a spec /
  notes repo is the source, read the relevant files (README,
  proposal docs, referenced notebooks) and summarize through the
  same lens. Always return: question / motivation / method
  outline — not a plan file, not acceptance criteria.
---

# Iterate from user

Source: the user (directly, or via a GitHub issue they own).
Output: a proposal handed back to `iterate-ml-experiment`.

## Output contract (read this before the body)

This skill **never writes `plan/` files** and **never authors
acceptance criteria**. It returns a **Proposal block** back to
`iterate-ml-experiment` (full shape in § What is returned at the
bottom): `Question`, `Motivation` (with the user quote, issue
link, or spec-repo path as `Source`), `Method outline`,
`Open gaps`. Required:

- Every Proposal must answer all **three shaping questions**
  (see § The three shaping questions). Missing → ask the user
  before returning.
- **GitHub-issue path:** check `gh auth status` first;
  resolve repo per § Resolution priority; fetch comments if
  the issue body is short.
- **Spec / notes repo path:** confirm the path / URL the user
  gave, read the relevant files only (don't crawl the whole
  repo), and cite specific files in the `Source` field.
- **Goal shifts** (different output shape, downstream
  consumer, or metric class) require user confirmation of a
  PLAN.md Status update **before** returning the proposal —
  see § Stop conditions.

There is **no "no proposal" outcome** for this skill: it only
fires when the user has volunteered an idea (or pointed at an
issue / repo). If the user is open-ended without an idea, the
dispatcher in `iterate-ml-experiment` asks them directly via
the sourcing menu instead of invoking this skill.

## Stop conditions

- **Don't write `plan/` files.** That belongs to
  `iterate-ml-experiment`. This skill returns a proposal as
  conversation text or structured fields; the parent skill
  drafts the file.
- **Don't infer an issue's content.** If the user references an
  issue, fetch it (`gh issue view <N>` / `gh api`) — don't
  reconstruct from the issue title alone.
- **Don't paper over missing fields.** If the user's idea (or
  the issue) doesn't answer one of the four shaping questions,
  surface the gap to the user before returning the proposal.
- **Check `gh` auth before fetching anything.** Before any
  `gh issue view` / `gh api` call, run `gh auth status`
  (cheap, cached). If unauthenticated or on the wrong host,
  **do not** retry blindly — ask the user to either run
  `gh auth login` themselves (suggest they type `! gh auth
  login` in the prompt so it runs in this session) or paste
  the issue body directly. A failed `gh` call surfaces a
  confusing error; the auth check makes the failure mode
  explicit.
- **Flag goal shifts before returning the proposal.** If the
  user's idea (or the issue) materially changes the **project
  goal** as recorded in `PLAN.md` Status — different output
  shape (point estimate → prediction interval), different
  downstream consumer (offline batch → online serving),
  different metric class (squared error → coverage) — that's
  not just a method change. Surface it as a question to the
  user **before** returning the proposal: *"this would update
  PLAN.md Status from <X> to <Y>; confirm or amend the goal
  first?"* The parent skill's per-experiment plan file should
  not silently re-define what success means while the Status
  block still reflects the old goal.

## The three shaping questions

Every proposal returned from this skill must answer:

1. **What are we trying to learn?** (turns "try X" into a
   hypothesis)
2. **Why now?** (the specific reason this idea surfaced — quote
   the user, link the issue, cite the spec-repo file)
3. **What changes vs. the previous experiment?** (which file in
   `src/<pkg>/` is touched, in prose — not code)

Missing → ask the user. Don't fabricate.

**No "how will we know it answered the question?" question.**
That's an acceptance-criteria slot, and the skill does not
author those — the user reads the headline result after the run
and judges. See `iterate-ml-experiment` § "What this skill does
NOT do".

## Three intake paths

### Direct user input

The user has a verbal or written idea. Ask the three questions in
order, in plain language. Quote them back when summarizing the
proposal so the framing stays theirs. Hand the synthesis to
`iterate-ml-experiment`.

### Spec / notes repo

The user pointed us at a separate repo / folder / set of notes
("read the spec at `~/code/<repo>`", "see the notes at
`https://github.com/<owner>/<repo>`", "look at `<dir>` for
ideas"). Treat it as a structured input source distinct from
their own verbal idea — the proposal still needs to come back
through the three-question lens.

Procedure:

1. **Confirm the path / URL** the user gave; if it's remote and
   not yet cloned, ask where to clone it (don't pick silently).
2. **Read selectively, not exhaustively.** Start with `README.md`
   / `SPEC.md` / `NOTES.md` / a top-level proposal doc; if the
   user named a specific file or directory, prioritize that.
   Don't crawl every file — that hides the actual signal.
3. **Map to the three shaping questions.** What does the spec
   want to learn? What's the motivation as the spec frames it?
   What concretely changes in `src/<pkg>/`? Quote the spec
   verbatim when answering "why now?".
4. **Cite specifically.** The `Source` field in the returned
   Proposal must reference the file paths (and line numbers if
   useful) — not just the repo name.
5. **Flag gaps.** If the spec doesn't answer one of the three
   questions, ask the user before returning — same rule as for
   issues.

### GitHub issue tracker

The user pointed us at an issue (number, link, or "check the
tracker").

**Resolution priority (never silently guess).** Pick the
owner/repo using the first rule that matches:

1. **Explicit URL** in the user's message
   (`https://github.com/<owner>/<repo>/issues/<N>`) — wins
   unconditionally.
2. **`org/repo#N` shorthand** in the user's message
   (`probabl-ai/skore#42`) — wins over current context.
3. **Bare `#N` or "issue 42"** with no qualifier — fall back to
   the current `gh` context (`gh repo view --json
   nameWithOwner` to confirm). If that returns nothing, ask
   the user before fetching.

Then fetch:

- `gh issue view <N> --json title,body,labels,url` for the
  baseline.
- **If the issue body is short (<200 chars) or visibly
  under-specified**, also pull the latest comments —
  `gh issue view <N> --json title,body,labels,url,comments`
  or `gh api repos/<owner>/<repo>/issues/<N>/comments` — and
  read the most recent ~5. The actual proposal often lives
  in the thread, not the top-post.

Map the assembled issue (body + relevant comments) to the three
shaping questions; flag missing fields and ask the user to
clarify before returning the proposal. The proposal returned
must include the issue link as **Source** so the per-experiment
plan file can cite it.

## What is returned

A short structured block, not a plan file:

```
Proposal (from: user | issue #<N> | spec-repo:<path>):
  Question:        <one sentence>
  Motivation:      <quote / link / spec-file path>
  Method outline:  <prose; which file in src/<pkg>/ is touched>
  Open gaps:       <anything the user / issue / spec didn't answer>
```

`iterate-ml-experiment` consumes this and drafts
`plan/NN_short_name.md`. **No `Success` field** — the skill
deliberately does not author acceptance criteria; the user judges
the result post-run.

## Companion skills

- **`iterate-ml-experiment`** — the caller; owns the plan file.
- **`iterate-from-literature` / `iterate-from-methodology` /
  `iterate-from-diagnostic`** — sibling strategies for when the
  user is open-ended.
