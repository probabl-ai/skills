# Organize ML Workspace — G-SKORE-MODE in detail

Full deep dive on the Skore Project mode gate. SKILL.md carries the
compact gate definition; this reference is for the moment you need
to actually fill the `<SKORE_PROJECT_INIT>` substitution or debug a
hub-vs-local mismatch.

Cross-referenced from `SKILL.md` § Stop conditions and § Decision
flow step 2a, and from `python-env-manager` § Tier 1 install
(skore variant), `audit-ml-pipeline` § Read-only contract.

## Project init forms — concrete side-by-side

The three forms are not "swap one word" variants; the argument shape
changes per mode.

### Local mode (default)

```python
import skore

from <pkg> import PROJECT_ROOT

project = skore.Project(
    name="<project-name>",
    mode="local",
    workspace=str(PROJECT_ROOT / "reports"),
)
```

### Hub mode

```python
import skore
from skore import login

# Interactive on first run (browser or API key); cached after.
login(mode="hub")

project = skore.Project(
    "<hub-workspace>/<project-name>",
    mode="hub",
)
```

### MLflow mode

```python
import skore

# No login() — auth (if any) is the MLflow server's concern.
project = skore.Project(
    name="<experiment-name>",
    mode="mlflow",
    tracking_uri="<mlflow-tracking-uri>",
)
```

`name=` is the **MLflow experiment name**; reports persist as MLflow
model artifacts in runs created under that experiment. `tracking_uri=`
is an **mlflow-only** kwarg — the URI of the MLflow tracking server
(e.g. `http://127.0.0.1:5000`, `https://mlflow.acme.internal`, or a
`file:./mlruns` / `sqlite:///mlflow.db` local backend). The
`project.put("<key>", report)` `key` becomes the **run name**.
Source: https://docs.skore.probabl.ai/stable/reference/api/skore.Project.html

### Diff at a glance

| Concern | Local | Hub | MLflow |
|---|---|---|---|
| `import` line for `login` | not needed | `from skore import login` | not needed |
| `login(mode="hub")` call | not needed | **required, before `Project(...)`** | not needed |
| `name=` argument | `name="<project-name>"` (bare) | `"<hub-workspace>/<project-name>"` (positional, slash-joined) | `name="<experiment-name>"` (MLflow experiment name) |
| `mode=` argument | `mode="local"` | `mode="hub"` | `mode="mlflow"` |
| `workspace=` argument | **required**: `workspace=str(PROJECT_ROOT / "reports")` | **MUST be absent** — passing it raises `TypeError` | **MUST be absent** — `tracking_uri=` is used instead |
| `tracking_uri=` argument | not used | not used | **required**: the MLflow tracking server URI |
| Install variant | `pixi add skore` | `pixi add "skore[hub]"` | `pixi add "skore[mlflow]"` |
| Pre-condition | none | Skore Hub account + access to `<hub-workspace>` | reachable MLflow tracking server at `<uri>` |

## The gate — AskUserQuestion shape

Fires at workspace scaffold, alongside G-PKG-NAME / G-TABULAR /
G-ENV-MGR (per `SKILL.md` § Decision flow step 2a). Never silent —
even if the user has used skore in `local` mode in prior projects.

### Structured pick with default and follow-up

1. **Mode.** Options:
   - `local` — artifacts on disk, no account needed, recommended
     for solo work.
   - `hub` — artifacts on https://skore.probabl.ai, requires
     account + workspace access, recommended for team
     collaboration.
   - `mlflow` — artifacts pushed to an MLflow tracking server (the
     skore `skore[mlflow]` backend integration), recommended when
     the team already runs MLflow or standardizes on it for
     experiment storage.

   Default proposal: `local`.

2. **Hub workspace name** (only when mode is `hub`). Free-form
   string — the org/team identifier on Skore Hub. The agent cannot
   infer this from the local environment; the user must know it
   (it's the workspace they've been granted access to). If the
   user picks `hub` without knowing the workspace name, surface
   that they need to create or join one at
   https://skore.probabl.ai first.

   **Validation**: the workspace name MUST NOT contain `/` — the
   slash is reserved as the separator between `<hub-workspace>`
   and `<project-name>` in the hub-mode `name=` argument (e.g.
   `"acme-corp/load-forecast"`). If the user types `acme/datasci`,
   ask whether `acme` was the intended workspace and `datasci` is
   part of the project name. Do not silently accept slashes — that
   produces an unparseable Project name at runtime.

