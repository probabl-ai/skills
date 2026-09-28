"""Gitignore merge, review-path classification, and an end-turn hook.

Never runs ``git init``, ``git add``, or ``git commit``. Those stay
on the real git CLI, driven by ``setup-git`` and ``persist-ml-git``.
"""

from __future__ import annotations

import json
import os
import subprocess
from collections.abc import Sequence
from pathlib import Path, PurePosixPath
from typing import Any

from skore_skills.policy import LOOP_STAGES, load_policy
from skore_skills.scaffold import template_root

PERSIST_SKILL = "persist-ml-git"

KEEP_EXCEPTIONS = frozenset({".gitignore", ".gitattributes"})
MUST_IGNORE_DOTFILES = frozenset(
    {
        ".env",
        ".skore",
        ".pixi",
        ".venv",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        ".DS_Store",
        ".idea",
        ".vscode",
        ".claude",
        ".coverage",
        ".git",
    }
)
BLOCKED_NAMES = frozenset({".env", ".skore"})
GIT_MISSING = "git is not installed on PATH"
RESOLVED_DOTFILES_PREFIX = "# skore-skills resolved-dotfiles:"
RESOLVED_REVIEW_PREFIX = "# skore-skills resolved-review:"
LARGE_FILE_BYTES = 10 * 1024 * 1024
LARGE_DIR_BYTES = 50 * 1024 * 1024
LARGE_DIR_COUNT = 200
DATASET_MIN_BYTES = 1 * 1024 * 1024
ARTIFACT_SUFFIXES = frozenset(
    {
        ".pkl",
        ".joblib",
        ".pt",
        ".pth",
        ".ckpt",
        ".onnx",
        ".safetensors",
        ".h5",
    }
)
ARTIFACT_DIR_NAMES = frozenset({"wandb", "lightning_logs", "checkpoints"})
DATASET_SUFFIXES = frozenset(
    {".csv", ".tsv", ".parquet", ".feather", ".xlsx", ".xls", ".arrow", ".jsonl"}
)
NOTEBOOK_SUFFIXES = frozenset({".ipynb", ".nb.html"})
_KIND_RANK = {"artifact": 0, "dataset": 1, "notebook": 2, "large": 3}


def _git_env() -> dict[str, str]:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    return env


def _run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            env=_git_env(),
        )
    except FileNotFoundError as exc:
        raise ValueError(GIT_MISSING) from exc


def _has_repo(root: Path) -> bool:
    return (root / ".git").exists()


def _is_blocked(rel: str) -> bool:
    path = Path(rel)
    return any(part in BLOCKED_NAMES or part.startswith(".env") for part in path.parts)


def _resolve_keep(root: Path, keep: Sequence[str]) -> list[str]:
    resolved: list[str] = []
    root_resolved = root.resolve()
    for raw in keep:
        path = Path(raw)
        if path.is_absolute():
            try:
                rel = path.resolve().relative_to(root_resolved)
            except ValueError as exc:
                raise ValueError(f"keep path outside workspace: {raw}") from exc
        else:
            rel = path
        if ".." in rel.parts:
            raise ValueError(f"keep path outside workspace: {raw}")
        posix = rel.as_posix()
        if _is_blocked(posix):
            raise ValueError(f"refusing to keep blocked path: {posix}")
        resolved.append(posix)
    return resolved


def _keep_patterns(root: Path, posix: str) -> list[str]:
    target = root / posix
    if target.is_dir() or posix.endswith("/"):
        name = posix.rstrip("/")
        return [f"!{name}/", f"!{name}/**"]
    return [f"!{posix}"]


def _dotfile_key(name: str) -> str:
    return name.rstrip("/")


def _gitignore_lines(root: Path) -> list[str]:
    dest = root / ".gitignore"
    if not dest.is_file():
        return []
    return dest.read_text(encoding="utf-8").splitlines()


def _kept_from_gitignore(root: Path) -> set[str]:
    keys: set[str] = set()
    for line in _gitignore_lines(root):
        stripped = line.strip()
        if not stripped.startswith("!"):
            continue
        pattern = stripped[1:]
        if pattern.endswith("/**"):
            pattern = pattern[:-3]
        keys.add(_dotfile_key(pattern))
    return keys


