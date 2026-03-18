from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from django.conf import settings


def _load_yaml(file_path: Path) -> dict[str, Any]:
    """Load a YAML file and return its content as a dictionary."""
    with open(file_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


@lru_cache(maxsize=1)
def load_cities() -> list[dict[str, str]]:
    """Load cities data from YAML."""
    data = _load_yaml(settings.DATA_DIR / "cities.yaml")
    return data["cities"]


def get_city_by_slug(slug: str) -> dict[str, str] | None:
    """Find a city by its slug."""
    for city in load_cities():
        if city["slug"] == slug:
            return city
    return None


def get_city_by_code(code: str) -> dict[str, str] | None:
    """Find a city by its code."""
    for city in load_cities():
        if city["code"] == code:
            return city
    return None


@lru_cache(maxsize=1)
def load_birth_bonus() -> dict[str, Any]:
    """Load birth bonus data."""
    return _load_yaml(settings.DATA_DIR / "subsidies" / "birth_bonus.yaml")


@lru_cache(maxsize=1)
def load_childcare_allowance() -> dict[str, Any]:
    """Load childcare allowance data."""
    return _load_yaml(settings.DATA_DIR / "subsidies" / "childcare_allowance.yaml")


@lru_cache(maxsize=1)
def load_daycare_subsidy() -> dict[str, Any]:
    """Load daycare subsidy data."""
    return _load_yaml(settings.DATA_DIR / "subsidies" / "daycare_subsidy.yaml")


@lru_cache(maxsize=1)
def load_parental_leave() -> dict[str, Any]:
    """Load parental leave data."""
    return _load_yaml(settings.DATA_DIR / "subsidies" / "parental_leave.yaml")


@lru_cache(maxsize=1)
def load_daycare_fees() -> dict[str, Any]:
    """Load daycare fees data."""
    return _load_yaml(settings.DATA_DIR / "subsidies" / "daycare_fees.yaml")


@lru_cache(maxsize=1)
def load_central_birth_subsidy() -> dict[str, Any]:
    """Load central birth subsidy (2026 guaranteed 100k) data."""
    return _load_yaml(
        settings.DATA_DIR / "subsidies" / "central_birth_subsidy.yaml"
    )


def load_all_subsidies() -> dict[str, Any]:
    """Load all subsidy data combined."""
    return {
        "central_birth_subsidy": load_central_birth_subsidy(),
        "birth_bonus": load_birth_bonus(),
        "childcare_allowance": load_childcare_allowance(),
        "daycare_subsidy": load_daycare_subsidy(),
        "parental_leave": load_parental_leave(),
        "daycare_fees": load_daycare_fees(),
    }


def get_city_subsidies(city_code: str) -> dict[str, Any]:
    """Get all subsidies for a specific city."""
    birth_bonus = load_birth_bonus()
    childcare = load_childcare_allowance()

    result: dict[str, Any] = {}

    # Central birth subsidy (2026, guaranteed 100k)
    result["central_birth_subsidy"] = load_central_birth_subsidy()

    # Birth bonus
    if city_code in birth_bonus.get("cities", {}):
        result["birth_bonus"] = birth_bonus["cities"][city_code]

    # Childcare allowance (central + city supplement)
    result["childcare_allowance"] = {
        "central": childcare["central"],
        "city_supplement": childcare.get("city_supplements", {}).get(city_code, {}),
    }

    # Daycare subsidy (central + city supplement)
    daycare_data = load_daycare_subsidy()
    result["daycare_subsidy"] = {
        "central": daycare_data["central"],
        "city_supplement": daycare_data.get("city_supplements", {}).get(city_code, {}),
    }

    # Parental leave (same for all cities)
    result["parental_leave"] = load_parental_leave()

    # Daycare fees
    fees = load_daycare_fees()
    result["daycare_fees"] = {
        "fee_ranges": fees["fee_ranges"],
        "city_public_fee": fees.get("city_public_fees", {}).get(city_code, {}),
    }

    return result


def export_all_data_as_json() -> dict[str, Any]:
    """Export all data as a JSON-serializable dictionary for frontend use."""
    return {
        "cities": load_cities(),
        "subsidies": load_all_subsidies(),
    }


def write_json_export(output_dir: Path | None = None) -> Path:
    """Write exported data to JSON file."""
    if output_dir is None:
        output_dir = settings.BASE_DIR / "static" / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    data = export_all_data_as_json()
    output_path = output_dir / "subsidies.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return output_path
