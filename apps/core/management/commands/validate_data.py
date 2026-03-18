from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from apps.core.data_loader import (
    load_birth_bonus,
    load_central_birth_subsidy,
    load_childcare_allowance,
    load_cities,
    load_daycare_fees,
    load_daycare_subsidy,
    load_parental_leave,
)


class Command(BaseCommand):
    help = "Validate all YAML data files for correctness and consistency"

    def handle(self, *args: object, **options: object) -> None:
        errors: list[str] = []

        self.stdout.write("Validating data files...")

        # Validate cities
        try:
            cities = load_cities()
            city_codes = {c["code"] for c in cities}
            city_slugs = {c["slug"] for c in cities}

            if len(city_codes) != len(cities):
                errors.append("Duplicate city codes found")
            if len(city_slugs) != len(cities):
                errors.append("Duplicate city slugs found")
            if len(cities) != 22:
                errors.append(f"Expected 22 cities, found {len(cities)}")

            for city in cities:
                for field in ("code", "name", "slug", "region"):
                    if field not in city:
                        errors.append(f"City missing field: {field}")

            self.stdout.write(f"  Cities: {len(cities)} loaded")
        except Exception as e:
            errors.append(f"Failed to load cities: {e}")

        # Validate birth bonus
        try:
            data = load_birth_bonus()
            bonus_cities = set(data.get("cities", {}).keys())
            missing = city_codes - bonus_cities
            if missing:
                errors.append(f"Birth bonus missing cities: {missing}")

            for code, info in data.get("cities", {}).items():
                if not info.get("amounts"):
                    errors.append(f"Birth bonus {code}: no amounts defined")
                for amt in info.get("amounts", []):
                    if amt["amount"] < 0:
                        errors.append(
                            f"Birth bonus {code}: negative amount {amt['amount']}"
                        )

            self.stdout.write(
                f"  Birth bonus: {len(bonus_cities)} cities loaded"
            )
        except Exception as e:
            errors.append(f"Failed to load birth bonus: {e}")

        # Validate central birth subsidy
        try:
            data = load_central_birth_subsidy()
            cbs = data.get("central_birth_subsidy", {})
            if not cbs.get("amount"):
                errors.append("Central birth subsidy: no amount defined")
            self.stdout.write("  Central birth subsidy: loaded")
        except Exception as e:
            errors.append(f"Failed to load central birth subsidy: {e}")

        # Validate childcare allowance
        try:
            data = load_childcare_allowance()
            if not data.get("central", {}).get("base_amounts"):
                errors.append("Childcare allowance: no central base amounts")
            self.stdout.write("  Childcare allowance: loaded")
        except Exception as e:
            errors.append(f"Failed to load childcare allowance: {e}")

        # Validate daycare subsidy
        try:
            data = load_daycare_subsidy()
            if not data.get("central", {}).get("public", {}).get("amounts"):
                errors.append("Daycare subsidy: no public amounts")
            if not data.get("central", {}).get("quasi_public", {}).get("amounts"):
                errors.append("Daycare subsidy: no quasi-public amounts")
            self.stdout.write("  Daycare subsidy: loaded")
        except Exception as e:
            errors.append(f"Failed to load daycare subsidy: {e}")

        # Validate parental leave
        try:
            data = load_parental_leave()
            pl = data.get("parental_leave", {})
            if not pl.get("salary_replacement_rate"):
                errors.append("Parental leave: no salary replacement rate")
            self.stdout.write("  Parental leave: loaded")
        except Exception as e:
            errors.append(f"Failed to load parental leave: {e}")

        # Validate daycare fees
        try:
            data = load_daycare_fees()
            if not data.get("fee_ranges"):
                errors.append("Daycare fees: no fee ranges defined")
            self.stdout.write("  Daycare fees: loaded")
        except Exception as e:
            errors.append(f"Failed to load daycare fees: {e}")

        # Report results
        if errors:
            self.stderr.write(self.style.ERROR(f"\n{len(errors)} error(s) found:"))
            for error in errors:
                self.stderr.write(self.style.ERROR(f"  - {error}"))
            raise CommandError("Data validation failed")

        self.stdout.write(self.style.SUCCESS("\nAll data files are valid!"))