def _resolved_from_gitignore(root: Path) -> set[str]:
    keys: set[str] = set()
    for line in _gitignore_lines(root):
        stripped = line.strip()
        if not stripped.startswith(RESOLVED_DOTFILES_PREFIX):
            continue
        rest = stripped[len(RESOLVED_DOTFILES_PREFIX) :].strip()
        for token in rest.split():
            keys.add(_dotfile_key(token))
    return keys


def _append_resolved_line(
    root: Path,
    names: Sequence[str],
    *,
    prefix: str,
    current: set[str],
) -> None:
    """Replace the single ``prefix`` comment in ``.gitignore`` with ``names``."""
    if not names:
        return
    dest = root / ".gitignore"
    existing = dest.read_text(encoding="utf-8") if dest.is_file() else ""
    current.update(_dotfile_key(name) for name in names)
    rendered: list[str] = []
    for key in sorted(current):
        suffix = "/" if (root / key).is_dir() else ""
        rendered.append(f"{key}{suffix}")
    new_line = f"{prefix} {' '.join(rendered)}"
    out: list[str] = []
    found = False
    for line in existing.splitlines():
        if line.strip().startswith(prefix):
            if not found:
                out.append(new_line)
                found = True
            continue
        out.append(line)
    if not found:
        out.append(new_line)
    dest.write_text("\n".join(out) + "\n", encoding="utf-8")


def _append_resolved(root: Path, names: Sequence[str]) -> None:
    _append_resolved_line(
        root,
        names,
        prefix=RESOLVED_DOTFILES_PREFIX,
        current=set() if not names else _resolved_from_gitignore(root),
    )


def _append_keep_exceptions(root: Path, keep: Sequence[str]) -> list[str]:
    dest = root / ".gitignore"
    existing = dest.read_text(encoding="utf-8") if dest.is_file() else ""
    existing_lines = {line.rstrip("\n") for line in existing.splitlines()}
    added: list[str] = []
    extra: list[str] = []
    for posix in keep:
        for pattern in _keep_patterns(root, posix):
            if pattern not in existing_lines:
                extra.append(pattern)
                existing_lines.add(pattern)
                added.append(pattern)
    if extra:
        body = existing.rstrip("\n")
        dest.write_text(body + "\n" + "\n".join(extra) + "\n", encoding="utf-8")
    return added


def merge_gitignore(root: Path) -> list[str]:
    """Union packaged ignore rules into ``root/.gitignore``.

    Never deletes user lines. Returns newly added pattern lines.
    """
    template = (template_root() / ".gitignore").read_text(encoding="utf-8")
    dest = root / ".gitignore"
    if not dest.is_file():
        dest.write_text(template, encoding="utf-8")
        return [
            line.strip()
            for line in template.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]

    existing = dest.read_text(encoding="utf-8")
    present = {
        line.strip()
        for line in existing.splitlines()
        if line.strip() and not line.strip().startswith("#")
    }
    added: list[str] = []
    out_lines = existing.splitlines()
    for line in template.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped not in present:
            out_lines.append(line)
            present.add(stripped)
            added.append(stripped)
    dest.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    return added


def list_ambiguous_dotfiles(root: Path, keep: Sequence[str] = ()) -> list[str]:
    """Return top-level ``.*`` paths that need a user decision."""
    decided = {_dotfile_key(item) for item in keep}
    decided |= _kept_from_gitignore(root)
    decided |= _resolved_from_gitignore(root)
    names: list[str] = []
    if not root.is_dir():
        return names
    for path in sorted(root.iterdir(), key=lambda item: item.name):
        name = path.name
        if not name.startswith(".") or name in {".", ".."}:
            continue
        if name in KEEP_EXCEPTIONS or name in MUST_IGNORE_DOTFILES:
            continue
        if name in decided:
            continue
        names.append(name + ("/" if path.is_dir() else ""))
    return names


def _porcelain_paths(root: Path) -> list[str]:
    proc = _run_git(root, "status", "--porcelain", "-uall")
    if proc.returncode != 0:
        raise ValueError(proc.stderr.strip() or "git status failed")
    paths: list[str] = []
    for line in proc.stdout.splitlines():
        if len(line) < 4:
            continue
        rest = line[3:]
        if " -> " in rest:
            rest = rest.split(" -> ", 1)[1]
        if rest.startswith('"') and rest.endswith('"'):
            rest = rest[1:-1]
        paths.append(rest.replace("\\", "/"))
    return paths


