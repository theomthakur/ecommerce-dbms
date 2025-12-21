# Modern Analytics Stack Implementation Guide

**Status:** Production-Ready Data Engineering Infrastructure  
**Last Updated:** December 2025

## Overview

This guide covers the implementation of a modern data analytics stack for the e-commerce project:

- **Apache Airflow**: DAG-based workflow orchestration
- **dbt**: SQL-first data transformations
- **Great Expectations**: Data quality validation
- **Warehouse**: BigQuery, Redshift, or PostgreSQL support

## Project Structure

```
├── airflow/
│   ├── dags/
│   │   ├── ecommerce_etl_dag.py          # Main ETL orchestration
│   │   ├── ecommerce_dbt_transformations.py  # dbt execution
│   │   └── ecommerce_data_quality.py     # Great Expectations validation
│   ├── plugins/                          # Custom operators
│   └── __init__.py
│
├── dbt/
│   ├── models/
│   │   ├── staging/                      # 1:1 source mappings
│   │   │   ├── stg_customers.sql
│   │   │   ├── stg_orders.sql
│   │   │   ├── stg_order_items.sql
│   │   │   ├── stg_products.sql
│   │   │   └── stg_returns.sql
│   │   ├── marts/
│   │   │   ├── core/                     # Core business models
│   │   │   │   ├── fact_customer_analytics.sql
│   │   │   │   └── fact_order_analytics.sql
│   │   │   ├── finance/                  # Finance-specific models
│   │   │   │   └── fct_revenue_analysis.sql
│   │   │   └── marketing/                # Marketing-specific models
│   │   │       └── fct_product_performance.sql
│   │   ├── sources.yml                   # Source definitions & tests
│   │   └── model_tests.yml               # Model validation
│   ├── macros/                           # Custom macros
│   ├── dbt_project.yml                   # Project configuration
│   └── profiles.yml                      # Connection profiles
│
├── great_expectations/
│   ├── suites/                           # Validation suites
│   │   ├── orders_quality/
│   │   ├── customers_quality/
│   │   ├── order_items_quality/
│   │   ├── products_quality/
│   │   └── returns_quality/
│   └── great_expectations.yml            # GE configuration
│
├── warehouse_config/
│   ├── warehouse_loader.py               # BigQuery/Redshift loaders
│   ├── config_templates.py               # Connection configs
│   └── .env.template                     # Environment variables
│
└── great_expectations_config.py          # GE runner & suites
```

---

## 1. Setup & Installation

### 1.1 Install Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# Or install individually for specific components
pip install 'apache-airflow>=2.5.0'
pip install 'dbt-core>=1.5.0' 'dbt-postgres>=1.5.0'
pip install 'great-expectations>=0.17.0'
```

### 1.2 Environment Configuration

Copy the template and fill in your credentials:

```bash
cp warehouse_config/.env.template .env
# Edit .env with your warehouse credentials
source .env
```

### 1.3 Initialize Airflow

```bash
# Set Airflow home
export AIRFLOW_HOME=./airflow

# Initialize Airflow database
airflow db init

# Create Airflow user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@company.com

# Set Airflow variables for database paths
airflow variables set orders_csv_path /path/to/Awesome_Inc_Superstore_Orders.csv
airflow variables set returns_csv_path /path/to/Awesome_Inc_Superstore_Returns.csv
airflow variables set warehouse_type postgres  # or bigquery, redshift
```

---

## 2. Apache Airflow DAGs

### 2.1 Main ETL Pipeline (`ecommerce_etl_dag.py`)

**Schedule**: Daily at midnight  
**Purpose**: Orchestrate end-to-end ETL pipeline

```
extract_validate 
    ↓
    oltp_layer (build_oltp → validate_oltp)
    ↓
    build_data_warehouse
    ↓
    trigger_dbt_transformations
    ↓
    trigger_data_quality_checks
    ↓
    load_to_warehouse
```

**Tasks:**
- `extract_and_validate`: Load and validate raw CSV files
- `build_oltp_db`: Create normalized OLTP database
- `validate_oltp`: Run integration tests
- `build_data_warehouse`: Create star schema
- `trigger_dbt_transformations`: Execute dbt models
- `trigger_data_quality_checks`: Run Great Expectations suites
- `load_to_warehouse`: Push to BigQuery/Redshift

### 2.2 dbt Transformations DAG (`ecommerce_dbt_transformations.py`)

**Triggered by**: Main ETL DAG  
**Purpose**: Execute dbt models and tests

```
dbt_parse
    ↓
    dbt_staging_models
    ↓
    dbt_mart_models
    ↓
    dbt_tests
    ↓
    dbt_docs_generate
