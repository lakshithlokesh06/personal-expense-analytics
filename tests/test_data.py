"""Regression coverage for the CSV boundary."""

import unittest

from expense_analytics.data import ExpenseValidationError, SAMPLE_PATH, load_expenses


class ExpenseDataTests(unittest.TestCase):
    def test_sample(self):
        frame = load_expenses(SAMPLE_PATH.read_bytes())
        self.assertEqual(list(frame.columns), ["date", "description", "category", "amount"])
        self.assertEqual(len(frame), 12)
        self.assertEqual(frame.iloc[-1]["amount"], -6.5)

    def test_normalizes_headers_and_retains_quoted_text(self):
        frame = load_expenses(b' Date ,DESCRIPTION, category ,amount,extra\n2026-09-01,"Lunch, coffee", Dining ,0,ignored\n')
        self.assertEqual(frame.iloc[0]["description"], "Lunch, coffee")
        self.assertEqual(frame.iloc[0]["category"], "Dining")
        self.assertEqual(frame.shape, (1, 4))

    def test_rejects_invalid_files(self):
        header = "date,description,category,amount\n"
        examples = [
            b"", b"\xff", header.encode(), b"date,amount\n2026-09-01,2",
            b"date,description,category,amount,Amount\n2026-09-01,A,B,2,3",
            (header + "2026-02-30,A,B,1").encode(),
            (header + "2026-9-01,A,B,1").encode(),
            (header + "2026-09-01, ,B,1").encode(),
            (header + "2026-09-01,A,B,NaN").encode(),
            (header + "2026-09-01,A,B,inf").encode(),
            (header + "2026-09-01,A,B,$10").encode(),
            (header + "2026-09-01,A,B").encode(),
            (header + '2026-09-01,"Unclosed,B,1').encode(),
            b"x" * (5 * 1024 * 1024 + 1),
        ]
        for content in examples:
            with self.subTest(content=content[:80]):
                with self.assertRaises(ExpenseValidationError):
                    load_expenses(content)


if __name__ == "__main__":
    unittest.main()