def _path_size(root: Path, rel: str) -> int:
    try:
        return (root / rel).stat().st_size
    except OSError:
        return 0


def _suffix(rel: str) -> str:
    name = PurePosixPath(rel).name.lower()
    if name.endswith(".nb.html"):
        return ".nb.html"
    return PurePosixPath(name).suffix


def _file_kind(rel: str, size: int) -> str | None:
    suffix = _suffix(rel)
    if suffix in NOTEBOOK_SUFFIXES:
        return "notebook"
    if suffix in ARTIFACT_SUFFIXES:
        return "artifact"
    if suffix in DATASET_SUFFIXES and size >= DATASET_MIN_BYTES:
        return "dataset"
    if size >= LARGE_FILE_BYTES:
        return "large"
    return None


def _outer_dir(rel: str, names: frozenset[str]) -> str | None:
    parts = PurePosixPath(rel).parts
    for index, part in enumerate(parts[:-1]):
        if part in names:
            return "/".join(parts[: index + 1]) + "/"
    return None


def _ancestor_dirs(rel: str) -> list[str]:
    parts = PurePosixPath(rel).parts[:-1]
    return ["/".join(parts[: index + 1]) + "/" for index in range(len(parts))]


def _review_entry(path: str, kind: str, nbytes: int) -> dict[str, Any]:
    return {"path": path, "kind": kind, "bytes": nbytes}


def _dominant_kind(kinds: Sequence[str]) -> str:
    return min(kinds, key=_KIND_RANK.__getitem__)


def _resolved_review_from_gitignore(root: Path) -> set[str]:
    keys: set[str] = set()
    for line in _gitignore_lines(root):
        stripped = line.strip()
        if not stripped.startswith(RESOLVED_REVIEW_PREFIX):
            continue
        rest = stripped[len(RESOLVED_REVIEW_PREFIX) :].strip()
        for token in rest.split():
            keys.add(_dotfile_key(token))
    return keys


def _is_resolved_review(rel: str, resolved: set[str]) -> bool:
    key = _dotfile_key(rel)
    if key in resolved:
        return True
    parts = PurePosixPath(key).parts
    return any("/".join(parts[:index]) in resolved for index in range(1, len(parts)))


def _append_resolved_review(root: Path, names: Sequence[str]) -> None:
    _append_resolved_line(
        root,
        names,
        prefix=RESOLVED_REVIEW_PREFIX,
        current=set() if not names else _resolved_review_from_gitignore(root),
    )


def _append_ignore_lines(root: Path, paths: Sequence[str]) -> list[str]:
    dest = root / ".gitignore"
    existing = dest.read_text(encoding="utf-8") if dest.is_file() else ""
    existing_lines = {line.rstrip("\n") for line in existing.splitlines()}
    extra: list[str] = []
    for posix in paths:
        if posix not in existing_lines:
            extra.append(posix)
            existing_lines.add(posix)
    if extra:
        body = existing.rstrip("\n")
        prefix = f"{body}\n" if body else ""
        dest.write_text(prefix + "\n".join(extra) + "\n", encoding="utf-8")
    return extra


def _resolve_review_path(root: Path, raw: str) -> str:
    folder = raw.endswith("/")
    posix = _resolve_keep(root, [raw])[0]
    if folder or (root / posix).is_dir():
        return f"{posix.rstrip('/')}/"
    return posix


def _group_by_dir(
    files: Sequence[tuple[str, int]], names: frozenset[str]
) -> dict[str, list[tuple[str, int]]]:
    grouped: dict[str, list[tuple[str, int]]] = {}
    for rel, size in files:
        folder = _outer_dir(rel, names)
        if folder is None:
            continue
        grouped.setdefault(folder, []).append((rel, size))
    return grouped


def _consume_folder(
    folders: dict[str, dict[str, Any]],
    consumed: set[str],
    folder: str,
    kind: str,
    members: Sequence[tuple[str, int]],
) -> None:
    folders[folder] = _review_entry(folder, kind, sum(size for _, size in members))
    consumed.update(rel for rel, _ in members)


