# Personal Expense Analytics

A modular Streamlit dashboard for uploading, validating, and exploring personal
expense transactions. Includes fictional sample data, shared filters, summary
metrics, interactive charts, and ranked expenses. Budgeting and automatic
categorization are not included.

## Run locally

Use Python 3.11 or newer. From the project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

On Windows, create the environment with `python -m venv .venv` and activate it
with `.venv\Scripts\Activate.ps1` in PowerShell instead.
Open the local URL printed in your terminal (normally http://localhost:8501).
Stop the server with Ctrl+C.

The app starts with sample expenses. Select **Upload CSV** to use your own file.
A downloadable sample is available under **CSV format guide**.

## Dashboard

- Total spending, average transaction, highest expense, and transaction count.
- Category breakdown and monthly spending charts with hover details, zoom, and pan.
- The 10 largest positive expenses and a preview of up to 100 filtered transactions.
- Inclusive start/end dates and a category multiselect control every dashboard view.
- **Reset filters** restores the full date range and all categories. Loading a
  different dataset also resets filters. Clearing all categories selects no rows.
- Totals, category/monthly sums, and averages include negative refunds and zero
  amounts; averages divide net spending by all selected transactions. Highest and
  top expenses use positive amounts only; the highest shows a dash when absent.
- Months without transactions show zero across the selected date range. Boundary
  months include only selected dates. The sample spans one month, so its trend
  initially contains a single point.
- Empty selections show zero total, average, and count, with a clear empty-state
  message. Reversed date ranges show an error until corrected or reset.
- Amounts use the file's currency without assuming a currency symbol.

## CSV contract

```csv
date,description,category,amount
2026-09-01,Weekly groceries,Groceries,64.80
2026-09-02,Train pass,Transport,45.00
```

- UTF-8 (optional BOM), comma-separated CSV, no larger than 5 MB.
- Required columns: `date`, `description`, `category`, `amount`.
- Headers are trimmed and case-insensitive; duplicate or empty headers are rejected.
- Dates must be valid calendar dates in `YYYY-MM-DD` format.
- Every required field must be populated. Amounts must be finite numbers without
  currency symbols or thousands separators. Negative refunds and zero are accepted.
- Use one currency per file; no conversion or currency inference is performed.
- Extra columns are ignored. Empty lines are skipped; duplicate transactions are retained.
- Malformed rows and invalid values reject the whole file with a readable error.
- The preview shows the first 100 transactions in original order; the entire file is validated.

Uploads are processed in memory and are not persisted by the application. Do not
commit personal expense files. The `data/` ignore rule tracks only the sample CSV;
files placed elsewhere need their own ignore rules.

## Structure

```text
app.py                       # App entry point and source selection
expense_analytics/
  __init__.py
  data.py                    # CSV loading, schema, and validation
  ui.py                      # Header, format guide, and preview components
  analytics.py               # Pure filtering, summaries, grouping, and ranking
  dashboard.py               # Shared filter controls, metrics, and charts
data/sample_expenses.csv     # Fictional example transactions
.streamlit/config.toml       # Theme and upload limit
tests/test_data.py           # CSV validation regression tests
tests/test_app.py            # Streamlit dashboard and filter tests
tests/test_analytics.py      # Calculation and analytics edge cases
requirements.txt            # Runtime dependencies
.gitignore
README.md
```

Keep future data transformations independent of Streamlit in `expense_analytics/`;
add presentation components to `ui.py` or new focused modules as the app grows.

## Verification

After installing dependencies:

```bash
python -m unittest discover -s tests -v
```

UI components use the official [Streamlit APIs](https://docs.streamlit.io/develop/api-reference),
including [interactive Altair charts](https://docs.streamlit.io/develop/api-reference/charts/st.altair_chart).
