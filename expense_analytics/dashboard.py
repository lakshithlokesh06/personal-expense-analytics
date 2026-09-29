"""Dashboard filters, metrics, and interactive charts."""

import altair as alt
import pandas as pd
import streamlit as st

from expense_analytics.analytics import (
    category_breakdown,
    filter_transactions,
    monthly_spending,
    summarize,
    top_expenses,
)
from expense_analytics.insights import spending_insights
from expense_analytics.ui import render_preview, render_transactions


def reset_filters(start, end, categories) -> None:
    st.session_state["expense_start"] = start
    st.session_state["expense_end"] = end
    st.session_state["expense_categories"] = categories


def render_dashboard(frame: pd.DataFrame, source: str, dataset_id: str) -> None:
    first, last = frame["date"].min().date(), frame["date"].max().date()
    categories = sorted(frame["category"].unique().tolist())
    if st.session_state.get("expense_dataset") != dataset_id or any(
        key not in st.session_state
        for key in ("expense_start", "expense_end", "expense_categories")
    ):
        reset_filters(first, last, categories)
        st.session_state["expense_dataset"] = dataset_id

    st.divider()
    st.subheader("Expense dashboard")
    st.caption(
        "All amounts use your file’s currency. Totals and averages include refunds. "
        "Highest and top expenses include positive amounts only."
    )
    with st.container(border=True):
        left, middle, right = st.columns([1, 1, 2])
        with left:
            start = st.date_input(
                "Start date", min_value=first, max_value=last, key="expense_start"
            )
        with middle:
            end = st.date_input("End date", min_value=first, max_value=last, key="expense_end")
        with right:
            selected = st.multiselect("Categories", categories, key="expense_categories")
        st.button("Reset filters", on_click=reset_filters, args=(first, last, categories))
    if start is None or end is None:
        st.info("Select both dates to view your dashboard.")
        return
    if start > end:
        st.error("Start date must be on or before end date.")
        return
    filtered = filter_transactions(frame, start, end, selected)
    st.caption(
        f"{len(filtered):,} of {len(frame):,} transactions selected · "
        f"{start:%d %b %Y} – {end:%d %b %Y}"
    )
    summary = summarize(filtered)
    metric_columns = [*st.columns(2), *st.columns(2)]
    for column, label, value in zip(
        metric_columns,
        ["Total spending", "Average transaction", "Highest expense", "Transaction count"],
        [
            f"{summary['total']:,.2f}",
            f"{summary['average']:,.2f}",
            f"{summary['highest']:,.2f}" if summary["highest"] is not None else "—",
            f"{summary['count']:,}",
        ],
    ):
        column.metric(label, value, border=True)
    if filtered.empty:
        st.info(
            "No transactions match your filters. Select categories, adjust dates, or reset filters."
        )
        return

    with st.expander("Spending insights", expanded=True):
        st.caption("Observations from your current dashboard selection.")
        for insight in spending_insights(filtered):
            st.write(insight)

    left, right = st.columns(2, gap="large")
    with left:
        st.subheader("Net spending by category")
        chart = (
            alt.Chart(category_breakdown(filtered))
            .mark_bar(color="#2563EB")
            .encode(
                x=alt.X("amount:Q", title="Net spending (file currency)"),
                y=alt.Y("category:N", sort="-x", title=None),
                tooltip=[
                    alt.Tooltip("category:N", title="Category"),
                    alt.Tooltip("amount:Q", title="Net spending (file currency)", format=",.2f"),
                ],
            )
            .properties(height=320)
            .interactive()
        )
        st.altair_chart(chart, width="stretch")
    with right:
        st.subheader("Monthly net spending")
        trend = (
            alt.Chart(monthly_spending(filtered, start, end))
            .mark_line(point=True, color="#2563EB")
            .encode(
                x=alt.X("month:T", title="Month", axis=alt.Axis(format="%b %Y", tickCount="month")),
                y=alt.Y(
                    "amount:Q", title="Net spending (file currency)", scale=alt.Scale(zero=True)
                ),
                tooltip=[
                    alt.Tooltip("month:T", title="Month", format="%B %Y"),
                    alt.Tooltip("amount:Q", title="Net spending (file currency)", format=",.2f"),
                ],
            )
            .properties(height=320)
            .interactive()
        )
        st.altair_chart(trend, width="stretch")
        st.caption(
            "Each point is a calendar month. Missing months show zero; boundary months reflect selected dates."
        )
    st.caption(
        "Hover for values; scroll to zoom, drag to pan, and double-click to restore chart view."
    )
    st.subheader("Top expenses")
    top = top_expenses(filtered)
    if top.empty:
        st.info("No positive expenses in this selection.")
    else:
        st.caption("Up to 10 largest positive transactions in this selection.")
        render_transactions(top)
    render_preview(filtered, source)
