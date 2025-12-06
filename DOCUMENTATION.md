# E-Commerce DBMS - Complete Technical Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Project Architecture](#project-architecture)
3. [Project Flow](#project-flow)
4. [Directory Structure](#directory-structure)
5. [Detailed File Documentation](#detailed-file-documentation)
6. [Data Flow Diagram](#data-flow-diagram)
7. [Setup and Execution Guide](#setup-and-execution-guide)

---

## Project Overview

This project implements a complete end-to-end e-commerce database management system with the following components:
- **ETL Pipeline**: Extracts, transforms, and loads raw CSV data into a normalized OLTP database
- **OLTP Database**: Normalized transactional database (SQLite and PostgreSQL support)
- **Data Warehouse**: Star schema dimensional model for analytics
- **Analytics Dashboard**: Interactive Streamlit web application with visualizations
- **Testing Suite**: Unit and integration tests
- **CI/CD**: GitHub Actions workflow for automated testing

---

## Project Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         RAW DATA                                 │
│          (CSV Files: Orders, Returns)                            │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ETL PIPELINE                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Data Cleaning│->│Transformation│->│ Validation   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CLEANED DATA                                   │
│           (Cleaned CSV Snapshots)                                │
└──────────┬──────────────────────────┬────────────────────────────┘
           │                          │
           ▼                          ▼
┌──────────────────────┐   ┌─────────────────────────┐
│   OLTP DATABASE      │   │   DATA WAREHOUSE        │
│   (SQLite/Postgres)  │   │   (Star Schema)         │
│                      │   │                         │
│  - customers         │   │  - dim_customer         │
│  - products          │   │  - dim_product          │
│  - orders            │   │  - dim_date             │
│  - order_items       │   │  - dim_region           │
│  - returns           │   │  - fact_sales           │
└──────────────────────┘   └────────┬────────────────┘
                                    │
                                    ▼
                          ┌──────────────────────┐
                          │  STREAMLIT DASHBOARD │
                          │                      │
                          │  - KPIs              │
                          │  - Visualizations    │
                          │  - Geographic Map    │
                          │  - Filters           │
                          └──────────────────────┘
```

---

## Project Flow

### 1. Data Ingestion Flow
```
Raw CSV Files
    ↓
[etl_oltp.py]
    ↓
Read & Parse Data
    ↓
[transform.py]
    ↓
Clean & Validate
    ↓
Generate Cleaned CSVs
    ↓
Store in data/ directory
```

### 2. OLTP Database Flow
```
Cleaned CSVs
    ↓
[etl_oltp.py]
    ↓
Apply OLTP Schema (oltp_schema.sql)
    ↓
Load into SQLite (oltp.db)
    ↓
Create Normalized Tables
```

### 3. PostgreSQL Migration Flow
```
Cleaned CSVs
    ↓
[migrate_to_postgres.py]
    ↓
Prepare Staging (data/pg_load/)
    ↓
Apply PostgreSQL Schema (oltp_schema_psql.sql)
    ↓
[load_from_csv_psql.py]
    ↓
Try Server COPY (psycopg2/psycopg)
    ↓
Fallback to psql \copy
    ↓
Final Fallback: pandas insert
    ↓
Validate Row Counts
```

### 4. Data Warehouse Flow
```
OLTP Database (oltp.db)
    ↓
[build_dw.py]
    ↓
Read Transactional Data
    ↓
Transform to Star Schema
    ↓
Create Dimensions (Customer, Product, Date, Region)
    ↓
Create Fact Table (Sales)
    ↓
Write to dw.db
```

### 5. Analytics Dashboard Flow
```
dw.db
    ↓
[streamlit_app.py]
    ↓
Query Dimensional Data
    ↓
Apply User Filters (Category, Region, Date)
    ↓
Generate Visualizations
    ↓
Display in Web Browser
    ↓
User Interaction (Filter, Export)
```

---

## Directory Structure

```
ecommerce-dbms/
│
├── .github/
│   └── workflows/
│       └── ci.yml                    # GitHub Actions CI/CD configuration
│
├── data/                             # Data directory
│   ├── Awesome_Inc_Superstore_Orders.csv      # Raw orders data
│   ├── Awesome_Inc_Superstore_Returns.csv     # Raw returns data
│   ├── cleaned_customers.csv         # Cleaned customer data
│   ├── cleaned_products.csv          # Cleaned product data
│   ├── cleaned_orders.csv            # Cleaned order data
│   ├── cleaned_order_items.csv       # Cleaned order items data
│   ├── cleaned_returns.csv           # Cleaned returns data
│   ├── date_summary.csv              # Date analysis summary
│   ├── archive/                      # Archived intermediate files
│   │   ├── returns_with_inferred_dates.csv
│   │   ├── returns_date_matches.csv
│   │   └── ... (other analysis files)
│   └── pg_load/                      # PostgreSQL staging area
│       ├── cleaned_customers.csv
│       ├── cleaned_products.csv
│       └── ... (staged CSVs for Postgres)
│
├── notebooks/                        # Jupyter notebooks
│   └── EDA_and_Cleaning.ipynb       # Exploratory Data Analysis
│
├── scripts/                          # Python scripts
│   ├── __init__.py                   # Package initializer
│   ├── db.py                         # Database connection utilities
│   ├── logger.py                     # Logging configuration
│   ├── transform.py                  # Data transformation functions
│   ├── etl_oltp.py                   # Main ETL pipeline script
│   ├── build_dw.py                   # Data warehouse builder
│   ├── migrate_to_postgres.py        # PostgreSQL migration orchestrator
│   ├── load_from_csv_psql.py         # PostgreSQL CSV loader with fallbacks
│   ├── create_views.py               # SQL views creator
│   └── cdc_extractor.py              # Change Data Capture utility
│
├── sql/                              # SQL schema definitions
│   ├── oltp_schema.sql               # SQLite OLTP schema
│   ├── oltp_schema_psql.sql          # PostgreSQL OLTP schema
│   ├── dw_schema.sql                 # Data warehouse schema
│   └── views.sql                     # Analytical views
│
├── tests/                            # Test suite
│   ├── test_pipeline.py              # Unit tests for ETL pipeline
│   └── test_integration_postgres.py  # PostgreSQL integration tests
│
├── web/                              # Web application
│   └── streamlit_app.py              # Streamlit dashboard application
│
├── .gitignore                        # Git ignore rules
├── pytest.ini                        # Pytest configuration
├── requirements.txt                  # Python dependencies
├── README.md                         # Project README
├── REPORT.md                         # Implementation report
├── DOCUMENTATION.md                  # This file
└── proposal.md                       # Project proposal
```

---

## Detailed File Documentation

### Root Configuration Files

#### `.gitignore`
**Purpose**: Specifies files and directories that Git should ignore
**Contents**:
- Python cache files (`__pycache__`, `*.pyc`)
- Virtual environments (`.venv`, `venv/`)
- Database files (`*.db`, `*.sqlite`)
- IDE settings (`.vscode/`, `.idea/`)
- Environment files (`.env`)

#### `requirements.txt`
**Purpose**: Lists all Python package dependencies
**Key Dependencies**:
- `pandas>=2.0.0` - Data manipulation
- `sqlalchemy>=1.4.0` - Database ORM
- `streamlit>=1.28.0` - Web dashboard framework
- `plotly>=5.17.0` - Interactive visualizations
- `psycopg2-binary` - PostgreSQL driver (v2)
- `psycopg` - PostgreSQL driver (v3, optional)
- `pytest>=7.4.0` - Testing framework
- `python-dateutil` - Date parsing
- `tqdm` - Progress bars

#### `pytest.ini`
**Purpose**: Pytest configuration file
**Configuration**:
- Registers custom test markers (e.g., `integration`)
- Sets test discovery patterns
- Configures test output format

---

### SQL Schema Files (`sql/`)

#### `sql/oltp_schema.sql`
**Purpose**: Defines the normalized OLTP database schema for SQLite
**Tables Defined**:
1. **customers**
   - Primary Key: `customer_id`
   - Columns: customer_name, segment, city, state, country, postal_code, region
   
2. **products**
   - Primary Key: `product_id`
   - Columns: category, sub_category, product_name
   
3. **orders**
   - Primary Key: `order_id`
   - Foreign Key: `customer_id` → customers
   - Columns: order_date, ship_date, ship_mode, region
   
4. **order_items**
   - Primary Key: `item_id`
   - Foreign Keys: `order_id` → orders, `product_id` → products
   - Columns: quantity, sales, discount, profit, shipping_cost
   
5. **returns**
   - Primary Key: `return_id`
   - Foreign Key: `order_id` → orders
   - Columns: returned_flag, region

**Key Features**:
- Normalized to 3NF (Third Normal Form)
- Foreign key constraints enforce referential integrity
- Indexes on frequently queried columns

#### `sql/oltp_schema_psql.sql`
**Purpose**: PostgreSQL-specific OLTP schema
**Differences from SQLite Schema**:
- Uses PostgreSQL data types (e.g., `BOOLEAN`, `NUMERIC`)
- Returns table uses `BOOLEAN` for returned_flag
- Optimized for PostgreSQL's query planner
- Supports COPY command for bulk loading

#### `sql/dw_schema.sql`
**Purpose**: Defines the star schema for the data warehouse
**Dimension Tables**:

1. **dim_date**
   - Primary Key: `date_key` (YYYYMMDD format)
   - Columns: date, year, quarter, month, day, weekday, is_weekend
   - Purpose: Time dimension for temporal analysis

2. **dim_customer**
   - Primary Key: `customer_key` (surrogate key)
   - Columns: customer_id, customer_name, segment, city, state, country, postal_code
   - Purpose: Customer dimension for customer analysis

3. **dim_product**
   - Primary Key: `product_key` (surrogate key)
   - Columns: product_id, category, sub_category, product_name
   - Purpose: Product dimension for product analysis

4. **dim_region**
   - Primary Key: `region_key` (surrogate key)
   - Columns: region
   - Purpose: Geographic dimension

**Fact Table**:

5. **fact_sales**
   - Primary Key: `fact_id` (surrogate key)
   - Foreign Keys: date_key, customer_key, product_key, region_key
   - Measures: quantity, sales, discount, profit, shipping_cost
   - Grain: One row per order item
   - Purpose: Central fact table for sales analysis

**Design Pattern**: Classic star schema optimized for OLAP queries

#### `sql/views.sql`
**Purpose**: Defines analytical SQL views
**Views**:
- Aggregated sales by category
- Customer lifetime value
- Product performance metrics
- Regional sales summaries

---

### Data Files (`data/`)

#### Raw Data Files

**`Awesome_Inc_Superstore_Orders.csv`**
- **Source**: Original orders dataset
- **Rows**: ~25,000 order records
- **Columns**: Order ID, Order Date, Ship Date, Customer details, Product details, Sales metrics

**`Awesome_Inc_Superstore_Returns.csv`**
- **Source**: Original returns dataset  
- **Rows**: ~1,000 return records
- **Columns**: Returned flag, Order ID, Region

#### Cleaned Data Files

All cleaned files are generated by `scripts/etl_oltp.py` and `scripts/transform.py`:

**`cleaned_customers.csv`**
- Deduplicated customer records
- Normalized names and addresses
- Unique customer_id per customer

**`cleaned_products.csv`**
- Deduplicated product records
- Standardized category names
- Unique product_id per product

**`cleaned_orders.csv`**
- Validated order dates
- Parsed ship modes
- Foreign keys to customers

**`cleaned_order_items.csv`**
- Line-item level details
- Validated numeric fields (sales, profit, discount)
- Foreign keys to orders and products

**`cleaned_returns.csv`**
- Normalized returned_flag (Yes/No)
- Inferred return dates using order date heuristics
- Foreign keys to orders

#### Staging Directory (`data/pg_load/`)

Contains staged CSV files for PostgreSQL import:
- Additional deduplication for PostgreSQL constraints
- Column header normalization
- Boolean value conversion (Yes/No → TRUE/FALSE)
- Files named with `.staged.csv` suffix

#### Archive Directory (`data/archive/`)

Contains intermediate analysis files from the returns date inference process:
- `returns_with_inferred_dates.csv` - Returns with estimated dates
- `returns_date_matches.csv` - Date matching analysis
- Various parsing attempt logs

---

### Python Scripts (`scripts/`)

#### `scripts/__init__.py`
**Purpose**: Makes scripts directory a Python package
**Contents**: Empty file for package recognition

#### `scripts/logger.py`
**Purpose**: Centralized logging configuration
**Functions**:
```python
def get_logger(name: str) -> logging.Logger
```
**Features**:
- Configures logging format with timestamps
- Sets log levels (INFO, DEBUG, ERROR)
- Creates loggers for each module
**Usage**: `logger = get_logger('module_name')`

#### `scripts/db.py`
**Purpose**: Database connection utilities
**Functions**:
```python
def get_engine(db_path: str) -> sqlalchemy.Engine
```
**Features**:
- Creates SQLAlchemy engine from database path
- Supports SQLite and PostgreSQL connection strings
- Respects `DATABASE_URL` environment variable
- Returns reusable connection engine
**Usage**: `engine = get_engine('sqlite:///oltp.db')`

#### `scripts/transform.py`
**Purpose**: Data transformation and cleaning utilities
**Key Functions**:

1. `clean_customer_data(df: pd.DataFrame) -> pd.DataFrame`
   - Deduplicates customers
   - Standardizes address fields
   - Generates unique customer IDs

2. `clean_product_data(df: pd.DataFrame) -> pd.DataFrame`
   - Deduplicates products
   - Normalizes category names
   - Generates unique product IDs

3. `clean_order_data(df: pd.DataFrame) -> pd.DataFrame`
   - Validates date fields
   - Parses ship modes
   - Ensures referential integrity

4. `clean_order_items(df: pd.DataFrame) -> pd.DataFrame`
   - Validates numeric fields
   - Calculates derived metrics
   - Handles missing values

5. `clean_returns_data(df: pd.DataFrame) -> pd.DataFrame`
   - Infers return dates from order dates
   - Normalizes returned flags
   - Matches to orders

**Design Pattern**: Pure functions that take a DataFrame and return a transformed DataFrame

#### `scripts/etl_oltp.py`
**Purpose**: Main ETL pipeline orchestrator
**Command Line Arguments**:
```bash
python scripts/etl_oltp.py \
    --orders data/Awesome_Inc_Superstore_Orders.csv \
    --returns data/Awesome_Inc_Superstore_Returns.csv \
    --out oltp.db
```

**Workflow**:
1. **Extract**: Read raw CSV files
2. **Transform**: 
   - Call transformation functions from `transform.py`
   - Validate data quality
   - Generate cleaned CSVs
3. **Load**:
   - Apply OLTP schema (`sql/oltp_schema.sql`)
   - Insert data into SQLite database
   - Create indexes
4. **Validate**: Check row counts and constraints

**Output Files**:
- `oltp.db` - SQLite OLTP database
- Cleaned CSV files in `data/` directory

#### `scripts/build_dw.py`
**Purpose**: Data warehouse builder
**Command Line Arguments**:
```bash
python scripts/build_dw.py --oltp oltp.db --dw dw.db
```

**Workflow**:
1. **Read OLTP Data**: Query from oltp.db
2. **Build Dimensions**:
   - `dim_date`: Extract unique dates, compute date attributes
   - `dim_customer`: Transform customer records, add surrogate keys
   - `dim_product`: Transform product records, add surrogate keys
   - `dim_region`: Extract unique regions
3. **Build Fact Table**:
   - Join order_items with dimensions
   - Map to dimension keys
   - Aggregate measures
4. **Write DW**: 
   - Apply star schema (`sql/dw_schema.sql`)
   - Load dimensions and facts
   - Create indexes

**Output**: `dw.db` - SQLite data warehouse

**Key Function**:
```python
def create_dim_date(dates: pd.Series) -> pd.DataFrame
```
Creates date dimension with computed attributes (quarter, weekday, weekend flag)

#### `scripts/migrate_to_postgres.py`
**Purpose**: Orchestrates PostgreSQL migration
**Command Line Arguments**:
```bash
python scripts/migrate_to_postgres.py \
    --database-url 'postgresql+psycopg2://user:pass@host:port/db' \
    --truncate
```

**Workflow**:
1. **Prepare Staging**:
   - Create `data/pg_load/` directory
   - Copy cleaned CSVs
   - Perform additional deduplication for customers and orders
   - Normalize returns boolean values (Yes/No → TRUE/FALSE)
   
2. **Apply DDL**:
   - Execute `sql/oltp_schema_psql.sql`
   - Create tables with constraints
   
3. **Truncate** (if --truncate flag):
   - Delete existing data for idempotent runs
   
4. **Load Data**:
   - Call `load_from_csv_psql.py` for each table
   - Pass database URL and file paths
   
5. **Validate**:
   - Query row counts (smoke test)
   - Print summary statistics

**Non-Destructive**: By default, does not truncate; use `--truncate` for idempotent runs

#### `scripts/load_from_csv_psql.py`
**Purpose**: Robust CSV to PostgreSQL loader with multiple fallback strategies
**Strategy Hierarchy**:

1. **Primary: Server-side COPY (psycopg2)**
   ```python
   cursor.copy_expert("COPY table FROM STDIN WITH CSV HEADER", file)
   ```
   - Fastest method (direct server copy)
   - Requires psycopg2 driver
   
2. **Secondary: Server-side COPY (psycopg v3)**
   ```python
   with cursor.copy("COPY table FROM STDIN WITH CSV HEADER") as copy:
       copy.write(data)
   ```
   - Modern psycopg v3 API
   - Attempts if psycopg2 fails
   
3. **Tertiary: Client-side psql \copy**
   ```bash
   psql -c "\copy table FROM 'file.csv' CSV HEADER"
   ```
   - Uses psql command-line tool
   - Works when drivers fail
   
4. **Final Fallback: pandas to_sql**
   ```python
   df.to_sql('table', engine, if_exists='append', chunksize=1000)
   ```
   - Progressive chunksize reduction on parameter limit errors
   - Always succeeds but slowest

**Key Features**:
- **Staging**: Creates normalized `.staged.csv` files with matching column headers
- **Validation**: Counts rows before and after COPY to detect silent failures
- **Error Handling**: Catches driver-specific exceptions and tries next method
- **Logging**: Detailed logs of which method succeeded

**Function Signature**:
```python
def load_csv_to_postgres(
    engine: sqlalchemy.Engine,
    table_name: str,
    csv_path: Path
) -> None
```

#### `scripts/create_views.py`
**Purpose**: Creates analytical SQL views
**Workflow**:
- Reads `sql/views.sql`
- Executes view definitions on target database
- Used for creating pre-computed aggregations

#### `scripts/cdc_extractor.py`
**Purpose**: Change Data Capture (CDC) utility
**Function**: Extracts incremental changes from OLTP for DW updates
**Not actively used**: Future enhancement for real-time sync

---

### Test Suite (`tests/`)

#### `tests/test_pipeline.py`
**Purpose**: Unit tests for ETL pipeline
**Test Cases**:

1. `test_transform_customers()`
   - Tests customer deduplication
   - Validates generated customer IDs
   - Checks data types

2. `test_transform_products()`
   - Tests product normalization
   - Validates category standardization

3. `test_transform_orders()`
   - Tests date parsing
   - Validates foreign key relationships

4. `test_clean_returns()`
   - Tests returns data cleaning
   - Validates date inference logic

**Run Command**: `pytest tests/test_pipeline.py -v`

#### `tests/test_integration_postgres.py`
**Purpose**: PostgreSQL integration tests
**Test Marker**: `@pytest.mark.integration`

**Test Case**: `test_postgres_migration_parity()`
**What it Tests**:
1. Runs migration with psycopg2 dialect
2. Runs migration with psycopg v3 dialect
3. Compares row counts from both runs
4. Asserts they match (driver parity)

**Smoke Test Validation**:
- customers: 17,415 records
- products: 3,788 records
- orders: 25,728 records
- order_items: 51,290 records
- returns: 1,079 records

**Skip Condition**: Skips if migration fails (e.g., no DB connection)

**Run Command**: `pytest tests/test_integration_postgres.py -v`

---

### Web Application (`web/`)

#### `web/streamlit_app.py`
**Purpose**: Interactive analytics dashboard
**Framework**: Streamlit

**Architecture**:
```python
# Caching Layer
@st.cache_data
def load_data():
    # Query dw.db and cache results
    pass

# UI Layer
st.sidebar  # Filters
st.metric   # KPIs
st.plotly_chart  # Visualizations
```

**Data Loading Functions**:

1. `load_categories()` → List of product categories
2. `load_regions()` → List of geographic regions
3. `load_date_bounds()` → Min/max dates in dataset
4. `load_monthly_sales_filtered(...)` → Monthly sales time series
5. `load_kpis(...)` → Total sales, orders, avg order value
6. `load_top_products(...)` → Top N products by sales
7. `load_product_time_series(...)` → Product-level time series
8. `load_sales_by_category(...)` → Sales by category
9. `load_order_value_distribution(...)` → Order value histogram data
10. `load_top_customers(...)` → Top customers by sales
11. `load_returns_df()` → Returns data from CSV
12. `load_returns_rate_by_category(...)` → Return rate analysis
13. `load_sales_by_location(...)` → Geographic sales data

**Visualizations**:

1. **KPI Cards**
   - Total Sales ($)
   - Total Orders (count)
   - Average Order Value ($)
   - Displayed in 3-column layout with `st.metric`

2. **Monthly Sales Chart**
   - Line chart showing sales trend over time
   - Filterable by category, region, date range
   - CSV export button
   - Uses Plotly Express

3. **Top Products Bar Chart**
   - Top N products (configurable via slider)
   - Horizontal bar chart
   - Click to drill down

4. **Product Drilldown**
   - Time series for selected product
   - Shows monthly sales trend
   - Dropdown selection

5. **Category Treemap**
   - Hierarchical visualization of sales by category
   - Bubble size proportional to sales
   - Plotly treemap

6. **Order Value Distribution**
   - Histogram of order values
   - Adjustable bin count (slider)
   - Log scale toggle for skewed distributions

7. **Returns Analysis**
   - Bar chart: return rate by category
   - Sample table of returned orders
   - Data from `cleaned_returns.csv`

8. **Top Customers Bar Chart**
   - Top K customers (configurable via slider)
   - Total sales per customer

9. **Geographic Sales Map** (NEW)
   - Interactive world map using `scatter_geo`
   - Bubble size = sales volume
   - Color gradient = sales intensity
   - Hover: city, state, country, sales, orders
   - Natural Earth projection
   - Top 10 cities table below map

**Sidebar Filters**:
- Category dropdown (All, or specific category)
- Region dropdown (All, or specific region)
- Date range picker
- Top N slider (products)
- Top K slider (customers)
- Histogram bins slider
- Log scale checkbox

**Caching Strategy**:
- All data loading functions use `@st.cache_data`
- Cache invalidates when function parameters change
- Improves performance by avoiding redundant queries

**Error Handling**:
- Checks if `dw.db` exists before rendering
- Displays user-friendly error message if database missing
- Early `st.stop()` to prevent crashes

**Run Command**: 
```bash
streamlit run web/streamlit_app.py --server.port 8501
```

---

### CI/CD Configuration

#### `.github/workflows/ci.yml`
**Purpose**: GitHub Actions CI/CD pipeline
**Triggers**:
- Push to `main` branch
- Pull requests to `main`

**Jobs**:

**Job 1: test**
```yaml
runs-on: ubuntu-latest
steps:
  - Checkout code
  - Set up Python 3.9
  - Install dependencies
  - Run pytest
```

**Services**:
- PostgreSQL 13 container for integration tests
- Exposed on port 5432
- Credentials: postgres/postgres

**Environment Variables**:
- `DATABASE_URL`: Set to PostgreSQL service URL

**Test Execution**:
```bash
pytest -v --tb=short
```

**Status Badge**: Can be added to README.md

---

### Documentation Files

#### `README.md`
**Purpose**: Project README with setup instructions
**Sections**:
- Project overview
- Features list
- Installation instructions
- Usage examples
- Testing guide
- PostgreSQL migration guide
- Contributing guidelines

#### `REPORT.md`
**Purpose**: Implementation summary report
**Sections**:
- Components implemented
- Files changed
- Local validation results
- How to run commands
- Screenshot checklist for deliverable
- Next steps

#### `DOCUMENTATION.md` (This File)
**Purpose**: Complete technical documentation
**Sections**:
- Architecture diagrams
- File-by-file documentation
- Data flow explanations
- Setup guides

#### `proposal.md`
**Purpose**: Initial project proposal
**Contents**:
- Problem statement
- Proposed solution
- Technical approach
- Deliverables

---

## Data Flow Diagram

### Complete System Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                           DATA SOURCES                               │
│                                                                       │
│  ┌─────────────────────────┐  ┌──────────────────────────┐          │
│  │ Superstore_Orders.csv   │  │ Superstore_Returns.csv   │          │
│  │ (~25K rows)             │  │ (~1K rows)               │          │
│  └────────────┬────────────┘  └────────────┬─────────────┘          │
└───────────────┼────────────────────────────┼────────────────────────┘
                │                            │
                └────────────┬───────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     ETL PIPELINE (scripts/etl_oltp.py)               │
│                                                                       │
│  1. EXTRACT                                                           │
│     ├─ Read CSV files                                                │
│     └─ Parse with pandas                                             │
│                                                                       │
│  2. TRANSFORM (scripts/transform.py)                                 │
│     ├─ Clean customer data (dedupe, normalize)                       │
│     ├─ Clean product data (dedupe, standardize)                      │
│     ├─ Clean order data (validate dates)                             │
│     ├─ Clean order items (validate numerics)                         │
│     └─ Clean returns (infer dates, normalize flags)                  │
│                                                                       │
│  3. VALIDATE                                                          │
│     ├─ Check referential integrity                                   │
│     ├─ Validate data types                                           │
│     └─ Ensure completeness                                           │
│                                                                       │
│  4. LOAD                                                              │
│     ├─ Write cleaned CSVs to data/                                   │
│     ├─ Apply OLTP schema (sql/oltp_schema.sql)                       │
│     └─ Insert into SQLite (oltp.db)                                  │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     ├───────────────────┐
                     │                   │
                     ▼                   ▼
┌─────────────────────────────┐  ┌────────────────────────────────────┐
│   CLEANED CSV SNAPSHOTS      │  │      OLTP DATABASE (SQLite)        │
│                              │  │                                    │
│  data/                       │  │  oltp.db                           │
│  ├─ cleaned_customers.csv    │  │  ├─ customers (17K rows)          │
│  ├─ cleaned_products.csv     │  │  ├─ products (3.8K rows)          │
│  ├─ cleaned_orders.csv       │  │  ├─ orders (25K rows)             │
│  ├─ cleaned_order_items.csv  │  │  ├─ order_items (51K rows)        │
│  └─ cleaned_returns.csv      │  │  └─ returns (1K rows)             │
└─────────────┬───────────────┘  └──────────────┬─────────────────────┘
              │                                  │
              │                                  │
              │  PostgreSQL Migration Path       │  DW Build Path
              │                                  │
              ▼                                  ▼
┌──────────────────────────────┐  ┌───────────────────────────────────┐
│  POSTGRES MIGRATION           │  │   DW BUILDER                       │
│  (migrate_to_postgres.py)    │  │   (build_dw.py)                    │
│                               │  │                                    │
│  1. Prepare Staging           │  │   1. Read OLTP Data                │
│     └─ data/pg_load/          │  │      └─ Query oltp.db              │
│        ├─ Dedupe customers    │  │                                    │
│        ├─ Dedupe orders       │  │   2. Create Date Dimension         │
│        └─ Normalize returns   │  │      ├─ Extract unique dates       │
│                               │  │      └─ Compute attributes         │
│  2. Apply PostgreSQL DDL      │  │                                    │
│     └─ oltp_schema_psql.sql   │  │   3. Create Customer Dimension     │
│                               │  │      ├─ Add surrogate keys         │
│  3. Load with Fallbacks       │  │      └─ Preserve attributes        │
│     (load_from_csv_psql.py)   │  │                                    │
│     ├─ Try: Server COPY       │  │   4. Create Product Dimension      │
│     ├─ Try: psycopg v3 COPY   │  │      ├─ Add surrogate keys         │
│     ├─ Try: psql \copy        │  │      └─ Preserve hierarchy         │
│     └─ Fallback: pandas       │  │                                    │
│                               │  │   5. Create Region Dimension       │
│  4. Validate Row Counts       │  │      └─ Extract unique regions     │
└──────────────┬────────────────┘  │                                    │
               │                   │   6. Build Fact Table              │
               ▼                   │      ├─ Join with dimensions       │
┌──────────────────────────────┐  │      ├─ Map to surrogate keys      │
│   POSTGRES DATABASE           │  │      └─ Aggregate measures         │
│                               │  │                                    │
│   Tables:                     │  │   7. Write Star Schema             │
│   ├─ customers                │  │      └─ Apply dw_schema.sql        │
│   ├─ products                 │  └──────────────┬─────────────────────┘
│   ├─ orders                   │                 │
│   ├─ order_items              │                 ▼
│   └─ returns                  │  ┌────────────────────────────────────┐
└───────────────────────────────┘  │   DATA WAREHOUSE (SQLite)          │
                                   │                                    │
                                   │   dw.db (Star Schema)              │
                                   │                                    │
                                   │   Dimensions:                      │
                                   │   ├─ dim_date (1.5K rows)          │
                                   │   ├─ dim_customer (17K rows)       │
                                   │   ├─ dim_product (3.8K rows)       │
                                   │   └─ dim_region (24 rows)          │
                                   │                                    │
                                   │   Fact:                            │
                                   │   └─ fact_sales (51K rows)         │
                                   └─────────────┬──────────────────────┘
                                                 │
                                                 │
                                                 ▼
                                   ┌─────────────────────────────────────┐
                                   │  STREAMLIT DASHBOARD                │
                                   │  (streamlit_app.py)                 │
                                   │                                     │
                                   │  Queries:                           │
                                   │  ├─ Load dimensions for filters     │
                                   │  ├─ Compute KPIs (aggregates)       │
                                   │  ├─ Generate time series            │
                                   │  ├─ Top products/customers          │
                                   │  └─ Geographic distribution         │
                                   │                                     │
                                   │  Visualizations:                    │
                                   │  ├─ KPI cards                       │
                                   │  ├─ Line charts (time series)       │
                                   │  ├─ Bar charts (rankings)           │
                                   │  ├─ Treemap (hierarchy)             │
                                   │  ├─ Histogram (distribution)        │
                                   │  └─ Geo map (locations)             │
                                   │                                     │
                                   │  Features:                          │
                                   │  ├─ Interactive filters             │
                                   │  ├─ CSV export                      │
                                   │  └─ Responsive caching              │
                                   └──────────────┬──────────────────────┘
                                                  │
                                                  ▼
                                   ┌──────────────────────────────────────┐
                                   │          WEB BROWSER                 │
                                   │      (localhost:8501)                │
                                   │                                      │
                                   │  User Interactions:                  │
                                   │  ├─ Apply filters                    │
                                   │  ├─ Select date ranges               │
                                   │  ├─ Download CSV exports             │
                                   │  └─ Drill down into details          │
                                   └──────────────────────────────────────┘
```

### Decision Flow: PostgreSQL Load Strategy

```
Start: Load CSV to PostgreSQL
        │
        ▼
    ┌───────────────────────┐
    │  Stage CSV File        │
    │  (Normalize headers)   │
    └───────┬───────────────┘
            │
            ▼
    ┌───────────────────────┐
    │  Count Existing Rows   │
    │  before_count = n      │
    └───────┬───────────────┘
            │
            ▼
    ┌───────────────────────┐
    │  Try: psycopg2 COPY   │
    │  cursor.copy_expert()  │
    └───────┬───────────────┘
            │
            ├─ Success? ──────┐
            │                 │
            No                Yes
            │                 │
            ▼                 ▼
    ┌───────────────────┐  ┌──────────────────┐
    │ Try: psycopg COPY │  │ Validate Rows    │
    │ cursor.copy()     │  │ after_count > n? │
    └───────┬───────────┘  └────┬────────┬────┘
            │                   │        │
            ├─ Success? ────────┘       No (Silent Failure)
            │                            │
            No                           │
            │                            │
            ▼                            │
    ┌────────────────────┐              │
    │ Try: psql \copy    │              │
    │ Run CLI command    │              │
    └────────┬───────────┘              │
             │                           │
             ├─ Success? ────────────────┘
             │                           
             No                          
             │                           
             ▼                           
    ┌────────────────────┐              
    │ Fallback: pandas   │              
    │ df.to_sql()        │              
    │                    │              
    │ Retry with:        │              
    │ chunksize=10000    │              
    │ chunksize=1000     │              
    │ chunksize=100      │              
    └────────┬───────────┘              
             │                           
             ▼                           
        ┌─────────┐                     
        │ SUCCESS │                     
        └─────────┘                     
```

---

## Setup and Execution Guide

### Prerequisites
```bash
# Python 3.9+
python --version

# PostgreSQL (optional, for migration)
psql --version
```

### Installation

1. **Clone Repository**
```bash
git clone https://github.com/theomthakur/ecommerce-dbms.git
cd ecommerce-dbms
```

2. **Create Virtual Environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### Execution Workflows

#### Workflow 1: Complete ETL to SQLite

```bash
# Step 1: Run ETL pipeline
python scripts/etl_oltp.py \
    --orders data/Awesome_Inc_Superstore_Orders.csv \
    --returns data/Awesome_Inc_Superstore_Returns.csv \
    --out oltp.db

# Output:
# - oltp.db (OLTP database)
# - data/cleaned_*.csv (cleaned snapshots)

# Step 2: Build data warehouse
python scripts/build_dw.py --oltp oltp.db --dw dw.db

# Output:
# - dw.db (star schema data warehouse)

# Step 3: Launch dashboard
streamlit run web/streamlit_app.py --server.port 8501

# Open browser: http://localhost:8501
```

#### Workflow 2: PostgreSQL Migration

```bash
# Prerequisites: PostgreSQL server running
# Create database: createdb ecommerce

# Step 1: Run cleaned snapshots (if not already done)
python scripts/etl_oltp.py \
    --orders data/Awesome_Inc_Superstore_Orders.csv \
    --returns data/Awesome_Inc_Superstore_Returns.csv

# Step 2: Migrate to PostgreSQL
python scripts/migrate_to_postgres.py \
    --database-url 'postgresql+psycopg2://user:pass@localhost:5432/ecommerce' \
    --truncate

# Output:
# - Data loaded into PostgreSQL
# - Smoke test row counts printed
```

#### Workflow 3: Run Tests

```bash
# Unit tests only
pytest tests/test_pipeline.py -v

# Integration tests (requires PostgreSQL)
pytest tests/test_integration_postgres.py -v

# All tests
pytest -v

# With coverage
pytest --cov=scripts --cov-report=html
```

### Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'scripts'`
**Solution**: Ensure you're in the project root directory

**Issue**: `DatabaseError: no such table: customers`
**Solution**: Run ETL pipeline first to create oltp.db

**Issue**: `FileNotFoundError: dw.db not found`
**Solution**: Run `build_dw.py` to create the data warehouse

**Issue**: PostgreSQL COPY fails
**Solution**: The loader has automatic fallbacks; check logs for which method succeeded

**Issue**: Streamlit shows "No data available"
**Solution**: Check filters; try selecting "All" for category and region

---

## Performance Optimization Tips

1. **ETL Pipeline**
   - Use `low_memory=False` in pandas for large CSVs
   - Process in chunks for very large datasets
   - Enable progress bars with `tqdm`

2. **PostgreSQL Loading**
   - Prefer server COPY over pandas insert (100x faster)
   - Disable indexes during bulk load, rebuild after
   - Use `--truncate` flag for idempotent runs

3. **Data Warehouse Queries**
   - Create indexes on frequently filtered columns
   - Pre-aggregate common queries into views
   - Use EXPLAIN to analyze slow queries

4. **Streamlit Dashboard**
   - All data loading functions use `@st.cache_data`
   - Cache invalidates only when parameters change
   - For large datasets, add pagination or lazy loading

---

## Future Enhancements

1. **Incremental ETL**
   - Implement CDC using `cdc_extractor.py`
   - Process only changed records

2. **Real-time Dashboard**
   - WebSocket connection to database
   - Auto-refresh on data updates

3. **Advanced Analytics**
   - ML models for sales forecasting
   - Customer segmentation clustering
   - Anomaly detection

4. **Data Lineage**
   - Track transformations end-to-end
   - Implement data catalog

5. **Multi-Database Support**
   - Add MySQL support
   - Support for cloud data warehouses (Snowflake, BigQuery)

---

## Glossary

**ETL**: Extract, Transform, Load - data pipeline pattern
**OLTP**: Online Transaction Processing - transactional database
**OLAP**: Online Analytical Processing - analytical queries
**DW**: Data Warehouse - centralized repository for analysis
**Star Schema**: Dimensional modeling with fact and dimension tables
**Surrogate Key**: System-generated primary key (not from source data)
**Dimension Table**: Describes business entities (who, what, where, when)
**Fact Table**: Measures business processes (how much, how many)
**CDC**: Change Data Capture - identifying changed records
**Idempotent**: Operation that produces same result when run multiple times

---

## Contact & Support

For questions or issues:
- Review this documentation
- Check README.md for quick start guide
- Review REPORT.md for implementation details
- Run tests to verify setup

---

*Last Updated: December 6, 2025*
*Version: 1.0*
