"""Calculation and filter regressions using independently known totals."""

from datetime import date
import unittest

import pandas as pd

from expense_analytics.analytics import (
    category_breakdown, filter_transactions, monthly_spending, summarize, top_expenses,
)
from expense_analytics.data import load_expenses


class AnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.frame = load_expenses(
            b'date,description,category,amount\n'
            b'2025-12-15,Rent,Housing,100\n'
            b'2026-01-01,Lunch,Food,30\n'
            b'2026-01-31,Refund,Food,-10\n'
            b'2026-03-01,Dinner,Food,20\n'
            b'2026-03-01,Free item,Other,0\n'
        )

    def test_metrics_include_refunds(self):
        self.assertEqual(summarize(self.frame),
                         dict(total=140.0, average=28.0, highest=100.0, count=5))

    def test_combined_inclusive_filters_do_not_mutate_input(self):
        original = self.frame.copy(deep=True)
        result = filter_transactions(self.frame, date(2026, 1, 1), date(2026, 1, 31), ['Food'])
        self.assertEqual(result['amount'].tolist(), [30, -10])
        self.assertEqual(summarize(result)['total'], 20)
        pd.testing.assert_frame_equal(self.frame, original)
        self.assertTrue(filter_transactions(self.frame, date(2025, 1, 1), date(2027, 1, 1), []).empty)
        with self.assertRaises(ValueError):
            filter_transactions(self.frame, date(2027, 1, 1), date(2025, 1, 1), ['Food'])

    def test_category_totals(self):
        result = category_breakdown(self.frame).set_index('category')['amount'].to_dict()
        self.assertEqual(result, {'Housing': 100, 'Food': 40, 'Other': 0})

    def test_monthly_order_and_zero_months(self):
        result = monthly_spending(self.frame, date(2025, 12, 1), date(2026, 3, 31))
        self.assertEqual(result['month'].dt.strftime('%Y-%m').tolist(),
                         ['2025-12', '2026-01', '2026-02', '2026-03'])
        self.assertEqual(result['amount'].tolist(), [100, 20, 0, 20])

    def test_top_positive_expenses_and_limit(self):
        self.assertEqual(top_expenses(self.frame, 2)['description'].tolist(), ['Rent', 'Lunch'])
        self.assertEqual(top_expenses(self.frame)['amount'].tolist(), [100, 30, 20])
        self.assertTrue(top_expenses(self.frame, 0).empty)

    def test_empty_and_refund_only(self):
        empty = self.frame.iloc[:0]
        self.assertEqual(summarize(empty), dict(total=0, average=0, highest=None, count=0))
        self.assertTrue(category_breakdown(empty).empty)
        self.assertTrue(top_expenses(empty).empty)
        self.assertEqual(monthly_spending(empty, date(2026, 1, 1), date(2026, 2, 1))['amount'].tolist(), [0, 0])
        refund = self.frame.loc[self.frame['amount'] < 0]
        self.assertEqual(summarize(refund), dict(total=-10, average=-10, highest=None, count=1))
        self.assertTrue(top_expenses(refund).empty)
