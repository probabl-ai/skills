"""Generate per-module API reference markdown files for the sklearn-api skill.

Reads doc/api_reference.py (the canonical list of public API for the docs site)
and emits one markdown file per module under .claude/skills/sklearn-api/references/.
"""
from __future__ import annotations

import importlib
import inspect
import sys
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]  # .claude/skills/sklearn-api/ -> repo root
OUT = HERE / "references"
OUT.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(REPO / "doc"))
from api_reference import API_REFERENCE  # noqa: E402


def resolve(module_key: str, dotted_name: str):
    """Resolve a dotted name relative to module_key into the actual object.

    e.g. resolve("sklearn.feature_extraction", "image.PatchExtractor")
    returns sklearn.feature_extraction.image.PatchExtractor.
    """
    full = f"{module_key}.{dotted_name}"
    parts = full.split(".")
    # Walk down: first import the longest leading prefix that's a module,
    # then getattr the rest.
    # Try importing decreasing prefixes until one works as a module, then
    # getattr the remainder.
    for cut in range(len(parts), 0, -1):
        mod_path = ".".join(parts[:cut])
        try:
            obj = importlib.import_module(mod_path)
        except ImportError:
            continue
        for attr in parts[cut:]:
            try:
                obj = getattr(obj, attr)
            except AttributeError:
                return None
        return obj
    return None


def signature_str(obj) -> str | None:
    try:
        sig = inspect.signature(obj)
    except (TypeError, ValueError):
        return None
    return str(sig)


def first_paragraph(doc: str | None) -> str:
    if not doc:
        return ""
    doc = inspect.cleandoc(doc)
    # The "summary" is everything until the first blank line.
    out_lines: list[str] = []
    for line in doc.splitlines():
        if not line.strip():
            if out_lines:
                break
            continue
        out_lines.append(line.strip())
    return " ".join(out_lines)


def kind_label(obj) -> str:
    if inspect.isclass(obj):
        return "class"
    if inspect.isfunction(obj) or inspect.isbuiltin(obj):
        return "function"
    return "object"


def render_entry(name: str, obj) -> str:
    if obj is None:
        return f"### `{name}`\n\n*(unresolved)*\n"
    kind = kind_label(obj)
    sig = signature_str(obj)
    summary = first_paragraph(getattr(obj, "__doc__", None))
    lines = [f"### `{name}` <sub>{kind}</sub>", ""]
    if sig:
        # Wrap very long signatures so the markdown stays readable.
        call = f"{name}{sig}"
        if len(call) > 100:
            wrapped = textwrap.fill(
                call,
                width=96,
                subsequent_indent="    ",
                break_long_words=False,
                break_on_hyphens=False,
            )
            lines.append("```python")
            lines.append(wrapped)
            lines.append("```")
        else:
            lines.append(f"```python\n{call}\n```")
    if summary:
        lines.append("")
        lines.append(summary)
    lines.append("")
    return "\n".join(lines)


def render_module(module_key: str, info: dict) -> str:
    out: list[str] = []
    out.append(f"# `{module_key}`")
    out.append("")
    out.append(f"_{info['short_summary']}_")
    out.append("")
    for section in info["sections"]:
        title = section.get("title")
        if title:
            out.append(f"## {title}")
            out.append("")
        names = section.get("autosummary", []) or []
        for name in names:
            obj = resolve(module_key, name)
            out.append(render_entry(name, obj))
    return "\n".join(out).rstrip() + "\n"


def filename_for(module_key: str) -> str:
    if module_key == "sklearn":
        return "sklearn.md"
    return module_key + ".md"


def main() -> None:
    written: list[str] = []
    for module_key, info in API_REFERENCE.items():
        text = render_module(module_key, info)
        path = OUT / filename_for(module_key)
        path.write_text(text)
        written.append(path.name)
    print(f"wrote {len(written)} files to {OUT}")
    for f in written:
        print(" -", f)


if __name__ == "__main__":
    main()
