#!/usr/bin/env python3
"""Validate ``.catalog.json`` against the on-disk ``skills/`` directory.

The validator enforces eight invariants:

1. Every directory under ``skills/`` has a matching entry in
   ``.catalog.json``'s ``skills`` array, and vice versa.
2. Every catalog entry's ``path`` resolves to a directory containing a
   ``SKILL.md`` file.
3. Every skill entry uses a known ``category`` and a permitted
   ``subcategory`` for that category (``null`` is required for
   categories that don't take a subcategory).
4. Every workflow's ``includes`` list references known skill ids.
5. Every ``SKILL.md`` description is shorter than 1024 characters,
   counted the way Cursor counts a folded ``description: >`` block.
6. Every ``SKILL.md`` ends its frontmatter with an unindented
   ``metadata:`` block whose ``modelTier`` is ``small``, ``medium``,
   or ``big``. ``role``, when present, is ``entry`` or ``helper``.
7. At most one skill declares ``metadata.role: entry``.
8. No skill loads a ``metadata.role: helper`` skill whose
   ``modelTier`` is higher than its own. A helper loaded while its
   caller keeps working runs on at most the caller's model, so its
   tier would never apply. A load is a ``load`` / ``route to`` /
   ``re-enter`` / ``hand off to`` instruction naming the helper;
   ``return to`` (back to the skill that loaded this one) and
   prohibitions ("Do not load ...") are not loads. The entry skill
   is exempt: it is not a caller.

Usage
-----
    python tools/validate_catalog.py

Exits 0 on success, 1 on the first error. Designed to be wired into
CI alongside ``hash_skills.py --check``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Cursor rejects a skill description at this length. The count includes
# the trailing newline that YAML ``>`` (clip) keeps.
DESCRIPTION_MAX_LENGTH = 1024
MODEL_TIERS = {"small", "medium", "big"}
ROLES = {"entry", "helper"}
TIER_RANK = {"small": 0, "medium": 1, "big": 2}
_FIELD = re.compile(r"^  ([A-Za-z]+):[ \t]*(\S+)[ \t]*$")
# A negation governing a load-like verb, then a skill name: not a load.
# Same rule as pi-skill-lifecycle's caller detection.
_PROHIBITION = re.compile(
    r"\b(?:do not|don't|never|must not|should not|shouldn't|not to)\s+"
    r"(?:\w+\s+)?(?:load|call|invoke|use|route to|hand off to)\s+"
    r"[`'\"]?[\w-]+[`'\"]?",
    re.IGNORECASE,
)
# An instruction to load another skill. ``return to`` is excluded on
# purpose: it continues the skill that loaded this one.
_LOAD = re.compile(
    r"\b(?:load|loads|loading|route to|routes to|route back to|routed to|"
    r"re-enter|re-enters|hand off to|hands off to)\s+(?:[\w-]+\s+)?"
    r"[`'\"]?([a-z][\w-]+)[`'\"]?",
    re.IGNORECASE,
)


def folded_description_length(text: str) -> int | None:
    """Return the Cursor length of a folded ``description: >`` block.

    Single newlines inside a paragraph become spaces. A blank line
    becomes a newline. Clip chomping keeps one trailing newline.
    Returns ``None`` when the file has no description field.
    """
    lines = text.splitlines()
    try:
        start = next(
            i for i, line in enumerate(lines) if line.startswith("description:")
        )
    except StopIteration:
        return None
    header = lines[start]
    inline = header.split(":", 1)[1].strip()
    if inline not in {">", ">-", "|", "|-"}:
        return len(inline.strip("\"'"))
    body: list[str] = []
    for line in lines[start + 1 :]:
        if line and not line.startswith((" ", "\t")):
            break
        body.append(line)
    indents = [len(line) - len(line.lstrip(" ")) for line in body if line.strip()]
    indent = min(indents) if indents else 0
    raw = [line[indent:] if len(line) >= indent else "" for line in body]
    while raw and raw[-1] == "":
        raw.pop()
    if inline.startswith("|"):
        folded = "\n".join(raw)
    else:
        paragraphs: list[str] = []
        current: list[str] = []
        for line in raw:
            if line.strip() == "":
                if current:
                    paragraphs.append(" ".join(current))
                    current = []
            else:
                current.append(line.strip())
        if current:
            paragraphs.append(" ".join(current))
        folded = "\n".join(paragraphs)
    if inline in {">", "|"}:
        folded += "\n"
    return len(folded)


def metadata_fields(text: str) -> dict[str, str] | None:
    """Return the keys of the unindented ``metadata:`` block.

    ``metadata:`` must be unindented. An indented key is inside the
    folded description and is not part of this block. Returns
    ``None`` when the block is missing or a nested line is not
    ``key: value``.
    """
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    lines = text[4:end].splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line == "metadata:")
    except StopIteration:
        return None
    fields: dict[str, str] = {}
    for line in lines[start + 1 :]:
        if line == "":
            continue
        if not line.startswith((" ", "\t")):
            break
        match = _FIELD.match(line)
        if match is None:
            return None
        fields[match.group(1)] = match.group(2)
    return fields


def loaded_skills(text: str, names: set[str], self_name: str) -> set[str]:
    """Return the skills a ``SKILL.md`` body tells the model to load.

    Frontmatter is skipped, line breaks are folded so a wrapped
    sentence still matches, and prohibitions are removed first.
    """
    end = text.find("\n---\n", 4) if text.startswith("---\n") else -1
    body = text[end + 5 :] if end != -1 else text
    body = _PROHIBITION.sub(" ", re.sub(r"\s+", " ", body))
    return {
        m.group(1)
        for m in _LOAD.finditer(body)
        if m.group(1) in names and m.group(1) != self_name
    }


def helper_tier_errors(skills: dict[str, tuple[str | None, str | None, str]]) -> list[str]:
    """Invariant 8: no skill loads a helper of a higher tier than its own.

    Parameters
    ----------
    skills : dict
        Skill id -> ``(role, modelTier, SKILL.md text)``.

    Returns
    -------
    list[str]
        One message per offending load.
    """
    errors: list[str] = []
    names = set(skills)
    for caller, (role, tier, text) in sorted(skills.items()):
        if role == "entry" or tier not in TIER_RANK:
            continue
        for helper in sorted(loaded_skills(text, names, caller)):
            h_role, h_tier, _ = skills[helper]
            if h_role != "helper" or h_tier not in TIER_RANK:
                continue
            if TIER_RANK[h_tier] > TIER_RANK[tier]:
                errors.append(
                    f"skills/{caller}/SKILL.md ({tier}) loads helper "
                    f"{helper!r} ({h_tier}): a helper runs on at most its "
                    "caller's model, so its tier never applies. Route "
                    f"through a skill of tier {h_tier} or more, or return "
                    "to the skill that loaded this one."
                )
    return errors


# Allow-list: category -> set of permitted subcategories.
# An empty set means the category does not take a subcategory
# (entries under it must have ``"subcategory": null``).
CATEGORIES: dict[str, set[str]] = {
    "action": set(),
    "meta": set(),
    "methodology": set(),
    "orchestration": {"dispatchers", "experiment-sourcing", "test-strategies"},
    "tooling": {"project-setup", "code-quality"},
    "reference": set(),
}


def validate(catalog_path: Path) -> list[str]:
    """Return a list of validation errors for ``catalog_path``.

    An empty list means the catalog is valid.

    Parameters
    ----------
    catalog_path : pathlib.Path
        Path to the catalog JSON file.

    Returns
    -------
    list[str]
        Human-readable error messages, one per problem detected.
    """
    repo_root = catalog_path.parent
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    errors: list[str] = []

    catalog_ids = {s["id"] for s in catalog["skills"]}
    skills_dir = repo_root / "skills"
    folder_ids = {p.name for p in skills_dir.iterdir() if p.is_dir()}

    missing_in_catalog = folder_ids - catalog_ids
    if missing_in_catalog:
        errors.append(
            f"skill folders without a .catalog.json entry: {sorted(missing_in_catalog)}"
        )

    missing_folders = catalog_ids - folder_ids
    if missing_folders:
        errors.append(
            ".catalog.json entries without a matching skills/ folder: "
            f"{sorted(missing_folders)}"
        )

    entries: list[str] = []
    declared: dict[str, tuple[str | None, str | None, str]] = {}
    for skill in catalog["skills"]:
        sid = skill["id"]
        skill_path = repo_root / skill["path"]
        skill_md = skill_path / "SKILL.md"
        if not skill_md.is_file():
            errors.append(f"{skill['path']}/SKILL.md is missing")
        else:
            text = skill_md.read_text(encoding="utf-8")
            length = folded_description_length(text)
            if length is not None and length >= DESCRIPTION_MAX_LENGTH:
                errors.append(
                    f"{skill['path']}/SKILL.md description exceeds "
                    f"{DESCRIPTION_MAX_LENGTH - 1} characters ({length})"
                )
            fields = metadata_fields(text)
            tier = None if fields is None else fields.get("modelTier")
            if tier not in MODEL_TIERS:
                errors.append(
                    f"{skill['path']}/SKILL.md metadata.modelTier must be "
                    "small, medium, or big, in an unindented metadata block"
                )
            role = None if fields is None else fields.get("role")
            if role is not None and role not in ROLES:
                errors.append(
                    f"{skill['path']}/SKILL.md metadata.role must be "
                    f"entry or helper, got {role!r}"
                )
            if role == "entry":
                entries.append(sid)
            declared[sid] = (role, tier, text)

        cat = skill.get("category")
        sub = skill.get("subcategory")
        if cat not in CATEGORIES:
            errors.append(
                f"skill {sid!r} has unknown category {cat!r} "
                f"(allowed: {sorted(CATEGORIES)})"
            )
            continue
        allowed_subs = CATEGORIES[cat]
        if allowed_subs:
            if sub not in allowed_subs:
                errors.append(
                    f"skill {sid!r}: subcategory {sub!r} not allowed under "
                    f"category {cat!r} (allowed: {sorted(allowed_subs)})"
                )
        elif sub is not None:
            errors.append(
                f"skill {sid!r}: category {cat!r} takes no subcategory, "
                f"got {sub!r}"
            )

    if len(entries) > 1:
        errors.append(
            "more than one skill declares metadata.role entry: "
            + ", ".join(entries)
        )

    errors.extend(helper_tier_errors(declared))

    for workflow in catalog.get("workflows", []):
        unknown = [s for s in workflow.get("includes", []) if s not in catalog_ids]
        if unknown:
            errors.append(
                f"workflow {workflow['id']!r} references unknown skill ids: {unknown}"
            )

    return errors


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    summary = (__doc__ or "").splitlines()[0] if __doc__ else ""
    parser = argparse.ArgumentParser(description=summary)
    default_catalog = Path(__file__).resolve().parent.parent / ".catalog.json"
    parser.add_argument(
        "--catalog",
        type=Path,
        default=default_catalog,
        help="Path to .catalog.json (default: %(default)s).",
    )
    return parser.parse_args()


def main() -> int:
    """Entry point."""
    args = parse_args()
    catalog_path = args.catalog.resolve()
    errors = validate(catalog_path)

    if errors:
        print("catalog validation failed:", file=sys.stderr)
        for err in errors:
            # ``::error::`` makes GitHub Actions surface it as an annotation
            # when run inside a workflow; harmless locally.
            print(f"::error::{err}", file=sys.stderr)
        return 1

    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    print(
        f"OK \u2014 {len(catalog['skills'])} skills, "
        f"{len(catalog.get('workflows', []))} workflow(s); all categories valid."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
