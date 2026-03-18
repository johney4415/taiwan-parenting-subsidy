"""Tests for the calculator engine."""
from __future__ import annotations

from django.test import SimpleTestCase

from .engine import (
    CalculatorInput,
    calculate_all,
    calculate_birth_bonus,
    calculate_childcare_allowance,
    calculate_daycare_subsidy,
    calculate_parental_leave,
    calculate_recommended_months,
    estimate_monthly_cost,
)


# Sample data for testing
SAMPLE_BIRTH_BONUS_CITY = {
    "name": "台北市",
    "amounts": [
        {"birth_order": 1, "amount": 40000, "note": ""},
        {"birth_order": 2, "amount": 45000, "note": ""},
        {"birth_order": 3, "amount": 50000, "note": ""},
    ],
    "eligibility": {"registration_months": 10, "income_limit": None},
    "application_deadline_days": 60,
}

SAMPLE_CENTRAL_CHILDCARE = {
    "base_amounts": [
        {"birth_order": 1, "monthly": 5000},
        {"birth_order": 2, "monthly": 7000},
        {"birth_order": 3, "monthly": 7000},
    ],
    "eligibility": {"income_tax_rate_limit": 20},
}

SAMPLE_CITY_CHILDCARE_SUPPLEMENT = {
    "amounts": [
        {"birth_order": 1, "monthly": 2500},
        {"birth_order": 2, "monthly": 2500},
    ],
}

SAMPLE_CENTRAL_DAYCARE = {
    "public": {
        "amounts": [
            {"birth_order": 1, "monthly": 7000},
            {"birth_order": 2, "monthly": 9000},
        ],
    },
    "quasi_public": {
        "amounts": [
            {"birth_order": 1, "monthly": 13000},
            {"birth_order": 2, "monthly": 15000},
        ],
    },
    "eligibility": {"income_tax_rate_limit": 20},
}

SAMPLE_PARENTAL_LEAVE = {
    "parental_leave": {
        "salary_replacement_rate": 0.8,
        "max_months": 6,
        "calculation": {"max_insured_salary": 45800},
    },
}

SAMPLE_FEE_DATA = {
    "fee_ranges": {
        "public_daycare": {"typical": 8000},
        "quasi_public_center": {"typical": 15000},
        "private_center": {"typical": 22000},
    },
}


class TestBirthBonus(SimpleTestCase):
    def test_first_child_taipei(self) -> None:
        result = calculate_birth_bonus(SAMPLE_BIRTH_BONUS_CITY, 1)
        assert result is not None
        self.assertEqual(result.amount, 40000)
        self.assertEqual(result.type, "one_time")

    def test_second_child(self) -> None:
        result = calculate_birth_bonus(SAMPLE_BIRTH_BONUS_CITY, 2)
        assert result is not None
        self.assertEqual(result.amount, 45000)

    def test_third_child(self) -> None:
        result = calculate_birth_bonus(SAMPLE_BIRTH_BONUS_CITY, 3)
        assert result is not None
        self.assertEqual(result.amount, 50000)

    def test_fourth_child_uses_third(self) -> None:
        result = calculate_birth_bonus(SAMPLE_BIRTH_BONUS_CITY, 4)
        assert result is not None
        self.assertEqual(result.amount, 50000)

    def test_empty_data(self) -> None:
        result = calculate_birth_bonus({}, 1)
        self.assertIsNone(result)


class TestChildcareAllowance(SimpleTestCase):
    def test_first_child_with_supplement(self) -> None:
        result = calculate_childcare_allowance(
            SAMPLE_CENTRAL_CHILDCARE,
            SAMPLE_CITY_CHILDCARE_SUPPLEMENT,
            birth_order=1,
            income_tax_rate=5,
        )
        assert result is not None
        self.assertEqual(result.amount, 7500)  # 5000 + 2500

    def test_income_too_high(self) -> None:
        result = calculate_childcare_allowance(
            SAMPLE_CENTRAL_CHILDCARE,
            SAMPLE_CITY_CHILDCARE_SUPPLEMENT,
            birth_order=1,
            income_tax_rate=20,
        )
        self.assertIsNone(result)

    def test_second_child(self) -> None:
        result = calculate_childcare_allowance(
            SAMPLE_CENTRAL_CHILDCARE,
            SAMPLE_CITY_CHILDCARE_SUPPLEMENT,
            birth_order=2,
            income_tax_rate=5,
        )
        assert result is not None
        self.assertEqual(result.amount, 9500)  # 7000 + 2500


class TestDaycareSubsidy(SimpleTestCase):
    def test_public_first_child(self) -> None:
        result = calculate_daycare_subsidy(
            SAMPLE_CENTRAL_DAYCARE,
            {},
            birth_order=1,
            care_type="public",
            income_tax_rate=5,
        )
        assert result is not None
        self.assertEqual(result.amount, 7000)

    def test_quasi_public_first_child(self) -> None:
        result = calculate_daycare_subsidy(
            SAMPLE_CENTRAL_DAYCARE,
            {},
            birth_order=1,
            care_type="quasi_public",
            income_tax_rate=5,
        )
        assert result is not None
        self.assertEqual(result.amount, 13000)

    def test_private_returns_none(self) -> None:
        result = calculate_daycare_subsidy(
            SAMPLE_CENTRAL_DAYCARE,
            {},
            birth_order=1,
            care_type="private",
            income_tax_rate=5,
        )
        self.assertIsNone(result)

    def test_income_too_high(self) -> None:
        result = calculate_daycare_subsidy(
            SAMPLE_CENTRAL_DAYCARE,
            {},
            birth_order=1,
            care_type="public",
            income_tax_rate=20,
        )
        self.assertIsNone(result)


