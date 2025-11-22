# E-Commerce OLTP + Data Warehouse Project

This repository contains an end-to-end example project that ingests retail CSVs, builds a normalized OLTP schema, constructs a star-schema data warehouse, and provides exploratory analysis and a Streamlit dashboard. It also includes optional tooling to migrate the generated data to PostgreSQL.

## Contents
- `data/` - raw CSVs and cleaned snapshots produced by ETL.
- `sql/oltp_schema.sql` - SQLite OLTP schema (used by default for local demo).
- `sql/oltp_schema_psql.sql` - PostgreSQL OLTP schema (Postgres-ified DDL).
- `sql/dw_schema.sql` - Data warehouse star schema DDL.
- `sql/views.sql` - Analytical views for common queries.
- `scripts/` - ETL, DW build, DB helpers, loaders, and migration wrapper.
  - `scripts/db.py` - returns SQLAlchemy engine; respects `DATABASE_URL` env var.
  - `scripts/etl_oltp.py` - ETL to transform CSVs into normalized OLTP tables and cleaned CSVs.
  - `scripts/build_dw.py` - build DW from OLTP and write `dw.db`.
  - `scripts/load_from_csv_psql.py` - COPY-based loader for PostgreSQL.
  - `scripts/migrate_to_postgres.py` - wrapper to run ETL (optional), prepare CSVs, apply Postgres DDL, and COPY CSVs.
- `notebooks/EDA_and_Cleaning.ipynb` - exploratory analysis and data cleaning steps.
- `web/streamlit_app.py` - Streamlit dashboard to visualize sales and filters.
- `tests/test_pipeline.py` - minimal smoke tests using `pytest`.
- `requirements.txt` - Python dependencies.

