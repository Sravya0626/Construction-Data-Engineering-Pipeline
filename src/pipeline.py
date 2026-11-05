"""Deterministic construction analytics demo with built-in Python libraries."""
import argparse
import csv
import datetime as dt
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "output"
DB = ROOT / "data" / "warehouse.db"

PROJECTS = [
    ("P101", "Highway Interchange", "2026-01-02", 1200000),
    ("P102", "Bridge Reinforcement", "2026-02-10", 800000),
    ("P103", "Hospital Expansion", "2026-03-01", 2000000),
    ("P104", "Water Treatment Upgrade", "2026-01-22", 950000),
]
EXPENSES = [
    ("E001", "P101", "2026-02-01", 450000), ("E002", "P101", "2026-03-01", 820000),
    ("E003", "P102", "2026-04-01", 350000), ("E004", "P102", "2026-05-01", 220000),
    ("E005", "P103", "2026-04-11", 1200000), ("E006", "P104", "2026-05-01", 990000),
]
MILESTONES = [
    ("M001", "P101", "Foundation", "2026-03-01", "2026-03-12"),
    ("M002", "P101", "Concrete", "2026-05-01", "2026-05-05"),
    ("M003", "P102", "Design Approval", "2026-04-05", "2026-04-04"),
    ("M004", "P103", "Permit", "2026-05-20", "2026-06-04"),
    ("M005", "P104", "Excavation", "2026-04-01", "2026-04-01"),
]

def write_csv(path, headers, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(headers); w.writerows(records)

def generate_data(raw=RAW):
    write_csv(raw / "projects.csv", ["project_id", "project_name", "start_date", "budget"], PROJECTS)
    write_csv(raw / "expenses.csv", ["expense_id", "project_id", "expense_date", "amount"], EXPENSES)
    write_csv(raw / "milestones.csv", ["milestone_id", "project_id", "milestone_name", "planned_date", "actual_date"], MILESTONES)

def read_table(raw, name, headers):
    path = raw / (name + ".csv")
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != headers:
            raise ValueError(f"{name}: schema mismatch; expected {headers}, got {reader.fieldnames}")
        return list(reader)

def date_field(value, origin):
    try: return dt.date.fromisoformat(value)
    except (ValueError, TypeError): raise ValueError(f"{origin}: invalid ISO date: {value!r}")

def unique(rows, key, name):
    seen = set()
    for i, r in enumerate(rows, 2):
        value = r[key]
        if not value or value in seen:
            raise ValueError(f"{name} row {i}: blank/duplicate {key}: {value!r}")
        seen.add(value)

def validate(projects, expenses, milestones):
    unique(projects, "project_id", "projects")
    unique(expenses, "expense_id", "expenses")
    unique(milestones, "milestone_id", "milestones")
    ids = {r["project_id"] for r in projects}
    for i, r in enumerate(projects, 2):
        if not r["project_name"].strip(): raise ValueError(f"projects row {i}: blank name")
        date_field(r["start_date"], f"projects row {i}")
        try: budget = float(r["budget"])
        except ValueError: raise ValueError(f"projects row {i}: invalid budget")
        if budget <= 0: raise ValueError(f"projects row {i}: budget must be positive")
    for name, rows, columns in [("expenses", expenses, ["expense_date"]), ("milestones", milestones, ["planned_date", "actual_date"])]:
        for i, r in enumerate(rows, 2):
            if r["project_id"] not in ids: raise ValueError(f"{name} row {i}: unknown project_id")
            for column in columns: date_field(r[column], f"{name} row {i}")
            if name == "expenses":
                try: amount = float(r["amount"])
                except ValueError: raise ValueError(f"expenses row {i}: invalid amount")
                if amount < 0: raise ValueError(f"expenses row {i}: negative amount")
    return True

def run(raw=RAW, db=DB, output=OUT / "project_performance.csv"):
    projects = read_table(raw, "projects", ["project_id", "project_name", "start_date", "budget"])
    expenses = read_table(raw, "expenses", ["expense_id", "project_id", "expense_date", "amount"])
    milestones = read_table(raw, "milestones", ["milestone_id", "project_id", "milestone_name", "planned_date", "actual_date"])
    validate(projects, expenses, milestones)
    db.parent.mkdir(parents=True, exist_ok=True)
    sql = (ROOT / "sql" / "project_performance.sql").read_text(encoding="utf-8")
    with sqlite3.connect(db) as conn:
        with conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS projects (project_id TEXT PRIMARY KEY, project_name TEXT, start_date TEXT, budget REAL);
            CREATE TABLE IF NOT EXISTS expenses (expense_id TEXT PRIMARY KEY, project_id TEXT, expense_date TEXT, amount REAL);
            CREATE TABLE IF NOT EXISTS milestones (milestone_id TEXT PRIMARY KEY, project_id TEXT, milestone_name TEXT, planned_date TEXT, actual_date TEXT);
            """)
            for table in ("milestones", "expenses", "projects"):
                conn.execute(f"DELETE FROM {table}")
            conn.executemany("INSERT INTO projects VALUES (?, ?, ?, ?)", [(r["project_id"],r["project_name"],r["start_date"],float(r["budget"])) for r in projects])
            conn.executemany("INSERT INTO expenses VALUES (?, ?, ?, ?)", [(r["expense_id"],r["project_id"],r["expense_date"],float(r["amount"])) for r in expenses])
            conn.executemany("INSERT INTO milestones VALUES (?, ?, ?, ?, ?)", [(r["milestone_id"],r["project_id"],r["milestone_name"],r["planned_date"],r["actual_date"]) for r in milestones])
        rows = conn.execute(sql)
        columns = [col[0] for col in rows.description]
        result = rows.fetchall()
    output.parent.mkdir(parents=True, exist_ok=True)
    write_csv(output, columns, result)
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate", action="store_true", help="Create synthetic CSV inputs before loading")
    args = parser.parse_args()
    if args.generate: generate_data()
    result = run()
    print(f"Published {len(result)} projects to data/output/project_performance.csv")
