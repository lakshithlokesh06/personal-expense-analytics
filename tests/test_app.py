"""Exercise the dashboard widgets and shared filtering through Streamlit."""

import unittest
from datetime import date
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).resolve().parent.parent / "app.py"


class AppTests(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(str(APP_PATH)).run(timeout=20)
        self.assertFalse(self.app.exception)

    def test_sample_dashboard_and_upload_empty_state(self):
        app = self.app
        self.assertEqual(app.title[0].value, "Personal Expense Analytics")
        self.assertEqual(
            [metric.value for metric in app.metric], ["1,520.89", "126.74", "1,200.00", "12"]
        )
        self.assertEqual(len(app.dataframe[-1].value), 12)
        self.assertEqual(len(app.get("vega_lite_chart")) + len(app.get("arrow_vega_lite_chart")), 2)
        self.assertEqual(len(app.dataframe[0].value), 10)
        app.radio[0].set_value("Upload CSV").run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.dataframe), 0)
        self.assertEqual(len(app.info), 1)

    def test_category_and_date_filters_and_reset(self):
        app = self.app
        app.multiselect[0].set_value(["Groceries"]).run()
        self.assertEqual(app.metric[0].value, "87.20")
        self.assertEqual(app.metric[3].value, "2")
        app.date_input(key="expense_start").set_value(date(2026, 9, 7)).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "22.40")
        self.assertEqual(len(app.dataframe[-1].value), 1)
        self.assertEqual(app.dataframe[0].value["description"].tolist(), ["Fresh vegetables"])
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[3].value, "12")
        self.assertEqual(app.date_input(key="expense_start").value, date(2026, 9, 1))
        self.assertEqual(len(app.multiselect[0].value), 8)

    def test_empty_and_invalid_range(self):
        app = self.app
        app.multiselect[0].set_value([]).run()
        self.assertEqual(app.metric[3].value, "0")
        self.assertEqual(len(app.dataframe), 0)
        self.assertTrue(app.info)
        app.date_input(key="expense_start").set_value(date(2026, 9, 10))
        app.date_input(key="expense_end").set_value(date(2026, 9, 2)).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.error[0].value, "Start date must be on or before end date.")
        self.assertEqual(len(app.metric), 0)
        app.button[0].click().run()
        self.assertEqual(app.metric[3].value, "12")

    def test_changed_dataset_resets_stale_filters(self):
        app = self.app
        app.multiselect[0].set_value(["Groceries"]).run()
        app.session_state["expense_dataset"] = "different-file"
        app.run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[3].value, "12")
