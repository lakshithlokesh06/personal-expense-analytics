# Personal Expense Analytics

A modular Streamlit dashboard for uploading, validating, and exploring personal
expense transactions. Includes fictional sample data, shared filters, summary
metrics, interactive charts, ranked expenses, transparent keyword categorization,
monthly/category budgets, and rule-based spending insights. No machine learning
or external categorization service is used.

## Run locally

Use Python 3.12–3.14 (release validated locally with Python 3.14). From the project directory:

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

## Quick tour

1. Start with **Sample expenses** to explore 12 fictional transactions.
2. Select a date range or categories, inspect the charts, then use **Reset filters**.
3. Select **Upload CSV** to load your own data; validation errors explain what to fix.
4. Open the categorization review to inspect matched keywords before enabling replacement.
5. Enter a monthly budget, then optional category limits. Clear a limit to remove it.
6. Open **About this project** for methodology, stack, and limitations.

The sample's net spending is **1,520.89**, average transaction **126.74**, highest
expense **1,200.00**, and transaction count **12**. Its dates span one month, so the
monthly trend contains one point.

## Tech stack and design

| Layer | Tools / responsibility |
| --- | --- |
| Interface | Streamlit widgets, native layout, loading and recovery states |
| Data | pandas and NumPy for validated transactions and aggregations |
| Charts | Altair with hover details, pan, and zoom |
| Rules | Ordered keyword matching; no machine learning or network service |
| Quality | unittest, Streamlit AppTest, coverage, Ruff, GitHub Actions |

Pure calculation modules are independent of Streamlit. The entry point coordinates
loading, categorization, dashboard rendering, and the separate budget workspace.
Runtime dependencies are pinned to the versions tested for this release. These are
direct dependency pins, not a complete transitive lockfile. Developer tools are
separate in `requirements-dev.txt`.

## Limitations and privacy

This is a local portfolio application, not an accounting system. Use one currency
per file. There is no exchange-rate conversion, bank integration, authentication,
or persistent database. Keyword rules may misclassify ambiguous descriptions.
Duplicate rows are retained; missing dates do not prove zero spending. The preview
is capped at 100 rows, while calculations use all validated rows. Amounts are
stored as numeric values and displayed to two decimals; budgets use half-up
rounding. Budget comparisons are based on the file, not forecasts.

Uploads remain in process memory; the application does not save them to disk or
send them to an external analytics service. Streamlit usage telemetry is disabled.
Budget settings live only in the active session. Do not commit real expense data;
the sample is fictional. This project has not been deployed or published by the
local release process.

## Dashboard

- Total spending, average transaction, highest expense, and transaction count.
- Category breakdown and monthly spending charts with hover details, zoom, and pan.
- The 10 largest positive expenses and a preview of up to 100 filtered transactions.
- Inclusive start/end dates and a category multiselect control dashboard metrics,
  charts, top expenses, transaction preview, and spending insights. The separate
  budget workspace always uses the full selected calendar month.
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

## Smart features

### Automatic categorization

The category column is optional. Missing/blank categories and the labels
`Uncategorized`/`Uncategorised` are assigned using description keywords. Unmatched
transactions remain `Uncategorized`. Existing categories are preserved by default.
Enable **Replace existing categories when a keyword matches** to reclassify matched
transactions; unmatched existing labels are retained. Disabling it restores the
original labels. Changing this option resets dashboard filters to the effective
categories; source files and amounts are never changed.

Rules use case-insensitive whole words or phrases, normalize whitespace, and apply
the first match in this order:

| Category | Keywords |
| --- | --- |
| Housing | rent, mortgage |
| Utilities | electricity, internet, water bill, gas bill, broadband |
| Groceries | groceries, grocery, supermarket, vegetables |
| Transport | train, bus, taxi, uber, fuel, parking |
| Health | pharmacy, doctor, hospital, medicine |
| Dining | coffee, cafe, restaurant, lunch, dinner |
| Entertainment | movie, cinema, netflix, concert |
| Shopping | notebook, pens, clothes, shoes |

For example, `COFFEE!` matches Dining, `parent` does not match rent, and
`rent and coffee` matches Housing because its rule comes first. Edit
`CATEGORY_RULES` in `expense_analytics/categorization.py` to extend the rules.
Open **Automatic categorization · rules and review** and enable **Show categorization
review** to see original and assigned categories, matched keywords, and decisions.
Rules are simple heuristics and can misclassify ambiguous descriptions.

### Monthly and category budgets

Choose a calendar month in **Monthly budgets** and enter an overall limit. Months
between the earliest and latest loaded transactions are selectable, including gaps.
Within **Category budgets and analysis**, choose a category and enter its monthly
limit. You can set multiple category limits by switching categories.

