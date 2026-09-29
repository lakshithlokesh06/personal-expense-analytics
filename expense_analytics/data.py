"""CSV ingestion and validation, independent of the Streamlit interface."""

import csv
import io
from pathlib import Path

import numpy as np
import pandas as pd

EXPENSE_COLUMNS = ("date", "description", "category", "amount")
REQUIRED_COLUMNS = ("date", "description", "amount")
SAMPLE_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_expenses.csv"
MAX_FILE_BYTES = 5 * 1024 * 1024


class ExpenseValidationError(ValueError):
    """An expense file does not satisfy the expected CSV contract."""


def load_expenses(content: bytes) -> pd.DataFrame:
    """Validate UTF-8 CSV bytes and return the four normalized expense columns.

    Reject the entire file on errors; never silently discard invalid transactions.
    Header names are case-insensitive and surrounding whitespace is removed.
    Additional columns are allowed but omitted from the returned data.
    """
    if len(content) > MAX_FILE_BYTES:
        raise ExpenseValidationError("The CSV must be 5 MB or smaller.")
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ExpenseValidationError("Save the CSV using UTF-8 encoding and try again.") from exc

    try:
        reader = csv.reader(io.StringIO(text, newline=""), strict=True)
        header = next(reader, None)
        if not header:
            raise ExpenseValidationError(
                "The CSV is empty. Add a header and at least one transaction."
            )
        columns = [name.strip().lower() for name in header]
        if any(not name for name in columns) or len(columns) != len(set(columns)):
            raise ExpenseValidationError("Column names must be non-empty and unique.")
        missing = set(REQUIRED_COLUMNS) - set(columns)
        if missing:
            raise ExpenseValidationError(f"Missing required columns: {', '.join(sorted(missing))}.")
        rows = []
        for row in reader:
            if not row:  # Ignore completely empty lines, but validate blank field values.
                continue
            if len(row) != len(columns):
                raise ExpenseValidationError(
                    f"CSV line {reader.line_num} has {len(row)} fields; expected {len(columns)}."
                )
            rows.append(row)
    except csv.Error as exc:
        raise ExpenseValidationError("Malformed CSV. Check delimiters and quoted values.") from exc

    if not rows:
        raise ExpenseValidationError("The CSV contains headers but no transactions.")
    frame = pd.DataFrame(rows, columns=columns)
    if "category" not in frame:
        frame["category"] = "Uncategorized"
    frame = frame.loc[:, list(EXPENSE_COLUMNS)]
    frame = frame.apply(lambda column: column.str.strip())
    frame["category"] = frame["category"].replace("", "Uncategorized")
    errors = []
    for column in REQUIRED_COLUMNS:
        blank = frame[column].eq("")
        if blank.any():
            errors.append(f"{column}: {int(blank.sum())} blank value(s)")

    dates = pd.to_datetime(frame["date"], format="%Y-%m-%d", errors="coerce")
    invalid_dates = ~frame["date"].str.fullmatch(r"\d{4}-\d{2}-\d{2}") | dates.isna()
    if invalid_dates.any():
        errors.append(f"date: {int(invalid_dates.sum())} invalid value(s); use YYYY-MM-DD")
    amounts = pd.to_numeric(frame["amount"], errors="coerce")
    invalid_amounts = ~np.isfinite(amounts)
    if invalid_amounts.any():
        errors.append(
            f"amount: {int(invalid_amounts.sum())} invalid value(s); use finite numbers without currency symbols"
        )
    if errors:
        raise ExpenseValidationError("Please correct the CSV: " + "; ".join(errors) + ".")
    frame["date"] = dates
    frame["amount"] = amounts
    return frame
