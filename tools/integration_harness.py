"""Launch a scenario workspace in Pi.

The adapter builds the Pi command. It uses Pi's existing authentication
and does not install the binary.
"""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import threading
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Any

INITIAL_PROMPT = (
    "Read SCENARIO.md and carry out that unattended journey. "
    "The choices in that file are already authorized. "
    "Stop if the workspace contradicts a choice instead of inventing another one."
)
EXIT_TIMEOUT = 124
EXIT_INTERRUPT = 130
EXIT_MISSING = 127
PI_DEFAULT_PROVIDER = "openrouter"
PI_DEFAULT_MODEL = "~deepseek/deepseek-flash-latest"
REPO_SRC = Path(__file__).resolve().parent.parent / "src"


class HarnessError(Exception):
    """A harness could not be launched."""

    def __init__(self, message: str, code: int = EXIT_MISSING) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class PreparedLaunch:
    """One harness process and the files it temporarily owns."""

    argv: list[str]
    cwd: Path
    env: dict[str, str]
    cleanup: Callable[[], None]


def build_launch(
    *,
    workspace: Path,
    driver: Path,
    interactive: bool,
    model: str | None,
    extra_args: list[str] | None = None,
    skill_paths: list[Path] | None = None,
) -> PreparedLaunch:
    """Return the Pi command without starting it."""
    if not driver.is_file():
        raise HarnessError(f"scenario driver is missing: {driver}", code=1)
    argv = [
        _require_executable(),
        "--append-system-prompt",
        str(driver),
        "--approve",
    ]
    for path in skill_paths or []:
        argv.extend(["--skill", str(path)])
    if not interactive:
        argv.extend(["--mode", "json"])
    extra = list(extra_args or [])
    _append_model(argv, model, extra)
    argv.extend(extra)
    argv.append(INITIAL_PROMPT)
    env = os.environ.copy()
    current_pythonpath = env.get("PYTHONPATH")
    pythonpath = str(REPO_SRC)
    if current_pythonpath:
        pythonpath += os.pathsep + current_pythonpath
    env["PYTHONPATH"] = pythonpath
    return PreparedLaunch(
        argv=argv,
        cwd=workspace,
        env=env,
        cleanup=lambda: None,
    )


def _append_model(argv: list[str], model: str | None, extra: list[str]) -> None:
    """Add provider and model flags that ``extra`` did not already set."""
    if "--provider" not in extra:
        argv.extend(["--provider", PI_DEFAULT_PROVIDER])
    if "--model" in extra:
        return
    argv.extend(["--model", model or PI_DEFAULT_MODEL])


def _require_executable() -> str:
    found = shutil.which("pi")
    if found is None:
        raise HarnessError("pi is not installed.")
    return found


def execute_launch(
    launch: PreparedLaunch,
    *,
    interactive: bool,
    timeout: float,
    stdout_path: Path,
    stderr_path: Path,
    popen: Callable[..., subprocess.Popen[str]] = subprocess.Popen,
    terminate: Callable[[int], None] | None = None,
) -> int:
    """Run ``launch`` until it exits, times out, or the user interrupts it."""
    if terminate is None:
        terminate = _terminate_process_group
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    spawned = _spawn_kwargs()
    try:
        if interactive:
            process = popen(
                launch.argv,
                cwd=launch.cwd,
                env=launch.env,
                text=True,
                **spawned,
            )
            return _wait(process, timeout=timeout, terminate=terminate)
        with stdout_path.open("w", encoding="utf-8") as stdout_file:
            with stderr_path.open("w", encoding="utf-8") as stderr_file:
                process = popen(
                    launch.argv,
                    cwd=launch.cwd,
                    env=launch.env,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    **spawned,
                )
                threads = (
                    _stream(process.stdout, stdout_file, sys.stdout),
                    _stream(process.stderr, stderr_file, sys.stderr),
                )
                status = _wait(process, timeout=timeout, terminate=terminate)
                for thread in threads:
                    thread.join()
                return status
    finally:
        launch.cleanup()


def _spawn_kwargs() -> dict[str, Any]:
    if os.name == "nt":
        return {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
    return {"start_new_session": True}


def _stream(source: IO[str] | None, sink: IO[str], echo: IO[str]) -> threading.Thread:
    def copy() -> None:
        if source is None:
            return
        while True:
            line = source.readline()
            if line == "":
                break
            sink.write(line)
            sink.flush()
            echo.write(line)
            echo.flush()

    thread = threading.Thread(target=copy)
    thread.start()
    return thread


def _wait(
    process: subprocess.Popen[str],
    *,
    timeout: float,
    terminate: Callable[[int], None],
) -> int:
    try:
        return process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        terminate(process.pid)
        _reap(process)
        return EXIT_TIMEOUT
    except KeyboardInterrupt:
        terminate(process.pid)
        _reap(process)
        return EXIT_INTERRUPT


def _reap(process: subprocess.Popen[str]) -> None:
    try:
        process.wait(timeout=1)
    except (subprocess.TimeoutExpired, OSError):
        return


def _terminate_process_group(pid: int) -> None:
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(pid)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(pid, sig)
        except ProcessLookupError:
            return
        except PermissionError:
            try:
                os.kill(pid, sig)
            except ProcessLookupError:
                return
