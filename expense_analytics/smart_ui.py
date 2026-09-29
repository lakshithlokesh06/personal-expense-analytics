"""Transparent category controls and independent full-month budget workspace."""

import altair as alt
import pandas as pd
import streamlit as st

from expense_analytics.budgets import (
    category_budget_analysis,
    compare_budget,
    month_transactions,
    spending_total,
)
from expense_analytics.categorization import CATEGORY_RULES, categorize_transactions
from expense_analytics.styles import style_chart


def render_categorization(frame: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    with st.expander("Automatic categorization · rules and review"):
        st.caption(
            "Missing or Uncategorized labels are filled automatically. Existing labels are kept "
            "unless you enable replacement. Unmatched descriptions stay Uncategorized."
        )
        replace = st.checkbox(
            "Replace existing categories when a keyword matches", key="replace_categories"
        )
        result, audit = categorize_transactions(frame, replace)
        st.caption(
            "Case-insensitive whole-word/phrase matching. First match wins in the order below. "
            "Disabling replacement restores the original labels. The CSV file is never changed."
        )
        for category, keywords in CATEGORY_RULES:
            st.text(f"{category}: {', '.join(keywords)}")
        if st.checkbox("Show categorization review", key="show_category_review"):
            st.dataframe(audit, hide_index=True, width="stretch")
    return result, replace


def _save_budget(storage_key, field, widget_key) -> None:
    st.session_state["expense_budgets"][storage_key][field] = st.session_state[widget_key]


def _budget_input(label, storage_key, field, widget_key):
    saved = st.session_state["expense_budgets"][storage_key]
    st.session_state[widget_key] = saved.get(field)
    return st.number_input(
        label,
        min_value=0.0,
        value=None,
        step=10.0,
        format="%.2f",
        placeholder="Not set",
        key=widget_key,
        on_change=_save_budget,
        args=(storage_key, field, widget_key),
    )


def render_budgets(frame: pd.DataFrame, dataset_id: str) -> None:
    st.subheader("Plan with perspective")
    st.caption(
        "Uses every loaded transaction in the selected calendar month, independently of dashboard "
        "filters. Actual spending is net of refunds. Missing dates may mean the CSV is incomplete; "
        "amounts are not forecasts. Budgets stay in this session only, separately for each dataset and month."
    )
    months = (
        pd.period_range(frame["date"].min(), frame["date"].max(), freq="M").astype(str).tolist()
    )
    month_key = f"budget_month_{dataset_id}"
    with st.sidebar:
        st.divider()
        st.subheader("Budget controls")
        st.caption("Full calendar month · independent of dashboard filters")
        month = st.selectbox("Budget month", months, index=len(months) - 1, key=month_key)
    storage_key = (dataset_id, month)
    st.session_state.setdefault("expense_budgets", {})
    st.session_state["expense_budgets"].setdefault(storage_key, {})
    saved = st.session_state["expense_budgets"][storage_key]
    with st.sidebar:
        overall = _budget_input("Monthly budget", storage_key, "overall", "monthly_budget_input")
    monthly = month_transactions(frame, month)
    actual = spending_total(monthly["amount"])
    if monthly.empty:
        st.info(
            "No recorded transactions in this month. Actual spending is zero; check that your CSV covers this period."
        )
    comparison = compare_budget(actual, overall)
    st.write(f"Recorded net spending for {month}: **{actual:,.2f}**")
    st.caption(
        "Leave blank for no budget. Zero is an explicit zero-spending limit. Clear an input to remove it."
    )
    if overall is not None:
        st.write(
            f"Budget: **{comparison['budget']:,.2f}** · Remaining: **{comparison['remaining']:,.2f}**"
        )
        if comparison["status"] == "Over budget":
            st.warning(f"Monthly overspending: {-comparison['remaining']:,.2f} over budget.")
        else:
            st.success(f"{comparison['status']} for the recorded transactions.")
        comparison_chart = pd.DataFrame(
            {"Measure": ["Budget", "Actual"], "Amount": [comparison["budget"], actual]}
        )
        st.markdown("**Monthly budget vs. net spending**")
        st.altair_chart(
            style_chart(
                alt.Chart(comparison_chart)
                .mark_bar(color="#087e8b")
                .encode(
                    x=alt.X("Amount:Q", title="Amount (file currency)"),
                    y=alt.Y("Measure:N", title=None),
                    tooltip=[
                        alt.Tooltip("Measure:N", title="Comparison"),
                        alt.Tooltip("Amount:Q", title="Amount", format=",.2f"),
                    ],
                )
                .properties(height=180)
            ),
            width="stretch",
        )
    with st.expander("Category budgets and analysis"):
        available = sorted(
            set(frame["category"]) | {key[1] for key in saved if isinstance(key, tuple)}
        )
        category_key = f"budget_category_{dataset_id}"
        if st.session_state.get(category_key) not in available:
            st.session_state[category_key] = available[0]
        with st.sidebar:
            category = st.selectbox("Budget category", available, key=category_key)
            _budget_input(
                "Category monthly budget",
                storage_key,
                ("category", category),
                "category_budget_input",
            )
        category_budgets = {
            key[1]: value
            for key, value in saved.items()
            if isinstance(key, tuple) and value is not None
        }
        if category_budgets:
            analysis = category_budget_analysis(frame, month, category_budgets)
            st.dataframe(
                analysis,
                hide_index=True,
                width="stretch",
                column_config={
                    "category": "Category",
                    "actual": st.column_config.NumberColumn("Actual", format="%.2f"),
                    "budget": st.column_config.NumberColumn("Budget", format="%.2f"),
                    "remaining": st.column_config.NumberColumn("Remaining", format="%.2f"),
                    "status": "Status",
                },
            )
            for row in analysis.loc[analysis["status"] == "Over budget"].itertuples():
                st.warning(f"{row.category}: {-row.remaining:,.2f} over its monthly budget.")
            allocated = spending_total(category_budgets.values())
            st.caption(
                f"Category budgets allocated: {allocated:,.2f}. Unbudgeted categories show Not set. "
                "Category limits and the overall limit are checked separately."
            )
            if overall is not None and allocated > comparison["budget"]:
                st.warning("Category budgets add up to more than the monthly budget.")
        else:
            st.caption("Choose a category and enter a limit to see category-level comparisons.")
