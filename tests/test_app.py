"""Smoke-test the default preview and upload empty state."""

from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest


class AppTests(unittest.TestCase):
    def test_sample_preview_and_upload_empty_state(self):
        app_path = Path(__file__).resolve().parent.parent / "app.py"
        app = AppTest.from_file(str(app_path)).run(timeout=20)
        self.assertFalse(app.exception)
        self.assertEqual(app.title[0].value, "Personal Expense Analytics")
        self.assertEqual(len(app.dataframe[0].value), 12)
        app.radio[0].set_value("Upload CSV").run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.dataframe), 0)
        self.assertEqual(len(app.info), 1)


if __name__ == "__main__":
    unittest.main()
