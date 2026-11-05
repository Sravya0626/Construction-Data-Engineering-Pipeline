import csv
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from src.pipeline import generate_data, read_table, run, validate

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.raw = self.root / "raw"
        generate_data(self.raw)
    def tearDown(self): self.temp.cleanup()
    def test_pipeline_expected_metrics(self):
        rows = run(self.raw, self.root / "warehouse.db", self.root / "out.csv")
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0][0], "P101")
        self.assertEqual(rows[0][4], -70000.0)
        self.assertEqual(rows[0][6], 2)
        self.assertEqual(rows[0][7], 15)
        self.assertEqual(rows[0][8], "OVER_BUDGET")
    def test_idempotent_run(self):
        first = run(self.raw, self.root / "warehouse.db", self.root / "out.csv")
        second = run(self.raw, self.root / "warehouse.db", self.root / "out.csv")
        self.assertEqual(first, second)
        with sqlite3.connect(self.root / "warehouse.db") as c:
            self.assertEqual(c.execute("SELECT count(*) FROM expenses").fetchone()[0], 6)
    def test_reject_orphan_expense(self):
        path = self.raw / "expenses.csv"
        lines = path.read_text().replace("E001,P101", "E001,P999")
        path.write_text(lines)
        with self.assertRaisesRegex(ValueError, "unknown project_id"):
            run(self.raw, self.root / "warehouse.db", self.root / "out.csv")
    def test_reject_duplicate_primary_key(self):
        path = self.raw / "expenses.csv"
        with path.open("a") as f: f.write("E001,P101,2026-05-15,23\n")
        with self.assertRaisesRegex(ValueError, "duplicate"):
            run(self.raw, self.root / "warehouse.db", self.root / "out.csv")
    def test_reject_negative_budget(self):
        path = self.raw / "projects.csv"
        path.write_text(path.read_text().replace("1200000", "-10"))
        with self.assertRaisesRegex(ValueError, "budget must be positive"):
            run(self.raw, self.root / "warehouse.db", self.root / "out.csv")
    def test_schema_change_detection(self):
        path = self.raw / "projects.csv"
        path.write_text(path.read_text().replace("project_name", "name", 1))
        with self.assertRaisesRegex(ValueError, "schema mismatch"):
            run(self.raw, self.root / "warehouse.db", self.root / "out.csv")

if __name__ == "__main__": unittest.main()