- Budgets are stored separately per dataset and month in the current Streamlit
  session. They survive filter changes and month/category switches, but are not
  saved to disk and may be lost on reload, disconnect, or server restart.
- Blank means **Not set**; zero is an explicit zero-spending limit. Clear an input
  to remove that budget. Negative and non-finite budgets are rejected.
- Actual is the sum of all loaded amounts in the selected month, including refunds,
  independent of dashboard filters. Remaining = budget − actual. Comparisons round
  monetary values to two decimal places, half up.
- Actual above budget triggers an overspending alert; equal spending is **At budget**.
  No budget means no overspending alert. Negative net spending increases remaining
  budget. No percentage division is used for zero budgets.
- Category analysis lists actual, budget, remaining, and status, including unbudgeted
  categories and budgeted categories with no spending. Category budgets and the
  overall budget are independent; a warning appears if allocations exceed the total.
- Budget amounts stay attached to their category names if categorization changes;
  actual spending is recomputed, and any previously budgeted category remains visible.
- The comparison chart shows overall budget vs actual. These are recorded amounts,
  not forecasts: missing dates or months may indicate an incomplete CSV.

### Spending insights

The dashboard explains the largest category's share of positive spending, the
largest positive transaction, refund totals, and any uncategorized transactions.
Insights use the current dashboard filters, handle refunds/zero-only selections,
and make no predictions. Refunds are excluded from category-share denominators.

## CSV contract

```csv
date,description,category,amount
2026-09-01,Weekly groceries,Groceries,64.80
2026-09-02,Train pass,Transport,45.00
```

- UTF-8 (optional BOM), comma-separated CSV, no larger than 5 MB.
- Required columns: `date`, `description`, `amount`. Optional: `category`.
  Missing or blank categories are normalized to `Uncategorized` before rule matching.
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
  categorization.py          # Ordered keyword rules and review audit
  budgets.py                 # Month selection and budget comparisons
  insights.py                # Deterministic spending observations
  smart_ui.py                # Categorization controls and budget workspace
data/sample_expenses.csv     # Fictional example transactions
.streamlit/config.toml       # Theme and upload limit
tests/test_data.py           # CSV validation regression tests
tests/test_app.py            # Streamlit dashboard and filter tests
tests/test_analytics.py      # Calculation and analytics edge cases
tests/test_smart_features.py # Rules, budgets, and insights
tests/test_smart_ui.py       # Budget state, alerts, and categorization integration
requirements.txt            # Pinned runtime dependencies
requirements-dev.txt        # Lint and coverage tools
pyproject.toml              # Ruff and coverage settings
.github/workflows/tests.yml # GitHub checks on Python 3.12 and 3.14
tests/test_release.py        # Loading/error recovery and full app checks
RELEASE_CHECKLIST.md         # Local validation results and release notes
.gitignore
README.md
```

Keep future data transformations independent of Streamlit in `expense_analytics/`;
add presentation components to `ui.py` or new focused modules as the app grows.

## Verification

For the standard test suite, after installing runtime dependencies:

```bash
python -m unittest discover -s tests -v
```

For the release checks:

```bash
python -m pip install -r requirements-dev.txt
python -m pip check
python -m ruff check .
python -m ruff format --check .
python -m coverage run -m unittest discover -s tests -v
python -m coverage report
```

Coverage includes branches and enforces an 85% minimum. The GitHub Actions workflow
runs these checks on pushes and pull requests; its remote run is separate from local
validation. See `RELEASE_CHECKLIST.md` for the last locally verified results.

## Troubleshooting

- **Missing package:** activate `.venv` and rerun `python -m pip install -r requirements.txt`.
- **Port already in use:** run `python -m streamlit run app.py --server.port 8502`.
- **Invalid CSV:** use UTF-8, comma separators, ISO dates, and numeric amounts;
  the entire file is rejected until invalid rows are corrected.
- **Missing sample:** restore `data/sample_expenses.csv` or switch to **Upload CSV**.
- **No matching transactions:** choose categories, adjust dates, or reset filters.
- **Budget disappeared:** budgets are session-only; reloads or server restarts can clear them.

## GitHub preparation

Run the release checks before pushing. Include source, tests, configuration, and the
fictional sample. `.gitignore` excludes virtual environments, tool caches, secrets,
and local datasets under `data/` (except the sample). Add ignore rules for any private
files placed elsewhere. The GitHub workflow will run once the repository is pushed.

UI components use the official [Streamlit APIs](https://docs.streamlit.io/develop/api-reference),
including [interactive Altair charts](https://docs.streamlit.io/develop/api-reference/charts/st.altair_chart).
