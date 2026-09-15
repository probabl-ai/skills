"""Temp-workspace tools for lookup-gated evals (list / read / write / run)."""

from __future__ import annotations

import json
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

TOOL_LOOP_CAP = 12
RUN_PYTHON_TIMEOUT = 30
RUN_SKORE_SKILLS_TIMEOUT = 30
CELLS_TIMEOUT = 120


def _is_absolute_path(raw: str) -> bool:
    return PurePosixPath(raw).is_absolute() or PureWindowsPath(raw).is_absolute()

TOOLS_NOTE = (
    "Harness note: you have tools this turn. The project root is a real "
    "directory (your cwd). If SKILL.md points at a relative "
    "`references/` path, that file is on disk here — open it with "
    "read_file before answering from memory. Use list_dir, read_file, "
    "write_file, run_python, and run_skore_skills. run_python only "
    "executes files under scratch/ — inline python -c is rejected. "
    "run_skore_skills runs python -m skore_skills with the given argv "
    "(cwd is this project root). When you are done, put the complete "
    "deliverable in the assistant message (not only in a thinking "
    "channel). The last message must be that deliverable, not another "
    "tool call."
)

TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List a directory relative to the project root.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path, relative to project root. Use '.' for root.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a UTF-8 text file relative to the project root.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write a UTF-8 text file relative to the project root. Parents are created.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": "Run a Python file under scratch/ with the eval interpreter. No python -c.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to a .py file under scratch/.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_skore_skills",
            "description": (
                "Run python -m skore_skills with argv after the module. "
                "cwd is the project root. No python -c; no shell."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Remaining argv, e.g. "
                            '["api", "get", "sklearn.model_selection.KFold"].'
                        ),
                    }
                },
                "required": ["args"],
            },
        },
    },
]


def _repo_file(rel: str) -> Path:
    raw = (rel or "").strip()
    if not raw or _is_absolute_path(raw):
        raise ValueError("copy source must be a repo-relative path")
    source = (REPO_ROOT / raw).resolve()
    try:
        source.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise ValueError("copy source escapes the repo") from exc
    if not source.is_file():
        raise FileNotFoundError(f"copy source is not a file: {rel}")
    return source


def normalize_relpath(rel: str) -> str:
    return (rel or "").replace("\\", "/").strip().lstrip("./")


def missing_reads(
    tool_trace: list[dict[str, Any]] | None, patterns: list[str]
) -> list[str]:
    """Return expect-read paths that never appeared in a read_file call."""
    seen: list[str] = []
    for item in tool_trace or []:
        if item.get("name") != "read_file":
            continue
        args = item.get("arguments") or {}
        seen.append(normalize_relpath(str(args.get("path") or "")))
    missing: list[str] = []
    for pattern in patterns:
        want = normalize_relpath(pattern)
        if not want:
            continue
        if not any(path == want or path.endswith("/" + want) for path in seen):
            missing.append(pattern)
    return missing


def _cli_argv_joined(arguments: dict[str, Any]) -> str:
    raw = arguments.get("args")
    if isinstance(raw, list):
        return " ".join(str(item) for item in raw)
    return str(raw or "")


def missing_cli(
    tool_trace: list[dict[str, Any]] | None, patterns: list[str]
) -> list[str]:
    """Return expect-cli argv substrings that never appeared in run_skore_skills."""
    seen: list[str] = []
    for item in tool_trace or []:
        if item.get("name") != "run_skore_skills":
            continue
        seen.append(_cli_argv_joined(item.get("arguments") or {}))
    missing: list[str] = []
    for pattern in patterns:
        want = pattern.strip().strip("`")
        if not want:
            continue
        if not any(want in call for call in seen):
            missing.append(pattern)
    return missing


def parse_cli_args(raw: Any) -> list[str]:
    """Normalize run_skore_skills args; raise ValueError on empty / -c / abs paths."""
    if raw is None:
        raise ValueError("args is required")
    if isinstance(raw, str):
        text = raw.strip()
        if not text:
            raise ValueError("args must be a non-empty list")
        if text.startswith("["):
            try:
                data = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError("args must be a non-empty list") from exc
            if not isinstance(data, list):
                raise ValueError("args must be a non-empty list")
            tokens = [str(item) for item in data]
        else:
            tokens = shlex.split(text)
    elif isinstance(raw, list):
        tokens = [str(item) for item in raw]
    else:
        raise ValueError("args must be a non-empty list")
    if not tokens:
        raise ValueError("args must be a non-empty list")
    joined = " ".join(tokens)
    if any(tok == "-c" for tok in tokens) or "python -c" in joined:
        raise ValueError("python -c is rejected")
    for tok in tokens:
        if _is_absolute_path(tok):
            raise ValueError("paths must be relative to the sandbox")
    return tokens


