# Integration scenarios

A scenario is a seed workspace, an ordered list of user replies, a driver
file, and a filesystem snapshot after each reply. Manual replies work in
Claude Code, OpenCode, Cursor, GitHub Copilot, and Pi. `run` launches Pi
on the spine.

Install the workflow pack named by the scenario, materialize the seed
into an empty folder, and open that folder in the harness. Paste one
reply, let the agent stop, then check the folder against that turn. A
check uses only that turn's `expect` block. It is the full snapshot, not
a delta from the previous turn.

Forks are alternate replies. Copy the workspace after the turn named by
`after`, then paste the fork instead of the next spine reply.

## Layout

```text
integration/scenarios/<id>/
├── README.md
├── SCENARIO.md
├── turns.json
├── forks.json
└── seed/
```

`turns.json` names the scenario, the workflow pack, the seed directory,
the driver file, and the turns. Each turn has `id`, `say`, optional
`checkpoint`, and `expect`. `forks.json` lists `id`, `after`, `say`, and
`expect`. The driver is copied to the workspace root. It lists the spine
choices that `run` treats as already authorized.

`expect` keys:

| Key | Meaning |
| --- | --- |
| `files` | Each relative path or glob matches at least one path. |
| `absent` | Each path or glob matches nothing. |
| `contains` | That exact file contains every substring. |
| `contains_any` | One file matching the glob contains every substring. |

Paths are POSIX and stay inside the workspace. Substring checks should
use filled cells, not scaffold placeholders. Stem slugs stay globbed
because the agent chooses them.

`validate` also checks the seed directory against the `setup-open` turn,
which is the untouched seed.

## Commands

```bash
python tools/integration_scenario.py validate
python tools/integration_scenario.py materialize <scenario> --dest PATH
python tools/integration_scenario.py prompt <scenario> --turn <id>
python tools/integration_scenario.py prompt <scenario> --fork <id>
python tools/integration_scenario.py check <scenario> --workspace PATH --turn <id>
python tools/integration_scenario.py run <scenario> --workspace PATH
```

`prompt` writes the reply to stdout. Checkpoint turns also print a copy
reminder on stderr. `materialize` refuses a non-empty destination unless
`--force` is set. `run` materializes an absent or empty workspace, refuses
a non-empty one unless `--reuse-workspace` is set, and copies the driver
when a reused workspace does not already contain it.

## Automated run

`run` starts one harness and sends one prompt: read `SCENARIO.md` and
carry out that journey. It does not type later replies. `--interactive`
inherits the terminal so the normal TUI is visible and can be interrupted.
The default is headless: output is streamed and also saved.

```bash
python tools/integration_scenario.py run california-housing --workspace ../housing
python tools/integration_scenario.py run california-housing \
  --workspace ../housing --interactive
```

`run` always launches Pi. Manual prompt and check stay available for any
harness. Optional `--model` is passed through. Pi defaults to
`--provider openrouter` and `--model ~deepseek/deepseek-flash-latest`
when `--model` is omitted. Repeat `--harness-arg` once per extra token.
A `--model` or `--provider` token there replaces that default.
`--timeout` defaults to 3600 seconds and then terminates the process
group. Ctrl-C does the same.

Pi uses its existing login. This command does not install Pi. Pi runs
require the skill-tool extension:

```bash
pi install npm:@probabl/pi-skore
```

Headless Pi uses `--mode json`. `--interactive` inherits the terminal
and shows the TUI. Pi reads the driver with `--append-system-prompt`.

`--approve` trusts project-local files for this workspace. Pi does not
ask before every tool call. Before Pi starts, the runner writes the
selected workflow's sidecars under `.agents/skills`, passes every
checkout skill with `--skill`, and prepends the checkout's `src` to
`PYTHONPATH`. Skill discovery and trust therefore happen before
`before_agent_start`; the agent uses the `skill` tool and does not need
to reload or read `SKILL.md` directly. The scenario may run
package-manager commands such as `pixi`.

Logs land in `.transcripts/integration/<run-id>/`: headless `stdout.txt`
and `stderr.txt`, plus `result.json` with the harness, mode, duration,
exit status, and check errors. After a harness exit of 0, `run` checks
`iterate-stop`. A missing executable exits 127, timeout exits 124, and
interruption exits 130. A failing harness status is returned as-is and
skips that check. A passing harness with a failed final check exits 1.

The first scenario is [california-housing](scenarios/california-housing/README.md).
