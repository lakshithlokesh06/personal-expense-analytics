"""Pure calculations over validated transactions; amounts include refunds."""

from datetime import date

import pandas as pd


def filter_transactions(
    frame: pd.DataFrame, start: date, end: date, categories: list[str]
) -> pd.DataFrame:
    """Apply inclusive dates and selected categories without changing the input."""
    if start > end:
        raise ValueError("Start date must be on or before end date.")
    dates = frame["date"].dt.date
    return frame.loc[dates.between(start, end) & frame["category"].isin(categories)].copy()


def summarize(frame: pd.DataFrame) -> dict:
    amounts = frame["amount"]
    positive = amounts[amounts > 0]
    return {
        "total": float(amounts.sum()),
        "average": float(amounts.mean()) if len(frame) else 0.0,
        "highest": float(positive.max()) if len(positive) else None,
        "count": len(frame),
    }


def category_breakdown(frame: pd.DataFrame) -> pd.DataFrame:
    return (
        frame.groupby("category", as_index=False)["amount"]
        .sum()
        .sort_values(["amount", "category"], ascending=[False, True])
    )


def monthly_spending(frame: pd.DataFrame, start: date, end: date) -> pd.DataFrame:
    """Keep year-month ordering and include zero months across the selected range."""
    if start > end:
        raise ValueError("Start date must be on or before end date.")
    months = pd.period_range(start, end, freq="M")
    totals = frame.groupby(frame["date"].dt.to_period("M"))["amount"].sum()
    return pd.DataFrame(
        {"month": months.to_timestamp(), "amount": totals.reindex(months, fill_value=0).to_numpy()}
    )


def top_expenses(frame: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """Rank positive expenses; preserve source order for equal amounts."""
    return (
        frame.loc[frame["amount"] > 0]
        .sort_values("amount", ascending=False, kind="stable")
        .head(max(0, limit))
        .copy()
    )
