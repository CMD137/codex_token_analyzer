from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_PRICING_CONFIG = Path(__file__).with_name("pricing_config.json")


def load_pricing_config(config_path: str | Path | None = None) -> dict[str, Any]:
    path = Path(config_path) if config_path else DEFAULT_PRICING_CONFIG
    with open(path, encoding="utf-8") as file_obj:
        config = json.load(file_obj)

    if "profiles" not in config or not isinstance(config["profiles"], dict):
        raise ValueError("Pricing config must define a 'profiles' object.")

    if not config["profiles"]:
        raise ValueError("Pricing config must contain at least one pricing profile.")

    default_profile = config.get("default_profile")
    if default_profile and default_profile not in config["profiles"]:
        raise ValueError(f"Unknown default pricing profile: {default_profile}")

    config["_resolved_path"] = str(path)
    return config


def get_default_profile(config: dict[str, Any]) -> str:
    default_profile = config.get("default_profile")
    if default_profile:
        return str(default_profile)
    return next(iter(config["profiles"]))


def get_profile_names(config: dict[str, Any]) -> list[str]:
    return list(config["profiles"].keys())


def resolve_model_name(model: str | None, config: dict[str, Any]) -> str | None:
    if not model:
        return None

    aliases = config.get("model_aliases") or {}
    resolved = aliases.get(model, model)
    return str(resolved)


def estimate_cost(
    *,
    model: str | None,
    input_tokens: int,
    cached_input_tokens: int,
    output_tokens: int,
    config: dict[str, Any],
    profile_name: str | None = None,
    regional: bool = False,
) -> dict[str, Any]:
    profile_name = profile_name or get_default_profile(config)
    profiles = config["profiles"]
    if profile_name not in profiles:
        raise ValueError(f"Unknown pricing profile: {profile_name}")

    resolved_model = resolve_model_name(model, config)
    if not resolved_model:
        return {
            "status": "missing_model",
            "profile": profile_name,
            "model": model,
            "resolved_model": None,
            "estimated_cost_usd": None,
        }

    model_rates = profiles[profile_name].get(resolved_model)
    if not model_rates:
        return {
            "status": "unknown_model",
            "profile": profile_name,
            "model": model,
            "resolved_model": resolved_model,
            "estimated_cost_usd": None,
        }

    input_rate = float(model_rates["input_per_million"])
    cached_input_rate = model_rates.get("cached_input_per_million")
    cached_input_rate = None if cached_input_rate is None else float(cached_input_rate)
    output_rate = float(model_rates["output_per_million"])

    if cached_input_rate is None:
        billable_input_tokens = input_tokens
        discounted_cached_tokens = 0
    else:
        discounted_cached_tokens = min(max(cached_input_tokens, 0), max(input_tokens, 0))
        billable_input_tokens = max(input_tokens - discounted_cached_tokens, 0)

    input_cost = billable_input_tokens / 1_000_000 * input_rate
    cached_input_cost = discounted_cached_tokens / 1_000_000 * cached_input_rate if cached_input_rate is not None else 0.0
    output_cost = output_tokens / 1_000_000 * output_rate
    subtotal = input_cost + cached_input_cost + output_cost

    uplift_percent = 0.0
    if regional:
        uplift_percent = float(model_rates.get("regional_uplift_percent") or 0.0)

    total = subtotal * (1 + uplift_percent / 100)

    return {
        "status": "priced",
        "profile": profile_name,
        "model": model,
        "resolved_model": resolved_model,
        "estimated_cost_usd": total,
        "subtotal_cost_usd": subtotal,
        "regional_uplift_percent": uplift_percent,
        "input_cost_usd": input_cost,
        "cached_input_cost_usd": cached_input_cost,
        "output_cost_usd": output_cost,
        "billable_input_tokens": billable_input_tokens,
        "discounted_cached_tokens": discounted_cached_tokens,
    }
