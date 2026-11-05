# Construction Project Cost & Schedule Analytics Pipeline

A **portfolio demonstration** of a reproducible batch data engineering workflow for synthetic construction data. **Not affiliated with Kiewit** and contains no real employer/customer data.

## What it does

1. Generates deterministic synthetic projects, expenses, and milestones.
2. Ingests CSVs with Python, applies schema and business-rule checks, and loads an SQLite analytics warehouse.
3. Builds a project performance mart with cost-variance and schedule-delay indicators.
4. Includes repeatable `unittest` checks and GitHub Actions continuous integration.

## Architecture

```text
Synthetic CSVs --> Python validation --> SQLite warehouse --> SQL data mart --> CSV analytics output
                           |                  |                     |
                       error checks       idempotent load         budget/schedule KPIs
```

## Quickstart (Python 3.10+, no third-party packages required)

```bash
python -m src.pipeline --generate
python -m unittest discover -s tests -v
```

Output: `data/warehouse.db` and `data/output/project_performance.csv` (generated locally and gitignored).

## Sample output

See [`docs/sample_project_performance.csv`](docs/sample_project_performance.csv) for a generated sample of the four construction projects.

## Business metrics

- `actual_cost`: sum of posted expense amounts per project.
- `budget_variance`: budget minus actual cost; negative values indicate overrun.
- `budget_utilization_pct`: actual cost / original budget × 100.
- `delay_days`: positive days between actual and planned milestone completion dates.
- `delayed_milestones`: count of late completed milestones.

## Reliability and data quality

- Rejects malformed dates, missing project references, duplicate primary keys, invalid amounts, and nonpositive budgets.
- Database load is transactional: input errors cause rollback, not a partially published mart.
- Load is idempotent: tables are replaced within each successful transaction.
- Validation errors include actionable table/row context.

## Cloud expansion (not implemented in this local demo)

`docs/cloud-extension.md` describes a possible production architecture with Azure Data Factory, Databricks, Snowflake and dbt. The `dbt_example/` directory contains **illustrative** modeling SQL, not a working/deployed dbt project. Do not represent these designs as deployed cloud infrastructure.

## Portfolio discussion prompts

Explain the cost/schedule data contract, the failure/recovery strategy, the modeling choices, how you'd make ingestion incremental, and when you would use Spark/Databricks instead of SQLite.

## Ownership

Independent portfolio project built from synthetic sample data for learning and demonstration. No customer or employer data.