def list_review_paths(
    root: Path, paths: Sequence[str] | None = None
) -> list[dict[str, Any]]:
    """Return dirty paths that need a keep-or-ignore decision."""
    dirty = list(paths) if paths is not None else _porcelain_paths(root)
    resolved = _resolved_review_from_gitignore(root)
    active: list[tuple[str, int]] = []
    for rel in dirty:
        if _is_blocked(rel) or _is_resolved_review(rel, resolved):
            continue
        if not (root / rel).exists():
            continue
        active.append((rel, _path_size(root, rel)))

    consumed: set[str] = set()
    folders: dict[str, dict[str, Any]] = {}
    for folder, members in _group_by_dir(active, ARTIFACT_DIR_NAMES).items():
        _consume_folder(folders, consumed, folder, "artifact", members)
    leftover = [(rel, size) for rel, size in active if rel not in consumed]
    for folder, members in _group_by_dir(leftover, frozenset({"raw"})).items():
        _consume_folder(folders, consumed, folder, "dataset", members)

    remaining = [(rel, size) for rel, size in leftover if rel not in consumed]
    dir_members: dict[str, list[tuple[str, int]]] = {}
    for rel, size in remaining:
        for folder in _ancestor_dirs(rel):
            dir_members.setdefault(folder, []).append((rel, size))
    large_dirs = {
        folder
        for folder, members in dir_members.items()
        if len(members) >= LARGE_DIR_COUNT
        or sum(size for _, size in members) >= LARGE_DIR_BYTES
    }
    minimal = [
        folder
        for folder in large_dirs
        if not any(other.startswith(folder) and other != folder for other in large_dirs)
    ]
    for folder in minimal:
        _consume_folder(folders, consumed, folder, "large", dir_members[folder])

    remaining = [(rel, size) for rel, size in remaining if rel not in consumed]
    kinds: dict[str, str] = {}
    for rel, size in remaining:
        kind = _file_kind(rel, size)
        if kind is not None:
            kinds[rel] = kind
    review_files = [(rel, size) for rel, size in remaining if rel in kinds]
    plain = {rel for rel, _ in remaining if rel not in kinds}
    review_by_dir: dict[str, list[tuple[str, int]]] = {}
    for rel, size in review_files:
        for folder in _ancestor_dirs(rel):
            review_by_dir.setdefault(folder, []).append((rel, size))
    collapsible = {
        folder
        for folder, members in review_by_dir.items()
        if len(members) >= 2 and not any(rel.startswith(folder) for rel in plain)
    }
    maximal = [
        folder
        for folder in collapsible
        if not any(
            folder.startswith(parent) and parent != folder for parent in collapsible
        )
    ]
    collapsed: set[str] = set()
    for folder in maximal:
        members = review_by_dir[folder]
        member_kinds = [kinds[rel] for rel, _ in members]
        kind = (
            member_kinds[0]
            if len(set(member_kinds)) == 1
            else _dominant_kind(member_kinds)
        )
        _consume_folder(folders, collapsed, folder, kind, members)

    entries = list(folders.values())
    for rel, size in review_files:
        if rel in collapsed:
            continue
        entries.append(_review_entry(rel, kinds[rel], size))
    entries.sort(key=lambda item: str(item["path"]))
    return entries


def _is_under_review(rel: str, review: Sequence[dict[str, Any]]) -> bool:
    for item in review:
        entry = str(item["path"])
        if entry.endswith("/"):
            if rel.startswith(entry):
                return True
        elif rel == entry:
            return True
    return False


def _commit_candidates(
    root: Path,
    review: Sequence[dict[str, Any]] = (),
    paths: Sequence[str] | None = None,
) -> tuple[list[str], list[str]]:
    found = list(paths) if paths is not None else _porcelain_paths(root)
    blocked = sorted({path for path in found if _is_blocked(path)})
    staged = [
        path
        for path in found
        if path not in blocked and not _is_under_review(path, review)
    ]
    return staged, blocked


def _payload(**fields: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "loop_stage": None,
        "autocommit": None,
        "repo": False,
        "skill": PERSIST_SKILL,
        "action": "skip",
        "reason": None,
        "status": [],
        "staged": [],
        "ambiguous_dotfiles": [],
        "review_paths": [],
        "blocked": [],
        "ignore_added": [],
    }
    base.update(fields)
    return base


