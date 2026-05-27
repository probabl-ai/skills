# python-api — Shape 1b LSP setup, Step 0 probe, footguns

Detail behind `SKILL.md` § "Shape 1b — LSP hover". Load before the
first Shape 1b use in a session, OR when an LSP probe is returning
unexpected results.

## Why Step 0 exists — session-startup ordering

The opencode LSP server reads `pyrightconfig.json` **once at
session startup**. If the config was written *during* the session
(e.g. as part of workspace scaffold), the LSP returns
`(import) <name>: Unknown` for every external library — not
because the install is broken, but because the server cached the
pre-config state.

**Re-editing the config will NOT fix this**; only a fresh opencode
session will. The fix is to **detect this state once at the top of
the session** and treat Shape 1b as unavailable from there.

## Step 0 — the probe

Make one LSP call to a known-installed library in a file the LSP
analyzes (`src/<pkg>/` is the safest; the bundled
`pyrightconfig.json` includes that path):

```
lsp(
    operation="hover",
    filePath="<absolute-path-to-an-included-source-file>",
    line=<a line with an external library import>,
    character=<the character offset of the imported symbol>,
)
```

## Step 0 — interpretation table

| Result | Decision for the rest of the session |
|---|---|
| `(function) def ...` / `(class) ...` / `(variable) ...` with a real type | Shape 1b is **available**. Use it for signature questions. |
| `(import) <name>: Unknown` for a library you know is installed | Shape 1b is **NOT available** this session. **Sticky decision: use Shape 1 (pydoc) for ALL signature questions until next opencode session.** Do NOT retry, do NOT edit `pyrightconfig.json`. The cause is session-startup ordering, not a config bug. |
| `No hover info` / empty result | Same as above — Shape 1b not available. |

## Stickiness is load-bearing

Once you've classified the session as "LSP unavailable", do not
flip-flop between shapes. A smaller model debugging "why isn't
hover working?" will burn turns editing the config; the rule
blocks that anti-pattern.

Cite the Step 0 decision in the pre-flight Evidence row:
`Evidence: lsp("hover", ...) returned <result> → Shape 1b
available | unavailable this session`.

## Footguns

### Conda-style envs need `pythonPath`, not `venvPath` + `venv`

pixi / conda envs have no `pyvenv.cfg`; pyright's
`venvPath` + `venv` resolution can fail silently on them. The
bundled `pyrightconfig.json` uses `pythonPath` for this reason.
Don't switch to `venvPath` + `venv` "to be more pyright-idiomatic"
— for managed envs, the interpreter path is the unambiguous form.

### Character offset is 1-based

Pyright uses **1-based** character offsets (matching VS Code's
column indicator). The first character of the symbol on its line
is `character=1`. Hovering at `character=0` may return no result.

### Pyright must see the module

If the LSP returns "no hover info" and the import line itself
shows red squiggles in your editor (and the session-startup
ordering above is OK), the `lsp` env doesn't have the package. Fix
the `pythonPath` in `pyrightconfig.json` or the `lsp` env's
composition before retrying.

### Scratch is excluded

The bundled `pyrightconfig.json` excludes `scratch/`, so probes
written there don't get diagnostics. For Shape 1b hover, the probe
file MUST live under `tests/` / `src/<pkg>/` / `experiments/` /
`audit/` — an included path.

The cleanest probe location for one-off hover queries is
`tests/_lookup_<lib>_<topic>.py` — pyright analyzes it; pytest's
`_`-prefix convention means `pytest tests/` ignores it.

### Dynamically generated symbols

Pyright statically analyzes imports; symbols defined only at
runtime (e.g. via `__getattr__` on a module, or registered late)
won't resolve. Fall through to Shape 1 — pydoc executes the code
and sees the real binding.

### C-extension types

Pyright relies on `.pyi` stub files for C extensions. Missing
stubs → empty hover. Pydoc still works via `__doc__` extraction
from the C symbol. Fall through to Shape 1.
