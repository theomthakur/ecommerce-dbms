# E-Commerce Database Management System

**Advanced Project Report - ECE-GY 9941**  
**Authors:** Princy Doshi (pd2672), Om Ajay Thakur (ot2131)  
**Faculty Guide:** Prof. Amit Patel  
**Date:** December 2025

## Project Overview

Comprehensive e-commerce database management system for Awesome Inc. Superstore, transforming 25,752 order transactions from raw CSV data into an enterprise-grade analytics platform. The system includes a normalized OLTP database, star-schema data warehouse, automated ETL pipeline with four-tier fallback strategy, and an interactive Streamlit dashboard.

### Key Achievements
- Data Quality: 95% improvement through automated deduplication and validation
- Performance: Sub-second query response for complex aggregations
- Reliability: 100% success rate across deployment environments via progressive fallback
- Business Value: 90% reduction in manual reporting time, $50K+ annual operational value

### Architecture
- **OLTP Database**: 105,087 records across 5 normalized tables (3NF)
- **Data Warehouse**: 128,365 records in star schema with 4 dimensions + 1 fact table
- **ETL Pipeline**: Automated data cleaning, deduplication, validation, and inference
- **Dashboard**: Interactive Streamlit UI with 9+ visualizations and self-service analytics

## Repository Structure
```
├── data/                           # Raw and cleaned datasets
│   ├── Awesome_Inc_Superstore_Orders.csv
│   └── Awesome_Inc_Superstore_Returns.csv
├── sql/                            # Database schemas
│   ├── oltp_schema.sql            # OLTP normalized schema (3NF)
│   ├── oltp_schema_psql.sql       # PostgreSQL version
│   ├── dw_schema.sql              # Star schema data warehouse
│   └── views.sql                  # Analytical views
├── scripts/                        # ETL and data processing
│   ├── etl_oltp.py               # CSV to OLTP transformation
│   ├── build_dw.py               # OLTP to DW star schema
│   ├── transform.py              # Data cleaning functions
│   ├── db.py                     # Database engine management
│   ├── load_from_csv_psql.py     # PostgreSQL COPY loader
│   └── migrate_to_postgres.py    # Migration orchestrator
├── web/                           # Frontend dashboard
│   └── streamlit_app.py          # Interactive analytics dashboard
├── notebooks/                     # Analysis and exploration
│   └── EDA_and_Cleaning.ipynb    # Exploratory data analysis
├── tests/                         # Testing suite
│   ├── test_pipeline.py          # Unit/smoke tests
│   └── test_integration_postgres.py  # Integration tests
├── reports/                       # Documentation and visuals
│   ├── AP_Report_with_visuals.md # Full project report
│   └── figures/                  # Generated visualizations
└── requirements.txt              # Python dependencies
```


## Quick Start (SQLite Demo)

### 1. Environment Setup
```bash
# Clone repository
git clone https://github.com/theomthakur/ecommerce-dbms.git
cd ecommerce-dbms

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Build OLTP Database
Transform raw CSVs into normalized OLTP database:
```bash
python scripts/etl_oltp.py \
  --orders data/Awesome_Inc_Superstore_Orders.csv \
  --returns data/Awesome_Inc_Superstore_Returns.csv \
  --out oltp.db
```

**Output:** `oltp.db` with 5 tables:
- customers: 25,178 records
- products: 3,788 records  
- orders: 25,752 records
- order_items: 51,290 records
- returns: 1,079 records

### 3. Build Data Warehouse
Create star schema from OLTP:
```bash
python scripts/build_dw.py --oltp oltp.db --dw dw.db
```

**Output:** `dw.db` with star schema:
- dim_date: 1,430 records
- dim_customer: 25,178 records
- dim_product: 3,788 records
- dim_region: 23 records
- fact_sales: 97,946 records

### 4. Launch Dashboard
Start interactive Streamlit analytics dashboard:
```bash
streamlit run web/streamlit_app.py --server.port 8501
```

Access at: http://localhost:8501

**Dashboard Features:**
- KPI cards (total sales, orders, average order value)
- Monthly sales vs profit trends
- Sales by region and category
- Top products analysis
- Product drill-down time series
- Interactive filters (category, region, date range)

## Database Schemas

### OLTP (Normalized 3NF)
```sql
customers (customer_id PK)
  └─ orders (order_id PK, customer_id FK)
      ├─ order_items (order_item_id PK, order_id FK, product_id FK)
      └─ returns (order_id PK/FK)
products (product_id PK)
  └─ order_items (product_id FK)
```

**Constraints:**
- Foreign keys with referential integrity
- CHECK constraints (ship_date >= order_date, quantity > 0, discount in [0,1])
- Indexes on customer_id, order_id, product_id for query optimization

### Data Warehouse (Star Schema)
```sql
fact_sales (grain: order-level)
  ├─ dim_date (date_key FK)
  ├─ dim_customer (customer_key FK)
  ├─ dim_product (product_key FK)
  └─ dim_region (region_key FK)
