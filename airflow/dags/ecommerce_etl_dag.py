"""
Airflow DAG: E-Commerce ETL Pipeline
Orchestrates data ingestion, transformation, and warehouse loading
"""

from datetime import datetime, timedelta
from pathlib import Path
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.task_group import TaskGroup
from airflow.models import Variable
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts import etl_oltp, build_dw, logger as logger_module

logger = logger_module.get_logger('airflow_etl')

# Default DAG arguments
default_args = {
    'owner': 'data-engineering',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025, 1, 1),
    'catchup': False,
    'email_on_failure': True,
    'email': ['data-team@company.com'],
}

# DAG definition
dag = DAG(
    'ecommerce_etl_pipeline',
    default_args=default_args,
    description='ETL pipeline for e-commerce data warehouse',
    schedule_interval='@daily',
    tags=['ecommerce', 'etl', 'warehouse'],
)

# Configuration from Airflow Variables
ORDERS_PATH = Variable.get('orders_csv_path', '/data/Awesome_Inc_Superstore_Orders.csv')
RETURNS_PATH = Variable.get('returns_csv_path', '/data/Awesome_Inc_Superstore_Returns.csv')
OLTP_DB = Variable.get('oltp_db_path', '/data/oltp.db')
DW_DB = Variable.get('dw_db_path', '/data/dw.db')


def task_extract_and_validate():
    """Extract raw CSVs and validate schema"""
    logger.info(f"Extracting orders from {ORDERS_PATH}")
    logger.info(f"Extracting returns from {RETURNS_PATH}")
    
    import pandas as pd
    orders = pd.read_csv(ORDERS_PATH, encoding='latin1', low_memory=False)
    returns = pd.read_csv(RETURNS_PATH, encoding='latin1', low_memory=False)
    
    logger.info(f"Orders shape: {orders.shape}")
    logger.info(f"Returns shape: {returns.shape}")
    
    return {'orders_rows': len(orders), 'returns_rows': len(returns)}


def task_build_oltp():
    """Build normalized OLTP database"""
    logger.info("Building OLTP database...")
    etl_oltp.build_oltp(
        orders_csv=Path(ORDERS_PATH),
        returns_csv=Path(RETURNS_PATH),
        out_db=Path(OLTP_DB)
    )
    logger.info("OLTP build completed")


def task_build_data_warehouse():
    """Build star schema data warehouse from OLTP"""
    logger.info("Building Data Warehouse...")
    build_dw.build_dw(
        source_db=Path(OLTP_DB),
        dest_db=Path(DW_DB)
    )
    logger.info("Data Warehouse build completed")


# Task 1: Extract and Validate
extract_validate = PythonOperator(
    task_id='extract_and_validate',
    python_callable=task_extract_and_validate,
    dag=dag,
)

# Task 2: Build OLTP
with TaskGroup('oltp_layer', dag=dag) as oltp_layer:
    build_oltp = PythonOperator(
        task_id='build_oltp_db',
        python_callable=task_build_oltp,
    )
    
    validate_oltp = BashOperator(
        task_id='validate_oltp',
        bash_command='python -m pytest {{ params.test_path }} -v',
        params={'test_path': f'{PROJECT_ROOT}/tests/test_integration_postgres.py'},
    )
    
    build_oltp >> validate_oltp

# Task 3: Build Data Warehouse
build_dw_task = PythonOperator(
    task_id='build_data_warehouse',
    python_callable=task_build_data_warehouse,
    dag=dag,
)

# Task 4: Trigger dbt transformations
trigger_dbt = TriggerDagRunOperator(
    task_id='trigger_dbt_transformations',
    trigger_dag_id='ecommerce_dbt_transformations',
    wait_for_completion=True,
    dag=dag,
)

# Task 5: Trigger Great Expectations validation
trigger_ge = TriggerDagRunOperator(
    task_id='trigger_data_quality_checks',
    trigger_dag_id='ecommerce_data_quality',
    wait_for_completion=True,
    dag=dag,
)

# Task 6: Load to warehouse (BigQuery/Redshift)
load_warehouse = BashOperator(
    task_id='load_to_warehouse',
    bash_command='''
    python -c "
    import sys
    from pathlib import Path
    sys.path.insert(0, '{{ params.project_root }}')
    from warehouse_config import warehouse_loader
    warehouse_loader.load_dw_to_warehouse(
        dw_db='{{ params.dw_db }}',
        warehouse_type='{{ params.warehouse_type }}'
    )
    "
    ''',
    params={
        'project_root': str(PROJECT_ROOT),
        'dw_db': DW_DB,
        'warehouse_type': Variable.get('warehouse_type', 'bigquery'),
    },
    dag=dag,
)

# Task Dependencies
extract_validate >> oltp_layer >> build_dw_task >> trigger_dbt >> trigger_ge >> load_warehouse
