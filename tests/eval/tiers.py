"""Per-skill eval model tiers.

Each skill has a minimum tier. ``assigned`` runs only that tier's model;
``all`` runs every skill on all three models. Unknown skill names fall
back to medium so a new evals.json is never silently skipped.
"""

from __future__ import annotations

from collections.abc import Mapping

TIERS = ("small", "medium", "big")
TIER_MODES = ("assigned", "all", "small", "medium", "big")
DEFAULT_TIER = "medium"
DEFAULT_TIER_MODELS = {
    "small": "openrouter/qwen/qwen3.7-flash",
    "medium": "openrouter/deepseek/deepseek-v4.1-flash",
    "big": "openrouter/deepseek/deepseek-v4.1-flash",
}

# Skills with no evals.json yet are listed so a later converter run
# picks the right model without a harness edit.
SKILL_TIER: dict[str, str] = {
    "setup-workspace": "medium",
    "setup-python-env": "medium",
    "evaluate-ml-pipeline": "medium",
    "smoke-test-ml-pipeline": "medium",
    "iterate-from-skore": "medium",
    "iterate-from-user": "medium",
    "explore-ml-data": "medium",
    "audit-ml-pipeline": "medium",
    "iterate-ml-experiment": "big",
    "build-ml-pipeline": "big",
}


def skill_tier(skill_name: str) -> str:
    return SKILL_TIER.get(skill_name, DEFAULT_TIER)


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
