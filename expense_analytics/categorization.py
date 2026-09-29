"""Ordered, whole-word keyword rules. No external services or ML."""

import re

import pandas as pd

# First matching category wins; specific essentials precede broader purchases.
CATEGORY_RULES = (
    ("Housing", ("rent", "mortgage")),
    ("Utilities", ("electricity", "internet", "water bill", "gas bill", "broadband")),
    ("Groceries", ("groceries", "grocery", "supermarket", "vegetables")),
    ("Transport", ("train", "bus", "taxi", "uber", "fuel", "parking")),
    ("Health", ("pharmacy", "doctor", "hospital", "medicine")),
    ("Dining", ("coffee", "cafe", "restaurant", "lunch", "dinner")),
    ("Entertainment", ("movie", "cinema", "netflix", "concert")),
    ("Shopping", ("notebook", "pens", "clothes", "shoes")),
)


def suggest_category(description: str) -> tuple[str, str | None]:
    text = " ".join(description.casefold().split())
    for category, keywords in CATEGORY_RULES:
        for keyword in keywords:
            if re.search(r"(?<!\w)" + re.escape(keyword) + r"(?!\w)", text):
                return category, keyword
    return "Uncategorized", None


def categorize_transactions(
    frame: pd.DataFrame, replace_existing: bool = False
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Fill unknown categories, optionally replace matched existing labels.

    Unmatched existing labels remain intact. Return a separate audit for review.
    """
    result = frame.copy(deep=True)
    audit = []
    categories = []
    for row in frame.itertuples(index=False):
        suggested, keyword = suggest_category(row.description)
        unknown = row.category.strip().casefold() in ("", "uncategorized", "uncategorised")
        assigned = suggested if unknown or (replace_existing and keyword) else row.category
        categories.append(assigned)
        audit.append(
            {
                "Description": row.description,
                "Original category": row.category,
                "Category": assigned,
                "Matched keyword": keyword or "No match",
                "Decision": "Rule applied"
                if keyword and (unknown or replace_existing)
                else "No match"
                if unknown
                else "Existing category kept",
            }
        )
    result["category"] = categories
    return result, pd.DataFrame(audit)
