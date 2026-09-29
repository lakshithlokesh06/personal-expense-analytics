"""Release checks for data-source failures and complete app rendering."""

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


class ReleaseTests(unittest.TestCase):
    def test_missing_sample_shows_recovery_and_about(self):
        app = AppTest.from_string("""
from unittest.mock import patch
from app import main
with patch("pathlib.Path.read_bytes", side_effect=FileNotFoundError):
    main()
""").run(timeout=20)
        self.assertFalse(app.exception)
        self.assertIn("Restore data/sample_expenses.csv", app.error[0].value)
        self.assertTrue(any("About this project" == item.label for item in app.expander))
        self.assertEqual(len(app.metric), 0)

    def test_invalid_upload_is_rejected_without_stale_dashboard(self):
        app = AppTest.from_string("""
from io import BytesIO
from unittest.mock import patch
from app import main
uploaded = BytesIO(b"date,description,amount\\n2026-01-01,Coffee,invalid")
uploaded.name = "invalid.csv"
with patch("app.st.radio", return_value="Upload CSV"), patch("app.st.file_uploader", return_value=uploaded):
    main()
""").run(timeout=20)
        self.assertFalse(app.exception)
        self.assertIn("invalid value", app.error[0].value)
        self.assertEqual(len(app.metric), 0)
        self.assertEqual(len(app.number_input), 0)

    def test_valid_upload_single_day_refund_only(self):
        app = AppTest.from_string("""
from io import BytesIO
from unittest.mock import patch
from app import main
uploaded = BytesIO(b"date,description,amount\\n2026-01-01,Refund,-10")
uploaded.name = "refund.csv"
with patch("app.st.radio", return_value="Upload CSV"), patch("app.st.file_uploader", return_value=uploaded):
    main()
""").run(timeout=20)
        self.assertFalse(app.exception)
        self.assertEqual([x.value for x in app.metric], ["-10.00", "-10.00", "—", "1"])
        self.assertTrue(any("No positive expenses" in x.value for x in app.info))
        self.assertEqual(app.dataframe[-1].value["category"].tolist(), ["Uncategorized"])
        app.number_input(key="monthly_budget_input").set_value(0.0).run()
        self.assertFalse(app.exception)
        self.assertFalse(app.warning)

    def test_missing_date_has_recovery_and_preserves_budgets(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parent.parent / "app.py")).run(
            timeout=20
        )
        app.date_input(key="expense_start").set_value(None).run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.metric), 0)
        self.assertTrue(any("Select both dates" in x.value for x in app.info))
        self.assertEqual(len(app.number_input), 2)