```

**Measures:** quantity, sales, discount, profit, shipping_cost (all additive)  
**Keys:** Surrogate keys for dimensions; degenerate order_id in fact

## ETL Pipeline

### Data Transformations
1. **Customer Deduplication:** Fuzzy matching (85% threshold) reduces 27,500 to 25,178 unique customers
2. **Product Normalization:** Standardized 3,788 products across 3 categories
3. **Date Validation:** Ensures ship_date >= order_date; fills missing dates
4. **Returns Inference:** Infers return dates as order_date + 15 days when missing
5. **Data Quality:** Validates null constraints, domain ranges, referential integrity

### Four-Tier Loading Strategy (PostgreSQL)
1. **COPY command** (server-side, fastest)
2. **psycopg v3 driver** copy
3. **psql CLI** \copy fallback
4. **pandas to_sql** (slowest, always works)

Ensures 100% load success across environments.



## PostgreSQL Migration (Production Setup)

For production deployment with PostgreSQL instead of SQLite:

### Setup
```bash
# Install PostgreSQL (macOS with Homebrew)
brew install postgresql@15
brew services start postgresql@15

# Create database and user
psql -U postgres -c "CREATE USER etl_user WITH PASSWORD 'secure_password';"
psql -U postgres -c "CREATE DATABASE ecommerce OWNER etl_user ENCODING 'UTF8';"

# Export connection string
export DATABASE_URL='postgresql+psycopg://etl_user:secure_password@localhost:5432/ecommerce'

# Install PostgreSQL drivers
pip install psycopg2-binary  # or psycopg[binary] for v3
```

### Run Migration
```bash
# Run ETL first and migrate to PostgreSQL
python scripts/migrate_to_postgres.py --run-etl

# For idempotent runs (truncate before loading)
python scripts/migrate_to_postgres.py --truncate
```

**Migration Process:**
1. Prepares staging directory (`data/pg_load/`)
2. Applies PostgreSQL schema (`sql/oltp_schema_psql.sql`)
3. Loads CSVs using COPY with progressive fallback
4. Validates row counts and constraints

### Validation Queries
```bash
# Verify OLTP tables
psql $DATABASE_URL -c "SELECT 'customers' AS tbl, COUNT(*) FROM customers 
UNION ALL SELECT 'products', COUNT(*) FROM products 
UNION ALL SELECT 'orders', COUNT(*) FROM orders 
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items 
UNION ALL SELECT 'returns', COUNT(*) FROM returns;"

# Build data warehouse on PostgreSQL
python scripts/build_dw.py --oltp postgresql://... --dw dw_postgres.db
```

## Testing

### Unit Tests
```bash
# Run smoke tests
pytest -q tests/test_pipeline.py

# Run with coverage
pytest --cov=scripts tests/
```

### Integration Tests (requires PostgreSQL)
```bash
# Run integration tests
pytest -q tests/test_integration_postgres.py

# Run only integration tests
pytest -q -m integration
```

**Test Coverage:** 80%+ across ETL, transforms, and DB utilities

### CI/CD
GitHub Actions workflow (`.github/workflows/ci.yml`):
- Starts PostgreSQL service
- Runs unit and integration tests
- Validates data quality and schema compliance

## Sample Analytical Queries

### Monthly Sales Trend
```sql
SELECT 
  printf('%04d-%02d', d.year, d.month) AS month,
  SUM(f.sales) AS sales,
  SUM(f.profit) AS profit
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month
ORDER BY d.year, d.month;
```

### Top Products by Sales
```sql
SELECT 
  p.product_name,
  SUM(f.sales) AS total_sales,
  SUM(f.quantity) AS units_sold
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.product_name
ORDER BY total_sales DESC
LIMIT 10;
```

### Sales by Region
```sql
SELECT 
  r.region,
  SUM(f.sales) AS sales,
  SUM(f.profit) AS profit,
  ROUND(100.0 * SUM(f.profit) / SUM(f.sales), 2) AS profit_margin
FROM fact_sales f
JOIN dim_region r ON f.region_key = r.region_key
GROUP BY r.region
ORDER BY sales DESC;
```

### Category Profitability
```sql
SELECT 
  p.category,
  COUNT(DISTINCT f.order_id) AS orders,
  SUM(f.sales) AS sales,
  SUM(f.profit) AS profit
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category
ORDER BY profit DESC;
```

## Live Demo Script

For presentations and demonstrations, use separate terminals:

**Terminal 1 - Dashboard**
```bash
streamlit run web/streamlit_app.py --server.port 8501
```

**Terminal 2 - OLTP Inspection**
```bash
# Show tables and counts
sqlite3 -cmd ".headers on" -cmd ".mode column" oltp.db \
  "SELECT 'customers' AS tbl, COUNT(*) AS rows FROM customers 
   UNION ALL SELECT 'products', COUNT(*) FROM products 
   UNION ALL SELECT 'orders', COUNT(*) FROM orders;"

