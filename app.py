"""Streamlit entry point: run with `streamlit run app.py`."""

from hashlib import sha256

import streamlit as st

from expense_analytics.dashboard import render_dashboard
from expense_analytics.data import SAMPLE_PATH, ExpenseValidationError, load_expenses
from expense_analytics.smart_ui import render_budgets, render_categorization
from expense_analytics.styles import apply_styles
from expense_analytics.ui import render_about, render_csv_guide, render_header


def main() -> None:
    st.set_page_config(
        page_title="Personal Expense Analytics",
        page_icon="📒",
        layout="wide",
        initial_sidebar_state="auto",
    )
    apply_styles()
    render_header()
    overview, analytics, budget, about = st.tabs(["Overview", "Analytics", "Budget", "About"])
    with about:
        st.subheader("Built for clarity")
        st.caption("Your data, understandable rules, and a transparent view of spending.")
        render_about()
    with st.sidebar:
        st.markdown("### Expense workspace")
        st.caption("DATA SOURCE")
        source = st.radio("Choose your data", ["Sample expenses", "Upload CSV"], horizontal=True)
        render_csv_guide()
        if source == "Upload CSV":
            uploaded = st.file_uploader("Upload your expense CSV", type=["csv"])
            st.caption("Uploaded data is processed in memory and is not saved by this app.")
        else:
            uploaded = None
    if source == "Upload CSV":
        if uploaded is None:
            with overview:
                st.subheader("Your spending story starts here")
                st.info("Choose a CSV file to validate and preview your transactions.")
                st.caption("Use the sidebar to upload a file or explore the fictional sample.")
            with analytics:
                st.caption("Charts and transactions appear once a valid dataset is loaded.")
            with budget:
                st.caption("Load your transactions to compare monthly spending with a budget.")
            return
        content = uploaded.getvalue()
        label = uploaded.name
    else:
        try:
            content = SAMPLE_PATH.read_bytes()
        except OSError:
            with overview:
                st.error(
                    "The sample dataset is unavailable. Restore data/sample_expenses.csv or choose Upload CSV."
                )
            return
        label = "Sample expenses — fictional data"
    try:
        with st.spinner("Validating transactions…"):
            transactions = load_expenses(content)
    except ExpenseValidationError as exc:
        with overview:
            st.error(str(exc))
        st.caption(
            "Correct the file and upload it again, or switch to Sample expenses. See CSV format guide in the sidebar."
        )
        return
    with st.sidebar:
        st.caption("✓ Validated · Ready to explore")
    dataset_id = sha256(content).hexdigest()
    with about:
        with st.spinner("Preparing category rules…"):
            transactions, replace = render_categorization(transactions)
    with overview:
        render_dashboard(transactions, label, f"{dataset_id}:{replace}", analytics_panel=analytics)
    with budget:
        render_budgets(transactions, dataset_id)


if __name__ == "__main__":
    main()
