# Python Env Manager — Composition model rationale

Why the workspace gets four composed envs (`default` / `dev` /
`agent` / `lsp`) and why `lsp` is structurally separate from
`agent`. Cross-referenced from SKILL.md § "Where does the package
belong?" and § "Auto-routing table".

## Why `lsp` is separate from `agent`

The `agent` feature exists for the audit runner and CLI pyright
invocations — its env is `default + agent`. But pyright as an LSP
needs to resolve imports the user writes in `tests/` (pytest),
`src/` (runtime), `audit/` (ipython), AND any optional feature.

The `lsp` env composes **all** features so pyright sees everything
in one site-packages search path. Without this composition pyright
would report false "unresolved import" warnings on legitimate code.

The two envs are intentionally separate:

- `agent` stays focused on the audit runner's runtime; it doesn't
  grow on every optional-feature addition.
- `lsp` is the only env that grows on every optional-feature
  addition.

## Growth on optional-feature addition

Each new optional feature (per `SKILL.md` § "G-ENV-SCOPE — new
named feature" 6-step procedure) is **also** added to the `lsp`
env's features list:

```toml
[environments]
default = { features = ["default"],                                       solve-group = "default" }
dev     = { features = ["default", "dev"],                                solve-group = "default" }
agent   = { features = ["default", "agent"],                              solve-group = "default" }
lsp     = { features = ["default", "dev", "agent", "tracing", "tuning"],  solve-group = "default" }
```

Step 3 of the new-feature procedure (append `<X>` to `lsp`'s
features list) is the load-bearing step. Skipping it produces the
silent failure: the package is installable into the new env but
pyright doesn't index it because `lsp` doesn't compose it.

## Why this is fixed (no per-install ask)

Earlier versions of this stack asked the user per install. That
produced friction without value: the right routing is mechanical
(runtime vs dev vs agent), and the only interesting decision is
the rare ambiguous extra. The fixed layout is also what makes the
LSP config and the audit runner work without per-workspace
ceremony.
