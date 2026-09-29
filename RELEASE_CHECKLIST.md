# Local release validation

Validated on 2026-09-29 using macOS arm64 and Python 3.14.5.

- [x] All 26 unittest / Streamlit AppTest tests pass.
- [x] Combined statement and branch coverage: 99% (85% minimum enforced).
- [x] Ruff lint and formatting checks pass.
- [x] `pip check` reports no broken requirements.
- [x] Streamlit server starts on localhost and its health endpoint returns `ok`.
- [x] Browser review of sample dashboard, charts, transaction tables, and About layout.
- [x] Recovery tests cover malformed uploads, absent sample files, missing dates,
      empty selections, and a single-day refund-only dataset.
- [x] Existing category rules, filter resets, budget persistence, alerts, and analytics
      regression tests continue to pass.
- [x] Runtime versions pinned; developer dependencies separated.
- [x] README documents setup, usage, schema, methodology, limitations, and checks.
- [x] Private datasets, secrets, virtual environments, and tool caches are ignored.

## Validation scope

Coverage measures executed code paths; it is not a guarantee of every possible input.
Browser checks supplement AppTest's UI state checks. AppTest prints a harmless
`missing ScriptRunContext` warning outside a running browser session.

The GitHub Actions workflow targets Linux with Python 3.12 and 3.14. Those remote
jobs have not been run here; results will be available after the repository is pushed.
No repository has been published and no deployment has been created by this release.

## Repeat the release checks

From an activated Python 3.12–3.14 virtual environment:

```bash
python -m pip install -r requirements-dev.txt
python -m pip check
python -m ruff check .
python -m ruff format --check .
python -m coverage run -m unittest discover -s tests -v
python -m coverage report
python -m streamlit run app.py
```

## Changed files

- `app.py`: loading feedback, missing-file recovery, and About entry point.
- `expense_analytics/ui.py`: consistent transaction tables, About content, and sample-download recovery.
- `expense_analytics/dashboard.py`: two-column metric cards that avoid narrow-window truncation, spacing, explicit chart labels, shared table rendering.
- `expense_analytics/smart_ui.py`: clearer budget chart labels and no-data month guidance.
- `expense_analytics/data.py`: distinguish required CSV inputs from the normalized output schema.
- `expense_analytics/analytics.py`, `budgets.py`, `categorization.py`, `insights.py`:
  consistent formatting and import ordering; calculation behavior preserved.
- Existing five `tests/test_*.py` files: consistent formatting and imports.
- `tests/test_release.py`: four release and recovery integration tests.
- `requirements.txt`: tested direct dependency pins; Python 3.12+ required by NumPy.
- `requirements-dev.txt`, `pyproject.toml`: repeatable lint, formatting, and coverage tooling.
- `.github/workflows/tests.yml`: automatic checks for pushes and pull requests.
- `.gitignore`: ignore new tool outputs.
- `README.md`, `RELEASE_CHECKLIST.md`: usage, methodology, release instructions, and evidence.
