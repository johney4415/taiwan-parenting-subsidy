"""
Calculation engine for Taiwan parenting subsidies.
This serves as the ground truth for calculations.
The JavaScript engine.js should produce identical results.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CalculatorInput:
    """User input for the subsidy calculator."""

    city_code: str
    birth_order: int  # 1, 2, 3+
    care_type: str  # "self", "public", "quasi_public", "private"
    income_tax_rate: int  # 0, 5, 12, 20, 30, 40
    parental_leave: bool  # Whether taking parental leave
    insured_salary: int  # Monthly insured salary for parental leave calc


@dataclass
class SubsidyResult:
    """Calculation result for a single subsidy item."""

    name: str
    type: str  # "one_time" or "monthly"
    amount: int
    duration_months: int | None = None
    notes: list[str] = field(default_factory=list)


@dataclass
class CalculatorOutput:
    """Full calculation output."""

    one_time_subsidies: list[SubsidyResult] = field(default_factory=list)
    monthly_subsidies: list[SubsidyResult] = field(default_factory=list)
    monthly_cost_estimate: int = 0
    monthly_subsidy_total: int = 0
    monthly_net_cost: int = 0
    recommended_birth_months: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def calculate_birth_bonus(
    city_data: dict[str, Any],
    birth_order: int,
) -> SubsidyResult | None:
    """Calculate birth bonus for a city and birth order."""
    if not city_data:
        return None

    amounts = city_data.get("amounts", [])
    # Find matching birth order, fall back to highest available
    amount = 0
    for entry in amounts:
        if entry["birth_order"] == birth_order:
            amount = entry["amount"]
            break
        if entry["birth_order"] == 3 and birth_order >= 3:
            amount = entry["amount"]
            break

    if amount > 0:
        return SubsidyResult(
            name="生育獎勵金",
            type="one_time",
            amount=amount,
            notes=[f"第{birth_order}胎"],
        )
    return None


def calculate_childcare_allowance(
    central_data: dict[str, Any],
    city_supplement: dict[str, Any],
    birth_order: int,
    income_tax_rate: int,
) -> SubsidyResult | None:
    """Calculate monthly childcare allowance."""
    # Check eligibility
    limit = central_data.get("eligibility", {}).get("income_tax_rate_limit", 20)
    if income_tax_rate >= limit:
        return None

    # Find central amount
    central_amount = 0
    for entry in central_data.get("base_amounts", []):
        if entry["birth_order"] == birth_order:
            central_amount = entry["monthly"]
            break
        if entry["birth_order"] == 3 and birth_order >= 3:
            central_amount = entry["monthly"]
            break

    # Find city supplement
    supplement = 0
    for entry in city_supplement.get("amounts", []):
        if entry["birth_order"] == birth_order:
            supplement = entry["monthly"]
            break
        if entry["birth_order"] == 3 and birth_order >= 3:
            supplement = entry["monthly"]
            break

    total = central_amount + supplement
    if total > 0:
        notes = [f"中央 {central_amount:,} 元/月"]
        if supplement > 0:
            notes.append(f"地方加碼 {supplement:,} 元/月")
        return SubsidyResult(
            name="育兒津貼",
            type="monthly",
            amount=total,
            duration_months=60,  # Up to 5 years
            notes=notes,
        )
    return None


def calculate_daycare_subsidy(
    central_data: dict[str, Any],
    city_supplement: dict[str, Any],
    birth_order: int,
    care_type: str,
    income_tax_rate: int,
) -> SubsidyResult | None:
    """Calculate monthly daycare subsidy."""
    if care_type not in ("public", "quasi_public"):
        return None

    # Check eligibility
    limit = central_data.get("eligibility", {}).get("income_tax_rate_limit", 20)
    if income_tax_rate >= limit:
        return None

    # Get central amount
    type_key = care_type
    type_data = central_data.get(type_key, {})
    central_amount = 0
    for entry in type_data.get("amounts", []):
        if entry["birth_order"] == birth_order:
            central_amount = entry["monthly"]
            break
        if entry["birth_order"] == 3 and birth_order >= 3:
            central_amount = entry["monthly"]
            break

    # Get city supplement
    supplement_key = f"{care_type}_supplement"
    supplement = 0
    for entry in city_supplement.get(supplement_key, []):
        if entry["birth_order"] == birth_order:
            supplement = entry["monthly"]
            break
        if entry["birth_order"] == 3 and birth_order >= 3:
            supplement = entry["monthly"]
            break

    total = central_amount + supplement
    if total > 0:
        care_label = "公共化托育" if care_type == "public" else "準公共化托育"
        notes = [care_label, f"中央 {central_amount:,} 元/月"]
        if supplement > 0:
            notes.append(f"地方加碼 {supplement:,} 元/月")
        return SubsidyResult(
            name="托育補助",
            type="monthly",
            amount=total,
            duration_months=24,  # Up to 2 years
            notes=notes,
        )
    return None


def calculate_parental_leave(
    parental_leave_data: dict[str, Any],
    insured_salary: int,
) -> SubsidyResult | None:
    """Calculate parental leave allowance."""
    pl = parental_leave_data.get("parental_leave", {})
    rate = pl.get("salary_replacement_rate", 0.8)
    max_months = pl.get("max_months", 6)
    max_salary = pl.get("calculation", {}).get("max_insured_salary", 45800)

    effective_salary = min(insured_salary, max_salary)
    amount = int(effective_salary * rate)

    if amount > 0:
        return SubsidyResult(
            name="育嬰留停津貼",
            type="monthly",
            amount=amount,
            duration_months=max_months,
            notes=[
                f"月投保薪資 {effective_salary:,} × {int(rate * 100)}%",
                f"最長 {max_months} 個月",
            ],
        )
    return None


def calculate_central_birth_subsidy(
    central_data: dict[str, Any],
    insured_salary: int,
) -> SubsidyResult | None:
    """Calculate central birth subsidy (2026 guaranteed 100k).

    The government guarantees a minimum of 100,000 NTD per newborn.
    If the social insurance birth benefit is less than 100,000,
    the government tops up the difference.
    """
    cbs = central_data.get("central_birth_subsidy", {})
    guaranteed = cbs.get("amount", 100000)

    # Labor insurance birth benefit = avg insured salary × 2 months
    insurance_benefit = insured_salary * 2
    top_up = max(0, guaranteed - insurance_benefit)
    total = max(guaranteed, insurance_benefit)

    notes = []
    if insurance_benefit > 0:
        notes.append(f"勞保生育給付 {insurance_benefit:,} 元")
        if top_up > 0:
            notes.append(f"中央補足 {top_up:,} 元")
        else:
            notes.append("勞保給付已超過 10 萬，領取較高金額")
    else:
        notes.append("無社會保險，中央全額補助 10 萬元")

    return SubsidyResult(
        name="中央生育補助",
        type="one_time",
        amount=total,
        notes=notes,
    )


def estimate_monthly_cost(
    care_type: str,
    fee_data: dict[str, Any],
    city_public_fee: dict[str, Any] | None = None,
) -> int:
    """Estimate monthly childcare cost before subsidies."""
    fee_ranges = fee_data.get("fee_ranges", {})

    type_map = {
        "self": 0,
        "public": "public_daycare",
        "quasi_public": "quasi_public_center",
        "private": "private_center",
    }

    fee_key = type_map.get(care_type, 0)
    if fee_key == 0:
        return 0

    # Use city-specific public fee if available
    if care_type == "public" and city_public_fee and city_public_fee.get("monthly_fee"):
        return city_public_fee["monthly_fee"]

    range_data = fee_ranges.get(fee_key, {})
    return range_data.get("typical", 0)


def calculate_all(
    user_input: CalculatorInput,
    subsidy_data: dict[str, Any],
) -> CalculatorOutput:
    """Run all calculations and return comprehensive results."""
    output = CalculatorOutput()

    central_birth_data = subsidy_data.get("central_birth_subsidy", {})
    birth_bonus_data = subsidy_data.get("birth_bonus", {})
    childcare_data = subsidy_data.get("childcare_allowance", {})
    daycare_data = subsidy_data.get("daycare_subsidy", {})
    parental_leave_data = subsidy_data.get("parental_leave", {})
    fee_data = subsidy_data.get("daycare_fees", {})

    city_code = user_input.city_code

    # 0. Central birth subsidy (2026 guaranteed 100k)
    cbs = calculate_central_birth_subsidy(
        central_birth_data,
        user_input.insured_salary,
    )
    if cbs:
        output.one_time_subsidies.append(cbs)

    # 1. Birth bonus
    city_bonus = birth_bonus_data.get("cities", {}).get(city_code, {})
    bonus = calculate_birth_bonus(city_bonus, user_input.birth_order)
    if bonus:
        output.one_time_subsidies.append(bonus)

    # 2. Childcare allowance (only if self-care or private)
    if user_input.care_type in ("self", "private"):
        ca = calculate_childcare_allowance(
            childcare_data.get("central", {}),
            childcare_data.get("city_supplements", {}).get(city_code, {}),
            user_input.birth_order,
            user_input.income_tax_rate,
        )
        if ca:
            output.monthly_subsidies.append(ca)

    # 3. Daycare subsidy (only if public or quasi_public)
    if user_input.care_type in ("public", "quasi_public"):
        ds = calculate_daycare_subsidy(
            daycare_data.get("central", {}),
            daycare_data.get("city_supplements", {}).get(city_code, {}),
            user_input.birth_order,
            user_input.care_type,
            user_input.income_tax_rate,
        )
        if ds:
            output.monthly_subsidies.append(ds)

    # 4. Parental leave
    if user_input.parental_leave and user_input.insured_salary > 0:
        pl = calculate_parental_leave(
            parental_leave_data,
            user_input.insured_salary,
        )
        if pl:
            output.monthly_subsidies.append(pl)

    # 5. Cost estimate
    city_public_fee = fee_data.get("city_public_fees", {}).get(city_code, {})
    output.monthly_cost_estimate = estimate_monthly_cost(
        user_input.care_type, fee_data, city_public_fee
    )

    # Calculate totals
    output.monthly_subsidy_total = sum(
        s.amount for s in output.monthly_subsidies if s.name != "育嬰留停津貼"
    )
    output.monthly_net_cost = max(
        0, output.monthly_cost_estimate - output.monthly_subsidy_total
    )

    # 6. Recommended birth months
    output.recommended_birth_months = calculate_recommended_months(user_input.care_type)

    return output


def calculate_recommended_months(care_type: str) -> list[dict[str, Any]]:
    """
    Calculate recommended birth months based on daycare enrollment cycles.

    Key factors:
    - Most public daycares recruit in March-April, admit from April-May
    - Children typically need to be at least 2-3 months old
    - Second enrollment wave around July-August
    - Parental leave is 6 months max
    """
    months = []

    for month in range(1, 13):
        score = 50  # Base score
        pros: list[str] = []
        cons: list[str] = []

        if care_type in ("public", "quasi_public"):
            # Public daycare enrollment timing
            # Main enrollment: April, need to be 2-3+ months old
            # Best: born Nov-Jan → 3-5 months by April
            if month in (11, 12, 1):
                score += 30
                pros.append("出生後 3-5 個月趕上隔年四月公托招生")
            elif month in (2, 3):
                score += 10
                pros.append("可能趕上同年七月第二梯次招生")
            elif month in (4, 5):
                score -= 10
                cons.append("剛出生無法立即入托，需等下次招生梯次")
            elif month in (6, 7, 8):
                score -= 5
                cons.append("需等隔年四月招生，等待期較長")

            # Parental leave alignment
            # 6-month leave ending near enrollment time is ideal
            if month in (10, 11, 12):
                score += 10
                pros.append("六個月育嬰假結束時間接近公托招生期")
        else:
            # Private/self care: no enrollment timing pressure
            pros.append("私托或自行照顧，入托時間較彈性")

        # General considerations
        if month in (1, 2):
            pros.append("農曆年後有較多行政資源處理申請")
        if month in (9, 10):
            score += 5
            pros.append("可趕上下年度政府預算的補助調整")

        months.append(
            {
                "month": month,
                "score": min(100, max(0, score)),
                "pros": pros,
                "cons": cons,
                "recommended": score >= 70,
            }
        )

    return months