## Quick start (SQLite demo)
1. Create and activate a Python virtual environment (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run the ETL to load the normalized OLTP SQLite DB and produce cleaned CSVs:
   ```bash
   python scripts/etl_oltp.py --orders data/Awesome_Inc_Superstore_Orders.csv --returns data/Awesome_Inc_Superstore_Returns.csv --out oltp.db
   ```
   This writes `oltp.db` and cleaned CSV snapshots into `data/` (e.g. `cleaned_orders.csv`).
3. Build the Data Warehouse (produces `dw.db`):
   ```bash
   python scripts/build_dw.py --oltp oltp.db --dw dw.db
   ```
4. Run the Streamlit dashboard (visual exploration):
   ```bash
   streamlit run web/streamlit_app.py --server.port 8501 --server.headless true
   ```

## Postgres migration (optional)
The repo contains tools to migrate the cleaned CSVs into PostgreSQL if you want a production-like setup.

1. Install Postgres (Homebrew recommended on macOS) or use a managed instance.
2. Create DB user and database (example local dev credentials):
   ```bash
   psql -U postgres -c "CREATE USER etl_user WITH PASSWORD '123';"
   psql -U postgres -c "CREATE DATABASE ecommerce OWNER etl_user ENCODING 'UTF8';"
   ```
3. Install Python deps and export `DATABASE_URL` (the migration supports both `psycopg2` and `psycopg` drivers):
   ```bash
   source .venv/bin/activate
   pip install -r requirements.txt
   # Example DB URL using psycopg (v3) driver on port 5433
   export DATABASE_URL='postgresql+psycopg://etl_user:123@localhost:5433/ecommerce'
   ```
4. Run the migration wrapper. The wrapper prepares a non-destructive staging directory (`data/pg_load/`) and will by default NOT mutate your source `data/` files.
   - To run ETL first (if cleaned CSVs are missing):
     ```bash
     python scripts/migrate_to_postgres.py --run-etl
     ```
   - To ensure idempotent runs during development or CI, the wrapper accepts `--truncate` to truncate the target OLTP tables before loading:
     ```bash
     python scripts/migrate_to_postgres.py --truncate
     ```

What the migration does:
- Prepares `data/pg_load/` and normalizes `cleaned_returns.csv` (maps `Yes/No` to `TRUE/FALSE`).
- Applies `sql/oltp_schema_psql.sql` to the target DB.
- Loads CSVs using PostgreSQL `COPY` (fast). If the driver-specific COPY reports completion but does not increase the table row count, the loader will fall back to a `psql \copy` client fallback and finally to a `pandas.to_sql` fallback.

Notes:
- During debugging the project used `localhost:5433` — if you run a single Postgres instance on `5432`, adjust the `DATABASE_URL` accordingly.
- The staging step performs non-destructive dedupe for large files (customers, orders) into `data/pg_load/` so the original `data/cleaned_*.csv` files are preserved.

**Cleanup & Archive**

- Intermediate analysis artifacts for the returns-date investigation have been moved to `data/archive/` to keep the main `data/` directory focused on source and cleaned snapshots.
- To remove the archive files completely:

```bash
rm data/archive/*.csv
```

- To keep the archive but stop tracking it in git, add it to `.gitignore`:

```text
data/archive/
```

- To remove staging artifacts created during migration (non-destructive staged CSVs), run:

```bash
rm data/pg_load/*.staged.csv
```

- The repository does not remove your virtual environment (`.venv`) automatically. To delete it and reclaim disk space:

```bash
rm -rf .venv
```

**Testing notes**

- There are two kinds of tests in this repo:
   - Unit / smoke tests: `pytest -q tests/test_pipeline.py`
   - Integration parity test (requires a local Postgres instance): `pytest -q tests/test_integration_postgres.py`

- The integration test is marked with `@pytest.mark.integration`. To avoid a Pytest warning about unknown marks or to configure defaults, add a `pytest.ini` file to the project root with the following content:

```ini
[pytest]
markers =
      integration: slow integration tests that require Postgres
```

- To run only integration tests (if you adopt the mark):

```bash
pytest -q -m integration
```

**CI**

- A GitHub Actions workflow was added at `.github/workflows/ci.yml` that starts a Postgres service and runs both unit and the integration parity test. If your CI environment has different credentials or ports, edit the workflow accordingly.

## Notes & Troubleshooting
- If Postgres is already running on `5432`, you can start a secondary local instance on a different port (e.g., `5433`) with Homebrew's `pg_ctl` and point `DATABASE_URL` to that port.
- `scripts/db.py` uses the `DATABASE_URL` environment variable when present; otherwise it falls back to local SQLite for convenience.
- The migration scripts are for local/dev use. For production, change passwords and secure credentials using environment variables or a secrets manager.

## Testing
- Run the smoke tests with `pytest -q tests/test_pipeline.py`.

## Next steps / TODOs
- Add more unit tests for `scripts/transform.py` and edge-case handling.
- Add Alembic for DDL migrations and CI steps to run tests and migration on PRs.

## Contact / help
If you want me to run the Postgres migration here, export `DATABASE_URL` in your shell and tell me to "Run migration now"; I can execute `scripts/migrate_to_postgres.py --run-etl` and paste the output. Alternatively, run the commands locally and paste any errors back here and I will help debug.
# E-Commerce OLTP & Data Warehouse Project

This repository contains a complete implementation for an advanced database project using the provided Awesome Inc Superstore datasets.

What is included
- Project proposal (`proposal.md`)
- OLTP normalized design DDL (`sql/oltp_schema.sql`)
- Data Warehouse (star schema) DDL (`sql/dw_schema.sql`)
- ETL script that cleans the CSVs and populates an OLTP SQLite DB (`scripts/etl_oltp.py`)
- DW build script that creates a star schema SQLite DB from OLTP (`scripts/build_dw.py`)
- `requirements.txt` with Python dependencies

Quick start
1. Create a python environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run ETL to create the OLTP DB (reads CSVs from `data/`):

```bash
python scripts/etl_oltp.py --orders data/Awesome_Inc_Superstore_Orders.csv --returns data/Awesome_Inc_Superstore_Returns.csv
```

This creates `oltp.db` in the repository root.

3. Build the Data Warehouse from `oltp.db`:

```bash
python scripts/build_dw.py --oltp oltp.db --dw dw.db
```

Outputs: `dw.db` SQLite database containing the star schema (`dim_date`, `dim_customer`, `dim_product`, `dim_region`, `fact_sales`).

GitHub
- Initialize a repository, commit files, and push. See `proposal.md` for suggested commit messages and organization.

If you want me to also open a remote repository on GitHub and push the changes, tell me and provide the repo name and permissions details.

Frontend (interactive dashboard)
- A simple Streamlit dashboard is included at `web/streamlit_app.py`. To run it:

```bash
source .venv/bin/activate
pip install -r requirements.txt
streamlit run web/streamlit_app.py
```

This will open a local web UI with monthly sales and top products charts.