def run_ignore_merge(
    root: Path, *, keep: Sequence[str] = (), decide: bool = False
) -> tuple[dict[str, Any], int]:
    """Merge packaged ignore rules; do not run git."""
    keep_paths = _resolve_keep(root, keep)
    ignore_added = merge_gitignore(root)
    ignore_added.extend(_append_keep_exceptions(root, keep_paths))
    if decide:
        _append_resolved(root, list_ambiguous_dotfiles(root, keep_paths))
    ambiguous = list_ambiguous_dotfiles(root, keep_paths)
    payload = _payload(
        action="resolve-dotfiles" if ambiguous else "ready",
        reason="ambiguous_dotfiles" if ambiguous else "ready",
        repo=_has_repo(root),
        autocommit=load_policy(root).get("git", {}).get("autocommit"),
        ambiguous_dotfiles=ambiguous,
        ignore_added=ignore_added,
    )
    return payload, (2 if ambiguous else 0)


def run_end_turn(root: Path, stage: str) -> tuple[dict[str, Any], int]:
    """Print whether to load ``persist-ml-git``. Never commits."""
    if stage not in LOOP_STAGES:
        raise ValueError(f"stage must be one of {', '.join(LOOP_STAGES)}")
    policy = load_policy(root)
    autocommit = policy.get("git", {}).get("autocommit")
    if not _has_repo(root):
        return (
            _payload(
                loop_stage=stage,
                autocommit=autocommit,
                repo=False,
                action="skip",
                reason="no_repo",
            ),
            0,
        )

    status = _porcelain_paths(root)
    ambiguous = list_ambiguous_dotfiles(root)
    review = list_review_paths(root, status)
    staged, blocked = _commit_candidates(root, review, status)
    common = {
        "loop_stage": stage,
        "autocommit": autocommit,
        "repo": True,
        "status": status,
        "staged": staged,
        "blocked": blocked,
        "ambiguous_dotfiles": ambiguous,
        "review_paths": review,
    }
    if autocommit is None:
        return (_payload(**common, action="skip", reason="unanswered"), 0)
    if autocommit == "off":
        return (_payload(**common, action="skip", reason="off"), 0)
    if ambiguous:
        return (
            _payload(**common, action="invoke", reason="resolve-dotfiles"),
            0,
        )
    if review:
        return (
            _payload(**common, action="invoke", reason="resolve-review"),
            0,
        )
    if not staged:
        reason = "clean" if not blocked else "nothing_to_commit"
        return (_payload(**common, action="skip", reason=reason), 0)
    return (_payload(**common, action="invoke", reason="persist"), 0)


def run_review(root: Path) -> tuple[dict[str, Any], int]:
    """Classify dirty paths that need a keep-or-ignore decision."""
    autocommit = load_policy(root).get("git", {}).get("autocommit")
    if not _has_repo(root):
        return (
            _payload(
                autocommit=autocommit,
                repo=False,
                action="ready",
                reason="no_repo",
            ),
            0,
        )
    status = _porcelain_paths(root)
    review = list_review_paths(root, status)
    staged, blocked = _commit_candidates(root, review, status)
    payload = _payload(
        repo=True,
        autocommit=autocommit,
        action="resolve-review" if review else "ready",
        reason="review_paths" if review else "ready",
        status=status,
        staged=staged,
        blocked=blocked,
        review_paths=review,
    )
    return payload, (2 if review else 0)


def run_review_decide(
    root: Path, *, keep: Sequence[str] = (), ignore: Sequence[str] = ()
) -> tuple[dict[str, Any], int]:
    """Record keep-or-ignore choices for review paths."""
    keep_paths = [_resolve_review_path(root, raw) for raw in keep]
    ignore_paths = [_resolve_review_path(root, raw) for raw in ignore]
    overlap = sorted(set(keep_paths) & set(ignore_paths))
    if overlap:
        listed = ", ".join(overlap)
        raise ValueError(f"path is both keep and ignore: {listed}")
    ignore_added = _append_ignore_lines(root, ignore_paths)
    _append_resolved_review(root, [*keep_paths, *ignore_paths])
    payload, code = run_review(root)
    payload["ignore_added"] = ignore_added
    return payload, code


def render_git_json(payload: dict[str, Any]) -> str:
    """Serialize a git command payload."""
    return json.dumps(payload, indent=2) + "\n"
