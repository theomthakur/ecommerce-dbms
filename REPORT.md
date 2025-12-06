Project Report — E-commerce DBMS

Date: 2025-11-22
Branch: feat/streamlit-ui

Overview
--------
This repository implements a complete end-to-end e-commerce deliverable:
- ETL that ingests the provided raw CSVs and produces cleaned snapshots.
- A small OLTP schema and an automated migration path to Postgres that favors fast COPY and provides robust fallbacks.
- A lightweight Data Warehouse (star schema) builder producing `dw.db` for analytics.
- A Streamlit dashboard (`web/streamlit_app.py`) with KPI cards, multiple visualizations, filters and CSV export.
- Unit and integration tests plus a GitHub Actions workflow for CI.

This report summarizes what was implemented, how to run and verify it locally, and which screenshots to capture for your deliverable.

Implemented Components
----------------------
1. ETL & Cleaning
- Scripts: `scripts/etl_oltp.py`, `scripts/transform.py`
- Outputs (cleaned snapshots in `data/`):
  - `data/cleaned_orders.csv`
  - `data/cleaned_order_items.csv`
  - `data/cleaned_customers.csv`
  - `data/cleaned_products.csv`
  - `data/cleaned_returns.csv`
- Notes: the returns file includes a heuristic to infer return dates where needed; intermediate artifacts were moved to `data/archive/`.

2. OLTP → Postgres migration
- DDL: `sql/oltp_schema_psql.sql`
- Loader: `scripts/load_from_csv_psql.py` — attempts server COPY via available drivers (`psycopg2`, `psycopg` v3), falls back to client `psql \copy`, and finally to a chunked pandas insert if needed.
- Orchestrator: `scripts/migrate_to_postgres.py` — prepares staging CSVs under `data/pg_load/`, applies DDL, supports `--truncate` for idempotent runs, and prints smoke-test counts after load.
- Robustness: row-count validation after COPY attempts to detect silent failures and trigger fallbacks.

3. Data Warehouse (DW)
- DW DDL: `sql/dw_schema.sql`
- Builder: `scripts/build_dw.py` — reads OLTP SQLite, builds dimensions (`dim_date`, `dim_customer`, `dim_product`, `dim_region`) and `fact_sales` and writes `dw.db`.

4. Streamlit Dashboard
- App: `web/streamlit_app.py` (updated on branch `feat/streamlit-ui`)
- Features added:
  - KPI cards: Total Sales, Total Orders, Avg Order Value (filterable by category, region, and date range).
  - Monthly sales time series with CSV export of filtered results.
  - Top-N products (slider) and product drilldown time series.
  - Category Breakdown (treemap).
  - Order Value Distribution histogram with bin and log-scale controls.
  - Returns analysis (return-rate by category) using `data/cleaned_returns.csv`.
  - Top customers chart (Top K slider).
- Caching: helpers use `@st.cache_data` for responsiveness.
- Deprecation fix: replaced `use_container_width=True` with `width='stretch'`.

5. Tests & CI
- Tests added/updated: `tests/test_pipeline.py`, `tests/test_integration_postgres.py`.
- Pytest config: `pytest.ini` registers the `integration` mark.
- CI: `.github/workflows/ci.yml` (pushed to the feature branch) to run tests on GitHub Actions.

