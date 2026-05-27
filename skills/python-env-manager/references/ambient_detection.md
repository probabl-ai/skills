# Python Env Manager — Ambient detection

Load when § Detection in `SKILL.md` returns `(nothing detected)` at
the project root — before defaulting to "pixi recommendation".

## The problem

A bare project root often sits on top of a developer machine that
already has one or more managers installed and existing envs the
user might want to reuse. Defaulting to a fresh pixi bootstrap when
an existing conda env could have served is a frequent ergonomic
miss.

## The probe

```bash
command -v pixi uv poetry hatch conda mamba
conda env list 2>/dev/null   # if conda/mamba is on PATH
```

## When to ask via AskUserQuestion

If **two or more** managers are on PATH, **or** there are existing
conda envs that already carry parts of the stack (sklearn / skrub /
skore), surface the situation via `AskUserQuestion`. Offer at least
these branches:

- **Bootstrap a fresh pixi project** — the default recommendation
  when nothing has to be reused.
- **Reuse an existing env** — if `conda env list` shows an env with
  the stack already installed (or close to it). Name the envs in
  the option descriptions so the user can see what's on offer.
- **Bootstrap a different manager** — uv / poetry / hatch / conda
  when the user's team standard differs from pixi.

The contract: "no project-root signals" does not mean "no relevant
state." The `AskUserQuestion` exists to surface that choice rather
than presume it.
