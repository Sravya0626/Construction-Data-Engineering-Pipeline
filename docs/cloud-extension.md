# Proposed cloud architecture (design only)

This page describes potential work, not functionality already deployed in this repository.

- **Azure Data Factory:** ingest construction cost and schedule extracts into cloud object storage, manage triggers and execution failures.
- **Databricks / Spark:** implement bronze/silver/gold medallion processing and handle large-scale incremental loads and schema changes.
- **Snowflake:** serve dimensional mart tables and optimize analytics queries.
- **dbt:** manage version-controlled SQL models, tests, lineage, and documentation.
- **Orchestration:** coordinate dependencies, backfills, retries and SLA checks through Dagster or Airflow.
- **Monitoring:** record row counts, freshness, reject counts and processing latency; alert on failures.
- **Security:** separate service identities, least-privilege roles, secure secret storage and non-production sample data.

To turn this into a real cloud demo, build and validate each integration, record evidence (screenshots and logs) and update the README precisely.
