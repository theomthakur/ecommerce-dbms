# Project Proposal — E-Commerce OLTP & Data Warehouse

**Abstract / Executive Summary**

This project ingests and models the "Awesome Inc Superstore" transactional datasets to produce a fully functioning OLTP database and a downstream data warehouse (star schema) suitable for analytics. The deliverables include data cleaning and ETL code, normalized OLTP schema and DDL, implementation scripts that load data into SQLite, a denormalized star schema with `dim_date` and `fact_sales`, and documentation to run and validate the pipeline.

**Purpose / Anticipated Benefits / Justification**
- Provide a reproducible end-to-end pipeline from raw CSVs to an analytics-ready DW.
- Demonstrate practical database design skills: normalization, DDL generation, indexing, and constraints.
- Provide dataset exploration and aggregation capabilities for business stakeholders (sales trends, returns analysis, product performance).

**Objectives (SMART)**
- Specific: Create a normalized OLTP schema, populate it with cleaned data, and create a star-schema DW with `dim_date` and `fact_sales`.
- Measurable: OLTP should contain all orders and items from the provided CSV files; DW should materialize date dimension and aggregated fact rows.
- Achievable: Implementation uses Python, Pandas, and SQLite. All code included.
- Relevant: Focuses on common industry workflows (ETL, data modeling, schema DDL, indexing).
- Time-bound: Target to complete in one work session (today).

**Scope**
- Product Scope: Scripts, DDL, and documentation sufficient to reproduce OLTP and DW databases from the CSVs provided.
- Project Scope: No production orchestration (Airflow) or cloud services — local SQLite and Python scripts are used for reproducibility.

**System**
- Backend: SQLite for OLTP and DW (portable, minimal), Python ETL using Pandas and SQLAlchemy. DDL and SQL files included for portability to other RDBMS.
- Frontend: Not included; analytical queries can be run against the `dw.db` or exported for visualization in tools like Power BI / Tableau.

**Technical Solution Overview**
- Step 1 — Data cleaning: parse dates, coerce numerics, normalize strings.
- Step 2 — OLTP design: normalized tables (`customers`, `products`, `orders`, `order_items`, `returns`) with DDL in `sql/oltp_schema.sql`.
- Step 3 — Load: `scripts/etl_oltp.py` builds `oltp.db` and adds indexes.
- Step 4 — DW design: star schema DDL in `sql/dw_schema.sql`, with `dim_date` (required), `dim_customer`, `dim_product`, `dim_region`, and `fact_sales`.
- Step 5 — DW build: `scripts/build_dw.py` reads OLTP tables and writes `dw.db`.

If you'd like, I can also:
- Replace SQLite with PostgreSQL (Docker) and provide `docker-compose`.
- Create Jupyter notebooks for EDA and sample SQL analytics queries.
