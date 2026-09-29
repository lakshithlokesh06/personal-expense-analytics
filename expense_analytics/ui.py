"""Reusable interface components for the expense workspace."""

import pandas as pd
import streamlit as st

from expense_analytics.data import SAMPLE_PATH


def render_header() -> None:
    st.caption("PERSONAL FINANCE · EXPENSE WORKSPACE")
    st.title("Personal Expense Analytics")
    st.write(
        "Understand your spending. Review transactions, explore patterns, and track monthly budgets."
    )


def render_csv_guide() -> None:
    with st.expander("CSV format guide"):
        st.markdown(
            "Required columns: **date**, **description**, and **amount**. "
            "Use dates in **YYYY-MM-DD** format and plain numeric amounts, "
            "such as **24.50**. Category is optional; keyword rules fill missing labels when possible."
        )
        st.code(
            "date,description,category,amount\n2026-09-01,Weekly groceries,Groceries,64.80",
            language="csv",
        )
        st.caption(
            "UTF-8 CSV · Up to 5 MB · One currency per file. "
            "Negative amounts may represent refunds; zero is allowed. "
            "Extra columns are ignored."
        )
        try:
            sample = SAMPLE_PATH.read_bytes()
        except OSError:
            st.caption("Sample download unavailable. Use the CSV example above as a template.")
        else:
            st.download_button(
                "Download sample CSV",
                data=sample,
                file_name="sample_expenses.csv",
                mime="text/csv",
            )


def render_preview(transactions: pd.DataFrame, source: str) -> None:
    st.divider()
    st.subheader("Transaction preview")
    st.caption(f"{source} · {len(transactions):,} transactions · Showing up to 100 rows")
    render_transactions(transactions.head(100))


def render_transactions(transactions: pd.DataFrame) -> None:
    """Keep date, amount, and column presentation consistent across tables."""
    st.dataframe(
        transactions,
        hide_index=True,
        width="stretch",
        column_config={
            "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
            "description": st.column_config.TextColumn("Description", width="large"),
            "category": st.column_config.TextColumn("Category"),
            "amount": st.column_config.NumberColumn("Amount", format="%.2f"),
        },
    )


def render_about() -> None:
    """Always available, including when the user has no valid dataset loaded."""
    with st.expander("About this project"):
        st.caption("Features, methodology, tech stack, and limitations")
        st.caption("A transparent personal finance dashboard")
        with st.expander("Features and methodology"):
            st.markdown(
                "**Features**\n\n"
                "CSV validation, transaction previews, date/category filters, interactive "
                "charts, keyword categorization, spending insights, and monthly/category budgets.\n\n"
                "**Methodology**\n\n"
                "Net spending includes refunds; average transaction divides net spending by "
                "all selected rows. Highest and top expenses include positive amounts only. "
                "Dates are inclusive. Keyword rules use whole-word matching and first-match priority. "
                "Budgets compare full calendar months independently of dashboard filters."
            )
        with st.expander("Tech stack and limitations"):
            st.markdown(
                "**Tech stack**\n\nPython · Streamlit · pandas · NumPy · Altair. "
                "Tested with unittest and Streamlit AppTest; checked with Ruff and coverage.\n\n"
                "**Limitations**\n\n"
                "One currency per file; no currency conversion, bank connections, or machine learning. "
                "Rules can misclassify ambiguous descriptions. Missing dates may mean incomplete data. "
                "Budgets are session-only and may be lost on reload. Uploads are processed in memory "
                "and are not saved by this app. Charts use recorded data, not forecasts."
            )
        st.caption("Start with the fictional sample, or upload a UTF-8 CSV up to 5 MB.")
