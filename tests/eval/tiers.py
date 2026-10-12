"""Per-skill eval model tiers.

Each skill declares ``metadata.modelTier`` in its ``SKILL.md``.
``assigned`` runs only that tier's model; ``all`` runs every skill on
all three models. A skill with no tier, or an unknown tier name, falls
back to medium so a new evals.json is never silently skipped.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from functools import lru_cache
from pathlib import Path

TIERS = ("small", "medium", "big")
TIER_MODES = ("assigned", "all", "small", "medium", "big")
DEFAULT_TIER = "medium"
DEFAULT_TIER_MODELS = {
    "small": "openrouter/qwen/qwen3.8-27b",
    "medium": "openrouter/deepseek/deepseek-v4.1-flash",
    "big": "openrouter/qwen/qwen3.8-max-0902",
}

SKILLS_DIR = Path(__file__).resolve().parents[2] / "skills"
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
_MODEL_TIER = re.compile(r"^  modelTier:\s*([A-Za-z]+)\s*$", re.MULTILINE)


@lru_cache(maxsize=None)
def _declared_tiers() -> dict[str, str]:
    tiers: dict[str, str] = {}
    if not SKILLS_DIR.is_dir():
        return tiers
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        match = _FRONTMATTER.match(skill_md.read_text(encoding="utf-8"))
        found = match and _MODEL_TIER.search(match.group(1))
        if found and found.group(1).lower() in TIERS:
            tiers[skill_dir.name] = found.group(1).lower()
    return tiers


def skill_tier(skill_name: str) -> str:
    """Tier declared in SKILL.md; unannotated or unknown skills fall back to medium."""
    return _declared_tiers().get(skill_name, DEFAULT_TIER)


def models_for_skill(
    skill_name: str,
    *,
    tier_mode: str,
    tier_models: Mapping[str, str],
) -> list[str]:
    """Return target model ids for one skill under ``tier_mode``."""
    assigned = skill_tier(skill_name)
    if tier_mode == "all":
        return [tier_models[name] for name in TIERS]
    if tier_mode == "assigned":
        return [tier_models[assigned]]
    if tier_mode in TIERS:
        if assigned != tier_mode:
            return []
        return [tier_models[tier_mode]]
    raise ValueError(f"unknown tier mode {tier_mode!r}; expected one of {TIER_MODES}")


def parse_tier_models(values: Mapping[str, str] | None = None) -> dict[str, str]:
    """Validate a complete small/medium/big model map."""
    raw = dict(values or {})
    missing = [name for name in TIERS if not raw.get(name)]
    if missing:
        raise ValueError("missing tier model(s): " + ", ".join(missing))
    return {name: raw[name] for name in TIERS}


def split_model_list(raw: str) -> list[str]:
    return [part.strip() for part in raw.split(",") if part.strip()]