class Sandbox:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "scratch").mkdir(exist_ok=True)

    def resolve(self, rel: str) -> Path:
        raw = (rel or ".").strip() or "."
        if _is_absolute_path(raw):
            raise ValueError("path must be relative to the project root")
        target = (self.root / raw).resolve()
        try:
            target.relative_to(self.root)
        except ValueError as exc:
            raise ValueError("path escapes the project root") from exc
        return target

    def seed(self, entries: list[dict[str, Any]] | None) -> None:
        for item in entries or []:
            kind = item.get("kind")
            path = str(item.get("path") or "")
            target = self.resolve(path)
            if kind == "dir":
                target.mkdir(parents=True, exist_ok=True)
            elif kind == "file":
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(str(item.get("content") or ""), encoding="utf-8")
            elif kind == "copy":
                source = _repo_file(str(item.get("source") or path))
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)

    def list_tree(self, limit: int = 80) -> list[str]:
        rows: list[str] = []
        for path in sorted(self.root.rglob("*")):
            rel = path.relative_to(self.root).as_posix()
            suffix = "/" if path.is_dir() else ""
            rows.append(rel + suffix)
            if len(rows) >= limit:
                break
        return rows

    def expect_ok(self, patterns: list[str]) -> list[str]:
        missing: list[str] = []
        for pattern in patterns:
            matches = list(self.root.glob(pattern))
            if not matches:
                missing.append(pattern)
        return missing

    def dispatch(self, name: str, arguments: dict[str, Any]) -> str:
        try:
            if name == "list_dir":
                return self._list_dir(str(arguments.get("path") or "."))
            if name == "read_file":
                return self._read_file(str(arguments.get("path") or ""))
            if name == "write_file":
                return self._write_file(
                    str(arguments.get("path") or ""),
                    str(arguments.get("content") or ""),
                )
            if name == "run_python":
                return self._run_python(str(arguments.get("path") or ""))
            if name == "run_skore_skills":
                return self._run_skore_skills(arguments.get("args"))
            return f"unknown tool: {name}"
        except Exception as exc:  # noqa: BLE001 — surface tool errors to the model
            return f"error: {exc}"

    def _list_dir(self, rel: str) -> str:
        target = self.resolve(rel)
        if not target.exists():
            return f"error: {rel} does not exist"
        if not target.is_dir():
            return f"error: {rel} is not a directory"
        names = sorted(p.name + ("/" if p.is_dir() else "") for p in target.iterdir())
        return "\n".join(names) if names else "(empty)"

    def _read_file(self, rel: str) -> str:
        target = self.resolve(rel)
        if not target.is_file():
            return f"error: {rel} is not a file"
        return target.read_text(encoding="utf-8")

    def _write_file(self, rel: str, content: str) -> str:
        target = self.resolve(rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"wrote {rel} ({len(content)} bytes)"

    def _run_python(self, rel: str) -> str:
        target = self.resolve(rel)
        try:
            target.relative_to(self.root / "scratch")
        except ValueError:
            return "error: run_python only executes files under scratch/"
        if target.suffix != ".py":
            return "error: run_python requires a .py file"
        if not target.is_file():
            return f"error: {rel} is not a file"
        proc = subprocess.run(
            [sys.executable, str(target)],
            cwd=self.root,
            capture_output=True,
            text=True,
            timeout=RUN_PYTHON_TIMEOUT,
            check=False,
        )
        out = []
        if proc.stdout:
            out.append(proc.stdout)
        if proc.stderr:
            out.append(proc.stderr)
        out.append(f"exit_code={proc.returncode}")
        return "\n".join(out).strip()

    def _run_skore_skills(self, raw_args: Any) -> str:
        try:
            args = parse_cli_args(raw_args)
        except ValueError as exc:
            return f"error: {exc}"
        timeout = CELLS_TIMEOUT if args[0] == "cells" else RUN_SKORE_SKILLS_TIMEOUT
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "skore_skills", *args],
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return f"error: timed out after {timeout}s"
        out = []
        if proc.stdout:
            out.append(proc.stdout)
        if proc.stderr:
            out.append(proc.stderr)
        out.append(f"exit_code={proc.returncode}")
        return "\n".join(out).strip()


_TOOL_XML_RE = re.compile(
    r"<minimax:tool_call>.*?</minimax:tool_call>"
    r"|<invoke\s+name=\"[^\"]+\">.*?</invoke>",
    re.DOTALL,
)


def strip_tool_xml(content: str) -> str:
    """Remove MiniMax-style XML tool wrappers; keep leftover prose."""
    if not content:
        return ""
    return _TOOL_XML_RE.sub("", content).strip()


def is_tool_xml_only(content: str) -> bool:
    raw = (content or "").strip()
    if not raw:
        return False
    if strip_tool_xml(raw):
        return False
    return "<invoke" in raw or "<minimax:tool_call>" in raw


def parse_xml_tool_calls(content: str) -> list[dict[str, Any]]:
    """MiniMax (and similar) sometimes emit XML tool calls in message content."""
    if not content or "<invoke" not in content:
        return []
    calls: list[dict[str, Any]] = []
    for invoke in re.finditer(
        r'<invoke\s+name="([^"]+)">\s*(.*?)\s*</invoke>',
        content,
        re.DOTALL,
    ):
        name = invoke.group(1)
        args: dict[str, Any] = {}
        for param in re.finditer(
            r'<parameter\s+name="([^"]+)">\s*(.*?)\s*</parameter>',
            invoke.group(2),
            re.DOTALL,
        ):
            args[param.group(1)] = param.group(2)
        calls.append({"name": name, "arguments": args})
    return calls


def parse_tool_arguments(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}