```

### 2.3 Data Quality DAG (`ecommerce_data_quality.py`)

**Triggered by**: Main ETL DAG  
**Purpose**: Validate data quality across all tables

```
validate_orders
    ├→ validate_customers
    ├→ validate_products
    ├→ validate_order_items
    └→ validate_returns
    
    ↓ (all complete)
    
generate_quality_report
```

### 2.4 Running DAGs

```bash
# Start Airflow webserver
airflow webserver --port 8080

# Start scheduler in another terminal
airflow scheduler

# Trigger DAG manually
airflow dags trigger ecommerce_etl_pipeline

# View logs
airflow tasks logs ecommerce_etl_pipeline extract_and_validate
```

Access UI at: http://localhost:8080

---

## 3. dbt Data Transformations

### 3.1 Project Structure

**Staging Layer** (`staging/`): 1:1 source mappings
- `stg_customers.sql`: Customer dimension
- `stg_orders.sql`: Order header dimension
- `stg_products.sql`: Product dimension
- `stg_order_items.sql`: Order line items
- `stg_returns.sql`: Product returns

**Marts Layer** (`marts/`): Business logic & aggregations

**Core Models:**
- `fact_customer_analytics.sql`: Customer lifetime value, tier classification
- `fact_order_analytics.sql`: Order metrics with return indicators

**Finance Models:**
- `fct_revenue_analysis.sql`: Monthly revenue by region/market

**Marketing Models:**
- `fct_product_performance.sql`: Product performance metrics

### 3.2 Configuration

**dbt_project.yml** settings:
```yaml
profile: 'ecommerce'
target: postgres  # or bigquery, redshift

models:
  staging:
    +materialized: view
    +schema: staging
  marts:
    +materialized: table
    +schema: marts
```

### 3.3 Running dbt

```bash
cd dbt

# Set target warehouse
export DBT_TARGET=postgres  # or bigquery, redshift

# Parse project (validate)
dbt parse --profiles-dir profiles

# Run all models
dbt run

# Run specific models
dbt run --select staging.*
dbt run --select marts.*

# Run tests
dbt test

# Generate documentation
dbt docs generate
dbt docs serve  # http://localhost:8000

# Full pipeline
dbt build  # parse → run → test
```

### 3.4 Available Variables

```yaml
vars:
  start_date: '2020-01-01'
  end_date: '2024-12-31'
  currency: 'USD'
```

Use in models:
```sql
where order_date >= '{{ var("start_date") }}'
```

---

## 4. Great Expectations Data Quality

### 4.1 Validation Suites

Predefined suites for each table:

| Suite | Table | Validations |
|-------|-------|-------------|
| `orders_quality` | orders | Row count, PK, FK, date format |
| `customers_quality` | customers | Row count, PK, valid segments |
| `products_quality` | products | Row count, PK, category values |
| `order_items_quality` | order_items | Row count, FK constraints, qty range |
| `returns_quality` | returns | Row count, PK, FK constraints |

### 4.2 Creating Custom Expectations

```python
from great_expectations_config import ge_runner

# Expectations are auto-created by functions in great_expectations_config.py
ge_runner.create_orders_quality_suite()
ge_runner.create_customers_quality_suite()
```

### 4.3 Running Validations

```python
from great_expectations_config import ge_runner

# Run single suite
results = ge_runner.run_validation_suite(
    suite_name='orders_quality',
    data_source='ecommerce_dw',
    table_name='orders',
    warehouse_type='postgres'
)

# Generate quality report
ge_runner.generate_quality_report(
    dw_db='./dw.db',
    output_path='./reports/data_quality_report.html'
)
```

### 4.4 Configuration

**great_expectations.yml** contains:
- **Datasources**: PostgreSQL, BigQuery, Redshift connectors
- **Stores**: Expectations, validations, evaluation parameters
- **Data Docs**: HTML documentation site

Update connection strings for your environment:
```yaml
datasources:
  ecommerce_datasource:
    data_connectors:
      postgres_connector:
        connection_string: "postgresql://user:password@host:5432/db"
