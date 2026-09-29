"""Monthly budget comparisons with explicit unset and zero-budget semantics."""

import math
from decimal import ROUND_HALF_UP, Decimal

import pandas as pd


def money(value) -> float:
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def spending_total(values) -> float:
    return money(sum((Decimal(str(value)) for value in values), Decimal(0)))


def compare_budget(actual: float, budget: float | None) -> dict:
    actual = money(actual)
    if budget is None:
        return dict(actual=actual, budget=None, remaining=None, status="Not set")
    if not math.isfinite(budget) or budget < 0:
        raise ValueError("Budgets must be finite, non-negative amounts.")
    budget = money(budget)
    remaining = money(budget - actual)
    status = "Over budget" if remaining < 0 else "At budget" if remaining == 0 else "Within budget"
    return dict(actual=actual, budget=budget, remaining=remaining, status=status)


def month_transactions(frame: pd.DataFrame, month: str) -> pd.DataFrame:
    return frame.loc[frame["date"].dt.to_period("M") == pd.Period(month, freq="M")].copy()


def category_budget_analysis(frame: pd.DataFrame, month: str, budgets: dict) -> pd.DataFrame:
    monthly = month_transactions(frame, month)
    categories = sorted(set(frame["category"]) | set(budgets))
    records = []
    for category in categories:
        values = monthly.loc[monthly["category"] == category, "amount"]
        records.append(
            {"category": category, **compare_budget(spending_total(values), budgets.get(category))}
        )
    return pd.DataFrame(records, columns=["category", "actual", "budget", "remaining", "status"])
