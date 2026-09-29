"""Streamlit entry point: run with `streamlit run app.py`."""

from hashlib import sha256

import streamlit as st

from expense_analytics.data import ExpenseValidationError, SAMPLE_PATH, load_expenses
from expense_analytics.ui import render_csv_guide, render_header
from expense_analytics.dashboard import render_dashboard
from expense_analytics.smart_ui import render_categorization, render_budgets


def main() -> None:
    st.set_page_config(page_title="Personal Expense Analytics", page_icon="📒", layout="wide")
    render_header()
    render_csv_guide()
    source = st.radio("Choose your data", ["Sample expenses", "Upload CSV"], horizontal=True)
    if source == "Upload CSV":
        uploaded = st.file_uploader("Upload your expense CSV", type=["csv"])
        st.caption("Uploaded data is processed in memory and is not saved by this app.")
        if uploaded is None:
            st.info("Choose a CSV file to validate and preview your transactions.")
            return
        content = uploaded.getvalue()
        label = uploaded.name
    else:
        content = SAMPLE_PATH.read_bytes()
        label = "Sample expenses — fictional data"
    try:
        transactions = load_expenses(content)
    except ExpenseValidationError as exc:
        st.error(str(exc))
        return
    st.success("CSV validated. Your transactions are ready to review.")
    dataset_id = sha256(content).hexdigest()
    transactions, replace = render_categorization(transactions)
    render_dashboard(transactions, label, f"{dataset_id}:{replace}")
    render_budgets(transactions, dataset_id)


if __name__ == "__main__":
    main()
