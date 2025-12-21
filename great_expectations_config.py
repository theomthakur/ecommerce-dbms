"""Great Expectations configuration and validation runner"""

from pathlib import Path
import json
from typing import Dict, Any
from great_expectations.data_context import DataContext
from great_expectations.core.batch import RuntimeBatchRequest
import logging

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GE_DIR = PROJECT_ROOT / 'great_expectations'


def get_data_context():
    """Initialize Great Expectations data context"""
    context = DataContext(
        context_root_dir=str(GE_DIR)
    )
    return context


def create_orders_quality_suite():
    """Create expectations suite for orders table"""
    context = get_data_context()
    
    suite = context.create_expectation_suite(
        expectation_suite_name='orders_quality',
        overwrite_existing=True,
    )
    
    batch_request = RuntimeBatchRequest(
        datasource_name='ecommerce_datasource',
        data_connector_name='postgres_connector',
        data_asset_name='orders',
    )
    
    validator = context.get_validator(batch_request=batch_request, expectation_suite_name='orders_quality')
    
    # Expectations
    validator.expect_table_row_count_to_be_between(min_value=1000, max_value=1000000)
    validator.expect_column_values_to_be_in_set('order_id', [])  # Non-null check
    validator.expect_column_values_to_not_be_null('customer_id')
    validator.expect_column_values_to_not_be_null('order_date')
    validator.expect_column_values_to_be_of_type('order_date', 'date')
    
    validator.save_expectation_suite(discard_failed_expectations=False)
    logger.info("Orders quality suite created")
    return suite


def create_customers_quality_suite():
    """Create expectations suite for customers table"""
    context = get_data_context()
    
    suite = context.create_expectation_suite(
        expectation_suite_name='customers_quality',
        overwrite_existing=True,
    )
    
    batch_request = RuntimeBatchRequest(
        datasource_name='ecommerce_datasource',
        data_connector_name='postgres_connector',
        data_asset_name='customers',
    )
    
    validator = context.get_validator(batch_request=batch_request, expectation_suite_name='customers_quality')
    
    # Expectations
    validator.expect_table_row_count_to_be_between(min_value=100, max_value=100000)
    validator.expect_column_values_to_not_be_null('customer_id')
    validator.expect_column_to_exist('customer_name')
    validator.expect_column_values_to_be_in_set('segment', ['Consumer', 'Corporate', 'Home Office'])
    
    validator.save_expectation_suite(discard_failed_expectations=False)
    logger.info("Customers quality suite created")
    return suite


def create_order_items_quality_suite():
    """Create expectations suite for order_items table"""
    context = get_data_context()
    
    suite = context.create_expectation_suite(
        expectation_suite_name='order_items_quality',
        overwrite_existing=True,
    )
    
    batch_request = RuntimeBatchRequest(
        datasource_name='ecommerce_datasource',
        data_connector_name='postgres_connector',
        data_asset_name='order_items',
    )
    
    validator = context.get_validator(batch_request=batch_request, expectation_suite_name='order_items_quality')
    
    # Expectations
    validator.expect_table_row_count_to_be_between(min_value=10000, max_value=10000000)
    validator.expect_column_values_to_not_be_null('order_id')
    validator.expect_column_values_to_not_be_null('product_id')
    validator.expect_column_values_to_be_between('quantity', min_value=1, max_value=10)
    validator.expect_column_values_to_be_between('sales', min_value=0)
    validator.expect_column_values_to_be_between('discount', min_value=0, max_value=1)
    
    validator.save_expectation_suite(discard_failed_expectations=False)
    logger.info("Order Items quality suite created")
    return suite


def run_validation_suite(
    suite_name: str,
    data_source: str,
    table_name: str,
    warehouse_type: str = 'postgres',
) -> Dict[str, Any]:
    """Run a validation suite and return results"""
    context = get_data_context()
    
    batch_request = RuntimeBatchRequest(
        datasource_name=data_source,
        data_connector_name=f'{warehouse_type}_connector',
        data_asset_name=table_name,
    )
    
    validator = context.get_validator(batch_request=batch_request, expectation_suite_name=suite_name)
    checkpoint = context.run_checkpoint(
        checkpoint_name=f'{suite_name}_checkpoint',
        validations=[
            {
                'batch_request': batch_request,
                'expectation_suite_name': suite_name,
            }
        ],
    )
    
    results = {
        'suite_name': suite_name,
        'table_name': table_name,
        'success': checkpoint.success,
        'results': checkpoint.run_results,
    }
    
    logger.info(f"Validation results for {suite_name}: {checkpoint.success}")
    return results


def generate_quality_report(dw_db: str, output_path: str) -> str:
    """Generate HTML data quality report"""
    context = get_data_context()
    
    # Build report HTML
    html_report = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Data Quality Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #4CAF50; color: white; }
            tr:nth-child(even) { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>Data Quality Report</h1>
        <p>Generated at: {timestamp}</p>
        <h2>Validation Suites</h2>
        <table>
            <tr>
                <th>Suite Name</th>
                <th>Status</th>
                <th>Details</th>
            </tr>
        </table>
    </body>
    </html>
    """
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(html_report)
    
    logger.info(f"Quality report generated: {output_path}")
    return output_path