Key Files Changed/Added
-----------------------
- web/streamlit_app.py (major UI + helpers; KPI, visualizations, CSV download, caching; deprecation fix)
- scripts/load_from_csv_psql.py (robust COPY + fallbacks)
- scripts/migrate_to_postgres.py (staging and orchestration)
- scripts/build_dw.py (DW builder)
- sql/* (DW and OLTP DDL)
- tests/* (unit and integration tests)
- .github/workflows/ci.yml (CI workflow)

What I validated locally
------------------------
- Unit & smoke tests: `pytest -q` → 4 passed (on local machine where this work was developed).
- Streamlit app: served at `http://localhost:8501`; helpers import cleanly in headless mode.
- Postgres migration: tested previously for both `psycopg2` and `psycopg` dialects with matching smoke counts (customers: 17415, products: 3788, orders: 25728, order_items: 51290, returns: 1079) — re-runable with a provided DB URL.

How to run (quick start)
------------------------
1. Create & activate virtualenv (if not already):
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Build the DW (if you have `oltp.db` or run ETL):
- If you have the OLTP DB already produced by `scripts/etl_oltp.py` (named `oltp.db`):
```bash
python scripts/build_dw.py --oltp oltp.db --dw dw.db
```
- Or run the ETL pipeline to produce `oltp.db` then build DW:
```bash
python scripts/etl_oltp.py --orders data/Awesome_Inc_Superstore_Orders.csv --returns data/Awesome_Inc_Superstore_Returns.csv --out oltp.db
python scripts/build_dw.py --oltp oltp.db --dw dw.db
```

3. Start the Streamlit dashboard:
```bash
streamlit run web/streamlit_app.py --server.port 8501
# then open http://localhost:8501
```

4. Run tests locally:
```bash
pytest -q
```

5. Run Postgres migration (example):
```bash
python scripts/migrate_to_postgres.py --database-url 'postgresql+psycopg2://etl_user:password@localhost:5433/ecommerce' --truncate
```

Screenshots to capture (suggested list)
--------------------------------------
Capture these screenshots to include with the deliverable. Save images into a folder `docs/screenshots/` with the suggested filenames.

1. `01_kpis_filters.png`
- What to show: The top of the Streamlit app showing KPI cards (Total Sales, Total Orders, Avg Order Value) with a specific Category and Region selected in the sidebar and a custom date range.
- Caption: "KPI overview filtered by Category=Furniture, Region=Central US, Date range=2013-01 to 2015-12."

2. `02_monthly_sales_and_download.png`
- What to show: Monthly Sales line chart and the CSV download button; also show the downloaded CSV opened in a spreadsheet if you want an additional image `02a_monthly_sales_csv.png`.
- Caption: "Monthly sales trend and exported filtered CSV."

3. `03_top_products_and_drilldown.png`
- What to show: Top Products bar chart; select a product to show its drilldown time series beneath.
- Caption: "Top products and time series drilldown."

4. `04_category_treemap.png`
- What to show: Category Breakdown treemap.
- Caption: "Treemap: sales share by category."

5. `05_order_value_distribution.png`
- What to show: Histogram of order values; show the histogram with log-scale toggled to illustrate skew.
- Caption: "Order value distribution (log scale enabled)."

6. `06_returns_rate.png`
- What to show: Return Rate by Category bar chart and the returned orders sample table.
- Caption: "Return rates by product category and returned orders sample."

7. `07_top_customers.png`
- What to show: Top Customers bar chart (Top K slider set appropriately).
- Caption: "Top customers by total sales."

8. Optional: `08_streamlit_sidebar.png`
- What to show: The full sidebar with filters and sliders visible.
- Caption: "Interactive filters in the sidebar."

How to capture (macOS quick steps)
---------------------------------
- Quick screenshot of a selected window: press `Cmd+Shift+4`, then press the `Space` bar and click the Streamlit window.
- Screen recording (screencast): use QuickTime → File → New Screen Recording.
- Recommended resolution: 1280×800 or native display; ensure charts and labels are readable.

Embedding screenshots in this report
-----------------------------------
Place screenshots in `docs/screenshots/` and then add relative image links to this `REPORT.md`. Example Markdown snippet to include in this report:

```markdown
### KPI Overview
![KPIs](docs/screenshots/01_kpis_filters.png)
*Figure 1 — KPI overview filtered by category and region.*
```

Testing & CI
------------
- Local: `pytest -q` — currently 4 tests pass on the development machine.
- Remote: push/PR triggers GitHub Actions using `.github/workflows/ci.yml`. Monitor the Actions tab for platform-specific failures (e.g., binary driver builds for `psycopg`).

Known caveats & recommendations
-------------------------------
- The Streamlit `width='stretch'` replacement silences deprecation warnings; all calls were updated.
- Geographic maps are not included because `dim_region` lacks lat/lon. Add a small mapping table if you need region maps.
- For very large `dw.db` files, consider pre-aggregating summary tables to speed the Streamlit UI.
- Postgres integration requires a reachable DB instance. CI may need prebuilt `psycopg` wheels if the runner cannot compile them.

Next steps (suggested)
----------------------
- Create the PR from `feat/streamlit-ui` → `main` (branch already pushed as `origin/feat/streamlit-ui`).
- Attach the screenshots recommended above to the PR and embed them in this `REPORT.md` or the PR description.
- Optionally run Postgres integration in CI or locally and share the test logs.

Appendix — Useful commands
--------------------------
- Run tests:
```bash
pytest -q
```
- Build DW:
```bash
python scripts/build_dw.py --oltp oltp.db --dw dw.db
```
- Run Streamlit:
```bash
streamlit run web/streamlit_app.py --server.port 8501
```
- Run Postgres migration:
```bash
python scripts/migrate_to_postgres.py --database-url 'postgresql+psycopg2://etl_user:password@host:5432/ecommerce' --truncate
```

Contact / Notes
----------------
If you want, I can:
- Open the PR and draft a PR description (requires token or web-UI click).
- Run Postgres migration and integration tests if you provide a DB URL for a dev instance.
- Prepare a short screencast and add it to `docs/` as a demo recording.

---
End of report.