3. **MLflow tracking URI** (only when mode is `mlflow`). Free-form
   string — the `tracking_uri=` passed to `skore.Project(...)`.
   The agent **cannot** infer the server address; the user must
   supply it. Accept the forms MLflow itself accepts:
   - an HTTP(S) tracking server — `http://127.0.0.1:5000`,
     `https://mlflow.acme.internal`;
   - a database backend — `sqlite:///mlflow.db`,
     `postgresql://…`;
   - a local file store — `file:./mlruns` or an absolute `file:`
     path.

   If the user picks `mlflow` without knowing the URI, surface that
   they need a running tracking server (or a local backend path)
   before reports can be pushed — do NOT default the URI silently.
   A bare host:port without a scheme (e.g. `localhost:5000`) should
   be confirmed as `http://localhost:5000` rather than passed
   verbatim.

### Free-text resolution

- Explicit naming of `local` / `hub` / `mlflow` resolves
  immediately.
- "use the cloud one" / "store remotely" → `hub`.
- "store locally" / "no account" → `local`.
- "push to mlflow" / "our mlflow server" / "track in mlflow" →
  `mlflow` (then ask for the tracking URI).
- Urgency phrasing ("quick" / "you pick") does NOT resolve — falls
  through to the structured ask.

## What the gate determines

The recorded `skore mode:` decision drives three downstream
artifacts:

| Downstream artifact | local-mode shape | hub-mode shape | mlflow-mode shape |
|---|---|---|---|
| `<SKORE_PROJECT_INIT>` in `experiments/NN_*.py` and `audit/NN_*.py` | `skore.Project(name="<project-name>", mode="local", workspace=str(PROJECT_ROOT / "reports"))` | `from skore import login; login(mode="hub"); skore.Project("<hub-workspace>/<project-name>", mode="hub")` | `skore.Project(name="<experiment-name>", mode="mlflow", tracking_uri="<mlflow-tracking-uri>")` |
| Tier 1 skore install variant (per `python-env-manager` § Tier 1 install) | `pixi add skore` (or equivalent) | `pixi add "skore[hub]"` (or equivalent) | `pixi add "skore[mlflow]"` (or equivalent) |
| `Workspace decisions` rows in `JOURNAL.md` | `skore mode: local` | `skore mode: hub` + `skore hub workspace: <name>` | `skore mode: mlflow` + `skore mlflow tracking uri: <uri>` |

The `name=` argument shape **changes between modes** — local uses a
bare name; hub uses `<hub-workspace>/<project>`; mlflow uses the
MLflow experiment name. The local-mode `workspace=` kwarg points to a
directory and is rejected by both hub and mlflow modes; mlflow takes
`tracking_uri=` instead. These are not "swap one word" differences;
the substitution marker exists precisely because the shape changes.

## Persistence in `Workspace decisions`

Three rows (only the one matching the chosen mode carries a value;
the other follow-up row is `n/a`):

```
- skore mode: <local | hub | mlflow> — recorded: <YYYY-MM-DD>
- skore hub workspace: <hub-workspace-name | n/a> — recorded: <YYYY-MM-DD>
- skore mlflow tracking uri: <mlflow-tracking-uri | n/a> — recorded: <YYYY-MM-DD>
```

The hub-workspace row carries `n/a` unless mode is `hub`; the
mlflow-tracking-uri row carries `n/a` unless mode is `mlflow`. On
every later session, skills that need the mode read these rows first
and skip re-asking — the standard `Workspace decisions` lookup
pattern (see `iterate-ml-experiment` template § Status).

## Switching mid-project

See the SKILL.md Stop condition "Switching skore mode mid-project
is forbidden by default". The short version: switching orphans
reports in the prior store (no built-in migration in skore between
modes).

Procedure:

