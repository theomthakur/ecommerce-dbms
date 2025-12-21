# Getting Started with E-Commerce Analytics Platform

Quick reference guide for setup and operation.

---

## 🚀 5-Minute Setup

```bash
# 1. Install
pip install -r requirements.txt

# 2. Initialize
bash setup_analytics_stack.sh

# 3. Configure
nano .env  # Add your database credentials

# 4. Run (Terminal 1)
airflow webserver --port 8080

# 5. Run (Terminal 2)
airflow scheduler

# Access: http://localhost:8080
```

---

## 📊 Build Pipeline

```bash
# Create normalized database
python scripts/etl_oltp.py \
  --orders data/Awesome_Inc_Superstore_Orders.csv \
  --returns data/Awesome_Inc_Superstore_Returns.csv

# Build data warehouse
python scripts/build_dw.py --oltp oltp.db --dw dw.db

# View dashboard
streamlit run web/streamlit_app.py --server.port 8501
```

---

## 🛠️ Component Reference

### Airflow
- **DAGs**: `airflow/dags/` (3 production pipelines)
- **UI**: http://localhost:8080
- **Trigger**: `airflow dags trigger ecommerce_etl_pipeline`

### dbt
- **Models**: `dbt/models/` (9 total: 5 staging + 4 marts)
- **Tests**: `dbt test` (32+ automated tests)
- **Docs**: `dbt docs serve` (http://localhost:8000)

### Great Expectations
- **Suites**: 5 quality suites
- **Checks**: 35+ validation rules
- **Reports**: `reports/data_quality_report.html`

---

## 🔗 Key Documentation

- **[README.md](README.md)** - Main project overview & architecture
- **[MODERN_ANALYTICS_STACK.md](MODERN_ANALYTICS_STACK.md)** - Detailed implementation guide
- **[MODERN_STACK_ARCHITECTURE.md](MODERN_STACK_ARCHITECTURE.md)** - System architecture
- **[INTERVIEW_GUIDE.md](INTERVIEW_GUIDE.md)** - Interview preparation

---

## ✅ Supported Features

✓ Orchestration (Apache Airflow)  
✓ SQL Transformations (dbt)  
✓ Data Quality Validation (Great Expectations)  
✓ Multi-Warehouse Support (Postgres, BigQuery, Redshift)  
✓ Interactive Dashboards (Streamlit)  

---

For detailed documentation, see main files linked above.
