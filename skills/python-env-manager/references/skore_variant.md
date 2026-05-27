# Python Env Manager — skore variant per mode

Why `skore` vs `skore[hub]` matters, and the procedure for switching
modes mid-project. Cross-referenced from SKILL.md § "Tier 1 install:
skore variant per mode".

## Why the variant matters

Hub mode calls `skore.login(mode="hub")` before instantiating
`skore.Project(...)`. That `login` flow is implemented in the
`[hub]` extra; on a plain `skore` install,
`from skore import login` raises `ImportError`.

Installing the wrong variant silently produces working CI for
local-mode operations but breaks hub-mode operations at first
`login()`.

## Reading the recorded decision

Before issuing the skore install command, read
`journal/JOURNAL.md` Status `Workspace decisions` for the
`skore mode:` row.

If the row is absent (workspace not yet bootstrapped through
`organize-ml-workspace`), route back to `organize-ml-workspace` §
G-SKORE-MODE — do not guess. The default proposal at G-SKORE-MODE
is `local`, but **the decision is the user's**, not the install
layer's.

## Forbidden

Silently picking `skore[hub]` "to be safe" or "because the user
might want hub later". The `[hub]` extra costs ~20 MB of network
deps + authentication infrastructure the local-mode user did not
ask for; the gate-based split exists to avoid that.

## Switching modes mid-project

If the user pivots `skore mode:` mid-project (per
`organize-ml-workspace` § "Switching skore mode mid-project is
forbidden by default" — requires explicit user confirmation):

- **`local` → `hub`**: run the manager's `add` command for
  `"skore[hub]"` over the existing install. The extra deps land
  additively; existing local-mode reports under `reports/` stay on
  disk but are no longer the active store.
- **`hub` → `local`**: optionally remove the hub extra to slim the
  env (`pixi remove skore` then `pixi add skore`, or the
  equivalent). Existing hub-mode reports stay on Skore Hub but are
  no longer the active store from this workspace.

In both directions, surface to the user that the prior store's
reports are orphaned from this workspace's perspective until a
manual migration.
