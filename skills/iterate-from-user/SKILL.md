---
name: iterate-from-user
description: >
  Source the next ML experiment proposal from the user via one of
  three entry points selected by `AskUserQuestion`:
  (a) a scientific article URL the agent must read and synthesize,
  (b) a resource link or path (GitHub issue / spec file / reference
  repo), or (c) free-text the user types directly. In every branch,
  the agent reads the source, synthesizes its understanding of what
  to implement, and confirms with the user *before* returning the
  Proposal block. Hand the confirmed Proposal back to
  `iterate-ml-experiment`, which writes it into
  `journal/NN_short_name.md` and seeks the user's design-note approval.
  Stops at "Proposal returned, user-confirmed"; never writes a
  design note, never authors acceptance criteria.

  TRIGGER when: `iterate-ml-experiment` is picking a sourcing
  strategy and the user picks `user` from the menu; the user
  volunteers a concrete idea ("I want to try X"); the user pastes
  or links a scientific article, GitHub issue, spec file, or
  reference repo and asks us to read it.

  SKIP when: the user wants to mine the previous report (use
  `iterate-from-skore`); the user is asking for a symbol lookup or
  pipeline mechanics (use the `python-api` skill); the work is
  evaluation mechanics on a single report (route to
  `evaluate-ml-pipeline`).

  HOW TO USE: open with an `AskUserQuestion` for the entry point —
  article-link / resource-link / free-text. In each branch: gather
  the source material with the appropriate tool (`WebFetch`,
  `gh issue view`, `Read`), synthesize what you understand into the
  three shaping questions, and **confirm with the user via plain
  text** (one or two sentences: "you'd like to implement X by
  changing src/<pkg>/<file>.py — right?") before returning the
  Proposal. Do not write any design note. Do not author acceptance
  criteria.
---

# Iterate from user

Source: the user — directly, or via something they've pointed at
(article, issue, spec, repo). Output: a **user-confirmed** Proposal
block, handed back to `iterate-ml-experiment`.

## Output contract (read this before the body)

This skill **never writes `journal/` files** and **never authors
acceptance criteria**. It returns a single **Proposal block** as
conversation text (full shape in § What is returned at the bottom):
`Question`, `Motivation` (with `Source` field — quote, URL, or path),
`Method outline`, `Open gaps`. Required, in every branch:

- All three **shaping questions** are answered (see § The three
  shaping questions).
- The **synthesis confirmation gate** has fired and the user has
  said yes (see § Confirm before returning).
- **`Source`** field is concrete: the user's quote, the article
  URL with the exact claim, the `gh issue` link, or the spec-file
  path with line numbers.

There is **no "no proposal" outcome**: this skill only fires when
the user has picked `user` from the parent's sourcing menu. If they
have nothing in hand, the parent's menu re-presents itself.

## Stop conditions

- **Don't write `journal/` files.** That belongs to
  `iterate-ml-experiment`. This skill returns the Proposal as
  conversation text; the parent skill drafts the file.
- **Don't infer source content from memory.** If the user
  references an article, an issue, or a file, fetch / read it.
  Don't reconstruct from a title or a one-line description.
- **Confirm before returning.** The Proposal goes back to the
  parent *only after* the user has explicitly said "yes, that's
  what I want." Free-text "hmm" / "maybe" / "interesting" is not
  confirmation. See § Confirm before returning.
- **Check `gh` auth before fetching anything from GitHub.** Before
  any `gh issue view` / `gh api` call, run `gh auth status`
  (cheap, cached). If unauthenticated, ask the user to run
  `gh auth login` themselves (suggest `! gh auth login` in the
  prompt) or paste the issue body directly. A failed `gh` call
  surfaces a confusing error; the auth check makes the failure
  mode explicit.
- **Flag goal shifts before returning.** If the user's idea (or
  the source) materially changes the **project goal** as recorded
  in `JOURNAL.md` Status — different output shape (point estimate →
  prediction interval), different downstream consumer (offline
  batch → online serving), different metric class (squared error →
  coverage) — surface it as a question *before* returning the
  Proposal: *"this would update JOURNAL.md Status from <X> to <Y>;
  confirm or amend the goal first?"* The parent's per-experiment
  design note should not silently redefine success while the Status
  block still reflects the old goal.