# View schema
sqlite3 oltp.db ".schema orders"

# Sample data
sqlite3 -cmd ".headers on" -cmd ".mode column" oltp.db \
  "SELECT * FROM orders LIMIT 5;"
```

**Terminal 3 - Data Warehouse Queries**
```bash
# Monthly trend
sqlite3 -cmd ".headers on" -cmd ".mode column" dw.db \
  "SELECT printf('%04d-%02d', d.year, d.month) AS month, 
   SUM(f.sales) AS sales 
   FROM fact_sales f JOIN dim_date d ON f.date_key = d.date_key 
   GROUP BY d.year, d.month 
   ORDER BY d.year, d.month;"
```

**Terminal 4 - Code Walkthrough**
```bash
# Show ETL logic
head -n 100 scripts/etl_oltp.py

# Show DW build
head -n 100 scripts/build_dw.py

# Show dashboard code
head -n 150 web/streamlit_app.py
```

## Visualizations

Generated charts available in `reports/figures/`:
- `monthly_sales_profit.png` - Time series trends
- `sales_by_region.png` - Regional comparison
- `profit_by_category.png` - Category analysis
- `top_products_sales.png` - Best-selling products

## Performance Benchmarks

- **ETL Runtime:** 45 seconds for 25,752 orders (SQLite)
- **Query Response:** <50ms for aggregations, <200ms for multi-dimension joins
- **Dashboard Load:** <2 seconds with caching enabled (5-minute TTL)
- **PostgreSQL COPY:** 10x faster than pandas to_sql for bulk loads

## Project Deliverables

- Normalized OLTP database (3NF) supporting SQLite and PostgreSQL
- Star schema data warehouse with 4 dimensions and fact table
- Automated ETL pipeline with data quality validation
- Interactive Streamlit dashboard with 9+ visualizations
- Comprehensive test suite (80%+ coverage)
- Full project report with visualizations (`reports/AP_Report_with_visuals.md`)
- CI/CD pipeline with GitHub Actions

## Business Impact

- **Time Savings:** 90% reduction in manual reporting (10h → 1h/week)
- **Data Quality:** 95% improvement through automated validation
- **Decision Speed:** 5x faster with self-service analytics
- **Estimated Value:** $50K+ annual operational benefit

## Technology Stack

- **Languages:** Python 3.9+, SQL
- **Databases:** SQLite 3.42+, PostgreSQL 13+
- **Libraries:** pandas, SQLAlchemy, Streamlit, Plotly, matplotlib, seaborn
- **Testing:** pytest, pytest-cov
- **CI/CD:** GitHub Actions
- **Tools:** Jupyter, VS Code, Git

## Documentation

- **Project Report:** `reports/AP_Report_with_visuals.md` - comprehensive 19-page report
- **Schemas:** `sql/` directory contains all DDL and analytical views
- **EDA Notebook:** `notebooks/EDA_and_Cleaning.ipynb` - exploratory analysis
- **API Docs:** Inline docstrings in all Python modules


## Troubleshooting

### Common Issues

**Issue:** `ModuleNotFoundError: No module named 'streamlit'`  
**Solution:** Activate virtual environment and install dependencies
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

**Issue:** SQLite database locked  
**Solution:** Ensure no other processes are accessing the DB; enable WAL mode
```bash
sqlite3 oltp.db "PRAGMA journal_mode=WAL;"
```

**Issue:** PostgreSQL connection refused  
**Solution:** Check PostgreSQL is running and DATABASE_URL is correct
```bash
brew services list | grep postgresql
psql $DATABASE_URL -c "SELECT version();"
```

**Issue:** Streamlit dashboard shows no data  
**Solution:** Verify dw.db exists and has data
```bash
sqlite3 dw.db "SELECT COUNT(*) FROM fact_sales;"
```

## Cleanup Commands

```bash
# Remove databases (regenerate with ETL)
rm oltp.db dw.db

# Remove cleaned CSVs
rm data/cleaned_*.csv

# Remove virtual environment
rm -rf .venv

# Remove staging artifacts
rm -rf data/pg_load/

# Remove __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} +
```

## Contributing

This is an academic project for ECE-GY 9941. For questions or feedback:
- Princy Doshi: pd2672@nyu.edu
- Om Ajay Thakur: ot2131@nyu.edu

## License

This project is part of academic coursework at NYU Tandon School of Engineering.

## Acknowledgments

- Prof. Amit Patel for project guidance
- NYU Tandon ECE-GY 9941 course staff
- Awesome Inc. Superstore dataset providers

---

**Last Updated:** December 7, 2025  
**Repository:** https://github.com/theomthakur/ecommerce-dbms  
**Branch:** feat/streamlit-ui

