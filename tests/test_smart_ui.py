"""Budget persistence, overspending alerts, and categorization UI integration."""

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).resolve().parent.parent / "app.py"
BUDGET_APP = """
import streamlit as st
from expense_analytics.data import load_expenses
from expense_analytics.smart_ui import render_budgets
frame = load_expenses(b"date,description,category,amount\\n2026-01-01,Rent,Housing,100\\n2026-03-01,Coffee,Dining,10")
dataset = st.radio("Dataset", ["first", "second"])
render_budgets(frame, dataset)
"""


class SmartUITests(unittest.TestCase):
    def test_overall_and_category_alerts_survive_dashboard_filters(self):
        app = AppTest.from_file(str(APP_PATH)).run(timeout=20)
        app.number_input(key="monthly_budget_input").set_value(1000.0).run()
        self.assertFalse(app.exception)
        self.assertTrue(any("Monthly overspending: 520.89" in x.value for x in app.warning))
        app.multiselect[0].set_value([]).run()
        self.assertTrue(any("Monthly overspending: 520.89" in x.value for x in app.warning))
        category_select = next(x for x in app.selectbox if x.label == "Budget category")
        category_select.set_value("Housing").run()
        app.number_input(key="category_budget_input").set_value(100.0).run()
        self.assertFalse(app.exception)
        self.assertTrue(any("Housing: 1,100.00" in x.value for x in app.warning))
        app.number_input(key="monthly_budget_input").set_value(None).run()
        self.assertFalse(any("Monthly overspending:" in x.value for x in app.warning))
        app.number_input(key="category_budget_input").set_value(None).run()
        self.assertEqual(len(app.warning), 0)

    def test_month_dataset_and_category_budgets_stay_separate(self):
        app = AppTest.from_string(BUDGET_APP).run(timeout=20)
        self.assertFalse(app.exception)
        app.number_input(key="monthly_budget_input").set_value(20.0).run()
        app.selectbox[0].set_value("2026-01").run()
        self.assertIsNone(app.number_input(key="monthly_budget_input").value)
        app.number_input(key="monthly_budget_input").set_value(50.0).run()
        app.selectbox[1].set_value("Housing").run()
        app.number_input(key="category_budget_input").set_value(60.0).run()
        app.selectbox[1].set_value("Dining").run()
        self.assertIsNone(app.number_input(key="category_budget_input").value)
        app.selectbox[1].set_value("Housing").run()
        self.assertEqual(app.number_input(key="category_budget_input").value, 60)
        app.selectbox[0].set_value("2026-03").run()
        self.assertEqual(app.number_input(key="monthly_budget_input").value, 20)
        app.radio[0].set_value("second").run()
        self.assertIsNone(app.number_input(key="monthly_budget_input").value)
        app.radio[0].set_value("first").run()
        self.assertEqual(app.number_input(key="monthly_budget_input").value, 20)
        app.selectbox[0].set_value("2026-02").run()
        app.number_input(key="monthly_budget_input").set_value(0.0).run()
        self.assertFalse(app.exception)
        self.assertFalse(app.warning)
        self.assertTrue(any("At budget" in x.value for x in app.success))

    def test_categorization_review_and_restore(self):
        app = AppTest.from_string("""
from expense_analytics.data import load_expenses
from expense_analytics.smart_ui import render_categorization
from expense_analytics.dashboard import render_dashboard
frame = load_expenses(b"date,description,category,amount\\n2026-01-01,Coffee,Custom,10\\n2026-01-02,Train,,5")
frame, replace = render_categorization(frame)
render_dashboard(frame, "Test", str(replace))
""").run(timeout=20)
        self.assertFalse(app.exception)
        self.assertIn("Custom", app.multiselect[0].options)
        self.assertIn("Transport", app.multiselect[0].options)
        app.checkbox(key="replace_categories").check().run()
        self.assertIn("Dining", app.multiselect[0].options)
        self.assertNotIn("Custom", app.multiselect[0].options)
        self.assertEqual(app.metric[0].value, "15.00")
        app.checkbox(key="show_category_review").check().run()
        self.assertEqual(app.dataframe[0].value["Matched keyword"].tolist(), ["coffee", "train"])
        app.checkbox(key="replace_categories").uncheck().run()
        self.assertIn("Custom", app.multiselect[0].options)
        self.assertFalse(app.exception)