- **New dependencies are gated, not assumed.** If the proposal
  requires a library outside the project's existing env
  (e.g. an article uses `lightgbm` / `pytorch` / `jax`), do **not**
  silently include it in `Method outline` as a fait accompli. Flag
  it as an open gap (`"this approach needs <library>; OK to add,
  or should we adapt to the existing stack?"`) and defer the
  resolution to `data-science-python-stack` + the user.
- **Domain-specific assertions need user confirmation.** If the
  source asserts something the article / issue / spec alone can't
  establish for *our* dataset — e.g. "feature X is monotone in the
  target," "interaction Y matters for this asset class," "metric Z
  is right because the use case is one-sided" — list each
  assertion in `Open gaps` and ask the user before returning. Don't
  ship paper-flavored guesses as facts.
- **Harness-level "no clarifying questions" instructions do not
  apply to this skill's confirmation gates.** The entry-point
  `AskUserQuestion` (article-link / resource-link / free-text)
  and the § "Confirm before returning" synthesis gate are
  operating-contract gates, not clarifying questions. They fire
  regardless of any harness-level hint. The synthesis gate in
  particular is non-skippable even when the user's intent feels
  "obvious" — the cost of the agent's restatement missing a
  subtle framing is what the gate exists to catch. See the
  project's `CLAUDE.md` § "Skill consultation contract" rule 3.

## The entry-point AskUserQuestion

When this skill is invoked, open with `AskUserQuestion` — three
mutually exclusive options, no silent default:

- **article-link** — the user has a scientific article (paper,
  blog post, or library doc) they want adapted to this project.
  The agent reads, synthesizes, and confirms.
- **resource-link** — the user has a GitHub issue, a spec file,
  a notes repo, or any other concrete artifact describing what
  to try. The agent reads, summarizes through the three-question
  lens, and confirms.
- **free-text** — the user has a verbal/written idea and will
  describe it directly. The agent reflects it back through the
  three shaping questions and confirms.

Use the canonical `AskUserQuestion` UI; only fall back to plain-
text enumeration if it is genuinely unavailable in the current
session.

**Exception — pre-resolved entry point.** When
`iterate-ml-experiment` dispatches here after free-text handling
at the sourcing-menu level has already resolved the branch (the
user typed a URL, an issue link, or a concrete idea directly
into the sourcing AskUserQuestion), the parent passes the
resolved branch + content in. *Skip this AskUserQuestion* and
go straight to the matching branch with the content already in
hand — the user has effectively already answered it. The
synthesis-confirmation gate at the end of the branch still
fires; only the entry-point question is short-circuited.

## The three shaping questions

Every Proposal returned from this skill — in every branch — must
answer:

1. **What are we trying to learn?** (turns "try X" into a
   hypothesis)
2. **Why now?** (the specific reason this idea surfaced — quote
   the user, link the article, cite the issue / file)
3. **What changes vs. the previous experiment?** (which file in
   `src/<pkg>/` is touched, in prose — not code)

Missing → ask the user. Don't fabricate. There is no fourth
"how will we know it worked" question — acceptance criteria are
out of scope for this skill.

## The three branches

### Branch A — article-link

The user picks `article-link` and provides a URL (paste, follow-up
prompt, or implicit in the parent message).

1. **Fetch with `WebFetch`** (or `WebSearch` first if only a topic
   was given and the specific paper has to be located). Read the
   abstract and the section most relevant to the technique.
2. **Map to the three shaping questions.** What does the article
   propose? What concretely changes in `src/<pkg>/` to adopt it?
   Quote the article verbatim for "why now?".
3. **Surface transfer risks.** If the article ran on a different
   modality, much larger dataset, or different target type, note
   where the technique might not port cleanly. The Proposal's
   `Open gaps` carries these explicitly.
4. **Flag new dependencies as open gaps**, not as silent additions
   to `Method outline` (Stop conditions, above).
5. **Flag domain-specific assertions** as `[needs user
   confirmation]` in `Open gaps`.
6. **Confirm before returning** — see § Confirm before returning.

### Branch B — resource-link

