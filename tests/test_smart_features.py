"""Rule matching, budget arithmetic, and deterministic insight regressions."""

import unittest

from expense_analytics.budgets import (
    category_budget_analysis,
    compare_budget,
    month_transactions,
    spending_total,
)
from expense_analytics.categorization import categorize_transactions, suggest_category
from expense_analytics.data import load_expenses
from expense_analytics.insights import spending_insights


class SmartFeatureTests(unittest.TestCase):
    def setUp(self):
        self.frame = load_expenses(
            b"date,description,category,amount\n"
            b"2025-12-31,Coffee,Uncategorized,20\n"
            b"2026-01-01,Rent,Housing,100\n"
            b"2026-01-15,Rent refund,Housing,-10\n"
            b"2026-01-31,Groceries,Groceries,30\n"
            b"2026-03-01,Unknown,Custom,0\n"
        )

    def test_keyword_case_boundaries_phrases_and_precedence(self):
        for text, expected in [
            ("COFFEE!", ("Dining", "coffee")),
            ("Water   BILL", ("Utilities", "water bill")),
            ("rent and coffee", ("Housing", "rent")),
            ("parent business", ("Uncategorized", None)),
        ]:
            with self.subTest(text=text):
                self.assertEqual(suggest_category(text), expected)

    def test_existing_labels_and_audit(self):
        original = self.frame.copy(deep=True)
        self.frame.loc[0, "category"] = "Custom coffee"
        kept, _ = categorize_transactions(self.frame)
        self.assertEqual(kept.iloc[0]["category"], "Custom coffee")
        replaced, audit = categorize_transactions(self.frame, replace_existing=True)
        self.assertEqual(replaced.iloc[0]["category"], "Dining")
        self.assertEqual(replaced.iloc[-1]["category"], "Custom")
        self.assertEqual(audit.iloc[0]["Matched keyword"], "coffee")
        self.assertEqual(audit.iloc[0]["Original category"], "Custom coffee")
        self.assertEqual(self.frame.iloc[0]["category"], "Custom coffee")
        categorized, _ = categorize_transactions(original)
        self.assertEqual(categorized.iloc[0]["category"], "Dining")

    def test_optional_blank_categories_and_unmatched(self):
        for content in [
            b"date,description,amount\n2026-01-01,Coffee,5\n2026-01-02,Mystery,7",
            b"date,description,amount,category\n2026-01-01,Coffee,5,\n2026-01-02,Mystery,7, ",
        ]:
            result, _ = categorize_transactions(load_expenses(content))
            self.assertEqual(result["category"].tolist(), ["Dining", "Uncategorized"])

    def test_budget_thresholds_zero_unset_and_refunds(self):
        self.assertEqual(compare_budget(20, None)["status"], "Not set")
        self.assertEqual(compare_budget(0, 0)["status"], "At budget")
        self.assertEqual(compare_budget(1, 0)["status"], "Over budget")
        self.assertEqual(compare_budget(-10, 0)["remaining"], 10)
        self.assertEqual(compare_budget(100, 100)["status"], "At budget")
        self.assertEqual(compare_budget(101, 100)["remaining"], -1)
        self.assertEqual(compare_budget(99, 100)["status"], "Within budget")
        self.assertEqual(compare_budget(0.1 + 0.2, 0.3)["status"], "At budget")
        self.assertEqual(spending_total([0.1, 0.2, -0.1]), 0.2)
        for value in [-1, float("nan"), float("inf")]:
            with self.assertRaises(ValueError):
                compare_budget(10, value)

    def test_month_boundaries_and_category_analysis(self):
        monthly = month_transactions(self.frame, "2026-01")
        self.assertEqual(spending_total(monthly["amount"]), 120)
        self.assertEqual(len(monthly), 3)
        self.assertTrue(month_transactions(self.frame, "2026-02").empty)
        result = category_budget_analysis(
            self.frame, "2026-01", {"Housing": 80, "Unused": 10}
        ).set_index("category")
        self.assertEqual(result.loc["Housing", "actual"], 90)
        self.assertEqual(result.loc["Housing", "status"], "Over budget")
        self.assertEqual(result.loc["Groceries", "status"], "Not set")
        self.assertEqual(result.loc["Unused", "remaining"], 10)
        self.assertEqual(result.loc["Unused", "actual"], 0)

    def test_insights_are_scoped_and_handle_empty_refunds(self):
        insights = spending_insights(month_transactions(self.frame, "2026-01"))
        self.assertIn("76.9%", insights[0])
        self.assertIn("10.00", insights[-1])
        self.assertEqual(
            spending_insights(self.frame.iloc[:0]),
            ["No transactions in this selection to summarize."],
        )
        refunds = spending_insights(self.frame.loc[self.frame["amount"] < 0])
        self.assertEqual(refunds[0], "This selection has no positive expenses.")
        self.assertTrue(
            any("remain Uncategorized" in line for line in spending_insights(self.frame))
        )