```

---

## 5. Warehouse Integration

### 5.1 PostgreSQL (Default)

Used in development and testing.

**Setup:**
```bash
# Create database
createdb ecommerce_dw

# Run migrations
psql ecommerce_dw < sql/dw_schema.sql
```

**Connection:**
```env
DBT_HOST=localhost
DBT_USER=postgres
DBT_PASSWORD=postgres
DBT_PORT=5432
DBT_DBNAME=ecommerce_dw
```

### 5.2 Google BigQuery

Production cloud warehouse.

**Setup:**
```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Authenticate
gcloud auth application-default login

# Create BigQuery dataset
bq mk \
    --dataset \
    --location=US \
    --description="E-commerce Data Warehouse" \
    ecommerce_dw
```

**Configuration:**
```env
GCP_PROJECT_ID=your-project-id
BIGQUERY_DATASET=ecommerce_dw
GCP_CREDENTIALS_PATH=/path/to/service-account-key.json
```

**dbt Profile:**
```yaml
bigquery:
  type: bigquery
  project: "{{ env_var('GCP_PROJECT_ID') }}"
  dataset: "{{ env_var('BIGQUERY_DATASET') }}"
  keyfile: "{{ env_var('GCP_CREDENTIALS_PATH') }}"
```

### 5.3 Amazon Redshift

Production cloud warehouse alternative.

**Setup:**
```bash
# Create cluster via AWS Console
# or use AWS CLI

aws redshift create-cluster \
    --cluster-identifier ecommerce-dw \
    --node-type dc2.large \
    --number-of-nodes 2 \
    --master-username admin \
    --master-user-password "YourPassword123!"
```

**Configuration:**
```env
REDSHIFT_HOST=cluster.region.redshift.amazonaws.com
REDSHIFT_USER=admin
REDSHIFT_PASSWORD=your_password
REDSHIFT_PORT=5439
REDSHIFT_DBNAME=ecommerce_dw
REDSHIFT_SCHEMA=public
```

**dbt Profile:**
```yaml
redshift:
  type: redshift
  host: "{{ env_var('REDSHIFT_HOST') }}"
  user: "{{ env_var('REDSHIFT_USER') }}"
  password: "{{ env_var('REDSHIFT_PASSWORD') }}"
  port: "{{ env_var('REDSHIFT_PORT') }}"
  dbname: "{{ env_var('REDSHIFT_DBNAME') }}"
```

### 5.4 Loading Data

**From Python:**
```python
from warehouse_config import warehouse_loader

# Load to BigQuery
warehouse_loader.load_dw_to_warehouse(
    dw_db='./dw.db',
    warehouse_type='bigquery',
    project_id='my-project',
    dataset_id='ecommerce_dw'
)

# Load to Redshift
warehouse_loader.load_dw_to_warehouse(
    dw_db='./dw.db',
    warehouse_type='redshift',
    host='cluster.region.redshift.amazonaws.com',
    user='admin',
    password='password',
    database='ecommerce_dw'
)
```

---

## 6. Complete End-to-End Workflow

### Step 1: Prepare Environment
```bash
# Install packages
pip install -r requirements.txt

# Copy and configure environment
cp warehouse_config/.env.template .env
# Edit .env with your credentials
source .env
```

### Step 2: Initialize Airflow
```bash
export AIRFLOW_HOME=./airflow
airflow db init
airflow users create --username admin --role Admin --email admin@company.com
airflow variables set warehouse_type postgres
```

### Step 3: Configure dbt
```bash
cd dbt
# Update profiles.yml with your connection details
dbt debug  # Test connection
dbt parse  # Validate project
```

### Step 4: Start Airflow
```bash
# Terminal 1: Webserver
airflow webserver --port 8080

# Terminal 2: Scheduler
airflow scheduler

# Access http://localhost:8080
```

### Step 5: Trigger Pipeline
```bash
# Via CLI
airflow dags trigger ecommerce_etl_pipeline

# Via UI: http://localhost:8080/dags/ecommerce_etl_pipeline
```

### Step 6: Monitor & Validate
```bash
# View logs
airflow tasks logs ecommerce_etl_pipeline extract_and_validate