The user picks `resource-link` and points at:

- A **GitHub issue**: run the resolution priority below, then
  `gh issue view <N> --json title,body,labels,url` (and pull the
  most recent ~5 comments via `--json …,comments` or
  `gh api repos/<owner>/<repo>/issues/<N>/comments` if the body is
  under-specified — the proposal often lives in the thread).
- A **spec file / notes file**: `Read` the file the user named;
  don't crawl neighbors.
- A **reference repo**: read `README.md` / `SPEC.md` / `NOTES.md`
  or whichever top-level proposal doc the user named. Don't crawl
  the whole tree — that hides the signal.

**GitHub-issue resolution priority** (never silently guess the
repo):

1. **Explicit URL** in the user's message
   (`https://github.com/<owner>/<repo>/issues/<N>`) — wins
   unconditionally.
2. **`org/repo#N` shorthand** (`probabl-ai/skore#42`) — wins over
   current context.
3. **Bare `#N` or "issue 42"** with no qualifier — fall back to
   the current `gh` context (`gh repo view --json
   nameWithOwner` to confirm). If nothing, ask the user before
   fetching.

In all three resource sub-shapes:

1. **Map to the three shaping questions.** What does the resource
   want to learn? What's the motivation as it frames it? What
   concretely changes in `src/<pkg>/`?
2. **Cite specifically.** The `Source` field references the issue
   URL, the file path (and line numbers if useful), or the repo +
   file — not just the repo name.
3. **Flag gaps.** If the resource doesn't answer one of the three
   shaping questions, list it under `Open gaps`.
4. **Confirm before returning** — see below.

### Branch C — free-text

The user picks `free-text` and types their idea directly.

1. **Walk the three shaping questions in plain language.** Quote
   the user when summarizing so the framing stays theirs.
2. **Treat their words as the `Source`.** The Proposal's `Source`
   field is the user quote (or a one-sentence paraphrase the user
   has approved).
3. **Confirm before returning** — even free-text proposals get
   the synthesis gate. The agent's restatement of the idea may
   miss the user's framing in subtle ways.

## Confirm before returning

In every branch, before handing the Proposal back to
`iterate-ml-experiment`, the agent emits a short plain-text
synthesis to the user and waits for explicit approval:

> "From <source>, I understand you'd like to **<one-line
> intent>** — concretely, change `src/<pkg>/<file>.py` to
> **<method-outline-summary>**. Open gaps: **<bullets>**. Does
> this capture what you want before I hand it to the planner?"

The user's answer determines what happens next:

- **"Yes / confirm / go" → return the Proposal.** The parent
  skill drafts `journal/NN_*.md` from it.
- **"No / not quite / adjust X" → revise and re-confirm.** Iterate
  the synthesis until the user is happy. Do not return a Proposal
  the user hasn't signed off on.

This gate is non-optional. It is the user-side analogue of the
parent's design-note approval gate — it catches misunderstandings
*before* a design note is drafted, when the cost of revision is
cheapest.

## What is returned

A short structured block, not a design note:

```
Proposal (from: user via <article-link | resource-link | free-text>):
  Question:        <one sentence>
  Motivation:      <quote / URL / file path + the why-now reason>
  Source:          <article URL with claim | gh issue URL | spec file:line | user quote>
  Method outline:  <prose; which file in src/<pkg>/ is touched>
  Open gaps:       <transfer risks, dep questions, domain assertions
                    needing user confirmation, anything the source
                    didn't answer>
```

`iterate-ml-experiment` consumes this and drafts
`journal/NN_short_name.md`. **No `Success` field** — the skill
deliberately does not author acceptance criteria; the user judges
the result post-run.

## Companion skills

- **`iterate-ml-experiment`** — the caller; owns the design notes.
- **`iterate-from-skore`** — the only sibling strategy; sources
  the next experiment by mining the previous skore report into
  the Backlog.
- **`data-science-python-stack`** — consulted when an article
  introduces a new dependency (Stop conditions, above).
- **`build-ml-pipeline`** / **`evaluate-ml-pipeline`** — owners
  of the files (`pipeline.py`, `evaluate.py`, …) that the
  `Method outline` will eventually touch.
