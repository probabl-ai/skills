---
name: iterate-from-literature
description: >
  Source the next ML experiment proposal by searching the
  scientific / engineering literature (papers, blog posts,
  library docs) for techniques applicable to the current
  problem. Hand the proposal back to `iterate-ml-experiment`,
  which writes it into `plan/NN_short_name.md` and seeks the
  user's approval. Stops at "a proposal (question, motivation,
  method outline, source citations) has been returned"; does not
  write any plan file itself, and does not author acceptance
  criteria — the user judges the result.

  TRIGGER when: `iterate-ml-experiment` is picking a sourcing
  strategy and the user asks "any papers on this?", "what does
  the literature say?", "how do people usually handle X?", or
  "search for techniques for Y"; the user has run out of obvious
  next steps and is open-ended; a sibling strategy
  (methodology / diagnostic) has surfaced a problem with no
  obvious in-house fix and external prior art would help.

  SKIP when: the user has a concrete idea already (use
  `iterate-from-user`); the gap is clearly methodological and
  internally fixable (use `iterate-from-methodology`); the
  diagnostic clearly points to an in-pipeline issue (use
  `iterate-from-diagnostic`); web access is unavailable in this
  environment — surface the gap and fall back to a different
  strategy.

  HOW TO USE: this skill is shallow. Frame the search around the
  current problem (dataset shape, target type, the failure mode
  you're trying to fix). Use `WebSearch` and `WebFetch` to find
  candidate techniques; **cite concretely** (paper title, year,
  URL, the exact claim you'd build on). Filter aggressively —
  one or two candidates that match the data are more useful than
  ten general ideas. Return a proposal in the structured shape
  below; do not write any plan file.
---

# Iterate from literature

Source: external prior art (papers, library docs, blog posts).
Output: a proposal handed back to `iterate-ml-experiment`,
backed by concrete citations.

## Output contract (read this before the body)

This skill **never writes `plan/` files**. It returns one of
two payloads back to `iterate-ml-experiment`:

- **Proposal — found a transferable technique** (full shape in
  § What is returned at the bottom): `Question`, `Motivation`,
  `Source(s)`, `Method outline`, `Success`, `Transfer risks`.
  Required: every `Source` carries a paper / doc / post title
  + URL + the exact claim. **New dependencies introduced by
  the proposal must be surfaced as a question in `Method`,
  not silently included.** Domain-specific assertions
  (monotonicity, target semantics, …) must be flagged
  `[needs user confirmation]` in `Risks`.
- **Empty search — no transferable prior art:** if the search
  surfaces nothing that ports cleanly to the current data
  shape, return the literal payload
  `{ "outcome": "literature_empty", "queries": [...],
  "considered": [<short list of titles ruled out and why>] }`
  (see § Stop conditions). Don't invent a weak proposal to
  fill the slot.

## Stop conditions

- **Don't write `plan/` files.** That belongs to
  `iterate-ml-experiment`.
- **Don't propose without a citation.** Every method idea must
  carry a paper / doc / post title and URL. "It's well known
  that X" is not acceptable.
- **Don't generalize past the data.** A technique demonstrated
  on a different modality or a much larger dataset may not
  transfer. State the original setting and flag the transfer
  risk.
- **Don't pile on candidates.** Return one well-matched
  proposal (or two only when they're complementary, not
  alternatives). The user can ask for alternatives in a
  follow-up.
- **An empty search is a real outcome.** If the search surfaces
  no transferable techniques (e.g., the relevant literature is
  on a different modality or scale, none of it ports cleanly to
  the current data shape), return the literal payload
  `{ "outcome": "literature_empty", "queries": [...],
  "considered": [<short list of titles you ruled out and why>] }`
  instead of a proposal. This is not a failure — it tells the
  parent skill "no actionable prior art on this turn." Do not
  invent a weak proposal just to have something to return.
- **New dependencies are gated, not assumed.** If the proposal's
  Method requires a library outside the project's existing env
  (e.g., the paper used `lightgbm` / `pytorch` / `jax`), do
  **not** silently include it in Method as a fait accompli.
  State the dep as a question in Method (`"this approach needs
  <library>; OK to add, or should we adapt to existing
  <substitute>?"`), and defer the resolution to
  `data-science-python-stack` (substitute fit) and the user
  (final call). The parent skill blocks approval until the dep
  question is answered.
- **Domain-specific assertions need user confirmation.** If the
  proposal asserts something that requires domain knowledge
  the literature alone can't establish — e.g., "feature X is
  monotone in the target," "interaction Y matters for this
  asset class," "metric Z is appropriate because the use case
  is one-sided" — flag each assertion in the **Risks** section
  with `[needs user confirmation]`. The parent skill blocks
  approval until the user has answered each flag. Don't ship
  paper-flavored guesses as facts.

## The search loop

1. **Frame the search.** Pull from `plan/PLAN.md` (status block)
   and the most recent `plan/NN_*.md`: dataset shape, target
   type, last experiment's failure mode. The query is "techniques
   for <failure mode> on <data shape>", not just "techniques for
   <task>".
2. **Search.** Use `WebSearch` for breadth, `WebFetch` for the
   one or two pages that look most relevant. Prefer:
   - peer-reviewed papers,
   - well-known library docs (sklearn, skrub, PyTorch, etc.),
   - established blog posts / talks from authors with track
     record on this kind of data.
3. **Filter for transfer.** For each candidate, ask: does the
   original setting (data size, modality, target) match ours?
   If not, can the technique still be relevant? Be honest —
   note where it might not transfer.
4. **Checkpoint with the user when the search is plural.** If
   the filtered shortlist has **more than one credible
   direction** (e.g., monotonic GBM *vs.* deep-hedging-style
   NN *vs.* shape-constrained quantile regression), do not
   pick silently. Surface the shortlist as a one-line-per-
   candidate summary with the citation and the trade-off
   (cost / fit / risk), and ask the user to pick one. Then
   draft the structured proposal for that one. If the
   shortlist has exactly one credible direction, skip the
   checkpoint and go to step 5. The goal is to spend turns on
   one well-understood proposal, not on a generic survey.
5. **Synthesize the proposal.** It carries:
   the technique, the citation, why it matches our failure
   mode, and what we'd actually change in `src/<pkg>/`. **Do
   not author a "success criterion" here** — the skill stops
   at the method intent; the user judges the result post-run.

## What is returned

A short structured block, not a plan file:

```
Proposal (from: literature):
  Question:        <one sentence — what would adopting this technique tell us?>
  Motivation:      <our failure mode + why this technique addresses it>
  Source(s):       <paper / doc title, year, URL — paste the exact claim>
  Method outline:  <prose; which file in src/<pkg>/ is touched>
  Transfer risks:  <where the original setting differs from ours>
```

`iterate-ml-experiment` consumes this and drafts
`plan/NN_short_name.md` (with the source URLs preserved).

## Companion skills

- **`iterate-ml-experiment`** — the caller; owns the plan file.
- **`iterate-from-user` / `iterate-from-methodology` /
  `iterate-from-diagnostic`** — sibling strategies.
