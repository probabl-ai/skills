"""Copy, print, check, and run harness-neutral integration scenarios.

A scenario is a seed workspace, ordered user replies, a driver file, and
filesystem snapshots. ``run`` launches Pi. It does not install Pi.

Usage
-----
    python tools/integration_scenario.py validate
    python tools/integration_scenario.py materialize <scenario> --dest PATH
    python tools/integration_scenario.py prompt <scenario> --turn ID
    python tools/integration_scenario.py prompt <scenario> --fork ID
    python tools/integration_scenario.py check <scenario> --workspace PATH --turn ID
    python tools/integration_scenario.py run <scenario> --workspace PATH

Exits 0 on success, 1 on the first batch of errors.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.integration_harness import (  # noqa: E402
    HarnessError,
    build_launch,
    execute_launch,
)

CHECKOUT_ROOT = Path(__file__).resolve().parent.parent
SCENARIOS_ROOT = CHECKOUT_ROOT / "integration" / "scenarios"
REPO_ROOT = SCENARIOS_ROOT.parent.parent
EXPECT_KEYS = frozenset({"files", "absent", "contains", "contains_any"})
TURN_KEYS = frozenset({"id", "say", "checkpoint", "expect"})
FORK_KEYS = frozenset({"id", "after", "say", "expect"})
SEED_CHECK_TURN = "setup-open"
FINAL_TURN = "iterate-stop"
SKILLS_REPO_PLACEHOLDER = "{{SKILLS_REPO}}"
SKILLS_REPO_URI_PLACEHOLDER = "{{SKILLS_REPO_URI}}"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _scenario_dirs() -> list[Path]:
    if not SCENARIOS_ROOT.is_dir():
        return []
    return sorted(path for path in SCENARIOS_ROOT.iterdir() if path.is_dir())


def _relative_error(value: str) -> str | None:
    if not isinstance(value, str) or not value or value.startswith(("/", "\\")):
        return "must be a non-empty relative path"
    if "\\" in value or ":" in value:
        return "must use POSIX relative paths"
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        return "must stay inside the workspace"
    return None


def _string_list(raw: Any, label: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(raw, list) or not all(isinstance(item, str) for item in raw):
        return [f"{label} must be a list of strings"]
    for item in raw:
        problem = _relative_error(item)
        if problem:
            errors.append(f"{label} entry {item!r}: {problem}")
    return errors


def _pattern_map(raw: Any, label: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(raw, dict):
        return [f"{label} must be an object"]
    for key, value in raw.items():
        if not isinstance(key, str):
            errors.append(f"{label} keys must be strings")
            continue
        problem = _relative_error(key)
        if problem:
            errors.append(f"{label} key {key!r}: {problem}")
        if (
            not isinstance(value, list)
            or not value
            or not all(isinstance(item, str) and item for item in value)
        ):
            errors.append(f"{label} {key!r} must be a non-empty list of strings")
    return errors


def _parse_expect(raw: Any, label: str) -> list[str]:
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        return [f"{label}: expect must be an object"]
    errors: list[str] = []
    unknown = sorted(set(raw) - EXPECT_KEYS)
    if unknown:
        errors.append(f"{label}: unknown expect keys {unknown}")
    errors.extend(_string_list(raw.get("files", []), f"{label} files"))
    errors.extend(_string_list(raw.get("absent", []), f"{label} absent"))
    errors.extend(_pattern_map(raw.get("contains", {}), f"{label} contains"))
    errors.extend(_pattern_map(raw.get("contains_any", {}), f"{label} contains_any"))
    return errors


def _load_scenario(directory: Path) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    errors: list[str] = []
    turns_path = directory / "turns.json"
    forks_path = directory / "forks.json"
    if not turns_path.is_file():
        return {}, {}, [f"{directory.name}: missing turns.json"]
    if not forks_path.is_file():
        return {}, {}, [f"{directory.name}: missing forks.json"]
    try:
        turns = _load_json(turns_path)
        forks = _load_json(forks_path)
    except json.JSONDecodeError as exc:
        return {}, {}, [f"{directory.name}: invalid JSON ({exc})"]
    if not isinstance(turns, dict) or not isinstance(forks, dict):
        return {}, {}, [f"{directory.name}: turns.json and forks.json must be objects"]
    return turns, forks, errors


def validate_scenario(directory: Path) -> list[str]:
    """Return validation errors for one scenario directory."""
    turns_doc, forks_doc, errors = _load_scenario(directory)
    if errors:
        return errors
    name = directory.name
    if turns_doc.get("id") != name:
        errors.append(f"{name}: turns.json id must be {name!r}")
    driver_name = turns_doc.get("driver")
    if not isinstance(driver_name, str) or _relative_error(driver_name):
        errors.append(f"{name}: driver must be a relative file")
    elif not (directory / driver_name).is_file():
        errors.append(f"{name}: driver {driver_name!r} is missing")
    seed_name = turns_doc.get("seed")
    if not isinstance(seed_name, str) or _relative_error(seed_name):
        errors.append(f"{name}: seed must be a relative directory")
        seed = None
    else:
        seed = directory / seed_name
        if not seed.is_dir() or not any(seed.iterdir()):
            errors.append(f"{name}: seed {seed_name!r} is missing or empty")
    turns = turns_doc.get("turns")
    if not isinstance(turns, list) or not turns:
        return errors + [f"{name}: turns must be a non-empty list"]
    seen: set[str] = set()
    setup_open: dict[str, Any] | None = None
    for index, turn in enumerate(turns):
        label = f"{name} turn[{index}]"
        if not isinstance(turn, dict):
            errors.append(f"{label} must be an object")
            continue
        unknown = sorted(set(turn) - TURN_KEYS)
        if unknown:
            errors.append(f"{label}: unknown keys {unknown}")
        turn_id = turn.get("id")
        if not isinstance(turn_id, str) or not turn_id:
            errors.append(f"{label}: id must be a non-empty string")
        elif turn_id in seen:
            errors.append(f"{name}: duplicate turn id {turn_id!r}")
        else:
            seen.add(turn_id)
            label = f"{name} turn {turn_id}"
        if turn_id == SEED_CHECK_TURN:
            setup_open = turn
        say = turn.get("say")
        if not isinstance(say, str) or not say.strip():
            errors.append(f"{label}: say must be a non-empty string")
        if "checkpoint" in turn and not isinstance(turn.get("checkpoint"), bool):
            errors.append(f"{label}: checkpoint must be a boolean")
        if "expect" not in turn:
            errors.append(f"{label}: expect is required")
        else:
            errors.extend(_parse_expect(turn.get("expect"), label))
    if setup_open is None:
        errors.append(f"{name}: missing {SEED_CHECK_TURN} turn")
    forks = forks_doc.get("forks")
    if not isinstance(forks, list):
        errors.append(f"{name}: forks must be a list")
        forks = []
    seen_forks: set[str] = set()
    for index, fork in enumerate(forks):
        label = f"{name} fork[{index}]"
        if not isinstance(fork, dict):
            errors.append(f"{label} must be an object")
            continue
        unknown = sorted(set(fork) - FORK_KEYS)
        if unknown:
            errors.append(f"{label}: unknown keys {unknown}")
        fork_id = fork.get("id")
        if not isinstance(fork_id, str) or not fork_id:
            errors.append(f"{label}: id must be a non-empty string")
        elif fork_id in seen_forks:
            errors.append(f"{name}: duplicate fork id {fork_id!r}")
        else:
            seen_forks.add(fork_id)
            label = f"{name} fork {fork_id}"
        after = fork.get("after")
        if not isinstance(after, str) or after not in seen:
            errors.append(f"{label}: after must name a turn")
        say = fork.get("say")
        if not isinstance(say, str) or not say.strip():
            errors.append(f"{label}: say must be a non-empty string")
        if "expect" not in fork:
            errors.append(f"{label}: expect is required")
        else:
            errors.extend(_parse_expect(fork.get("expect"), label))
    if seed is not None and setup_open is not None and not errors:
        errors.extend(
            f"{name} seed vs {SEED_CHECK_TURN}: {item}"
            for item in check_workspace(seed, setup_open.get("expect") or {})
        )
    return errors


def _is_glob(pattern: str) -> bool:
    return any(char in pattern for char in "*?[")


def _matched(root: Path, pattern: str) -> list[Path]:
    if _is_glob(pattern):
        return sorted(path for path in root.glob(pattern) if path.exists())
    path = root / pattern
    return [path] if path.exists() else []


def _read_text(path: Path) -> tuple[str | None, str | None]:
    """Return ``(text, problem)``. ``problem`` is None when ``text`` is set."""
    if not path.is_file():
        return None, "missing"
    try:
        return path.read_text(encoding="utf-8"), None
    except UnicodeDecodeError:
        return None, "not UTF-8 text"


def check_workspace(root: Path, expect: dict[str, Any]) -> list[str]:
    """Return filesystem mismatches for ``expect`` under ``root``."""
    errors: list[str] = []
    if not root.is_dir():
        return [f"workspace does not exist: {root}"]
    for pattern in expect.get("files") or []:
        if not _matched(root, pattern):
            errors.append(f"missing {pattern}")
    for pattern in expect.get("absent") or []:
        found = _matched(root, pattern)
        if found:
            shown = ", ".join(str(path.relative_to(root)) for path in found)
            errors.append(f"expected absent {pattern} (found {shown})")
    for path_name, needles in (expect.get("contains") or {}).items():
        text, problem = _read_text(root / path_name)
        if problem == "missing":
            errors.append(f"missing {path_name}")
            continue
        if problem is not None or text is None:
            errors.append(f"{path_name} is {problem}")
            continue
        for needle in needles:
            if needle not in text:
                errors.append(f"{path_name} missing substring: {needle}")
    for pattern, needles in (expect.get("contains_any") or {}).items():
        files = [path for path in _matched(root, pattern) if path.is_file()]
        if not files:
            errors.append(f"no file matches {pattern}")
            continue
        texts: list[str] = []
        for path in files:
            text, problem = _read_text(path)
            if problem is not None or text is None:
                errors.append(f"{path.relative_to(root)} is {problem}")
                continue
            texts.append(text)
        matched = any(
            all(needle in text for needle in needles) for text in texts
        )
        if texts and not matched:
            joined = ", ".join(needles)
            errors.append(f"no file matching {pattern} contains: {joined}")
    return errors


def _require_scenario(name: str) -> Path:
    directory = SCENARIOS_ROOT / name
    if not directory.is_dir():
        known = ", ".join(path.name for path in _scenario_dirs()) or "(none)"
        raise SystemExit(f"unknown scenario {name!r}; known: {known}")
    return directory


def _entries(directory: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    turns_doc, forks_doc, errors = _load_scenario(directory)
    if errors:
        raise SystemExit("\n".join(errors))
    turns = turns_doc.get("turns")
    forks = forks_doc.get("forks")
    if not isinstance(turns, list) or not isinstance(forks, list):
        raise SystemExit(f"{directory.name}: invalid turns or forks")
    return turns, forks


def _find(items: list[dict[str, Any]], item_id: str, kind: str) -> dict[str, Any]:
    for item in items:
        if item.get("id") == item_id:
            return item
    known = ", ".join(str(item.get("id")) for item in items)
    raise SystemExit(f"unknown {kind} {item_id!r}; known: {known}")


def _print_say(entry: dict[str, Any]) -> None:
    say = str(entry["say"])
    sys.stdout.write(say if say.endswith("\n") else say + "\n")
    if entry.get("checkpoint") is True:
        print(
            "Checkpoint: copy this workspace before trying a fork.",
            file=sys.stderr,
        )


def validate_all() -> list[str]:
    """Validate every scenario and the untouched-seed snapshot."""
    directories = _scenario_dirs()
    if not directories:
        return [f"no scenarios under {SCENARIOS_ROOT}"]
    errors: list[str] = []
    for directory in directories:
        errors.extend(validate_scenario(directory))
    return errors


def materialize(name: str, dest: Path, *, force: bool) -> None:
    """Copy the scenario seed to ``dest``."""
    directory = _require_scenario(name)
    turns_doc, _, errors = _load_scenario(directory)
    if errors:
        raise SystemExit("\n".join(errors))
    seed_name = turns_doc.get("seed")
    if not isinstance(seed_name, str):
        raise SystemExit(f"{name}: seed is missing")
    seed = directory / seed_name
    if dest.exists() and not dest.is_dir():
        raise SystemExit(f"destination is not a directory: {dest}")
    if dest.is_dir() and any(dest.iterdir()):
        if not force:
            raise SystemExit(f"destination is not empty: {dest}")
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(seed, dest, dirs_exist_ok=True)
    _copy_driver(directory, turns_doc, dest)
    print(f"materialized {name} at {dest}")


def _copy_driver(directory: Path, turns_doc: dict[str, Any], dest: Path) -> Path:
    driver_name = turns_doc.get("driver")
    if not isinstance(driver_name, str):
        raise SystemExit(f"{directory.name}: driver is missing")
    source = directory / driver_name
    if not source.is_file():
        raise SystemExit(f"{directory.name}: driver {driver_name!r} is missing")
    target = dest / Path(driver_name).name
    repo = CHECKOUT_ROOT.resolve()
    text = source.read_text(encoding="utf-8")
    text = text.replace(SKILLS_REPO_URI_PLACEHOLDER, repo.as_uri())
    text = text.replace(SKILLS_REPO_PLACEHOLDER, str(repo))
    target.write_text(text, encoding="utf-8")
    return target


def ensure_workspace(name: str, dest: Path, *, reuse: bool) -> None:
    """Materialize ``dest`` or reuse it when that was requested."""
    if dest.exists() and not dest.is_dir():
        raise SystemExit(f"destination is not a directory: {dest}")
    nonempty = dest.is_dir() and any(dest.iterdir())
    if nonempty and not reuse:
        raise SystemExit(
            f"destination is not empty: {dest} (pass --reuse-workspace to use it)"
        )
    if not nonempty:
        materialize(name, dest, force=False)
        return
    directory = _require_scenario(name)
    turns_doc, _, errors = _load_scenario(directory)
    if errors:
        raise SystemExit("\n".join(errors))
    driver_name = turns_doc.get("driver")
    if isinstance(driver_name, str) and not (dest / Path(driver_name).name).is_file():
        _copy_driver(directory, turns_doc, dest)


def stage_workflow_skills(workflow_id: str, workspace: Path) -> list[Path]:
    """Stage install metadata and return source paths for one workflow."""
    catalog = _load_json(CHECKOUT_ROOT / ".catalog.json")
    if not isinstance(catalog, dict):
        raise SystemExit(".catalog.json must contain an object")
    workflows = catalog.get("workflows")
    workflow = next(
        (
            item
            for item in workflows or []
            if isinstance(item, dict) and item.get("id") == workflow_id
        ),
        None,
    )
    if workflow is None or not isinstance(workflow.get("includes"), list):
        raise SystemExit(f"unknown or invalid workflow {workflow_id!r}")
    skill_entries = {
        item["id"]: item
        for item in catalog.get("skills") or []
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    selected: list[dict[str, Any]] = []
    paths: list[Path] = []
    target = workspace / ".agents" / "skills"
    target.mkdir(parents=True, exist_ok=True)
    for skill_id in workflow["includes"]:
        entry = skill_entries.get(skill_id)
        if entry is None:
            raise SystemExit(f"workflow {workflow_id!r} includes unknown skill {skill_id!r}")
        source = CHECKOUT_ROOT / str(entry.get("path"))
        if not (source / "SKILL.md").is_file():
            raise SystemExit(f"skill source is missing: {source}")
        sidecar_dir = target / skill_id
        sidecar_dir.mkdir(parents=True, exist_ok=True)
        (sidecar_dir / ".skore-skill.json").write_text(
            json.dumps({"id": skill_id}, indent=2) + "\n",
            encoding="utf-8",
        )
        selected.append(entry)
        paths.append(source.resolve())
    local_catalog = {
        key: value
        for key, value in catalog.items()
        if key not in {"skills", "workflows", "catalog_hash"}
    }
    local_catalog["skills"] = selected
    local_catalog["workflows"] = [workflow]
    (target / ".catalog.json").write_text(
        json.dumps(local_catalog, indent=2) + "\n",
        encoding="utf-8",
    )
    return paths


def run_scenario(
    name: str,
    *,
    workspace: Path,
    interactive: bool,
    model: str | None,
    timeout: float,
    reuse: bool,
    extra_args: list[str] | None = None,
) -> int:
    """Launch Pi and check the final spine snapshot."""
    started = time.monotonic()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"{stamp}-pi-{uuid.uuid4().hex[:8]}"
    log_dir = REPO_ROOT / ".transcripts" / "integration" / run_id
    log_dir.mkdir(parents=True, exist_ok=True)
    status = 1
    check_errors: list[str] = []
    mode = "interactive" if interactive else "headless"
    try:
        ensure_workspace(name, workspace, reuse=reuse)
        directory = _require_scenario(name)
        turns_doc, _, errors = _load_scenario(directory)
        if errors:
            raise SystemExit("\n".join(errors))
        driver_name = turns_doc.get("driver")
        if not isinstance(driver_name, str):
            raise SystemExit(f"{name}: driver is missing")
        workflow_id = turns_doc.get("workflow")
        if not isinstance(workflow_id, str):
            raise SystemExit(f"{name}: workflow is missing")
        skill_paths = stage_workflow_skills(workflow_id, workspace)
        launch = build_launch(
            workspace=workspace,
            driver=workspace / Path(driver_name).name,
            interactive=interactive,
            model=model,
            extra_args=extra_args,
            skill_paths=skill_paths,
        )
        status = execute_launch(
            launch,
            interactive=interactive,
            timeout=timeout,
            stdout_path=log_dir / "stdout.txt",
            stderr_path=log_dir / "stderr.txt",
        )
        if status == 0:
            turns, _forks = _entries(directory)
            expect = _find(turns, FINAL_TURN, "turn").get("expect") or {}
            check_errors = check_workspace(workspace, expect)
            if check_errors:
                status = 1
                print(f"{name} {FINAL_TURN} failed:", file=sys.stderr)
                for err in check_errors:
                    print(f"- {err}", file=sys.stderr)
        elif status != 0:
            print(f"pi exited {status}", file=sys.stderr)
    except HarnessError as exc:
        status = exc.code
        print(str(exc), file=sys.stderr)
    payload = {
        "scenario": name,
        "harness": "pi",
        "mode": mode,
        "duration_seconds": round(time.monotonic() - started, 3),
        "exit_status": status,
        "check_errors": check_errors,
    }
    result_path = log_dir / "result.json"
    result_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"result: {result_path}", file=sys.stderr)
    return status


def cmd_validate() -> int:
    errors = validate_all()
    if errors:
        print("integration scenario validation failed:", file=sys.stderr)
        for err in errors:
            print(f"::error::{err}", file=sys.stderr)
        return 1
    count = len(_scenario_dirs())
    print(f"OK — {count} integration scenario(s).")
    return 0


def cmd_prompt(name: str, turn: str | None, fork: str | None) -> int:
    directory = _require_scenario(name)
    turns, forks = _entries(directory)
    if turn:
        _print_say(_find(turns, turn, "turn"))
    else:
        _print_say(_find(forks, fork or "", "fork"))
    return 0


def cmd_check(
    name: str,
    workspace: Path,
    turn: str | None,
    fork: str | None,
) -> int:
    directory = _require_scenario(name)
    turns, forks = _entries(directory)
    if turn:
        entry = _find(turns, turn, "turn")
    else:
        entry = _find(forks, fork or "", "fork")
    errors = check_workspace(workspace, entry.get("expect") or {})
    if errors:
        label = turn or fork
        print(f"{name} {label} failed:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1
    print(f"OK — {name} {turn or fork}")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    summary = (__doc__ or "").splitlines()[0] if __doc__ else ""
    parser = argparse.ArgumentParser(description=summary)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate", help="Validate scenario files and the seed snapshot.")

    materialize_parser = sub.add_parser(
        "materialize", help="Copy a scenario seed into a workspace."
    )
    materialize_parser.add_argument("scenario")
    materialize_parser.add_argument("--dest", type=Path, required=True)
    materialize_parser.add_argument(
        "--force",
        action="store_true",
        help="Replace a non-empty destination.",
    )

    prompt_parser = sub.add_parser("prompt", help="Print one turn or fork reply.")
    prompt_parser.add_argument("scenario")
    choice = prompt_parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--turn")
    choice.add_argument("--fork")

    check_parser = sub.add_parser(
        "check", help="Check a workspace against one turn or fork."
    )
    check_parser.add_argument("scenario")
    check_parser.add_argument("--workspace", type=Path, required=True)
    check_choice = check_parser.add_mutually_exclusive_group(required=True)
    check_choice.add_argument("--turn")
    check_choice.add_argument("--fork")

    run_parser = sub.add_parser("run", help="Launch Pi on one scenario.")
    run_parser.add_argument("scenario")
    run_parser.add_argument("--workspace", type=Path, required=True)
    run_parser.add_argument("--model")
    run_parser.add_argument(
        "--harness-arg",
        action="append",
        default=None,
        help="Extra harness argument. Repeat once per token.",
    )
    run_parser.add_argument(
        "--interactive",
        action="store_true",
        help="Inherit the terminal and show the harness TUI.",
    )
    run_parser.add_argument(
        "--reuse-workspace",
        action="store_true",
        help="Use a non-empty workspace instead of refusing it.",
    )
    run_parser.add_argument(
        "--timeout",
        type=float,
        default=3600,
        help="Seconds before the harness process group is terminated.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    args = parse_args(argv)
    if args.command == "validate":
        return cmd_validate()
    if args.command == "materialize":
        materialize(args.scenario, args.dest, force=args.force)
        return 0
    if args.command == "prompt":
        return cmd_prompt(args.scenario, args.turn, args.fork)
    if args.command == "check":
        return cmd_check(args.scenario, args.workspace, args.turn, args.fork)
    if args.command == "run":
        return run_scenario(
            args.scenario,
            workspace=args.workspace,
            interactive=args.interactive,
            model=args.model,
            timeout=args.timeout,
            reuse=args.reuse_workspace,
            extra_args=args.harness_arg,
        )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
