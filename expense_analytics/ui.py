"""Reusable interface components for the expense workspace."""

import pandas as pd
import streamlit as st

from expense_analytics.data import SAMPLE_PATH


def render_header() -> None:
    st.caption("PERSONAL FINANCE · EXPENSE WORKSPACE")
    st.title("Personal Expense Analytics")
    st.write("Bring your expenses together. Explore your spending by category and month.")


def render_csv_guide() -> None:
    with st.expander("CSV format guide"):
        st.markdown(
            "Include **date**, **description**, **category**, and **amount** columns. "
            "Use dates in **YYYY-MM-DD** format and plain numeric amounts, "
            "such as **24.50**. Date, description, and amount are required. Category may be omitted or blank; keyword rules will fill it when possible."
        )
        st.code("date,description,category,amount\n2026-09-01,Weekly groceries,Groceries,64.80", language="csv")
        st.caption(
            "UTF-8 CSV · Up to 5 MB · One currency per file. "
            "Negative amounts may represent refunds; zero is allowed. "
            "Extra columns are ignored."
        )
        st.download_button(
            "Download sample CSV", data=SAMPLE_PATH.read_bytes(),
            file_name="sample_expenses.csv", mime="text/csv",
        )


def render_preview(transactions: pd.DataFrame, source: str) -> None:
    st.divider()
    st.subheader("Transaction preview")
    st.caption(f"{source} · {len(transactions):,} transactions · Showing up to 100 rows")
    st.dataframe(
        transactions.head(100), hide_index=True, width="stretch",
        column_config={
            "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
            "description": st.column_config.TextColumn("Description", width="large"),
            "category": st.column_config.TextColumn("Category"),
            "amount": st.column_config.NumberColumn("Amount", format="%.2f"),
        },
    )
