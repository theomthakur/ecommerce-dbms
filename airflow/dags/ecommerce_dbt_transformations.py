"""
Airflow DAG: dbt Transformations
Executes dbt models for dimensional modeling and business logic
"""

from datetime import datetime, timedelta
from pathlib import Path
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.models import Variable

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DBT_PROJECT_DIR = PROJECT_ROOT / 'dbt'

default_args = {
    'owner': 'data-engineering',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025, 1, 1),
    'catchup': False,
}

dag = DAG(
    'ecommerce_dbt_transformations',
    default_args=default_args,
    description='dbt transformation pipeline for e-commerce data',
    schedule_interval=None,  # Triggered by main ETL DAG
    tags=['dbt', 'transformations'],
)

DBT_PROFILES_DIR = Variable.get('dbt_profiles_dir', str(PROJECT_ROOT / 'dbt/profiles'))
WAREHOUSE_TYPE = Variable.get('warehouse_type', 'postgres')

# dbt Parse (validate project)
dbt_parse = BashOperator(
    task_id='dbt_parse',
    bash_command=f'''
    cd {DBT_PROJECT_DIR} && \
    dbt parse --profiles-dir {DBT_PROFILES_DIR} --target {WAREHOUSE_TYPE}
    ''',
    dag=dag,
)

# dbt Staging Models
dbt_staging = BashOperator(
    task_id='dbt_staging_models',
    bash_command=f'''
    cd {DBT_PROJECT_DIR} && \
    dbt run --select staging.* --profiles-dir {DBT_PROFILES_DIR} --target {WAREHOUSE_TYPE}
    ''',
    dag=dag,
)

# dbt Mart Models
dbt_marts = BashOperator(
    task_id='dbt_mart_models',
    bash_command=f'''
    cd {DBT_PROJECT_DIR} && \
    dbt run --select marts.* --profiles-dir {DBT_PROFILES_DIR} --target {WAREHOUSE_TYPE}
    ''',
    dag=dag,
)

# dbt Tests
dbt_tests = BashOperator(
    task_id='dbt_tests',
    bash_command=f'''
    cd {DBT_PROJECT_DIR} && \
    dbt test --profiles-dir {DBT_PROFILES_DIR} --target {WAREHOUSE_TYPE}
    ''',
    dag=dag,
)

# dbt Generate Documentation
dbt_docs = BashOperator(
    task_id='dbt_docs_generate',
    bash_command=f'''
    cd {DBT_PROJECT_DIR} && \
    dbt docs generate --profiles-dir {DBT_PROFILES_DIR} --target {WAREHOUSE_TYPE}
    ''',
    dag=dag,
)

# Task dependencies
dbt_parse >> dbt_staging >> dbt_marts >> dbt_tests >> dbt_docs