class TestParentalLeave(SimpleTestCase):
    def test_normal_salary(self) -> None:
        result = calculate_parental_leave(SAMPLE_PARENTAL_LEAVE, 40000)
        assert result is not None
        self.assertEqual(result.amount, 32000)  # 40000 * 0.8
        self.assertEqual(result.duration_months, 6)

    def test_salary_above_cap(self) -> None:
        result = calculate_parental_leave(SAMPLE_PARENTAL_LEAVE, 60000)
        assert result is not None
        self.assertEqual(result.amount, 36640)  # 45800 * 0.8

    def test_zero_salary(self) -> None:
        result = calculate_parental_leave(SAMPLE_PARENTAL_LEAVE, 0)
        self.assertIsNone(result)


class TestMonthlyCost(SimpleTestCase):
    def test_self_care(self) -> None:
        cost = estimate_monthly_cost("self", SAMPLE_FEE_DATA)
        self.assertEqual(cost, 0)

    def test_public_daycare(self) -> None:
        cost = estimate_monthly_cost("public", SAMPLE_FEE_DATA)
        self.assertEqual(cost, 8000)

    def test_quasi_public(self) -> None:
        cost = estimate_monthly_cost("quasi_public", SAMPLE_FEE_DATA)
        self.assertEqual(cost, 15000)


class TestRecommendedMonths(SimpleTestCase):
    def test_returns_12_months(self) -> None:
        result = calculate_recommended_months("public")
        self.assertEqual(len(result), 12)

    def test_public_recommends_winter(self) -> None:
        result = calculate_recommended_months("public")
        # Months 11, 12, 1 should be recommended for public daycare
        recommended = [m["month"] for m in result if m["recommended"]]
        for month in (11, 12, 1):
            self.assertIn(month, recommended)

    def test_scores_in_range(self) -> None:
        result = calculate_recommended_months("public")
        for m in result:
            self.assertGreaterEqual(m["score"], 0)
            self.assertLessEqual(m["score"], 100)


class TestCalculateAll(SimpleTestCase):
    def test_full_calculation_public(self) -> None:
        user_input = CalculatorInput(
            city_code="TPE",
            birth_order=1,
            care_type="public",
            income_tax_rate=5,
            parental_leave=True,
            insured_salary=40000,
        )
        subsidy_data = {
            "birth_bonus": {"cities": {"TPE": SAMPLE_BIRTH_BONUS_CITY}},
            "childcare_allowance": {
                "central": SAMPLE_CENTRAL_CHILDCARE,
                "city_supplements": {"TPE": SAMPLE_CITY_CHILDCARE_SUPPLEMENT},
            },
            "daycare_subsidy": {
                "central": SAMPLE_CENTRAL_DAYCARE,
                "city_supplements": {"TPE": {}},
            },
            "parental_leave": SAMPLE_PARENTAL_LEAVE,
            "daycare_fees": SAMPLE_FEE_DATA,
        }
        result = calculate_all(user_input, subsidy_data)

        # Should have birth bonus as one-time
        self.assertEqual(len(result.one_time_subsidies), 1)
        self.assertEqual(result.one_time_subsidies[0].amount, 40000)

        # Should have daycare subsidy + parental leave (not childcare allowance)
        monthly_names = [s.name for s in result.monthly_subsidies]
        self.assertIn("托育補助", monthly_names)
        self.assertIn("育嬰留停津貼", monthly_names)
        self.assertNotIn("育兒津貼", monthly_names)

    def test_full_calculation_self_care(self) -> None:
        user_input = CalculatorInput(
            city_code="TPE",
            birth_order=1,
            care_type="self",
            income_tax_rate=5,
            parental_leave=False,
            insured_salary=0,
        )
        subsidy_data = {
            "birth_bonus": {"cities": {"TPE": SAMPLE_BIRTH_BONUS_CITY}},
            "childcare_allowance": {
                "central": SAMPLE_CENTRAL_CHILDCARE,
                "city_supplements": {"TPE": SAMPLE_CITY_CHILDCARE_SUPPLEMENT},
            },
            "daycare_subsidy": {"central": SAMPLE_CENTRAL_DAYCARE},
            "parental_leave": SAMPLE_PARENTAL_LEAVE,
            "daycare_fees": SAMPLE_FEE_DATA,
        }
        result = calculate_all(user_input, subsidy_data)

        # Should have childcare allowance (not daycare subsidy)
        monthly_names = [s.name for s in result.monthly_subsidies]
        self.assertIn("育兒津貼", monthly_names)
        self.assertNotIn("托育補助", monthly_names)
        self.assertEqual(result.monthly_cost_estimate, 0)
