"""Deterministic observations about the selected transactions, not predictions."""

import pandas as pd

from expense_analytics.budgets import spending_total


def spending_insights(frame: pd.DataFrame) -> list[str]:
    if frame.empty:
        return ["No transactions in this selection to summarize."]
    insights = []
    positive = frame.loc[frame["amount"] > 0]
    if not positive.empty:
        totals = (
            positive.groupby("category")["amount"].sum().sort_values(ascending=False, kind="stable")
        )
        total = positive["amount"].sum()
        insights.append(
            f"{totals.index[0]} accounts for {totals.iloc[0] / total:.1%} of positive "
            f"spending ({totals.iloc[0]:,.2f}); refunds are excluded from this share."
        )
        insights.append(
            f"The largest positive transaction is {positive['amount'].max():,.2f}; "
            f"the selection contains {len(positive):,} positive transactions."
        )
    else:
        insights.append("This selection has no positive expenses.")
    refunds = frame.loc[frame["amount"] < 0, "amount"]
    if len(refunds):
        insights.append(
            f"{len(refunds):,} refund/credit transaction(s) reduce net spending "
            f"by {-spending_total(refunds):,.2f}."
        )
    unknown = frame["category"].str.casefold().isin(["uncategorized", "uncategorised"])
    if unknown.any():
        insights.append(
            f"{int(unknown.sum()):,} transaction(s) remain Uncategorized; "
            "no keyword rule matched their descriptions."
        )
    return insights
