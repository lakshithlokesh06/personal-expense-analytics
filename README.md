# Personal Expense Analytics

A modular Streamlit foundation for uploading, validating, and previewing personal
expense transactions. Includes fictional sample data and a clean interface.
Advanced analytics, charts, storage, and categorization are intentionally deferred.

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
data/sample_expenses.csv     # Fictional example transactions
.streamlit/config.toml       # Theme and upload limit
tests/test_data.py           # CSV validation regression tests
tests/test_app.py            # Streamlit smoke tests
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

UI components use the official [Streamlit APIs](https://docs.streamlit.io/develop/api-reference).
