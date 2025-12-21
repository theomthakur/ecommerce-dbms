"""
Airflow DAG: Great Expectations Data Quality Validation
Runs data quality checks on ingested and transformed data
"""

from datetime import datetime, timedelta
from pathlib import Path
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from great_expectations.core.batch import RuntimeBatchRequest
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from great_expectations_config import ge_runner

default_args = {
    'owner': 'data-engineering',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025, 1, 1),
    'catchup': False,
}

dag = DAG(
    'ecommerce_data_quality',
    default_args=default_args,
    description='Data quality validation using Great Expectations',
    schedule_interval=None,  # Triggered by main ETL DAG
    tags=['data-quality', 'great-expectations'],
)

WAREHOUSE_TYPE = Variable.get('warehouse_type', 'postgres')
DW_DB = Variable.get('dw_db_path', '/data/dw.db')


def validate_orders_table():
    """Validate orders table against expectations"""
    print("Validating orders table...")
    results = ge_runner.run_validation_suite(
        suite_name='orders_quality',
        data_source='ecommerce_dw',
        table_name='orders',
        warehouse_type=WAREHOUSE_TYPE,
    )
    print(f"Orders validation results: {results}")
    return results


def validate_customers_table():
    """Validate customers table against expectations"""
    print("Validating customers table...")
    results = ge_runner.run_validation_suite(
        suite_name='customers_quality',
        data_source='ecommerce_dw',
        table_name='customers',
        warehouse_type=WAREHOUSE_TYPE,
    )
    print(f"Customers validation results: {results}")
    return results


def validate_products_table():
    """Validate products table against expectations"""
    print("Validating products table...")
    results = ge_runner.run_validation_suite(
        suite_name='products_quality',
        data_source='ecommerce_dw',
        table_name='products',
        warehouse_type=WAREHOUSE_TYPE,
    )
    print(f"Products validation results: {results}")
    return results


def validate_order_items_table():
    """Validate order_items table against expectations"""
    print("Validating order_items table...")
    results = ge_runner.run_validation_suite(
        suite_name='order_items_quality',
        data_source='ecommerce_dw',
        table_name='order_items',
        warehouse_type=WAREHOUSE_TYPE,
    )
    print(f"Order Items validation results: {results}")
    return results


def validate_returns_table():
    """Validate returns table against expectations"""
    print("Validating returns table...")
    results = ge_runner.run_validation_suite(
        suite_name='returns_quality',
        data_source='ecommerce_dw',
        table_name='returns',
        warehouse_type=WAREHOUSE_TYPE,
    )
    print(f"Returns validation results: {results}")
    return results


def generate_quality_report():
    """Generate consolidated data quality report"""
    print("Generating data quality report...")
    report = ge_runner.generate_quality_report(
        dw_db=DW_DB,
        output_path=f'{PROJECT_ROOT}/reports/data_quality_report.html',
    )
    print(f"Quality report generated: {report}")
    return report


# Data Quality Tasks
validate_orders = PythonOperator(
    task_id='validate_orders',
    python_callable=validate_orders_table,
    dag=dag,
)

validate_customers = PythonOperator(
    task_id='validate_customers',
    python_callable=validate_customers_table,
    dag=dag,
)

validate_products = PythonOperator(
    task_id='validate_products',
    python_callable=validate_products_table,
    dag=dag,
)

validate_order_items = PythonOperator(
    task_id='validate_order_items',
    python_callable=validate_order_items_table,
    dag=dag,
)

validate_returns = PythonOperator(
    task_id='validate_returns',
    python_callable=validate_returns_table,
    dag=dag,
)

generate_report = PythonOperator(
    task_id='generate_quality_report',
    python_callable=generate_quality_report,
    dag=dag,
)

# Task dependencies (all validations in parallel, then report)
[validate_orders, validate_customers, validate_products, validate_order_items, validate_returns] >> generate_report
