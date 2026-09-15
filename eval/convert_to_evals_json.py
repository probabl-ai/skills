#!/usr/bin/env python3
"""Convert our prompts.md → skill-creator's evals.json schema.

Reads `eval/<skill>/prompts.md` for each skill listed and writes
`skills/<skill>/evals/evals.json` in the official skill-creator schema.

Mapping:
  CASE_NN heading      → eval id (parsed from NN)
  User prompt block    → prompt (prefixed with workspace state)
  Workspace state      → inlined into prompt
  Must do bullets      → expectations (verbatim)
  Tools: yes            → evals[].tools (default false)
  Sandbox: dir/file/copy → evals[].sandbox (seeded temp workspace)
    Expect files          → evals[].expect_files (pytest glob checks)
    Expect reads          → evals[].expect_reads (tool-trace path checks)
    Expect cli            → evals[].expect_cli (run_skore_skills argv substrings)

Usage:
    python3 eval/convert_to_evals_json.py                 # all skills with eval/<name>/prompts.md
    python3 eval/convert_to_evals_json.py build-ml-pipeline …  # named skills
    python3 eval/convert_to_evals_json.py --check         # exit non-zero if evals.json is stale
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REPO = Path(__file__).parent.parent.resolve()


def parse_prompts_md(text: str) -> list[dict]:
    """Return [{id, title, prompt, must_do, must_not, tools, sandbox, expect_files, expect_reads, expect_cli}]."""
    cases = []
    for block in text.split("\n---\n"):
        head = re.search(r"^## CASE_(\d+) — (.+)$", block, re.MULTILINE)
        if not head:
            continue
        case_id = int(head.group(1))
        title = head.group(2).strip()

        up = re.search(
            r"\*\*User prompt:\*\*\s*\n((?:>[ \t]?.*(?:\n|$))+)", block
        )
        if not up:
            continue
        user_prompt = "\n".join(
            line.removeprefix("> ").removeprefix(">").rstrip()
            for line in up.group(1).strip().splitlines()
        )

        ws = re.search(
            r"\*\*Assumed workspace state:\*\*\s*\n((?:[-\s].*(?:\n|$))+?)\n\*\*",
            block,
        )
        workspace_state = ws.group(1).strip() if ws else ""

        tools = bool(re.search(r"\*\*Tools:\*\*\s*yes\b", block, re.IGNORECASE))
        sandbox = _parse_sandbox(block)
        expect_files = [
            item.strip("`")
            for item in _extract_bullets(block, r"\*\*Expect files:\*\*")
        ]
        expect_reads = [
            item.strip("`")
            for item in _extract_bullets(block, r"\*\*Expect reads:\*\*")
        ]
        expect_cli = [
            item.strip("`")
            for item in _extract_bullets(block, r"\*\*Expect cli:\*\*")
        ]
        must_do = _extract_bullets(block, r"\*\*Must do:?\*\*")
        must_not = _extract_bullets(block, r"\*\*Must NOT do:?\*\*")

        cases.append({
            "id": case_id,
            "title": title,
            "workspace_state": workspace_state,
            "user_prompt": user_prompt,
            "tools": tools,
            "sandbox": sandbox,
            "expect_files": expect_files,
            "expect_reads": expect_reads,
            "expect_cli": expect_cli,
            "must_do": must_do,
            "must_not": must_not,
        })
    return cases


def _parse_sandbox(block: str) -> list[dict]:
    """Parse **Sandbox:** dir/file bullets and optional fenced file bodies."""
    m = re.search(r"\*\*Sandbox:\*\*\s*\n", block)
    if not m:
        return []
    rest = block[m.end() :]
    stop = re.search(r"\n\*\*[^*]+\*\*", rest)
    section = rest[: stop.start()] if stop else rest
    entries: list[dict] = []
    lines = section.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        dir_m = re.match(r"- dir:\s*`?([^`]+?)`?\s*$", line)
        file_m = re.match(r"- file:\s*`?([^`]+?)`?\s*$", line)
        copy_m = re.match(
            r"- copy:\s*`?([^`]+?)`?(?:\s+as\s+`?([^`]+?)`?)?\s*$",
            line,
        )
        if dir_m:
            entries.append({"kind": "dir", "path": dir_m.group(1).strip()})
            i += 1
            continue
        if copy_m:
            source = copy_m.group(1).strip()
            dest = (copy_m.group(2) or source).strip()
            entries.append({"kind": "copy", "source": source, "path": dest})
            i += 1
            continue
        if file_m:
            path = file_m.group(1).strip()
            i += 1
            content = ""
            if i < len(lines) and lines[i].startswith("```"):
                fence = lines[i]
                fence_len = len(fence) - len(fence.lstrip("`"))
                i += 1
                body: list[str] = []
                closer = "`" * fence_len
                while i < len(lines):
                    if lines[i].startswith(closer):
                        i += 1
                        break
                    body.append(lines[i])
                    i += 1
                content = "\n".join(body)
                if content and not content.endswith("\n"):
                    content += "\n"
            entries.append({"kind": "file", "path": path, "content": content})
            continue
        i += 1
    return entries


def _extract_bullets(block: str, header_re: str) -> list[str]:
    """Extract `- ` bullet items under a bolded header."""
    m = re.search(
        header_re + r"\s*\n((?:-[ \t].*(?:\n[ \t]+\S.*)*(?:\n|$))+)", block
    )
    if not m:
        return []
    raw = m.group(1)
    bullets = []
    current = None
    for line in raw.splitlines():
        if line.startswith("- "):
            if current is not None:
                bullets.append(current.strip())
            current = line[2:].strip()
        elif line.startswith("  ") and current is not None:
            current += " " + line.strip()
    if current is not None:
        bullets.append(current.strip())
    return bullets


def to_evals_json(skill_name: str, cases: list[dict]) -> dict:
    evals = []
    for case in cases:
        if case["workspace_state"]:
            prompt = (
                f"[Workspace state — read but do not narrate back:\n"
                f"{case['workspace_state']}]\n\n{case['user_prompt']}"
            )
        else:
            prompt = case["user_prompt"]

        # Expectations = Must do (positive) + negated Must NOT.
        expectations = list(case["must_do"])
        for n in case["must_not"]:
            expectations.append(f"The response does NOT: {n}")

        expected_output_lines = [
            f"Behavioural response satisfying:",
            *[f"- {m}" for m in case["must_do"][:3]],
        ]
        if case["must_not"]:
            expected_output_lines.append("It must NOT:")
            expected_output_lines.extend(f"- {n}" for n in case["must_not"][:3])
        expected_output = " ".join(expected_output_lines)

        rec = {
            "id": case["id"],
            "title": case["title"],
            "prompt": prompt,
            "expected_output": expected_output,
            "files": [],
            "expectations": expectations,
            "tools": bool(case.get("tools")),
            "sandbox": case.get("sandbox") or [],
            "expect_files": case.get("expect_files") or [],
        }
        if case.get("expect_reads"):
            rec["expect_reads"] = case["expect_reads"]
        if case.get("expect_cli"):
            rec["expect_cli"] = case["expect_cli"]
        evals.append(rec)
    return {"skill_name": skill_name, "evals": evals}


def convert_skill(skill: str, *, check: bool = False) -> int:
    """Write or check ``evals.json`` for one skill. Return 1 on check drift."""
    prompts_path = REPO / "eval" / skill / "prompts.md"
    if not prompts_path.exists():
        print(f"  [skip] {skill}: no prompts.md")
        return 0

    cases = parse_prompts_md(prompts_path.read_text())
    if not cases:
        print(f"  [skip] {skill}: no cases parsed")
        return 0

    evals = to_evals_json(skill, cases)
    rendered = json.dumps(evals, indent=2) + "\n"
    out = REPO / "skills" / skill / "evals" / "evals.json"
    if check:
        if not out.is_file():
            print(f"  [stale] {skill}: {out.relative_to(REPO)} is missing")
            return 1
        current = out.read_text()
        if current != rendered:
            print(f"  [stale] {skill}: {out.relative_to(REPO)} does not match prompts.md")
            return 1
        print(f"  [ok]   {skill}: {len(cases)} cases")
        return 0

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(rendered)
    print(f"  [ok]   {skill}: {len(cases)} cases → {out.relative_to(REPO)}")
    return 0


def _skill_names(requested: list[str]) -> list[str]:
    if requested:
        return requested
    return sorted(
        p.name
        for p in (REPO / "eval").iterdir()
        if p.is_dir() and (p / "prompts.md").exists()
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument(
        "skills",
        nargs="*",
        help="Skill folder names under eval/. Default: every skill with prompts.md.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if any evals.json is stale; do not write.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skills = _skill_names(args.skills)
    verb = "Checking" if args.check else "Converting"
    print(f"{verb} {len(skills)} skill(s):")
    status = 0
    for skill in skills:
        status |= convert_skill(skill, check=args.check)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