1. Fire `AskUserQuestion` surfacing the migration burden:
   "Existing reports under <prior mode> will become inaccessible
   from this workspace. Proceed anyway? (y / n / migrate manually
   first)".
2. Only on explicit user confirmation, update the
   `Workspace decisions` row.
3. Rewrite **every** `<SKORE_PROJECT_INIT>` block in `experiments/`
   AND `audit/`.
4. Update the install variant via `python-env-manager` (plain
   `skore` ↔ `skore[hub]` ↔ `skore[mlflow]`).
5. Document the switch in `JOURNAL.md` History as a horizontal
   divider (same shape as goal pivots — see `iterate-ml-experiment`
   § Maintenance modes).

## Anatomy of the substitution

The `<SKORE_PROJECT_INIT>` marker is a **comment line** inside the
template that signals the start of the Project init block. The
substitution replaces the comment AND the block that follows it
(up to the next blank line) with the mode-appropriate code. The
marker comment itself **is removed** in the substituted file —
it's not a permanent anchor, it's a scaffold-time signal.

### Before substitution (`templates/experiment.py`)

```python
# %%
# <SKORE_PROJECT_INIT>
project = skore.Project(
    name="<project-name>",
    mode="local",
    workspace=str(PROJECT_ROOT / "reports"),
)
```

### After substitution — local mode

Replacing `<project-name>`, keeping the rest:

```python
# %%
project = skore.Project(
    name="load-forecast",
    mode="local",
    workspace=str(PROJECT_ROOT / "reports"),
)
```

### After substitution — hub mode

The whole block (including the `# %%` cell marker) is rewritten to
include the `login` call AND the new `Project` shape:

```python
# %%
from skore import login

login(mode="hub")
project = skore.Project(
    "acme-corp/load-forecast",
    mode="hub",
)
```

Note that in the hub form:

- `workspace=` is **gone** (would raise `TypeError`).
- `name=` becomes positional and uses the slash-joined
  `<hub-workspace>/<project-name>` shape.
- `login(...)` precedes `Project(...)` in the same cell so a
  single execution does both.

### After substitution — mlflow mode

The block is rewritten to drop `workspace=` and add the
`tracking_uri=` recorded at G-SKORE-MODE. No `login(...)`:

```python
# %%
project = skore.Project(
    name="load-forecast",
    mode="mlflow",
    tracking_uri="http://127.0.0.1:5000",
)
```

Note that in the mlflow form:

- `workspace=` is **gone** — `tracking_uri=` replaces it.
- `name=` is the **MLflow experiment name** (bare, no slash join).
- no `login(...)` — authentication, if any, is the MLflow server's
  concern, handled out-of-band (env vars / server config), not by
  skore.
- `project.put("<stem>", report)` creates a run named `<stem>`
  under the experiment.

### Audit-file copy rule

For `audit/<stem>.py`: the same substitution rule applies, but with
one extra constraint — the substituted block must match what
`experiments/<stem>.py` actually contains, byte-for-byte (modulo
formatting). Read the experiment file first, copy its Project init
block, paste into the audit's substitution marker.

**Do not re-derive from the `skore mode:` decision alone** — a typo
or formatting drift would silently open a different Project. See
the `audit-ml-pipeline` Forbidden shortcuts row "Substituting
`<SKORE_PROJECT_INIT>` in audit independently of the experiment".

## Out of scope

- **Running / provisioning the MLflow server.** When the user picks
  `mlflow`, the gate captures the `tracking_uri=` but does NOT
  stand up the tracking server, create the backing database, or
  configure object storage. A reachable server (or a local
  `file:`/`sqlite:` backend) at the supplied URI is the user's
  responsibility — surface that pre-condition rather than spinning
  one up.

- **MLflow `delete`.** `skore.Project.delete(...)` is not
  implemented for mlflow-mode projects. The read-back contract
  (`summarize()` → `get(id)`) still holds; deletions must be done
  through MLflow's own tooling.

- **Skore Hub account creation.** The gate assumes the user has an
  account when they pick `hub`. Sign-up is a probabl.ai concern
  (https://probabl.ai/skore); this skill won't drive the user
  through it.