# Check data
dbt test
dbt docs serve  # http://localhost:8000

# Validate quality
python -c "from great_expectations_config import ge_runner; \
  ge_runner.generate_quality_report('./dw.db', './reports/quality_report.html')"
```

---

## 7. Performance Optimization

### dbt Best Practices

```sql
-- Use refs for dependencies
select * from {{ ref('stg_customers') }}

-- Use sources for external tables
select * from {{ source('ecommerce', 'raw_orders') }}

-- Implement incremental models for large datasets
{{ config(
    materialized='incremental',
    unique_key='order_id',
    on_schema_change='fail'
) }}

-- Use dbt tests for quality gates
select * from {{ ref('fact_orders') }}
where order_id is null  -- This fails the test
```

### Airflow Optimization

```python
# Use TaskGroups for organization
with TaskGroup('data_quality', dag=dag) as dq:
    task1 >> task2 >> task3

# Set resource limits
extract_validate = PythonOperator(
    task_id='extract',
    python_callable=extract_func,
    pool='default_pool',  # Limit concurrent tasks
    queue='default',      # Route to specific workers
)

# Use branching for conditional execution
branching = BranchPythonOperator(
    task_id='branch',
    python_callable=decide_path,
)
```

### Great Expectations Optimization

```python
# Batch expectations for performance
validator.expect_column_values_to_not_be_null('id')
validator.expect_column_values_to_be_unique('id')
validator.save_expectation_suite(discard_failed_expectations=False)

# Use sampling for large tables
batch_request = RuntimeBatchRequest(
    datasource_name='ecommerce',
    data_connector_name='sql_connector',
    data_asset_name='orders',
    sampling_method='limit',
    sampling_kwargs={'n_rows': 10000}
)
```

---

## 8. Monitoring & Alerting

### Airflow Monitoring
```python
default_args = {
    'email': ['data-team@company.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}
```

### dbt Artifacts
```bash
# Generated automatically
dbt run generates:
- target/manifest.json (lineage)
- target/graph.gpickle   (DAG)
- target/run_results.json (execution results)
```

### Great Expectations Reports
```bash
# Generated HTML reports
reports/data_quality_report.html
great_expectations/data_docs/site/index.html
```

---

## 9. Troubleshooting

### Common Issues

**Airflow DAGs not showing:**
```bash
# Check DAGs folder
ls $AIRFLOW_HOME/dags/

# Verify imports
python -m py_compile airflow/dags/ecommerce_etl_dag.py

# Clear cache
rm -rf ~/airflow/logs/*
airflow dags list
```

**dbt connection failing:**
```bash
# Debug connection
dbt debug --profiles-dir dbt/

# Check environment variables
echo $DBT_HOST $DBT_USER $DBT_DBNAME

# Test manually
psql -h $DBT_HOST -U $DBT_USER -d $DBT_DBNAME
```

**Great Expectations validation errors:**
```bash
# Inspect expectations
cat great_expectations/suites/orders_quality.json

# Run validation with verbose logging
python -c "import logging; logging.basicConfig(level=logging.DEBUG); \
  from great_expectations_config import ge_runner; \
  ge_runner.run_validation_suite('orders_quality', ...)"
```

---

## 10. Production Deployment Checklist

- [ ] All environment variables configured in `.env`
- [ ] Database connections tested (`dbt debug`)
- [ ] Airflow users created and roles assigned
- [ ] DAG scheduling configured
- [ ] Email alerts enabled
- [ ] dbt tests passing (`dbt test`)
- [ ] Great Expectations suites created and passing
- [ ] Warehouse dataset/schema created
- [ ] Cloud credentials/permissions verified
- [ ] Monitoring dashboards set up
- [ ] Documentation generated (`dbt docs serve`)
- [ ] Backup strategy implemented

---

## 11. Additional Resources

- **Airflow Docs**: https://airflow.apache.org/docs/
- **dbt Docs**: https://docs.getdbt.com/
- **Great Expectations Docs**: https://docs.greatexpectations.io/
- **BigQuery Docs**: https://cloud.google.com/bigquery/docs
- **Redshift Docs**: https://docs.aws.amazon.com/redshift/

---

**Questions?** Refer to individual component documentation or check logs in `reports/` and `airflow/logs/`.
